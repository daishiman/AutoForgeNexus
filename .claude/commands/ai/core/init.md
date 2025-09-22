---
name: init
description: "AIプロンプト最適化システムの初期化とエージェント編成"
category: core
complexity: high
agents:
  [
    system-architect,
    domain-modellerr,
    devops-coordinator,
    product-manager,
    technical-documentation,
    version-control-specialist,
  ]
---

# /ai:core:init - システム初期化とエージェント編成

## Triggers

- 新規プロジェクト開始時のシステム初期化要求
- 開発環境セットアップと基盤構築の必要性
- エージェントチーム編成と役割定義の要求
- フェーズ別の段階的システム立ち上げ

## Context Trigger Pattern

```
/ai:core:init [project-name] [--phase 1-5] [--agents core|all|custom] [--env dev|staging|prod] [--ddd]
```

## Behavioral Flow

1. **環境分析**: 既存リソースの評価と利用可能なインフラの確認
2. **チーム編成**: フェーズに応じた必要エージェントの選定と活性化
3. **基盤構築**: DDD 準拠のプロジェクト構造とドメイン境界の確立
4. **設定同期**: 全エージェント間での設定共有とコンテキスト確立
5. **検証**: 初期化完了確認とシステムヘルスチェック

Key behaviors:

- フェーズ別エージェント活性化（Phase1: 6 エージェント、Phase5: 29 エージェント）
- DDD 原則に基づくプロジェクト構造の自動生成
- エージェント間の依存関係マッピングと通信チャネル確立
- 環境別設定の自動適用とバリデーション

## Agent Coordination

- **system-architect** → システム全体のアーキテクチャビジョン策定
- **domain-modellerr** → ドメイン境界の定義と集約ルート設計
- **devops-coordinator** → CI/CD パイプラインとインフラ準備
- **product-manager** → ビジネス要件の整理と優先順位付け
- **technical-documentation** → 初期ドキュメント構造の作成

## Tool Coordination

- **create_file**: プロジェクト構造とコンフィグファイル生成
- **bash_tool**: 開発ツールのインストールと環境設定
- **str_replace**: 設定ファイルのカスタマイズ
- **view**: 既存環境の調査と確認

## Key Patterns

- **フェーズ管理**: Phase1(基盤) → Phase2(コア) → Phase3(高度) → Phase4(最適化) → Phase5(エンタープライズ)
- **エージェント編成**: コア 6 → 必須 12 → 拡張 18 → 最適化 24 → 完全 29
- **環境分離**: 開発/ステージング/本番の明確な境界設定
- **DDD 構造**: ドメイン層/アプリケーション層/インフラ層の分離

## Examples

### 基本的なプロジェクト初期化

```
/ai:core:init prompt-optimization-system --phase 1 --agents core
# Phase1の6エージェントで基盤構築開始
# DDD構造の自動生成と基本設定
```

### 完全なチーム編成での初期化

```
/ai:core:init enterprise-prompt --phase 5 --agents all --env prod --ddd
# 29エージェント全体の活性化
# 本番環境設定とDDD完全準拠
```

### カスタムエージェント選定

```
/ai:core:init mvp-project --agents custom --env dev
# 対話的にエージェント選定
# 開発環境での最小構成
```

## Boundaries

**Will:**

- プロジェクト基盤の構築と DDD 準拠構造の生成
- フェーズに応じたエージェントチームの段階的編成
- 環境別の適切な設定とツールチェーン準備
- エージェント間の依存関係と通信チャネルの確立

**Will Not:**

- 既存プロジェクトの破壊的変更や無断の上書き
- 承認なしの本番環境へのアクセスや変更
- 不適切なフェーズでの高度なエージェント活性化
