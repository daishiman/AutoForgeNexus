---
name: domain
description: 'DDD準拠のドメインモデリングとユビキタス言語確立'
category: requirements
complexity: extreme
agents:
  [
    domain-modellerr,
    system-architect,
    api-designer,
    backend-developer,
    database-administrator,
    version-control-specialist,
  ]
---

# /ai:requirements:domain - ドメイン駆動設計

## Triggers

- ドメイン境界の定義と見直し
- 集約ルートとエンティティ設計
- ドメインイベントの特定と定義
- ユビキタス言語の確立と統一

## Context Trigger Pattern

```
/ai:requirements:domain [context-name] [--aggregate root|entity|value-object] [--event-sourcing] [--cqrs]
```

## Behavioral Flow

1. **コンテキスト分析**: ビジネスドメインの理解と分解
2. **境界定義**: Bounded Context の特定と境界設定
3. **モデリング**: エンティティ、値オブジェクト、集約の設計
4. **イベント設計**: ドメインイベントの定義と流れ
5. **言語統一**: ユビキタス言語の確立と用語集作成
6. **API 設計**: ドメインモデルから API へのマッピング
7. **永続化設計**: リポジトリパターンとデータモデル
8. **検証**: モデルの整合性と実装可能性確認

Key behaviors:

- 戦略的設計と戦術的設計の統合
- イベントストーミングによる発見
- CQRS/イベントソーシング対応
- コンテキストマップの維持

## Agent Coordination

- **domain-modellerr** → ドメイン設計主導とモデリング
- **system-architect** → アーキテクチャとの整合性確保
- **api-designer** → RESTful/GraphQL API への変換
- **backend-developer** → 実装可能性の検証
- **database-administrator** → 永続化層の設計

## Tool Coordination

- **create_file**: ドメインモデルドキュメント作成
- **view**: 既存モデルとビジネスルール確認
- **str_replace**: モデル定義の更新
- **bash_tool**: モデリングツールとの連携

## Key Patterns

- **集約設計**: トランザクション境界の明確化
- **イベント駆動**: ドメインイベントによる疎結合
- **リポジトリ**: 永続化の抽象化
- **ファクトリー**: 複雑なオブジェクト生成

## Examples

### プロンプトドメインモデリング

```
/ai:requirements:domain prompt-context --aggregate root --event-sourcing
# プロンプト集約ルートの設計
# イベントソーシング対応
# PromptCreated, PromptUpdatedイベント定義
```

### 評価ドメイン設計

```
/ai:requirements:domain evaluation-context --cqrs
# 評価ドメインのCQRS設計
# 読み取りモデルと書き込みモデル分離
# EvaluationScore値オブジェクト
```

### 完全なドメイン分析

```
/ai:requirements:domain entire-system --event-sourcing --cqrs
# システム全体のドメイン設計
# イベントストーミング実施
# コンテキストマップ作成
```

## Boundaries

**Will:**

- ビジネスロジックの適切なモデル化
- トランザクション境界の明確化
- ユビキタス言語の確立と維持
- イベント駆動設計の適用

**Will Not:**

- 技術的実装詳細の過度な考慮
- ビジネスルールの勝手な変更
- 過度に複雑なモデル設計
- パフォーマンスのみを重視した設計
