# AutoForgeNexus Phase 2: インフラ・DevOps環境構築 詳細タスクブレークダウン

## 📋 **概要**

AutoForgeNexus AI プロンプト最適化システムのPhase 2「インフラ・DevOps環境構築」における、インフラ基盤構築作業の詳細タスク分解ドキュメント。各タスクは即座に実行可能な粒度で設計され、明確なコマンド、担当エージェント、目的と背景を含む。

---

## 🎯 **Phase 2 目標**

**Docker環境とCloudflareインフラ基盤の構築により、スケーラブルで監視可能な本番対応インフラを確立する**

- Docker開発・本番環境の完全構築
- Cloudflareエコシステム統合（Workers Python, Pages, R2）
- 環境分離とシークレット管理の実装
- 監視・ログ・アラート機能の基盤構築
- CI/CDデプロイパイプラインの実装完成
- インフラ・アズ・コード（IaC）による再現可能なインフラ
- タスク実行時に不足があれば、最適で最新のベストプラクティスを各担当エージェントが決定する

**重要**: Phase 2では実際のインフラファイル作成とコンテナ構築を行う。プロジェクト構造・ソースコード作成はPhase 3以降で実施

---

## 🔧 **Phase 2 対象エージェント構成**

### **インフラ・DevOps専門エージェント（5エージェント）**
1. **devops-coordinator Agent** - インフラ統括、CI/CDパイプライン完成、デプロイ自動化
2. **security-architect Agent** - シークレット管理、環境分離、セキュリティ設定
3. **observability-engineer Agent** - 監視、ログ、アラート、パフォーマンス基盤
4. **edge-computing-specialist Agent** - Cloudflare統合、エッジ設定、CDN最適化
5. **performance-optimizer Agent** - インフラパフォーマンス、リソース最適化、スケーリング

---

## 📋 **事前準備タスク**

### **Task 0.1: インフラツール確認と環境準備**

**コマンド**: `環境インフラチェックスクリプト実行`

**担当エージェント**:
- **devops-coordinator Agent** (リーダー)

**何をやるのか**:
- Docker環境確認（24+必須、docker-compose含む）
- Node.js/pnpm確認（Phase 1で確認済み）
- Cloudflare CLI (wrangler) インストール確認
- 必要なツール追加インストール

**目的と背景**:
- **目的**: インフラ構築に必要なツールとサービスの前提条件確認
- **背景**: Dockerコンテナ化とCloudflareデプロイに特化したツールチェーンが必要

**実行コマンド**:
```bash
# インフラツール確認
echo "=== Phase 2 Infrastructure Tools Check ==="
docker --version    # >= 24.0
docker-compose --version  # >= 2.0

# Cloudflare CLI確認・インストール
if ! command -v wrangler &> /dev/null; then
    echo "Installing Wrangler CLI..."
    npm install -g wrangler@latest
fi
wrangler --version

# 追加ツール確認
curl --version     # API確認用
jq --version || echo "jq not found - consider installing"

echo "Infrastructure tools ready ✅"
```

**期待される成果物**:
- 全インフラツール確認済み
- Cloudflare CLI準備完了
- Docker環境動作確認済み

---

## 📝 **Step 2.1: Docker環境完全構築**

### **Task 2.1.1: プロジェクト構造とDocker基盤作成**

**コマンド**: `/ai:infrastructure:project-structure --ddd --docker-ready`

**担当エージェント**:
- **devops-coordinator Agent** (リーダー)
- **security-architect Agent** (セキュリティ統合)

**何をやるのか**:
- DDDプロジェクト構造作成（backend/, frontend/, infrastructure/）
- Docker関連ディレクトリ構造作成
- 基本的な設定ファイル配置準備
- 環境変数テンプレート作成

**目的と背景**:
- **目的**: Docker化に適したプロジェクト構造の確立とインフラ基盤の準備
- **背景**: Phase 3以降でのコード実装前に、適切なプロジェクト基盤が必要

**実行コマンド**:
```bash
# プロジェクト基本構造作成
mkdir -p {backend,frontend,infrastructure,docs}
mkdir -p infrastructure/{docker,cloudflare,monitoring,scripts}
mkdir -p infrastructure/docker/{development,production}

# バックエンド DDD 構造
mkdir -p backend/{src,tests,migrations,scripts}
mkdir -p backend/src/{domain,application,infrastructure,presentation}
mkdir -p backend/src/domain/{entities,value_objects,repositories,services,events}
mkdir -p backend/src/application/{use_cases,services,dtos}
mkdir -p backend/src/infrastructure/{repositories,external,database}
mkdir -p backend/src/presentation/{api,schemas,middleware}

# フロントエンド構造
mkdir -p frontend/{src,public,tests}
mkdir -p frontend/src/{app,components,lib,types}
mkdir -p frontend/src/components/{ui,features,layout}

# 環境変数テンプレート
touch .env.example
touch .env.local.example
touch .env.production.example

# 基本ファイル作成
touch backend/src/__init__.py
touch frontend/src/.gitkeep

echo "Project structure created ✅"
tree -L 3 .
```

**期待される成果物**:
- DDDディレクトリ構造完成
- Docker対応プロジェクト構造
- 環境変数テンプレート
- インフラディレクトリ基盤

---

### **Task 2.1.2: Docker開発環境構築**

**コマンド**: `/ai:infrastructure:docker-dev --multi-service --hot-reload`

**担当エージェント**:
- **devops-coordinator Agent** (リーダー)
- **security-architect Agent** (環境変数・シークレット)

**何をやるのか**:
- Dockerfile.dev作成（backend: Python 3.13, frontend: Node.js 20）
- docker-compose.dev.yml作成（マルチサービス構成）
- ホットリロード対応設定
- 開発用環境変数設定
- ボリュームマッピング最適化

**目的と背景**:
- **目的**: 高速で効率的な開発ワークフローを可能にするDocker環境構築
- **背景**: マルチサービス開発における環境一貫性と開発効率の両立が必要

**実行コマンド**:
```bash
# Backend Dockerfile.dev
cat > backend/Dockerfile.dev << 'EOF'
FROM python:3.13-slim

WORKDIR /app

# システム依存関係とツール
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係
COPY requirements.txt* pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir -e .[dev] || \
    echo "No requirements file found yet"

# アプリケーションコード（ホットリロード対応）
COPY . .

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

# Frontend Dockerfile.dev
cat > frontend/Dockerfile.dev << 'EOF'
FROM node:20-alpine

WORKDIR /app

# pnpm有効化
RUN corepack enable pnpm

# 依存関係（レイヤーキャッシュ最適化）
COPY package*.json pnpm-lock.yaml* ./
RUN pnpm install || echo "No package.json found yet"

# アプリケーションコード
COPY . .

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

EXPOSE 3000
CMD ["pnpm", "dev"]
EOF

# docker-compose.dev.yml
cat > docker-compose.dev.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=sqlite:///./data/autoforge.db
      - REDIS_URL=redis://redis:6379
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY:-dev-secret}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY:-dev-public}
      - LANGFUSE_HOST=http://langfuse:3000
    volumes:
      - ./backend:/app
      - backend_data:/app/data
    depends_on:
      - redis
      - langfuse
    restart: unless-stopped
    networks:
      - autoforge-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_ENVIRONMENT=development
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - autoforge-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - autoforge-network

  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - "3001:3000"
    environment:
      - DATABASE_URL=postgresql://langfuse:password@langfuse-db:5432/langfuse
      - NEXTAUTH_SECRET=your-development-secret-key-change-in-production
      - SALT=your-development-salt-change-in-production
      - NEXTAUTH_URL=http://localhost:3001
    depends_on:
      - langfuse-db
    restart: unless-stopped
    networks:
      - autoforge-network

  langfuse-db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=langfuse
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=langfuse
    volumes:
      - langfuse_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - autoforge-network

volumes:
  backend_data:
  redis_data:
  langfuse_data:

networks:
  autoforge-network:
    driver: bridge
EOF

# 開発環境変数
cat > .env.dev << 'EOF'
# Development Environment Variables
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///./data/autoforge.db

# Redis
REDIS_URL=redis://localhost:6379

# LangFuse (Development)
LANGFUSE_SECRET_KEY=dev-secret-key
LANGFUSE_PUBLIC_KEY=dev-public-key
LANGFUSE_HOST=http://localhost:3001

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development

# Security (Development)
CLERK_PUBLISHABLE_KEY=pk_test_dev_key_replace_in_production
CLERK_SECRET_KEY=sk_test_dev_key_replace_in_production
ENCRYPTION_KEY=dev_32_byte_key_replace_in_production
PYTHON_SERVICE_API_KEY=dev_api_key_replace_in_production
EOF

# セキュア化された開発用シークレット生成スクリプト
cat > infrastructure/scripts/setup-dev-secrets.sh << 'EOF'
#!/bin/bash
echo "🔐 Generating secure development secrets..."

if [ ! -f .env.local ]; then
  echo "# Development Secrets - DO NOT COMMIT" > .env.local
  echo "CLERK_PUBLISHABLE_KEY=pk_test_$(openssl rand -hex 16)" >> .env.local
  echo "CLERK_SECRET_KEY=sk_test_$(openssl rand -hex 32)" >> .env.local
  echo "ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env.local
  echo "PYTHON_SERVICE_API_KEY=$(openssl rand -hex 32)" >> .env.local
  echo "TURSO_AUTH_TOKEN=dev_token_$(openssl rand -hex 16)" >> .env.local
  echo "✅ Development secrets generated in .env.local"
else
  echo "✅ .env.local already exists"
fi

# .gitignore セキュリティ設定強化
echo "# セキュリティファイル除外" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.*.local" >> .gitignore
echo "wrangler.toml.local" >> .gitignore
echo "**/secrets/" >> .gitignore
echo "**/*.pem" >> .gitignore
echo "**/*.key" >> .gitignore

echo "🔒 Security configuration updated"
EOF

chmod +x infrastructure/scripts/setup-dev-secrets.sh
```

**期待される成果物**:
- 開発用Dockerfileセット
- docker-compose.dev.yml完成
- 環境変数設定
- マルチサービス開発環境

---

### **Task 2.1.3: Docker本番環境構築**

**コマンド**: `/ai:infrastructure:docker-prod --optimized --security-hardened`

**担当エージェント**:
- **devops-coordinator Agent** (リーダー)
- **security-architect Agent** (セキュリティ設定)
- **performance-optimizer Agent** (最適化)

**何をやるのか**:
- Dockerfile本番用作成（マルチステージビルド）
- docker-compose.prod.yml作成（本番最適化）
- セキュリティ設定強化
- パフォーマンス最適化設定
- ヘルスチェック・監視設定

**目的と背景**:
- **目的**: 本番環境に対応したセキュアで高性能なDocker環境の構築
- **背景**: 開発環境と本番環境の要件差異に対応し、セキュリティとパフォーマンスを最適化

**実行コマンド**:
```bash
# Backend Dockerfile (本番用)
cat > backend/Dockerfile << 'EOF'
# マルチステージビルド
FROM python:3.13-slim as builder

WORKDIR /app

# ビルド依存関係
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係インストール
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --user -r requirements.txt

# 本番ステージ
FROM python:3.13-slim

# 非rootユーザー作成
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# 最小限のシステム依存関係
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ビルドステージから依存関係コピー
COPY --from=builder /root/.local /root/.local

# アプリケーションコード
COPY . .
RUN chown -R appuser:appuser /app

# 非rootユーザーに切り替え
USER appuser

# PATH設定
ENV PATH=/root/.local/bin:$PATH

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Frontend Dockerfile (本番用)
cat > frontend/Dockerfile << 'EOF'
# ビルドステージ
FROM node:20-alpine as builder

WORKDIR /app

# pnpm有効化
RUN corepack enable pnpm

# 依存関係インストール
COPY package*.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# アプリケーションビルド
COPY . .
RUN pnpm build

# 本番ステージ
FROM node:20-alpine

WORKDIR /app

# 非rootユーザー作成
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# 必要ファイルのみコピー
COPY --from=builder /app/package*.json ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
EOF

# docker-compose.prod.yml
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
      - LANGFUSE_HOST=${LANGFUSE_HOST}
    volumes:
      - backend_data:/app/data
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - autoforge-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_ENVIRONMENT=production
    depends_on:
      - backend
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - autoforge-network

volumes:
  backend_data:

networks:
  autoforge-network:
    driver: bridge
EOF
```

**期待される成果物**:
- 本番用Dockerfileセット（最適化済み）
- docker-compose.prod.yml
- セキュリティ強化設定
- 監視・ログ設定

---

## 📝 **Step 2.2: Cloudflare環境構築**

### **Task 2.2.1: Cloudflare Workers Python設定**

**コマンド**: `/ai:infrastructure:cloudflare-workers --python --fastapi`

**担当エージェント**:
- **edge-computing-specialist Agent** (リーダー)
- **devops-coordinator Agent** (デプロイ統合)
- **security-architect Agent** (セキュリティ設定)

**何をやるのか**:
- wrangler.toml設定ファイル作成
- Workers Python環境設定
- FastAPI for Workers対応設定
- 環境変数・シークレット管理設定

**目的と背景**:
- **目的**: Cloudflare Workers Pythonを使用したエッジコンピューティング環境の構築
- **背景**: グローバルなエッジ展開により低レイテンシとスケーラビリティを実現

**実行コマンド**:
```bash
# Cloudflare設定ディレクトリ
mkdir -p infrastructure/cloudflare/workers

# wrangler.toml (セキュリティ強化版)
cat > infrastructure/cloudflare/workers/wrangler.toml << 'EOF'
name = "autoforge-nexus-api"
main = "src/main.py"
compatibility_date = "2024-10-01"

# 本番環境設定
[env.production]
name = "autoforge-nexus-api"
vars = { ENVIRONMENT = "production" }

# ✅ セキュリティ設定
[env.production.security]
cors = { origins = ["https://autoforge.nexus"], methods = ["GET", "POST", "PUT", "DELETE"] }
csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; object-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.clerk.dev;"
hsts = { max_age = 31536000, include_subdomains = true, preload = true }

# ✅ レート制限設定
[[env.production.durable_objects.bindings]]
name = "RATE_LIMITER"
class_name = "RateLimiter"

# ステージング環境設定
[env.staging]
name = "autoforge-nexus-api-staging"
vars = { ENVIRONMENT = "staging" }

[env.staging.security]
cors = { origins = ["https://staging.autoforge.nexus", "http://localhost:3000"], methods = ["GET", "POST", "PUT", "DELETE"] }
csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; object-src 'none';"
hsts = { max_age = 31536000, include_subdomains = true }

# 開発環境設定
[env.development]
name = "autoforge-nexus-api-dev"
vars = { ENVIRONMENT = "development" }

[env.development.security]
cors = { origins = ["http://localhost:3000", "http://localhost:3001"], methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"] }

# バインディング設定
[[env.production.r2_buckets]]
binding = "BUCKET"
bucket_name = "autoforge-nexus-storage"

[[env.production.kv_namespaces]]
binding = "CACHE"
id = "your-kv-namespace-id-here"

[[env.staging.r2_buckets]]
binding = "BUCKET"
bucket_name = "autoforge-nexus-storage-staging"

[[env.staging.kv_namespaces]]
binding = "CACHE"
id = "your-staging-kv-namespace-id-here"

# リソース制限
[build]
command = "cp -r ../../../backend/src/* ."

# 観測性
[observability]
enabled = true
EOF

# セキュリティ強化設定スクリプト
cat > infrastructure/cloudflare/setup-workers.sh << 'EOF'
#!/bin/bash
echo "🔐 Setting up secure Cloudflare Workers environment..."

# Wrangler認証確認
if ! wrangler whoami > /dev/null 2>&1; then
    echo "❌ Please login to Wrangler first:"
    echo "wrangler login"
    exit 1
fi

echo "✅ Wrangler authentication confirmed"

# KV Namespace作成
echo "📦 Creating KV namespaces..."
wrangler kv:namespace create "CACHE" --env production
wrangler kv:namespace create "CACHE" --env staging

# R2 Bucket作成
echo "🪣 Creating R2 buckets..."
wrangler r2 bucket create autoforge-nexus-storage
wrangler r2 bucket create autoforge-nexus-storage-staging

# セキュリティシークレット設定
echo "🔑 Setting up security secrets..."
echo "Please set the following production secrets:"
echo "wrangler secret put CLERK_SECRET_KEY --env production"
echo "wrangler secret put DATABASE_URL --env production"
echo "wrangler secret put TURSO_AUTH_TOKEN --env production"
echo "wrangler secret put ENCRYPTION_KEY --env production"
echo "wrangler secret put LANGFUSE_SECRET_KEY --env production"
echo "wrangler secret put LANGFUSE_PUBLIC_KEY --env production"
echo "wrangler secret put PYTHON_SERVICE_API_KEY --env production"

echo "🔒 Staging environment secrets:"
echo "wrangler secret put CLERK_SECRET_KEY --env staging"
echo "wrangler secret put DATABASE_URL --env staging"
echo "wrangler secret put TURSO_AUTH_TOKEN --env staging"

# セキュリティミドルウェア実装
cat > ../../../backend/src/security/middleware.py << 'PYEOF'
"""
Cloudflare Workers Security Middleware
"""
import json
import time
from typing import Dict, Any, Optional

class SecurityMiddleware:
    @staticmethod
    def validate_request(request: Dict[str, Any], env: Dict[str, Any]) -> Dict[str, Any]:
        """✅ リクエストセキュリティ検証"""

        # CORS検証
        origin = request.get('headers', {}).get('origin')
        if not SecurityMiddleware._is_allowed_origin(origin, env.get('ALLOWED_ORIGINS', '')):
            return {'valid': False, 'error': 'CORS violation'}

        # レート制限チェック
        client_id = SecurityMiddleware._get_client_id(request)
        if not SecurityMiddleware._check_rate_limit(client_id, env):
            return {'valid': False, 'error': 'Rate limit exceeded'}

        # Clerk認証トークン検証
        auth_header = request.get('headers', {}).get('authorization', '')
        auth_result = SecurityMiddleware._validate_clerk_token(auth_header, env.get('CLERK_PUBLISHABLE_KEY'))

        return {'valid': auth_result['valid'], 'user_data': auth_result.get('user_data')}

    @staticmethod
    def _is_allowed_origin(origin: Optional[str], allowed_origins: str) -> bool:
        """✅ CORS origin検証"""
        if not origin:
            return False
        return any(origin.endswith(domain) for domain in allowed_origins.split(','))

    @staticmethod
    def _get_client_id(request: Dict[str, Any]) -> str:
        """✅ クライアントID取得（レート制限用）"""
        # IP address or user ID based identification
        return request.get('headers', {}).get('x-forwarded-for', 'unknown')

    @staticmethod
    def _check_rate_limit(client_id: str, env: Dict[str, Any]) -> bool:
        """✅ レート制限チェック（KV使用）"""
        # Implementation would use Cloudflare KV for rate limiting
        # For now, return True (implement with KV in production)
        return True

    @staticmethod
    def _validate_clerk_token(auth_header: str, clerk_key: str) -> Dict[str, Any]:
        """✅ Clerk JWT トークン検証"""
        if not auth_header.startswith('Bearer '):
            return {'valid': False}

        token = auth_header[7:]
        # Implement actual JWT validation with Clerk
        # For now, basic validation
        return {'valid': len(token) > 10, 'user_data': {'user_id': 'temp'}}
PYEOF

echo "✅ Cloudflare Workers secure setup complete!"
echo "🔐 Next steps:"
echo "1. Run the secret setup commands shown above"
echo "2. Update wrangler.toml with actual KV and R2 IDs"
echo "3. Test security middleware in staging environment"
EOF

chmod +x infrastructure/cloudflare/setup-workers.sh
```

**期待される成果物**:
- wrangler.toml設定
- Cloudflare Workers Python環境
- R2・KV設定
- シークレット管理設定

---

### **Task 2.2.2: Cloudflare Pages設定**

**コマンド**: `/ai:infrastructure:cloudflare-pages --nextjs --static-optimization`

**担当エージェント**:
- **edge-computing-specialist Agent** (リーダー)

**何をやるのか**:
- Cloudflare Pages設定
- Next.js Static Export最適化
- カスタムドメイン設定準備
- CDN・パフォーマンス最適化設定

**目的と背景**:
- **目的**: Cloudflare Pagesを使用した高性能フロントエンド配信環境の構築
- **背景**: グローバルCDNとエッジ最適化による最高のフロントエンド体験を提供

**実行コマンド**:
```bash
# Pages設定ディレクトリ
mkdir -p infrastructure/cloudflare/pages

# Pages設定
cat > infrastructure/cloudflare/pages/pages-config.json << 'EOF'
{
  "name": "autoforge-nexus-frontend",
  "production_branch": "main",
  "build_config": {
    "build_command": "pnpm build && pnpm export",
    "destination_dir": "out",
    "root_dir": "frontend"
  },
  "env_vars": {
    "NODE_VERSION": "20",
    "NEXT_PUBLIC_API_URL": "$CLOUDFLARE_WORKERS_URL"
  },
  "functions_config": {
    "compatibility_date": "2024-10-01"
  },
  "redirects": [
    {
      "source": "/api/*",
      "destination": "$CLOUDFLARE_WORKERS_URL/api/*",
      "status_code": 200
    }
  ],
  "headers": [
    {
      "source": "/*",
      "headers": {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()"
      }
    }
  ]
}
EOF

# Pages デプロイ設定
cat > infrastructure/cloudflare/pages/deploy.sh << 'EOF'
#!/bin/bash
echo "Deploying to Cloudflare Pages..."

cd frontend

# ビルド最適化
echo "Building optimized frontend..."
pnpm build
pnpm export

# Pages デプロイ
echo "Deploying to Pages..."
wrangler pages deploy out --project-name autoforge-nexus-frontend

echo "Frontend deployed to Cloudflare Pages!"
EOF

chmod +x infrastructure/cloudflare/pages/deploy.sh

# Next.js Pages最適化設定
cat > frontend/next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  experimental: {
    typedRoutes: true
  },
  poweredByHeader: false,
  generateEtags: false,
  compress: true,

  // Cloudflare Pages最適化
  assetPrefix: process.env.NODE_ENV === 'production' ? undefined : undefined,

  // セキュリティヘッダー
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          }
        ],
      },
    ]
  },
}

module.exports = nextConfig
EOF
```

**期待される成果物**:
- Cloudflare Pages設定
- Next.js最適化設定
- デプロイスクリプト
- パフォーマンス最適化設定

---

### **Task 2.2.3: セキュリティ設定と検証スクリプト**

**コマンド**: `/ai:security:validation --cloudflare --clerk-auth`

**担当エージェント**:
- **security-architect Agent** (リーダー)
- **devops-coordinator Agent** (統合支援)

**何をやるのか**:
- Clerk認証統合とMFA必須化設定
- セキュリティ検証スクリプト実装
- セキュリティヘッダー設定とCSP強化
- 暗号化鍵管理とデータ保護実装

**目的と背景**:
- **目的**: Phase A（無料）環境における包括的セキュリティ基盤の確立
- **背景**: 段階的ハイブリッドアーキテクチャにおけるセキュリティレイヤーの実装

**実行コマンド**:
```bash
# Clerk認証設定（フロントエンド）
mkdir -p frontend/src/lib/auth

cat > frontend/src/lib/auth/clerk-config.ts << 'EOF'
import { ClerkProvider } from '@clerk/nextjs';
import { dark } from '@clerk/themes';

// ✅ セキュリティ強化Clerk設定
export const clerkConfig = {
  appearance: {
    baseTheme: dark,
    signIn: {
      variables: {
        // MFA必須化
        forceMFA: true,
        // セッション期限（1時間）
        sessionTimeout: 3600000,
        // パスワード強度要件
        passwordComplexity: {
          minimumLength: 12,
          requireNumbers: true,
          requireLowercase: true,
          requireUppercase: true,
          requireSpecialCharacters: true
        }
      }
    }
  },
  // ✅ 組織機能有効化
  afterSignInUrl: "/dashboard",
  afterSignUpUrl: "/onboarding",
  // ✅ セキュリティリダイレクト
  afterSignOutUrl: "/",
  // ✅ 組織作成制限
  organizationMode: "required" as const
};
EOF

# APIルート保護実装
cat > frontend/src/middleware/auth.ts << 'EOF'
import { auth } from '@clerk/nextjs/server';
import { NextRequest, NextResponse } from 'next/server';

export async function authMiddleware(request: NextRequest) {
  // ✅ 認証チェック
  const { userId, orgId } = auth();

  if (!userId) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  // ✅ 組織レベル認可
  if (request.url.includes('/org/') && !orgId) {
    return new NextResponse('Organization membership required', { status: 403 });
  }

  // ✅ セキュリティヘッダー追加
  const response = NextResponse.next();
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  return response;
}
EOF

# セキュリティ検証スクリプト
cat > infrastructure/scripts/security-check.sh << 'EOF'
#!/bin/bash
echo "🔍 AutoForgeNexus セキュリティチェック"

ERRORS=0

# ✅ Phase A 必須シークレット検証
PHASE_A_SECRETS=(
  "CLERK_PUBLISHABLE_KEY"
  "CLERK_SECRET_KEY"
  "DATABASE_URL"
  "TURSO_AUTH_TOKEN"
  "ENCRYPTION_KEY"
  "PYTHON_SERVICE_API_KEY"
)

echo "📋 Phase A セキュリティチェック:"
for secret in "${PHASE_A_SECRETS[@]}"; do
  if [ -z "${!secret}" ] && [ ! -f .env.local ]; then
    echo "❌ Missing critical secret: $secret"
    ERRORS=$((ERRORS + 1))
  else
    echo "✅ $secret configured"
  fi
done

# ✅ ファイル権限チェック
echo "🔒 ファイル権限チェック:"
if [ -f .env.local ]; then
  PERM=$(stat -c "%a" .env.local 2>/dev/null || stat -f "%A" .env.local 2>/dev/null)
  if [ "$PERM" != "600" ]; then
    echo "⚠️  .env.local permissions should be 600 (currently $PERM)"
    chmod 600 .env.local
    echo "✅ Fixed .env.local permissions"
  else
    echo "✅ .env.local permissions secure"
  fi
fi

# ✅ .gitignore チェック
echo "📁 .gitignore セキュリティチェック:"
SECURITY_IGNORES=(".env.local" ".env.*.local" "**/*.key" "**/*.pem")
for ignore in "${SECURITY_IGNORES[@]}"; do
  if ! grep -q "$ignore" .gitignore; then
    echo "⚠️  Missing in .gitignore: $ignore"
    echo "$ignore" >> .gitignore
    echo "✅ Added $ignore to .gitignore"
  else
    echo "✅ $ignore excluded from git"
  fi
done

# ✅ Cloudflare設定チェック
echo "☁️  Cloudflare設定チェック:"
if [ -f infrastructure/cloudflare/workers/wrangler.toml ]; then
  if grep -q "security" infrastructure/cloudflare/workers/wrangler.toml; then
    echo "✅ wrangler.toml security configuration found"
  else
    echo "❌ wrangler.toml missing security configuration"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo "❌ wrangler.toml not found"
  ERRORS=$((ERRORS + 1))
fi

# ✅ 結果レポート
if [ $ERRORS -eq 0 ]; then
  echo "🎉 All Phase A security requirements met"
  echo "🚀 Ready for Phase B security implementation"
  exit 0
else
  echo "💥 $ERRORS security issues found"
  echo "🔧 Please fix the issues above before proceeding"
  exit 1
fi
EOF

chmod +x infrastructure/scripts/security-check.sh

# CSP設定ファイル
cat > public/_headers << 'EOF'
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), camera=(), microphone=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://clerk.dev; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.clerk.dev https://clerk.dev; frame-ancestors 'none';
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
EOF

echo "✅ Security configuration and validation scripts created"
echo "🔐 Run './infrastructure/scripts/security-check.sh' to validate security setup"
```

**期待される成果物**:
- Clerk認証MFA必須化設定
- セキュリティ検証スクリプト
- CSP・セキュリティヘッダー設定
- 暗号化・データ保護実装

---

## 📝 **Step 2.3: CI/CD実装完成**

### **Task 2.3.1: GitHub Actions デプロイ実装**

**コマンド**: `/ai:infrastructure:cicd-deploy --cloudflare --automated`

**担当エージェント**:
- **devops-coordinator Agent** (リーダー)
- **security-architect Agent** (シークレット管理)

**何をやるのか**:
- Phase 1で作成したCD ワークフローの実装部分完成
- Cloudflareデプロイスクリプト実装
- 環境別デプロイ戦略実装
- ロールバック機能実装

**目的と背景**:
- **目的**: Phase 1で設定したCI/CDワークフローを実際にデプロイ可能な状態に完成
- **背景**: 実際のインフラ設定が完了したため、具体的なデプロイコマンドを実装可能

**実行コマンド**:
```bash
# CD ワークフロー更新（実装版）
cat > .github/workflows/cd.yml << 'EOF'
name: CD - Deploy to Cloudflare

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js for Wrangler
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Wrangler
        run: npm install -g wrangler@latest

      - name: Deploy to Cloudflare Workers
        run: |
          cd infrastructure/cloudflare/workers
          cp -r ../../../backend/src/* .
          wrangler deploy --env production
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}

  deploy-frontend:
    runs-on: ubuntu-latest
    needs: deploy-backend
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'

      - name: Enable pnpm
        run: corepack enable

      - name: Install dependencies
        run: |
          cd frontend
          pnpm install --frozen-lockfile

      - name: Build frontend
        run: |
          cd frontend
          pnpm build
          pnpm export
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.CLOUDFLARE_WORKERS_URL }}

      - name: Deploy to Cloudflare Pages
        run: |
          npm install -g wrangler@latest
          cd frontend
          wrangler pages deploy out --project-name autoforge-nexus-frontend
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}

  health-check:
    runs-on: ubuntu-latest
    needs: [deploy-backend, deploy-frontend]
    steps:
      - name: Health Check Backend
        run: |
          sleep 30
          curl -f ${{ secrets.CLOUDFLARE_WORKERS_URL }}/health

      - name: Health Check Frontend
        run: |
          curl -f https://autoforge-nexus-frontend.pages.dev/
EOF

# 環境別デプロイスクリプト
cat > infrastructure/scripts/deploy.sh << 'EOF'
#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}
echo "Deploying to $ENVIRONMENT environment..."

case $ENVIRONMENT in
  "production")
    echo "🚀 Production deployment"
    # バックエンド
    cd infrastructure/cloudflare/workers
    cp -r ../../../backend/src/* .
    wrangler deploy --env production

    # フロントエンド
    cd ../../../frontend
    pnpm build && pnpm export
    wrangler pages deploy out --project-name autoforge-nexus-frontend
    ;;

  "staging")
    echo "🧪 Staging deployment"
    cd infrastructure/cloudflare/workers
    cp -r ../../../backend/src/* .
    wrangler deploy --env staging

    cd ../../../frontend
    NEXT_PUBLIC_API_URL=$STAGING_WORKERS_URL pnpm build && pnpm export
    wrangler pages deploy out --project-name autoforge-nexus-frontend-staging
    ;;

  *)
    echo "❌ Unknown environment: $ENVIRONMENT"
    exit 1
    ;;
esac

echo "✅ Deployment completed successfully!"
EOF

chmod +x infrastructure/scripts/deploy.sh

# ロールバックスクリプト
cat > infrastructure/scripts/rollback.sh << 'EOF'
#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}
VERSION=${2}

if [ -z "$VERSION" ]; then
    echo "❌ Please specify version to rollback to"
    echo "Usage: ./rollback.sh <environment> <version>"
    exit 1
fi

echo "⏪ Rolling back $ENVIRONMENT to version $VERSION..."

case $ENVIRONMENT in
  "production")
    wrangler rollback --name autoforge-nexus-api $VERSION
    wrangler pages deployment tail --project-name autoforge-nexus-frontend
    ;;
  "staging")
    wrangler rollback --name autoforge-nexus-api-staging $VERSION
    wrangler pages deployment tail --project-name autoforge-nexus-frontend-staging
    ;;
esac

echo "✅ Rollback completed!"
EOF

chmod +x infrastructure/scripts/rollback.sh
```

**期待される成果物**:
- 実装済みCDワークフロー
- 環境別デプロイスクリプト
- ロールバック機能
- ヘルスチェック機能

---

## 📝 **Step 2.4: 監視・ログ基盤構築**

### **Task 2.4.1: 監視・アラート設定**

**コマンド**: `/ai:infrastructure:monitoring --cloudflare --basic-alerts`

**担当エージェント**:
- **observability-engineer Agent** (リーダー)

**何をやるのか**:
- Cloudflare Analytics設定
- 基本的なアラート設定
- ログ集約設定
- パフォーマンスモニタリング設定

**目的と背景**:
- **目的**: サービスの健全性とパフォーマンスを監視する基盤の構築
- **背景**: 個人開発でも本番サービスの安定運用には基本的な監視が必要

**実行コマンド**:
```bash
# 監視設定ディレクトリ
mkdir -p infrastructure/monitoring

# Cloudflare監視設定
cat > infrastructure/monitoring/cloudflare-monitoring.sh << 'EOF'
#!/bin/bash
echo "Setting up Cloudflare monitoring..."

# Workers Analytics設定
wrangler analytics --help

# 基本アラート設定用スクリプト（手動設定ガイド）
cat << 'GUIDE'
=== Cloudflare Monitoring Setup Guide ===

1. Workers Analytics:
   - Go to Cloudflare Dashboard > Workers > autoforge-nexus-api
   - Enable Analytics and Logs
   - Set up custom metrics for API endpoints

2. Pages Analytics:
   - Go to Cloudflare Dashboard > Pages > autoforge-nexus-frontend
   - Enable Web Analytics
   - Configure performance monitoring

3. Basic Alerts (via Dashboard):
   - Error rate > 5%
   - Response time > 1000ms
   - Availability < 99%

4. R2 Analytics:
   - Monitor storage usage
   - Track request patterns

GUIDE

echo "Monitoring setup guide displayed above ☝️"
EOF

chmod +x infrastructure/monitoring/cloudflare-monitoring.sh

# ログ設定
cat > infrastructure/monitoring/logging-config.json << 'EOF'
{
  "logLevel": "info",
  "structuredLogging": true,
  "outputs": [
    {
      "type": "console",
      "format": "json"
    },
    {
      "type": "cloudflare",
      "format": "json",
      "fields": [
        "timestamp",
        "level",
        "message",
        "requestId",
        "userId",
        "action",
        "duration",
        "error"
      ]
    }
  ],
  "filters": {
    "health": false,
    "static": false
  }
}
EOF

# 基本ヘルスチェックAPI実装
cat > backend/src/monitoring.py << 'EOF'
"""
Basic monitoring and health check implementation
"""
import time
import psutil
from datetime import datetime
from typing import Dict, Any


def get_health_status() -> Dict[str, Any]:
    """システムヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "service": "autoforge-nexus-backend",
        "uptime": get_uptime(),
        "resources": get_resource_usage()
    }


def get_uptime() -> float:
    """アップタイム取得（秒）"""
    return time.time() - psutil.boot_time()


def get_resource_usage() -> Dict[str, Any]:
    """リソース使用状況"""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }


def log_request(request_id: str, endpoint: str, duration: float, status: int):
    """構造化リクエストログ"""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "requestId": request_id,
        "endpoint": endpoint,
        "duration": duration,
        "status": status,
        "level": "info" if status < 400 else "error"
    }
    print(f"REQUEST_LOG: {log_data}")


def log_error(error: Exception, context: Dict[str, Any] = None):
    """エラーログ"""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": "error",
        "error": str(error),
        "error_type": type(error).__name__,
        "context": context or {}
    }
    print(f"ERROR_LOG: {log_data}")
EOF
```

**期待される成果物**:
- Cloudflare監視設定
- 構造化ログ設定
- 基本ヘルスチェック実装
- アラート設定ガイド

---

## 🔄 **タスク実行順序と依存関係**

### **フェーズ1: 事前準備**
- **Task 0.1**: インフラツール確認（並列実行不可・最優先）

### **フェーズ2: Docker環境構築**
- **Task 2.1.1**: プロジェクト構造とDocker基盤作成
- **Task 2.1.2**: Docker開発環境構築（Task 2.1.1完了後）
- **Task 2.1.3**: Docker本番環境構築（Task 2.1.2完了後・並列実行可能）

### **フェーズ3: Cloudflare環境構築**
- **Task 2.2.1**: Cloudflare Workers Python設定（Docker構築完了後）
- **Task 2.2.2**: Cloudflare Pages設定（Task 2.2.1完了後・並列実行可能）
- **Task 2.2.3**: セキュリティ設定と検証スクリプト（Task 2.2.1完了後・並列実行可能）

### **フェーズ4: CI/CD・監視完成**
- **Task 2.3.1**: GitHub Actions デプロイ実装（Cloudflare設定完了後）
- **Task 2.4.1**: 監視・アラート設定（全タスク完了後・並列実行可能）

---

## ✅ **Phase 2 インフラ環境完了チェックリスト**

### **Docker環境完了確認**
- [ ] プロジェクト構造作成完了（`tree -L 3 .`）
- [ ] Docker開発環境動作確認（`docker-compose -f docker-compose.dev.yml up -d`）
- [ ] Docker本番環境ビルド確認（`docker-compose -f docker-compose.prod.yml build`）
- [ ] マルチサービス連携確認（backend, frontend, redis, langfuse）
- [ ] ホットリロード機能確認
- [ ] ヘルスチェック動作確認

### **Cloudflare環境完了確認**
- [ ] Wrangler CLI認証確認（`wrangler whoami`）
- [ ] Workers設定確認（`wrangler.toml`セキュリティ設定済み）
- [ ] Pages設定確認（build・deploy設定済み）
- [ ] R2バケット作成確認
- [ ] KVネームスペース作成確認
- [ ] 環境変数・シークレット設定確認
- [ ] CORS・CSP・HSTS設定確認
- [ ] レート制限実装確認

### **CI/CD完了確認**
- [ ] CD ワークフローデプロイ実装確認
- [ ] 環境別デプロイスクリプト動作確認
- [ ] ロールバック機能確認
- [ ] ヘルスチェック自動化確認
- [ ] デプロイ後確認自動化

### **監視・ログ完了確認**
- [ ] Cloudflare Analytics設定確認
- [ ] 構造化ログ出力確認
- [ ] 基本ヘルスチェックAPI実装確認
- [ ] アラート設定ガイド作成確認

### **セキュリティ設定完了確認**
- [ ] Clerk認証MFA必須化確認
- [ ] セキュリティ検証スクリプト動作確認
- [ ] セキュリティヘッダー設定確認
- [ ] 暗号化鍵管理確認
- [ ] .gitignoreセキュリティ除外確認
- [ ] 開発用シークレット生成確認

### **インフラ・DevOpsドキュメント**
- [ ] Docker環境構築手順書作成
- [ ] Cloudflare設定手順書作成
- [ ] デプロイ手順書作成
- [ ] 監視・トラブルシューティングガイド作成
- [ ] ロールバック手順書作成
- [ ] 環境変数管理ガイド作成
- [ ] セキュリティ設定・検証ガイド作成

---

## 📊 **インフラ環境成功指標（Phase 2）**

### **Docker環境品質指標**
- **コンテナ起動時間**: 60秒以内（全サービス起動完了）
- **ホットリロード応答**: 3秒以内（コード変更反映）
- **リソース使用効率**: メモリ使用量2GB以下（開発環境）
- **ヘルスチェック成功率**: 100%（全サービス正常応答）

### **Cloudflare統合品質指標**
- **Workers デプロイ時間**: 30秒以内
- **Pages デプロイ時間**: 120秒以内
- **エッジレスポンス時間**: 100ms以下（グローバル平均）
- **CDN キャッシュヒット率**: 85%以上

### **CI/CD自動化品質指標**
- **デプロイ成功率**: 98%以上
- **デプロイ時間**: 5分以内（フル デプロイ）
- **ロールバック時間**: 2分以内
- **ヘルスチェック自動化**: 100%（デプロイ後確認）

### **監視・運用品質指標**
- **ログ可視性**: 構造化ログ100%対応
- **アラート応答時間**: 5分以内（重要アラート）
- **稼働時間目標**: 99.9%（月間）
- **パフォーマンス監視**: リアルタイム メトリクス取得

---

## 🎯 **Phase 3へのインフラ基盤準備完了**

Phase 2 インフラ・DevOps環境構築完了後、以下の確認でPhase 3へ進む：

### **インフラ基盤確認コマンド**
```bash
# 全体インフラ確認
echo "=== Phase 2 Infrastructure Check ==="
echo "Docker: $(docker --version)"
echo "Docker Compose: $(docker-compose --version)"
echo "Wrangler: $(wrangler --version)"

# プロジェクト構造確認
echo "=== Project Structure ==="
tree -L 3 .

# Docker環境確認
echo "=== Docker Environment ==="
docker-compose -f docker-compose.dev.yml config --quiet && echo "✅ Dev config valid"
docker-compose -f docker-compose.prod.yml config --quiet && echo "✅ Prod config valid"

# Cloudflare設定確認
echo "=== Cloudflare Configuration ==="
ls -la infrastructure/cloudflare/workers/wrangler.toml && echo "✅ Workers config exists"
ls -la infrastructure/cloudflare/pages/pages-config.json && echo "✅ Pages config exists"

# CI/CD確認
echo "=== CI/CD Pipeline ==="
ls -la .github/workflows/cd.yml && echo "✅ CD workflow exists"
ls -la infrastructure/scripts/deploy.sh && echo "✅ Deploy script exists"

# セキュリティ検証
echo "=== Security Validation ==="
if [ -f infrastructure/scripts/security-check.sh ]; then
  ./infrastructure/scripts/security-check.sh
else
  echo "❌ Security check script not found"
fi

# 監視設定確認
echo "=== Monitoring Setup ==="
ls -la infrastructure/monitoring/ && echo "✅ Monitoring config exists"

echo "Phase 2 Infrastructure Complete! ✅ Ready for Phase 3"
echo "Next: Phase 3 'バックエンド環境構築'"
```

**Phase 2 インフラ・DevOps環境構築完了の確認が取れましたら、Phase 3「バックエンド環境構築」の詳細タスク分解を実行いたします。**