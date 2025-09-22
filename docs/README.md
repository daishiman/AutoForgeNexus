# AutoForgeNexus ドキュメンテーション

## 📋 ドキュメント概要

AutoForgeNexus AIプロンプト最適化システムの包括的なドキュメンテーションです。
プロダクト仕様から技術アーキテクチャまで、開発・運用に必要な全情報を提供します。

## 🗂️ ドキュメント構造

### 📋 要件定義 (`requirements/`)

| ドキュメント | 概要 | 対象読者 |
|-------------|------|---------|
| [プロダクト要件定義書](requirements/product_requirements.md) | 包括的なPRD、ビジョン、目標、機能要件 | PO、開発者、ステークホルダー |
| [ユーザーストーリーマッピング](requirements/user_stories.md) | 21のユーザーストーリー、優先順位、スプリント計画 | 開発者、Scrum Master |
| [革新的機能仕様書](requirements/innovative_features.md) | 17の革新機能の詳細仕様と実装方針 | 開発者、アーキテクト |

### 🏗️ アーキテクチャ (`architecture/`)

| ドキュメント | 概要 | 対象読者 |
|-------------|------|---------|
| [システムアーキテクチャ設計書](architecture/system_architecture.md) | DDD+イベント駆動+クリーンアーキテクチャ設計 | アーキテクト、開発者 |
| [ドメインモデル設計書](architecture/domain/domain_model.md) | DDD戦術・戦略パターンの完全実装 | ドメインエキスパート、開発者 |

### 📚 参考資料 (`legacy/`)

| ドキュメント | 概要 | 用途 |
|-------------|------|-----|
| [技術スタック.md](legacy/技術スタック.md) | 包括的技術仕様書（600行超） | 参考資料 |
| [プロンプト作成支援システム 構想整理書.md](legacy/プロンプト作成支援システム%20構想整理書.md) | 初期構想とアイデア | 参考資料 |

## 🎯 ドキュメントマップ

### 🚀 プロジェクト開始時
1. **[プロダクト要件定義書](requirements/product_requirements.md)** - 全体像把握
2. **[ユーザーストーリーマッピング](requirements/user_stories.md)** - 開発計画理解
3. **[システムアーキテクチャ設計書](architecture/system_architecture.md)** - 技術方針確認

### 💻 開発フェーズ
1. **[ドメインモデル設計書](architecture/domain/domain_model.md)** - ドメイン実装
2. **[革新的機能仕様書](requirements/innovative_features.md)** - 17機能の実装
3. **[システムアーキテクチャ設計書](architecture/system_architecture.md)** - 技術詳細参照

### 🔍 機能仕様確認
1. **[革新的機能仕様書](requirements/innovative_features.md)** - 17の革新機能
2. **[ユーザーストーリーマッピング](requirements/user_stories.md)** - ユーザー視点
3. **[プロダクト要件定義書](requirements/product_requirements.md)** - ビジネス要件

## 📊 プロジェクト概要

### システム概要
**AutoForgeNexus**は、ユーザーの言語化能力に依存せず、高品質なAIプロンプトの作成・最適化・管理ができる統合環境を提供する世界最高水準のAIプロンプト最適化プラットフォームです。

### 主要価値提案
- **17の革新的機能**: 業界初の画期的機能群
- **DDD+イベント駆動設計**: 保守性と拡張性を最大化
- **マルチLLM対応**: 100+プロバイダー統合
- **品質保証**: 多層評価メトリクスによる自動最適化

### 技術スタック概要
- **Backend**: Python 3.13 + FastAPI 0.116.1
- **Frontend**: Next.js 15.5 + React 19
- **Database**: Turso (libSQL/SQLite) + libSQL Vector + Redis
- **Authentication**: Clerk (OAuth 2.0, MFA, Organization Management)
- **Infrastructure**: Cloudflare (Workers/Pages/R2)
- **Observability**: LangFuse (LLM Tracing & Evaluation)
- **AI/ML**: LangChain 0.3.27 + LangGraph 0.6.7 + LiteLLM 1.76.1

## 🎯 主要機能

### 🔍 コア機能（Phase 1）
1. **意図差分ビューワー** - ユーザー意図とプロンプトの差分可視化
2. **プロンプトSLO** - 運用品質指標による安定性保証
3. **スタイル・ゲノム** - ユーザー固有スタイルの抽出・再現

### ⚡ 品質向上（Phase 2）
4. **プロンプト・ジェンガ** - ロバストネス自動テスト
5. **影武者システム** - 敵対的テストによる盲点発見
6. **レグレット・リプレイ** - 人間編集の学習データ化

### 🔧 運用効率（Phase 3）
7. **コンテキストTTL** - 情報鮮度管理
8. **逆向きRAG** - 理想出力からの逆算検索

## 📈 開発計画

### マイルストーン
- **MVP**: Week 12 - 基本機能実装
- **Beta**: Week 24 - 全機能実装
- **GA**: Week 36 - 本番運用開始
- **v2.0**: Week 48 - エンタープライズ版

### 成功指標
- **プロンプト生成成功率**: 85%以上
- **品質向上**: 30%の品質改善
- **効率化**: 2-3倍の作成速度向上
- **コスト削減**: 年間95%以上のコスト削減

## 🔗 クイックリンク

### 📋 計画・要件
- [プロダクトビジョン](requirements/product_requirements.md#プロダクトビジョン)
- [機能要件一覧](requirements/product_requirements.md#機能要件-アジャイル形式)
- [非機能要件](requirements/product_requirements.md#非機能要件)

### 🏗️ 技術・設計
- [全体アーキテクチャ](architecture/system_architecture.md#全体アーキテクチャ)
- [ドメイン設計](architecture/domain/domain_model.md#境界付きコンテキスト-bounded-context)
- [技術スタック詳細](architecture/system_architecture.md#詳細技術スタック)

### 🌟 革新機能
- [17の革新機能一覧](requirements/innovative_features.md#17の革新的機能)
- [実装優先度](requirements/innovative_features.md#実装優先度)
- [成功指標](requirements/innovative_features.md#成功指標)

## 📝 ドキュメント作成・更新ルール

### 作成原則
- **完全性**: 実装に必要な全情報を含む
- **正確性**: 技術的に正しく実装可能
- **明確性**: 役割別の読者に最適化
- **追跡可能性**: 要件と実装の紐付け

### 更新ルール
- **バージョン管理**: 主要変更時にバージョン更新
- **承認プロセス**: 技術的変更は開発チーム承認
- **同期更新**: 関連ドキュメントの整合性維持

---

## 🤝 貢献・問い合わせ

### ドキュメント更新
- プルリクエストによる更新提案
- イシューによる改善提案
- レビューによる品質保証

### 問い合わせ先
- **技術的質問**: 開発チーム
- **要件確認**: プロダクトオーナー
- **ドキュメント**: テクニカルライター

---

**このドキュメンテーションにより、AutoForgeNexus開発チーム全体の効率的な協働と高品質な成果物の実現を目指します。**

---

**ドキュメント情報**
- 作成日: 2025-09-22
- バージョン: 1.0
- 総ページ数: 5ドキュメント
- 最終更新: システム初期化完了時

🤖 Generated with AutoForgeNexus System