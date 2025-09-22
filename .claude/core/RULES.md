# AI Prompt Optimization System - Agent Collaboration Rules

## Rule Priority System

**🔴 CRITICAL**: TDD 実装、ドメイン境界遵守、データ整合性
**🟡 IMPORTANT**: エージェント間通信、品質基準、ドキュメント化
**🟢 RECOMMENDED**: パフォーマンス最適化、コスト効率、UX 改善

## Fundamental Rules

### TDD Implementation Rules

**Priority**: 🔴 **Triggers**: すべての機能実装

- **Red-Green-Refactor Cycle**: テストファースト → 実装 → リファクタリング
- **Test Coverage Requirements**: 単体 80%、統合 70%、E2E クリティカルパス 100%
- **Test Isolation**: モック/スタブによる依存関係の分離
- **Contract Testing**: エージェント間インターフェースの契約テスト必須
- **Regression Prevention**: 既存テストの破壊禁止

✅ **Right**: テスト作成 → 失敗確認 → 最小実装 → 成功確認 → リファクタリング
❌ **Wrong**: 実装先行、テストなしマージ、カバレッジ無視

### Domain Boundary Rules

**Priority**: 🔴 **Triggers**: エージェント間協働

- **Single Responsibility**: 各エージェントは単一ドメインに集中
- **Interface Segregation**: 必要最小限のインターフェース公開
- **Dependency Direction**: 上位レイヤー → 下位レイヤーのみ
- **Event-Driven Communication**: 直接呼び出し禁止、イベント経由必須
- **Context Isolation**: 境界づけられたコンテキストの維持

✅ **Right**: Event 発行 → EventBus → 購読者処理
❌ **Wrong**: エージェント直接呼び出し、ドメイン越境アクセス

### Data Consistency Rules

**Priority**: 🔴 **Triggers**: データ操作、状態変更

- **Eventual Consistency**: 分散システムでの結果整合性保証
- **Idempotency**: すべての操作の冪等性確保
- **Transaction Boundaries**: 集約単位でのトランザクション管理
- **Event Sourcing**: 状態変更の完全記録
- **Compensating Actions**: 失敗時の補償トランザクション

✅ **Right**: イベント記録 → 状態導出 → 補償可能
❌ **Wrong**: 直接状態変更、履歴なし更新

### Agent Coordination Rules

**Priority**: 🟡 **Triggers**: マルチエージェントタスク

- **Team Formation**: タスクに応じた動的チーム編成
- **Leader Election**: チームリーダーの自動選出
- **Consensus Protocol**: 重要決定での合意形成
- **Failure Handling**: エージェント障害時の自動フェイルオーバー
- **Load Balancing**: 作業負荷の動的分散

✅ **Right**: チーム編成 → リーダー選出 → 協調実行 → 結果統合
❌ **Wrong**: 単独判断、調整なし並行作業

### Documentation Rules

**Priority**: 🟡 **Triggers**: 実装、API 変更、設計決定

- **API Documentation**: OpenAPI 仕様の自動生成と維持
- **ADR (Architecture Decision Records)**: 設計決定の記録
- **Test Documentation**: テストケースの意図と期待値明記
- **Event Catalog**: イベント定義の中央管理
- **Change Log**: セマンティックバージョニング準拠

✅ **Right**: 実装と同時にドキュメント更新
❌ **Wrong**: 後回しドキュメント、不整合な仕様書
