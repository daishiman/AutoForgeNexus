# 環境変数設定分離ガイド
## AutoForgeNexus セキュリティ強化版

### 📋 概要

本ドキュメントは、AutoForgeNexusプロジェクトの環境変数を適切に分離・管理するためのガイドです。セキュリティ、保守性、スケーラビリティを考慮した設定構造を提供します。

**⚠️ 重要警告**: 現在の.envファイルには公開されたAPIキーやトークンが含まれています。これらは直ちに無効化し、新しいものを生成してください。

### 🔒 セキュリティ侵害の検出（例示）

以下の認証情報形式が露出していた例（モック値）:
- GitHub Personal Access Token: `ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
- Cloudflare API Token: `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`
- Discord Webhook URL: `https://discord.com/api/webhooks/XXXXX/XXXXX`
- Brave API Key: `BSABXXXXXXXXXXXXXXXXXXXXXXX`

**対応手順**:
1. 上記トークンを各サービスで即座に無効化
2. 新しいトークンを生成
3. `.env`ファイルを`.gitignore`に追加確認
4. リポジトリ履歴から機密情報を削除（BFG Repo-Cleanerを使用）

---

## 📁 推奨ディレクトリ構造

```
AutoForgeNexus/
├── .env                        # 共通設定（非機密）
├── .env.example               # 全体のテンプレート
├── .gitignore                 # *.local, *.production を除外
│
├── backend/
│   ├── .env.local            # ローカル開発環境（機密）
│   ├── .env.example          # バックエンドテンプレート
│   ├── .env.test             # テスト環境
│   ├── .env.production       # 本番環境（暗号化必須）
│   └── .env.docker           # Docker開発環境
│
├── frontend/
│   ├── .env.local            # ローカル開発環境
│   ├── .env.example          # フロントエンドテンプレート
│   ├── .env.test             # テスト環境
│   ├── .env.production       # 本番環境
│   └── .env.docker           # Docker開発環境
│
└── infrastructure/
    ├── .env.ci               # CI/CD環境
    └── .env.monitoring       # 監視環境
```

---

## 🔄 設定ファイル分離方針

### 1️⃣ ルート共通設定 (.env)

**対象**: すべてのサービスで共有される非機密設定

```bash
# ================================
# 共通環境設定
# ================================
# Application
ENVIRONMENT=development
LOG_LEVEL=DEBUG
TZ=Asia/Tokyo

# Docker
COMPOSE_PROJECT_NAME=autoforgenexus-mvp

# Redis共通
REDIS_HOST=redis
REDIS_PORT=6379

# 共通パフォーマンス設定
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10
CACHE_TTL=300
CACHE_MAX_SIZE=1000

# 監視
ENABLE_METRICS=true
METRICS_PORT=9090
```

---

## 🔧 バックエンド環境変数

### backend/.env.local（開発環境）

```bash
# ================================
# Backend Local Development
# ================================

# Application
DEBUG=true
API_PORT=8000
API_HOST=0.0.0.0

# Database (SQLite for development)
DATABASE_URL=sqlite:///./dev.db

# Redis (ローカル)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=redis_dev_password_change_me

# ================================
# Authentication (Clerk)
# ================================
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key_here
CLERK_JWT_ISSUER=https://your-app.clerk.accounts.dev

# ================================
# Security Keys
# ================================
# Generate: openssl rand -hex 32
SECRET_KEY=your_secret_key_here_32_characters_minimum
ENCRYPTION_KEY=your_encryption_key_base64_encoded

# JWT
JWT_SECRET=your_jwt_secret_here_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# ================================
# LLM API Keys
# ================================
# OpenAI
OPENAI_API_KEY=sk-your_openai_api_key_here
OPENAI_ORG_ID=org-your_org_id

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key_here

# Google AI
GOOGLE_AI_API_KEY=your_google_ai_key

# Cohere
COHERE_API_KEY=your_cohere_api_key

# ================================
# External Services
# ================================
# Email (開発用)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=dev@autoforgenexus.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=noreply@autoforgenexus.com

# Error Tracking
SENTRY_DSN=https://your_sentry_dsn_here
SENTRY_ENVIRONMENT=development

# ================================
# Development Tools
# ================================
ENABLE_API_DOCS=true
ENABLE_DEBUG_TOOLBAR=true
ENABLE_TRACING=true

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_PATH=./uploads

# ================================
# MCP Server Credentials (開発用)
# ================================
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx_REPLACE_ME
BRAVE_API_KEY=BSA_xxx_REPLACE_ME
```

### backend/.env.test（テスト環境）

```bash
# ================================
# Backend Test Environment
# ================================

# Application
DEBUG=false
API_PORT=8001
API_HOST=127.0.0.1

# Test Database (In-memory)
DATABASE_URL=sqlite:///:memory:

# Redis (Test)
REDIS_URL=redis://localhost:6379/1
REDIS_PASSWORD=redis_test

# Mock Authentication
CLERK_SECRET_KEY=sk_test_mock_key_for_testing
JWT_SECRET=test_jwt_secret_not_for_production

# Disable external services
ENABLE_API_DOCS=false
ENABLE_DEBUG_TOOLBAR=false
ENABLE_METRICS=false
SENTRY_DSN=

# Test API Keys (モック用)
OPENAI_API_KEY=sk-test-mock-key
ANTHROPIC_API_KEY=sk-ant-test-mock-key
```

### backend/.env.production（本番環境）

```bash
# ================================
# Backend Production Environment
# ================================
# ⚠️ このファイルは暗号化して管理すること

# Application
DEBUG=false
API_PORT=${PORT:-8000}
API_HOST=0.0.0.0
LOG_LEVEL=INFO

# Database (Turso)
TURSO_DATABASE_URL=${TURSO_DATABASE_URL}
TURSO_AUTH_TOKEN=${TURSO_AUTH_TOKEN}

# Redis (Production)
REDIS_URL=${REDIS_CLOUD_URL}
REDIS_PASSWORD=${REDIS_CLOUD_PASSWORD}
REDIS_TLS_ENABLED=true

# ================================
# Authentication (Clerk Production)
# ================================
CLERK_SECRET_KEY=${CLERK_SECRET_KEY}
CLERK_WEBHOOK_SECRET=${CLERK_WEBHOOK_SECRET}
CLERK_JWT_ISSUER=${CLERK_JWT_ISSUER}

# ================================
# Security (Vault/KMSから取得)
# ================================
SECRET_KEY=${SECRET_KEY}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=RS256
JWT_EXPIRE_MINUTES=60

# ================================
# LLM API Keys (Vault管理)
# ================================
OPENAI_API_KEY=${OPENAI_API_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY}

# ================================
# Production Services
# ================================
# Cloudflare
CLOUDFLARE_ACCOUNT_ID=${CLOUDFLARE_ACCOUNT_ID}
CLOUDFLARE_API_TOKEN=${CLOUDFLARE_API_TOKEN}

# Monitoring
SENTRY_DSN=${SENTRY_DSN}
SENTRY_ENVIRONMENT=production
LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}

# Email (Production)
SMTP_HOST=${SMTP_HOST}
SMTP_PORT=465
SMTP_USER=${SMTP_USER}
SMTP_PASSWORD=${SMTP_PASSWORD}
EMAIL_FROM=noreply@autoforgenexus.com

# ================================
# Performance & Security
# ================================
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_BURST=5
ENABLE_API_DOCS=false
ENABLE_DEBUG_TOOLBAR=false
ENABLE_METRICS=true
ENABLE_TRACING=true

# CORS
CORS_ORIGINS=${FRONTEND_URL}
```

---

## 🎨 フロントエンド環境変数

### frontend/.env.local（開発環境）

```bash
# ================================
# Frontend Local Development
# ================================

# Application
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_APP_NAME=AutoForgeNexus
NEXT_PUBLIC_APP_VERSION=1.0.0

# API Connection
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Authentication (Public Keys)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding

# Analytics (開発用)
NEXT_PUBLIC_POSTHOG_KEY=phc_development_key
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
NEXT_PUBLIC_GA_MEASUREMENT_ID=

# Features Flags
NEXT_PUBLIC_ENABLE_PWA=false
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_SENTRY=false
```

### frontend/.env.test（テスト環境）

```bash
# ================================
# Frontend Test Environment
# ================================

# Application
NEXT_PUBLIC_ENVIRONMENT=test
NEXT_PUBLIC_APP_NAME=AutoForgeNexus Test
NEXT_PUBLIC_APP_VERSION=test

# API Connection
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_WS_URL=ws://localhost:8001/ws

# Mock Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_mock_key

# Disable analytics
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_SENTRY=false
```

### frontend/.env.production（本番環境）

```bash
# ================================
# Frontend Production Environment
# ================================

# Application
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_APP_NAME=AutoForgeNexus
NEXT_PUBLIC_APP_VERSION=${APP_VERSION}
NEXT_PUBLIC_APP_URL=https://autoforgenexus.com

# API Connection
NEXT_PUBLIC_API_URL=${API_URL}
NEXT_PUBLIC_WS_URL=${WS_URL}

# Authentication (Clerk Public)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${CLERK_PUBLISHABLE_KEY}
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up

# Analytics & Monitoring
NEXT_PUBLIC_POSTHOG_KEY=${POSTHOG_KEY}
NEXT_PUBLIC_POSTHOG_HOST=${POSTHOG_HOST}
NEXT_PUBLIC_GA_MEASUREMENT_ID=${GA_MEASUREMENT_ID}
NEXT_PUBLIC_SENTRY_DSN=${SENTRY_DSN}

# Features
NEXT_PUBLIC_ENABLE_PWA=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_SENTRY=true

# Performance
NEXT_PUBLIC_IMAGE_DOMAINS=autoforgenexus.com,cdn.autoforgenexus.com
```

---

## 🐳 Docker環境変数

### backend/.env.docker

```bash
# ================================
# Backend Docker Development
# ================================

# Application
DEBUG=true
API_PORT=8000
API_HOST=0.0.0.0

# Database (PostgreSQL in Docker)
DATABASE_URL=postgresql://postgres:postgres@db:5432/autoforgenexus

# Redis (Docker)
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=redis_docker_password

# Network
BACKEND_NETWORK=autoforgenexus-network

# 他の設定は.env.localから継承
```

### frontend/.env.docker

```bash
# ================================
# Frontend Docker Development
# ================================

# API Connection (Docker Network)
NEXT_PUBLIC_API_URL=http://backend:8000
NEXT_PUBLIC_WS_URL=ws://backend:8000/ws

# 他の設定は.env.localから継承
```

---

## 🚀 CI/CD環境変数

### infrastructure/.env.ci

```bash
# ================================
# CI/CD Environment (GitHub Actions)
# ================================

# Test Configuration
NODE_ENV=test
CI=true

# Database (CI用)
DATABASE_URL=sqlite:///:memory:

# Redis (CI用)
REDIS_URL=redis://localhost:6379/15

# Mock Services
MOCK_EXTERNAL_APIS=true
SKIP_AUTH_CHECKS=true

# Coverage
COVERAGE_THRESHOLD=80

# Build
BUILD_ID=${GITHUB_RUN_ID}
COMMIT_SHA=${GITHUB_SHA}
```

---

## 📊 環境変数管理マトリックス

| 変数カテゴリ | ルート | Backend | Frontend | Docker | CI/CD |
|------------|--------|---------|----------|---------|-------|
| 共通設定 | ✅ | 継承 | 継承 | 継承 | - |
| データベース | - | ✅ | - | ✅ | ✅ |
| Redis | ✅ | ✅ | - | ✅ | ✅ |
| 認証（秘密） | - | ✅ | - | ✅ | - |
| 認証（公開） | - | - | ✅ | ✅ | - |
| API Keys | - | ✅ | - | ✅ | - |
| セキュリティ | - | ✅ | - | ✅ | - |
| 監視 | ✅ | ✅ | ✅ | - | ✅ |
| パフォーマンス | ✅ | カスタム | - | - | - |

---

## 🔐 セキュリティベストプラクティス

### 1. 機密情報の管理

```bash
# 絶対にコミットしないファイル
*.local
*.production
*.secret

# .gitignoreに追加
echo "*.env.local" >> .gitignore
echo "*.env.production" >> .gitignore
echo "backend/.env.local" >> .gitignore
echo "frontend/.env.local" >> .gitignore
```

### 2. 環境変数の暗号化

```bash
# 本番環境変数の暗号化
gpg --symmetric --cipher-algo AES256 backend/.env.production

# 復号化
gpg --decrypt backend/.env.production.gpg > backend/.env.production
```

### 3. シークレット管理サービスの利用

**推奨サービス**:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Google Secret Manager
- Doppler

### 4. ローテーション戦略

```yaml
# 定期的なキーローテーション
rotation_schedule:
  jwt_secret: 30_days
  api_keys: 90_days
  database_password: 60_days
  encryption_keys: 180_days
```

---

## 📝 移行手順

### Step 1: バックアップ作成

```bash
# 現在の.envをバックアップ
cp .env .env.backup.$(date +%Y%m%d)
```

### Step 2: ディレクトリ構造作成

```bash
# 必要なディレクトリを作成
mkdir -p backend frontend infrastructure
```

### Step 3: 環境変数ファイル作成

```bash
# 共通設定を作成
cat > .env << 'EOF'
# 共通設定の内容をコピー
EOF

# Backend設定を作成
cat > backend/.env.local << 'EOF'
# Backend設定の内容をコピー
EOF

# Frontend設定を作成
cat > frontend/.env.local << 'EOF'
# Frontend設定の内容をコピー
EOF
```

### Step 4: .gitignore更新

```bash
# .gitignoreに追加
cat >> .gitignore << 'EOF'
# Environment variables
*.env.local
*.env.production
*.env.*.local
.env.local
.env.production
backend/.env.local
backend/.env.production
frontend/.env.local
frontend/.env.production
EOF
```

### Step 5: Docker Compose更新

```yaml
# docker-compose.dev.yml
services:
  backend:
    env_file:
      - .env                    # 共通設定
      - backend/.env.docker     # Docker固有
      - backend/.env.local      # 開発環境（オーバーライド）

  frontend:
    env_file:
      - .env                    # 共通設定
      - frontend/.env.docker    # Docker固有
      - frontend/.env.local     # 開発環境（オーバーライド）
```

### Step 6: アプリケーション設定更新

**Backend (Python/FastAPI)**:
```python
# backend/src/core/config/settings.py
from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    environment: str = "development"
    debug: bool = False

    # Database
    database_url: str

    # Redis
    redis_url: str
    redis_password: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # 環境固有の設定を優先
        env_file_priority = [
            "../.env",  # 共通設定
            ".env.local",  # ローカル設定
            f".env.{os.getenv('ENVIRONMENT', 'development')}",  # 環境固有
        ]
```

**Frontend (Next.js)**:
```javascript
// frontend/next.config.js
module.exports = {
  env: {
    // 環境変数の読み込み優先順位を設定
    ...require('dotenv').config({ path: '../.env' }).parsed,
    ...require('dotenv').config({ path: '.env.local' }).parsed,
  }
}
```

---

## 🚨 緊急対応: 露出した認証情報の無効化

### 1. GitHub Personal Access Token

```bash
# GitHubで即座に無効化
# Settings > Developer settings > Personal access tokens
# トークンを削除し、新規作成

# リポジトリ履歴から削除
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

### 2. Cloudflare API Token

```bash
# Cloudflareダッシュボードで無効化
# My Profile > API Tokens
# トークンを削除し、新規作成
```

### 3. Discord Webhook

```bash
# Discord Server Settings > Integrations > Webhooks
# Webhookを削除し、新規作成
```

### 4. Brave Search API Key

```bash
# Brave Search APIダッシュボードで無効化
# 新しいAPIキーを生成
```

---

## 📚 参考資料

- [The Twelve-Factor App - Config](https://12factor.net/config)
- [OWASP - Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Next.js - Environment Variables](https://nextjs.org/docs/pages/building-your-application/configuring/environment-variables)
- [FastAPI - Settings and Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)

---

## ✅ チェックリスト

- [ ] 露出した認証情報をすべて無効化
- [ ] 新しい認証情報を生成
- [ ] 環境変数ファイルを適切に分離
- [ ] .gitignoreを更新
- [ ] Dockerファイルを更新
- [ ] CI/CD設定を更新
- [ ] チームメンバーに新しい設定方法を共有
- [ ] セキュリティ監査の実施
- [ ] リポジトリ履歴のクリーンアップ

---

**最終更新**: 2025年1月28日
**作成者**: AutoForgeNexus Development Team