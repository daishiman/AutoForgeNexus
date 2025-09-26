# AutoForgeNexus 最適化CI/CDワークフロー設定

## 🎯 最適化方針

### DevOps原則
- **自動化可能なものはすべて自動化**
- **システム信頼性、監視性、迅速な復旧の観点で設計**
- **すべてのプロセスは再現可能で、監査可能**
- **障害シナリオに対応した自動検出と復旧機能**

## ⚡ 最適化されたCI/CDワークフロー

### 1. 高性能並列CIワークフロー

```yaml
# .github/workflows/ci-optimized.yml
name: Optimized CI Pipeline

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

# 環境別設定
env:
  PYTHON_VERSION: '3.13'
  NODE_VERSION: '20'
  PNPM_VERSION: '8'

# 並列実行で最大効率化
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      backend: ${{ steps.changes.outputs.backend }}
      frontend: ${{ steps.changes.outputs.frontend }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            backend:
              - 'backend/**'
              - 'requirements*.txt'
              - 'pyproject.toml'
            frontend:
              - 'frontend/**'
              - 'package.json'
              - 'pnpm-lock.yaml'

  backend-ci:
    runs-on: ubuntu-latest
    needs: changes
    if: needs.changes.outputs.backend == 'true'
    strategy:
      matrix:
        task: [lint, type-check, test, security]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python with cache
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
          cache-dependency-path: |
            backend/requirements.txt
            backend/requirements-dev.txt

      - name: Install dependencies
        run: |
          cd backend
          pip install -e .[dev]
          pip install pytest-xdist pytest-cov bandit safety

      - name: Run linting
        if: matrix.task == 'lint'
        run: |
          cd backend
          ruff check src/ --output-format=github
          ruff format src/ --check

      - name: Run type checking
        if: matrix.task == 'type-check'
        run: |
          cd backend
          mypy src/ --strict

      - name: Run tests with coverage
        if: matrix.task == 'test'
        run: |
          cd backend
          pytest tests/ -n auto --cov=src --cov-report=xml --cov-fail-under=80

      - name: Run security checks
        if: matrix.task == 'security'
        run: |
          cd backend
          bandit -r src/
          safety check --json

      - name: Upload coverage
        if: matrix.task == 'test'
        uses: codecov/codecov-action@v3
        with:
          file: backend/coverage.xml
          flags: backend

  frontend-ci:
    runs-on: ubuntu-latest
    needs: changes
    if: needs.changes.outputs.frontend == 'true'
    strategy:
      matrix:
        task: [lint, type-check, test, build]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js with pnpm
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
          cache-dependency-path: frontend/pnpm-lock.yaml

      - name: Install pnpm
        run: corepack enable

      - name: Install dependencies
        run: |
          cd frontend
          pnpm install --frozen-lockfile

      - name: Run linting
        if: matrix.task == 'lint'
        run: |
          cd frontend
          pnpm lint --max-warnings 0

      - name: Run type checking
        if: matrix.task == 'type-check'
        run: |
          cd frontend
          pnpm type-check

      - name: Run tests
        if: matrix.task == 'test'
        run: |
          cd frontend
          pnpm test --coverage --watchAll=false

      - name: Build application
        if: matrix.task == 'build'
        run: |
          cd frontend
          pnpm build

      - name: Upload build artifacts
        if: matrix.task == 'build'
        uses: actions/upload-artifact@v3
        with:
          name: frontend-build
          path: frontend/.next/
          retention-days: 7

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  ci-gate:
    runs-on: ubuntu-latest
    needs: [backend-ci, frontend-ci, security-scan]
    if: always()
    steps:
      - name: Check CI status
        run: |
          if [[ "${{ needs.backend-ci.result }}" == "failure" || "${{ needs.frontend-ci.result }}" == "failure" || "${{ needs.security-scan.result }}" == "failure" ]]; then
            echo "CI pipeline failed"
            exit 1
          fi
          echo "CI pipeline passed successfully"
```

### 2. Cloudflare最適化デプロイワークフロー

```yaml
# .github/workflows/cd-cloudflare.yml
name: Cloudflare Deployment

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

env:
  CF_API_TOKEN: ${{ secrets.CF_API_TOKEN }}
  CF_ACCOUNT_ID: ${{ secrets.CF_ACCOUNT_ID }}

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    environment:
      name: ${{ github.event.inputs.environment || 'production' }}
      url: ${{ steps.deploy.outputs.url }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Build backend for Workers
        run: |
          cd backend
          pip install -e .
          # Cloudflare Workers Python 最適化ビルド
          python scripts/build_for_workers.py

      - name: Deploy to Cloudflare Workers
        id: deploy
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ env.CF_API_TOKEN }}
          accountId: ${{ env.CF_ACCOUNT_ID }}
          command: deploy --env ${{ github.event.inputs.environment || 'production' }}
          workingDirectory: backend

      - name: Run smoke tests
        run: |
          curl -f ${{ steps.deploy.outputs.url }}/health || exit 1

  deploy-frontend:
    runs-on: ubuntu-latest
    environment:
      name: ${{ github.event.inputs.environment || 'production' }}
      url: ${{ steps.deploy.outputs.url }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js with pnpm
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
          cache-dependency-path: frontend/pnpm-lock.yaml

      - name: Install pnpm
        run: corepack enable

      - name: Install and build
        run: |
          cd frontend
          pnpm install --frozen-lockfile
          pnpm build

      - name: Deploy to Cloudflare Pages
        id: deploy
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ env.CF_API_TOKEN }}
          accountId: ${{ env.CF_ACCOUNT_ID }}
          projectName: autoforge-nexus
          directory: frontend/.next
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}

      - name: Run E2E tests
        run: |
          cd frontend
          pnpm playwright test --base-url ${{ steps.deploy.outputs.url }}

  deploy-monitoring:
    runs-on: ubuntu-latest
    needs: [deploy-backend, deploy-frontend]
    if: success()
    steps:
      - name: Setup monitoring
        run: |
          # Cloudflare Analytics, Web Analytics設定
          curl -X POST "https://api.cloudflare.com/client/v4/zones/${{ secrets.CF_ZONE_ID }}/analytics/dashboard" \
            -H "Authorization: Bearer ${{ env.CF_API_TOKEN }}" \
            -H "Content-Type: application/json"

      - name: Health check notification
        uses: 8398a7/action-slack@v3
        if: always()
        with:
          status: ${{ job.status }}
          text: "Deployment to ${{ github.event.inputs.environment || 'production' }} completed"
```

### 3. 高度なセキュリティワークフロー

```yaml
# .github/workflows/security-advanced.yml
name: Advanced Security Scanning

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1'  # 毎週月曜日 AM 2:00

jobs:
  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run TruffleHog
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --debug --only-verified

  dependency-scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        ecosystem: [python, javascript]
    steps:
      - uses: actions/checkout@v4

      - name: Python dependency scan
        if: matrix.ecosystem == 'python'
        run: |
          pip install safety
          cd backend && safety check --json --output safety-report.json

      - name: JavaScript dependency scan
        if: matrix.ecosystem == 'javascript'
        run: |
          cd frontend
          pnpm audit --audit-level high
          npx audit-ci --config audit-ci.json

  sast-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: python, javascript
          queries: security-and-quality

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2

  infrastructure-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: github_actions,dockerfile,secrets
```

## 📊 監視・観測性の実装

### 1. メトリクス収集設定

```yaml
# .github/workflows/metrics.yml
name: DevOps Metrics

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  collect-metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Calculate metrics
        run: |
          # DORA メトリクス計算
          echo "DEPLOYMENT_FREQUENCY=$(git log --since='1 week ago' --grep='deploy' --oneline | wc -l)" >> $GITHUB_ENV
          echo "LEAD_TIME=$(git log --since='1 week ago' --pretty=format:'%ct' | head -1)" >> $GITHUB_ENV
          echo "MTTR=$(curl -s https://api.github.com/repos/${{ github.repository }}/issues?labels=incident | jq '.[0].closed_at')" >> $GITHUB_ENV

      - name: Send metrics to monitoring
        run: |
          curl -X POST ${{ secrets.METRICS_WEBHOOK_URL }} \
            -H "Content-Type: application/json" \
            -d '{
              "deployment_frequency": "${{ env.DEPLOYMENT_FREQUENCY }}",
              "lead_time": "${{ env.LEAD_TIME }}",
              "mttr": "${{ env.MTTR }}"
            }'
```

### 2. アラート設定

```yaml
# .github/workflows/alerts.yml
name: Automated Alerts

on:
  workflow_run:
    workflows: ["Optimized CI Pipeline", "Cloudflare Deployment"]
    types: [completed]

jobs:
  alert-on-failure:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    steps:
      - name: Send failure alert
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
          text: |
            🚨 Workflow failed: ${{ github.event.workflow_run.name }}
            Repository: ${{ github.repository }}
            Branch: ${{ github.event.workflow_run.head_branch }}
            Commit: ${{ github.event.workflow_run.head_sha }}

  performance-alert:
    runs-on: ubuntu-latest
    steps:
      - name: Check build time
        run: |
          BUILD_TIME=$(curl -s https://api.github.com/repos/${{ github.repository }}/actions/runs/${{ github.event.workflow_run.id }} | jq '.run_time_ms')
          if [ $BUILD_TIME -gt 600000 ]; then  # 10分超
            echo "::warning::Build time exceeded 10 minutes"
          fi
```

## 🔧 インフラ設定の最適化

### 1. 環境管理最適化

```bash
# scripts/setup-development-env.sh
#!/bin/bash
set -euo pipefail

echo "🚀 AutoForgeNexus 開発環境セットアップ開始"

# 必須ツールのバージョン確認と自動インストール
check_and_install() {
    local tool=$1
    local version=$2
    local install_cmd=$3

    if ! command -v $tool &> /dev/null; then
        echo "⚠️ $tool not found. Installing..."
        eval $install_cmd
    else
        echo "✅ $tool $(${tool} --version) detected"
    fi
}

# 開発ツールチェーン確認
check_and_install "git" "2.40" "brew install git"
check_and_install "python3.13" "3.13" "pyenv install 3.13.0"
check_and_install "node" "20" "nvm install 20"
check_and_install "pnpm" "8" "corepack enable"
check_and_install "docker" "24" "brew install docker"

# 仮想環境セットアップ
echo "📦 Python仮想環境セットアップ"
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# フロントエンド依存関係インストール
echo "🌐 フロントエンド依存関係インストール"
cd ../frontend
pnpm install

# Git設定適用
echo "🔧 Git設定適用"
cd ..
git config --local commit.template .gitmessage
git config --local init.defaultBranch main

echo "✅ 開発環境セットアップ完了"
```

### 2. Docker最適化設定

```dockerfile
# Dockerfile.optimized
# マルチステージビルドで最適化
FROM python:3.13-slim as backend-builder
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM node:20-alpine as frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY frontend/ .
RUN pnpm build

# 本番イメージ
FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=backend-builder /app/backend /app/backend
COPY --from=frontend-builder /app/frontend/.next /app/frontend/.next

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "-m", "backend.main"]
```

### 3. 運用効率化スクリプト

```bash
# scripts/deployment-rollback.sh
#!/bin/bash
# ゼロダウンタイムロールバック機能

ENVIRONMENT=${1:-staging}
PREVIOUS_VERSION=${2:-HEAD~1}

echo "🔄 Rolling back to $PREVIOUS_VERSION in $ENVIRONMENT"

# 現在のバージョンをバックアップ
CURRENT_VERSION=$(git rev-parse HEAD)

# 以前のバージョンをデプロイ
git checkout $PREVIOUS_VERSION

# Cloudflare Workers デプロイ
wrangler deploy --env $ENVIRONMENT

# ヘルスチェック
HEALTH_CHECK_URL="https://api-$ENVIRONMENT.autoforge.com/health"
if curl -f $HEALTH_CHECK_URL; then
    echo "✅ Rollback successful"
else
    echo "❌ Rollback failed, reverting to $CURRENT_VERSION"
    git checkout $CURRENT_VERSION
    wrangler deploy --env $ENVIRONMENT
    exit 1
fi
```

## 📈 パフォーマンス最適化指標

### CI/CD効率化目標
- **ビルド時間**: <5分 (現状予想: 10-15分)
- **並列化率**: 80%以上のタスク並列実行
- **キャッシュ効率**: 依存関係インストール時間70%削減
- **デプロイ時間**: <2分 (Cloudflare Workers/Pages)

### 品質保証強化
- **テストカバレッジ**: 80%以上強制
- **セキュリティスキャン**: 100%自動化
- **依存関係脆弱性**: ゼロ許容（高/重要レベル）
- **パフォーマンス監視**: Core Web Vitals追跡

### 運用効率向上
- **MTTR**: <30分（平均復旧時間）
- **デプロイ頻度**: 日次以上
- **失敗率**: <5%（CI/CDパイプライン）
- **自動化率**: 90%以上の手動作業削減

この最適化により、個人開発でもエンタープライズレベルの信頼性と効率性を実現できます。