# AutoForgeNexus Backend

Python 3.13 + FastAPI backend for AI prompt optimization platform.

## 🚀 Quick Start

```bash
# Local development
cd backend
python3.13 -m venv venv
source venv/bin/activate
pip install -e .[dev]
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Docker development
docker compose -f ../docker-compose.dev.yml up backend
```

## 📊 現在の実装状況 (2025年9月29日更新)

### ✅ 完了項目

- **基盤構築**: FastAPI 0.116.1 + Python 3.13環境構築
- **Docker環境**: 開発用docker-compose.dev.yml設定完了
- **プロジェクト構造**: DDD + Clean Architectureに基づくディレクトリ構造
- **設定管理**: Pydantic v2による階層型環境設定システム
- **テスト環境**: pytest + coverage設定（目標カバレッジ80%）
- **CI/CD基盤**: GitHub Actions最適化済み（52.3%コスト削減達成）
- **データベース準備**: Alembicマイグレーション環境構築

### 🚧 実装中

- **認証システム**: Clerk統合準備中
- **ドメインモデル**: プロンプト管理機能のエンティティ設計中

### 📋 未実装（今後の予定）

- LiteLLM統合（100+プロバイダー対応）
- CQRS実装（コマンド/クエリ分離）
- Redis Streamsイベントバス
- 並列評価実行システム
- バージョン管理機能

## 🏗️ Architecture

### 技術スタック

- **Framework**: FastAPI 0.116.1
- **Python**: 3.13
- **Database**: Turso (libSQL) / SQLite (dev)
- **Cache**: Redis 7.4.1
- **Architecture**: Clean Architecture with DDD
- **ORM**: SQLAlchemy 2.0.32
- **Validation**: Pydantic v2
- **Testing**: pytest 8.3.3 + coverage

### レイヤーアーキテクチャ

```
src/
├── domain/           # ドメイン層（ビジネスロジック）
├── application/      # アプリケーション層（ユースケース）
├── core/            # 横断的関心事（設定、セキュリティ等）
├── infrastructure/   # インフラ層（外部連携）
└── presentation/     # プレゼンテーション層（API）
```

## 📡 API Documentation

- **Development**: http://localhost:8000/docs (Swagger UI)
- **API Base**: http://localhost:8000/api/v1
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics (Prometheus形式)

## 🧪 Testing

```bash
# 単体テスト実行
pytest tests/unit/ -v

# 統合テスト実行
pytest tests/integration/ -v

# カバレッジレポート生成
pytest tests/ --cov=src --cov-report=html --cov-fail-under=80

# 品質チェック
ruff check src/ --fix      # Linting
ruff format src/           # フォーマット
mypy src/ --strict        # 型チェック
```

## 🔧 Development Commands

```bash
# 依存関係更新
pip install -e .[dev]

# データベースマイグレーション
alembic revision --autogenerate -m "Description"
alembic upgrade head

# 開発サーバー起動（ホットリロード付き）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Docker環境でのログ確認
docker compose -f ../docker-compose.dev.yml logs -f backend
```

## 📈 Performance Targets

- **API Response**: P95 < 200ms
- **Concurrent Connections**: 10,000+ (WebSocket)
- **Cache Hit Rate**: > 80%
- **Test Coverage**: > 80%
- **Memory Usage**: < 512MB per instance

## 🔐 Security Features

- JWT認証（Clerk統合予定）
- レート制限（60 req/min）
- CORS設定
- SQLインジェクション対策（SQLAlchemy ORM）
- 環境変数による秘匿情報管理

## 📝 Implementation Roadmap

### Phase 1: 基盤構築 ✅ 完了

- FastAPI環境構築
- Docker設定
- テスト環境整備
- CI/CD基本設定

### Phase 2: コア機能（実装中）

- ドメインモデル実装
- 基本CRUD API
- 認証システム統合

### Phase 3: 高度な機能（予定）

- LiteLLM統合
- CQRS実装
- イベント駆動アーキテクチャ
- 並列評価システム

## 🤝 Contributing

開発に参加する際は、必ず[CLAUDE.md](./CLAUDE.md)を参照してください。

## 📚 Related Documents

- [バックエンドアーキテクチャガイド](./CLAUDE.md)
- [プロジェクト全体README](../README.md)
- [環境構築ガイド](../docs/setup/DOCKER_ENVIRONMENT_SETUP.md)
- [API仕様書](../docs/api/)

## 🚀 CI/CD最適化の成果（2025年9月29日追加）

### GitHub Actions使用量削減

- **削減率**: 52.3%（3,200分/月 → 1,525分/月）
- **無料枠使用率**: 36.5%（730分/2,000分）
- **コスト削減**: $9.6/月（年間$115.2）

### 最適化内容

- 共有ワークフロー導入（Python/Node.js環境、ビルドキャッシュ）
- スケジュール頻度最適化（監視・セキュリティチェック）
- 並列実行による時間短縮（30分 → 15分）

### セキュリティ維持

- CodeQL分析継続（Python/TypeScript）
- TruffleHog秘密情報検出
- 監査ログ（365日保存）
- DORAメトリクス収集
