---
name: team
description: "動的エージェントチーム編成と協調管理"
category: core
complexity: extreme
agents:
  [
    product-manager,
    system-architect,
    domain-modeller,
    api-designer,
    prompt-engineering-specialist,
    llm-integration,
    evaluation-engine,
    workflow-orchestrator,
    ui-ux-designer,
    frontend-architect,
    real-time-features-specialist,
    backend-developer,
    database-administrator,
    vector-database-specialist,
    event-bus-manager,
    edge-computing-specialist,
    security-architect,
    performance-optimizer,
    observability-engineer,
    test-automation-engineer,
    technical-documentation,
    devops-coordinator,
    data-migration-specialist,
    compliance-officer,
    cost-optimization,
    user-research,
    data-analyst,
    sre-agent,
    qa-coordinator,
    version-control-specialist,
  ]
---

# /ai:core:team - 動的チーム編成

## Triggers

- 特定タスクに最適なチーム編成要求
- リソース最適化によるエージェント配分
- 複雑タスクのための専門家チーム結成
- プロジェクトフェーズ移行時の再編成

## Context Trigger Pattern

```
/ai:core:team [task-type] [--size small|medium|large] [--optimize performance|cost|quality] [--duration sprint|epic]
```

## Behavioral Flow

1. **タスク分析**: 必要なスキルセットと専門性の特定
2. **エージェント評価**: 利用可能エージェントの能力評価
3. **チーム選定**: 最適なエージェント組み合わせの決定
4. **役割割当**: リーダーとメンバーの役割定義
5. **依存関係設定**: エージェント間の協調パターン確立
6. **パフォーマンス監視**: チーム効率とアウトプットの追跡

Key behaviors:

- タスク特性に基づく動的チーム編成
- エージェント負荷分散と最適配置
- リアルタイムパフォーマンス監視
- 自動スケーリングと再編成

## Agent Coordination

- **product-manager** → チーム編成戦略と優先順位
- **system-architect** → 技術的役割配分と依存関係
- **Selected Agents** → タスク実行と協調

## Tool Coordination

- **view**: エージェント状態と可用性確認
- **create_file**: チーム構成ドキュメント
- **bash_tool**: チーム活性化スクリプト

## Key Patterns

- **チームサイズ**: Small(3-5) / Medium(6-10) / Large(11+)
- **最適化戦略**: パフォーマンス/コスト/品質
- **期間管理**: スプリント(2 週間) / エピック(2-3 ヶ月)
- **編成パターン**: 機能横断/専門特化/ハイブリッド

## Examples

### プロンプト最適化チーム編成

```
/ai:core:team prompt-optimization --size medium --optimize quality
# 5エージェントの品質重視チーム
# prompt-engineering-specialist主導
```

### インシデント対応チーム

```
/ai:core:team incident-response --size small --optimize performance --duration sprint
# 3エージェントの即応チーム
# sre-agent主導で2週間集中対応
```

## Boundaries

**Will:**

- タスクに最適なエージェント組み合わせ選定
- 動的な負荷分散とリソース最適化
- チームパフォーマンスの継続的監視

**Will Not:**

- 必須エージェントの強制除外
- 承認なしのチーム解散
- 過負荷によるエージェント故障
