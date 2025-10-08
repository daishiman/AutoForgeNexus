# Frontend CI/CD 段階的実行戦略 - 実装ガイド

**作成日**: 2025-10-08
**対象**: 開発者・DevOpsエンジニア
**目的**: フロントエンドCI/CDワークフローの段階的実行戦略の実装手順と検証方法

---

## 📋 実装概要

### 変更内容サマリー

本実装により、**Phase 3（バックエンド実装中）からフロントエンドCI/CDの一部ジョブを実行可能**にし、早期品質検証とインフラ検証を実現します。

| 項目 | 変更前 | 変更後 |
|------|--------|--------|
| Phase 3実行ジョブ | 0（全スキップ） | 3（setup/quality/build） |
| Phase 5実行ジョブ | 全8ジョブ | 全8ジョブ（変更なし） |
| Phase 3月間コスト | 0分 | +285分（30 PR想定） |
| Phase 5月間コスト | 未計測 | 1,560分（30 PR + 20 main） |
| コスト削減率維持 | 52.3% | 45-35%（Phase進行で減少） |

---

## 🔧 実装済み変更内容

### 1. quality-checks ジョブ

**変更点**: Phase 3でも実行可能 + matrix動的生成

```yaml
# 変更前
if: ${{ vars.CURRENT_PHASE >= 5 || github.event_name == 'workflow_dispatch' }}
matrix:
  check-type: [lint, format, type-check, build-check]

# 変更後
if: |
  (vars.CURRENT_PHASE >= 3 && hashFiles('frontend/src/**/*.{ts,tsx}') != '') ||
  vars.CURRENT_PHASE >= 5 ||
  github.event_name == 'workflow_dispatch'
matrix:
  check-type: >-
    ${{
      vars.CURRENT_PHASE >= 5
        ? fromJSON('["lint", "format", "type-check", "build-check"]')
        : fromJSON('["lint", "type-check"]')
    }}
```

**Phase 3での動作**:
- ✅ ESLint実行（コード品質チェック）
- ✅ TypeScript型チェック（型安全性検証）
- ❌ Prettier formatスキップ（コード量少ないため優先度低）
- ❌ build-checkスキップ（本格実装前は不要）

### 2. test-suite ジョブ

**変更点**: テストファイル存在確認を追加

```yaml
# 変更前
if: ${{ vars.CURRENT_PHASE >= 5 || github.event_name == 'workflow_dispatch' }}

# 変更後
if: |
  hashFiles('frontend/**/*.test.{ts,tsx}', 'frontend/playwright.config.ts') != '' &&
  (vars.CURRENT_PHASE >= 5 || github.event_name == 'workflow_dispatch')
```

**Phase 3での動作**:
- ❌ 完全スキップ（テストファイル未実装のため）

### 3. production-build ジョブ

**変更点**: Phase 3でも実行可能

```yaml
# 変更前
if: ${{ vars.CURRENT_PHASE >= 5 || github.event_name == 'workflow_dispatch' }}

# 変更後
if: |
  !failure() &&
  (
    (vars.CURRENT_PHASE >= 3 && hashFiles('frontend/src/**/*.{ts,tsx}') != '') ||
    vars.CURRENT_PHASE >= 5 ||
    github.event_name == 'workflow_dispatch'
  )
```

**Phase 3での動作**:
- ✅ Next.js 15.5.4ビルド設定検証
- ✅ next.config.js構文チェック
- ✅ Turbopack動作確認
- ⚠️ ビルド成功してもページ内容は最小限

### 4. performance-audit ジョブ

**変更点**: ページファイル存在確認を追加

```yaml
# 変更前
if: |
  (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop') &&
  (vars.CURRENT_PHASE >= 5 || github.event_name == 'workflow_dispatch')

# 変更後
if: |
  (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop') &&
  vars.CURRENT_PHASE >= 5 &&
  hashFiles('frontend/src/app/**/page.tsx') != ''
```

**Phase 3での動作**:
- ❌ 完全スキップ（実装不完全なため意味あるメトリクス取得不可）

### 5. docker-build ジョブ

**変更点**: Dockerfile存在確認を追加

```yaml
# 変更前
if: |
  !failure() &&
  (vars.CURRENT_PHASE >= 5 || github.event_name == 'workflow_dispatch')

# 変更後
if: |
  !failure() &&
  hashFiles('frontend/Dockerfile') != '' &&
  (vars.CURRENT_PHASE >= 5 || github.event_name == 'workflow_dispatch')
```

**Phase 3での動作**:
- ❌ 完全スキップ（Dockerfile未作成）

### 6. deployment-prep ジョブ

**変更点**: ビルド成果物存在確認を追加

```yaml
# 変更前
if: |
  (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop') &&
  (vars.CURRENT_PHASE >= 5 || github.event_name == 'workflow_dispatch')

# 変更後
if: |
  (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop') &&
  vars.CURRENT_PHASE >= 5 &&
  hashFiles('frontend/out/**') != ''
```

**Phase 3での動作**:
- ❌ 完全スキップ（本番デプロイ準備不要）

### 7. ci-status ジョブ

**変更点**: Phase依存のcritical jobs動的生成 + ステータスサマリー拡張

```yaml
# critical jobsリスト
# 変更前
CRITICAL_JOBS=("setup-environment" "quality-checks" "test-suite" "production-build")

# 変更後
if [[ "${{ vars.CURRENT_PHASE }}" -ge 5 ]]; then
  CRITICAL_JOBS=("setup-environment" "quality-checks" "test-suite" "production-build")
else
  CRITICAL_JOBS=("setup-environment" "quality-checks" "production-build")
fi
```

**Phase 3での動作**:
- ✅ test-suiteをcriticalリストから除外（スキップされるため）
- ✅ Phase情報を含むステータスメッセージ表示

---

## ✅ 検証手順

### 事前準備

```bash
# 1. ブランチ作成
git checkout -b fix/frontend-ci-phased-execution

# 2. 現在のPhase確認
gh variable list | grep CURRENT_PHASE
# 出力例: CURRENT_PHASE  3

# 3. TypeScriptファイル存在確認
ls -la frontend/src/**/*.{ts,tsx} | head -5
# middleware.ts等が存在すればOK
```

### Phase 3動作検証

#### 検証1: quality-checksジョブ実行確認

```bash
# 1. ダミーTypeScriptファイル作成（既存ファイルで検証可能ならスキップ）
# frontend/src/test-validation.tsが既に存在する想定

# 2. コミット・プッシュ
git add .github/workflows/frontend-ci.yml
git commit -m "fix(ci): フロントエンドCI/CD段階的実行戦略実装"
git push origin fix/frontend-ci-phased-execution

# 3. GitHub ActionsでCI実行確認
gh run watch

# 4. quality-checksジョブ確認
gh run view --log | grep "Quality Checks"
# 期待: "🔍 Quality Checks" が表示され、lint/type-checkが実行される
```

**期待結果**:
- ✅ `quality-checks`ジョブ実行
- ✅ matrix: `[lint, type-check]`（2ジョブのみ）
- ✅ ESLint・TypeScriptチェック成功
- ❌ format/build-checkスキップ

#### 検証2: production-buildジョブ実行確認

```bash
# GitHub Actionsログ確認
gh run view --log | grep "Production Build"
# 期待: "🏗️ Production Build" が表示され、ビルド実行される
```

**期待結果**:
- ✅ `production-build`ジョブ実行
- ✅ `pnpm build`成功（警告あっても可）
- ✅ アーティファクト作成（.next/, out/）

#### 検証3: test-suite/docker-build/performance-audit スキップ確認

```bash
# GitHub Actionsログ確認
gh run view --log | grep -E "Test Suite|Docker Build|Performance Audit"
# 期待: これらのジョブがスキップされる
```

**期待結果**:
- ⏭️ `test-suite`スキップ（テストファイル未実装）
- ⏭️ `docker-build`スキップ（Dockerfile未作成）
- ⏭️ `performance-audit`スキップ（Phase 5未満）

#### 検証4: ci-statusジョブ確認

```bash
# GitHub ActionsのSummary表示確認
gh run view
# 期待: "Frontend CI/CD Status (Phase 3)" が表示される
```

**期待結果**:
```markdown
## 🔍 Frontend CI/CD Status (Phase 3)

| Job | Status | Phase Requirement |
|-----|--------|-------------------|
| Environment Setup | ✅ | Always |
| Quality Checks | ✅ | Phase 3+ (TypeScript files exist) |
| Test Suite | ⏭️ | Phase 5+ (Test files exist) |
| Production Build | ✅ | Phase 3+ (TypeScript files exist) |
| Docker Build | ⏭️ | Phase 5+ (Dockerfile exists) |

**Overall Status**: All critical checks passed! 🎉 (Phase 3)

**Optimizations Applied**:
- ✅ Phase-aware execution (smart job skipping based on implementation status)
- ✅ Shared environment setup (eliminates 9 dependency duplications)
- ...

**Phase 3 Mode**: Early quality validation (lint, type-check, build verification)
**Phase 5 Mode**: Full CI/CD pipeline (tests, performance audit, deployment)
```

### Phase 5動作検証（Phase 5移行後）

#### 検証5: CURRENT_PHASE変数更新

```bash
# Phase 5に移行（Phase 4完了後に実施）
gh variable set CURRENT_PHASE --body "5" --repo daishiman/AutoForgeNexus

# 確認
gh variable list | grep CURRENT_PHASE
# 出力: CURRENT_PHASE  5
```

#### 検証6: 全ジョブ実行確認

```bash
# テストファイル作成（Phase 5移行時に実施）
touch frontend/src/components/Button.test.tsx
touch frontend/Dockerfile

# コミット・プッシュ
git add frontend/
git commit -m "feat(frontend): テストファイル・Dockerfile追加（Phase 5移行）"
git push origin feature/phase5-migration

# CI実行確認
gh run watch
```

**期待結果**:
- ✅ `quality-checks`: 全matrix実行（lint/format/type-check/build-check）
- ✅ `test-suite`: unit/e2e実行
- ✅ `production-build`: 完全ビルド
- ✅ `docker-build`: イメージビルド成功
- ✅ `performance-audit`: Lighthouse実行（main/developブランチのみ）
- ✅ `deployment-prep`: デプロイパッケージ作成（main/developブランチのみ）

---

## 📊 コスト監視

### GitHub Actions使用量確認

```bash
# 月間使用量確認
gh api /repos/daishiman/AutoForgeNexus/actions/billing/usage \
  --jq '.total_minutes_used, .total_paid_minutes_used'

# ワークフロー別使用量
gh api /repos/daishiman/AutoForgeNexus/actions/runs \
  --jq '.workflow_runs[] | select(.name == "Frontend CI/CD Pipeline - Optimized") | {created_at, conclusion, run_duration_ms}'
```

### 目標コスト（月次）

| Phase | 推定使用量 | 無料枠使用率 | 目標コスト削減率 |
|-------|-----------|-------------|----------------|
| Phase 3 | 1,015分 | 50.8% | 45.0% |
| Phase 5 | 1,560分 | 78.0% | 35.0% |

**重要**: 無料枠（2,000分/月）を超えないよう監視

---

## 🐛 トラブルシューティング

### 問題1: quality-checksがスキップされる（Phase 3）

**症状**:
```
質uality-checks: Skipped
```

**原因**:
- TypeScriptファイルが存在しない
- CURRENT_PHASE変数が3未満

**解決策**:
```bash
# TypeScriptファイル確認
ls frontend/src/**/*.{ts,tsx}

# Phase変数確認
gh variable list | grep CURRENT_PHASE

# Phase 3未満の場合は変数更新
gh variable set CURRENT_PHASE --body "3" --repo daishiman/AutoForgeNexus
```

### 問題2: production-buildが失敗（Phase 3）

**症状**:
```
Error: Build failed
```

**原因**:
- next.config.js構文エラー
- 依存関係不足
- 環境変数未設定

**解決策**:
```bash
# ローカルでビルド確認
cd frontend
pnpm install
pnpm build

# エラーログ確認
gh run view --log | grep -A 20 "Production Build"

# next.config.js検証
node -c frontend/next.config.js
```

### 問題3: matrix動的生成が機能しない

**症状**:
```
Error: Invalid matrix expression
```

**原因**:
- fromJSON構文エラー
- CURRENT_PHASE変数の型不一致

**解決策**:
```yaml
# デバッグステップ追加
- name: Debug matrix
  run: |
    echo "CURRENT_PHASE: ${{ vars.CURRENT_PHASE }}"
    echo "Matrix: ${{ toJSON(matrix.check-type) }}"
```

---

## 📝 チェックリスト

### Phase 3実装確認

- [x] `frontend-ci.yml`更新完了
- [x] quality-checks: Phase 3条件追加
- [x] quality-checks: matrix動的生成実装
- [x] test-suite: テストファイル存在確認追加
- [x] production-build: Phase 3条件追加
- [x] performance-audit: ページファイル存在確認追加
- [x] docker-build: Dockerfile存在確認追加
- [x] deployment-prep: ビルド成果物存在確認追加
- [x] ci-status: Phase依存critical jobs実装
- [x] ci-status: ステータスサマリー拡張

### Phase 3検証確認

- [ ] quality-checks実行確認（lint/type-check）
- [ ] production-build実行確認
- [ ] test-suite/docker-build/performance-auditスキップ確認
- [ ] ci-statusサマリー表示確認（Phase 3表記）
- [ ] GitHub Actions使用量監視（1,015分/月以下）

### Phase 5準備確認

- [ ] テストファイル実装計画作成
- [ ] Dockerfile作成計画作成
- [ ] Lighthouse CI設定準備
- [ ] Phase 5移行チェックリスト作成

---

## 🔗 関連ドキュメント

- [段階的実行戦略ドキュメント](../reports/frontend-ci-phased-execution-strategy.md) - 設計思想・コスト分析
- [CI/CD最適化レポート](../reports/ci-cd-optimization-report-2025-09-30.md) - 52.3%削減実績
- [プロジェクトCLAUDE.md](/Users/dm/dev/dev/個人開発/AutoForgeNexus/CLAUDE.md) - Phase定義

---

## 📞 サポート

質問・問題報告:
- GitHub Issues: https://github.com/daishiman/AutoForgeNexus/issues
- 担当: DevOpsチーム
