# Infrastructure CLAUDE.md

このファイルは、AutoForgeNexusのインフラストラクチャを作業する際のClaude Code
(claude.ai/code) へのガイダンスを提供します。

## 🎯 インフラストラクチャ概要

Cloudflareエコシステムを中心としたエッジファーストインフラストラクチャ。99.9%可用性とグローバル低レイテンシを実現。

## 🏗️ アーキテクチャ

### ディレクトリ構造

```
infrastructure/
├── cloudflare/          # Cloudflare設定
│   ├── workers/        # Workers設定（バックエンドAPI）
│   │   ├── wrangler.toml
│   │   └── src/
│   ├── pages/          # Pages設定（フロントエンド）
│   │   ├── pages-config.json
│   │   └── deploy.sh
│   └── security-worker.js  # セキュリティミドルウェア
├── monitoring/          # 監視・観測性
│   ├── cloudflare-monitoring.sh
│   ├── alerts-config.yaml
│   ├── monitoring-config.json
│   ├── prometheus-security.yml
│   └── security-performance.yml
├── scripts/            # デプロイメント・運用スクリプト
│   ├── deploy.sh      # 環境別デプロイ
│   ├── rollback.sh    # ロールバック
│   └── security-check.sh  # セキュリティチェック
└── docker/            # Docker設定（将来実装）
```

## 🌐 Cloudflare構成

### Workers（バックエンドAPI）

#### wrangler.toml主要設定

```toml
name = "autoforgenexus"
main = "src/main.py"
compatibility_date = "2025-01-07"
compatibility_flags = ["python_workers", "nodejs_compat"]

[env.production]
vars = { ENVIRONMENT = "production" }
routes = [{ pattern = "api.autoforgenexus.com/*", zone_name = "autoforgenexus.com" }]

[env.staging]
name = "autoforgenexus-staging"
vars = { ENVIRONMENT = "staging" }
```

#### Python Workers設定

```toml
[[pyodide.packages]]
package = ["fastapi", "pydantic", "sqlalchemy", "redis", "langchain"]
```

### Pages（フロントエンド）

#### デプロイ設定

```json
{
  "projectName": "autoforge-nexus-frontend",
  "framework": "next",
  "buildCommand": "pnpm build && pnpm export",
  "outputDirectory": "out"
}
```

### セキュリティ設定

#### CSPヘッダー

```javascript
const CSP_HEADER = `
  default-src 'self';
  script-src 'self' 'unsafe-eval' 'unsafe-inline' *.clerk.dev;
  style-src 'self' 'unsafe-inline';
  connect-src 'self' *.turso.io *.clerk.dev;
`;
```

## 📊 監視システム

### 監視スタック

- **メトリクス**: Cloudflare Analytics + Prometheus
- **ログ**: 構造化JSON + Cloudflare Logpush
- **トレース**: LangFuse (LLM専用)
- **アラート**: Discord Webhook + Email

### アラート設定（alerts-config.yaml）

```yaml
alerts:
  - name: high_error_rate
    condition: error_rate > 0.05
    severity: critical
    action: notify_oncall

  - name: slow_response_time
    condition: p95_latency > 2000ms
    severity: high
    action: notify_team

  - name: low_availability
    condition: availability < 0.999
    severity: critical
    action: page_oncall
```

### ヘルスチェック

```bash
# エッジロケーション（5拠点）
- US-East (iad)
- US-West (lax)
- Europe (lhr)
- Asia (nrt)
- Australia (syd)
```

## 🚀 デプロイメントコマンド

### 環境別デプロイ

```bash
# 開発環境
./infrastructure/scripts/deploy.sh development

# ステージング環境
./infrastructure/scripts/deploy.sh staging

# 本番環境（承認必要）
./infrastructure/scripts/deploy.sh production
```

### ロールバック

```bash
# バージョン一覧表示
./infrastructure/scripts/rollback.sh staging

# 特定バージョンへロールバック
./infrastructure/scripts/rollback.sh staging v1.2.3

# コンポーネント指定
./infrastructure/scripts/rollback.sh production v1.2.3 backend
```

### 監視セットアップ

```bash
# 監視設定の初期化
cd infrastructure/monitoring
./cloudflare-monitoring.sh setup

# アラート設定の適用
./cloudflare-monitoring.sh apply-alerts

# ダッシュボード作成
./cloudflare-monitoring.sh create-dashboards
```

## ⚙️ 環境変数管理

### 必須環境変数

```env
# Cloudflare
CLOUDFLARE_API_TOKEN=<your_cloudflare_api_token>
CLOUDFLARE_ACCOUNT_ID=<your_cloudflare_account_id>
CLOUDFLARE_ZONE_ID=<your_cloudflare_zone_id>

# Workers
CLOUDFLARE_WORKERS_URL=https://api.autoforgenexus.com
STAGING_WORKERS_URL=https://staging-api.autoforgenexus.com
DEV_WORKERS_URL=http://localhost:8787

# Pages
CLOUDFLARE_PAGES_URL=https://autoforge-nexus-frontend.pages.dev

# 監視
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx
ALERT_EMAIL=oncall@autoforgenexus.com
```

### シークレット管理

```bash
# Workersシークレット設定
wrangler secret put TURSO_DATABASE_URL
wrangler secret put TURSO_AUTH_TOKEN
wrangler secret put CLERK_SECRET_KEY
wrangler secret put OPENAI_API_KEY

# 環境別設定
wrangler secret put --env staging TURSO_DATABASE_URL
```

## 🔒 セキュリティ実装

### WAFルール

```javascript
// DDoS対策
if (request.cf.threatScore > 50) {
  return new Response('Blocked', { status: 403 });
}

// レート制限
const rateLimit = await env.RATE_LIMITER.get(clientIP);
if (rateLimit > 60) {
  return new Response('Too Many Requests', { status: 429 });
}
```

### ゼロトラスト設定

```yaml
# Cloudflare Access設定
policies:
  - name: admin_only
    include:
      - email: { domain: 'autoforgenexus.com' }
    require:
      - mfa: true
```

## 📈 パフォーマンス最適化

### Workersキャッシュ

```javascript
// KVキャッシュ
const cached = await env.CACHE.get(key);
if (cached) return new Response(cached);

// Durable Objects
const id = env.COUNTER.idFromName(name);
const stub = env.COUNTER.get(id);
```

### エッジ最適化

```javascript
// 画像最適化
const imageURL = new URL(request.url);
imageURL.searchParams.set('format', 'webp');
imageURL.searchParams.set('quality', '85');
```

## 🎯 運用手順

### 日次運用

1. **ヘルスチェック確認**

   ```bash
   curl https://api.autoforgenexus.com/health
   ```

2. **メトリクス確認**

   - Cloudflare Dashboard
   - Grafanaダッシュボード

3. **ログレビュー**
   ```bash
   wrangler tail --env production
   ```

### インシデント対応

1. **アラート受信**

   - Discord通知確認
   - 重要度判定

2. **初期対応**

   ```bash
   # ステータス確認
   ./scripts/health-check.sh

   # ログ調査
   wrangler tail --env production --search "error"
   ```

3. **ロールバック判断**
   ```bash
   ./scripts/rollback.sh production previous
   ```

## 📊 SLO/SLI

### 可用性目標

- **SLO**: 99.9%（月間43.2分のダウンタイム許容）
- **測定**: Cloudflare Analytics

### レイテンシ目標

- **P50**: < 100ms
- **P95**: < 500ms
- **P99**: < 2000ms

### エラー率目標

- **SLO**: < 0.5%
- **測定**: 5xx エラー率

## 🚨 注意事項

1. **本番デプロイ**: 必ず2名以上の承認
2. **シークレット**: 絶対にコミットしない
3. **ロールバック**: 問題発生時は即座に実行
4. **キャッシュ**: TTLを適切に設定
5. **コスト**: Workers呼び出し数を監視

## 📝 トラブルシューティング

### よくある問題

#### Workers起動エラー

```bash
# ログ確認
wrangler tail --env production

# 設定検証
wrangler deploy --dry-run
```

#### Pages ビルド失敗

```bash
# ビルドログ確認
wrangler pages deployment list --project-name autoforge-nexus-frontend

# ローカルビルドテスト
cd frontend && pnpm build && pnpm export
```

#### 監視アラート過多

```bash
# アラート設定確認
cat infrastructure/monitoring/alerts-config.yaml

# 閾値調整
vim alerts-config.yaml
./cloudflare-monitoring.sh apply-alerts
```

## 🔗 関連ドキュメント

- [プロジェクトCLAUDE.md](../CLAUDE.md)
- [デプロイメントガイド](../docs/setup/deployment.md)
- [Cloudflare公式ドキュメント](https://developers.cloudflare.com/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)

## 📊 現在の実装状況（2025年9月29日更新）

### Phase 2: インフラ・監視基盤 ✅ 完了 (100%)

#### 完了項目

- Docker環境構築（docker-compose.dev.yml）
- Cloudflare Workers/Pages設定
- Prometheus/Grafana/LangFuse監視スタック
- GitHub Actions CI/CD最適化
  - 共有ワークフロー実装で52.3%のコスト削減
  - 無料枠使用量: 730分/月（36.5%）
  - セキュリティ強化: CodeQL、TruffleHog統合

#### セキュリティ強化実装

- CodeQL静的解析（Python/TypeScript）
- TruffleHog秘密情報検出
- 監査ログシステム（365日保存）
- DORAメトリクス自動収集

#### デプロイメント戦略

- ブルーグリーンデプロイメント準備
- 自動ロールバック機構
- Cloudflare CDN最適化
