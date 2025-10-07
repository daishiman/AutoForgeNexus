"""
AutoForgeNexus - Backend Monitoring and Health Check System
observability-engineer による包括的ヘルスチェック実装
"""

import asyncio
import logging
import os
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import aioredis
import httpx
import psutil
from sqlalchemy import text

# カスタムロガー設定
logger = logging.getLogger("autoforgenexus.monitoring")


class HealthStatus(str, Enum):
    """ヘルス状態の列挙型"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class SystemMetrics:
    """システムメトリクス"""

    cpu_percent: float
    memory_percent: float
    disk_percent: float
    load_average: list[float] | None
    uptime_seconds: float
    process_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DependencyHealth:
    """依存サービスのヘルス状態"""

    name: str
    status: HealthStatus
    response_time_ms: float
    version: str | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HealthCheckResponse:
    """ヘルスチェックレスポンス"""

    service: str
    status: HealthStatus
    timestamp: str
    environment: str
    version: str
    uptime_seconds: float
    system: SystemMetrics
    dependencies: list[DependencyHealth]
    checks: dict[str, bool]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["system"] = self.system.to_dict()
        result["dependencies"] = [dep.to_dict() for dep in self.dependencies]
        return result


class HealthChecker:
    """ヘルスチェック実行クラス"""

    def __init__(self) -> None:
        self.start_time = time.time()
        self.service_name = "AutoForgeNexus Backend"
        self.version = os.getenv("APP_VERSION", "0.1.0")
        self.environment = os.getenv("ENVIRONMENT", "development")

    async def get_health_status(self) -> HealthCheckResponse:
        """包括的なヘルスチェックを実行"""
        try:
            # システムメトリクス取得
            system_metrics = self._get_system_metrics()

            # 依存サービスチェック
            dependencies = await self._check_dependencies()

            # 全体的なヘルス状態判定
            overall_status = self._determine_overall_status(dependencies)

            # チェック結果サマリー
            checks = {
                dep.name: dep.status == HealthStatus.HEALTHY for dep in dependencies
            }

            return HealthCheckResponse(
                service=self.service_name,
                status=overall_status,
                timestamp=datetime.now(UTC).isoformat(),
                environment=self.environment,
                version=self.version,
                uptime_seconds=time.time() - self.start_time,
                system=system_metrics,
                dependencies=dependencies,
                checks=checks,
            )

        except Exception as e:
            logger.exception("Health check failed")
            return HealthCheckResponse(
                service=self.service_name,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.now(UTC).isoformat(),
                environment=self.environment,
                version=self.version,
                uptime_seconds=time.time() - self.start_time,
                system=self._get_fallback_system_metrics(),
                dependencies=[],
                checks={},
                error=str(e),
            )

    def _get_system_metrics(self) -> SystemMetrics:
        """システムメトリクスを取得"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            # メモリ使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # ディスク使用率
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100

            # ロードアベレージ（Unix系のみ）
            load_average = None
            if hasattr(os, "getloadavg"):
                load_average = list(os.getloadavg())

            # アップタイム
            uptime_seconds = time.time() - psutil.boot_time()

            # プロセス数
            process_count = len(psutil.pids())

            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                load_average=load_average,
                uptime_seconds=uptime_seconds,
                process_count=process_count,
            )

        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            return self._get_fallback_system_metrics()

    def _get_fallback_system_metrics(self) -> SystemMetrics:
        """フォールバック用のシステムメトリクス"""
        return SystemMetrics(
            cpu_percent=0.0,
            memory_percent=0.0,
            disk_percent=0.0,
            load_average=None,
            uptime_seconds=time.time() - self.start_time,
            process_count=0,
        )

    async def _check_dependencies(self) -> list[DependencyHealth]:
        """依存サービスのヘルスチェック"""
        checks = await asyncio.gather(
            self._check_database(),
            self._check_redis(),
            self._check_langfuse(),
            self._check_external_apis(),
            return_exceptions=True,
        )

        dependencies = []
        for check in checks:
            if isinstance(check, DependencyHealth):
                dependencies.append(check)
            elif isinstance(check, Exception):
                logger.error(f"Dependency check failed: {check}")
                dependencies.append(
                    DependencyHealth(
                        name="unknown",
                        status=HealthStatus.UNHEALTHY,
                        response_time_ms=0,
                        error=str(check),
                    )
                )

        return dependencies

    async def _check_database(self) -> DependencyHealth:
        """データベース接続チェック"""
        start_time = time.time()

        try:
            from .infrastructure.database import get_database_session

            async with get_database_session() as session:
                result = await session.execute(text("SELECT 1"))
                await result.fetchone()

            response_time = (time.time() - start_time) * 1000

            return DependencyHealth(
                name="database",
                status=HealthStatus.HEALTHY,
                response_time_ms=response_time,
                version="turso",
                metadata={
                    "connection_pool": "active",
                    "database_url": (
                        os.getenv("TURSO_DATABASE_URL", "").split("@")[-1]
                        if os.getenv("TURSO_DATABASE_URL")
                        else "not_configured"
                    ),
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return DependencyHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error=str(e),
            )

    async def _check_redis(self) -> DependencyHealth:
        """Redis接続チェック"""
        start_time = time.time()

        try:
            redis_url = os.getenv("REDIS_URL")
            if not redis_url:
                return DependencyHealth(
                    name="redis",
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=0,
                    error="Redis URL not configured",
                )

            redis = aioredis.from_url(redis_url)
            await redis.ping()
            info = await redis.info()
            await redis.close()

            response_time = (time.time() - start_time) * 1000

            return DependencyHealth(
                name="redis",
                status=HealthStatus.HEALTHY,
                response_time_ms=response_time,
                version=info.get("redis_version", "unknown"),
                metadata={
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "unknown"),
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return DependencyHealth(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error=str(e),
            )

    async def _check_langfuse(self) -> DependencyHealth:
        """LangFuse接続チェック"""
        start_time = time.time()

        try:
            langfuse_host = os.getenv("LANGFUSE_HOST")
            if not langfuse_host:
                return DependencyHealth(
                    name="langfuse",
                    status=HealthStatus.DEGRADED,
                    response_time_ms=0,
                    error="LangFuse host not configured",
                )

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{langfuse_host}/api/public/health")
                response.raise_for_status()

            response_time = (time.time() - start_time) * 1000

            return DependencyHealth(
                name="langfuse",
                status=HealthStatus.HEALTHY,
                response_time_ms=response_time,
                metadata={"endpoint": f"{langfuse_host}/api/public/health"},
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return DependencyHealth(
                name="langfuse",
                status=HealthStatus.DEGRADED,
                response_time_ms=response_time,
                error=str(e),
            )

    async def _check_external_apis(self) -> DependencyHealth:
        """外部API接続チェック"""
        start_time = time.time()

        try:
            # OpenAI API チェック（例）
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={
                        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', 'test')}"
                    },
                )

                if response.status_code == 401:
                    # 認証エラーは設定の問題なので degraded として扱う
                    status = HealthStatus.DEGRADED
                    error = "API key not configured or invalid"
                elif response.status_code == 200:
                    status = HealthStatus.HEALTHY
                    error = None
                else:
                    status = HealthStatus.UNHEALTHY
                    error = f"HTTP {response.status_code}"

            response_time = (time.time() - start_time) * 1000

            return DependencyHealth(
                name="external_apis",
                status=status,
                response_time_ms=response_time,
                error=error,
                metadata={"checked_endpoints": ["openai"]},
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return DependencyHealth(
                name="external_apis",
                status=HealthStatus.DEGRADED,
                response_time_ms=response_time,
                error=str(e),
            )

    def _determine_overall_status(
        self, dependencies: list[DependencyHealth]
    ) -> HealthStatus:
        """全体のヘルス状態を判定"""
        if not dependencies:
            return HealthStatus.UNHEALTHY

        # クリティカルな依存関係の確認
        critical_deps = ["database"]
        for dep in dependencies:
            if dep.name in critical_deps and dep.status == HealthStatus.UNHEALTHY:
                return HealthStatus.UNHEALTHY

        # 全体的な健全性チェック
        unhealthy_count = sum(
            1 for dep in dependencies if dep.status == HealthStatus.UNHEALTHY
        )
        degraded_count = sum(
            1 for dep in dependencies if dep.status == HealthStatus.DEGRADED
        )

        if unhealthy_count > 0:
            return HealthStatus.DEGRADED
        elif degraded_count > len(dependencies) // 2:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


class MetricsCollector:
    """メトリクス収集クラス"""

    def __init__(self) -> None:
        self.metrics: dict[str, Any] = {}
        self.start_time = time.time()

    def record_request_metrics(
        self, method: str, endpoint: str, status_code: int, duration: float
    ) -> None:
        """リクエストメトリクスを記録"""
        timestamp = datetime.now(UTC).isoformat()

        metric = {
            "timestamp": timestamp,
            "type": "http_request",
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": duration * 1000,
            "environment": os.getenv("ENVIRONMENT", "development"),
        }

        logger.info("Request metric", extra={"metric": metric})

    def record_llm_metrics(
        self, provider: str, model: str, tokens_used: int, cost: float, duration: float
    ) -> None:
        """LLMメトリクスを記録"""
        timestamp = datetime.now(UTC).isoformat()

        metric = {
            "timestamp": timestamp,
            "type": "llm_call",
            "provider": provider,
            "model": model,
            "tokens_used": tokens_used,
            "cost_usd": cost,
            "duration_ms": duration * 1000,
            "environment": os.getenv("ENVIRONMENT", "development"),
        }

        logger.info("LLM metric", extra={"metric": metric})

    def record_error_metrics(
        self, error_type: str, error_message: str, stack_trace: str | None = None
    ) -> None:
        """エラーメトリクスを記録"""
        timestamp = datetime.now(UTC).isoformat()

        metric = {
            "timestamp": timestamp,
            "type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "environment": os.getenv("ENVIRONMENT", "development"),
        }

        logger.error("Error metric", extra={"metric": metric})


# グローバルインスタンス
health_checker = HealthChecker()
metrics_collector = MetricsCollector()


async def get_health() -> dict[str, Any]:
    """ヘルスチェックエンドポイント用関数"""
    health_status = await health_checker.get_health_status()
    return health_status.to_dict()


async def get_metrics() -> dict[str, Any]:
    """メトリクス取得エンドポイント用関数"""
    system_metrics = health_checker._get_system_metrics()

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "AutoForgeNexus Backend",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "uptime_seconds": time.time() - health_checker.start_time,
        "system": system_metrics.to_dict(),
        "version": os.getenv("APP_VERSION", "0.1.0"),
    }


async def check_readiness() -> dict[str, Any]:
    """Readiness probe用関数"""
    # 重要な依存関係のみチェック
    database_check = await health_checker._check_database()

    is_ready = database_check.status == HealthStatus.HEALTHY

    return {
        "ready": is_ready,
        "timestamp": datetime.now(UTC).isoformat(),
        "checks": {"database": database_check.to_dict()},
    }


async def check_liveness() -> dict[str, Any]:
    """Liveness probe用関数"""
    # 基本的な応答性のみチェック
    return {
        "alive": True,
        "timestamp": datetime.now(UTC).isoformat(),
        "uptime_seconds": time.time() - health_checker.start_time,
    }
