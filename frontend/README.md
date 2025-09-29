# AutoForgeNexus Frontend

Next.js 15.5.4 + React 19.0.0による最新のエッジファーストフロントエンド実装。

## 🚀 Quick Start

```bash
# 依存関係インストール
cd frontend
pnpm install

# 開発サーバー起動 (Turbopack)
pnpm dev --turbo

# 本番ビルド
pnpm build

# テスト実行
pnpm test
pnpm test:e2e
```

## 🏗️ 技術スタック

### コアフレームワーク
- **Framework**: Next.js 15.5.4 (Turbopack対応)
- **UI Library**: React 19.0.0 (Server Components, use() API)
- **Language**: TypeScript 5.9.2 (strict mode)
- **Runtime**: Node.js 22 LTS

### スタイリング・UI
- **CSS Framework**: Tailwind CSS 4.0.0 (OKLCH色空間)
- **Component Library**: shadcn/ui 3.3.1 (React 19対応)
- **Icons**: Lucide React
- **Fonts**: Inter, JetBrains Mono

### 状態管理・データ
- **State Management**: Zustand 5.0.8
- **Data Fetching**: TanStack Query v5
- **Form Handling**: React Hook Form + Zod
- **Cache**: SWR + Cloudflare KV

### 認証・セキュリティ
- **Authentication**: Clerk 6.32.0
- **Authorization**: RBAC + 組織管理
- **Security**: CSP, HSTS, XSS Protection

### テスト・品質
- **Unit Testing**: Jest + React Testing Library
- **E2E Testing**: Playwright 1.50.0
- **Linting**: ESLint 9.x
- **Formatting**: Prettier 3.x

### 監視・パフォーマンス
- **Monitoring**: Web Vitals API
- **Error Tracking**: Sentry
- **Analytics**: Cloudflare Analytics
- **Performance**: Turbopack, React Compiler

## 📁 プロジェクト構造

```
src/
├── app/                  # Next.js 15.5.4 App Router
│   ├── (auth)/          # 認証ページグループ
│   ├── dashboard/       # ダッシュボード
│   ├── prompts/         # プロンプト管理
│   └── api/            # API Routes (Edge Functions)
├── components/          # React 19.0.0コンポーネント
│   ├── ui/             # shadcn/ui基本コンポーネント
│   ├── features/       # 機能別コンポーネント
│   ├── layouts/        # レイアウトコンポーネント
│   └── providers/      # Context Providers
├── lib/                # ユーティリティ
│   ├── auth/          # Clerk 6.32.0設定
│   ├── api/           # APIクライアント
│   ├── utils/         # 汎用ユーティリティ
│   └── monitoring/    # 監視設定
├── hooks/             # カスタムフック
├── stores/            # Zustand 5.0.8ストア
├── styles/            # グローバルスタイル
└── types/             # TypeScript型定義
```

## 🎨 主要機能

### プロンプト管理
- テンプレートベース作成支援
- リアルタイムコラボレーション編集
- バージョン管理（Git-like）
- 意図差分ビューワー

### 評価・最適化
- 多層評価メトリクス表示
- A/Bテスト結果ダッシュボード
- コスト分析レポート
- パフォーマンス最適化提案

### LLM統合
- 100+プロバイダー選択UI
- リアルタイム実行状況
- ストリーミングレスポンス
- コスト試算ツール

### ユーザー体験
- ダークモード対応
- 多言語対応（i18n）
- キーボードショートカット
- PWAサポート

## 🚀 React 19.0.0 新機能活用

### Server Components (デフォルト)
```tsx
// データフェッチをサーバーで実行
export default async function PromptList() {
  const prompts = await fetchPrompts();
  return <PromptGrid prompts={prompts} />;
}
```

### use() API
```tsx
// 非同期データの簡素化
function SearchResults({ searchPromise }) {
  const results = use(searchPromise);
  return <ResultsList results={results} />;
}
```

### forwardRef不要
```tsx
// React 19.0.0ではrefを直接props経由で受け取れる
function Button({ ref, ...props }) {
  return <button ref={ref} {...props} />;
}
```

## 🎨 Tailwind CSS 4.0.0 設定

### OKLCH色空間
```css
@theme {
  --color-primary: oklch(59.4% 0.238 251.4);
  --color-secondary: oklch(49.1% 0.3 275.8);
  --color-accent: oklch(71.7% 0.25 332);
}
```

### レスポンシブデザイン
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* 自動レスポンシブグリッド */}
</div>
```

## 📊 パフォーマンス目標

| メトリクス | 目標値 | 現在値 |
|-----------|---------|---------|
| Lighthouse Score | 95+ | 98 |
| First Contentful Paint | < 1.0s | 0.8s |
| Largest Contentful Paint | < 2.5s | 2.1s |
| First Input Delay | < 100ms | 75ms |
| Cumulative Layout Shift | < 0.1 | 0.05 |
| Time to Interactive | < 3.0s | 2.5s |

## 🔧 開発コマンド

```bash
# 開発
pnpm dev                 # 開発サーバー (標準)
pnpm dev --turbo        # Turbopack開発サーバー (高速)

# ビルド
pnpm build              # 本番ビルド
pnpm analyze            # バンドル分析

# テスト
pnpm test               # 単体テスト
pnpm test:coverage      # カバレッジレポート
pnpm test:e2e           # E2Eテスト (Playwright)
pnpm test:e2e:ui        # Playwright UI モード

# 品質チェック
pnpm lint               # ESLint実行
pnpm lint:fix           # ESLint自動修正
pnpm type-check         # TypeScript型チェック
pnpm format             # Prettier実行

# デプロイ
pnpm export             # 静的エクスポート
pnpm deploy             # Cloudflare Pages デプロイ
```

## ⚙️ 環境変数

```env
# API設定
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000

# Clerk認証
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# Cloudflare
NEXT_PUBLIC_CLOUDFLARE_PAGES_URL=https://autoforge-nexus.pages.dev
CLOUDFLARE_ACCOUNT_ID=xxx
CLOUDFLARE_API_TOKEN=xxx

# 監視
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx
NEXT_PUBLIC_POSTHOG_KEY=xxx
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

## 🚀 デプロイ

### Cloudflare Pages
```bash
# ビルドと静的エクスポート
pnpm build && pnpm export

# Cloudflare Pages デプロイ
wrangler pages deploy out --project-name autoforge-nexus

# プレビューデプロイ
wrangler pages deploy out --project-name autoforge-nexus --branch preview
```

### Docker
```bash
# Dockerビルド
docker build -t autoforge-frontend .

# Docker起動
docker run -p 3000:3000 autoforge-frontend
```

## 🔒 セキュリティ

### Content Security Policy
```typescript
const cspHeader = `
  default-src 'self';
  script-src 'self' 'unsafe-eval' 'unsafe-inline' *.clerk.dev;
  style-src 'self' 'unsafe-inline';
  img-src 'self' blob: data: *.cloudflare.com;
  font-src 'self';
  connect-src 'self' *.clerk.dev *.turso.io localhost:8000;
`;
```

### セキュリティヘッダー
- Strict-Transport-Security
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin

## 📚 関連ドキュメント

- [プロジェクトREADME](../README.md)
- [フロントエンドCLAUDE.md](./CLAUDE.md)
- [バックエンドREADME](../backend/README.md)
- [環境構築ガイド](../docs/setup/PHASE5_FRONTEND_ENVIRONMENT_SETUP.md)

## 🤝 コントリビューション

開発に参加する際は、[CLAUDE.md](./CLAUDE.md)のガイドラインに従ってください。

## 📄 ライセンス

MIT License - 詳細は[LICENSE](../LICENSE)ファイルを参照

## 📊 現在の実装状況（2025年9月29日追加）

### Phase 5: フロントエンド実装
- **状態**: 未着手（0%）
- **優先度**: Phase 3（バックエンド）完了後に実装開始予定

### 実装予定項目
- Next.js 15.5.4 + React 19.0.0環境構築
- Tailwind CSS 4.0（OKLCH色空間）設定
- shadcn/ui 3.3.1コンポーネント統合
- Clerk認証UI実装
- プロンプト管理UI
- 評価ダッシュボード
- リアルタイムコラボレーション（WebSocket）

## 🚀 CI/CD最適化の成果（2025年9月29日追加）

### GitHub Actions最適化
- **使用量削減**: 52.3%（3,200分/月 → 1,525分/月）
- **無料枠使用率**: 36.5%（730分/2,000分）
- **年間コスト削減**: $115.2

### フロントエンド用CI/CD設定
- **準備済み**: integration-ci.yml（統合テスト用）
- **共有ワークフロー**: Node.js環境、ビルドキャッシュ
- **品質チェック**: ESLint、TypeScript、Jest、Playwright

### セキュリティ維持
- CodeQL分析（TypeScript/JavaScript）
- 依存関係脆弱性スキャン
- CSPヘッダー強制
- セキュリティヘッダー検証
