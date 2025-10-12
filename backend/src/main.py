"""
FastAPI Main Application
TDD実装: テストを満たす最小限の実装
"""

import sys
from pathlib import Path
from typing import Any

# Pyodide環境でsys.path初期化（タスク3: Pyodide sys.path初期化）
if "__pyodide__" in sys.modules or "pyodide" in sys.modules:
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config.settings import Settings
from presentation.api.shared import health

# 設定読み込み
settings = Settings()

# FastAPIアプリケーションの作成
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS設定
# Ensure CORS settings are lists
cors_origins = (
    settings.cors_allow_origins
    if isinstance(settings.cors_allow_origins, list)
    else [settings.cors_allow_origins]
)
cors_methods = (
    settings.cors_allow_methods
    if isinstance(settings.cors_allow_methods, list)
    else [settings.cors_allow_methods]
)
cors_headers = (
    settings.cors_allow_headers
    if isinstance(settings.cors_allow_headers, list)
    else [settings.cors_allow_headers]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=cors_methods,
    allow_headers=cors_headers,
)

# ヘルスチェックルーター追加
app.include_router(health.router)


@app.get("/", response_model=dict[str, Any])
async def root() -> dict[str, Any]:
    """
    ヘルスチェックエンドポイント
    システムの状態とメタデータを返す
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.app_env,
        "debug": settings.debug,
        "active_providers": settings.get_active_llm_providers(),
    }


@app.get("/api/v1/config", response_model=dict[str, Any])
async def get_config() -> dict[str, Any]:
    """
    開発環境向け設定エンドポイント
    本番環境では空レスポンスを返す
    """
    # 本番環境では設定を表示しない
    if settings.is_production():
        return {"error": "Config endpoint is only available in development mode"}

    # 開発環境では安全な設定情報を返す
    return {
        "environment": settings.app_env,
        "database": {
            "type": "sqlite" if settings.is_development() else "turso",
            "pool_size": settings.database_pool_size,
            "echo": settings.database_echo,
        },
        "redis": {
            "host": settings.redis_host,
            "port": settings.redis_port,
            "db": settings.redis_db,
            "has_password": bool(settings.redis_password),
        },
        "llm_providers": {
            "active": settings.get_active_llm_providers(),
            "default_model": settings.litellm_default_model,
            "fallback_models": settings.litellm_fallback_models,
        },
        "features": {
            "evaluation_enabled": settings.evaluation_enabled,
            "cache_enabled": settings.cache_enabled,
            "event_streaming_enabled": settings.event_streaming_enabled,
        },
    }


# イベントハンドラー
@app.on_event("startup")
async def startup_event() -> None:
    """
    アプリケーション起動時の処理
    """
    print(f"🚀 {settings.app_name} starting...")
    print(f"📍 Environment: {settings.app_env}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🌐 API URL: http://{settings.host}:{settings.port}")

    # アクティブなLLMプロバイダーを表示
    providers = settings.get_active_llm_providers()
    if providers:
        print(f"🤖 Active LLM providers: {', '.join(providers)}")
    else:
        print("⚠️  No LLM providers configured")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    アプリケーション終了時の処理
    """
    print(f"👋 {settings.app_name} shutting down...")
