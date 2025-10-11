---
name: design
description: 'システムアーキテクチャ設計と技術的意思決定'
category: architecture
complexity: extreme
agents:
  [
    system-architect,
    security-architect,
    performance-optimizer,
    event-bus-manager,
    edge-computing-specialist,
    version-control-specialist,
  ]
---

# /ai:architecture:design - アーキテクチャ設計

## Triggers

- 新規システムアーキテクチャの設計
- マイクロサービス移行の計画
- イベント駆動アーキテクチャの導入
- 技術スタック選定と評価

## Context Trigger Pattern

```
/ai:architecture:design [pattern microservices|monolith|serverless|hybrid] [--ddd] [--event-driven] [--scale horizontal|vertical]
```

## Behavioral Flow

1. **要件分析**: 機能要件と非機能要件(NFR)の評価
2. **パターン選定**: アーキテクチャパターンの選択と理由
3. **コンポーネント設計**: システム分割と責任分離
4. **セキュリティ設計**: ゼロトラスト、認証認可、暗号化
5. **性能設計**: スケーラビリティ、レイテンシ、スループット
6. **イベント設計**: 非同期通信とイベント駆動
7. **エッジ設計**: CDN とエッジコンピューティング戦略
8. **ADR 作成**: Architecture Decision Record の文書化

Key behaviors:

- 4+1 アーキテクチャビューの作成
- 非機能要件の完全対応
- 技術的負債の最小化
- 将来の拡張性考慮

## Agent Coordination

- **system-architect** → 全体設計統括と意思決定
- **security-architect** → セキュリティパターンとゼロトラスト
- **performance-optimizer** → 性能要件と最適化戦略
- **event-bus-manager** → イベント駆動とメッセージング
- **edge-computing-specialist** → Cloudflare エッジ活用

## Tool Coordination

- **create_file**: アーキテクチャドキュメントと ADR
- **view**: 既存システムと制約確認
- **bash_tool**: アーキテクチャ検証ツール実行
- **str_replace**: 設計ドキュメント更新

## Key Patterns

- **レイヤー分離**: プレゼンテーション/アプリケーション/ドメイン/Core/インフラ
- **機能ベース集約**: 高凝集・低結合な機能単位の整理（DDD準拠）
- **マイクロサービス**: サービス境界と API 設計
- **イベント駆動**: Pub/Sub、CQRS、イベントソーシング
- **エッジ最適化**: CDN 活用とレイテンシ削減

## Examples

### マイクロサービス設計

```
/ai:architecture:design microservices --ddd --event-driven --scale horizontal
# DDDベースのマイクロサービス設計
# イベント駆動通信パターン
# 水平スケーリング対応
```

### サーバーレス+エッジ設計

```
/ai:architecture:design serverless --scale horizontal
# Cloudflare Workers活用設計
# エッジコンピューティング最適化
# コールドスタート最小化
```

### ハイブリッドアーキテクチャ

```
/ai:architecture:design hybrid --ddd --event-driven
# モノリスとマイクロサービスの共存
# 段階的移行計画
# イベントバスによる統合
```

## Boundaries

**Will:**

- 包括的なアーキテクチャ設計
- NFR 完全対応の保証
- スケーラビリティと拡張性確保
- セキュリティファースト設計

**Will Not:**

- 過度に複雑な設計の推奨
- 実証されていない技術の採用
- コスト無視の理想設計
- 既存制約の無視
