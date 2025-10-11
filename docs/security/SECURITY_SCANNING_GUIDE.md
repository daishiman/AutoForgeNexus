# セキュリティスキャン運用ガイド

## 📋 ドキュメント情報

| 項目 | 内容 |
|------|------|
| **作成日** | 2025-10-10 |
| **最終更新** | 2025-10-10 |
| **対象システム** | AutoForgeNexus |
| **担当エージェント** | security-architect, compliance-officer |
| **レビュー周期** | 四半期ごと |

---

## 🎯 概要

AutoForgeNexus プロジェクトでは、以下の4つのセキュリティスキャンを自動実行しています。

### スキャンツール一覧

1. **TruffleHog** - シークレットスキャン
2. **Python Security Tools** - Safety, Bandit, pip-audit
3. **JavaScript Security Tools** - pnpm audit, audit-ci
4. **Checkov** - インフラストラクチャスキャン

---

## 🔐 1. TruffleHog（シークレットスキャン）

### 目的
Git 履歴から API キー、トークン、パスワード等の秘密情報を検出

### 実行タイミング

| イベント | 頻度 | 説明 |
|---------|------|------|
| **pull_request** | PR作成/更新時 | 差分スキャン |
| **push** | main/develop プッシュ時 | 全履歴スキャン |
| **schedule** | 毎週月曜日 03:00 JST | 定期フルスキャン |
| **workflow_dispatch** | 手動実行 | オンデマンド |

### 設定詳細

#### GitHub Actions 設定
```yaml
- name: Run TruffleHog
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    base: main
    head: HEAD
    extra_args: --only-verified --exclude-paths=.trufflehog_regex_ignore
    # 注: --fail, --no-update, --github-actions は Action により自動付与されます
```

#### 重要な設定パラメータ

| パラメータ | 値 | 説明 |
|-----------|---|------|
| `path` | `./` | スキャン対象ディレクトリ |
| `base` | `main` | ベースコミット |
| `head` | `HEAD` | 対象コミット |
| `--only-verified` | フラグ | 検証済み秘密情報のみ検出 |
| `--exclude-paths` | `.trufflehog_regex_ignore` | 除外パターンファイル |

#### 自動付与されるフラグ（extra_args に含めない）

⚠️ **重要**: 以下のフラグは TruffleHog Action v3 が自動で付与します。`extra_args` に含めると重複エラーになります。

- `--fail`: 秘密情報検出時にジョブを失敗させる
- `--no-update`: 検出器の自動更新を無効化
- `--github-actions`: GitHub Actions 用の出力形式

### 除外パターン管理

#### ファイル: `.trufflehog_regex_ignore`

**除外対象の例**:
```regex
# プロジェクトドキュメント
^CLAUDE\.md$
^README\.md$
^LICENSE$

# テストデータ
^tests/fixtures/.*$
^backend/tests/.*\.py$

# ビルド成果物
^node_modules/.*$
^\.next/.*$
^dist/.*$

# サンプルファイル
^\.env\.example$
^backend/\.env\.example$

# GitHub Actions 一時トークン（期限付き）
^ghp_[a-zA-Z0-9]{36}$
^ghs_[a-zA-Z0-9]{36}$
^github_pat_[a-zA-Z0-9]{82}$
```

#### 除外パターン追加手順

```bash
# 1. パターンファイルを編集
nano .trufflehog_regex_ignore

# 2. パターンのテスト
while IFS= read -r pattern; do
  [[ -z "$pattern" || "$pattern" =~ ^#.* ]] && continue
  
  if echo "test-string" | grep -qE "$pattern" 2>/dev/null; then
    echo "✅ 有効: $pattern"
  else
    echo "❌ 無効: $pattern"
    exit 1
  fi
done < .trufflehog_regex_ignore

# 3. ローカルテスト
docker run --rm -v "$(pwd):/repo" \
  ghcr.io/trufflesecurity/trufflehog:latest \
  git file:///repo/ \
  --since-commit=HEAD~10 \
  --only-verified \
  --exclude-paths=.trufflehog_regex_ignore

# 4. コミット
git add .trufflehog_regex_ignore
git commit -m "chore(security): TruffleHog除外パターン追加"
```

### ローカル実行方法

```bash
# 最新10コミットをスキャン
docker run --rm -v "$(pwd):/repo" \
  ghcr.io/trufflesecurity/trufflehog:latest \
  git file:///repo/ \
  --since-commit=HEAD~10 \
  --only-verified \
  --exclude-paths=.trufflehog_regex_ignore

# 全リポジトリをスキャン
docker run --rm -v "$(pwd):/repo" \
  ghcr.io/trufflesecurity/trufflehog:latest \
  git file:///repo/ \
  --only-verified \
  --exclude-paths=.trufflehog_regex_ignore

# JSON 形式で結果を保存
docker run --rm -v "$(pwd):/repo" \
  ghcr.io/trufflesecurity/trufflehog:latest \
  git file:///repo/ \
  --only-verified \
  --exclude-paths=.trufflehog_regex_ignore \
  --json > trufflehog-results.json
```

---

## 🐍 2. Python セキュリティスキャン

### 使用ツール

#### Safety - 既知の脆弱性チェック

**目的**: PyPI パッケージの既知の脆弱性を検出

**実行方法**:
```bash
cd backend
pip install safety
safety check --json --output safety-report.json
```

**出力例**:
```json
{
  "report": {
    "vulnerabilities": [
      {
        "package": "requests",
        "installed_version": "2.25.0",
        "vulnerable_versions": "<2.31.0",
        "severity": "high"
      }
    ]
  }
}
```

#### Bandit - セキュリティ問題検出

**目的**: Python コードの一般的なセキュリティ問題を検出

**実行方法**:
```bash
cd backend
pip install bandit[toml]
bandit -r src/ -f json -o bandit-report.json
```

**検出例**:
- ハードコードされたパスワード
- SQL インジェクション
- 安全でない乱数生成
- pickle の使用

#### pip-audit - PyPI 脆弱性チェック

**目的**: PyPI アドバイザリデータベースと照合

**実行方法**:
```bash
cd backend
pip install pip-audit
pip-audit --format=json --output=pip-audit-report.json
```

### CI/CD 統合

```yaml
- name: Run Safety scan
  run: |
    cd backend
    safety check --json --output safety-report.json || true

- name: Run Bandit scan
  run: |
    cd backend
    bandit -r src/ -f json -o bandit-report.json || true

- name: Run pip-audit
  run: |
    cd backend
    pip-audit --format=json --output=pip-audit-report.json || true
```

**注**: `|| true` により、脆弱性検出時もジョブを継続（レポートを優先）

---

## 📦 3. JavaScript/TypeScript セキュリティスキャン

### 使用ツール

#### pnpm audit - 依存関係の脆弱性チェック

**目的**: npm パッケージの既知の脆弱性を検出

**実行方法**:
```bash
cd frontend
pnpm audit --json > pnpm-audit-report.json
```

**重要度レベル**:
- **critical**: 即座対応必須
- **high**: 24時間以内に対応
- **moderate**: 1週間以内に対応
- **low**: 次回スプリントで対応

#### audit-ci - CI/CD統合監査

**目的**: CI/CD パイプラインでの自動監査

**実行方法**:
```bash
cd frontend
npx audit-ci --package-manager pnpm --report-type json --output-file audit-ci-report.json
```

**設定ファイル**: `frontend/.audit-ci.json`
```json
{
  "low": true,
  "moderate": true,
  "high": true,
  "critical": true,
  "allowlist": [
    "GHSA-xxxx-xxxx-xxxx"
  ]
}
```

### ローカル実行

```bash
# pnpm audit のみ
cd frontend
pnpm audit

# audit-ci での厳格チェック
cd frontend
npx audit-ci --package-manager pnpm --critical --high

# 修正提案の自動適用
pnpm audit --fix
```

---

## 🏗️ 4. インフラストラクチャスキャン（Checkov）

### 目的
Infrastructure as Code (IaC) のセキュリティ問題を検出

### スキャン対象

#### Docker 設定
```bash
checkov -f docker-compose.yml -o json --output-file checkov-docker-report.json
checkov -f docker-compose.dev.yml -o json --output-file checkov-docker-dev-report.json
checkov -f docker-compose.prod.yml -o json --output-file checkov-docker-prod-report.json
```

**検出例**:
- ルート権限での実行
- 最新タグの使用（non-specific version）
- ヘルスチェックの欠如
- リソース制限の欠如

#### GitHub Actions ワークフロー
```bash
checkov -d .github/workflows -o json --output-file checkov-github-actions-report.json
```

**検出例**:
- シークレットのハードコード
- 過度な権限設定
- 信頼されていないアクションの使用
- タイムアウト設定の欠如

### 推奨設定

#### .checkov.yml
```yaml
# Checkov 設定ファイル
framework:
  - dockerfile
  - github_actions

skip-check:
  # 開発環境でのルート権限は許可
  - CKV_DOCKER_2

output: json
quiet: false
```

---

## 📊 監査ログ保存

### GDPR Article 30 準拠

**保存期間**: 365日

**保存場所**: GitHub Actions Artifacts

**設定**:
```yaml
- name: Upload scan results
  uses: actions/upload-artifact@v4
  with:
    name: security-scan-results
    path: |
      backend/safety-report.json
      backend/bandit-report.json
      frontend/pnpm-audit-report.json
      checkov-report.json
    retention-days: 365  # GDPR Article 30準拠
```

### アクセス管理

| 役割 | 権限 | 対象 |
|------|------|------|
| **Security Team** | Read/Write | 全スキャン結果 |
| **Development Team** | Read | 自チームのスキャン結果 |
| **Compliance Officer** | Read | 全監査ログ |
| **External Auditor** | Read（期間限定） | 監査期間中のみ |

---

## 🔧 トラブルシューティング

### 問題1: TruffleHog - `flag 'fail' cannot be repeated`

#### 症状
```
trufflehog: error: flag 'fail' cannot be repeated, try --help
Error: Process completed with exit code 1.
```

#### 原因
`extra_args` で `--fail`, `--no-update`, `--github-actions` を重複指定

#### 解決策
```yaml
# ❌ 間違い
extra_args: --only-verified --exclude-paths=.trufflehog_regex_ignore --fail --no-update --github-actions

# ✅ 正しい
extra_args: --only-verified --exclude-paths=.trufflehog_regex_ignore
# 注: --fail, --no-update, --github-actions は Action により自動付与されます
```

#### 詳細ガイド
`docs/issues/TRUFFLEHOG_DUPLICATE_FLAG_ERROR_FIX_GUIDE.md` を参照

---

### 問題2: 誤検知（False Positive）

#### 症状
テストデータや公開情報が秘密情報として検出される

#### 解決策

##### Step 1: 除外パターンの追加
```bash
# .trufflehog_regex_ignore を編集
nano .trufflehog_regex_ignore

# パターン例を追加:
# テストデータの除外
^tests/fixtures/sample-api-key\.txt$

# ドキュメント内のサンプルトークン除外
^docs/examples/.*$
```

##### Step 2: パターンのテスト
```bash
# パターンが正しく動作するか確認
echo "tests/fixtures/sample-api-key.txt" | grep -E "^tests/fixtures/.*$"
# 期待出力: tests/fixtures/sample-api-key.txt（マッチした場合）

# ローカルスキャンで検証
docker run --rm -v "$(pwd):/repo" \
  ghcr.io/trufflesecurity/trufflehog:latest \
  git file:///repo/ \
  --since-commit=HEAD~5 \
  --only-verified \
  --exclude-paths=.trufflehog_regex_ignore
```

##### Step 3: PR で変更提出
```bash
git add .trufflehog_regex_ignore
git commit -m "chore(security): TruffleHog除外パターン追加 - テストデータ誤検知対策"
git push origin <branch-name>
```

---

### 問題3: Python Safety - 脆弱性検出

#### 症状
```json
{
  "vulnerabilities": [
    {
      "package": "requests",
      "installed_version": "2.25.0",
      "vulnerable_versions": "<2.31.0",
      "severity": "high"
    }
  ]
}
```

#### 解決手順

##### Step 1: 脆弱性の評価
```bash
# 詳細情報を確認
cd backend
safety check --full-report

# CVE 詳細を確認
# 出力例:
# -> Vulnerability found in requests version 2.25.0
# -> CVE-2023-32681
# -> Description: Requests is vulnerable to SSRF
```

##### Step 2: パッケージのアップデート
```bash
# requirements.txt を更新
# requests==2.25.0 → requests>=2.31.0

# 依存関係の再インストール
pip install -e .[dev]

# 再スキャン
safety check
# 期待出力: All good! No known security vulnerabilities found.
```

##### Step 3: テストの実行
```bash
# アップデート後のテスト
pytest tests/ --cov=src --cov-report=term

# 互換性確認
python -c "import requests; print(requests.__version__)"
# 期待出力: 2.31.0 以上
```

---

### 問題4: pnpm audit - 依存関係の脆弱性

#### 症状
```
┌─────────────────────┬──────────────────────────────────┐
│ high                │ Prototype Pollution in lodash    │
├─────────────────────┼──────────────────────────────────┤
│ Package             │ lodash                           │
├─────────────────────┼──────────────────────────────────┤
│ Vulnerable versions │ <4.17.21                         │
└─────────────────────┴──────────────────────────────────┘
```

#### 解決手順

##### Step 1: 自動修正を試行
```bash
cd frontend
pnpm audit --fix

# 出力例:
# fixed 5 vulnerabilities in 1234 packages
```

##### Step 2: 手動アップデート（自動修正できない場合）
```bash
# 影響範囲を確認
pnpm why lodash

# 出力例:
# lodash 4.17.15
# └─┬ some-package 1.0.0
#   └── lodash ^4.17.15

# package.json を更新
# "lodash": "^4.17.21" に変更

# 再インストール
pnpm install

# 再スキャン
pnpm audit
```

##### Step 3: Breaking Changes の確認
```bash
# テストを実行
pnpm test

# 型チェック
pnpm type-check

# ビルド確認
pnpm build
```

---

### 問題5: Checkov - インフラストラクチャ問題

#### 症状
```
Check: CKV_DOCKER_2: "Ensure that HEALTHCHECK instructions have been added"
FAILED for resource: Dockerfile.backend
```

#### 解決例

##### Docker ヘルスチェック追加
```dockerfile
# Dockerfile.backend に追加

# ヘルスチェックの設定
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

##### リソース制限の追加
```yaml
# docker-compose.yml に追加
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

---

## 📈 スキャン結果の分析

### GitHub Actions での確認

```bash
# 最新のスキャン結果を確認
gh run view --log

# スキャン履歴を確認
gh run list --workflow="Security Scanning" --limit 10

# 特定のスキャン結果をダウンロード
gh run download <run-id> -n security-scan-results
```

### ローカルでの結果分析

```bash
# JSON 結果の解析
cat safety-report.json | jq '.report.vulnerabilities[] | {package, severity, cve}'

# 重要度別カウント
cat bandit-report.json | jq '.metrics._totals | {high, medium, low}'

# pnpm audit のサマリー
pnpm audit --json | jq '.metadata | {vulnerabilities, dependencies, devDependencies}'
```

---

## 🔄 定期メンテナンス

### 週次タスク（月曜日）

```bash
# 1. 定期スキャン結果の確認
gh run list --workflow="Security Scanning" --limit 1

# 2. 検出された脆弱性の評価
# GitHub Actions の Artifacts から結果をダウンロード

# 3. 優先度付けと対応計画
# Critical/High は即座対応、Medium/Low はバックログ登録
```

### 月次タスク

```bash
# 1. 除外パターンのレビュー
cat .trufflehog_regex_ignore

# 2. 不要な除外パターンの削除
# 3. 監査ログの確認（GDPR 準拠）
# 4. セキュリティメトリクスのレポート作成
```

### 四半期タスク

```bash
# 1. スキャンツールのバージョンアップデート
# 2. 本ガイドのレビューと更新
# 3. セキュリティポリシーの見直し
# 4. チームトレーニングの実施
```

---

## 📚 参考資料

### 公式ドキュメント

| ツール | URL |
|--------|-----|
| **TruffleHog** | https://github.com/trufflesecurity/trufflehog |
| **Safety** | https://pyup.io/safety/ |
| **Bandit** | https://bandit.readthedocs.io/ |
| **pip-audit** | https://pypi.org/project/pip-audit/ |
| **audit-ci** | https://github.com/IBM/audit-ci |
| **Checkov** | https://www.checkov.io/ |

### コンプライアンス

| 規制 | URL |
|------|-----|
| **GDPR Article 30** | https://gdpr-info.eu/art-30-gdpr/ |
| **OWASP Top 10** | https://owasp.org/www-project-top-ten/ |
| **SOC2** | https://www.aicpa.org/soc |

### 社内資料

- [TruffleHog 重複フラグエラー修正ガイド](../issues/TRUFFLEHOG_DUPLICATE_FLAG_ERROR_FIX_GUIDE.md)
- [セキュリティポリシー](SECURITY_POLICY.md)
- [インシデント対応手順](INCIDENT_RESPONSE.md)

---

## 🤝 サポート

### 問い合わせ先

| 役割 | 担当 | 連絡先 |
|------|------|--------|
| **セキュリティ全般** | Security Team | `#security` |
| **CI/CD 問題** | DevOps Team | `#devops` |
| **コンプライアンス** | Compliance Officer | `compliance@example.com` |

### エージェントコマンド

```bash
# セキュリティ監査の実行
/ai:quality:security --scan both --pentest --compliance gdpr

# インシデント対応
/ai:operations:incident critical --escalate --rca --postmortem

# 監視設定
/ai:operations:monitor security --logs --alerts
```

---

## 🔄 バージョン履歴

| バージョン | 日付 | 変更内容 | 承認者 |
|-----------|------|---------|--------|
| 1.0 | 2025-10-10 | 初版作成 | security-architect, compliance-officer |

---

**作成**: security-architect, compliance-officer, technical-documentation  
**承認**: 2025-10-10  
**次回レビュー**: 2026-01-10（四半期レビュー）
