# Docker環境セットアップガイド

## 🐳 Docker環境構築手順

### 前提条件
- Docker Desktop for Mac がインストール済み
- Docker Compose v2 が利用可能

### 1. Docker Desktop 起動

```bash
# Docker Desktop を起動
open /Applications/Docker.app

# Docker が起動したことを確認
docker --version
docker compose version
```

### 2. 環境ファイルの準備

```bash
# プロジェクトルートに移動
cd /path/to/AutoForgeNexus

# 環境変数ファイルをコピー（初回のみ）
cp .env.dev .env.local
```

### 3. Dockerイメージのビルド

```bash
# 全サービスをビルド
docker compose -f docker-compose.dev.yml build

# または個別にビルド
docker compose -f docker-compose.dev.yml build backend
docker compose -f docker-compose.dev.yml build frontend
docker compose -f docker-compose.dev.yml build redis
```

### 4. コンテナ起動

```bash
# 全サービスを起動（デタッチモード）
docker compose -f docker-compose.dev.yml up -d

# ログを確認
docker compose -f docker-compose.dev.yml logs -f

# 特定サービスのログを確認
docker compose -f docker-compose.dev.yml logs -f backend
```

### 5. サービス確認

#### アクセスURL
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Redis**: localhost:6379

#### ヘルスチェック
```bash
# Backend ヘルスチェック
curl http://localhost:8000/

# Frontend ヘルスチェック
curl http://localhost:3000/api/health

# コンテナ状態確認
docker compose -f docker-compose.dev.yml ps
```

### 6. 開発作業

#### コンテナ内でコマンド実行
```bash
# Backend コンテナでシェル起動
docker compose -f docker-compose.dev.yml exec backend /bin/bash

# マイグレーション実行
docker compose -f docker-compose.dev.yml exec backend alembic upgrade head

# テスト実行
docker compose -f docker-compose.dev.yml exec backend pytest tests/
```

#### ホットリロード
- Backend: ソースコード変更時に自動リロード（uvicorn --reload）
- Frontend: Turbopackによる高速ホットリロード

### 7. 停止・クリーンアップ

```bash
# コンテナ停止
docker compose -f docker-compose.dev.yml stop

# コンテナ停止＋削除
docker compose -f docker-compose.dev.yml down

# ボリュームも含めて完全削除
docker compose -f docker-compose.dev.yml down -v

# イメージも含めて完全削除
docker compose -f docker-compose.dev.yml down --rmi all
```

## 🔧 トラブルシューティング

### Docker Daemonが起動していない場合
```bash
# エラー: Cannot connect to the Docker daemon
# 解決策: Docker Desktop を起動
open /Applications/Docker.app
```

### ポートが既に使用中の場合
```bash
# 8000番ポートを使用しているプロセスを確認
lsof -i :8000

# プロセスを終了
kill -9 <PID>

# または uvicorn プロセスを全て終了
pkill -f uvicorn
```

### ビルドエラーの対処
```bash
# キャッシュを無視して再ビルド
docker compose -f docker-compose.dev.yml build --no-cache

# 不要なイメージ・コンテナを削除
docker system prune -a
```

### ログ確認
```bash
# 全サービスのログ
docker compose -f docker-compose.dev.yml logs

# リアルタイムログ監視
docker compose -f docker-compose.dev.yml logs -f --tail=100
```

## 📝 設定ファイル

### docker-compose.dev.yml
開発用Docker Compose設定ファイル
- Backend (FastAPI): ポート8000
- Frontend (Next.js): ポート3000
- Redis: ポート6379

### Dockerfile.dev
各サービスの開発用Dockerfile
- `backend/Dockerfile.dev`: Python 3.13 + FastAPI
- `frontend/Dockerfile.dev`: Node.js 22 + Next.js 15.5

### .env.dev
Docker環境用の環境変数設定ファイル

## 🚀 本番環境への移行

本番環境では以下のファイルを使用：
- `docker-compose.prod.yml`
- `Dockerfile` (最適化された本番用)
- `.env.production`

詳細は [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md) を参照。