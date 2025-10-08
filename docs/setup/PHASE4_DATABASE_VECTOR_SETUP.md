# Phase 4: データベース・ベクトル環境構築

## 📋 このフェーズの概要

### 目的

AutoForgeNexusの永続化層とベクトル検索基盤を構築し、高性能なデータアクセスとAI機能のための埋め込み処理を実現します。

### 担当エージェント

#### **主要担当エージェント**

- **edge-database-administrator** (リーダー):
  Turso/libSQL設計・最適化、エッジデータベース管理
- **vector-database-specialist**: libSQL
  Vector管理、埋め込み戦略、類似度検索最適化
- **data-migration-specialist**: データ移行戦略、ETLパイプライン、ゼロダウンタイム移行

#### **支援エージェント**

- **backend-architect**: データ整合性設計、障害許容性、データアクセス層アーキテクチャ
- **performance-optimizer**: データベースパフォーマンス最適化、クエリチューニング
- **security-architect**: データベースセキュリティ、暗号化、アクセス制御
- **sre-agent-agent**: 運用監視、バックアップ戦略、障害対応
- **devops-coordinator**: Docker統合、CI/CD パイプライン、環境管理

### 関連AIコマンド

- `/ai:data:vector` - libSQL Vectorによるベクトルデータベース管理
- `/ai:data:analyze` - データ分析と洞察抽出
- `/ai:data:migrate` - ゼロダウンタイムデータ移行
- `/ai:operations:monitor` - データベースメトリクス監視
- `/ai:troubleshoot` - データベース問題診断

### 最終状態

- ✅ Turso (libSQL)による分散型メインデータベース稼働
- ✅ Redisによる高速キャッシュレイヤー構築
- ✅ libSQL Vectorでベクトル検索環境整備
- ✅ SQLAlchemy ORMとAlembicマイグレーション設定
- ✅ 開発・本番環境の分離とブランチング戦略確立
- ✅ 自動バックアップとレプリケーション体制構築

### 技術スタック

```yaml
データベース:
  メイン: Turso (libSQL) - 分散SQLite
  キャッシュ: Redis 7.4.1
  ベクトル: libSQL Vector Extension

ORM/マイグレーション:
  ORM: SQLAlchemy 2.0.32
  マイグレーション: Alembic 1.14.0

管理ツール:
  CLI: Turso CLI 0.97.1
  モニタリング: Redis Insight
  ベクトル管理: pgvector-python 0.3.7
```

---

## 🚀 事前準備チェックリスト

### 必須確認項目

```bash
# Phase 3完了確認
cat backend/.env.local | grep DATABASE_URL  # 環境変数準備確認
docker --version  # Docker 24.0以上
docker-compose --version  # Docker Compose 2.20以上
python --version  # Python 3.13確認

# M1 Mac固有の確認
uname -m  # 出力: arm64 を確認
arch  # 出力: arm64 を確認
softwareupdate --list  # macOS最新版確認

# Rosetta 2確認（x86_64互換レイヤー）
/usr/bin/pgrep oahd >/dev/null 2>&1 && echo "Rosetta 2: Installed" || echo "Rosetta 2: Not installed"
# インストールが必要な場合:
# softwareupdate --install-rosetta --agree-to-license

# 利用可能リソース確認（macOS用）
df -h  # 20GB以上の空き容量
sysctl hw.memsize | awk '{print $2/1073741824 " GB"}'  # 8GB以上のメモリ
sysctl -n hw.ncpu  # CPU コア数確認

# ネットワーク確認
curl -I https://api.turso.tech  # Turso API接続確認
```

### 環境変数テンプレート準備

```bash
# backend/.env.localに追加（セキュアな設定）
cat >> backend/.env.local << 'EOF'

# === Database Configuration ===
# Turso (Primary Database)
TURSO_DATABASE_URL="libsql://[database]-[organization].turso.io"
TURSO_AUTH_TOKEN="[your-auth-token]"
TURSO_SYNC_URL="https://[database]-[organization].turso.io"

# Redis Cache (セキュリティ強化)
REDIS_URL="redis://localhost:6379/0"
REDIS_PASSWORD="$(openssl rand -base64 32)"  # 自動生成される強力なパスワード
REDIS_SSL="false"  # ローカル開発
REDIS_DB=0
REDIS_MAX_RETRIES=3
REDIS_RETRY_DELAY=1000

# Vector Database
VECTOR_DIMENSION=1536  # OpenAI埋め込みサイズ
VECTOR_INDEX_TYPE="hnsw"  # 高速近似最近傍探索
VECTOR_METRIC="cosine"  # 類似度メトリック

# Database Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_ECHO=false  # 開発時はtrueで SQL ログ出力

# Migration Settings
ALEMBIC_CONFIG="backend/alembic.ini"
ALEMBIC_MIGRATION_DIR="backend/migrations"
EOF
```

### Claude Agentの活用準備

```bash
# 関連エージェントの確認
/ai:data:vector --help  # ベクトルDB管理
/ai:data:migrate --help  # データ移行
/ai:operations:deploy --help  # デプロイ設定
```

---

## 1️⃣ Turso (libSQL)セットアップ

### 担当エージェント

- **主担当**: edge-database-administrator
- **支援**: backend-architect, devops-coordinator

### 背景・目的

Turso
(libSQL)は分散SQLiteベースのデータベースで、エッジコンピューティングに最適化されています。グローバルなレプリケーション、低レイテンシアクセス、SQLiteの信頼性を組み合わせた次世代データベースです。

### 使用コマンド

```bash
# データベース設計と構造確認
/ai:architecture:design --database-structure

# 初期スキーマの最適化
/ai:data:analyze --schema-optimization
```

### 1.1 Turso CLIインストール（M1 Mac対応）

```bash
# M1 Mac (Apple Silicon)
# ARM64ネイティブビルドを優先
brew install tursodatabase/tap/turso

# インストール後のアーキテクチャ確認
file $(which turso)
# 期待出力: Mach-O 64-bit executable arm64

# もしx86_64版がインストールされた場合
brew uninstall turso
brew install --build-from-source tursodatabase/tap/turso

# Linux
curl -sSfL https://get.tur.so/install.sh | bash

# Windows (WSL2)
curl -sSfL https://get.tur.so/install.sh | bash

# インストール確認
turso --version
# 期待出力: turso 0.97.1 (arm64)
```

### 1.2 Tursoアカウント設定

```bash
# サインアップ/ログイン
turso auth signup  # 新規の場合
# または
turso auth login  # 既存アカウント

# 認証確認
turso account show
# 期待出力:
# Email: your-email@example.com
# Plan: Starter (または他のプラン)
```

### 1.3 データベース作成

```bash
# 本番データベース作成
turso db create autoforgenexus-prod \
  --location nrt  # 東京リージョン

# 開発データベース作成（本番のレプリカ）
turso db create autoforgenexus-dev \
  --from-db autoforgenexus-prod

# ステージング環境
turso db create autoforgenexus-staging \
  --from-db autoforgenexus-prod

# データベース一覧確認
turso db list
# 期待出力:
# NAME                    LOCATIONS  SIZE
# autoforgenexus-prod     nrt        0 B
# autoforgenexus-dev      nrt        0 B
# autoforgenexus-staging  nrt        0 B
```

### 1.4 接続情報取得

```bash
# 本番DB接続情報
turso db show autoforgenexus-prod --url
turso db tokens create autoforgenexus-prod

# 開発DB接続情報
turso db show autoforgenexus-dev --url
turso db tokens create autoforgenexus-dev

# 接続テスト
turso db shell autoforgenexus-dev "SELECT 1"
# 期待出力: 1
```

### 1.5 libSQL Vector Extension有効化（修正版）

```bash
# Vector拡張インストール
turso db shell autoforgenexus-dev << 'EOF'
-- Vector拡張有効化（正しい構文）
CREATE VIRTUAL TABLE IF NOT EXISTS vec_items
USING vec0(
  embedding FLOAT[1536]
);

-- メタデータカラムを別テーブルで管理
CREATE TABLE IF NOT EXISTS vec_items_metadata (
    id TEXT PRIMARY KEY,
    vec_id INTEGER REFERENCES vec_items(rowid),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- HNSWパラメータ最適化
CREATE TABLE IF NOT EXISTS vec_config (
    key TEXT PRIMARY KEY,
    value TEXT
);

INSERT OR REPLACE INTO vec_config VALUES
    ('hnsw_m', '16'),  -- 接続数（精度と速度のバランス）
    ('hnsw_ef_construction', '200'),  -- 構築時の探索幅
    ('hnsw_ef_search', '50');  -- 検索時の探索幅

-- 確認
SELECT name, sql FROM sqlite_master
WHERE type='table' AND name LIKE 'vec_%';
EOF
```

### 1.6 初期スキーマ設定

```bash
# backend/sql/001_initial_schema.sql作成
cat > backend/sql/001_initial_schema.sql << 'EOF'
-- ユーザーテーブル
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    clerk_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    username TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

-- プロンプトテーブル
CREATE TABLE IF NOT EXISTS prompts (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    status TEXT CHECK(status IN ('draft', 'active', 'archived')) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

-- プロンプト埋め込みテーブル
CREATE TABLE IF NOT EXISTS prompt_embeddings (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    prompt_id TEXT NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    embedding BLOB NOT NULL,  -- 1536次元ベクトル
    model TEXT DEFAULT 'text-embedding-ada-002',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 評価結果テーブル
CREATE TABLE IF NOT EXISTS evaluations (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    prompt_id TEXT NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    score REAL NOT NULL,
    metrics JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX idx_users_clerk_id ON users(clerk_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_prompts_user_id ON prompts(user_id);
CREATE INDEX idx_prompts_status ON prompts(status);
CREATE INDEX idx_prompt_embeddings_prompt_id ON prompt_embeddings(prompt_id);
CREATE INDEX idx_evaluations_prompt_id ON evaluations(prompt_id);
EOF

# スキーマ適用
turso db shell autoforgenexus-dev < backend/sql/001_initial_schema.sql
```

---

## 2️⃣ Redis環境構築

### 担当エージェント

- **主担当**: backend-architect
- **支援**: performance-optimizer, sre-agent-agent

### 背景・目的

Redisは高速インメモリデータストアで、キャッシング、セッション管理、リアルタイム機能のバックボーンとして機能します。Pub/Sub機能により、イベント駆動アーキテクチャの実装も可能です。

### 使用コマンド

```bash
# キャッシュ戦略の設計
/ai:architecture:design --cache-strategy

# パフォーマンス最適化
/ai:operations:monitor --redis-metrics
```

### 2.1 Redisインストール（M1 Mac最適化）

```bash
# M1 Mac (ARM64ネイティブ)
brew install redis

# ARM64最適化設定を追加
echo "io-threads 4" >> /opt/homebrew/etc/redis.conf
echo "io-threads-do-reads yes" >> /opt/homebrew/etc/redis.conf

# サービス起動
brew services start redis

# インストール確認
redis-server --version
# 期待出力: Redis server v=7.4.1 ... (arm64)

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server

# 動作確認
redis-cli ping
# 期待出力: PONG

# パフォーマンステスト（M1 Mac用）
redis-benchmark -q -n 100000
# M1での期待値: SET: 100000+ requests per second
```

### 2.2 Redis設定ファイル（セキュア版）

```bash
# backend/config/redis.conf作成
cat > backend/config/redis.conf << 'EOF'
# 基本設定（セキュリティ強化）
bind 127.0.0.1 ::1
protected-mode yes
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300

# 認証設定（必須）
requirepass $(openssl rand -base64 32)

# ACL設定
aclfile /opt/homebrew/etc/redis-acl.conf

# メモリ管理
maxmemory 2gb
maxmemory-policy allkeys-lru

# 永続化設定（開発環境）
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./data/redis

# ログ設定
loglevel notice
logfile ./logs/redis.log

# スローログ
slowlog-log-slower-than 10000
slowlog-max-len 128

# クライアント管理
maxclients 10000

# パフォーマンス
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
EOF

# Redis起動（設定ファイル指定）
redis-server backend/config/redis.conf
```

### 2.3 Redis接続テスト

```bash
# Python接続テスト
python << 'EOF'
import redis
import json

# 接続
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 基本操作テスト
r.set('test_key', 'test_value')
print(f"SET結果: {r.get('test_key')}")

# JSON操作
test_data = {"name": "AutoForgeNexus", "type": "AI Platform"}
r.set('test_json', json.dumps(test_data))
retrieved = json.loads(r.get('test_json'))
print(f"JSON結果: {retrieved}")

# 削除
r.delete('test_key', 'test_json')
print("テストデータ削除完了")
EOF
```

### 2.4 Redisクラスター設定（本番用）

```bash
# backend/config/redis-cluster.conf
cat > backend/config/redis-cluster.conf << 'EOF'
# クラスター設定
cluster-enabled yes
cluster-config-file nodes-6379.conf
cluster-node-timeout 5000
cluster-replica-validity-factor 10
cluster-migration-barrier 1
cluster-require-full-coverage yes

# レプリケーション
replicaof no one
replica-read-only yes
replica-serve-stale-data yes
EOF
```

---

## 3️⃣ libSQL Vector設定

### 担当エージェント

- **主担当**: vector-database-specialist
- **支援**: prompt-engineering-specialist, llm-integration

### 背景・目的

libSQL
VectorはSQLiteベースのベクトルデータベース拡張で、AI埋め込みの高速検索を実現します。OpenAI、Cohere、HuggingFaceなどの埋め込みモデルと統合し、セマンティック検索やRAG（Retrieval-Augmented
Generation）の基盤となります。

### 使用コマンド

```bash
# ベクトルDB初期化
/ai:data:vector --init --dimension 1536 --model "text-embedding-3-small"

# 埋め込み戦略の設計
/ai:prompt:create --embedding-strategy

# ベクトル検索の最適化
/ai:data:vector --optimize-index
```

### 3.1 Vectorライブラリインストール（M1 Mac対応）

```bash
# M1 Mac用の依存関係インストール
# NumPyのARM64最適化版を確認
pip install --upgrade pip

# ARM64ネイティブビルドのNumPy
pip install numpy==1.26.4 --no-binary :all: --compile

# libSQL experimental（ARM64サポート確認）
pip install libsql-experimental==0.0.30

# Sentence Transformers（PyTorch ARM64版を使用）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers==3.3.1

# OpenAI埋め込み用（代替）
pip install openai==1.55.3
pip install tiktoken==0.8.0

# 依存関係とアーキテクチャ確認
pip show numpy | grep Location
file $(python -c "import numpy; print(numpy.__file__)")
# 期待: Mach-O 64-bit ... arm64
```

### 3.2 Vector初期化スクリプト（改良版）

```python
# backend/database/vector_setup.py
cat > backend/database/vector_setup.py << 'EOF'
"""libSQL Vector初期化とテスト（M1 Mac最適化）"""
import libsql_experimental as libsql
import numpy as np
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging

# OpenAI埋め込みを使用（本番推奨）
try:
    from openai import OpenAI
    USE_OPENAI = True
except ImportError:
    from sentence_transformers import SentenceTransformer
    USE_OPENAI = False

load_dotenv('.env.local')

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDatabase:
    def __init__(self):
        self.conn = libsql.connect(
            database=os.getenv("TURSO_DATABASE_URL"),
            auth_token=os.getenv("TURSO_AUTH_TOKEN")
        )

        if USE_OPENAI:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.embedding_model = "text-embedding-3-small"  # 1536次元
            self.dimension = 1536
        else:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.dimension = 384  # MiniLMの次元

        logger.info(f"Vector DB initialized with {'OpenAI' if USE_OPENAI else 'SentenceTransformers'}")

    def create_collection(self, name: str, dimension: int = None):
        """ベクトルコレクション作成（改良版）"""
        if dimension is None:
            dimension = self.dimension

        cursor = self.conn.cursor()

        # ベクトルテーブル作成
        cursor.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS {name}_vectors
            USING vec0(
                embedding FLOAT[{dimension}]
            )
        """)

        # メタデータテーブル作成
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {name}_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vec_rowid INTEGER,
                content TEXT,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        logger.info(f"Collection '{name}' created with dimension {dimension}")

    def insert_vector(self, collection: str, text: str, metadata: dict = None):
        """テキストをベクトル化して挿入"""
        embedding = self.model.encode(text)
        cursor = self.conn.cursor()
        cursor.execute(f"""
            INSERT INTO {collection}_vectors (embedding, metadata)
            VALUES (?, ?)
        """, (embedding.tolist(), json.dumps(metadata or {})))
        self.conn.commit()

    def search_similar(self, collection: str, query: str, k: int = 5):
        """類似ベクトル検索"""
        query_embedding = self.model.encode(query)
        cursor = self.conn.cursor()
        results = cursor.execute(f"""
            SELECT id, metadata, distance
            FROM {collection}_vectors
            WHERE embedding MATCH ?
            ORDER BY distance
            LIMIT ?
        """, (query_embedding.tolist(), k))
        return results.fetchall()

    def test_setup(self):
        """セットアップテスト"""
        # テストコレクション作成
        self.create_collection("test", 384)  # MiniLMの次元数

        # サンプルデータ挿入
        samples = [
            "AIプロンプト最適化システム",
            "機械学習モデルのファインチューニング",
            "自然言語処理の応用"
        ]

        for text in samples:
            self.insert_vector("test", text, {"text": text})

        # 検索テスト
        results = self.search_similar("test", "プロンプトエンジニアリング", k=2)
        print("\n検索結果:")
        for r in results:
            print(f"  - {r}")

if __name__ == "__main__":
    vdb = VectorDatabase()
    vdb.test_setup()
EOF

# 実行テスト
python backend/database/vector_setup.py
```

### 3.3 埋め込みモデル設定

```bash
# AIコマンドでベクトルDB管理
/ai:data:vector --init --dimension 1536 --model "text-embedding-ada-002"

# 設定確認
/ai:data:vector --status
```

---

## 4️⃣ SQLAlchemy・Alembic設定

### 担当エージェント

- **主担当**: backend-developer
- **支援**: domain-modeller, database-administrator

### 背景・目的

SQLAlchemy 2.0はPythonの最新ORM（Object-Relational
Mapping）で、型安全性と非同期サポートを提供します。Alembicと組み合わせることで、データベーススキーマのバージョン管理と安全なマイグレーションを実現します。

### 使用コマンド

```bash
# ドメインモデルの設計
/ai:requirements:domain --entity-mapping

# マイグレーション戦略
/ai:data:migrate --strategy-design
```

### 4.1 SQLAlchemy設定

```python
# backend/database/base.py
cat > backend/database/base.py << 'EOF'
"""データベース基本設定"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

# データベースURL構築
DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

# 接続URL作成（libSQL用）
if DATABASE_URL and AUTH_TOKEN:
    connection_url = f"{DATABASE_URL}?authToken={AUTH_TOKEN}"
else:
    # フォールバック（ローカルSQLite）
    connection_url = "sqlite:///./backend/data/local.db"

# エンジン作成
engine = create_engine(
    connection_url,
    poolclass=QueuePool,
    pool_size=int(os.getenv("DB_POOL_SIZE", 20)),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", 40)),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", 30)),
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", 3600)),
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    connect_args={
        "check_same_thread": False,  # SQLite用
        "timeout": 30
    } if "sqlite" in connection_url else {}
)

# セッション設定
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ベースクラス
Base = declarative_base()

# WALモード設定（SQLite/libSQL用）
if "sqlite" in connection_url or "libsql" in connection_url:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

def get_db() -> Session:
    """データベースセッション取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# テスト接続
if __name__ == "__main__":
    with SessionLocal() as session:
        result = session.execute("SELECT 1")
        print(f"Database connection test: {result.scalar()}")
EOF

# 接続テスト
python backend/database/base.py
```

### 4.2 Alembic初期化

```bash
# Alembic初期化
cd backend
alembic init migrations

# alembic.ini設定
cat > alembic.ini << 'EOF'
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = driver://user:pass@localhost/dbname  # env.pyで上書き

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 88

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

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
EOF
```

### 4.3 Alembic環境設定

```python
# backend/migrations/env.py
cat > backend/migrations/env.py << 'EOF'
"""Alembic環境設定"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from database.base import Base, connection_url
from models import *  # すべてのモデルをインポート

config = context.config
fileConfig(config.config_file_name)

# メタデータ設定
target_metadata = Base.metadata

# 接続URL設定
config.set_main_option("sqlalchemy.url", connection_url)

def run_migrations_offline():
    """オフラインマイグレーション"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """オンラインマイグレーション"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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
EOF
```

### 4.4 初期マイグレーション作成

```bash
# 初期マイグレーション生成
alembic revision --autogenerate -m "Initial schema"

# マイグレーション適用
alembic upgrade head

# 現在のバージョン確認
alembic current
```

---

## 5️⃣ Docker統合

### 担当エージェント

- **主担当**: devops-coordinator
- **支援**: sre-agent-agent, edge-computing-specialist

### 背景・目的

Dockerによるコンテナ化により、開発環境の一貫性と本番環境への移行可能性を保証します。docker-composeによるマルチコンテナ管理で、データベース、キャッシュ、プロキシを統合的に管理します。

### 使用コマンド

```bash
# Docker環境の構築
/ai:operations:deploy --docker-setup

# コンテナ最適化
/sc:build --optimize-containers
```

### 5.1 Docker Compose設定（M1 Mac対応）

```yaml
# docker-compose.database.yml
cat > docker-compose.database.yml << 'EOF'
version: '3.9'

services:
  # Redis Cache (ARM64対応)
  redis:
    image: redis:7.4.1-alpine
    platform: linux/arm64  # M1 Mac用に明示的に指定
    container_name: autoforge_redis
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis:/data
      - ./backend/config/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    networks:
      - autoforge_network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD}

  # Redis Commander (管理UI - ARM64対応)
  redis-commander:
    image: rediscommander/redis-commander:latest
    platform: linux/arm64
    container_name: autoforge_redis_commander
    environment:
      - REDIS_HOSTS=local:redis:6379:0:${REDIS_PASSWORD}
      - HTTP_USER=admin
      - HTTP_PASSWORD=${REDIS_COMMANDER_PASSWORD:-admin}
    ports:
      - "8081:8081"
    networks:
      - autoforge_network
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped

  # Turso Edge Proxy (ARM64ネイティブ)
  turso-proxy:
    image: ghcr.io/tursodatabase/libsql-server:latest
    platform: linux/arm64
    container_name: autoforge_turso_proxy
    ports:
      - "8080:8080"
      - "5001:5001"
    environment:
      - SQLD_DB_PATH=/var/lib/sqld/data.db
      - SQLD_HTTP_LISTEN_ADDR=0.0.0.0:8080
      - SQLD_GRPC_LISTEN_ADDR=0.0.0.0:5001
      - SQLD_AUTH_JWT_KEY_FILE=/var/lib/sqld/jwt.key  # セキュリティ強化
    volumes:
      - ./data/turso:/var/lib/sqld
      - ./backend/config/jwt.key:/var/lib/sqld/jwt.key:ro
    networks:
      - autoforge_network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

networks:
  autoforge_network:
    driver: bridge

volumes:
  redis_data:
  turso_data:
EOF

# 起動
docker-compose -f docker-compose.database.yml up -d

# ステータス確認
docker-compose -f docker-compose.database.yml ps

# ログ確認
docker-compose -f docker-compose.database.yml logs -f
```

### 5.2 データベース初期化スクリプト

```bash
# backend/scripts/init_db.sh
cat > backend/scripts/init_db.sh << 'EOF'
#!/bin/bash
set -e

echo "🔧 データベース初期化開始..."

# 環境変数読み込み
source backend/.env.local

# Turso接続確認
echo "📡 Turso接続確認..."
turso db shell $TURSO_DATABASE_NAME "SELECT 1" || {
    echo "❌ Turso接続失敗"
    exit 1
}

# Redis接続確認
echo "📡 Redis接続確認..."
redis-cli ping || {
    echo "❌ Redis接続失敗"
    exit 1
}

# スキーマ適用
echo "📋 スキーマ適用..."
turso db shell $TURSO_DATABASE_NAME < backend/sql/001_initial_schema.sql

# Alembicマイグレーション
echo "🔄 マイグレーション実行..."
cd backend
alembic upgrade head
cd ..

# ベクトルDB初期化
echo "🎯 ベクトルDB初期化..."
python backend/database/vector_setup.py

# テストデータ投入（開発環境のみ）
if [ "$ENVIRONMENT" = "development" ]; then
    echo "📝 テストデータ投入..."
    python backend/scripts/seed_data.py
fi

echo "✅ データベース初期化完了!"
EOF

chmod +x backend/scripts/init_db.sh

# 実行
./backend/scripts/init_db.sh
```

---

## 6️⃣ 動作確認とテスト

### 担当エージェント

- **主担当**: test-automation-engineer
- **支援**: qa-coordinator, performance-optimizer

### 背景・目的

包括的な統合テストにより、データベース層の信頼性とパフォーマンスを検証します。自動化されたテストスイートは、継続的な品質保証の基盤となります。

### 使用コマンド

```bash
# テスト実行と品質レポート
/sc:test --integration --coverage

# パフォーマンステスト
/ai:operations:monitor --performance-test

# データ整合性検証
/ai:data:analyze --integrity-check
```

### 6.1 統合テストスクリプト

```python
# backend/tests/test_database_integration.py
cat > backend/tests/test_database_integration.py << 'EOF'
"""データベース統合テスト"""
import pytest
import asyncio
import redis
import libsql_experimental as libsql
from sqlalchemy import create_engine, text
import numpy as np
from sentence_transformers import SentenceTransformer
import time
import json
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

class DatabaseIntegrationTest:
    def __init__(self):
        self.results = []
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def test_turso_connection(self):
        """Turso接続テスト"""
        try:
            conn = libsql.connect(
                database=os.getenv("TURSO_DATABASE_URL"),
                auth_token=os.getenv("TURSO_AUTH_TOKEN")
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
            self.results.append("✅ Turso接続: 成功")
        except Exception as e:
            self.results.append(f"❌ Turso接続: {e}")

    def test_redis_operations(self):
        """Redis操作テスト"""
        try:
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)

            # 基本操作
            r.set('test:key', 'test_value', ex=60)
            assert r.get('test:key') == 'test_value'

            # JSON操作
            data = {"id": 1, "name": "test"}
            r.set('test:json', json.dumps(data))
            retrieved = json.loads(r.get('test:json'))
            assert retrieved == data

            # 削除
            r.delete('test:key', 'test:json')

            self.results.append("✅ Redis操作: 成功")
        except Exception as e:
            self.results.append(f"❌ Redis操作: {e}")

    def test_vector_operations(self):
        """ベクトル操作テスト"""
        try:
            conn = libsql.connect(
                database=os.getenv("TURSO_DATABASE_URL"),
                auth_token=os.getenv("TURSO_AUTH_TOKEN")
            )
            cursor = conn.cursor()

            # ベクトル挿入
            text = "テストプロンプト"
            embedding = self.model.encode(text)

            cursor.execute("""
                INSERT INTO test_vectors (embedding, metadata)
                VALUES (?, ?)
            """, (embedding.tolist(), json.dumps({"text": text})))

            # ベクトル検索
            query = "プロンプト最適化"
            query_embedding = self.model.encode(query)

            results = cursor.execute("""
                SELECT metadata, distance
                FROM test_vectors
                WHERE embedding MATCH ?
                ORDER BY distance
                LIMIT 3
            """, (query_embedding.tolist(),))

            assert results.fetchone() is not None
            self.results.append("✅ ベクトル操作: 成功")
        except Exception as e:
            self.results.append(f"❌ ベクトル操作: {e}")

    def test_sqlalchemy_orm(self):
        """SQLAlchemy ORM テスト"""
        try:
            from database.base import SessionLocal

            with SessionLocal() as session:
                # クエリテスト
                result = session.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                assert count is not None

                self.results.append("✅ SQLAlchemy ORM: 成功")
        except Exception as e:
            self.results.append(f"❌ SQLAlchemy ORM: {e}")

    def test_performance(self):
        """パフォーマンステスト"""
        try:
            conn = libsql.connect(
                database=os.getenv("TURSO_DATABASE_URL"),
                auth_token=os.getenv("TURSO_AUTH_TOKEN")
            )
            cursor = conn.cursor()

            # 書き込みパフォーマンス
            start = time.time()
            for i in range(100):
                cursor.execute(
                    "INSERT INTO test_perf (data) VALUES (?)",
                    (f"test_data_{i}",)
                )
            conn.commit()
            write_time = time.time() - start

            # 読み取りパフォーマンス
            start = time.time()
            cursor.execute("SELECT * FROM test_perf LIMIT 100")
            cursor.fetchall()
            read_time = time.time() - start

            self.results.append(f"✅ パフォーマンス: 書込{write_time:.2f}s, 読取{read_time:.2f}s")

            # クリーンアップ
            cursor.execute("DROP TABLE IF EXISTS test_perf")
            conn.commit()
        except Exception as e:
            self.results.append(f"❌ パフォーマンス: {e}")

    def run_all_tests(self):
        """全テスト実行"""
        print("\n🔬 データベース統合テスト開始\n")
        print("-" * 50)

        self.test_turso_connection()
        self.test_redis_operations()
        self.test_vector_operations()
        self.test_sqlalchemy_orm()
        self.test_performance()

        print("\n📊 テスト結果:")
        print("-" * 50)
        for result in self.results:
            print(result)

        # 成功/失敗カウント
        success = len([r for r in self.results if "✅" in r])
        failed = len([r for r in self.results if "❌" in r])

        print("-" * 50)
        print(f"\n総計: 成功 {success}/{len(self.results)}, 失敗 {failed}/{len(self.results)}")

        return failed == 0

if __name__ == "__main__":
    test = DatabaseIntegrationTest()
    success = test.run_all_tests()
    exit(0 if success else 1)
EOF

# テスト実行
python backend/tests/test_database_integration.py
```

### 6.2 ヘルスチェックエンドポイント

```python
# backend/api/health.py
cat > backend/api/health.py << 'EOF'
"""データベースヘルスチェック"""
from fastapi import APIRouter, HTTPException
import redis
import libsql_experimental as libsql
from database.base import SessionLocal
import os
import time

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/database")
async def check_database_health():
    """データベース健全性チェック"""
    health_status = {
        "turso": False,
        "redis": False,
        "vector": False,
        "timestamp": time.time()
    }

    # Turso確認
    try:
        with SessionLocal() as session:
            session.execute("SELECT 1")
            health_status["turso"] = True
    except Exception as e:
        health_status["turso_error"] = str(e)

    # Redis確認
    try:
        r = redis.Redis(host='localhost', port=6379)
        r.ping()
        health_status["redis"] = True
    except Exception as e:
        health_status["redis_error"] = str(e)

    # Vector DB確認
    try:
        conn = libsql.connect(
            database=os.getenv("TURSO_DATABASE_URL"),
            auth_token=os.getenv("TURSO_AUTH_TOKEN")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE name LIKE 'vec_%'")
        if cursor.fetchone():
            health_status["vector"] = True
    except Exception as e:
        health_status["vector_error"] = str(e)

    # 総合判定
    all_healthy = all([
        health_status["turso"],
        health_status["redis"],
        health_status["vector"]
    ])

    if not all_healthy:
        raise HTTPException(status_code=503, detail=health_status)

    return health_status
EOF
```

---

## 7️⃣ トラブルシューティング

### 担当エージェント

- **主担当**: root-cause-analyst
- **支援**: performance-engineer, sre-agent-agent

### 使用コマンド

```bash
# 問題診断
/ai:troubleshoot --database --deep-analysis

# パフォーマンス分析
/ai:operations:monitor --bottleneck-detection

# ログ分析
/sc:analyze --logs --pattern-detection
```

### M1 Mac固有の問題と解決策

#### Docker パフォーマンス問題

```bash
# エラー: Dockerが遅い、CPU使用率が高い
# 解決策:

# Docker Desktop設定最適化
cat > ~/.docker/daemon.json << 'EOF'
{
  "experimental": true,
  "features": {
    "buildkit": true
  },
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "cpu-rt-runtime": 95000,
  "cpu-rt-period": 100000
}
EOF

# Docker Desktop再起動
osascript -e 'quit app "Docker"'
sleep 5
open -a Docker
```

#### Python パッケージのARM64互換性

```bash
# エラー: ImportError: dlopen failed
# 解決策:

# Conda環境を使用（ARM64ネイティブ）
conda create -n autoforge python=3.13
conda activate autoforge
conda install -c conda-forge numpy scipy

# または、Rosetta 2経由でx86_64版を実行
arch -x86_64 pip install numpy
```

### よくある問題と解決策

#### Turso接続エラー

```bash
# エラー: Connection refused
# 解決策:
turso auth login  # 再認証
turso db show autoforgenexus-dev  # DB存在確認
curl -I https://api.turso.tech  # API到達確認

# M1 Macでのファイアウォール確認
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

#### Redis接続エラー

```bash
# エラー: Could not connect to Redis
# 解決策:
redis-cli ping  # Redis起動確認
ps aux | grep redis  # プロセス確認
sudo systemctl restart redis-server  # 再起動

# 設定確認
redis-cli CONFIG GET bind
redis-cli CONFIG GET protected-mode
```

#### ベクトル操作エラー

```bash
# エラー: Vector extension not found
# 解決策:
turso db shell autoforgenexus-dev << 'EOF'
-- 拡張再インストール
DROP TABLE IF EXISTS vec_items;
CREATE VIRTUAL TABLE vec_items
USING vec0(embedding float[1536]);
EOF

# Python パッケージ再インストール
pip uninstall libsql-experimental -y
pip install libsql-experimental==0.0.30
```

#### マイグレーションエラー

```bash
# エラー: Alembic migration failed
# 解決策:
alembic downgrade -1  # 1つ前に戻す
alembic history  # 履歴確認
alembic current  # 現在位置確認
alembic upgrade head  # 再実行

# リセット（開発環境のみ）
rm -rf backend/migrations/versions/*
alembic revision --autogenerate -m "Reset"
alembic upgrade head
```

#### パフォーマンス問題（M1 Mac最適化）

```bash
# Turso最適化（M1向けチューニング）
turso db shell autoforgenexus-dev << 'EOF'
PRAGMA cache_size = 20000;  # M1のメモリ帯域を活用
PRAGMA temp_store = MEMORY;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA mmap_size = 30000000000;  # 30GB mmap（M1の高速SSDを活用）
PRAGMA page_size = 8192;  # より大きなページサイズ
ANALYZE;  -- 統計更新
EOF

# Redis最適化（ARM64向け）
redis-cli << 'EOF'
CONFIG SET maxmemory 4gb
CONFIG SET maxmemory-policy allkeys-lru
CONFIG SET io-threads 4  # M1のマルチコア活用
CONFIG SET io-threads-do-reads yes
CONFIG SET save ""  # 永続化無効（高速化）
EOF

# システム最適化（macOS）
sudo sysctl -w kern.maxfiles=65536
sudo sysctl -w kern.maxfilesperproc=65536
sudo sysctl -w net.inet.tcp.msl=1000
```

### 診断コマンド集（M1 Mac対応）

```bash
# システムリソース確認（macOS）
sudo powermetrics --samplers cpu_power,gpu_power -i 1000 -n 1  # M1電力使用状況
top -o cpu  # CPU使用率順
sudo fs_usage -w | grep -E 'turso|redis'  # ファイルシステム監視
netstat -an | grep -E '6379|8080'  # ポート確認

# M1 固有のメモリ圧力確認
vm_stat 1  # メモリ統計
memory_pressure  # メモリ圧力テスト

# データベースサイズ確認
turso db show autoforgenexus-dev --size
redis-cli INFO memory | grep used_memory_human

# Docker リソース確認
docker stats --no-stream
docker system df

# ログ確認
tail -f backend/logs/database.log
docker-compose -f docker-compose.database.yml logs -f
```

---

## 8️⃣ ベストプラクティス

### 担当エージェント

- **主担当**: security-architect
- **支援**: compliance-officer, sre-agent-agent

### 使用コマンド

```bash
# セキュリティ監査
/ai:quality:security --audit --database

# コンプライアンスチェック
/ai:requirements:define --security-requirements
```

### セキュリティ（強化版）

```bash
# 1. 環境変数暗号化（macOS Keychain統合）
# backend/utils/secure_env.py
cat > backend/utils/secure_env.py << 'EOF'
"""セキュア環境変数管理（M1 Mac対応）"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
import subprocess
import base64
import json
from pathlib import Path

class SecureEnvManager:
    def __init__(self):
        self.keychain_service = "AutoForgeNexus"
        self.keychain_account = "env_encryption"

    def generate_key(self, password: str) -> bytes:
        """パスワードベースのキー生成"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'autoforge_salt_v1',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def store_in_keychain(self, key: str):
        """macOS Keychainにキーを保存"""
        subprocess.run([
            "security", "add-generic-password",
            "-a", self.keychain_account,
            "-s", self.keychain_service,
            "-w", key,
            "-U"  # 既存を更新
        ])

    def get_from_keychain(self) -> str:
        """macOS Keychainからキーを取得"""
        result = subprocess.run([
            "security", "find-generic-password",
            "-a", self.keychain_account,
            "-s", self.keychain_service,
            "-w"
        ], capture_output=True, text=True)
        return result.stdout.strip()

    def encrypt_env_file(self):
        """環境変数ファイル暗号化"""
        # マスターパスワード取得（または生成）
        import getpass
        password = getpass.getpass("Enter master password: ")

        key = self.generate_key(password)
        cipher = Fernet(key)

        # 暗号化
        with open('.env.local', 'rb') as f:
            encrypted = cipher.encrypt(f.read())

        # 保存
        with open('.env.local.enc', 'wb') as f:
            f.write(encrypted)

        # Keychainにキー保存
        self.store_in_keychain(key.decode())

        print("✅ Environment variables encrypted and key stored in macOS Keychain")

if __name__ == "__main__":
    manager = SecureEnvManager()
    manager.encrypt_env_file()
EOF

# 2. 接続制限
turso db update autoforgenexus-prod \
  --allowed-locations nrt,sin  # 特定リージョンのみ

# 3. 監査ログ
turso db audit autoforgenexus-prod --enable
```

### バックアップ戦略

```bash
# backend/scripts/backup_db.sh
cat > backend/scripts/backup_db.sh << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Tursoバックアップ
turso db dump autoforgenexus-prod > backups/turso_$TIMESTAMP.sql

# Redisバックアップ
redis-cli BGSAVE
cp data/redis/dump.rdb backups/redis_$TIMESTAMP.rdb

# S3アップロード（本番）
aws s3 cp backups/ s3://autoforge-backups/$TIMESTAMP/ --recursive

echo "✅ Backup completed: $TIMESTAMP"
EOF

# Cron設定（毎日2AM）
echo "0 2 * * * /path/to/backup_db.sh" | crontab -
```

### モニタリング設定（包括的）

```python
# backend/monitoring/db_metrics.py
cat > backend/monitoring/db_metrics.py << 'EOF'
"""データベースメトリクス収集（本番対応）"""
import prometheus_client as prom
import redis
import libsql_experimental as libsql
import psutil
import time
import json
import logging
from typing import Dict, Any
from datetime import datetime
import asyncio

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# メトリクス定義
db_connections = prom.Gauge('db_connections', 'Active DB connections', ['database'])
cache_hit_rate = prom.Gauge('cache_hit_rate', 'Redis cache hit rate')
query_duration = prom.Histogram('query_duration_seconds', 'Query execution time', ['operation'])
vector_search_latency = prom.Histogram('vector_search_latency_seconds', 'Vector search latency')
memory_usage = prom.Gauge('memory_usage_bytes', 'Memory usage', ['type'])
cpu_usage = prom.Gauge('cpu_usage_percent', 'CPU usage')

# アラート闾値
ALERT_THRESHOLDS = {
    'cpu_high': 80,
    'memory_high': 85,
    'cache_hit_low': 0.7,
    'query_slow': 1.0,  # 秒
    'connection_limit': 100
}

class DatabaseMonitor:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True
        )
        self.alerts = []

    async def collect_metrics(self):
        """メトリクス収集"""
        while True:
            try:
                # CPU/メモリ
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_usage.set(cpu_percent)

                mem = psutil.virtual_memory()
                memory_usage.labels(type='used').set(mem.used)
                memory_usage.labels(type='available').set(mem.available)

                # Redisメトリクス
                info = self.redis_client.info('stats')
                if info['keyspace_hits'] + info['keyspace_misses'] > 0:
                    hit_rate = info['keyspace_hits'] / (
                        info['keyspace_hits'] + info['keyspace_misses']
                    )
                    cache_hit_rate.set(hit_rate)

                    # アラートチェック
                    if hit_rate < ALERT_THRESHOLDS['cache_hit_low']:
                        self.trigger_alert('LOW_CACHE_HIT_RATE', hit_rate)

                # システムアラート
                if cpu_percent > ALERT_THRESHOLDS['cpu_high']:
                    self.trigger_alert('HIGH_CPU_USAGE', cpu_percent)

                if mem.percent > ALERT_THRESHOLDS['memory_high']:
                    self.trigger_alert('HIGH_MEMORY_USAGE', mem.percent)

            except Exception as e:
                logger.error(f"Metrics collection error: {e}")

            await asyncio.sleep(10)  # 10秒ごとに収集

    def trigger_alert(self, alert_type: str, value: Any):
        """アラート発火"""
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': alert_type,
            'value': value,
            'threshold': ALERT_THRESHOLDS.get(alert_type.lower().replace('_', ''), 'N/A')
        }

        self.alerts.append(alert)
        logger.warning(f"ALERT: {alert}")

        # Slack/Discord通知（実装例）
        # self.send_notification(alert)

    async def start_monitoring(self):
        """監視開始"""
        # Prometheusエンドポイント起動
        prom.start_http_server(9090)
        logger.info("Monitoring started on http://localhost:9090/metrics")

        # メトリクス収集開始
        await self.collect_metrics()

if __name__ == "__main__":
    monitor = DatabaseMonitor()
    asyncio.run(monitor.start_monitoring())
EOF

def collect_metrics():
    """メトリクス収集"""
    # 接続数
    # ... 実装

    # キャッシュヒット率
    r = redis.Redis()
    info = r.info('stats')
    hit_rate = info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses'])
    cache_hit_rate.set(hit_rate)

    # Prometheusエンドポイント起動
    prom.start_http_server(8000)
EOF
```

### 開発のコツ

```yaml
推奨事項:
  - ブランチ戦略: main/dev/feature-*でTursoDB分離
  - キャッシュ戦略: 頻繁アクセスデータは必ずRedis経由
  - ベクトル最適化: バッチ処理で埋め込み生成
  - インデックス: クエリパターン分析後に追加
  - 接続プール: 本番は必ず接続プール使用

避けるべきこと:
  - N+1クエリ問題
  - 同期的な大量データ処理
  - キャッシュなしの繰り返しクエリ
  - インデックスなしのフルスキャン
  - トランザクション内の外部API呼び出し
```

---

## ✅ 完了チェックリスト

### 必須項目

- [ ] Turso DBの3環境構築完了（dev/staging/prod）
- [ ] Redis起動とヘルスチェック成功
- [ ] libSQL Vector拡張有効化
- [ ] SQLAlchemy接続確認
- [ ] Alembic初期マイグレーション適用
- [ ] Docker Compose統合完了
- [ ] 統合テスト全項目パス
- [ ] バックアップスクリプト設定
- [ ] 環境変数すべて設定済み

### 確認コマンド

```bash
# 最終確認
/ai:data:analyze --health-check
python backend/tests/test_database_integration.py
curl http://localhost:8000/health/database

# パフォーマンス確認
/ai:operations:monitor --database-metrics
```

---

## 🎯 Phase 5への接続

データベース環境が構築できたら、次は[Phase 5: フロントエンド環境構築](./PHASE5_FRONTEND_ENVIRONMENT_SETUP.md)へ進んでください。

### Phase 5で使用する情報

```bash
# 以下の情報をPhase 5で使用
export NEXT_PUBLIC_DATABASE_URL=$TURSO_DATABASE_URL
export NEXT_PUBLIC_REDIS_URL=$REDIS_URL
export NEXT_PUBLIC_VECTOR_API_ENDPOINT="http://localhost:8000/api/v1/vectors"
```

### 統合ポイント

- APIエンドポイント: `http://localhost:8000`
- WebSocket: `ws://localhost:8000/ws`
- Redis Pub/Sub: `redis://localhost:6379`

---

## 📚 参考資料

- [Turso公式ドキュメント](https://docs.turso.tech)
- [libSQL Vector Guide](https://github.com/tursodatabase/libsql/blob/main/docs/vector.md)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

## 🆘 サポート

問題が発生した場合：

1. [トラブルシューティング](#7️⃣-トラブルシューティング)セクション確認
2. `backend/logs/`のログファイル確認
3. AIコマンド使用: `/ai:troubleshoot --database`
4. GitHub Issuesで報告

---

_Last Updated: 2024-12-24_ _Version: 1.0.0_
