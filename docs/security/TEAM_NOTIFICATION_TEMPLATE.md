# 🚨 チーム通知テンプレート

TruffleHogで秘密情報が検出された際のチーム通知用テンプレート

---

## 📧 メール・Slack通知テンプレート

### 件名

```
[SECURITY] TruffleHog秘密情報検出 - 即時対応必要
```

### 本文

````markdown
## 🚨 セキュリティアラート: 秘密情報検出

### 📊 検出サマリー

- **検出日時**: 2025年10月8日
- **検出ツール**: TruffleHog v3.82.13
- **影響範囲**: ワーキングディレクトリ（Git履歴はクリーン）
- **深刻度**: HIGH（本番環境トークン含む）

### 🔍 検出内容

- **Discord Webhook URL**: `.env`, `backend/.env.local`
- **Cloudflare API Token**: `.env`, `backend/.env.*`（複数環境ファイル）

### ✅ 安全確認

- ✅ Git履歴に秘密情報は含まれていない
- ✅ `.gitignore`は適切に設定済み
- ✅ Git履歴書き換え（git-filter-repo）は不要

### 🔒 即時対応（実施期限: 本日中）

**1. 秘密情報の無効化**

- Discord Webhook URL削除 → 新規作成
- Cloudflare API Token削除 → 新規発行

**2. GitHub Secretsへの移行**

```bash
gh secret set DISCORD_WEBHOOK_URL --body "new_webhook_url"
gh secret set CLOUDFLARE_API_TOKEN --body "new_api_token"
```
````

**3. ローカル環境の更新**

```bash
# 自動クリーンアップスクリプト実行
./scripts/security/cleanup-secrets.sh

# .env.exampleから開発用.envを作成
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 新しいトークンを設定
# （GitHub Secretsから取得またはチームリードから配布）
```

### 📋 詳細ドキュメント

- 対応計画: `docs/security/SECRET_REMEDIATION_PLAN.md`
- 実行スクリプト: `scripts/security/cleanup-secrets.sh`

### ⏰ タイムライン

| フェーズ                | 期限       | 責任者           |
| ----------------------- | ---------- | ---------------- |
| Phase 1: 秘密情報無効化 | 2025-10-08 | セキュリティ担当 |
| Phase 2: 環境整理       | 2025-10-09 | 開発チーム全員   |
| Phase 3: 自動検知強化   | 2025-10-10 | DevOps担当       |
| Phase 4: ドキュメント   | 2025-10-11 | テックリード     |

### 🚫 やってはいけないこと

- ❌ 既存の.envファイルをコミット
- ❌ 古いトークンを引き続き使用
- ❌ ローカル.envをチームメンバーと共有

### 📞 連絡先

- セキュリティ担当: [担当者名]
- テックリード: [担当者名]
- 緊急連絡先: [連絡先]

---

**このアラートを受け取ったら**:

1. 本メッセージを確認
2. 上記「即時対応」を実施
3. 完了後に返信またはチケット更新

```

---

## 💬 GitHub Issue テンプレート

### Issueタイトル
```

[SECURITY] TruffleHog秘密情報検出 - 環境ファイル整理

````

### Issue本文

```markdown
## 🚨 Issue概要

TruffleHogが秘密情報を検出したため、環境ファイルの整理と秘密情報のローテーションを実施します。

## 🔍 検出内容

- **検出ツール**: TruffleHog v3.82.13
- **検出日時**: 2025年10月8日
- **検出ファイル**:
  - `.env`
  - `backend/.env.local`
  - `backend/.env.production`
  - `backend/.env.staging`
  - その他複数の環境ファイル

- **検出秘密情報**:
  - Discord Webhook URL
  - Cloudflare API Token

## ✅ 診断結果

- ✅ Git履歴はクリーン（過去コミットに秘密情報なし）
- ✅ `.gitignore`は適切に設定済み
- ⚠️ ワーキングディレクトリに秘密情報が存在

## 📋 対応タスク

### Phase 1: 即時対応（CRITICAL）
- [ ] Discord Webhook URL無効化 + 再発行
- [ ] Cloudflare API Token削除 + 再発行
- [ ] GitHub Secretsに新トークン登録
- [ ] ローカル.envファイル更新

### Phase 2: 環境整理（HIGH）
- [ ] 不要な.envファイル削除（14 → 5ファイル）
- [ ] .env.exampleの最新化
- [ ] Cloudflare Workers環境変数設定
- [ ] CI/CDパイプライン動作確認

### Phase 3: 自動化強化（MEDIUM）
- [ ] pre-commit フック統合
- [ ] GitHub Actions秘密検知強化
- [ ] ベースライン設定（.secrets.baseline）
- [ ] 全ブランチでの検証実施

### Phase 4: ドキュメント（LOW）
- [ ] 環境変数管理ガイド作成
- [ ] セキュリティポリシー更新
- [ ] チーム通知・研修実施
- [ ] 定期監査手順確立

## 📚 関連ドキュメント

- [対応計画書](../security/SECRET_REMEDIATION_PLAN.md)
- [実行スクリプト](../../scripts/security/cleanup-secrets.sh)
- [セキュリティポリシー](../security/SECURITY_POLICY.md)

## 🔗 参考リンク

- [TruffleHog公式ドキュメント](https://github.com/trufflesecurity/trufflehog)
- [GitHub Secrets管理](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Cloudflare Workers Secrets](https://developers.cloudflare.com/workers/configuration/secrets/)

## ⏰ 期限

- **Phase 1**: 2025年10月8日中
- **Phase 2**: 2025年10月9日
- **Phase 3**: 2025年10月10日
- **Phase 4**: 2025年10月11日

## 👥 担当者

- **セキュリティ担当**: @security-team
- **DevOps担当**: @devops-team
- **テックリード**: @tech-lead

---

**ラベル**: `security`, `critical`, `tech-debt`
**マイルストーン**: Security Q4 2025
````

---

## 🎯 PR (Pull Request) テンプレート

### PRタイトル

```
fix(security): TruffleHog検出対応 - 環境ファイル整理とpre-commit強化
```

### PR説明

````markdown
## 📝 変更概要

TruffleHogで検出された秘密情報への対応として、環境ファイル整理とセキュリティ強化を実施しました。

## 🔍 関連Issue

Closes #XXX

## 🎯 変更内容

### セキュリティ対策

- ✅ 秘密情報を含む.envファイルを削除（Git履歴影響なし）
- ✅ GitHub Secretsに秘密情報を移行
- ✅ pre-commit フックにTruffleHog統合
- ✅ CI/CDパイプラインに秘密検知強化

### ファイル変更

- `docs/security/SECRET_REMEDIATION_PLAN.md` (新規作成)
- `scripts/security/cleanup-secrets.sh` (新規作成)
- `.pre-commit-config.yaml` (TruffleHog追加)
- `.github/workflows/security-scan.yml` (強化)

## ✅ チェックリスト

- [x] Discord Webhook URL無効化 + 再発行
- [x] Cloudflare API Token削除 + 再発行
- [x] GitHub Secretsに新トークン登録
- [x] 不要な.envファイル削除
- [x] pre-commit フック設定
- [x] TruffleHogスキャンで検出ゼロ確認
- [x] CI/CDパイプライン動作確認
- [x] ドキュメント作成

## 🧪 テスト方法

```bash
# 1. pre-commit フックのテスト
pre-commit run --all-files

# 2. TruffleHogスキャン
docker run --rm -v $(pwd):/tmp trufflesecurity/trufflehog:latest \
  git file:///tmp/ --only-verified

# 3. CI/CDパイプライン確認
gh workflow run security-scan.yml
```
````

## 📊 影響範囲

- **Git履歴**: 影響なし（クリーン維持）
- **開発環境**: .env.exampleから各自作成が必要
- **CI/CD**: GitHub Secrets統合により改善
- **本番環境**: Cloudflare Workers Secrets移行

## 🚀 デプロイ手順

1. PR承認後、mainブランチにマージ
2. 開発者は`.env.example`から`.env`を作成
3. 必要なトークンはチームリードから配布
4. pre-commitフック有効化: `pre-commit install`

## 📚 関連ドキュメント

- [対応計画書](docs/security/SECRET_REMEDIATION_PLAN.md)
- [実行スクリプト](scripts/security/cleanup-secrets.sh)

## 👥 レビュワー

@security-team @devops-team

---

**この変更により**:

- 🔒 秘密情報漏洩リスクゼロ化
- 🤖 自動検知による再発防止
- 📋 明確な管理プロセス確立

```

---

## 📱 Slack通知スニペット

### 緊急アラート用
```

🚨 **セキュリティアラート: TruffleHog秘密情報検出**

**影響範囲**: ワーキングディレクトリのみ（Git履歴クリーン） **深刻度**: HIGH

**即時対応必要**:

1. Discord Webhook + Cloudflare Token無効化
2. 新トークンをGitHub Secretsに登録
3. ローカル環境をクリーンアップ

詳細: docs/security/SECRET_REMEDIATION_PLAN.md

cc: @security-team @devops-team

```

### 完了通知用
```

✅ **TruffleHog秘密情報対応完了**

**実施内容**:

- 秘密情報のローテーション完了
- GitHub Secrets移行完了
- pre-commit フック統合完了
- TruffleHogスキャン: 検出ゼロ

**次のステップ**: 各開発者は`.env.example`から`.env`を作成してください。

詳細: PR #XXX

```

---

**作成日**: 2025年10月8日
**最終更新**: 2025年10月8日
**責任者**: version-control-specialist Agent
```
