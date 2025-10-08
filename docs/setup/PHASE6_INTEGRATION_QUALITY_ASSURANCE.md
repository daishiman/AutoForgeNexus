# Phase 6: 統合・品質保証 - 環境構築詳細ガイド

## 📋 概要

AutoForgeNexus プロジェクトの Phase
6 は、エンタープライズレベルの品質保証環境を構築する最終フェーズです。統合テスト、CI/CD、監視、セキュリティ、パフォーマンステストの完全な環境を整備します。

---

## 🔧 Step 6.1: 統合テスト環境セットアップ

### コマンド

```bash
/ai:quality:tdd test-env --playwright --pytest --jest --coverage 80 --docker
```

### **起動エージェント**

Phase 6 Step 6.1 で起動されるべきエージェント：

- **qa-coordinator Agent**
  (リーダー): 統合テスト環境全体の設計と品質保証戦略の統括
- **test-automation-engineer
  Agent**: テストフレームワークのセットアップとテスト戦略の実装
- **backend-developer Agent**: API テスト環境とモックサービスの構築
- **frontend-architect Agent**: フロントエンド E2E テスト環境の構築
- **edge-database-administrator
  Agent**: テストデータベース環境とデータ管理の設定

### AI への詳細指示

````markdown
# 統合テスト環境構築指示

## 実行内容

Playwright, pytest, Jest を使用した包括的テスト環境の構築

## 具体的な作業項目

### E2E テストセットアップ (Playwright)

#### frontend/playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/e2e-results.json' }],
    ['junit', { outputFile: 'test-results/e2e-junit.xml' }],
  ],
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
```
````

### API テストセットアップ (pytest)

#### backend/tests/conftest.py

```python
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.redis import RedisContainer
from testcontainers.compose import DockerCompose

from src.main import app
from src.infrastructure.database import get_db
from src.domain.events import EventBus

@pytest.fixture(scope="session")
def event_loop():
    """セッション全体で使用するイベントループ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """テスト用データベース"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()

@pytest.fixture
async def db_session(test_db) -> AsyncGenerator[AsyncSession, None]:
    """データベースセッション"""
    async with AsyncSession(test_db) as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """テスト用HTTPクライアント"""
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(
        app=app,
        base_url="http://test",
        headers={"X-Test-Client": "true"}
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def redis():
    """テスト用Redisコンテナ"""
    with RedisContainer() as redis:
        yield redis.get_client()

@pytest.fixture(scope="session")
def docker_compose():
    """統合テスト用Docker Compose環境"""
    compose = DockerCompose(
        "../",
        compose_file_name="docker-compose.test.yml",
        pull=True,
    )
    compose.start()
    compose.wait_for("http://localhost:8000/health")
    yield compose
    compose.stop()
```

### フロントエンドユニットテスト (Jest)

#### frontend/jest.config.js

```javascript
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@/components/(.*)$': '<rootDir>/src/components/$1',
  },
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/**/_*.{js,jsx,ts,tsx}',
  ],
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{spec,test}.{js,jsx,ts,tsx}',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};

module.exports = createJestConfig(customJestConfig);
```

## 検証項目

1. ✅ Playwright でのマルチブラウザテスト実行
2. ✅ pytest での API テスト実行
3. ✅ Jest でのユニットテスト実行
4. ✅ カバレッジレポートの生成
5. ✅ Docker Compose での統合テスト環境起動

````

---

## 🔧 Step 6.2: CI/CDパイプライン構築（続き）

### コマンド

```bash
/ai:operations:deploy pipeline --github-actions --cloudflare --strategy canary --rollback auto
````

### **起動エージェント**

Phase 6 Step 6.2で起動されるべきエージェント：

- **devops-coordinator Agent** (リーダー): CI/CDパイプライン全体の設計と統括
- **test-automation-engineer Agent**: 自動テスト戦略とテストステップの設計
- **security-architect Agent**: セキュリティスキャンとセキュリティゲートの設定
- **version-control-specialist Agent**: ブランチ戦略とマージルールの設定
- **observability-engineer Agent**: CI/CDメトリクスと監視の設定

### AI への詳細指示

```markdown
# CI/CD パイプライン構築指示

## 実行内容

GitHub Actions + Cloudflare デプロイメントパイプラインの構築

## 具体的な作業項目

### GitHub Actions ワークフロー

#### .github/workflows/ci.yml

name: CI Pipeline

on: push: branches: [main, develop] pull_request: branches: [main, develop]

env: PYTHON_VERSION: '3.13' NODE_VERSION: '20' PNPM_VERSION: '8'

jobs: lint-backend: runs-on: ubuntu-latest steps: - uses: actions/checkout@v4 -
uses: actions/setup-python@v5 with: python-version: ${{ env.PYTHON_VERSION }} -
name: Install dependencies run: | cd backend pip install -e .[dev] - name: Run
ruff run: | cd backend ruff check src/ - name: Run mypy run: | cd backend mypy
src/ --strict

lint-frontend: runs-on: ubuntu-latest steps: - uses: actions/checkout@v4 - uses:
pnpm/action-setup@v2 with: version: ${{ env.PNPM_VERSION }} - uses:
actions/setup-node@v4 with: node-version: ${{ env.NODE_VERSION }} cache:
'pnpm' - name: Install dependencies run: | cd frontend pnpm install - name: Run
ESLint run: | cd frontend pnpm lint - name: Type check run: | cd frontend pnpm
type-check

test-backend: runs-on: ubuntu-latest needs: lint-backend steps: - uses:
actions/checkout@v4 - uses: actions/setup-python@v5 with: python-version:
${{ env.PYTHON_VERSION }} - name: Install dependencies run: | cd backend pip
install -e .[dev] - name: Run tests with coverage run: | cd backend pytest
--cov=src --cov-report=xml --cov-fail-under=80 - name: Upload coverage to
Codecov uses: codecov/codecov-action@v3 with: files: ./backend/coverage.xml
flags: backend

test-frontend: runs-on: ubuntu-latest needs: lint-frontend steps: - uses:
actions/checkout@v4 - uses: pnpm/action-setup@v2 with: version:
${{ env.PNPM_VERSION }} - uses: actions/setup-node@v4 with: node-version:
${{ env.NODE_VERSION }} cache: 'pnpm' - name: Install dependencies run: | cd
frontend pnpm install - name: Run tests with coverage run: | cd frontend pnpm
test:ci --coverage - name: Upload coverage to Codecov uses:
codecov/codecov-action@v3 with: files: ./frontend/coverage/lcov.info flags:
frontend

e2e-tests: runs-on: ubuntu-latest needs: [test-backend, test-frontend] steps: -
uses: actions/checkout@v4 - uses: pnpm/action-setup@v2 with: version:
${{ env.PNPM_VERSION }} - uses: actions/setup-node@v4 with: node-version:
${{ env.NODE_VERSION }} - name: Install Playwright run: npx playwright install
--with-deps - name: Run E2E tests run: npx playwright test - uses:
actions/upload-artifact@v3 if: always() with: name: playwright-report path:
playwright-report/ retention-days: 30

security-scan: runs-on: ubuntu-latest steps: - uses: actions/checkout@v4 - name:
Run Trivy vulnerability scanner uses: aquasecurity/trivy-action@master with:
scan-type: 'fs' scan-ref: '.' format: 'sarif' output: 'trivy-results.sarif' -
name: Upload Trivy results to GitHub Security uses:
github/codeql-action/upload-sarif@v2 with: sarif_file: 'trivy-results.sarif'

### デプロイメントワークフロー

#### .github/workflows/deploy.yml

name: Deploy to Cloudflare

on: push: branches: [main] workflow_dispatch:

jobs: deploy-backend: runs-on: ubuntu-latest if: github.ref == 'refs/heads/main'
steps: - uses: actions/checkout@v4 - name: Deploy to Cloudflare Workers uses:
cloudflare/wrangler-action@v3 with: apiToken:
${{ secrets.CLOUDFLARE_API_TOKEN }} workingDirectory: 'backend' command: deploy

deploy-frontend: runs-on: ubuntu-latest if: github.ref == 'refs/heads/main'
steps: - uses: actions/checkout@v4 - uses: pnpm/action-setup@v2 with: version:
8 - uses: actions/setup-node@v4 with: node-version: '20' cache: 'pnpm' - name:
Build frontend run: | cd frontend pnpm install pnpm build - name: Deploy to
Cloudflare Pages uses: cloudflare/pages-action@v1 with: apiToken:
${{ secrets.CLOUDFLARE_API_TOKEN }} accountId:
${{ secrets.CLOUDFLARE_ACCOUNT_ID }} projectName: 'autoforge-nexus' directory:
'frontend/out'

## 期待される成果物

- 完全な CI/CD パイプライン
- 自動テスト実行
- セキュリティスキャン
- Cloudflare 自動デプロイ
- コードカバレッジレポート
```

### 検証方法

```bash
# GitHub Actions確認
gh workflow list
gh workflow run ci.yml
gh run watch

# Cloudflare設定確認
wrangler whoami
wrangler pages project list
```

---

## 🔧 Step 6.3: 品質メトリクスとコードカバレッジ

### コマンド

```bash
/ai:quality:analyze metrics --coverage 80 --complexity 10 --sonarqube
```

### **起動エージェント**

Phase 6 Step 6.3 で起動されるべきエージェント：

- **quality-engineer Agent** (リーダー): 品質メトリクス戦略全体の設計と実装
- **performance-optimizer
  Agent**: パフォーマンスメトリクスとプロファイリングの設定
- **security-engineer Agent**: セキュリティメトリクスと脆弱性分析の設定
- **technical-documentation
  Agent**: メトリクスレポートとドキュメンテーションの自動生成
- **data-analyst Agent**: メトリクスデータの分析と洞察の提供

### AI への詳細指示

```markdown
# 品質メトリクス設定指示

## 実行内容

コードカバレッジ 80%+、循環複雑度 10 以下を目標とする品質管理体制の構築

## 具体的な作業項目

### SonarQube 設定

#### sonar-project.properties

sonar.projectKey=autoforge-nexus sonar.organization=autoforge
sonar.sources=backend/src,frontend/src sonar.tests=backend/tests,frontend/tests
sonar.python.coverage.reportPaths=backend/coverage.xml
sonar.javascript.lcov.reportPaths=frontend/coverage/lcov.info
sonar.python.version=3.13
sonar.exclusions=**/\*.test.ts,**/\*.spec.py,**/migrations/**

### 品質ゲート設定

#### .github/quality-gates.yml

quality_gates: coverage: backend: 80 frontend: 75 complexity: max_cyclomatic: 10
max_cognitive: 15 duplications: max_percentage: 3 security_hotspots: 0
code_smells: max_count: 10 max_debt: 1d

### pytest カバレッジ設定

#### backend/.coveragerc

[run] source = src omit = _/tests/_ _/migrations/_ _/**init**.py _/conftest.py

[report] precision = 2 show_missing = True skip_covered = True fail_under = 80

[html] directory = htmlcov

### Jest カバレッジ設定

#### frontend/jest.coverage.config.js

module.exports = { collectCoverage: true, collectCoverageFrom: [
'src/**/*.{ts,tsx}', '!src/**/*.d.ts', '!src/**/*.stories.tsx',
'!src/**/index.ts', ], coverageDirectory: 'coverage', coverageReporters:
['text', 'lcov', 'html'], coverageThreshold: { global: { branches: 75,
functions: 75, lines: 75, statements: 75, }, }, };

## 期待される成果物

- SonarQube 統合
- 品質ゲート設定
- カバレッジレポート自動生成
- 複雑度分析
- 技術的負債追跡
```

### 検証方法

```bash
# バックエンドカバレッジ
cd backend
pytest --cov=src --cov-report=html
open htmlcov/index.html

# フロントエンドカバレッジ
cd frontend
pnpm test:coverage
open coverage/index.html

# SonarQube分析
sonar-scanner
```

---

## 🔧 Step 6.4: 監視・ログ収集システム

### コマンド

```bash
/ai:operations:monitor observability --langfuse --prometheus --grafana --loki
```

### **起動エージェント**

Phase 6 Step 6.4 で起動されるべきエージェント：

- **observability-engineer Agent** (リーダー): 監視システム全体の設計と実装
- **sre-agent-agent Agent**: SLO/SLI 定義とアラート戦略の設計
- **performance-engineer Agent**: パフォーマンスモニタリングと APM 設定
- **llm-integration Agent**: LangFuse と LLM トレーシングの設定
- **edge-computing-specialist Agent**: Cloudflare Analytics とエッジ監視の設定

### AI への詳細指示

```markdown
# 監視システム構築指示

## 実行内容

LangFuse + Prometheus + Grafana + Loki による包括的監視体制の構築

## 具体的な作業項目

### Docker Compose 監視スタック

#### docker-compose.monitoring.yml

version: '3.8'

services: prometheus: image: prom/prometheus:latest volumes: -
./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml -
prometheus_data:/prometheus ports: - "9090:9090" command: -
'--config.file=/etc/prometheus/prometheus.yml' -
'--storage.tsdb.path=/prometheus'

grafana: image: grafana/grafana:latest volumes: -
grafana_data:/var/lib/grafana -
./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards -
./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
environment: - GF_SECURITY_ADMIN_PASSWORD=admin -
GF_INSTALL_PLUGINS=grafana-piechart-panel ports: - "3001:3000"

loki: image: grafana/loki:latest ports: - "3100:3100" volumes: -
./monitoring/loki-config.yaml:/etc/loki/local-config.yaml - loki_data:/loki

promtail: image: grafana/promtail:latest volumes: -
./monitoring/promtail-config.yaml:/etc/promtail/config.yml - /var/log:/var/log
command: -config.file=/etc/promtail/config.yml

langfuse: image: langfuse/langfuse:latest environment: -
DATABASE_URL=postgresql://langfuse:password@postgres:5432/langfuse -
NEXTAUTH_SECRET=${{ secrets.NEXTAUTH_SECRET }}
      - SALT=${{ secrets.SALT }} ports: - "3002:3000" depends_on: - postgres

postgres: image: postgres:16 environment: - POSTGRES_DB=langfuse -
POSTGRES_USER=langfuse - POSTGRES_PASSWORD=password volumes: -
postgres_data:/var/lib/postgresql/data

volumes: prometheus_data: grafana_data: loki_data: postgres_data:

### Prometheus 設定

#### monitoring/prometheus.yml

global: scrape_interval: 15s evaluation_interval: 15s

scrape_configs:

- job_name: 'backend' static_configs:

  - targets: ['backend:8000'] metrics_path: '/metrics'

- job_name: 'frontend' static_configs:

  - targets: ['frontend:3000'] metrics_path: '/api/metrics'

- job_name: 'node-exporter' static_configs:
  - targets: ['node-exporter:9100']

### LangFuse 統合

#### backend/src/infrastructure/langfuse_config.py

from langfuse import Langfuse from langfuse.decorators import observe import os

langfuse = Langfuse( public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
secret_key=os.getenv("LANGFUSE_SECRET_KEY"), host=os.getenv("LANGFUSE_HOST",
"http://localhost:3002") )

@observe() async def track_llm_call( prompt: str, model: str, response: str,
latency: float, cost: float ): """LLM 呼び出しのトラッキング""" langfuse.trace(
name="llm_call", input=prompt, output=response, metadata={ "model": model,
"latency_ms": latency \* 1000, "cost_usd": cost } )

## 期待される成果物

- 統合監視スタック
- メトリクス収集設定
- ログ集約システム
- LLM トレーシング
- ダッシュボード設定
```

### 検証方法

```bash
# 監視スタック起動
docker-compose -f docker-compose.monitoring.yml up -d

# アクセス確認
open http://localhost:9090  # Prometheus
open http://localhost:3001  # Grafana (admin/admin)
open http://localhost:3002  # LangFuse
```

---

## 🔧 Step 6.5: セキュリティとコンプライアンス

### コマンド

```bash
/ai:quality:security scan --owasp --gdpr --trivy --snyk
```

### **起動エージェント**

Phase 6 Step 6.5 で起動されるべきエージェント：

- **security-architect Agent**
  (リーダー): セキュリティアーキテクチャ全体の設計と実装
- **compliance-officer Agent**: GDPR/CCPA コンプライアンス要件の実装
- **security-engineer Agent**: セキュリティスキャンツールと脆弱性管理の設定
- **backend-architect Agent**: セキュアな API とデータ保護の実装
- **devops-architect Agent**: セキュリティパイプラインとインフラ保護の設定

### AI への詳細指示

```markdown
# セキュリティ設定指示

## 実行内容

OWASP Top 10 対策、GDPR 準拠、脆弱性スキャンの完全実装

## 具体的な作業項目

### セキュリティスキャン設定

#### .github/workflows/security.yml

name: Security Scan

on: push: branches: [main, develop] schedule: - cron: '0 0 \* \* \*' # 毎日実行

jobs: trivy-scan: runs-on: ubuntu-latest steps: - uses: actions/checkout@v4 -
name: Run Trivy vulnerability scanner in repo mode uses:
aquasecurity/trivy-action@master with: scan-type: 'fs' ignore-unfixed: true
format: 'sarif' output: 'trivy-results.sarif' severity: 'CRITICAL,HIGH'

snyk-scan: runs-on: ubuntu-latest steps: - uses: actions/checkout@v4 - name: Run
Snyk to check for vulnerabilities uses: snyk/actions/python@master env:
SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }} with: args: --severity-threshold=high

owasp-zap: runs-on: ubuntu-latest steps: - name: OWASP ZAP Baseline Scan uses:
zaproxy/action-baseline@v0.9.0 with: target: 'http://localhost:3000'
rules_file_name: '.zap/rules.tsv' cmd_options: '-a'

### シークレット検出

#### .gitleaks.toml

[allowlist] paths = [ '''\.env\.example''', '''\.env\.template''', ]

[[rules]] id = "aws-access-key" description = "AWS Access Key" regex =
'''(?i)aws*?access*?key\_?id["']?\s*[:=]\s*["']?[A-Z0-9]{20}["']?'''

[[rules]] id = "private-key" description = "Private Key" regex = '''-----BEGIN
(?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'''

### GDPR コンプライアンス

#### backend/src/infrastructure/gdpr/data_protection.py

from typing import Dict, Any, List import hashlib from datetime import datetime

class DataProtectionService: """GDPR 準拠のデータ保護サービス"""

    async def anonymize_user_data(self, user_id: str) -> Dict[str, Any]:
        """ユーザーデータの匿名化"""
        # PII（個人識別情報）をハッシュ化
        return {
            "user_id": hashlib.sha256(user_id.encode()).hexdigest(),
            "anonymized_at": datetime.utcnow(),
            "data_retained": ["usage_stats", "preferences"],
            "data_deleted": ["email", "name", "phone"]
        }

    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """データポータビリティ対応"""
        # ユーザーデータの完全エクスポート
        return {
            "user_profile": {},
            "prompts": [],
            "evaluations": [],
            "exported_at": datetime.utcnow()
        }

    async def delete_user_data(self, user_id: str) -> bool:
        """忘れられる権利の実装"""
        # 完全削除処理
        return True

### セキュリティヘッダー設定

#### frontend/next.config.js

const securityHeaders = [ { key: 'X-DNS-Prefetch-Control', value: 'on' }, { key:
'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains;
preload' }, { key: 'X-Frame-Options', value: 'SAMEORIGIN' }, { key:
'X-Content-Type-Options', value: 'nosniff' }, { key: 'X-XSS-Protection', value:
'1; mode=block' }, { key: 'Referrer-Policy', value: 'origin-when-cross-origin'
}, { key: 'Content-Security-Policy', value: "default-src 'self'; script-src
'self' 'unsafe-eval' 'unsafe-inline';" } ]

module.exports = { async headers() { return [ { source: '/:path*', headers:
securityHeaders, }, ] }, }

## 期待される成果物

- 自動セキュリティスキャン
- OWASP Top 10 対策
- GDPR 準拠機能
- シークレット検出
- セキュリティヘッダー
```

### 検証方法

```bash
# セキュリティスキャン実行
trivy fs .
snyk test
gitleaks detect

# OWASP ZAPスキャン
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:3000
```

---

## 🔧 Step 6.6: パフォーマンステスト環境

### コマンド

```bash
/ai:performance-engineer load-test --locust --k6 --target 10000
```

### **起動エージェント**

Phase 6 Step 6.6 で起動されるべきエージェント：

- **performance-engineer Agent**
  (リーダー): パフォーマンステスト戦略全体の設計と実装
- **real-time-features-specialist Agent**:
  WebSocket と リアルタイム機能の負荷テスト
- **edge-database-administrator
  Agent**: データベースパフォーマンステストと最適化
- **vector-database-specialist Agent**: ベクトル検索パフォーマンスの測定と最適化
- **cost-optimization Agent**: パフォーマンス対コスト分析とリソース最適化

### AI への詳細指示

```markdown
# パフォーマンステスト環境構築指示

## 実行内容

10,000 同時接続を目標とする負荷テスト環境の構築

## 具体的な作業項目

### Locust 設定

#### tests/performance/locustfile.py

from locust import HttpUser, task, between import random

class AutoForgeUser(HttpUser): wait_time = between(1, 3)

    def on_start(self):
        # ログイン処理
        self.client.post("/api/auth/login", json={
            "email": f"test_{random.randint(1, 10000)}@example.com",
            "password": "password123"
        })

    @task(3)
    def create_prompt(self):
        self.client.post("/api/v1/prompts", json={
            "title": f"Test Prompt {random.randint(1, 1000)}",
            "content": "This is a test prompt for load testing",
            "description": "Load test description"
        })

    @task(2)
    def get_prompts(self):
        self.client.get("/api/v1/prompts")

    @task(1)
    def search_prompts(self):
        self.client.get(f"/api/v1/prompts/search?q=test")

### K6 テストシナリオ

#### tests/performance/k6-scenario.js

import http from 'k6/http'; import { check, sleep } from 'k6'; import { Rate }
from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = { stages: [ { duration: '2m', target: 100 }, //
ランプアップ { duration: '5m', target: 1000 }, // 維持 { duration: '2m', target:
10000 }, // スパイク { duration: '5m', target: 10000 }, // 高負荷維持 {
duration: '2m', target: 0 }, // ランプダウン ], thresholds: { http_req_duration:
['p(95)<200'], // 95% < 200ms errors: ['rate<0.1'], // エラー率 < 10% }, };

export default function () { const url = 'http://localhost:8000/api/v1/prompts';
const params = { headers: { 'Content-Type': 'application/json', }, };

const res = http.get(url, params);

const success = check(res, { 'status is 200': (r) => r.status === 200, 'response
time < 200ms': (r) => r.timings.duration < 200, });

errorRate.add(!success); sleep(1); }

### WebSocket 負荷テスト

#### tests/performance/websocket_test.py

import asyncio import websockets import json from datetime import datetime

async def websocket_client(client_id: int): uri = "ws://localhost:8000/ws" async
with websockets.connect(uri) as websocket: # 接続メッセージ await
websocket.send(json.dumps({ "type": "connect", "client_id": client_id,
"timestamp": datetime.utcnow().isoformat() }))

        # リアルタイム協調編集シミュレーション
        for i in range(100):
            await websocket.send(json.dumps({
                "type": "edit",
                "content": f"Edit from client {client_id} - {i}",
                "timestamp": datetime.utcnow().isoformat()
            }))
            await asyncio.sleep(0.1)

async def load_test(num_clients: int = 10000): tasks = [] for i in
range(num_clients): tasks.append(websocket_client(i)) if i % 100 == 0: await
asyncio.sleep(0.1) # 段階的接続

    await asyncio.gather(*tasks)

if **name** == "**main**": asyncio.run(load_test())

### パフォーマンステスト実行スクリプト

#### Makefile

.PHONY: perf-test perf-locust perf-k6 perf-websocket

perf-locust: @echo "🔥 Starting Locust load test..." locust -f
tests/performance/locustfile.py \
 --host=http://localhost:8000 \
 --users=1000 \
 --spawn-rate=50 \
 --run-time=10m \
 --headless

perf-k6: @echo "📊 Starting K6 performance test..." k6 run
tests/performance/k6-scenario.js

perf-websocket: @echo "🌐 Starting WebSocket load test..." python
tests/performance/websocket_test.py

perf-test: perf-locust perf-k6 perf-websocket @echo "✅ All performance tests
completed"

perf-report: @echo "📈 Generating performance report..." python
scripts/generate_perf_report.py

## 期待される成果物

- Locust 負荷テスト設定
- K6 パフォーマンステスト
- WebSocket 同時接続テスト
- パフォーマンスレポート生成
- 10,000 同時接続達成
```

### 検証方法

```bash
# Locust Web UI起動
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# K6テスト実行
k6 run tests/performance/k6-scenario.js

# WebSocketテスト
python tests/performance/websocket_test.py

# 統合パフォーマンステスト
make perf-test
```

---

## 📝 Phase 6 完了チェックリスト

### ✅ 必須項目

- [ ] **統合テスト環境**

  - [ ] Playwright E2E テスト設定完了
  - [ ] pytest API 統合テスト設定完了
  - [ ] Jest フロントエンドテスト設定完了
  - [ ] Docker Compose テスト環境構築完了

- [ ] **CI/CD パイプライン**

  - [ ] GitHub Actions ワークフロー設定完了
  - [ ] Cloudflare デプロイメント設定完了
  - [ ] 品質ゲート設定完了
  - [ ] セキュリティスキャン統合完了

- [ ] **品質メトリクス**

  - [ ] バックエンドカバレッジ 80%以上
  - [ ] フロントエンドカバレッジ 75%以上
  - [ ] SonarQube 統合完了
  - [ ] 循環複雑度 10 以下

- [ ] **監視システム**

  - [ ] Prometheus + Grafana 設定完了
  - [ ] LangFuse LLM トレーシング設定完了
  - [ ] Loki ログ集約設定完了
  - [ ] アラート設定完了

- [ ] **セキュリティ**

  - [ ] OWASP Top 10 対策実装
  - [ ] GDPR 準拠機能実装
  - [ ] セキュリティスキャン自動化
  - [ ] シークレット検出設定

- [ ] **パフォーマンス**
  - [ ] API 応答時間 P95 < 200ms
  - [ ] WebSocket 10,000 同時接続達成
  - [ ] 負荷テストシナリオ作成完了
  - [ ] パフォーマンスレポート生成

---

## 🚀 次のステップ

Phase 6 完了後は、以下の作業に進みます：

1. **本番環境デプロイ準備**

   - 環境変数の最終確認
   - シークレット管理の設定
   - バックアップ・リカバリ手順の確立

2. **ユーザー受け入れテスト（UAT）**

   - ステークホルダーによる検証
   - フィードバック収集と対応

3. **本番リリース**

   - 段階的ロールアウト
   - モニタリング強化
   - インシデント対応体制確立

4. **継続的改善**
   - パフォーマンス最適化
   - 機能追加・改善
   - ユーザーフィードバック対応
