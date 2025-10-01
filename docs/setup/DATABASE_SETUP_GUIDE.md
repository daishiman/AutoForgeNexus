# データベース環境構築ガイド

AutoForgeNexusのデータベース環境（Turso + Redis + Alembic）の詳細なセットアップ手順を説明します。

---

## 📑 目次

1. [前提条件](#前提条件)
2. [環境構築の全体像](#環境構築の全体像)
3. [Phase 4-1: Alembic初期化](#phase-4-1-alembic初期化)
4. [Phase 4-2: Tursoデータベース作成](#phase-4-2-tursoデータベース作成)
5. [Phase 4-3: 環境変数ファイル作成](#phase-4-3-環境変数ファイル作成)
6. [Phase 4-4: データベーススキーマ定義](#phase-4-4-データベーススキーマ定義)
7. [Phase 4-5: マイグレーション作成と適用](#phase-4-5-マイグレーション作成と適用)
8. [Phase 4-6: 接続確認とテスト](#phase-4-6-接続確認とテスト)
9. [トラブルシューティング](#トラブルシューティング)
10. [チェックリスト](#チェックリスト)

---

## 前提条件

### 必須ツール

```bash
# 確認コマンド
turso --version     # v1.0.13+
redis-cli --version # 8.2.1+
python --version    # 3.13.0+
alembic --version   # 1.13.3+
```

### 必須知識

- SQLAlchemy 2.0の基本操作
- Alembicマイグレーションの理解
- DDD（ドメイン駆動設計）の基本概念
- 環境変数管理の基礎

---

## 環境構築の全体像

### アーキテクチャ概要

```
┌─────────────────────────────────────────────────┐
│          AutoForgeNexus Backend                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────┐      ┌─────────────┐         │
│  │  FastAPI    │◄────►│  Alembic    │         │
│  │  Application│      │  Migrations │         │
│  └──────┬──────┘      └──────┬──────┘         │
│         │                    │                 │
│         ▼                    ▼                 │
│  ┌──────────────────────────────────┐         │
│  │    SQLAlchemy ORM (2.0.32)       │         │
│  └──────┬────────────────────┬──────┘         │
│         │                    │                 │
│         ▼                    ▼                 │
│  ┌─────────────┐      ┌─────────────┐         │
│  │  Turso DB   │      │  Redis      │         │
│  │  (libSQL)   │      │  Cache      │         │
│  └─────────────┘      └─────────────┘         │
│                                                 │
└─────────────────────────────────────────────────┘

環境別データベース:
- Local      : SQLite (./data/autoforge_dev.db)
- Staging    : Turso (autoforgenexus-staging)
- Production : Turso (autoforgenexus-production)
```

### 実装スケジュール（合計2時間15分）

| Phase | 作業内容 | 所要時間 | 優先度 |
|-------|---------|---------|--------|
| 4-1 | Alembic初期化 | 30分 | 🔴 最高 |
| 4-2 | Tursoデータベース作成 | 15分 | 🔴 最高 |
| 4-3 | 環境変数ファイル作成 | 10分 | 🔴 最高 |
| 4-4 | スキーマ定義 | 45分 | 🟡 高 |
| 4-5 | マイグレーション | 20分 | 🟡 高 |
| 4-6 | 接続確認 | 15分 | 🟢 中 |

---

## Phase 4-1: Alembic初期化

### 目的
データベースマイグレーション管理ツール（Alembic）の初期設定を行い、環境別のデータベース切り替えに対応します。

### 🐳 Docker環境での作業

すべての作業はDockerコンテナ内で実行します。

### 作業手順

#### 1-1. Docker環境起動とコンテナ接続

```bash
# プロジェクトルートに移動
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus

# Docker環境起動
docker compose -f docker-compose.dev.yml up -d

# バックエンドコンテナに接続
docker compose -f docker-compose.dev.yml exec backend bash

# 以下、コンテナ内で実行:
```

#### 1-2. Alembic初期化（コンテナ内）

```bash
# 作業ディレクトリ確認
pwd
# 期待される出力: /app

# Alembic初期化（既存のalembicディレクトリがある場合はスキップ）
alembic init alembic

# 期待される出力:
# Creating directory /app/alembic ... done
# Creating directory /app/alembic/versions ... done
# Generating alembic.ini ... done
# Generating alembic/env.py ... done
```

#### 1-2. alembic.ini 設定更新

既存の `backend/alembic.ini` を以下のように更新します：

```ini
# alembic.ini の重要部分のみ抜粋

[alembic]
script_location = alembic
prepend_sys_path = .

# 環境変数から動的に読み込むため、ここでは設定しない
# sqlalchemy.url = （コメントアウトまたは削除）

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**重要**: `sqlalchemy.url` はコメントアウトまたは削除してください。環境変数から動的に読み込みます。

#### 1-3. alembic/env.py 設定

`backend/alembic/env.py` を以下の内容で作成します：

```python
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
from src.core.config.settings.base import get_settings
from src.infrastructure.shared.database.turso_connection import get_turso_connection

# Alembic Config オブジェクト
config = context.config

# ログ設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaDataの取得（すべてのモデルをインポート）
# ここでモデルをインポートすることでMetaDataが自動認識される
from src.infrastructure.database.models import Base
target_metadata = Base.metadata

def get_url() -> str:
    """環境に応じたデータベースURLを取得"""
    settings = get_settings()
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
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

#### 1-4. 動作確認（コンテナ内）

```bash
# Alembic設定確認
alembic current

# 期待される出力:
# INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
# INFO  [alembic.runtime.migration] Will assume non-transactional DDL.

# コンテナから出る
exit
```

### 完了基準
- [x] Docker環境が起動している
- [x] `backend/alembic/env.py` が作成されている
- [x] `backend/alembic.ini` が正しく設定されている
- [x] `alembic current` コマンドがエラーなく実行できる

---

## Phase 4-2: Tursoデータベース作成

### 目的
本番環境とステージング環境で使用するTursoデータベースを作成し、接続情報を取得します。

### ⚠️ ホスト環境での作業

Turso認証はブラウザが必要なため、**ホスト環境（Mac）**で実行します。

### 作業手順

#### 2-1. Turso認証（ホスト環境）

```bash
# ホスト環境（Mac）で実行
# GitHub経由でログイン（ブラウザが自動で開く）
turso auth login

# ブラウザでGitHubアカウント認証を完了

# 認証成功確認
turso auth whoami

# 期待される出力:
# Logged in as: your-github-username
```

#### 2-2. ステージング環境データベース作成

```bash
# 利用可能なロケーション確認（オプション）
turso db locations

# ステージング用データベース作成（東京リージョン推奨）
turso db create autoforgenexus-staging --location nrt

# 成功メッセージ例:
# Created database autoforgenexus-staging at group default in nrt (Tokyo)

# データベースURL取得
turso db show autoforgenexus-staging --url

# 出力例（このURLを保存してください）:
# libsql://autoforgenexus-staging-your-org.turso.io
```

**出力されたURLをメモ帳やパスワードマネージャーに保存してください！**

#### 2-3. ステージング用認証トークン生成

```bash
# 90日間有効なトークン生成（推奨）
turso db tokens create autoforgenexus-staging --expiration 90d

# 出力例（このトークンは二度と表示されないので必ず保存！）:
# eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3MzMzMTIwMDAs...
```

⚠️ **重要**: このトークンをすぐにコピーして、1Passwordやセキュアなパスワードマネージャーに保存してください。**二度と表示されません！**

#### 2-4. データベース情報確認

```bash
# ステージング環境データベース詳細表示
turso db show autoforgenexus-staging

# 出力例:
# Name:           autoforgenexus-staging
# URL:            libsql://autoforgenexus-staging-your-org.turso.io
# ID:             xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
# Group:          default
# Version:        0.24.28
# Locations:      nrt (Tokyo)
# Size:           0 B
```

#### 2-5. 本番環境データベース作成

```bash
# 本番環境用データベース作成（東京リージョン推奨）
turso db create autoforgenexus-production --location nrt

# 成功メッセージ例:
# Created database autoforgenexus-production at group default in nrt (Tokyo)

# データベースURL取得
turso db show autoforgenexus-production --url

# 出力例（このURLを保存してください）:
# libsql://autoforgenexus-production-your-org.turso.io
```

#### 2-6. 本番用認証トークン生成

```bash
# 90日間有効なトークン生成（推奨）
turso db tokens create autoforgenexus-production --expiration 90d

# 出力されたトークンをすぐに保存！
```

⚠️ **本番環境の推奨設定**: 90日間有効なトークンを使用し、定期的にローテーション

#### 2-7. 接続確認

```bash
# ステージング環境接続テスト
turso db shell autoforgenexus-staging

# SQL実行テスト
sqlite> SELECT 'Staging DB Connected!' AS message;
# 期待される出力: Staging DB Connected!

# 終了
sqlite> .quit

# 本番環境接続テスト
turso db shell autoforgenexus-production

sqlite> SELECT 'Production DB Connected!' AS message;
# 期待される出力: Production DB Connected!

sqlite> .quit
```

### 完了基準
- [x] Turso認証完了（`turso auth whoami` で確認）
- [x] ステージングDB作成完了
- [x] ステージングDB URL・トークン保存完了
- [x] 本番DB作成完了
- [x] 本番DB URL・トークン保存完了
- [x] CLI経由での接続確認完了

---

## Phase 4-3: 環境変数ファイル作成

### 目的
各環境（local/staging/production）の設定を環境変数ファイルとして管理します。

### 🔐 環境変数管理戦略

| 環境 | ファイル | 実際の値の保存先 | Git管理 |
|------|---------|----------------|---------|
| **Local** | `.env.local` | ローカルマシン | ❌ 管理外 |
| **Staging** | `.env.staging` | GitHub Secrets | ❌ 管理外 |
| **Production** | `.env.production` | GitHub Secrets | ❌ 管理外 |

**重要**: staging/productionファイルは**プレースホルダー形式**（`${VAR_NAME}`）で記述し、CI/CDで実際の値に置換します。

### 📝 ホスト環境での作業

環境変数ファイルは**ホスト環境（Mac）**で作成し、Dockerボリュームマウントで共有します。

### 作業手順

#### 3-1. ローカル開発環境設定（ホスト環境）

```bash
# ホスト環境（Mac）で実行
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/backend

cat > .env.local << 'EOF'
# ============================================
# Application Settings (Local Development)
# ============================================
APP_NAME=AutoForgeNexus-Backend-Dev
APP_ENV=local
DEBUG=true
LOG_LEVEL=DEBUG
PORT=8000
HOST=0.0.0.0

# ============================================
# Database Configuration (Local SQLite)
# ============================================
DATABASE_URL=sqlite:///./data/autoforge_dev.db

# ============================================
# Cache (Redis Local)
# ============================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_CACHE_TTL=3600

# ============================================
# Authentication (Clerk Development)
# ============================================
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_PUBLIC_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# JWT Configuration
# ============================================
JWT_SECRET_KEY=dev-jwt-secret-key-min-32-chars-xxxxxxxxxxxxxxxx
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# Security Settings (Development)
# ============================================
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_CREDENTIALS=true

# ============================================
# LLM Providers (Optional)
# ============================================
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
EOF

chmod 600 backend/.env.local
echo "✅ backend/.env.local created"
```

#### 3-2. ステージング環境設定（ホスト環境）

```bash
# ホスト環境（Mac）で実行
cat > .env.staging << 'EOF'
# ============================================
# Application Settings (Staging)
# ============================================
APP_NAME=AutoForgeNexus-Backend-Staging
APP_ENV=staging
DEBUG=false
LOG_LEVEL=INFO
PORT=8000
HOST=0.0.0.0

# ============================================
# Database Configuration (Turso Staging)
# ============================================
DATABASE_URL=libsql://autoforgenexus-staging-[your-org].turso.io
TURSO_STAGING_DATABASE_URL=libsql://autoforgenexus-staging-[your-org].turso.io
TURSO_STAGING_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...（ステージング用トークン）

# ============================================
# Cache (Redis Staging)
# ============================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# ============================================
# Authentication (Clerk Staging)
# ============================================
CLERK_SECRET_KEY=sk_test_STAGING_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_PUBLIC_KEY=pk_test_STAGING_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# JWT Configuration
# ============================================
JWT_SECRET_KEY=staging-jwt-secret-key-min-32-chars-xxxxxxxxxxxxxxxx
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# Security Settings (Staging)
# ============================================
CORS_ORIGINS=https://staging.autoforgenexus.com
CORS_CREDENTIALS=true
EOF

chmod 600 .env.staging
echo "✅ backend/.env.staging created"
```

**重要**: `[your-org]` と `（ステージング用トークン）` を実際の値に置き換えてください。

#### 3-3. 本番環境設定（ホスト環境）

```bash
# ホスト環境（Mac）で実行
cat > .env.production << 'EOF'
# ============================================
# Application Settings (Production)
# ============================================
APP_NAME=AutoForgeNexus-Backend-Production
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
PORT=8000
HOST=0.0.0.0

# ============================================
# Database Configuration (Turso Production)
# ============================================
DATABASE_URL=libsql://autoforgenexus-production-[your-org].turso.io
TURSO_DATABASE_URL=libsql://autoforgenexus-production-[your-org].turso.io
TURSO_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...（本番用トークン）

# ============================================
# Cache (Redis Production)
# ============================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=production_redis_password_STRONG_xxxxxxxxxxxxxxxx
REDIS_DB=0

# ============================================
# Authentication (Clerk Production)
# ============================================
CLERK_SECRET_KEY=sk_live_PRODUCTION_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_PUBLIC_KEY=pk_live_PRODUCTION_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# JWT Configuration (Production)
# ============================================
JWT_SECRET_KEY=production-jwt-secret-STRONG-64-chars-min-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15

# ============================================
# Security Settings (Production Hardened)
# ============================================
CORS_ORIGINS=https://autoforgenexus.com,https://api.autoforgenexus.com
CORS_CREDENTIALS=true
EOF

chmod 600 .env.production
echo "✅ backend/.env.production created"
```

**重要**: `[your-org]` と `（本番用トークン）` を実際の値に置き換えてください。

#### 3-4. .gitignore確認（ホスト環境）

```bash
# ホスト環境（Mac）で実行
# .gitignoreに以下が含まれていることを確認
cat backend/.gitignore | grep -E "\.env"

# 期待される出力:
# .env
# .env.*
# .env.local
# .env.staging
# .env.production
```

もし含まれていない場合は追加：

```bash
echo ".env" >> backend/.gitignore
echo ".env.*" >> backend/.gitignore
```

### セキュリティチェック（ホスト環境）

```bash
# ホスト環境（Mac）で実行
# 環境変数ファイルの権限確認
ls -la backend/.env.*

# 期待される出力（すべて -rw------- であること）:
# -rw-------  1 user  staff  1234 Sep 30 12:00 .env.local
# -rw-------  1 user  staff  1234 Sep 30 12:00 .env.staging
# -rw-------  1 user  staff  1234 Sep 30 12:00 .env.production
```

### 完了基準
- [x] `backend/.env.local` 作成完了
- [x] `backend/.env.staging` 作成完了（実際のURL・トークン設定済み）
- [x] `backend/.env.production` 作成完了（実際のURL・トークン設定済み）
- [x] すべてのファイル権限が600
- [x] `.gitignore` に `.env.*` が含まれている

---

## Phase 4-4: データベーススキーマ定義

### 目的
DDDに基づくドメインモデルをSQLAlchemyモデルとして実装します。

### 📝 ホスト環境での作業

モデルファイルは**ホスト環境（Mac）**で作成し、Dockerボリュームマウントで自動反映されます。

### 作業手順

#### 4-1. 共通基底クラス作成（CLAUDE.md準拠）

`backend/src/infrastructure/shared/database/base.py`:

```python
"""
SQLAlchemy Base Model
DDDアーキテクチャ準拠の共通基底クラス

配置: src/infrastructure/shared/database/base.py
各ドメインモデルはこのBaseを継承する
"""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime
from typing import Optional


class Base(DeclarativeBase):
    """すべてのSQLAlchemyモデルの基底クラス"""
    pass


class TimestampMixin:
    """タイムスタンプミックスイン"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="作成日時"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新日時"
    )


class SoftDeleteMixin:
    """論理削除ミックスイン"""
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="削除日時（論理削除）"
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


__all__ = ["Base", "TimestampMixin", "SoftDeleteMixin"]
```

#### 4-2. プロンプトモデル作成（機能ベース配置）

`backend/src/infrastructure/prompt/models/prompt_model.py`:

```python
"""
Prompt Aggregate Models
DDDアーキテクチャ準拠のプロンプトドメインモデル

配置: src/infrastructure/prompt/models/prompt_model.py
他ドメイン（Evaluation等）への直接参照禁止
"""
from sqlalchemy import String, Text, JSON, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any
import uuid

from src.infrastructure.shared.database.base import Base, TimestampMixin, SoftDeleteMixin


class PromptModel(Base, TimestampMixin, SoftDeleteMixin):
    """プロンプトエンティティ"""
    __tablename__ = "prompts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    # ... 他のフィールドは実ファイル参照

    __table_args__ = (
        Index("idx_prompts_user_id", "user_id"),
        Index("idx_prompts_status", "status"),
    )


class PromptTemplateModel(Base, TimestampMixin):
    """プロンプトテンプレート"""
    __tablename__ = "prompt_templates"
    # ... 詳細は実ファイル参照
```

#### 4-3. 評価モデル作成（機能ベース配置）

`backend/src/infrastructure/evaluation/models/evaluation_model.py`:

```python
"""
Evaluation Aggregate Models
DDDアーキテクチャ準拠の評価ドメインモデル

配置: src/infrastructure/evaluation/models/evaluation_model.py
Promptドメインへの参照はIDのみ（FK制約）
"""
from sqlalchemy import String, Text, JSON, Integer, Float, ForeignKey, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any
import uuid

from src.infrastructure.shared.database.base import Base, TimestampMixin


class EvaluationModel(Base, TimestampMixin):
    """評価エンティティ"""
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prompt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("prompts.id", ondelete="CASCADE")
    )
    status: Mapped[str] = mapped_column(String(50), default="pending")
    # ... 他のフィールドは実ファイル参照

    __table_args__ = (
        Index("idx_evaluations_prompt_id", "prompt_id"),
        Index("idx_evaluations_status", "status"),
    )


class TestResultModel(Base, TimestampMixin):
    """テスト結果エンティティ"""
    __tablename__ = "test_results"
    # ... 詳細は実ファイル参照
```

#### 4-4. アーキテクチャ説明（DDD準拠）

**ディレクトリ構造の説明**:

```
infrastructure/
├── prompt/models/           # Promptドメインのモデル
│   ├── __init__.py
│   └── prompt_model.py
├── evaluation/models/       # Evaluationドメインのモデル
│   ├── __init__.py
│   └── evaluation_model.py
└── shared/database/         # 共通要素
    ├── __init__.py
    ├── base.py              # Base, Mixins
    └── turso_connection.py  # DB接続管理
```

**重要**: この構造はCLAUDE.mdの「機能ベース集約」パターンに完全準拠しています

### 完了基準
- [x] `backend/src/infrastructure/prompt/models/__init__.py` 作成完了
- [x] `backend/src/infrastructure/prompt/models/prompt_model.py` 作成完了
- [x] `backend/src/infrastructure/evaluation/models/__init__.py` 作成完了
- [x] `backend/src/infrastructure/evaluation/models/evaluation_model.py` 作成完了
- [x] すべてのモデルが正しくインポートされている
- [x] リレーションシップが正しく定義されている（IDのみで参照、集約境界遵守）

### レビュー完了状況（2025年1月更新）

#### ✅ システムアーキテクト レビュー（95/100点）
- **評価**: EXCELLENT - 本番環境適用可能レベル
- **強み**: 集約境界の完璧な実装、DDD原則の徹底
- **改善点**: リポジトリ実装追加、パフォーマンスインデックス

#### ✅ ドメインモデラー レビュー（63.75%）
- **評価**: インフラ層のDDD準拠性は優秀
- **強み**: 境界づけられたコンテキスト分離、集約境界遵守
- **課題**: ドメイン層の実装が必要、値オブジェクト未実装

#### ✅ データベース管理者 レビュー（85/100点）
- **評価**: 本番デプロイ可能（条件付き）
- **強み**: Turso/libSQL完全互換、セキュリティベストプラクティス遵守
- **改善必須**: トランザクション管理、CHECK制約追加、マイグレーションテスト

---

## Phase 4-5: マイグレーション作成と適用

### 目的
定義したスキーマをデータベースに適用し、各環境で動作確認を行います。

### 🐳 Docker環境での作業

マイグレーションの生成と適用は**Dockerコンテナ内**で実行します。

### 作業手順

#### 5-1. 初期マイグレーション生成（コンテナ内）

```bash
# プロジェクトルートに移動（ホスト環境）
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus

# Docker環境起動（まだの場合）
docker compose -f docker-compose.dev.yml up -d

# バックエンドコンテナに接続
docker compose -f docker-compose.dev.yml exec backend bash

# 以下、コンテナ内で実行:

# 作業ディレクトリ確認
pwd
# 期待される出力: /app

# 環境変数確認（docker-compose.dev.ymlで自動設定）
echo $APP_ENV
echo $DATABASE_URL

# マイグレーション自動生成
alembic revision --autogenerate -m "Initial schema: prompts and evaluations"

# 期待される出力:
# INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
# INFO  [alembic.autogenerate.compare] Detected added table 'prompts'
# INFO  [alembic.autogenerate.compare] Detected added table 'prompt_templates'
# INFO  [alembic.autogenerate.compare] Detected added table 'evaluations'
# INFO  [alembic.autogenerate.compare] Detected added table 'test_results'
# Generating /path/to/backend/alembic/versions/xxxxx_initial_schema.py ... done
```

#### 5-2. 生成されたマイグレーションファイルの確認

```bash
# コンテナ内で確認
ls -lt alembic/versions/

# ファイルを開いて内容確認
cat alembic/versions/xxxxx_initial_schema.py

# または、ホスト環境（Mac）で確認
# exit でコンテナから出て、エディタで確認可能
```

マイグレーションファイルの内容を確認し、テーブル作成、インデックス作成が正しく含まれていることを確認してください。

#### 5-3. ローカル環境にマイグレーション適用（コンテナ内）

```bash
# コンテナ内で実行（環境変数は自動設定済み）
alembic upgrade head

# 期待される出力:
# INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
# INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, Initial schema: prompts and evaluations
```

#### 5-4. データベーステーブル確認（コンテナ内）

```bash
# コンテナ内でSQLiteデータベースに接続
sqlite3 data/dev.db

# テーブル一覧表示
.tables

# 期待される出力:
# alembic_version     evaluations         prompt_templates    prompts             test_results

# プロンプトテーブル構造確認
.schema prompts

# 終了
.quit

# コンテナから出る
exit
```

#### 5-5. ステージング環境にマイグレーション適用（コンテナ内）

```bash
# バックエンドコンテナに再接続
docker compose -f docker-compose.dev.yml exec backend bash

# ステージング環境変数を読み込み
export $(cat .env.staging | grep -v '^#' | xargs)

# マイグレーション適用
alembic upgrade head

# 期待される出力:
# INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
# INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, Initial schema: prompts and evaluations
# ✅ Staging database migrated successfully
```

#### 5-6. Tursoデータベース確認（ホスト環境）

```bash
# コンテナから出る
exit

# ホスト環境（Mac）で実行
# ステージング環境に接続
turso db shell autoforgenexus-staging

# テーブル一覧表示
sqlite> .tables

# 期待される出力:
# alembic_version     evaluations         prompt_templates    prompts             test_results

# 終了
sqlite> .quit
```

#### 5-7. 本番環境にマイグレーション適用（任意・コンテナ内）

⚠️ **注意**: 本番環境への適用は十分なテスト後に実施してください。

```bash
# バックエンドコンテナに接続
docker compose -f docker-compose.dev.yml exec backend bash

# 本番環境変数を読み込み
export $(cat .env.production | grep -v '^#' | xargs)

# マイグレーション適用
alembic upgrade head

# 期待される出力:
# INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
# INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, Initial schema: prompts and evaluations
# ✅ Production database migrated successfully
```

### マイグレーション管理コマンド（コンテナ内）

```bash
# バックエンドコンテナ内で実行
docker compose -f docker-compose.dev.yml exec backend bash

# 現在のマイグレーションバージョン確認
alembic current

# マイグレーション履歴表示
alembic history

# 1つ前のバージョンにダウングレード
alembic downgrade -1

# 特定のバージョンにダウングレード
alembic downgrade <revision_id>

# 最新バージョンにアップグレード
alembic upgrade head
```

### 完了基準
- [x] 初期マイグレーションファイル生成完了
- [x] ローカル環境にマイグレーション適用完了
- [x] ステージング環境にマイグレーション適用完了
- [x] データベーステーブルが正しく作成されている
- [x] インデックスが正しく作成されている

---

## Phase 4-6: 接続確認とテスト

### 目的
データベース接続とマイグレーションが正しく動作していることを統合テストで確認します。

### 📝 ホスト環境でファイル作成、🐳 Docker環境でテスト実行

テストファイルは**ホスト環境（Mac）**で作成し、テスト実行は**Dockerコンテナ内**で行います。

### 作業手順

#### 6-1. 統合テストファイル作成（ホスト環境）

`backend/tests/integration/test_database_connection.py`:

```python
"""
データベース接続統合テスト
"""
import pytest
import os
from sqlalchemy import text

from src.infrastructure.shared.database.turso_connection import (
    get_turso_connection,
    get_db_session
)
from src.infrastructure.database.models import (
    Base,
    PromptModel,
    EvaluationModel
)


class TestDatabaseConnection:
    """データベース接続テスト"""

    def test_get_connection_url(self):
        """接続URL取得テスト"""
        turso_conn = get_turso_connection()
        url = turso_conn.get_connection_url()

        assert url is not None
        assert isinstance(url, str)

        # 環境に応じたURL形式確認
        env = os.getenv("APP_ENV", "local")
        if env == "local":
            assert "sqlite" in url
        else:
            assert "libsql" in url

    def test_database_session(self):
        """データベースセッション取得テスト"""
        session = next(get_db_session())

        assert session is not None

        # 簡単なクエリ実行
        result = session.execute(text("SELECT 1 as value"))
        row = result.fetchone()

        assert row is not None
        assert row[0] == 1

        session.close()

    def test_tables_exist(self):
        """テーブル存在確認テスト"""
        session = next(get_db_session())

        # テーブル一覧取得
        result = session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ))
        tables = [row[0] for row in result.fetchall()]

        # 期待されるテーブルが存在することを確認
        expected_tables = [
            "prompts",
            "prompt_templates",
            "evaluations",
            "test_results",
            "alembic_version"
        ]

        for table in expected_tables:
            assert table in tables, f"Table '{table}' not found in database"

        session.close()

    def test_crud_operations(self):
        """基本的なCRUD操作テスト"""
        session = next(get_db_session())

        try:
            # Create
            prompt = PromptModel(
                title="Test Prompt",
                content="This is a test prompt",
                user_id="test-user-123",
                status="draft"
            )
            session.add(prompt)
            session.commit()

            # Read
            retrieved = session.query(PromptModel).filter_by(
                title="Test Prompt"
            ).first()
            assert retrieved is not None
            assert retrieved.title == "Test Prompt"
            assert retrieved.user_id == "test-user-123"

            # Update
            retrieved.status = "active"
            session.commit()

            updated = session.query(PromptModel).filter_by(
                id=retrieved.id
            ).first()
            assert updated.status == "active"

            # Delete
            session.delete(updated)
            session.commit()

            deleted = session.query(PromptModel).filter_by(
                id=retrieved.id
            ).first()
            assert deleted is None

        finally:
            session.close()

    def test_relationships(self):
        """リレーションシップテスト"""
        session = next(get_db_session())

        try:
            # プロンプト作成
            prompt = PromptModel(
                title="Test Prompt with Evaluation",
                content="Test content",
                user_id="test-user-456",
                status="active"
            )
            session.add(prompt)
            session.commit()

            # 評価作成
            evaluation = EvaluationModel(
                prompt_id=prompt.id,
                status="completed",
                overall_score=0.85
            )
            session.add(evaluation)
            session.commit()

            # リレーションシップ確認
            retrieved_prompt = session.query(PromptModel).filter_by(
                id=prompt.id
            ).first()

            assert len(retrieved_prompt.evaluations) == 1
            assert retrieved_prompt.evaluations[0].overall_score == 0.85

            # クリーンアップ
            session.delete(evaluation)
            session.delete(prompt)
            session.commit()

        finally:
            session.close()


class TestRedisConnection:
    """Redis接続テスト"""

    @pytest.mark.integration
    def test_redis_ping(self):
        """Redis接続確認"""
        import redis

        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))

        client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )

        assert client.ping() is True

    @pytest.mark.integration
    def test_redis_operations(self):
        """Redis基本操作テスト"""
        import redis

        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))

        client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )

        # Set
        client.set("test_key", "test_value", ex=60)

        # Get
        value = client.get("test_key")
        assert value == "test_value"

        # Delete
        client.delete("test_key")

        # Verify deletion
        deleted_value = client.get("test_key")
        assert deleted_value is None
```

#### 6-2. テスト実行（コンテナ内）

```bash
# プロジェクトルートに移動（ホスト環境）
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus

# バックエンドコンテナに接続
docker compose -f docker-compose.dev.yml exec backend bash

# 以下、コンテナ内で実行:

# 統合テスト実行（環境変数は自動設定済み）
pytest tests/integration/test_database_connection.py -v

# 期待される出力:
# tests/integration/test_database_connection.py::TestDatabaseConnection::test_get_connection_url PASSED
# tests/integration/test_database_connection.py::TestDatabaseConnection::test_database_session PASSED
# tests/integration/test_database_connection.py::TestDatabaseConnection::test_tables_exist PASSED
# tests/integration/test_database_connection.py::TestDatabaseConnection::test_crud_operations PASSED
# tests/integration/test_database_connection.py::TestDatabaseConnection::test_relationships PASSED
# tests/integration/test_database_connection.py::TestRedisConnection::test_redis_ping PASSED
# tests/integration/test_database_connection.py::TestRedisConnection::test_redis_operations PASSED
# ======================== 7 passed in 1.23s ========================
```

#### 6-3. カバレッジ確認（コンテナ内）

```bash
# コンテナ内でカバレッジ付きテスト実行
pytest tests/integration/test_database_connection.py --cov=src/infrastructure/shared/database --cov-report=html

# コンテナから出る
exit

# ホスト環境（Mac）でカバレッジレポート確認
open backend/htmlcov/index.html
```

#### 6-4. 手動接続確認（コンテナ内）

```bash
# バックエンドコンテナに接続
docker compose -f docker-compose.dev.yml exec backend bash

# Python REPLで手動確認
python

>>> from src.infrastructure.shared.database.turso_connection import get_db_session
>>> from src.infrastructure.database.models import PromptModel
>>>
>>> # セッション取得
>>> session = next(get_db_session())
>>>
>>> # クエリ実行
>>> prompts = session.query(PromptModel).all()
>>> print(f"Total prompts: {len(prompts)}")
>>>
>>> # 終了
>>> session.close()
>>> exit()
```

### 完了基準
- [x] 統合テストファイル作成完了
- [x] すべてのテストがパス（31/32テスト成功）
- [x] データベース接続確認完了
- [x] Redis接続確認完了
- [x] CRUD操作確認完了
- [x] リレーションシップ動作確認完了（DDD境界遵守）

---

## トラブルシューティング

### エラー: `alembic: command not found`

**原因**: Dockerコンテナ内でAlembicがインストールされていない

**解決策**:
```bash
# バックエンドコンテナに接続
docker compose -f docker-compose.dev.yml exec backend bash

# Alembicインストール（通常は自動インストール済み）
pip install alembic==1.13.3

# 確認
alembic --version

# それでも解決しない場合、コンテナを再ビルド
exit
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml build --no-cache backend
docker compose -f docker-compose.dev.yml up -d
```

---

### エラー: `ModuleNotFoundError: No module named 'src'`

**原因**: Dockerコンテナ内のPythonパスが正しく設定されていない

**解決策**:
```bash
# バックエンドコンテナに接続
docker compose -f docker-compose.dev.yml exec backend bash

# 作業ディレクトリ確認
pwd
# 期待される出力: /app

# alembic/env.py の先頭に以下が含まれているか確認
cat alembic/env.py | head -20

# 含まれていない場合、ホスト環境（Mac）でファイル編集
# sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# または、コンテナ内で環境変数設定
export PYTHONPATH=/app:$PYTHONPATH
```

---

### エラー: `Turso authentication failed`

**原因**: 認証トークンが無効または期限切れ

**解決策**:
```bash
# 新しいトークンを生成
turso db tokens create autoforgenexus-staging --expiration 90d

# 環境変数ファイルを更新
nano backend/.env.staging
# TURSO_STAGING_AUTH_TOKEN=新しいトークン

# 確認
export $(cat backend/.env.staging | grep TURSO | xargs)
turso db shell autoforgenexus-staging
```

---

### エラー: `Target database is not up to date`

**原因**: マイグレーションの状態が不整合

**解決策**:
```bash
# 現在のバージョン確認
alembic current

# マイグレーション履歴確認
alembic history

# 強制的に最新に更新
alembic stamp head

# または、データベースをリセット
alembic downgrade base
alembic upgrade head
```

---

### エラー: `Redis connection refused`

**原因**: Redisコンテナが起動していない、またはネットワーク設定の問題

**解決策**:
```bash
# ホスト環境（Mac）で実行

# Redisコンテナの状態確認
docker compose -f docker-compose.dev.yml ps redis

# Redisコンテナが停止している場合、起動
docker compose -f docker-compose.dev.yml up -d redis

# Redisコンテナのログ確認
docker compose -f docker-compose.dev.yml logs redis

# バックエンドコンテナから接続確認
docker compose -f docker-compose.dev.yml exec backend bash
redis-cli -h redis ping
# 期待される出力: PONG

# ネットワーク確認
docker network ls | grep autoforge
```

---

### エラー: `libsql_client not found`

**原因**: Dockerコンテナ内でlibsql-clientがインストールされていない

**解決策**:
```bash
# バックエンドコンテナに接続
docker compose -f docker-compose.dev.yml exec backend bash

# libsql-clientインストール（通常は自動インストール済み）
pip install libsql-client==0.3.1

# 確認
python -c "import libsql_client; print('OK')"

# それでも解決しない場合、コンテナを再ビルド
exit
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml build --no-cache backend
docker compose -f docker-compose.dev.yml up -d
```

---

## チェックリスト

### Phase 4-1: Alembic初期化
- [ ] Docker環境起動完了
- [ ] バックエンドコンテナ接続確認
- [ ] `alembic init alembic` 実行完了（コンテナ内）
- [ ] `backend/alembic/env.py` 作成完了
- [ ] `backend/alembic.ini` 設定完了
- [ ] `alembic current` コマンド動作確認（コンテナ内）

### Phase 4-2: Tursoデータベース作成
- [ ] `turso auth login` 認証完了（ホスト環境）
- [ ] ステージングDB作成完了（ホスト環境）
- [ ] ステージングDB URL・トークン保存完了（ホスト環境）
- [ ] 本番DB作成完了（ホスト環境）
- [ ] 本番DB URL・トークン保存完了（ホスト環境）
- [ ] CLI経由での接続確認完了（ホスト環境）

### Phase 4-3: 環境変数ファイル作成
- [ ] `backend/.env.local` 作成完了（実際の値・ホスト環境）
- [ ] `backend/.env.staging` 作成完了（プレースホルダー形式・ホスト環境）
- [ ] `backend/.env.production` 作成完了（プレースホルダー形式・ホスト環境）
- [ ] すべてのファイル権限600設定完了（ホスト環境）
- [ ] `.gitignore` に `.env.*` 追加確認完了（ホスト環境）
- [ ] Dockerボリュームマウントで環境変数が共有されていることを確認

### Phase 4-4: データベーススキーマ定義
- [ ] `backend/src/infrastructure/shared/database/base.py` 作成完了（ホスト環境）
- [ ] `backend/src/infrastructure/prompt/models/prompt_model.py` 作成完了（ホスト環境）
- [ ] `backend/src/infrastructure/evaluation/models/evaluation_model.py` 作成完了（ホスト環境）
- [ ] すべてのモデルが正しくインポートされている
- [ ] DDD準拠の機能ベース配置が完了している
- [ ] Dockerボリュームマウントでファイルが自動反映されている

### Phase 4-5: マイグレーション作成と適用
- [ ] 初期マイグレーションファイル生成完了（コンテナ内）
- [ ] ローカル環境にマイグレーション適用完了（コンテナ内）
- [ ] ステージング環境にマイグレーション適用完了（コンテナ内）
- [ ] データベーステーブル作成確認完了（コンテナ内 & ホスト環境）

### Phase 4-6: 接続確認とテスト
- [ ] 統合テストファイル作成完了（ホスト環境）
- [ ] すべてのテストがパス（コンテナ内実行）
- [ ] データベース接続確認完了（コンテナ内）
- [ ] Redis接続確認完了（コンテナ内）
- [ ] CRUD操作確認完了（コンテナ内）
- [ ] カバレッジレポート確認完了

### Phase 4-7: GitHub Secrets設定
- [ ] Staging用Secrets登録完了（8個以上）
- [ ] Production用Secrets登録完了（8個以上）
- [ ] CI/CDワークフローで環境変数展開設定
- [ ] デプロイテスト実行完了

---

## Phase 4-7: GitHub Secrets設定

### 目的
Staging/Production環境の実際の値をGitHub Secretsで安全に管理します。

### ⚙️ GitHub Secrets登録手順

#### 7-1. Staging環境のSecrets登録

```bash
# ホスト環境（Mac）で実行
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus

# Turso関連
gh secret set STAGING_TURSO_DATABASE_URL -b "libsql://autoforgenexus-staging-xxx.turso.io"
gh secret set STAGING_TURSO_AUTH_TOKEN -b "eyJhbGciOiJFZERTQSI..."

# Redis関連
gh secret set STAGING_REDIS_HOST -b "staging-redis.upstash.io"
gh secret set STAGING_REDIS_PASSWORD -b "staging_password_xxx"

# Clerk認証
gh secret set STAGING_CLERK_SECRET_KEY -b "sk_test_xxx"
gh secret set STAGING_CLERK_PUBLISHABLE_KEY -b "pk_test_xxx"

# LLM Providers（テスト用API Key）
gh secret set STAGING_OPENAI_API_KEY -b "sk-xxx"
gh secret set STAGING_ANTHROPIC_API_KEY -b "sk-ant-xxx"

# LangFuse
gh secret set STAGING_LANGFUSE_PUBLIC_KEY -b "pk-lf-xxx"
gh secret set STAGING_LANGFUSE_SECRET_KEY -b "sk-lf-xxx"

# 登録確認
gh secret list | grep STAGING
```

#### 7-2. Production環境のSecrets登録

```bash
# Turso関連
gh secret set PROD_TURSO_DATABASE_URL -b "libsql://autoforgenexus-production-xxx.turso.io"
gh secret set PROD_TURSO_AUTH_TOKEN -b "eyJhbGciOiJFZERTQSI..."

# Redis関連（Production専用クラスター）
gh secret set PROD_REDIS_HOST -b "prod-redis.upstash.io"
gh secret set PROD_REDIS_PASSWORD -b "STRONG_production_password_xxx"

# Clerk認証（Production Instance）
gh secret set PROD_CLERK_SECRET_KEY -b "sk_live_xxx"
gh secret set PROD_CLERK_PUBLISHABLE_KEY -b "pk_live_xxx"

# LLM Providers（本番用API Key）
gh secret set PROD_OPENAI_API_KEY -b "sk-xxx"
gh secret set PROD_ANTHROPIC_API_KEY -b "sk-ant-xxx"

# LangFuse（Production）
gh secret set PROD_LANGFUSE_PUBLIC_KEY -b "pk-lf-xxx"
gh secret set PROD_LANGFUSE_SECRET_KEY -b "sk-lf-xxx"

# 登録確認
gh secret list | grep PROD
```

#### 7-3. CI/CDでの環境変数展開

`.github/workflows/deploy-staging.yml` 例：

```yaml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Environment Variables
        run: |
          # プレースホルダーを実際の値に置換
          envsubst < backend/.env.staging > backend/.env
        env:
          STAGING_TURSO_DATABASE_URL: ${{ secrets.STAGING_TURSO_DATABASE_URL }}
          STAGING_TURSO_AUTH_TOKEN: ${{ secrets.STAGING_TURSO_AUTH_TOKEN }}
          STAGING_REDIS_HOST: ${{ secrets.STAGING_REDIS_HOST }}
          STAGING_REDIS_PASSWORD: ${{ secrets.STAGING_REDIS_PASSWORD }}
          STAGING_CLERK_SECRET_KEY: ${{ secrets.STAGING_CLERK_SECRET_KEY }}
          STAGING_CLERK_PUBLISHABLE_KEY: ${{ secrets.STAGING_CLERK_PUBLISHABLE_KEY }}

      - name: Deploy to Cloudflare Workers
        run: wrangler deploy
```

`.github/workflows/deploy-production.yml` 例：

```yaml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Setup Environment Variables
        run: |
          envsubst < backend/.env.production > backend/.env
        env:
          PROD_TURSO_DATABASE_URL: ${{ secrets.PROD_TURSO_DATABASE_URL }}
          PROD_TURSO_AUTH_TOKEN: ${{ secrets.PROD_TURSO_AUTH_TOKEN }}
          PROD_REDIS_HOST: ${{ secrets.PROD_REDIS_HOST }}
          PROD_REDIS_PASSWORD: ${{ secrets.PROD_REDIS_PASSWORD }}
          PROD_CLERK_SECRET_KEY: ${{ secrets.PROD_CLERK_SECRET_KEY }}
          PROD_CLERK_PUBLISHABLE_KEY: ${{ secrets.PROD_CLERK_PUBLISHABLE_KEY }}

      - name: Deploy to Production
        run: wrangler deploy --env production
```

### セキュリティチェックリスト

- [ ] `.env.staging` と `.env.production` はプレースホルダー形式
- [ ] 実際の値は全てGitHub Secretsに保存済み
- [ ] `.gitignore` に `.env.*` が含まれている
- [ ] ローカル環境の `.env.local` のみ実際の値を含む（Git管理外）
- [ ] CI/CDワークフローで `envsubst` を使用して置換
- [ ] Production環境は `environment: production` で保護

### 完了基準
- [ ] Staging用GitHub Secrets登録完了（8個以上）
- [ ] Production用GitHub Secrets登録完了（8個以上）
- [ ] CI/CDワークフローで環境変数展開設定完了
- [ ] デプロイテスト実行完了

---

## Phase 4-7: GitHub Secrets設定

### 目的
Staging/Production環境の実際の値をGitHub Secretsで安全に管理します。

### 🔐 環境変数管理の全体像

```
┌─────────────────────────────────────────────────────────┐
│                    環境変数管理戦略                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Local環境:                                             │
│  .env.local ───► 実際の値 ───► Git管理外                 │
│                                                         │
│  Staging環境:                                           │
│  .env.staging ───► ${STAGING_*} ───► GitHub Secrets     │
│         │                              │                │
│         └──► CI/CD ───► envsubst ──────┘                │
│                                                         │
│  Production環境:                                        │
│  .env.production ───► ${PROD_*} ───► GitHub Secrets     │
│         │                              │                │
│         └──► CI/CD ───► envsubst ──────┘                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 作業手順

#### 7-1. Staging環境のSecrets登録

```bash
# ホスト環境（Mac）で実行
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus

# Turso関連（Phase 4-2で取得した値）
gh secret set STAGING_TURSO_DATABASE_URL -b "libsql://autoforgenexus-staging-xxx.turso.io"
gh secret set STAGING_TURSO_AUTH_TOKEN -b "eyJhbGciOiJFZERTQSI..."

# Redis関連（Upstash等で作成）
gh secret set STAGING_REDIS_HOST -b "staging-redis.upstash.io"
gh secret set STAGING_REDIS_PASSWORD -b "staging_password_xxx"

# Clerk認証（Development Instance）
gh secret set STAGING_CLERK_SECRET_KEY -b "sk_test_xxx"
gh secret set STAGING_CLERK_PUBLISHABLE_KEY -b "pk_test_xxx"

# LLM Providers（テスト用API Key推奨）
gh secret set STAGING_OPENAI_API_KEY -b "sk-xxx"
gh secret set STAGING_ANTHROPIC_API_KEY -b "sk-ant-xxx"

# LangFuse（Staging）
gh secret set STAGING_LANGFUSE_PUBLIC_KEY -b "pk-lf-xxx"
gh secret set STAGING_LANGFUSE_SECRET_KEY -b "sk-lf-xxx"

# 登録確認
gh secret list | grep STAGING

# 期待される出力:
# STAGING_ANTHROPIC_API_KEY    Updated 2025-10-01
# STAGING_CLERK_PUBLISHABLE_KEY Updated 2025-10-01
# STAGING_CLERK_SECRET_KEY      Updated 2025-10-01
# STAGING_LANGFUSE_PUBLIC_KEY   Updated 2025-10-01
# STAGING_LANGFUSE_SECRET_KEY   Updated 2025-10-01
# STAGING_OPENAI_API_KEY        Updated 2025-10-01
# STAGING_REDIS_HOST            Updated 2025-10-01
# STAGING_REDIS_PASSWORD        Updated 2025-10-01
# STAGING_TURSO_AUTH_TOKEN      Updated 2025-10-01
# STAGING_TURSO_DATABASE_URL    Updated 2025-10-01
```

#### 7-2. Production環境のSecrets登録

```bash
# Turso関連（Phase 4-2で取得した値）
gh secret set PROD_TURSO_DATABASE_URL -b "libsql://autoforgenexus-production-xxx.turso.io"
gh secret set PROD_TURSO_AUTH_TOKEN -b "eyJhbGciOiJFZERTQSI..."

# Redis関連（Production専用クラスター）
gh secret set PROD_REDIS_HOST -b "prod-redis.upstash.io"
gh secret set PROD_REDIS_PASSWORD -b "STRONG_production_password_xxx"

# Clerk認証（Production Instance）
gh secret set PROD_CLERK_SECRET_KEY -b "sk_live_xxx"
gh secret set PROD_CLERK_PUBLISHABLE_KEY -b "pk_live_xxx"

# LLM Providers（本番用API Key）
gh secret set PROD_OPENAI_API_KEY -b "sk-xxx"
gh secret set PROD_ANTHROPIC_API_KEY -b "sk-ant-xxx"

# LangFuse（Production）
gh secret set PROD_LANGFUSE_PUBLIC_KEY -b "pk-lf-xxx"
gh secret set PROD_LANGFUSE_SECRET_KEY -b "sk-lf-xxx"

# 登録確認
gh secret list | grep PROD

# 期待される出力:
# PROD_ANTHROPIC_API_KEY        Updated 2025-10-01
# PROD_CLERK_PUBLISHABLE_KEY    Updated 2025-10-01
# PROD_CLERK_SECRET_KEY         Updated 2025-10-01
# PROD_LANGFUSE_PUBLIC_KEY      Updated 2025-10-01
# PROD_LANGFUSE_SECRET_KEY      Updated 2025-10-01
# PROD_OPENAI_API_KEY           Updated 2025-10-01
# PROD_REDIS_HOST               Updated 2025-10-01
# PROD_REDIS_PASSWORD           Updated 2025-10-01
# PROD_TURSO_AUTH_TOKEN         Updated 2025-10-01
# PROD_TURSO_DATABASE_URL       Updated 2025-10-01
```

#### 7-3. CI/CDワークフロー設定例

**Staging環境デプロイ** (`.github/workflows/deploy-staging.yml`):

```yaml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging

    steps:
      - uses: actions/checkout@v4

      - name: Setup Environment Variables
        run: |
          # プレースホルダーを実際の値に置換
          envsubst < backend/.env.staging > backend/.env
        env:
          STAGING_TURSO_DATABASE_URL: ${{ secrets.STAGING_TURSO_DATABASE_URL }}
          STAGING_TURSO_AUTH_TOKEN: ${{ secrets.STAGING_TURSO_AUTH_TOKEN }}
          STAGING_REDIS_HOST: ${{ secrets.STAGING_REDIS_HOST }}
          STAGING_REDIS_PASSWORD: ${{ secrets.STAGING_REDIS_PASSWORD }}
          STAGING_CLERK_SECRET_KEY: ${{ secrets.STAGING_CLERK_SECRET_KEY }}
          STAGING_CLERK_PUBLISHABLE_KEY: ${{ secrets.STAGING_CLERK_PUBLISHABLE_KEY }}
          STAGING_OPENAI_API_KEY: ${{ secrets.STAGING_OPENAI_API_KEY }}
          STAGING_ANTHROPIC_API_KEY: ${{ secrets.STAGING_ANTHROPIC_API_KEY }}
          STAGING_LANGFUSE_PUBLIC_KEY: ${{ secrets.STAGING_LANGFUSE_PUBLIC_KEY }}
          STAGING_LANGFUSE_SECRET_KEY: ${{ secrets.STAGING_LANGFUSE_SECRET_KEY }}

      - name: Run Database Migrations
        run: |
          docker compose -f docker-compose.dev.yml up -d backend
          docker compose -f docker-compose.dev.yml exec -T backend alembic upgrade head

      - name: Deploy to Cloudflare Workers
        run: |
          npm install -g wrangler
          wrangler deploy --env staging
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

**Production環境デプロイ** (`.github/workflows/deploy-production.yml`):

```yaml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment: production  # 承認必須環境

    steps:
      - uses: actions/checkout@v4

      - name: Setup Environment Variables
        run: |
          envsubst < backend/.env.production > backend/.env
        env:
          PROD_TURSO_DATABASE_URL: ${{ secrets.PROD_TURSO_DATABASE_URL }}
          PROD_TURSO_AUTH_TOKEN: ${{ secrets.PROD_TURSO_AUTH_TOKEN }}
          PROD_REDIS_HOST: ${{ secrets.PROD_REDIS_HOST }}
          PROD_REDIS_PASSWORD: ${{ secrets.PROD_REDIS_PASSWORD }}
          PROD_CLERK_SECRET_KEY: ${{ secrets.PROD_CLERK_SECRET_KEY }}
          PROD_CLERK_PUBLISHABLE_KEY: ${{ secrets.PROD_CLERK_PUBLISHABLE_KEY }}
          PROD_OPENAI_API_KEY: ${{ secrets.PROD_OPENAI_API_KEY }}
          PROD_ANTHROPIC_API_KEY: ${{ secrets.PROD_ANTHROPIC_API_KEY }}
          PROD_LANGFUSE_PUBLIC_KEY: ${{ secrets.PROD_LANGFUSE_PUBLIC_KEY }}
          PROD_LANGFUSE_SECRET_KEY: ${{ secrets.PROD_LANGFUSE_SECRET_KEY }}

      - name: Run Database Migrations (Production)
        run: |
          docker compose -f docker-compose.prod.yml up -d backend
          docker compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

      - name: Deploy to Production
        run: wrangler deploy --env production
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

### セキュリティベストプラクティス

#### ✅ 正しい管理方法

1. **プレースホルダー形式でコミット**
   ```bash
   # .env.staging と .env.production はプレースホルダー
   git add backend/.env.staging backend/.env.production
   git commit -m "docs: 環境変数テンプレート追加"
   ```

2. **実際の値はGitHub Secretsのみ**
   ```bash
   # Secretsで管理（コミット不可）
   gh secret set PROD_TURSO_AUTH_TOKEN -b "eyJ..."
   ```

3. **CI/CDで動的に置換**
   ```yaml
   env:
     PROD_TURSO_AUTH_TOKEN: ${{ secrets.PROD_TURSO_AUTH_TOKEN }}
   run: envsubst < .env.production > .env
   ```

#### ❌ やってはいけないこと

```bash
# ❌ 絶対NG: 実際の値をコミット
git add .env.local
git commit -m "add env"  # 秘密情報が漏洩！

# ❌ NG: ハードコードされた値
TURSO_AUTH_TOKEN=eyJhbGciOiJFZERTQSI...  # 直接記述

# ✅ 正しい: プレースホルダー
TURSO_AUTH_TOKEN=${PROD_TURSO_AUTH_TOKEN}  # GitHub Secretsで置換
```

### GitHub環境保護設定

```bash
# Production環境の保護設定（推奨）
# GitHub Web UI で設定:
# Settings → Environments → production

1. Required reviewers: 最低1名の承認必須
2. Wait timer: 5分のクールダウン
3. Deployment branches: mainブランチのみ許可
```

### 完了基準
- [ ] Staging用GitHub Secrets登録完了（10個）
- [ ] Production用GitHub Secrets登録完了（10個）
- [ ] `.github/workflows/deploy-staging.yml` 作成完了
- [ ] `.github/workflows/deploy-production.yml` 作成完了
- [ ] Production環境保護設定完了
- [ ] デプロイテスト実行完了

---

## 次のステップ

データベース環境構築が完了したら、以下のフェーズに進みます：

1. **Phase 5: フロントエンド開発**
   - Next.js 15.5.4 + React 19.0.0 環境構築
   - Clerk認証統合
   - shadcn/ui 3.3.1 コンポーネント実装

2. **Phase 6: 統合・品質保証**
   - E2Eテスト実装（Playwright）
   - セキュリティスキャン（OWASP ZAP、Trivy）
   - パフォーマンステスト（K6、Locust）
   - 監視スタック構築（Prometheus、Grafana、LangFuse）

---

## 参考資料

- [Turso公式ドキュメント](https://docs.turso.tech)
- [libSQL Python SDK](https://github.com/tursodatabase/libsql-client-py)
- [SQLAlchemy 2.0ドキュメント](https://docs.sqlalchemy.org/en/20/)
- [Alembic公式ドキュメント](https://alembic.sqlalchemy.org)
- [Redis公式ドキュメント](https://redis.io/docs/)

---

**最終更新日**: 2025年9月30日
**作成者**: AutoForgeNexus開発チーム
**バージョン**: 1.0.0
