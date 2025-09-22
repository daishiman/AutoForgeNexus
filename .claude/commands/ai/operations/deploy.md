---
name: deploy
description: "マルチ環境デプロイメントとリリース管理"
category: operations
complexity: high
agents:
  [
    devops-coordinator,
    edge-computing-specialist,
    sre-agent,
    observability-engineer,
    security-architect,
    version-control-specialist,
  ]
---

# /ai:operations:deploy - デプロイメント管理

## Triggers

- 環境別デプロイメント実行
- カナリアリリースの実施
- ブルーグリーンデプロイメント
- エッジへの展開

## Context Trigger Pattern

```
/ai:operations:deploy [env dev|staging|prod] [--strategy canary|blue-green|rolling] [--rollback auto] [--edge]
```

## Behavioral Flow

1. **前準備**: デプロイ前チェックリスト実行
2. **ビルド**: デプロイアーティファクト生成
3. **検証**: セキュリティスキャンと依存関係確認
4. **デプロイ実行**: 選択戦略での段階的展開
5. **ヘルスチェック**: エンドポイント監視
6. **トラフィック切替**: 負荷分散設定更新
7. **監視**: メトリクスとログの確認
8. **完了/ロールバック**: 成功確認または自動復旧

Key behaviors:

- ゼロダウンタイムデプロイ
- 自動ロールバック条件
- プログレッシブデリバリー
- エッジロケーション同期

## Agent Coordination

- **devops-coordinator** → デプロイ全体統括
- **edge-computing-specialist** → Cloudflare Workers 展開
- **sre-agent** → 信頼性と SLO 監視
- **observability-engineer** → リアルタイム監視
- **security-architect** → セキュリティ検証

## Tool Coordination

- **bash_tool**: デプロイスクリプト実行
- **create_file**: デプロイ設定生成
- **view**: 環境状態確認
- **str_replace**: 設定更新

## Key Patterns

- **カナリアリリース**: 段階的ユーザー展開
- **ブルーグリーン**: 即座切り替え可能
- **ローリング**: 順次更新
- **エッジデプロイ**: グローバル展開

## Examples

### 本番カナリアデプロイ

```
/ai:operations:deploy prod --strategy canary --rollback auto
# 5% → 25% → 50% → 100%展開
# エラー率監視で自動ロールバック
# SLO違反で即時停止
```

### エッジワーカー展開

```
/ai:operations:deploy prod --edge --strategy rolling
# Cloudflare Workers展開
# 地域別順次更新
# グローバル同期確認
```

### ステージング検証

```
/ai:operations:deploy staging --strategy blue-green
# 完全な環境切り替え
# A/Bテスト実行
# 本番模擬検証
```

## Boundaries

**Will:**

- 安全なデプロイメント実行
- 自動ロールバック機能
- 包括的な監視と検証
- エッジ展開のサポート

**Will Not:**

- 未検証のデプロイ実行
- SLO 違反の無視
- 手動介入なしの強制展開
- セキュリティチェックスキップ
