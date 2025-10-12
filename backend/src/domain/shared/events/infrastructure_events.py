"""
Infrastructure層のドメインイベント

データベース接続状態、ヘルスチェック、インフラ異常などのイベントを定義
"""

from datetime import UTC, datetime
from enum import Enum

from domain.shared.events.domain_event import DomainEvent


class HealthStatus(str, Enum):
    """インフラストラクチャのヘルスステータス"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DatabaseType(str, Enum):
    """データベースタイプ"""

    TURSO = "turso"
    SQLITE = "sqlite"
    REDIS = "redis"


class Environment(str, Enum):
    """実行環境"""

    PRODUCTION = "production"
    STAGING = "staging"
    LOCAL = "local"
    DEVELOPMENT = "development"


class DatabaseConnectionEstablished(DomainEvent):
    """
    データベース接続確立イベント

    データベース接続が正常に確立された時に発行される。
    監視システム、ログ集約、メトリクス収集に使用される。

    Attributes:
        environment: 実行環境 (production/staging/local)
        database_type: データベースタイプ (turso/sqlite)
        connection_pool_size: 接続プールサイズ
        timestamp: イベント発生時刻
    """

    def __init__(
        self,
        environment: str | Environment,
        database_type: str | DatabaseType,
        connection_pool_size: int,
        timestamp: datetime | None = None,
    ):
        """
        データベース接続確立イベントを初期化

        Args:
            environment: 実行環境
            database_type: データベースタイプ
            connection_pool_size: 接続プールサイズ
            timestamp: イベント発生時刻（省略時は現在時刻）
        """
        # Enumの場合は値を取得
        self.environment = (
            environment.value if isinstance(environment, Environment) else environment
        )
        self.database_type = (
            database_type.value
            if isinstance(database_type, DatabaseType)
            else database_type
        )
        self.connection_pool_size = connection_pool_size
        self.timestamp = timestamp or datetime.now(UTC)

        # 基底クラスの初期化
        super().__init__(
            aggregate_id=f"db_connection_{self.environment}_{self.database_type}",
            event_type="DatabaseConnectionEstablished",
            occurred_at=self.timestamp,
            payload={
                "environment": self.environment,
                "database_type": self.database_type,
                "connection_pool_size": self.connection_pool_size,
            },
        )


class DatabaseConnectionFailed(DomainEvent):
    """
    データベース接続失敗イベント

    データベース接続に失敗した時に発行される。
    アラート、エラーログ、自動復旧トリガーに使用される。

    Attributes:
        environment: 実行環境
        error_message: エラーメッセージ
        retry_count: リトライ回数
        timestamp: イベント発生時刻
    """

    def __init__(
        self,
        environment: str | Environment,
        error_message: str,
        retry_count: int = 0,
        timestamp: datetime | None = None,
    ):
        """
        データベース接続失敗イベントを初期化

        Args:
            environment: 実行環境
            error_message: エラーメッセージ
            retry_count: リトライ回数（デフォルト: 0）
            timestamp: イベント発生時刻（省略時は現在時刻）
        """
        self.environment = (
            environment.value if isinstance(environment, Environment) else environment
        )
        self.error_message = error_message
        self.retry_count = retry_count
        self.timestamp = timestamp or datetime.now(UTC)

        super().__init__(
            aggregate_id=f"db_connection_failed_{self.environment}",
            event_type="DatabaseConnectionFailed",
            occurred_at=self.timestamp,
            payload={
                "environment": self.environment,
                "error_message": error_message,
                "retry_count": retry_count,
            },
        )


class DatabaseHealthCheckCompleted(DomainEvent):
    """
    データベースヘルスチェック完了イベント

    定期的なヘルスチェックの結果を通知する。
    監視ダッシュボード、SLO追跡、自動スケーリングに使用される。

    Attributes:
        status: ヘルスステータス (HEALTHY/DEGRADED/UNHEALTHY)
        latency_ms: レイテンシ（ミリ秒）
        timestamp: イベント発生時刻
        details: 追加詳細情報（オプション）
    """

    def __init__(
        self,
        status: str | HealthStatus,
        latency_ms: int,
        timestamp: datetime | None = None,
        details: dict[str, str | int | float] | None = None,
    ):
        """
        ヘルスチェック完了イベントを初期化

        Args:
            status: ヘルスステータス
            latency_ms: レイテンシ（ミリ秒）
            timestamp: イベント発生時刻（省略時は現在時刻）
            details: 追加詳細情報（オプション）
        """
        self.status = status.value if isinstance(status, HealthStatus) else status
        self.latency_ms = latency_ms
        self.timestamp = timestamp or datetime.now(UTC)
        self.details = details

        super().__init__(
            aggregate_id=f"db_health_check_{self.status}",
            event_type="DatabaseHealthCheckCompleted",
            occurred_at=self.timestamp,
            payload={
                "status": self.status,
                "latency_ms": latency_ms,
                "details": details or {},
            },
        )

    @property
    def is_healthy(self) -> bool:
        """ヘルスステータスがHEALTHYかどうか"""
        return self.status == HealthStatus.HEALTHY.value

    @property
    def requires_alert(self) -> bool:
        """アラートが必要かどうか（DEGRADED以下）"""
        return self.status in [
            HealthStatus.DEGRADED.value,
            HealthStatus.UNHEALTHY.value,
        ]
