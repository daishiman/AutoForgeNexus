# Backend CLAUDE.md

このファイルは、AutoForgeNexusのバックエンドを作業する際のClaude Code (claude.ai/code) へのガイダンスを提供します。

## 🎯 バックエンド概要

Python 3.13 + FastAPI による高性能API実装。ドメイン駆動設計（DDD）とクリーンアーキテクチャに準拠。

## 🏗️ アーキテクチャ

### レイヤー構造

```
src/
├── domain/         # ビジネスロジック層（エンティティ、値オブジェクト、集約）
├── application/    # アプリケーション層（ユースケース、CQRS、イベントハンドラー）
├── infrastructure/ # インフラ層（Turso、Redis、LangFuse、外部API実装）
├── presentation/   # プレゼンテーション層（FastAPI、WebSocket、コントローラー）
├── monitoring.py   # ヘルスチェック・メトリクス
└── middleware/     # ミドルウェア（認証、監視、セキュリティ）
```

### 設計原則

- **DDD**: 境界づけられたコンテキスト、ユビキタス言語
- **CQRS**: コマンドとクエリの責任分離
- **Event Sourcing**: 全状態変更をイベントとして記録
- **依存性逆転**: ビジネスロジックはインフラに依存しない

## 🛠️ 技術スタック

- **Framework**: FastAPI 0.116.1
- **ORM**: SQLAlchemy 2.0.32
- **Validation**: Pydantic v2
- **Queue**: Redis Streams
- **Testing**: pytest 8.3.3 (coverage 80%+)
- **Linting**: Ruff 0.7.4
- **Type Check**: mypy 1.13.0 (--strict)

## 📁 主要ファイル説明

### src/monitoring.py
- **役割**: ヘルスチェックとシステムメトリクス
- **機能**:
  - 依存関係チェック（DB、Redis、LangFuse）
  - リソース使用状況（CPU、メモリ、ディスク）
  - 準備状態プローブ（/health、/ready、/live）

### src/middleware/observability.py
- **役割**: リクエスト追跡と監視
- **機能**:
  - 構造化ログ（相関ID付き）
  - LLMコール監視とコスト追跡
  - パフォーマンスメトリクス
  - PII保護とGDPR準拠

## 🚀 開発コマンド

```bash
# 環境セットアップ
python3.13 -m venv venv
source venv/bin/activate
pip install -e .[dev]

# 開発サーバー起動
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 品質チェック
ruff check src/ --fix          # Linting
ruff format src/               # フォーマット
mypy src/ --strict             # 型チェック
pytest tests/ --cov=src --cov-fail-under=80  # テスト実行

# データベースマイグレーション
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## ⚙️ 環境変数

必須設定項目（.env）:

```env
# Database
TURSO_DATABASE_URL=libsql://your-database.turso.io
TURSO_AUTH_TOKEN=your_turso_auth_token

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password

# Authentication
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key
CLERK_JWT_ISSUER=https://your-app.clerk.accounts.dev

# LLM Providers
OPENAI_API_KEY=sk-your_openai_api_key
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key

# Monitoring
LANGFUSE_SECRET_KEY=sk-lf-xxx
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
```

## 🔍 実装ガイドライン

### API エンドポイント設計

```python
# ✅ 正しい実装例
@router.post("/api/v1/prompts", response_model=PromptResponse)
async def create_prompt(
    prompt: PromptCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> PromptResponse:
    # ビジネスロジックはユースケースに委譲
    use_case = CreatePromptUseCase(db)
    result = await use_case.execute(prompt, user)
    return PromptResponse.from_domain(result)
```

### エラーハンドリング

```python
# ドメイン例外の定義
class PromptQuotaExceeded(DomainException):
    def __init__(self, user_id: str, limit: int):
        super().__init__(
            code="PROMPT_QUOTA_EXCEEDED",
            message=f"User {user_id} exceeded prompt limit of {limit}",
            status_code=429
        )
```

### 監視実装

```python
# LLM呼び出しの追跡
async with llm_middleware.track_llm_call(
    provider="openai",
    model="gpt-4",
    prompt=prompt_text,
    user_id=user.id
) as call_id:
    response = await openai_client.chat.completions.create(...)
    # 自動的にコストとレイテンシを記録
```

## 🧪 テスト戦略

### 単体テスト
```python
# tests/unit/test_prompt_service.py
async def test_create_prompt_validates_input():
    service = PromptService(mock_repo)
    with pytest.raises(ValidationError):
        await service.create_prompt(invalid_data)
```

### 統合テスト
```python
# tests/integration/test_api.py
async def test_prompt_creation_flow(client: TestClient):
    response = await client.post("/api/v1/prompts", json=prompt_data)
    assert response.status_code == 201
    assert response.json()["id"]
```

## 📊 品質基準

- **テストカバレッジ**: 80%以上必須
- **型安全性**: mypy strict モード準拠
- **コードスタイル**: Ruff フォーマット準拠
- **ドキュメント**: OpenAPI仕様自動生成
- **パフォーマンス**: API P95 < 200ms

## 🚨 注意事項

1. **セキュリティ**: 秘密情報をハードコードしない
2. **トランザクション**: 重要な操作は必ずトランザクション内で実行
3. **非同期処理**: I/O処理は必ずasync/awaitを使用
4. **ログ**: 構造化ログとPII保護を徹底
5. **エラー**: ドメイン例外を適切に定義・使用

## 🔗 関連ドキュメント

- [プロジェクトCLAUDE.md](../CLAUDE.md) - プロジェクト全体ガイド
- [インフラCLAUDE.md](../infrastructure/CLAUDE.md) - インフラ設定
- [API仕様書](http://localhost:8000/docs) - 開発サーバー起動後にアクセス