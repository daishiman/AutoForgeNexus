"""
設定管理モジュール
環境変数の階層的読み込みと型安全な設定を提供
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# プロジェクトルートとバックエンドディレクトリのパス
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
BACKEND_DIR = Path(__file__).parent.parent.parent.parent


class EnvironmentLoader:
    """環境変数ファイルの階層的読み込み"""

    @staticmethod
    def load_env_files() -> None:
        """
        環境変数ファイルを階層的に読み込む
        1. 共通設定 (.env.common)
        2. 環境別設定 (.env.local, .env.staging, .env.production)
        3. ローカル上書き (.env.local)
        """
        env = os.getenv("APP_ENV", "local")

        # 読み込むファイルのリスト（後のファイルが前のファイルを上書き）
        env_files = [
            PROJECT_ROOT / ".env.common",  # 共通設定
            BACKEND_DIR / f".env.{env}",  # 環境別設定
            BACKEND_DIR / ".env.local",  # ローカル上書き
        ]

        for env_file in env_files:
            if env_file.exists():
                load_dotenv(env_file, override=True)
                print(f"✅ Loaded: {env_file}")


# 環境変数ファイルを読み込み（テスト時はスキップ）
if "pytest" not in sys.modules:
    EnvironmentLoader.load_env_files()


class Settings(BaseSettings):
    """
    アプリケーション設定
    Pydanticによる型安全な設定管理
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        json_schema_mode_override="validation",
    )

    # === Application Settings ===
    app_name: str = Field(default="AutoForgeNexus-Backend")
    app_env: str = Field(default="local")
    debug: bool = Field(default=True)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # === Database Settings ===
    database_url: str | None = Field(default=None)
    database_pool_size: int = Field(default=10)
    database_pool_timeout: int = Field(default=30)
    database_pool_recycle: int = Field(default=1800)
    database_echo: bool = Field(default=False)

    # === Cache Settings (Redis) ===
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: str | None = Field(default=None)
    redis_pool_size: int = Field(default=10)
    cache_ttl: int = Field(default=3600)
    cache_enabled: bool = Field(default=True)

    # === Authentication Settings ===
    clerk_publishable_key: str | None = Field(default=None)
    clerk_secret_key: str | None = Field(default=None)
    auth_enabled: bool = Field(default=True)

    # === LLM Provider API Keys ===
    openai_api_key: str | None = Field(default=None)
    anthropic_api_key: str | None = Field(default=None)
    google_ai_api_key: str | None = Field(default=None)
    cohere_api_key: str | None = Field(default=None)

    # === LiteLLM Settings ===
    litellm_default_model: str = Field(default="gpt-4")
    litellm_fallback_models: str = Field(default="claude-3-opus,gpt-4-turbo")
    litellm_max_retries: int = Field(default=3)
    litellm_timeout: int = Field(default=60)
    litellm_stream: bool = Field(default=True)

    # === Feature Flags ===
    evaluation_enabled: bool = Field(default=True)
    versioning_enabled: bool = Field(default=True)
    event_streaming_enabled: bool = Field(default=True)
    multi_tenant_enabled: bool = Field(default=False)

    # === Monitoring Settings ===
    langfuse_public_key: str | None = Field(default=None)
    langfuse_secret_key: str | None = Field(default=None)
    langfuse_host: str = Field(default="https://cloud.langfuse.com")
    sentry_dsn: str | None = Field(default=None)

    # === CORS Settings ===
    cors_allow_origins: str | list[str] = Field(default="http://localhost:3000")
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: str | list[str] = Field(
        default="GET,POST,PUT,DELETE,PATCH,OPTIONS"
    )
    cors_allow_headers: str | list[str] = Field(default="*")

    # === Rate Limiting ===
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=60)
    rate_limit_period: int = Field(default=60)

    @field_validator("app_env")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """環境名のバリデーション"""
        valid_envs = ["local", "development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"app_env must be one of {valid_envs}")
        return v

    @field_validator("litellm_fallback_models")
    @classmethod
    def parse_fallback_models(cls, v: str) -> list[str]:
        """フォールバックモデルをリストに変換"""
        if isinstance(v, str):
            return [model.strip() for model in v.split(",") if model.strip()]
        return v

    @field_validator("cors_allow_origins")
    @classmethod
    def parse_cors_origins(cls, v) -> list[str]:
        """CORS許可オリジンをリストに変換"""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return ["*"]

    @field_validator("cors_allow_methods")
    @classmethod
    def parse_cors_methods(cls, v) -> list[str]:
        """CORS許可メソッドをリストに変換"""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [method.strip() for method in v.split(",") if method.strip()]
        if isinstance(v, list):
            return v
        return ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

    @field_validator("cors_allow_headers")
    @classmethod
    def parse_cors_headers(cls, v) -> list[str]:
        """CORS許可ヘッダーをリストに変換"""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [header.strip() for header in v.split(",") if header.strip()]
        if isinstance(v, list):
            return v
        return ["*"]

    def get_redis_url(self) -> str:
        """Redis接続URLを生成"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def get_database_url(self) -> str:
        """データベース接続URLを取得"""
        if self.database_url:
            return self.database_url

        # ローカル環境ではSQLiteを使用
        if self.app_env == "local":
            db_path = BACKEND_DIR / "data" / "local.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_path}"

        # それ以外は環境変数から取得
        return os.getenv("DATABASE_URL", "")

    def is_production(self) -> bool:
        """本番環境かどうか"""
        return self.app_env == "production"

    def is_development(self) -> bool:
        """開発環境かどうか"""
        return self.app_env in ["local", "development"]

    def get_active_llm_providers(self) -> list[str]:
        """設定済みのLLMプロバイダーリストを取得"""
        providers = []
        if self.openai_api_key:
            providers.append("openai")
        if self.anthropic_api_key:
            providers.append("anthropic")
        if self.google_ai_api_key:
            providers.append("google")
        if self.cohere_api_key:
            providers.append("cohere")
        return providers
