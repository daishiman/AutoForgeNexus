# AutoForgeNexus 推奨開発コマンド

## macOS/Darwin システム固有コマンド
```bash
# 基本システムコマンド
ls -la                    # ファイル一覧（詳細表示）
find . -name "*.py"       # Pythonファイル検索
grep -r "search_term" .   # 文字列検索
cd /path/to/directory     # ディレクトリ移動
```

## Phase別セットアップコマンド

### Phase 1: Git・基盤環境確認
```bash
git --version                    # Git 2.40+必須
node --version                   # Node.js 20.0+必須
pnpm --version                   # pnpm 8.0+必須
docker --version                 # Docker 24.0+必須
gh auth status                   # GitHub CLI認証確認
```

### Phase 2: Docker環境
```bash
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d
docker-compose logs -f
```

### Phase 3: バックエンド (Python 3.13/FastAPI)
```bash
cd backend
python3.13 -m venv venv
source venv/bin/activate
pip install -e .[dev]
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Phase 4: データベース・ベクトル環境
```bash
turso auth login
turso db create autoforgenexus
redis-server --daemonize yes --port 6379
alembic upgrade head
```

### Phase 5: フロントエンド (Next.js 15.5/React 19)
```bash
cd frontend
pnpm install
npx shadcn@canary init
pnpm dev --turbo               # Turbopack開発サーバー
```

## 品質・テストコマンド
```bash
# バックエンド品質チェック
ruff check src/ --fix           # Linting + 自動修正
ruff format src/                # フォーマット
mypy src/ --strict              # 型チェック (strict)
pytest tests/ --cov=src --cov-report=html --cov-fail-under=80

# フロントエンド品質チェック
pnpm build                      # Next.js本番ビルド
pnpm test                       # Jest単体テスト
pnpm test:e2e                   # Playwright E2Eテスト
pnpm lint                       # ESLint チェック
pnpm type-check                 # TypeScript検証
```

## Tursoデータベース操作
```bash
turso db show autoforgenexus       # データベース情報
turso db shell autoforgenexus     # SQLシェル
turso db create autoforgenexus-dev --from-db autoforgenexus
```

## タスク完了時の必須コマンド
1. `ruff check src/ --fix && ruff format src/` - Python品質チェック
2. `mypy src/ --strict` - 型チェック
3. `pytest tests/` - テスト実行
4. `pnpm lint && pnpm type-check` - フロントエンド品質チェック
5. `git status` - 変更確認