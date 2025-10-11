# Domain Boundaries and Responsibilities

## Bounded Contexts

### Prompt Domain

**Owner**: prompt-engineering-specialist Agent **Aggregates**:

- PromptAggregate (root)
- TemplateAggregate
- VariableAggregate

**Responsibilities**:

- プロンプトのライフサイクル管理
- テンプレート処理
- 変数解決

**Events Published**:

- PromptCreated
- PromptUpdated
- PromptValidated
- TemplateProcessed

### Evaluation Domain

**Owner**: evaluation-engine Agent **Aggregates**:

- EvaluationAggregate (root)
- MetricsAggregate
- BenchmarkAggregate

**Responsibilities**:

- 品質評価実行
- メトリクス計算
- ベンチマーク管理

**Events Published**:

- EvaluationStarted
- MetricsCalculated
- EvaluationCompleted
- ThresholdViolated

### Workflow Domain

**Owner**: workflow-orchestrator Agent **Aggregates**:

- WorkflowAggregate (root)
- StepAggregate
- TransitionAggregate

**Responsibilities**:

- ワークフロー定義と実行
- ステップ管理
- 状態遷移制御

**Events Published**:

- WorkflowStarted
- StepExecuted
- WorkflowCompleted
- WorkflowFailed

### llm-integration Domain

**Owner**: llm-integration Agent **Aggregates**:

- ProviderAggregate
- ModelAggregate
- ExecutionAggregate

**Responsibilities**:

- プロバイダー管理
- モデル選択
- API 呼び出し実行

**Events Published**:

- ModelSelected
- ExecutionStarted
- ResponseReceived
- QuotaExceeded

### User Domain

**Owner**: product-manager Agent **Aggregates**:

- UserAggregate (root)
- PreferenceAggregate
- SubscriptionAggregate

**Responsibilities**:

- ユーザー管理
- 設定管理
- サブスクリプション

**Events Published**:

- UserRegistered
- PreferencesUpdated
- SubscriptionChanged

## Anti-Corruption Layers

### External API Gateway

- LLM プロバイダー API の抽象化
- 外部サービスとの境界保護
- レート制限とリトライ

### Legacy System Adapter

- 既存システムとの統合
- データフォーマット変換
- 後方互換性維持

## Context Mapping

```
[Prompt Domain] <--Published Language--> [Evaluation Domain]
        |                                        |
        v                                        v
[Workflow Domain] <--Shared Kernel--> [llm-integration Domain]
        |                                        |
        v                                        v
[User Domain] <-------Customer/Supplier-------> [All Domains]
```
