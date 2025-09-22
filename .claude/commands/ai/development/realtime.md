### `/ai:development:realtime`

```markdown
---
name: realtime
description: "リアルタイム機能と協調編集の実装"
category: development
complexity: extreme
agents:
  [
    real-time-features-specialist,
    frontend-architect,
    event-bus-manager,
    backend-developer,
    ui-ux-designer,
    version-control-specialist,
  ]
---

# /ai:development:realtime - リアルタイム機能実装

## Triggers

- WebSocket 通信の実装
- 協調編集機能の開発
- リアルタイム同期システム
- ライブ更新機能の追加

## Context Trigger Pattern
```

/ai:development:realtime [feature] [--websocket] [--crdt|ot] [--scale] [--presence]

```

## Behavioral Flow
1. **アーキテクチャ設計**: WebSocketサーバー構成
2. **同期アルゴリズム**: CRDT/OT選択と実装
3. **クライアント実装**: リアルタイムUI更新
4. **サーバー実装**: WebSocketハンドラー
5. **状態管理**: 分散状態の同期
6. **プレゼンス**: ユーザー状態の共有
7. **スケーリング**: 水平展開対応
8. **最適化**: レイテンシとスループット

Key behaviors:
- 低レイテンシ通信
- 楽観的UI更新
- 衝突解決アルゴリズム
- 自動再接続処理

## Agent Coordination
- **real-time-features-specialist** → リアルタイム設計主導
- **frontend-architect** → クライアントサイド実装
- **event-bus-manager** → イベント配信設計
- **backend-developer** → サーバーサイド実装
- **ui-ux-designer** → リアルタイムUX設計

## Tool Coordination
- **create_file**: WebSocketハンドラーとクライアント
- **bash_tool**: 負荷テストとベンチマーク
- **view**: 既存実装の確認
- **str_replace**: 最適化の適用

## Key Patterns
- **同期戦略**: CRDT(無競合)/OT(変換)
- **接続管理**: 自動再接続とバックオフ
- **状態共有**: SharedWorkerとBroadcastChannel
- **スケーリング**: Redisアダプター

## Examples

### 協調編集システム
```

/ai:development:realtime collaborative-editor --crdt --presence

# Yjs CRDT ベース実装

# カーソル位置共有

# リアルタイムプレゼンス

```

### ライブダッシュボード
```

/ai:development:realtime live-dashboard --websocket --scale

# リアルタイム更新

# 水平スケーリング対応

# 効率的な diff 配信

```

### チャットシステム
```

/ai:development:realtime chat-system --websocket --presence

# リアルタイムメッセージング

# タイピングインジケーター

# オンライン状態管理

```

## Boundaries

**Will:**
- 低レイテンシ実装
- スケーラブル設計
- 堅牢な再接続処理
- 効率的な状態同期

**Will Not:**
- 非効率なポーリング
- 状態の不整合許容
- セキュリティの妥協
- スケーラビリティ無視
```
