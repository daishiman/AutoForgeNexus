---
name: style-genome
description: 'ユーザースタイル・ゲノムの抽出と適用'
category: prompt
complexity: extreme
agents:
  [
    data-analyst,
    prompt-engineering-specialist,
    vector-database-specialist,
    user-research,
    ui-ux-designer,
    version-control-specialist,
  ]
---

# /ai:prompt:style-genome - スタイルベクトル管理

## Triggers

- ユーザー固有スタイルの抽出
- スタイルベクトルの生成と保存
- パーソナライズドプロンプト作成
- スタイル転送と適用

## Context Trigger Pattern

```
/ai:prompt:style-genome [user-id] [--analyze history|feedback] [--extract] [--apply prompt-id] [--transfer]
```

## Behavioral Flow

1. **データ収集**: ユーザーの過去プロンプトと良作収集
2. **パターン分析**: 文体、構造、語彙の特徴抽出
3. **統計処理**: スタイル要素の定量化
4. **ベクトル生成**: 高次元スタイルベクトル作成
5. **クラスタリング**: 類似スタイルのグループ化
6. **プロファイル作成**: YAML スタイル定義生成
7. **適用**: 新規プロンプトへのスタイル注入
8. **検証**: スタイル一致度の測定

Key behaviors:

- 多次元スタイル分析
- 転移学習の活用
- 個人化アルゴリズム
- プライバシー保護

## Agent Coordination

- **data-analyst** → スタイル統計分析
- **prompt-engineering-specialist** → スタイル適用戦略
- **vector-database-specialist** → ベクトル管理と検索
- **user-research** → ユーザー嗜好理解
- **ui-ux-designer** → スタイル可視化

## Tool Coordination

- **create_file**: スタイルプロファイル YAML
- **bash_tool**: ベクトル生成スクリプト
- **view**: ユーザー履歴確認
- **str_replace**: スタイル適用更新

## Key Patterns

- **スタイル次元**: トーン/複雑度/形式/語彙
- **ベクトル空間**: 1536 次元埋め込み
- **転送学習**: スタイル転送技術
- **個人化**: ユーザー別最適化

## Examples

### スタイル抽出と保存

```
/ai:prompt:style-genome user-456 --analyze history --extract
# 過去6ヶ月の履歴分析
# スタイルベクトル生成
# プロファイル保存
```

### スタイル適用

```
/ai:prompt:style-genome user-456 --apply new-prompt --transfer
# 保存済みスタイル読み込み
# 新プロンプトへ転送
# 一致度90%以上確保
```

### スタイル比較分析

```
/ai:prompt:style-genome team --analyze feedback
# チーム全体のスタイル分析
# 共通パターン抽出
# 標準スタイルガイド生成
```

## Boundaries

**Will:**

- 高精度なスタイル抽出
- プライバシー保護された分析
- 効果的なスタイル転送
- 個人化の最大化

**Will Not:**

- プライバシー侵害
- スタイルの強制適用
- 不適切な一般化
- 品質を犠牲にした個人化
