# Agent Activation Flags

## Task Complexity Flags

**--simple-prompt**

- Triggers: 単純なプロンプト作成要求
- Active Agents: prompt-engineering-specialist, domain-modellerr
- Team Size: 2-3 agents

**--complex-prompt**

- Triggers: 高度なプロンプトチェーン、ワークフロー要求
- Active Agents: Full Prompt Team (5 agents)
- Team Size: 5-7 agents

**--evaluation-mode**

- Triggers: 評価実行、品質測定要求
- Active Agents: evaluation-engine, data-analyst, llm-integration
- Team Size: 4-6 agents

**--optimization-mode**

- Triggers: パフォーマンス改善、コスト削減要求
- Active Agents: performance-optimizer, cost-optimization, data-analyst
- Team Size: 3-5 agents

## Feature Implementation Flags

**--intent-diffoscope**

- Triggers: 意図差分ビューワー機能
- Lead Agent: prompt-engineering-specialist
- Support Agents: ui-ux-designer, frontend-architect, evaluation-engine

**--prompt-slo**

- Triggers: プロンプト SLO 機能
- Lead Agent: sre-agent
- Support Agents: observability-engineer, qa-coordinator, performance-optimizer

**--style-genome**

- Triggers: スタイル・ゲノム機能
- Lead Agent: data-analyst
- Support Agents: vector-database-specialist, prompt-engineering-specialist

**--mutation-fuzz**

- Triggers: プロンプト・ジェンガ機能
- Lead Agent: test-automation-engineer
- Support Agents: qa-coordinator, security-architect

**--adversarial-twin**

- Triggers: 影武者システム
- Lead Agent: security-architect
- Support Agents: test-automation-engineer, evaluation-engine

## Environment Flags

**--development**

- Triggers: 開発環境での実行
- Modifications: 詳細ログ、デバッグモード、モック許可

**--staging**

- Triggers: ステージング環境
- Modifications: 統合テスト、パフォーマンステスト

**--production**

- Triggers: 本番環境
- Modifications: 最大セキュリティ、監査ログ、エラー通知

## Collaboration Flags

**--distributed-team**

- Triggers: 5+ エージェントのタスク
- Behavior: 分散コーディネーション有効化

**--consensus-required**

- Triggers: クリティカルな設計決定
- Behavior: 合意形成プロトコル有効化

**--parallel-execution**

- Triggers: 独立したサブタスク存在
- Behavior: 並列実行最適化

## Testing Flags

**--tdd-strict**

- Triggers: すべての実装
- Behavior: テストなしコード拒否

**--contract-testing**

- Triggers: エージェント間通信
- Behavior: 契約テスト必須化

**--chaos-engineering**

- Triggers: 本番前検証
- Behavior: ランダム障害注入
