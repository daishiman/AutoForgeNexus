---
name: implement
description: "TDD駆動による機能実装とマルチドメイン開発"
category: development
complexity: extreme
agents:
  [
    test-automation-engineer,
    backend-developer,
    frontend-architect,
    real-time-features-specialist,
    domain-modeller,
    version-control-specialist,
  ]
---

# /ai:development:implement - TDD 機能実装

## Triggers

- 新機能の実装開始
- TDD サイクルの実行
- マルチコンポーネント開発
- リアルタイム機能の追加

## Context Trigger Pattern

```
/ai:development:implement [feature] [--tdd] [--realtime] [--coverage 80] [--parallel]
```

## Behavioral Flow

1. **要件確認**: 実装要件とドメインモデル確認
2. **テスト設計**: 失敗するテストケース作成
3. **Red Phase**: テスト実行と失敗確認
4. **Green Phase**: 最小限の実装でテスト成功
5. **Refactor Phase**: コード品質改善と DRY 原則
6. **統合**: フロント/バック/リアルタイム統合
7. **カバレッジ**: テストカバレッジ測定
8. **最適化**: パフォーマンスと品質改善

Key behaviors:

- 厳格な TDD サイクル遵守
- ドメイン駆動実装
- 並列開発の調整
- CI/CD 統合

## Agent Coordination

- **test-automation-engineer** → TDD プロセス主導
- **backend-developer** → サーバーサイド実装
- **frontend-architect** → クライアントサイド実装
- **real-time-features-specialist** → WebSocket/リアルタイム
- **domain-modeller** → ドメインロジック検証（機能ベース集約）

## Tool Coordination

- **create_file**: テストとソースコード作成
- **bash_tool**: テスト実行とカバレッジ測定
- **str_replace**: リファクタリング適用
- **view**: 既存コードとテスト確認

## Key Patterns

- **TDD サイクル**: Red→Green→Refactor
- **テスト戦略**: Unit→Integration→E2E
- **カバレッジ目標**: 80%以上維持
- **並列開発**: フロント/バック同時進行

## Examples

### 認証機能の TDD 実装

```
/ai:development:implement authentication --tdd --coverage 90
# 認証機能のTDD実装
# 90%カバレッジ目標
# JWT/OAuth実装
```

### リアルタイム協調編集

```
/ai:development:implement collaborative-editing --realtime --tdd
# CRDT/OTアルゴリズム実装
# WebSocket統合
# リアルタイム同期テスト
```

### マイクロサービス実装

```
/ai:development:implement payment-service --tdd --parallel
# 決済マイクロサービス
# 並列開発調整
# API契約テスト
```

## Boundaries

**Will:**

- 厳格な TDD 実践
- 高カバレッジの維持
- ドメインモデル準拠
- 品質基準の確保

**Will Not:**

- テストなしの実装
- カバレッジ目標の妥協
- ドメインロジックの逸脱
- 技術的負債の蓄積
