"""
Phase 4: Database Vector Setup - Turso Connection Module
Handles connection to Turso (libSQL) database for staging/production environments
"""

# cspell:ignore libsql libSQL Turso authToken

import logging
import os
from collections.abc import Generator

import libsql_client
from libsql_client import ResultSet
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from core.config.settings import Settings
from domain.shared.events.event_bus import InMemoryEventBus
from domain.shared.events.infrastructure_events import (
    DatabaseConnectionEstablished,
    DatabaseConnectionFailed,
    DatabaseType,
    Environment,
)

logger = logging.getLogger(__name__)


class TursoConnection:
    """
    Turso database connection manager

    データベース接続のライフサイクルを管理し、
    接続状態の変化をイベントとして発行する。
    """

    def __init__(self, event_bus: InMemoryEventBus | None = None) -> None:
        """
        初期化

        Args:
            event_bus: イベントバス（省略時は新規作成）
        """
        self.settings = Settings()
        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None
        self._client: libsql_client.Client | None = None
        self._event_bus = event_bus or InMemoryEventBus()

    def get_connection_url(self) -> str:
        """Get appropriate database URL based on environment"""
        env = os.getenv("APP_ENV", "local")

        if env == "production":
            # Production: Use Turso
            url = os.getenv("TURSO_DATABASE_URL")
            token = os.getenv("TURSO_AUTH_TOKEN")
            if url and token:
                # Format: libsql://[DATABASE_NAME]-[ORG_NAME].turso.io?authToken=[TOKEN]
                return f"{url}?authToken={token}"

        elif env == "staging":
            # Staging: Use Turso
            url = os.getenv("TURSO_STAGING_DATABASE_URL")
            token = os.getenv("TURSO_STAGING_AUTH_TOKEN")
            if url and token:
                return f"{url}?authToken={token}"

        # Development: Use local SQLite
        return os.getenv("DATABASE_URL", "sqlite:///./data/autoforge_dev.db")

    def get_libsql_client(self) -> libsql_client.Client:
        """Get libSQL client for direct database operations"""
        if self._client is None:
            env = os.getenv("APP_ENV", "local")

            if env in ["production", "staging"]:
                url = (
                    os.getenv("TURSO_DATABASE_URL")
                    if env == "production"
                    else os.getenv("TURSO_STAGING_DATABASE_URL")
                )
                token = (
                    os.getenv("TURSO_AUTH_TOKEN")
                    if env == "production"
                    else os.getenv("TURSO_STAGING_AUTH_TOKEN")
                )

                if url and token:
                    self._client = libsql_client.create_client(
                        url=url, auth_token=token
                    )
                else:
                    raise ValueError(f"Missing Turso credentials for {env} environment")
            else:
                # Development: Use local file
                self._client = libsql_client.create_client(
                    url="file:./data/autoforge_dev.db"
                )

        return self._client

    def get_engine(self) -> Engine:
        """
        Get SQLAlchemy engine

        接続確立時にDatabaseConnectionEstablishedイベントを発行する。
        接続失敗時にDatabaseConnectionFailedイベントを発行する。

        Returns:
            SQLAlchemy engine

        Raises:
            ValueError: 接続URL取得に失敗した場合
            Exception: エンジン作成に失敗した場合
        """
        if self._engine is None:
            env_str = os.getenv("APP_ENV", "local")
            environment = self._parse_environment(env_str)

            try:
                connection_url = self.get_connection_url()

                # 🔐 セキュリティ改善: スキーム判定を明示的に（CodeQL CWE-20対策）
                # 変更前: if "sqlite" in connection_url
                # 変更後: スキームプレフィックスで明確に判定
                if connection_url.startswith("sqlite:///"):
                    # SQLite specific settings
                    self._engine = create_engine(
                        connection_url,
                        connect_args={"check_same_thread": False},
                        poolclass=StaticPool,
                        echo=self.settings.debug,
                    )
                    database_type = DatabaseType.SQLITE
                    pool_size = 1  # SQLiteはStaticPool
                else:
                    # Turso/libSQL settings
                    self._engine = create_engine(
                        connection_url,
                        echo=self.settings.debug,
                        pool_size=10,
                        max_overflow=20,
                        pool_pre_ping=True,
                    )
                    database_type = DatabaseType.TURSO
                    pool_size = 10

                # 🎉 イベント発行: 接続確立成功
                event = DatabaseConnectionEstablished(
                    environment=environment,
                    database_type=database_type,
                    connection_pool_size=pool_size,
                )
                self._event_bus.publish(event)
                logger.info(
                    f"Database connection established: {database_type.value} ({environment.value})"
                )

            except Exception as e:
                # 🚨 イベント発行: 接続失敗
                error_event = DatabaseConnectionFailed(
                    environment=environment,
                    error_message=str(e),
                    retry_count=0,
                )
                self._event_bus.publish(error_event)
                logger.error(
                    f"Database connection failed: {environment.value} - {e}",
                    exc_info=True,
                )
                raise

        return self._engine

    def _parse_environment(self, env_str: str) -> Environment:
        """
        環境文字列をEnvironment enumに変換

        Args:
            env_str: 環境文字列

        Returns:
            Environment enum
        """
        env_map = {
            "production": Environment.PRODUCTION,
            "staging": Environment.STAGING,
            "local": Environment.LOCAL,
            "development": Environment.DEVELOPMENT,
        }
        return env_map.get(env_str.lower(), Environment.LOCAL)

    def get_session_factory(self) -> sessionmaker[Session]:
        """Get session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                autocommit=False, autoflush=False, bind=self.get_engine()
            )
        return self._session_factory

    def get_session(self) -> Session:
        """Get database session"""
        session_factory = self.get_session_factory()
        return session_factory()

    async def execute_raw(
        self,
        query: str,
        params: dict[str, str | int | float | bool | None] | None = None,
    ) -> ResultSet:
        """Execute raw SQL query using libSQL client"""
        client = self.get_libsql_client()
        return await client.execute(query, params or {})

    async def batch_execute(
        self, queries: list[tuple[str, dict[str, str | int | float | bool | None]]]
    ) -> list[ResultSet]:
        """Execute multiple queries in a batch"""
        client = self.get_libsql_client()
        results: list[ResultSet] = []
        for query, params in queries:
            result = await client.execute(query, params)
            results.append(result)
        return results

    def close(self) -> None:
        """Close all connections"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
        if self._client:
            self._client.close()
            self._client = None
        self._session_factory = None


# Singleton instance
_turso_connection = TursoConnection()


def get_turso_connection() -> TursoConnection:
    """Get Turso connection singleton"""
    return _turso_connection


def get_db_session() -> Generator[Session, None, None]:
    """Get database session for dependency injection"""
    session = _turso_connection.get_session()
    try:
        yield session
    finally:
        session.close()
