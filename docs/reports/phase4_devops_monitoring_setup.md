# Phase 4 DevOps監視セットアップ実装計画

## 🎯 概要

Phase 4データベース環境の運用品質向上のため、包括的な監視・観測性スタックの実装計画です。

## 📊 実装優先度

### 🔴 Tier 1（即座実装必須）
1. **アプリケーションメトリクス**: Prometheus + Grafana
2. **データベース監視**: Turso接続・パフォーマンス
3. **基本アラート**: サービス停止、エラー率急増
4. **ヘルスチェック**: 多層ヘルスチェック実装

### 🟡 Tier 2（2週間以内）
1. **LLM監視**: LangFuse統合
2. **ログ集約**: 構造化ログ + Loki
3. **SLI/SLO定義**: 可用性・レスポンス時間
4. **コスト監視**: LLMプロバイダー使用量

### 🟢 Tier 3（1ヶ月以内）
1. **分散トレーシング**: OpenTelemetry
2. **セキュリティ監視**: 異常検知
3. **予測アラート**: 容量・パフォーマンス予測

## 🏗️ 技術実装

### Prometheus設定
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: autoforge-nexus
    environment: ${ENVIRONMENT}

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # FastAPI メトリクス
  - job_name: 'autoforge-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # Redis メトリクス
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  # Node.js メトリクス
  - job_name: 'autoforge-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/api/metrics'
```

### Grafana ダッシュボード
```json
{
  "dashboard": {
    "title": "AutoForgeNexus - Phase 4 Database Operations",
    "panels": [
      {
        "title": "Database Connection Pool",
        "type": "graph",
        "targets": [
          {
            "expr": "sqlalchemy_pool_size{instance=\"backend:8000\"}",
            "legendFormat": "Pool Size"
          },
          {
            "expr": "sqlalchemy_pool_checked_out{instance=\"backend:8000\"}",
            "legendFormat": "Active Connections"
          }
        ]
      },
      {
        "title": "API Response Times (P95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket{job=\"autoforge-backend\"})",
            "legendFormat": "P95 Response Time"
          }
        ]
      },
      {
        "title": "Turso Query Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "turso_query_duration_seconds{quantile=\"0.95\"}",
            "legendFormat": "P95 Query Time"
          }
        ]
      }
    ]
  }
}
```

### アラートルール
```yaml
# monitoring/rules/database.yml
groups:
  - name: database.rules
    rules:
      - alert: DatabaseConnectionHigh
        expr: sqlalchemy_pool_checked_out / sqlalchemy_pool_size > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool utilization high"
          description: "Connection pool is {{ $value | humanizePercentage }} full"

      - alert: DatabaseQuerySlow
        expr: histogram_quantile(0.95, turso_query_duration_seconds_bucket) > 1.0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database queries are slow"
          description: "P95 query time is {{ $value }}s"

      - alert: APIResponseSlow
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket{job="autoforge-backend"}) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "API response time degraded"
          description: "P95 response time is {{ $value }}s"
```

## 🔧 実装手順

### Step 1: 基本監視スタック
```bash
# 1. 監視設定ファイル作成
mkdir -p monitoring/{prometheus,grafana,alertmanager}

# 2. Docker Compose監視スタック
docker-compose -f docker-compose.monitoring.yml up -d

# 3. ダッシュボード導入
curl -X POST http://grafana:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @monitoring/grafana/autoforge-dashboard.json
```

### Step 2: アプリケーション監視
```python
# backend/src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# メトリクス定義
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
DB_CONNECTIONS = Gauge('db_connections_active', 'Active database connections')

class MonitoringMiddleware:
    async def __call__(self, request, call_next):
        start_time = time.time()

        response = await call_next(request)

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        REQUEST_LATENCY.observe(time.time() - start_time)

        return response
```

### Step 3: SLI/SLO定義
```yaml
# monitoring/slos.yml
objectives:
  availability:
    target: 99.9%
    measurement: "sum(rate(http_requests_total{status!~'5..'}[5m])) / sum(rate(http_requests_total[5m]))"

  latency:
    target: 95%  # 95%のリクエストが500ms以下
    measurement: "histogram_quantile(0.95, http_request_duration_seconds_bucket) < 0.5"

  database_performance:
    target: 99%   # 99%のクエリが1秒以下
    measurement: "histogram_quantile(0.99, turso_query_duration_seconds_bucket) < 1.0"
```

## 📱 アラート通知

### Discord統合
```python
# monitoring/alerting/discord_webhook.py
import httpx
import json

async def send_alert(webhook_url: str, alert_data: dict):
    embed = {
        "title": f"🚨 {alert_data['alertname']}",
        "description": alert_data.get('description', ''),
        "color": 15158332,  # Red
        "fields": [
            {"name": "Environment", "value": alert_data.get('environment'), "inline": True},
            {"name": "Severity", "value": alert_data.get('severity'), "inline": True},
            {"name": "Instance", "value": alert_data.get('instance'), "inline": True}
        ],
        "timestamp": alert_data.get('timestamp')
    }

    payload = {"embeds": [embed]}

    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json=payload)
```

## 🎯 運用手順

### デイリーチェック
```bash
#!/bin/bash
# scripts/daily_health_check.sh

echo "=== AutoForgeNexus Daily Health Check ==="

# 1. サービス稼働状況
curl -f http://localhost:8000/health || echo "❌ Backend down"
curl -f http://localhost:3000 || echo "❌ Frontend down"

# 2. データベース接続
python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); engine.connect()" || echo "❌ DB connection failed"

# 3. Redis状況
redis-cli ping || echo "❌ Redis down"

# 4. メトリクス確認
curl -f http://localhost:9090/-/healthy || echo "❌ Prometheus down"
curl -f http://localhost:3001/api/health || echo "❌ Grafana down"

echo "=== Health Check Complete ==="
```

### ウィークリーレポート
```python
# scripts/weekly_report.py
import asyncio
from datetime import datetime, timedelta

async def generate_weekly_report():
    # SLI達成率計算
    availability = await get_metric_value("availability_sli")
    latency_p95 = await get_metric_value("latency_p95")

    report = f"""
    ## Weekly SLI Report - {datetime.now().strftime('%Y-W%U')}

    ### Availability
    - Target: 99.9%
    - Actual: {availability:.2%}
    - Status: {'✅ Met' if availability >= 0.999 else '❌ Missed'}

    ### Performance
    - P95 Latency Target: <500ms
    - Actual: {latency_p95:.0f}ms
    - Status: {'✅ Met' if latency_p95 < 500 else '❌ Missed'}
    """

    # Discord通知
    await send_weekly_report(report)
```

## 💰 コスト最適化

### リソース監視
```yaml
# Cloudflare Workers使用量監視
cloudflare_workers_requests_total:
  target: <100,000/day
  alert_threshold: 80,000/day

# Turso使用量監視
turso_rows_read_total:
  target: <1M/day
  alert_threshold: 800K/day
```

## 📈 継続改善

### メトリクス収集の拡張
1. **ビジネスメトリクス**: プロンプト作成数、評価実行数
2. **ユーザーエクスペリエンス**: Core Web Vitals、エラー率
3. **セキュリティ**: 認証失敗、レート制限達成
4. **コスト**: LLMプロバイダー別使用量、Cloudflare使用量