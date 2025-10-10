# Edge Computing DevOps Best Practices for AutoForgeNexus

## Overview

AutoForgeNexusのエッジコンピューティング環境におけるインフラストラクチャとCI/CDベストプラクティス。Cloudflareエコシステムを活用したグローバル分散AIプロンプト最適化プラットフォームの実装指針。

## 1. GitOps Edge Deployment Pipeline

### 目的

継続的デリバリーによる自動化されたエッジデプロイメント。GitHub ActionsとWrangler
CLIを組み合わせた宣言的インフラ管理。

### 実装方法

```yaml
# .github/workflows/edge-deploy.yml
name: Edge Deployment Pipeline

on:
  push:
    branches: [main, staging, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '22'
  PYTHON_VERSION: '3.13'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Backend Tests (Python/FastAPI)
      - name: Setup Python 3.13
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install Python dependencies
        run: |
          cd backend
          pip install -e .[dev]

      - name: Run Backend Tests
        run: |
          cd backend
          pytest tests/ --cov=src --cov-fail-under=80

      # Frontend Tests (Next.js 15.5)
      - name: Setup Node.js 22
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Install Frontend dependencies
        run: |
          cd frontend
          npm install -g pnpm
          pnpm install

      - name: Run Frontend Tests
        run: |
          cd frontend
          pnpm test
          pnpm build

  deploy-workers:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    strategy:
      matrix:
        environment: [staging, production]
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Cloudflare Workers
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          workingDirectory: 'backend'
          command: deploy --env ${{ matrix.environment }}

  deploy-pages:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4

      - name: Build Frontend
        run: |
          cd frontend
          npm install -g pnpm
          pnpm install
          pnpm build

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: autoforgenexus
          directory: frontend/out
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

### ブランチ戦略

```bash
# GitFlow + エッジ環境マッピング
main        → production.autoforgenexus.com
staging     → staging.autoforgenexus.com
develop     → dev.autoforgenexus.com
feature/*   → preview.autoforgenexus.com
```

### KPI・メトリクス

- デプロイ時間: < 3分
- テスト実行時間: < 5分
- 失敗率: < 2%
- ロールバック時間: < 30秒

## 2. Infrastructure as Code (Terraform)

### 目的

宣言的インフラ管理によるマルチ環境の一貫性確保。Terraformを使用したCloudflareリソースの完全自動化。

### 実装方法

```hcl
# infrastructure/environments/production/main.tf
terraform {
  required_version = ">= 1.6"
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    bucket = "autoforgenexus-terraform-state"
    key    = "production/terraform.tfstate"
    region = "auto"
  }
}

# Cloudflare Zone Configuration
resource "cloudflare_zone" "main" {
  zone = var.domain_name
  plan = "business"
}

# Workers Configuration
resource "cloudflare_worker_script" "backend_api" {
  name    = "autoforgenexus-backend-${var.environment}"
  content = file("../../../backend/dist/index.js")

  kv_namespace_binding {
    name         = "PROMPT_CACHE"
    namespace_id = cloudflare_workers_kv_namespace.prompt_cache.id
  }

  r2_bucket_binding {
    name        = "ASSETS"
    bucket_name = cloudflare_r2_bucket.assets.name
  }

  analytics_engine_binding {
    name = "ANALYTICS"
  }
}

# R2 Storage Configuration
resource "cloudflare_r2_bucket" "assets" {
  account_id = var.cloudflare_account_id
  name       = "autoforgenexus-assets-${var.environment}"
  location   = "APAC"
}

resource "cloudflare_r2_bucket" "prompts" {
  account_id = var.cloudflare_account_id
  name       = "autoforgenexus-prompts-${var.environment}"
  location   = "APAC"
}

# KV Namespaces
resource "cloudflare_workers_kv_namespace" "prompt_cache" {
  account_id = var.cloudflare_account_id
  title      = "prompt-cache-${var.environment}"
}

resource "cloudflare_workers_kv_namespace" "user_sessions" {
  account_id = var.cloudflare_account_id
  title      = "user-sessions-${var.environment}"
}

# Pages Project
resource "cloudflare_pages_project" "frontend" {
  account_id        = var.cloudflare_account_id
  name              = "autoforgenexus-${var.environment}"
  production_branch = var.production_branch

  build_config {
    build_command   = "pnpm build"
    destination_dir = "out"
    root_dir        = "frontend"
  }

  deployment_configs {
    production {
      environment_variables = {
        NODE_VERSION = "22"
        NEXT_TELEMETRY_DISABLED = "1"
      }
    }
  }
}

# DNS Configuration
resource "cloudflare_record" "api" {
  zone_id = cloudflare_zone.main.id
  name    = "api"
  value   = cloudflare_worker_script.backend_api.subdomain
  type    = "CNAME"
  proxied = true
}

# Web Application Firewall Rules
resource "cloudflare_ruleset" "waf_custom" {
  zone_id     = cloudflare_zone.main.id
  name        = "AutoForgeNexus WAF Rules"
  description = "Custom WAF rules for AI prompt platform"
  kind        = "zone"
  phase       = "http_request_firewall_custom"

  rules {
    action = "block"
    action_parameters {
      response {
        status_code   = 429
        content       = "Rate limit exceeded"
        content_type  = "application/json"
      }
    }
    expression = "(rate(1m) > 100)"
    description = "Rate limiting for API endpoints"
  }
}
```

### 環境管理

```bash
# 環境別デプロイ
cd infrastructure/environments/staging
terraform init
terraform plan -var-file="staging.tfvars"
terraform apply

cd ../production
terraform init
terraform plan -var-file="production.tfvars"
terraform apply
```

### 変数管理

```hcl
# infrastructure/environments/production/terraform.tfvars
domain_name = "autoforgenexus.com"
environment = "production"
cloudflare_account_id = "YOUR_ACCOUNT_ID"
production_branch = "main"

# Scaling Configuration
workers_cpu_limit = 100
workers_memory_limit = 128
kv_ttl_seconds = 86400

# Security Configuration
waf_protection_level = "high"
ddos_protection = true
bot_fight_mode = true
```

### KPI・メトリクス

- インフラプロビジョニング時間: < 5分
- 設定ドリフト検出: 0件
- 環境間一貫性: 100%
- コスト最適化: 月20%削減目標

## 3. Intelligent Edge Caching Strategy

### 目的

プロンプト評価結果とメタデータの戦略的キャッシングによるレイテンシ最小化。階層キャッシングとスマート無効化の実装。

### 実装方法

```javascript
// backend/src/edge/cache-strategy.js
export class EdgeCacheManager {
  constructor(env) {
    this.kv = env.PROMPT_CACHE;
    this.analytics = env.ANALYTICS;
  }

  // キャッシュ階層定義
  getCacheConfig(requestType) {
    const strategies = {
      'prompt-evaluation': {
        ttl: 3600, // 1時間
        edge_ttl: 300, // 5分
        stale_while_revalidate: 86400,
        vary: ['Authorization', 'Accept-Language'],
      },
      'llm-provider-meta': {
        ttl: 86400, // 24時間
        edge_ttl: 7200, // 2時間
        stale_while_revalidate: 604800,
        vary: ['CF-IPCountry'],
      },
      'user-preferences': {
        ttl: 1800, // 30分
        edge_ttl: 60, // 1分
        stale_while_revalidate: 3600,
        vary: ['Authorization'],
      },
      'prompt-templates': {
        ttl: 604800, // 7日
        edge_ttl: 86400, // 24時間
        stale_while_revalidate: 2592000,
        vary: ['Accept-Language'],
      },
    };

    return strategies[requestType] || strategies['default'];
  }

  // インテリジェントキャッシュキー生成
  generateCacheKey(request, context) {
    const url = new URL(request.url);
    const userId = context.userId;
    const region = request.cf.colo;
    const language = request.headers.get('Accept-Language')?.split(',')[0];

    // ハッシュベースキー生成
    const keyComponents = [
      url.pathname,
      url.searchParams.toString(),
      userId ? `user:${userId}` : 'anonymous',
      `region:${region}`,
      `lang:${language}`,
    ].filter(Boolean);

    return `cache:${btoa(keyComponents.join('|'))}`;
  }

  // スマートキャッシュ取得
  async get(request, context) {
    const cacheKey = this.generateCacheKey(request, context);
    const config = this.getCacheConfig(context.requestType);

    // KV から取得
    const cached = await this.kv.get(cacheKey, { type: 'json' });
    if (cached && !this.isStale(cached, config)) {
      // キャッシュヒットログ
      await this.analytics.writeDataPoint({
        blobs: [cacheKey],
        doubles: [Date.now()],
        indexes: ['cache-hit'],
      });

      return cached.data;
    }

    return null;
  }

  // キャッシュ更新
  async set(request, context, data, customTTL = null) {
    const cacheKey = this.generateCacheKey(request, context);
    const config = this.getCacheConfig(context.requestType);
    const ttl = customTTL || config.ttl;

    const cacheData = {
      data,
      timestamp: Date.now(),
      ttl,
      version: context.version || '1.0',
    };

    await this.kv.put(cacheKey, JSON.stringify(cacheData), {
      expirationTtl: ttl,
    });

    // キャッシュ更新ログ
    await this.analytics.writeDataPoint({
      blobs: [cacheKey],
      doubles: [Date.now(), ttl],
      indexes: ['cache-set'],
    });
  }

  // キャッシュ無効化
  async invalidate(pattern) {
    const listResponse = await this.kv.list({ prefix: pattern });
    const deletePromises = listResponse.keys.map((key) =>
      this.kv.delete(key.name)
    );

    await Promise.all(deletePromises);

    return {
      invalidated: listResponse.keys.length,
      pattern,
    };
  }

  // 地理的キャッシュ最適化
  getRegionalStrategy(country, colo) {
    const regionalStrategies = {
      JP: { ttl_multiplier: 1.5, prefer_tokyo: true },
      US: { ttl_multiplier: 1.2, prefer_east: true },
      EU: { ttl_multiplier: 1.0, gdpr_compliance: true },
      AU: { ttl_multiplier: 1.3, prefer_sydney: true },
    };

    return regionalStrategies[country] || { ttl_multiplier: 1.0 };
  }

  isStale(cached, config) {
    const age = Date.now() - cached.timestamp;
    const staleThreshold = config.stale_while_revalidate || config.ttl;
    return age > staleThreshold;
  }
}

// 使用例
export default {
  async fetch(request, env, ctx) {
    const cacheManager = new EdgeCacheManager(env);
    const context = {
      requestType: 'prompt-evaluation',
      userId: getUserId(request),
      version: '1.0',
    };

    // キャッシュから取得試行
    let response = await cacheManager.get(request, context);

    if (!response) {
      // オリジンから取得
      response = await processPromptEvaluation(request);

      // キャッシュに保存
      await cacheManager.set(request, context, response);
    }

    return new Response(JSON.stringify(response), {
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': `max-age=${cacheManager.getCacheConfig(context.requestType).edge_ttl}`,
        'CF-Cache-Status': response ? 'HIT' : 'MISS',
      },
    });
  },
};
```

### CDN設定最適化

```javascript
// Cloudflare Page Rules設定
const pageRules = [
  {
    pattern: 'autoforgenexus.com/api/prompts/templates/*',
    settings: {
      cache_level: 'cache_everything',
      edge_cache_ttl: 86400, // 24時間
      browser_cache_ttl: 7200, // 2時間
      rocket_loader: 'off',
    },
  },
  {
    pattern: 'autoforgenexus.com/api/llm/providers/meta',
    settings: {
      cache_level: 'cache_everything',
      edge_cache_ttl: 7200, // 2時間
      vary_for_device_type: true,
      rocket_loader: 'off',
    },
  },
  {
    pattern: 'autoforgenexus.com/api/evaluate/*',
    settings: {
      cache_level: 'bypass', // 動的コンテンツ
      security_level: 'high',
      waf: 'on',
    },
  },
];
```

### KPI・メトリクス

- キャッシュヒット率: > 85%
- エッジレスポンス時間: < 50ms
- オリジン負荷削減: 70%
- CDNコスト削減: 40%

## 4. Multi-Region LLM Optimization

### 目的

100+LLMプロバイダーの地理的最適化とレイテンシ最小化。リージョン別ルーティングとフォールバック戦略の実装。

### 実装方法

```javascript
// backend/src/edge/llm-router.js
export class LLMRegionRouter {
  constructor(env) {
    this.kv = env.LLM_ROUTING;
    this.analytics = env.ANALYTICS;
  }

  // リージョン別LLMプロバイダーマッピング
  getRegionalProviders() {
    return {
      'asia-pacific': {
        primary: [
          {
            name: 'openai-tokyo',
            endpoint: 'https://api.openai.com',
            latency_avg: 45,
          },
          {
            name: 'anthropic-sydney',
            endpoint: 'https://api.anthropic.com',
            latency_avg: 52,
          },
          {
            name: 'google-singapore',
            endpoint: 'https://generativelanguage.googleapis.com',
            latency_avg: 38,
          },
        ],
        fallback: [
          {
            name: 'azure-eastasia',
            endpoint: 'https://eastasia.api.cognitive.microsoft.com',
            latency_avg: 65,
          },
        ],
      },
      'north-america': {
        primary: [
          {
            name: 'openai-us-east',
            endpoint: 'https://api.openai.com',
            latency_avg: 35,
          },
          {
            name: 'anthropic-us-west',
            endpoint: 'https://api.anthropic.com',
            latency_avg: 42,
          },
          {
            name: 'cohere-us-central',
            endpoint: 'https://api.cohere.ai',
            latency_avg: 38,
          },
        ],
        fallback: [
          {
            name: 'huggingface-us',
            endpoint: 'https://api-inference.huggingface.co',
            latency_avg: 55,
          },
        ],
      },
      europe: {
        primary: [
          {
            name: 'openai-dublin',
            endpoint: 'https://api.openai.com',
            latency_avg: 41,
          },
          {
            name: 'mistral-paris',
            endpoint: 'https://api.mistral.ai',
            latency_avg: 35,
          },
          {
            name: 'anthropic-london',
            endpoint: 'https://api.anthropic.com',
            latency_avg: 48,
          },
        ],
        fallback: [
          {
            name: 'azure-westeurope',
            endpoint: 'https://westeurope.api.cognitive.microsoft.com',
            latency_avg: 58,
          },
        ],
        gdpr_compliant: true,
      },
    };
  }

  // 最適プロバイダー選択
  async selectOptimalProvider(request, model_requirements) {
    const region = this.getRegionFromRequest(request);
    const providers = this.getRegionalProviders()[region];

    if (!providers) {
      throw new Error(`No providers configured for region: ${region}`);
    }

    // リアルタイムレイテンシ情報を取得
    const healthChecks = await this.getProviderHealth(providers.primary);

    // 最適プロバイダーをソート
    const rankedProviders = this.rankProviders(
      providers.primary,
      healthChecks,
      model_requirements
    );

    return {
      primary: rankedProviders[0],
      fallback: providers.fallback,
      region,
      selection_reason: this.getSelectionReason(
        rankedProviders[0],
        model_requirements
      ),
    };
  }

  // プロバイダー健全性チェック
  async getProviderHealth(providers) {
    const healthPromises = providers.map(async (provider) => {
      try {
        const start = Date.now();

        // Health Check エンドポイント
        const response = await fetch(`${provider.endpoint}/health`, {
          method: 'GET',
          timeout: 2000,
          headers: { 'User-Agent': 'AutoForgeNexus-HealthCheck/1.0' },
        });

        const latency = Date.now() - start;
        const isHealthy = response.ok;

        return {
          name: provider.name,
          latency,
          healthy: isHealthy,
          status_code: response.status,
          timestamp: Date.now(),
        };
      } catch (error) {
        return {
          name: provider.name,
          latency: 9999,
          healthy: false,
          error: error.message,
          timestamp: Date.now(),
        };
      }
    });

    const results = await Promise.all(healthPromises);

    // 健全性データをKVに保存
    await this.kv.put(`health:${Date.now()}`, JSON.stringify(results), {
      expirationTtl: 300,
    });

    return results;
  }

  // プロバイダーランキング
  rankProviders(providers, healthChecks, requirements) {
    return providers
      .map((provider) => {
        const health = healthChecks.find((h) => h.name === provider.name);
        const score = this.calculateProviderScore(
          provider,
          health,
          requirements
        );

        return { ...provider, health, score };
      })
      .filter((p) => p.health?.healthy)
      .sort((a, b) => b.score - a.score);
  }

  calculateProviderScore(provider, health, requirements) {
    if (!health?.healthy) return 0;

    let score = 100;

    // レイテンシスコア (50% weight)
    const latencyScore = Math.max(0, 100 - (health.latency - 30) * 2);
    score *= (latencyScore / 100) * 0.5;

    // モデル対応スコア (30% weight)
    const modelScore = this.getModelCompatibilityScore(provider, requirements);
    score *= (modelScore / 100) * 0.3;

    // 信頼性スコア (20% weight)
    const reliabilityScore = this.getReliabilityScore(provider.name);
    score *= (reliabilityScore / 100) * 0.2;

    return Math.round(score);
  }

  getModelCompatibilityScore(provider, requirements) {
    const compatibility = {
      openai: { 'gpt-4': 100, 'gpt-3.5': 100, embedding: 95 },
      anthropic: { 'claude-3': 100, 'claude-2': 95, embedding: 80 },
      google: { gemini: 100, palm: 90, embedding: 85 },
    };

    const providerCompat = compatibility[provider.name.split('-')[0]] || {};
    return providerCompat[requirements.model_type] || 70;
  }

  async getReliabilityScore(providerName) {
    // 過去24時間の成功率を取得
    const key = `reliability:${providerName}:24h`;
    const stored = await this.kv.get(key, { type: 'json' });

    if (!stored) return 85; // デフォルト値

    const successRate =
      (stored.successful_requests / stored.total_requests) * 100;
    return Math.min(100, successRate);
  }

  getRegionFromRequest(request) {
    const country = request.cf?.country;
    const continent = request.cf?.continent;

    // 地域マッピング
    const regionMap = {
      AS: 'asia-pacific',
      OC: 'asia-pacific',
      NA: 'north-america',
      SA: 'north-america',
      EU: 'europe',
      AF: 'europe',
    };

    return regionMap[continent] || 'north-america';
  }

  getSelectionReason(provider, requirements) {
    return {
      provider_name: provider.name,
      region: provider.region,
      latency: provider.health?.latency,
      score: provider.score,
      selection_factors: [
        'optimal_latency',
        'model_compatibility',
        'regional_preference',
      ],
    };
  }
}

// ロードバランシングとフォールバック
export class LLMLoadBalancer {
  constructor(router) {
    this.router = router;
    this.circuitBreakers = new Map();
  }

  async executeWithFallback(request, model_requirements) {
    const selection = await this.router.selectOptimalProvider(
      request,
      model_requirements
    );

    try {
      // プライマリプロバイダー試行
      return await this.callProvider(
        selection.primary,
        request,
        model_requirements
      );
    } catch (error) {
      console.warn(`Primary provider failed: ${error.message}`);

      // フォールバックプロバイダー試行
      for (const fallbackProvider of selection.fallback) {
        try {
          return await this.callProvider(
            fallbackProvider,
            request,
            model_requirements
          );
        } catch (fallbackError) {
          console.warn(`Fallback provider failed: ${fallbackError.message}`);
        }
      }

      throw new Error('All providers failed');
    }
  }

  async callProvider(provider, request, requirements) {
    const circuitBreaker = this.getCircuitBreaker(provider.name);

    if (circuitBreaker.isOpen()) {
      throw new Error(`Circuit breaker open for ${provider.name}`);
    }

    try {
      const response = await fetch(`${provider.endpoint}/v1/completions`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${provider.api_key}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: requirements.model,
          prompt: request.prompt,
          max_tokens: requirements.max_tokens || 150,
          temperature: requirements.temperature || 0.7,
        }),
        timeout: 10000,
      });

      if (!response.ok) {
        throw new Error(`Provider API error: ${response.status}`);
      }

      circuitBreaker.recordSuccess();
      return await response.json();
    } catch (error) {
      circuitBreaker.recordFailure();
      throw error;
    }
  }

  getCircuitBreaker(providerName) {
    if (!this.circuitBreakers.has(providerName)) {
      this.circuitBreakers.set(
        providerName,
        new CircuitBreaker({
          failureThreshold: 5,
          resetTimeout: 30000,
        })
      );
    }
    return this.circuitBreakers.get(providerName);
  }
}
```

### 設定管理

```yaml
# LLMプロバイダー設定 (wrangler.toml)
[vars]
LLM_TIMEOUT_MS = "10000"
MAX_RETRIES = "3"
CIRCUIT_BREAKER_THRESHOLD = "5"

[[kv_namespaces]]
binding = "LLM_ROUTING"
id = "YOUR_KV_NAMESPACE_ID"

[[r2_buckets]]
binding = "LLM_CACHE"
bucket_name = "autoforgenexus-llm-cache"

[env.production.vars]
OPENAI_API_KEY = "YOUR_OPENAI_KEY"
ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_KEY"
GOOGLE_API_KEY = "YOUR_GOOGLE_KEY"
```

### KPI・メトリクス

- LLMレスポンス時間: P95 < 200ms
- プロバイダー可用性: > 99.5%
- 地域最適化効率: 30%改善
- フォールバック成功率: > 95%

## 5. Comprehensive Edge Observability

### 目的

Cloudflare
Analytics、LangFuse、カスタムメトリクスを統合した包括的な監視・アラート体系。エッジパフォーマンスとLLM実行の完全な可視化。

### 実装方法

```javascript
// backend/src/edge/observability.js
export class EdgeObservabilityManager {
  constructor(env) {
    this.analytics = env.ANALYTICS;
    this.kv = env.OBSERVABILITY_KV;
    this.langfuse = new LangFuse({
      secret_key: env.LANGFUSE_SECRET_KEY,
      public_key: env.LANGFUSE_PUBLIC_KEY,
      base_url: env.LANGFUSE_BASE_URL,
    });
  }

  // パフォーマンスメトリクス収集
  async recordPerformanceMetrics(request, response, context) {
    const metrics = {
      // リクエストメトリクス
      timestamp: Date.now(),
      request_id: context.request_id,
      method: request.method,
      url: request.url,
      user_agent: request.headers.get('User-Agent'),

      // Cloudflare メトリクス
      colo: request.cf?.colo,
      country: request.cf?.country,
      region: request.cf?.region,
      asn: request.cf?.asn,

      // レスポンスメトリクス
      status_code: response.status,
      content_length: response.headers.get('Content-Length'),
      cache_status: response.headers.get('CF-Cache-Status'),

      // パフォーマンスメトリクス
      response_time: context.response_time,
      cpu_time: context.cpu_time,
      memory_usage: context.memory_usage,

      // ビジネスメトリクス
      user_id: context.user_id,
      organization_id: context.organization_id,
      feature_used: context.feature_used,
      prompt_length: context.prompt_length,
      tokens_generated: context.tokens_generated,
    };

    // Analytics Engine に送信
    await this.analytics.writeDataPoint({
      indexes: [
        metrics.status_code.toString(),
        metrics.colo,
        metrics.country,
        metrics.feature_used,
      ],
      doubles: [
        metrics.response_time,
        metrics.cpu_time,
        metrics.memory_usage,
        metrics.tokens_generated || 0,
      ],
      blobs: [
        metrics.request_id,
        metrics.user_id || 'anonymous',
        JSON.stringify({
          method: metrics.method,
          cache_status: metrics.cache_status,
          user_agent: metrics.user_agent?.substring(0, 100),
        }),
      ],
    });

    // 高レイテンシアラートチェック
    if (metrics.response_time > 1000) {
      await this.triggerHighLatencyAlert(metrics);
    }

    return metrics;
  }

  // LLM実行トレーシング
  async traceLLMExecution(llm_request, llm_response, context) {
    const trace = this.langfuse.trace({
      name: 'llm_execution',
      id: context.trace_id,
      user_id: context.user_id,
      session_id: context.session_id,
      metadata: {
        region: context.region,
        provider: context.provider,
        model: context.model,
        colo: context.colo,
      },
    });

    const span = trace.span({
      name: 'llm_generation',
      input: {
        prompt: llm_request.prompt,
        model: llm_request.model,
        parameters: llm_request.parameters,
      },
      output: {
        content: llm_response.content,
        tokens: llm_response.usage,
      },
      metadata: {
        provider: context.provider,
        latency_ms: context.llm_latency,
        cost_usd: context.estimated_cost,
        cache_hit: context.cache_hit,
      },
    });

    // 品質スコア評価
    if (context.quality_score) {
      span.score({
        name: 'quality',
        value: context.quality_score,
        comment: context.quality_feedback,
      });
    }

    await trace.update({
      output: llm_response,
      metadata: {
        total_duration: context.total_duration,
        success: true,
      },
    });

    return trace;
  }

  // エラートラッキング
  async trackError(error, context) {
    const errorData = {
      timestamp: Date.now(),
      request_id: context.request_id,
      error_type: error.constructor.name,
      error_message: error.message,
      stack_trace: error.stack,

      // コンテキスト情報
      url: context.url,
      method: context.method,
      user_id: context.user_id,
      colo: context.colo,
      country: context.country,

      // 環境情報
      worker_version: context.worker_version,
      deployment_id: context.deployment_id,
    };

    // Analytics Engine にエラーログ送信
    await this.analytics.writeDataPoint({
      indexes: [
        'error',
        errorData.error_type,
        errorData.colo,
        errorData.country,
      ],
      doubles: [Date.now()],
      blobs: [
        errorData.request_id,
        errorData.error_message,
        JSON.stringify({
          stack: errorData.stack_trace?.substring(0, 500),
          context: {
            url: errorData.url,
            method: errorData.method,
            user_id: errorData.user_id,
          },
        }),
      ],
    });

    // 重要なエラーはSlack通知
    if (this.isCriticalError(error)) {
      await this.sendSlackAlert({
        type: 'critical_error',
        message: `Critical error in ${context.colo}: ${error.message}`,
        details: errorData,
      });
    }
  }

  // アラート管理
  async checkSLOViolations() {
    const timeWindow = 5 * 60 * 1000; // 5分
    const now = Date.now();
    const windowStart = now - timeWindow;

    // SLO定義
    const slos = {
      availability: { target: 99.9, threshold: 0.1 }, // 99.9%
      latency_p95: { target: 200, threshold: 50 }, // P95 < 200ms
      error_rate: { target: 1.0, threshold: 0.5 }, // < 1%
    };

    // メトリクス集計クエリ（Analytics Engine）
    const metrics = await this.queryMetrics(windowStart, now);

    const currentSLOs = {
      availability: this.calculateAvailability(metrics),
      latency_p95: this.calculateP95Latency(metrics),
      error_rate: this.calculateErrorRate(metrics),
    };

    // SLO違反チェック
    for (const [slo, config] of Object.entries(slos)) {
      const current = currentSLOs[slo];
      const violation = this.checkSLOViolation(slo, current, config);

      if (violation.violated) {
        await this.handleSLOViolation(slo, violation, config);
      }
    }

    return currentSLOs;
  }

  async queryMetrics(start, end) {
    // Note: Analytics Engine GraphQL クエリの実装
    const query = `
      query GetMetrics($start: DateTime!, $end: DateTime!) {
        viewer {
          accounts(filter: { accountTag: "${this.account_id}" }) {
            analyticsEngineEvents(
              filter: {
                datetime_gte: $start,
                datetime_lte: $end
              }
              orderBy: [datetime_DESC]
            ) {
              dimensions {
                index1  # status_code
                index2  # colo
                index3  # country
                double1 # response_time
                double2 # cpu_time
              }
            }
          }
        }
      }
    `;

    // GraphQL実装省略（実際のプロジェクトでは実装必要）
    return {
      total_requests: 1000,
      successful_requests: 995,
      response_times: [45, 62, 78, 95, 120, 156, 189, 220, 280, 350],
    };
  }

  calculateP95Latency(metrics) {
    const sorted = metrics.response_times.sort((a, b) => a - b);
    const p95Index = Math.ceil(sorted.length * 0.95) - 1;
    return sorted[p95Index];
  }

  calculateAvailability(metrics) {
    return (metrics.successful_requests / metrics.total_requests) * 100;
  }

  calculateErrorRate(metrics) {
    const errorRequests = metrics.total_requests - metrics.successful_requests;
    return (errorRequests / metrics.total_requests) * 100;
  }

  async handleSLOViolation(slo, violation, config) {
    const alert = {
      type: 'slo_violation',
      slo,
      current_value: violation.current,
      target_value: config.target,
      severity: violation.severity,
      timestamp: Date.now(),
      details: violation.details,
    };

    // Slack通知
    await this.sendSlackAlert({
      type: 'slo_violation',
      message: `🚨 SLO Violation: ${slo}`,
      fields: [
        { title: 'Current Value', value: violation.current, short: true },
        { title: 'Target Value', value: config.target, short: true },
        { title: 'Severity', value: violation.severity, short: true },
      ],
    });

    // PagerDuty統合（高重要度の場合）
    if (violation.severity === 'critical') {
      await this.triggerPagerDutyAlert(alert);
    }
  }

  async sendSlackAlert(alert) {
    const webhook_url = this.env.SLACK_WEBHOOK_URL;
    if (!webhook_url) return;

    const payload = {
      text: alert.message,
      username: 'AutoForgeNexus Monitor',
      icon_emoji: ':warning:',
      fields: alert.fields || [],
    };

    await fetch(webhook_url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  }

  isCriticalError(error) {
    const criticalTypes = [
      'SecurityError',
      'DatabaseConnectionError',
      'LLMProviderDownError',
      'QuotaExceededError',
    ];

    return criticalTypes.includes(error.constructor.name);
  }
}

// ダッシュボード用データ集約
export class MetricsDashboard {
  constructor(observability) {
    this.obs = observability;
  }

  async generateDashboardData(timeRange = '1h') {
    const metrics = await this.obs.queryMetrics(
      Date.now() - this.parseTimeRange(timeRange),
      Date.now()
    );

    return {
      performance: {
        avg_response_time: this.calculateAverage(metrics.response_times),
        p95_response_time: this.obs.calculateP95Latency(metrics),
        throughput:
          metrics.total_requests / (this.parseTimeRange(timeRange) / 1000 / 60), // req/min
        cache_hit_rate: this.calculateCacheHitRate(metrics),
      },
      reliability: {
        uptime: this.obs.calculateAvailability(metrics),
        error_rate: this.obs.calculateErrorRate(metrics),
        slo_compliance: await this.calculateSLOCompliance(),
      },
      geographic: {
        top_regions: this.getTopRegions(metrics),
        regional_latency: this.getRegionalLatency(metrics),
      },
      llm_metrics: {
        total_tokens: await this.getTotalTokenUsage(timeRange),
        avg_cost_per_request: await this.getAverageCost(timeRange),
        provider_performance: await this.getProviderPerformance(timeRange),
      },
    };
  }

  parseTimeRange(range) {
    const units = { m: 60000, h: 3600000, d: 86400000 };
    const match = range.match(/^(\d+)([mhd])$/);
    return match ? parseInt(match[1]) * units[match[2]] : 3600000;
  }
}
```

### Grafana ダッシュボード設定

```json
{
  "dashboard": {
    "title": "AutoForgeNexus Edge Performance",
    "panels": [
      {
        "title": "Response Time P95",
        "type": "stat",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, cloudflare_response_time_bucket)",
            "legendFormat": "P95 Response Time"
          }
        ],
        "thresholds": [
          { "color": "green", "value": 0 },
          { "color": "yellow", "value": 150 },
          { "color": "red", "value": 200 }
        ]
      },
      {
        "title": "Geographic Distribution",
        "type": "geomap",
        "targets": [
          {
            "expr": "sum by (country) (cloudflare_requests_total)",
            "legendFormat": "{{ country }}"
          }
        ]
      },
      {
        "title": "LLM Provider Performance",
        "type": "table",
        "targets": [
          {
            "expr": "avg by (provider) (langfuse_llm_latency_ms)",
            "legendFormat": "Avg Latency"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "type": "gauge",
        "targets": [
          {
            "expr": "(cloudflare_cache_hits_total / cloudflare_requests_total) * 100"
          }
        ]
      }
    ]
  }
}
```

### KPI・メトリクス

- SLO準拠率: > 99%
- アラート精度: > 95% (false positive < 5%)
- 平均検出時間: < 2分
- 運用可視性: 100% (全コンポーネント監視)

## 6. Dynamic Traffic Routing & A/B Testing

### 目的

エッジでのA/Bテスト、カナリアリリース、ブルーグリーンデプロイメント。トラフィック分散とフィーチャーフラグによる段階的機能展開。

### 実装方法

```javascript
// backend/src/edge/traffic-router.js
export class DynamicTrafficRouter {
  constructor(env) {
    this.kv = env.TRAFFIC_ROUTING;
    this.analytics = env.ANALYTICS;
    this.durable_objects = env.FEATURE_FLAGS;
  }

  // A/Bテスト設定管理
  async configureABTest(config) {
    const abTest = {
      id: config.id,
      name: config.name,
      description: config.description,

      // トラフィック分散設定
      variants: {
        control: {
          name: 'control',
          traffic_percentage: config.control_percentage || 50,
          deployment: config.control_deployment || 'stable',
          features: config.control_features || {},
        },
        treatment: {
          name: 'treatment',
          traffic_percentage: config.treatment_percentage || 50,
          deployment: config.treatment_deployment || 'canary',
          features: config.treatment_features || {},
        },
      },

      // ターゲティング条件
      targeting: {
        user_segments: config.user_segments || ['all'],
        geographic_regions: config.regions || ['all'],
        device_types: config.device_types || ['all'],
        custom_attributes: config.custom_attributes || {},
      },

      // 期間設定
      schedule: {
        start_date: config.start_date,
        end_date: config.end_date,
        timezone: config.timezone || 'UTC',
      },

      // 成功指標
      metrics: {
        primary_metric: config.primary_metric,
        secondary_metrics: config.secondary_metrics || [],
        significance_level: config.significance_level || 0.05,
        minimum_sample_size: config.minimum_sample_size || 1000,
      },

      // 安全性設定
      safeguards: {
        max_error_rate: config.max_error_rate || 5.0,
        min_conversion_rate: config.min_conversion_rate || null,
        auto_stop_on_significance: config.auto_stop || false,
      },

      created_at: Date.now(),
      status: 'active',
    };

    await this.kv.put(`ab_test:${config.id}`, JSON.stringify(abTest), {
      expirationTtl: 90 * 24 * 3600, // 90日
    });

    return abTest;
  }

  // ユーザーのバリアント決定
  async assignUserVariant(request, test_id, user_context) {
    const test = await this.getABTest(test_id);
    if (!test || test.status !== 'active') {
      return { variant: 'control', reason: 'test_inactive' };
    }

    // テスト期間チェック
    if (!this.isTestActive(test)) {
      return { variant: 'control', reason: 'outside_schedule' };
    }

    // ターゲティング条件チェック
    if (!this.matchesTargeting(request, user_context, test.targeting)) {
      return { variant: 'control', reason: 'targeting_mismatch' };
    }

    // 一貫したバリアント割り当て（user_idベース）
    const userId = user_context.user_id || this.generateSessionId(request);
    const hash = await this.hashUserId(userId, test_id);
    const assignment_percentage = hash % 100;

    let assigned_variant = 'control';
    let cumulative_percentage = 0;

    for (const [variant_name, variant_config] of Object.entries(
      test.variants
    )) {
      cumulative_percentage += variant_config.traffic_percentage;
      if (assignment_percentage < cumulative_percentage) {
        assigned_variant = variant_name;
        break;
      }
    }

    // 割り当て結果を記録
    await this.recordAssignment({
      test_id,
      user_id: userId,
      variant: assigned_variant,
      timestamp: Date.now(),
      request_context: {
        colo: request.cf?.colo,
        country: request.cf?.country,
        user_agent: request.headers.get('User-Agent')?.substring(0, 100),
      },
    });

    return {
      variant: assigned_variant,
      reason: 'assigned',
      test_config: test.variants[assigned_variant],
      assignment_id: `${test_id}:${userId}:${assigned_variant}`,
    };
  }

  // カナリアデプロイメント管理
  async configureCanaryDeployment(config) {
    const canary = {
      deployment_id: config.deployment_id,
      name: config.name,

      // トラフィック段階設定
      traffic_stages: config.stages || [
        { percentage: 5, duration: 300, max_error_rate: 2.0 }, // 5% for 5min
        { percentage: 25, duration: 600, max_error_rate: 1.5 }, // 25% for 10min
        { percentage: 50, duration: 900, max_error_rate: 1.0 }, // 50% for 15min
        { percentage: 100, duration: 0, max_error_rate: 0.5 }, // 100%
      ],

      current_stage: 0,
      started_at: Date.now(),

      // 健全性チェック
      health_checks: {
        endpoint: config.health_endpoint || '/health',
        interval: config.check_interval || 30,
        timeout: config.check_timeout || 5,
        success_threshold: config.success_threshold || 3,
        failure_threshold: config.failure_threshold || 2,
      },

      // 自動ロールバック設定
      rollback_triggers: {
        error_rate_threshold: config.error_threshold || 2.0,
        latency_threshold: config.latency_threshold || 500,
        health_check_failures: config.health_failures || 3,
      },

      status: 'active',
    };

    await this.kv.put(`canary:${config.deployment_id}`, JSON.stringify(canary));

    // 段階的トラフィック増加スケジューラー
    await this.scheduleCanaryProgression(canary);

    return canary;
  }

  // リアルタイムトラフィックルーティング
  async routeRequest(request, user_context) {
    const routing_decision = {
      timestamp: Date.now(),
      request_id: crypto.randomUUID(),
      user_id: user_context.user_id,
      deployment: 'stable', // デフォルト
      features: {},
      routing_reason: [],
    };

    // アクティブなカナリアデプロイメントチェック
    const canaries = await this.getActiveCanaries();
    for (const canary of canaries) {
      const canary_routing = await this.evaluateCanaryRouting(request, canary);
      if (canary_routing.route_to_canary) {
        routing_decision.deployment = canary.deployment_id;
        routing_decision.routing_reason.push(`canary_${canary.current_stage}`);
        break;
      }
    }

    // A/Bテストバリアント適用
    const active_tests = await this.getActiveABTests();
    for (const test of active_tests) {
      const variant_assignment = await this.assignUserVariant(
        request,
        test.id,
        user_context
      );
      if (variant_assignment.variant !== 'control') {
        routing_decision.features = {
          ...routing_decision.features,
          ...variant_assignment.test_config.features,
        };
        routing_decision.routing_reason.push(
          `ab_test_${test.id}_${variant_assignment.variant}`
        );
      }
    }

    // フィーチャーフラグ適用
    const feature_flags = await this.evaluateFeatureFlags(
      request,
      user_context
    );
    routing_decision.features = {
      ...routing_decision.features,
      ...feature_flags,
    };

    // ルーティング決定をログ
    await this.logRoutingDecision(routing_decision);

    return routing_decision;
  }

  // ブルーグリーンデプロイメント
  async executeBlueGreenSwitch(deployment_config) {
    const switch_plan = {
      switch_id: crypto.randomUUID(),
      blue_deployment: deployment_config.current_deployment,
      green_deployment: deployment_config.new_deployment,
      switch_strategy: deployment_config.strategy || 'instant', // instant, gradual, dns

      // 事前チェック
      pre_switch_checks: [
        'health_check_green',
        'smoke_tests',
        'performance_baseline',
        'security_scan',
      ],

      // スイッチ後検証
      post_switch_validation: [
        'traffic_distribution_check',
        'error_rate_monitoring',
        'performance_validation',
        'user_feedback_monitoring',
      ],

      // ロールバック計画
      rollback_plan: {
        trigger_conditions: deployment_config.rollback_triggers,
        rollback_strategy: 'instant',
        notification_channels: ['slack', 'pagerduty'],
      },
    };

    // 事前チェック実行
    const pre_checks = await this.executePreSwitchChecks(switch_plan);
    if (!pre_checks.all_passed) {
      throw new Error(
        `Pre-switch checks failed: ${pre_checks.failures.join(', ')}`
      );
    }

    // トラフィックスイッチ実行
    switch (switch_plan.switch_strategy) {
      case 'instant':
        await this.instantTrafficSwitch(switch_plan);
        break;
      case 'gradual':
        await this.gradualTrafficSwitch(switch_plan);
        break;
      case 'dns':
        await this.dnsBasedSwitch(switch_plan);
        break;
    }

    // スイッチ後検証
    const post_validation = await this.executePostSwitchValidation(switch_plan);
    if (!post_validation.all_passed) {
      await this.executeRollback(switch_plan, post_validation.failures);
    }

    return {
      switch_id: switch_plan.switch_id,
      status: post_validation.all_passed ? 'success' : 'rolled_back',
      execution_time: Date.now() - switch_plan.started_at,
      details: { pre_checks, post_validation },
    };
  }

  async instantTrafficSwitch(switch_plan) {
    // DNS レコード更新（即座に100%トラフィックを新デプロイメントに）
    await this.updateDNSRecord({
      name: 'api.autoforgenexus.com',
      target: switch_plan.green_deployment.endpoint,
      ttl: 60, // 短いTTLで素早い切り替え
    });

    // ロードバランサー設定更新
    await this.updateLoadBalancerConfig({
      upstream: switch_plan.green_deployment.endpoint,
      backup: switch_plan.blue_deployment.endpoint,
    });

    switch_plan.switched_at = Date.now();
  }

  // メトリクス収集とアラート
  async monitorTrafficRouting() {
    const monitoring_data = {
      timestamp: Date.now(),
      active_experiments: 0,
      total_traffic_routed: 0,
      routing_decisions: {},
      health_metrics: {},
    };

    // アクティブなA/Bテスト監視
    const active_tests = await this.getActiveABTests();
    monitoring_data.active_experiments = active_tests.length;

    for (const test of active_tests) {
      const test_metrics = await this.getABTestMetrics(test.id);

      // 統計的有意性チェック
      if (test_metrics.sample_size >= test.metrics.minimum_sample_size) {
        const significance =
          await this.calculateStatisticalSignificance(test_metrics);

        if (
          significance.is_significant &&
          test.safeguards.auto_stop_on_significance
        ) {
          await this.stopABTest(test.id, 'statistical_significance_reached');
        }
      }

      // セーフガードチェック
      if (test_metrics.error_rate > test.safeguards.max_error_rate) {
        await this.stopABTest(test.id, 'error_rate_exceeded');
      }
    }

    // カナリアデプロイメント進捗監視
    const active_canaries = await this.getActiveCanaries();
    for (const canary of active_canaries) {
      const canary_metrics = await this.getCanaryMetrics(canary.deployment_id);

      // 自動進行 or ロールバック判定
      const progression_decision = await this.evaluateCanaryProgression(
        canary,
        canary_metrics
      );

      if (progression_decision.action === 'advance') {
        await this.advanceCanaryStage(canary);
      } else if (progression_decision.action === 'rollback') {
        await this.rollbackCanary(canary, progression_decision.reason);
      }
    }

    return monitoring_data;
  }

  // ユーティリティメソッド
  async hashUserId(userId, testId) {
    const encoder = new TextEncoder();
    const data = encoder.encode(`${userId}:${testId}:salt`);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = new Uint8Array(hashBuffer);
    return (
      hashArray.reduce((hash, byte) => (hash << 5) - hash + byte, 0) &
      0x7fffffff
    );
  }

  generateSessionId(request) {
    const fingerprint = [
      request.cf?.colo,
      request.headers.get('User-Agent'),
      request.cf?.country,
    ].join('|');

    return btoa(fingerprint).substring(0, 16);
  }

  async getABTest(test_id) {
    const stored = await this.kv.get(`ab_test:${test_id}`, { type: 'json' });
    return stored;
  }

  isTestActive(test) {
    const now = Date.now();
    return now >= test.schedule.start_date && now <= test.schedule.end_date;
  }

  matchesTargeting(request, user_context, targeting) {
    // 地理的ターゲティング
    if (
      targeting.geographic_regions?.length > 0 &&
      !targeting.geographic_regions.includes('all')
    ) {
      const user_region = request.cf?.country;
      if (!targeting.geographic_regions.includes(user_region)) {
        return false;
      }
    }

    // ユーザーセグメンテーション
    if (
      targeting.user_segments?.length > 0 &&
      !targeting.user_segments.includes('all')
    ) {
      const user_segment = user_context.segment;
      if (!targeting.user_segments.includes(user_segment)) {
        return false;
      }
    }

    return true;
  }
}

// 設定例
const trafficRoutingConfig = {
  ab_tests: [
    {
      id: 'prompt_evaluation_ui_v2',
      name: 'New Prompt Evaluation Interface',
      control_percentage: 70,
      treatment_percentage: 30,
      treatment_features: {
        new_evaluation_ui: true,
        enhanced_analytics: true,
      },
      primary_metric: 'user_satisfaction_score',
      regions: ['US', 'EU', 'JP'],
      start_date: Date.now(),
      end_date: Date.now() + 14 * 24 * 3600 * 1000, // 2週間
    },
  ],
  canary_deployments: [
    {
      deployment_id: 'backend_v2_1_0',
      name: 'Backend API v2.1.0 Rollout',
      stages: [
        { percentage: 5, duration: 600 }, // 5% for 10 min
        { percentage: 25, duration: 1800 }, // 25% for 30 min
        { percentage: 100, duration: 0 }, // 100%
      ],
    },
  ],
};
```

### GitHub Actions ワークフロー統合

```yaml
# .github/workflows/canary-deployment.yml
name: Canary Deployment

on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  deploy-canary:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Canary
        run: |
          # Wrangler でカナリアデプロイメント
          cd backend
          wrangler deploy --env canary

          # トラフィックルーティング設定
          curl -X POST "${{ secrets.TRAFFIC_ROUTER_API }}/canary" \
            -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{
              "deployment_id": "'$GITHUB_SHA'",
              "name": "Backend Canary '$GITHUB_SHA'",
              "stages": [
                {"percentage": 5, "duration": 300},
                {"percentage": 25, "duration": 600},
                {"percentage": 100, "duration": 0}
              ]
            }'

  monitor-canary:
    needs: deploy-canary
    runs-on: ubuntu-latest
    steps:
      - name: Monitor Canary Health
        run: |
          # 30分間監視
          for i in {1..30}; do
            HEALTH=$(curl -s "${{ secrets.CANARY_ENDPOINT }}/health")
            ERROR_RATE=$(curl -s "${{ secrets.METRICS_API }}/error-rate")
            
            if [[ "$ERROR_RATE" > "2.0" ]]; then
              echo "Error rate too high: $ERROR_RATE%"
              curl -X POST "${{ secrets.TRAFFIC_ROUTER_API }}/rollback" \
                -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" \
                -d '{"deployment_id": "'$GITHUB_SHA'", "reason": "high_error_rate"}'
              exit 1
            fi
            
            sleep 60
          done
```

### KPI・メトリクス

- A/Bテスト統計的信頼度: > 95%
- カナリア成功率: > 98%
- 平均デプロイ時間: < 10分
- ロールバック時間: < 2分
- トラフィック分散精度: ±2%

## 7. Zero Trust Edge Security

### 目的

Cloudflare Access、Workers
KV暗号化、地理的アクセス制御による包括的エッジセキュリティ。ゼロトラストアーキテクチャとDDoS保護の実装。

### 実装方法

```javascript
// backend/src/edge/security-manager.js
export class ZeroTrustSecurityManager {
  constructor(env) {
    this.kv = env.SECURITY_KV;
    this.access_policies = env.ACCESS_POLICIES;
    this.rate_limiter = env.RATE_LIMITER;
    this.encryption_key = env.ENCRYPTION_KEY;
  }

  // リクエスト認証・認可
  async authenticateRequest(request, context) {
    const auth_result = {
      authenticated: false,
      authorized: false,
      user_context: null,
      security_level: 'unknown',
      risk_score: 0,
      applied_policies: [],
    };

    try {
      // JWTトークン検証
      const token = this.extractBearerToken(request);
      if (token) {
        const jwt_validation = await this.validateJWT(token);
        if (jwt_validation.valid) {
          auth_result.authenticated = true;
          auth_result.user_context = jwt_validation.payload;
          auth_result.security_level = jwt_validation.security_level;
        }
      }

      // Cloudflare Access ヘッダー検証（管理者エンドポイント用）
      const cf_access_jwt = request.headers.get('CF-Access-Jwt-Assertion');
      if (cf_access_jwt) {
        const access_validation =
          await this.validateCloudflareAccess(cf_access_jwt);
        if (access_validation.valid) {
          auth_result.authenticated = true;
          auth_result.security_level = 'high';
          auth_result.user_context = {
            ...auth_result.user_context,
            ...access_validation.claims,
          };
        }
      }

      // リスクスコア計算
      auth_result.risk_score = await this.calculateRiskScore(
        request,
        auth_result.user_context
      );

      // 認可チェック
      if (auth_result.authenticated) {
        const authorization = await this.checkAuthorization(
          request,
          auth_result.user_context
        );
        auth_result.authorized = authorization.authorized;
        auth_result.applied_policies = authorization.applied_policies;
      }

      return auth_result;
    } catch (error) {
      console.error('Authentication failed:', error);
      return {
        ...auth_result,
        error: error.message,
        risk_score: 100, // 認証エラー時は最高リスク
      };
    }
  }

  // レート制限とDDoS保護
  async enforceRateLimit(request, user_context) {
    const client_id = this.getClientIdentifier(request, user_context);
    const endpoint = this.getEndpointCategory(request.url);

    // 階層的レート制限設定
    const rate_limits = {
      auth: {
        anonymous: { requests: 10, window: 60 }, // 10 req/min
        authenticated: { requests: 60, window: 60 }, // 60 req/min
        premium: { requests: 200, window: 60 }, // 200 req/min
      },
      'llm-evaluation': {
        anonymous: { requests: 5, window: 300 }, // 5 req/5min
        authenticated: { requests: 100, window: 60 }, // 100 req/min
        premium: { requests: 1000, window: 60 }, // 1000 req/min
      },
      admin: {
        anonymous: { requests: 0, window: 60 }, // 禁止
        authenticated: { requests: 10, window: 60 }, // 10 req/min
        admin: { requests: 100, window: 60 }, // 100 req/min
      },
    };

    const user_tier = this.getUserTier(user_context);
    const limit_config = rate_limits[endpoint]?.[user_tier];

    if (!limit_config) {
      return { allowed: false, reason: 'no_rate_limit_defined' };
    }

    // トークンバケット実装
    const bucket_key = `rate_limit:${client_id}:${endpoint}`;
    const current_bucket = (await this.kv.get(bucket_key, {
      type: 'json',
    })) || {
      tokens: limit_config.requests,
      last_refill: Date.now(),
    };

    // バケット補充
    const now = Date.now();
    const time_passed = (now - current_bucket.last_refill) / 1000;
    const tokens_to_add = Math.floor(
      time_passed * (limit_config.requests / limit_config.window)
    );

    current_bucket.tokens = Math.min(
      limit_config.requests,
      current_bucket.tokens + tokens_to_add
    );
    current_bucket.last_refill = now;

    // リクエスト許可判定
    if (current_bucket.tokens >= 1) {
      current_bucket.tokens -= 1;

      // バケット状態保存
      await this.kv.put(bucket_key, JSON.stringify(current_bucket), {
        expirationTtl: limit_config.window * 2,
      });

      return {
        allowed: true,
        remaining_tokens: current_bucket.tokens,
        reset_time: now + limit_config.window * 1000,
      };
    } else {
      // レート制限超過ログ
      await this.logSecurityEvent('rate_limit_exceeded', {
        client_id,
        endpoint,
        user_tier,
        timestamp: now,
      });

      return {
        allowed: false,
        reason: 'rate_limit_exceeded',
        retry_after: limit_config.window - time_passed,
      };
    }
  }

  // 地理的アクセス制御
  async enforceGeoRestrictions(request, endpoint) {
    const country = request.cf?.country;
    const region = this.getRegion(country);

    // エンドポイント別地理制限設定
    const geo_policies = {
      '/admin/*': {
        allowed_countries: ['US', 'JP', 'GB', 'DE'],
        blocked_countries: ['CN', 'RU', 'KP'],
        require_vpn_detection: true,
      },
      '/api/llm/providers/restricted/*': {
        allowed_regions: ['north-america', 'europe'],
        gdpr_compliance_required: true,
      },
      '/api/export/data/*': {
        gdpr_countries: ['EU'],
        data_residency_check: true,
      },
    };

    const applicable_policy = this.findMatchingGeoPolicy(
      endpoint,
      geo_policies
    );
    if (!applicable_policy) {
      return { allowed: true, reason: 'no_geo_restrictions' };
    }

    // 国別制限チェック
    if (applicable_policy.blocked_countries?.includes(country)) {
      await this.logSecurityEvent('geo_restriction_blocked', {
        country,
        endpoint,
        reason: 'blocked_country',
      });

      return {
        allowed: false,
        reason: 'geo_blocked',
        country,
        policy: 'blocked_countries',
      };
    }

    if (
      applicable_policy.allowed_countries &&
      !applicable_policy.allowed_countries.includes(country)
    ) {
      return {
        allowed: false,
        reason: 'geo_not_allowed',
        country,
        policy: 'allowed_countries_only',
      };
    }

    // VPN検出（必要に応じて）
    if (applicable_policy.require_vpn_detection) {
      const vpn_detected = await this.detectVPN(request);
      if (vpn_detected.is_vpn && !vpn_detected.is_trusted) {
        return {
          allowed: false,
          reason: 'untrusted_vpn_detected',
          vpn_info: vpn_detected,
        };
      }
    }

    // GDPR コンプライアンス（EU圏）
    if (applicable_policy.gdpr_compliance_required && region === 'europe') {
      const gdpr_consent = request.headers.get('X-GDPR-Consent');
      if (!gdpr_consent || !this.validateGDPRConsent(gdpr_consent)) {
        return {
          allowed: false,
          reason: 'gdpr_consent_required',
          region,
        };
      }
    }

    return {
      allowed: true,
      applied_policy: applicable_policy,
      country,
      region,
    };
  }

  // データ暗号化（機密データ保護）
  async encryptSensitiveData(data, context) {
    // データ分類に基づく暗号化
    const classification = this.classifyData(data);
    const encryption_config = this.getEncryptionConfig(classification);

    if (encryption_config.encrypt) {
      // AES-256-GCM 暗号化
      const encrypted = await this.encrypt(
        JSON.stringify(data),
        encryption_config.key,
        encryption_config.algorithm
      );

      // 暗号化メタデータ
      return {
        encrypted_data: encrypted.ciphertext,
        iv: encrypted.iv,
        auth_tag: encrypted.auth_tag,
        encryption_algorithm: encryption_config.algorithm,
        key_version: encryption_config.key_version,
        data_classification: classification,
        encrypted_at: Date.now(),
      };
    }

    return { plaintext_data: data, classification };
  }

  async decrypt(encrypted_data, context) {
    if (!encrypted_data.encrypted_data) {
      return encrypted_data.plaintext_data;
    }

    const decryption_key = await this.getDecryptionKey(
      encrypted_data.key_version
    );
    const decrypted = await crypto.subtle.decrypt(
      {
        name: encrypted_data.encryption_algorithm,
        iv: this.base64ToArrayBuffer(encrypted_data.iv),
        tagLength: 128,
      },
      decryption_key,
      this.base64ToArrayBuffer(encrypted_data.encrypted_data)
    );

    return JSON.parse(new TextDecoder().decode(decrypted));
  }

  // セキュリティイベント監視
  async detectSecurityThreats(request, user_context) {
    const threats = [];
    const risk_indicators = {
      sql_injection: this.detectSQLInjection(request),
      xss_attempt: this.detectXSS(request),
      unusual_patterns: await this.detectAnomalousPatterns(
        request,
        user_context
      ),
      suspicious_headers: this.analyzeSuspiciousHeaders(request),
      bot_behavior: await this.detectBotBehavior(request, user_context),
    };

    // 脅威検出結果の評価
    for (const [threat_type, detection_result] of Object.entries(
      risk_indicators
    )) {
      if (detection_result.detected) {
        threats.push({
          type: threat_type,
          severity: detection_result.severity,
          confidence: detection_result.confidence,
          indicators: detection_result.indicators,
          recommended_action: detection_result.action,
        });
      }
    }

    // 高リスク脅威の場合は即座にブロック
    const high_risk_threats = threats.filter((t) => t.severity === 'high');
    if (high_risk_threats.length > 0) {
      await this.logSecurityEvent('high_risk_threat_detected', {
        threats: high_risk_threats,
        request_details: this.sanitizeRequestForLogging(request),
        user_context: user_context?.user_id || 'anonymous',
      });
    }

    return {
      threats_detected: threats.length > 0,
      threat_count: threats.length,
      high_risk_count: high_risk_threats.length,
      threats,
      block_request: high_risk_threats.length > 0,
    };
  }

  // Bot管理とCAPTCHA統合
  async manageBotTraffic(request, user_context) {
    const bot_score = await this.calculateBotScore(request);
    const bot_management = {
      is_bot: bot_score.score > 80,
      bot_score: bot_score.score,
      bot_type: bot_score.type, // 'search_engine', 'malicious', 'good', 'unknown'
      action: 'allow',
      challenge_required: false,
    };

    // Bot種別による処理分岐
    switch (bot_score.type) {
      case 'search_engine':
        // 検索エンジンボットは許可（但し、レート制限適用）
        bot_management.action = 'allow';
        bot_management.apply_rate_limit = true;
        break;

      case 'malicious':
        // 悪意のあるボットはブロック
        bot_management.action = 'block';
        await this.addToBlocklist(request.cf?.ray_id, 'malicious_bot', 3600);
        break;

      case 'suspicious':
        // 疑わしいボットにはCAPTCHA チャレンジ
        if (bot_score.score > 60) {
          bot_management.action = 'challenge';
          bot_management.challenge_required = true;
          bot_management.challenge_type = 'turnstile';
        }
        break;

      case 'good':
      case 'unknown':
      default:
        // 良性・不明ボットは許可（監視継続）
        bot_management.action = 'allow';
        break;
    }

    // ボット分析結果をログ
    if (bot_management.is_bot) {
      await this.logSecurityEvent('bot_detected', {
        bot_score: bot_score.score,
        bot_type: bot_score.type,
        action: bot_management.action,
        user_agent: request.headers.get('User-Agent')?.substring(0, 200),
        cf_ray_id: request.cf?.ray_id,
      });
    }

    return bot_management;
  }

  // ユーティリティメソッド
  calculateRiskScore(request, user_context) {
    let risk_score = 0;

    // 地理的リスク
    const high_risk_countries = ['CN', 'RU', 'KP', 'IR'];
    if (high_risk_countries.includes(request.cf?.country)) {
      risk_score += 30;
    }

    // 認証状態
    if (!user_context) {
      risk_score += 20; // 未認証
    } else if (!user_context.verified_email) {
      risk_score += 10; // メール未認証
    }

    // アクセス時間（深夜・早朝アクセス）
    const hour = new Date().getUTCHours();
    if (hour >= 23 || hour <= 5) {
      risk_score += 5;
    }

    // 新規IPアドレス
    const client_ip = request.headers.get('CF-Connecting-IP');
    if (user_context && !this.isKnownIP(client_ip, user_context.user_id)) {
      risk_score += 15;
    }

    return Math.min(100, risk_score);
  }

  getClientIdentifier(request, user_context) {
    // 認証済みユーザーはuser_id、未認証はIP+フィンガープリント
    if (user_context?.user_id) {
      return `user:${user_context.user_id}`;
    }

    const ip = request.headers.get('CF-Connecting-IP');
    const user_agent = request.headers.get('User-Agent') || 'unknown';
    const fingerprint = btoa(`${ip}:${user_agent}`).substring(0, 16);

    return `anon:${fingerprint}`;
  }

  async validateJWT(token) {
    try {
      // JWT署名検証とペイロード取得
      const jwt_payload = await this.verifyJWTSignature(token);

      // トークン有効期限チェック
      if (jwt_payload.exp < Date.now() / 1000) {
        return { valid: false, reason: 'token_expired' };
      }

      // セキュリティレベル決定
      const security_level = this.determineSecurityLevel(jwt_payload);

      return {
        valid: true,
        payload: jwt_payload,
        security_level,
      };
    } catch (error) {
      return { valid: false, reason: error.message };
    }
  }

  detectSQLInjection(request) {
    const sql_patterns = [
      /(\bUNION\b.*\bSELECT\b)/i,
      /(\bSELECT\b.*\bFROM\b.*\bWHERE\b)/i,
      /(\bINSERT\b.*\bINTO\b)/i,
      /(\bDELETE\b.*\bFROM\b)/i,
      /(\bDROP\b.*\bTABLE\b)/i,
      /(\'.*(\bOR\b|\bAND\b).*\')/i,
      /(\-\-|\#|\/\*|\*\/)/,
    ];

    const suspicious_params = [];
    const url = new URL(request.url);

    // URLパラメータチェック
    url.searchParams.forEach((value, key) => {
      for (const pattern of sql_patterns) {
        if (pattern.test(value)) {
          suspicious_params.push({
            param: key,
            value,
            pattern: pattern.source,
          });
        }
      }
    });

    return {
      detected: suspicious_params.length > 0,
      severity: suspicious_params.length > 2 ? 'high' : 'medium',
      confidence: suspicious_params.length * 25,
      indicators: suspicious_params,
      action: suspicious_params.length > 0 ? 'block' : 'allow',
    };
  }

  classifyData(data) {
    const data_str = JSON.stringify(data).toLowerCase();

    // PII (個人識別情報) 検出
    const pii_patterns = {
      email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/,
      phone: /(\+\d{1,3}[- ]?)?\d{10}/,
      ssn: /\b\d{3}-\d{2}-\d{4}\b/,
      credit_card: /\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/,
    };

    let classification = 'public';

    for (const [type, pattern] of Object.entries(pii_patterns)) {
      if (pattern.test(data_str)) {
        classification = 'pii';
        break;
      }
    }

    // API key, token 検出
    const secret_patterns = [
      /api[_-]?key/i,
      /secret/i,
      /token/i,
      /password/i,
      /private[_-]?key/i,
    ];

    for (const pattern of secret_patterns) {
      if (pattern.test(data_str)) {
        classification = 'secret';
        break;
      }
    }

    return classification;
  }

  getEncryptionConfig(classification) {
    const configs = {
      public: { encrypt: false },
      internal: {
        encrypt: true,
        algorithm: 'AES-GCM',
        key_version: 'v1',
        key: this.encryption_key,
      },
      pii: {
        encrypt: true,
        algorithm: 'AES-GCM',
        key_version: 'v1',
        key: this.encryption_key,
        additional_protection: true,
      },
      secret: {
        encrypt: true,
        algorithm: 'AES-GCM',
        key_version: 'v1',
        key: this.encryption_key,
        additional_protection: true,
        audit_log: true,
      },
    };

    return configs[classification] || configs['internal'];
  }

  async logSecurityEvent(event_type, details) {
    const security_log = {
      timestamp: Date.now(),
      event_type,
      severity: this.getEventSeverity(event_type),
      details,
      source: 'edge_security_manager',
    };

    // セキュリティログをKVに保存
    const log_key = `security_log:${Date.now()}:${crypto.randomUUID()}`;
    await this.kv.put(log_key, JSON.stringify(security_log), {
      expirationTtl: 30 * 24 * 3600, // 30日保持
    });

    // 重要度の高いイベントは即座に通知
    if (
      security_log.severity === 'critical' ||
      security_log.severity === 'high'
    ) {
      await this.sendSecurityAlert(security_log);
    }
  }
}

// セキュリティ設定例
export const securityConfig = {
  cloudflare_access: {
    applications: [
      {
        name: 'AutoForgeNexus Admin Panel',
        domain: 'admin.autoforgenexus.com',
        policies: [
          {
            name: 'Admin Access',
            decision: 'allow',
            include: [
              { email_domain: 'autoforgenexus.com' },
              { email: ['admin@autoforgenexus.com'] },
            ],
            require: [{ mfa: true }, { country: ['US', 'JP', 'GB'] }],
          },
        ],
      },
      {
        name: 'AutoForgeNexus API Management',
        domain: 'api-admin.autoforgenexus.com',
        policies: [
          {
            name: 'Developer Access',
            decision: 'allow',
            include: [{ github: { teams: ['autoforgenexus/developers'] } }],
          },
        ],
      },
    ],
  },
  waf_rules: [
    {
      description: 'Block suspicious SQL injection patterns',
      expression:
        '(http.request.uri.query contains "union select") or (http.request.uri.query contains "drop table")',
      action: 'block',
    },
    {
      description: 'Rate limit API endpoints',
      expression: '(http.request.uri.path matches "^/api/.*")',
      action: 'challenge',
      rate_limit: {
        threshold: 100,
        period: 60,
      },
    },
  ],
};
```

### Terraform設定（セキュリティリソース）

```hcl
# Cloudflare Access Application
resource "cloudflare_access_application" "admin_panel" {
  zone_id          = var.zone_id
  name             = "AutoForgeNexus Admin Panel"
  domain           = "admin.autoforgenexus.com"
  type             = "self_hosted"
  session_duration = "24h"

  cors_headers {
    allowed_methods = ["GET", "POST", "OPTIONS"]
    allowed_origins = ["https://autoforgenexus.com"]
    max_age         = 600
  }
}

# Access Policy
resource "cloudflare_access_policy" "admin_policy" {
  application_id = cloudflare_access_application.admin_panel.id
  zone_id        = var.zone_id
  name           = "Admin Access Policy"
  precedence     = 1
  decision       = "allow"

  include {
    email_domain = ["autoforgenexus.com"]
  }

  require {
    mfa = true
  }

  require {
    geo = ["US", "JP", "GB", "DE"]
  }
}

# WAF Custom Rules
resource "cloudflare_ruleset" "waf_security" {
  zone_id     = var.zone_id
  name        = "AutoForgeNexus Security Rules"
  description = "Custom WAF rules for AutoForgeNexus"
  kind        = "zone"
  phase       = "http_request_firewall_custom"

  rules {
    action = "block"
    action_parameters {
      response {
        status_code = 403
        content     = "{\"error\": \"Request blocked by security policy\"}"
        content_type = "application/json"
      }
    }
    expression = "(http.request.uri.query contains \"union select\") or (http.request.uri.query contains \"drop table\") or (http.request.uri.query contains \"<script\")"
    description = "Block SQL injection and XSS attempts"
  }

  rules {
    action = "challenge"
    expression = "(cf.bot_management.score lt 30) and (http.request.uri.path matches \"^/api/.*\")"
    description = "Challenge suspicious bots on API endpoints"
  }
}

# Rate Limiting
resource "cloudflare_rate_limit" "api_rate_limit" {
  zone_id   = var.zone_id
  threshold = 100
  period    = 60
  match {
    request {
      url_pattern = "*.autoforgenexus.com/api/*"
      schemes     = ["HTTPS"]
      methods     = ["GET", "POST", "PUT", "DELETE"]
    }
  }
  action {
    mode    = "challenge"
    timeout = 86400
  }
}
```

### KPI・メトリクス

- セキュリティインシデント検出率: 99%+
- false positive率: < 5%
- 脅威ブロック成功率: > 98%
- アクセス制御精度: 100%
- 平均脅威対応時間: < 30秒
- データ暗号化カバレッジ: 100% (PII/秘匿情報)

## まとめ

これらの7つのベストプラクティスにより、AutoForgeNexusのエッジコンピューティング環境において以下を実現します：

### 期待効果

- **パフォーマンス**: P95レスポンス時間 < 200ms
- **可用性**: 99.9%+ SLA達成
- **スケーラビリティ**: グローバル分散による無制限スケーリング
- **セキュリティ**: ゼロトラストによる包括的保護
- **運用効率**: 自動化による90%の運用工数削減
- **コスト最適化**: エッジキャッシングによる50%のインフラコスト削減

### 実装優先順位

1. **Phase 1** (即座): GitOps Pipeline + IaC基盤
2. **Phase 2** (1-2週間): Edge Caching + Multi-Region LLM
3. **Phase 3** (2-4週間): Observability + Traffic Routing
4. **Phase 4** (継続的): Zero Trust Security強化

これらの実装により、AIプロンプト最適化プラットフォームとしての要求仕様（レイテンシ、スケーラビリティ、セキュリティ）を全て満たし、グローバル展開に対応できる堅牢なエッジインフラストラクチャを構築できます。
