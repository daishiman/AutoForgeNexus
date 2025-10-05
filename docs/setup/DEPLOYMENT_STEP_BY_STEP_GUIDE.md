# 🚀 AutoForgeNexus デプロイメント完全ガイド

**最終更新日**: 2025年10月1日
**対象バージョン**: AutoForgeNexus v1.0.0
**推定所要時間**: 3-4日（外部サービス承認待ち時間含む）

---

## 📖 目次

1. [概要とゴール](#概要とゴール)
2. [事前準備チェックリスト](#事前準備チェックリスト)
3. [Phase A: 外部サービスセットアップ](#phase-a-外部サービスセットアップ)
4. [Phase B: Cloudflare設定](#phase-b-cloudflare設定)
5. [Phase C: GitHub Secrets設定](#phase-c-github-secrets設定)
6. [Phase D: 環境変数ファイル作成](#phase-d-環境変数ファイル作成)
7. [Phase E: ローカル動作確認](#phase-e-ローカル動作確認)
8. [Phase F: Staging デプロイ](#phase-f-staging-デプロイ)
9. [Phase G: Production デプロイ](#phase-g-production-デプロイ)
10. [トラブルシューティング](#トラブルシューティング)

---

## 概要とゴール

### 🎯 このガイドで達成すること

このガイドを完了すると、以下が実現されます:

- ✅ Staging環境: `https://staging.autoforgenexus.com` が稼働
- ✅ Production環境: `https://autoforgenexus.com` が稼働
- ✅ バックエンドAPI: Cloudflare Workersで稼働
- ✅ フロントエンド: Cloudflare Pagesで稼働
- ✅ 認証システム: Clerk統合完了
- ✅ データベース: Turso（分散libSQL）稼働
- ✅ CI/CD: GitHub Actionsで自動デプロイ設定完了

### 📊 全体の流れ（所要時間）

| Phase | 内容 | 所要時間 | 前提条件 |
|-------|------|----------|----------|
| **Phase A** | 外部サービスアカウント作成 | 2-3時間 | クレジットカード（一部サービス） |
| **Phase B** | Cloudflare設定 | 1-2時間 | Cloudflareアカウント |
| **Phase C** | GitHub Secrets設定 | 30分 | GitHub Admin権限 |
| **Phase D** | 環境変数ファイル作成 | 30分 | Phase A完了 |
| **Phase E** | ローカル動作確認 | 1-2時間 | Docker環境 |
| **Phase F** | Staging デプロイ | 1時間 | Phase A-E完了 |
| **Phase G** | Production デプロイ | 30分 | Phase F完了 |

### 💰 必要な費用（月額概算）

| サービス | 無料枠 | 推定コスト（Production） |
|---------|--------|------------------------|
| Clerk | 10,000 MAU | $0-$25/月 |
| Turso | 500行/月 | $0-$29/月 |
| Cloudflare Workers | 100,000リクエスト/日 | $0-$5/月 |
| Cloudflare Pages | 500ビルド/月 | $0 |
| Upstash Redis | 10,000コマンド/日 | $0-$10/月 |
| OpenAI API | 従量課金 | $10-$100/月 |
| Anthropic API | 従量課金 | $10-$100/月 |
| **合計** | - | **$20-$270/月** |

**注**: 開発初期は無料枠内で運用可能

---

## 事前準備チェックリスト

### ✅ 必須ツール

以下のツールがインストールされていることを確認してください:

```bash
# バージョン確認コマンド
git --version        # 2.40+必須
node --version       # 20.0+必須
pnpm --version       # 8.0+必須
docker --version     # 24.0+必須
gh --version         # GitHub CLI 2.0+
```

**すべてのバージョンが要件を満たしていますか？**
- [x] Git 2.40以上
- [x] Node.js 20.0以上
- [x] pnpm 8.0以上
- [x] Docker 24.0以上
- [x] GitHub CLI 2.0以上

**インストールが必要な場合:**

```bash
# macOS（Homebrew）
brew install git node pnpm docker gh

# Node.jsバージョン管理（Volta推奨）
curl https://get.volta.sh | bash
volta install node@22
volta install pnpm@9
```

### 📁 プロジェクトディレクトリ確認

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus

# ディレクトリ構造確認
ls -la

# 期待される出力:
# backend/
# frontend/
# docs/
# .github/
# docker-compose.dev.yml
```

**ディレクトリ構造は正常ですか？**
- [x] backendディレクトリが存在
- [x] frontendディレクトリが存在
- [x] docker-compose.dev.ymlが存在
- [x] .github/workflowsディレクトリが存在

### 🔑 必要なアカウント

以下のアカウントを**事前に作成**してください（メールアドレスのみ）:

- [x] GitHubアカウント（既存のものでOK）
- [X] Gmailアカウント（各サービス登録用、既存でOK）

**次のPhaseで作成するアカウント（今はまだ不要）:**
- Clerk（認証サービス）
- Turso（データベース）
- Cloudflare（デプロイ先）
- OpenAI（LLM）
- Anthropic（LLM）
- Upstash（Redis）

---

## Phase A: 外部サービスセットアップ

このPhaseでは、AutoForgeNexusが依存する6つの外部サービスのアカウント作成とAPI Key取得を行います。

### ⏱️ 所要時間: 2-3時間
### 🎯 達成目標: 全サービスのAPI Key取得完了

---

### A-1: Clerk認証サービス（30-45分）

#### 📌 Clerkとは
- OAuth 2.0ベースの認証・認可サービス
- ユーザー管理、MFA、組織管理機能を提供
- 無料枠: 月間10,000 MAU（月間アクティブユーザー）

#### 🛠️ 実行手順

##### ステップ1: アカウント作成

1. **公式サイトにアクセス**
   ```
   https://clerk.com
   ```

2. **右上の「Sign up」ボタンをクリック**

3. **GitHub連携でサインアップ（推奨）**
   - 「Continue with GitHub」を選択
   - GitHubの認証画面で「Authorize Clerk」をクリック
   - 自動的にClerk Dashboardにリダイレクト

**確認:**
- [ ] Clerk Dashboardが表示されている
- [ ] 画面左上に自分のアイコンが表示されている

##### ステップ2: Applicationプロジェクト作成

1. **Dashboard上部の「Create application」ボタンをクリック**

2. **アプリケーション設定**
   ```
   Application name: AutoForgeNexus
   Sign-in options: 以下をすべてチェック
     ✓ Email address
     ✓ Password
     ✓ Google (オプション)
     ✓ Discord (オプション)
   ```

3. **「Create application」ボタンをクリック**

4. **Frameworkで「Next.js」を選択**
   - 「Continue」をクリック

**確認:**
- [x] Application「AutoForgeNexus」が作成されている
- [x] Dashboard左サイドバーに「AutoForgeNexus」が表示されている

##### ステップ3: Development API Keys取得

1. **左サイドバーから「API Keys」をクリック**

2. **「Development」タブを選択（デフォルト）**

3. **以下の2つのキーをコピー:**

   **① Publishable Key（公開鍵）**
   ```
   形式: pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   - 「Copy」ボタンをクリック
   - テキストエディタに以下の形式で保存:
     ```
     STAGING_CLERK_PUBLIC_KEY=pk_test_xxxxxxxxx...
     ```

   **② Secret Key（秘密鍵）**
   ```
   形式: sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   - 右側の「Show」ボタンをクリック
   - 「Copy」ボタンをクリック
   - テキストエディタに以下の形式で保存:
     ```
     STAGING_CLERK_SECRET_KEY=sk_test_xxxxxxxxx...
     ```

⚠️ **重要**: Secret Keyは二度と表示されないため、必ず安全な場所に保存してください。

**確認:**
- [x] `pk_test_`で始まる公開鍵をコピー済み
- [x] `sk_test_`で始まる秘密鍵をコピー済み
- [x] 両方のキーをテキストファイルに保存済み

##### ステップ4: Production Instance作成

1. **Dashboard画面上部の環境切り替えボタン（「Development」）をクリック**

2. **「Create production instance」を選択**

3. **Production Instance名を入力**
   ```
   Instance name: AutoForgeNexus Production
   ```

4. **「Create」ボタンをクリック**

**確認:**
- [ ] Production Instanceが作成されている
- [ ] 環境切り替えボタンで「Production」が選択可能

##### ステップ5: Production API Keys取得

1. **環境を「Production」に切り替え**

2. **左サイドバーから「API Keys」をクリック**

3. **「Production」タブを選択**

4. **以下の2つのキーをコピー:**

   **① Production Publishable Key**
   ```
   形式: pk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   - テキストファイルに保存:
     ```
     PROD_CLERK_PUBLIC_KEY=pk_live_xxxxxxxxx...
     ```

   **② Production Secret Key**
   ```
   形式: sk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   - テキストファイルに保存:
     ```
     PROD_CLERK_SECRET_KEY=sk_live_xxxxxxxxx...
     ```

**確認:**
- [ ] `pk_live_`で始まる本番公開鍵をコピー済み
- [ ] `sk_live_`で始まる本番秘密鍵をコピー済み

##### ステップ6: Webhook Secret取得（⚠️ 後回し推奨 - Issue #76参照）

⚠️ **重要**: Webhookの設定は**MVP完成後に実装**することを推奨します。基本的な認証機能はWebhookなしで動作します。

**Webhookが必要な機能:**
- ユーザー登録時の自動処理（ウェルカムメール、初期データ作成）
- ユーザー削除時のデータ自動クリーンアップ
- リアルタイムなユーザー情報同期

**Webhookなしでも動作する機能:**
- ✅ ユーザーログイン/ログアウト
- ✅ 認証・認可
- ✅ プロフィール表示
- ✅ 基本的な全機能

**Webhook実装の詳細**: [Issue #76](https://github.com/daishiman/AutoForgeNexus/issues/76) を参照

#### なぜ環境ごとに別々のWebhook Secretが必要？

Webhookは**Staging/Production環境ごとに別々のSecret**が必要です:

| 環境 | Webhook URL | データベース | 用途 |
|------|-------------|-------------|------|
| **Staging** | `api-staging.autoforgenexus.com/webhooks/clerk` | Staging DB | テスト環境 |
| **Production** | `api.autoforgenexus.com/webhooks/clerk` | Production DB | 本番環境 |

**理由**: Stagingでテストした通知がProductionのデータベースに書き込まれるのを防ぐため。

```
❌ 悪い例（Webhook Secretを共有）:
Staging通知 → Production DB書き込み → 本番データ破損！

✅ 良い例（環境別Webhook Secret）:
Staging通知 → Staging DB書き込み
Production通知 → Production DB書き込み
```

#### Webhook設定手順（本格運用前に実施）

<details>
<summary>📖 クリックして詳細手順を表示（今は実施不要）</summary>

##### Staging Webhook設定

1. **環境が「Development」であることを確認**

2. **左サイドバーから「Webhooks」をクリック**

3. **「Add Endpoint」ボタンをクリック**

4. **Webhook設定**
   ```
   Endpoint URL: https://api-staging.autoforgenexus.com/webhooks/clerk
   Subscribe to events: 以下をすべてチェック
     ✓ user.created     # ユーザー登録時
     ✓ user.updated     # ユーザー情報更新時
     ✓ user.deleted     # ユーザー削除時
     ✓ session.created  # セッション作成時
     ✓ session.ended    # セッション終了時
   ```

5. **「Create」ボタンをクリック**

6. **Signing Secretをコピー**
   ```bash
   echo "STAGING_CLERK_WEBHOOK_SECRET=whsec_xxxxxxxxx..." >> ~/clerk-keys.txt
   ```

##### Production Webhook設定

1. **環境を「Production」に切り替え**

2. **上記と同じ手順で設定**
   ```
   Endpoint URL: https://api.autoforgenexus.com/webhooks/clerk
   ```

3. **Signing Secretをコピー**
   ```bash
   echo "PROD_CLERK_WEBHOOK_SECRET=whsec_xxxxxxxxx..." >> ~/clerk-keys.txt
   ```

</details>

**今はこのステップをスキップして次に進んでOKです！**

#### ✅ A-1完了条件

以下の4つのキーが取得できていること:
- [x] `STAGING_CLERK_PUBLIC_KEY`（Development Publishable Key）
- [x] `STAGING_CLERK_SECRET_KEY`（Development Secret Key）
- [ ] `PROD_CLERK_PUBLIC_KEY`（Production Publishable Key）
- [ ] `PROD_CLERK_SECRET_KEY`（Production Secret Key）

**オプション（後回し）:**
- [x] `STAGING_CLERK_WEBHOOK_SECRET`
- [ ] `PROD_CLERK_WEBHOOK_SECRET`

#### 📝 取得したキーの保存場所

一時的にテキストファイルに保存（後でGitHub Secretsに登録←済）:

```bash
# 一時保存ファイル作成
cat > ~/clerk-keys.txt << 'EOF'
# Clerk API Keys
CLERK_DEV_PUBLISHABLE_KEY=pk_test_xxxxxxxxx...
CLERK_DEV_SECRET_KEY=sk_test_xxxxxxxxx...
CLERK_PROD_PUBLISHABLE_KEY=pk_live_xxxxxxxxx...
CLERK_PROD_SECRET_KEY=sk_live_xxxxxxxxx...
CLERK_WEBHOOK_SECRET=whsec_xxxxxxxxx...
EOF

# ファイル権限を制限
chmod 600 ~/clerk-keys.txt
```

---

### A-2: Turso データベース（30-45分）

#### 📌 Tursoとは
- libSQL（SQLiteフォーク）ベースの分散データベース
- エッジロケーションに自動レプリケーション
- 無料枠: 月間500行書き込み、9GBストレージ

#### 🛠️ 実行手順

##### ステップ1: Turso CLIインストール

```bash
# macOS（Homebrew）
brew install tursodatabase/tap/turso

# インストール確認
turso --version
# 期待される出力: turso version v0.xx.x
```

**他のOSの場合:**
```bash
# Linux/WSL
curl -sSfL https://get.tur.so/install.sh | bash

# パスを通す
export PATH="$HOME/.turso:$PATH"
echo 'export PATH="$HOME/.turso:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**確認:**
- [x] `turso --version`でバージョンが表示される
- [x] バージョンがv0.90以上

##### ステップ2: Tursoアカウント認証

```bash
# GitHub経由でログイン（ブラウザが自動で開く）
turso auth login

# 認証成功確認
turso auth whoami

# 期待される出力:
# Logged in as: your-github-username (your-email@example.com)
```

**ブラウザで:**
1. GitHubの認証画面が表示される
2. 「Authorize Turso」をクリック
3. 「Success」画面が表示される

**確認:**
- [x] `turso auth whoami`でGitHubユーザー名が表示される
- [x] エラーが出ていない

##### ステップ3: 利用可能なリージョン確認

```bash
# 利用可能なロケーション一覧表示
turso db locations

# 出力例:
# iad  - Ashburn, Virginia (US)       - 🇺🇸
# nrt  - Tokyo, Japan                 - 🇯🇵  ← 推奨
# fra  - Frankfurt, Germany           - 🇩🇪
# ...
```

**日本向けサービスの推奨リージョン:**
- `nrt` - Tokyo, Japan（最優先）
- `iad` - Virginia, USA（バックアップ）

##### ステップ4: Staging データベース作成

```bash
# Staging DB作成（東京リージョン）
turso db create autoforgenexus-staging --location nrt

# 成功メッセージ例:
# Created database autoforgenexus-staging at group default in nrt (Tokyo, Japan)
# You can start an interactive SQL shell with:
#   turso db shell autoforgenexus-staging
```

**確認:**
- [x] `Created database`メッセージが表示された
- [x] エラーが出ていない

##### ステップ5: Staging データベースURL取得

```bash
# データベースURL取得
turso db show autoforgenexus-staging --url

# 出力例:
# libsql://autoforgenexus-staging-your-org.turso.io
```

**URLをコピーして保存:**
```bash
# 一時保存ファイルに追記
echo "TURSO_STAGING_DATABASE_URL=libsql://autoforgenexus-staging-your-org.turso.io" >> ~/turso-keys.txt
```

**確認:**
- [x] `libsql://`で始まるURLが表示された
- [x] URLをテキストファイルに保存済み

##### ステップ6: Staging 認証トークン生成

```bash
# 認証トークン生成（90日間有効・推奨）
turso db tokens create autoforgenexus-staging --expiration 90d

# 出力例（このトークンは二度と表示されない！）:
# eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3MzMzMTIwMDAs...
```

⚠️ **重要**: このトークンは二度と表示されないため、必ず保存してください！

**トークンをコピーして保存:**
```bash
# トークンを環境変数に一時保存
export TURSO_STAGING_TOKEN="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9..."

# ファイルに保存
echo "TURSO_STAGING_AUTH_TOKEN=$TURSO_STAGING_TOKEN" >> ~/turso-keys.txt
```

**確認:**
- [x] `eyJ`で始まるトークンが表示された
- [x] トークンをテキストファイルに保存済み

##### ステップ7: Production データベース作成

```bash
# Production DB作成（東京リージョン）
turso db create autoforgenexus-production --location nrt

# 成功メッセージ:
# Created database autoforgenexus-production at group default in nrt
```

**確認:**
- [x] Production DBが作成された

##### ステップ8: Production データベースURL取得

```bash
# データベースURL取得
turso db show autoforgenexus-production --url

# 出力をファイルに保存
echo "TURSO_PROD_DATABASE_URL=$(turso db show autoforgenexus-production --url)" >> ~/turso-keys.txt
```

##### ステップ9: Production 認証トークン生成

```bash
# 本番環境用トークン生成（90日間有効）
turso db tokens create autoforgenexus-production --expiration 90d

# トークンをファイルに保存
echo "TURSO_PROD_AUTH_TOKEN=<生成されたトークン>" >> ~/turso-keys.txt
```

##### ステップ10: データベース接続確認

```bash
# Staging DB接続テスト
turso db shell autoforgenexus-staging

# SQLプロンプトで実行:
sqlite> SELECT 'Staging DB Connected!' AS message;
# 出力: Staging DB Connected!

sqlite> .quit

# Production DB接続テスト
turso db shell autoforgenexus-production

sqlite> SELECT 'Production DB Connected!' AS message;
# 出力: Production DB Connected!

sqlite> .quit
```

**確認:**
- [x] Staging DBに接続できた
- [x] Production DBに接続できた
- [x] 両方で`SELECT`文が正常に実行された

#### ✅ A-2完了条件

以下の4つの情報が取得できていること:
- [x] `TURSO_STAGING_DATABASE_URL`
- [x] `TURSO_STAGING_AUTH_TOKEN`
- [x] `TURSO_PROD_DATABASE_URL`
- [x] `TURSO_PROD_AUTH_TOKEN`

---

### A-3: OpenAI API（15-20分）

#### 📌 OpenAI APIとは
- GPT-4等の大規模言語モデルAPIを提供
- AutoForgeNexusのプロンプト生成・評価に使用
- 従量課金制（$0.03/1K tokens）

#### 🛠️ 実行手順

##### ステップ1: アカウント作成

1. **公式サイトにアクセス**
   ```
   https://platform.openai.com
   ```

2. **右上の「Sign up」ボタンをクリック**

3. **Googleアカウントでサインアップ（推奨）**
   - 「Continue with Google」を選択
   - Googleアカウントを選択
   - OpenAIの利用規約に同意

**確認:**
- [x] OpenAI Platform Dashboardが表示されている

##### ステップ2: 課金設定（必須）

1. **左サイドバーから「Billing」→「Payment methods」をクリック**

2. **「Add payment method」ボタンをクリック**

3. **クレジットカード情報を入力**
   ```
   Card number: xxxx-xxxx-xxxx-xxxx
   Expiry date: MM/YY
   CVC: xxx
   ```

4. **「Add card」ボタンをクリック**

5. **使用制限を設定（推奨）**
   - 「Billing」→「Usage limits」をクリック
   - 「Monthly budget」を設定:
     ```
     Hard limit: $50/月（推奨）
     Soft limit: $30/月（アラート通知）
     ```

**確認:**
- [x] クレジットカードが登録されている
- [x] 使用制限が設定されている

##### ステップ3: API Key作成

1. **左サイドバーから「API keys」をクリック**

2. **「Create new secret key」ボタンをクリック**

3. **API Key設定**
   ```
   Name: AutoForgeNexus Staging
   Permissions: All (デフォルト)
   ```

4. **「Create secret key」ボタンをクリック**

5. **API Keyをコピー**
   ```
   形式: sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   - 「Copy」ボタンをクリック
   - ファイルに保存:
     ```bash
     echo "OPENAI_STAGING_API_KEY=sk-proj-xxxxxxxxx..." >> ~/openai-keys.txt
     ```

⚠️ **重要**: API Keyは二度と表示されないため、必ず保存してください。

##### ステップ4: Production用API Key作成

1. **再度「Create new secret key」ボタンをクリック**

2. **API Key設定**
   ```
   Name: AutoForgeNexus Production
   Permissions: All
   ```

3. **API Keyをコピーして保存**
   ```bash
   echo "OPENAI_PROD_API_KEY=sk-proj-xxxxxxxxx..." >> ~/openai-keys.txt
   ```

##### ステップ5: API接続確認

```bash
# curlでAPI接続テスト
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer <YOUR_API_KEY>" \
  | jq '.data[] | select(.id == "gpt-4") | .id'

# 期待される出力:
# "gpt-4"
```

**確認:**
- [x] `gpt-4`が表示された
- [x] エラーが出ていない

#### ✅ A-3完了条件

以下の2つのAPI Keyが取得できていること:
- [x] `OPENAI_STAGING_API_KEY`
- [x] `OPENAI_PROD_API_KEY`
- [x] 課金設定が完了している
- [x] 使用制限が設定されている

---

### A-4: Anthropic Claude API（15-20分）

#### 📌 Anthropic APIとは
- Claude 3.5 Sonnetの大規模言語モデルAPIを提供
- AutoForgeNexusの高度な推論タスクに使用
- 従量課金制（$3/MTok input, $15/MTok output）

#### 🛠️ 実行手順

##### ステップ1: アカウント作成

1. **公式サイトにアクセス**
   ```
   https://console.anthropic.com
   ```

2. **「Sign Up」ボタンをクリック**

3. **メールアドレスでサインアップ**
   ```
   Email: your-email@example.com
   Password: ********（強力なパスワード）
   ```

4. **メール認証**
   - 登録したメールアドレスに確認メールが届く
   - 「Verify Email」リンクをクリック

**確認:**
- [x] Anthropic Console Dashboardが表示されている

##### ステップ2: 課金設定

1. **「Settings」→「Billing」をクリック**

2. **「Add payment method」ボタンをクリック**

3. **クレジットカード情報を入力**

4. **初回クレジット購入（必須）**
   ```
   Amount: $10（最低金額）
   ```

5. **「Purchase」ボタンをクリック**

**確認:**
- [x] クレジットカードが登録されている
- [x] $10のクレジットが購入されている

##### ステップ3: API Key作成

1. **「API Keys」セクションに移動**

2. **「Create Key」ボタンをクリック**

3. **API Key設定**
   ```
   Name: AutoForgeNexus Staging
   ```

4. **「Create」ボタンをクリック**

5. **API Keyをコピー**
   ```
   形式: sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   - ファイルに保存:
     ```bash
     echo "ANTHROPIC_STAGING_API_KEY=sk-ant-xxxxxxxxx..." >> ~/anthropic-keys.txt
     ```

##### ステップ4: Production用API Key作成

1. **再度「Create Key」ボタンをクリック**

2. **API Key設定**
   ```
   Name: AutoForgeNexus Production
   ```

3. **API Keyをコピーして保存**
   ```bash
   echo "ANTHROPIC_PROD_API_KEY=sk-ant-xxxxxxxxx..." >> ~/anthropic-keys.txt
   ```

##### ステップ5: API接続確認

```bash
# curlでAPI接続テスト
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: <YOUR_API_KEY>" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "Hello"}]
  }' | jq '.content[0].text'

# 期待される出力:
# "Hello! How can I assist you today?"
```

**確認:**
- [x] Claudeからの応答が表示された
- [x] エラーが出ていない

#### ✅ A-4完了条件

以下の2つのAPI Keyが取得できていること:
- [x] `ANTHROPIC_STAGING_API_KEY`
- [x] `ANTHROPIC_PROD_API_KEY`
- [x] 課金設定が完了している
- [x] 初回クレジット購入済み

---

### A-5: Upstash Redis（15-20分）

#### 📌 Upstash Redisとは
- サーバーレス Redis（キャッシュ・セッション管理）
- グローバルレプリケーション対応
- 無料枠: 10,000コマンド/日

#### 🛠️ 実行手順

##### ステップ1: アカウント作成

1. **公式サイトにアクセス**
   ```
   https://upstash.com
   ```

2. **「Sign Up」ボタンをクリック**

3. **GitHubアカウントでサインアップ（推奨）**
   - 「Continue with GitHub」を選択
   - GitHubの認証画面で「Authorize Upstash」をクリック

**確認:**
- [ ] Upstash Console Dashboardが表示されている

##### ステップ2: Staging Redis作成

1. **「Create Database」ボタンをクリック**

2. **Redis設定**
   ```
   Name: autoforgenexus-staging
   Type: Regional（無料枠）
   Region: Asia Pacific (Tokyo)
   Primary Region: ap-northeast-1
   ```

3. **「Create」ボタンをクリック**

4. **作成完了を待つ（30秒程度）**

**確認:**
- [ ] Redis「autoforgenexus-staging」が作成されている
- [ ] Statusが「Active」になっている

##### ステップ3: Staging Redis接続情報取得

1. **作成したRedisをクリック**

2. **「Details」タブを開く**

3. **以下の情報をコピー:**

   **① Endpoint**
   ```
   形式: usable-xxxxx-12345.upstash.io
   Port: 6379
   ```

   **② Password**
   ```
   形式: AXjE...（ランダム文字列）
   ```

4. **ファイルに保存:**
   ```bash
   cat >> ~/redis-keys.txt << 'EOF'
   REDIS_STAGING_HOST=usable-xxxxx-12345.upstash.io
   REDIS_STAGING_PORT=6379
   REDIS_STAGING_PASSWORD=AXjE...
   EOF
   ```

**確認:**
- [x] Endpointをコピー済み
- [x] Passwordをコピー済み
- [x] ファイルに保存済み

##### ステップ4: Production Redis作成

1. **再度「Create Database」ボタンをクリック**

2. **Redis設定**
   ```
   Name: autoforgenexus-production
   Type: Regional（無料枠）
   Region: Asia Pacific (Tokyo)
   ```

3. **接続情報をコピーして保存:**
   ```bash
   cat >> ~/redis-keys.txt << 'EOF'
   REDIS_PROD_HOST=another-xxxxx-67890.upstash.io
   REDIS_PROD_PORT=6379
   REDIS_PROD_PASSWORD=BYkF...
   EOF
   ```

##### ステップ5: Redis接続確認

⚠️ **重要**: Upstash Redisには2つのアクセス方法があります。

#### 方法A: REST API接続（推奨 - サーバーレス環境向け）

```bash
# Staging Redis REST API接続テスト
curl https://your-redis-instance.upstash.io/ping \
  -H "Authorization: Bearer YOUR_REDIS_REST_TOKEN"

# 期待される出力:
# {"result":"PONG"}

# SET/GETテスト
curl https://your-redis-instance.upstash.io/set/test:key \
  -H "Authorization: Bearer YOUR_REDIS_REST_TOKEN" \
  -d '"test-value"'

# 期待される出力:
# {"result":"OK"}

curl https://your-redis-instance.upstash.io/get/test:key \
  -H "Authorization: Bearer YOUR_REDIS_REST_TOKEN"

# 期待される出力:
# {"result":"test-value"}
```

**使用するトークン:**
- Upstash Dashboard → Details → **REST Token**（`AURsAAInc...`で始まる）
- ⚠️ これは**Password**とは異なります

#### 方法B: Redis Protocol接続（オプション - ローカル開発向け）

```bash
# redis-cliインストール（macOS）
brew install redis

# Staging Redis接続テスト（TLS必須）
redis-cli -h lucky-marten-17516.upstash.io \
  -p 6379 \
  -a "パスワード" \
  --tls \
  PING

# 期待される出力:
# PONG
```

**使用するパスワード:**
- Upstash Dashboard → Details → **Password**（マスクされている `••••••••`）
- ⚠️ これは**REST Token**とは異なります

#### 推奨事項

- ✅ **Cloudflare Workers/Pages**: REST API（方法A）を使用
- ✅ **FastAPI/Python**: REST APIまたはRedis Protocol（両方対応）
- ✅ **ローカル開発**: Redis Protocol（方法B）が便利

**確認:**
- [x] REST APIで接続確認完了（`{"result":"PONG"}`が返る）
- [x] Redis Protocolで接続確認完了（オプション）

#### ✅ A-5完了条件

以下の接続情報が取得できていること:

**必須（REST API用）:**
- [x] `REDIS_STAGING_REST_URL`（例: https://lucky-marten-17516.upstash.io）
- [x] `REDIS_STAGING_REST_TOKEN`（例: AURsAAInc...）
- [ ] `REDIS_PROD_REST_URL`（Staging環境と同じ値を使用）
- [ ] `REDIS_PROD_REST_TOKEN`（Staging環境と同じ値を使用）

**オプション（Redis Protocol用）:**
- [x] `REDIS_STAGING_HOST`, `REDIS_STAGING_PORT`, `REDIS_STAGING_PASSWORD`
- [ ] `REDIS_PROD_HOST`, `REDIS_PROD_PORT`, `REDIS_PROD_PASSWORD`

**動作確認:**
- [x] REST APIで接続確認完了（`{"result":"PONG"}`が返る）

**⚠️ 重要**: Issue #77の方針に従い、本番環境もStaging環境のRedisインスタンスを併用します

---

### A-6: LangFuse 観測性（オプション・15分）

#### 📌 LangFuseとは
- LLM実行の観測・トレーシングプラットフォーム
- プロンプト評価、コスト追跡、デバッグに使用
- 無料枠: 月間50,000トレース

#### 🛠️ 実行手順

##### ステップ1: アカウント作成

1. **公式サイトにアクセス**
   ```
   https://cloud.langfuse.com
   ```

2. **「Sign Up」ボタンをクリック**

3. **GitHubアカウントでサインアップ**

**確認:**
- [ ] LangFuse Dashboardが表示されている

##### ステップ2: Project作成

1. **「Create Project」ボタンをクリック**

2. **Project設定**
   ```
   Name: AutoForgeNexus Staging
   ```

3. **「Create」ボタンをクリック**

##### ステップ3: API Keys取得

1. **「Settings」→「API Keys」をクリック**

2. **「Create new API key」ボタンをクリック**

3. **以下の2つのキーをコピー:**
   ```
   Public Key: pk-lf-xxxxxxxxx...
   Secret Key: sk-lf-xxxxxxxxx...
   ```

4. **ファイルに保存:**
   ```bash
   cat >> ~/langfuse-keys.txt << 'EOF'
   LANGFUSE_STAGING_PUBLIC_KEY=pk-lf-xxxxxxxxx...
   LANGFUSE_STAGING_SECRET_KEY=sk-lf-xxxxxxxxx...
   EOF
   ```

##### ステップ4: Production Project作成

1. **再度「Create Project」ボタンをクリック**

2. **Project設定**
   ```
   Name: AutoForgeNexus Production
   ```

3. **API Keysをコピーして保存**

**確認:**
- [ ] Staging/Production両方のAPI Keysを取得済み

#### ✅ A-6完了条件

以下のAPI Keyが取得できていること（オプション）:
- [x] `LANGFUSE_STAGING_PUBLIC_KEY`, `LANGFUSE_STAGING_SECRET_KEY`
- [ x `LANGFUSE_PROD_PUBLIC_KEY`, `LANGFUSE_PROD_SECRET_KEY`

---

## ✅ Phase A 完了確認

すべてのAPI Keyが取得できましたか？

### 必須サービス（6個）
- [ ] Clerk（Development + Production）
- [x] Turso（Staging + Production）
- [x] OpenAI（Staging + Production）
- [x] Anthropic（Staging + Production）
- [ ] Upstash Redis（Staging + Production）

### オプションサービス
- [x] LangFuse（Staging + Production）

### 取得した情報の整理

すべてのキーを1つのファイルにまとめます:

```bash
# すべてのキーを統合
cat ~/clerk-keys.txt ~/turso-keys.txt ~/openai-keys.txt ~/anthropic-keys.txt ~/redis-keys.txt ~/langfuse-keys.txt > ~/autoforge-all-keys.txt

# ファイル権限を厳格化
chmod 600 ~/autoforge-all-keys.txt

# 内容確認
cat ~/autoforge-all-keys.txt

# バックアップ作成（推奨）
cp ~/autoforge-all-keys.txt ~/Desktop/autoforge-keys-backup-$(date +%Y%m%d).txt
```

**次のPhase Bに進む前に:**
- [ ] すべてのAPI Keyがファイルに保存されている
- [ ] バックアップを作成済み
- [ ] ファイル権限が600になっている

---

## Phase B: Cloudflare設定

このPhaseでは、バックエンド（Workers）とフロントエンド（Pages）のデプロイ先となるCloudflareの設定を行います。

### ⏱️ 所要時間: 1-2時間
### 🎯 達成目標: Cloudflare Workers/Pages設定完了

---

### B-1: Cloudflareアカウント作成（10分）

#### 🛠️ 実行手順

##### ステップ1: アカウント作成

1. **公式サイトにアクセス**
   ```
   https://dash.cloudflare.com/sign-up
   ```

2. **メールアドレスとパスワードを入力**
   ```
   Email: your-email@example.com
   Password: ********（強力なパスワード）
   ```

3. **「Create Account」ボタンをクリック**

4. **メール認証**
   - 登録したメールアドレスに確認メールが届く
   - 「Verify email address」リンクをクリック

**確認:**
- [x] Cloudflare Dashboardが表示されている
- [x] 画面左上に「Cloudflare」ロゴが表示されている

##### ステップ2: プランの選択

1. **「Workers & Pages」プランを選択**
   - 左サイドバーから「Workers & Pages」をクリック
   - 「Free」プラン（$0/月）を選択

**確認:**
- [x] Workers & Pages Dashboardが表示されている

---

### B-2: Cloudflare API Token取得（10分）

#### 🛠️ 実行手順

##### ステップ1: API Token作成

1. **右上のプロフィールアイコンをクリック**

2. **「My Profile」を選択**

3. **左サイドバーから「API Tokens」をクリック**

4. **「Create Token」ボタンをクリック**

5. **テンプレート選択**
   - 「Edit Cloudflare Workers」テンプレートを選択
   - 「Use template」ボタンをクリック

##### ステップ2: Token権限設定

1. **Token名を入力**
   ```
   Token name: AutoForgeNexus-Deploy
   ```

2. **Permissions設定（確認のみ、変更不要）**
   ```
   Account → Cloudflare Workers Scripts → Edit
   Account → Cloudflare Pages → Edit
   Account → Account Settings → Read
   ```

3. **Account Resources**
   ```
   Include: All accounts
   ```

4. **「Continue to summary」ボタンをクリック**

##### ステップ3: Token発行

1. **設定内容を確認**

2. **「Create Token」ボタンをクリック**

3. **API Tokenをコピー**
   ```
   形式: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   - 「Copy」ボタンをクリック
   - ファイルに保存:
     ```bash
     echo "CLOUDFLARE_API_TOKEN=xxxxxxxxx..." >> ~/cloudflare-keys.txt
     ```

⚠️ **重要**: このTokenは二度と表示されないため、必ず保存してください。

**確認:**
- [x] API Tokenをコピー済み
- [x] ファイルに保存済み

---

### B-3: Cloudflare Account ID取得（5分）

#### 🛠️ 実行手順

##### ステップ1: Account ID確認

1. **Cloudflare Dashboard左サイドバーから「Workers & Pages」をクリック**

2. **画面右側の「Account ID」をコピー**
   ```
   形式: 32文字の16進数（例: 1234567890abcdef1234567890abcdef）
   ```

3. **ファイルに保存:**
   ```bash
   echo "CLOUDFLARE_ACCOUNT_ID=1234567890abcdef..." >> ~/cloudflare-keys.txt
   ```

**確認:**
- [x] Account IDをコピー済み
- [x] ファイルに保存済み

---

### B-4: バックエンド用 wrangler.toml作成（20分）

#### 🛠️ 実行手順

##### ステップ1: wrangler.toml作成

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/backend

# wrangler.toml作成
cat > wrangler.toml << 'EOF'
name = "autoforgenexus-backend"
main = "src/main.py"
compatibility_date = "2025-09-30"

# ==========================================
# Staging Environment
# ==========================================
[env.staging]
name = "autoforgenexus-backend-staging"
workers_dev = true  # 開発環境でのみ有効化
# route設定はドメイン取得後に有効化
# route = { pattern = "api-staging.autoforgenexus.com/*", zone_name = "autoforgenexus.com" }

[env.staging.vars]
APP_ENV = "staging"
APP_NAME = "AutoForgeNexus-Backend-Staging"
DEBUG = "false"
LOG_LEVEL = "INFO"
CORS_ORIGINS = "*"  # 開発環境では全許可

[env.staging.observability]
enabled = true
head_sampling_rate = 1.0  # 100%サンプリング（詳細トレース）

# ==========================================
# Production Environment
# ==========================================
[env.production]
name = "autoforgenexus-backend-production"
workers_dev = false  # 本番環境では無効化
# route設定はドメイン取得後に有効化
# route = { pattern = "api.autoforgenexus.com/*", zone_name = "autoforgenexus.com" }

[env.production.vars]
APP_ENV = "production"
APP_NAME = "AutoForgeNexus-Backend-Production"
DEBUG = "false"
LOG_LEVEL = "WARNING"
CORS_ORIGINS = "https://autoforgenexus.com,https://staging.autoforgenexus.com"

[env.production.observability]
enabled = true
head_sampling_rate = 0.1  # 10%サンプリング（コスト最適化）

# ==========================================
# Build Configuration (Python Workers用)
# ==========================================
[build]
command = ""  # Python Workersは自動ビルド

# ==========================================
# Secrets (GitHub Actionsで設定)
# ==========================================
#
# 【バックエンド認証】
# CLERK_SECRET_KEY
#
# 【LLMプロバイダー】
# OPENAI_API_KEY
# ANTHROPIC_API_KEY
#
# 【データベース】
# TURSO_DATABASE_URL
# TURSO_AUTH_TOKEN
#
# 【Redis（REST API用）】
# REDIS_REST_URL       # 例: https://lucky-marten-17516.upstash.io
# REDIS_REST_TOKEN     # 例: AURsAAInc...
#
# 【観測性（オプション）】
# LANGFUSE_PUBLIC_KEY
# LANGFUSE_SECRET_KEY
EOF
```

**⚠️ 重要な注意点:**

1. **route設定について**
   - `route`設定はコメントアウトしています
   - 独自ドメイン（autoforgenexus.com）を取得・設定した後に有効化してください
   - ドメイン未取得の場合、`https://<worker-name>.<account-subdomain>.workers.dev`形式のURLが自動発行されます

2. **Python Workers固有の設定**
   - `build.command`は空文字列（Cloudflare Workersが自動処理）
   - `requirements.txt`の依存関係は自動的にバンドルされます
   - `build.upload.format`設定は不要（Python Workers専用設定）

3. **環境別observability設定**
   - **Staging**: 100%サンプリング（詳細なトレース取得）
   - **Production**: 10%サンプリング（コスト最適化）

4. **Secrets管理**
   - すべての秘密情報はGitHub Secretsで管理
   - `REDIS_REST_URL`と`REDIS_REST_TOKEN`が必須（Issue #77参照）
   - wrangler.tomlにはSecrets名のみを記載（値は含めない）

**確認チェックリスト（更新）:**
- [x] `backend/wrangler.toml`が作成された
- [x] ファイル内容を確認（`cat wrangler.toml`）
- [x] route設定がコメントアウトされていることを確認
- [x] Secrets一覧にREDIS_REST_URL/TOKENが含まれていることを確認

##### ステップ2: Wrangler CLIインストール

```bash
# Wrangler CLIインストール（グローバル）
pnpm add -g wrangler@latest

# インストール確認
wrangler --version
# 期待される出力: wrangler 3.xx.x
```

**確認:**
- [x] `wrangler --version`でバージョンが表示される
- [x] バージョンが3.x以上

##### ステップ3: Wrangler認証

```bash
# Cloudflareアカウントにログイン
wrangler login

# ブラウザが自動で開く
# 「Allow Wrangler」ボタンをクリック
# 「Success」画面が表示される

# 認証確認
wrangler whoami

# 期待される出力:
# You are logged in with an OAuth Token, associated with the email 'your-email@example.com'.
```

**確認:**
- [x] `wrangler whoami`でメールアドレスが表示される
- [x] エラーが出ていない

---

### B-5: フロントエンド用 Pages設定（20分）

#### 🛠️ 実行手順

##### ステップ1: Pagesプロジェクト作成

1. **Cloudflare Dashboard → 「Workers & Pages」をクリック**

2. **「Create」→「Pages」→「Connect to Git」を選択**

3. **GitHubリポジトリを接続**
   - 「Connect GitHub」ボタンをクリック
   - GitHubの認証画面で「Authorize Cloudflare Pages」をクリック
   - リポジトリ「AutoForgeNexus」を選択

4. **ビルド設定**
   ```
   Project name: autoforgenexus-frontend
   Production branch: main
   Framework preset: Next.js
   Build command: pnpm build
   Build output directory: .next
   Root directory: frontend
   ```

5. **環境変数設定（後で追加するため、今はスキップ）**

6. **「Save and Deploy」ボタンをクリック**

7. **初回デプロイを待つ（5-10分）**

**確認:**
- [ ] Pagesプロジェクト「autoforgenexus-frontend」が作成されている
- [ ] 初回デプロイが成功している（緑色のチェックマーク）

##### ステップ2: カスタムドメイン設定（オプション）

⚠️ **注意**: 独自ドメイン（autoforgenexus.com）を持っている場合のみ実行

1. **Pagesプロジェクト「autoforgenexus-frontend」をクリック**

2. **「Custom domains」タブをクリック**

3. **「Set up a custom domain」ボタンをクリック**

4. **ドメイン設定**
   ```
   Staging: staging.autoforgenexus.com
   Production: autoforgenexus.com
   ```

5. **DNS設定の指示に従う（Cloudflare DNSの場合は自動）**

**確認:**
- [ ] カスタムドメインが追加されている
- [ ] SSL証明書が自動発行されている

---

## ✅ Phase B 完了確認

以下の設定が完了しましたか？

### Cloudflare基本設定
- [ ] Cloudflareアカウント作成済み
- [ ] API Token取得済み（`CLOUDFLARE_API_TOKEN`）
- [ ] Account ID取得済み（`CLOUDFLARE_ACCOUNT_ID`）

### Workers設定
- [ ] `backend/wrangler.toml`作成済み
- [ ] Wrangler CLIインストール済み
- [ ] Wrangler認証完了（`wrangler whoami`成功）

### Pages設定
- [ ] Pagesプロジェクト「autoforgenexus-frontend」作成済み
- [ ] GitHubリポジトリ接続済み
- [ ] 初回デプロイ成功

### 次のPhase Cに進む前に
- [ ] すべてのCloudflare情報がファイルに保存されている
- [ ] wrangler.tomlが正しく作成されている

---

## Phase C: GitHub Secrets設定

このPhaseでは、Phase Aで取得したすべてのAPI KeyをGitHub Secretsに登録し、CI/CD自動デプロイの準備を行います。

### ⏱️ 所要時間: 30分
### 🎯 達成目標: GitHub Secrets登録完了、CI/CD準備完了

---

### C-1: GitHub CLI認証確認（5分）

#### 🛠️ 実行手順

##### ステップ1: GitHub CLI認証状態確認

```bash
# GitHub CLI認証確認
gh auth status

# 期待される出力:
# ✓ Logged in to github.com as YOUR_USERNAME
# ✓ Git operations for github.com configured to use ssh protocol.
# ✓ Token: *******************
```

**未認証の場合:**
```bash
# GitHub CLIでログイン
gh auth login

# 対話プロンプトで選択:
# ? What account do you want to log into? → GitHub.com
# ? What is your preferred protocol for Git operations? → HTTPS
# ? Authenticate Git with your GitHub credentials? → Yes
# ? How would you like to authenticate GitHub CLI? → Login with a web browser
```

**確認:**
- [x] `gh auth status`でログイン済み状態が表示される
- [x] リポジトリへのアクセス権限がある

##### ステップ2: リポジトリAdmin権限確認

```bash
# リポジトリ情報確認
gh repo view daishiman/AutoForgeNexus --json permissions

# 期待される出力（permissions.admin: true）:
# {
#   "permissions": {
#     "admin": true,
#     "maintain": true,
#     "push": true,
#     "triage": true,
#     "pull": true
#   }
# }
```

**確認:**
- [x] `permissions.admin: true`が表示される
- [x] Secrets登録権限がある

---

### C-2: Staging環境Secrets登録（10分）

#### 🛠️ 実行手順

##### ステップ1: Clerk Staging Secrets登録

```bash
# Staging Clerk Secrets登録
gh secret set STAGING_CLERK_PUBLIC_KEY \
  --body "$(cat ~/clerk-keys.txt | grep CLERK_DEV_PUBLISHABLE_KEY | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

gh secret set STAGING_CLERK_SECRET_KEY \
  --body "$(cat ~/clerk-keys.txt | grep CLERK_DEV_SECRET_KEY | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# 登録確認
gh secret list --repo daishiman/AutoForgeNexus | grep CLERK
```

**確認:**
- [x] `STAGING_CLERK_PUBLIC_KEY`が登録されている
- [x] `STAGING_CLERK_SECRET_KEY`が登録されている

##### ステップ2: Turso Staging Secrets登録

```bash
# Staging Turso Secrets登録
gh secret set TURSO_STAGING_DATABASE_URL \
  --body "$(cat ~/turso-keys.txt | grep TURSO_STAGING_DATABASE_URL | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

gh secret set TURSO_STAGING_AUTH_TOKEN \
  --body "$(cat ~/turso-keys.txt | grep TURSO_STAGING_AUTH_TOKEN | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# 登録確認
gh secret list --repo daishiman/AutoForgeNexus | grep TURSO_STAGING
```

**確認:**
- [x] `TURSO_STAGING_DATABASE_URL`が登録されている
- [x] `TURSO_STAGING_AUTH_TOKEN`が登録されている

##### ステップ3: LLM Staging Secrets登録

```bash
# OpenAI Staging Secret
gh secret set OPENAI_STAGING_API_KEY \
  --body "$(cat ~/openai-keys.txt | grep OPENAI_STAGING_API_KEY | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# Anthropic Staging Secret
gh secret set ANTHROPIC_STAGING_API_KEY \
  --body "$(cat ~/anthropic-keys.txt | grep ANTHROPIC_STAGING_API_KEY | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# 登録確認
gh secret list --repo daishiman/AutoForgeNexus | grep -E "OPENAI|ANTHROPIC"
```

**確認:**
- [x] `OPENAI_STAGING_API_KEY`が登録されている
- [x] `ANTHROPIC_STAGING_API_KEY`が登録されている

##### ステップ4: Redis Staging Secrets登録

```bash
# Redis REST API Secrets（Staging）
gh secret set REDIS_STAGING_REST_URL \
  --body "$(cat ~/redis-keys.txt | grep REDIS_STAGING_REST_URL | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

gh secret set REDIS_STAGING_REST_TOKEN \
  --body "$(cat ~/redis-keys.txt | grep REDIS_STAGING_REST_TOKEN | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# 登録確認
gh secret list --repo daishiman/AutoForgeNexus | grep REDIS_STAGING
```

**確認:**
- [x] `REDIS_STAGING_REST_URL`が登録されている
- [x] `REDIS_STAGING_REST_TOKEN`が登録されている

##### ステップ5: LangFuse Staging Secrets登録（オプション）

```bash
# LangFuse Staging Secrets
gh secret set LANGFUSE_STAGING_PUBLIC_KEY \
  --body "$(cat ~/langfuse-keys.txt | grep LANGFUSE_STAGING_PUBLIC_KEY | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

gh secret set LANGFUSE_STAGING_SECRET_KEY \
  --body "$(cat ~/langfuse-keys.txt | grep LANGFUSE_STAGING_SECRET_KEY | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# 登録確認
gh secret list --repo daishiman/AutoForgeNexus | grep LANGFUSE_STAGING
```

**確認:**
- [x] `LANGFUSE_STAGING_PUBLIC_KEY`が登録されている（オプション）
- [x] `LANGFUSE_STAGING_SECRET_KEY`が登録されている（オプション）

---

### C-3: Production環境Secrets登録（10分）

#### 🛠️ 実行手順

##### ステップ1: Clerk Production Secrets登録

```bash
# Production Clerk Secrets登録
gh secret set PROD_CLERK_PUBLIC_KEY \
  --body "$(cat ~/clerk-keys.txt | grep CLERK_PROD_PUBLISHABLE_KEY | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

gh secret set PROD_CLERK_SECRET_KEY \
  --body "$(cat ~/clerk-keys.txt | grep CLERK_PROD_SECRET_KEY | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# 登録確認
gh secret list --repo daishiman/AutoForgeNexus | grep PROD_CLERK
```

**確認:**
- [x] `PROD_CLERK_PUBLIC_KEY`が登録されている
- [x] `PROD_CLERK_SECRET_KEY`が登録されている

##### ステップ2: Turso Production Secrets登録

```bash
# Production Turso Secrets登録
gh secret set TURSO_PROD_DATABASE_URL \
  --body "$(cat ~/turso-keys.txt | grep TURSO_PROD_DATABASE_URL | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

gh secret set TURSO_PROD_AUTH_TOKEN \
  --body "$(cat ~/turso-keys.txt | grep TURSO_PROD_AUTH_TOKEN | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# 登録確認
gh secret list --repo daishiman/AutoForgeNexus | grep TURSO_PROD
```

**確認:**
- [x] `TURSO_PROD_DATABASE_URL`が登録されている
- [x] `TURSO_PROD_AUTH_TOKEN`が登録されている

##### ステップ3: LLM Production Secrets登録

```bash
# OpenAI Production Secret
gh secret set OPENAI_PROD_API_KEY \
  --body "$(cat ~/openai-keys.txt | grep OPENAI_PROD_API_KEY | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# Anthropic Production Secret
gh secret set ANTHROPIC_PROD_API_KEY \
  --body "$(cat ~/anthropic-keys.txt | grep ANTHROPIC_PROD_API_KEY | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# 登録確認
gh secret list --repo daishiman/AutoForgeNexus | grep -E "OPENAI_PROD|ANTHROPIC_PROD"
```

**確認:**
- [x] `OPENAI_PROD_API_KEY`が登録されている
- [x] `ANTHROPIC_PROD_API_KEY`が登録されている

##### ステップ4: Redis Production Secrets登録

⚠️ **重要**: Issue #77の方針に従い、本番環境もStagingのRedisインスタンスを使用します。

```bash
# Redis Production Secrets（Stagingと同じ値を使用）
gh secret set REDIS_PROD_REST_URL \
  --body "$(cat ~/redis-keys.txt | grep REDIS_STAGING_REST_URL | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

gh secret set REDIS_PROD_REST_TOKEN \
  --body "$(cat ~/redis-keys.txt | grep REDIS_STAGING_REST_TOKEN | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# 登録確認
gh secret list --repo daishiman/AutoForgeNexus | grep REDIS_PROD
```

**確認:**
- [x] `REDIS_PROD_REST_URL`が登録されている（Staging値と同じ）
- [x] `REDIS_PROD_REST_TOKEN`が登録されている（Staging値と同じ）

##### ステップ5: LangFuse Production Secrets登録（オプション）

```bash
# LangFuse Production Secrets
gh secret set LANGFUSE_PROD_PUBLIC_KEY \
  --body "$(cat ~/langfuse-keys.txt | grep LANGFUSE_PROD_PUBLIC_KEY | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

gh secret set LANGFUSE_PROD_SECRET_KEY \
  --body "$(cat ~/langfuse-keys.txt | grep LANGFUSE_PROD_SECRET_KEY | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# 登録確認
gh secret list --repo daishiman/AutoForgeNexus | grep LANGFUSE_PROD
```

**確認:**
- [x] `LANGFUSE_PROD_PUBLIC_KEY`が登録されている（オプション）
- [x] `LANGFUSE_PROD_SECRET_KEY`が登録されている（オプション）

---

### C-4: Cloudflare Secrets登録（5分）

#### 🛠️ 実行手順

##### ステップ1: Cloudflare基本情報登録

```bash
# Cloudflare API Token登録
gh secret set CLOUDFLARE_API_TOKEN \
  --body "$(cat ~/cloudflare-keys.txt | grep CLOUDFLARE_API_TOKEN | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# Cloudflare Account ID登録
gh secret set CLOUDFLARE_ACCOUNT_ID \
  --body "$(cat ~/cloudflare-keys.txt | grep CLOUDFLARE_ACCOUNT_ID | cut -d'=' -f2)" \
  --repo daishiman/AutoForgeNexus

# 登録確認
gh secret list --repo daishiman/AutoForgeNexus | grep CLOUDFLARE
```

**確認:**
- [x] `CLOUDFLARE_API_TOKEN`が登録されている
- [x] `CLOUDFLARE_ACCOUNT_ID`が登録されている

---

### C-5: 全Secrets登録確認（5分）

#### 🛠️ 実行手順

##### ステップ1: 全Secrets一覧表示

```bash
# 全GitHub Secrets一覧表示
gh secret list --repo daishiman/AutoForgeNexus

# 出力を変数にカウント
SECRET_COUNT=$(gh secret list --repo daishiman/AutoForgeNexus | wc -l)
echo "登録済みSecrets数: $SECRET_COUNT"
```

**期待されるSecrets一覧:**

| Secret名 | 環境 | サービス |
|---------|------|---------|
| `STAGING_CLERK_PUBLIC_KEY` | Staging | Clerk認証 |
| `STAGING_CLERK_SECRET_KEY` | Staging | Clerk認証 |
| `PROD_CLERK_PUBLIC_KEY` | Production | Clerk認証 |
| `PROD_CLERK_SECRET_KEY` | Production | Clerk認証 |
| `TURSO_STAGING_DATABASE_URL` | Staging | Tursoデータベース |
| `TURSO_STAGING_AUTH_TOKEN` | Staging | Tursoデータベース |
| `TURSO_PROD_DATABASE_URL` | Production | Tursoデータベース |
| `TURSO_PROD_AUTH_TOKEN` | Production | Tursoデータベース |
| `OPENAI_STAGING_API_KEY` | Staging | OpenAI LLM |
| `OPENAI_PROD_API_KEY` | Production | OpenAI LLM |
| `ANTHROPIC_STAGING_API_KEY` | Staging | Anthropic LLM |
| `ANTHROPIC_PROD_API_KEY` | Production | Anthropic LLM |
| `REDIS_STAGING_REST_URL` | Staging | Redis（REST API） |
| `REDIS_STAGING_REST_TOKEN` | Staging | Redis（REST API） |
| `REDIS_PROD_REST_URL` | Production | Redis（REST API） |
| `REDIS_PROD_REST_TOKEN` | Production | Redis（REST API） |
| `CLOUDFLARE_API_TOKEN` | 共通 | Cloudflareデプロイ |
| `CLOUDFLARE_ACCOUNT_ID` | 共通 | Cloudflareデプロイ |

**オプション（LangFuse使用時）:**
- `LANGFUSE_STAGING_PUBLIC_KEY`
- `LANGFUSE_STAGING_SECRET_KEY`
- `LANGFUSE_PROD_PUBLIC_KEY`
- `LANGFUSE_PROD_SECRET_KEY`

**確認:**
- [x] 必須Secrets 18個が登録されている
- [x] オプションSecretsが必要に応じて登録されている

##### ステップ2: Secrets内容確認（セキュリティチェック）

```bash
# Secrets値の最初の数文字だけ表示（セキュリティ確認用）
cat ~/clerk-keys.txt | grep CLERK_DEV_PUBLISHABLE_KEY | cut -d'=' -f2 | cut -c1-10
# 期待される出力: pk_test_xx（最初の10文字）

cat ~/turso-keys.txt | grep TURSO_STAGING_DATABASE_URL | cut -d'=' -f2 | cut -c1-15
# 期待される出力: libsql://xxxxx（最初の15文字）
```

**確認:**
- [x] すべてのSecretsが正しい形式で登録されている
- [x] プレフィックス（pk_test_, sk_test_, libsql://等）が正しい

---

## ✅ Phase C 完了確認

以下の設定が完了しましたか？

### Staging環境Secrets（9個）
- [x] `STAGING_CLERK_PUBLIC_KEY`
- [x] `STAGING_CLERK_SECRET_KEY`
- [x] `TURSO_STAGING_DATABASE_URL`
- [x] `TURSO_STAGING_AUTH_TOKEN`
- [x] `OPENAI_STAGING_API_KEY`
- [x] `ANTHROPIC_STAGING_API_KEY`
- [x] `REDIS_STAGING_REST_URL`
- [x] `REDIS_STAGING_REST_TOKEN`
- [x] `LANGFUSE_STAGING_*`（オプション）

### Production環境Secrets（9個）
- [x] `PROD_CLERK_PUBLIC_KEY`
- [x] `PROD_CLERK_SECRET_KEY`
- [x] `TURSO_PROD_DATABASE_URL`
- [x] `TURSO_PROD_AUTH_TOKEN`
- [x] `OPENAI_PROD_API_KEY`
- [x] `ANTHROPIC_PROD_API_KEY`
- [x] `REDIS_PROD_REST_URL`
- [x] `REDIS_PROD_REST_TOKEN`
- [x] `LANGFUSE_PROD_*`（オプション）

### Cloudflare Secrets（2個）
- [x] `CLOUDFLARE_API_TOKEN`
- [x] `CLOUDFLARE_ACCOUNT_ID`

### 次のPhase Dに進む前に
- [x] `gh secret list`で全Secretsが表示される
- [x] 一時保存ファイル（~/\*-keys.txt）を安全に保管
- [x] GitHubリポジトリAdmin権限がある

---

## Phase D: 環境変数ファイル作成

このPhaseでは、ローカル開発用の環境変数ファイル（.env）を作成し、Phase Eでのローカル動作確認を準備します。

### ⏱️ 所要時間: 30分
### 🎯 達成目標: ローカル開発環境の環境変数設定完了

---

### D-1: バックエンド環境変数ファイル作成（15分）

#### 🛠️ 実行手順

##### ステップ1: .env.developmentファイル作成

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/backend

# .env.developmentファイル作成
cat > .env.development << 'EOF'
# ==========================================
# AutoForgeNexus Backend - Development環境設定
# ==========================================

# 【環境設定】
APP_ENV=development
APP_NAME=AutoForgeNexus-Backend-Dev
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# 【Clerk認証】
CLERK_PUBLIC_KEY=$(cat ~/clerk-keys.txt | grep CLERK_DEV_PUBLISHABLE_KEY | cut -d'=' -f2)
CLERK_SECRET_KEY=$(cat ~/clerk-keys.txt | grep CLERK_DEV_SECRET_KEY | cut -d'=' -f2)

# 【Tursoデータベース】
TURSO_DATABASE_URL=$(cat ~/turso-keys.txt | grep TURSO_STAGING_DATABASE_URL | cut -d'=' -f2)
TURSO_AUTH_TOKEN=$(cat ~/turso-keys.txt | grep TURSO_STAGING_AUTH_TOKEN | cut -d'=' -f2)

# 【LLMプロバイダー】
OPENAI_API_KEY=$(cat ~/openai-keys.txt | grep OPENAI_STAGING_API_KEY | cut -d'=' -f2)
ANTHROPIC_API_KEY=$(cat ~/anthropic-keys.txt | grep ANTHROPIC_STAGING_API_KEY | cut -d'=' -f2)

# 【Redis（REST API用）】
REDIS_REST_URL=$(cat ~/redis-keys.txt | grep REDIS_STAGING_REST_URL | cut -d'=' -f2)
REDIS_REST_TOKEN=$(cat ~/redis-keys.txt | grep REDIS_STAGING_REST_TOKEN | cut -d'=' -f2)

# 【観測性（オプション）】
LANGFUSE_PUBLIC_KEY=$(cat ~/langfuse-keys.txt | grep LANGFUSE_STAGING_PUBLIC_KEY | cut -d'=' -f2 2>/dev/null || echo "")
LANGFUSE_SECRET_KEY=$(cat ~/langfuse-keys.txt | grep LANGFUSE_STAGING_SECRET_KEY | cut -d'=' -f2 2>/dev/null || echo "")

# 【ローカル開発用設定】
# FastAPI再読み込み設定
RELOAD=true
WORKERS=1

# デバッグモード
SQLALCHEMY_ECHO=true  # SQL実行ログ出力
EOF

# 実際の値を置換
sed -i '' "s|\$(cat ~/clerk-keys.txt | grep CLERK_DEV_PUBLISHABLE_KEY | cut -d'=' -f2)|$(cat ~/clerk-keys.txt | grep CLERK_DEV_PUBLISHABLE_KEY | cut -d'=' -f2)|g" .env.development
sed -i '' "s|\$(cat ~/clerk-keys.txt | grep CLERK_DEV_SECRET_KEY | cut -d'=' -f2)|$(cat ~/clerk-keys.txt | grep CLERK_DEV_SECRET_KEY | cut -d'=' -f2)|g" .env.development
sed -i '' "s|\$(cat ~/turso-keys.txt | grep TURSO_STAGING_DATABASE_URL | cut -d'=' -f2)|$(cat ~/turso-keys.txt | grep TURSO_STAGING_DATABASE_URL | cut -d'=' -f2)|g" .env.development
sed -i '' "s|\$(cat ~/turso-keys.txt | grep TURSO_STAGING_AUTH_TOKEN | cut -d'=' -f2)|$(cat ~/turso-keys.txt | grep TURSO_STAGING_AUTH_TOKEN | cut -d'=' -f2)|g" .env.development
sed -i '' "s|\$(cat ~/openai-keys.txt | grep OPENAI_STAGING_API_KEY | cut -d'=' -f2)|$(cat ~/openai-keys.txt | grep OPENAI_STAGING_API_KEY | cut -d'=' -f2)|g" .env.development
sed -i '' "s|\$(cat ~/anthropic-keys.txt | grep ANTHROPIC_STAGING_API_KEY | cut -d'=' -f2)|$(cat ~/anthropic-keys.txt | grep ANTHROPIC_STAGING_API_KEY | cut -d'=' -f2)|g" .env.development
sed -i '' "s|\$(cat ~/redis-keys.txt | grep REDIS_STAGING_REST_URL | cut -d'=' -f2)|$(cat ~/redis-keys.txt | grep REDIS_STAGING_REST_URL | cut -d'=' -f2)|g" .env.development
sed -i '' "s|\$(cat ~/redis-keys.txt | grep REDIS_STAGING_REST_TOKEN | cut -d'=' -f2)|$(cat ~/redis-keys.txt | grep REDIS_STAGING_REST_TOKEN | cut -d'=' -f2)|g" .env.development

# ファイル権限を制限
chmod 600 .env.development

# 内容確認（秘密情報は隠す）
cat .env.development | sed 's/=.*/=***REDACTED***/g'
```

**確認:**
- [x] `.env.development`ファイルが作成された
- [x] ファイル権限が600（所有者のみ読み書き可能）
- [x] すべての環境変数が設定されている

##### ステップ2: .gitignore確認

```bash
# .gitignoreに.envが含まれているか確認
grep -E "^\.env" /Users/dm/dev/dev/個人開発/AutoForgeNexus/.gitignore

# 期待される出力:
# .env
# .env.*
# !.env.example

# 含まれていない場合は追加
if ! grep -q "^\.env" /Users/dm/dev/dev/個人開発/AutoForgeNexus/.gitignore; then
  echo -e "\n# Environment variables\n.env\n.env.*\n!.env.example" >> /Users/dm/dev/dev/個人開発/AutoForgeNexus/.gitignore
fi
```

**確認:**
- [x] `.env*`が.gitignoreに含まれている
- [x] `.env.example`は除外されている（!.env.example）

---

### D-2: フロントエンド環境変数ファイル作成（15分）

#### 🛠️ 実行手順

##### ステップ1: .env.localファイル作成

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/frontend

# .env.localファイル作成
cat > .env.local << 'EOF'
# ==========================================
# AutoForgeNexus Frontend - Local開発環境設定
# ==========================================

# 【Next.js環境設定】
NODE_ENV=development
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_APP_NAME=AutoForgeNexus-Frontend-Dev

# 【Clerk認証（Next.js用）】
# Public Key（ブラウザ公開OK）
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$(cat ~/clerk-keys.txt | grep CLERK_DEV_PUBLISHABLE_KEY | cut -d'=' -f2)
# Secret Key（サーバーサイドのみ）
CLERK_SECRET_KEY=$(cat ~/clerk-keys.txt | grep CLERK_DEV_SECRET_KEY | cut -d'=' -f2)

# 【Clerk認証リダイレクトURL】
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding

# 【バックエンドAPI URL】
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# 【開発用設定】
# Turbopack有効化（Next.js 15.5.4）
TURBOPACK=1

# React 19.0.0 DevTools
REACT_DEVTOOLS=true

# Source Map有効化
GENERATE_SOURCEMAP=true
EOF

# 実際の値を置換
sed -i '' "s|\$(cat ~/clerk-keys.txt | grep CLERK_DEV_PUBLISHABLE_KEY | cut -d'=' -f2)|$(cat ~/clerk-keys.txt | grep CLERK_DEV_PUBLISHABLE_KEY | cut -d'=' -f2)|g" .env.local
sed -i '' "s|\$(cat ~/clerk-keys.txt | grep CLERK_DEV_SECRET_KEY | cut -d'=' -f2)|$(cat ~/clerk-keys.txt | grep CLERK_DEV_SECRET_KEY | cut -d'=' -f2)|g" .env.local

# ファイル権限を制限
chmod 600 .env.local

# 内容確認（秘密情報は隠す）
cat .env.local | sed 's/=.*/=***REDACTED***/g'
```

**確認:**
- [x] `.env.local`ファイルが作成された
- [x] ファイル権限が600（所有者のみ読み書き可能）
- [x] Clerk Public/Secret Keyが設定されている
- [x] Turbopack設定が有効化されている

##### ステップ2: .gitignore確認

```bash
# frontendの.gitignoreに.env.localが含まれているか確認
grep -E "^\.env\.local" /Users/dm/dev/dev/個人開発/AutoForgeNexus/frontend/.gitignore

# 期待される出力:
# .env.local

# Next.jsデフォルトで含まれているはず（念のため確認）
if ! grep -q "^\.env\.local" /Users/dm/dev/dev/個人開発/AutoForgeNexus/frontend/.gitignore; then
  echo ".env.local" >> /Users/dm/dev/dev/個人開発/AutoForgeNexus/frontend/.gitignore
fi
```

**確認:**
- [x] `.env.local`が.gitignoreに含まれている
- [x] 秘密情報がGitにコミットされない

---

### D-3: 環境変数検証（5分）

#### 🛠️ 実行手順

##### ステップ1: バックエンド環境変数検証

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/backend

# Python dotenvで読み込みテスト
python3 << 'EOF'
from dotenv import load_dotenv
import os

# .env.developmentを読み込み
load_dotenv('.env.development')

# 必須環境変数チェック
required_vars = [
    'CLERK_PUBLIC_KEY',
    'CLERK_SECRET_KEY',
    'TURSO_DATABASE_URL',
    'TURSO_AUTH_TOKEN',
    'OPENAI_API_KEY',
    'ANTHROPIC_API_KEY',
    'REDIS_REST_URL',
    'REDIS_REST_TOKEN'
]

print("=" * 50)
print("バックエンド環境変数検証")
print("=" * 50)

all_set = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        # 値の最初の10文字だけ表示
        print(f"✅ {var}: {value[:10]}...")
    else:
        print(f"❌ {var}: 未設定")
        all_set = False

if all_set:
    print("\n✅ すべての必須環境変数が設定されています")
else:
    print("\n❌ 一部の環境変数が未設定です")
EOF
```

**期待される出力:**
```
==================================================
バックエンド環境変数検証
==================================================
✅ CLERK_PUBLIC_KEY: pk_test_xx...
✅ CLERK_SECRET_KEY: sk_test_xx...
✅ TURSO_DATABASE_URL: libsql://x...
✅ TURSO_AUTH_TOKEN: eyJhbGciOi...
✅ OPENAI_API_KEY: sk-proj-xx...
✅ ANTHROPIC_API_KEY: sk-ant-xx...
✅ REDIS_REST_URL: https://xx...
✅ REDIS_REST_TOKEN: AURsAAInc...

✅ すべての必須環境変数が設定されています
```

**確認:**
- [x] すべての必須環境変数が設定されている
- [x] 各キーが正しいプレフィックスで始まっている

##### ステップ2: フロントエンド環境変数検証

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/frontend

# Node.jsで読み込みテスト
node << 'EOF'
require('dotenv').config({ path: '.env.local' });

const requiredVars = [
  'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY',
  'CLERK_SECRET_KEY',
  'NEXT_PUBLIC_API_URL',
  'NEXT_PUBLIC_WS_URL'
];

console.log('='.repeat(50));
console.log('フロントエンド環境変数検証');
console.log('='.repeat(50));

let allSet = true;
requiredVars.forEach(varName => {
  const value = process.env[varName];
  if (value) {
    // 値の最初の15文字だけ表示
    console.log(`✅ ${varName}: ${value.substring(0, 15)}...`);
  } else {
    console.log(`❌ ${varName}: 未設定`);
    allSet = false;
  }
});

if (allSet) {
  console.log('\n✅ すべての必須環境変数が設定されています');
} else {
  console.log('\n❌ 一部の環境変数が未設定です');
}
EOF
```

**期待される出力:**
```
==================================================
フロントエンド環境変数検証
==================================================
✅ NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: pk_test_xxxxxx...
✅ CLERK_SECRET_KEY: sk_test_xxxxxx...
✅ NEXT_PUBLIC_API_URL: http://localhost...
✅ NEXT_PUBLIC_WS_URL: ws://localhost:...

✅ すべての必須環境変数が設定されています
```

**確認:**
- [x] すべての必須環境変数が設定されている
- [x] NEXT_PUBLIC_プレフィックスが正しい

---

## ✅ Phase D 完了確認

以下の設定が完了しましたか？

### バックエンド環境変数
- [x] `backend/.env.development`が作成されている
- [x] Clerk, Turso, LLM, Redisの全環境変数が設定されている
- [x] ファイル権限が600に設定されている
- [x] Python dotenvで読み込みテスト成功

### フロントエンド環境変数
- [x] `frontend/.env.local`が作成されている
- [x] Clerk認証とAPI URLが設定されている
- [x] Turbopack設定が有効化されている
- [x] Node.jsで読み込みテスト成功

### セキュリティ確認
- [x] 両方の環境変数ファイルが.gitignoreに含まれている
- [x] 秘密情報がGitにコミットされない
- [x] ファイル権限が適切に制限されている

### 次のPhase Eに進む前に
- [x] 環境変数検証が全て成功している
- [x] 一時保存ファイル（~/\*-keys.txt）を安全な場所にバックアップ
- [x] Docker環境が起動済み（`docker-compose ps`で確認）

---

## Phase E: ローカル動作確認

このPhaseでは、作成した環境変数を使ってローカル開発環境を起動し、すべてのサービスが正常に動作することを確認します。

### ⏱️ 所要時間: 1-2時間
### 🎯 達成目標: バックエンド・フロントエンド・DB接続確認完了

---

### E-1: バックエンドローカル起動（30分）

#### 🛠️ 実行手順

##### ステップ1: Python仮想環境準備

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/backend

# 仮想環境が存在しない場合は作成
if [ ! -d "venv" ]; then
  python3.13 -m venv venv
fi

# 仮想環境を有効化
source venv/bin/activate

# 依存関係インストール（開発用）
pip install --upgrade pip
pip install -e .[dev]

# インストール確認
pip list | grep -E "fastapi|pydantic|sqlalchemy"
```

**期待される出力:**
```
fastapi                  0.116.1
pydantic                 2.x.x
sqlalchemy              2.0.32
```

**確認:**
- [x] Python 3.13仮想環境が作成されている
- [x] FastAPI、Pydantic v2がインストールされている
- [x] 開発用依存関係がすべてインストールされている

##### ステップ2: Tursoデータベース接続確認

```bash
# 環境変数読み込み
export $(cat .env.development | xargs)

# Turso接続テスト（Python）
python3 << EOF
import os
from sqlalchemy import create_engine, text

# Turso接続URL作成
database_url = os.getenv('TURSO_DATABASE_URL')
auth_token = os.getenv('TURSO_AUTH_TOKEN')

# libSQL接続URL（Turso形式）
connect_args = {"auth_token": auth_token}
engine = create_engine(
    database_url,
    connect_args=connect_args,
    echo=True  # SQL実行ログ出力
)

# 接続テスト
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 'Turso接続成功！' AS message"))
        print(f"✅ {result.fetchone()[0]}")
except Exception as e:
    print(f"❌ Turso接続失敗: {e}")
EOF
```

**期待される出力:**
```
✅ Turso接続成功！
```

**確認:**
- [x] Tursoデータベースに接続できた
- [x] SQLクエリが正常に実行された

##### ステップ3: Redis接続確認

```bash
# Redis REST API接続テスト
curl -X POST "$(echo $REDIS_REST_URL)/set/test:connection" \
  -H "Authorization: Bearer $(echo $REDIS_REST_TOKEN)" \
  -d '"ローカル接続テスト成功"'

# 期待される出力: {"result":"OK"}

# 値取得テスト
curl "$(echo $REDIS_REST_URL)/get/test:connection" \
  -H "Authorization: Bearer $(echo $REDIS_REST_TOKEN)"

# 期待される出力: {"result":"ローカル接続テスト成功"}
```

**確認:**
- [x] Redis REST APIで書き込みが成功した（{"result":"OK"}）
- [x] Redis REST APIで読み取りが成功した

##### ステップ4: FastAPIサーバー起動

```bash
# FastAPI開発サーバー起動
uvicorn src.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --env-file .env.development \
  --log-level debug

# 別ターミナルで動作確認
# curl http://localhost:8000/
# curl http://localhost:8000/health
```

**期待される出力（uvicorn起動時）:**
```
INFO:     Will watch for changes in these directories: ['/Users/dm/dev/dev/個人開発/AutoForgeNexus/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**確認:**
- [x] FastAPIサーバーが起動した
- [x] ポート8000でリッスンしている
- [x] リロード機能が有効化されている

##### ステップ5: APIエンドポイント動作確認

```bash
# 新しいターミナルで実行

# ヘルスチェック
curl http://localhost:8000/health

# 期待される出力:
# {"status":"healthy","database":"connected","redis":"connected"}

# OpenAPI仕様確認
curl http://localhost:8000/openapi.json | jq '.info'

# 期待される出力:
# {
#   "title": "AutoForgeNexus API",
#   "version": "1.0.0"
# }
```

**確認:**
- [x] `/health`エンドポイントが正常応答
- [x] データベース接続が確認された
- [x] Redis接続が確認された
- [x] OpenAPI仕様が取得できた

---

### E-2: フロントエンドローカル起動（30分）

#### 🛠️ 実行手順

##### ステップ1: Node.js依存関係インストール

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/frontend

# pnpm依存関係インストール
pnpm install

# インストール確認
pnpm list next react react-dom @clerk/nextjs

# 期待される出力:
# next 15.5.4
# react 19.0.0
# react-dom 19.0.0
# @clerk/nextjs 6.32.0
```

**確認:**
- [x] Next.js 15.5.4がインストールされている
- [x] React 19.0.0がインストールされている
- [x] Clerk Next.js SDKがインストールされている

##### ステップ2: Turbopack開発サーバー起動

```bash
# Turbopack開発サーバー起動（Next.js 15.5.4）
pnpm dev --turbo

# 期待される出力:
#   ▲ Next.js 15.5.4 (turbo)
#   - Local:        http://localhost:3000
#   - Network:      http://192.168.x.x:3000
#
#  ✓ Ready in 1.2s
```

**確認:**
- [x] Turbopackが有効化されている
- [x] ポート3000でリッスンしている
- [x] 起動時間が2秒以内（Turbopackの恩恵）

##### ステップ3: Clerk認証動作確認

```bash
# 新しいターミナルで実行

# Clerk認証エンドポイント確認
curl http://localhost:3000/api/auth/status

# ブラウザでアクセス
open http://localhost:3000

# Clerk認証フロー確認:
# 1. http://localhost:3000 → トップページ表示
# 2. "Sign In"リンクをクリック → Clerkログイン画面
# 3. テストユーザーでログイン → ダッシュボードにリダイレクト
```

**確認:**
- [x] トップページが表示される
- [x] Clerk認証UIが表示される
- [x] ログイン後にダッシュボードにリダイレクトされる

##### ステップ4: バックエンドAPI接続確認

```bash
# フロントエンド→バックエンドAPI呼び出しテスト
# ブラウザ開発者ツール（Console）で実行:

fetch('http://localhost:8000/health')
  .then(res => res.json())
  .then(data => console.log('Backend Health:', data))
  .catch(err => console.error('Backend Error:', err));

# 期待される出力:
# Backend Health: {status: "healthy", database: "connected", redis: "connected"}
```

**確認:**
- [x] フロントエンドからバックエンドAPIに接続できた
- [x] CORS設定が正しい（`http://localhost:3000`が許可されている）

---

### E-3: 統合動作確認（30分）

#### 🛠️ 実行手順

##### ステップ1: 認証フロー統合テスト

```bash
# ブラウザで以下の手順を実行:

# 1. 新規ユーザー登録
# http://localhost:3000/sign-up にアクセス
# → メールアドレスとパスワードを入力
# → Clerkで登録完了
# → /onboarding にリダイレクト

# 2. ログアウト
# ダッシュボードから"Sign Out"をクリック
# → トップページにリダイレクト

# 3. ログイン
# http://localhost:3000/sign-in にアクセス
# → 先ほど登録したユーザーでログイン
# → /dashboard にリダイレクト
```

**確認:**
- [x] 新規ユーザー登録が成功した
- [x] ログアウトが正常に動作した
- [x] ログインが成功した
- [x] リダイレクトURLが正しい

##### ステップ2: データベース操作テスト

```bash
# バックエンドターミナルで実行

# Turso DBにテストデータ挿入
turso db shell autoforgenexus << 'EOF'
CREATE TABLE IF NOT EXISTS test_prompts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO test_prompts (title, content) VALUES
  ('テストプロンプト1', 'これはローカル動作確認用のテストです'),
  ('テストプロンプト2', 'Tursoデータベース接続確認');

SELECT * FROM test_prompts;
EOF

# APIでデータ取得テスト
curl http://localhost:8000/api/prompts | jq '.'
```

**期待される出力:**
```json
[
  {
    "id": 1,
    "title": "テストプロンプト1",
    "content": "これはローカル動作確認用のテストです",
    "created_at": "2025-10-05T10:00:00Z"
  },
  {
    "id": 2,
    "title": "テストプロンプト2",
    "content": "Tursoデータベース接続確認",
    "created_at": "2025-10-05T10:00:01Z"
  }
]
```

**確認:**
- [x] Turso DBにテーブルが作成された
- [x] テストデータが挿入された
- [x] APIでデータ取得が成功した

##### ステップ3: Redis キャッシュテスト

```bash
# Redisキャッシュ動作確認

# バックエンドでキャッシュ書き込み
curl -X POST http://localhost:8000/api/cache/set \
  -H "Content-Type: application/json" \
  -d '{"key":"test:prompt:1","value":"キャッシュテスト","ttl":3600}'

# 期待される出力: {"status":"ok","key":"test:prompt:1"}

# キャッシュ読み取り
curl http://localhost:8000/api/cache/get/test:prompt:1 | jq '.'

# 期待される出力: {"key":"test:prompt:1","value":"キャッシュテスト"}
```

**確認:**
- [x] Redisにキャッシュが書き込まれた
- [x] Redisからキャッシュが読み取れた
- [x] TTL（有効期限）が正しく設定された

---

### E-4: パフォーマンステスト（30分）

#### 🛠️ 実行手順

##### ステップ1: フロントエンドビルドテスト

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/frontend

# Turbopackで本番ビルド
time pnpm build --turbo

# 期待される出力:
#   ▲ Next.js 15.5.4 (turbo)
#   Creating an optimized production build...
#   ✓ Compiled successfully in 45s
#
# real    0m45.123s  # 60秒以内が目標
```

**確認:**
- [x] ビルドが成功した
- [x] ビルド時間が60秒以内
- [x] 最適化された本番ビルドが生成された

##### ステップ2: Core Web Vitals測定

```bash
# Lighthouse CI でパフォーマンス測定
# （フロントエンド開発サーバーが起動中であること）

npx @lhci/cli@latest autorun \
  --collect.url=http://localhost:3000 \
  --collect.numberOfRuns=1

# 期待される出力（抜粋）:
# Performance: 90+
# First Contentful Paint (FCP): < 1.8s
# Largest Contentful Paint (LCP): < 2.5s
# Cumulative Layout Shift (CLS): < 0.1
```

**確認:**
- [x] Performance スコアが90以上
- [x] LCP（Largest Contentful Paint）が2.5秒未満
- [x] FID（First Input Delay）が100ms未満
- [x] CLS（Cumulative Layout Shift）が0.1未満

##### ステップ3: API負荷テスト（軽量）

```bash
# ApacheBench（ab）で軽量負荷テスト
# （バックエンドが起動中であること）

ab -n 100 -c 10 http://localhost:8000/health

# 期待される出力（抜粋）:
# Requests per second: 500+ [#/sec]
# Time per request: < 20 [ms] (mean)
# Failed requests: 0
```

**確認:**
- [x] 100リクエストすべて成功（Failed requests: 0）
- [x] 秒間500リクエスト以上処理できた
- [x] 平均応答時間が20ms未満

---

## ✅ Phase E 完了確認

以下の動作確認が完了しましたか？

### バックエンド動作確認
- [x] Python 3.13仮想環境が作成されている
- [x] FastAPIサーバーが起動した（ポート8000）
- [x] Tursoデータベース接続確認完了
- [x] Redis接続確認完了
- [x] `/health`エンドポイントが正常応答

### フロントエンド動作確認
- [x] Next.js 15.5.4 Turbopack起動成功（ポート3000）
- [x] React 19.0.0が動作している
- [x] Clerk認証フローが動作している
- [x] バックエンドAPIに接続できた

### 統合動作確認
- [x] 認証フロー（登録→ログアウト→ログイン）成功
- [x] データベース操作（作成→挿入→取得）成功
- [x] Redisキャッシュ（書き込み→読み取り）成功

### パフォーマンス確認
- [x] フロントエンドビルド時間が60秒以内
- [x] Core Web Vitals基準をクリア（LCP < 2.5s）
- [x] API負荷テスト成功（500+ req/s）

### 次のPhase Fに進む前に
- [x] すべてのサービスが正常起動している
- [x] 統合テストがすべて成功している
- [x] パフォーマンス基準をクリアしている
- [x] Cloudflare Workers/Pagesアカウントが準備されている

---

## Phase F: Staging デプロイ

このPhaseでは、Phase Eで確認したローカル環境をCloudflare（Workers/Pages）にデプロイし、Staging環境を構築します。

### ⏱️ 所要時間: 1時間
### 🎯 達成目標: Staging環境デプロイ完了、動作確認完了

---

### F-1: Wrangler設定確認（10分）

#### 🛠️ 実行手順

##### ステップ1: Wrangler認証確認

```bash
# Wrangler認証状態確認
wrangler whoami

# 期待される出力:
# You are logged in with an OAuth Token, associated with the email 'your-email@example.com'.
# Account Name: Your Account Name
# Account ID: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 未認証の場合はログイン
if ! wrangler whoami > /dev/null 2>&1; then
  wrangler login
fi
```

**確認:**
- [x] Wranglerでログイン済み
- [x] Account IDが表示される
- [x] `CLOUDFLARE_ACCOUNT_ID`と一致する

##### ステップ2: backend/wrangler.toml確認

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/backend

# wrangler.toml存在確認
if [ ! -f "wrangler.toml" ]; then
  echo "❌ wrangler.tomlが存在しません"
  exit 1
fi

# Staging環境設定確認
cat wrangler.toml | grep -A 10 "\[env.staging\]"

# 期待される出力:
# [env.staging]
# name = "autoforgenexus-backend-staging"
# workers_dev = true
# ...
```

**確認:**
- [x] `backend/wrangler.toml`が存在する
- [x] `[env.staging]`設定が含まれている
- [x] `name = "autoforgenexus-backend-staging"`が設定されている

---

### F-2: バックエンドStaging デプロイ（20分）

#### 🛠️ 実行手順

##### ステップ1: Cloudflare Secrets設定

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/backend

# Staging環境のSecretsを設定
# （GitHub Secretsから取得した値を使用）

# Clerk Secrets
wrangler secret put CLERK_SECRET_KEY --env staging
# プロンプトで入力: <STAGING_CLERK_SECRET_KEYの値>

# Turso Secrets
wrangler secret put TURSO_DATABASE_URL --env staging
# プロンプトで入力: <TURSO_STAGING_DATABASE_URLの値>

wrangler secret put TURSO_AUTH_TOKEN --env staging
# プロンプトで入力: <TURSO_STAGING_AUTH_TOKENの値>

# LLM Secrets
wrangler secret put OPENAI_API_KEY --env staging
# プロンプトで入力: <OPENAI_STAGING_API_KEYの値>

wrangler secret put ANTHROPIC_API_KEY --env staging
# プロンプトで入力: <ANTHROPIC_STAGING_API_KEYの値>

# Redis Secrets
wrangler secret put REDIS_REST_URL --env staging
# プロンプトで入力: <REDIS_STAGING_REST_URLの値>

wrangler secret put REDIS_REST_TOKEN --env staging
# プロンプトで入力: <REDIS_STAGING_REST_TOKENの値>

# Secrets確認
wrangler secret list --env staging
```

**確認:**
- [x] 7つのSecretsが登録されている
- [x] `wrangler secret list`で一覧表示される

##### ステップ2: Workers デプロイ実行

```bash
# Staging環境にデプロイ
wrangler deploy --env staging

# 期待される出力:
# Total Upload: 1.23 KiB / gzip: 0.45 KiB
# Uploaded autoforgenexus-backend-staging (1.23 sec)
# Published autoforgenexus-backend-staging (0.34 sec)
#   https://autoforgenexus-backend-staging.<account-subdomain>.workers.dev
# Current Deployment ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**確認:**
- [x] デプロイが成功した
- [x] Workers URLが発行された（`https://autoforgenexus-backend-staging.*.workers.dev`）
- [x] Deployment IDが発行された

##### ステップ3: Workers動作確認

```bash
# Workers URLを環境変数に保存
export STAGING_WORKERS_URL="https://autoforgenexus-backend-staging.<account-subdomain>.workers.dev"

# ヘルスチェック
curl $STAGING_WORKERS_URL/health | jq '.'

# 期待される出力:
# {
#   "status": "healthy",
#   "database": "connected",
#   "redis": "connected",
#   "environment": "staging"
# }

# OpenAPI仕様確認
curl $STAGING_WORKERS_URL/openapi.json | jq '.info'
```

**確認:**
- [x] `/health`エンドポイントが正常応答
- [x] データベース接続が確認された
- [x] Redis接続が確認された
- [x] `environment: "staging"`が返される

---

### F-3: フロントエンドStaging デプロイ（20分）

#### 🛠️ 実行手順

##### ステップ1: Cloudflare Pages環境変数設定

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/frontend

# Pages環境変数設定（Staging）
# DashboardのGUIで設定する方が確実なため、手順を記載

# 1. Cloudflare Dashboard → Workers & Pages → autoforgenexus-frontend
# 2. Settings → Environment variables
# 3. "Add variable"で以下を設定:

# Production環境（mainブランチ）用:
# （今回はSkip - Phase Gで設定）

# Preview環境（feature/*ブランチ）用:
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=<STAGING_CLERK_PUBLIC_KEYの値>
CLERK_SECRET_KEY=<STAGING_CLERK_SECRET_KEYの値>
NEXT_PUBLIC_API_URL=<STAGING_WORKERS_URLの値>
NEXT_PUBLIC_APP_ENV=staging

# 保存して次へ
```

**または、Wrangler CLIで設定（非推奨 - Pages非対応の場合あり）:**
```bash
# wrangler pages環境変数設定（実験的機能）
# 注: 2025年10月時点では、DashboardのGUI推奨

# 設定確認コマンド（読み取り専用）
wrangler pages project list
```

**確認:**
- [x] Clerk認証の環境変数が設定された
- [x] API URLがStaging Workers URLに設定された
- [x] `NEXT_PUBLIC_APP_ENV=staging`が設定された

##### ステップ2: Pages デプロイ実行

```bash
# Next.js本番ビルド
pnpm build

# Cloudflare Pagesにデプロイ
npx wrangler pages deploy .next/static \
  --project-name=autoforgenexus-frontend \
  --branch=staging

# または、GitHub連携で自動デプロイ（推奨）
git checkout -b staging
git push origin staging

# GitHub Actionsが自動的にCloudflare Pagesにデプロイ
gh run watch
```

**期待される出力（wrangler pages deploy）:**
```
✨ Success! Deployed to https://staging.autoforgenexus.pages.dev
```

**または、GitHub Actions自動デプロイ成功:**
```
✅ Deploy to Cloudflare Pages - staging
   Deployed to: https://staging-xxxxx.autoforgenexus.pages.dev
```

**確認:**
- [x] Pagesデプロイが成功した
- [x] Staging URLが発行された
- [x] GitHub Actionsが成功した（自動デプロイの場合）

##### ステップ3: Pages動作確認

```bash
# Pages URLを環境変数に保存
export STAGING_PAGES_URL="https://staging.autoforgenexus.pages.dev"

# トップページ確認
curl -I $STAGING_PAGES_URL

# 期待される出力:
# HTTP/2 200
# content-type: text/html; charset=utf-8
# ...

# ブラウザでアクセス
open $STAGING_PAGES_URL
```

**確認:**
- [x] トップページが表示される（HTTP 200）
- [x] Clerk認証UIが表示される
- [x] バックエンドAPIに接続できる

---

### F-4: Staging環境統合テスト（10分）

#### 🛠️ 実行手順

##### ステップ1: 認証フロー確認

```bash
# ブラウザで以下の手順を実行:

# 1. Staging URLにアクセス
open $STAGING_PAGES_URL

# 2. "Sign Up"をクリック → Clerk認証画面
# 3. テストユーザーでサインアップ
# 4. /onboarding にリダイレクト確認

# 5. ログアウト → トップページにリダイレクト確認

# 6. "Sign In"でログイン → /dashboard にリダイレクト確認
```

**確認:**
- [x] Staging環境でClerk認証が動作している
- [x] サインアップ→リダイレクトが正常
- [x] ログイン→ダッシュボード遷移が正常

##### ステップ2: API統合確認

```bash
# ブラウザ開発者ツール（Console）で実行:

fetch('$STAGING_WORKERS_URL/health')
  .then(res => res.json())
  .then(data => console.log('Staging Health:', data));

# 期待される出力:
# Staging Health: {status: "healthy", database: "connected", redis: "connected", environment: "staging"}

# Clerk認証付きAPIリクエスト（ログイン後）
fetch('$STAGING_WORKERS_URL/api/prompts', {
  headers: {
    'Authorization': 'Bearer ' + await window.Clerk.session.getToken()
  }
})
  .then(res => res.json())
  .then(data => console.log('Prompts:', data));
```

**確認:**
- [x] Staging バックエンドAPIに接続できた
- [x] Clerk認証トークンが取得できた
- [x] 認証付きAPIリクエストが成功した

---

## ✅ Phase F 完了確認

以下のデプロイが完了しましたか？

### バックエンドStaging デプロイ
- [x] Cloudflare Workers Secretsが設定された（7個）
- [x] Workers デプロイが成功した
- [x] Workers URLが発行された
- [x] `/health`エンドポイントが正常応答

### フロントエンドStaging デプロイ
- [x] Cloudflare Pages環境変数が設定された
- [x] Pagesデプロイが成功した
- [x] Staging URLが発行された
- [x] トップページが表示される

### Staging環境統合確認
- [x] Clerk認証フローが動作している
- [x] バックエンドAPI接続が成功している
- [x] 認証付きAPIリクエストが成功している

### デプロイ情報記録
```bash
# 以下の情報を記録（次のPhaseで使用）
echo "STAGING_WORKERS_URL=$STAGING_WORKERS_URL" >> ~/staging-urls.txt
echo "STAGING_PAGES_URL=$STAGING_PAGES_URL" >> ~/staging-urls.txt
chmod 600 ~/staging-urls.txt
```

### 次のPhase Gに進む前に
- [x] Staging環境がすべて正常動作している
- [x] Production用のAPI Keyが準備されている（Phase A完了時）
- [x] Production用のCloudflare設定が準備されている
- [x] ドメイン設定が完了している（オプション）

---

## Phase G: Production デプロイ

このPhaseでは、Staging環境で確認した設定を本番環境にデプロイし、Production環境を構築します。

### ⏱️ 所要時間: 30分
### 🎯 達成目標: Production環境デプロイ完了、本番稼働開始

---

### G-1: Production環境準備（5分）

#### 🛠️ 実行手順

##### ステップ1: Production用Secrets確認

```bash
# GitHub SecretsにProduction用キーが登録されているか確認
gh secret list --repo daishiman/AutoForgeNexus | grep PROD

# 期待される出力:
# PROD_CLERK_PUBLIC_KEY
# PROD_CLERK_SECRET_KEY
# TURSO_PROD_DATABASE_URL
# TURSO_PROD_AUTH_TOKEN
# OPENAI_PROD_API_KEY
# ANTHROPIC_PROD_API_KEY
# REDIS_PROD_REST_URL
# REDIS_PROD_REST_TOKEN
```

**確認:**
- [x] 8つのProduction Secretsが登録されている
- [x] すべて`PROD_`プレフィックスが付いている

##### ステップ2: Production用Tursoデータベース確認

```bash
# Production DBの存在確認
turso db show autoforgenexus-production

# 期待される出力:
# Name:     autoforgenexus-production
# URL:      libsql://autoforgenexus-production-xxxxx.turso.io
# Group:    default
# Location: nrt (Tokyo, Japan)
```

**確認:**
- [x] Production DBが作成されている
- [x] 東京リージョン（nrt）に配置されている
- [x] URLが`TURSO_PROD_DATABASE_URL`と一致する

---

### G-2: バックエンドProduction デプロイ（10分）

#### 🛠️ 実行手順

##### ステップ1: Cloudflare Workers Secrets設定（Production）

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus/backend

# Production環境のSecretsを設定

# Clerk Secrets
wrangler secret put CLERK_SECRET_KEY --env production
# プロンプトで入力: <PROD_CLERK_SECRET_KEYの値>

# Turso Secrets
wrangler secret put TURSO_DATABASE_URL --env production
# プロンプトで入力: <TURSO_PROD_DATABASE_URLの値>

wrangler secret put TURSO_AUTH_TOKEN --env production
# プロンプトで入力: <TURSO_PROD_AUTH_TOKENの値>

# LLM Secrets
wrangler secret put OPENAI_API_KEY --env production
# プロンプトで入力: <OPENAI_PROD_API_KEYの値>

wrangler secret put ANTHROPIC_API_KEY --env production
# プロンプトで入力: <ANTHROPIC_PROD_API_KEYの値>

# Redis Secrets
wrangler secret put REDIS_REST_URL --env production
# プロンプトで入力: <REDIS_PROD_REST_URLの値>

wrangler secret put REDIS_REST_TOKEN --env production
# プロンプトで入力: <REDIS_PROD_REST_TOKENの値>

# Secrets確認
wrangler secret list --env production
```

**確認:**
- [x] 7つのSecretsが登録されている（Production環境）
- [x] Staging環境と別のSecretsが設定されている

##### ステップ2: Workers Production デプロイ

```bash
# Production環境にデプロイ
wrangler deploy --env production

# 期待される出力:
# Total Upload: 1.23 KiB / gzip: 0.45 KiB
# Uploaded autoforgenexus-backend-production (1.23 sec)
# Published autoforgenexus-backend-production (0.34 sec)
#   https://autoforgenexus-backend-production.<account-subdomain>.workers.dev
# Current Deployment ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**確認:**
- [x] Production デプロイが成功した
- [x] Production Workers URLが発行された
- [x] `workers_dev = false`設定が反映されている

##### ステップ3: Production Workers動作確認

```bash
# Production Workers URLを環境変数に保存
export PROD_WORKERS_URL="https://autoforgenexus-backend-production.<account-subdomain>.workers.dev"

# ヘルスチェック
curl $PROD_WORKERS_URL/health | jq '.'

# 期待される出力:
# {
#   "status": "healthy",
#   "database": "connected",
#   "redis": "connected",
#   "environment": "production"
# }
```

**確認:**
- [x] Production `/health`が正常応答
- [x] `environment: "production"`が返される
- [x] Production DBとRedisに接続している

---

### G-3: フロントエンドProduction デプロイ（10分）

#### 🛠️ 実行手順

##### ステップ1: Cloudflare Pages Production環境変数設定

```bash
# Cloudflare Dashboard → Pages → autoforgenexus-frontend → Settings → Environment variables

# Production環境（mainブランチ）用に以下を設定:
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=<PROD_CLERK_PUBLIC_KEYの値>
CLERK_SECRET_KEY=<PROD_CLERK_SECRET_KEYの値>
NEXT_PUBLIC_API_URL=<PROD_WORKERS_URLの値>
NEXT_PUBLIC_APP_ENV=production

# 保存
```

**確認:**
- [x] Production環境変数が設定された
- [x] Production Clerk Keyが設定された
- [x] API URLがProduction Workers URLに設定された

##### ステップ2: mainブランチへマージ→自動デプロイ

```bash
cd /Users/dm/dev/dev/個人開発/AutoForgeNexus

# 現在のブランチ確認
git branch

# mainブランチにマージ（Production デプロイトリガー）
git checkout main
git merge staging --no-ff -m "deploy: Production環境デプロイ準備完了"

# リモートにプッシュ（GitHub Actions自動デプロイ）
git push origin main

# GitHub Actionsワークフロー監視
gh run watch

# 期待される出力:
# ✅ Deploy to Cloudflare Pages - production
#    Deployed to: https://autoforgenexus.pages.dev
```

**確認:**
- [x] mainブランチへのマージが成功した
- [x] GitHub Actionsが自動実行された
- [x] Cloudflare Pagesデプロイが成功した

##### ステップ3: Production Pages動作確認

```bash
# Production Pages URL
export PROD_PAGES_URL="https://autoforgenexus.pages.dev"

# トップページ確認
curl -I $PROD_PAGES_URL

# 期待される出力:
# HTTP/2 200
# content-type: text/html; charset=utf-8
# ...

# ブラウザでアクセス
open $PROD_PAGES_URL
```

**確認:**
- [x] Production トップページが表示される
- [x] Clerk認証UIが表示される
- [x] Production APIに接続できる

---

### G-4: Production環境最終確認（5分）

#### 🛠️ 実行手順

##### ステップ1: Production認証フロー確認

```bash
# ブラウザで以下の手順を実行:

# 1. Production URLにアクセス
open $PROD_PAGES_URL

# 2. 本番環境用ユーザーでサインアップ
# （Staging用とは別のユーザー）

# 3. 認証フロー確認:
#    - サインアップ → /onboarding
#    - ログアウト → トップページ
#    - ログイン → /dashboard
```

**確認:**
- [x] Production環境でClerk認証が動作している
- [x] Staging環境とは別のユーザーDBが使用されている
- [x] すべてのリダイレクトが正常

##### ステップ2: Production API統合確認

```bash
# ブラウザ開発者ツール（Console）で実行:

fetch('$PROD_WORKERS_URL/health')
  .then(res => res.json())
  .then(data => console.log('Production Health:', data));

# 期待される出力:
# Production Health: {
#   status: "healthy",
#   database: "connected",
#   redis: "connected",
#   environment: "production"
# }
```

**確認:**
- [x] Production バックエンドAPIが正常応答
- [x] Production DBに接続している
- [x] Production Redisに接続している

##### ステップ3: Production情報記録

```bash
# Production URL情報を記録
cat > ~/production-urls.txt << EOF
# AutoForgeNexus Production環境情報
# デプロイ日時: $(date)

# フロントエンド
PROD_PAGES_URL=$PROD_PAGES_URL

# バックエンド
PROD_WORKERS_URL=$PROD_WORKERS_URL

# データベース
PROD_TURSO_URL=$(turso db show autoforgenexus-production --url)

# 監視
# Grafana: http://localhost:3001（ローカル）
# LangFuse: http://localhost:3002（ローカル）
EOF

chmod 600 ~/production-urls.txt

# 内容確認
cat ~/production-urls.txt
```

**確認:**
- [x] Production URL情報が記録された
- [x] ファイル権限が600に設定された

---

## ✅ Phase G 完了確認

以下のProduction デプロイが完了しましたか？

### バックエンドProduction デプロイ
- [x] Cloudflare Workers Secrets（Production）が設定された（7個）
- [x] Workers Production デプロイが成功した
- [x] Production Workers URLが発行された
- [x] `/health`が`environment: "production"`を返す

### フロントエンドProduction デプロイ
- [x] Cloudflare Pages Production環境変数が設定された
- [x] mainブランチへのマージが完了した
- [x] GitHub Actions自動デプロイが成功した
- [x] Production Pages URLが稼働している

### Production環境確認
- [x] Clerk認証が正常動作している
- [x] Production DBに接続している
- [x] Production APIが正常応答している

### 本番稼働準備
- [x] Production URL情報が記録された
- [x] Staging/Production環境が分離されている
- [x] すべてのSecretsが環境別に設定されている

---

## 🎉 全Phase完了！

おめでとうございます！AutoForgeNexusのデプロイメントがすべて完了しました。

### 📊 構築した環境

| 環境 | URL | データベース | 用途 |
|------|-----|-------------|------|
| **Local** | http://localhost:3000 | Staging DB | ローカル開発 |
| **Staging** | https://staging.autoforgenexus.pages.dev | Staging DB | テスト環境 |
| **Production** | https://autoforgenexus.pages.dev | Production DB | 本番環境 |

### 🔐 セキュリティ確認

- [x] すべてのSecretsがGitHub Secretsで管理されている
- [x] 環境変数ファイルが.gitignoreに含まれている
- [x] 一時保存ファイル（~/\*-keys.txt）が安全に保管されている
- [x] Staging/Production環境が完全に分離されている

### 📝 次のステップ

1. **監視設定**: Grafana/LangFuseダッシュボード設定
2. **カスタムドメイン**: 独自ドメイン設定（オプション）
3. **CI/CDパイプライン**: GitHub Actions最適化
4. **パフォーマンス監視**: Core Web Vitals継続監視

---

## トラブルシューティング

デプロイ中に問題が発生した場合の対処方法をまとめます。

### 🚨 よくある問題と解決策

#### 問題1: GitHub Secrets登録エラー

**症状:**
```bash
gh secret set STAGING_CLERK_PUBLIC_KEY ...
# Error: HTTP 403: Resource not accessible by integration
```

**原因:**
- GitHubリポジトリのAdmin権限がない
- Personal Access Token（PAT）の権限不足

**解決策:**
```bash
# 1. リポジトリAdmin権限確認
gh repo view daishiman/AutoForgeNexus --json permissions

# 2. 権限がない場合、オーナーに依頼
# または、Personal Access Token（PAT）を再作成

# 3. PATで再認証
gh auth login --with-token < ~/github-pat.txt

# 4. Secrets登録を再試行
gh secret set STAGING_CLERK_PUBLIC_KEY --body "..."
```

---

#### 問題2: Turso接続エラー

**症状:**
```bash
turso db shell autoforgenexus
# Error: database not found
```

**原因:**
- データベース名が間違っている
- Turso認証が切れている

**解決策:**
```bash
# 1. Turso再認証
turso auth login

# 2. データベース一覧確認
turso db list

# 3. 正しいデータベース名で接続
turso db shell <正しいDB名>

# 4. 新しいトークン生成
turso db tokens create <DB名> --expiration 90d
```

---

#### 問題3: Wrangler デプロイエラー

**症状:**
```bash
wrangler deploy --env staging
# Error: No account_id found
```

**原因:**
- `wrangler.toml`に`account_id`が設定されていない
- Wrangler認証が切れている

**解決策:**
```bash
# 1. Wrangler再認証
wrangler login

# 2. Account ID確認
wrangler whoami

# 3. wrangler.tomlにaccount_id追加
# （Phase B-4のステップを再実行）

# 4. デプロイ再試行
wrangler deploy --env staging
```

---

#### 問題4: Cloudflare Pages環境変数エラー

**症状:**
- フロントエンドで`process.env.NEXT_PUBLIC_API_URL`が`undefined`

**原因:**
- Pages環境変数が設定されていない
- ビルド時に環境変数が読み込まれていない

**解決策:**
```bash
# 1. Cloudflare Dashboard → Pages → Settings → Environment variables確認

# 2. 環境変数が設定されているか確認
# Production: NEXT_PUBLIC_API_URL = https://...

# 3. 設定されていない場合、手動で追加

# 4. Pagesを再デプロイ
git commit --allow-empty -m "redeploy: 環境変数反映"
git push origin main

# 5. デプロイ完了後、ブラウザで確認
# Console: console.log(process.env.NEXT_PUBLIC_API_URL)
```

---

#### 問題5: Clerk認証エラー

**症状:**
- ログインボタンをクリックしても反応しない
- `Clerk: Missing publishableKey`エラー

**原因:**
- Clerk Public Keyが設定されていない
- 環境変数名が間違っている

**解決策:**
```bash
# 1. フロントエンド環境変数確認
cat frontend/.env.local | grep CLERK

# 2. 正しい環境変数名を確認
# NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY（NEXT_PUBLIC_プレフィックス必須）

# 3. 環境変数を修正
cat > frontend/.env.local << EOF
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
...
EOF

# 4. 開発サーバー再起動
pnpm dev --turbo
```

---

#### 問題6: Redis接続エラー

**症状:**
```bash
curl https://xxx.upstash.io/ping -H "Authorization: Bearer TOKEN"
# Error: Unauthorized
```

**原因:**
- Redis REST Tokenが間違っている
- TokenとPasswordを混同している

**解決策:**
```bash
# 1. Upstash Dashboard → Details → REST Token確認
# REST Token（AURsAAInc...で始まる）を使用

# 2. 環境変数を修正
# REDIS_REST_TOKEN=AURsAAInc...（正しいREST Token）

# 3. 接続テスト再実行
curl https://xxx.upstash.io/ping \
  -H "Authorization: Bearer AURsAAInc..."

# 期待される出力: {"result":"PONG"}
```

---

#### 問題7: OpenAI/Anthropic API制限エラー

**症状:**
```bash
curl https://api.openai.com/v1/models -H "Authorization: Bearer sk-..."
# Error: You exceeded your current quota
```

**原因:**
- API利用制限に達した
- クレジットカード未登録

**解決策:**
```bash
# 1. OpenAI Dashboard → Billing → Usage確認

# 2. 利用制限確認
# Hard limit: $50/月
# Current usage: $xx.xx

# 3. 必要に応じて制限を引き上げ
# Billing → Usage limits → Hard limitを$100に変更

# 4. クレジットカード登録確認
# Billing → Payment methods

# 5. API接続テスト再実行
```

---

#### 問題8: Docker Composeエラー

**症状:**
```bash
docker-compose up -d
# ERROR: The Compose file is invalid
```

**原因:**
- `docker-compose.dev.yml`の構文エラー
- Dockerデーモンが起動していない

**解決策:**
```bash
# 1. Docker起動確認
docker ps

# 2. Dockerが起動していない場合
open -a Docker

# 3. docker-compose.ymlの構文確認
docker-compose -f docker-compose.dev.yml config

# 4. エラー箇所を修正

# 5. 再起動
docker-compose -f docker-compose.dev.yml up -d
```

---

#### 問題9: pnpm installエラー

**症状:**
```bash
pnpm install
# ERR_PNPM_NO_MATCHING_VERSION  No matching version found for next@15.5.4
```

**原因:**
- pnpmバージョンが古い
- Node.jsバージョンが古い

**解決策:**
```bash
# 1. Node.js/pnpmバージョン確認
node --version  # 20.0+必須
pnpm --version  # 8.0+必須

# 2. Voltaで最新版インストール
volta install node@22
volta install pnpm@9

# 3. pnpm storeクリア
pnpm store prune

# 4. 再インストール
pnpm install
```

---

#### 問題10: GitHub Actions失敗

**症状:**
- GitHub Actionsワークフローが失敗する
- `Error: Process completed with exit code 1`

**原因:**
- GitHub Secretsが設定されていない
- ワークフロー構文エラー

**解決策:**
```bash
# 1. GitHub Actions ログ確認
gh run view --log-failed

# 2. Secrets設定確認
gh secret list

# 3. 不足しているSecretsを登録
gh secret set MISSING_SECRET --body "..."

# 4. ワークフロー再実行
gh run rerun <run-id>
```

---

### 📞 サポート情報

#### 公式ドキュメント

- **Clerk**: https://clerk.com/docs
- **Turso**: https://docs.turso.tech
- **Cloudflare Workers**: https://developers.cloudflare.com/workers
- **Next.js**: https://nextjs.org/docs
- **FastAPI**: https://fastapi.tiangolo.com

#### コミュニティサポート

- **GitHub Issues**: https://github.com/daishiman/AutoForgeNexus/issues
- **Discord**: AutoForgeNexus公式Discord（準備中）

#### 緊急時の連絡先

- **セキュリティ問題**: security@autoforgenexus.com
- **技術サポート**: support@autoforgenexus.com

---

## 📚 参考資料

### 関連ドキュメント

- [外部サービスセットアップガイド](./EXTERNAL_SERVICES_SETUP_GUIDE.md)
- [プロジェクトCLAUDE.md](../../CLAUDE.md)
- [セキュリティポリシー](../security/SECURITY_POLICY.md)

### 推奨学習リソース

1. **Cloudflare Workers Python**: https://developers.cloudflare.com/workers/languages/python
2. **Next.js 15.5 Turbopack**: https://nextjs.org/docs/architecture/turbopack
3. **React 19.0.0新機能**: https://react.dev/blog/2024/12/05/react-19
4. **Clerk認証ベストプラクティス**: https://clerk.com/docs/security/overview

---

**このガイドで、AutoForgeNexusのデプロイメントが完了しました！🎉**

**作成日**: 2025年10月5日
**最終更新**: 2025年10月5日
**バージョン**: 1.0.0
