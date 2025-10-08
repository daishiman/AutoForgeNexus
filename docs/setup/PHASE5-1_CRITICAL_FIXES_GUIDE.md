# Phase 5 フロントエンド - クリティカル修正実施ガイド

## 📋 概要

Phase
5フロントエンド実装で発見された問題の修正手順を、各専門エージェントが最適化した形で文書化します。

---

## 🚨 即座対応項目（24時間以内）

### 1. Node.js 22へのアップグレード手順

#### 担当: DevOps Coordinator + Frontend Architect

##### 事前確認

```bash
# 現在のNode.jsバージョン確認
node --version  # 現在: v20.19.0

# Voltaのインストール状況確認
volta --version

# 既存プロジェクトの依存関係確認
cd frontend && pnpm ls
```

##### 実行手順

```bash
# Step 1: 実行中のプロセスを停止
# すべての開発サーバーを停止（Ctrl+C）

# Step 2: Node.js 22のインストール
volta install node@22.12.0  # LTS版を指定
volta install pnpm@9.15.9   # pnpmも最新版に

# Step 3: プロジェクトにピン留め
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus
volta pin node@22.12.0
volta pin pnpm@9.15.9

# Step 4: 依存関係の再インストール
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Step 5: 動作確認
pnpm dev --turbo
```

##### 検証項目

- [ ] Node.js 22.12.0がインストールされている
- [ ] pnpm 9.15.9が使用されている
- [ ] 開発サーバーが警告なしで起動する
- [ ] ビルドが成功する

---

### 2. lightningcssモジュールエラーの解決

#### 担当: Frontend Architect + Performance Optimizer

##### 問題分析

```
エラー: Module not found: '../lightningcss.darwin-arm64.node'
原因: Tailwind CSS 4.0依存関係とM1 Macネイティブバイナリの不整合
```

##### 解決手順

###### オプション1: lightningcssの再ビルド（推奨）

```bash
cd frontend

# Step 1: キャッシュクリア
pnpm store prune
rm -rf .next node_modules/.cache

# Step 2: lightningcssのインストールと再ビルド
pnpm add -D lightningcss
pnpm rebuild lightningcss

# Step 3: PostCSS設定の確認
cat > postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
EOF

# Step 4: 動作確認
pnpm dev --turbo
```

###### オプション2: Tailwind CSS 3.x環境の完全セットアップ

```bash
# Step 1: Tailwind CSS 3.xクリーンインストール
pnpm remove tailwindcss @tailwindcss/postcss
pnpm add -D tailwindcss@^3.4.0 postcss autoprefixer

# Step 2: 設定ファイルの再生成
npx tailwindcss init -p

# Step 3: globals.css内のTailwind v4構文を修正
# theme()関数をCSS変数に置き換え
```

##### 検証項目

- [ ] lightningcssエラーが解消されている
- [ ] CSSのビルドが成功する
- [ ] スタイルが正常に適用される

---

### 3. 型定義エラーの修正

#### 担当: Quality Engineer + Test Automation Engineer

##### 修正手順

```bash
cd frontend

# Step 1: 必要な型定義のインストール
pnpm add -D \
  @types/jest@^29.5.0 \
  @types/node@^22.0.0 \
  @types/react@^19.0.0 \
  @types/react-dom@^19.0.0

# Step 2: tsconfig.jsonの型定義追加
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "types": ["jest", "node"],
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

# Step 3: 型チェック実行
pnpm type-check
```

##### 検証項目

- [ ] 型エラーが0件になっている
- [ ] IDEで型補完が機能する
- [ ] ビルドが成功する

---

## 📅 短期対応項目（1週間以内）

### 4. Docker環境構築

#### 担当: DevOps Coordinator + Observability Engineer

##### Dockerfile.dev作成

```dockerfile
# frontend/Dockerfile.dev
FROM node:22-alpine AS base

# Install pnpm
RUN corepack enable && corepack prepare pnpm@9.15.9 --activate

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Expose port
EXPOSE 3001

# Development command
CMD ["pnpm", "dev", "--turbo"]
```

##### docker-compose追加

```yaml
# docker-compose.dev.yml に追加
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - '3001:3001'
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - app-network
```

##### 実行手順

```bash
# ビルドと起動
docker-compose -f docker-compose.dev.yml up -d frontend

# ログ確認
docker-compose -f docker-compose.dev.yml logs -f frontend
```

---

### 5. Web Vitals監視実装

#### 担当: Performance Optimizer + Observability Engineer

##### 実装手順

###### Step 1: Web Vitals設定

```typescript
// src/lib/monitoring/web-vitals.ts
import { onCLS, onFID, onFCP, onLCP, onTTFB } from 'web-vitals';

type MetricType = 'CLS' | 'FID' | 'FCP' | 'LCP' | 'TTFB';

interface Metric {
  id: string;
  name: MetricType;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  entries: any[];
}

const vitalsUrl = process.env.NEXT_PUBLIC_ANALYTICS_URL || '/api/analytics';

function sendToAnalytics(metric: Metric) {
  const body = JSON.stringify({
    dsn: process.env.NEXT_PUBLIC_ANALYTICS_ID,
    id: metric.id,
    page: window.location.pathname,
    href: window.location.href,
    event_name: metric.name,
    value: metric.value.toString(),
    speed: metric.rating,
  });

  if (navigator.sendBeacon) {
    navigator.sendBeacon(vitalsUrl, body);
  } else {
    fetch(vitalsUrl, {
      body,
      method: 'POST',
      keepalive: true,
    });
  }
}

export function reportWebVitals() {
  onCLS(sendToAnalytics);
  onFID(sendToAnalytics);
  onFCP(sendToAnalytics);
  onLCP(sendToAnalytics);
  onTTFB(sendToAnalytics);
}
```

###### Step 2: アプリケーションへの統合

```typescript
// src/app/layout.tsx に追加
import { reportWebVitals } from '@/lib/monitoring/web-vitals';

if (typeof window !== 'undefined') {
  reportWebVitals();
}
```

###### Step 3: APIエンドポイント作成

```typescript
// src/app/api/analytics/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const data = await request.json();

  // ログ記録（本番では監視システムへ送信）
  console.log('Web Vitals:', data);

  // LangFuseや他の監視システムへ転送
  // await sendToLangFuse(data);

  return NextResponse.json({ success: true });
}
```

---

### 6. Git Hooks設定

#### 担当: Quality Engineer + Security Architect

##### 実装手順

```bash
cd frontend

# Step 1: Huskyとlint-stagedのインストール
pnpm add -D husky lint-staged

# Step 2: Huskyの初期化
npx husky install

# Step 3: pre-commitフック作成
npx husky add .husky/pre-commit "npx lint-staged"

# Step 4: lint-staged設定
cat > .lintstagedrc.json << 'EOF'
{
  "*.{js,jsx,ts,tsx}": [
    "eslint --fix",
    "prettier --write"
  ],
  "*.{json,md,yml,yaml}": [
    "prettier --write"
  ],
  "*.css": [
    "prettier --write"
  ]
}
EOF

# Step 5: package.jsonにprepareスクリプト追加
npm pkg set scripts.prepare="husky install"
```

##### コミット前チェック項目

```bash
# .husky/pre-commit
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# lint-staged実行
npx lint-staged

# 型チェック
pnpm type-check

# テスト実行（基本テストのみ）
pnpm test:unit --passWithNoTests
```

---

## 🗓️ 中期対応項目（2週間以内）

### 7. CI/CDパイプライン設定

#### 担当: DevOps Coordinator + Test Automation Engineer

##### GitHub Actions設定

```yaml
# .github/workflows/frontend-ci.yml
name: Frontend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci.yml'
  pull_request:
    branches: [main, develop]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [22.x]

    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4
        with:
          version: 9.15.9

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'pnpm'
          cache-dependency-path: frontend/pnpm-lock.yaml

      - name: Install dependencies
        working-directory: ./frontend
        run: pnpm install --frozen-lockfile

      - name: Lint
        working-directory: ./frontend
        run: pnpm lint

      - name: Type check
        working-directory: ./frontend
        run: pnpm type-check

      - name: Test
        working-directory: ./frontend
        run: pnpm test:ci

      - name: Build
        working-directory: ./frontend
        run: pnpm build

      - name: E2E Test
        working-directory: ./frontend
        run: pnpm test:e2e:ci
```

---

## 📊 実装優先順位マトリクス

| タスク                   | 緊急度 | 重要度 | 工数 | 担当エージェント            |
| ------------------------ | ------ | ------ | ---- | --------------------------- |
| Node.js 22アップグレード | 高     | 高     | 1h   | DevOps + Frontend           |
| lightningcss修正         | 高     | 高     | 2h   | Frontend + Performance      |
| 型定義修正               | 中     | 高     | 1h   | Quality + Test              |
| Docker環境               | 中     | 高     | 3h   | DevOps + Observability      |
| Web Vitals               | 中     | 高     | 2h   | Performance + Observability |
| Git Hooks                | 低     | 高     | 1h   | Quality + Security          |
| CI/CD                    | 低     | 高     | 4h   | DevOps + Test               |

---

## ✅ 成功基準

### 即座対応項目の完了条件

- Node.js 22で警告なしで動作
- CSS関連エラーゼロ
- TypeScript型エラーゼロ

### 短期対応項目の完了条件

- Dockerコンテナで動作確認
- Web Vitalsデータ収集開始
- コミット時の自動チェック動作

### 中期対応項目の完了条件

- PRごとの自動テスト実行
- ビルド成功率100%
- E2Eテストカバレッジ50%以上

---

## 📝 注意事項

1. **各手順は順番に実行** - 依存関係があるため順序を守る
2. **バックアップ必須** - 変更前に現状をコミット
3. **段階的適用** - 一度にすべて変更せず段階的に
4. **検証重視** - 各ステップ後の動作確認を徹底

---

**文書作成者**: 全専門エージェント協働 **作成日時**: 2025-09-29 07:00 JST
**次回レビュー**: 実装完了後
