# Phase 5 フロントエンド実装移行チェックリスト

**作成日**: 2025年10月8日
**目的**: Phase 3 → Phase 5 移行時のCI/CD問題を事前に防止

---

## 🎯 Phase 5移行前の必須確認事項

### 1. 環境変数更新

```yaml
# .github/workflows/integration-ci.yml
# .github/workflows/frontend-ci.yml
env:
  CURRENT_PHASE: '5'  # '3' → '5' に更新
```

**確認方法**:
```bash
grep -r "CURRENT_PHASE:" .github/workflows/
# すべて '5' になっていることを確認
```

---

### 2. フロントエンド依存関係の事前検証

**Phase 5着手前（Phase 4完了時）に実施**:

```bash
# 1. ローカルで依存関係インストール
cd frontend
pnpm install

# 2. 型チェック実行
pnpm type-check
# エラー: 0件であることを確認

# 3. Lint実行
pnpm lint
# エラー: 0件であることを確認

# 4. ビルド実行
pnpm build
# 成功することを確認

# 5. テスト実行
pnpm test:ci
# すべてのテストが合格することを確認
```

**期待結果**:
- ✅ TypeScript型エラー: 0件
- ✅ ESLint警告: 0件
- ✅ ビルド成功
- ✅ テスト: すべて合格

---

### 3. CI/CDワークフローの手動テスト

**GitHub Actions で手動実行**:

```bash
# 1. frontend-ci.yml を手動トリガー
gh workflow run frontend-ci.yml \
  --ref feature/phase5-frontend \
  -f CURRENT_PHASE=5

# 2. 実行状況を監視
gh run watch

# 3. 結果確認
gh run list --workflow=frontend-ci.yml --limit 1
```

**確認項目**:
- ✅ quality-checks: すべて合格
- ✅ test-suite: unit/e2e合格
- ✅ production-build: アーティファクト生成成功
- ✅ performance-audit: Lighthouse CI実行成功
- ✅ docker-build: イメージビルド成功
- ✅ deployment-prep: デプロイ準備完了

---

### 4. 欠落ファイルの確認

**Phase 5実装前に作成が必要なファイル**:

```bash
# すでに存在（問題なし）
frontend/src/lib/utils.ts ✅
frontend/src/lib/monitoring/web-vitals.ts ✅

# Phase 5で実装するファイル
frontend/src/lib/api/client.ts
frontend/src/lib/hooks/use-prompt.ts
frontend/src/components/prompt/PromptEditor.tsx
```

---

### 5. Docker統合確認

**フロントエンドDockerfile検証**:

```bash
# 1. Dockerfile存在確認
ls -la frontend/Dockerfile

# 2. ローカルビルドテスト
cd frontend
docker build -t autoforgenexus-frontend:test .

# 3. コンテナ起動テスト
docker run -p 3000:3000 autoforgenexus-frontend:test
curl http://localhost:3000
```

**期待結果**:
- ✅ Dockerfileが存在
- ✅ イメージビルド成功
- ✅ コンテナ起動成功
- ✅ ヘルスチェック応答

---

### 6. Integration CI確認

**フルスタック統合テスト**:

```bash
# integration-ci.yml の Phase 5対応確認
grep "CURRENT_PHASE" .github/workflows/integration-ci.yml

# 期待:
# - フロントエンド待機ロジック有効化
# - フロントエンドヘルスチェック有効化
# - E2Eテスト実行
```

**確認項目**:
- ✅ バックエンド起動（localhost:8000）
- ✅ フロントエンド起動（localhost:3000）
- ✅ 両方のヘルスチェック成功
- ✅ E2Eテスト実行

---

## 📋 Phase 5移行手順

### Step 1: Phase 4完了確認

```bash
# Phase 4要件完了チェック
- [ ] Turso/Redis統合完了
- [ ] LiteLLM統合完了
- [ ] CQRS実装完了
- [ ] イベントバス実装完了
```

### Step 2: フロントエンド基本実装

```bash
# 1. Next.js 15.5.4 セットアップ
cd frontend
pnpm install

# 2. 基本ページ実装
- [ ] ダッシュボード（/dashboard）
- [ ] プロンプトエディタ（/prompt/editor）
- [ ] 評価結果（/evaluation）

# 3. API統合
- [ ] バックエンドAPI接続
- [ ] 認証（Clerk）統合
```

### Step 3: CI/CD段階的有効化

```bash
# 1. 環境変数更新
# CURRENT_PHASE: '3' → '5'

# 2. 手動ワークフロー実行（検証）
gh workflow run frontend-ci.yml

# 3. エラー修正

# 4. 自動実行有効化（main/developマージ時）
```

### Step 4: 本番デプロイ

```bash
# 1. Cloudflare Pages設定
wrangler pages project create autoforgenexus-frontend

# 2. 環境変数設定
wrangler pages secret put NEXT_PUBLIC_API_URL
wrangler pages secret put CLERK_SECRET_KEY

# 3. デプロイ実行
pnpm build
wrangler pages deploy frontend/out
```

---

## 🚨 Phase 5移行時の既知のリスク

| リスク | 影響度 | 対策 |
|--------|--------|------|
| **依存関係エラー** | 高 | Phase 4完了時にpnpm installテスト |
| **型エラー大量発生** | 中 | 段階的型定義追加 |
| **E2Eテスト失敗** | 中 | Playwright設定見直し |
| **ビルド時間超過** | 低 | Turbopack最適化 |
| **アーティファクトサイズ超過** | 低 | .dockerignore最適化 |

---

## ✅ Phase 5移行成功基準

### 必須条件

- ✅ すべてのCI/CDジョブが成功
- ✅ テストカバレッジ75%達成
- ✅ TypeScript型エラー0件
- ✅ Lighthouse CI: すべてのメトリクスグリーン
- ✅ Docker build成功
- ✅ E2Eテスト合格

### 推奨条件

- ✅ バンドルサイズ < 500KB
- ✅ ビルド時間 < 60秒
- ✅ Core Web Vitals達成
  - LCP < 2.5s
  - FID < 100ms
  - CLS < 0.1

---

## 📝 Phase 5実装前の推奨アクション

### 今すぐ実施可能（リスク低減）

1. **最小限のフロントエンド検証**
```bash
cd frontend
pnpm install  # 依存関係インストール
pnpm type-check  # 型チェック（エラー確認）
```

2. **CI/CD手動テスト**
```bash
# workflow_dispatch で手動実行
gh workflow run frontend-ci.yml
```

3. **ドキュメント確認**
```bash
# Phase 5実装要件の再確認
cat docs/setup/PHASE5_*.md
```

---

## 🎯 結論

**現在のPhase判定ロジック**:
- ✅ Phase 3では問題なし（すべてスキップ）
- ⚠️ Phase 5移行時に一斉有効化されるリスク

**推奨対応**:
1. **Phase 4完了時**: フロントエンド依存関係の事前検証
2. **Phase 5着手前**: CI/CD手動テスト実行
3. **Phase 5実装中**: 段階的ジョブ有効化

**デプロイ時のリスク**: 中程度
**リスク軽減策**: 本チェックリストに従った段階的移行で対応可能

---

**次のステップ**: Phase 4完了後、本チェックリストに基づいて移行準備を開始
