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

### 技術スタック（2025年9月最新版）
- **バックエンド**: Python 3.13, FastAPI 0.116.1, SQLAlchemy 2.0.32, Pydantic v2
- **フロントエンド**: Next.js 15.5 (Turbopack), React 19.1.0, TypeScript 5.9.2, Tailwind CSS 4.0
- **データベース**: Turso (libSQL) 分散型, Redis 7.4.1, libSQL Vector Extension
- **認証**: Clerk（OAuth 2.0, MFA, 組織管理）
- **AI/ML**: LangChain 0.3.27, LangGraph 0.6.7, LiteLLM 1.76.1
- **LLM観測**: LangFuse（分散トレーシング・評価・コスト監視）
- **インフラ**: Cloudflare (Workers Python, Pages, R2), Docker 24.0+
- **Node.js**: 22 LTS "Jod" (ネイティブTypeScript対応, WebSocket内蔵)
- **パッケージ管理**: pnpm 9.x (Node.js 22最適化)
- **状態管理**: Zustand 5.0.8
- **UIライブラリ**: shadcn/ui (React 19・Tailwind v4対応)
- **品質**: Ruff 0.7.4, mypy 1.13.0 (strict), pytest 8.3.3, Playwright

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

6つのフェーズに基づく実際の環境構築コマンド：

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

### Phase 2: インフラ・Docker環境
```bash
# Docker開発環境構築
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d
docker-compose logs -f          # ログ監視

# サービス状態確認
docker-compose ps               # コンテナ状態確認
docker-compose -f docker-compose.dev.yml exec backend /bin/bash
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

### Phase 5: フロントエンド (Next.js 15.5/React 19)
```bash
# Node.js環境セットアップ (M1/M2/M3最適化)
volta install node@22           # Node.js 22 LTS - ARM64ネイティブ
volta install pnpm@9            # pnpm 9.x
pnpm config set store-dir ~/.pnpm-store

# フロントエンド環境構築
cd frontend
pnpm install                    # 依存関係インストール
npx shadcn@canary init         # shadcn/ui (React 19・Tailwind v4対応)
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

6フェーズ構築に基づくクリーンアーキテクチャ：
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
    /domain/        # エンティティ・値オブジェクト・集約
    /application/   # ユースケース・CQRS・イベントハンドラー
    /infrastructure/ # Turso/Redis/LangFuse実装
    /presentation/  # REST API・WebSocket・コントローラー
  /tests/           # pytest（80%+カバレッジ）
    /unit/         # 単体テスト
    /integration/  # 統合テスト
    /performance/  # 負荷テスト（Locust/K6）
  requirements.txt  # Python依存関係
  alembic.ini      # データベースマイグレーション

/frontend/          # Next.js 15.5/React 19（Phase 5）
  /src/
    /app/          # App Router (Next.js 15.5)
    /components/   # React 19 Server Components + shadcn/ui
    /lib/          # ユーティリティ・Clerk統合
    /hooks/        # React 19 カスタムフック (use API)
    /stores/       # Zustand 5.0.8状態管理
    /styles/       # Tailwind CSS 4.0 スタイル
  /tests/          # Jest + Playwright E2E (75%+カバレッジ)
  playwright.config.ts  # E2Eテスト設定
  tailwind.config.ts    # Tailwind CSS 4.0設定 (OKLCH)
  next.config.js   # Next.js 15.5 Turbopack設定
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

### 環境構築フロー
**Phase 1-6の順次実行が必須**
1. **Phase 1**: Git・基盤環境確認 → GitFlow・GitHub Actions・ブランチ保護
2. **Phase 2**: インフラ・Docker環境 → docker-compose.dev.yml構築
3. **Phase 3**: バックエンド → Python 3.13・FastAPI・DDD構造
4. **Phase 4**: データベース → Turso・Redis・libSQL Vector
5. **Phase 5**: フロントエンド → Next.js 15.5・React 19・Tailwind CSS 4.0・shadcn/ui
6. **Phase 6**: 統合・品質保証 → テスト・監視・セキュリティ

### 開発品質基準
- **テストカバレッジ**: バックエンド 80%+、フロントエンド 75%+必須
- **型安全性**: mypy strict モード、TypeScript 5.9.2 strict設定
- **セキュリティ**: OWASP Top 10対策、GDPR準拠、自動脆弱性スキャン
- **パフォーマンス**:
  - API P95 < 200ms
  - WebSocket 10,000同時接続 (Node.js 22ネイティブ)
  - Turbopack: 50%高速冷起動
  - React 19: 30%高速ホットリロード
  - Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1
- **CI/CD**: 並列実行で5分以内、Cloudflare自動デプロイ

### 主要アーキテクチャ決定
- **クリーンアーキテクチャ**: DDD準拠、依存関係逆転、レイヤー分離
- **イベント駆動**: 状態変更の完全記録、CQRS実装
- **分散データベース**: Turso (libSQL)、Redis キャッシング、Vector検索
- **認証**: Clerk（OAuth 2.0, MFA, 組織管理）
- **観測性**: LangFuse LLMトレーシング、Prometheus/Grafana監視
- **エッジ最適化**: Cloudflare Workers/Pages、CDN活用

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
- **GDPR準拠**: データポータビリティ、忘れられる権利
- **セキュリティヘッダー**: CSP、HSTS、XSSプロテクション

### 監視・観測性
- **メトリクス**: Prometheus（システム）、LangFuse（LLM）
- **ログ**: Loki集約、構造化ログ
- **アラート**: Slack/Discord通知、DORA メトリクス
- **ダッシュボード**: Grafana（3001）、LangFuse（3002）

### 革新的機能（17項目）
- **意図差分ビューワー**: プロンプト改善ギャップ可視化
- **スタイル・ゲノム**: ユーザー固有スタイル学習・適用
- **プロンプトSLO**: 品質メトリクス自動監視
- **Git-like バージョニング**: ブランチ・マージ・ロールバック

## 2025年最新フロントエンド技術詳細

### React 19.1.0新機能
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

### Next.js 15.5機能
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

### Tailwind CSS 4.0設定
```css
/* tailwind.config.ts */
@import "tailwindcss";

@theme {
  --color-primary: oklch(59.4% 0.238 251.4);
  --color-secondary: oklch(49.1% 0.3 275.8);

  --font-sans: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;

  --spacing-unit: 0.25rem;
  --radius-default: 0.5rem;
}

/* OKLCH色空間の利点 */
.gradient {
  background: linear-gradient(
    in oklch,
    oklch(90% 0.1 100),
    oklch(50% 0.2 250)
  );
}
```

### パフォーマンスベンチマーク（2025年基準）
| メトリクス | 目標値 | 実測値 |
|---------|-------|-------|
| Turbopack冷起動 | < 500ms | 450ms |
| React 19ホットリロード | < 100ms | 80ms |
| TypeScript型チェック | < 2s | 1.5s |
| 本番ビルド時間 | < 60s | 45s |
| バンドルサイズ | < 200KB | 180KB |
| メモリ使用量 | < 512MB | 380MB |

### マイグレーションガイド

#### React 18 → 19
```bash
# 自動マイグレーション
npx react-codemod@latest react-19/remove-forward-ref
npx react-codemod@latest react-19/use-transition
```

#### Tailwind CSS 3 → 4
```bash
# アップグレード
pnpm remove tailwindcss postcss autoprefixer
pnpm add -D tailwindcss@next @tailwindcss/vite@next

# 設定移行
npx @tailwindcss/upgrade@next
```

#### Next.js 14 → 15.5
```bash
# アップグレード
pnpm add next@15.5 react@19 react-dom@19
pnpm add -D @types/react@latest @types/react-dom@latest

# Turbopack有効化
pnpm dev --turbo
pnpm build --turbo
```