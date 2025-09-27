# AutoForgeNexus

**世界最高水準の AI プロンプト最適化プラットフォーム**

AutoForgeNexus は、ユーザーの言語化能力に依存せず、高品質な AI プロンプトの作成
・最適化・管理ができる統合環境を提供します。

## 🚀 主要機能

- **17 の革新的機能**: 意図差分ビューワー、プロンプト SLO、スタイル・ゲノムなど
  業界初の画期的機能
- **マルチ LLM 対応**: 100+プロバイダー統合とコスト最適化
- **AI 支援創作**: テンプレートと AI 支援による段階的プロンプト作成
- **品質保証**: 多層評価メトリクスによる自動最適化
- **Git-like 管理**: バージョニング、ブランチ、マージ機能

## 🏗️ 技術スタック

### Core Technologies

- **Backend**: Python 3.13 + FastAPI 0.116.1
- **Frontend**: Next.js 15.5 + React 19 + TypeScript 5.x
- **Database**: Turso (libSQL/SQLite) + libSQL Vector + Redis 7
- **Authentication**: Clerk (OAuth 2.0, MFA, Organization Management)
- **Infrastructure**: Cloudflare (Workers/Pages/R2)
- **Observability**: LangFuse (LLM Tracing & Evaluation)
- **AI/ML**: LangChain 0.3.27 + LangGraph 0.6.7 + LiteLLM 1.76.1

### Architecture

- **DDD + Event-Driven + Clean Architecture**
- **CQRS + Event Sourcing**
- **Edge-First Database Design**
- **Zero Trust Security**

## 📋 クイックスタート

### 前提条件

- Python 3.13+
- Node.js 18+ & pnpm
- Turso CLI
- Docker (オプション)

### セットアップ

```bash
# リポジトリクローン
git clone https://github.com/[username]/AutoForgeNexus
cd AutoForgeNexus

# Tursoデータベース作成
turso auth login
turso db create autoforgenexus

# 環境変数設定
cp .env.example .env
# TURSO_DATABASE_URL, TURSO_AUTH_TOKEN, CLERK_SECRET_KEY等を設定

# バックエンドセットアップ
cd backend
make setup
make dev

# フロントエンドセットアップ
cd frontend
pnpm install
pnpm run dev
```

## 📚 ドキュメント

- [📋 プロダクト要件定義書](docs/requirements/product_requirements.md)
- [🏗️ システムアーキテクチャ](docs/architecture/system_architecture.md)
- [🚀 17 の革新的機能](docs/requirements/innovative_features.md)
- [👥 ユーザーストーリー](docs/requirements/user_stories.md)

## 🚀 CI/CD & 監視

### GitHub Actions ワークフロー

- **CI Pipeline** - プルリクエスト時の自動テスト・品質チェック
- **CD Pipeline** - main/tag プッシュ時の自動デプロイ (Cloudflare)
- **セキュリティスキャン** - CodeQL, Dependabot, TruffleHog
- **DORA メトリクス** - デプロイ頻度、リードタイム、障害率、MTTR
- **自動リリース** - Release Please による自動バージョニング

### 監視・アラート

- **Discord 通知** - ワークフロー失敗、セキュリティアラート、パフォーマンス警告
- **GitHub Issues** - 自動 Issue 作成、SLA 管理、優先度設定
- **メトリクス収集** - 日次 DORA 指標、パフォーマンス分析

詳細設定: [📊 監視設定ガイド](docs/monitoring/setup-notifications.md)

## 🛠️ 開発

### 開発コマンド

```bash
# バックエンド
make dev            # 開発サーバー起動
make test           # テスト実行
make lint           # コード品質チェック

# フロントエンド
pnpm run dev         # 開発サーバー起動
pnpm run build       # 本番ビルド
pnpm run test        # テスト実行
pnpm run type-check  # TypeScript検証

# Turso操作
turso db show autoforgenexus       # データベース情報
turso db shell autoforgenexus     # SQLシェル
turso db create autoforgenexus-dev --from-db autoforgenexus  # 開発ブランチ
```

### プロジェクト構造

```
AutoForgeNexus/
├── backend/                # Python/FastAPI バックエンド
│   ├── src/
│   │   ├── domain/         # ドメインエンティティ
│   │   ├── application/    # ユースケース
│   │   ├── infrastructure/ # 外部サービス
│   │   └── presentation/   # API
├── frontend/               # Next.js/React フロントエンド
│   ├── src/
│   │   ├── components/     # UIコンポーネント
│   │   ├── pages/          # ページ/ルート
│   │   ├── hooks/          # Reactフック
│   │   └── stores/         # 状態管理
├── docs/                   # ドキュメント
└── .claude/                # AI開発支援設定
```

## 🎯 開発ロードマップ

### Phase 1: MVP (Week 1-12)

- [x] 基盤アーキテクチャ設計
- [x] Turso + Clerk + LangFuse 統合
- [ ] 意図差分ビューワー実装
- [ ] プロンプト SLO 実装
- [ ] スタイル・ゲノム実装

### Phase 2: 革新機能 (Week 13-24)

- [ ] プロンプト・ジェンガ (Mutation Fuzz)
- [ ] 影武者システム (Adversarial Twin)
- [ ] レグレット・リプレイ (Human-Edit Feedback)

### Phase 3: エンタープライズ (Week 25-36)

- [ ] 組織管理・権限制御
- [ ] 高度分析・レポート
- [ ] API・SDK 提供

## 🤝 コントリビューション

1. プロジェクトをフォーク
2. フィーチャーブランチ作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエスト作成

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 🙏 謝辞

- [Turso](https://turso.tech/) - エッジデータベース
- [Clerk](https://clerk.com/) - 認証プラットフォーム
- [LangFuse](https://langfuse.com/) - LLM 観測性
- [Cloudflare](https://cloudflare.com/) - エッジインフラ

---

**AutoForgeNexus** - プロンプトエンジニアリングの未来を創造する
