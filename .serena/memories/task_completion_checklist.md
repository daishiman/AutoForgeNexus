# AutoForgeNexus タスク完了時チェックリスト

## 必須実行項目（順序重要）

### 1. コード品質チェック
```bash
# Python (バックエンド)
ruff check src/ --fix           # Linting + 自動修正
ruff format src/                # フォーマット
mypy src/ --strict              # 型チェック (strict)

# TypeScript (フロントエンド)
pnpm lint                       # ESLint チェック
pnpm type-check                 # TypeScript検証
```

### 2. テスト実行
```bash
# バックエンドテスト
pytest tests/ --cov=src --cov-report=html --cov-fail-under=80

# フロントエンドテスト
pnpm test                       # Jest単体テスト
pnpm test:e2e                   # Playwright E2Eテスト（必要時）
```

### 3. ビルド検証
```bash
# バックエンドビルド検証
python -m src.main              # アプリケーション起動確認

# フロントエンドビルド
pnpm build                      # Next.js本番ビルド
```

### 4. Git操作前確認
```bash
git status                      # 変更ファイル確認
git diff                        # 差分確認
git add .                       # ステージング
git commit -m "feat: 説明的なコミットメッセージ"
```

## 品質ゲート
- [ ] 全自動テストがpass
- [ ] カバレッジが基準値以上（バックエンド80%+、フロントエンド75%+）
- [ ] 型チェックエラーなし
- [ ] Linting警告なし
- [ ] ビルドエラーなし
- [ ] 実行時エラーなし

## 任意実行項目
- セキュリティスキャン（重要機能変更時）
- パフォーマンステスト（パフォーマンス影響時）
- ドキュメント更新（API変更時）

## 緊急リリース時の最小チェック
1. `pytest tests/` - 最低限のテスト実行
2. `pnpm type-check` - 型チェック
3. `git status && git diff` - 変更確認