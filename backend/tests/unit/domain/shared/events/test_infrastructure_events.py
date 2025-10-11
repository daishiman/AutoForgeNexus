"""
Infrastructure Events のテストケース

データベース接続イベント、ヘルスチェックイベントのテスト
"""

from datetime import UTC, datetime

from src.domain.shared.events.infrastructure_events import (
    DatabaseConnectionEstablished,
    DatabaseConnectionFailed,
    DatabaseHealthCheckCompleted,
    DatabaseType,
    Environment,
    HealthStatus,
)


class TestDatabaseConnectionEstablished:
    """DatabaseConnectionEstablishedイベントのテスト"""

    def test_create_event_with_enum(self):
        """Enumを使った正常なイベント作成"""
        event = DatabaseConnectionEstablished(
            environment=Environment.PRODUCTION,
            database_type=DatabaseType.TURSO,
            connection_pool_size=10,
        )

        assert event.environment == "production"
        assert event.database_type == "turso"
        assert event.connection_pool_size == 10
        assert event.event_type == "DatabaseConnectionEstablished"
        assert event.aggregate_id == "db_connection_production_turso"

    def test_create_event_with_string(self):
        """文字列を使ったイベント作成"""
        event = DatabaseConnectionEstablished(
            environment="staging",
            database_type="sqlite",
            connection_pool_size=1,
        )

        assert event.environment == "staging"
        assert event.database_type == "sqlite"
        assert event.connection_pool_size == 1

    def test_event_has_expected_attributes(self):
        """イベントが期待される属性を持つことを確認"""
        event = DatabaseConnectionEstablished(
            environment=Environment.LOCAL,
            database_type=DatabaseType.SQLITE,
            connection_pool_size=1,
        )

        # イベントの属性が正しく設定されている
        assert hasattr(event, "environment")
        assert hasattr(event, "database_type")
        assert hasattr(event, "connection_pool_size")
        assert hasattr(event, "timestamp")
        assert hasattr(event, "event_id")
        assert hasattr(event, "aggregate_id")

    def test_event_timestamp_default(self):
        """タイムスタンプのデフォルト値"""
        event = DatabaseConnectionEstablished(
            environment=Environment.LOCAL,
            database_type=DatabaseType.SQLITE,
            connection_pool_size=1,
        )

        # デフォルトで現在時刻が設定される
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)
        assert event.timestamp.tzinfo == UTC

    def test_event_timestamp_custom(self):
        """カスタムタイムスタンプ"""
        custom_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        event = DatabaseConnectionEstablished(
            environment=Environment.PRODUCTION,
            database_type=DatabaseType.TURSO,
            connection_pool_size=10,
            timestamp=custom_time,
        )

        assert event.timestamp == custom_time

    def test_event_payload(self):
        """イベントペイロードの内容確認"""
        event = DatabaseConnectionEstablished(
            environment=Environment.PRODUCTION,
            database_type=DatabaseType.TURSO,
            connection_pool_size=10,
        )

        payload = event.payload
        assert payload["environment"] == "production"
        assert payload["database_type"] == "turso"
        assert payload["connection_pool_size"] == 10


class TestDatabaseConnectionFailed:
    """DatabaseConnectionFailedイベントのテスト"""

    def test_create_event_with_default_retry(self):
        """デフォルトのリトライ回数でイベント作成"""
        event = DatabaseConnectionFailed(
            environment=Environment.PRODUCTION,
            error_message="Connection timeout",
        )

        assert event.environment == "production"
        assert event.error_message == "Connection timeout"
        assert event.retry_count == 0
        assert event.event_type == "DatabaseConnectionFailed"

    def test_create_event_with_retry_count(self):
        """リトライ回数指定でイベント作成"""
        event = DatabaseConnectionFailed(
            environment=Environment.STAGING,
            error_message="Network error",
            retry_count=3,
        )

        assert event.retry_count == 3

    def test_event_payload_includes_error(self):
        """ペイロードにエラー情報が含まれる"""
        event = DatabaseConnectionFailed(
            environment=Environment.LOCAL,
            error_message="Database locked",
            retry_count=1,
        )

        payload = event.payload
        assert payload["error_message"] == "Database locked"
        assert payload["retry_count"] == 1


class TestDatabaseHealthCheckCompleted:
    """DatabaseHealthCheckCompletedイベントのテスト"""

    def test_create_healthy_event(self):
        """HEALTHYステータスのイベント作成"""
        event = DatabaseHealthCheckCompleted(
            status=HealthStatus.HEALTHY,
            latency_ms=50,
        )

        assert event.status == "healthy"
        assert event.latency_ms == 50
        assert event.event_type == "DatabaseHealthCheckCompleted"
        assert event.is_healthy is True
        assert event.requires_alert is False

    def test_create_degraded_event(self):
        """DEGRADEDステータスのイベント作成"""
        event = DatabaseHealthCheckCompleted(
            status=HealthStatus.DEGRADED,
            latency_ms=300,
        )

        assert event.status == "degraded"
        assert event.is_healthy is False
        assert event.requires_alert is True

    def test_create_unhealthy_event(self):
        """UNHEALTHYステータスのイベント作成"""
        event = DatabaseHealthCheckCompleted(
            status=HealthStatus.UNHEALTHY,
            latency_ms=5000,
        )

        assert event.status == "unhealthy"
        assert event.is_healthy is False
        assert event.requires_alert is True

    def test_event_with_details(self):
        """詳細情報付きイベント作成"""
        details = {
            "query_count": 150,
            "error_rate": 0.05,
            "connection_pool_usage": 80.5,
        }
        event = DatabaseHealthCheckCompleted(
            status=HealthStatus.DEGRADED,
            latency_ms=250,
            details=details,
        )

        assert event.details is not None
        assert event.details["query_count"] == 150
        assert event.details["error_rate"] == 0.05

    def test_event_without_details(self):
        """詳細情報なしイベント作成"""
        event = DatabaseHealthCheckCompleted(
            status=HealthStatus.HEALTHY,
            latency_ms=30,
        )

        assert event.details is None
        assert event.payload["details"] == {}

    def test_health_status_properties(self):
        """ヘルスステータスプロパティのテスト"""
        healthy_event = DatabaseHealthCheckCompleted(
            status=HealthStatus.HEALTHY,
            latency_ms=50,
        )
        degraded_event = DatabaseHealthCheckCompleted(
            status=HealthStatus.DEGRADED,
            latency_ms=250,
        )
        unhealthy_event = DatabaseHealthCheckCompleted(
            status=HealthStatus.UNHEALTHY,
            latency_ms=5000,
        )

        # HEALTHYのみがis_healthy=True
        assert healthy_event.is_healthy is True
        assert degraded_event.is_healthy is False
        assert unhealthy_event.is_healthy is False

        # HEALTHYのみがrequires_alert=False
        assert healthy_event.requires_alert is False
        assert degraded_event.requires_alert is True
        assert unhealthy_event.requires_alert is True


class TestEventSerialization:
    """イベントのシリアライズ/デシリアライズテスト"""

    def test_connection_established_to_dict(self):
        """接続確立イベントの辞書変換"""
        event = DatabaseConnectionEstablished(
            environment=Environment.PRODUCTION,
            database_type=DatabaseType.TURSO,
            connection_pool_size=10,
        )

        event_dict = event.to_dict()
        assert event_dict["event_type"] == "DatabaseConnectionEstablished"
        assert event_dict["payload"]["environment"] == "production"
        assert event_dict["payload"]["database_type"] == "turso"

    def test_connection_failed_to_dict(self):
        """接続失敗イベントの辞書変換"""
        event = DatabaseConnectionFailed(
            environment=Environment.STAGING,
            error_message="Timeout",
            retry_count=2,
        )

        event_dict = event.to_dict()
        assert event_dict["event_type"] == "DatabaseConnectionFailed"
        assert event_dict["payload"]["error_message"] == "Timeout"
        assert event_dict["payload"]["retry_count"] == 2

    def test_health_check_to_dict(self):
        """ヘルスチェックイベントの辞書変換"""
        event = DatabaseHealthCheckCompleted(
            status=HealthStatus.HEALTHY,
            latency_ms=50,
            details={"query_count": 100},
        )

        event_dict = event.to_dict()
        assert event_dict["event_type"] == "DatabaseHealthCheckCompleted"
        assert event_dict["payload"]["status"] == "healthy"
        assert event_dict["payload"]["latency_ms"] == 50
        assert event_dict["payload"]["details"]["query_count"] == 100
