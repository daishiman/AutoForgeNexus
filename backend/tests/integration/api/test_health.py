"""
ヘルスチェックエンドポイントの統合テスト
"""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """ヘルスチェックエンドポイントのテストクラス"""

    def test_health_check_returns_200(self) -> None:
        """ヘルスチェックが200を返すこと"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_response_structure(self) -> None:
        """ヘルスチェックレスポンスの構造が正しいこと"""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert data["status"] == "healthy"

    def test_readiness_check_returns_200(self) -> None:
        """Readinessチェックが200を返すこと"""
        response = client.get("/readiness")
        assert response.status_code == 200

    def test_readiness_check_response_structure(self) -> None:
        """Readinessチェックレスポンスの構造が正しいこと"""
        response = client.get("/readiness")
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert "checks" in data
        assert data["status"] == "ready"

    def test_readiness_check_includes_process_check(self) -> None:
        """Readinessチェックがプロセスチェックを含むこと"""
        response = client.get("/readiness")
        data = response.json()

        assert "checks" in data
        assert "process" in data["checks"]
        assert data["checks"]["process"] == "ok"

    def test_root_endpoint_returns_api_info(self) -> None:
        """ルートエンドポイントがAPI情報を返すこと"""
        response = client.get("/")
        data = response.json()

        # 既存のルートエンドポイントまたは health.py のルートエンドポイント
        assert response.status_code == 200
        assert isinstance(data, dict)

    def test_health_check_is_fast(self) -> None:
        """ヘルスチェックが高速であること（< 100ms）"""
        import time

        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.1  # 100ms未満

    def test_multiple_health_checks_are_consistent(self) -> None:
        """複数回のヘルスチェックが一貫した結果を返すこと"""
        responses = [client.get("/health") for _ in range(5)]

        # すべて200を返す
        assert all(r.status_code == 200 for r in responses)

        # すべてhealthyステータス
        assert all(r.json()["status"] == "healthy" for r in responses)
