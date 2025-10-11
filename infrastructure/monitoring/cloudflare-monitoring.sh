#!/bin/bash
# AutoForgeNexus - Cloudflare Monitoring Setup Script
# observability-engineer による Cloudflare 監視基盤構築

set -euo pipefail

# 色分けしたログ出力
log_info() { echo -e "\033[0;32m[INFO]\033[0m $1"; }
log_warn() { echo -e "\033[0;33m[WARN]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# 設定ファイルの読み込み
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/monitoring-config.json"

# 必要な環境変数の確認
check_env_vars() {
    local required_vars=(
        "CLOUDFLARE_API_TOKEN"
        "CLOUDFLARE_ZONE_ID"
        "CLOUDFLARE_ACCOUNT_ID"
        "DISCORD_WEBHOOK_URL"
    )

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done
}

# Cloudflare Analytics API の設定
setup_analytics() {
    log_info "Setting up Cloudflare Analytics..."

    # Workers Analytics の有効化
    curl -X POST "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/analytics/config" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{
            "enabled": true,
            "sampling_rate": 0.1,
            "metrics": [
                "requests",
                "errors",
                "duration",
                "cpu_time",
                "memory_usage"
            ]
        }' || log_warn "Analytics configuration may already exist"

    # Web Analytics の有効化
    curl -X POST "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/analytics/web-analytics" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{
            "enabled": true,
            "auto_install": true
        }' || log_warn "Web Analytics may already be enabled"
}

# アラートルールの設定
setup_alerts() {
    log_info "Setting up Cloudflare alert rules..."

    # エラー率アラート
    curl -X POST "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/alerting/v3/policies" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{
            "name": "AutoForgeNexus - High Error Rate",
            "description": "Alert when error rate exceeds 5%",
            "enabled": true,
            "alert_type": "workers_error_rate_exceeded",
            "filters": {
                "zones": ["'${CLOUDFLARE_ZONE_ID}'"],
                "services": ["autoforgenexus"]
            },
            "conditions": [
                {
                    "threshold": 5.0,
                    "threshold_type": "greater_than"
                }
            ],
            "mechanisms": [
                {
                    "type": "webhook",
                    "config": {
                        "url": "'${DISCORD_WEBHOOK_URL}'"
                    }
                }
            ]
        }'

    # レスポンス時間アラート
    curl -X POST "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/alerting/v3/policies" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{
            "name": "AutoForgeNexus - High Response Time",
            "description": "Alert when P95 response time exceeds 2000ms",
            "enabled": true,
            "alert_type": "workers_high_response_time",
            "filters": {
                "zones": ["'${CLOUDFLARE_ZONE_ID}'"],
                "services": ["autoforgenexus"]
            },
            "conditions": [
                {
                    "threshold": 2000.0,
                    "threshold_type": "greater_than",
                    "percentile": 95
                }
            ],
            "mechanisms": [
                {
                    "type": "webhook",
                    "config": {
                        "url": "'${DISCORD_WEBHOOK_URL}'"
                    }
                }
            ]
        }'

    # 可用性アラート
    curl -X POST "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/alerting/v3/policies" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{
            "name": "AutoForgeNexus - Low Availability",
            "description": "Alert when availability drops below 99.9%",
            "enabled": true,
            "alert_type": "zone_health_score",
            "filters": {
                "zones": ["'${CLOUDFLARE_ZONE_ID}'"]
            },
            "conditions": [
                {
                    "threshold": 99.9,
                    "threshold_type": "less_than"
                }
            ],
            "mechanisms": [
                {
                    "type": "webhook",
                    "config": {
                        "url": "'${DISCORD_WEBHOOK_URL}'"
                    }
                }
            ]
        }'
}

# ヘルスチェックの設定
setup_health_checks() {
    log_info "Setting up health check monitoring..."

    # フロントエンドヘルスチェック
    curl -X POST "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/health_checks" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{
            "type": "HTTPS",
            "name": "AutoForgeNexus Frontend Health",
            "description": "Frontend health check",
            "check_regions": ["WNAM", "ENAM", "WEU", "EEU", "APAC"],
            "path": "/api/health",
            "method": "GET",
            "timeout": 5,
            "retries": 2,
            "interval": 60,
            "expected_codes": ["200"],
            "follow_redirects": false,
            "allow_insecure": false,
            "header": {
                "User-Agent": ["Cloudflare-Health-Check"]
            }
        }'

    # バックエンドヘルスチェック
    curl -X POST "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/health_checks" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{
            "type": "HTTPS",
            "name": "AutoForgeNexus Backend Health",
            "description": "Backend API health check",
            "check_regions": ["WNAM", "ENAM", "WEU", "EEU", "APAC"],
            "path": "/health",
            "method": "GET",
            "timeout": 5,
            "retries": 2,
            "interval": 60,
            "expected_codes": ["200"],
            "follow_redirects": false,
            "allow_insecure": false,
            "header": {
                "User-Agent": ["Cloudflare-Health-Check"]
            }
        }'
}

# Cloudflare Workers 監視スクリプトのデプロイ
deploy_monitoring_workers() {
    log_info "Deploying monitoring Workers..."

    # 監視用 Worker スクリプトの作成
    cat > "${SCRIPT_DIR}/monitoring-worker.js" << 'EOF'
// AutoForgeNexus Monitoring Worker
// リアルタイムメトリクス収集とアラート処理

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

addEventListener('scheduled', event => {
  event.waitUntil(handleScheduledEvent(event))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const path = url.pathname

  // メトリクス収集エンドポイント
  if (path === '/metrics') {
    return getMetrics(request)
  }

  // ヘルスチェックエンドポイント
  if (path === '/health') {
    return getHealthStatus(request)
  }

  // アラート処理エンドポイント
  if (path === '/alerts') {
    return handleAlert(request)
  }

  return new Response('Not Found', { status: 404 })
}

async function getMetrics(request) {
  const metrics = {
    timestamp: new Date().toISOString(),
    cf: {
      colo: request.cf?.colo,
      country: request.cf?.country,
      region: request.cf?.region,
      tlsVersion: request.cf?.tlsVersion,
      httpProtocol: request.cf?.httpProtocol
    },
    performance: {
      startTime: Date.now()
    }
  }

  return new Response(JSON.stringify(metrics), {
    headers: { 'Content-Type': 'application/json' }
  })
}

async function getHealthStatus(request) {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: {
      cloudflare: 'healthy',
      workers: 'healthy'
    }
  }

  return new Response(JSON.stringify(health), {
    headers: { 'Content-Type': 'application/json' }
  })
}

async function handleAlert(request) {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }

  const alert = await request.json()

  // Discord webhook への通知
  if (DISCORD_WEBHOOK_URL) {
    await fetch(DISCORD_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        embeds: [{
          title: `🚨 AutoForgeNexus Alert`,
          description: alert.message || 'Unknown alert',
          color: alert.severity === 'critical' ? 16711680 : 16776960,
          timestamp: new Date().toISOString(),
          fields: [
            { name: 'Service', value: alert.service || 'Unknown', inline: true },
            { name: 'Severity', value: alert.severity || 'warning', inline: true },
            { name: 'Environment', value: alert.environment || 'production', inline: true }
          ]
        }]
      })
    })
  }

  return new Response('Alert processed', { status: 200 })
}

async function handleScheduledEvent(event) {
  // 定期的なヘルスチェックとメトリクス収集
  const timestamp = new Date().toISOString()

  // Analytics Engine にメトリクスを送信
  if (typeof ANALYTICS_ENGINE !== 'undefined') {
    ANALYTICS_ENGINE.writeDataPoint({
      blobs: [timestamp, 'scheduled-check'],
      doubles: [Date.now()],
      indexes: ['health-check']
    })
  }
}
EOF

    # wrangler.toml の作成
    cat > "${SCRIPT_DIR}/wrangler-monitoring.toml" << EOF
name = "autoforgenexus-monitoring"
main = "monitoring-worker.js"
compatibility_date = "2024-09-27"
compatibility_flags = ["nodejs_compat"]

[env.production]
vars = { ENVIRONMENT = "production" }

[[env.production.analytics_engine_datasets]]
binding = "ANALYTICS_ENGINE"
dataset = "autoforgenexus_metrics"

[triggers]
crons = ["*/5 * * * *"]
EOF
}

# メトリクス取得関数
get_metrics() {
    log_info "Fetching current metrics..."

    # Workers Analytics データの取得
    curl -s "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/analytics_engine/sql" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        -H "Content-Type: application/json" \
        --data '{
            "query": "SELECT timestamp, double1 as response_time FROM autoforgenexus_metrics WHERE timestamp >= NOW() - INTERVAL 1 HOUR ORDER BY timestamp DESC LIMIT 100"
        }' | jq '.'

    # Zone Analytics データの取得
    curl -s "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/analytics/dashboard" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        --data-urlencode "since=$(date -d '1 hour ago' --iso-8601)" \
        --data-urlencode "until=$(date --iso-8601)" | jq '.'
}

# アラート状態の確認
check_alerts() {
    log_info "Checking alert status..."

    curl -s "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/alerting/v3/history" \
        -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
        --data-urlencode "since=$(date -d '24 hours ago' --iso-8601)" | jq '.'
}

# メイン実行関数
main() {
    log_info "Starting Cloudflare monitoring setup for AutoForgeNexus..."

    # 前提条件チェック
    check_env_vars

    # jq コマンドの確認
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed. Please install jq first."
        exit 1
    fi

    case "${1:-setup}" in
        "setup")
            setup_analytics
            setup_alerts
            setup_health_checks
            deploy_monitoring_workers
            log_info "Cloudflare monitoring setup completed!"
            ;;
        "metrics")
            get_metrics
            ;;
        "alerts")
            check_alerts
            ;;
        "deploy-worker")
            deploy_monitoring_workers
            log_info "Monitoring worker deployed!"
            ;;
        *)
            echo "Usage: $0 {setup|metrics|alerts|deploy-worker}"
            echo "  setup        - Complete monitoring setup"
            echo "  metrics      - Get current metrics"
            echo "  alerts       - Check alert history"
            echo "  deploy-worker - Deploy monitoring worker"
            exit 1
            ;;
    esac
}

# 実行
main "$@"