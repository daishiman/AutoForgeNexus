---
name: intent-diff
description: "意図差分ビューワーによる自動改善"
category: prompt
complexity: extreme
agents:
  [
    prompt-engineering-specialist,
    evaluation-engine,
    data-analyst,
    ui-ux-designer,
    user-research,
    version-control-specialist,
  ]
---

# /ai:prompt:intent-diff - 意図差分分析と自動修復

## Triggers

- ユーザー意図と出力の乖離検出
- プロンプト改善ポイントの特定
- 自動修復提案の生成
- ユーザーフィードバックの分析

## Context Trigger Pattern

```
/ai:prompt:intent-diff [prompt-id] [--visualize] [--auto-fix] [--threshold 0.8] [--interactive]
```

## Behavioral Flow

1. **意図抽出**: 自然言語処理による真の意図理解
2. **出力分析**: 実際の出力パターンの分析
3. **差分計算**: 意図と出力のギャップ定量化
4. **可視化**: 差分のビジュアル表現生成
5. **原因分析**: 乖離の根本原因特定
6. **修正案生成**: 自動改善提案の作成
7. **シミュレーション**: 改善効果の事前検証
8. **適用**: 承認後の自動適用

Key behaviors:

- 意味的類似度の計算
- 構造的差分の検出
- 自動修復アルゴリズム
- インタラクティブな改善プロセス

## Agent Coordination

- **prompt-engineering-specialist** → 差分分析と修正案作成
- **evaluation-engine** → 品質影響評価
- **data-analyst** → 統計的分析
- **ui-ux-designer** → 差分可視化 UI
- **user-research** → ユーザー意図の検証

## Tool Coordination

- **create_file**: 差分レポートと修正案
- **view**: プロンプトと出力の確認
- **bash_tool**: 差分分析ツール実行
- **str_replace**: 自動修正の適用

## Key Patterns

- **意図マッピング**: ユーザー意図の構造化
- **差分メトリクス**: 定量的な乖離測定
- **自動修復**: パターンベースの改善
- **反復改善**: 段階的な精度向上

## Examples

### ビジュアル差分分析

```
/ai:prompt:intent-diff prompt-123 --visualize --threshold 0.9
# 視覚的な差分表示
# 90%精度閾値設定
# ヒートマップ生成
```

### 自動修復モード

```
/ai:prompt:intent-diff failing-prompt --auto-fix --interactive
# 自動修正案生成
# インタラクティブな確認
# 段階的適用
```

### バッチ差分分析

```
/ai:prompt:intent-diff all-prompts --threshold 0.7
# 全プロンプトの差分分析
# 問題のあるプロンプト特定
# 優先順位付き改善リスト
```

## Boundaries

**Will:**

- 意図と出力の正確な差分分析
- 実用的な自動修復提案
- 視覚的な問題表現
- 段階的な改善プロセス

**Will Not:**

- 意図の誤解釈
- 無検証の自動適用
- 過度な修正による品質低下
- ユーザー確認なしの変更
