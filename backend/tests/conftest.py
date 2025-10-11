"""
Pytest configuration and shared fixtures
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    """FastAPIアプリケーションのフィクスチャ"""
    from src.main import app as _app

    return _app


@pytest.fixture
def client(app) -> Generator[TestClient]:
    """テスト用HTTPクライアント"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_settings(monkeypatch):
    """設定のモック用フィクスチャ"""

    def _mock_settings(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key.upper(), str(value))

    return _mock_settings
