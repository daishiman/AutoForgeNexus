# System Design Principles

## Core Directive

**Test-Driven > Implementation | Domain Clarity > Technical Complexity | Agent Autonomy > Central Control**

## TDD Philosophy

### Red-Green-Refactor Mindset

- **Red Phase**: 明確な失敗するテストから開始
- **Green Phase**: テストを通す最小限の実装
- **Refactor Phase**: 設計改善とコード品質向上

### Testing Pyramid Strategy

```
         E2E Tests (10%)
        /              \
    Integration (30%)
   /                  \
Unit Tests (60%)
```

### Test-First Benefits

- **Design Clarity**: テスト可能な設計の強制
- **Documentation**: テストが仕様書として機能
- **Confidence**: リファクタリング時の安全性
- **Debugging**: 問題の早期発見と特定

## DDD Principles

### Strategic Design

- **Bounded Contexts**: 明確なドメイン境界
- **Ubiquitous Language**: 統一された用語体系
- **Context Mapping**: ドメイン間の関係定義

### Tactical Design

- **Aggregates**: トランザクション境界の定義
- **Entities**: 識別子を持つドメインオブジェクト
- **Value Objects**: 不変の値表現
- **Domain Services**: 複数エンティティにまたがるロジック
- **Domain Events**: ドメイン変更の通知

## Agent Design Principles

### Autonomy

- **Self-Management**: 自己監視と自己修復
- **Decision Making**: ローカル情報での意思決定
- **Adaptation**: 環境変化への動的適応

### Collaboration

- **Loose Coupling**: イベント駆動による疎結合
- **High Cohesion**: 関連機能の凝集
- **Contract-First**: インターフェース契約の事前定義

### Resilience

- **Fault Tolerance**: 部分障害の局所化
- **Circuit Breaker**: カスケード障害の防止
- **Graceful Degradation**: 機能縮退での継続

## Quality Attributes

### Performance

- **Response Time**: P95 < 500ms
- **Throughput**: 1000 req/sec minimum
- **Resource Efficiency**: 最適なリソース利用

### Reliability

- **Availability**: 99.9% SLA
- **Data Durability**: 99.999999999% (11 nines)
- **Recovery**: RTO < 2 hours, RPO < 1 hour

### Security

- **Defense in Depth**: 多層防御
- **Least Privilege**: 最小権限原則
- **Zero Trust**: 検証なき信頼なし
