---
name: analyze
description: 'データ分析と洞察抽出'
category: data
complexity: high
agents:
  [
    data-analyst,
    vector-database-specialist,
    user-research,
    performance-optimizer,
    version-control-specialist,
  ]
---

# /ai:data:analyze - データ分析

## Triggers

- データ傾向分析要求
- 異常検知の実施
- パフォーマンス分析
- ユーザー行動分析

## Context Trigger Pattern

```
/ai:data:analyze [dataset] [--type statistical|ml|vector] [--visualize] [--report]
```

## Behavioral Flow

1. **データ収集**: 分析対象データの取得
2. **前処理**: クレンジングと正規化
3. **探索的分析**: 統計量と分布確認
4. **パターン検出**: 傾向と異常の発見
5. **機械学習**: 予測モデル構築
6. **可視化**: グラフとダッシュボード
7. **洞察抽出**: アクション可能な知見
8. **レポート生成**: 結果の文書化

Key behaviors:

- リアルタイム分析
- 予測的アナリティクス
- 異常検知アルゴリズム
- インタラクティブ可視化

## Agent Coordination

- **data-analyst** → 分析主導と統計処理
- **vector-database-specialist** → ベクトル分析
- **user-research** → ユーザー洞察
- **performance-optimizer** → パフォーマンス分析

## Tool Coordination

- **bash_tool**: 分析スクリプト実行
- **create_file**: レポートと可視化
- **view**: データ確認
- **str_replace**: 分析パラメータ調整

## Key Patterns

- **EDA**: 探索的データ分析
- **時系列分析**: トレンドと季節性
- **クラスタリング**: セグメンテーション
- **異常検知**: 統計的/ML 手法

## Examples

### ユーザー行動分析

```
/ai:data:analyze user-events --type ml --visualize
# 行動パターン抽出
# セグメント識別
# チャーン予測
```

### パフォーマンス分析

```
/ai:data:analyze metrics --type statistical --report
# レイテンシ分析
# ボトルネック特定
# 最適化提案
```

### 異常検知

```
/ai:data:analyze system-logs --type ml
# 異常パターン学習
# リアルタイム検知
# アラート生成
```

## Boundaries

**Will:**

- データ駆動の洞察
- 統計的に有意な分析
- 実用的な提案
- 継続的モニタリング

**Will Not:**

- 不十分なデータでの結論
- プライバシー侵害分析
- バイアスのある解釈
- 過度な一般化
