# Core層とInfrastructure層 ディレクトリ構造設計書

## 概要

Core層とInfrastructure層の責務を明確化し、横断的関心事と外部連携を適切に管理する構造設計。

## Core層（横断的関心事）

Core層はアプリケーション全体で共有される横断的関心事を管理します。

```
backend/src/core/
├── config/                   # 設定管理
│   ├── settings/            # アプリケーション設定
│   ├── environments/        # 環境別設定
│   ├── validators/          # 設定検証
│   └── loaders/            # 設定読み込み
│
├── security/                # セキュリティ
│   ├── authentication/      # 認証処理
│   ├── authorization/       # 認可処理
│   ├── encryption/          # 暗号化
│   └── validation/          # 入力検証
│
├── exceptions/              # 例外管理
│   ├── base.py             # 基底例外クラス
│   ├── domain.py           # ドメイン例外
│   ├── application.py      # アプリケーション例外
│   └── infrastructure.py   # インフラ例外
│
├── logging/                 # ロギング
│   ├── formatters/         # ログフォーマッター
│   ├── handlers/           # ログハンドラー
│   └── filters/            # ログフィルター
│
├── middleware/              # ミドルウェア
│   ├── cors.py            # CORS設定
│   ├── rate_limit.py      # レート制限
│   ├── request_id.py      # リクエストID
│   └── error_handler.py   # エラーハンドリング
│
├── monitoring/              # 監視
│   ├── metrics/            # メトリクス収集
│   ├── tracing/            # 分散トレーシング
│   └── health/             # ヘルスチェック
│
└── dependencies/            # 依存性注入
    ├── container.py        # DIコンテナ
    └── providers.py        # プロバイダー定義
```

### Core層の設計原則

1. **横断的関心事の集約**

   - アプリケーション全体で使用される機能
   - 特定の機能に依存しない共通処理

2. **設定の一元管理**

   - 環境変数、設定ファイルの統合管理
   - バリデーションと型安全性

3. **セキュリティの標準化**
   - 認証・認可の共通実装
   - 暗号化・検証の統一

## Infrastructure層（外部連携）

Infrastructure層は外部システムとの連携を管理し、機能ベースで整理します。

```
backend/src/infrastructure/
├── prompt/                  # プロンプト機能の実装
│   ├── repositories/       # リポジトリ実装
│   │   ├── turso_prompt_repository.py
│   │   └── redis_cache_repository.py
│   └── adapters/           # 外部サービスアダプター
│       └── openai_adapter.py
│
├── evaluation/              # 評価機能の実装
│   ├── repositories/
│   └── adapters/
│
├── llm_integration/         # LLM統合の実装
│   ├── providers/          # プロバイダー実装
│   │   ├── openai/
│   │   ├── anthropic/
│   │   └── litellm/
│   ├── repositories/
│   └── adapters/
│
├── user_interaction/        # ユーザー操作の実装
│   ├── repositories/
│   └── adapters/
│
├── workflow/                # ワークフローの実装
│   ├── engines/            # ワークフローエンジン
│   │   └── langraph_engine.py
│   ├── repositories/
│   └── adapters/
│
└── shared/                  # 共有インフラ要素
    ├── database/           # データベース接続
    │   ├── turso.py       # Turso接続
    │   ├── redis.py       # Redis接続
    │   └── connection_pool.py
    ├── monitoring/         # 監視実装
    │   ├── langfuse.py    # LangFuse統合
    │   └── prometheus.py   # Prometheus統合
    └── auth/              # 認証実装
        └── clerk.py       # Clerk統合
```

### Infrastructure層の設計原則

1. **機能ベースの実装分離**

   - 各機能のインフラ実装を独立管理
   - 外部依存の局所化

2. **アダプターパターンの適用**

   - 外部サービスへの依存を抽象化
   - 交換可能な実装

3. **共有リソースの管理**
   - データベース接続プール
   - 監視・認証の統合

## レイヤー間の関係

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│         (API, WebSocket)                │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Application Layer               │
│      (Use Cases, CQRS, Services)        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│          Domain Layer                   │
│    (Entities, Value Objects)            │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐ ┌───────▼──────┐
│  Core Layer  │ │Infrastructure│
│ (Cross-cutting) │  (External)  │
└──────────────┘ └──────────────┘
```

## 実装ガイドライン

### Core層実装時の注意点

1. **状態を持たない**

   - ステートレスな実装
   - 設定は外部から注入

2. **循環依存の回避**

   - 他レイヤーへの依存禁止
   - インターフェース経由の通信

3. **テスタビリティ**
   - モック可能な設計
   - 単体テスト容易性

### Infrastructure層実装時の注意点

1. **外部依存の隔離**

   - 外部ライブラリを直接公開しない
   - アダプター経由でのアクセス

2. **エラーハンドリング**

   - 外部エラーをドメインエラーに変換
   - リトライ・フォールバック戦略

3. **パフォーマンス最適化**
   - 接続プーリング
   - キャッシング戦略
   - バッチ処理

## ファイル命名規約

### Core層

- 設定: `{環境}.config.py`
- セキュリティ: `{機能}_security.py`
- ミドルウェア: `{機能}_middleware.py`
- 例外: `{レイヤー}_exceptions.py`

### Infrastructure層

- リポジトリ: `{技術}_{エンティティ}_repository.py`
- アダプター: `{サービス}_adapter.py`
- プロバイダー: `{プロバイダー}_provider.py`

## 移行チェックリスト

- [x] Core層のディレクトリ作成
- [x] Infrastructure層の重複削除
- [x] 機能ベース構造の適用
- [x] 共有要素の整理
- [ ] 各ディレクトリの**init**.py作成
- [ ] テスト構造の整合

## まとめ

Core層は横断的関心事を責務ベースで、Infrastructure層は外部連携を機能ベースで整理することで、明確な責務分離と高い保守性を実現します。
