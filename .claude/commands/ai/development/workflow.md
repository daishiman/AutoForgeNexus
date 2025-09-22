---
name: workflow
description: "LangGraphによるワークフロー自動化実装"
category: development
complexity: high
agents:
  [
    workflow-orchestrator,
    event-bus-manager,
    backend-developer,
    frontend-architect,
    prompt-engineering-specialist,
    version-control-specialist,
  ]
---

# /ai:development:workflow - ワークフロー実装

## Triggers

- ワークフロー定義と実装
- LangGraph チェーンの構築
- ビジュアルエディタの開発
- 自動化フローの作成

## Context Trigger Pattern

```
/ai:development:workflow [name] [--langgraph] [--visual-editor] [--type sequential|parallel|conditional]
```

## Behavioral Flow

1. **フロー設計**: ワークフロー要件とステップ定義
2. **ノード設計**: 各処理ノードの責務と入出力
3. **エッジ定義**: ノード間の接続と条件分岐
4. **LangGraph 実装**: Python でのグラフ構築
5. **状態管理**: ワークフロー状態の永続化
6. **エディタ開発**: React Flow ビジュアルエディタ
7. **実行エンジン**: ワークフロー実行とモニタリング
8. **エラー処理**: 例外処理とリトライ戦略

Key behaviors:

- 宣言的ワークフロー定義
- 動的グラフ構築
- 並列実行サポート
- トレーサビリティ確保

## Agent Coordination

- **workflow-orchestrator** → ワークフロー設計統括
- **event-bus-manager** → イベント駆動統合
- **backend-developer** → 実行エンジン実装
- **frontend-architect** → ビジュアルエディタ開発
- **prompt-engineering-specialist** → プロンプトチェーン設計

## Tool Coordination

- **create_file**: ワークフロー定義とコード
- **bash_tool**: LangGraph 実行とテスト
- **view**: 既存フローの確認
- **str_replace**: フロー定義の更新

## Key Patterns

- **グラフ構造**: DAG(有向非巡回グラフ)
- **実行モード**: Sequential/Parallel/Conditional
- **状態管理**: チェックポイントと復元
- **監視**: リアルタイム実行追跡

## Examples

### プロンプトチェーンワークフロー

```
/ai:development:workflow prompt-chain --langgraph --type sequential
# 多段階プロンプト処理
# LangGraphチェーン実装
# 中間結果の管理
```

### 条件分岐ワークフロー

```
/ai:development:workflow decision-flow --langgraph --visual-editor --type conditional
# 条件分岐フロー
# ビジュアルエディタ付き
# 動的パス選択
```

### 並列処理ワークフロー

```
/ai:development:workflow batch-processing --langgraph --type parallel
# 並列バッチ処理
# Fork/Join パターン
# 負荷分散実装
```

## Boundaries

**Will:**

- LangGraph 準拠の実装
- スケーラブルなワークフロー
- 視覚的な管理インターフェース
- 堅牢なエラー処理

**Will Not:**

- 無限ループの許可
- 状態管理なしの実行
- モニタリングなしの本番適用
- 過度に複雑なフロー
