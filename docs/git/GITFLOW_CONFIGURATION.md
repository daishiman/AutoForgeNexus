# GitFlow Configuration

## ブランチ戦略

このプロジェクトではGitFlowワークフローを採用しています。

### ブランチ構成

| ブランチタイプ | ブランチ名 | 説明 | マージ先 |
|------------|---------|------|----------|
| Production | `main` | 本番環境リリース用ブランチ | - |
| Development | `develop` | 開発統合ブランチ | `main` |
| Feature | `feature/*` | 機能開発ブランチ | `develop` |
| Release | `release/*` | リリース準備ブランチ | `main`, `develop` |
| Hotfix | `hotfix/*` | 緊急修正ブランチ | `main`, `develop` |
| Support | `support/*` | 長期サポートブランチ | - |

### GitFlow設定値

```
Production branch: main
Development branch: develop
Feature branch prefix: feature/
Release branch prefix: release/
Hotfix branch prefix: hotfix/
Support branch prefix: support/
Version tag prefix: v
```

## ワークフロー

### 1. 機能開発

```bash
# 機能ブランチの作成
git flow feature start <feature-name>

# 開発作業
git add .
git commit -m "feat: <description>"

# 機能ブランチの終了
git flow feature finish <feature-name>
```

### 2. リリース準備

```bash
# リリースブランチの作成
git flow release start <version>

# バージョン更新とテスト
# ...

# リリースの完了
git flow release finish <version>
```

### 3. ホットフィックス

```bash
# ホットフィックスブランチの作成
git flow hotfix start <version>

# 修正作業
# ...

# ホットフィックスの完了
git flow hotfix finish <version>
```

## コミットメッセージ規約

[Conventional Commits](https://www.conventionalcommits.org/)に準拠：

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント変更
- `style`: コードフォーマット変更
- `refactor`: リファクタリング
- `perf`: パフォーマンス改善
- `test`: テスト追加・修正
- `chore`: ビルドプロセスや補助ツールの変更
- `ci`: CI/CD設定の変更

## マージ戦略

- `develop` → `main`: --no-ff（マージコミット作成）
- `feature` → `develop`: --no-ff（履歴保持）
- `hotfix` → `main`/`develop`: --no-ff（追跡性確保）

## 初期化日時

- 初期化日: 2025-09-26
- GitFlowバージョン: AVH Edition