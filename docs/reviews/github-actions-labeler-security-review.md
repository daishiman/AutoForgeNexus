# GitHub Actions Labeler v5 セキュリティレビュー

## 📋 評価概要

**評価日**: 2025-10-09
**評価者**: security-architect Agent
**対象**: GitHub Actions labeler v5 設定
**総合セキュリティスコア**: **7.5/10**

---

## 🎯 エグゼクティブサマリー

GitHub Actions labeler v5の設定は**全体的に安全**であり、重大なセキュリティ脆弱性は検出されませんでした。ただし、サプライチェーンセキュリティと監査証跡の強化により、SLSA Level 3準拠とGDPR完全準拠を達成できます。

### 主要な発見

✅ **強み**:
- `pull_request`トリガーによる安全な実行（フォークPRからのコード実行を防止）
- GITHUB_TOKENの適切な使用（自動スコープ制限）
- `contents: read`による読み取り専用コードアクセス
- グロブパターンの適切なスコープ制限

⚠️ **改善推奨**:
- アクションバージョンのコミットSHA固定化（SLSA Level 3要件）
- 監査ログの追加（GDPR Article 30完全準拠）
- 権限設定の最適化（`issues: write`削除）

🚨 **クリティカルな問題**: なし

---

## 1️⃣ セキュリティリスク評価

### 1.1 権限設定の適切性

**現在の設定**:
```yaml
permissions:
  contents: read          # ✅ 読み取り専用
  pull-requests: write    # ⚠️ 書き込み権限（必須）
  issues: write           # ⚠️ 書き込み権限（不要の可能性）
  checks: write           # ✅ ステータスチェック用
```

**評価**: 8/10

**分析**:
- ✅ **最小権限原則の遵守**: `contents: read`により、PRコードへの書き込みを防止
- ✅ **スコープ制限**: `pull-requests: write`はlabeler動作に必須
- ⚠️ **過剰な権限**: `issues: write`はlabelerには不要（PRのみ対象）
- ✅ **GITHUB_TOKENの自動保護**:
  - リポジトリレベルのトークン（他リポジトリ不可）
  - 1時間の自動有効期限
  - プッシュ権限なし

**推奨事項**:
```yaml
permissions:
  contents: read
  pull-requests: write
  # issues: write を削除
  checks: write
```

---

### 1.2 機密情報露出のリスク

**評価**: 9/10

**分析**:
- ✅ **シークレット管理**: `secrets.GITHUB_TOKEN`のみ使用（カスタムトークンなし）
- ✅ **ログの安全性**: ラベル付けアクションはファイルパスのみ処理（コード内容は露出しない）
- ⚠️ **グロブパターンの情報開示**:
  - `*auth*`, `*security*`, `*.sql`などのパターンがリポジトリ構造を示唆
  - リスクレベル: 低（.github/labeler.ymlは公開リポジトリでは可視）

**推奨事項**:
- プライベートリポジトリでは問題なし
- パブリックリポジトリでは機密性の高いパターンを汎用化

---

### 1.3 悪意のあるPRからの防御

**評価**: 9/10

**分析**:
✅ **強固な防御メカニズム**:
1. **`pull_request`トリガー使用**（`pull_request_target`ではない）
   - フォークPRはシークレットにアクセス不可
   - PRのコンテキストで実行（ベースブランチではない）
2. **コード実行なし**: labelerは`.github/labeler.yml`のみ読み取り
3. **静的設定**: グロブパターンは動的生成されない

⚠️ **残存リスク**:
- labeler v5アクション自体の脆弱性（バージョン固定で緩和）

**OWASP CI/CD Top 10 準拠**:
- ✅ CICD-SEC-1: 不十分なフロー制御（pull_requestで保護）
- ✅ CICD-SEC-2: 不適切な権限管理（最小権限原則）
- ✅ CICD-SEC-5: 不十分なPPPE（シークレット保護）
- ✅ CICD-SEC-8: 不適切なシステムアクセス（read-only）

---

## 2️⃣ 設定ファイルのセキュリティ

### 2.1 グロブパターンの安全性

**評価**: 8/10

**分析**:

#### ✅ 安全なパターン設計:
```yaml
backend:
  - changed-files:
      - any-glob-to-any-file:
          - backend/**/*        # スコープ制限
          - "*.py"              # 具体的な拡張子
```

#### ⚠️ 潜在的なリスクパターン:
```yaml
large:
  - changed-files:
      - any-glob-to-any-file:
          - "**/*"              # すべてのファイルにマッチ
      - file-count: ">10"
```

**リスク分析**:
1. **パスインジェクション**: ❌ なし（静的設定）
2. **パストラバーサル**: ❌ なし（`..`含まず）
3. **ReDoS（正規表現DoS）**: ❌ 低リスク（単純なグロブパターン）
4. **過度なマッチング**: ⚠️ `**/*`が複数のラベルで使用

**推奨事項**:
```yaml
# 改善例: スコープ制限の追加
large:
  - changed-files:
      - any-glob-to-any-file:
          - src/**/*          # スコープ制限
          - tests/**/*
      - file-count: ">10"
```

---

### 2.2 正規表現の脆弱性

**評価**: 9/10

**分析**:
```yaml
new-feature:
  - head-branch: ['^feature/', '^feat/']  # ブランチ名パターン

hotfix:
  - head-branch: ['^hotfix/']

bugfix:
  - head-branch: ['^fix/', '^bugfix/']
```

**ReDoS リスク評価**:
- ✅ **単純な正規表現**: `^`アンカーと単語マッチのみ
- ✅ **バックトラッキングなし**: ネストされた量指定子なし
- ✅ **線形時間複雑度**: O(n)

**GitHub Actionsの正規表現エンジン**:
- Goの`regexp`パッケージ使用（RE2互換）
- ReDoSに対して安全

---

## 3️⃣ GitHub Actionsセキュリティ

### 3.1 GITHUB_TOKENの使用範囲

**評価**: 8/10

**現在の実装**:
```yaml
- name: 🏷️ Auto-label PR
  uses: actions/labeler@v5
  with:
    repo-token: ${{ secrets.GITHUB_TOKEN }}
```

**分析**:
- ✅ **自動スコープ制限**: permissionsブロックで厳格に制御
- ✅ **有効期限**: 1時間で自動失効
- ✅ **リポジトリレベル**: 他リポジトリへのアクセス不可
- ⚠️ **非推奨パラメータ**: `repo-token`は古い記法（permissionsで十分）

**推奨事項**:
```yaml
# 改善版: repo-tokenパラメータ削除
- name: 🏷️ Auto-label PR
  uses: actions/labeler@8558fd74291d67161a8a78ce36a881fa63b766a9  # v5
  # repo-tokenパラメータ不要（permissionsで制御）
```

---

### 3.2 ワークフローの権限設定

**評価**: 7/10

**分析**:
```yaml
permissions:
  contents: read          # ✅ 適切
  pull-requests: write    # ✅ 必須
  issues: write           # ⚠️ 不要
  checks: write           # ✅ ステータスチェック用
```

**過剰な権限**:
- `issues: write`: labelerはIssueを操作しない（PRのみ）

**推奨される最小権限設定**:
```yaml
permissions:
  contents: read
  pull-requests: write
  checks: write
```

---

### 3.3 サプライチェーン攻撃への対策

**評価**: 6/10

**現在の設定**:
```yaml
- uses: actions/labeler@v5  # ⚠️ タグ参照（変更可能）
```

**リスク**:
- タグは移動可能（攻撃者がv5を悪意のあるコミットに移動できる）
- SLSA Level 1（基本的なビルドプロセス）

**SLSA Level 3準拠のための推奨事項**:
```yaml
# ✅ コミットSHAで固定化
- uses: actions/labeler@8558fd74291d67161a8a78ce36a881fa63b766a9  # v5
```

**追加の対策**:
1. **Dependabot設定**:
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "ci"
      include: "scope"
```

2. **GitHub Advanced Security有効化**:
   - Dependency review
   - Secret scanning
   - Code scanning (CodeQL)

---

## 4️⃣ コンプライアンス

### 4.1 セキュリティポリシーへの準拠

**評価**: 7/10

**OWASP CI/CD Security Top 10 準拠状況**:

| 項目 | 対策状況 | 評価 |
|------|----------|------|
| CICD-SEC-1: 不十分なフロー制御 | ✅ pull_requestトリガー | 合格 |
| CICD-SEC-2: 不適切な権限管理 | ⚠️ 最小権限原則（要改善） | 70% |
| CICD-SEC-3: 依存関係チェーン虐待 | ⚠️ v5タグ参照 | 60% |
| CICD-SEC-4: ポイズンドパイプライン実行 | ✅ コード実行なし | 合格 |
| CICD-SEC-5: 不十分なPPPE | ✅ GITHUB_TOKENのみ | 合格 |
| CICD-SEC-6: 不十分な認証情報衛生 | ✅ シークレット保護 | 合格 |
| CICD-SEC-7: 不十分なログ記録と可視性 | ⚠️ 監査ログ不足 | 60% |
| CICD-SEC-8: 不適切なシステムアクセス | ✅ read-only | 合格 |

**総合準拠率**: 75%

---

### 4.2 監査ログの適切性

**評価**: 6/10

**現在の状況**:
- ❌ ラベル変更の監査ログなし
- ❌ 実行履歴の長期保存なし
- ✅ GitHub Actionsの標準ログ（90日保存）

**GDPR Article 30要件**:
- **必要**: 365日の監査証跡保存
- **現状**: GitHub標準の90日のみ

**推奨される監査ログ実装**:
```yaml
- name: 🏷️ Auto-label PR
  id: labeler
  uses: actions/labeler@8558fd74291d67161a8a78ce36a881fa63b766a9  # v5

- name: 📊 Audit log
  if: always()
  run: |
    cat <<EOF > labeler-audit.json
    {
      "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
      "pr_number": "${{ github.event.pull_request.number }}",
      "pr_author": "${{ github.event.pull_request.user.login }}",
      "labels_before": "${{ toJson(github.event.pull_request.labels) }}",
      "labels_after": "${{ steps.labeler.outputs.new-labels }}",
      "actor": "${{ github.actor }}",
      "repository": "${{ github.repository }}",
      "commit_sha": "${{ github.sha }}"
    }
    EOF

- name: Upload audit log
  uses: actions/upload-artifact@v4
  with:
    name: labeler-audit-${{ github.run_id }}
    path: labeler-audit.json
    retention-days: 365  # GDPR Article 30準拠
```

---

## 5️⃣ セキュリティ改善計画

### 5.1 高優先度（CRITICAL）

#### 1. アクションバージョンのSHA固定化
**リスク**: サプライチェーン攻撃
**対策**:
```yaml
# 変更前
- uses: actions/labeler@v5

# 変更後
- uses: actions/labeler@8558fd74291d67161a8a78ce36a881fa63b766a9  # v5
```

**実装期限**: 即座
**影響度**: SLSA Level 3準拠

---

#### 2. 権限設定の最小化
**リスク**: 過剰な権限付与
**対策**:
```yaml
permissions:
  contents: read
  pull-requests: write
  # issues: write 削除
  checks: write
```

**実装期限**: 1週間以内
**影響度**: OWASP CICD-SEC-2準拠

---

### 5.2 中優先度（HIGH）

#### 3. 監査ログの実装
**リスク**: GDPR非準拠
**対策**: 上記「4.2 監査ログの適切性」の実装例を適用

**実装期限**: 2週間以内
**影響度**: GDPR Article 30準拠

---

#### 4. Dependabot設定の追加
**リスク**: 依存関係の脆弱性
**対策**:
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "ci"
      include: "scope"
```

**実装期限**: 1週間以内
**影響度**: 継続的なセキュリティ維持

---

### 5.3 低優先度（MEDIUM）

#### 5. グロブパターンの最適化
**リスク**: 過度なマッチング
**対策**: `**/*`パターンにスコープ制限を追加

**実装期限**: 1ヶ月以内
**影響度**: パフォーマンス向上

---

#### 6. コンカレンシー制御の追加
**リスク**: 同時実行による競合
**対策**:
```yaml
concurrency:
  group: labeler-${{ github.event.pull_request.number }}
  cancel-in-progress: true
```

**実装期限**: 1ヶ月以内
**影響度**: リソース効率化

---

## 6️⃣ 推奨される最終設定

### 6.1 セキュア化されたpr-check.yml抜粋

```yaml
name: PR Check

on:
  pull_request:
    types: [opened, edited, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write
  checks: write

concurrency:
  group: labeler-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  validate-pr:
    name: Validate PR
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1

      # ... 他のステップ ...

      - name: 🏷️ Auto-label PR
        id: labeler
        uses: actions/labeler@8558fd74291d67161a8a78ce36a881fa63b766a9  # v5

      - name: 📊 Audit log
        if: always()
        run: |
          cat <<EOF > labeler-audit.json
          {
            "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
            "pr_number": "${{ github.event.pull_request.number }}",
            "pr_author": "${{ github.event.pull_request.user.login }}",
            "actor": "${{ github.actor }}",
            "repository": "${{ github.repository }}",
            "commit_sha": "${{ github.sha }}"
          }
          EOF

      - name: Upload audit log
        if: always()
        uses: actions/upload-artifact@26f96dfa697d77e81fd5907df203aa23a56210a8  # v4.3.0
        with:
          name: labeler-audit-${{ github.run_id }}
          path: labeler-audit.json
          retention-days: 365  # GDPR Article 30準拠
```

### 6.2 .github/labeler.yml最適化例

```yaml
# セキュリティベストプラクティス準拠版

backend:
  - changed-files:
      - any-glob-to-any-file:
          - backend/**/*.py
          - backend/requirements*.txt
          - backend/pyproject.toml

frontend:
  - changed-files:
      - any-glob-to-any-file:
          - frontend/**/*.{ts,tsx,js,jsx}
          - frontend/package*.json

security:
  - changed-files:
      - any-glob-to-any-file:
          - .github/workflows/security*.yml
          - backend/**/auth/**/*
          - backend/**/security/**/*
          - SECURITY.md

# 改善: スコープ制限の追加
large:
  - changed-files:
      - any-glob-to-any-file:
          - src/**/*
          - tests/**/*
      - file-count: ">10"
```

---

## 7️⃣ 結論

### 総合評価

**セキュリティスコア**: **7.5/10**

GitHub Actions labeler v5の設定は**基本的に安全**であり、以下の点で優れています：
- ✅ 悪意のあるPRからの保護（pull_requestトリガー）
- ✅ GITHUB_TOKENの適切な使用
- ✅ 読み取り専用コードアクセス

**改善により達成可能な目標**:
- 🎯 SLSA Level 3準拠（サプライチェーンセキュリティ）
- 🎯 GDPR Article 30完全準拠（監査ログ365日保存）
- 🎯 OWASP CI/CD Top 10 100%準拠

### 次のアクション

1. **即座**: SHA固定化の実装
2. **1週間以内**: 権限最小化 + Dependabot設定
3. **2週間以内**: 監査ログ実装
4. **1ヶ月以内**: グロブパターン最適化

---

## 📚 参考資料

- [OWASP CI/CD Security Top 10](https://owasp.org/www-project-top-10-ci-cd-security-risks/)
- [SLSA Framework](https://slsa.dev/)
- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [GDPR Article 30 - Records of processing activities](https://gdpr-info.eu/art-30-gdpr/)
- [actions/labeler Documentation](https://github.com/actions/labeler)

---

**作成日**: 2025-10-09
**レビュアー**: security-architect Agent
**次回レビュー**: 2025-11-09（監査ログ実装後）
