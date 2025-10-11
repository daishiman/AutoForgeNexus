# CLAUDE.md

このファイルは、このリポジトリでコードを作業する際の Claude Code
(claude.ai/code) へのガイダンスを提供します。

## 🎯 重要な初期設定

### 必須確認事項

1. **設定ファイル**: `.claude/settings.json` を必ず読み込む
2. **エージェント一覧**: `.claude/agents/00.agent_list.md`
   で利用可能なエージェントを確認
3. **コマンドガイド**: `.claude/commands/ai/README.md` で最適なコマンドを選択

### 推奨 MCP サーバー

- **serena**: セマンティックコード理解とメモリ管理（必須）
- **context7**: ライブラリドキュメンテーション検索（必須）
- **sequential-thinking**: 複雑な分析と問題解決（必須）
- **github**: GitHub 統合と PR 管理（必須）
- **playwright**: E2E テスト自動化（オプション）

## 📁 ドキュメント管理

すべてのレポート、レビュー、Issueは `docs/` 配下で一元管理されます：

```
docs/
├── reports/     # 実装レポート・成果報告
├── reviews/     # コードレビュー・セキュリティレビュー
├── issues/      # Issue追跡・課題管理（ISSUE_TRACKING.md参照）
└── setup/       # セットアップガイド
```

**重要**: レポートやレビュー結果を作成する際は、必ず上記ディレクトリに配置してください。

## 🎨 システム設計思想

### なぜこのシステムを作るのか

- **問題**: プロンプト作成は専門知識が必要で、品質のばらつきが大きい
- **解決策**: AIと人間の協働により、誰でも高品質なプロンプトを作成・最適化
- **価値**: 開発時間50%削減、プロンプト品質30%向上を実現

### 設計原則

1. **ユーザーファースト**: 言語化能力に依存しない直感的UI
2. **品質保証**: 多層評価による客観的な品質測定
3. **継続的改善**: Git-likeバージョニングで改善履歴を管理
4. **コスト最適化**: 100+LLMから最適なモデルを自動選択

## プロジェクト概要

AutoForgeNexus は、AI プロンプト最適化システム - 包括的なプロンプトエンジニアリング支援プラットフォームです。ユーザーの言語化能力に依存せず、高品質な AI プロンプトの作成・最適化・管理ができる統合環境を提供します。

### 主要機能

- テンプレートと AI 支援による段階的プロンプト作成支援
- 多層評価メトリクスによる自動評価・最適化
- Git-like なバージョニング、ブランチ、マージ機能
- 100+プロバイダー統合とコスト最適化によるマルチ LLM 対応
- 意図差分ビューワー、スタイル・ゲノム、プロンプト SLO など 17 の革新的機能

## アーキテクチャ

### 設計原則

- **ドメイン駆動設計（DDD）**: 明確な境界づけられたコンテキストとユビキタス言語
- **クリーンアーキテクチャ**: 依存性逆転の原則、レイヤー分離
- **イベント駆動**: CQRS、イベントソーシング、非同期メッセージング
- **マイクロサービス対応**: 将来のサービス分離を想定した疎結合設計

### 技術スタック（2025 年 9 月最新版）

- **バックエンド**: Python 3.13, FastAPI 0.116.1, SQLAlchemy 2.0.32, Pydantic v2
- **フロントエンド**: Next.js 15.5.4 (Turbopack), React 19.0.0, TypeScript
  5.9.2, Tailwind CSS 4.0.0
- **データベース**: Turso (libSQL) 分散型, Redis 7.4.1, libSQL Vector Extension
- **認証**: Clerk 6.32.0（OAuth 2.0, MFA, 組織管理）
- **AI/ML**: LangChain 0.3.27, LangGraph 0.2.60, LiteLLM 1.77.5
- **LLM 観測**: LangFuse 2.56.2（分散トレーシング・評価・コスト監視）
- **インフラ**: Cloudflare (Workers Python, Pages, R2), Docker 24.0+（開発環境のみ）
- **Node.js**: 22 LTS "Jod" (ネイティブ TypeScript 対応, WebSocket 内蔵)
- **パッケージ管理**: pnpm 9.x (Node.js 22 最適化)
- **状態管理**: Zustand 5.0.8
- **UI ライブラリ**: shadcn/ui 3.3.1 (React 19・Tailwind v4 対応)
- **品質**: Ruff 0.7.4, mypy 1.13.0 (strict), pytest 8.3.3, Playwright 1.50.0

### レイヤーアーキテクチャ

```
プレゼンテーション層 (Next.js/React + Clerk Auth)
├── アプリケーション層 (ユースケース, CQRS, イベントバス)
│   ├── コマンド側: CreatePrompt, OptimizePrompt, ExecuteEvaluation
│   ├── クエリ側: GetPromptDetails, GetEvaluationReport
│   └── サービス: PromptOrchestration, EvaluationPipeline, Reporting
├── ドメイン層 (エンティティ, 値オブジェクト, 集約)
│   ├── PromptAggregate: Prompt, Version, Template, Conversation
│   ├── EvaluationAggregate: Evaluation, TestResult, Metrics
│   └── TestSuiteAggregate: TestSuite, TestCase, ValidationRule
└── インフラストラクチャ層 (Turso, Redis, LLMプロバイダー, LangFuse)
```

## 開発コマンド

6 つのフェーズに基づく実際の環境構築コマンド：

### Phase 1: Git・基盤環境確認

```bash
# 環境確認 (最優先実行)
git --version                    # Git 2.40+必須
node --version                   # Node.js 20.0+必須
pnpm --version                   # pnpm 8.0+必須
docker --version                 # Docker 24.0+必須
gh auth status                   # GitHub CLI認証確認

# Git環境セットアップ
git flow init -d                 # GitFlow初期化
git config commit.template .gitmessage  # コミットテンプレート設定
gh workflow list                 # GitHub Actions確認
```

### Phase 2: インフラ・Docker 環境（開発環境のみ）

```bash
# Docker開発環境構築（ローカル開発用）
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d
docker-compose logs -f          # ログ監視

# サービス状態確認
docker-compose ps               # コンテナ状態確認
docker-compose -f docker-compose.dev.yml exec backend /bin/bash

# 注: 本番環境ではDockerを使用せず、Cloudflare Workers/Pagesにデプロイ
# - Backend: wrangler deploy --env production
# - Frontend: wrangler pages deploy frontend/out
```

### Phase 3: バックエンド (Python 3.13/FastAPI)

```bash
# Python環境セットアップ (M1 Mac最適化)
cd backend
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e .[dev]

# 開発サーバー起動
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 品質チェック
ruff check src/ --fix           # Linting + 自動修正
ruff format src/                # フォーマット
mypy src/ --strict              # 型チェック (strict)
pytest tests/ --cov=src --cov-report=html --cov-fail-under=80

# AIエージェント実行用コマンド
/ai:development:implement backend-setup
/ai:architecture:design clean-architecture
/ai:quality:tdd test-coverage --target 80
```

### Phase 4: データベース・ベクトル環境

```bash
# Turso CLI セットアップ
brew install tursodatabase/tap/turso
turso auth login

# データベース作成と設定
turso db create autoforgenexus
turso db create autoforgenexus-dev --from-db autoforgenexus
turso db tokens create autoforgenexus

# Redis セットアップ
redis-server --daemonize yes --port 6379
redis-cli ping                  # PONG が返ることを確認

# マイグレーション実行
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# AIエージェント実行用コマンド
/ai:data:vector setup-libsql-vector
/ai:data:migrate zero-downtime-migration
```

### Phase 5: フロントエンド (Next.js 15.5.4/React 19.0.0)

```bash
# Node.js環境セットアップ (M1/M2/M3最適化)
volta install node@22           # Node.js 22 LTS - ARM64ネイティブ
volta install pnpm@9            # pnpm 9.x
pnpm config set store-dir ~/.pnpm-store

# フロントエンド環境構築
cd frontend
pnpm install                    # 依存関係インストール
npx shadcn@latest init         # shadcn/ui 3.3.1 (React 19・Tailwind v4対応)
pnpm dev --turbo               # Turbopack開発サーバー (localhost:3000)

# ビルドとテスト
pnpm build                      # Next.js本番ビルド
pnpm test                       # Jest単体テスト
pnpm test:e2e                   # Playwright E2Eテスト
pnpm lint                       # ESLint チェック
pnpm type-check                 # TypeScript検証

# AIエージェント実行用コマンド
/ai:architecture:design frontend-layer
/sc:design ui-components --shadcn
```

### Phase 6: 統合・品質保証

```bash
# 統合テスト実行
make test-all                   # 全テスト実行
make perf-test                  # パフォーマンステスト
make security-scan              # セキュリティスキャン

# 品質メトリクス
cd backend && pytest --cov=src --cov-report=html
cd frontend && pnpm test:coverage
sonar-scanner                   # SonarQube分析

# 監視スタック起動
docker-compose -f docker-compose.monitoring.yml up -d
open http://localhost:9090      # Prometheus
open http://localhost:3001      # Grafana
open http://localhost:3002      # LangFuse

# AIエージェント実行用コマンド
/ai:quality:tdd test-env --playwright --pytest --jest --coverage 80
/ai:operations:deploy pipeline --github-actions --cloudflare
/ai:quality:security scan --owasp --gdpr --trivy
```

### 本番デプロイ・CI/CD

```bash
# GitHub Actions ワークフロー
gh workflow run ci.yml          # CI実行
gh workflow run deploy.yml      # デプロイ実行
gh run watch                    # 実行状況監視

# Cloudflare デプロイ
wrangler login                  # Cloudflare認証
wrangler deploy                 # Workers デプロイ
wrangler pages deploy frontend/out  # Pages デプロイ

# リリース管理
gh release create v1.0.0 --generate-notes
```

### トラブルシューティング

```bash
# 環境リセット
docker-compose down -v          # 全コンテナ・ボリューム削除
docker system prune -a          # Docker完全クリーンアップ

# ログ確認
docker-compose logs backend     # バックエンドログ
docker-compose logs frontend    # フロントエンドログ
docker-compose logs redis       # Redisログ

# パフォーマンス診断
k6 run tests/performance/k6-scenario.js  # K6負荷テスト
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

## プロジェクト構造

6 フェーズ構築に基づくクリーンアーキテクチャ：

```
/                   # プロジェクトルート（Phase 1: Git管理）
├── .github/        # GitHub Actions, Issue/PR テンプレート
├── .gitignore      # 多言語対応（Python + Node.js + Docker）
├── docker-compose.dev.yml    # 開発環境（Phase 2）
├── docker-compose.prod.yml   # 本番環境
├── docker-compose.monitoring.yml  # 監視スタック
├── sonar-project.properties      # 品質ゲート設定
└── release-please-config.json    # 自動リリース設定

/backend/           # Python/FastAPI（Phase 3）
  /src/
    /domain/        # 機能ベース集約パターン
      /prompt/      # プロンプト管理機能 ✅
        /entities/, /value_objects/, /services/, /repositories/
      /evaluation/, /llm_integration/, /user_interaction/, /workflow/
      /shared/      # 共通要素
    /application/   # CQRSパターン ✅
      /prompt/, /evaluation/, /llm_integration/, /user_interaction/, /workflow/
        /commands/, /queries/, /services/
      /shared/      # 共通要素 ✅
        /commands/, /queries/, /services/, /dto/, /events/
    /core/          # 横断的関心事層 ✅
      /config/      # 設定管理（settings/, environments/, validators/, loaders/）
      /security/    # セキュリティ（authentication/, authorization/, encryption/, validation/）
      /exceptions/, /logging/, /middleware/, /monitoring/, /dependencies/
    /infrastructure/ # 機能ベース実装層 ✅
      /prompt/, /evaluation/, /llm_integration/, /user_interaction/, /workflow/
        /repositories/, /adapters/
      /shared/      # database/, monitoring/, auth/
    /presentation/  # API層
      /api/v1/      # prompt/, evaluation/, llm/, user/, workflow/
      /websocket/   # handlers/
  /tests/           # 機能ごとのテスト構造
    /unit/domain/prompt/ ✅
    /integration/, /e2e/
  requirements.txt  # Python依存関係
  alembic.ini      # データベースマイグレーション

/frontend/          # Next.js 15.5.4/React 19.0.0（Phase 5）
  /src/
    /app/          # App Router (Next.js 15.5.4)
    /components/   # React 19.0.0 Server Components + shadcn/ui 3.3.1
    /lib/          # ユーティリティ・Clerk統合
    /hooks/        # React 19.0.0 カスタムフック (use API)
    /stores/       # Zustand 5.0.8状態管理
    /styles/       # Tailwind CSS 4.0.0 スタイル
  /tests/          # Jest + Playwright E2E (75%+カバレッジ)
  playwright.config.ts  # E2Eテスト設定
  tailwind.config.ts    # Tailwind CSS 4.0.0設定 (OKLCH)
  next.config.js   # Next.js 15.5.4 Turbopack設定
  tsconfig.json    # TypeScript 5.9.2 strict設定

/monitoring/        # 観測性設定（Phase 6）
  prometheus.yml    # メトリクス収集
  grafana/          # ダッシュボード
  loki-config.yaml  # ログ集約

/docs/              # 技術文書
  /development/     # Phase別セットアップガイド
  /security/        # セキュリティポリシー・GDPR
  /setup/           # 6フェーズ環境構築手順
```

## Claude Code 設定

### 🤖 モデル設定

- **使用モデル**: Claude Opus 4.1 (`claude-opus-4-1-20250805`)
- **最大トークン**: 32,000
- **温度**: 0.2（一貫性重視）
- **タイムアウト**: 120 秒

### 📦 必須 MCP サーバー

```bash
# MCPサーバーはnpxで自動インストールされます（手動インストール不要）
# 設定は .claude/settings.json を参照

# 必須サーバー
- serena          # セマンティックコード理解・メモリ管理
- context7        # ライブラリドキュメンテーション検索
- sequential      # 複雑な分析・体系的問題解決
- github          # GitHub統合・PR管理

# オプションサーバー
- playwright      # ブラウザ自動化・E2Eテスト
- brave-search    # Web検索（要API KEY）
- desktop-commander # デスクトップ操作
```

### 🎭 専門エージェント（30 種類）

#### アーキテクチャ設計

- `system-architect`: システム全体設計、技術選定
- `domain-modeller`: DDD 境界コンテキスト、集約設計
- `api-designer`: OpenAPI/GraphQL/gRPC 設計

#### フロントエンド開発

- `frontend-architect`: React 19.0.0/Next.js 15.5.4 アーキテクチャ
- `uiux-designer`: shadcn/ui 3.3.1、OKLCH 色空間
- `real-time-specialist`: WebSocket/WebRTC 実装

#### バックエンド開発

- `backend-developer`: Python 3.13/FastAPI 実装
- `database-administrator`: Turso/Redis 管理
- `vector-specialist`: libSQL Vector 検索最適化
- `event-bus-manager`: Redis Streams/CQRS 実装

#### 品質・運用

- `test-automation-engineer`: Playwright/pytest 自動化
- `performance-optimizer`: Core Web Vitals 最適化
- `observability-engineer`: LangFuse/監視設定
- `version-control-specialist`: Git 戦略・PR 管理

### 🔧 開発ワークフロー

#### 1. セッション開始

```bash
# プロジェクトをアクティベート
serena activate /path/to/AutoForgeNexus

# 前回のセッションを読み込み
/sc:load

# 現在の状態確認
git status && git branch
```

#### 2. 実装作業

```bash
# 適切なエージェントを選択
/ai:core:team --task "認証機能実装"

# または個別エージェント実行
/ai:backend:implement auth-system
/ai:frontend:implement login-ui
```

#### 3. 品質チェック

```bash
# 自動品質チェック
/ai:quality:analyze --full
/ai:quality:security scan
/ai:quality:tdd coverage --target 80
```

#### 4. セッション終了

```bash
# 作業内容を保存
/sc:save

# コミット・PR作成
/ai:development:git commit --granular
/ai:development:git pr --auto-merge
```

## 重要なコンテキスト

### 環境構築フロー

**Phase 1-6 の順次実行が必須**

1. **Phase 1**: Git・基盤環境確認 → GitFlow・GitHub Actions・ブランチ保護
2. **Phase 2**: インフラ・Docker 環境 → docker-compose.dev.yml 構築
3. **Phase 3**: バックエンド → Python 3.13・FastAPI・DDD 構造
4. **Phase 4**: データベース → Turso・Redis・libSQL Vector
5. **Phase 5**: フロントエンド → Next.js 15.5.4・React 19.0.0・Tailwind CSS
   4.0.0・shadcn/ui 3.3.1
6. **Phase 6**: 統合・品質保証 → テスト・監視・セキュリティ

### 開発品質基準

- **テストカバレッジ**: バックエンド 80%+、フロントエンド 75%+必須
- **型安全性**: mypy strict モード、TypeScript 5.9.2 strict 設定
- **セキュリティ**: OWASP Top 10 対策、GDPR 準拠、自動脆弱性スキャン
- **パフォーマンス**:
  - API P95 < 200ms
  - WebSocket 10,000 同時接続 (Node.js 22 ネイティブ)
  - Turbopack: 50%高速冷起動 (Next.js 15.5.4)
  - React 19.0.0: 30%高速ホットリロード
  - Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1
- **CI/CD**: 並列実行で 5 分以内、Cloudflare 自動デプロイ

### 主要アーキテクチャ決定

- **クリーンアーキテクチャ**: DDD 準拠、依存関係逆転、レイヤー分離
- **イベント駆動**: 状態変更の完全記録、CQRS 実装
- **分散データベース**: Turso (libSQL)、Redis キャッシング、Vector 検索
- **認証**: Clerk 6.32.0（OAuth 2.0, MFA, 組織管理）
- **観測性**: LangFuse LLM トレーシング、Prometheus/Grafana 監視
- **エッジ最適化**: Cloudflare Workers/Pages、CDN 活用

### 必須開発ツール

```bash
# 環境確認コマンド（最優先）
git --version     # 2.40+
node --version    # 20.0+
pnpm --version    # 8.0+
docker --version  # 24.0+
python3.13 --version
```

### セキュリティ・コンプライアンス

- **自動セキュリティスキャン**: Trivy、Snyk、OWASP ZAP
- **秘匿情報検出**: TruffleHog、gitleaks
- **GDPR 準拠**: データポータビリティ、忘れられる権利
- **セキュリティヘッダー**: CSP、HSTS、XSS プロテクション

### 監視・観測性

- **メトリクス**: Prometheus（システム）、LangFuse（LLM）
- **ログ**: Loki 集約、構造化ログ
- **アラート**: Slack/Discord 通知、DORA メトリクス
- **ダッシュボード**: Grafana（3001）、LangFuse（3002）

### 革新的機能（17 項目）

- **意図差分ビューワー**: プロンプト改善ギャップ可視化
- **スタイル・ゲノム**: ユーザー固有スタイル学習・適用
- **プロンプト SLO**: 品質メトリクス自動監視
- **Git-like バージョニング**: ブランチ・マージ・ロールバック

## 2025 年最新フロントエンド技術詳細

### React 19.0.0 新機能

```jsx
// Server Componentsデフォルト
export default async function ProductList() {
  const products = await fetchProducts(); // サーバー実行
  return <ProductGrid products={products} />;
}

// 新use API
function SearchResults() {
  const results = use(searchPromise); // 非同期データ簡素化
  return <ResultsList results={results} />;
}

// forwardRef不要
function Button({ ref, ...props }) {
  return <button ref={ref} {...props} />;
}
```

### Next.js 15.5.4 機能

```javascript
// next.config.js - Turbopack設定
module.exports = {
  experimental: {
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
  },
  // TypeScript型付きルート
  experimental: {
    typedRoutes: true,
  },
};
```

### Tailwind CSS 4.0.0 設定

```css
/* tailwind.config.ts */
@import 'tailwindcss';

@theme {
  --color-primary: oklch(59.4% 0.238 251.4);
  --color-secondary: oklch(49.1% 0.3 275.8);

  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  --spacing-unit: 0.25rem;
  --radius-default: 0.5rem;
}

/* OKLCH色空間の利点 */
.gradient {
  background: linear-gradient(in oklch, oklch(90% 0.1 100), oklch(50% 0.2 250));
}
```

### パフォーマンスベンチマーク（2025 年基準）

| メトリクス                  | 目標値  | 実測値 |
| --------------------------- | ------- | ------ |
| Turbopack 冷起動            | < 500ms | 450ms  |
| React 19.0.0 ホットリロード | < 100ms | 80ms   |
| TypeScript 型チェック       | < 2s    | 1.5s   |
| 本番ビルド時間              | < 60s   | 45s    |
| バンドルサイズ              | < 200KB | 180KB  |
| メモリ使用量                | < 512MB | 380MB  |

### マイグレーションガイド

#### React 18 → 19.0.0

```bash
# 自動マイグレーション
npx react-codemod@latest react-19/remove-forward-ref
npx react-codemod@latest react-19/use-transition
```

#### Tailwind CSS 3 → 4.0.0

```bash
# アップグレード
pnpm remove tailwindcss postcss autoprefixer
pnpm add -D tailwindcss@4.0.0 postcss autoprefixer

# 設定移行
npx @tailwindcss/upgrade@latest
```

#### Next.js 14 → 15.5.4

```bash
# アップグレード
pnpm add next@15.5.4 react@19.0.0 react-dom@19.0.0
pnpm add -D @types/react@19.0.6 @types/react-dom@19.0.2

# Turbopack有効化
pnpm dev --turbo
pnpm build --turbo
```

## 📊 開発進捗状況

### Phase 1: Git・基盤環境 ✅ 完了 (100%)

- **1.1 Git 環境**: GitFlow、ブランチ保護、コミットテンプレート ✅
- **1.2 GitHub 設定**: CI/CD、Issue/PR テンプレート、セキュリティ設定 ✅
- **1.3 CI/CD 環境対応**: 段階的環境構築、権限修正 ✅

### Phase 2: インフラ・監視基盤 ✅ 完了 (100%)

- **2.1 Docker環境**: 開発環境構築、docker-compose設定 ✅
- **2.2 Cloudflare設定**: Workers Python、Pages、セキュリティ ✅
- **2.3 デプロイメント**: CI/CD、自動デプロイ、ロールバック ✅
- **2.4 監視基盤**: Prometheus、Grafana、LangFuse、構造化ログ ✅
- **2.5 CI/CD最適化**: GitHub Actions共有ワークフロー、52.3%コスト削減 ✅
- **2.6 セキュリティ強化**: CodeQL、TruffleHog、監査ログ実装 ✅

### Phase 3: バックエンド (Python 3.13/FastAPI) 🚧 進行中 (40%)

#### 完了項目 ✅

- **3.1 環境構築**: Python 3.13 + FastAPI 0.116.1環境 ✅
- **3.2 プロジェクト構造**: DDD + Clean Architectureディレクトリ構造 ✅
- **3.3 設定管理**: Pydantic v2階層型環境設定システム ✅
- **3.4 テスト基盤**: pytest + coverage設定（目標80%） ✅
- **3.5 Docker統合**: 開発用Dockerfile.dev作成 ✅
- **3.6 DB準備**: Alembicマイグレーション環境 ✅

#### 実装中 🚧

- **3.7 ドメインモデル**: プロンプト管理エンティティ設計
- **3.8 認証システム**: Clerk統合準備

#### 未実装 📋

- LiteLLM統合（100+プロバイダー対応）
- CQRS実装（コマンド/クエリ分離）
- Redis Streamsイベントバス
- 並列評価実行システム
- バージョン管理機能

### Phase 4-6: 未着手

- Phase 4: データベース（Turso, Redis, libSQL Vector）
- Phase 5: フロントエンド（Next.js 15.5.4/React 19.0.0）
- Phase 6: 統合・品質保証

## 📋 重要な作業指針

### ✅ 必須ルール

1. **要求された作業のみ実行** - 追加機能の勝手な実装禁止
2. **既存ファイル優先** - 新規作成より既存ファイル編集を優先
3. **ドキュメント作成制限** - 明示的要求がない限り README 等を作成しない
4. **テストカバレッジ遵守** - Backend 80%、Frontend 75%必須
5. **型安全性厳守** - mypy --strict、tsc --strict 必須
6. **段階的環境構築対応** - Phase未実装部分はCI/CDでスキップ

### 🚀 推奨プラクティス

- **並列処理優先**: 独立したタスクは並列実行
- **TodoWrite 活用**: 3 段階以上のタスクは必ず Todo 管理
- **エージェント活用**: タスクに適した専門エージェントを選択
- **メモリ永続化**: Serena メモリでセッション間の継続性確保
- **品質ゲート**: コミット前に lint/typecheck/test 実行

### ⚠️ 注意事項

- **秘密情報管理**: .env、API KEY 等を絶対にコミットしない
- **ブランチ戦略**: main 直接編集禁止、必ずフィーチャーブランチ使用
- **コミット規約**: Conventional Commits 形式で日本語メッセージ
- **PR 要件**: 最低 1 名のレビュー必須、CI 全パス必須

### 🎯 クイックスタート

```bash
# 1. プロジェクト初期化
git clone https://github.com/daishiman/AutoForgeNexus.git
cd AutoForgeNexus
cp .claude/.env.example .env

# 2. Claude Codeでセッション開始
serena activate .
/sc:load

# 3. 開発開始
/ai:core:init              # プロジェクト初期化
/ai:core:team --planning    # タスク計画
/ai:development:implement   # 実装開始

# 4. 品質チェック・デプロイ
/ai:quality:analyze
/ai:operations:deploy
```
