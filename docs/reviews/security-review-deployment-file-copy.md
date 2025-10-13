# セキュリティレビュー: `cp -r src/* .` デプロイ方法の評価

**レビュー日**: 2025-10-12
**レビュアー**: Security Architect (Alex Stamos Persona)
**対象**: CI/CDパイプラインにおける `cp -r src/* .` コマンドの使用
**重要度**: 🔴 Critical
**総合リスクスコア**: 7.8/10.0（High Risk）

---

## エグゼクティブサマリー

`cp -r src/* .` によるデプロイ方法は、**4つの重大なセキュリティリスク**を含んでおり、即時の対応が必要です。特に機密情報漏洩リスクは**CVSS 8.5-9.0相当**であり、GDPR/CCPA違反による法的リスクも伴います。

**推奨**: 即座に使用を停止し、マニフェストベースデプロイまたはコンテナイメージビルドに移行すべきです。

---

## 1. リスク評価マトリクス

| リスク項目 | 影響度 | 発生確率 | リスクレベル | CVSS v3.1相当 | 対策優先度 |
|-----------|--------|---------|-------------|---------------|-----------|
| **機密情報漏洩** | 致命的(9) | 高(0.7) | 🔴 Critical | 8.5-9.0 | P0 |
| **不要ファイル包含** | 高(7) | 非常に高(0.9) | 🔴 High | 7.0-7.5 | P1 |
| **パーミッション継承** | 中(5) | 中(0.5) | 🟡 Medium | 5.0-5.5 | P2 |
| **予測不可能な動作** | 中(6) | 中(0.4) | 🟡 Medium | 4.5-5.0 | P2 |

**総合評価**: 🔴 **High Risk (7.8/10.0)**

---

## 2. 詳細リスク分析

### 2.1 リスク1: 機密情報の漏洩 🔴 Critical

#### 問題の詳細
- `.gitignore`で除外されているファイルも、`src/`内にあれば無条件でコピーされる
- ワイルドカード（`*`）による無差別選択で、意図しないファイルが含まれる

#### 具体的な脅威シナリオ
```bash
# 開発者が誤って作成した機密ファイル
src/.env.local          # Turso Auth Token, Clerk Secret
src/secrets.json        # LiteLLM API Keys
src/.aws/credentials    # AWS Access Keys
src/test_data.json      # 個人情報を含むテストデータ

# これらがすべて本番環境にコピーされる
$ cp -r src/* .
# → .env.local, secrets.json, .aws/, test_data.json が展開
```

#### 影響範囲
| 漏洩情報 | 影響 | CVSS Base Score |
|---------|------|-----------------|
| **Turso Auth Tokens** | データベース全アクセス、データ改竄・削除 | 9.0 |
| **Clerk Secret Key** | 認証バイパス、全ユーザーなりすまし | 8.8 |
| **LiteLLM API Keys** | コスト爆発（$10,000+）、不正利用 | 7.5 |
| **PII（個人情報）** | GDPR違反、罰金最大2000万ユーロ | 8.5 |

#### OWASP Top 10 マッピング
- **A01:2021 - Broken Access Control**: 機密ファイルへの不正アクセス
- **A05:2021 - Security Misconfiguration**: 不適切なデプロイ設定

#### STRIDE分析
- **Information Disclosure（情報漏洩）**: 機密データの露出
- **Elevation of Privilege（権限昇格）**: 漏洩した認証情報による権限奪取

#### コンプライアンス影響
- **GDPR Art.32**: 技術的・組織的保護措置の欠如 → 罰金最大2000万ユーロまたは全世界年間売上高の4%
- **CCPA §1798.150**: データ侵害時の損害賠償（1件あたり$100-$750）
- **ISO 27001**: A.18.1.3 個人データ保護要件違反

---

### 2.2 リスク2: 不要ファイルの包含 🔴 High

#### 問題の詳細
- 開発時に作成された一時ファイル、バックアップ、キャッシュも無差別にコピー
- デバッグ情報、テストデータが本番環境に混入

#### 典型的な不要ファイル
```bash
src/__pycache__/        # Pythonバイトコードキャッシュ
src/.pytest_cache/      # pytest実行キャッシュ
src/*.pyc               # コンパイル済みファイル
src/*.log               # ローカルログファイル
src/*.backup            # エディタバックアップ
src/test_*.py           # テストファイル（本番不要）
src/.coverage           # カバレッジレポート
```

#### セキュリティへの影響
1. **情報漏洩**: ログファイルにスタックトレース、内部パス、環境変数が含まれる
2. **攻撃対象の拡大**: 不要なテストエンドポイントが本番で有効化
3. **パフォーマンス劣化**: キャッシュファイルによるディスク使用量増加
4. **脆弱性の増加**: テストコードの脆弱性が本番環境に混入

#### 実際の事例
```python
# src/debug_helpers.py（開発用）
DEBUG_MODE = True
ENABLE_SQL_LOGGING = True
SKIP_AUTHENTICATION = True  # ⚠️ 本番環境で有効化されると致命的

# これが本番環境にコピーされると認証バイパス脆弱性に
```

#### CVSS v3.1評価
- **Attack Vector (AV)**: Network (N)
- **Attack Complexity (AC)**: Low (L)
- **Confidentiality Impact (C)**: High (H)
- **Integrity Impact (I)**: High (H)
- **Base Score**: **7.5 (High)**

---

### 2.3 リスク3: パーミッション・所有権の継承 🟡 Medium

#### 問題の詳細
- `cp -r`はデフォルトでファイルパーミッションを保持（`-p`オプション不使用でも一部継承）
- 開発環境の緩いパーミッション設定が本番環境に適用される

#### 脆弱なパーミッションの例
```bash
# 開発環境で作成されたファイル
-rwxrwxrwx 1 developer developer config.py       # 777（全ユーザー読み書き実行可）
-rw-rw-rw- 1 developer developer secrets.json    # 666（全ユーザー読み書き可）
-rwxr-xr-x 1 developer developer migrate.sh      # 755（実行権限あり）

# 本番環境にコピー後
$ ls -l /app/
-rwxrwxrwx 1 www-data www-data config.py         # ⚠️ Webサーバーから書き込み可能
-rw-rw-rw- 1 www-data www-data secrets.json      # ⚠️ すべてのプロセスから読み取り可能
```

#### セキュリティへの影響
1. **ローカルファイルインクルージョン（LFI）**: 書き込み可能な設定ファイルの改竄
2. **コード実行**: 意図しないスクリプトファイルが実行権限を持つ
3. **情報漏洩**: 過度に緩いパーミッションによるファイル読み取り

#### CIS Controls準拠違反
- **CIS Control 3.3**: ファイルシステムパーミッションの制限
- **CIS Control 5.2**: 最小権限の原則（Principle of Least Privilege）

#### 推奨パーミッション
```bash
# 本番環境の推奨パーミッション
-rw-r--r-- 1 root     www-data config.py        # 644（rootのみ書き込み可）
-rw------- 1 root     root     secrets.json     # 600（rootのみアクセス可）
-rwxr-xr-x 1 root     root     app.py           # 755（rootのみ書き込み可）
```

---

### 2.4 リスク4: 予測不可能な動作 🟡 Medium

#### ワイルドカードの環境依存性
```bash
# bashのglob展開はシェル設定に依存
src/
├── .env.example        # コピーされない（dotfileはデフォルト除外）
├── .gitkeep           # コピーされない
├── ..hidden           # コピーされる可能性（bashバージョン依存）
├── file with spaces   # スペースを含むファイル名（エラーの可能性）
├── symlink -> /etc    # シンボリックリンク（-Lオプション次第）
```

#### シンボリックリンク攻撃リスク
```bash
# 攻撃者が悪意あるシンボリックリンクを作成
$ ln -s /etc/passwd src/users.txt
$ ln -s /etc/shadow src/.secrets

# cp -r src/* . を実行すると
# /etc/passwd, /etc/shadowがコピー先に露出する可能性
```

#### 対策の欠如
- ファイル検証なし: コピー前のファイルリスト確認がない
- エラーハンドリングなし: 失敗しても処理が継続
- ログ記録なし: 何がコピーされたか追跡不可能

---

## 3. 安全な代替手法

### 3.1 推奨手法1: マニフェストベースデプロイ（最推奨）

```yaml
# .deploy/manifest.yaml
version: 1.0
include:
  - "app/**/*.py"
  - "core/**/*.py"
  - "api/**/*.py"
  - "templates/**/*.html"
  - "static/**"
exclude:
  - "**/__pycache__"
  - "**/.pytest_cache"
  - "**/*.pyc"
  - "**/test_*"
  - "**/.env*"
  - "**/*.log"
  - "**/*.backup"

permissions:
  files: "644"
  directories: "755"
  owner: "root"
  group: "www-data"
```

```bash
# デプロイスクリプト
#!/bin/bash
set -euo pipefail

MANIFEST=".deploy/manifest.yaml"
SRC_DIR="src"
DEST_DIR="/app"

# マニフェストベースのファイルコピー
yq eval '.include[]' "$MANIFEST" | while read -r pattern; do
  find "$SRC_DIR" -path "$SRC_DIR/$pattern" -type f -exec cp --parents {} "$DEST_DIR" \;
done

# パーミッション修正
find "$DEST_DIR" -type f -exec chmod 644 {} \;
find "$DEST_DIR" -type d -exec chmod 755 {} \;
chown -R root:www-data "$DEST_DIR"

# 検証
echo "Deployed files:"
find "$DEST_DIR" -type f | sort
```

**メリット**:
- ✅ デプロイ対象が明示的で予測可能
- ✅ バージョン管理によるレビュー可能性
- ✅ パーミッション・所有権の厳格な管理
- ✅ 監査証跡の確保

---

### 3.2 推奨手法2: .deployignore利用

```bash
# .deployignore（.gitignoreと同様の形式）
# 機密情報
.env*
*.local
secrets.*
credentials.*

# 開発ファイル
__pycache__/
.pytest_cache/
*.pyc
*.pyo
*.pyd
.coverage
htmlcov/

# テスト・デバッグ
test_*
*_test.py
debug_*
*.log
*.backup

# エディタ・IDE
.vscode/
.idea/
*.swp
*.swo
*~

# ドキュメント（本番不要）
docs/
*.md
!README.md  # READMEのみ許可
```

```bash
# rsyncによる除外制御デプロイ
#!/bin/bash
rsync -av \
  --exclude-from='.deployignore' \
  --chmod=D755,F644 \
  --chown=root:www-data \
  --delete \
  src/ /app/

# 検証: 機密ファイルが含まれていないか確認
if find /app -name ".env*" -o -name "secrets.*" | grep -q .; then
  echo "ERROR: Secret files detected in deployment!"
  exit 1
fi
```

**メリット**:
- ✅ .gitignoreの知見を活用可能
- ✅ 除外ルールの集約管理
- ✅ rsyncの差分転送で効率的

---

### 3.3 推奨手法3: コンテナイメージビルド（Cloudflare Workers Python）

```dockerfile
# Dockerfile.production
FROM python:3.13-slim AS builder

# 依存関係のみインストール
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 本番ステージ
FROM python:3.13-slim
WORKDIR /app

# 依存関係コピー
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# アプリケーションコードのみコピー（明示的）
COPY src/app /app/app
COPY src/core /app/core
COPY src/api /app/api
COPY src/main.py /app/

# 機密情報は環境変数で注入（ビルド時には含めない）
# ENV DATABASE_URL は実行時に設定

# パーミッション設定
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    chmod -R 644 /app/**/*.py

USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# .dockerignore（コンテナビルドで除外）
**/__pycache__
**/.pytest_cache
**/*.pyc
**/.env*
**/test_*
**/*.log
.git
.github
docs/
tests/
Dockerfile*
docker-compose*.yml
```

**メリット**:
- ✅ 多段階ビルドで最小限のファイルのみ含む
- ✅ イミュータブルなデプロイメント
- ✅ 環境変数による機密情報注入（ビルド時除外）
- ✅ Cloudflare Workers Pythonとの統合

---

### 3.4 推奨手法4: GitHub Actionsでの検証付きデプロイ

```yaml
# .github/workflows/deploy.yml
name: Secure Deployment

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 機密ファイル検出
      - name: Scan for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./src
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

      # 不要ファイル検出
      - name: Check for unwanted files
        run: |
          UNWANTED_PATTERNS=(
            "*.pyc"
            "__pycache__"
            ".env*"
            "*.log"
            "test_*"
          )

          for pattern in "${UNWANTED_PATTERNS[@]}"; do
            if find src/ -name "$pattern" | grep -q .; then
              echo "ERROR: Unwanted files detected: $pattern"
              exit 1
            fi
          done

      # マニフェストベースデプロイ
      - name: Deploy with manifest
        run: |
          chmod +x .deploy/deploy.sh
          .deploy/deploy.sh --manifest .deploy/manifest.yaml --dest /app

      # デプロイ検証
      - name: Verify deployment
        run: |
          # 機密ファイルが含まれていないか確認
          if find /app -name ".env*" -o -name "secrets.*" | grep -q .; then
            echo "ERROR: Secret files found in deployment!"
            exit 1
          fi

          # パーミッション検証
          if find /app -type f -perm /022 | grep -q .; then
            echo "ERROR: World-writable files detected!"
            exit 1
          fi
```

---

## 4. 実装ロードマップ

### Phase 1: 即時対応（24時間以内）🚨

**優先度**: P0（Critical）

```bash
# 1. 現在のデプロイメントを一時停止
# 2. .deployignoreファイルを作成
cat > .deployignore <<EOF
.env*
*.local
secrets.*
__pycache__/
.pytest_cache/
*.pyc
test_*
*.log
*.backup
EOF

# 3. rsyncベースのデプロイに切り替え
cat > deploy-safe.sh <<'EOF'
#!/bin/bash
set -euo pipefail

rsync -av \
  --exclude-from='.deployignore' \
  --chmod=D755,F644 \
  --chown=root:www-data \
  src/ /app/

# 機密ファイル検証
if find /app -name ".env*" -o -name "secrets.*" | grep -q .; then
  echo "ERROR: Secret files detected!"
  exit 1
fi

echo "Deployment successful"
EOF

chmod +x deploy-safe.sh
```

---

### Phase 2: 検証強化（1週間以内）🔴

**優先度**: P1（High）

```yaml
# .github/workflows/deploy-validation.yml
name: Deployment Validation

on:
  push:
    branches: [main, develop]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # TruffleHogによる機密情報スキャン
      - name: Scan for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./src
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --only-verified

      # gitleaksによる二重チェック
      - name: Gitleaks scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}

      # 不要ファイル検出
      - name: Check unwanted files
        run: |
          ./.github/scripts/check-unwanted-files.sh

      # SBOM生成
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          path: ./src
          format: cyclonedx-json
```

---

### Phase 3: マニフェストベース移行（2週間以内）🟡

**優先度**: P2（Medium）

```yaml
# .deploy/manifest.yaml
version: 1.0
metadata:
  project: AutoForgeNexus
  environment: production
  created: 2025-10-12

include:
  - "app/**/*.py"
  - "core/**/*.py"
  - "api/**/*.py"
  - "domain/**/*.py"
  - "infrastructure/**/*.py"
  - "templates/**/*.html"
  - "static/**/*.css"
  - "static/**/*.js"
  - "alembic/**/*.py"
  - "alembic.ini"
  - "requirements.txt"

exclude:
  - "**/__pycache__"
  - "**/.pytest_cache"
  - "**/*.pyc"
  - "**/*.pyo"
  - "**/test_*"
  - "**/*_test.py"
  - "**/.env*"
  - "**/*.log"
  - "**/*.backup"
  - "**/debug_*"

permissions:
  files: "644"
  directories: "755"
  owner: "root"
  group: "www-data"

validation:
  max_file_size: "10MB"
  allowed_extensions:
    - ".py"
    - ".html"
    - ".css"
    - ".js"
    - ".json"
    - ".yaml"
    - ".ini"
  forbidden_patterns:
    - "password"
    - "secret"
    - "token"
    - "api_key"
```

---

### Phase 4: IaCスキャン統合（1ヶ月以内）🟢

**優先度**: P3（Low）

```yaml
# .github/workflows/iac-security.yml
name: IaC Security Scanning

on:
  pull_request:
    paths:
      - '.deploy/**'
      - 'docker-compose*.yml'
      - 'Dockerfile*'
      - '.github/workflows/**'

jobs:
  checkov:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Checkovによるインフラコードスキャン
      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: dockerfile,yaml
          output_format: sarif
          output_file_path: checkov-results.sarif

      # 結果をGitHub Security Advisoriesにアップロード
      - name: Upload SARIF results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: checkov-results.sarif

  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Trivyによる設定スキャン
      - name: Run Trivy config scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-config-results.sarif'
```

---

## 5. モニタリングとアラート

### 5.1 デプロイ時検証スクリプト

```python
# .deploy/validate_deployment.py
import os
import sys
from pathlib import Path
from typing import List, Tuple

# 禁止パターン
FORBIDDEN_PATTERNS = [
    ".env",
    ".env.local",
    ".env.production",
    "secrets.json",
    "credentials.json",
    "*.key",
    "*.pem",
    "id_rsa",
]

# 禁止ファイル名（部分一致）
FORBIDDEN_NAMES = [
    "password",
    "secret",
    "token",
    "api_key",
    "private_key",
]

def scan_directory(directory: Path) -> Tuple[List[Path], List[Path]]:
    """デプロイディレクトリをスキャン"""
    forbidden_files = []
    suspicious_files = []

    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue

        # 禁止パターンチェック
        for pattern in FORBIDDEN_PATTERNS:
            if file_path.match(pattern):
                forbidden_files.append(file_path)
                break

        # 疑わしいファイル名チェック
        file_name_lower = file_path.name.lower()
        for name in FORBIDDEN_NAMES:
            if name in file_name_lower:
                suspicious_files.append(file_path)
                break

    return forbidden_files, suspicious_files

def check_permissions(directory: Path) -> List[Path]:
    """パーミッションチェック"""
    world_writable = []

    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue

        # 022（world-writable）チェック
        mode = file_path.stat().st_mode
        if mode & 0o022:
            world_writable.append(file_path)

    return world_writable

def main():
    deploy_dir = Path("/app")

    print("🔍 Scanning deployment directory...")

    # ファイルスキャン
    forbidden, suspicious = scan_directory(deploy_dir)

    if forbidden:
        print("❌ CRITICAL: Forbidden files detected!")
        for f in forbidden:
            print(f"  - {f}")
        sys.exit(1)

    if suspicious:
        print("⚠️ WARNING: Suspicious files detected:")
        for f in suspicious:
            print(f"  - {f}")

    # パーミッションチェック
    world_writable = check_permissions(deploy_dir)
    if world_writable:
        print("❌ CRITICAL: World-writable files detected!")
        for f in world_writable:
            print(f"  - {f} (mode: {oct(f.stat().st_mode)})")
        sys.exit(1)

    print("✅ Deployment validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

---

### 5.2 Prometheusアラート設定

```yaml
# monitoring/prometheus/alerts/deployment.yml
groups:
  - name: deployment_security
    interval: 30s
    rules:
      # デプロイ時の機密ファイル検出
      - alert: SecretFileDeployed
        expr: deployment_secret_files_count > 0
        for: 1m
        labels:
          severity: critical
          category: security
        annotations:
          summary: "Secret files detected in deployment"
          description: "{{ $value }} secret files found in /app directory"

      # 不正なパーミッション検出
      - alert: InsecureFilePermissions
        expr: deployment_world_writable_files_count > 0
        for: 5m
        labels:
          severity: high
          category: security
        annotations:
          summary: "World-writable files detected"
          description: "{{ $value }} files with insecure permissions (022)"

      # デプロイ失敗率
      - alert: DeploymentFailureRateHigh
        expr: rate(deployment_failures_total[5m]) > 0.2
        for: 10m
        labels:
          severity: warning
          category: reliability
        annotations:
          summary: "High deployment failure rate"
          description: "Deployment failure rate: {{ $value | humanizePercentage }}"
```

---

## 6. コンプライアンスマッピング

### 6.1 GDPR準拠

| 条項 | 要件 | 現状リスク | 対策 |
|-----|------|-----------|------|
| **Art.25** データ保護バイデザイン | デフォルトで個人データ保護 | 🔴 機密情報が無防備にデプロイ | マニフェストベースデプロイ導入 |
| **Art.32** セキュリティ対策 | 技術的・組織的保護措置 | 🔴 不十分なアクセス制御 | パーミッション厳格化 |
| **Art.33** 侵害通知 | 72時間以内の通知義務 | 🟡 検出メカニズム不足 | デプロイ検証自動化 |

### 6.2 NIST Cybersecurity Framework

| 機能 | カテゴリ | 現状ギャップ | 改善アクション |
|-----|---------|-------------|--------------|
| **Identify (ID)** | ID.AM-2: ソフトウェアプラットフォーム管理 | 🔴 デプロイ対象が不明確 | SBOM生成・管理 |
| **Protect (PR)** | PR.DS-1: データの保護 | 🔴 機密データ保護不足 | .deployignore実装 |
| **Detect (DE)** | DE.CM-7: 不正行為監視 | 🟡 デプロイ検証なし | 自動スキャン導入 |
| **Respond (RS)** | RS.AN-1: 通知の分析 | 🟡 アラート設定なし | Prometheus監視 |

### 6.3 CIS Controls v8

| Control | 要件 | 実装状況 | 優先度 |
|---------|------|---------|--------|
| **3.3** | ファイルシステムパーミッション管理 | 🔴 未実装 | P0 |
| **5.2** | 最小権限の原則 | 🔴 未実装 | P0 |
| **8.3** | 監査ログ管理 | 🟡 部分実装 | P1 |
| **16.6** | ソフトウェア配信の保護 | 🔴 未実装 | P0 |

---

## 7. 参考資料

### セキュリティ標準
- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP Application Security Verification Standard (ASVS) 4.0](https://owasp.org/www-project-application-security-verification-standard/)
- [CIS Controls v8](https://www.cisecurity.org/controls/v8)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### コンプライアンス
- [GDPR Art.32: Security of processing](https://gdpr-info.eu/art-32-gdpr/)
- [CCPA §1798.150: Personal information security breaches](https://oag.ca.gov/privacy/ccpa)
- [ISO/IEC 27001:2022](https://www.iso.org/standard/27001)

### ツール・ライブラリ
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - 機密情報検出
- [gitleaks](https://github.com/gitleaks/gitleaks) - Git履歴スキャン
- [Checkov](https://www.checkov.io/) - IaCセキュリティスキャン
- [Trivy](https://trivy.dev/) - 脆弱性・設定スキャン

---

## 8. 承認・レビュー履歴

| 日付 | レビュアー | 役割 | 承認状況 |
|-----|----------|------|---------|
| 2025-10-12 | Security Architect | セキュリティ評価 | ✅ 承認 |
| - | DevOps Coordinator | 運用実装レビュー | ⏳ 保留 |
| - | Compliance Officer | コンプライアンスレビュー | ⏳ 保留 |
| - | System Architect | アーキテクチャ承認 | ⏳ 保留 |

---

## 9. アクションアイテム

### 即時対応（24時間以内）🚨
- [ ] `cp -r src/* .` の使用を即座に停止
- [ ] .deployignoreファイルの作成
- [ ] rsyncベースデプロイスクリプトの実装
- [ ] 緊急パッチのデプロイ（機密ファイル除外）

### 短期対応（1週間以内）🔴
- [ ] TruffleHog/gitleaksの統合
- [ ] 不要ファイル検出スクリプトの実装
- [ ] GitHub Actions検証ワークフローの追加
- [ ] SBOM生成の自動化

### 中期対応（2週間以内）🟡
- [ ] マニフェストベースデプロイの完全移行
- [ ] パーミッション自動修正の実装
- [ ] デプロイ検証スクリプトの統合
- [ ] Prometheus監視・アラートの設定

### 長期対応（1ヶ月以内）🟢
- [ ] Checkov/Trivy IaCスキャンの統合
- [ ] コンテナイメージビルドへの完全移行
- [ ] コンプライアンス自動レポート生成
- [ ] 定期的なセキュリティ監査の実施

---

**次のステップ**: このレビュー結果をDevOps CoordinatorとCompliance Officerに共有し、実装計画の承認を得てください。
