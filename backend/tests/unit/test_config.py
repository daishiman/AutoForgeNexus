"""
設定管理のテスト
環境変数の階層的読み込みを確認
"""

from unittest.mock import patch

import pytest


class TestSettings:
    """設定クラスのテスト"""

    def test_settings_loads_default_values(self):
        """
        デフォルト値が正しく読み込まれることを確認
        """
        from src.core.config.settings import Settings

        # Act
        settings = Settings()

        # Assert
        assert settings.app_name == "AutoForgeNexus-Backend"
        assert settings.app_env == "local"
        assert settings.port == 8000
        assert settings.host == "0.0.0.0"

    def test_settings_loads_from_environment_variables(self, monkeypatch):
        """
        環境変数から設定が読み込まれることを確認
        """
        # Arrange
        monkeypatch.setenv("APP_ENV", "staging")
        monkeypatch.setenv("PORT", "9000")
        monkeypatch.setenv("DEBUG", "true")

        from src.core.config.settings import Settings

        # Act
        settings = Settings()

        # Assert
        assert settings.app_env == "staging"
        assert settings.port == 9000
        assert settings.debug is True

    def test_settings_validates_environment_name(self):
        """
        不正な環境名が検証されることを確認
        """
        from pydantic import ValidationError

        from src.core.config.settings import Settings

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            Settings(app_env="invalid_env")

        assert "app_env" in str(exc_info.value)

    def test_settings_parses_fallback_models(self):
        """
        フォールバックモデルがカンマ区切りで解析されることを確認
        """
        from src.core.config.settings import Settings

        # Arrange & Act
        settings = Settings(litellm_fallback_models="gpt-4,claude-3,gemini-pro")

        # Assert
        assert settings.litellm_fallback_models == ["gpt-4", "claude-3", "gemini-pro"]

    def test_settings_parses_cors_origins(self):
        """
        CORS設定が正しく解析されることを確認
        """
        from src.core.config.settings import Settings

        # Test wildcard
        settings = Settings(cors_allow_origins="*")
        assert settings.cors_allow_origins == ["*"]

        # Test multiple origins
        settings = Settings(
            cors_allow_origins="http://localhost:3000,https://app.example.com"
        )
        assert settings.cors_allow_origins == [
            "http://localhost:3000",
            "https://app.example.com",
        ]

    def test_get_redis_url_with_password(self):
        """
        パスワード付きRedis URLが正しく構築されることを確認
        """
        from src.core.config.settings import Settings

        # Arrange
        settings = Settings(
            redis_host="redis.example.com",
            redis_port=6380,
            redis_password="secret123",
            redis_db=1,
        )

        # Act
        url = settings.get_redis_url()

        # Assert
        assert url == "redis://:secret123@redis.example.com:6380/1"

    def test_get_redis_url_without_password(self):
        """
        パスワードなしRedis URLが正しく構築されることを確認
        """
        from src.core.config.settings import Settings

        # Arrange
        settings = Settings(redis_host="localhost", redis_port=6379, redis_db=0)

        # Act
        url = settings.get_redis_url()

        # Assert
        assert url == "redis://localhost:6379/0"

    def test_get_database_url_for_local_environment(self):
        """
        ローカル環境でSQLiteが使用されることを確認
        """
        from src.core.config.settings import Settings

        # Arrange
        settings = Settings(app_env="local")

        # Act
        db_url = settings.get_database_url()

        # Assert
        assert db_url.startswith("sqlite://")

    def test_is_production_returns_true_for_production(self):
        """
        本番環境判定が正しく動作することを確認
        """
        from src.core.config.settings import Settings

        # Arrange & Act
        settings = Settings(app_env="production")

        # Assert
        assert settings.is_production() is True
        assert settings.is_development() is False

    def test_is_development_returns_true_for_local(self):
        """
        開発環境判定が正しく動作することを確認
        """
        from src.core.config.settings import Settings

        # Arrange & Act
        settings = Settings(app_env="local")

        # Assert
        assert settings.is_development() is True
        assert settings.is_production() is False

    def test_get_active_llm_providers(self):
        """
        アクティブなLLMプロバイダーが正しく取得されることを確認
        """
        from src.core.config.settings import Settings

        # Arrange
        settings = Settings(
            openai_api_key="sk-test-123",
            anthropic_api_key="sk-ant-456",
            google_ai_api_key=None,
        )

        # Act
        providers = settings.get_active_llm_providers()

        # Assert
        assert "openai" in providers
        assert "anthropic" in providers
        assert "google" not in providers


class TestEnvironmentLoader:
    """環境変数ローダーのテスト"""

    @patch("src.core.config.settings.load_dotenv")
    @patch("src.core.config.settings.Path.exists")
    def test_load_env_files_in_correct_order(self, mock_exists, mock_load_dotenv):
        """
        環境変数ファイルが正しい順序で読み込まれることを確認
        """
        from src.core.config.settings import EnvironmentLoader

        # Arrange
        mock_exists.return_value = True

        # Act
        EnvironmentLoader.load_env_files()

        # Assert
        assert mock_load_dotenv.call_count == 3
        # 呼び出し順序を確認
        calls = mock_load_dotenv.call_args_list
        assert ".env.common" in str(calls[0])
        assert ".env.local" in str(calls[1])  # 環境別
        assert ".env.local" in str(calls[2])  # ローカル上書き
