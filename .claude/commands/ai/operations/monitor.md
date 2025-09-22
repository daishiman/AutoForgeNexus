---
name: monitor
description: "包括的なシステム監視とオブザーバビリティ"
category: operations
complexity: high
agents:
  [
    observability-engineer,
    sre-agent,
    performance-optimizer,
    security-architect,
    version-control-specialist,
  ]
---

# /ai:operations:monitor - 監視とオブザーバビリティ

## Triggers

- 監視システムのセットアップ
- メトリクス収集の設定
- アラート閾値の調整
- ダッシュボード作成

## Context Trigger Pattern

```
/ai:operations:monitor [scope system|service|endpoint] [--metrics] [--traces] [--logs] [--alerts]
```

## Behavioral Flow

1. **計装**: アプリケーションへの監視コード追加
2. **収集設定**: メトリクス、トレース、ログの収集
3. **集約**: データの統合と相関
4. **可視化**: ダッシュボード構築
5. **アラート設定**: 閾値とルール定義
6. **SLI/SLO**: サービスレベル指標設定
7. **分析**: 異常検知とトレンド分析
8. **最適化**: 監視コストと精度のバランス

Key behaviors:

- OpenTelemetry 標準準拠
- 3 Pillars の統合
- 分散トレーシング
- 予測的アラート

## Agent Coordination

- **observability-engineer** → 監視システム設計
- **sre-agent** → SLI/SLO 定義
- **performance-optimizer** → パフォーマンス指標
- **security-architect** → セキュリティ監視

## Tool Coordination

- **create_file**: 監視設定とダッシュボード定義
- **bash_tool**: メトリクス収集スクリプト
- **view**: 現在の監視状態確認
- **str_replace**: アラート設定更新

## Key Patterns

- **RED**: Rate/Errors/Duration
- **USE**: Utilization/Saturation/Errors
- **Golden Signals**: レイテンシ/トラフィック/エラー/飽和
- **SLI/SLO**: サービスレベル管理

## Examples

### マイクロサービス監視

```
/ai:operations:monitor microservices --metrics --traces --alerts
# 分散トレーシング設定
# サービスメッシュ統合
# 依存関係マッピング
```

### SLO ベース監視

```
/ai:operations:monitor system --metrics --alerts
# SLI定義と測定
# エラーバジェット追跡
# SLOアラート設定
```

### セキュリティ監視

```
/ai:operations:monitor security --logs --alerts
# 異常アクセス検知
# 脅威インテリジェンス統合
# インシデント自動通知
```

## Boundaries

**Will:**

- 包括的な監視カバレッジ
- 実用的なアラート設定
- コスト効率的な実装
- 予防的な問題検知

**Will Not:**

- 過剰な監視による負荷
- ノイズの多いアラート
- プライバシー侵害
- 不必要なデータ保持
