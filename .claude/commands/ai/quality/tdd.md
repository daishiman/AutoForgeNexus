---
name: tdd
description: 'テスト駆動開発の実践と管理'
category: quality
complexity: high
agents:
  [
    test-automation-engineer,
    qa-coordinator,
    backend-developer,
    frontend-architect,
    version-control-specialist,
  ]
---

# /ai:quality:tdd - TDD 実践管理

## Triggers

- TDD サイクルの開始
- テストカバレッジ向上
- テスト戦略の実装
- レガシーコードのテスト追加

## Context Trigger Pattern

```
/ai:quality:tdd [feature] [--coverage 80] [--contract] [--mutation] [--watch]
```

## Behavioral Flow

1. **要件分析**: テスト可能な仕様の定義
2. **Red Phase**: 失敗するテスト作成
3. **Green Phase**: 最小実装でテスト成功
4. **Refactor Phase**: コード品質改善
5. **カバレッジ測定**: 行/分岐/条件網羅
6. **契約テスト**: インターフェース検証
7. **ミューテーション**: テスト品質評価
8. **CI 統合**: パイプライン設定

Key behaviors:

- 厳格な TDD サイクル
- テストファースト思考
- 継続的カバレッジ監視
- テストの保守性確保

## Agent Coordination

- **test-automation-engineer** → TDD プロセス管理
- **qa-coordinator** → 品質基準維持
- **backend-developer** → バックエンド TDD
- **frontend-architect** → フロントエンド TDD

## Tool Coordination

- **create_file**: テストケース作成
- **bash_tool**: テスト実行とカバレッジ
- **str_replace**: コード改善
- **view**: テスト結果確認

## Key Patterns

- **テストピラミッド**: Unit > Integration > E2E
- **AAA**: Arrange/Act/Assert
- **テストダブル**: Mock/Stub/Spy
- **プロパティベース**: 生成的テスト

## Examples

### 新機能 TDD

```
/ai:quality:tdd new-feature --coverage 90 --mutation
# 90%カバレッジ目標
# ミューテーションテスト実施
# 品質ゲート設定
```

### API 契約テスト

```
/ai:quality:tdd api --contract --watch
# Consumer/Provider契約
# 継続的検証
# 破壊的変更検出
```

### レガシー改善

```
/ai:quality:tdd legacy-module --coverage 60
# 段階的テスト追加
# リファクタリング準備
# 安全な変更
```

## Boundaries

**Will:**

- TDD 原則の厳守
- 高品質テストの作成
- カバレッジ目標達成
- 継続的改善促進

**Will Not:**

- テストなし実装許可
- 品質基準の妥協
- 脆弱なテスト作成
- カバレッジのみ重視
