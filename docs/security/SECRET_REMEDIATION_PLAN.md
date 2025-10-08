# 秘密情報検出対応計画

## 🎯 状況サマリー

TruffleHogが検出した秘密情報への対応計画（2025年10月8日作成）

### 検出結果
- **Discord Webhook URL**: `.env`, `backend/.env.local`
- **Cloudflare API Token**: `.env`, `backend/.env.*`（複数環境ファイル）
- **Git履歴**: ✅ クリーン（過去コミットに秘密情報なし）

### 診断コマンド実行履歴
```bash
# Git履歴確認 → 秘密情報なし
git log --all --oneline --follow -- .env
git log --all --full-history -- .env backend/.env.local

# .envファイル検索 → 14ファイル検出
find . -name ".env*" -not -path "*/node_modules/*"

# 秘密情報特定
grep -l "discord.com/api/webhooks" .env backend/.env*
grep -l "CLOUDFLARE_API_TOKEN" .env backend/.env*
```

## ✅ 確認された安全性

### Git履歴
- ✅ `.env`ファイルは過去コミットに含まれていない
- ✅ `.gitignore`は完璧（`.env`, `.env.*`, `.env.local`除外済み）
- ✅ Git履歴書き換え（git-filter-repo等）は**不要**

### 現状
- ⚠️ ワーキングディレクトリに秘密情報が存在
- ⚠️ 環境ファイルが複数に分散（14ファイル）
- ⚠️ 一部ファイルが本番環境用（`.env.production`, `.env.staging`）

## 🔒 対策実施計画

### Phase 1: 即時対応（CRITICAL）

#### 1.1 秘密情報のローテーション
```bash
# Discord Webhook URL
# → Discordダッシュボードで新規Webhook作成
# → 既存Webhookを無効化

# Cloudflare API Token
# → Cloudflare Dashboardで新規Token発行
# → 既存Tokenを即座に削除（Revoke）
```

**実施期限**: 2025年10月8日中

#### 1.2 GitHub Secrets統合
```bash
# GitHub Secretsに登録（リポジトリ設定）
gh secret set DISCORD_WEBHOOK_URL --body "new_webhook_url"
gh secret set CLOUDFLARE_API_TOKEN --body "new_api_token"

# GitHub Actions環境別Secrets
gh secret set CLOUDFLARE_API_TOKEN_PROD --env production
gh secret set CLOUDFLARE_API_TOKEN_STAGING --env staging
```

**実施期限**: 2025年10月8日中

### Phase 2: 環境ファイル整理（HIGH）

#### 2.1 .envファイル構造の最適化
```bash
# 現状: 14ファイル分散 → 目標: exampleファイルのみ

# 削除対象（Git管理外）
.env
backend/.env
backend/.env.local
backend/.env.production
backend/.env.staging
backend/.env.test
frontend/.env.local
frontend/.env.production
frontend/.env.staging

# 保持対象（Git管理、秘密情報なし）
backend/.env.example
backend/.env.production.example
frontend/.env.example
.claude/.env.example
infrastructure/cloudflare/workers/.env.example
```

**実施期限**: 2025年10月9日

#### 2.2 環境変数管理の統一化
```bash
# 開発環境: .env.exampleをコピー
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 本番環境: GitHub Secrets + Cloudflare Workers環境変数
wrangler secret put CLOUDFLARE_API_TOKEN
wrangler secret put DISCORD_WEBHOOK_URL
```

**実施期限**: 2025年10月9日

### Phase 3: 自動検知強化（MEDIUM）

#### 3.1 pre-commit フックの厳格化
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/trufflesecurity/trufflehog
    rev: v3.82.13
    hooks:
      - id: trufflehog
        name: TruffleHog秘密検知
        entry: trufflehog filesystem .
        language: system
        stages: [commit]

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        name: Detect Secrets
        args: ['--baseline', '.secrets.baseline']
        stages: [commit]
```

**実施期限**: 2025年10月10日

#### 3.2 CI/CDでの検証強化
```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [main, develop, 'feature/**']
  pull_request:
    branches: [main, develop]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 全履歴取得

      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --only-verified --fail
```

**実施期限**: 2025年10月10日

### Phase 4: ドキュメント整備（LOW）

#### 4.1 環境変数管理ガイド作成
```markdown
# docs/setup/ENVIRONMENT_VARIABLES.md

## 環境変数の管理方針
- ローカル開発: .env.exampleをコピー
- CI/CD: GitHub Secrets
- 本番環境: Cloudflare Workers Secrets
```

**実施期限**: 2025年10月11日

#### 4.2 セキュリティポリシー更新
```markdown
# docs/security/SECURITY_POLICY.md

## 秘密情報管理
- .envファイルは絶対にコミットしない
- API Keyは90日ごとにローテーション
- 検出時は即座にRevoke + Issue報告
```

**実施期限**: 2025年10月11日

## 📋 チェックリスト

### 即時対応（2025年10月8日）
- [ ] Discord Webhook URL無効化 + 再発行
- [ ] Cloudflare API Token削除 + 再発行
- [ ] GitHub Secretsに新しいトークン登録
- [ ] ローカル.envファイルを新トークンで更新

### 環境整理（2025年10月9日）
- [ ] 不要な.envファイル削除（14 → 5ファイル）
- [ ] .env.exampleの最新化
- [ ] Cloudflare Workers環境変数設定
- [ ] CI/CDパイプラインでの動作確認

### 自動化強化（2025年10月10日）
- [ ] pre-commit フック統合
- [ ] GitHub Actions秘密検知強化
- [ ] ベースライン設定（.secrets.baseline）
- [ ] 全ブランチでの検証実施

### ドキュメント（2025年10月11日）
- [ ] 環境変数管理ガイド作成
- [ ] セキュリティポリシー更新
- [ ] チーム通知・研修実施
- [ ] 定期監査手順確立

## 🚨 緊急時対応手順

### 秘密情報が漏洩した場合
1. **即座に無効化**: 該当トークン・Webhookを削除
2. **影響範囲調査**: アクセスログ・監査ログ確認
3. **再発行**: 新しいトークン発行 + GitHub Secrets更新
4. **インシデント報告**: Issue作成 + チーム通知
5. **再発防止**: pre-commitフック強化

### エスカレーション基準
- **CRITICAL**: 本番環境のAPIキー漏洩
- **HIGH**: ステージング環境のトークン漏洩
- **MEDIUM**: 開発環境の秘密情報漏洩

## 📊 成功メトリクス

- ✅ TruffleHogスキャンで検出ゼロ
- ✅ 環境ファイル5個以下に集約
- ✅ pre-commit フック導入率100%
- ✅ 定期監査（月次）実施率100%

## 📝 参考リソース

- [TruffleHog公式ドキュメント](https://github.com/trufflesecurity/trufflehog)
- [GitHub Secrets管理](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Cloudflare Workers Secrets](https://developers.cloudflare.com/workers/configuration/secrets/)
- [OWASP Secret Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

**作成日**: 2025年10月8日
**最終更新**: 2025年10月8日
**責任者**: version-control-specialist Agent
**ステータス**: Phase 1実施中
