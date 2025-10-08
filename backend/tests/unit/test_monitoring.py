"""
監視・ヘルスチェックシステムのテスト
observability-engineer による包括的テストスイート
"""

import time
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest


class TestSystemMetrics:
    """SystemMetricsデータクラスのテスト"""

    def test_システムメトリクスが正しく初期化される(self):
        """
        SystemMetricsが期待されるフィールドで初期化されることを確認
        """
        # Arrange & Act
        from src.monitoring import SystemMetrics

        metrics = SystemMetrics(
            cpu_percent=25.5,
            memory_percent=60.2,
            disk_percent=45.8,
            load_average=[1.5, 1.8, 2.0],
            uptime_seconds=3600.0,
            process_count=150,
        )

        # Assert
        assert metrics.cpu_percent == 25.5
        assert metrics.memory_percent == 60.2
        assert metrics.disk_percent == 45.8
        assert metrics.load_average == [1.5, 1.8, 2.0]
        assert metrics.uptime_seconds == 3600.0
        assert metrics.process_count == 150

    def test_システムメトリクスが辞書に変換される(self):
        """
        to_dict()メソッドが正しく辞書を返すことを確認
        """
        # Arrange
        from src.monitoring import SystemMetrics

        metrics = SystemMetrics(
            cpu_percent=10.0,
            memory_percent=20.0,
            disk_percent=30.0,
            load_average=None,
            uptime_seconds=1000.0,
            process_count=50,
        )

        # Act
        result = metrics.to_dict()

        # Assert
        assert isinstance(result, dict)
        assert result["cpu_percent"] == 10.0
        assert result["memory_percent"] == 20.0
        assert result["disk_percent"] == 30.0
        assert result["load_average"] is None
        assert result["uptime_seconds"] == 1000.0
        assert result["process_count"] == 50


class TestDependencyHealth:
    """DependencyHealthデータクラスのテスト"""

    def test_依存サービス状態が正しく初期化される(self):
        """
        DependencyHealthが必須フィールドで初期化されることを確認
        """
        # Arrange & Act
        from src.monitoring import DependencyHealth, HealthStatus

        dep = DependencyHealth(
            name="database",
            status=HealthStatus.HEALTHY,
            response_time_ms=15.5,
        )

        # Assert
        assert dep.name == "database"
        assert dep.status == HealthStatus.HEALTHY
        assert dep.response_time_ms == 15.5
        assert dep.version is None
        assert dep.error is None
        assert dep.metadata is None

    def test_依存サービス状態がオプションフィールド付きで初期化される(self):
        """
        DependencyHealthがオプションフィールド含めて初期化されることを確認
        """
        # Arrange & Act
        from src.monitoring import DependencyHealth, HealthStatus

        dep = DependencyHealth(
            name="redis",
            status=HealthStatus.HEALTHY,
            response_time_ms=8.2,
            version="7.4.1",
            metadata={"connected_clients": 5},
        )

        # Assert
        assert dep.version == "7.4.1"
        assert dep.metadata == {"connected_clients": 5}

    def test_依存サービス状態が辞書に変換される(self):
        """
        to_dict()メソッドが正しく辞書を返すことを確認
        """
        # Arrange
        from src.monitoring import DependencyHealth, HealthStatus

        dep = DependencyHealth(
            name="langfuse",
            status=HealthStatus.DEGRADED,
            response_time_ms=250.0,
            error="Connection timeout",
        )

        # Act
        result = dep.to_dict()

        # Assert
        assert isinstance(result, dict)
        assert result["name"] == "langfuse"
        assert result["status"] == HealthStatus.DEGRADED
        assert result["response_time_ms"] == 250.0
        assert result["error"] == "Connection timeout"


class TestHealthCheckResponse:
    """HealthCheckResponseデータクラスのテスト"""

    def test_ヘルスチェックレスポンスが正しく初期化される(self):
        """
        HealthCheckResponseが必須フィールドで初期化されることを確認
        """
        # Arrange
        from src.monitoring import (
            DependencyHealth,
            HealthCheckResponse,
            HealthStatus,
            SystemMetrics,
        )

        system = SystemMetrics(
            cpu_percent=15.0,
            memory_percent=40.0,
            disk_percent=50.0,
            load_average=[1.0, 1.2, 1.5],
            uptime_seconds=7200.0,
            process_count=100,
        )

        dependencies = [
            DependencyHealth(
                name="database", status=HealthStatus.HEALTHY, response_time_ms=10.0
            ),
        ]

        # Act
        response = HealthCheckResponse(
            service="TestService",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now(UTC).isoformat(),
            environment="test",
            version="1.0.0",
            uptime_seconds=3600.0,
            system=system,
            dependencies=dependencies,
            checks={"database": True},
        )

        # Assert
        assert response.service == "TestService"
        assert response.status == HealthStatus.HEALTHY
        assert response.environment == "test"
        assert response.version == "1.0.0"
        assert response.uptime_seconds == 3600.0
        assert len(response.dependencies) == 1

    def test_ヘルスチェックレスポンスが辞書に変換される(self):
        """
        to_dict()メソッドがネストした構造を正しく変換することを確認
        """
        # Arrange
        from src.monitoring import (
            DependencyHealth,
            HealthCheckResponse,
            HealthStatus,
            SystemMetrics,
        )

        system = SystemMetrics(
            cpu_percent=20.0,
            memory_percent=50.0,
            disk_percent=60.0,
            load_average=None,
            uptime_seconds=1000.0,
            process_count=75,
        )

        dependencies = [
            DependencyHealth(
                name="redis", status=HealthStatus.HEALTHY, response_time_ms=5.0
            ),
        ]

        response = HealthCheckResponse(
            service="TestService",
            status=HealthStatus.HEALTHY,
            timestamp="2025-09-30T10:00:00Z",
            environment="test",
            version="1.0.0",
            uptime_seconds=1000.0,
            system=system,
            dependencies=dependencies,
            checks={"redis": True},
        )

        # Act
        result = response.to_dict()

        # Assert
        assert isinstance(result, dict)
        assert isinstance(result["system"], dict)
        assert isinstance(result["dependencies"], list)
        assert len(result["dependencies"]) == 1
        assert isinstance(result["dependencies"][0], dict)
        assert result["dependencies"][0]["name"] == "redis"


class TestHealthChecker:
    """HealthCheckerクラスのテスト"""

    @pytest.fixture
    def health_checker(self, monkeypatch):
        """HealthCheckerのフィクスチャ"""
        # 環境変数を設定
        monkeypatch.setenv("APP_VERSION", "1.0.0")
        monkeypatch.setenv("ENVIRONMENT", "test")

        from src.monitoring import HealthChecker

        return HealthChecker()

    def test_ヘルスチェッカーが正しく初期化される(self, health_checker):
        """
        HealthCheckerが環境変数を読み込んで初期化されることを確認
        """
        # Assert
        assert health_checker.service_name == "AutoForgeNexus Backend"
        assert health_checker.version == "1.0.0"
        assert health_checker.environment == "test"
        assert health_checker.start_time > 0

    @patch("src.monitoring.psutil.cpu_percent")
    @patch("src.monitoring.psutil.virtual_memory")
    @patch("src.monitoring.psutil.disk_usage")
    @patch("src.monitoring.psutil.boot_time")
    @patch("src.monitoring.psutil.pids")
    @patch("src.monitoring.os.getloadavg")
    def test_システムメトリクスが正常に取得される(
        self,
        mock_getloadavg,
        mock_pids,
        mock_boot_time,
        mock_disk_usage,
        mock_virtual_memory,
        mock_cpu_percent,
        health_checker,
    ):
        """
        _get_system_metrics()がpsutilから正しくメトリクスを取得することを確認
        """
        # Arrange
        mock_cpu_percent.return_value = 30.0
        mock_virtual_memory.return_value = Mock(percent=50.0)
        mock_disk_usage.return_value = Mock(used=50 * 1024**3, total=100 * 1024**3)
        mock_boot_time.return_value = time.time() - 7200
        mock_pids.return_value = list(range(100))
        mock_getloadavg.return_value = (1.0, 1.5, 2.0)

        # Act
        metrics = health_checker._get_system_metrics()

        # Assert
        assert metrics.cpu_percent == 30.0
        assert metrics.memory_percent == 50.0
        assert abs(metrics.disk_percent - 50.0) < 1.0
        assert metrics.load_average == [1.0, 1.5, 2.0]
        assert metrics.process_count == 100

    @patch("src.monitoring.psutil.cpu_percent")
    def test_システムメトリクス取得でエラー時にフォールバック値が返される(
        self, mock_cpu_percent, health_checker
    ):
        """
        _get_system_metrics()でエラー発生時にフォールバックメトリクスが返されることを確認
        """
        # Arrange
        mock_cpu_percent.side_effect = Exception("psutil error")

        # Act
        metrics = health_checker._get_system_metrics()

        # Assert
        assert metrics.cpu_percent == 0.0
        assert metrics.memory_percent == 0.0
        assert metrics.disk_percent == 0.0
        assert metrics.load_average is None
        assert metrics.process_count == 0

    def test_フォールバックシステムメトリクスが返される(self, health_checker):
        """
        _get_fallback_system_metrics()がデフォルト値を返すことを確認
        """
        # Act
        metrics = health_checker._get_fallback_system_metrics()

        # Assert
        assert metrics.cpu_percent == 0.0
        assert metrics.memory_percent == 0.0
        assert metrics.disk_percent == 0.0
        assert metrics.load_average is None
        assert metrics.uptime_seconds >= 0
        assert metrics.process_count == 0


class TestMetricsCollector:
    """MetricsCollectorクラスのテスト"""

    @pytest.fixture
    def metrics_collector(self):
        """MetricsCollectorのフィクスチャ"""
        from src.monitoring import MetricsCollector

        return MetricsCollector()

    def test_メトリクスコレクターが正しく初期化される(self, metrics_collector):
        """
        MetricsCollectorが初期化されることを確認
        """
        # Assert
        assert isinstance(metrics_collector.metrics, dict)
        assert metrics_collector.start_time > 0

    @patch("src.monitoring.logger")
    def test_リクエストメトリクスが記録される(self, mock_logger, metrics_collector):
        """
        record_request_metrics()がログに記録することを確認
        """
        # Act
        metrics_collector.record_request_metrics(
            method="GET", endpoint="/health", status_code=200, duration=0.05
        )

        # Assert
        mock_logger.info.assert_called_once()
        args, kwargs = mock_logger.info.call_args
        assert args[0] == "Request metric"
        assert "metric" in kwargs["extra"]
        metric = kwargs["extra"]["metric"]
        assert metric["method"] == "GET"
        assert metric["endpoint"] == "/health"
        assert metric["status_code"] == 200
        assert metric["duration_ms"] == 50.0

    @patch("src.monitoring.logger")
    def test_LLMメトリクスが記録される(self, mock_logger, metrics_collector):
        """
        record_llm_metrics()がログに記録することを確認
        """
        # Act
        metrics_collector.record_llm_metrics(
            provider="openai",
            model="gpt-4",
            tokens_used=1500,
            cost=0.045,
            duration=2.5,
        )

        # Assert
        mock_logger.info.assert_called_once()
        args, kwargs = mock_logger.info.call_args
        assert args[0] == "LLM metric"
        assert "metric" in kwargs["extra"]
        metric = kwargs["extra"]["metric"]
        assert metric["provider"] == "openai"
        assert metric["model"] == "gpt-4"
        assert metric["tokens_used"] == 1500
        assert metric["cost_usd"] == 0.045
        assert metric["duration_ms"] == 2500.0

    @patch("src.monitoring.logger")
    def test_エラーメトリクスが記録される(self, mock_logger, metrics_collector):
        """
        record_error_metrics()がエラーログに記録することを確認
        """
        # Act
        metrics_collector.record_error_metrics(
            error_type="ValueError",
            error_message="Invalid input",
            stack_trace="Traceback...",
        )

        # Assert
        mock_logger.error.assert_called_once()
        args, kwargs = mock_logger.error.call_args
        assert args[0] == "Error metric"
        assert "metric" in kwargs["extra"]
        metric = kwargs["extra"]["metric"]
        assert metric["error_type"] == "ValueError"
        assert metric["error_message"] == "Invalid input"
        assert metric["stack_trace"] == "Traceback..."


class TestHealthCheckerDependencies:
    """HealthChecker依存サービスチェックのテスト"""

    @pytest.fixture
    def health_checker(self, monkeypatch):
        """HealthCheckerのフィクスチャ"""
        monkeypatch.setenv("APP_VERSION", "1.0.0")
        monkeypatch.setenv("ENVIRONMENT", "test")

        from src.monitoring import HealthChecker

        return HealthChecker()

    @pytest.mark.skip(reason="infrastructure.database モジュールが未実装のためスキップ")
    @pytest.mark.asyncio
    async def test_データベースチェックが成功する(self, health_checker, monkeypatch):
        """
        _check_database()がデータベース接続成功時にHEALTHYを返すことを確認
        """
        # Arrange
        monkeypatch.setenv("TURSO_DATABASE_URL", "libsql://test@test.turso.io")

        mock_result = AsyncMock()
        mock_result.fetchone = AsyncMock(return_value=(1,))

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        async def mock_get_session():
            return mock_session

        with patch(
            "src.infrastructure.database.get_database_session",
            return_value=mock_session,
        ):
            # Act
            result = await health_checker._check_database()

            # Assert
            from src.monitoring import HealthStatus

            assert result.name == "database"
            assert result.status == HealthStatus.HEALTHY
            assert result.response_time_ms > 0
            assert result.version == "turso"
            # 🔐 セキュリティ改善: 部分一致 → 完全一致検証（CodeQL Alert #5対応）
            # CWE-20対策: URL substring sanitization の脆弱性を排除
            # 変更前: assert "test.turso.io" in result.metadata["database_url"]
            # 変更理由: 部分一致は攻撃者がホスト名を任意位置に埋め込む攻撃を許す
            expected_hostname = "test.turso.io"
            actual_hostname = result.metadata["database_url"]
            assert (
                actual_hostname == expected_hostname
            ), f"Expected exact hostname match '{expected_hostname}', got '{actual_hostname}'"

    @pytest.mark.skip(reason="infrastructure.database モジュールが未実装のためスキップ")
    @pytest.mark.asyncio
    async def test_データベースチェックが失敗する(self, health_checker):
        """
        _check_database()がデータベース接続失敗時にUNHEALTHYを返すことを確認
        """
        # Arrange
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=Exception("Connection failed"))
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "src.infrastructure.database.get_database_session",
            return_value=mock_session,
        ):
            # Act
            result = await health_checker._check_database()

            # Assert
            from src.monitoring import HealthStatus

            assert result.name == "database"
            assert result.status == HealthStatus.UNHEALTHY
            assert result.error == "Connection failed"

    @pytest.mark.asyncio
    async def test_Redisチェックが成功する(self, health_checker, monkeypatch):
        """
        _check_redis()がRedis接続成功時にHEALTHYを返すことを確認
        """
        # Arrange
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.info = AsyncMock(
            return_value={
                "redis_version": "7.4.1",
                "connected_clients": 5,
                "used_memory_human": "1.5M",
            }
        )
        mock_redis.aclose = AsyncMock()

        with patch("redis.asyncio.from_url", return_value=mock_redis):
            # Act
            result = await health_checker._check_redis()

            # Assert
            from src.monitoring import HealthStatus

            assert result.name == "redis"
            assert result.status == HealthStatus.HEALTHY
            assert result.version == "7.4.1"
            assert result.metadata["connected_clients"] == 5
            assert result.metadata["used_memory_human"] == "1.5M"

    @pytest.mark.asyncio
    async def test_Redisチェックが設定なしでUNHEALTHYを返す(
        self, health_checker, monkeypatch
    ):
        """
        _check_redis()がREDIS_URL未設定時にUNHEALTHYを返すことを確認
        """
        # Arrange
        monkeypatch.delenv("REDIS_URL", raising=False)

        # Act
        result = await health_checker._check_redis()

        # Assert
        from src.monitoring import HealthStatus

        assert result.name == "redis"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.error == "Redis URL not configured"

    @pytest.mark.asyncio
    async def test_LangFuseチェックが成功する(self, health_checker, monkeypatch):
        """
        _check_langfuse()がLangFuse接続成功時にHEALTHYを返すことを確認
        """
        # Arrange
        monkeypatch.setenv("LANGFUSE_HOST", "http://localhost:3002")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("src.monitoring.httpx.AsyncClient", return_value=mock_client):
            # Act
            result = await health_checker._check_langfuse()

            # Assert
            from src.monitoring import HealthStatus

            assert result.name == "langfuse"
            assert result.status == HealthStatus.HEALTHY
            assert result.response_time_ms > 0

    @pytest.mark.asyncio
    async def test_LangFuseチェックが設定なしでDEGRADEDを返す(
        self, health_checker, monkeypatch
    ):
        """
        _check_langfuse()がLANGFUSE_HOST未設定時にDEGRADEDを返すことを確認
        """
        # Arrange
        monkeypatch.delenv("LANGFUSE_HOST", raising=False)

        # Act
        result = await health_checker._check_langfuse()

        # Assert
        from src.monitoring import HealthStatus

        assert result.name == "langfuse"
        assert result.status == HealthStatus.DEGRADED
        assert result.error == "LangFuse host not configured"

    @pytest.mark.asyncio
    async def test_外部APIチェックが成功する(self, health_checker, monkeypatch):
        """
        _check_external_apis()がAPI接続成功時にHEALTHYを返すことを確認
        """
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")

        mock_response = Mock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("src.monitoring.httpx.AsyncClient", return_value=mock_client):
            # Act
            result = await health_checker._check_external_apis()

            # Assert
            from src.monitoring import HealthStatus

            assert result.name == "external_apis"
            assert result.status == HealthStatus.HEALTHY
            assert result.error is None

    @pytest.mark.asyncio
    async def test_外部APIチェックが認証エラーでDEGRADEDを返す(
        self, health_checker, monkeypatch
    ):
        """
        _check_external_apis()が認証失敗時にDEGRADEDを返すことを確認
        """
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "invalid-key")

        mock_response = Mock()
        mock_response.status_code = 401

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("src.monitoring.httpx.AsyncClient", return_value=mock_client):
            # Act
            result = await health_checker._check_external_apis()

            # Assert
            from src.monitoring import HealthStatus

            assert result.name == "external_apis"
            assert result.status == HealthStatus.DEGRADED
            assert result.error == "API key not configured or invalid"

    @pytest.mark.asyncio
    async def test_依存サービスチェックが並列実行される(self, health_checker):
        """
        _check_dependencies()が複数のチェックを並列実行することを確認
        """
        # Arrange
        from src.monitoring import DependencyHealth, HealthStatus

        mock_db = DependencyHealth(
            name="database", status=HealthStatus.HEALTHY, response_time_ms=10.0
        )
        mock_redis = DependencyHealth(
            name="redis", status=HealthStatus.HEALTHY, response_time_ms=5.0
        )
        mock_langfuse = DependencyHealth(
            name="langfuse", status=HealthStatus.DEGRADED, response_time_ms=50.0
        )
        mock_apis = DependencyHealth(
            name="external_apis", status=HealthStatus.HEALTHY, response_time_ms=100.0
        )

        with (
            patch.object(health_checker, "_check_database", return_value=mock_db),
            patch.object(health_checker, "_check_redis", return_value=mock_redis),
            patch.object(health_checker, "_check_langfuse", return_value=mock_langfuse),
            patch.object(
                health_checker, "_check_external_apis", return_value=mock_apis
            ),
        ):
            # Act
            dependencies = await health_checker._check_dependencies()

            # Assert
            assert len(dependencies) == 4
            assert any(dep.name == "database" for dep in dependencies)
            assert any(dep.name == "redis" for dep in dependencies)
            assert any(dep.name == "langfuse" for dep in dependencies)
            assert any(dep.name == "external_apis" for dep in dependencies)

    def test_全体ステータス判定でクリティカルな依存が不健全な場合UNHEALTHYになる(
        self, health_checker
    ):
        """
        _determine_overall_status()でデータベースがUNHEALTHYの場合、全体がUNHEALTHYになることを確認
        """
        # Arrange
        from src.monitoring import DependencyHealth, HealthStatus

        dependencies = [
            DependencyHealth(
                name="database", status=HealthStatus.UNHEALTHY, response_time_ms=0
            ),
            DependencyHealth(
                name="redis", status=HealthStatus.HEALTHY, response_time_ms=5.0
            ),
        ]

        # Act
        status = health_checker._determine_overall_status(dependencies)

        # Assert
        assert status == HealthStatus.UNHEALTHY

    def test_全体ステータス判定で一部が不健全な場合DEGRADEDになる(self, health_checker):
        """
        _determine_overall_status()で非クリティカルサービスがUNHEALTHYの場合、DEGRADEDになることを確認
        """
        # Arrange
        from src.monitoring import DependencyHealth, HealthStatus

        dependencies = [
            DependencyHealth(
                name="database", status=HealthStatus.HEALTHY, response_time_ms=10.0
            ),
            DependencyHealth(
                name="langfuse", status=HealthStatus.UNHEALTHY, response_time_ms=0
            ),
        ]

        # Act
        status = health_checker._determine_overall_status(dependencies)

        # Assert
        assert status == HealthStatus.DEGRADED

    def test_全体ステータス判定で全て健全な場合HEALTHYになる(self, health_checker):
        """
        _determine_overall_status()で全依存が健全な場合、HEALTHYになることを確認
        """
        # Arrange
        from src.monitoring import DependencyHealth, HealthStatus

        dependencies = [
            DependencyHealth(
                name="database", status=HealthStatus.HEALTHY, response_time_ms=10.0
            ),
            DependencyHealth(
                name="redis", status=HealthStatus.HEALTHY, response_time_ms=5.0
            ),
        ]

        # Act
        status = health_checker._determine_overall_status(dependencies)

        # Assert
        assert status == HealthStatus.HEALTHY


class TestEndpointFunctions:
    """エンドポイント関数のテスト"""

    @pytest.mark.asyncio
    async def test_get_healthが正常にヘルスチェックを返す(self):
        """
        get_health()がヘルスチェック結果を辞書で返すことを確認
        """
        # Arrange
        from src.monitoring import HealthCheckResponse, HealthStatus, SystemMetrics

        mock_response = HealthCheckResponse(
            service="TestService",
            status=HealthStatus.HEALTHY,
            timestamp="2025-09-30T10:00:00Z",
            environment="test",
            version="1.0.0",
            uptime_seconds=1000.0,
            system=SystemMetrics(
                cpu_percent=20.0,
                memory_percent=40.0,
                disk_percent=50.0,
                load_average=None,
                uptime_seconds=1000.0,
                process_count=100,
            ),
            dependencies=[],
            checks={},
        )

        with patch(
            "src.monitoring.health_checker.get_health_status",
            return_value=mock_response,
        ):
            from src.monitoring import get_health

            # Act
            result = await get_health()

            # Assert
            assert isinstance(result, dict)
            assert result["service"] == "TestService"
            assert result["status"] == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_get_metricsがシステムメトリクスを返す(self):
        """
        get_metrics()がシステムメトリクスを辞書で返すことを確認
        """
        # Arrange
        from src.monitoring import SystemMetrics

        mock_metrics = SystemMetrics(
            cpu_percent=15.0,
            memory_percent=35.0,
            disk_percent=45.0,
            load_average=[1.0, 1.2, 1.5],
            uptime_seconds=2000.0,
            process_count=120,
        )

        with (
            patch(
                "src.monitoring.health_checker._get_system_metrics",
                return_value=mock_metrics,
            ),
            patch("src.monitoring.health_checker.start_time", time.time() - 2000),
        ):
            from src.monitoring import get_metrics

            # Act
            result = await get_metrics()

            # Assert
            assert isinstance(result, dict)
            assert result["service"] == "AutoForgeNexus Backend"
            assert "timestamp" in result
            assert "system" in result
            assert result["system"]["cpu_percent"] == 15.0

    @pytest.mark.asyncio
    async def test_check_readinessがデータベース状態を確認する(self):
        """
        check_readiness()がデータベースの準備状態をチェックすることを確認
        """
        # Arrange
        from src.monitoring import DependencyHealth, HealthStatus

        mock_db_health = DependencyHealth(
            name="database", status=HealthStatus.HEALTHY, response_time_ms=10.0
        )

        with patch(
            "src.monitoring.health_checker._check_database",
            return_value=mock_db_health,
        ):
            from src.monitoring import check_readiness

            # Act
            result = await check_readiness()

            # Assert
            assert isinstance(result, dict)
            assert result["ready"] is True
            assert "timestamp" in result
            assert "checks" in result
            assert result["checks"]["database"]["name"] == "database"

    @pytest.mark.asyncio
    async def test_check_readinessがデータベース不健全時にfalseを返す(self):
        """
        check_readiness()がデータベース不健全時にready=falseを返すことを確認
        """
        # Arrange
        from src.monitoring import DependencyHealth, HealthStatus

        mock_db_health = DependencyHealth(
            name="database",
            status=HealthStatus.UNHEALTHY,
            response_time_ms=0,
            error="Connection failed",
        )

        with patch(
            "src.monitoring.health_checker._check_database",
            return_value=mock_db_health,
        ):
            from src.monitoring import check_readiness

            # Act
            result = await check_readiness()

            # Assert
            assert result["ready"] is False

    @pytest.mark.asyncio
    async def test_check_livenessが生存状態を返す(self):
        """
        check_liveness()が生存状態を返すことを確認
        """
        # Arrange
        with patch("src.monitoring.health_checker.start_time", time.time() - 5000):
            from src.monitoring import check_liveness

            # Act
            result = await check_liveness()

            # Assert
            assert isinstance(result, dict)
            assert result["alive"] is True
            assert "timestamp" in result
            assert result["uptime_seconds"] >= 5000
