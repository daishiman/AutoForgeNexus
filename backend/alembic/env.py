"""
Alembic環境設定
環境別（local/staging/production）のデータベース接続を管理
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Pythonパスにsrcを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 設定とモデルのインポート
from src.infrastructure.shared.database.turso_connection import get_turso_connection

# Alembic Config オブジェクト
config = context.config

# ログ設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaDataの取得（すべてのモデルをインポート）
# DDDアーキテクチャ準拠: 各ドメインから明示的にインポート

# 各ドメインモデルのインポート（Alembic自動検出用）
from src.infrastructure.shared.database.base import Base  # noqa: E402

target_metadata = Base.metadata


def get_url() -> str:
    """環境に応じたデータベースURLを取得"""
    turso_conn = get_turso_connection()
    return turso_conn.get_connection_url()


def run_migrations_offline() -> None:
    """オフラインモードでマイグレーション実行"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """オンラインモードでマイグレーション実行"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
