# 🚀 TruffleHog検出対応 - クイックリファレンス

秘密情報検出時の即座に使える1ページリファレンス

---

## 📊 現状確認（1分）

```bash
# Git履歴に秘密情報があるか確認
git log --all --oneline --follow -- .env

# .envファイル一覧
find . -name ".env*" -not -path "*/node_modules/*" -not -path "*/.git/*"

# .gitignore設定確認
grep -E "(\.env|secret|key)" .gitignore
```

**結果**: ✅ Git履歴クリーン、✅ .gitignore適切 → Git履歴書き換え不要

---

## ⚡ 即時対応（5分）

### 1. 秘密情報の無効化
```bash
# Discord Webhook
# → https://discord.com/developers/applications
# → 既存Webhook削除 + 新規作成

# Cloudflare API Token
# → https://dash.cloudflare.com/profile/api-tokens
# → 既存Token削除 + 新規発行（読み取り権限のみ）
```

### 2. GitHub Secretsに登録
```bash
gh secret set DISCORD_WEBHOOK_URL --body "<新webhook_url>"
gh secret set CLOUDFLARE_API_TOKEN --body "<新api_token>"
```

---

## 🧹 環境クリーンアップ（5分）

### 自動スクリプト実行
```bash
# バックアップ + 削除 + 検証
./scripts/security/cleanup-secrets.sh
```

### 手動実行（スクリプトが使えない場合）
```bash
# バックアップ
BACKUP_DIR="backup-secrets-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp .env backend/.env* "$BACKUP_DIR/"

# 削除
rm .env backend/.env backend/.env.local backend/.env.production backend/.env.staging

# .env.exampleから作成
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

---

## ✅ 検証（3分）

```bash
# 1. TruffleHogスキャン
docker run --rm -v $(pwd):/tmp trufflesecurity/trufflehog:latest \
  git file:///tmp/ --only-verified

# 2. Git状態確認
git status
git diff --cached --name-only | grep "\.env"

# 3. 開発環境起動
cd backend && uvicorn src.main:app --reload
cd frontend && pnpm dev
```

**期待結果**:
- ✅ TruffleHog検出ゼロ
- ✅ .envファイルがステージングされていない
- ✅ ローカル開発環境が起動

---

## 🔄 ロールバック（問題発生時）

```bash
# 最新バックアップから復元
BACKUP_DIR=$(ls -td backup-secrets-* | head -1)
cp "$BACKUP_DIR"/* ./

# GitHub Secrets削除
gh secret remove DISCORD_WEBHOOK_URL
gh secret remove CLOUDFLARE_API_TOKEN

# 詳細: docs/security/ROLLBACK_PROCEDURE.md
```

---

## 📋 チェックリスト

### Phase 1: 即時対応（本日中）
- [ ] Discord Webhook無効化 + 再発行
- [ ] Cloudflare Token削除 + 再発行
- [ ] GitHub Secrets登録
- [ ] 環境ファイルクリーンアップ
- [ ] TruffleHogスキャンで検出ゼロ

### Phase 2: 自動化（翌日）
- [ ] pre-commit フック統合
- [ ] CI/CD秘密検知強化
- [ ] ベースライン設定

### Phase 3: ドキュメント（2日後）
- [ ] 環境変数管理ガイド作成
- [ ] チーム通知・研修実施

---

## 🚨 緊急連絡先

- **セキュリティ担当**: [担当者名]
- **DevOps担当**: [担当者名]
- **テックリード**: [担当者名]

---

## 📚 詳細ドキュメント

| ドキュメント | 用途 |
|------------|------|
| [SECRET_REMEDIATION_PLAN.md](SECRET_REMEDIATION_PLAN.md) | 全体計画・詳細手順 |
| [cleanup-secrets.sh](../../scripts/security/cleanup-secrets.sh) | 自動クリーンアップスクリプト |
| [TEAM_NOTIFICATION_TEMPLATE.md](TEAM_NOTIFICATION_TEMPLATE.md) | チーム通知テンプレート |
| [ROLLBACK_PROCEDURE.md](ROLLBACK_PROCEDURE.md) | ロールバック手順 |

---

## 💡 よくある質問

**Q: Git履歴を書き換える必要はありますか？**
A: いいえ。Git履歴には秘密情報が含まれていないため、git-filter-repo等は不要です。

**Q: 開発環境が起動しなくなりました**
A: `backup-secrets-*`ディレクトリから.envファイルを復元してください。

**Q: TruffleHogがまだ検出します**
A: .envファイルが残っているか確認。`git status`で追跡されていないか確認。

**Q: チームメンバーに通知すべきですか？**
A: はい。[TEAM_NOTIFICATION_TEMPLATE.md](TEAM_NOTIFICATION_TEMPLATE.md)を使用してください。

---

**最終更新**: 2025年10月8日
**責任者**: version-control-specialist Agent
