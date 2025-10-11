---
name: analyze
description: '包括的なコード品質とシステム分析'
category: quality
complexity: high
agents:
  [
    qa-coordinator,
    test-automation-engineer,
    performance-optimizer,
    security-architect,
    version-control-specialist,
  ]
---

# /ai:quality:analyze - 品質分析

## Triggers

- コード品質の総合評価
- パフォーマンス分析の実施
- セキュリティ監査の要求
- 技術的負債の評価

## Context Trigger Pattern

```
/ai:quality:analyze [scope] [--focus quality|security|performance|all] [--depth shallow|deep] [--fix]
```

## Behavioral Flow

1. **スコープ定義**: 分析対象と深度の設定
2. **静的分析**: コード品質とパターン検出
3. **動的分析**: 実行時の挙動分析
4. **セキュリティスキャン**: 脆弱性とリスク評価
5. **パフォーマンス測定**: ボトルネックと最適化機会
6. **メトリクス算出**: 定量的品質指標
7. **優先順位付け**: 改善項目のランキング
8. **レポート生成**: 実用的な改善提案

Key behaviors:

- 多層品質分析
- 自動修正提案
- ベンチマーク比較
- トレンド追跡

## Agent Coordination

- **qa-coordinator** → 品質分析統括
- **test-automation-engineer** → テスト品質評価
- **performance-optimizer** → パフォーマンス分析
- **security-architect** → セキュリティ評価

## Tool Coordination

- **bash_tool**: 分析ツール実行
- **create_file**: 分析レポート生成
- **view**: コードとメトリクス確認
- **str_replace**: 自動修正適用

## Key Patterns

- **品質メトリクス**: 複雑度/重複/カバレッジ
- **セキュリティ**: OWASP Top 10 準拠
- **パフォーマンス**: Big-O 分析
- **保守性**: 認知的複雑度

## Examples

### 総合品質分析

```
/ai:quality:analyze --focus all --depth deep
# 全側面の深層分析
# 100+メトリクス測定
# 優先順位付き改善リスト
```

### セキュリティ監査

```
/ai:quality:analyze --focus security --fix
# SAST/DAST実行
# 脆弱性自動修正
# コンプライアンスチェック
```

### パフォーマンス分析

```
/ai:quality:analyze api --focus performance
# エンドポイント分析
# N+1問題検出
# 最適化提案
```

## Boundaries

**Will:**

- 包括的な品質評価
- 実用的な改善提案
- 自動修正の安全適用
- 継続的品質追跡

**Will Not:**

- 破壊的な自動修正
- 不完全な分析での判断
- ビジネスロジック変更
- 過度な最適化
