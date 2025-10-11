---
name: event
description: 'イベント駆動アーキテクチャとメッセージング設計'
category: architecture
complexity: high
agents:
  [
    event-bus-manager,
    system-architect,
    domain-modellerr,
    backend-developer,
    real-time-features-specialist,
    version-control-specialist,
  ]
---

# /ai:architecture:event - イベント駆動設計

## Triggers

- イベントバスの設計と実装
- ドメインイベントの定義と管理
- 非同期メッセージングパターンの適用
- リアルタイム通信の実現

## Context Trigger Pattern

```
/ai:architecture:event [domain] [--pattern saga|cqrs|event-sourcing] [--broker redis|kafka|rabbitmq]
```

## Behavioral Flow

1. **イベント識別**: ビジネスイベントの発見と分類
2. **スキーマ設計**: イベントペイロードとメタデータ定義
3. **フロー設計**: イベントの発行と購読パターン
4. **順序保証**: イベント順序とべき等性の確保
5. **エラー処理**: 補償トランザクションとリトライ戦略
6. **リアルタイム設計**: WebSocket と SSE の活用
7. **監視設計**: イベントトレーシングとデバッグ

Key behaviors:

- イベントストーミングによる発見
- スキーマレジストリの活用
- デッドレターキューの実装
- イベントバージョニング戦略

## Agent Coordination

- **event-bus-manager** → イベント設計主導
- **system-architect** → 全体アーキテクチャ整合性
- **domain-modellerr** → ドメインイベント定義
- **backend-developer** → ハンドラー実装
- **real-time-features-specialist** → リアルタイム配信

## Tool Coordination

- **create_file**: イベントスキーマとハンドラー定義
- **view**: 既存イベントフローの確認
- **bash_tool**: メッセージブローカー設定
- **str_replace**: イベント定義の更新

## Key Patterns

- **Saga パターン**: 分散トランザクション管理
- **CQRS**: コマンドとクエリの分離
- **イベントソーシング**: 状態の再構築
- **アウトボックス**: トランザクション保証

## Examples

### Saga パターン実装

```
/ai:architecture:event payment --pattern saga --broker redis
# 決済処理のSaga実装
# 補償トランザクション設計
# Redis Streamsの活用
```

### CQRS とイベントソーシング

```
/ai:architecture:event user-management --pattern cqrs --pattern event-sourcing
# ユーザー管理のCQRS設計
# イベントソーシング実装
# 読み取りモデル最適化
```

### リアルタイムイベント配信

```
/ai:architecture:event notifications --broker redis
# 通知システムの設計
# WebSocket配信
# スケーラブルなPub/Sub
```

## Boundaries

**Will:**

- 堅牢なイベント駆動設計
- 順序保証とべき等性確保
- エラー処理と補償設計
- スケーラブルなメッセージング

**Will Not:**

- 同期的な密結合設計
- イベントの過度な細分化
- 保証なしの配信
- 監視なしの実装
