# AutoForgeNexus 環境構築完全ガイド

## 📋 **概要**

AutoForgeNexus
AI プロンプト最適化システムの環境構築を段階的に実行するための完全ガイドです。各コマンドの詳細な指示、AI への具体的なコメント、設定、仕様を含め、タスクを完了させるための包括的な手順書を提供します。

## 🎯 **目的**

- バックエンド（Python 3.13 + FastAPI）環境の完全構築
- フロントエンド（Next.js 15.5 + React 19）環境の完全構築
- Git・バージョン管理環境の最適化設定
- インフラ（Cloudflare + Docker）環境の構築
- 品質保証・監視システムの構築

## 📚 **ドキュメント構成**

### **フェーズ別詳細ガイド**

- [Phase 1: Git・基盤環境構築](#phase-1-git基盤環境構築)
- [Phase 2: インフラ・DevOps環境構築](#phase-2-インフラdevops環境構築)
- [Phase 3: バックエンド環境構築](#phase-3-バックエンド環境構築)
- [Phase 4: データベース・ベクトル環境構築](#phase-4-データベースベクトル環境構築)
- [Phase 5: フロントエンド環境構築](#phase-5-フロントエンド環境構築)
- [Phase 6: 統合・品質保証](#phase-6-統合品質保証)

### **補助資料**

- [トラブルシューティング](#トラブルシューティング)
- [FAQ](#faq)
- [参考資料](#参考資料)

---

# Phase 1: Git・基盤環境構築

## 🚀 **目標**

Git環境とプロジェクト基盤の確立により、全ての開発作業の基盤を構築する。

## 📋 **前提条件**

### **必須ツール確認**

```bash
# Git バージョン確認（2.40+必須）
git --version
# Node.js バージョン確認（20+必須）
node --version
# Python バージョン確認（3.13必須）
python3.13 --version
# pnpm バージョン確認（8+必須）
pnpm --version
# Docker バージョン確認（24+必須）
docker --version
```

## 🔧 **Step 1.1: Git環境とブランチ戦略の確立**

### **コマンド**

```bash
/ai:development:git init --strategy gitflow --hooks --semantic-version
```

### **AI への詳細指示**

```markdown
# Git 環境構築指示

## 実行内容

1. GitFlow ブランチ戦略の完全セットアップ
2. pre-commit、commit-msg、pre-push フックの設定
3. semantic versioning 対応の設定
4. ブランチ保護ルールの設定

## 具体的な作業項目

### GitFlow ブランチ設定

- main: 本番リリース用
- develop: 開発統合用
- feature/\*: 機能開発用
- release/\*: リリース準備用
- hotfix/\*: 緊急修正用

### Git フック設定

- pre-commit: コード品質チェック（ruff, mypy, prettier）
- commit-msg: Conventional Commits 強制
- pre-push: テスト実行とビルド確認

### 設定ファイル作成

- .gitignore: Python, Node.js, Docker対応
- .gitmessage: コミットメッセージテンプレート
- CODEOWNERS: コードオーナー設定

### ブランチ保護設定

- main, develop ブランチの direct push 禁止
- PR マージ前のレビュー必須
- status check 必須（CI/CD パス）

## 期待される成果物

- 完全に設定された Git リポジトリ
- ブランチ戦略の文書化
- 開発ワークフローガイド
```

### **検証方法**

```bash
# ブランチ確認
git branch -a
git flow version

# フック確認
ls -la .git/hooks/

# 設定確認
cat .gitignore
cat .gitmessage
cat CODEOWNERS
```

---

## 🔧 **Step 1.2: プロジェクト基盤初期化**

### **コマンド**

```bash
/ai:core:init AutoForgeNexus --phase 1 --agents core --env dev --ddd
```

### **AI への詳細指示**

```markdown
# プロジェクト基盤初期化指示

## 実行内容

DDD 原則に基づくプロジェクト構造の構築と Phase 1 エージェントチームの起動

## 具体的な作業項目

### プロジェクト構造作成
```

/backend/ # Python/FastAPI バックエンド /src/
/domain/ # ドメインエンティティとビジネスロジック /entities/ # ドメインエンティティ /value_objects/ # 値オブジェクト /repositories/ # リポジトリインターフェース /services/ # ドメインサービス /application/ # ユースケースとアプリケーションサービス /use_cases/ # ビジネスユースケース /services/ # アプリケーションサービス /dtos/ # データ転送オブジェクト /infrastructure/ # 外部サービス実装 /repositories/ # リポジトリ実装 /external/ # 外部API統合 /database/ # データベース接続 /presentation/ #
APIコントローラーとスキーマ /api/ # FastAPI ルーター /schemas/ #
Pydantic スキーマ /middleware/ # ミドルウェア /tests/ # テスト /unit/ # ユニットテスト /integration/ # 統合テスト /e2e/ #
E2Eテスト /migrations/ # データベースマイグレーション /scripts/ # ユーティリティスクリプト

/frontend/ # Next.js/React フロントエンド /src/ /app/ # Next.js 15 App Router
/components/ # 再利用可能UIコンポーネント /ui/ # 基本UIコンポーネント /features/ # 機能固有コンポーネント /layout/ # レイアウトコンポーネント /hooks/ # カスタムReactフック /stores/ #
Zustand状態管理 /lib/ # ユーティリティ /types/ #
TypeScript型定義 /public/ # 静的ファイル /tests/ # フロントエンドテスト /**tests**/ #
Jest テスト /e2e/ # Playwright E2Eテスト

/docs/ # ドキュメント /architecture/ # アーキテクチャドキュメント /api/ #
API ドキュメント /development/ # 開発ガイド /deployment/ # デプロイガイド

/infrastructure/ # インフラ設定 /docker/ # Docker設定 /terraform/ #
Terraform設定（必要に応じて）/kubernetes/ # K8s設定（必要に応じて）

````

### 設定ファイル作成

#### backend/pyproject.toml
```toml
[project]
name = "autoforge-nexus-backend"
version = "0.1.0"
description = "AutoForgeNexus Backend API"
requires-python = ">=3.13"
dependencies = [
    "fastapi==0.116.1",
    "sqlalchemy==2.0.32",
    "pydantic==2.9.2",
    "uvicorn==0.32.0",
    "python-dotenv==1.0.1",
    "redis==5.2.0",
    "langchain==0.3.27",
    "langgraph==0.6.7",
    "litellm==1.76.1",
    "langfuse==2.56.2"
]

[project.optional-dependencies]
dev = [
    "pytest==8.3.3",
    "pytest-asyncio==0.24.0",
    "ruff==0.7.4",
    "mypy==1.13.0",
    "black==24.10.0"
]

[tool.ruff]
line-length = 88
target-version = "py313"

[tool.mypy]
python_version = "3.13"
strict = true
````

#### frontend/package.json

```json
{
  "name": "autoforge-nexus-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "next": "15.5.0",
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "typescript": "5.6.3",
    "tailwindcss": "4.0.0"
  },
  "devDependencies": {
    "@types/react": "19.0.0",
    "@types/react-dom": "19.0.0",
    "eslint": "9.15.0",
    "eslint-config-next": "15.5.0",
    "prettier": "3.3.3",
    "jest": "29.7.0",
    "@playwright/test": "1.48.0"
  }
}
```

#### docker-compose.dev.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - '8000:8000'
    environment:
      - DATABASE_URL=sqlite:///./autoforge.db
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./backend:/app
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - '3000:3000'
    volumes:
      - ./frontend:/app
    depends_on:
      - backend

  redis:
    image: redis:7-alpine
    ports:
      - '6379:6379'

  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - '3001:3000'
    environment:
      - DATABASE_URL=postgresql://langfuse:password@langfuse-db:5432/langfuse
    depends_on:
      - langfuse-db

  langfuse-db:
    image: postgres:16
    environment:
      - POSTGRES_USER=langfuse
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=langfuse
    volumes:
      - langfuse_data:/var/lib/postgresql/data

volumes:
  langfuse_data:
```

### エージェント起動確認

Phase 1 で起動されるべきエージェント（7エージェント）:

- system-architect (リーダー)
- domain-modeller
- backend-developer
- database-administrator
- devops-coordinator
- security-architect
- version-control-specialist

## 期待される成果物

- DDD準拠のプロジェクト構造
- 必要な設定ファイル一式
- Docker開発環境
- Phase 1 エージェントチーム起動

````

### **検証方法**
```bash
# プロジェクト構造確認
tree -L 3

# 設定ファイル確認
cat backend/pyproject.toml
cat frontend/package.json
cat docker-compose.dev.yml

# Docker環境起動テスト
docker-compose -f docker-compose.dev.yml up --build -d
docker-compose -f docker-compose.dev.yml ps
````

---

# Phase 2: インフラ・DevOps環境構築

## 🚀 **目標**

Cloudflareエコシステムを活用したスケーラブルなインフラ基盤と、観測可能性を持つ監視システムの構築。

## 🔧 **Step 2.1: デプロイメント戦略とインフラ準備**

### **コマンド**

```bash
/ai:operations:deploy dev --strategy rolling --edge
```

### **AI への詳細指示**

````markdown
# インフラ・デプロイメント構築指示

## 実行内容

Cloudflare エコシステムを活用した開発環境デプロイメント基盤の構築

## 具体的な作業項目

### Cloudflare 設定

1. **Cloudflare Workers 設定**

   - backend API 用 Worker 設定
   - エッジでの API 処理設定
   - KV ストレージ設定

2. **Cloudflare Pages 設定**

   - frontend 静的サイト配信
   - プレビューデプロイ設定
   - カスタムドメイン設定

3. **Cloudflare R2 設定**
   - ファイルストレージ設定
   - CDN 配信設定

### Docker 設定最適化

#### backend/Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install -e .

# Copy source code
COPY src/ ./src/
COPY migrations/ ./migrations/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.presentation.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```
````

#### frontend/Dockerfile

```dockerfile
FROM node:20-alpine AS base

# Install pnpm
RUN corepack enable

FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

FROM base AS runner
WORKDIR /app
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### CI/CD パイプライン設定

#### .github/workflows/deploy-dev.yml

```yaml
name: Deploy Development

on:
  push:
    branches: [develop]
  pull_request:
    branches: [develop]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          cd backend
          pip install -e .[dev]
      - name: Run tests
        run: |
          cd backend
          pytest
      - name: Run linting
        run: |
          cd backend
          ruff check
          mypy src/

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with:
          version: 8
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - name: Install dependencies
        run: |
          cd frontend
          pnpm install
      - name: Run tests
        run: |
          cd frontend
          pnpm test
      - name: Type check
        run: |
          cd frontend
          pnpm type-check
      - name: Lint
        run: |
          cd frontend
          pnpm lint

  deploy-backend:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Cloudflare Workers
        run: |
          cd backend
          wrangler deploy

  deploy-frontend:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Cloudflare Pages
        run: |
          cd frontend
          pnpm build
          wrangler pages deploy dist
```

### Rolling Deployment 戦略

1. **段階的デプロイ**

   - 20% → 50% → 100% のトラフィック移行
   - 各段階でヘルスチェック実行
   - 異常検知時の自動ロールバック

2. **ヘルスチェック設定**
   - API エンドポイントの応答確認
   - データベース接続確認
   - 外部サービス連携確認

## 期待される成果物

- Cloudflare 環境の完全設定
- Docker コンテナの最適化
- CI/CD パイプライン
- Rolling Deployment 設定

````

### **検証方法**
```bash
# Docker ビルドテスト
docker build -t autoforge-backend ./backend
docker build -t autoforge-frontend ./frontend

# Cloudflare 設定確認
wrangler whoami
wrangler pages project list

# CI/CD 動作確認
git push origin develop
````

---

## 🔧 **Step 2.2: 監視・観測可能性の設定**

### **コマンド**

```bash
/ai:operations:monitor system --metrics --traces --logs --alerts
```

### **AI への詳細指示**

````markdown
# 監視・観測可能性構築指示

## 実行内容

3 つの柱（メトリクス、トレース、ログ）を統合した包括的監視体制の構築

## 具体的な作業項目

### 1. メトリクス収集設定

#### backend/src/presentation/middleware/metrics.py

```python
from prometheus_client import Counter, Histogram, generate_latest
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# メトリクス定義
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        return response
```
````

#### frontend/src/lib/monitoring.ts

```typescript
// Web Vitals 収集
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

export function initWebVitals() {
  getCLS(sendToAnalytics);
  getFID(sendToAnalytics);
  getFCP(sendToAnalytics);
  getLCP(sendToAnalytics);
  getTTFB(sendToAnalytics);
}

function sendToAnalytics(metric: any) {
  // Cloudflare Analytics に送信
  fetch('/api/analytics', {
    method: 'POST',
    body: JSON.stringify(metric),
  });
}

// エラー監視
export function initErrorMonitoring() {
  window.addEventListener('error', (event) => {
    console.error('JavaScript Error:', event.error);
    // エラーログの送信
    fetch('/api/errors', {
      method: 'POST',
      body: JSON.stringify({
        message: event.error?.message,
        stack: event.error?.stack,
        url: window.location.href,
        timestamp: new Date().toISOString(),
      }),
    });
  });
}
```

### 2. 分散トレーシング設定

#### backend/src/infrastructure/tracing.py

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

def init_tracing(app):
    # Tracer Provider 設定
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    # Jaeger Exporter 設定
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=14268,
    )

    # Span Processor 設定
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # FastAPI 自動計装
    FastAPIInstrumentor.instrument_app(app)

    # SQLAlchemy 自動計装
    SQLAlchemyInstrumentor().instrument()

    return tracer
```

### 3. 構造化ログ設定

#### backend/src/infrastructure/logging.py

```python
import structlog
import logging
from typing import Any, Dict

def configure_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=False,
    )

logger = structlog.get_logger()

# ログコンテキスト
def log_context(**kwargs: Any) -> Dict[str, Any]:
    return {
        "service": "autoforge-nexus",
        "version": "0.1.0",
        **kwargs
    }
```

### 4. アラート設定

#### monitoring/alerts.yml

```yaml
groups:
  - name: autoforge_alerts
    rules:
      - alert: HighErrorRate
        expr:
          (rate(http_requests_total{status=~"5.."}[5m]) /
          rate(http_requests_total[5m])) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: 'High error rate detected'
          description: 'Error rate is {{ $value }} for the last 5 minutes'

      - alert: HighResponseTime
        expr:
          histogram_quantile(0.95,
          rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: 'High response time detected'
          description: '95th percentile response time is {{ $value }}s'

      - alert: DatabaseConnectionFailure
        expr: up{job="database"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: 'Database connection failure'
          description: 'Database is not responding'
```

### 5. ダッシュボード設定

#### monitoring/grafana-dashboard.json

```json
{
  "dashboard": {
    "title": "AutoForgeNexus Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "Errors/sec"
          }
        ]
      }
    ]
  }
}
```

### 6. 監視スタック起動

#### docker-compose.monitoring.yml

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - '9090:9090'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/alerts.yml:/etc/prometheus/alerts.yml

  grafana:
    image: grafana/grafana
    ports:
      - '3001:3000'
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./monitoring/grafana-dashboard.json:/var/lib/grafana/dashboards/dashboard.json

  jaeger:
    image: jaegertracing/all-in-one
    ports:
      - '16686:16686'
      - '14268:14268'
    environment:
      - COLLECTOR_OTLP_ENABLED=true

  alertmanager:
    image: prom/alertmanager
    ports:
      - '9093:9093'
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
```

## 期待される成果物

- 完全な監視スタック
- メトリクス、トレース、ログの統合
- アラート設定
- ダッシュボード
- 自動異常検知システム

````

### **検証方法**
```bash
# 監視スタック起動
docker-compose -f docker-compose.monitoring.yml up -d

# エンドポイント確認
curl http://localhost:9090  # Prometheus
curl http://localhost:3001  # Grafana
curl http://localhost:16686 # Jaeger

# メトリクス確認
curl http://localhost:8000/metrics
````

---

# Phase 3: バックエンド環境構築

## 🚀 **目標**

DDD原則とイベント駆動アーキテクチャに基づく堅牢なバックエンドシステムの構築。

## 🔧 **Step 3.1: バックエンドアーキテクチャ設計**

### **コマンド**

```bash
/ai:architecture:design microservices --ddd --event-driven --scale horizontal
```

### **AI への詳細指示**

```markdown
# バックエンドアーキテクチャ設計指示

## 実行内容

DDD + イベント駆動 + 水平スケーリング対応のマイクロサービス設計

## 具体的な作業項目

### 1. ドメイン境界の定義
```

Bounded Contexts:

1. Prompt Context (プロンプト管理)

   - エンティティ: Prompt, Template, Version
   - 値オブジェクト: PromptContent, Quality, Style

2. Evaluation Context (評価システム)

   - エンティティ: Evaluation, Metric, Benchmark
   - 値オブジェクト: Score, Feedback, Criteria

3. User Context (ユーザー管理)

   - エンティティ: User, Organization, Subscription
   - 値オブジェクト: UserProfile, Preferences

4. LLM Context (LLM統合)

   - エンティティ: Provider, Model, APIKey
   - 値オブジェクト: Usage, Cost, Limits

5. Workflow Context (ワークフロー)
   - エンティティ: Workflow, Step, Execution
   - 値オブジェクト: Configuration, Status

````

### 2. マイクロサービス構成
```python
# backend/src/domain/prompt/entities/prompt.py
from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from ..value_objects import PromptContent, Quality, Style
from ...shared.entity import Entity
from ...shared.domain_events import DomainEvent

@dataclass
class PromptCreated(DomainEvent):
    prompt_id: UUID
    user_id: UUID
    content: str
    created_at: datetime

@dataclass
class PromptUpdated(DomainEvent):
    prompt_id: UUID
    user_id: UUID
    old_content: str
    new_content: str
    updated_at: datetime

class Prompt(Entity):
    def __init__(
        self,
        user_id: UUID,
        content: PromptContent,
        title: str,
        description: Optional[str] = None,
        style: Optional[Style] = None,
        quality: Optional[Quality] = None
    ):
        super().__init__()
        self._user_id = user_id
        self._content = content
        self._title = title
        self._description = description
        self._style = style
        self._quality = quality
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

        # ドメインイベント追加
        self.add_domain_event(PromptCreated(
            prompt_id=self.id,
            user_id=user_id,
            content=content.value,
            created_at=self._created_at
        ))

    def update_content(self, new_content: PromptContent) -> None:
        old_content = self._content.value
        self._content = new_content
        self._updated_at = datetime.utcnow()

        self.add_domain_event(PromptUpdated(
            prompt_id=self.id,
            user_id=self._user_id,
            old_content=old_content,
            new_content=new_content.value,
            updated_at=self._updated_at
        ))

    @property
    def content(self) -> PromptContent:
        return self._content

    @property
    def user_id(self) -> UUID:
        return self._user_id
````

### 3. リポジトリパターン実装

```python
# backend/src/domain/prompt/repositories/prompt_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities import Prompt

class PromptRepository(ABC):
    @abstractmethod
    async def save(self, prompt: Prompt) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, prompt_id: UUID) -> Optional[Prompt]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[Prompt]:
        pass

    @abstractmethod
    async def delete(self, prompt_id: UUID) -> None:
        pass

# backend/src/infrastructure/repositories/sqlalchemy_prompt_repository.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from ...domain.prompt.repositories import PromptRepository
from ...domain.prompt.entities import Prompt
from ..models import PromptModel

class SQLAlchemyPromptRepository(PromptRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, prompt: Prompt) -> None:
        model = PromptModel.from_entity(prompt)
        self._session.add(model)
        await self._session.commit()

    async def get_by_id(self, prompt_id: UUID) -> Optional[Prompt]:
        result = await self._session.execute(
            select(PromptModel).where(PromptModel.id == prompt_id)
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None
```

### 4. ユースケース実装

```python
# backend/src/application/use_cases/create_prompt.py
from dataclasses import dataclass
from uuid import UUID
from typing import Optional

from ...domain.prompt.entities import Prompt
from ...domain.prompt.repositories import PromptRepository
from ...domain.prompt.value_objects import PromptContent
from ..services import EventPublisher

@dataclass
class CreatePromptCommand:
    user_id: UUID
    content: str
    title: str
    description: Optional[str] = None

class CreatePromptUseCase:
    def __init__(
        self,
        prompt_repository: PromptRepository,
        event_publisher: EventPublisher
    ):
        self._prompt_repository = prompt_repository
        self._event_publisher = event_publisher

    async def execute(self, command: CreatePromptCommand) -> UUID:
        # ドメインオブジェクト作成
        prompt_content = PromptContent(command.content)
        prompt = Prompt(
            user_id=command.user_id,
            content=prompt_content,
            title=command.title,
            description=command.description
        )

        # 永続化
        await self._prompt_repository.save(prompt)

        # ドメインイベント発行
        for event in prompt.domain_events:
            await self._event_publisher.publish(event)

        return prompt.id
```

### 5. FastAPI コントローラー

```python
# backend/src/presentation/api/prompt_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from ...application.use_cases import CreatePromptUseCase
from ...application.dtos import CreatePromptRequest, PromptResponse
from ..dependencies import get_create_prompt_use_case

router = APIRouter(prefix="/api/v1/prompts", tags=["prompts"])

@router.post("/", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    request: CreatePromptRequest,
    use_case: CreatePromptUseCase = Depends(get_create_prompt_use_case)
):
    try:
        command = CreatePromptCommand(
            user_id=request.user_id,
            content=request.content,
            title=request.title,
            description=request.description
        )
        prompt_id = await use_case.execute(command)
        return PromptResponse(id=prompt_id, message="Prompt created successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
```

### 6. イベント駆動統合

```python
# backend/src/infrastructure/events/event_bus.py
from typing import Dict, List, Callable
from dataclasses import asdict
import json
import asyncio
import redis.asyncio as redis

from ...domain.shared.domain_events import DomainEvent

class EventBus:
    def __init__(self, redis_client: redis.Redis):
        self._redis = redis_client
        self._handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent):
        event_data = {
            "event_type": event.__class__.__name__,
            "data": asdict(event),
            "timestamp": event.occurred_at.isoformat()
        }

        # Redis Streams に発行
        await self._redis.xadd(
            f"events:{event.__class__.__name__}",
            event_data
        )

        # ローカルハンドラー実行
        handlers = self._handlers.get(event.__class__.__name__, [])
        for handler in handlers:
            asyncio.create_task(handler(event))
```

### 7. 水平スケーリング対応

```python
# backend/src/infrastructure/scaling/load_balancer.py
from typing import List
import random
import httpx
from dataclasses import dataclass

@dataclass
class ServiceInstance:
    host: str
    port: int
    health: bool = True
    load: int = 0

class LoadBalancer:
    def __init__(self):
        self._instances: List[ServiceInstance] = []

    def add_instance(self, host: str, port: int):
        self._instances.append(ServiceInstance(host, port))

    def get_instance(self) -> ServiceInstance:
        # ラウンドロビン + 負荷考慮
        healthy_instances = [i for i in self._instances if i.health]
        if not healthy_instances:
            raise Exception("No healthy instances available")

        # 負荷が最も低いインスタンスを選択
        return min(healthy_instances, key=lambda x: x.load)

    async def health_check(self):
        for instance in self._instances:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"http://{instance.host}:{instance.port}/health",
                        timeout=5.0
                    )
                    instance.health = response.status_code == 200
            except:
                instance.health = False
```

## 期待される成果物

- DDD準拠のドメイン設計
- イベント駆動アーキテクチャ
- 水平スケーリング対応の設計
- マイクロサービス境界の明確化
- 完全なコード例とドキュメント

````

### **検証方法**
```bash
# ドメイン構造確認
tree backend/src/domain/

# テスト実行
cd backend
pytest src/tests/unit/domain/
pytest src/tests/integration/

# アーキテクチャ検証
python -m pytest src/tests/architecture/
````

---

## 🔧 **Step 3.2: ドメインモデリング**

### **コマンド**

```bash
/ai:requirements:domain prompt-context --aggregate root --event-sourcing --cqrs
```

### **AI への詳細指示**

````markdown
# ドメインモデリング詳細指示

## 実行内容

プロンプトコンテキストの完全なドメインモデル設計とイベントソーシング実装

## 具体的な作業項目

### 1. 集約ルート設計

```python
# backend/src/domain/prompt/aggregates/prompt_aggregate.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..entities import Prompt, PromptVersion, PromptTemplate
from ..value_objects import PromptContent, Quality, Style
from ..events import (
    PromptCreated, PromptUpdated, PromptOptimized,
    PromptPublished, PromptArchived
)
from ...shared.aggregate_root import AggregateRoot

class PromptAggregate(AggregateRoot):
    def __init__(self, prompt_id: UUID):
        super().__init__(prompt_id)
        self._prompt: Optional[Prompt] = None
        self._versions: List[PromptVersion] = []
        self._templates: List[PromptTemplate] = []
        self._published = False
        self._archived = False

    def create_prompt(
        self,
        user_id: UUID,
        content: PromptContent,
        title: str,
        description: Optional[str] = None
    ) -> None:
        if self._prompt is not None:
            raise ValueError("Prompt already exists")

        self._prompt = Prompt(
            id=self.id,
            user_id=user_id,
            content=content,
            title=title,
            description=description
        )

        self.add_event(PromptCreated(
            aggregate_id=self.id,
            user_id=user_id,
            content=content.value,
            title=title,
            description=description,
            occurred_at=datetime.utcnow()
        ))
```
````

### 2. イベントソーシング実装

```python
# backend/src/infrastructure/event_store/event_store.py
import json
from typing import List, Optional, Type
from uuid import UUID
from dataclasses import asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from ...domain.shared.domain_events import DomainEvent
from ..models.event_model import EventModel

class EventStore:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save_events(
        self,
        aggregate_id: UUID,
        events: List[DomainEvent],
        expected_version: int
    ) -> None:
        # 楽観的ロック確認
        current_version = await self.get_version(aggregate_id)
        if current_version != expected_version:
            raise ConcurrencyError(
                f"Expected version {expected_version}, got {current_version}"
            )

        # イベント保存
        for i, event in enumerate(events):
            event_model = EventModel(
                aggregate_id=aggregate_id,
                event_type=event.__class__.__name__,
                event_data=json.dumps(asdict(event)),
                version=expected_version + i + 1,
                occurred_at=event.occurred_at
            )
            self._session.add(event_model)

        await self._session.commit()
```

### 3. CQRS実装

```python
# backend/src/application/queries/prompt_queries.py
from typing import List, Optional
from uuid import UUID
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from ...infrastructure.read_models import PromptReadModel

@dataclass
class PromptSummary:
    id: UUID
    title: str
    description: Optional[str]
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    quality_score: Optional[float]
    published: bool

class PromptQueryService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_prompt_by_id(self, prompt_id: UUID) -> Optional[PromptSummary]:
        result = await self._session.execute(
            select(PromptReadModel)
            .where(PromptReadModel.id == prompt_id)
        )
        model = result.scalar_one_or_none()

        if not model:
            return None

        return PromptSummary(
            id=model.id,
            title=model.title,
            description=model.description,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            quality_score=model.quality_score,
            published=model.published
        )
```

## 期待される成果物

- 完全な集約ルート実装
- イベントソーシング基盤
- CQRS読み書き分離
- イベント投影機能
- 楽観的ロック機能

````

### **検証方法**
```bash
# ドメインテスト
pytest src/tests/unit/domain/prompt/

# イベントソーシング確認
python -c "
from src.domain.prompt.aggregates import PromptAggregate
from src.domain.prompt.value_objects import PromptContent
from uuid import uuid4

aggregate = PromptAggregate(uuid4())
aggregate.create_prompt(uuid4(), PromptContent('test'), 'Test Prompt')
print(f'Events: {len(aggregate.uncommitted_events)}')
"
````

---

## 🔧 **Step 3.3: バックエンド実装基盤**

### **コマンド**

```bash
/ai:development:implement backend-core --tdd --coverage 80 --parallel
```

### **AI への詳細指示**

````markdown
# バックエンド実装基盤構築指示

## 実行内容

TDD手法により80%カバレッジを達成するバックエンドコア機能の実装

## 具体的な作業項目

### 1. TDDサイクル実行

#### Red Phase (失敗テスト作成)

```python
# backend/src/tests/unit/domain/test_prompt_aggregate.py
import pytest
from uuid import uuid4
from datetime import datetime

from src.domain.prompt.aggregates import PromptAggregate
from src.domain.prompt.value_objects import PromptContent
from src.domain.prompt.events import PromptCreated

class TestPromptAggregate:
    def test_create_prompt_success(self):
        # Given
        aggregate_id = uuid4()
        user_id = uuid4()
        content = PromptContent("Test prompt content")
        title = "Test Prompt"

        # When
        aggregate = PromptAggregate(aggregate_id)
        aggregate.create_prompt(user_id, content, title)

        # Then
        assert aggregate.id == aggregate_id
        assert len(aggregate.uncommitted_events) == 1
        event = aggregate.uncommitted_events[0]
        assert isinstance(event, PromptCreated)
        assert event.user_id == user_id
        assert event.content == content.value
        assert event.title == title
```
````

### 2. 並列実装戦略

```python
# backend/src/application/services/parallel_processor.py
import asyncio
from typing import List, Callable, Any
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

class ParallelProcessor:
    def __init__(self, max_workers: int = 4):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    async def process_batch(
        self,
        items: List[Any],
        processor: Callable,
        batch_size: int = 10
    ) -> List[Any]:
        """バッチ処理を並列実行"""
        results = []

        # バッチに分割
        batches = [
            items[i:i + batch_size]
            for i in range(0, len(items), batch_size)
        ]

        # 並列処理
        tasks = [
            self._process_single_batch(batch, processor)
            for batch in batches
        ]

        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 結果統合
        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                logger.error(f"Batch processing error: {batch_result}")
                continue
            results.extend(batch_result)

        return results
```

## 期待される成果物

- 80%以上のテストカバレッジ
- TDD完全実践の実装
- 並列処理対応の高性能API
- 品質ゲート統合
- 完全なCI/CD統合

````

### **検証方法**
```bash
# テスト実行とカバレッジ確認
cd backend
pytest --cov=src --cov-report=html
open htmlcov/index.html

# 品質チェック
ruff check src/
mypy src/
bandit -r src/

# 並列処理テスト
python -c "
import asyncio
from src.application.services.parallel_processor import ParallelProcessor

async def test():
    processor = ParallelProcessor(max_workers=4)
    items = list(range(100))
    results = await processor.process_batch(items, lambda x: x * 2)
    print(f'Processed {len(results)} items')

asyncio.run(test())
"
````

---

# Phase 5: フロントエンド環境構築

## 🚀 **目標**

Next.js 15.5 + React
19 による最先端フロントエンド環境の構築と、リアルタイム協調編集機能の実装基盤整備。

## 📋 **前提条件**

### **必須ツール確認**

```bash
# Node.js バージョン確認（20+必須）
node --version

# pnpm バージョン確認（8+必須）
pnpm --version

# TypeScript バージョン確認
pnpm tsc --version

# Next.js CLI確認
pnpm next --version
```

## 🔧 **Step 5.1: フロントエンドプロジェクト初期化**

### **コマンド**

```bash
/ai:development:implement frontend-init --next 15.5 --react 19 --typescript --tailwind 4
```

### **AI への詳細指示**

```markdown
# フロントエンド初期化指示

## 実行内容

Next.js 15.5 + React 19 + TypeScript + Tailwind CSS 4.0 環境の構築

## 具体的な作業項目

### プロジェクト設定

#### frontend/package.json

{ "name": "autoforge-nexus-frontend", "version": "0.1.0", "private": true,
"scripts": { "dev": "next dev", "build": "next build", "start": "next start",
"lint": "next lint", "type-check": "tsc --noEmit", "test": "jest --watch",
"test:ci": "jest --ci", "test:e2e": "playwright test" }, "dependencies": {
"next": "15.5.0", "react": "19.0.0", "react-dom": "19.0.0", "typescript":
"5.6.3", "@clerk/nextjs": "^4.29.0", "zustand": "^4.5.0", "swr": "^2.2.5",
"@tanstack/react-query": "^5.20.0" }, "devDependencies": { "@types/react":
"19.0.0", "@types/react-dom": "19.0.0", "tailwindcss": "4.0.0", "autoprefixer":
"^10.4.17", "postcss": "^8.4.35", "eslint": "9.15.0", "eslint-config-next":
"15.5.0", "prettier": "3.3.3", "jest": "^29.7.0", "@testing-library/react":
"^14.2.0", "@playwright/test": "^1.48.0" } }

### TypeScript設定

#### frontend/tsconfig.json

{ "compilerOptions": { "target": "ES2022", "lib": ["dom", "dom.iterable",
"esnext"], "allowJs": true, "skipLibCheck": true, "strict": true,
"forceConsistentCasingInFileNames": true, "noEmit": true, "esModuleInterop":
true, "module": "esnext", "moduleResolution": "bundler", "resolveJsonModule":
true, "isolatedModules": true, "jsx": "preserve", "incremental": true,
"plugins": [ { "name": "next" } ], "paths": { "@/_": ["./src/_"] } }, "include":
["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"], "exclude":
["node_modules"] }

### Tailwind CSS 4.0設定

#### frontend/tailwind.config.ts

import type { Config } from 'tailwindcss'

const config: Config = { content: [ './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
'./src/components/**/*.{js,ts,jsx,tsx,mdx}',
'./src/app/**/*.{js,ts,jsx,tsx,mdx}', ], theme: { extend: { colors: { primary: {
50: '#f0f9ff', 500: '#3b82f6', 900: '#1e3a8a', }, secondary: { 50: '#faf5ff',
500: '#a855f7', 900: '#581c87', }, }, animation: { 'fade-in': 'fadeIn 0.5s
ease-in-out', 'slide-up': 'slideUp 0.3s ease-out', }, keyframes: { fadeIn: {
'0%': { opacity: '0' }, '100%': { opacity: '1' }, }, slideUp: { '0%': {
transform: 'translateY(10px)', opacity: '0' }, '100%': { transform:
'translateY(0)', opacity: '1' }, }, }, }, }, plugins: [], }

export default config

## 期待される成果物

- Next.js 15.5プロジェクト構造
- TypeScript厳密設定
- Tailwind CSS 4.0設定
- 開発環境の完全構築
```

### **検証方法**

```bash
# 依存関係インストール
cd frontend
pnpm install

# 開発サーバー起動
pnpm dev

# TypeScript検証
pnpm type-check

# ビルド確認
pnpm build
```

---

## 🔧 **Step 5.2: UIコンポーネントシステム構築**

### **コマンド**

```bash
/ai:ui-ux-designer design-system --shadcn --accessible --responsive
```

### **AI への詳細指示**

```markdown
# UIコンポーネントシステム構築指示

## 実行内容

shadcn/ui ベースのアクセシブルでレスポンシブなデザインシステム構築

## 具体的な作業項目

### shadcn/ui設定

# frontend/components.json

{ "$schema": "https://ui.shadcn.com/schema.json", "style": "default", "rsc":
true, "tsx": true, "tailwind": { "config": "tailwind.config.ts", "css":
"src/app/globals.css", "baseColor": "slate", "cssVariables": true, "prefix": ""
}, "aliases": { "components": "@/components", "utils": "@/lib/utils" } }

### 基本スタイル設定

# frontend/src/app/globals.css

@tailwind base; @tailwind components; @tailwind utilities;

@layer base { :root { --background: 0 0% 100%; --foreground: 222.2 84% 4.9%;
--card: 0 0% 100%; --card-foreground: 222.2 84% 4.9%; --popover: 0 0% 100%;
--popover-foreground: 222.2 84% 4.9%; --primary: 221.2 83.2% 53.3%;
--primary-foreground: 210 40% 98%; --secondary: 210 40% 96.1%;
--secondary-foreground: 222.2 47.4% 11.2%; --muted: 210 40% 96.1%;
--muted-foreground: 215.4 16.3% 46.9%; --accent: 210 40% 96.1%;
--accent-foreground: 222.2 47.4% 11.2%; --destructive: 0 84.2% 60.2%;
--destructive-foreground: 210 40% 98%; --border: 214.3 31.8% 91.4%; --input:
214.3 31.8% 91.4%; --ring: 221.2 83.2% 53.3%; --radius: 0.5rem; }

.dark { --background: 222.2 84% 4.9%; --foreground: 210 40% 98%; --card: 222.2
84% 4.9%; --card-foreground: 210 40% 98%; --popover: 222.2 84% 4.9%;
--popover-foreground: 210 40% 98%; --primary: 217.2 91.2% 59.8%;
--primary-foreground: 222.2 47.4% 11.2%; --secondary: 217.2 32.6% 17.5%;
--secondary-foreground: 210 40% 98%; --muted: 217.2 32.6% 17.5%;
--muted-foreground: 215 20.2% 65.1%; --accent: 217.2 32.6% 17.5%;
--accent-foreground: 210 40% 98%; --destructive: 0 62.8% 30.6%;
--destructive-foreground: 210 40% 98%; --border: 217.2 32.6% 17.5%; --input:
217.2 32.6% 17.5%; --ring: 224.3 76.3% 48%; } }

### ユーティリティ関数

# frontend/src/lib/utils.ts

import { type ClassValue, clsx } from "clsx" import { twMerge } from
"tailwind-merge"

export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)) }

### Storybookセットアップ

# frontend/.storybook/main.ts

import type { StorybookConfig } from "@storybook/nextjs"

const config: StorybookConfig = { stories:
["../src/**/*.stories.@(js|jsx|ts|tsx|mdx)"], addons: [
"@storybook/addon-links", "@storybook/addon-essentials",
"@storybook/addon-interactions", "@storybook/addon-a11y" ], framework: { name:
"@storybook/nextjs", options: {}, }, }

export default config

## 期待される成果物

- shadcn/ui統合
- アクセシビリティ対応
- レスポンシブデザイン
- Storybook環境
- ダークモード対応
```

### **検証方法**

```bash
# shadcn/ui CLIインストール
pnpm dlx shadcn-ui@latest init

# コンポーネント追加例
pnpm dlx shadcn-ui@latest add button
pnpm dlx shadcn-ui@latest add card
pnpm dlx shadcn-ui@latest add form

# Storybook起動
pnpm storybook

# アクセシビリティチェック
pnpm exec pa11y http://localhost:3000
```

---

# Phase 6: 統合・品質保証

## 🚀 **目標**

エンタープライズレベルの品質基準を満たす統合テスト、CI/CD、監視、セキュリティ、パフォーマンステスト環境の完全構築。

## 📋 **前提条件**

### **必須ツール確認**

```bash
# Docker バージョン確認（24+必須）
docker --version
docker-compose --version

# GitHub CLI確認
gh --version

# 負荷テストツール確認
locust --version 2>/dev/null || echo "Locust not installed"
k6 version 2>/dev/null || echo "K6 not installed"

# セキュリティツール確認
trivy --version 2>/dev/null || echo "Trivy not installed"
```

## 🔧 **Step 6.1: 統合テスト環境のセットアップ**

### **コマンド**

```bash
/ai:quality:tdd test-environment --e2e playwright --api pytest --frontend jest --coverage 80
```

### **AI への詳細指示**

```markdown
# 統合テスト環境構築指示

## 実行内容

E2E、API、フロントエンドの包括的テスト環境構築（80%カバレッジ目標）

## 具体的な作業項目

### E2Eテスト設定（Playwright）

#### tests/e2e/playwright.config.ts

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({ testDir: './e2e', fullyParallel: true, forbidOnly:
!!process.env.CI, retries: process.env.CI ? 2 : 0, workers: process.env.CI ? 1 :
undefined, reporter: 'html', use: { baseURL: 'http://localhost:3000', trace:
'on-first-retry', }, projects: [ { name: 'chromium', use: { ...devices['Desktop
Chrome'] } }, { name: 'firefox', use: { ...devices['Desktop Firefox'] } }, {
name: 'webkit', use: { ...devices['Desktop Safari'] } }, ], webServer: {
command: 'npm run dev', url: 'http://localhost:3000', reuseExistingServer:
!process.env.CI, }, });

### API統合テスト設定（pytest）

#### backend/pytest.ini

[tool:pytest] minversion = 6.0 addopts = -ra -q --strict-markers --cov=src
--cov-report=html --cov-report=term-missing:skip-covered --cov-fail-under=80
testpaths = tests python*files = test*_.py python_classes = Test_
python*functions = test*\*

### フロントエンドテスト設定（Jest）

#### frontend/jest.config.js

const nextJest = require('next/jest')

const createJestConfig = nextJest({ dir: './', })

const customJestConfig = { setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
moduleNameMapper: { '^@/(._)$': '<rootDir>/src/$1', }, testEnvironment:
'jest-environment-jsdom', collectCoverageFrom: [ 'src/\*\*/_.{js,jsx,ts,tsx}',
'!src/**/\*.d.ts', '!src/**/\*.stories.{js,jsx,ts,tsx}', ], coverageThreshold: {
global: { branches: 75, functions: 75, lines: 75, statements: 75 } } }

module.exports = createJestConfig(customJestConfig)

### Docker Composeテスト環境

#### docker-compose.test.yml

version: '3.8'

services: test-db: image: postgres:16-alpine environment: POSTGRES_DB: test_db
POSTGRES_USER: test_user POSTGRES_PASSWORD: test_pass healthcheck: test:
["CMD-SHELL", "pg_isready -U test_user"] interval: 5s timeout: 5s retries: 5

test-redis: image: redis:7-alpine healthcheck: test: ["CMD", "redis-cli",
"ping"] interval: 5s timeout: 5s retries: 5

test-backend: build: ./backend environment: DATABASE_URL:
postgresql://test_user:test_pass@test-db:5432/test_db REDIS_URL:
redis://test-redis:6379 TESTING: "true" depends_on: test-db: condition:
service_healthy test-redis: condition: service_healthy volumes: - ./backend:/app
command: pytest

test-frontend: build: ./frontend environment: NEXT_PUBLIC_API_URL:
http://test-backend:8000 volumes: - ./frontend:/app command: npm run test:ci

### Makefile統合

#### Makefile

.PHONY: test test-unit test-integration test-e2e test-all

test-env-up: docker-compose -f docker-compose.test.yml up -d

test-env-down: docker-compose -f docker-compose.test.yml down -v

test-unit: cd backend && pytest tests/unit --cov=src cd frontend && npm run
test:unit

test-integration: docker-compose -f docker-compose.test.yml run --rm
test-backend docker-compose -f docker-compose.test.yml run --rm test-frontend

test-e2e: npx playwright test

test-all: test-env-up test-unit test-integration test-e2e test-env-down

test-coverage: cd backend && pytest --cov=src --cov-report=html cd frontend &&
npm run test:coverage @echo "Backend coverage: htmlcov/index.html" @echo
"Frontend coverage: coverage/index.html"

## 期待される成果物

- 完全なテスト環境
- 80%+のコードカバレッジ
- E2E/API/UI統合テスト
- Docker Composeテスト環境
- CI統合可能な設定
```

### **検証方法**

```bash
# テスト環境起動
make test-env-up

# 全テスト実行
make test-all

# カバレッジ確認
make test-coverage

# E2E テストのみ
npx playwright test --headed
```

---

## 🔧 **Step 6.2: CI/CDパイプライン構築**

### **コマンド**

```bash
/ai:operations:deploy ci-cd --github-actions --cloudflare --multi-stage
```

### **AI への詳細指示**

````markdown
# ベクトルデータベース構築指示

## 実行内容

libSQL Vector を使用した1536次元ベクトルデータベースとHNSWインデックスの構築

## 具体的な作業項目

### 1. libSQL Vector設定

```sql
-- backend/migrations/001_create_vector_tables.sql
-- libSQL Vector 拡張の有効化
PRAGMA vector_enable = 1;

-- プロンプト埋め込みテーブル
CREATE TABLE prompt_embeddings (
    id TEXT PRIMARY KEY,
    prompt_id TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    model_name TEXT NOT NULL DEFAULT 'text-embedding-ada-002',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- HNSWインデックス作成
CREATE INDEX prompt_embeddings_hnsw_idx ON prompt_embeddings(embedding)
USING HNSW
WITH (
    m = 16,
    ef_construction = 200,
    ef_search = 50
);

-- メタデータ検索用インデックス
CREATE INDEX prompt_embeddings_prompt_id_idx ON prompt_embeddings(prompt_id);
CREATE INDEX prompt_embeddings_model_idx ON prompt_embeddings(model_name);
```
````

### 2. 埋め込み生成サービス

```python
# backend/src/infrastructure/embeddings/embedding_service.py
from typing import List, Dict, Any
import asyncio
import numpy as np
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

class EmbeddingService:
    def __init__(self, openai_client: AsyncOpenAI, session: AsyncSession):
        self._client = openai_client
        self._session = session
        self._model = "text-embedding-ada-002"
        self._dimension = 1536

    async def generate_embedding(self, text: str) -> List[float]:
        """単一テキストの埋め込み生成"""
        try:
            response = await self._client.embeddings.create(
                input=text,
                model=self._model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """バッチ埋め込み生成"""
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = await self._client.embeddings.create(
                    input=batch,
                    model=self._model
                )

                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)

                # API制限を考慮した待機
                if len(batch) == batch_size:
                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Failed to generate batch embeddings: {e}")
                # 個別処理にフォールバック
                for text in batch:
                    try:
                        embedding = await self.generate_embedding(text)
                        embeddings.append(embedding)
                    except:
                        embeddings.append([0.0] * self._dimension)

        return embeddings

    async def save_embedding(
        self,
        prompt_id: str,
        text: str,
        embedding: List[float]
    ) -> None:
        """埋め込みをデータベースに保存"""
        await self._session.execute(
            text("""
                INSERT INTO prompt_embeddings
                (id, prompt_id, embedding, model_name)
                VALUES (?, ?, ?, ?)
            """),
            (
                str(uuid4()),
                prompt_id,
                np.array(embedding).tobytes(),
                self._model
            )
        )
        await self._session.commit()
```

### 3. ベクトル検索実装

```python
# backend/src/infrastructure/search/vector_search.py
from typing import List, Tuple, Dict, Optional
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ...domain.search.value_objects import SearchResult, SimilarityScore

class VectorSearchService:
    def __init__(self, session: AsyncSession, embedding_service: EmbeddingService):
        self._session = session
        self._embedding_service = embedding_service

    async def similarity_search(
        self,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """類似度検索実行"""

        # クエリ埋め込み生成
        query_embedding = await self._embedding_service.generate_embedding(query)

        # フィルター条件構築
        filter_clause = ""
        filter_params = []

        if filters:
            conditions = []
            if "user_id" in filters:
                conditions.append("p.user_id = ?")
                filter_params.append(filters["user_id"])
            if "tags" in filters:
                conditions.append("EXISTS (SELECT 1 FROM prompt_tags pt WHERE pt.prompt_id = p.id AND pt.tag IN ?)")
                filter_params.append(tuple(filters["tags"]))

            if conditions:
                filter_clause = "AND " + " AND ".join(conditions)

        # ベクトル類似度検索
        query_sql = f"""
            SELECT
                p.id,
                p.title,
                p.content,
                p.user_id,
                p.created_at,
                pe.embedding <-> ? as similarity_score
            FROM prompt_embeddings pe
            JOIN prompts p ON pe.prompt_id = p.id
            WHERE pe.embedding <-> ? < ?
            {filter_clause}
            ORDER BY similarity_score ASC
            LIMIT ?
        """

        params = [
            np.array(query_embedding).tobytes(),
            np.array(query_embedding).tobytes(),
            1.0 - min_similarity,  # 距離を類似度に変換
            *filter_params,
            limit
        ]

        result = await self._session.execute(text(query_sql), params)
        rows = result.fetchall()

        search_results = []
        for row in rows:
            similarity = 1.0 - row.similarity_score  # 距離を類似度に戻す

            search_results.append(SearchResult(
                prompt_id=row.id,
                title=row.title,
                content=row.content[:200] + "..." if len(row.content) > 200 else row.content,
                user_id=row.user_id,
                similarity_score=SimilarityScore(similarity),
                created_at=row.created_at
            ))

        return search_results

    async def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        vector_weight: float = 0.7,
        text_weight: float = 0.3,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """ハイブリッド検索（ベクトル + テキスト）"""

        # 並列でベクトル検索とテキスト検索を実行
        vector_results, text_results = await asyncio.gather(
            self.similarity_search(query, limit * 2, filters=filters),
            self._text_search(query, limit * 2, filters=filters)
        )

        # スコア正規化と統合
        combined_scores = {}

        # ベクトル検索結果
        for i, result in enumerate(vector_results):
            score = (1 - i / len(vector_results)) * vector_weight
            combined_scores[result.prompt_id] = {
                'result': result,
                'score': score,
                'vector_score': result.similarity_score.value
            }

        # テキスト検索結果
        for i, result in enumerate(text_results):
            score = (1 - i / len(text_results)) * text_weight
            if result.prompt_id in combined_scores:
                combined_scores[result.prompt_id]['score'] += score
            else:
                combined_scores[result.prompt_id] = {
                    'result': result,
                    'score': score,
                    'vector_score': 0.0
                }

        # スコア順でソート
        sorted_results = sorted(
            combined_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        return [item['result'] for item in sorted_results[:limit]]
```

### 4. インデックス最適化

```python
# backend/src/infrastructure/search/index_optimizer.py
from typing import Dict, Any
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

class IndexOptimizer:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def optimize_hnsw_index(self, table_name: str = "prompt_embeddings") -> Dict[str, Any]:
        """HNSWインデックスの最適化"""

        # 現在のインデックス統計取得
        stats_before = await self._get_index_stats(table_name)

        # インデックス再構築
        await self._session.execute(text(f"""
            REINDEX prompt_embeddings_hnsw_idx
        """))

        # 最適化後の統計取得
        stats_after = await self._get_index_stats(table_name)

        # VACUUM実行（ストレージ最適化）
        await self._session.execute(text("VACUUM"))

        await self._session.commit()

        return {
            "before": stats_before,
            "after": stats_after,
            "improvement": {
                "size_reduction": stats_before["size"] - stats_after["size"],
                "search_time_improvement": stats_before["avg_search_time"] - stats_after["avg_search_time"]
            }
        }

    async def _get_index_stats(self, table_name: str) -> Dict[str, Any]:
        """インデックス統計情報取得"""
        result = await self._session.execute(text(f"""
            SELECT
                COUNT(*) as record_count,
                AVG(LENGTH(embedding)) as avg_embedding_size
            FROM {table_name}
        """))

        row = result.fetchone()

        return {
            "record_count": row.record_count,
            "avg_embedding_size": row.avg_embedding_size,
            "size": row.record_count * row.avg_embedding_size,
            "avg_search_time": 0.0  # 実測値で更新
        }
```

## 期待される成果物

- libSQL Vector 完全設定
- 1536次元埋め込みシステム
- HNSW高速検索インデックス
- ハイブリッド検索機能
- インデックス最適化機能

````

### **検証方法**
```bash
# ベクトルDB接続確認
python -c "
import sqlite3
conn = sqlite3.connect('autoforge.db')
cursor = conn.cursor()
cursor.execute('PRAGMA vector_enable')
result = cursor.fetchone()
print(f'Vector enabled: {result[0]}')
"

# 埋め込み生成テスト
cd backend
python -c "
import asyncio
from src.infrastructure.embeddings.embedding_service import EmbeddingService

async def test():
    service = EmbeddingService(openai_client, session)
    embedding = await service.generate_embedding('Test prompt')
    print(f'Embedding dimension: {len(embedding)}')

asyncio.run(test())
"

# 検索テスト
python -c "
import asyncio
from src.infrastructure.search.vector_search import VectorSearchService

async def test():
    search = VectorSearchService(session, embedding_service)
    results = await search.similarity_search('machine learning prompt', limit=5)
    print(f'Found {len(results)} similar prompts')

asyncio.run(test())
"
````

---

## 🔧 **Step 4.2: データ管理基盤**

### **コマンド**

```bash
/ai:development:implement data-layer --tdd --coverage 85
```

### **AI への詳細指示**

````markdown
# データ管理基盤構築指示

## 実行内容

85%カバレッジを目標とするデータ管理層の完全実装

## 具体的な作業項目

### 1. データベースモデル定義

```python
# backend/src/infrastructure/models/prompt_models.py
from sqlalchemy import Column, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
from datetime import datetime

Base = declarative_base()

class PromptModel(Base):
    __tablename__ = "prompts"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    quality_score = Column(Float)

    # リレーション
    versions = relationship("PromptVersionModel", back_populates="prompt")
    embeddings = relationship("PromptEmbeddingModel", back_populates="prompt")
    evaluations = relationship("EvaluationModel", back_populates="prompt")

    def to_entity(self) -> 'Prompt':
        from ...domain.prompt.entities import Prompt
        from ...domain.prompt.value_objects import PromptContent

        return Prompt(
            id=UUID(self.id),
            user_id=UUID(self.user_id),
            content=PromptContent(self.content),
            title=self.title,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_entity(cls, prompt: 'Prompt') -> 'PromptModel':
        return cls(
            id=str(prompt.id),
            user_id=str(prompt.user_id),
            title=prompt.title,
            content=prompt.content.value,
            description=prompt.description,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at
        )

class PromptEmbeddingModel(Base):
    __tablename__ = "prompt_embeddings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    prompt_id = Column(String, ForeignKey("prompts.id"), nullable=False)
    embedding = Column(BLOB, nullable=False)  # Vector stored as blob
    model_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    prompt = relationship("PromptModel", back_populates="embeddings")
```
````

### 2. リポジトリ実装

```python
# backend/src/infrastructure/repositories/prompt_repository.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from ...domain.prompt.entities import Prompt
from ...domain.prompt.repositories import PromptRepository
from ...domain.search.specifications import PromptSearchSpec
from ..models.prompt_models import PromptModel

class SQLAlchemyPromptRepository(PromptRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, prompt: Prompt) -> None:
        existing = await self._session.execute(
            select(PromptModel).where(PromptModel.id == str(prompt.id))
        )
        existing_model = existing.scalar_one_or_none()

        if existing_model:
            # 更新
            existing_model.title = prompt.title
            existing_model.content = prompt.content.value
            existing_model.description = prompt.description
            existing_model.updated_at = prompt.updated_at
        else:
            # 新規作成
            model = PromptModel.from_entity(prompt)
            self._session.add(model)

        await self._session.commit()

    async def get_by_id(self, prompt_id: UUID) -> Optional[Prompt]:
        result = await self._session.execute(
            select(PromptModel)
            .options(selectinload(PromptModel.versions))
            .where(PromptModel.id == str(prompt_id))
        )
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_user_id(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Prompt]:
        result = await self._session.execute(
            select(PromptModel)
            .where(PromptModel.user_id == str(user_id))
            .where(PromptModel.archived == False)
            .order_by(PromptModel.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [model.to_entity() for model in result.scalars()]

    async def search(self, spec: PromptSearchSpec) -> List[Prompt]:
        query = select(PromptModel).where(PromptModel.archived == False)

        # 仕様パターンによるフィルタリング
        if spec.user_id:
            query = query.where(PromptModel.user_id == str(spec.user_id))

        if spec.title_contains:
            query = query.where(
                PromptModel.title.ilike(f"%{spec.title_contains}%")
            )

        if spec.content_contains:
            query = query.where(
                PromptModel.content.ilike(f"%{spec.content_contains}%")
            )

        if spec.published is not None:
            query = query.where(PromptModel.published == spec.published)

        if spec.quality_min:
            query = query.where(PromptModel.quality_score >= spec.quality_min)

        # 並び順
        if spec.order_by == "created_at":
            query = query.order_by(PromptModel.created_at.desc())
        elif spec.order_by == "quality":
            query = query.order_by(PromptModel.quality_score.desc())
        else:
            query = query.order_by(PromptModel.updated_at.desc())

        query = query.limit(spec.limit).offset(spec.offset)

        result = await self._session.execute(query)
        return [model.to_entity() for model in result.scalars()]

    async def delete(self, prompt_id: UUID) -> None:
        await self._session.execute(
            select(PromptModel).where(PromptModel.id == str(prompt_id))
        )
        # ソフトデリート
        model = await self.get_by_id(prompt_id)
        if model:
            await self._session.execute(
                update(PromptModel)
                .where(PromptModel.id == str(prompt_id))
                .values(archived=True)
            )
            await self._session.commit()
```

### 3. データ整合性管理

```python
# backend/src/infrastructure/data/consistency_manager.py
from typing import List, Dict, Any
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
import logging

logger = logging.getLogger(__name__)

class DataConsistencyManager:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def check_referential_integrity(self) -> Dict[str, Any]:
        """参照整合性チェック"""
        issues = []

        # 孤立したプロンプト埋め込みチェック
        result = await self._session.execute(text("""
            SELECT pe.id, pe.prompt_id
            FROM prompt_embeddings pe
            LEFT JOIN prompts p ON pe.prompt_id = p.id
            WHERE p.id IS NULL
        """))

        orphaned_embeddings = result.fetchall()
        if orphaned_embeddings:
            issues.append({
                "type": "orphaned_embeddings",
                "count": len(orphaned_embeddings),
                "items": [{"id": row.id, "prompt_id": row.prompt_id} for row in orphaned_embeddings]
            })

        # 埋め込みがないプロンプトチェック
        result = await self._session.execute(text("""
            SELECT p.id, p.title
            FROM prompts p
            LEFT JOIN prompt_embeddings pe ON p.id = pe.prompt_id
            WHERE pe.prompt_id IS NULL
            AND p.archived = FALSE
        """))

        prompts_without_embeddings = result.fetchall()
        if prompts_without_embeddings:
            issues.append({
                "type": "prompts_without_embeddings",
                "count": len(prompts_without_embeddings),
                "items": [{"id": row.id, "title": row.title} for row in prompts_without_embeddings]
            })

        return {
            "status": "healthy" if not issues else "issues_found",
            "issues": issues,
            "checked_at": datetime.utcnow()
        }

    async def repair_data_consistency(self) -> Dict[str, Any]:
        """データ整合性の修復"""
        repair_log = []

        # 孤立した埋め込みを削除
        result = await self._session.execute(text("""
            DELETE FROM prompt_embeddings
            WHERE prompt_id NOT IN (SELECT id FROM prompts)
        """))
        if result.rowcount > 0:
            repair_log.append(f"Deleted {result.rowcount} orphaned embeddings")

        # 埋め込みがないプロンプトの埋め込み生成をキューに追加
        result = await self._session.execute(text("""
            SELECT id, content
            FROM prompts
            WHERE id NOT IN (SELECT DISTINCT prompt_id FROM prompt_embeddings)
            AND archived = FALSE
        """))

        prompts_to_embed = result.fetchall()
        if prompts_to_embed:
            # 埋め込み生成タスクをキューに追加
            for row in prompts_to_embed:
                await self._add_embedding_task(row.id, row.content)

            repair_log.append(f"Queued {len(prompts_to_embed)} prompts for embedding generation")

        await self._session.commit()

        return {
            "repairs_completed": len(repair_log),
            "repair_log": repair_log,
            "repaired_at": datetime.utcnow()
        }

    async def _add_embedding_task(self, prompt_id: str, content: str) -> None:
        """埋め込み生成タスクをキューに追加"""
        # Redis Queueまたは同等のタスクキューに追加
        pass
```

### 4. データマイグレーション

```python
# backend/src/infrastructure/migrations/migration_manager.py
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class MigrationManager:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._migrations = [
            self._migration_001_initial_schema,
            self._migration_002_add_embeddings,
            self._migration_003_add_evaluations,
            self._migration_004_optimize_indexes
        ]

    async def run_migrations(self) -> Dict[str, Any]:
        """マイグレーション実行"""
        results = []

        # 現在のマイグレーションバージョン取得
        current_version = await self._get_current_version()

        for i, migration in enumerate(self._migrations):
            migration_version = i + 1

            if migration_version <= current_version:
                continue

            try:
                logger.info(f"Running migration {migration_version}")
                await migration()
                await self._set_version(migration_version)
                results.append({
                    "version": migration_version,
                    "status": "success",
                    "name": migration.__name__
                })
                logger.info(f"Migration {migration_version} completed")

            except Exception as e:
                logger.error(f"Migration {migration_version} failed: {e}")
                results.append({
                    "version": migration_version,
                    "status": "failed",
                    "name": migration.__name__,
                    "error": str(e)
                })
                break

        return {
            "migrations_run": len([r for r in results if r["status"] == "success"]),
            "results": results,
            "current_version": await self._get_current_version()
        }

    async def _migration_001_initial_schema(self) -> None:
        """初期スキーマ作成"""
        await self._session.execute(text("""
            CREATE TABLE IF NOT EXISTS prompts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published BOOLEAN DEFAULT FALSE,
                archived BOOLEAN DEFAULT FALSE,
                quality_score REAL
            )
        """))

        await self._session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_prompts_user_id ON prompts(user_id)
        """))

        await self._session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_prompts_created_at ON prompts(created_at DESC)
        """))

    async def _migration_002_add_embeddings(self) -> None:
        """埋め込みテーブル追加"""
        # libSQL Vector拡張を有効化
        await self._session.execute(text("PRAGMA vector_enable = 1"))

        await self._session.execute(text("""
            CREATE TABLE IF NOT EXISTS prompt_embeddings (
                id TEXT PRIMARY KEY,
                prompt_id TEXT NOT NULL,
                embedding VECTOR(1536) NOT NULL,
                model_name TEXT NOT NULL DEFAULT 'text-embedding-ada-002',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prompt_id) REFERENCES prompts(id)
            )
        """))

        await self._session.execute(text("""
            CREATE INDEX IF NOT EXISTS prompt_embeddings_hnsw_idx
            ON prompt_embeddings(embedding)
            USING HNSW
            WITH (m = 16, ef_construction = 200, ef_search = 50)
        """))

    async def _get_current_version(self) -> int:
        """現在のマイグレーションバージョン取得"""
        try:
            result = await self._session.execute(text("""
                SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1
            """))
            row = result.fetchone()
            return row.version if row else 0
        except:
            # テーブルが存在しない場合
            await self._session.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            return 0
```

## 期待される成果物

- 完全なデータ管理基盤
- 85%以上のテストカバレッジ
- データ整合性管理システム
- 自動マイグレーション機能
- 高性能なリポジトリパターン実装

````

### **検証方法**
```bash
# データ層テスト
cd backend
pytest src/tests/infrastructure/repositories/ --cov=src.infrastructure --cov-report=html

# マイグレーション実行
python -c "
import asyncio
from src.infrastructure.migrations.migration_manager import MigrationManager

async def test():
    manager = MigrationManager(session)
    result = await manager.run_migrations()
    print(f'Migrations completed: {result}')

asyncio.run(test())
"

# データ整合性チェック
python -c "
import asyncio
from src.infrastructure.data.consistency_manager import DataConsistencyManager

async def test():
    manager = DataConsistencyManager(session)
    result = await manager.check_referential_integrity()
    print(f'Consistency status: {result[\"status\"]}')

asyncio.run(test())
"
````

---

<function_calls> <invoke name="TodoWrite"> <parameter name="todos">[{"content":
"環境構築完全ガイドの構造設計と基本テンプレート作成", "status": "completed",
"activeForm": "環境構築ガイド構造設計完了"}, {"content": "Phase 1:
Git・基盤環境構築の詳細手順書作成", "status": "completed", "activeForm":
"Git基盤環境手順書作成完了"}, {"content": "Phase 2:
インフラ・DevOps環境構築の詳細手順書作成", "status": "completed", "activeForm":
"インフラDevOps手順書作成完了"}, {"content": "Phase 3:
バックエンド環境構築の詳細手順書作成", "status": "in_progress", "activeForm":
"バックエンド環境手順書作成中"}, {"content": "Phase 4:
データベース・ベクトル環境の詳細手順書作成", "status": "pending", "activeForm":
"データベース環境手順書作成待ち"}, {"content": "Phase 5:
フロントエンド環境構築の詳細手順書作成", "status": "pending", "activeForm":
"フロントエンド環境手順書作成待ち"}, {"content": "Phase 6:
統合・品質保証の詳細手順書作成", "status": "pending", "activeForm":
"統合品質保証手順書作成待ち"}, {"content": "トラブルシューティングガイドと
FAQ作成", "status": "pending", "activeForm":
"トラブルシューティングガイド作成待ち"}]
