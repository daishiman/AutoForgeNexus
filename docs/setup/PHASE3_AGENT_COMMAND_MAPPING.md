# Phase 3 バックエンド実装 - エージェント・コマンド選定ガイド

## 🎯 概要

このドキュメントは、Phase 3バックエンド実装の各タスクに対して、最適なエージェントとコマンドを`.claude/agents/00.agent_list.md`と`.claude/commands/ai/`から選定したマッピングです。

## 📋 タスクとエージェント・コマンドのマッピング

### 1. ドメイン層実装

#### 1.1 プロンプト集約の実装

**選定エージェント:**
- **domain-modeller Agent** (主担当)
  - ドメイン境界の定義と集約ルート設計
  - エンティティ・値オブジェクトのモデリング
  - ユビキタス言語の確立

**選定コマンド:**
```bash
# ドメインモデル設計
/ai:architecture:design domain-layer --ddd --aggregates

# ドメイン実装
/ai:development:implement domain-prompt-aggregate
```

**実装タスク:**
```python
# backend/src/domain/prompt/
├── entities/
│   └── prompt.py          # domain-modeller + backend-developer
├── value_objects/
│   ├── prompt_id.py       # domain-modeller
│   ├── prompt_content.py  # domain-modeller
│   └── prompt_metadata.py # domain-modeller
├── events/
│   ├── prompt_created.py  # domain-modeller + event-bus-manager
│   ├── prompt_saved.py    # domain-modeller + event-bus-manager
│   └── prompt_updated.py  # domain-modeller + event-bus-manager
└── repositories/
    └── prompt_repository.py # domain-modeller + backend-developer
```

#### 1.2 共有カーネルの実装

**選定エージェント:**
- **system-architect Agent** (設計承認)
- **domain-modeller Agent** (実装)

**選定コマンド:**
```bash
# 共有カーネル設計
/ai:architecture:design shared-kernel --value-objects --domain-events
```

### 2. アプリケーション層実装

#### 2.1 CQRS実装

**選定エージェント:**
- **backend-developer Agent** (主担当)
- **event-bus-manager Agent** (イベント処理)
- **api-designer Agent** (インターフェース定義)

**選定コマンド:**
```bash
# CQRS実装
/ai:development:implement cqrs-pattern --commands --queries

# イベントバス実装
/ai:architecture:event setup-eventbus --redis-streams
```

**実装タスク:**
```python
# backend/src/application/prompt/
├── commands/
│   ├── create_prompt.py    # backend-developer
│   ├── save_prompt.py      # backend-developer
│   └── update_prompt.py    # backend-developer
├── queries/
│   ├── get_prompt.py       # backend-developer
│   └── list_prompts.py     # backend-developer
└── handlers/
    └── prompt_handlers.py  # event-bus-manager
```

#### 2.2 イベントハンドラー実装

**選定エージェント:**
- **event-bus-manager Agent** (主担当)
- **workflow-orchestrator Agent** (ワークフロー統合)

**選定コマンド:**
```bash
# イベント駆動アーキテクチャ実装
/ai:architecture:event implement-handlers --async --redis

# ワークフロー設計
/ai:development:workflow create-prompt-workflow
```

### 3. インフラストラクチャ層実装

#### 3.1 リポジトリ実装

**選定エージェント:**
- **database-administrator Agent** (主担当)
- **backend-developer Agent** (実装支援)
- **data-migration-specialist Agent** (マイグレーション)

**選定コマンド:**
```bash
# データベース設計・実装
/ai:data:migrate setup-turso --schema-design

# リポジトリパターン実装
/ai:development:implement repository-pattern --sqlalchemy
```

**実装タスク:**
```python
# backend/src/infrastructure/prompt/
├── repositories/
│   └── turso_prompt_repository.py  # database-administrator
├── mappers/
│   └── prompt_mapper.py           # backend-developer
└── models/
    └── prompt_model.py            # database-administrator
```

#### 3.2 外部サービス統合

**選定エージェント:**
- **edge-computing-specialist Agent** (エッジ実装)
- **observability-engineer Agent** (監視設定)

**選定コマンド:**
```bash
# エッジデプロイ準備
/ai:operations:deploy edge-setup --cloudflare-workers

# 監視設定
/ai:operations:monitor setup-observability --langfuse
```

### 4. プレゼンテーション層実装

#### 4.1 REST API実装

**選定エージェント:**
- **api-designer Agent** (API設計)
- **backend-developer Agent** (実装)
- **security-architect Agent** (認証・認可)

**選定コマンド:**
```bash
# API設計・実装
/ai:development:implement rest-api --fastapi --openapi

# セキュリティ実装
/ai:quality:security implement-auth --rate-limiting
```

**実装タスク:**
```python
# backend/src/presentation/api/v1/
├── prompts/
│   ├── routes.py          # api-designer + backend-developer
│   ├── schemas.py         # api-designer
│   └── dependencies.py    # backend-developer
└── middleware/
    ├── error_handler.py   # backend-developer
    └── validation.py      # security-architect
```

### 5. テスト実装

#### 5.1 単体テスト

**選定エージェント:**
- **test-automation-engineer Agent** (主担当)
- **qa-coordinator Agent** (品質戦略)

**選定コマンド:**
```bash
# TDDアプローチでテスト実装
/ai:quality:tdd implement-tests --pytest --coverage=80

# 品質分析
/ai:quality:analyze test-coverage --report
```

**実装タスク:**
```python
# backend/tests/
├── unit/
│   ├── domain/
│   │   └── prompt/        # test-automation-engineer
│   ├── application/
│   │   └── prompt/        # test-automation-engineer
│   └── infrastructure/
│       └── prompt/        # test-automation-engineer
└── integration/
    └── api/               # test-automation-engineer + api-designer
```

### 6. 品質保証

#### 6.1 コード品質チェック

**選定エージェント:**
- **qa-coordinator Agent** (品質統括)
- **performance-optimizer Agent** (パフォーマンス最適化)
- **security-architect Agent** (セキュリティ監査)

**選定コマンド:**
```bash
# 品質チェック
/ai:quality:analyze full-scan --ruff --mypy --black

# セキュリティスキャン
/ai:quality:security scan --owasp --vulnerability

# パフォーマンス分析
/ai:quality:analyze performance --profiling
```

## 🔄 実装フロー

### Phase 3-A: 基盤実装（Week 1）

1. **ドメインモデル定義**
   ```bash
   /ai:core:team --task "Phase3 ドメイン層実装"
   # 自動選定: domain-modeller, system-architect, backend-developer
   ```

2. **共有カーネル実装**
   ```bash
   /ai:architecture:design shared-kernel
   # domain-modeller Agent実行
   ```

3. **イベント定義**
   ```bash
   /ai:architecture:event define-domain-events
   # event-bus-manager Agent実行
   ```

### Phase 3-B: アプリケーション層（Week 2）

1. **CQRS実装**
   ```bash
   /ai:development:implement cqrs-layer
   # backend-developer + event-bus-manager連携
   ```

2. **ユースケース実装**
   ```bash
   /ai:development:implement use-cases --prompt-management
   # backend-developer Agent実行
   ```

### Phase 3-C: インフラ層（Week 3）

1. **データベース実装**
   ```bash
   /ai:data:migrate implement-repositories --turso
   # database-administrator + data-migration-specialist連携
   ```

2. **外部サービス統合**
   ```bash
   /ai:operations:deploy setup-infrastructure
   # edge-computing-specialist + devops-coordinator連携
   ```

### Phase 3-D: API層（Week 4）

1. **REST API実装**
   ```bash
   /ai:development:implement api-layer --fastapi
   # api-designer + backend-developer連携
   ```

2. **セキュリティ実装**
   ```bash
   /ai:quality:security implement-security-layer
   # security-architect Agent実行
   ```

### Phase 3-E: テスト・品質保証（Week 5）

1. **テスト実装**
   ```bash
   /ai:quality:tdd full-test-suite --coverage=80
   # test-automation-engineer + qa-coordinator連携
   ```

2. **品質監査**
   ```bash
   /ai:quality:analyze comprehensive-audit
   # qa-coordinator統括で全品質エージェント連携
   ```

## 📊 エージェント使用頻度（Phase 3）

| エージェント | 使用頻度 | 主要タスク |
|------------|---------|-----------|
| backend-developer | 高 | 全実装タスク |
| domain-modeller | 高 | ドメイン層全般 |
| test-automation-engineer | 高 | テスト実装 |
| api-designer | 中 | API設計・実装 |
| database-administrator | 中 | DB層実装 |
| event-bus-manager | 中 | イベント処理 |
| qa-coordinator | 中 | 品質統括 |
| security-architect | 低 | セキュリティ監査 |
| system-architect | 低 | 設計承認 |
| performance-optimizer | 低 | 最適化 |

## 🚀 クイックスタートコマンド

```bash
# Phase 3全体を一括実行
/ai:core:init phase3-backend

# または個別実行
/ai:architecture:design backend-layer --ddd
/ai:development:implement domain-layer
/ai:development:implement application-layer --cqrs
/ai:development:implement infrastructure-layer
/ai:development:implement api-layer
/ai:quality:tdd implement-tests
/ai:quality:analyze final-audit
```

## 📝 注意事項

1. **エージェント連携**
   - 各エージェントは自動的に必要な他エージェントと連携
   - `/ai:core:team`コマンドで最適なチーム編成を自動選定

2. **コマンド実行順序**
   - 設計系コマンド（architecture）→ 実装系（development）→ 品質系（quality）
   - 各フェーズは前フェーズの完了を前提

3. **並列実行可能タスク**
   - ドメインイベント定義と値オブジェクト実装
   - 各集約のリポジトリ実装
   - 単体テストの並列作成

4. **依存関係**
   - アプリケーション層はドメイン層完了後
   - API層はアプリケーション層完了後
   - テストは各層の実装と並行可能（TDD）