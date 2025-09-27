# アラート設定ガイド

## 概要

AutoForgeNexusのアラートシステムは、重要なイベントを自動検知してDiscordとGitHub Issuesで通知する仕組みです。

## アラートの種類

### 1. ワークフロー失敗アラート
**トリガー**: CI/CD、セキュリティスキャン、デプロイメントの失敗

**通知内容**:
- 失敗したワークフロー名
- ブランチ名
- コミットハッシュ
- 実行者
- 失敗時刻

### 2. パフォーマンスアラート
**トリガー**: ワークフロー実行時間が10分を超過

**通知内容**:
- ワークフロー名
- 実行時間
- パフォーマンス警告

### 3. セキュリティアラート
**トリガー**: セキュリティラベル付きIssueの作成

**通知内容**:
- Issue番号
- タイトル
- 作成者
- リンク

### 4. 高優先度アラート
**トリガー**: critical/urgentラベル付きIssue/PRの作成

**通知内容**:
- Issue/PR番号
- タイトル
- 優先度レベル
- リンク

## 通知チャンネル設定

AutoForgeNexusでは、DiscordとGitHub Issuesの2つの通知チャンネルをサポートしています。

### Discord設定

#### 1. Webhook作成
1. Discordサーバーの設定を開く
2. 「連携サービス」→「ウェブフック」を選択
3. 「新しいウェブフック」を作成
4. Webhook URLをコピー

#### 2. GitHub Secrets設定
```bash
# GitHub CLIを使用
gh secret set DISCORD_WEBHOOK_URL --body "https://discord.com/api/webhooks/..."

# Web UIから設定
# Settings → Secrets and variables → Actions → New repository secret
# Name: DISCORD_WEBHOOK_URL
# Value: [Webhook URL]
```

### カスタムWebhook設定

独自のWebhookエンドポイントを使用する場合：

```bash
# メトリクス用Webhook
gh secret set METRICS_WEBHOOK_URL --body "https://your-api.com/metrics"
```

### GitHub Issues自動作成

以下の条件で自動的にGitHub Issueが作成されます：

1. **セキュリティ関連のワークフロー失敗時**
   - Securityワークフローの失敗
   - 自動的に`bug`、`critical`、`workflow-failure`ラベル付与

2. **デプロイメント失敗時**
   - Deployワークフローの失敗
   - 詳細なエラー情報と対応手順を含む

3. **パフォーマンス問題発生時**
   - ワークフロー実行時間が20分を超過
   - `performance`、`workflow-optimization`ラベル付与

4. **セキュリティIssue作成時**
   - 重要度分析と自動優先度設定
   - SLA管理と自動エスカレーション

## アラートのカスタマイズ

### 通知条件の変更

`.github/workflows/alerts.yml`を編集：

```yaml
# パフォーマンス閾値の変更（デフォルト: 10分）
if [ $RUN_DURATION_MS -gt 600000 ]; then  # 600000ms = 10分
  # この値を変更して閾値を調整
```

### 通知対象ワークフローの追加

```yaml
on:
  workflow_run:
    workflows:
      - "Your Workflow Name"  # 追加
    types: [completed]
```

## 通知フォーマット

### Discordメッセージ形式
```json
{
  "content": "アラートタイトル",
  "embeds": [{
    "title": "詳細",
    "color": 15158332,
    "fields": [
      { "name": "項目", "value": "値", "inline": true }
    ],
    "timestamp": "ISO8601形式"
  }]
}
```

## アラートテスト

### 手動テスト実行
```bash
# テストアラート送信
gh workflow run alerts.yml -f alert_type=test

# 特定タイプのテスト
gh workflow run alerts.yml -f alert_type=failure
gh workflow run alerts.yml -f alert_type=performance
gh workflow run alerts.yml -f alert_type=security
```

### 通知確認ポイント
1. Discord Webhook URLが正しく設定されているか
2. Discord チャンネルに権限があるか
3. メッセージフォーマットが正しいか
4. ネットワーク接続が可能か
5. GitHub Actions権限が適切に設定されているか

## トラブルシューティング

### 通知が届かない場合

#### 1. Secret設定を確認
```bash
# 設定済みSecretsの確認
gh secret list

# 期待される出力
DISCORD_WEBHOOK_URL   Updated 2024-01-01
METRICS_WEBHOOK_URL   Updated 2024-01-01  # オプション
```

#### 2. ワークフローログを確認
1. Actionsタブを開く
2. 該当のワークフロー実行を選択
3. ログでエラーメッセージを確認

#### 3. Webhook URLをテスト
```bash
# Discord Webhookテスト
curl -X POST https://discord.com/api/webhooks/YOUR/WEBHOOK/URL \
  -H 'Content-type: application/json' \
  --data '{"content":"Test message"}'
```

### エラーメッセージ対応

| エラー | 原因 | 解決方法 |
|-------|------|----------|
| `invalid_token` | Webhook URLが無効 | 新しいWebhook URLを生成 |
| `404 Not Found` | URLが間違っている | URLを再確認 |
| `rate_limited` | レート制限超過 | 通知頻度を調整 |
| `timeout` | ネットワーク問題 | ネットワーク設定確認 |

## ベストプラクティス

### 1. 通知の優先度設定
- **Critical (P0)**: 1時間以内に対応が必要 → Discord + GitHub Issue
- **High (P1)**: 4時間以内に対応 → Discord + GitHub Issue
- **Medium (P2)**: 24時間以内に対応 → GitHub Issue
- **Low**: 情報共有のみ → ログのみ

### 2. 通知疲れの防止
- 重要なアラートのみ通知
- 同種のアラートをグループ化
- 通知時間帯の設定
- ノイズの削減

### 3. エスカレーションルール
1. 初回通知: Discord通知 + GitHub Issue作成
2. Critical/High: 自動で担当者アサイン
3. SLA超過: 優先度自動昇格
4. 長期未対応: 定期リマインド（GitHub Actions）

### 4. 通知内容の充実
- エラーの詳細情報を含める
- 対応手順へのリンクを追加
- 関連するログへのアクセス方法
- 過去の類似事例への参照

## 監視ダッシュボード統合

### Grafana連携（オプション）
```yaml
# メトリクスをGrafanaに送信
- name: Send to Grafana
  env:
    GRAFANA_API_KEY: ${{ secrets.GRAFANA_API_KEY }}
  run: |
    curl -X POST https://grafana.example.com/api/annotations \
      -H "Authorization: Bearer $GRAFANA_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"text": "Alert", "tags": ["github", "workflow"]}'
```

## まとめ

効果的なアラート設定により:
- 問題の早期発見
- 迅速な対応
- サービス品質の向上
- 個人開発でも本格的な運用

## 主な通知先

| 通知タイプ | Discord | GitHub Issue |
|-----------|---------|-------------|
| ワークフロー失敗 | ✅ | ✅（重要なもののみ） |
| パフォーマンス警告 | ✅ | ✅（20分超過時） |
| セキュリティアラート | ✅（P0/P1のみ） | ✅（全て） |
| 高優先度アラート | ✅ | ✅ |
| テストアラート | ✅ | ❌ |

DiscordとGitHub Issuesを組み合わせることで、リアルタイム通知と追跡管理の両方を実現します。