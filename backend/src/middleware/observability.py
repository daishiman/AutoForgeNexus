"""
AutoForgeNexus - Observability Middleware
observability-engineer による包括的観測可能性ミドルウェア
"""

import json
import logging
import time
import uuid
from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..monitoring import metrics_collector

# ロガー設定
logger = logging.getLogger("autoforgenexus.observability")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """包括的観測可能性ミドルウェア"""

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: list | None = None,
        include_request_body: bool = False,
        include_response_body: bool = False,
        sensitive_headers: list | None = None,
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/favicon.ico"]
        self.include_request_body = include_request_body
        self.include_response_body = include_response_body
        self.sensitive_headers = sensitive_headers or [
            "authorization",
            "cookie",
            "x-api-key",
            "x-auth-token",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """リクエスト処理と観測データ収集"""

        # 除外パスのチェック
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # リクエスト開始時刻
        start_time = time.time()

        # リクエストID生成
        request_id = str(uuid.uuid4())

        # コンテキスト情報
        context = {
            "request_id": request_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": self._sanitize_headers(dict(request.headers)),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
        }

        # リクエストボディの記録（設定されている場合）
        if self.include_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    context["request_body"] = await self._sanitize_body(body)
            except Exception as e:
                logger.warning(f"Failed to read request body: {e}")

        # ログ開始
        logger.info("Request started", extra={"context": context})

        # リクエスト処理
        try:
            response = await call_next(request)

            # 処理時間計算
            duration = time.time() - start_time

            # レスポンス情報
            response_context = {
                **context,
                "status_code": response.status_code,
                "duration_ms": duration * 1000,
                "response_headers": self._sanitize_headers(dict(response.headers)),
            }

            # レスポンスボディの記録（設定されている場合）
            if self.include_response_body and response.status_code < 400:
                try:
                    # レスポンスボディは読み込み済みの場合のみ
                    if hasattr(response, "_body") and response._body:
                        response_context["response_body"] = await self._sanitize_body(
                            response._body
                        )
                except Exception as e:
                    logger.warning(f"Failed to read response body: {e}")

            # メトリクス記録
            metrics_collector.record_request_metrics(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration,
            )

            # ログ記録
            if response.status_code >= 400:
                logger.warning(
                    "Request completed with error", extra={"context": response_context}
                )
            else:
                logger.info(
                    "Request completed successfully",
                    extra={"context": response_context},
                )

            # レスポンスヘッダーにリクエストIDを追加
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = str(int(duration * 1000))

            return response

        except Exception as e:
            # エラー発生時の処理
            duration = time.time() - start_time

            error_context = {
                **context,
                "duration_ms": duration * 1000,
                "error": str(e),
                "error_type": type(e).__name__,
            }

            # エラーメトリクス記録
            metrics_collector.record_error_metrics(
                error_type=type(e).__name__, error_message=str(e)
            )

            # エラーログ
            logger.error(
                "Request failed with exception",
                extra={"context": error_context},
                exc_info=True,
            )

            # 例外を再発生
            raise

    def _get_client_ip(self, request: Request) -> str:
        """クライアントIPアドレスを取得"""
        # Cloudflare の場合
        cf_connecting_ip = request.headers.get("cf-connecting-ip")
        if cf_connecting_ip:
            return cf_connecting_ip

        # 一般的なプロキシヘッダー
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # フォールバック
        return getattr(request.client, "host", "unknown")

    def _sanitize_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """ヘッダーの機密情報をサニタイズ"""
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        return sanitized

    async def _sanitize_body(self, body: bytes) -> str:
        """ボディの機密情報をサニタイズ"""
        try:
            # JSON の場合
            data = json.loads(body.decode("utf-8"))
            if isinstance(data, dict):
                return self._sanitize_dict(data)
            return str(data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # JSON でない場合はサイズ制限のみ
            text = body.decode("utf-8", errors="ignore")
            if len(text) > 1000:
                return text[:1000] + "... [TRUNCATED]"
            return text

    def _sanitize_dict(self, data: dict[str, Any], depth: int = 0) -> dict[str, Any]:
        """辞書データの機密情報をサニタイズ"""
        # Prevent deep nesting DoS attacks
        max_depth = 10
        if depth > max_depth:
            return {"error": "[DEPTH_LIMIT_EXCEEDED]"}

        sensitive_keys = [
            "password",
            "token",
            "secret",
            "key",
            "auth",
            "credential",
            "private",
            "session",
            "cookie",
        ]

        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value, depth + 1)
            else:
                sanitized[key] = value

        return sanitized


class LLMObservabilityMiddleware:
    """LLM呼び出し専用の観測ミドルウェア"""

    def __init__(self):
        self.logger = logging.getLogger("autoforgenexus.llm")

    @asynccontextmanager
    async def track_llm_call(
        self,
        provider: str,
        model: str,
        prompt: str,
        user_id: str | None = None,
        session_id: str | None = None,
    ):
        """LLM呼び出しの追跡"""
        start_time = time.time()
        call_id = str(uuid.uuid4())

        context = {
            "call_id": call_id,
            "provider": provider,
            "model": model,
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "prompt_length": len(prompt),
        }

        self.logger.info("LLM call started", extra={"context": context})

        try:
            yield call_id

            duration = time.time() - start_time
            context["duration_ms"] = duration * 1000

            self.logger.info("LLM call completed", extra={"context": context})

        except Exception as e:
            duration = time.time() - start_time
            context.update(
                {
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )

            self.logger.error(
                "LLM call failed", extra={"context": context}, exc_info=True
            )

            # エラーメトリクス記録
            metrics_collector.record_error_metrics(
                error_type=f"LLM_{type(e).__name__}", error_message=str(e)
            )

            raise

    def record_llm_result(
        self,
        call_id: str,
        response: str,
        tokens_used: int,
        cost: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ):
        """LLM呼び出し結果の記録"""
        context = {
            "call_id": call_id,
            "response_length": len(response),
            "tokens_used": tokens_used,
            "cost_usd": cost,
            "metadata": metadata or {},
        }

        self.logger.info("LLM response recorded", extra={"context": context})


class DatabaseObservabilityMiddleware:
    """データベース操作の観測ミドルウェア"""

    def __init__(self):
        self.logger = logging.getLogger("autoforgenexus.database")

    @asynccontextmanager
    async def track_query(
        self,
        operation: str,
        table: str | None = None,
        user_id: str | None = None,
    ):
        """データベースクエリの追跡"""
        start_time = time.time()
        query_id = str(uuid.uuid4())

        context = {
            "query_id": query_id,
            "operation": operation,
            "table": table,
            "user_id": user_id,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self.logger.info("Database query started", extra={"context": context})

        try:
            yield query_id

            duration = time.time() - start_time
            context["duration_ms"] = duration * 1000

            # スロークエリの警告
            if duration > 1.0:  # 1秒以上
                self.logger.warning(
                    "Slow database query detected", extra={"context": context}
                )
            else:
                self.logger.info("Database query completed", extra={"context": context})

        except Exception as e:
            duration = time.time() - start_time
            context.update(
                {
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )

            self.logger.error(
                "Database query failed", extra={"context": context}, exc_info=True
            )

            # エラーメトリクス記録
            metrics_collector.record_error_metrics(
                error_type=f"DB_{type(e).__name__}", error_message=str(e)
            )

            raise


# グローバルインスタンス
llm_observability = LLMObservabilityMiddleware()
db_observability = DatabaseObservabilityMiddleware()


# 使用例とヘルパー関数
async def track_prompt_processing(
    prompt_id: str,
    user_id: str,
    prompt_text: str,
    provider: str = "openai",
    model: str = "gpt-4",
) -> str:
    """プロンプト処理の完全な追跡"""
    async with llm_observability.track_llm_call(
        provider=provider,
        model=model,
        prompt=prompt_text,
        user_id=user_id,
        session_id=prompt_id,
    ) as call_id:
        # ここで実際のLLM呼び出し処理
        # ...
        return call_id


def setup_observability_logging():
    """観測可能性ログの設定"""
    import logging.config

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(funcName)s %(process)d %(thread)d",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {
            "autoforgenexus.observability": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "autoforgenexus.llm": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "autoforgenexus.database": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(config)
