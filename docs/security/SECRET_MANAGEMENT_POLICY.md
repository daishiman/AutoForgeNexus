# 秘密情報管理ポリシー

**文書番号**: SEC-POL-2025-001 **発効日**: 2025年10月8日 **適用範囲**:
AutoForgeNexusプロジェクト全体 **承認者**: security-architect Agent
**レビューサイクル**: 四半期ごと

---

## 1. ポリシー概要

### 1.1 目的

本ポリシーは、AutoForgeNexusプロジェクトにおける秘密情報（API キー、認証トークン、パスワード等）の管理方法を標準化し、情報漏洩リスクを最小化することを目的とします。

### 1.2 適用対象

- すべての開発者
- DevOpsエンジニア
- セキュリティチーム
- プロジェクトマネージャー

### 1.3 定義

| 用語                       | 定義                                                                                                                   |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **秘密情報**               | API キー、認証トークン、パスワード、暗号鍵、証明書など、認可されていないアクセスによって被害が発生する可能性のある情報 |
| **環境変数**               | アプリケーション実行時に外部から注入される設定値                                                                       |
| **シークレット管理ツール** | GitHub Secrets、HashiCorp Vault、AWS Secrets Manager等の秘密情報専用管理システム                                       |

---

## 2. 秘密情報の分類

### 2.1 リスクレベル分類

| レベル       | 定義                         | 例                           | 漏洩時の対応時間 |
| ------------ | ---------------------------- | ---------------------------- | ---------------- |
| **Critical** | 本番環境への直接アクセス権限 | 本番DB認証情報、本番API キー | 即座（15分以内） |
| **High**     | ステージング環境アクセス権限 | ステージングDB認証情報       | 1時間以内        |
| **Medium**   | 開発環境アクセス権限         | 開発環境API キー             | 1日以内          |
| **Low**      | 通知・ログ送信権限のみ       | Discord Webhook              | 1週間以内        |

### 2.2 秘密情報の種類

#### 🔴 Critical

- **LLM API キー** (OpenAI, Anthropic, Google AI等)
- **データベース認証情報** (Turso Auth Token)
- **暗号鍵** (JWT Secret Key, AES Key)
- **認証プロバイダー秘密鍵** (Clerk Secret Key)

#### 🟡 High

- **インフラAPI トークン** (Cloudflare API Token)
- **監視サービスキー** (LangFuse Secret Key)
- **ストレージ認証情報** (S3 Access Key)

#### 🟢 Medium

- **通知Webhook** (Discord, Slack)
- **開発環境API キー**
- **テスト用ダミー値**

---

## 3. 秘密情報の保存方法

### 3.1 禁止事項（絶対に守る）

❌ **以下の場所への秘密情報保存は絶対禁止**

1. ソースコード内へのハードコード
2. Gitリポジトリへのコミット
3. コミットメッセージ
4. Pull Request説明文
5. GitHub Issues
6. Slack/Discord メッセージ
7. メール
8. 共有ドキュメント（Google Docs, Notion等）

### 3.2 許可された保存場所

#### ローカル開発環境

✅ **`.env`ファイル（.gitignore対象）**

```bash
# プロジェクトルート/.env
OPENAI_API_KEY=sk-proj-your-actual-key
ANTHROPIC_API_KEY=sk-ant-your-actual-key

# 必須条件:
# 1. .gitignore に .env が含まれている
# 2. git status で Untracked と表示される
```

#### CI/CD環境

✅ **GitHub Secrets**

```yaml
# .github/workflows/deploy.yml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

**登録方法**:

```bash
gh secret set OPENAI_API_KEY --repo daishiman/AutoForgeNexus
```

#### 本番環境

✅ **Cloudflare Workers環境変数**

```bash
# Cloudflare Workers へ秘密情報を設定
wrangler secret put OPENAI_API_KEY

# ステージング環境
wrangler secret put --env staging OPENAI_API_KEY
```

---

## 4. 秘密情報のライフサイクル管理

### 4.1 生成

#### 要件

- 十分なエントロピー（ランダム性）
- 推測困難な長さ（最低32文字）
- 定期的なローテーション

#### 生成方法

```bash
# JWT Secret Key生成
openssl rand -hex 32

# UUID生成
uuidgen

# 強力なパスワード生成
openssl rand -base64 48 | tr -d "=+/" | cut -c1-32
```

### 4.2 配布

#### 新規開発者への配布手順

1. **GitHub Secrets権限付与**

   - リポジトリ管理者が権限設定
   - Settings → Collaborators → Add people → Write権限

2. **ローカル環境セットアップ**

   ```bash
   # .env.example をコピー
   cp .env.example .env

   # 安全な方法で秘密情報を受け取る
   # (1対1のセキュアチャネル経由)
   ```

3. **動作確認**
   ```bash
   # 秘密情報が正しく読み込まれるか確認
   python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
   ```

### 4.3 ローテーション（定期更新）

#### ローテーション頻度

| 秘密情報タイプ     | 頻度       | 理由               |
| ------------------ | ---------- | ------------------ |
| 本番環境DB認証情報 | 90日ごと   | 規制要件           |
| LLM API キー       | 180日ごと  | ベストプラクティス |
| JWT Secret Key     | 365日ごと  | セキュリティ標準   |
| Webhook URL        | 漏洩時のみ | 低リスク           |

#### ローテーション手順

```bash
# 1. 新しい秘密情報を生成
NEW_KEY=$(openssl rand -hex 32)

# 2. 新しい秘密情報をGitHub Secretsに追加
gh secret set OPENAI_API_KEY_NEW --body "$NEW_KEY"

# 3. アプリケーションを新しい秘密情報で動作確認

# 4. 古い秘密情報を削除
gh secret delete OPENAI_API_KEY

# 5. 新しい秘密情報を正式名称にリネーム
gh secret set OPENAI_API_KEY --body "$NEW_KEY"
```

### 4.4 無効化（漏洩時対応）

#### 即座に実行（5分以内）

1. **秘密情報を無効化**

   - API プロバイダーの管理画面で削除/無効化
   - トークンの取り消し

2. **インシデント報告**

   ```bash
   gh issue create \
     --title "🚨 [SECURITY] Secret Leaked: [種類]" \
     --label "security,incident,P0"
   ```

3. **新しい秘密情報を生成・配布**

---

## 5. 技術的統制

### 5.1 pre-commitフック（必須）

#### セットアップ

```bash
# 初回セットアップ（全開発者必須）
./scripts/security/setup-pre-commit.sh
```

#### 動作

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/trufflesecurity/trufflehog
    hooks:
      - id: trufflehog-git # Git履歴スキャン
      - id: trufflehog-filesystem # ファイルシステムスキャン

  - repo: https://github.com/gitleaks/gitleaks
    hooks:
      - id: gitleaks # 追加スキャン
```

**効果**: コミット時に自動で秘密情報を検出し、コミットをブロック

### 5.2 CI/CD統合（自動実行）

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  pull_request:
  push:
    branches: [main, develop]

jobs:
  trufflehog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # 全履歴取得

      - name: TruffleHog Scan
        run: |
          docker run --rm -v "$PWD:/workdir" \
            trufflesecurity/trufflehog:latest \
            git file:///workdir --only-verified --fail
```

**効果**: PR作成時・マージ時に自動スキャン、問題があればマージブロック

### 5.3 定期スキャン（バックグラウンド）

```yaml
# .github/workflows/scheduled-security-scan.yml
name: Scheduled Security Scan

on:
  schedule:
    - cron: '0 2 * * 1' # 毎週月曜2:00 AM (JST 11:00 AM)

jobs:
  full-scan:
    runs-on: ubuntu-latest
    steps:
      - name: TruffleHog Full History Scan
        run: |
          docker run --rm -v "$PWD:/workdir" \
            trufflesecurity/trufflehog:latest \
            git file:///workdir --since-commit "" --only-verified
```

**効果**: 週次で全履歴をスキャン、見逃しを防止

---

## 6. インシデント対応手順

### 6.1 検出フロー

```
秘密情報検出（TruffleHog/Gitleaks）
  ↓
分類（Critical/High/Medium/Low）
  ↓
[Critical/High]
  ├─ 即座に秘密情報を無効化（5分以内）
  ├─ インシデント報告（GitHub Issue）
  ├─ 新しい秘密情報を生成・配布（1時間以内）
  └─ 事後レポート作成（24時間以内）
  ↓
[Medium/Low]
  ├─ Issue登録（1日以内）
  ├─ 計画的に秘密情報を更新（1週間以内）
  └─ 影響調査
```

### 6.2 対応時間 SLA

| リスクレベル | 無効化 | 報告  | 復旧  | 事後報告 |
| ------------ | ------ | ----- | ----- | -------- |
| Critical     | 5分    | 15分  | 1時間 | 24時間   |
| High         | 15分   | 1時間 | 4時間 | 48時間   |
| Medium       | 1時間  | 4時間 | 1日   | 1週間    |
| Low          | 1日    | 1週間 | 2週間 | 1ヶ月    |

### 6.3 報告テンプレート

```markdown
## セキュリティインシデント報告

**インシデントID**: SEC-INC-[YYYY-MM-DD]-[連番] **検出日時**: YYYY-MM-DD
HH:MM:SS **検出者**: [氏名] **リスクレベル**: Critical/High/Medium/Low

### 検出内容

- **秘密情報の種類**: [API Key/Token/Password等]
- **検出場所**: [Git履歴/ファイルシステム/ログ等]
- **漏洩範囲**: [ローカル/GitHub/本番環境等]

### 影響範囲

- **影響を受けるシステム**: [システム名]
- **漏洩期間**: [開始日時] - [検出日時]
- **アクセス可能性**: [公開/非公開]

### 対応履歴

- [ ] 秘密情報無効化（実施日時: ）
- [ ] 新しい秘密情報生成（実施日時: ）
- [ ] GitHub Secrets更新（実施日時: ）
- [ ] Git履歴クリーンアップ（実施日時: ）
```

---

## 7. 監査とコンプライアンス

### 7.1 定期監査

| 監査項目                  | 頻度   | 実施者             |
| ------------------------- | ------ | ------------------ |
| GitHub Secrets棚卸し      | 月次   | DevOps             |
| 秘密情報使用状況レビュー  | 四半期 | security-architect |
| pre-commitフック動作確認  | 週次   | 各開発者           |
| CI/CDスキャン結果レビュー | 週次   | DevOps             |

### 7.2 コンプライアンス要件

#### GDPR準拠

- 秘密情報は暗号化保存（AES-256）
- アクセスログの記録（最低90日保管）
- データポータビリティ対応
- 忘れられる権利（秘密情報削除要求への対応）

#### SOC 2 Type II準拠

- 秘密情報へのアクセス制御
- 変更履歴の記録
- 定期的なアクセスレビュー
- インシデント対応手順の文書化

---

## 8. トレーニングと意識向上

### 8.1 必須トレーニング

| 対象       | トレーニング内容               | 頻度   |
| ---------- | ------------------------------ | ------ |
| 新規開発者 | セキュリティオンボーディング   | 入社時 |
| 全開発者   | 秘密情報管理ベストプラクティス | 四半期 |
| DevOps     | インシデント対応演習           | 半年   |

### 8.2 意識向上施策

- 月次セキュリティニュースレター
- セキュリティインシデント事例共有
- セキュリティチャンピオン制度

---

## 9. 例外処理

### 9.1 例外申請

本ポリシーの例外を申請する場合は、以下の手順に従う：

1. **例外申請書作成**

   - 例外が必要な理由
   - 代替統制手段
   - リスク評価

2. **承認プロセス**

   - security-architect レビュー
   - プロジェクトリード承認
   - 期限付き例外（最大90日）

3. **例外記録**
   - GitHub Issue で記録
   - 定期レビュー

---

## 10. ポリシー違反

### 10.1 違反の定義

以下の行為はポリシー違反とみなされる：

- 秘密情報のGitコミット
- 秘密情報の非安全な共有
- pre-commitフックの無効化
- 秘密情報漏洩の未報告

### 10.2 対応

| 違反レベル   | 対応                   |
| ------------ | ---------------------- |
| 初回（軽微） | 警告・再教育           |
| 複数回       | アクセス権限の一時停止 |
| 重大な違反   | プロジェクトからの除外 |

---

## 11. 関連ドキュメント

- [セキュリティインシデント対応レポート](./INCIDENT_RESPONSE_REPORT_2025-10-08.md)
- [開発者向けセキュリティガイド](./DEVELOPER_SECURITY_GUIDE.md)
- [インシデント対応プレイブック](./INCIDENT_RESPONSE_PLAYBOOK.md)（作成予定）

---

## 12. ポリシー管理

| 項目         | 値                       |
| ------------ | ------------------------ |
| 発効日       | 2025年10月8日            |
| 次回レビュー | 2026年1月8日             |
| 承認者       | security-architect Agent |
| バージョン   | 1.0                      |

### 変更履歴

| バージョン | 日付       | 変更内容 | 承認者             |
| ---------- | ---------- | -------- | ------------------ |
| 1.0        | 2025-10-08 | 初版作成 | security-architect |

---

**このポリシーは全チームメンバーに適用されます。違反は重大なセキュリティインシデントにつながる可能性があります。**

🤖 Generated with [Claude Code](https://claude.com/claude-code)
