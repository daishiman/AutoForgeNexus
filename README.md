# AutoForgeNexus

**世界最高水準の AI プロンプト最適化プラットフォーム**

AutoForgeNexus は、ユーザーの言語化能力に依存せず、高品質な AI プロンプトの作成・最適化・管理ができる統合環境を提供します。

## 🎯 プロジェクトステータス

### Phase 2: インフラ・監視基盤構築 🚧 進行中

| フェーズ | 状態 | 完了度 |
|----------|------|-------|
| Phase 1: Git・基盤環境 | ✅ 完了 | 100% |
| **Phase 2: インフラ・監視** | 🚧 進行中 | **85%** |
| Phase 3: バックエンド | ⏳ 待機 | 0% |
| Phase 4: データベース | ⏳ 待機 | 0% |
| Phase 5: フロントエンド | ⏳ 待機 | 0% |
| Phase 6: 統合・品質保証 | ⏳ 待機 | 0% |

### 最近の実装（2025年9月27日更新）

- ✅ Cloudflare Workers/Pages設定完了
- ✅ デプロイ・ロールバックスクリプト実装
- ✅ 包括的監視基盤構築（99.9% SLO対応）
- ✅ 構造化ログとヘルスチェック実装
- ✅ セキュリティミドルウェア実装

## 🚀 主要機能

- **17 の革新的機能**: 意図差分ビューワー、プロンプト SLO、スタイル・ゲノムなど業界初の画期的機能
- **マルチ LLM 対応**: 100+プロバイダー統合とコスト最適化
- **AI 支援創作**: テンプレートと AI 支援による段階的プロンプト作成
- **品質保証**: 多層評価メトリクスによる自動最適化
- **Git-like 管理**: バージョニング、ブランチ、マージ機能
- **エンタープライズ監視**: 99.9%可用性保証、包括的オブザーバビリティ

## 🏗️ 技術スタック

### Core Technologies

- **Backend**: Python 3.13 + FastAPI 0.116.1 + SQLAlchemy 2.0.32
- **Frontend**: Next.js 15.5 + React 19.1.0 + TypeScript 5.9.2
- **Database**: Turso (libSQL/SQLite) + libSQL Vector + Redis 7.4.1
- **Authentication**: Clerk (OAuth 2.0, MFA, Organization Management)
- **Infrastructure**: Cloudflare (Workers Python/Pages/R2/Analytics)
- **Monitoring**: Prometheus + Grafana + LangFuse + Structured Logging
- **AI/ML**: LangChain 0.3.27 + LangGraph 0.6.7 + LiteLLM 1.76.1

### Architecture

- **DDD + Clean Architecture**: 明確な責任分離とテスタビリティ
- **Event-Driven Architecture**: Redis Streamsによる非同期処理
- **CQRS Pattern**: コマンドとクエリの責任分離で高速化
- **5つの境界づけられたコンテキスト**: 
  - Prompt Engineering（プロンプト設計）
  - Evaluation（評価）
  - LLM Integration（AI連携）
  - User Interaction（ユーザー操作）
  - Data Management（データ管理）
- **CQRS + Event Sourcing**: 完全な監査証跡とイベント駆動
- **Edge-First Design**: Cloudflare Workers による低レイテンシ
- **Zero Trust Security**: 多層防御とGDPR準拠

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

### 📁 ドキュメント管理体制

すべてのレポート・レビュー・Issueは `docs/` 配下で一元管理されています：

```
docs/
├── reports/     # 実装レポート・成果報告
├── reviews/     # コードレビュー・セキュリティレビュー
├── issues/      # Issue追跡・課題管理
└── setup/       # セットアップガイド
```

### 主要ドキュメント

- [📋 プロダクト要件定義書](docs/requirements/product_requirements.md)
- [🏗️ システムアーキテクチャ](docs/architecture/system_architecture.md)
- [🚀 17 の革新的機能](docs/requirements/innovative_features.md)
- [👥 ユーザーストーリー](docs/requirements/user_stories.md)
- [🔒 セキュリティレビュー](docs/reviews/SECURITY_REVIEW_FINAL_REPORT.md)
- [📊 Issue追跡管理](docs/issues/ISSUE_TRACKING.md)

## 🚀 CI/CD & 監視

### GitHub Actions ワークフロー

- **CI Pipeline** - プルリクエスト時の自動テスト・品質チェック（環境チェック機能付き）
- **CD Pipeline** - main/tag プッシュ時の自動デプロイ (Cloudflare)
- **セキュリティスキャン** - CodeQL, Dependabot, TruffleHog
- **DORA メトリクス** - デプロイ頻度、リードタイム、障害率、MTTR
- **自動リリース** - Release Please による自動バージョニング

### 監視・アラート

- **Discord 通知** - ワークフロー失敗、セキュリティアラート、パフォーマンス警告
- **GitHub Issues** - 自動 Issue 作成、SLA 管理、優先度設定
- **メトリクス収集** - 日次 DORA 指標、パフォーマンス分析

### 段階的環境構築対応

- **環境チェック機能** - Phase 進行に応じた自動ジョブ有効化
- **条件付き実行** - 未構築環境のジョブは自動スキップ

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
