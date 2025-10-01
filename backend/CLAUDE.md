# AutoForgeNexus Backend Architecture Guide

このファイルは、バックエンド実装時の Claude Code (claude.ai/code) へのガイダンスを提供します。

## 🎯 このバックエンドが実現すること

### システムの目的
**「誰でも高品質なAIプロンプトを作成・最適化できる」を実現するバックエンド**

### 主要な要件と技術選定理由

| 要件 | 選定技術 | 理由 |
|------|---------|------|
| **高速レスポンス** | FastAPI + Redis | 非同期処理とキャッシングでP95 < 200ms実現 |
| **100+ LLM対応** | LiteLLM | 統一APIで全プロバイダー対応、コスト最適化 |
| **並列評価** | Redis Streams + CQRS | イベント駆動で10並列以上の評価を実現 |
| **バージョン管理** | Event Sourcing | Git-likeな履歴管理と改善追跡 |
| **品質保証** | DDD + Clean Architecture | ビジネスロジックの整合性とテスタビリティ |
| **スケーラビリティ** | マイクロサービス対応設計 | 将来の分離を想定した疎結合 |

## 🏗️ アーキテクチャ概要

### DDD境界づけられたコンテキスト

```
1. Prompt Engineering Context（プロンプト設計）
   - プロンプトの作成、最適化、バージョン管理
   
2. Evaluation Context（評価）
   - テスト実行、メトリクス分析、レポート生成
   
3. LLM Integration Context（AI連携）
   - 100+プロバイダー統合、リクエスト処理、コスト管理
   
4. User Interaction Context（ユーザー操作）
   - 人間-AI対話、フィードバック、協働作業
   
5. Data Management Context（データ管理）
   - プロンプト/履歴/テストケース永続化
```

## 📁 ディレクトリ構造

```
backend/
├── src/
│   ├── domain/           # ドメイン層（機能ベース集約）
│   │   ├── prompt/       # プロンプト管理機能
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   ├── services/
│   │   │   └── repositories/
│   │   ├── evaluation/   # 評価機能
│   │   ├── llm_integration/ # LLM統合
│   │   ├── user_interaction/ # ユーザー操作
│   │   ├── workflow/     # ワークフロー管理
│   │   └── shared/       # 共通要素
│   ├── application/      # アプリケーション層（CQRS適用）
│   │   ├── prompt/
│   │   │   ├── commands/  # コマンド（書き込み）
│   │   │   ├── queries/   # クエリ（読み取り）
│   │   │   └── services/  # ワークフロー調整
│   │   ├── evaluation/
│   │   ├── llm_integration/
│   │   ├── user_interaction/
│   │   ├── workflow/
│   │   └── shared/
│   │       ├── commands/  # 基底コマンド
│   │       ├── queries/   # 基底クエリ
│   │       ├── services/  # 基底サービス
│   │       ├── dto/       # DTO
│   │       └── events/    # イベントバス
│   ├── core/            # 横断的関心事
│   │   ├── config/      # 設定管理
│   │   │   ├── settings/, environments/, validators/, loaders/
│   │   ├── security/    # セキュリティ
│   │   │   ├── authentication/, authorization/, encryption/, validation/
│   │   ├── exceptions/  # 例外管理
│   │   ├── logging/     # ログ管理
│   │   ├── middleware/  # ミドルウェア
│   │   ├── monitoring/  # 監視
│   │   └── dependencies/# 依存性注入
│   ├── infrastructure/   # 外部連携層（機能ベース）
│   │   ├── prompt/
│   │   │   ├── repositories/  # DB実装
│   │   │   └── adapters/     # 外部サービス
│   │   ├── evaluation/, llm_integration/, user_interaction/, workflow/
│   │   └── shared/
│   │       ├── database/  # DB接続
│   │       ├── monitoring/ # 監視実装
│   │       └── auth/      # 認証実装
│   └── presentation/    # プレゼンテーション層
│       ├── api/         # FastAPI エンドポイント
│       ├── websocket/   # WebSocketハンドラー
│       └── middleware/  # 認証・エラー処理
└── tests/
    ├── unit/           # 単体テスト
    ├── integration/    # 統合テスト
    └── e2e/           # E2Eテスト
```

## 🎯 実装ガイドライン

### 1. ドメイン層実装方針

**エンティティ設計**
- 各エンティティは自身のビジネスルールを保持
- 集約ルートを通じてのみ外部からアクセス
- 不変条件は必ずエンティティ内で保証

**値オブジェクト設計**
- immutable（不変）として実装
- 自己検証ロジックを内包
- IDは全て値オブジェクトとして実装

**集約境界の厳守（機能ベース）**
- **prompt/**: プロンプト管理機能（Prompt, PromptContent, PromptMetadata, UserInput）
- **evaluation/**: 評価機能（Evaluation, TestResult, Metrics）
- **llm_integration/**: LLM統合（Provider, Request, Response, Cost）
- **user_interaction/**: ユーザー操作（Session, Feedback, History）
- **workflow/**: ワークフロー（Flow, Step, Condition）
- 各集約は独立したディレクトリとして管理
- 集約間は必ずIDで参照（直接参照禁止）

### 2. アプリケーション層実装方針

**CQRS実装ルール**
- コマンド側：データ変更、イベント発行、トランザクション保証
- クエリ側：読み取り専用、キャッシュ活用、DTO返却
- コマンドとクエリのモデルは完全分離

**ユースケース設計**
- 1ユースケース = 1つのビジネス操作
- 依存性注入でリポジトリとサービスを受け取る
- 必ずドメインイベントを発行

**アプリケーションサービス設計**
- 複数ユースケースの調整役
- ワークフローの管理
- 外部サービスとの統合調整

### 3. インフラストラクチャ層実装方針

**リポジトリ実装**
- インターフェース定義はドメイン層
- 実装はインフラ層（Turso/Redis）
- ORMはSQLAlchemy 2.0を使用
- 生SQLは原則禁止

**LLM統合方針**
- LiteLLMで100+プロバイダー統合
- フォールバック戦略の実装必須
- コスト最適化ルーティング
- レスポンスキャッシング

**イベント駆動実装**
- Redis Streamsでイベントバス実装
- at-least-once配信保証
- イベントソーシングでの履歴記録
- 非同期処理の徹底

## 🔧 開発コマンド

```bash
# 開発環境起動
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# テスト実行
pytest tests/ --cov=src --cov-report=html
pytest tests/unit/ -v          # 単体テストのみ
pytest tests/integration/ -v   # 統合テストのみ

# 品質チェック
ruff check src/ --fix          # Linting
ruff format src/               # フォーマット
mypy src/ --strict            # 型チェック

# データベースマイグレーション
alembic revision --autogenerate -m "Add prompt table"
alembic upgrade head
```

## 📊 パフォーマンス目標

- API レスポンス: P95 < 200ms
- 並列評価実行: 10並列以上
- WebSocket同時接続: 10,000+
- キャッシュヒット率: > 80%
- テストカバレッジ: > 80%

## 🔐 セキュリティ実装

- Clerk認証統合（JWT検証）
- レート制限（60 req/min）
- API キー暗号化（AES-256）
- SQLインジェクション対策（SQLAlchemy ORM）
- CORS設定（許可オリジン制限）

## 📝 実装手順（これ通りに実装する）

### Step 1: プロジェクト初期化
```bash
cd backend
python3.13 -m venv venv
source venv/bin/activate
pip install -e .[dev]
```

### Step 2: ディレクトリ構造作成
上記の `📁 ディレクトリ構造` の通りにフォルダを作成

### Step 3: Phase別実装

#### Phase 1: 基盤構築（Week 1-2）
**実装順序：**
1. ドメインモデル定義 → `src/domain/prompt/` 配下（機能ベース）
2. リポジトリインターフェース → `src/domain/prompt/repositories/`
3. Turso接続設定 → `src/infrastructure/shared/database/`
4. 基本CRUD API → `src/presentation/api/v1/prompt/`
5. Clerk認証ミドルウェア → `src/presentation/api/shared/middleware.py`

**完了基準：**
- [ ] プロンプトの作成・取得・更新・削除が可能
- [ ] 認証付きAPIエンドポイントが動作
- [ ] 単体テストカバレッジ > 80%

#### Phase 2: コア機能（Week 3-4）
**実装順序：**
1. CreatePromptUseCase → `src/application/prompt/commands/create_prompt.py`
2. LiteLLM統合 → `src/infrastructure/llm_integration/providers/litellm/`
3. 基本評価機能 → `src/application/evaluation/commands/`
4. レポート生成 → `src/application/evaluation/services/`

**完了基準：**
- [ ] プロンプト作成から評価まで一連のフロー完成
- [ ] OpenAI/Anthropic経由でプロンプト実行可能
- [ ] 評価結果のレポート生成

#### Phase 3: 高度な機能（Week 5-6）
**実装順序：**
1. CQRSパターン適用 → 各機能のcommands/queries分離
2. Redis Streamsイベントバス → `src/application/shared/events/`
3. 並列評価実行 → `src/application/evaluation/services/`
4. バージョニング機能 → `src/domain/prompt/entities/`

**完了基準：**
- [ ] 10並列以上の評価実行
- [ ] イベント駆動での非同期処理
- [ ] Git-likeなバージョン管理

## 🚨 重要な注意事項

### やってはいけないこと ❌
1. ドメインロジックをコントローラーに書かない
2. 集約境界を越えた直接参照をしない
3. 同期的な重い処理（必ずイベント駆動で）
4. 生のSQLクエリ（SQLAlchemy ORM使用）

### 必須事項 ✅
1. すべてのAPIにOpenAPI仕様を記述
2. エラーは構造化して返却
3. ログは構造化ログ形式
4. 重要な処理はイベント記録
5. テストファースト開発（TDD）

## 🔗 関連ドキュメント

- [アーキテクチャ設計書](../docs/architecture/backend_architecture.md)
- [レイヤー依存関係](../docs/architecture/layer_dependencies.md)
- [API仕様書](../docs/api/openapi.yaml)
- [セキュリティポリシー](../docs/security/SECURITY_POLICY.md)

## 📊 現在の実装状況（2025年9月30日更新）

### Phase 3: バックエンド実装進捗（45%完了）

#### ✅ 完了項目（Task 3.1完了）
- ✅ Python 3.13 + FastAPI 0.116.1環境構築
- ✅ DDD + Clean Architecture構造（機能ベース集約パターン全面適用）
- ✅ Domain層構造改善（prompt/評価/LLM/ユーザー操作/ワークフロー集約）
- ✅ Application層CQRS適用（commands/queries/services分離）
- ✅ Core層構造化（config/security/exceptions/logging/middleware/monitoring）
- ✅ Infrastructure層機能別実装（repositories/adapters構造）
- ✅ Pydantic v2階層型環境設定システム
- ✅ pytestテスト基盤（カバレッジ目標80%、tests/unit/domain/prompt実装済み）
- ✅ Docker開発環境統合（Dockerfile.dev最適化済み）
- ✅ Alembicマイグレーション環境準備
- ✅ ドメインモデル基底クラス（BaseEntity, BaseValue, BaseRepository）

#### 🚧 実装中（Task 3.2-3.7予定）
- プロンプト管理コア機能（Prompt/PromptContent/PromptMetadataエンティティ）
- Clerk認証システム統合
- Turso/libSQL接続実装
- 基本CRUD API実装

#### 📋 未実装（MVP必須）
- LiteLLM統合（100+プロバイダー対応）
- Redis Streamsイベントバス実装
- 並列評価実行システム
- バージョン管理機能（Event Sourcing）

### 構造改善の成果（Task 3.1）
- **機能ベース集約パターン採用**: 変更範囲の局所化、マイクロサービス化への道筋
- **CQRS全面適用**: 読み書き分離による性能最適化準備完了
- **無限ループ解消**: src/application/src/applicationなど重複構造を削除
- **テストカバレッジ基盤**: domain/prompt配下のテスト構造完成

### CI/CD最適化の成果（Phase 2完了）
- ✅ GitHub Actions使用量: 730分/月（無料枠36.5%）
- ✅ 共有ワークフロー実装で52.3%のコスト削減達成
- ✅ セキュリティ強化: CodeQL、TruffleHog統合済み
- ✅ セキュリティスコア: 78/100（2025年9月29日評価）

### セキュリティ改善項目（Critical対応必須）
- 🚨 CVE-2024-SECRETS-01: GitHub Actions シークレット漏洩リスク（CVSS 9.1）
- 🚨 CVE-2024-SECRETS-02: Git Hooks 秘密検知の回避可能性（CVSS 8.8）
- ⚠️ アクション権限の最小化（write-all → 必要最小限）

