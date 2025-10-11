# Git Hooks Configuration

## 概要

このプロジェクトでは、コード品質と一貫性を保つためにGit
Hooksを活用しています。すべてのフックは `.githooks/`
ディレクトリに配置されています。

## セットアップ

Git Hooksは自動的に有効になっています：

```bash
# 手動で有効化する場合
git config core.hooksPath .githooks

# フックの実行権限を付与
chmod +x .githooks/*
```

## 実装されているフック

### 1. pre-commit

**目的**: コミット前の品質チェック

**チェック項目**:

- ✅ Pythonコード: Ruff linting、Black formatting
- ✅ TypeScript/JavaScript: ESLint
- ✅ 大容量ファイル警告 (>1MB)
- ✅ 秘密情報の漏洩防止
- ✅ .envファイルのコミット防止
- ✅ TODO/FIXME コメントの通知

### 2. commit-msg

**目的**: コミットメッセージの検証

**検証内容**:

- ✅ Conventional Commits形式の遵守
- ✅ メッセージ長の制限 (100文字以下推奨)
- ✅ Breaking Change の検出
- ✅ GitFlow/Merge コミットの許可

**有効なフォーマット**:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### 3. pre-push

**目的**: プッシュ前の最終検証

**チェック項目**:

- ✅ mainブランチへの直接プッシュ防止
- ✅ developブランチへのプッシュ警告
- ✅ テストの実行 (pytest, npm test)
- ✅ ビルドチェック (TypeScript compilation)
- ✅ ブランチ名の検証
- ✅ コミット数の確認

### 4. prepare-commit-msg

**目的**: コミットメッセージテンプレートの自動生成

**機能**:

- ブランチ名からtype/scopeを自動推定
- Conventional Commitsヘルパーテキスト表示
- コミットテンプレートの適用

## コミットメッセージテンプレート

`.gitmessage` ファイルがグローバルテンプレートとして設定されています：

```bash
# ローカル設定
git config commit.template .gitmessage
```

## トラブルシューティング

### フックが実行されない場合

```bash
# フックパスの確認
git config core.hooksPath

# 実行権限の確認
ls -la .githooks/

# 手動で権限付与
chmod +x .githooks/*
```

### フックをスキップする場合

```bash
# 緊急時のみ使用（推奨しない）
git commit --no-verify
git push --no-verify
```

### エラーメッセージ

| エラー                    | 解決方法                         |
| ------------------------- | -------------------------------- |
| `Ruff check failed`       | `ruff check --fix` で自動修正    |
| `Black formatting failed` | `black <files>` でフォーマット   |
| `ESLint check failed`     | `pnpm lint:fix` で自動修正       |
| `Tests failed`            | テストを修正してから再度コミット |
| `Commit message invalid`  | Conventional Commits形式に修正   |

## カスタマイズ

プロジェクト固有の要件に応じて、`.githooks/`
内のスクリプトを編集できます。変更後は必ず実行権限を付与してください：

```bash
chmod +x .githooks/<hook-name>
```

## 無効化

特定の開発者がフックを無効化する場合：

```bash
# 一時的に無効化
git config core.hooksPath /dev/null

# 再度有効化
git config core.hooksPath .githooks
```

---

**設定日**: 2025-09-26 **最終更新**: 2025-09-26
