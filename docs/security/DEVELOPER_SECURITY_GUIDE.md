# 開発者向けセキュリティガイド

**対象**: AutoForgeNexus開発チーム全員 **最終更新**: 2025年10月8日
**バージョン**: 1.0 **必読**: ✅ 必須

---

## 🎯 このガイドの目的

このガイドは、AutoForgeNexusプロジェクトにおけるセキュアな開発実践を標準化し、秘密情報漏洩、脆弱性混入、セキュリティインシデントを防止することを目的としています。

**重要な前提**:

- セキュリティは**全員の責任**です
- **予防**は修正よりも100倍効率的です
- セキュリティ問題を発見したら**即座に報告**してください

---

## 📚 目次

1. [秘密情報管理](#1-秘密情報管理)
2. [Git操作のベストプラクティス](#2-git操作のベストプラクティス)
3. [コーディング規約](#3-コーディング規約)
4. [依存関係管理](#4-依存関係管理)
5. [テストとCI/CD](#5-テストとcicd)
6. [インシデント対応](#6-インシデント対応)
7. [チェックリスト](#7-チェックリスト)

---

## 1. 秘密情報管理

### 1.1 秘密情報の定義

以下は**絶対にGitにコミットしてはいけない**情報です：

#### 🔴 高リスク（即座に無効化が必要）

- API キー（OpenAI, Anthropic, Google AI, Mistral, Cohere等）
- データベース認証情報（Turso Auth Token、Redis Password）
- OAuth クライアントシークレット
- JWT シークレットキー
- Cloudflare API Token
- SSH 秘密鍵、GPG秘密鍵

#### 🟡 中リスク（慎重な管理が必要）

- Discord/Slack Webhook URL
- セッションシークレット
- 暗号化キー
- 内部API エンドポイント

#### 🟢 低リスク（公開可能だが注意）

- 開発環境のダミー値
- `.env.example`のプレースホルダー
- 公開APIのエンドポイント

### 1.2 秘密情報の保存場所

#### ✅ 正しい保存場所

| 環境             | 保存場所                               | 例                                                 |
| ---------------- | -------------------------------------- | -------------------------------------------------- |
| **ローカル開発** | `.env`, `.env.local`（.gitignore対象） | `OPENAI_API_KEY=sk-proj-xxx`                       |
| **CI/CD**        | GitHub Secrets                         | `${{ secrets.OPENAI_API_KEY }}`                    |
| **本番環境**     | Cloudflare Workers環境変数             | `wrangler secret put OPENAI_API_KEY`               |
| **ステージング** | Cloudflare Workers環境変数             | `wrangler secret put --env staging OPENAI_API_KEY` |

#### ❌ 間違った保存場所

- ソースコード内にハードコード
- コミットメッセージ
- PR説明文
- GitHub Issues
- Slack/Discord メッセージ
- `.env.production`（コミット対象）

### 1.3 .envファイルの正しい使い方

#### ファイル構成

```bash
AutoForgeNexus/
├── .env                    # ローカル開発用（.gitignore対象）
├── .env.example            # テンプレート（コミット対象）
└── backend/
    ├── .env.local          # バックエンド固有設定（.gitignore対象）
    └── .env.example        # テンプレート（コミット対象）
```

#### .env.example の書き方

```bash
# ✅ 正しい例
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
DATABASE_URL=libsql://your-database-name.turso.io

# ❌ 間違った例（実際の値を記載）
OPENAI_API_KEY=sk-proj-AbCdEf123456789
ANTHROPIC_API_KEY=sk-ant-RealSecretKey
```

#### .env ファイルの作成手順

```bash
# 1. プロジェクトルートで .env.example をコピー
cd /path/to/AutoForgeNexus
cp .env.example .env

# 2. 実際の秘密情報を設定
nano .env  # または vim, vscode等

# 3. 絶対にコミットしない
git status  # .env が Untracked であることを確認
```

### 1.4 GitHub Secrets の使い方

#### Secrets の登録

```bash
# GitHub CLI経由（推奨）
gh secret set OPENAI_API_KEY --repo daishiman/AutoForgeNexus

# またはWeb UI
# Settings → Secrets and variables → Actions → New repository secret
```

#### Secrets の使用

```yaml
# .github/workflows/test.yml
name: Test

env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }} # ✅ 正しい
  # OPENAI_API_KEY: sk-proj-xxx  # ❌ 間違い

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run Tests
        run: pytest tests/
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### 1.5 秘密情報の検証

#### pre-commit フックのセットアップ

```bash
# 初回セットアップ（全開発者必須）
cd /path/to/AutoForgeNexus
./scripts/security/setup-pre-commit.sh

# セットアップ確認
pre-commit run --all-files
```

#### 手動スキャン

```bash
# TruffleHog でGit履歴スキャン
trufflehog git file://. --only-verified

# Gitleaks でスキャン
gitleaks detect --source . --verbose

# ファイルシステムスキャン
trufflehog filesystem . --only-verified
```

### 1.6 秘密情報が漏洩した場合の対応

#### 🚨 即座に実行（5分以内）

1. **秘密情報を無効化**

   ```bash
   # 例: Cloudflare API Token削除
   # Cloudflare Dashboard → My Profile → API Tokens → Delete

   # 例: Discord Webhook削除
   # Discord Server → Settings → Integrations → Webhooks → Delete
   ```

2. **インシデント報告**
   ```bash
   # GitHub Issue作成
   gh issue create --title "🚨 Security Incident: Secret Leaked" \
     --body "検出された秘密情報: [種類]" \
     --label "security,incident"
   ```

#### 🔧 復旧作業（1時間以内）

3. **新しい秘密情報を生成**
4. **GitHub Secrets更新**

   ```bash
   gh secret set OPENAI_API_KEY --repo daishiman/AutoForgeNexus
   ```

5. **ローカル環境更新**
   ```bash
   nano .env  # 新しい秘密情報に更新
   ```

#### 📋 事後対応（24時間以内）

6. **Git履歴から削除（必要な場合のみ）**

   ```bash
   # BFG Repo-Cleanerを使用（推奨）
   brew install bfg
   bfg --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive

   # Force push（チーム全員に通知が必要）
   git push --force --all
   ```

7. **インシデント報告書作成**
   - テンプレート: `docs/security/INCIDENT_RESPONSE_REPORT_TEMPLATE.md`

---

## 2. Git操作のベストプラクティス

### 2.1 コミット前チェックリスト

#### 必須確認事項

```bash
# ✅ ステップ1: ステータス確認
git status

# ✅ ステップ2: 差分確認
git diff
git diff --staged  # ステージング済みファイル

# ✅ ステップ3: 秘密情報スキャン（pre-commit自動実行）
# pre-commit run --all-files  # 手動実行も可能

# ✅ ステップ4: コミット
git commit -m "feat(auth): Clerk認証統合を実装"

# ✅ ステップ5: Push
git push origin feature/auth-integration
```

### 2.2 ブランチ戦略

#### GitFlow の使用

```bash
# ✅ フィーチャーブランチ作成
git checkout -b feature/prompt-optimization

# ✅ 修正ブランチ作成
git checkout -b fix/security-vulnerability

# ❌ main/masterブランチで直接作業しない
git checkout main
git commit -m "..."  # 絶対にNG
```

#### ブランチ命名規則

```
feature/[機能名]     例: feature/auth-integration
fix/[修正内容]       例: fix/sql-injection
hotfix/[緊急修正]    例: hotfix/critical-security-patch
refactor/[対象]      例: refactor/domain-model
docs/[対象]          例: docs/security-guide
```

### 2.3 コミットメッセージ規約

#### Conventional Commits 形式

```bash
# ✅ 正しい例
git commit -m "feat(prompt): AI支援プロンプト作成機能を追加"
git commit -m "fix(security): SQLインジェクション脆弱性を修正"
git commit -m "docs(security): 開発者セキュリティガイドを追加"
git commit -m "refactor(domain): DDD準拠の集約構造に再設計"

# ❌ 間違った例
git commit -m "update"
git commit -m "fix bug"
git commit -m "add new feature"
```

#### コミットタイプ

| タイプ     | 説明               | 例                                       |
| ---------- | ------------------ | ---------------------------------------- |
| `feat`     | 新機能             | `feat(api): プロンプト評価APIを追加`     |
| `fix`      | バグ修正           | `fix(auth): JWT検証エラーを修正`         |
| `docs`     | ドキュメント       | `docs(readme): セットアップ手順を更新`   |
| `refactor` | リファクタリング   | `refactor(domain): Entityクラス再設計`   |
| `test`     | テスト追加         | `test(prompt): プロンプト作成テスト追加` |
| `chore`    | ビルド・設定       | `chore(deps): 依存関係を更新`            |
| `perf`     | パフォーマンス改善 | `perf(api): キャッシュ戦略最適化`        |
| `ci`       | CI/CD              | `ci(github): TruffleHogスキャン追加`     |
| `security` | セキュリティ       | `security(auth): レート制限を実装`       |

---

## 3. コーディング規約

### 3.1 Python (Backend)

#### セキュアコーディング

```python
# ✅ 正しい例: パラメータ化クエリ
from sqlalchemy import select

def get_user_by_email(email: str) -> User:
    query = select(User).where(User.email == email)
    return session.execute(query).scalar_one_or_none()

# ❌ 間違った例: SQLインジェクション脆弱性
def get_user_by_email(email: str) -> User:
    query = f"SELECT * FROM users WHERE email = '{email}'"  # 危険！
    return session.execute(query)
```

#### 入力検証

```python
# ✅ 正しい例: Pydantic検証
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    email: EmailStr  # メールアドレス形式検証
    password: str = Field(..., min_length=8, max_length=128)
    username: str = Field(..., regex=r"^[a-zA-Z0-9_-]+$")

# ❌ 間違った例: 検証なし
def create_user(email: str, password: str, username: str):
    user = User(email=email, password=password, username=username)
    session.add(user)
```

#### パスワードハッシング

```python
# ✅ 正しい例: Bcryptでハッシング
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ❌ 間違った例: 平文保存
def save_password(password: str):
    user.password = password  # 絶対にNG！
```

### 3.2 TypeScript (Frontend)

#### XSS対策

```typescript
// ✅ 正しい例: React自動エスケープ
import React from 'react';

const UserProfile = ({ name }: { name: string }) => {
  return <div>{name}</div>;  // 自動エスケープ
};

// ❌ 間違った例: dangerouslySetInnerHTML
const UserProfile = ({ html }: { html: string }) => {
  return <div dangerouslySetInnerHTML={{ __html: html }} />;  // 危険！
};
```

#### API呼び出しのセキュリティ

```typescript
// ✅ 正しい例: 環境変数からAPIキー取得
const apiKey = process.env.NEXT_PUBLIC_API_KEY;

// ❌ 間違った例: ハードコード
const apiKey = 'sk-proj-AbCdEf123456789'; // 絶対にNG！
```

### 3.3 OWASP Top 10 対策

#### A01:2021 – アクセス制御の不備

```python
# ✅ 正しい例: 権限チェック
from fastapi import Depends, HTTPException

def require_admin(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, admin: User = Depends(require_admin)):
    # 管理者のみ実行可能
    pass
```

#### A02:2021 – 暗号化の失敗

```python
# ✅ 正しい例: 暗号化通信
from fastapi import FastAPI

app = FastAPI()

# Cloudflare Pages/Workers では自動的にHTTPS強制
# ローカル開発ではmkcertでHTTPS証明書を生成
```

#### A03:2021 – インジェクション

```python
# ✅ 正しい例: ORMとパラメータ化
query = select(Prompt).where(Prompt.user_id == user_id)

# ❌ 間違った例: 文字列結合
query = f"SELECT * FROM prompts WHERE user_id = {user_id}"
```

---

## 4. 依存関係管理

### 4.1 依存関係の追加

#### Python (backend)

```bash
# ✅ 正しい手順
cd backend

# 1. 依存関係追加
poetry add fastapi

# 2. 開発依存関係追加
poetry add --group dev pytest

# 3. requirements.txt生成
poetry export -f requirements.txt --output requirements.txt --without-hashes

# 4. セキュリティスキャン
safety check
bandit -r src/
```

#### Node.js (frontend)

```bash
# ✅ 正しい手順
cd frontend

# 1. 依存関係追加
pnpm add next@latest

# 2. 開発依存関係追加
pnpm add -D @types/node

# 3. セキュリティ監査
pnpm audit
pnpm audit --fix  # 自動修正
```

### 4.2 脆弱性スキャン

#### 定期スキャン（週次推奨）

```bash
# Python
cd backend
safety check --json
pip-audit

# Node.js
cd frontend
pnpm audit
npm audit fix

# Docker
trivy image autoforgenexus-backend:latest
```

### 4.3 依存関係更新

```bash
# Python
cd backend
poetry update
poetry show --outdated

# Node.js
cd frontend
pnpm update
pnpm outdated
```

---

## 5. テストとCI/CD

### 5.1 テスト要件

#### カバレッジ目標

| 領域     | 最低カバレッジ | 推奨カバレッジ |
| -------- | -------------- | -------------- |
| Backend  | 80%            | 90%+           |
| Frontend | 75%            | 85%+           |
| E2E      | 50%            | 70%+           |

#### テスト実行

```bash
# Backend
cd backend
pytest tests/ --cov=src --cov-report=html --cov-fail-under=80

# Frontend
cd frontend
pnpm test --coverage

# E2E
cd frontend
pnpm test:e2e
```

### 5.2 CI/CD セキュリティ

#### GitHub Actions ベストプラクティス

```yaml
# ✅ 正しい例
name: Security Scan

on:
  pull_request:
  push:
    branches: [main, develop]

permissions:
  contents: read # 最小権限
  security-events: write

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: TruffleHog Scan
        run: |
          docker run --rm -v "$PWD:/workdir" \
            trufflesecurity/trufflehog:latest \
            git file:///workdir --only-verified --fail

      - name: Dependency Scan
        run: |
          pip install safety
          safety check --json
```

---

## 6. インシデント対応

### 6.1 インシデントの定義

| レベル       | 定義                             | 対応時間         | 例                     |
| ------------ | -------------------------------- | ---------------- | ---------------------- |
| **Critical** | 本番システム停止、大規模情報漏洩 | 即座（15分以内） | API Key漏洩、RCE脆弱性 |
| **High**     | 部分的機能停止、中規模情報漏洩   | 1時間以内        | SQLインジェクション    |
| **Medium**   | パフォーマンス低下、軽微な漏洩   | 1日以内          | 脆弱な依存関係         |
| **Low**      | 軽微な問題、予防的対応           | 1週間以内        | コード品質問題         |

### 6.2 報告手順

#### 秘密情報漏洩を発見した場合

```bash
# 1. GitHub Issue作成
gh issue create \
  --title "🚨 [SECURITY] Secret Leaked: [種類]" \
  --body "検出内容: [詳細]" \
  --label "security,incident,P0" \
  --assignee security-architect

# 2. Discordで即座に通知
# (Webhook URL: CI/CD経由で通知される)

# 3. 秘密情報を即座に無効化
# (各サービスの管理画面で削除/再生成)
```

### 6.3 インシデント対応フロー

```
検出
  ↓
分類（Critical/High/Medium/Low）
  ↓
[Critical/High] → 即座に対応
  ├─ 秘密情報無効化
  ├─ インシデント報告
  ├─ 復旧作業
  └─ 事後レポート作成
  ↓
[Medium/Low] → 計画的対応
  ├─ Issue登録
  ├─ 優先度設定
  └─ スプリント計画
```

---

## 7. チェックリスト

### 7.1 新規開発者オンボーディング

- [ ] このガイドを最初から最後まで読む
- [ ] pre-commitフックをセットアップ
  ```bash
  ./scripts/security/setup-pre-commit.sh
  ```
- [ ] .envファイルを作成（.env.exampleからコピー）
- [ ] GitHub Secretsへのアクセス権限を確認
- [ ] セキュリティトレーニングを受講
- [ ] 秘密情報管理ポリシーに署名

### 7.2 コミット前チェックリスト

- [ ] `git status` で変更内容を確認
- [ ] `git diff` で差分を確認
- [ ] 秘密情報が含まれていないか目視確認
- [ ] pre-commitフックが実行されることを確認
- [ ] テストが全てパス
  ```bash
  pytest tests/  # Backend
  pnpm test      # Frontend
  ```
- [ ] Lintエラーがない
  ```bash
  ruff check src/  # Backend
  pnpm lint        # Frontend
  ```

### 7.3 PR作成前チェックリスト

- [ ] ブランチ名が命名規則に従っている
- [ ] コミットメッセージがConventional Commits形式
- [ ] PR説明文にテスト手順を記載
- [ ] CI/CDが全てパス
- [ ] セキュリティスキャンが全てパス
- [ ] カバレッジが目標値以上
- [ ] レビュアーを2名以上指定

### 7.4 レビュアーチェックリスト

- [ ] コードがセキュアコーディング規約に準拠
- [ ] 入力検証が適切に実装されている
- [ ] 秘密情報がハードコードされていない
- [ ] SQLインジェクション対策が実装されている
- [ ] XSS対策が実装されている
- [ ] 認証・認可が適切に実装されている
- [ ] エラーハンドリングが適切
- [ ] ログに秘密情報が出力されていない

---

## 📚 参考資料

### 公式ドキュメント

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/archive/2023/2023_top25_list.html)

### ツール

- [TruffleHog](https://github.com/trufflesecurity/trufflehog)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [Bandit](https://bandit.readthedocs.io/)
- [Safety](https://pyup.io/safety/)
- [Snyk](https://snyk.io/)

### 社内ドキュメント

- [セキュリティインシデント対応レポート](./INCIDENT_RESPONSE_REPORT_2025-10-08.md)
- [秘密情報管理ポリシー](./SECRET_MANAGEMENT_POLICY.md)（作成予定）
- [インシデント対応プレイブック](./INCIDENT_RESPONSE_PLAYBOOK.md)（作成予定）

---

## 🆘 サポート

### 質問・相談

- **セキュリティ質問**: security@autoforgenexus.dev
- **GitHub Issue**: `security` ラベルで作成
- **Discord**: #security チャンネル

### 緊急連絡先

- **セキュリティインシデント**: security-incident@autoforgenexus.dev
- **オンコール**: +81-XX-XXXX-XXXX

---

## ✍️ ドキュメント管理

| 項目         | 値                       |
| ------------ | ------------------------ |
| 作成日       | 2025年10月8日            |
| 最終更新     | 2025年10月8日            |
| バージョン   | 1.0                      |
| 次回レビュー | 2025年11月8日            |
| 承認者       | security-architect Agent |

---

**このガイドは全開発者必読です。不明点があれば遠慮なく質問してください。**

🤖 Generated with [Claude Code](https://claude.com/claude-code)
