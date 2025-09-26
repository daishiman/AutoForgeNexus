# GitHub セキュリティ機能の有効化ガイド

## 📍 設定場所への詳細な行き方

### ステップ1: リポジトリページを開く
```
https://github.com/daishiman/AutoForgeNexus
```

### ステップ2: Settings（設定）へ移動
- リポジトリ名の下にある **⚙️ Settings** タブをクリック
- もし見えない場合は、右端の「...」メニューから選択

### ステップ3: セキュリティ設定を開く
```
左サイドバー構成：
├── General
├── Access
├── Code and automation
│   ├── Actions
│   ├── Webhooks
│   └── Environments
└── Security
    └── 🔒 Code security and analysis  ← これをクリック！
```

## 🔐 有効化する機能（無料で利用可能）

### 1. Dependabot alerts（依存関係の脆弱性検出）
```
設定画面での表示：
┌─────────────────────────────────────┐
│ Dependabot alerts                   │
│ Get notified when one of your       │
│ dependencies has a vulnerability    │
│                                      │
│ [Disable] ← これを [Enable] に変更   │
└─────────────────────────────────────┘
```

**有効化方法**:
- 「Enable」ボタンをクリック
- 緑色のチェックマークが表示されたら完了

### 2. Dependabot security updates（自動セキュリティ更新）
```
設定画面での表示：
┌─────────────────────────────────────┐
│ Dependabot security updates         │
│ Allow Dependabot to open PRs to     │
│ update vulnerable dependencies      │
│                                      │
│ [Enable] をクリック                  │
└─────────────────────────────────────┘
```

**前提条件**: Dependabot alerts が有効になっていること

### 3. Code scanning（コードの脆弱性スキャン）
```
設定画面での表示：
┌─────────────────────────────────────┐
│ Code scanning                       │
│ Automatically scan code for         │
│ vulnerabilities and errors          │
│                                      │
│ [Set up] → [Default] を選択         │
└─────────────────────────────────────┘
```

**設定オプション**:
- **Default**: GitHub推奨の設定（簡単）
- **Advanced**: カスタマイズ可能（上級者向け）

### 4. Secret scanning（秘密情報の検出）
```
設定画面での表示：
┌─────────────────────────────────────┐
│ Secret scanning                     │
│ Receive alerts when secrets are     │
│ pushed to this repository          │
│                                      │
│ [Enable] をクリック                  │
└─────────────────────────────────────┘
```

**パブリックリポジトリ**: 自動的に有効
**プライベートリポジトリ**: 手動で有効化が必要

### 5. Push protection（プッシュ保護）
```
設定画面での表示：
┌─────────────────────────────────────┐
│ Push protection                     │
│ Block commits that contain          │
│ supported secrets                   │
│                                      │
│ [Enable] をクリック                  │
└─────────────────────────────────────┘
```

## ✅ 推奨設定チェックリスト

個人開発プロジェクトで有効化すべき機能：

- [x] **Dependabot alerts** - 必須
- [x] **Dependabot security updates** - 必須
- [x] **Code scanning** - 強く推奨
- [x] **Secret scanning** - 必須
- [x] **Push protection** - 強く推奨

## 📊 有効化後の確認方法

### 1. Security タブで確認
```
リポジトリページ → Security タブ
├── 🛡️ Security overview
├── 🔔 Dependabot alerts
├── 🔍 Code scanning alerts
└── 🔑 Secret scanning alerts
```

### 2. 通知設定の確認
```
Settings → Notifications
├── Email notifications
├── Web notifications
└── Mobile notifications (GitHub アプリ)
```

## 🚨 よくある質問

### Q: プライベートリポジトリでも無料？
**A**: 基本的なセキュリティ機能は無料です：
- Dependabot alerts: ✅ 無料
- Secret scanning: ✅ 無料
- Code scanning: ⚠️ 制限あり（月500分まで無料）

### Q: 有効化したらすぐに動く？
**A**: はい、以下のタイミングで自動実行：
- 即座: 既存コードのスキャン開始
- プッシュ時: 新しいコードをチェック
- 定期: 週1回の定期スキャン

### Q: 誤検出が多い場合は？
**A**: 以下の方法で調整可能：
1. `.github/dependabot.yml` で除外設定
2. Security タブで個別に「Dismiss」
3. 重要度でフィルタリング

## 💡 Tips

### 初回設定後にやること
1. **Security タブ**を開いて既存の警告を確認
2. **Critical/High** の警告から優先対応
3. **Dependabot PR** を確認してマージ
4. **通知設定**を調整（メール通知の頻度など）

### 個人開発での運用コツ
- 週1回は Security タブをチェック
- Dependabot PR は信頼してすぐマージ
- Critical 警告は24時間以内に対応
- 定期的に依存関係を整理

## 🔗 参考リンク

- [GitHub Docs - Security and analysis settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-security-and-analysis-settings-for-your-repository)
- [Dependabot alerts 設定ガイド](https://docs.github.com/en/code-security/dependabot/dependabot-alerts/configuring-dependabot-alerts)
- [Code scanning 設定ガイド](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/configuring-code-scanning-for-a-repository)