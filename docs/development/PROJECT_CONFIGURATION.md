# Project Configuration

## プロジェクト設定ファイル

AutoForgeNexusプロジェクトの開発環境を統一するための設定ファイル群です。

## 設定ファイル一覧

### 1. EditorConfig (.editorconfig)

**目的**: エディタ間でのコーディングスタイル統一

**主な設定**:

- 文字コード: UTF-8
- 改行コード: LF (Unix形式)
- インデント: スペース使用
  - Python: 4スペース
  - TypeScript/JavaScript: 2スペース
  - YAML/JSON: 2スペース
- 末尾空白削除: 有効
- 最終行改行: 有効

### 2. Prettier (.prettierrc)

**目的**: JavaScript/TypeScript/JSON/Markdown等の自動フォーマット

**主な設定**:

- 行幅: 100文字
- タブ幅: 2スペース
- セミコロン: 必須
- シングルクォート: 使用（JSX除く）
- 末尾カンマ: ES5準拠
- アロー関数括弧: 常に付与

### 3. Git Attributes (.gitattributes)

**目的**: Git操作時のファイル属性制御

**主な機能**:

- 改行コード自動正規化 (LF)
- バイナリファイル識別
- 差分表示の最適化
- Git LFS設定（大容量ファイル）
- Linguist設定（言語統計）

### 4. VS Code設定 (.vscode/)

#### settings.json

- 保存時自動フォーマット
- Python: Black + Ruff + mypy
- TypeScript: ESLint + Prettier
- ファイル除外設定
- 拡張機能設定

#### extensions.json

推奨拡張機能リスト:

- Python開発ツール
- TypeScript/JavaScript開発ツール
- Git統合ツール
- Docker支援
- AI補完（GitHub Copilot）

#### launch.json

デバッグ設定:

- FastAPI サーバー起動
- Next.js 開発サーバー
- pytest デバッグ
- フルスタック同時起動

## 適用方法

### 1. 新規開発者セットアップ

```bash
# リポジトリクローン
git clone https://github.com/daishiman/AutoForgeNexus.git
cd AutoForgeNexus

# VS Code推奨拡張機能インストール
code --install-extension ms-python.python
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode

# EditorConfig対応確認
# VS Code: EditorConfig拡張機能
# JetBrains IDE: 標準サポート
# Vim: editorconfig-vim プラグイン
```

### 2. 自動フォーマット有効化

**VS Code**:

- 設定は自動適用（.vscode/settings.json）
- 保存時に自動フォーマット実行

**コマンドライン**:

```bash
# Python
black backend/
ruff check backend/ --fix

# TypeScript/JavaScript
cd frontend && pnpm prettier --write .
```

### 3. Git設定確認

```bash
# 改行コード設定確認
git config core.autocrlf

# Windows: input推奨
git config core.autocrlf input

# macOS/Linux: false推奨
git config core.autocrlf false
```

## トラブルシューティング

### フォーマット競合

問題: Prettier と ESLint の競合

```bash
# 解決方法
cd frontend
pnpm add -D eslint-config-prettier
```

### 改行コード問題

問題: CRLF/LF混在警告

```bash
# 全ファイルLF変換
find . -type f -not -path "./.git/*" -exec dos2unix {} \;

# または
git add --renormalize .
```

### Python環境問題

問題: Black/Ruff が動作しない

```bash
# 仮想環境確認
which python
which black
which ruff

# 再インストール
pip install --upgrade black ruff mypy
```

## カスタマイズ

プロジェクト固有の要件に応じて設定をカスタマイズできます：

1. `.editorconfig`: チーム標準に合わせて調整
2. `.prettierrc`: フォーマットルール変更
3. `.vscode/settings.json`: 個人設定は `settings.json` (workspace)に記載

## 関連ドキュメント

- [GitFlow Configuration](./git/GITFLOW_CONFIGURATION.md)
- [Git Hooks Configuration](./git/GIT_HOOKS_CONFIGURATION.md)
- [Development Guidelines](./DEVELOPMENT_GUIDELINES.md)

---

**設定日**: 2025-09-26 **最終更新**: 2025-09-26
