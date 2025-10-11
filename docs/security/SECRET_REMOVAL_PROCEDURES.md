# 🚨 秘密情報履歴除去手順書

## 状況概要

**リスクレベル**: 🔴 **CRITICAL**

---

## ⚠️ 事前準備（必須）

### 1. 秘密情報の即座の無効化

**最優先で実行してください**:

```bash
# GitHub Personal Access Token を無効化
# 1. https://github.com/settings/tokens にアクセス
# 2. 該当トークンを削除
# 3. 新しいトークンを生成（必要に応じて）

# Cloudflare API Token を無効化
# 1. https://dash.cloudflare.com/profile/api-tokens にアクセス
# 2. 該当トークンを削除
# 3. 新しいトークンを生成

# Brave Search API Key を無効化
# 1. https://api.search.brave.com/app/keys にアクセス
# 2. 該当キーを無効化
# 3. 新しいキーを生成

# Discord Webhook を再生成
# 1. Discord チャンネル設定 → 連携サービス → Webhooks
# 2. 既存Webhookを削除
# 3. 新しいWebhookを作成
```

### 2. バックアップ作成

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus

# 現在のブランチをバックアップ
git checkout feature/phase2-infrastructure-setup
git branch backup-before-secret-removal-$(date +%Y%m%d-%H%M%S)

# 作業用ブランチを作成
git checkout -b secret-removal-$(date +%Y%m%d-%H%M%S)
```

---

## 🛠️ 履歴クリーニング手順

### 方法 1: git filter-branch（推奨・確実）

```bash
# 1. 問題のファイルを履歴から完全除去
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch docs/security/SECURITY_IMPROVEMENTS_REPORT.md' \
  --prune-empty --tag-name-filter cat -- --all

# 2. reflogをクリーンアップ
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin

# 3. reflogを期限切れにする
git reflog expire --expire=now --all

# 4. ガベージコレクションを実行
git gc --prune=now --aggressive

# 5. 除去確認
echo "=== 秘密情報の残存チェック ==="
git log --all --full-history --grep="github_pat_" || echo "✅ GitHub Token not found"
git log --all --full-history --grep="FgOoUC-WVOS0" || echo "✅ Cloudflare Token not found"
git log --all --full-history --grep="BSABTeXrpBy5UtjduTGyrXHzbVRDo8h" || echo "✅ Brave API Key not found"
git log --all --full-history --grep="webhooks/REDACTED_WEBHOOK_ID" || echo "✅ Discord Webhook not found"
```

### 方法 2: BFG Repo-Cleaner（代替案）

```bash
# BFGをインストール（Java必須）
brew install bfg

# 秘密情報を含むファイルを削除
bfg --delete-files SECURITY_IMPROVEMENTS_REPORT.md

# ガベージコレクション
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

---

## 🔍 除去確認手順

### 1. ファイル検索確認

```bash
# ファイルが履歴に残っていないことを確認
git log --all --name-only | grep -i "SECURITY_IMPROVEMENTS_REPORT.md" || echo "✅ File not found in history"

# 秘密情報が含まれていないことを確認
git grep -r "github_pat_11AQ66RBQ" $(git rev-list --all) || echo "✅ GitHub Token removed"
git grep -r "FgOoUC-WVOS0_ALqVUsbos61jy0eyO06To6RNaE0" $(git rev-list --all) || echo "✅ Cloudflare Token removed"
git grep -r "BSABTeXrpBy5UtjduTGyrXHzbVRDo8h" $(git rev-list --all) || echo "✅ Brave API Key removed"
git grep -r "webhooks/REDACTED_WEBHOOK_ID" $(git rev-list --all) || echo "✅ Discord Webhook removed"
```

### 2. コミット履歴確認

```bash
# 問題のコミットが除去されたことを確認
git show 856c9fbdef822304fd8e1dd3401a23e3c0558de1 2>/dev/null || echo "✅ Problematic commit removed"

# ブランチの整合性確認
git log --oneline feature/phase2-infrastructure-setup | head -10
```

---

## 🚀 Force Push 準備手順

⚠️ **注意**: 以下のコマンドは実際には実行せず、準備のみ行ってください。

```bash
# Force pushの準備（実行しない）
echo "準備コマンド（実行しないでください）:"
echo "git push origin feature/phase2-infrastructure-setup --force-with-lease"

# チームメンバーがいる場合の通知準備
echo "=== チーム通知テンプレート ==="
echo "件名: [緊急] feature/phase2-infrastructure-setup ブランチの履歴書き換えについて"
echo ""
echo "セキュリティ上の理由により、feature/phase2-infrastructure-setup ブランチの"
echo "履歴を書き換えました。以下の手順でローカルブランチを更新してください："
echo ""
echo "git checkout feature/phase2-infrastructure-setup"
echo "git fetch origin"
echo "git reset --hard origin/feature/phase2-infrastructure-setup"
```

---

## 📋 実行後チェックリスト

### 即座に実行

- [ ] GitHub Personal Access Token を無効化
- [ ] Cloudflare API Token を無効化
- [ ] Brave Search API Key を無効化
- [ ] Discord Webhook を再生成
- [ ] 新しい秘密情報で環境変数を更新

### 履歴クリーニング

- [ ] バックアップブランチを作成
- [ ] git filter-branch または BFG で履歴をクリーニング
- [ ] 秘密情報の完全除去を確認
- [ ] ガベージコレクションを実行

### Force Push 前の確認

- [ ] 除去確認テストをすべて実行
- [ ] main ブランチに影響がないことを確認
- [ ] チームメンバーへの通知準備
- [ ] ローカルテスト環境での動作確認

### セキュリティ強化

- [ ] .env.example ファイルの見直し
- [ ] .gitignore ファイルの強化
- [ ] pre-commit フックの設定
- [ ] 秘密情報検出ツール（gitleaks 等）の導入

---

## 🛡️ 今後の予防策

### 1. .gitignore 強化

```gitignore
# 秘密情報ファイル
*.env
*.env.*
!*.env.example
.env.local
.env.production
secrets.json
config/secrets.*

# APIキー・トークンファイル
*api_key*
*token*
*secret*
credentials.*
auth.*
```

### 2. pre-commit フック設定

```bash
# gitleaks インストール
brew install gitleaks

# pre-commit hook 設定
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
gitleaks detect --source . --verbose
if [ $? -ne 0 ]; then
    echo "⚠️  秘密情報が検出されました。コミットを中止します。"
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

### 3. 継続的監視

```bash
# 定期的な秘密情報スキャン
gitleaks detect --source . --report-path security-scan.json

# GitHub Secrets Scanning の有効化
# Repository Settings → Security → Code security and analysis
```

---

## ⚡ 緊急時の連絡先

- **セキュリティインシデント**: GitHub Security Advisory
- **Cloudflare**: セキュリティセンター
- **チーム通知**: Discord/Slack セキュリティチャンネル

**最終更新**: 2025 年 9 月 27 日 **責任者**: version-control-specialist Agent
