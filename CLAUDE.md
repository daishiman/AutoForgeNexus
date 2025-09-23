# CLAUDE.md

このファイルは、このリポジトリでコードを作業する際のClaude Code (claude.ai/code) へのガイダンスを提供します。

## プロジェクト概要

AutoForgeNexusは、AIプロンプト最適化システム - 包括的なプロンプトエンジニアリング支援プラットフォームです。ユーザーの言語化能力に依存せず、高品質なAIプロンプトの作成・最適化・管理ができる統合環境を提供します。

### 主要機能
- テンプレートとAI支援による段階的プロンプト作成支援
- 多層評価メトリクスによる自動評価・最適化
- Git-likeなバージョニング、ブランチ、マージ機能
- 100+プロバイダー統合とコスト最適化によるマルチLLM対応
- 意図差分ビューワー、スタイル・ゲノム、プロンプトSLOなど17の革新的機能

## アーキテクチャ

- システムはドメイン駆動設計（DDD）原則に従い、クリーンアーキテクチャアプローチを採用
- Claude Codeを実行する時は、絶対に .claude/commands/ai/README.md 読み込んで最適なコマンドを設定する

### 技術スタック（最終版）
- **バックエンド**: Python 3.13, FastAPI 0.116.1, SQLAlchemy 2.0.32
- **フロントエンド**: Next.js 15.5, React 19, TypeScript 5.x, Tailwind CSS 4.0
- **データベース**: Turso (libSQL), Redis 7, libSQL Vector（埋め込み用）
- **認証**: Clerk（認証・認可・組織管理）
- **AI/ML**: LangChain 0.3.27, LangGraph 0.6.7, LiteLLM 1.76.1
- **LLM観測**: LangFuse（トレーシング・評価）
- **インフラ**: Cloudflare (Workers Python, Pages, R2), Docker

### レイヤーアーキテクチャ
```
プレゼンテーション層 (Next.js/React + Clerk Auth)
├── アプリケーション層 (ユースケース, CQRS, イベントバス)
├── ドメイン層 (エンティティ, 値オブジェクト, 集約)
└── インフラストラクチャ層 (Turso, Redis, LLMプロバイダー, LangFuse)
```

### 主要設計パターン
- **ドメイン駆動設計**: 明確なドメイン境界とユビキタス言語
- **イベントソーシング**: 状態変更の完全記録
- **CQRS**: 最適パフォーマンスのための読み書き分離
- **マイクロサービス対応**: 将来のサービス分離を想定した設計

## 開発コマンド

計画されている技術スタックに基づく使用コマンド：

### バックエンド (Python/FastAPI)
```bash
# Python 3.13 必須、仮想環境管理
python3.13 -m venv venv           # 仮想環境作成
source venv/bin/activate          # 仮想環境有効化 (Linux/Mac)
pip install -r requirements.txt   # 依存関係インストール

# 開発コマンド
make setup          # 初期プロジェクトセットアップ (Python 3.13)
make dev            # 開発サーバー起動 (FastAPI 0.116.1)
make test           # 全テスト実行 (pytest, 80%+カバレッジ)
make lint           # コード品質チェック (ruff, mypy厳密モード)
make format         # コードフォーマット (Black, isort)
make type-check     # mypy型チェック (strict設定)

# Docker開発環境 (必須)
docker-compose -f docker-compose.dev.yml up backend    # バックエンド開発環境
docker-compose -f docker-compose.dev.yml up database   # Turso + Redis
docker-compose -f docker-compose.dev.yml up langfuse   # LangFuse観測
docker-compose logs -f backend  # バックエンドログ監視

# 本番環境
docker-compose -f docker-compose.prod.yml up -d  # 本番環境起動
```

### フロントエンド (Next.js/React)
```bash
# パッケージマネージャー: pnpm (PAPN) 必須使用
pnpm install        # 依存関係インストール
pnpm dev            # 開発サーバー起動 (Next.js 15.5)
pnpm build          # 本番ビルド (React 19)
pnpm test           # テスト実行 (Jest/React Testing Library)
pnpm lint           # ESLintチェック (TypeScript 5.x)
pnpm type-check     # TypeScript厳密検証
pnpm format         # Prettier自動フォーマット

# Docker開発環境 (必須)
docker-compose -f docker-compose.dev.yml up frontend  # フロントエンド開発環境
docker-compose -f docker-compose.dev.yml logs -f frontend  # ログ監視
```

### データベース操作
```bash
# Tursoデータベース管理
turso db create autoforgenexus  # データベース作成
turso db show autoforgenexus    # データベース情報表示
turso db shell autoforgenexus   # データベースシェル接続

# ブランチ管理
turso db create autoforgenexus-dev --from-db autoforgenexus  # 開発ブランチ作成
turso db replicate autoforgenexus tokyo  # 東京リージョンレプリカ

# マイグレーション (SQLAlchemy併用)
alembic upgrade head    # マイグレーション適用
alembic revision --autogenerate -m "説明"  # マイグレーション作成
```

## プロジェクト構造

DDDの組織化に従った構造：
```
/backend/           # Python/FastAPIバックエンド
  /src/
    /domain/        # ドメインエンティティとビジネスロジック
    /application/   # ユースケースとアプリケーションサービス
    /infrastructure/ # 外部サービス実装
    /presentation/  # APIコントローラーとスキーマ
/frontend/          # Next.js/Reactフロントエンド
  /src/
    /components/    # 再利用可能UIコンポーネント
    /pages/         # Next.jsページ/ルート
    /hooks/         # カスタムReactフック
    /stores/        # Zustand状態管理
/docs/              # 追加ドキュメント
```

## Claude Code設定

### モデル固定設定
- **絶対使用モデル**: Claude 3.5 Sonnet (Opus 4.1)
- **フォールバック**: なし - 必ずOpus 4.1を使用
- **理由**: プロジェクトの複雑性とコード品質要求のため

### 必須MCP (Model Context Protocol) サーバー
```bash
# 必要なMCPサーバーの再インストール
claude mcp add context7        # ライブラリドキュメンテーション検索
claude mcp add sequential      # 複雑な分析・デバッグ
claude mcp add serena          # セマンティックコード理解
claude mcp add playwright      # ブラウザ自動化・テスト

# MCP設定確認
claude mcp list               # インストール済みMCP確認
claude mcp status             # MCP状態確認
```

### Claude Agentの設定
このプロジェクトには高度な`.claude/`ディレクトリが含まれています：
- **エージェント定義**: 異なる開発タスク用の27+専門エージェント
- **コアルール**: 開発原則、品質ゲート、アーキテクチャパターン
- **イベント契約**: イベント駆動アーキテクチャ用システムイベント定義

このプロジェクトで作業する際は、システムアーキテクチャ、プロンプトエンジニアリング、LLM統合、評価エンジン開発などのドメイン固有タスクに特化エージェントを活用してください。

## 重要なコンテキスト

### 開発哲学
- **ドメインファーストアプローチ**: 実装前にドメインモデリングから開始
- **品質ゲート**: 80%+カバレッジ目標を持つ包括的テスト戦略
- **イベント駆動**: コンポーネント間の疎結合のためイベント使用
- **漸進的開発**: MVPから始めるフェーズ別構築

### 主要アーキテクチャ決定
- **単一リポジトリ**: バックエンドとフロントエンドのモノレポ構造
- **データベース**: Turso (libSQL)をプライマリ、Redisキャッシュ、libSQL Vector埋め込み
- **認証**: Clerk（OAuth 2.0, MFA, 組織管理機能付き）
- **LLM観測**: LangFuse（トレーシング、評価、コスト監視）
- **リアルタイム機能**: 協調編集とライブ更新用WebSocket

### 革新フォーカス領域
システムは詳細にドキュメント化された17の革新的機能を実装：
- ユーザー意図と現在のプロンプトギャップを可視化する意図差分ビューワー
- 運用品質メトリクスのプロンプトSLO
- ユーザー固有スタイル抽出・再現のスタイル・ゲノム