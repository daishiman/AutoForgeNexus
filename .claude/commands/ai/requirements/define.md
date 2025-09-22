---
name: define
description: "包括的な要件定義とユーザーストーリー作成"
category: requirements
complexity: high
agents:
  [
    product-manager,
    domain-modellerr,
    user-research,
    prompt-engineering-specialist,
    Requirements Analyst,
    version-control-specialist,
  ]
---

# /ai:requirements:define - 要件定義とユーザーストーリー

## Triggers

- 新機能の要件定義開始
- 既存要件の見直しと更新
- ユーザーストーリーの作成と詳細化
- 受入基準の明確化要求

## Context Trigger Pattern

```
/ai:requirements:define [scope] [--format agile|waterfall|hybrid] [--validate] [--priority]
```

## Behavioral Flow

1. **要件収集**: ステークホルダーインタビューと要求抽出
2. **分類整理**: 機能要件と非機能要件の分離
3. **優先順位付け**: MoSCoW 法による重要度評価
4. **詳細化**: ユーザーストーリーと受入基準作成
5. **ドメイン分析**: ドメインモデルへのマッピング
6. **検証**: 完全性、一貫性、実現可能性の確認
7. **文書化**: 要件定義書の生成と承認準備

Key behaviors:

- ユーザー中心の要件抽出
- ドメイン駆動設計との整合性確保
- プロンプト要件の特殊性考慮
- トレーサビリティマトリクスの維持

## Agent Coordination

- **product-manager** → ビジネス要件の整理と優先順位
- **domain-modellerr** → ドメイン要件の抽出と構造化
- **user-research** → ユーザーニーズの検証と分析
- **prompt-engineering-specialist** → プロンプト固有要件の定義
- **Requirements Analyst** → 要件の形式化と検証

## Tool Coordination

- **create_file**: 要件定義書とユーザーストーリー作成
- **view**: 既存ドキュメントとコンテキスト確認
- **str_replace**: 要件の更新と修正
- **bash_tool**: 要件管理ツールとの統合

## Key Patterns

- **要件分類**: 機能/非機能/制約/インターフェース
- **優先順位**: Must/Should/Could/Won't (MoSCoW)
- **ストーリー形式**: As a [role], I want [feature], so that [benefit]
- **受入基準**: Given/When/Then 形式

## Examples

### アジャイル要件定義

```
/ai:requirements:define user-authentication --format agile --priority
# ユーザー認証機能の要件定義
# ユーザーストーリーと受入基準作成
# MoSCoW優先順位付け
```

### プロンプト機能要件

```
/ai:requirements:define prompt-optimization --validate
# プロンプト最適化要件の定義
# ドメインモデルとの整合性検証
# 特殊要件の明確化
```

### 包括的要件分析

```
/ai:requirements:define entire-system --format hybrid --validate
# システム全体の要件定義
# 機能・非機能要件の完全網羅
# クロスリファレンス検証
```

## Boundaries

**Will:**

- ステークホルダー要求の体系的整理
- ドメインモデルとの整合性確保
- 検証可能な受入基準の作成
- トレーサビリティの維持

**Will Not:**

- 技術的実装の詳細設計
- 承認なしの要件変更
- スコープの無制限拡大
- 実現不可能な要件の承認
