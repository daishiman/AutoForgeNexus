"""
ヘルスチェック・Readinessエンドポイント
Kubernetes、Docker、ロードバランサー対応
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""

    status: str = Field(..., description="サービスステータス")
    timestamp: datetime = Field(..., description="チェック時刻")
    version: str = Field(default="0.1.0", description="アプリケーションバージョン")
    environment: str = Field(..., description="実行環境")


class ReadinessResponse(BaseModel):
    """Readinessチェックレスポンス（詳細）"""

    status: str = Field(..., description="サービスステータス")
    timestamp: datetime = Field(..., description="チェック時刻")
    version: str = Field(default="0.1.0", description="アプリケーションバージョン")
    environment: str = Field(..., description="実行環境")
    checks: dict[str, Any] = Field(..., description="個別チェック結果")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="ヘルスチェック",
    description="サービスの生存確認（Liveness Probe）",
    status_code=status.HTTP_200_OK,
)
async def health_check() -> HealthResponse:
    """
    シンプルなヘルスチェック

    Docker HEALTHCHECK、Kubernetes Liveness Probeで使用
    依存サービスの状態は確認せず、プロセスの生存のみ確認

    Returns:
        HealthResponse: ヘルスチェック結果
    """
    import os

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC),
        version="0.1.0",
        environment=os.getenv("APP_ENV", "local"),
    )


@router.get(
    "/readiness",
    response_model=ReadinessResponse,
    summary="Readinessチェック",
    description="サービスのリクエスト受付準備確認（Readiness Probe）",
    status_code=status.HTTP_200_OK,
)
async def readiness_check(response: Response) -> ReadinessResponse:
    """
    詳細なReadinessチェック

    Kubernetes Readiness Probe、ロードバランサーで使用
    データベース、キャッシュ等の依存サービス状態を確認

    Returns:
        ReadinessResponse: Readiness結果（全チェック成功時のみ200）

    Note:
        Phase 4（データベース統合）以降に依存サービスチェック追加予定
        現在はプロセス生存のみ確認
    """
    import os

    checks: dict[str, Any] = {
        "process": "ok",
        # Phase 4以降に追加予定:
        # "database": await check_database_connection(),
        # "redis": await check_redis_connection(),
        # "llm_providers": await check_llm_availability(),
    }

    # すべてのチェックがOKか確認
    all_healthy = all(v == "ok" for v in checks.values())

    if not all_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status="ready" if all_healthy else "not_ready",
        timestamp=datetime.now(UTC),
        version="0.1.0",
        environment=os.getenv("APP_ENV", "local"),
        checks=checks,
    )


@router.get(
    "/",
    summary="ルートエンドポイント",
    description="API情報取得",
    status_code=status.HTTP_200_OK,
)
async def root() -> dict[str, str]:
    """
    ルートエンドポイント

    APIの基本情報を返却

    Returns:
        dict: API情報
    """
    return {
        "name": "AutoForgeNexus Backend API",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "readiness": "/readiness",
    }
