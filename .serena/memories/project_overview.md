# AutoForgeNexus プロジェクト概要

## プロジェクト目的

AIプロンプト最適化システム - ユーザーの言語化能力に依存せず、高品質なAIプロンプトの作成・最適化・管理ができる統合環境

## 技術スタック（2025年最新版）

- **バックエンド**: Python 3.13, FastAPI 0.116.1, SQLAlchemy 2.0.32, Pydantic v2
- **フロントエンド**: Next.js 15.5 (Turbopack), React 19.1.0, TypeScript 5.9.2,
  Tailwind CSS 4.0
- **データベース**: Turso (libSQL) 分散型, Redis 7.4.1, libSQL Vector Extension
- **認証**: Clerk（OAuth 2.0, MFA, 組織管理）
- **AI/ML**: LangChain 0.3.27, LangGraph 0.6.7, LiteLLM 1.76.1
- **LLM観測**: LangFuse（分散トレーシング・評価・コスト監視）
- **インフラ**: Cloudflare (Workers Python, Pages, R2), Docker 24.0+
- **状態管理**: Zustand 5.0.8
- **UIライブラリ**: shadcn/ui (React 19・Tailwind v4対応)
- **品質**: Ruff 0.7.4, mypy 1.13.0 (strict), pytest 8.3.3, Playwright

## 主要機能

- 17の革新的機能（意図差分ビューワー、スタイル・ゲノム、プロンプトSLO等）
- マルチLLM対応（100+プロバイダー統合とコスト最適化）
- Git-likeバージョニング、ブランチ、マージ機能
- リアルタイム協調編集機能
- 多層評価メトリクスによる自動最適化

## アーキテクチャパターン

- ドメイン駆動設計（DDD）原則
- クリーンアーキテクチャアプローチ
- イベントソーシング（状態変更の完全記録）
- CQRS（最適パフォーマンスのための読み書き分離）
- マイクロサービス対応設計
