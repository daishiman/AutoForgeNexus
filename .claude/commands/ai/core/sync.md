---
name: sync
description: "エージェント間の状態同期とコンテキスト共有"
category: core
complexity: medium
agents:
  [
    event-bus-manager,
    system-architect,
    product-manager,
    version-control-specialist,
  ]
---

# /ai:core:sync - エージェント同期とコンテキスト管理

## Triggers

- エージェント間の状態不整合検出時
- タスク進捗の統合更新要求
- コンテキスト情報の全体共有必要時
- 定期的な同期チェックポイント

## Context Trigger Pattern

```
/ai:core:sync [--scope all|team|specific-agents] [--mode share|merge|resolve] [--priority high|normal]
```

## Behavioral Flow

1. **状態収集**: 各エージェントの現在状態とコンテキスト取得
2. **差分検出**: 同期が必要な情報とコンフリクトの特定
3. **優先順位付け**: 重要度に基づく同期順序の決定
4. **調整実行**: コンフリクト解決とマージ戦略の適用
5. **配信**: イベントバス経由での更新情報配信
6. **検証**: 同期完了確認と整合性チェック

Key behaviors:

- イベント駆動による非同期状態同期
- CRDT ベースのコンフリクト解決
- 優先度ベースの同期順序制御
- 部分同期とフル同期の自動判定

## Agent Coordination

- **event-bus-manager** → イベント配信とメッセージルーティング
- **system-architect** → 全体整合性の確保と依存関係管理
- **product-manager** → ビジネスコンテキストの同期

## Tool Coordination

- **view**: 各エージェントの状態確認
- **str_replace**: 設定ファイルの更新
- **create_file**: 同期レポートの生成
- **bash_tool**: 同期スクリプトの実行

## Key Patterns

- **イベント配信**: Pub/Sub パターンによる疎結合通信
- **同期モード**: 共有(read-only) / マージ(統合) / 解決(コンフリクト)
- **スコープ制御**: 全体/チーム単位/特定エージェント
- **優先度管理**: クリティカルパス優先の同期順序

## Examples

### 全エージェント同期

```
/ai:core:sync --scope all --mode merge
# 29エージェント全体の状態同期
# 自動コンフリクト解決とマージ
```

### チーム単位の同期

```
/ai:core:sync --scope team:prompt-optimization --mode share
# プロンプト最適化チームの状態共有
# 読み取り専用モードで情報配信
```

### 緊急同期

```
/ai:core:sync --scope specific-agents --priority high --mode resolve
# 特定エージェント間の緊急同期
# コンフリクト解決モードで実行
```

## Boundaries

**Will:**

- エージェント間の状態整合性確保
- 自動コンフリクト検出と解決
- 優先度ベースの同期制御
- イベント駆動による効率的な情報配信

**Will Not:**

- 破壊的な状態変更の強制実行
- 承認なしの重要データ上書き
- 同期中のシステム停止
