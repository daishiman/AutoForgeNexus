"""
Cloudflare Workers Python用リトライデコレータ

tenacityの代替として、シンプルなエクスポネンシャルバックオフ付きリトライを実装します。
Pure Pythonで、追加依存関係は不要です。

使用例:
    from src.core.cloudflare.retry import retry
    from httpx import HTTPError

    @retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(HTTPError,))
    async def call_openai_api(prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json={"model": "gpt-4", "messages": [{"role": "user", "content": prompt}]}
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
"""

import asyncio
import logging
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    log_errors: bool = True,
):
    """
    エクスポネンシャルバックオフ付きリトライデコレータ

    Args:
        max_attempts: 最大試行回数（デフォルト: 3回）
        delay: 初回待機時間（秒）（デフォルト: 1.0秒）
        backoff: バックオフ係数（デフォルト: 2.0倍）
        exceptions: リトライ対象の例外タプル（デフォルト: すべての例外）
        log_errors: エラーログを出力するか（デフォルト: True）

    Returns:
        デコレートされた関数

    Examples:
        >>> @retry(max_attempts=3, delay=1.0)
        ... async def flaky_function():
        ...     # 最大3回リトライ
        ...     pass

        >>> @retry(max_attempts=5, delay=0.5, backoff=2.0, exceptions=(HTTPError,))
        ... async def call_api():
        ...     # HTTPErrorのみリトライ（0.5秒、1秒、2秒、4秒待機）
        ...     pass

    Notes:
        - 非同期関数と同期関数の両方をサポート
        - エクスポネンシャルバックオフ: delay * (backoff ** attempt)
        - 最終試行でも失敗した場合、元の例外をre-raise
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    # 最終試行の場合は即座にre-raise
                    if attempt == max_attempts - 1:
                        if log_errors:
                            logger.error(
                                f"{func.__name__} failed after {max_attempts} attempts: {e}",
                                exc_info=True,
                            )
                        raise

                    # バックオフ計算
                    wait_time = delay * (backoff**attempt)

                    if log_errors:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts}). "
                            f"Retrying in {wait_time:.2f}s... Error: {e}"
                        )

                    await asyncio.sleep(wait_time)

            # 到達不可能（念のため）
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic error")

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    # 最終試行の場合は即座にre-raise
                    if attempt == max_attempts - 1:
                        if log_errors:
                            logger.error(
                                f"{func.__name__} failed after {max_attempts} attempts: {e}",
                                exc_info=True,
                            )
                        raise

                    # バックオフ計算
                    wait_time = delay * (backoff**attempt)

                    if log_errors:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts}). "
                            f"Retrying in {wait_time:.2f}s... Error: {e}"
                        )

                    import time

                    time.sleep(wait_time)

            # 到達不可能（念のため）
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic error")

        # 非同期関数か同期関数かを判定
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def retry_on_network_error(
    max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0
):
    """
    ネットワークエラー専用リトライデコレータ

    HTTPError, TimeoutError, ConnectionErrorをリトライ対象とします。

    Args:
        max_attempts: 最大試行回数
        delay: 初回待機時間（秒）
        backoff: バックオフ係数

    Examples:
        >>> @retry_on_network_error(max_attempts=5, delay=0.5)
        ... async def call_llm_api(prompt: str) -> str:
        ...     # ネットワークエラーのみリトライ
        ...     pass
    """

    try:
        from httpx import HTTPError, TimeoutException

        network_exceptions = (HTTPError, TimeoutException, ConnectionError, OSError)
    except ImportError:
        # httpx未インストール時はデフォルト例外のみ
        network_exceptions = (ConnectionError, OSError, TimeoutError)

    return retry(
        max_attempts=max_attempts,
        delay=delay,
        backoff=backoff,
        exceptions=network_exceptions,
    )


def retry_with_circuit_breaker(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
):
    """
    サーキットブレーカー付きリトライデコレータ

    連続失敗回数が閾値を超えた場合、一定時間リクエストを遮断します。

    Args:
        max_attempts: 最大試行回数
        delay: 初回待機時間（秒）
        backoff: バックオフ係数
        failure_threshold: サーキットブレーカー発動閾値
        recovery_timeout: サーキットブレーカー回復時間（秒）

    Examples:
        >>> @retry_with_circuit_breaker(failure_threshold=5, recovery_timeout=60.0)
        ... async def call_external_service():
        ...     # 5回連続失敗で60秒間遮断
        ...     pass

    Notes:
        - 実装は簡易版（本格実装は別ライブラリ推奨）
        - グローバル状態管理（関数ごとに独立）
    """

    import time

    # サーキットブレーカー状態（関数ごとに保持）
    circuit_state = {
        "failure_count": 0,
        "last_failure_time": 0.0,
        "is_open": False,
    }

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            # サーキットブレーカーチェック
            if circuit_state["is_open"]:
                elapsed = time.time() - circuit_state["last_failure_time"]
                if elapsed < recovery_timeout:
                    raise RuntimeError(
                        f"Circuit breaker OPEN for {func.__name__}. "
                        f"Retry after {recovery_timeout - elapsed:.1f}s"
                    )
                else:
                    # 回復タイムアウト経過、リセット
                    circuit_state["is_open"] = False
                    circuit_state["failure_count"] = 0
                    logger.info(f"Circuit breaker CLOSED for {func.__name__}")

            try:
                # リトライ実行
                result = await retry(
                    max_attempts=max_attempts,
                    delay=delay,
                    backoff=backoff,
                )(func)(*args, **kwargs)

                # 成功時はカウンタリセット
                circuit_state["failure_count"] = 0
                return result

            except Exception:
                # 失敗カウンタ増加
                circuit_state["failure_count"] += 1
                circuit_state["last_failure_time"] = time.time()

                # 閾値超過でサーキットブレーカーOPEN
                if circuit_state["failure_count"] >= failure_threshold:
                    circuit_state["is_open"] = True
                    logger.error(
                        f"Circuit breaker OPEN for {func.__name__} "
                        f"(failures: {circuit_state['failure_count']})"
                    )

                raise

        return async_wrapper

    return decorator
