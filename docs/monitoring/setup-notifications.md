# 📱 Discord・GitHub Issue 通知設定ガイド

このガイドでは、AutoForgeNexusの監視通知システムの設定方法を、画像付きでわかりやすく説明します。

## 🎯 必要なもの

- Discordアカウント（無料）
- GitHubアカウント（既にプロジェクトで使用中）
- 5〜10分の設定時間

---

## 🎮 Discord Webhook 設定方法

### Step 1: Discordサーバーの準備

#### 1-1. Discordサーバーを作成（既にある場合はスキップ）

1. **Discordを開く**
   - ブラウザ版: https://discord.com
   - デスクトップアプリ: ダウンロード済みの場合

2. **サーバーを作成**
   ```
   左サイドバーの「+」ボタンをクリック
   ↓
   「オリジナルの作成」を選択
   ↓
   「自分と友達のため」を選択
   ↓
   サーバー名: 「AutoForgeNexus開発」（例）
   ↓
   「作成」をクリック
   ```

### Step 2: Webhook URLの作成

#### 2-1. サーバー設定を開く

```
作成したサーバー名の横の「⌄」をクリック
↓
「サーバー設定」を選択
```

#### 2-2. 連携サービス（Webhook）設定

```
左メニューから「連携サービス」をクリック
↓
「ウェブフックを作成」ボタンをクリック
```

#### 2-3. Webhook の設定

```
1. 名前: 「AutoForgeNexus Alerts」（わかりやすい名前）
2. チャンネル: 通知を受け取りたいチャンネルを選択
   推奨: #alerts または #notifications チャンネルを作成
3. アバター: オプション（ロゴ画像など）
```

#### 2-4. Webhook URLをコピー

```
「ウェブフックURLをコピー」ボタンをクリック

URLの形式:
https://discord.com/api/webhooks/1234567890/abcdefghijklmnop...
```

⚠️ **重要**: このURLは秘密情報です。他人に教えないでください！

### Step 3: GitHub Secretsに登録

#### 3-1. GitHubリポジトリの設定ページへ

```
1. GitHubでAutoForgeNexusリポジトリを開く
2. 上部メニューの「Settings」タブをクリック
3. 左サイドバーの「Secrets and variables」→「Actions」をクリック
```

#### 3-2. 新しいSecretを作成

```
「New repository secret」ボタンをクリック
↓
Name: DISCORD_WEBHOOK_URL
Value: [先ほどコピーしたDiscordのWebhook URL]
↓
「Add secret」をクリック
```

### Step 4: 動作テスト

#### 4-1. GitHub CLIを使用した場合

```bash
# GitHub CLIがインストール済みの場合
gh workflow run alerts.yml -f alert_type=test
```

#### 4-2. GitHub Web UIを使用した場合

```
1. Actionsタブを開く
2. 左サイドバーから「Automated Alerts」を選択
3. 「Run workflow」をクリック
4. Alert type: 「test」を選択
5. 「Run workflow」ボタンをクリック
```

#### 4-3. テスト結果の確認

Discordに以下のようなメッセージが届けば成功です：

```
🧪 This is a test alert from AutoForgeNexus
```

---

## 📝 GitHub Issue 自動作成の仕組み

GitHub Issueは**追加設定不要**で自動的に作成されます！

### なぜ設定不要？

GitHub Actionsには、デフォルトで以下の権限が付与されています：

```yaml
permissions:
  issues: write        # Issue作成権限
  pull-requests: read  # PR読み取り権限
```

### 自動作成されるタイミング

#### 1. セキュリティ問題発生時

```yaml
条件: Issueに「security」ラベルが付いた時
動作:
  - 重要度を自動判定（P0/P1/P2）
  - 担当者を自動アサイン
  - SLA（対応期限）を設定
```

#### 2. ワークフロー失敗時（重要なもののみ）

```yaml
条件: Security または Deploy ワークフローが失敗
動作:
  - 自動でIssue作成
  - 「bug」「critical」ラベル付与
  - エラー詳細と対応手順を記載
```

#### 3. パフォーマンス問題時

```yaml
条件: ワークフロー実行時間が20分を超過
動作:
  - パフォーマンスIssue作成
  - 「performance」ラベル付与
  - 最適化の提案を含める
```

### Issue テンプレートの例

```markdown
## 🚨 Critical Workflow Failure: Security Scanning

**Workflow**: Security Scanning
**Branch**: main
**Commit**: abc123def456
**Run URL**: https://github.com/.../actions/runs/123456
**Actor**: @username
**Time**: 2024-01-15T10:30:00Z

### Action Required
This is a critical workflow failure that requires immediate attention.

### Investigation Steps
1. Check the [workflow run](URL)
2. Review the error logs
3. Identify the root cause
4. Create a fix or rollback if necessary

### Labels
- bug
- critical
- workflow-failure
```

---

## 🔧 よくあるトラブルと解決方法

### Discord通知が届かない場合

#### 1. Webhook URLの確認

```bash
# Secretが登録されているか確認
gh secret list

# 出力にDISCORD_WEBHOOK_URLが含まれていることを確認
```

#### 2. Webhook URLの再設定

```bash
# URLを再設定（新しいURLをコピー後）
gh secret set DISCORD_WEBHOOK_URL
# プロンプトが出たら、新しいURLをペースト
```

#### 3. Discord側の設定確認

- Webhookが削除されていないか
- チャンネルが存在するか
- サーバーの通知設定で無効化されていないか

### GitHub Issue が作成されない場合

#### 1. 権限の確認

```yaml
# .github/workflows/alerts.yml を確認
permissions:
  issues: write  # この行があることを確認
```

#### 2. ワークフローログの確認

```
1. Actionsタブを開く
2. 失敗したワークフローを選択
3. エラーメッセージを確認
```

#### 3. ラベルの存在確認

必要なラベルが存在することを確認：
- `security`
- `critical`
- `bug`
- `performance`

ラベルがない場合は手動で作成：

```
1. Issuesタブ → Labels
2. 「New label」をクリック
3. ラベル名と色を設定
```

---

## 🚀 クイックスタート（5分設定）

### 最速セットアップ手順

```bash
# 1. Discord Webhook URLを環境変数に設定（一時的）
export DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."

# 2. GitHub Secretに登録
gh secret set DISCORD_WEBHOOK_URL --body "$DISCORD_WEBHOOK"

# 3. テスト実行
gh workflow run alerts.yml -f alert_type=test

# 4. Discord確認
# テストメッセージが届いたら成功！
```

---

## 📊 通知のカスタマイズ

### Discord通知の見た目を変更

`.github/workflows/alerts.yml` を編集：

```yaml
# 色の変更（10進数で指定）
STATUS_COLOR=3066993   # 緑: 成功
STATUS_COLOR=16776960  # 黄: 警告
STATUS_COLOR=15158332  # 赤: エラー

# 絵文字の変更
content: "🎉 **Success!**"  # 成功時
content: "⚠️ **Warning!**"  # 警告時
content: "🚨 **Error!**"    # エラー時
```

### 通知頻度の調整

```yaml
# パフォーマンス閾値の変更（デフォルト: 10分）
if [ $RUN_DURATION_MS -gt 600000 ]; then  # 600000ms = 10分
  # この値を変更して調整
  # 例: 1200000 = 20分
```

---

## 💡 ベストプラクティス

### 1. 専用チャンネルの作成

Discord内で用途別にチャンネルを分ける：

```
📁 AutoForgeNexus開発
├── 📢 general
├── 🚨 alerts-critical  （P0/P1用）
├── ⚠️ alerts-warning   （P2用）
├── 📊 metrics         （メトリクス用）
└── 🧪 test-alerts     （テスト用）
```

### 2. 通知の優先度管理

```yaml
# 重要度別の通知先を分ける
P0_WEBHOOK_URL: 緊急用チャンネル
P1_WEBHOOK_URL: 重要用チャンネル
P2_WEBHOOK_URL: 通常用チャンネル
```

### 3. モバイル通知の設定

Discordアプリの通知設定：

```
1. スマートフォンにDiscordアプリをインストール
2. 設定 → 通知 → サーバー通知設定
3. AutoForgeNexusサーバー → 通知設定
4. 「@mentionsのみ」または「すべてのメッセージ」を選択
```

### 4. 定期的な動作確認

```bash
# 週1回のテスト実行をcronで設定
0 9 * * 1 gh workflow run alerts.yml -f alert_type=test
```

---

## 📞 サポート

設定で困った場合は：

1. **GitHub Discussions**: プロジェクトのDiscussionsで質問
2. **Issue作成**: 具体的な問題はIssueとして報告
3. **ドキュメント**: `/docs`ディレクトリの他のガイドも参照

---

## 🎯 チェックリスト

設定完了の確認：

- [ ] Discordサーバーを作成した
- [ ] Webhookを作成した
- [ ] Webhook URLをGitHub Secretsに登録した
- [ ] テストアラートが届いた
- [ ] GitHub Issueの自動作成を確認した
- [ ] モバイル通知を設定した（オプション）

すべてチェックできたら、監視システムの設定は完了です！🎉