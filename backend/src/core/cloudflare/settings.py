"""
Cloudflare Workers Python用設定管理モジュール

pydantic-settingsの代替として、os.environから直接環境変数を読み込みます。
Pyodide環境で完全動作し、pydanticのみを使用します。

使用例:
    from src.core.cloudflare.settings import settings

    # 環境変数から自動読み込み
    print(settings.app_name)  # "AutoForgeNexus"
    print(settings.clerk_secret_key)  # wrangler secretで設定

    # 型安全アクセス
    if settings.debug:
        print("Debug mode enabled")
"""

import os
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Settings(BaseModel):
    """
    Cloudflare Workers環境変数から設定を読み込む

    環境変数の設定方法:
        1. 公開変数: wrangler.toml の [env.*.vars]
        2. シークレット: wrangler secret put <key> --env <env>

    Examples:
        # wrangler.toml
        [env.production.vars]
        APP_NAME = "AutoForgeNexus"
        DEBUG = "false"
        LOG_LEVEL = "WARNING"

        # wrangler secret
        wrangler secret put CLERK_SECRET_KEY --env production
        wrangler secret put OPENAI_API_KEY --env production
    """

    # ==========================================
    # アプリケーション基本設定
    # ==========================================

    app_name: str = Field(
        default_factory=lambda: os.environ.get("APP_NAME", "AutoForgeNexus"),
        description="アプリケーション名",
    )

    environment: Literal["development", "develop", "staging", "production"] = Field(
        default_factory=lambda: os.environ.get("ENVIRONMENT", "development"),
        description="実行環境",
    )

    debug: bool = Field(
        default_factory=lambda: os.environ.get("DEBUG", "false").lower() == "true",
        description="デバッグモード",
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"),
        description="ログレベル",
    )

    # ==========================================
    # CORS設定
    # ==========================================

    cors_allow_origins: list[str] = Field(
        default_factory=lambda: os.environ.get(
            "CORS_ALLOW_ORIGINS", "http://localhost:3000"
        ).split(","),
        description="CORS許可オリジン",
    )

    # ==========================================
    # 認証設定（Clerk）
    # ==========================================

    clerk_secret_key: str = Field(
        default_factory=lambda: os.environ.get("CLERK_SECRET_KEY", ""),
        description="Clerk Secret Key（wrangler secretで設定）",
    )

    clerk_jwks_url: str = Field(
        default_factory=lambda: os.environ.get(
            "CLERK_JWKS_URL", "https://clerk.autoforgenexus.com/.well-known/jwks.json"
        ),
        description="Clerk JWKS URL",
    )

    # ==========================================
    # LLMプロバイダーAPI Keys
    # ==========================================

    openai_api_key: str = Field(
        default_factory=lambda: os.environ.get("OPENAI_API_KEY", ""),
        description="OpenAI API Key（wrangler secretで設定）",
    )

    anthropic_api_key: str = Field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", ""),
        description="Anthropic API Key（wrangler secretで設定）",
    )

    cohere_api_key: str = Field(
        default_factory=lambda: os.environ.get("COHERE_API_KEY", ""),
        description="Cohere API Key（オプション）",
    )

    google_api_key: str = Field(
        default_factory=lambda: os.environ.get("GOOGLE_API_KEY", ""),
        description="Google Gemini API Key（オプション）",
    )

    # ==========================================
    # データベース設定
    # ==========================================

    turso_database_url: str = Field(
        default_factory=lambda: os.environ.get("TURSO_DATABASE_URL", ""),
        description="Turso Database URL（wrangler secretで設定）",
    )

    turso_auth_token: str = Field(
        default_factory=lambda: os.environ.get("TURSO_AUTH_TOKEN", ""),
        description="Turso Auth Token（wrangler secretで設定）",
    )

    redis_rest_url: str = Field(
        default_factory=lambda: os.environ.get("REDIS_REST_URL", ""),
        description="Redis REST URL（Upstash）",
    )

    redis_rest_token: str = Field(
        default_factory=lambda: os.environ.get("REDIS_REST_TOKEN", ""),
        description="Redis REST Token（Upstash）",
    )

    # ==========================================
    # 観測性設定（オプション）
    # ==========================================

    langfuse_public_key: str = Field(
        default_factory=lambda: os.environ.get("LANGFUSE_PUBLIC_KEY", ""),
        description="LangFuse Public Key（オプション、開発環境のみ）",
    )

    langfuse_secret_key: str = Field(
        default_factory=lambda: os.environ.get("LANGFUSE_SECRET_KEY", ""),
        description="LangFuse Secret Key（オプション、開発環境のみ）",
    )

    # ==========================================
    # パフォーマンス設定
    # ==========================================

    http_timeout: float = Field(
        default_factory=lambda: float(os.environ.get("HTTP_TIMEOUT", "30.0")),
        description="HTTP リクエストタイムアウト（秒）",
    )

    max_retries: int = Field(
        default_factory=lambda: int(os.environ.get("MAX_RETRIES", "3")),
        description="API呼び出し最大リトライ回数",
    )

    # ==========================================
    # バリデーション
    # ==========================================

    @field_validator("clerk_secret_key", "openai_api_key", "turso_database_url")
    @classmethod
    def validate_required_secrets(cls, v: str, info) -> str:
        """本番環境で必須シークレットをバリデーション"""

        # 開発環境ではスキップ
        environment = os.environ.get("ENVIRONMENT", "development")
        if environment == "development":
            return v

        if not v:
            raise ValueError(
                f"{info.field_name} is required in {environment} environment. "
                f"Set via 'wrangler secret put {info.field_name.upper()}'"
            )

        return v

    @field_validator("cors_allow_origins")
    @classmethod
    def validate_cors_origins(cls, v: list[str]) -> list[str]:
        """CORS設定のバリデーション"""

        if not v:
            return ["*"]

        # "*"が含まれる場合は単独で使用
        if "*" in v and len(v) > 1:
            raise ValueError("CORS_ALLOW_ORIGINS: '*' must be used alone")

        return v

    # ==========================================
    # ユーティリティメソッド
    # ==========================================

    @property
    def is_production(self) -> bool:
        """本番環境かどうか"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """開発環境かどうか"""
        return self.environment == "development"

    def get_llm_api_key(self, provider: str) -> str:
        """
        プロバイダー名からAPI Keyを取得

        Args:
            provider: プロバイダー名（openai, anthropic, cohere, google）

        Returns:
            API Key

        Raises:
            ValueError: プロバイダーが不正、またはAPI Keyが未設定
        """

        provider_map = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "cohere": self.cohere_api_key,
            "google": self.google_api_key,
        }

        if provider not in provider_map:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Supported: {', '.join(provider_map.keys())}"
            )

        api_key = provider_map[provider]
        if not api_key:
            raise ValueError(
                f"{provider.upper()}_API_KEY is not set. "
                f"Set via 'wrangler secret put {provider.upper()}_API_KEY'"
            )

        return api_key

    class Config:
        frozen = True  # Immutable（設定変更不可）
        validate_assignment = True


# グローバルシングルトン
settings = Settings()


# 設定の整合性チェック（起動時に実行推奨）
def validate_settings() -> None:
    """
    設定の整合性を検証

    Raises:
        ValueError: 設定が不正
    """

    errors: list[str] = []

    # 本番環境での必須設定チェック
    if settings.is_production:
        if not settings.clerk_secret_key:
            errors.append("CLERK_SECRET_KEY is required in production")
        if not settings.openai_api_key:
            errors.append("OPENAI_API_KEY is required in production")
        if not settings.turso_database_url:
            errors.append("TURSO_DATABASE_URL is required in production")
        if not settings.turso_auth_token:
            errors.append("TURSO_AUTH_TOKEN is required in production")

    # CORS設定チェック
    if settings.is_production and "*" in settings.cors_allow_origins:
        errors.append(
            "CORS_ALLOW_ORIGINS='*' is not allowed in production. "
            "Specify allowed origins explicitly."
        )

    if errors:
        raise ValueError(
            "Settings validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        )
