# 🔄 ロールバック手順書

秘密情報クリーンアップ実施後に問題が発生した場合の復旧手順

---

## 🎯 ロールバック概要

### 適用ケース

- クリーンアップスクリプト実行後にCI/CDが失敗
- 新しいトークンが正常に動作しない
- 環境ファイル削除により開発環境が起動しない
- GitHub Secretsの設定ミス

### 前提条件

- バックアップディレクトリ（`backup-secrets-*`）が存在すること
- Git履歴は改変されていないこと（Git履歴クリーンアップは未実施）

---

## 📋 ロールバック手順

### Phase 1: 影響範囲の特定

#### 1.1 エラー内容の確認

```bash
# CI/CDログ確認
gh run list --limit 5
gh run view <run_id> --log-failed

# ローカル開発環境エラー
cd backend && uvicorn src.main:app --reload
cd frontend && pnpm dev

# 環境変数の確認
echo $CLOUDFLARE_API_TOKEN
echo $DISCORD_WEBHOOK_URL
```

#### 1.2 バックアップディレクトリの確認

```bash
# バックアップ一覧表示
ls -la backup-secrets-*

# 最新バックアップの中身確認
ls -la backup-secrets-$(ls -t backup-secrets-* | head -1)

# バックアップ環境変数の確認（値は表示しない）
grep -o "^[A-Z_]*=" backup-secrets-*/backend/.env.local
```

---

### Phase 2: 環境ファイルの復元

#### 2.1 単一ファイルの復元

```bash
# 特定ファイルのみ復元
BACKUP_DIR=$(ls -td backup-secrets-* | head -1)

# 例: backend/.env.localの復元
cp "$BACKUP_DIR/backend/.env.local" backend/.env.local
log "復元完了: backend/.env.local"

# 復元後の検証
ls -la backend/.env.local
head -n 5 backend/.env.local  # 先頭5行のみ表示
```

#### 2.2 全環境ファイルの一括復元

```bash
#!/bin/bash
set -euo pipefail

# 最新バックアップディレクトリを取得
BACKUP_DIR=$(ls -td backup-secrets-* | head -1)

if [[ -z "$BACKUP_DIR" ]]; then
    echo "エラー: バックアップディレクトリが見つかりません"
    exit 1
fi

echo "バックアップディレクトリ: $BACKUP_DIR"

# 環境ファイル一覧
FILES=(
    ".env"
    "backend/.env"
    "backend/.env.local"
    "backend/.env.production"
    "backend/.env.staging"
    "backend/.env.test"
    "frontend/.env.local"
    "frontend/.env.production"
    "frontend/.env.staging"
)

# 一括復元
for file in "${FILES[@]}"; do
    backup_file="$BACKUP_DIR/$(basename "$file")"
    if [[ -f "$backup_file" ]]; then
        cp "$backup_file" "$file"
        echo "✅ 復元完了: $file"
    else
        echo "⚠️  バックアップが存在しません: $file"
    fi
done

echo ""
echo "🎉 環境ファイルの復元完了"
```

---

### Phase 3: GitHub Secretsのロールバック

#### 3.1 既存Secretsの確認

```bash
# 現在のSecrets一覧
gh secret list

# 特定Secretの削除
gh secret remove DISCORD_WEBHOOK_URL
gh secret remove CLOUDFLARE_API_TOKEN
```

#### 3.2 旧トークンの再設定

```bash
# バックアップから旧トークンを取得（手動でコピー）
cat backup-secrets-*/backend/.env.local | grep DISCORD_WEBHOOK_URL
cat backup-secrets-*/backend/.env.local | grep CLOUDFLARE_API_TOKEN

# GitHub Secretsに再設定
gh secret set DISCORD_WEBHOOK_URL --body "<旧webhook_url>"
gh secret set CLOUDFLARE_API_TOKEN --body "<旧api_token>"

# 環境別Secrets
gh secret set CLOUDFLARE_API_TOKEN_PROD --env production --body "<旧token>"
gh secret set CLOUDFLARE_API_TOKEN_STAGING --env staging --body "<旧token>"
```

---

### Phase 4: Cloudflare Workers Secretsの復元

#### 4.1 現在のSecrets確認

```bash
# Cloudflare Workers Secrets一覧
cd infrastructure/cloudflare/workers
wrangler secret list

# 特定Secretの削除
wrangler secret delete CLOUDFLARE_API_TOKEN
wrangler secret delete DISCORD_WEBHOOK_URL
```

#### 4.2 旧Secretsの再設定

```bash
# 旧トークンをCloudflare Workersに再設定
wrangler secret put CLOUDFLARE_API_TOKEN
# プロンプトで旧トークンを貼り付け

wrangler secret put DISCORD_WEBHOOK_URL
# プロンプトで旧Webhook URLを貼り付け
```

---

### Phase 5: CI/CDパイプラインの復旧

#### 5.1 ワークフロー変更のrevert

```bash
# 最近のコミットを確認
git log --oneline -10

# セキュリティ対応PRのコミットを特定
git log --grep="TruffleHog" --oneline

# 特定コミットをrevert
git revert <commit_hash>
git push origin <branch_name>
```

#### 5.2 ワークフロー手動トリガー

```bash
# CI/CDワークフロー再実行
gh workflow run ci.yml --ref <branch_name>
gh workflow run security-scan.yml --ref <branch_name>

# 実行状況確認
gh run watch
```

---

### Phase 6: pre-commit フックの無効化

#### 6.1 TruffleHogフック削除

```bash
# .pre-commit-config.yamlの編集
# TruffleHog関連のフックをコメントアウト

# 例:
# repos:
#   - repo: https://github.com/trufflesecurity/trufflehog
#     rev: v3.82.13
#     hooks:
#       - id: trufflehog  # ← この行をコメントアウト

# pre-commitキャッシュクリア
pre-commit clean
pre-commit uninstall
```

#### 6.2 pre-commit再インストール（オプション）

```bash
# TruffleHogなしで再インストール
pre-commit install

# 動作確認
pre-commit run --all-files
```

---

### Phase 7: 検証

#### 7.1 ローカル開発環境の起動確認

```bash
# バックエンド起動
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# フロントエンド起動
cd frontend
pnpm dev

# 疎通確認
curl http://localhost:8000/health
curl http://localhost:3000
```

#### 7.2 CI/CDパイプライン確認

```bash
# 最新ワークフロー実行状況
gh run list --limit 5

# 特定ワークフローの詳細
gh run view <run_id>

# すべてのジョブが成功していることを確認
gh run view <run_id> --log
```

#### 7.3 環境変数の検証

```bash
# GitHub Secretsが正しく設定されているか確認
gh secret list

# Cloudflare Workers Secretsの確認
wrangler secret list

# ローカル環境変数の確認（値は表示しない）
grep -o "^[A-Z_]*=" backend/.env.local
```

---

## 🚨 ロールバック後の対応

### 完了確認チェックリスト

- [ ] ローカル開発環境が正常起動
- [ ] CI/CDパイプラインが成功
- [ ] GitHub Secrets設定完了
- [ ] Cloudflare Workers Secrets設定完了
- [ ] 環境ファイルが復元されている

### 次のステップ

1. **根本原因の分析**

   - なぜロールバックが必要だったのか
   - どの手順で問題が発生したか
   - ドキュメントの不備はないか

2. **対策の見直し**

   - 対応計画の修正
   - スクリプトのデバッグ
   - 段階的アプローチの再検討

3. **再実行の計画**
   - より慎重なPhase別実施
   - 各Phase後の検証強化
   - チーム全体への事前通知徹底

---

## 📝 ロールバックログ

### テンプレート

```markdown
## ロールバック実施記録

**実施日時**: 2025-10-XX XX:XX **実施者**: [名前] **ロールバック理由**:
[理由を詳細に記述]

**影響範囲**:

- [ ] ローカル開発環境
- [ ] CI/CDパイプライン
- [ ] GitHub Secrets
- [ ] Cloudflare Workers

**実施手順**:

1. Phase X: [実施内容]
2. Phase Y: [実施内容]

**復旧結果**:

- [ ] ローカル環境正常化
- [ ] CI/CD成功
- [ ] 機能動作確認完了

**根本原因**: [問題の根本原因を記述]

**再発防止策**: [今後の対策を記述]

**関連Issue**: #XXX
```

---

## 🔗 関連ドキュメント

- [対応計画書](SECRET_REMEDIATION_PLAN.md)
- [実行スクリプト](../../scripts/security/cleanup-secrets.sh)
- [チーム通知テンプレート](TEAM_NOTIFICATION_TEMPLATE.md)

---

## 📞 エスカレーション

### 連絡先

- **セキュリティ担当**: [担当者名・連絡先]
- **DevOps担当**: [担当者名・連絡先]
- **テックリード**: [担当者名・連絡先]

### エスカレーション基準

- **CRITICAL**: 本番環境が停止・動作不能
- **HIGH**: 開発環境が全員影響・CI/CD完全停止
- **MEDIUM**: 一部環境のみ影響・復旧手順が不明

---

**作成日**: 2025年10月8日 **最終更新**: 2025年10月8日 **責任者**:
version-control-specialist Agent **ステータス**: 準備完了
