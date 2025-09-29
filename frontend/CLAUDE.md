# Frontend CLAUDE.md

このファイルは、AutoForgeNexusのフロントエンドを作業する際のClaude Code (claude.ai/code) へのガイダンスを提供します。

## 🎯 フロントエンド概要

Next.js 15.5.4 + React 19.0.0による最新のエッジファーストフロントエンド実装。Cloudflare Pagesでのデプロイ最適化。

## 🏗️ アーキテクチャ

### ディレクトリ構造

```
src/
├── app/                # Next.js 15.5.4 App Router
│   ├── api/           # API Routes (Edge Functions)
│   ├── dashboard/     # ダッシュボード
│   └── (auth)/        # 認証関連ページ
├── components/         # React 19.0.0 コンポーネント
│   ├── auth/          # 認証コンポーネント
│   ├── client/        # Client Components
│   ├── server/        # Server Components
│   └── providers/     # Context Providers
├── lib/               # ユーティリティ
│   ├── auth/          # Clerk 6.32.0認証
│   └── monitoring/    # クライアント監視
├── middleware/        # エッジミドルウェア
│   └── observability.ts # 監視ミドルウェア
├── hooks/             # React 19.0.0 カスタムフック
├── stores/            # Zustand 5.0.8状態管理
└── types/             # TypeScript型定義
```

### 主要技術

- **Framework**: Next.js 15.5.4 (Turbopack)
- **UI Library**: React 19.0.0
- **Language**: TypeScript 5.9.2
- **Styling**: Tailwind CSS 4.0.0 (OKLCH色空間)
- **Components**: shadcn/ui 3.3.1 (React 19対応)
- **State**: Zustand 5.0.8
- **Auth**: Clerk 6.32.0 (OAuth 2.0, MFA)

## 🚀 React 19.0.0 新機能活用

### Server Components（デフォルト）

```tsx
// ✅ サーバーコンポーネント（デフォルト）
export default async function ProductList() {
  const products = await fetchProducts(); // サーバー実行
  return <ProductGrid products={products} />;
}
```

### use API活用

```tsx
// ✅ 新しいuse API
function SearchResults({ searchPromise }) {
  const results = use(searchPromise); // 非同期データ簡素化
  return <ResultsList results={results} />;
}
```

### forwardRef不要

```tsx
// ✅ React 19.0.0でforwardRef不要
function Button({ ref, ...props }) {
  return <button ref={ref} {...props} />;
}
```

## 🎨 Tailwind CSS 4.0.0設定

### OKLCH色空間

```css
/* tailwind.config.ts */
@theme {
  --color-primary: oklch(59.4% 0.238 251.4);
  --color-secondary: oklch(49.1% 0.3 275.8);
  --color-accent: oklch(71.7% 0.25 332);
}

/* より滑らかなグラデーション */
.gradient {
  background: linear-gradient(
    in oklch,
    oklch(90% 0.1 100),
    oklch(50% 0.2 250)
  );
}
```

## 📁 主要ファイル説明

### src/app/api/health/route.ts
- **役割**: ヘルスチェックエンドポイント
- **機能**: システム状態、依存関係チェック、Web Vitals

### src/lib/monitoring/index.ts
- **役割**: クライアント側監視
- **機能**:
  - Web Vitals測定（LCP、FID、CLS）
  - エラー追跡とレポート
  - ユーザーインタラクション追跡
  - パフォーマンスメトリクス

### src/middleware/observability.ts
- **役割**: エッジミドルウェア監視
- **機能**:
  - リクエスト追跡
  - レスポンスタイム測定
  - セキュリティヘッダー追加
  - 相関ID生成

### src/lib/auth/clerk-config.ts
- **役割**: 認証設定
- **機能**:
  - OAuth 2.0プロバイダー設定
  - MFA設定
  - 組織管理
  - セッション管理

## 🚀 開発コマンド

```bash
# 依存関係インストール
pnpm install

# 開発サーバー起動（Turbopack）
pnpm dev --turbo

# 本番ビルド
pnpm build

# 静的エクスポート（Cloudflare Pages用）
pnpm export

# 品質チェック
pnpm lint                  # ESLint
pnpm type-check           # TypeScript
pnpm test                 # Jest
pnpm test:e2e            # Playwright

# Cloudflareデプロイ
wrangler pages deploy out --project-name autoforge-nexus-frontend
```

## ⚙️ 環境変数

必須設定項目（.env.local）:

```env
# API設定
NEXT_PUBLIC_API_URL=http://localhost:8000

# Clerk認証
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx

# Cloudflare
NEXT_PUBLIC_CLOUDFLARE_PAGES_URL=https://autoforge-nexus.pages.dev

# 監視
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx
```

## 🎯 実装ガイドライン

### コンポーネント設計

```tsx
// ✅ Server Component（データフェッチ）
export default async function PromptList() {
  const prompts = await fetchPrompts();
  return (
    <div className="grid gap-4">
      {prompts.map(prompt => (
        <PromptCard key={prompt.id} prompt={prompt} />
      ))}
    </div>
  );
}

// ✅ Client Component（インタラクティブ）
'use client';

export function PromptEditor({ initialPrompt }) {
  const [prompt, setPrompt] = useState(initialPrompt);

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        className="w-full min-h-[200px]"
      />
    </form>
  );
}
```

### エラーハンドリング

```tsx
// app/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // エラーを監視システムに送信
    logError(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center gap-4">
      <h2>エラーが発生しました</h2>
      <button onClick={reset}>再試行</button>
    </div>
  );
}
```

### パフォーマンス最適化

```tsx
// ✅ 動的インポート
const HeavyComponent = dynamic(
  () => import('@/components/HeavyComponent'),
  {
    loading: () => <Skeleton />,
    ssr: false
  }
);

// ✅ 画像最適化
<Image
  src="/hero.jpg"
  alt="Hero"
  width={1920}
  height={1080}
  priority
  placeholder="blur"
/>
```

## 📊 品質基準

- **テストカバレッジ**: 75%以上
- **TypeScript**: strict モード
- **Core Web Vitals**:
  - LCP < 2.5秒
  - FID < 100ms
  - CLS < 0.1
- **Lighthouse Score**: 95+
- **バンドルサイズ**: < 200KB (初期)

## 🔒 セキュリティ実装

### CSPヘッダー

```typescript
// middleware.ts
const cspHeader = `
  default-src 'self';
  script-src 'self' 'unsafe-eval' 'unsafe-inline' *.clerk.dev;
  style-src 'self' 'unsafe-inline';
  img-src 'self' blob: data: *.cloudflare.com;
  font-src 'self';
  connect-src 'self' *.clerk.dev *.turso.io;
`;
```

### 認証保護

```tsx
// middleware.ts
export async function middleware(request: NextRequest) {
  const { userId } = auth();

  if (!userId && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/sign-in', request.url));
  }

  return NextResponse.next();
}
```

## 🚨 注意事項

1. **Server/Client境界**: 'use client'ディレクティブを適切に使用
2. **環境変数**: NEXT_PUBLIC_プレフィックスに注意
3. **エッジ互換性**: Node.js APIを使用しない
4. **静的生成**: 可能な限りSSGを活用
5. **画像最適化**: next/imageを必ず使用

## 🔗 関連ドキュメント

- [プロジェクトCLAUDE.md](../CLAUDE.md) - プロジェクト全体ガイド
- [バックエンドCLAUDE.md](../backend/CLAUDE.md) - API仕様
- [Next.js 15.5.4ドキュメント](https://nextjs.org/docs) - 公式ドキュメント
- [React 19.0.0ドキュメント](https://react.dev) - 公式ドキュメント

## 📊 現在の実装状況（2025年9月29日更新）

### Phase 5: フロントエンド実装（未着手 - 0%）
※Phase 3（バックエンド）完了後に実装開始予定

#### 📋 実装予定項目
- Next.js 15.5.4 + React 19.0.0環境構築
- Tailwind CSS 4.0（OKLCH色空間）設定
- shadcn/ui 3.3.1コンポーネント統合
- Clerk認証UI実装
- プロンプト管理UI
- 評価ダッシュボード

### CI/CD最適化の成果
- GitHub Actions使用量: 730分/月（無料枠36.5%）
- 共有ワークフロー実装で52.3%のコスト削減達成
- フロントエンド用CI/CD設定準備済み（integration-ci.yml）

