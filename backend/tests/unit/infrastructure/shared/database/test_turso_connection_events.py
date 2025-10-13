"""
TursoConnection イベント発行のテスト

データベース接続時のイベント発行動作を検証
"""

import os
from unittest.mock import patch

import pytest

from src.domain.shared.events.event_bus import InMemoryEventBus
from src.domain.shared.events.infrastructure_events import (
    DatabaseConnectionEstablished,
    DatabaseConnectionFailed,
    DatabaseType,
    Environment,
)
from src.infrastructure.shared.database.turso_connection import TursoConnection


class TestTursoConnectionEvents:
    """TursoConnectionのイベント発行テスト"""

    @pytest.fixture
    def event_bus(self):
        """テスト用イベントバス"""
        bus = InMemoryEventBus(_enable_history=True)
        return bus

    @pytest.fixture
    def turso_connection(self, event_bus):
        """テスト用TursoConnection"""
        return TursoConnection(event_bus=event_bus)

    @patch.dict(os.environ, {"APP_ENV": "local"}, clear=True)
    def test_sqlite_connection_established_event(self, turso_connection, event_bus):
        """SQLite接続時にDatabaseConnectionEstablishedイベントが発行される"""
        # 接続実行
        engine = turso_connection.get_engine()

        # エンジンが作成される
        assert engine is not None

        # イベント履歴を確認
        events = event_bus.get_event_history()
        assert len(events) >= 1

        # 最初のイベントがDatabaseConnectionEstablished
        connection_event = events[0]
        assert isinstance(connection_event, DatabaseConnectionEstablished)
        assert connection_event.environment == Environment.LOCAL.value
        assert connection_event.database_type == DatabaseType.SQLITE.value
        assert connection_event.connection_pool_size == 1

    @patch.dict(os.environ, {"APP_ENV": "production"}, clear=True)
    @patch("src.infrastructure.shared.database.turso_connection.create_engine")
    def test_turso_connection_established_event(
        self, mock_create_engine, turso_connection, event_bus
    ):
        """Turso接続時にDatabaseConnectionEstablishedイベントが発行される"""
        # モックエンジンを返す
        mock_engine = object()
        mock_create_engine.return_value = mock_engine

        # Turso環境変数を設定
        with patch.dict(
            os.environ,
            {
                "TURSO_DATABASE_URL": "libsql://test.turso.io",
                "TURSO_AUTH_TOKEN": "test_token",
            },
        ):
            engine = turso_connection.get_engine()

        assert engine is not None

        # イベント確認
        events = event_bus.get_event_history()
        connection_event = events[0]
        assert isinstance(connection_event, DatabaseConnectionEstablished)
        assert connection_event.environment == Environment.PRODUCTION.value
        assert connection_event.database_type == DatabaseType.TURSO.value
        assert connection_event.connection_pool_size == 10

    @patch.dict(os.environ, {"APP_ENV": "local"}, clear=True)
    @patch("src.infrastructure.shared.database.turso_connection.create_engine")
    def test_connection_failed_event(
        self, mock_create_engine, turso_connection, event_bus
    ):
        """接続失敗時にDatabaseConnectionFailedイベントが発行される"""
        # エンジン作成で例外を発生
        mock_create_engine.side_effect = Exception("Connection timeout")

        # 接続試行（例外が発生）
        with pytest.raises(Exception, match="Connection timeout"):
            turso_connection.get_engine()

        # イベント履歴確認
        events = event_bus.get_event_history()
        assert len(events) == 1

        # 失敗イベントが発行される
        failed_event = events[0]
        assert isinstance(failed_event, DatabaseConnectionFailed)
        assert failed_event.environment == Environment.LOCAL.value
        assert "Connection timeout" in failed_event.error_message
        assert failed_event.retry_count == 0

    @patch.dict(os.environ, {"APP_ENV": "staging"}, clear=True)
    @patch("src.infrastructure.shared.database.turso_connection.create_engine")
    def test_staging_connection_event(
        self, mock_create_engine, turso_connection, event_bus
    ):
        """Staging環境での接続イベント"""
        mock_engine = object()
        mock_create_engine.return_value = mock_engine

        with patch.dict(
            os.environ,
            {
                "TURSO_STAGING_DATABASE_URL": "libsql://staging.turso.io",
                "TURSO_STAGING_AUTH_TOKEN": "staging_token",
            },
        ):
            engine = turso_connection.get_engine()

        assert engine is not None

        events = event_bus.get_event_history()
        connection_event = events[0]
        assert connection_event.environment == Environment.STAGING.value

    def test_event_bus_integration(self, turso_connection, event_bus):
        """イベントバス統合のテスト"""
        # イベントハンドラーを登録
        received_events = []

        def handler(event):
            received_events.append(event)

        event_bus.subscribe(DatabaseConnectionEstablished, handler)

        # 接続実行
        with patch.dict(os.environ, {"APP_ENV": "local"}, clear=True):
            turso_connection.get_engine()

        # ハンドラーが呼ばれる
        assert len(received_events) == 1
        assert isinstance(received_events[0], DatabaseConnectionEstablished)

    def test_multiple_connection_attempts(self, event_bus):
        """複数回の接続試行でイベントが発行される"""
        # 新しいインスタンスを作成（_engine=None状態）
        conn1 = TursoConnection(event_bus=event_bus)
        conn2 = TursoConnection(event_bus=event_bus)

        with patch.dict(os.environ, {"APP_ENV": "local"}, clear=True):
            # 2つの接続を作成
            conn1.get_engine()
            conn2.get_engine()

        # 2つのイベントが発行される
        events = event_bus.get_event_history()
        assert len(events) == 2
        assert all(isinstance(e, DatabaseConnectionEstablished) for e in events)

    def test_singleton_connection_does_not_duplicate_events(
        self, turso_connection, event_bus
    ):
        """シングルトン接続では重複イベントが発行されない"""
        with patch.dict(os.environ, {"APP_ENV": "local"}, clear=True):
            # 同じインスタンスで複数回get_engineを呼ぶ
            engine1 = turso_connection.get_engine()
            engine2 = turso_connection.get_engine()

        # 同じエンジンが返される
        assert engine1 is engine2

        # イベントは1回だけ発行される
        events = event_bus.get_event_history()
        assert len(events) == 1


class TestEnvironmentParsing:
    """環境文字列パース機能のテスト"""

    def test_parse_production_environment(self):
        """production環境のパース"""
        conn = TursoConnection()
        result = conn._parse_environment("production")
        assert result == Environment.PRODUCTION

    def test_parse_staging_environment(self):
        """staging環境のパース"""
        conn = TursoConnection()
        result = conn._parse_environment("staging")
        assert result == Environment.STAGING

    def test_parse_local_environment(self):
        """local環境のパース"""
        conn = TursoConnection()
        result = conn._parse_environment("local")
        assert result == Environment.LOCAL

    def test_parse_development_environment(self):
        """development環境のパース"""
        conn = TursoConnection()
        result = conn._parse_environment("development")
        assert result == Environment.DEVELOPMENT

    def test_parse_unknown_environment_defaults_to_local(self):
        """未知の環境はLOCALにフォールバック"""
        conn = TursoConnection()
        result = conn._parse_environment("unknown_env")
        assert result == Environment.LOCAL

    def test_parse_case_insensitive(self):
        """大文字小文字を区別しない"""
        conn = TursoConnection()
        assert conn._parse_environment("PRODUCTION") == Environment.PRODUCTION
        assert conn._parse_environment("Production") == Environment.PRODUCTION
        assert conn._parse_environment("pRoDuCtIoN") == Environment.PRODUCTION
