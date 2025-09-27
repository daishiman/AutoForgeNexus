# DORA メトリクス監視ガイド

## 概要

DORA（DevOps Research and Assessment）メトリクスは、ソフトウェアデリバリーのパフォーマンスを測定する業界標準の指標です。

## 4つの主要メトリクス

### 1. デプロイ頻度（Deployment Frequency）
**定義**: 本番環境へのデプロイ頻度

**パフォーマンスレベル**:
- **Elite**: 1日に複数回
- **High**: 週1回〜月1回
- **Medium**: 月1回〜半年1回
- **Low**: 半年1回以下

**計測方法**: mainブランチへのマージ数をカウント

### 2. 変更のリードタイム（Lead Time for Changes）
**定義**: コミットから本番デプロイまでの時間

**パフォーマンスレベル**:
- **Elite**: 1時間未満
- **High**: 1日〜1週間
- **Medium**: 1週間〜1ヶ月
- **Low**: 1ヶ月以上

**計測方法**: PRの作成から終了までの平均時間

### 3. 変更失敗率（Change Failure Rate）
**定義**: 本番環境で障害を引き起こす変更の割合

**パフォーマンスレベル**:
- **Elite**: 0-5%
- **High**: 5-10%
- **Medium**: 10-15%
- **Low**: 15%以上

**計測方法**: revert/rollback/hotfixを含むコミットの割合

### 4. 平均修復時間（Mean Time to Recovery）
**定義**: サービス障害から復旧までの時間

**パフォーマンスレベル**:
- **Elite**: 1時間未満
- **High**: 1日未満
- **Medium**: 1日〜1週間
- **Low**: 1週間以上

**計測方法**: 緊急PRのマージまでの平均時間

## ワークフローの使用方法

### 手動実行
```bash
# GitHub CLIを使用
gh workflow run metrics.yml

# 期間を指定して実行
gh workflow run metrics.yml -f period="7 days"
gh workflow run metrics.yml -f period="30 days"
gh workflow run metrics.yml -f period="90 days"
```

### 自動実行
- **日次実行**: 毎日午前3時（JST）に自動収集
- **PRマージ時**: mainブランチへのマージ時に自動計測
- **プッシュ時**: main/developブランチへのプッシュ時に更新

### メトリクスの確認方法

#### 1. GitHub Actions UI
1. Actionsタブを開く
2. "DevOps Metrics Collection"ワークフローを選択
3. 実行結果を確認

#### 2. アーティファクト
- 各実行後に`dora-metrics-{run-id}`として保存
- 90日間保持
- JSON形式でダウンロード可能

#### 3. PR コメント
PRに対して自動的にメトリクスレポートがコメントされます。

## Webhook連携

### Slack通知設定
1. Slack Incoming Webhookを作成
2. GitHub Secretsに`SLACK_WEBHOOK_URL`として登録
3. ワークフローが自動的に通知を送信

### Discord通知設定
1. Discord Webhookを作成
2. GitHub Secretsに`DISCORD_WEBHOOK_URL`として登録
3. ワークフローが自動的に通知を送信

### カスタムWebhook
`METRICS_WEBHOOK_URL`にエンドポイントを設定すると、JSON形式でメトリクスを送信します。

## メトリクスの改善方法

### デプロイ頻度の向上
- CI/CDパイプラインの高速化
- 自動テストの充実
- フィーチャーフラグの活用
- 小さなバッチでのリリース

### リードタイムの短縮
- PRレビューの迅速化
- 自動化の推進
- ブランチ戦略の最適化
- 並列処理の活用

### 変更失敗率の低減
- テストカバレッジの向上
- ステージング環境での検証
- ロールバック手順の整備
- コードレビューの徹底

### 修復時間の短縮
- 監視・アラートの充実
- インシデント対応手順の整備
- ロールバック自動化
- ポストモーテムの実施

## トラブルシューティング

### メトリクスが0になる場合
- Git履歴が不足している → `fetch-depth: 0`を確認
- GitHub tokenの権限不足 → permissions設定を確認
- ブランチ名の不一致 → ブランチ戦略を確認

### Webhook通知が届かない
- Secret設定を確認
- Webhook URLの有効性を確認
- ネットワーク制限を確認

## ベストプラクティス

1. **定期的な確認**: 週次でメトリクスをレビュー
2. **目標設定**: 段階的に改善目標を設定
3. **チーム共有**: メトリクスを可視化して共有
4. **継続的改善**: メトリクスを基に改善活動を実施

## 参考リンク
- [DORA Research](https://dora.dev/)
- [State of DevOps Report](https://cloud.google.com/devops/state-of-devops)
- [Four Key Metrics](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance)