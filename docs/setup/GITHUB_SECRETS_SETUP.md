# GitHub Secrets セットアップガイド

**作成日**: 2025-10-01
**対象環境**: Production / Staging
**セキュリティレベル**: Critical

## 🎯 概要

AutoForgeNexusプロジェクトで使用するGitHub Secretsの設定ガイド。
`.env.production`と`.env.staging`の環境変数をGitHub Secretsに安全に保管します。

## 🔐 セキュリティ原則

1. **実際の値は絶対にコミットしない**
2. **Production/Staging環境でのみSecrets使用**
3. **ローカル開発では`.env.local`使用**
4. **Secretsのローテーション（90日毎推奨）**
5. **最小権限の原則（必要なSecretsのみアクセス）**

## 📋 必須Secrets一覧

### Backend Production Secrets

```bash
# === Database ===
PROD_TURSO_DATABASE_URL=libsql://autoforgenexus-xxx.turso.io
PROD_TURSO_AUTH_TOKEN=eyJhbGc...

# === Cache ===
PROD_REDIS_HOST=redis-production.example.com
PROD_REDIS_PASSWORD=xxx

# === Authentication ===
PROD_CLERK_SECRET_KEY=sk_live_xxx
PROD_CLERK_PUBLIC_KEY=pk_live_xxx
PROD_CLERK_WEBHOOK_SECRET=whsec_xxx

# === JWT ===
PROD_JWT_SECRET_KEY=xxx-production-secret-xxx

# === LLM API Keys ===
PROD_OPENAI_API_KEY=sk-proj-xxx
PROD_ANTHROPIC_API_KEY=sk-ant-xxx
PROD_GOOGLE_AI_API_KEY=AIza...
PROD_MISTRAL_API_KEY=xxx
PROD_COHERE_API_KEY=xxx
PROD_HUGGINGFACE_API_KEY=hf_xxx

# === LiteLLM ===
PROD_LITELLM_API_KEY=sk-xxx

# === Observability ===
PROD_LANGFUSE_PUBLIC_KEY=pk-lf-xxx
PROD_LANGFUSE_SECRET_KEY=sk-lf-xxx

# === Cloudflare ===
PROD_CLOUDFLARE_ACCOUNT_ID=xxx
PROD_CLOUDFLARE_API_TOKEN=xxx
PROD_CLOUDFLARE_ZONE_ID=xxx

# === S3/R2 Storage ===
PROD_S3_ACCESS_KEY_ID=xxx
PROD_S3_SECRET_ACCESS_KEY=xxx
PROD_S3_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com

# === Monitoring ===
PROD_SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Backend Staging Secrets

```bash
# === Database ===
STAGING_TURSO_DATABASE_URL=libsql://autoforgenexus-staging-xxx.turso.io
STAGING_TURSO_AUTH_TOKEN=eyJhbGc...

# === Cache ===
STAGING_REDIS_HOST=redis-staging.example.com
STAGING_REDIS_PASSWORD=xxx

# === Authentication ===
STAGING_CLERK_SECRET_KEY=sk_test_xxx
STAGING_CLERK_PUBLIC_KEY=pk_test_xxx
STAGING_CLERK_WEBHOOK_SECRET=whsec_xxx

# === JWT ===
STAGING_JWT_SECRET_KEY=xxx-staging-secret-xxx

# === LLM API Keys (Test Keys) ===
STAGING_OPENAI_API_KEY=sk-proj-xxx
STAGING_ANTHROPIC_API_KEY=sk-ant-xxx
STAGING_GOOGLE_AI_API_KEY=AIza...
STAGING_MISTRAL_API_KEY=xxx
STAGING_COHERE_API_KEY=xxx
STAGING_HUGGINGFACE_API_KEY=hf_xxx

# === LiteLLM ===
STAGING_LITELLM_API_KEY=sk-xxx

# === Observability ===
STAGING_LANGFUSE_PUBLIC_KEY=pk-lf-xxx
STAGING_LANGFUSE_SECRET_KEY=sk-lf-xxx

# === Cloudflare ===
STAGING_CLOUDFLARE_ACCOUNT_ID=xxx
STAGING_CLOUDFLARE_API_TOKEN=xxx
STAGING_CLOUDFLARE_ZONE_ID=xxx

# === S3/R2 Storage ===
STAGING_S3_ACCESS_KEY_ID=xxx
STAGING_S3_SECRET_ACCESS_KEY=xxx
STAGING_S3_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com

# === Monitoring ===
STAGING_SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Frontend Production Secrets

```bash
# === Clerk ===
PROD_CLERK_PUBLIC_KEY=pk_live_xxx

# === Analytics ===
PROD_GA_MEASUREMENT_ID=G-XXXXXXXXXX
PROD_POSTHOG_KEY=phc_xxx

# === Error Tracking ===
PROD_SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Frontend Staging Secrets

```bash
# === Clerk ===
STAGING_CLERK_PUBLIC_KEY=pk_test_xxx

# === Analytics ===
STAGING_GA_MEASUREMENT_ID=G-XXXXXXXXXX
STAGING_POSTHOG_KEY=phc_xxx

# === Error Tracking ===
STAGING_SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Shared Secrets

```bash
# === GitHub ===
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx
GITHUB_TOKEN=ghp_xxx  # GitHub Actions自動生成、通常設定不要

# === Cloudflare (Shared) ===
CLOUDFLARE_API_TOKEN=xxx  # Workers/Pages共通
```

## 🚀 セットアップ手順

### 1. GitHub Secretsに登録

```bash
# GitHub CLI使用（推奨）
gh secret set PROD_TURSO_DATABASE_URL -b "libsql://xxx.turso.io"
gh secret set PROD_TURSO_AUTH_TOKEN -b "eyJhbGc..."
gh secret set PROD_CLERK_SECRET_KEY -b "sk_live_xxx"
# ... 以下同様

# または GitHub Web UIから設定
# Settings → Secrets and variables → Actions → New repository secret
```

### 2. Environment Secrets設定

```bash
# Production Environment
gh secret set PROD_OPENAI_API_KEY -b "sk-proj-xxx" --env production
gh secret set PROD_ANTHROPIC_API_KEY -b "sk-ant-xxx" --env production

# Staging Environment
gh secret set STAGING_OPENAI_API_KEY -b "sk-proj-xxx" --env staging
gh secret set STAGING_ANTHROPIC_API_KEY -b "sk-ant-xxx" --env staging
```

### 3. ワークフローでの使用例

```yaml
# .github/workflows/cd.yml
jobs:
  deploy-backend:
    environment: production  # または staging
    steps:
      - name: Deploy to Cloudflare Workers
        env:
          # Secrets → 環境変数へマッピング
          TURSO_DATABASE_URL: ${{ secrets.PROD_TURSO_DATABASE_URL }}
          TURSO_AUTH_TOKEN: ${{ secrets.PROD_TURSO_AUTH_TOKEN }}
          CLERK_SECRET_KEY: ${{ secrets.PROD_CLERK_SECRET_KEY }}
          OPENAI_API_KEY: ${{ secrets.PROD_OPENAI_API_KEY }}
        run: |
          # デプロイコマンド
          wrangler deploy
```

## 📝 .envファイル管理方針

### ローカル開発（`.env.local`）
```bash
# backend/.env.local - Gitignore対象
APP_ENV=local
DEBUG=true
DATABASE_URL=sqlite:///./data/autoforge_dev.db
REDIS_URL=redis://localhost:6379/0
# 実際の開発用値を記載
```

### Production（`.env.production`）
```bash
# backend/.env.production - テンプレートのみコミット
APP_ENV=production
DEBUG=false
# 実際の値は ${PROD_*} プレースホルダーのみ
TURSO_DATABASE_URL=${PROD_TURSO_DATABASE_URL}
CLERK_SECRET_KEY=${PROD_CLERK_SECRET_KEY}
```

### Staging（`.env.staging`）
```bash
# backend/.env.staging - テンプレートのみコミット
APP_ENV=staging
DEBUG=false
# 実際の値は ${STAGING_*} プレースホルダーのみ
TURSO_DATABASE_URL=${STAGING_TURSO_DATABASE_URL}
CLERK_SECRET_KEY=${STAGING_CLERK_SECRET_KEY}
```

## 🔒 セキュリティベストプラクティス

### 1. Secretsのローテーション

```bash
# 90日毎に更新推奨
gh secret set PROD_CLERK_SECRET_KEY -b "新しい値"
```

### 2. 権限最小化

```yaml
permissions:
  contents: read
  id-token: write  # OIDC認証用のみ
  # 不要な権限は付与しない
```

### 3. 環境分離

- **Production**: 本番用Secrets（厳格な管理）
- **Staging**: ステージング用Secrets（テスト用API Key）
- **Development**: ローカル`.env.local`（Gitignore）

### 4. 監査ログ

```bash
# Secretsアクセス履歴確認
gh api /repos/{owner}/{repo}/actions/secrets
```

## 🚨 緊急対応

### Secrets漏洩時の対応

1. **即座に無効化**
   ```bash
   # 漏洩したSecretを削除
   gh secret delete LEAKED_SECRET_NAME
   ```

2. **新しいキーを生成**
   - サービス側で新しいキーを発行
   - GitHub Secretsに新しい値を設定

3. **影響範囲の調査**
   - アクセスログ確認
   - 不正使用の検出

4. **再デプロイ**
   ```bash
   # 新しいSecretsで再デプロイ
   gh workflow run cd.yml -f environment=production
   ```

## 📊 Secrets管理チェックリスト

### 初期セットアップ
- [ ] すべてのProduction Secretsを登録
- [ ] すべてのStaging Secretsを登録
- [ ] Environment Secretsを設定（production/staging）
- [ ] `.env.production`/`.env.staging`をプレースホルダーのみに変更
- [ ] `.env.local`を`.gitignore`に追加確認

### 定期メンテナンス
- [ ] 90日毎にSecretsローテーション
- [ ] 未使用Secretsの削除
- [ ] アクセス権限の監査
- [ ] ワークフロー実行ログの確認

### デプロイ前
- [ ] 必要なSecretsがすべて設定されているか確認
- [ ] Environment設定が正しいか確認
- [ ] ワークフローでのSecretsマッピングが正しいか確認

## 🔗 関連ドキュメント

- [GitHub Actions Secrets 公式ドキュメント](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [環境別デプロイ戦略](./MVP_DEPLOYMENT_CHECKLIST.md)
- [セキュリティポリシー](../security/SECURITY_POLICY.md)
- [Clerk認証設定](./EXTERNAL_SERVICES_SETUP_GUIDE.md#clerk)
- [Tursoデータベース設定](./DATABASE_SETUP_GUIDE.md)

## 💡 トラブルシューティング

### Secret未設定エラー
```
Error: Secret PROD_TURSO_DATABASE_URL not found
```
**対処**: GitHub UIまたは`gh secret set`でSecret登録

### 環境変数置換失敗
```
Error: ${PROD_XXX} が展開されない
```
**対処**: ワークフローで`env:`セクションにSecretsマッピング追加

### 権限エラー
```
Error: Resource not accessible by integration
```
**対処**: ワークフローの`permissions:`を確認、必要最小限の権限を付与

---

**重要**: 実際のSecret値は絶対にGitにコミットしないでください。
このドキュメントはセットアップ手順のみを記載しています。
