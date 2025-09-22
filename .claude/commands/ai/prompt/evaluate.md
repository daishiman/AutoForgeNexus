---
name: evaluate
description: "プロンプト品質の多層評価と改善"
category: prompt
complexity: high
agents:
  [
    evaluation-engine,
    prompt-engineering-specialist,
    data-analyst,
    llm-integration,
    qa-coordinator,
    version-control-specialist,
  ]
---

# /ai:prompt:evaluate - プロンプト評価と改善

## Triggers

- プロンプト品質の定量評価
- A/B テストの実行と分析
- 改善提案の自動生成
- ベンチマーク比較の実施

## Context Trigger Pattern

```
/ai:prompt:evaluate [prompt-id] [--metrics accuracy|consistency|cost|all] [--compare baseline] [--improve]
```

## Behavioral Flow

1. **メトリクス設定**: 評価指標の選定と重み付け
2. **テストデータ準備**: 評価用データセットの構築
3. **実行**: マルチモデルでのテスト実行
4. **測定**: 品質指標の定量化
5. **統計分析**: 有意性検定とばらつき評価
6. **比較分析**: ベースラインとの差分評価
7. **改善提案**: 具体的な改善ポイント生成
8. **検証**: 改善版の効果測定

Key behaviors:

- RAG 指標(Precision/Recall/Faithfulness)測定
- 倫理指標(毒性/バイアス)評価
- コスト効率分析
- 統計的有意性検証

## Agent Coordination

- **evaluation-engine** → 評価実行と指標測定
- **prompt-engineering-specialist** → 改善提案と適用
- **data-analyst** → 統計分析とレポート
- **llm-integration** → マルチモデルテスト
- **qa-coordinator** → 品質基準の確保

## Tool Coordination

- **bash_tool**: 評価スクリプト実行
- **create_file**: 評価レポート生成
- **view**: 評価結果の確認
- **str_replace**: プロンプト改善適用

## Key Patterns

- **多層評価**: 品質/RAG/倫理/コストの統合評価
- **A/B テスト**: 統計的有意性のある比較
- **継続的改善**: 反復的な評価と最適化
- **ベンチマーク**: 業界標準との比較

## Examples

### 包括的品質評価

```
/ai:prompt:evaluate prompt-v2 --metrics all --compare prompt-v1
# 全指標での品質評価
# バージョン間比較
# 改善効果の定量化
```

### A/B テスト実行

```
/ai:prompt:evaluate variants --metrics accuracy --improve
# 複数バリアントのA/Bテスト
# 統計的有意性検証
# 最適バリアント選定
```

### コスト最適化評価

```
/ai:prompt:evaluate production-prompt --metrics cost --improve
# トークン使用量分析
# コスト削減提案
# 品質維持の検証
```

## Boundaries

**Will:**

- 定量的な品質評価
- 統計的に有効な分析
- 実用的な改善提案
- マルチモデル対応評価

**Will Not:**

- 主観的な評価のみ
- 不十分なデータでの判断
- 品質を犠牲にしたコスト削減
- 評価なしの本番適用
