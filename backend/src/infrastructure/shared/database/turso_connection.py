"""
Phase 4: Database Vector Setup - Turso Connection Module
Handles connection to Turso (libSQL) database for staging/production environments
"""

# cspell:ignore libsql libSQL Turso authToken

import os
from collections.abc import Generator

import libsql_client
from libsql_client import ResultSet
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.config.settings import Settings


class TursoConnection:
    """Turso database connection manager"""

    def __init__(self) -> None:
        self.settings = Settings()
        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None
        self._client: libsql_client.Client | None = None

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
        """Get SQLAlchemy engine"""
        if self._engine is None:
            connection_url = self.get_connection_url()

            if "sqlite" in connection_url:
                # SQLite specific settings
                self._engine = create_engine(
                    connection_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=self.settings.debug,
                )
            else:
                # Turso/libSQL settings
                self._engine = create_engine(
                    connection_url,
                    echo=self.settings.debug,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                )

        return self._engine

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
