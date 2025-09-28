# バックエンド ディレクトリ構造設計書

## 設計方針

### 機能ベース集約パターン（Feature-Based Aggregation）

**原則**: 関連する機能を1つのディレクトリ内に集約し、高い凝集性と低い結合性を実現

**メリット**:
- 機能追加・変更が局所的に完結
- 新メンバーが理解しやすい
- テストと実装の対応関係が明確
- マイクロサービス化が容易

## 新ディレクトリ構造

```
backend/
├── src/
│   ├── domain/                    # ドメイン層（ビジネスロジック）
│   │   ├── prompt/                # プロンプト管理集約
│   │   │   ├── __init__.py
│   │   │   ├── entities/         # プロンプトエンティティ
│   │   │   ├── value_objects/    # 値オブジェクト
│   │   │   ├── services/         # ドメインサービス
│   │   │   ├── repositories/     # リポジトリインターフェース
│   │   │   └── exceptions.py     # プロンプト固有例外
│   │   │
│   │   ├── evaluation/            # 評価機能集約
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   └── exceptions.py
│   │   │
│   │   ├── llm_integration/       # LLM統合集約
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   └── exceptions.py
│   │   │
│   │   ├── user_interaction/      # ユーザー操作集約
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   └── exceptions.py
│   │   │
│   │   ├── workflow/              # ワークフロー管理集約
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   └── exceptions.py
│   │   │
│   │   └── shared/                # 共通要素
│   │       ├── __init__.py
│   │       ├── base_entity.py    # 基底エンティティ
│   │       ├── base_value.py     # 基底値オブジェクト
│   │       ├── base_repository.py # 基底リポジトリ
│   │       ├── exceptions.py     # 共通例外
│   │       └── types.py          # 共通型定義
│   │
│   ├── application/               # アプリケーション層
│   │   ├── prompt/               # プロンプト関連ユースケース
│   │   │   ├── __init__.py
│   │   │   ├── commands/        # コマンド（書き込み）
│   │   │   │   ├── create_prompt.py
│   │   │   │   ├── update_prompt.py
│   │   │   │   └── delete_prompt.py
│   │   │   ├── queries/         # クエリ（読み取り）
│   │   │   │   ├── get_prompt.py
│   │   │   │   ├── list_prompts.py
│   │   │   │   └── search_prompts.py
│   │   │   └── services/        # アプリケーションサービス
│   │   │       └── prompt_workflow.py
│   │   │
│   │   ├── evaluation/           # 評価関連ユースケース
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   ├── queries/
│   │   │   └── services/
│   │   │
│   │   ├── llm_integration/      # LLM統合ユースケース
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   ├── queries/
│   │   │   └── services/
│   │   │
│   │   ├── user_interaction/     # ユーザー操作ユースケース
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   ├── queries/
│   │   │   └── services/
│   │   │
│   │   ├── workflow/              # ワークフロー管理ユースケース
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   ├── queries/
│   │   │   └── services/
│   │   │
│   │   └── shared/               # 共通アプリケーション要素
│   │       ├── __init__.py
│   │       ├── commands/        # 基底コマンドクラス
│   │       │   └── base.py
│   │       ├── queries/         # 基底クエリクラス
│   │       │   └── base.py
│   │       ├── services/        # 基底サービスクラス
│   │       │   └── base.py
│   │       ├── dto/             # データ転送オブジェクト
│   │       │   └── base.py
│   │       └── events/          # イベントバス
│   │           ├── __init__.py
│   │           └── event_bus.py
│   │
│   ├── core/                    # 横断的関心事層
│   │   ├── config/              # 設定管理
│   │   │   ├── settings/        # アプリケーション設定
│   │   │   ├── environments/    # 環境別設定
│   │   │   ├── validators/      # 設定検証
│   │   │   └── loaders/        # 設定読み込み
│   │   ├── security/            # セキュリティ
│   │   │   ├── authentication/  # 認証処理
│   │   │   ├── authorization/   # 認可処理
│   │   │   ├── encryption/      # 暗号化
│   │   │   └── validation/      # 入力検証
│   │   ├── exceptions/          # 例外管理
│   │   ├── logging/             # ログ管理
│   │   ├── middleware/          # ミドルウェア
│   │   ├── monitoring/          # 監視
│   │   └── dependencies/        # 依存性注入
│   │
│   ├── infrastructure/           # インフラストラクチャ層
│   │   ├── prompt/              # プロンプト関連実装
│   │   │   ├── __init__.py
│   │   │   ├── repositories/   # リポジトリ実装
│   │   │   │   ├── turso_prompt_repository.py
│   │   │   │   └── redis_cache_repository.py
│   │   │   └── adapters/       # 外部サービスアダプター
│   │   │       └── openai_adapter.py
│   │   │
│   │   ├── evaluation/          # 評価関連実装
│   │   │   ├── __init__.py
│   │   │   ├── repositories/
│   │   │   └── adapters/
│   │   │
│   │   ├── llm_integration/     # LLM統合実装
│   │   │   ├── __init__.py
│   │   │   ├── providers/      # LLMプロバイダー
│   │   │   │   ├── openai/
│   │   │   │   ├── anthropic/
│   │   │   │   └── litellm/
│   │   │   └── repositories/
│   │   │
│   │   ├── user_interaction/    # ユーザー操作実装
│   │   │   ├── __init__.py
│   │   │   ├── repositories/
│   │   │   └── adapters/
│   │   │
│   │   ├── workflow/            # ワークフロー実装
│   │   │   ├── __init__.py
│   │   │   ├── repositories/
│   │   │   └── engines/       # ワークフローエンジン
│   │   │       └── langraph_engine.py
│   │   │
│   │   └── shared/              # 共通インフラ要素
│   │       ├── __init__.py
│   │       ├── database/       # データベース接続
│   │       │   ├── turso.py
│   │       │   └── redis.py
│   │       ├── monitoring/     # 監視
│   │       │   └── langfuse.py
│   │       └── auth/          # 認証
│   │           └── clerk.py
│   │
│   └── presentation/            # プレゼンテーション層
│       ├── api/                # REST API
│       │   ├── __init__.py
│       │   ├── v1/            # APIバージョン1
│       │   │   ├── prompt/    # プロンプトAPI
│       │   │   │   ├── __init__.py
│       │   │   │   ├── router.py
│       │   │   │   ├── schemas.py
│       │   │   │   └── dependencies.py
│       │   │   ├── evaluation/ # 評価API
│       │   │   │   ├── __init__.py
│       │   │   │   ├── router.py
│       │   │   │   ├── schemas.py
│       │   │   │   └── dependencies.py
│       │   │   ├── llm/       # LLM統合API
│       │   │   │   ├── __init__.py
│       │   │   │   ├── router.py
│       │   │   │   ├── schemas.py
│       │   │   │   └── dependencies.py
│       │   │   ├── user/      # ユーザー操作API
│       │   │   │   ├── __init__.py
│       │   │   │   ├── router.py
│       │   │   │   ├── schemas.py
│       │   │   │   └── dependencies.py
│       │   │   └── workflow/  # ワークフローAPI
│       │   │       ├── __init__.py
│       │   │       ├── router.py
│       │   │       ├── schemas.py
│       │   │       └── dependencies.py
│       │   └── shared/        # 共通API要素
│       │       ├── __init__.py
│       │       ├── middleware.py
│       │       ├── exceptions.py
│       │       └── responses.py
│       │
│       ├── websocket/          # WebSocket
│       │   ├── __init__.py
│       │   ├── handlers/      # ハンドラー
│       │   │   ├── prompt_handler.py
│       │   │   └── evaluation_handler.py
│       │   └── manager.py     # 接続管理
│       │
│       └── main.py            # アプリケーションエントリーポイント
│
└── tests/                      # テスト
    ├── unit/                   # 単体テスト
    │   ├── domain/            # ドメイン層テスト
    │   │   ├── prompt/
    │   │   │   ├── entities/
    │   │   │   ├── value_objects/
    │   │   │   └── services/
    │   │   ├── evaluation/
    │   │   ├── llm_integration/
    │   │   ├── user_interaction/
    │   │   └── workflow/
    │   ├── application/       # アプリケーション層テスト
    │   │   ├── prompt/
    │   │   ├── evaluation/
    │   │   ├── llm_integration/
    │   │   ├── user_interaction/
    │   │   └── workflow/
    │   └── infrastructure/   # インフラ層テスト
    │       ├── prompt/
    │       ├── evaluation/
    │       ├── llm_integration/
    │       ├── user_interaction/
    │       └── workflow/
    │
    ├── integration/           # 統合テスト
    │   ├── api/
    │   ├── database/
    │   └── external/
    │
    └── e2e/                   # E2Eテスト
        ├── scenarios/
        └── fixtures/
```

## 設計原則

### 1. 機能単位の集約

各機能（prompt、evaluation、llm_integration等）は独立したモジュールとして：
- entities、value_objects、services、repositoriesを内包
- 機能固有の例外を定義
- 外部への依存は最小限に

### 2. レイヤー間の明確な責務

- **Domain層**: ビジネスロジック、ビジネスルール
- **Application層**: ユースケース、ワークフロー調整
- **Infrastructure層**: 外部サービス統合、永続化
- **Presentation層**: API、WebSocket、入出力変換

### 3. CQRS原則

Application層でCommand（書き込み）とQuery（読み取り）を分離：
- commands/: データ変更操作
- queries/: データ取得操作
- services/: 複雑なワークフロー

### 4. 依存関係の方向

```
Presentation → Application → Domain
     ↓             ↓           ↑
Infrastructure ←──────────────┘
```

## 移行ガイド

### Phase 1: ディレクトリ作成（完了済み: prompt）

prompt集約は既に移行完了

### Phase 2: 他の集約の作成

```bash
# 各集約のディレクトリ作成
mkdir -p src/domain/{evaluation,llm_integration,user_interaction,workflow}/{entities,value_objects,services,repositories}
mkdir -p src/application/{prompt,evaluation,llm_integration,user_interaction,workflow}/{commands,queries,services}
mkdir -p src/infrastructure/{prompt,evaluation,llm_integration,user_interaction,workflow}/{repositories,adapters}
mkdir -p src/presentation/api/v1/{prompt,evaluation,llm,user,workflow}
```

### Phase 3: 共通要素の配置

```bash
# shared ディレクトリの作成
mkdir -p src/domain/shared
mkdir -p src/application/shared/{commands,queries,services,dto,events}
mkdir -p src/infrastructure/shared/{database,monitoring,auth}
mkdir -p src/presentation/api/shared
```

### Phase 4: テスト構造の整備

```bash
# テストディレクトリの作成
mkdir -p tests/unit/{domain,application,infrastructure}/{prompt,evaluation,llm_integration,user_interaction,workflow}
mkdir -p tests/integration/{api,database,external}
mkdir -p tests/e2e/{scenarios,fixtures}
```

## ファイル命名規約

### エンティティ
- `{entity_name}.py` (例: prompt.py, evaluation_result.py)

### 値オブジェクト
- `{value_object_name}.py` (例: prompt_content.py, score.py)

### サービス
- `{service_name}_service.py` (例: prompt_generation_service.py)

### リポジトリ
- インターフェース: `{entity}_repository.py`
- 実装: `{technology}_{entity}_repository.py` (例: turso_prompt_repository.py)

### ユースケース
- コマンド: `{action}_{entity}.py` (例: create_prompt.py)
- クエリ: `{query_type}_{entity}.py` (例: get_prompt.py)

### API
- `router.py`: ルート定義
- `schemas.py`: Pydanticスキーマ
- `dependencies.py`: 依存性注入

## 利点

1. **高い凝集性**: 関連コードが1箇所に集約
2. **低い結合性**: 機能間の依存が最小限
3. **テスタビリティ**: テストと実装の対応が明確
4. **拡張性**: 新機能追加が容易
5. **マイクロサービス化**: 将来の分離が容易
6. **理解容易性**: 新メンバーが理解しやすい

## 注意事項

- 循環依存を避けるため、依存関係は必ず上位層から下位層へ
- 共通要素はsharedに配置し、重複を避ける
- 各集約は独立して開発・テスト可能にする