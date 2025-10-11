# 外部サービスセットアップガイド

AutoForgeNexusで使用する外部サービス（Clerk認証、Tursoデータベース等）の詳細なセットアップ手順を説明します。

---

## 📑 目次

1. [Clerk認証サービスのセットアップ](#clerk認証サービスのセットアップ)
2. [Tursoデータベースのセットアップ](#tursoデータベースのセットアップ)
3. [環境変数の統合設定](#環境変数の統合設定)
4. [接続確認とトラブルシューティング](#接続確認とトラブルシューティング)

---

# 🔐 Clerk認証サービスのセットアップ

## 前提条件

- GitHubアカウント（Clerk認証に使用）
- メールアドレス

## ステップ1: Clerkアカウント作成

### 1-1. 公式サイトアクセス

```
https://clerk.com にアクセス
  ↓
「Sign up」をクリック
  ↓
GitHub連携でアカウント作成（推奨）
```

### 1-2. プロジェクト作成

```
Dashboard → 「Create application」
  ↓
Application name: AutoForgeNexus
  ↓
認証方法選択:
  ✓ Email + Password（推奨）
  ✓ Google OAuth（オプション）
  ✓ GitHub OAuth（オプション）
```

## ステップ2: API Keys取得

### 2-1. Developmentキー取得

```
Clerk Dashboard
  ↓
左サイドバー → 「API Keys」
  ↓
「Development」タブを選択
  ↓
以下をコピー:
```

**Publishable Key（公開鍵）**:

```
pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ クライアント側で使用可能（ブラウザで公開OK）

**Secret Key（秘密鍵）**:

```
sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ サーバー側のみで使用（絶対に公開しない）

### 2-2. Productionキー取得

```
Clerk Dashboard 上部
  ↓
「Development」→「Create production instance」
  ↓
Production Instance作成
  ↓
「API Keys」→「Production」タブ
  ↓
以下をコピー:
```

**Production Publishable Key**:

```
pk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Production Secret Key**:

```
sk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## ステップ3: ドメイン設定（Production環境）

### 3-1. カスタムドメイン設定

```
Production Instance → 左サイドバー「Domains」
  ↓
「Change domain」セクション
  ↓
カスタムドメイン入力: autoforgenexus.com
```

### 3-2. DNS設定（5つの必須レコード）

**Cloudflare DNSの場合**:

| タイプ | 名前        | 値                                  | Proxy       |
| ------ | ----------- | ----------------------------------- | ----------- |
| CNAME  | clerk       | clerk.shared.lcl.dev                | DNS only ⚠️ |
| CNAME  | accounts    | accounts-clerk.lcl.dev              | DNS only ⚠️ |
| CNAME  | \_domainkey | dkim1.\_domainkey.clerk.com         | DNS only    |
| TXT    | \_clerk     | clerk-verification=xxxxx            | -           |
| TXT    | @           | v=spf1 include:\_spf.clerk.com ~all | -           |

⚠️ **重要**: Cloudflareの場合、Proxy status（プロキシ）を必ず「DNS
only」（グレー雲マーク）に設定してください。

### 3-3. 証明書デプロイ

```
DNS伝播完了後（最大48時間）
  ↓
Clerk Dashboard ホーム
  ↓
「Deploy certificates」ボタンが表示される
  ↓
クリックしてSSL証明書自動発行
```

---

# 🗄️ Tursoデータベースのセットアップ

## 前提条件

- GitHubアカウント（Turso認証に使用）
- Turso CLI インストール

## ステップ1: Turso CLIインストール

### macOS (Homebrew)

```bash
# Turso CLI インストール
brew install tursodatabase/tap/turso

# インストール確認
turso --version

# 期待される出力: turso version v0.xx.x
```

### その他のOS

```bash
# curl経由でインストール
curl -sSfL https://get.tur.so/install.sh | bash

# パスを通す
export PATH="$HOME/.turso:$PATH"
echo 'export PATH="$HOME/.turso:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## ステップ2: Tursoアカウント認証

```bash
# GitHub経由でログイン（ブラウザが自動で開く）
turso auth login

# 認証成功確認
turso auth whoami

# 期待される出力:
# Logged in as: your-github-username
```

## ステップ3: ステージング環境データベース作成

### 3-1. データベース作成

```bash
# ステージング用データベース作成
turso db create autoforgenexus-staging

# 成功メッセージ例:
# Created database autoforgenexus-staging at group default in iad (Washington, D.C.)
```

**オプション: リージョン指定**

```bash
# 利用可能なロケーション確認
turso db locations

# 東京リージョン指定（低レイテンシー・推奨）
turso db create autoforgenexus-staging --location aws-ap-northeast-1

# 主要な利用可能なロケーション（2025年最新）:
# aws-ap-northeast-1  - Tokyo, Japan（推奨: 日本向け）
# aws-ap-southeast-1  - Singapore
# aws-ap-southeast-2  - Sydney, Australia
# aws-eu-central-1    - Frankfurt, Germany
# aws-eu-west-1       - Dublin, Ireland
# aws-us-east-1       - Virginia, USA
# aws-us-west-2       - Oregon, USA

# 現在のグループ情報確認
turso group show default
```

### 3-2. 接続情報取得

```bash
# データベースURL取得
turso db show autoforgenexus-staging --url

# 出力例:
# libsql://autoforgenexus-staging-your-org.turso.io
```

**このURLをコピーして保存してください！**

### 3-3. 認証トークン生成

```bash
# 認証トークン生成（有効期限なし）
turso db tokens create autoforgenexus-staging

# 出力例（このトークンは二度と表示されないので必ず保存！）:
# eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3MzMzMTIwMDAs...
```

⚠️
**重要**: このトークンをすぐにコピーして、1Passwordやセキュアなパスワードマネージャーに保存してください。二度と表示されません！

**セキュリティベストプラクティス: 有効期限付きトークン**

```bash
# 90日間有効なトークン生成（推奨）
turso db tokens create autoforgenexus-staging --expiration 90d

# 環境変数に直接設定
export TURSO_STAGING_AUTH_TOKEN=$(turso db tokens create autoforgenexus-staging)
```

### 3-4. データベース情報確認

```bash
# データベース詳細表示
turso db show autoforgenexus-staging

# 出力例:
# Name:           autoforgenexus-staging
# URL:            libsql://autoforgenexus-staging-your-org.turso.io
# ID:             xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
# Group:          default
# Version:        0.24.28
# Locations:      nrt (Tokyo)
# Size:           0 B
```

## ステップ4: 本番環境データベース作成

### 4-1. データベース作成

```bash
# 本番環境用データベース作成（東京リージョン推奨）
turso db create autoforgenexus-production --location aws-ap-northeast-1

# 成功メッセージ例:
# Created database autoforgenexus-production at group default in aws-ap-northeast-1 (Tokyo, Japan)
```

### 4-2. 接続情報取得

```bash
# データベースURL取得
turso db show autoforgenexus-production --url

# 出力例:
# libsql://autoforgenexus-production-your-org.turso.io
```

**このURLをコピーして保存してください！**

### 4-3. 認証トークン生成

```bash
# 本番環境用認証トークン生成（有効期限なし）
turso db tokens create autoforgenexus-production

# 出力されたトークンをすぐに保存！
```

⚠️ **本番環境の推奨設定**: 90日間有効なトークンを使用し、定期的にローテーション

```bash
# 90日間有効な本番トークン
turso db tokens create autoforgenexus-production --expiration 90d
```

### 4-4. データベース情報確認

```bash
# 本番環境データベース詳細表示
turso db show autoforgenexus-production

# 出力例:
# Name:           autoforgenexus-production
# URL:            libsql://autoforgenexus-production-your-org.turso.io
# ID:             xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
# Group:          default
# Version:        0.24.28
# Locations:      nrt (Tokyo)
# Size:           0 B
```

## ステップ5: データベース接続確認

### 5-1. Turso CLI経由で接続

```bash
# ステージング環境接続
turso db shell autoforgenexus-staging

# SQL実行テスト
sqlite> SELECT 'Staging DB Connected!' AS message;
# 期待される出力: Staging DB Connected!

# 終了
sqlite> .quit
```

```bash
# 本番環境接続
turso db shell autoforgenexus-production

sqlite> SELECT 'Production DB Connected!' AS message;
# 期待される出力: Production DB Connected!

sqlite> .quit
```

### 5-2. Python SDK経由で接続確認

#### 🐳 方法A: Docker環境で確認（推奨）

```bash
# プロジェクトルートに移動
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus

# Docker環境起動
docker compose -f docker-compose.dev.yml up -d

# バックエンドコンテナに入る
docker compose -f docker-compose.dev.yml exec backend bash

# 以下、コンテナ内で実行:

# 接続テストスクリプト作成
cat > test_turso_connection.py << 'EOF'
import os
import libsql_client

# 環境変数から接続情報取得
db_url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

print(f"Connecting to: {db_url}")

try:
    client = libsql_client.create_client_sync(
        url=db_url,
        auth_token=auth_token
    )
    result = client.execute("SELECT 'Connection OK' AS status")
    print(f"✅ Database Connection: {result.rows[0]['status']}")
    print(f"✅ Database URL: {db_url}")
except Exception as e:
    print(f"❌ Database Connection Error: {e}")
EOF

# ステージング環境で実行
export $(cat .env.staging | grep TURSO | xargs)
python test_turso_connection.py

# 期待される出力:
# Connecting to: libsql://autoforgenexus-staging-your-org.turso.io
# ✅ Database Connection: Connection OK
# ✅ Database URL: libsql://autoforgenexus-staging-your-org.turso.io

# 本番環境で実行
export $(cat .env.production | grep TURSO | xargs)
python test_turso_connection.py

# 期待される出力:
# Connecting to: libsql://autoforgenexus-production-your-org.turso.io
# ✅ Database Connection: Connection OK
# ✅ Database URL: libsql://autoforgenexus-production-your-org.turso.io

# コンテナから出る
exit

# Docker環境停止
docker compose -f docker-compose.dev.yml down
```

#### 💻 方法B: ローカル環境で確認（オプション）

```bash
# プロジェクトルートに移動
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/backend

# Python仮想環境作成（初回のみ）
python3.13 -m venv venv

# Python仮想環境アクティベート
source venv/bin/activate

# libsql-clientインストール
pip install libsql-client

# 接続テストスクリプト作成（上記と同じスクリプト）
cat > test_turso_connection.py << 'EOF'
import os
import libsql_client

db_url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

print(f"Connecting to: {db_url}")

try:
    client = libsql_client.create_client_sync(
        url=db_url,
        auth_token=auth_token
    )
    result = client.execute("SELECT 'Connection OK' AS status")
    print(f"✅ Database Connection: {result.rows[0]['status']}")
except Exception as e:
    print(f"❌ Database Connection Error: {e}")
EOF

# ステージング環境で実行
export $(cat .env.staging | grep TURSO | xargs)
python test_turso_connection.py

# 本番環境で実行
export $(cat .env.production | grep TURSO | xargs)
python test_turso_connection.py

# 仮想環境から出る
deactivate
```

#### 📊 開発環境の選択基準

| 用途               | 推奨環境    | 理由                       |
| ------------------ | ----------- | -------------------------- |
| **通常の開発作業** | 🐳 Docker   | 本番と同じ環境、チーム統一 |
| **クイックテスト** | 💻 ローカル | 起動が速い、軽量           |
| **デバッグ作業**   | 💻 ローカル | デバッガー使用が容易       |
| **CI/CD**          | 🐳 Docker   | 一貫性のある環境           |
| **本番環境**       | 🐳 Docker   | 完全な環境再現性           |

⚠️
**推奨**: 特別な理由がない限り**Docker環境**を使用してください。本番環境との一貫性が保たれます。

---

# 🔧 環境変数の統合設定

## バックエンド環境変数

### Development環境（backend/.env.local）

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/backend

cat > .env.local << 'EOF'
# ============================================
# Application Settings
# ============================================
APP_NAME=AutoForgeNexus-Backend-Dev
APP_ENV=local
DEBUG=true
LOG_LEVEL=DEBUG
PORT=8000
HOST=0.0.0.0

# ============================================
# Database Configuration (Turso/libSQL)
# ============================================
# 開発環境: ローカルSQLite使用（オプション）
DATABASE_URL=sqlite:///./data/local.db

# または Turso開発用DB使用
# DATABASE_URL=libsql://autoforgenexus-dev-[your-org].turso.io
# TURSO_DATABASE_URL=libsql://autoforgenexus-dev-[your-org].turso.io
# TURSO_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...

# ============================================
# Cache (Redis)
# ============================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_CACHE_TTL=3600

# ============================================
# Authentication (Clerk Backend)
# ============================================
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_PUBLIC_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# JWT Configuration
# ============================================
JWT_SECRET_KEY=dev-jwt-secret-key-min-32-chars-xxxxxxxxxxxxxxxx
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# Security Settings
# ============================================
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_CREDENTIALS=true
EOF

chmod 600 .env.local
echo "✅ backend/.env.local created"
```

### Staging環境（backend/.env.staging）

```bash
cat > .env.staging << 'EOF'
# ============================================
# Application Settings
# ============================================
APP_NAME=AutoForgeNexus-Backend-Staging
APP_ENV=staging
DEBUG=false
LOG_LEVEL=INFO
PORT=8000
HOST=0.0.0.0

# ============================================
# Database Configuration (Turso/libSQL Staging)
# ============================================
DATABASE_URL=libsql://autoforgenexus-staging-[your-org].turso.io
TURSO_DATABASE_URL=libsql://autoforgenexus-staging-[your-org].turso.io
TURSO_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...（ステージング用トークン）

# ============================================
# Cache (Redis) - Upstash Staging
# ============================================
REDIS_HOST=your-staging-redis.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=staging_redis_password_xxxxxxxxxx
REDIS_DB=0

# ============================================
# Authentication (Clerk Staging)
# ============================================
CLERK_SECRET_KEY=sk_test_STAGING_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_PUBLIC_KEY=pk_test_STAGING_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# JWT Configuration
# ============================================
JWT_SECRET_KEY=staging-jwt-secret-key-min-32-chars-xxxxxxxxxxxxxxxx
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# Security Settings
# ============================================
CORS_ORIGINS=https://staging.autoforgenexus.com,https://staging-api.autoforgenexus.com
CORS_CREDENTIALS=true
EOF

chmod 600 .env.staging
echo "✅ backend/.env.staging created"
```

### Production環境（backend/.env.production）

```bash
cat > .env.production << 'EOF'
# ============================================
# Application Settings
# ============================================
APP_NAME=AutoForgeNexus-Backend-Production
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
PORT=8000
HOST=0.0.0.0

# ============================================
# Database Configuration (Turso/libSQL Production)
# ============================================
DATABASE_URL=libsql://autoforgenexus-production-[your-org].turso.io
TURSO_DATABASE_URL=libsql://autoforgenexus-production-[your-org].turso.io
TURSO_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...（本番用トークン）

# ============================================
# Cache (Redis) - Upstash Production
# ============================================
REDIS_HOST=your-production-redis.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=production_redis_password_STRONG_xxxxxxxxxxxxxxxx
REDIS_DB=0

# ============================================
# Authentication (Clerk Production)
# ============================================
CLERK_SECRET_KEY=sk_live_PRODUCTION_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_PUBLIC_KEY=pk_live_PRODUCTION_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# JWT Configuration (Production)
# ============================================
JWT_SECRET_KEY=production-jwt-secret-STRONG-64-chars-min-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15

# ============================================
# Security Settings (Production Hardened)
# ============================================
CORS_ORIGINS=https://autoforgenexus.com,https://api.autoforgenexus.com
CORS_CREDENTIALS=true
EOF

chmod 600 .env.production
echo "✅ backend/.env.production created"
```

## フロントエンド環境変数

### Development環境（frontend/.env.local）

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/frontend

cat > .env.local << 'EOF'
# ============================================
# Clerk Authentication (Development)
# ============================================
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# Clerk Redirect URLs
# ============================================
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# ============================================
# Environment
# ============================================
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# ============================================
# Database (Optional: Direct Frontend Access)
# ============================================
# DATABASE_URL=sqlite:///./data/local.db
EOF

chmod 600 .env.local
echo "✅ frontend/.env.local created"
```

### Staging環境（frontend/.env.staging）

```bash
cat > .env.staging << 'EOF'
# ============================================
# Clerk Authentication (Staging)
# ============================================
CLERK_SECRET_KEY=sk_test_STAGING_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_STAGING_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# Clerk Redirect URLs (Staging)
# ============================================
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding

# ============================================
# Environment
# ============================================
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://staging.autoforgenexus.com
NEXT_PUBLIC_API_URL=https://staging-api.autoforgenexus.com

# ============================================
# Database & Backend (Staging)
# ============================================
DATABASE_URL=libsql://autoforgenexus-staging-[your-org].turso.io
TURSO_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...（ステージング用トークン）
EOF

chmod 600 .env.staging
echo "✅ frontend/.env.staging created"
```

### Production環境（frontend/.env.production）

```bash
cat > .env.production << 'EOF'
# ============================================
# Clerk Authentication (Production)
# ============================================
CLERK_SECRET_KEY=sk_live_PRODUCTION_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_PRODUCTION_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# Clerk Redirect URLs (Production)
# ============================================
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding

# ============================================
# Environment
# ============================================
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://autoforgenexus.com
NEXT_PUBLIC_API_URL=https://api.autoforgenexus.com

# ============================================
# Database & Backend (Production)
# ============================================
DATABASE_URL=libsql://autoforgenexus-production-[your-org].turso.io
TURSO_AUTH_TOKEN=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...（本番用トークン）
EOF

chmod 600 .env.production
echo "✅ frontend/.env.production created"
```

---

# ✅ 接続確認とトラブルシューティング

## 統合接続確認

### 1. Clerk認証確認

```bash
# フロントエンド起動
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/frontend
pnpm dev

# ブラウザで確認
open http://localhost:3000

# 期待される動作:
# 1. Clerkログイン画面が表示される
# 2. サインアップ/サインインが正常に動作
# 3. ダッシュボードにリダイレクトされる
```

### 2. Tursoデータベース確認

```bash
# バックエンド起動
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/backend
source venv/bin/activate
uvicorn src.main:app --reload

# ヘルスチェック確認
curl http://localhost:8000/health

# 期待される出力:
# {
#   "status": "healthy",
#   "database": "connected",
#   "turso": "OK",
#   "timestamp": "2025-09-30T12:00:00Z"
# }
```

### 3. データベースマイグレーション実行

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/backend
source venv/bin/activate

# ステージング環境にマイグレーション適用
export $(cat .env.staging | grep -E 'TURSO|DATABASE' | xargs)
alembic upgrade head

# 期待される出力:
# INFO  [alembic.runtime.migration] Running upgrade -> xxxxx, Initial migration
# ✅ Staging database migrated successfully

# 本番環境にマイグレーション適用
export $(cat .env.production | grep -E 'TURSO|DATABASE' | xargs)
alembic upgrade head

# ✅ Production database migrated successfully
```

## トラブルシューティング

### エラー: Clerk authentication failed

**原因**: API Keyが正しく設定されていない

**解決策**:

```bash
# 1. Clerk Dashboardで正しいキーを確認
# 2. 環境変数ファイルを再確認
cat backend/.env.local | grep CLERK
cat frontend/.env.local | grep CLERK

# 3. キーを正しく設定して再起動
```

### エラー: Turso connection refused

**原因**: 認証トークンが無効または期限切れ

**解決策**:

```bash
# 新しいトークンを生成
turso db tokens create autoforgenexus-staging

# 環境変数ファイルを更新
nano backend/.env.staging
# TURSO_AUTH_TOKEN=新しいトークン

# アプリケーション再起動
```

### エラー: DNS validation failed (Clerk)

**原因**: DNSレコードが正しく設定されていない

**解決策**:

```bash
# DNS伝播確認
dig clerk.autoforgenexus.com CNAME +short
# 期待される出力: clerk.shared.lcl.dev

# Cloudflareの場合、Proxyをオフにする
# Dashboard → DNS → Proxyステータス: DNS only（グレー雲マーク）
```

---

## 📊 セットアップ完了チェックリスト

### Clerk認証

- [ ] Clerkアカウント作成完了
- [ ] Development API Keys取得完了
- [ ] Production API Keys取得完了
- [ ] ドメイン設定完了（Production）
- [ ] DNS設定完了（5つのレコード）
- [ ] SSL証明書デプロイ完了
- [ ] ローカル認証動作確認完了

### Tursoデータベース

- [ ] Turso CLI インストール完了
- [ ] Turso認証完了
- [ ] ステージングDB作成完了
- [ ] ステージングトークン生成・保存完了
- [ ] 本番DB作成完了
- [ ] 本番トークン生成・保存完了
- [ ] CLI接続確認完了
- [ ] Python SDK接続確認完了

### 環境変数設定

- [ ] backend/.env.local 作成完了
- [ ] backend/.env.staging 作成完了
- [ ] backend/.env.production 作成完了
- [ ] frontend/.env.local 作成完了
- [ ] frontend/.env.staging 作成完了
- [ ] frontend/.env.production 作成完了
- [ ] すべてのファイル権限600設定完了

### 統合確認

- [ ] Clerk認証フロー動作確認完了
- [ ] Tursoデータベース接続確認完了
- [ ] データベースマイグレーション完了
- [ ] ヘルスチェックエンドポイント正常応答

---

## 🔐 セキュリティベストプラクティス

### 1. API Key管理

```bash
# ❌ 絶対にやってはいけないこと
git add .env.local
git add .env.staging
git add .env.production
git commit -m "add env files"  # 絶対NG！

# ✅ 正しい管理方法
echo ".env.*" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.staging" >> .gitignore
echo ".env.production" >> .gitignore

# Git履歴から削除（もしコミットしてしまった場合）
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env.*" \
  --prune-empty --tag-name-filter cat -- --all
```

### 2. トークンローテーション

```bash
# 90日ごとにトークンを更新（推奨）
turso db tokens create autoforgenexus-production --expiration 90d

# 古いトークンを無効化
turso db tokens list autoforgenexus-production
turso db tokens revoke autoforgenexus-production <TOKEN_NAME>
```

### 3. 秘密情報の安全な保存

- **1Password**: チーム全体で秘密情報を共有
- **GitHub Secrets**: CI/CD用の環境変数
- **Cloudflare環境変数**: デプロイ先の環境変数

---

## 🚀 次のステップ

1. **Next.js統合コード実装**

   - `middleware.ts` - ルート保護
   - `layout.tsx` - ClerkProviderラップ
   - サインイン/サインアップページ作成

2. **データベーススキーマ設計**

   - Alembicマイグレーションファイル作成
   - モデル定義（SQLAlchemy）

3. **GitHub Secretsに登録**（CI/CD用）

   ```bash
   gh secret set CLERK_SECRET_KEY_PRODUCTION
   gh secret set TURSO_AUTH_TOKEN_PRODUCTION
   ```

4. **Cloudflare環境変数設定**（デプロイ用）
   ```bash
   wrangler secret put CLERK_SECRET_KEY
   wrangler secret put TURSO_AUTH_TOKEN
   ```

---

## 📚 参考資料

- [Clerk公式ドキュメント](https://clerk.com/docs)
- [Turso公式ドキュメント](https://docs.turso.tech)
- [libSQL Python SDK](https://github.com/tursodatabase/libsql-client-py)
- [Alembic公式ドキュメント](https://alembic.sqlalchemy.org)

---

**最終更新日**: 2025年9月30日 **作成者**: AutoForgeNexus開発チーム
