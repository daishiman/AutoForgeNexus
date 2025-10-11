# セキュリティドキュメント

このディレクトリには、プロジェクトのセキュリティ設定と管理に関するドキュメントが含まれています。

## 📚 ドキュメント一覧

### GitHub セキュリティ

- [github-setup-guide.md](./github-setup-guide.md) -
  GitHubセキュリティ機能の有効化ガイド
  - Dependabot設定
  - Code scanning設定
  - Secret scanning設定
  - Push protection設定

## 🔐 セキュリティ設定ファイル

### 依存関係管理

- [.github/dependabot.yml](../../.github/dependabot.yml) -
  Dependabot自動更新設定
- [.safety-policy.json](../../.safety-policy.json) -
  Python依存関係脆弱性チェック
- [audit-ci.json](../../audit-ci.json) - npm/pnpm脆弱性チェック設定

### コードスキャン

- [.github/workflows/codeql.yml](../../.github/workflows/codeql.yml) -
  CodeQLセキュリティスキャン
- [.github/workflows/security.yml](../../.github/workflows/security.yml) - 包括的セキュリティチェック
- [.bandit](../../.bandit) - Pythonセキュリティスキャン設定

### ポリシー

- [.github/SECURITY.md](../../.github/SECURITY.md) - セキュリティポリシー

## 🛡️ セキュリティチェックリスト

### 自動化設定

- [ ] Dependabot alerts 有効化
- [ ] Dependabot security updates 有効化
- [ ] Code scanning 有効化
- [ ] Secret scanning 有効化
- [ ] Push protection 有効化

### 定期確認項目（週次）

- [ ] Security タブの警告確認
- [ ] Dependabot PRのレビュー
- [ ] Critical/High脆弱性の対応
- [ ] セキュリティログの確認

### 緊急対応

- Critical脆弱性: 24時間以内
- High脆弱性: 3日以内
- Medium脆弱性: 1週間以内
- Low脆弱性: 次回リリース時

## 📊 セキュリティメトリクス

監視すべき指標：

- 未対応の脆弱性数
- 平均対応時間
- 依存関係の更新頻度
- セキュリティスキャンのパス率

## 🔗 参考リンク

- [GitHub Security Documentation](https://docs.github.com/en/code-security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
