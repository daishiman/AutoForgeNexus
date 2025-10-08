# Frontend CI/CD 段階的実行戦略

**作成日**: 2025-10-08
**対象**: AutoForgeNexus Frontend CI/CD Pipeline
**目的**: Phase 3から実行可能なジョブとPhase 5待機ジョブの明確な分離による効率的CI/CD運用

---

## 🎯 戦略概要

### 設計原則

1. **段階的環境構築遵守**: Phase 3（バックエンド実装中）とPhase 5（フロントエンド本格実装）で実行ジョブを分離
2. **コスト効率維持**: 52.3%削減実績を維持（730分/月 → 目標: 800分/月以下）
3. **品質保証確保**: 必要なチェックはPhase 3から実行、不要な実行は避ける
4. **インフラ検証優先**: 構成ファイル検証・依存関係チェックは早期実行

### 現状分析（2025-10-08時点）

| 項目 | 状態 | 備考 |
|------|------|------|
| package.json | ✅ 存在 | 全依存関係定義済み |
| src/ディレクトリ | ✅ 存在 | 基本構造作成済み（10ディレクトリ） |
| TypeScriptコード | 🟡 部分的 | middleware.ts等の一部ファイルのみ |
| テストコード | ❌ 未実装 | jest/playwright設定のみ |
| Dockerfile | ❌ 未作成 | Phase 5で作成予定 |
| 本番ビルド | 🟡 可能 | next buildは実行可能だが内容最小限 |

---

## 📊 ジョブ実行マトリクス

### Category A: Phase非依存（常に実行）

| ジョブ名 | Phase 3 | Phase 5 | 実行条件 | コスト影響 |
|---------|---------|---------|---------|-----------|
| `setup-environment` | ✅ | ✅ | 常に実行 | +2分/実行 |
| `ci-status` | ✅ | ✅ | 常に実行（集約のみ） | +0.5分/実行 |

**理由**: 環境セットアップは依存関係検証・キャッシュウォームアップとして価値あり

### Category B: コード存在依存（条件付き実行）

| ジョブ名 | Phase 3 | Phase 5 | 実行条件 | コスト影響 |
|---------|---------|---------|---------|-----------|
| `quality-checks` | 🔄 部分実行 | ✅ 完全実行 | TypeScriptファイル存在時 | +3分/実行 |
| `production-build` | 🔄 軽量実行 | ✅ 完全実行 | package.json + next.config.js存在時 | +4分/実行 |

**quality-checks詳細**:
- **Phase 3**: `lint`、`type-check`のみ（formatはスキップ）
- **Phase 5**: 全matrixジョブ実行（lint/format/type-check/build-check）

### Category C: 実装完了依存（Phase 5のみ）

| ジョブ名 | Phase 3 | Phase 5 | 実行条件 | コスト影響 |
|---------|---------|---------|---------|-----------|
| `test-suite` | ❌ | ✅ | テストファイル存在時 | 0分（Phase 3）→ +6分（Phase 5） |
| `performance-audit` | ❌ | ✅ | main/develop + 完全実装 | 0分（Phase 3）→ +8分（Phase 5） |
| `docker-build` | ❌ | ✅ | Dockerfile存在時 | 0分（Phase 3）→ +5分（Phase 5） |
| `deployment-prep` | ❌ | ✅ | main/develop + 完全実装 | 0分（Phase 3）→ +3分（Phase 5） |

**凡例**:
- ✅ 完全実行
- 🔄 条件付き部分実行
- ❌ スキップ

---

## 💡 推奨実装パターン

### パターン1: ファイル存在チェック（基本）

```yaml
# TypeScriptファイルの存在確認
if: hashFiles('frontend/src/**/*.{ts,tsx}') != ''

# テストファイルの存在確認
if: hashFiles('frontend/**/*.test.{ts,tsx}', 'frontend/playwright.config.ts') != ''

# Dockerfileの存在確認
if: hashFiles('frontend/Dockerfile') != ''
```

### パターン2: Phase + ファイル存在（複合条件）

```yaml
# Phase 3以降 かつ TypeScriptファイル存在時
if: |
  (vars.CURRENT_PHASE >= 3 && hashFiles('frontend/src/**/*.{ts,tsx}') != '') ||
  vars.CURRENT_PHASE >= 5 ||
  github.event_name == 'workflow_dispatch'
```

### パターン3: スクリプト存在チェック（package.json検証）

```yaml
# package.jsonにtest:ciスクリプトが定義されているか
steps:
  - name: Check test script availability
    id: check-test
    run: |
      if jq -e '.scripts["test:ci"]' frontend/package.json > /dev/null; then
        echo "has-tests=true" >> $GITHUB_OUTPUT
      else
        echo "has-tests=false" >> $GITHUB_OUTPUT
      fi

  - name: Run tests
    if: steps.check-test.outputs.has-tests == 'true'
    run: pnpm test:ci
```

---

## 🔧 具体的な実装方針

### ジョブ1: setup-environment

```yaml
setup-environment:
  name: 🔧 Setup Environment
  uses: ./.github/workflows/shared-setup-node.yml
  with:
    node-version: '22'
    pnpm-version: '9'
    working-directory: './frontend'
    cache-key-suffix: '-frontend'
    install-playwright: true
  # 変更なし - 常に実行
```

**Phase 3での価値**:
- package.json依存関係の整合性検証
- pnpm-lock.yamlのバージョン検証
- Node.js 22 + pnpm 9の動作確認
- キャッシュウォームアップ

### ジョブ2: quality-checks

```yaml
quality-checks:
  name: 🔍 Quality Checks
  runs-on: ubuntu-latest
  needs: setup-environment
  # 🆕 スマート条件分岐
  if: |
    (vars.CURRENT_PHASE >= 3 && hashFiles('frontend/src/**/*.{ts,tsx}') != '') ||
    vars.CURRENT_PHASE >= 5 ||
    github.event_name == 'workflow_dispatch'

  strategy:
    fail-fast: false
    matrix:
      # 🆕 Phase依存のmatrix動的生成
      check-type: >-
        ${{
          vars.CURRENT_PHASE >= 5
            ? fromJSON('["lint", "format", "type-check", "build-check"]')
            : fromJSON('["lint", "type-check"]')
        }}
      include:
        - check-type: lint
          command: 'pnpm lint'
          name: 'ESLint Analysis'
        - check-type: format
          command: 'pnpm prettier --check .'
          name: 'Prettier Format Check'
        - check-type: type-check
          command: 'pnpm type-check'
          name: 'TypeScript Type Check'
        - check-type: build-check
          command: 'pnpm build && npx size-limit || true'
          name: 'Build & Bundle Size Check'
```

**Phase 3での実行内容**:
- ✅ `lint`: 既存TypeScriptファイルのESLint検証
- ✅ `type-check`: 型安全性チェック
- ❌ `format`: スキップ（コード量が少ないため優先度低）
- ❌ `build-check`: スキップ（本格実装前は不要）

**Phase 5での実行内容**:
- ✅ 全matrixジョブ実行（lint/format/type-check/build-check）

### ジョブ3: test-suite

```yaml
test-suite:
  name: 🧪 Test Suite
  runs-on: ubuntu-latest
  needs: setup-environment
  # 🆕 テストファイル存在確認
  if: |
    hashFiles('frontend/**/*.test.{ts,tsx}', 'frontend/playwright.config.ts') != '' &&
    (vars.CURRENT_PHASE >= 5 || github.event_name == 'workflow_dispatch')

  strategy:
    fail-fast: false
    matrix:
      test-type: [unit, e2e]
      # ... (既存設定維持)
```

**Phase 3での動作**:
- ❌ 完全スキップ（テストファイル未実装のため）
- コスト削減: 6分/実行

**Phase 5での動作**:
- ✅ unit/e2eテスト実行
- ✅ Codecovカバレッジレポート

### ジョブ4: production-build

```yaml
production-build:
  name: 🏗️ Production Build
  uses: ./.github/workflows/shared-build-cache.yml
  needs: [quality-checks]
  # 🆕 スマート条件分岐
  if: |
    !failure() &&
    (
      (vars.CURRENT_PHASE >= 3 && hashFiles('frontend/src/**/*.{ts,tsx}') != '') ||
      vars.CURRENT_PHASE >= 5 ||
      github.event_name == 'workflow_dispatch'
    )

  with:
    build-type: 'frontend'
    working-directory: './frontend'
    build-command: 'pnpm build'
    artifact-paths: |
      frontend/.next/
      frontend/out/
      frontend/build-stats.json
    environment-vars: '{"NODE_ENV": "production", "NEXT_TELEMETRY_DISABLED": "1"}'
```

**Phase 3での価値**:
- ✅ Next.js 15.5.4ビルド設定検証
- ✅ next.config.js構文チェック
- ✅ Turbopack動作確認
- ⚠️ 警告: ビルド成功してもページ内容は最小限

**Phase 5での価値**:
- ✅ 完全な本番ビルド検証
- ✅ バンドルサイズ監視
- ✅ Tree Shaking効果測定

### ジョブ5: performance-audit

```yaml
performance-audit:
  name: ⚡ Performance Audit
  runs-on: ubuntu-latest
  needs: [setup-environment, production-build]
  # 🆕 厳格な実行条件
  if: |
    (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop') &&
    vars.CURRENT_PHASE >= 5 &&
    hashFiles('frontend/src/app/**/page.tsx') != ''
```

**Phase 3での動作**:
- ❌ 完全スキップ（実装不完全なため意味あるメトリクス取得不可）
- コスト削減: 8分/実行

**Phase 5での動作**:
- ✅ Lighthouse CI実行
- ✅ Core Web Vitals測定
- ✅ バンドル分析レポート

### ジョブ6: docker-build

```yaml
docker-build:
  name: 🐳 Docker Build
  runs-on: ubuntu-latest
  needs: [production-build]
  # 🆕 Dockerfile存在確認
  if: |
    !failure() &&
    hashFiles('frontend/Dockerfile') != '' &&
    (vars.CURRENT_PHASE >= 5 || github.event_name == 'workflow_dispatch')
```

**Phase 3での動作**:
- ❌ 完全スキップ（Dockerfile未作成）
- コスト削減: 5分/実行

**Phase 5での動作**:
- ✅ Dockerイメージビルド検証
- ✅ マルチステージビルド最適化
- ✅ GitHub Actions Cache活用

### ジョブ7: deployment-prep

```yaml
deployment-prep:
  name: 📦 Deployment Preparation
  runs-on: ubuntu-latest
  needs: [production-build, test-suite, docker-build]
  # 🆕 厳格な実行条件
  if: |
    (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop') &&
    vars.CURRENT_PHASE >= 5 &&
    hashFiles('frontend/out/**') != ''
```

**Phase 3での動作**:
- ❌ 完全スキップ（本番デプロイ準備不要）
- コスト削減: 3分/実行

**Phase 5での動作**:
- ✅ Cloudflare Pagesパッケージ作成
- ✅ デプロイアーティファクト生成

### ジョブ8: ci-status

```yaml
ci-status:
  name: 📊 CI Status
  runs-on: ubuntu-latest
  needs: [setup-environment, quality-checks, test-suite, production-build, docker-build]
  if: always()

  steps:
    - name: 📋 Calculate overall status
      id: status
      run: |
        # 🆕 Phase依存のジョブリスト動的生成
        if [[ "${{ vars.CURRENT_PHASE }}" -ge 5 ]]; then
          CRITICAL_JOBS=("setup-environment" "quality-checks" "test-suite" "production-build")
        else
          CRITICAL_JOBS=("setup-environment" "quality-checks" "production-build")
        fi

        FAILED_JOBS=""
        for job in "${CRITICAL_JOBS[@]}"; do
          if [[ "${{ toJSON(needs) }}" =~ "$job".*"failure" ]]; then
            FAILED_JOBS="$FAILED_JOBS $job"
          fi
        done

        if [ -z "$FAILED_JOBS" ]; then
          echo "status=success" >> $GITHUB_OUTPUT
          echo "message=All critical checks passed! 🎉 (Phase ${{ vars.CURRENT_PHASE }})" >> $GITHUB_OUTPUT
        else
          echo "status=failure" >> $GITHUB_OUTPUT
          echo "message=Critical jobs failed:$FAILED_JOBS ❌" >> $GITHUB_OUTPUT
        fi

    - name: 📊 Create status summary
      run: |
        echo "## 🔍 Frontend CI/CD Status (Phase ${{ vars.CURRENT_PHASE }})" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "| Job | Status | Phase Requirement |" >> $GITHUB_STEP_SUMMARY
        echo "|-----|--------|-------------------|" >> $GITHUB_STEP_SUMMARY
        echo "| Environment Setup | ${{ needs.setup-environment.result == 'success' && '✅' || needs.setup-environment.result == 'skipped' && '⏭️' || '❌' }} | Always |" >> $GITHUB_STEP_SUMMARY
        echo "| Quality Checks | ${{ needs.quality-checks.result == 'success' && '✅' || needs.quality-checks.result == 'skipped' && '⏭️' || '❌' }} | Phase 3+ (TypeScript files exist) |" >> $GITHUB_STEP_SUMMARY
        echo "| Test Suite | ${{ needs.test-suite.result == 'success' && '✅' || needs.test-suite.result == 'skipped' && '⏭️' || '❌' }} | Phase 5+ (Test files exist) |" >> $GITHUB_STEP_SUMMARY
        echo "| Production Build | ${{ needs.production-build.result == 'success' && '✅' || needs.production-build.result == 'skipped' && '⏭️' || '❌' }} | Phase 3+ (TypeScript files exist) |" >> $GITHUB_STEP_SUMMARY
        echo "| Docker Build | ${{ needs.docker-build.result == 'success' && '✅' || needs.docker-build.result == 'skipped' && '⏭️' || '❌' }} | Phase 5+ (Dockerfile exists) |" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "**Overall Status**: ${{ steps.status.outputs.message }}" >> $GITHUB_STEP_SUMMARY
```

---

## 📊 コスト影響分析

### Phase 3実行コスト（現状 vs 最適化後）

| シナリオ | 現状（全スキップ） | 最適化後（スマート実行） | 差分 |
|---------|-------------------|------------------------|------|
| feature/PRプッシュ | 0分 | +9.5分/実行 | +9.5分 |
| main/developプッシュ | 0分 | +9.5分/実行 | +9.5分 |
| 月間推定（30 PR） | 0分 | +285分 | +285分 |

**内訳（最適化後Phase 3）**:
- setup-environment: 2分
- quality-checks (lint/type-check): 3分
- production-build: 4分
- ci-status: 0.5分
- **合計**: 9.5分/実行

### Phase 5実行コスト（完全実装後）

| シナリオ | 推定時間 |
|---------|---------|
| feature/PRプッシュ | 28分/実行 |
| main/developプッシュ | 36分/実行（performance-audit含む） |
| 月間推定（30 PR + 20 main） | 1,560分 |

**内訳（Phase 5 main/develop）**:
- setup-environment: 2分
- quality-checks（全matrix）: 6分
- test-suite（unit + e2e）: 8分
- production-build: 5分
- performance-audit: 8分
- docker-build: 5分
- deployment-prep: 2分
- **合計**: 36分/実行

### コスト削減効果維持検証

| 指標 | Phase 2実績 | Phase 3目標 | Phase 5予測 |
|------|-----------|-----------|-----------|
| 月間使用量 | 730分 | 1,015分 | 1,560分 |
| 無料枠使用率 | 36.5% | 50.8% | 78.0% |
| コスト削減率 | 52.3% | 45.0%（推定） | 35.0%（推定） |

**重要**:
- Phase 5でも無料枠（2,000分/月）内に収まる設計
- 並列実行最適化により実時間は短縮（wall time vs CPU time）

---

## ✅ 期待効果

### Phase 3での効果

1. **早期品質検証**
   - TypeScript型安全性チェック開始
   - ESLint規約違反の早期検出
   - Next.js設定ファイル検証

2. **依存関係管理**
   - package.json整合性自動検証
   - pnpm-lock.yamlバージョンロック確認
   - Node.js 22互換性チェック

3. **インフラ準備**
   - CI/CDパイプライン動作確認
   - キャッシュ戦略検証
   - 環境変数設定検証

### Phase 5での効果

1. **完全な品質保証**
   - 75%以上のテストカバレッジ
   - Core Web Vitals自動測定
   - セキュリティスキャン統合

2. **デプロイ自動化**
   - Cloudflare Pages自動デプロイ
   - Preview環境自動生成
   - ロールバック機能

3. **パフォーマンス監視**
   - Lighthouse CI連続測定
   - バンドルサイズ変化追跡
   - リグレッション自動検出

---

## 🚀 移行計画

### ステップ1: Phase 3即時適用（2025-10-08）

```bash
# 1. ワークフロー更新
git checkout -b fix/frontend-ci-phased-execution

# 2. frontend-ci.ymlを本戦略に基づいて更新
# （具体的な変更内容は次セクション参照）

# 3. テスト実行
git commit -m "fix(ci): フロントエンドCI/CD段階的実行戦略実装"
git push origin fix/frontend-ci-phased-execution

# 4. PR作成・マージ
gh pr create --title "フロントエンドCI/CD段階的実行戦略実装" \
  --body "Phase 3で実行可能なジョブとPhase 5待機ジョブを分離し、コスト効率を維持しながら早期品質検証を実現"
```

### ステップ2: Phase 4移行期（データベース実装中）

- フロントエンドCI/CDは引き続きPhase 3モードで実行
- バックエンドAPI完成後、モックデータでのE2Eテスト準備

### ステップ3: Phase 5完全移行（フロントエンド本格実装開始）

```bash
# 1. CURRENT_PHASE変数を5に更新
gh variable set CURRENT_PHASE --body "5" --repo daishiman/AutoForgeNexus

# 2. 全ジョブ自動有効化確認
# （条件分岐により自動的にPhase 5モードに移行）

# 3. テストファイル・Dockerfile作成
# （存在確認条件により該当ジョブが自動有効化）
```

---

## 📝 実装チェックリスト

### Phase 3対応（即時実施）

- [ ] `quality-checks`: matrix動的生成実装
- [ ] `production-build`: TypeScriptファイル存在チェック追加
- [ ] `test-suite`: テストファイル存在条件追加
- [ ] `performance-audit`: Phase 5条件追加
- [ ] `docker-build`: Dockerfile存在チェック追加
- [ ] `deployment-prep`: Phase 5条件追加
- [ ] `ci-status`: Phase依存のジョブリスト動的生成

### Phase 5準備（Phase 4完了後）

- [ ] テストファイル実装（unit/e2e）
- [ ] Dockerfile作成
- [ ] Lighthouse CI設定ファイル作成
- [ ] size-limit設定追加
- [ ] Cloudflare Pages設定

### 監視・改善

- [ ] GitHub Actions使用量監視（月次）
- [ ] コスト削減率トラッキング
- [ ] ジョブ実行時間最適化
- [ ] キャッシュヒット率改善

---

## 🔗 関連ドキュメント

- [プロジェクトCLAUDE.md](/Users/dm/dev/dev/個人開発/AutoForgeNexus/CLAUDE.md) - 環境構築フェーズ定義
- [フロントエンドCLAUDE.md](/Users/dm/dev/dev/個人開発/AutoForgeNexus/frontend/CLAUDE.md) - 実装状況
- [CI/CD最適化レポート](./ci-cd-optimization-report-2025-09-30.md) - 52.3%削減実績
- [GitHub Actions使用量レポート](./github-actions-usage-analysis-2025-09-30.md) - 無料枠分析

---

## 📊 成果指標

### Phase 3（2025年10月）

- **目標**: 環境検証とコード品質チェックの早期開始
- **KPI**:
  - TypeScript型エラー検出: 0件維持
  - ESLint違反検出: 0件維持
  - 依存関係整合性: 100%維持
  - CI実行時間: 9.5分/実行以下
  - 月間使用量: 1,015分以下（50.8%以下）

### Phase 5（2025年11月予定）

- **目標**: 完全な品質保証とデプロイ自動化
- **KPI**:
  - テストカバレッジ: 75%以上
  - Lighthouse Score: 95+
  - Core Web Vitals合格率: 100%
  - CI実行時間: 36分/実行以下（main/develop）
  - 月間使用量: 1,560分以下（78.0%以下）

---

**次のアクション**: `frontend-ci.yml`への本戦略適用実装
