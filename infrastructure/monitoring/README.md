# AutoForgeNexus Monitoring and Logging Infrastructure

observability-engineer による包括的監視・ログ基盤の実装完了

## 📊 概要

このディレクトリには、AutoForgeNexus の包括的な監視・ログ・観測可能性インフラストラクチャが含まれています。

### 実装済みコンポーネント

1. **Cloudflare 監視システム** (`cloudflare-monitoring.sh`)
2. **構造化ログ設定** (`logging-config.json`)
3. **アラート設定** (`alerts-config.yaml`)
4. **バックエンドヘルスチェック** (`../backend/src/monitoring.py`)
5. **フロントエンド監視** (`../frontend/src/lib/monitoring/`)
6. **観測可能性ミドルウェア** (backend/frontend)
7. **監視設定** (`monitoring-config.json`)

## 🚀 セットアップ手順

### 1. 環境変数設定

```bash
# .env ファイルに以下を追加
CLOUDFLARE_API_TOKEN=your_api_token
CLOUDFLARE_ZONE_ID=your_zone_id
CLOUDFLARE_ACCOUNT_ID=your_account_id
DISCORD_WEBHOOK_URL=your_discord_webhook
LANGFUSE_HOST=https://your-langfuse-instance.com
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
TURSO_DATABASE_URL=your_turso_url
TURSO_AUTH_TOKEN=your_turso_token
REDIS_URL=your_redis_url
```

### 2. Cloudflare 監視セットアップ

```bash
# 監視インフラ全体のセットアップ
./infrastructure/monitoring/cloudflare-monitoring.sh setup

# メトリクス確認
./infrastructure/monitoring/cloudflare-monitoring.sh metrics

# アラート状態確認
./infrastructure/monitoring/cloudflare-monitoring.sh alerts
```

### 3. バックエンド監視設定

```python
# FastAPI アプリケーションに追加
from src.middleware.observability import ObservabilityMiddleware, setup_observability_logging
from src.monitoring import health_checker

# ログ設定初期化
setup_observability_logging()

# ミドルウェア追加
app.add_middleware(ObservabilityMiddleware)

# ヘルスチェックエンドポイント
@app.get("/health")
async def health():
    return await health_checker.get_health_status()
```

### 4. フロントエンド監視設定

```typescript
// Next.js middleware.ts
import { observabilityMiddleware } from '@/middleware/observability';

export function middleware(request: NextRequest) {
  return observabilityMiddleware(request);
}

// アプリケーション初期化
import { monitor, initializeSessionTracking } from '@/lib/monitoring';

// セッション追跡開始
initializeSessionTracking();

// ユーザーID設定（ログイン後）
monitor.setUserId(user.id);
```

## 🔍 監視機能

### Cloudflare 監視

- **Analytics**: Workers・Pages・Web Analytics 有効化
- **Alerts**: エラー率・レスポンス時間・可用性アラート
- **Health Checks**: フロントエンド・バックエンドヘルスチェック
- **Real-time Metrics**: リアルタイムメトリクス収集

### バックエンド監視

- **Health Endpoints**:

  - `/health` - 包括的ヘルスチェック
  - `/health/ready` - Readiness Probe
  - `/health/live` - Liveness Probe
  - `/metrics` - Prometheus メトリクス

- **Dependencies Monitoring**:

  - Database (Turso) 接続状態
  - Redis 接続状態
  - LangFuse API 状態
  - 外部 LLM API 状態

- **System Metrics**:
  - CPU・メモリ・ディスク使用率
  - プロセス数・アップタイム
  - ロードアベレージ

### フロントエンド監視

- **Web Vitals**: LCP, FID, CLS, FCP, TTFB, INP
- **Error Tracking**: JavaScript エラー, Promise
  rejection, リソース読み込みエラー
- **Performance Tracking**: ナビゲーション・リソースタイミング
- **User Interactions**: クリック・スクロール・フォーム送信

### LLM 専用監視

- **Token Usage**: プロバイダー・モデル別使用量
- **Cost Tracking**: リアルタイムコスト監視
- **Quality Metrics**: レスポンス品質スコア
- **Latency Monitoring**: API 呼び出し時間

## 📈 メトリクス・アラート

### SLI/SLO 定義

| メトリクス | SLI           | SLO   | 時間枠 |
| ---------- | ------------- | ----- | ------ |
| 可用性     | HTTP 成功率   | 99.9% | 30日   |
| レイテンシ | P95 応答時間  | < 2秒 | 30日   |
| エラー率   | HTTP エラー率 | < 1%  | 30日   |
| LLM品質    | 品質スコア    | > 80% | 7日    |

### アラート設定

- **Critical**: システムダウン・データ損失 (5分以内対応)
- **High**: 主要機能障害・大幅な性能低下 (15分以内対応)
- **Medium**: 部分的障害・警告レベル (1時間以内対応)
- **Low**: 情報提供・将来的な問題予兆 (24時間以内対応)

## 🛠️ 運用コマンド

### 監視状態確認

```bash
# Cloudflare メトリクス取得
./infrastructure/monitoring/cloudflare-monitoring.sh metrics

# バックエンドヘルス確認
curl http://localhost:8000/health | jq '.'

# フロントエンドヘルス確認
curl http://localhost:3000/api/health | jq '.'
```

### ログ確認

```bash
# 構造化ログ確認
tail -f /var/log/autoforgenexus/backend.log | jq '.'

# エラーログのみ
tail -f /var/log/autoforgenexus/error.log | jq '.'

# 監査ログ
tail -f /var/log/autoforgenexus/audit.log | jq '.'
```

### トラブルシューティング

```bash
# 監視 Worker デプロイ
./infrastructure/monitoring/cloudflare-monitoring.sh deploy-worker

# アラート履歴確認
./infrastructure/monitoring/cloudflare-monitoring.sh alerts

# システムメトリクス確認
curl http://localhost:8000/metrics
```

## 🔐 セキュリティ・コンプライアンス

### データ保護

- **PII フィールド**: 自動マスキング・ハッシュ化
- **機密情報**: ヘッダー・ボディのサニタイズ
- **GDPR 準拠**: データポータビリティ・忘れられる権利

### データ保持

- **メトリクス**: 高解像度7日、中解像度30日、低解像度1年
- **ログ**: デバッグ1日、情報7日、警告30日、エラー90日、監査2年
- **トレース**: 詳細3日、サンプル30日、エラーのみ90日

## 📊 ダッシュボード

### Grafana ダッシュボード

1. **Overview**: システム全体の健全性
2. **LLM Analytics**: LLM 使用状況・コスト・品質
3. **Performance**: パフォーマンスメトリクス
4. **Security**: セキュリティイベント・認証状況

### アクセス

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001
- LangFuse: http://localhost:3002

## 🚀 自動化機能

### 自動インシデント対応

- 自動チケット作成
- 通知遅延設定
- エスカレーションポリシー

### コスト最適化

- 予算アラート
- 使用量レコメンデーション
- プロバイダー最適化提案

## 📝 カスタマイズ

### カスタムメトリクス追加

```python
# バックエンド
from src.monitoring import metrics_collector

metrics_collector.record_llm_metrics(
    provider="openai",
    model="gpt-4",
    tokens_used=150,
    cost=0.003,
    duration=2.5
)
```

```typescript
// フロントエンド
import { monitor } from '@/lib/monitoring';

monitor.recordCustomEvent('prompt_optimization', {
  promptId: 'abc123',
  improvement: 0.15,
  iterations: 3,
});
```

### アラート追加

`alerts-config.yaml` を編集して新しいアラートルールを追加できます。

### ダッシュボード追加

`monitoring-config.json` の `dashboard_config`
セクションを編集してカスタムダッシュボードを追加できます。

## 🔧 メンテナンス

### 定期メンテナンス

- ログローテーション: 自動（設定済み）
- メトリクス圧縮: 自動（設定済み）
- データ削除: 保持期間に基づく自動削除

### モニタリング

- 監視システム自体の健全性チェック
- 通知チャネルのテスト
- データ品質検証

## 📞 サポート

監視システムに関する問題や質問は、以下のチャネルで報告してください：

- Discord: #autoforgenexus-alerts
- Email: admin@autoforgenexus.com
- GitHub Issues: セキュリティ以外の問題

---

**Note**: この監視インフラストラクチャは本番レベルの観測可能性を提供し、AutoForgeNexus の 99.9% 可用性目標をサポートします。
