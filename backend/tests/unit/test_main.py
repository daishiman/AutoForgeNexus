"""
メインアプリケーションのテスト
TDD: Red → Green → Refactor サイクル
"""

import pytest
from fastapi import status


class TestHealthCheck:
    """ヘルスチェックエンドポイントのテスト"""

    def test_root_endpoint_returns_healthy_status(self, client):
        """
        ルートエンドポイントが正常なステータスを返すことを確認
        """
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "environment" in data

    def test_root_endpoint_includes_debug_flag(self, client):
        """
        ルートエンドポイントがdebugフラグを含むことを確認
        """
        # Act
        response = client.get("/")

        # Assert
        data = response.json()
        assert "debug" in data
        assert isinstance(data["debug"], bool)

    def test_root_endpoint_includes_active_providers(self, client):
        """
        ルートエンドポイントがアクティブなLLMプロバイダーを含むことを確認
        """
        # Act
        response = client.get("/")

        # Assert
        data = response.json()
        assert "active_providers" in data
        assert isinstance(data["active_providers"], list)


class TestConfigEndpoint:
    """設定エンドポイントのテスト"""

    def test_config_endpoint_available_in_development(self, client, mock_settings):
        """
        開発環境では設定エンドポイントが利用可能であることを確認
        """
        # Arrange
        mock_settings(app_env="local")

        # Act
        response = client.get("/api/v1/config")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "environment" in data
        assert "database" in data
        assert "redis" in data
        assert "llm_providers" in data
        assert "features" in data

    @pytest.mark.xfail(reason="Production環境の設定が未実装")
    def test_config_endpoint_blocked_in_production(self, client, mock_settings):
        """
        本番環境では設定エンドポイントがブロックされることを確認
        """
        # Arrange
        mock_settings(app_env="production")

        # Act
        response = client.get("/api/v1/config")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "error" in data
        assert "development mode" in data["error"]


class TestCORSMiddleware:
    """CORSミドルウェアのテスト"""

    def test_cors_headers_present_in_response(self, client):
        """
        CORSヘッダーがレスポンスに含まれることを確認
        """
        # Act
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_configured_origins(self, client):
        """
        設定されたオリジンからのリクエストが許可されることを確認
        """
        # Act
        response = client.get("/", headers={"Origin": "http://localhost:3000"})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert (
            response.headers.get("access-control-allow-origin")
            == "http://localhost:3000"
        )
