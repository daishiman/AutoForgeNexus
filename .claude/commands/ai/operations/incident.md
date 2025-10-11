---
name: incident
description: 'インシデント対応と根本原因分析'
category: operations
complexity: extreme
agents:
  [
    sre-agent,
    observability-engineer,
    security-architect,
    technical-documentation,
    product-manager,
    version-control-specialist,
  ]
---

# /ai:operations:incident - インシデント管理

## Triggers

- インシデント検知とアラート
- 手動インシデント報告
- SLO 違反の発生
- セキュリティイベント検出

## Context Trigger Pattern

```

/ai:operations:incident [severity critical|high|medium|low] [--escalate] [--rca] [--postmortem]

```

## Behavioral Flow

1. **検知**: アラート受信と初期評価
2. **分類**: 重要度とインパクト評価
3. **通知**: ステークホルダーへの連絡
4. **初期対応**: 影響軽減措置の実施
5. **調査**: ログ分析とメトリクス確認
6. **根本原因**: RCA 実施と問題特定
7. **解決**: 修正適用と検証
8. **ポストモーテム**: 振り返りと改善策

Key behaviors:

- インシデントコマンダー制
- タイムライン記録
- ステータスページ更新
- Blameless ポストモーテム

## Agent Coordination

- **sre-agent** → インシデント対応主導
- **observability-engineer** → 原因調査とトレース
- **security-architect** → セキュリティインシデント対応
- **technical-documentation** → ポストモーテム作成
- **product-manager** → ステークホルダー調整

## Tool Coordination

- **bash_tool**: 診断コマンド実行
- **view**: ログとメトリクス確認
- **create_file**: インシデントレポート
- **str_replace**: 設定修正適用

## Key Patterns

- **エスカレーション**: 3 段階通知体系
- **RCA 手法**: 5 Whys/フィッシュボーン
- **MTTR 短縮**: 自動診断と修復
- **学習**: ポストモーテム文化

## Examples

### クリティカルインシデント

```

/ai:operations:incident critical --escalate --rca

# 即座エスカレーション

# 全チーム動員

# リアルタイム RCA 実施

```

### セキュリティインシデント

```

/ai:operations:incident high --escalate --postmortem

# セキュリティチーム主導

# フォレンジック調査

# 詳細ポストモーテム

```

### SLO 違反対応

```

/ai:operations:incident medium --rca --postmortem

# エラーバジェット分析

# 根本原因特定

# 改善アクション定義

```

## Boundaries

**Will:**

- 迅速なインシデント対応
- 体系的な原因分析
- 学習と改善の促進
- ステークホルダー管理

**Will Not:**

- 責任追及型の対応
- 不十分な調査での結論
- 改善なしの場当たり対応
- コミュニケーション不足
