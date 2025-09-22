---
name: create
description: "高品質プロンプトの作成と最適化"
category: prompt
complexity: high
agents:
  [
    prompt-engineering-specialist,
    llm-integration,
    evaluation-engine,
    vector-database-specialist,
    user-research,
    version-control-specialist,
  ]
---

# /ai:prompt:create - プロンプト作成と最適化

## Triggers

- 新規プロンプトテンプレートの作成
- マルチモデル対応プロンプト設計
- プロンプトチェーンの構築
- コンテキスト最適化の実施

## Context Trigger Pattern

```
/ai:prompt:create [purpose] [--model gpt4|claude|gemini|all] [--chain] [--optimize] [--template]
```

## Behavioral Flow

1. **意図理解**: ユーザー要求の深層理解と目的明確化
2. **テンプレート設計**: 構造化されたプロンプト骨格作成
3. **変数定義**: 動的部分とコンテキスト注入ポイント
4. **モデル最適化**: 各 LLM 特性に応じた調整
5. **チェーン設計**: 複数プロンプトの連携定義
6. **ベクトル化**: 埋め込み生成と類似検索準備
7. **評価準備**: 品質メトリクスとベンチマーク設定

Key behaviors:

- Few-shot/Zero-shot 戦略の選択
- Chain-of-Thought 推論の活用
- トークン効率の最適化
- 幻覚(Hallucination)の最小化

## Agent Coordination

- **prompt-engineering-specialist** → プロンプト設計と構造化
- **llm-integration** → マルチモデル互換性確保
- **evaluation-engine** → 品質評価基準設定
- **vector-database-specialist** → 埋め込みとインデックス
- **user-research** → ユーザー意図の検証

## Tool Coordination

- **create_file**: プロンプトテンプレートファイル作成
- **view**: 既存プロンプトとパターン確認
- **bash_tool**: LLM テスト実行
- **str_replace**: プロンプト最適化更新

## Key Patterns

- **構造化**: システム/ユーザー/アシスタントロール
- **コンテキスト管理**: 関連情報の効率的注入
- **出力制御**: フォーマット指定と制約
- **エラー処理**: 失敗ケースの考慮

## Examples

### マルチモデル対応プロンプト

```
/ai:prompt:create code-review --model all --optimize
# 全主要LLM対応のコードレビュープロンプト
# モデル別の特性活用
# トークン効率最適化
```

### プロンプトチェーン構築

```
/ai:prompt:create research-assistant --chain --template
# 調査→分析→要約のチェーン設計
# 各ステップのテンプレート作成
# コンテキスト引き継ぎ設計
```

### 特化型プロンプト作成

```
/ai:prompt:create sql-generator --model gpt4 --optimize
# SQL生成特化プロンプト
# GPT-4最適化
# エラー処理組み込み
```

## Boundaries

**Will:**

- 高品質なプロンプトテンプレート作成
- マルチモデル対応の保証
- トークン効率の最適化
- 評価可能な品質基準設定

**Will Not:**

- 無検証のプロンプト承認
- モデル制限を超える設計
- 著作権侵害コンテンツ
- バイアスを含む設計
