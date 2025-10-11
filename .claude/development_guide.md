# AutoForgeNexus 開発環境ガイド

## フロントエンド開発のDocker要件

### 🤔 Dockerは必要？

**結論**: 必須ではないが、推奨

### 📋 開発方法の選択肢

#### 1. **ローカル開発（非Docker）**

```bash
# 前提条件
node -v    # v18.19.0+ 必要
pnpm -v    # v9.1.0+ 必要

# フロントエンド開発
cd packages/frontend  # 作成予定
pnpm dev              # http://localhost:3000
```

**メリット**:

- ✅ 高速起動・HMR（Hot Module Replacement）
- ✅ IDEとの統合が容易
- ✅ デバッグツールの直接利用

**デメリット**:

- ❌ 環境差異の可能性
- ❌ バックエンド統合で複雑性

#### 2. **Docker統合開発（推奨）**

```bash
# 統合環境起動
docker-compose -f docker-compose.dev.yml up

# 個別サービス起動
docker-compose -f docker-compose.dev.yml up frontend
```

**メリット**:

- ✅ 環境統一（Node 18.19.0固定）
- ✅ バックエンド(Python 3.13)と同時起動
- ✅ Redis、LangFuse等の依存サービス自動起動
- ✅ チーム開発での一貫性

**デメリット**:

- ❌ 初回ビルド時間
- ❌ Docker知識が必要

### 🏗️ 既存Docker設定

現在の`docker-compose.dev.yml`にフロントエンド設定済み：

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile.dev
    args:
      NODE_VERSION: 18
  ports:
    - '3000:3000'
  volumes:
    - ./frontend:/app
    - /app/node_modules
    - /app/.next
```

### 🎯 推奨開発フロー

#### 開発開始時

```bash
# 1. 依存関係インストール
pnpm install

# 2. 開発方法選択
# オプションA: ローカル開発
pnpm dev:frontend

# オプションB: Docker統合開発
docker-compose -f docker-compose.dev.yml up
```

#### 本格開発時

```bash
# フル統合環境（推奨）
docker-compose -f docker-compose.dev.yml up
# → Frontend(3000) + Backend(8000) + Redis + LangFuse
```

### 📦 プロダクション環境

本番環境では**Dockerが必須**：

```bash
# 本番ビルド・デプロイ
docker-compose -f docker-compose.prod.yml up -d
```

**理由**:

- Cloudflare Pages/Workers統合
- 環境一貫性
- スケーラビリティ

### 🛠️ 開発ツール統合

#### VSCode設定

```json
{
  "remote.containers.workspaceFolder": "/app",
  "typescript.preferences.quoteStyle": "single"
}
```

#### デバッグ設定

- **ローカル**: Chrome DevTools直接利用
- **Docker**: VSCode Remote Container利用

### 🚀 結論・推奨事項

1. **学習・プロトタイプ**: ローカル開発
2. **チーム開発**: Docker統合開発
3. **本番デプロイ**: Docker必須

**最適解**: Docker環境を基本とし、開発速度重視時にローカル併用
