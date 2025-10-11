# PR自動生成テンプレート

このファイルは、Claude CodeがPR作成時に参照するテンプレートです。

## PR作成時の自動処理

### 1. タイトル生成ルール

**ブランチ名からの自動生成**:
- `feature/auth-system` → `feat: Auth system`
- `bugfix/login-error` → `fix: Login error`
- `hotfix/critical-bug` → `fix: Critical bug`
- `docs/api-guide` → `docs: Api guide`
- `refactor/clean-code` → `refactor: Clean code`

**スコープの自動検出**:
最近のコミットメッセージから頻出スコープを検出:
- `feat: xxx` + `(frontend)` 多数 → `feat(frontend): xxx`
- `fix: xxx` + `(backend)` 多数 → `fix(backend): xxx`
- `docs: xxx` + `(ci)` 多数 → `docs(ci): xxx`

### 2. PR本文の自動生成

**変更内容からの推測**:
```markdown
## 概要
【最新コミットメッセージの詳細から生成】

## 変更内容
【git diff --stat から自動生成】
- 変更ファイル数: X件
- 追加行数: +XXX
- 削除行数: -XXX

## テスト結果
【CI/CD結果から自動生成】
- Backend: XX%+ coverage
- Frontend: XX%+ coverage
- CI/CD: 全パス

## 関連Issue
【コミットメッセージから自動抽出】
Closes #XXX

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### 3. ラベルの自動付与

**ファイルパスからの推測**:
- `.github/workflows/` → `ci/cd`
- `backend/` → `backend`
- `frontend/` → `frontend`
- `docs/` → `documentation`
- `*security*` → `security`

## Claude Code使用方法

### PR作成コマンド

```bash
# 自動タイトル生成付きPR作成
gh pr create --base develop

# Claude Codeが以下を自動実行:
# 1. .claude/scripts/generate-pr-title.sh でタイトル生成
# 2. コミット履歴から本文生成
# 3. ファイルパスからラベル推測
# 4. PRテンプレートに自動入力
```

### 手動タイトル上書き

```bash
# 自動生成を使わない場合
gh pr create --base develop --title "custom: My custom title"
```

## Conventional Commits検証

### 有効なタイプ

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: フォーマット
- `refactor`: リファクタリング
- `perf`: パフォーマンス
- `test`: テスト
- `build`: ビルド
- `ci`: CI設定
- `chore`: その他
- `revert`: 取り消し

### 有効なスコープ例

- `frontend`, `backend`, `ci`, `docs`, `test`, `api`, `auth`, `db`, `security`

### タイトル要件

- 長さ: 72文字以内推奨
- 形式: `<type>[(scope)]: <description>`
- 先頭: 小文字
- 説明: 空でない

## エラー時の自動修正

Claude Codeが検証エラーを検出した場合:

1. **自動提案**: 正しい形式のタイトルを提案
2. **対話的修正**: ユーザーに確認を求める
3. **再検証**: 修正後のタイトルを再度検証

---

**このテンプレートにより、Claude CodeはConventional Commits準拠のPRを自動生成できます**
