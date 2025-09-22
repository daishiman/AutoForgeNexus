# AI プロンプト最適化システム 全コマンド・全オプション完全ガイド

## 📋 **全 24 コマンドの詳細使用方法**

---

## **1. コア管理コマンド (3 コマンド)**

### `/ai:core:init` - システム初期化

#### 全オプション一覧

| オプション | 値               | 説明                   |
| ---------- | ---------------- | ---------------------- |
| --phase    | 1-5              | 活性化フェーズ指定     |
| --agents   | core/all/custom  | エージェント選択モード |
| --env      | dev/staging/prod | 環境指定               |
| --ddd      | フラグ           | DDD 構造強制適用       |

#### 使用例と説明

```bash
# 基本形: プロジェクト名のみ指定（デフォルト: phase 1, agents core, env dev）
/ai:core:init my-project

# Phase 1: 基盤構築（7エージェント）
/ai:core:init my-project --phase 1 --agents core --env dev
# system-architect, domain-modeller, devops-coordinator,
# product-manager, technical-documentation, backend-developer, version-control-specialist が起動

# Phase 2: コア機能（13エージェント）
/ai:core:init my-project --phase 2 --agents core --env dev
# Phase 1 + api-designer, frontend-architect, database-administrator,
# test-automation-engineer, prompt-engineering-specialist, llm-integration

# Phase 3: 高度機能（19エージェント）
/ai:core:init my-project --phase 3 --agents all --env staging
# Phase 2 + evaluation-engine, workflow-orchestrator, vector-database-specialist,
# real-time-features-specialist, ui-ux-designer, observability-engineer

# Phase 4: 最適化（25エージェント）
/ai:core:init my-project --phase 4 --agents all --env staging
# Phase 3 + performance-optimizer, edge-computing-specialist, sre,
# cost-optimization, data-analyst, qa-coordinator

# Phase 5: エンタープライズ（全30エージェント）
/ai:core:init my-project --phase 5 --agents all --env prod --ddd
# 全エージェント起動 + DDD完全準拠構造

# カスタムエージェント選択（対話的）
/ai:core:init my-project --agents custom
# 対話形式で必要なエージェントを選択

# 本番環境での初期化
/ai:core:init production-system --phase 5 --agents all --env prod --ddd
# 本番用設定、全エージェント、DDD強制
```

### `/ai:core:sync` - エージェント同期

#### 全オプション一覧

| オプション | 値                       | 説明       |
| ---------- | ------------------------ | ---------- |
| --scope    | all/team/specific-agents | 同期範囲   |
| --mode     | share/merge/resolve      | 同期モード |
| --priority | high/normal              | 優先度     |

#### 使用例と説明

```bash
# 基本形: 全エージェント共有モード
/ai:core:sync

# 全エージェント同期 - 共有モード（読み取り専用）
/ai:core:sync --scope all --mode share
# 全30エージェントの状態を共有、変更なし

# 全エージェント同期 - マージモード（統合）
/ai:core:sync --scope all --mode merge
# 各エージェントの状態を統合、自動コンフリクト解決

# 全エージェント同期 - 解決モード（コンフリクト解決）
/ai:core:sync --scope all --mode resolve --priority high
# コンフリクトを優先度付きで解決

# チーム単位の同期
/ai:core:sync --scope team:prompt-optimization --mode share
# プロンプト最適化チーム（5エージェント）のみ同期

# 特定エージェント間の同期
/ai:core:sync --scope specific-agents --mode merge
# 対話的に選択したエージェント間で同期

# 緊急同期（高優先度）
/ai:core:sync --scope all --mode resolve --priority high
# システム異常時の緊急同期、強制解決
```

### `/ai:core:team` - チーム編成

#### 全オプション一覧

| オプション | 値                       | 説明         |
| ---------- | ------------------------ | ------------ |
| --size     | small/medium/large       | チームサイズ |
| --optimize | performance/cost/quality | 最適化戦略   |
| --duration | sprint/epic              | 期間設定     |

#### 使用例と説明

```bash
# 基本形: タスクタイプのみ指定
/ai:core:team feature-development

# 小規模チーム（3-5エージェント）
/ai:core:team simple-task --size small --optimize cost
# コスト重視の小規模チーム編成

# 中規模チーム（6-10エージェント）
/ai:core:team normal-task --size medium --optimize quality --duration sprint
# 品質重視、2週間スプリント向けチーム

# 大規模チーム（11+エージェント）
/ai:core:team complex-project --size large --optimize performance --duration epic
# パフォーマンス重視、2-3ヶ月エピック向け

# インシデント対応チーム
/ai:core:team incident-response --size small --optimize performance --duration sprint
# sre, observability-engineer, security-architect の即応チーム

# プロンプト最適化チーム
/ai:core:team prompt-optimization --size medium --optimize quality
# prompt-engineering-specialist主導の5エージェントチーム
```

---

## **2. 要件定義コマンド (2 コマンド)**

### `/ai:requirements:define` - 要件定義

#### 全オプション一覧

| オプション | 値                     | 説明         |
| ---------- | ---------------------- | ------------ |
| --format   | agile/waterfall/hybrid | 開発手法     |
| --validate | フラグ                 | 検証実行     |
| --priority | フラグ                 | 優先順位付け |

#### 使用例と説明

```bash
# 基本形: スコープのみ指定
/ai:requirements:define user-authentication

# アジャイル形式
/ai:requirements:define payment-system --format agile
# ユーザーストーリー形式での要件定義

# ウォーターフォール形式
/ai:requirements:define enterprise-feature --format waterfall --validate
# 詳細な仕様書形式、完全性検証付き

# ハイブリッド形式
/ai:requirements:define complex-system --format hybrid --priority
# アジャイルとウォーターフォールの混合、MoSCoW優先順位

# 完全検証付き要件定義
/ai:requirements:define critical-feature --format agile --validate --priority
# すべてのオプション有効化
```

### `/ai:requirements:domain` - ドメインモデリング

#### 全オプション一覧

| オプション       | 値                       | 説明                     |
| ---------------- | ------------------------ | ------------------------ |
| --aggregate      | root/entity/value-object | 集約タイプ               |
| --event-sourcing | フラグ                   | イベントソーシング有効化 |
| --cqrs           | フラグ                   | CQRS 有効化              |

#### 使用例と説明

```bash
# 基本形: コンテキスト名のみ
/ai:requirements:domain user-context

# 集約ルート設計
/ai:requirements:domain prompt-context --aggregate root
# プロンプト集約ルートの定義

# エンティティ設計
/ai:requirements:domain evaluation-context --aggregate entity
# 評価エンティティの定義

# 値オブジェクト設計
/ai:requirements:domain score-context --aggregate value-object
# スコア値オブジェクトの定義

# イベントソーシング対応
/ai:requirements:domain audit-context --aggregate root --event-sourcing
# 監査ログ用イベントソーシング設計

# CQRS実装
/ai:requirements:domain reporting-context --cqrs
# 読み取りモデルと書き込みモデル分離

# 完全DDD設計
/ai:requirements:domain core-context --aggregate root --event-sourcing --cqrs
# すべての戦術的パターン適用
```

---

## **3. アーキテクチャコマンド (2 コマンド)**

### `/ai:architecture:design` - システム設計

#### 全オプション一覧

| オプション     | 値                                       | 説明                   |
| -------------- | ---------------------------------------- | ---------------------- |
| pattern        | microservices/monolith/serverless/hybrid | アーキテクチャパターン |
| --ddd          | フラグ                                   | DDD 適用               |
| --event-driven | フラグ                                   | イベント駆動有効化     |
| --scale        | horizontal/vertical                      | スケーリング戦略       |

#### 使用例と説明

```bash
# マイクロサービス設計
/ai:architecture:design microservices
# 基本的なマイクロサービスアーキテクチャ

# モノリス設計
/ai:architecture:design monolith --ddd
# DDDモノリス設計

# サーバーレス設計
/ai:architecture:design serverless --scale horizontal
# Cloudflare Workers活用、水平スケーリング

# ハイブリッド設計
/ai:architecture:design hybrid --ddd --event-driven
# モノリスとマイクロサービスの混合、イベント駆動

# 完全な設計
/ai:architecture:design microservices --ddd --event-driven --scale horizontal
# DDD+イベント駆動+水平スケーリング
```

### `/ai:architecture:event` - イベント設計

#### 全オプション一覧

| オプション | 値                       | 説明                 |
| ---------- | ------------------------ | -------------------- |
| --pattern  | saga/cqrs/event-sourcing | イベントパターン     |
| --broker   | redis/kafka/rabbitmq     | メッセージブローカー |

#### 使用例と説明

```bash
# 基本形: ドメインのみ指定
/ai:architecture:event payment-domain

# Sagaパターン
/ai:architecture:event order-processing --pattern saga --broker redis
# 分散トランザクション管理

# CQRSパターン
/ai:architecture:event user-management --pattern cqrs --broker kafka
# コマンドとクエリの分離

# イベントソーシング
/ai:architecture:event audit-log --pattern event-sourcing --broker kafka
# イベントストア実装

# 複合パターン
/ai:architecture:event complex-domain --pattern saga --pattern cqrs --broker redis
# Saga+CQRS実装
```

---

## **4. プロンプト管理コマンド (4 コマンド)**

### `/ai:prompt:create` - プロンプト作成

#### 全オプション一覧

| オプション | 値                     | 説明           |
| ---------- | ---------------------- | -------------- |
| --model    | gpt4/claude/gemini/all | 対象モデル     |
| --chain    | フラグ                 | チェーン有効化 |
| --optimize | フラグ                 | 最適化実行     |
| --template | フラグ                 | テンプレート化 |

#### 使用例と説明

```bash
# 基本形: 目的のみ指定
/ai:prompt:create code-review

# 単一モデル向け
/ai:prompt:create sql-query --model gpt4
# GPT-4専用プロンプト

# マルチモデル対応
/ai:prompt:create general-assistant --model all --optimize
# 全モデル対応、最適化済み

# プロンプトチェーン
/ai:prompt:create research-flow --chain --template
# 多段階プロンプト、テンプレート化

# 完全最適化
/ai:prompt:create production-prompt --model all --chain --optimize --template
# すべての機能有効化
```

### `/ai:prompt:evaluate` - プロンプト評価

#### 全オプション一覧

| オプション | 値                            | 説明         |
| ---------- | ----------------------------- | ------------ |
| --metrics  | accuracy/consistency/cost/all | 評価指標     |
| --compare  | baseline-id                   | 比較対象     |
| --improve  | フラグ                        | 改善提案生成 |

#### 使用例と説明

```bash
# 基本形: プロンプトIDのみ
/ai:prompt:evaluate prompt-123

# 特定メトリクス評価
/ai:prompt:evaluate prompt-123 --metrics accuracy
# 正確性のみ評価

# コスト評価
/ai:prompt:evaluate prompt-123 --metrics cost --improve
# トークンコスト分析と改善提案

# 全メトリクス評価
/ai:prompt:evaluate prompt-123 --metrics all --compare baseline-v1
# 全指標でベースラインと比較

# 完全分析
/ai:prompt:evaluate prompt-123 --metrics all --compare baseline-v1 --improve
# 比較分析と改善提案
```

### `/ai:prompt:intent-diff` - 意図差分分析

#### 全オプション一覧

| オプション    | 値      | 説明       |
| ------------- | ------- | ---------- |
| --visualize   | フラグ  | 可視化有効 |
| --auto-fix    | フラグ  | 自動修正   |
| --threshold   | 0.0-1.0 | 精度閾値   |
| --interactive | フラグ  | 対話モード |

#### 使用例と説明

```bash
# 基本形: プロンプトIDのみ
/ai:prompt:intent-diff prompt-123

# 可視化付き分析
/ai:prompt:intent-diff prompt-123 --visualize
# 差分のビジュアル表示

# 自動修正
/ai:prompt:intent-diff prompt-123 --auto-fix --threshold 0.8
# 80%精度での自動修正

# 対話的修正
/ai:prompt:intent-diff prompt-123 --visualize --interactive
# ユーザー確認付き修正

# 完全機能
/ai:prompt:intent-diff prompt-123 --visualize --auto-fix --threshold 0.9 --interactive
# すべての機能有効化
```

### `/ai:prompt:style-genome` - スタイル管理

#### 全オプション一覧

| オプション | 値               | 説明         |
| ---------- | ---------------- | ------------ |
| --analyze  | history/feedback | 分析対象     |
| --extract  | フラグ           | スタイル抽出 |
| --apply    | prompt-id        | 適用先       |
| --transfer | フラグ           | スタイル転送 |

#### 使用例と説明

```bash
# 履歴分析
/ai:prompt:style-genome user-123 --analyze history
# 過去プロンプトからスタイル分析

# フィードバック分析
/ai:prompt:style-genome user-123 --analyze feedback --extract
# フィードバックからスタイル抽出

# スタイル適用
/ai:prompt:style-genome user-123 --apply new-prompt
# 特定プロンプトへスタイル適用

# スタイル転送
/ai:prompt:style-genome user-123 --apply target-prompt --transfer
# 別ユーザーへスタイル転送

# 完全処理
/ai:prompt:style-genome user-123 --analyze history --extract --apply new-prompt --transfer
# 分析→抽出→適用→転送
```

---

## **5. 開発コマンド (4 コマンド)**

### `/ai:development:implement` - 機能実装

#### 全オプション一覧

| オプション | 値     | 説明             |
| ---------- | ------ | ---------------- |
| --tdd      | フラグ | TDD 有効化       |
| --realtime | フラグ | リアルタイム機能 |
| --coverage | 0-100  | カバレッジ目標   |
| --parallel | フラグ | 並列実行         |

#### 使用例と説明

```bash
# 基本形: 機能名のみ
/ai:development:implement login-feature

# TDD実装
/ai:development:implement payment --tdd --coverage 80
# 80%カバレッジでTDD実装

# リアルタイム機能
/ai:development:implement chat --realtime --tdd
# WebSocket対応チャット機能

# 並列開発
/ai:development:implement multi-feature --tdd --coverage 90 --parallel
# 90%カバレッジ、並列実行

# フル機能
/ai:development:implement complex-feature --tdd --realtime --coverage 95 --parallel
# すべてのオプション有効
```

### `/ai:development:workflow` - ワークフロー実装

#### 全オプション一覧

| オプション      | 値                              | 説明               |
| --------------- | ------------------------------- | ------------------ |
| --langgraph     | フラグ                          | LangGraph 使用     |
| --visual-editor | フラグ                          | ビジュアルエディタ |
| --type          | sequential/parallel/conditional | 実行タイプ         |

#### 使用例と説明

```bash
# 基本形: ワークフロー名のみ
/ai:development:workflow approval-flow

# LangGraph実装
/ai:development:workflow data-pipeline --langgraph
# LangGraphベースのパイプライン

# ビジュアルエディタ付き
/ai:development:workflow user-journey --visual-editor
# ドラッグ&ドロップエディタ

# 実行タイプ指定
/ai:development:workflow batch-process --type parallel
# 並列処理ワークフロー

# 条件分岐フロー
/ai:development:workflow decision-tree --type conditional --visual-editor
# 条件分岐付きビジュアルフロー

# 完全機能
/ai:development:workflow complex-flow --langgraph --visual-editor --type conditional
# すべての機能有効化
```

### `/ai:development:realtime` - リアルタイム機能

#### 全オプション一覧

| オプション  | 値     | 説明             |
| ----------- | ------ | ---------------- |
| --websocket | フラグ | WebSocket 使用   |
| --crdt/--ot | フラグ | 同期アルゴリズム |
| --scale     | フラグ | スケーリング対応 |
| --presence  | フラグ | プレゼンス機能   |

#### 使用例と説明

```bash
# 基本形: 機能名のみ
/ai:development:realtime live-updates

# WebSocket実装
/ai:development:realtime notifications --websocket
# WebSocketベース通知

# CRDT同期
/ai:development:realtime collaborative-doc --crdt --presence
# CRDT協調編集、カーソル共有

# OT同期
/ai:development:realtime text-editor --ot --scale
# Operational Transform、スケーラブル

# 完全機能
/ai:development:realtime collaboration --websocket --crdt --scale --presence
# すべての機能有効化
```

### `/ai:development:git` - バージョン管理

#### 全オプション一覧

| オプション         | 値                                           | 説明                         |
| ------------------ | -------------------------------------------- | ---------------------------- |
| operation          | init/merge/release/resolve-conflict/monorepo | Git 操作                     |
| --strategy         | gitflow/github-flow/trunk-based              | ブランチ戦略                 |
| --auto-merge       | フラグ                                       | 自動マージ有効化             |
| --semantic-version | フラグ                                       | セマンティックバージョニング |
| --hooks            | フラグ                                       | Git フック設定               |

#### 使用例と説明

```bash
# 基本形: 操作のみ指定
/ai:development:git status
# 現在のリポジトリ状態確認

# ブランチ戦略実装
/ai:development:git init --strategy gitflow --hooks
# Git Flow戦略の完全セットアップ
# develop, release, hotfixブランチ作成
# 保護ルールとフックの自動設定
# CODEOWNERSファイル生成
# .gitignore最適化
# コミットテンプレート設定

# GitHub Flow戦略
/ai:development:git init --strategy github-flow --hooks
# シンプルなfeatureブランチワークフロー
# mainブランチ保護
# プルリクエストテンプレート作成
# 自動レビュー設定

# Trunk-Based Development
/ai:development:git init --strategy trunk-based
# 単一mainブランチ戦略
# 短命なfeatureブランチ
# 機能フラグ統合準備

# 自動マージとCI/CD連携
/ai:development:git merge feature-branch --auto-merge --strategy github-flow
# テスト成功後の自動マージ
# コンフリクト自動解決試行
# CI/CDパイプライントリガー
# Slackへの完了通知
# レビュー承認チェック

# セマンティックリリース
/ai:development:git release v1.2.0 --semantic-version --hooks
# バージョン番号の自動計算
# CHANGELOG自動生成（conventional-changelog）
# リリースノート作成
# タグ付けとGitHubリリース作成
# NPM/PyPI公開準備
# リリースブランチ作成
# ホットフィックス準備

# コンフリクト解決支援
/ai:development:git resolve-conflict feature-branch --strategy rebase
# インテリジェントコンフリクト分析
# 3-way マージ戦略適用
# テスト実行による検証
# コンフリクト解決レポート
# マージコミット最適化

# モノレポ管理
/ai:development:git monorepo --strategy trunk-based
# モノレポ用ブランチ戦略
# パッケージ別バージョニング
# 依存関係グラフ生成
# 選択的CI/CD実行
# Lerna/Nx統合設定

# プルリクエスト管理
/ai:development:git pr feature-branch --auto-merge
# PR自動作成
# レビュアー自動割当
# ラベル自動付与
# マージ条件設定
# ドラフトPR管理

# コミット管理
/ai:development:git commit --hooks --semantic-version
# Conventional Commits強制
# コミットメッセージ検証
# チケット番号自動追加
# 署名付きコミット
# pre-commitフック実行

# ブランチクリーンアップ
/ai:development:git cleanup --strategy gitflow
# マージ済みブランチ削除
# 古いfeatureブランチ警告
# リモートブランチ同期
# ブランチ履歴整理

# Git履歴管理
/ai:development:git history --strategy rebase
# コミット履歴のクリーンアップ
# インタラクティブリベース
# コミットのsquash/fixup
# 履歴の線形化

# タグ管理
/ai:development:git tag v1.0.0 --semantic-version
# アノテーション付きタグ作成
# GPG署名
# タグのプッシュ
# リリースとの関連付け

# サブモジュール管理
/ai:development:git submodule add https://github.com/org/repo
# サブモジュール追加
# 依存関係管理
# 更新戦略設定
# 再帰的クローン設定

# Git LFS設定
/ai:development:git lfs --strategy gitflow
# Large File Storage設定
# バイナリファイル管理
# トラッキングルール設定
# ストレージ最適化

# バックアップとリカバリ
/ai:development:git backup --strategy gitflow
# リポジトリバックアップ
# ブランチアーカイブ
# 災害復旧計画
# ミラーリング設定
```

---

## **6. 運用コマンド (3 コマンド)**

### `/ai:operations:deploy` - デプロイメント

#### 全オプション一覧

| オプション | 値                        | 説明             |
| ---------- | ------------------------- | ---------------- |
| env        | dev/staging/prod          | 環境指定         |
| --strategy | canary/blue-green/rolling | デプロイ戦略     |
| --rollback | auto/manual               | ロールバック設定 |
| --edge     | フラグ                    | エッジデプロイ   |

#### 使用例と説明

```bash
# 開発環境デプロイ
/ai:operations:deploy dev
# シンプルなdev環境デプロイ

# カナリアデプロイ
/ai:operations:deploy staging --strategy canary
# 段階的リリース（5%→25%→50%→100%）

# ブルーグリーンデプロイ
/ai:operations:deploy prod --strategy blue-green --rollback auto
# 即座切替、自動ロールバック

# ローリングデプロイ
/ai:operations:deploy staging --strategy rolling
# 順次更新

# エッジデプロイ
/ai:operations:deploy prod --edge --strategy canary
# Cloudflare Workers展開

# 本番フルオプション
/ai:operations:deploy prod --strategy canary --rollback auto --edge
# 全機能有効の本番デプロイ
```

### `/ai:operations:incident` - インシデント管理

#### 全オプション一覧

| オプション   | 値                       | 説明             |
| ------------ | ------------------------ | ---------------- |
| severity     | critical/high/medium/low | 重要度           |
| --escalate   | フラグ                   | エスカレーション |
| --rca        | フラグ                   | 根本原因分析     |
| --postmortem | フラグ                   | ポストモーテム   |

#### 使用例と説明

```bash
# 低重要度インシデント
/ai:operations:incident low
# 記録のみ

# 中重要度インシデント
/ai:operations:incident medium --rca
# 根本原因分析実施

# 高重要度インシデント
/ai:operations:incident high --escalate --rca
# エスカレーション+RCA

# クリティカルインシデント
/ai:operations:incident critical --escalate --rca --postmortem
# 全対応実施
```

### `/ai:operations:monitor` - 監視設定

#### 全オプション一覧

| オプション | 値                      | 説明           |
| ---------- | ----------------------- | -------------- |
| scope      | system/service/endpoint | 監視範囲       |
| --metrics  | フラグ                  | メトリクス収集 |
| --traces   | フラグ                  | トレース収集   |
| --logs     | フラグ                  | ログ収集       |
| --alerts   | フラグ                  | アラート設定   |

#### 使用例と説明

```bash
# システム全体監視
/ai:operations:monitor system
# 基本監視

# メトリクス監視
/ai:operations:monitor service --metrics
# サービスメトリクス収集

# トレーシング
/ai:operations:monitor endpoint --traces
# 分散トレース

# フル監視
/ai:operations:monitor system --metrics --traces --logs --alerts
# 3 Pillars + アラート
```

---

## **7. 品質コマンド (3 コマンド)**

### `/ai:quality:analyze` - 品質分析

#### 全オプション一覧

| オプション | 値                               | 説明     |
| ---------- | -------------------------------- | -------- |
| scope      | 分析対象パス                     | 対象指定 |
| --focus    | quality/security/performance/all | 焦点     |
| --depth    | shallow/deep                     | 分析深度 |
| --fix      | フラグ                           | 自動修正 |

#### 使用例と説明

```bash
# 品質分析
/ai:quality:analyze src/ --focus quality
# コード品質分析

# セキュリティ分析
/ai:quality:analyze api/ --focus security --depth deep
# 深層セキュリティ監査

# パフォーマンス分析
/ai:quality:analyze --focus performance --fix
# パフォーマンス最適化と自動修正

# 全側面分析
/ai:quality:analyze --focus all --depth deep --fix
# 包括的分析と修正
```

### `/ai:quality:tdd` - TDD 管理

#### 全オプション一覧

| オプション | 値     | 説明             |
| ---------- | ------ | ---------------- |
| feature    | 機能名 | 対象機能         |
| --coverage | 0-100  | カバレッジ目標   |
| --contract | フラグ | 契約テスト       |
| --mutation | フラグ | ミューテーション |
| --watch    | フラグ | 監視モード       |

#### 使用例と説明

```bash
# 基本TDD
/ai:quality:tdd login --coverage 80
# 80%カバレッジ

# 契約テスト
/ai:quality:tdd api --contract --coverage 85
# API契約テスト

# ミューテーションテスト
/ai:quality:tdd core --mutation --coverage 90
# テスト品質検証

# ウォッチモード
/ai:quality:tdd feature --watch --coverage 80
# 継続的テスト実行

# フルテスト
/ai:quality:tdd critical --coverage 95 --contract --mutation --watch
# すべてのテスト機能
```

### `/ai:quality:security` - セキュリティ監査

#### 全オプション一覧

| オプション   | 値                  | 説明             |
| ------------ | ------------------- | ---------------- |
| scope        | 監査範囲            | 対象指定         |
| --scan       | static/dynamic/both | スキャンタイプ   |
| --pentest    | フラグ              | ペネトレーション |
| --compliance | gdpr/soc2           | コンプライアンス |

#### 使用例と説明

```bash
# 静的スキャン
/ai:quality:security src/ --scan static
# SAST実行

# 動的スキャン
/ai:quality:security api/ --scan dynamic
# DAST実行

# 両方のスキャン
/ai:quality:security --scan both --pentest
# SAST+DAST+ペネトレーション

# コンプライアンス監査
/ai:quality:security --compliance gdpr
# GDPR準拠確認

# フル監査
/ai:quality:security --scan both --pentest --compliance soc2
# 完全セキュリティ監査
```

---

## **8. データ管理コマンド (3 コマンド)**

### `/ai:data:vector` - ベクトル DB 管理

#### 全オプション一覧

| オプション  | 値                            | 説明         |
| ----------- | ----------------------------- | ------------ |
| operation   | embed/search/optimize/analyze | 操作         |
| --dimension | 数値                          | ベクトル次元 |
| --index     | hnsw/ivfflat                  | インデックス |

#### 使用例と説明

```bash
# 埋め込み生成
/ai:data:vector embed --dimension 1536
# 1536次元埋め込み

# 検索実装
/ai:data:vector search --dimension 1536 --index hnsw
# HNSW検索（精度重視）

# 最適化
/ai:data:vector optimize --index ivfflat
# IVFFlat最適化（速度重視）

# 分析
/ai:data:vector analyze
# ベクトル分析とクラスタリング
```

### `/ai:data:migrate` - データ移行

#### 全オプション一覧

| オプション      | 値           | 説明             |
| --------------- | ------------ | ---------------- |
| source          | ソース名     | 移行元           |
| target          | ターゲット名 | 移行先           |
| --zero-downtime | フラグ       | ゼロダウンタイム |
| --validate      | フラグ       | 検証実行         |
| --rollback-plan | フラグ       | ロールバック準備 |

#### 使用例と説明

```bash
# 基本移行
/ai:data:migrate old-db new-db
# シンプルな移行

# ゼロダウンタイム移行
/ai:data:migrate postgres-14 postgres-16 --zero-downtime
# ダウンタイムなし

# 検証付き移行
/ai:data:migrate legacy cloud --validate
# データ整合性検証

# 完全移行
/ai:data:migrate production staging --zero-downtime --validate --rollback-plan
# 全オプション有効
```

### `/ai:data:analyze` - データ分析

#### 全オプション一覧

| オプション  | 値                    | 説明         |
| ----------- | --------------------- | ------------ |
| dataset     | データセット名        | 分析対象     |
| --type      | statistical/ml/vector | 分析タイプ   |
| --visualize | フラグ                | 可視化       |
| --report    | フラグ                | レポート生成 |

#### 使用例と説明

```bash
# 統計分析
/ai:data:analyze user-data --type statistical
# 基本統計量

# 機械学習分析
/ai:data:analyze events --type ml --visualize
# ML分析と可視化

# ベクトル分析
/ai:data:analyze embeddings --type vector --report
# ベクトル分析レポート

# 完全分析
/ai:data:analyze all-data --type statistical --visualize --report
# 全機能での分析
```

---

## **コマンド組み合わせパターン**

### 新プロジェクト立ち上げの完全フロー

```bash
# 1. 初期化（すべてのオプション活用）
/ai:core:init new-project --phase 1 --agents core --env dev --ddd

# 2. Git設定
/ai:development:git init --strategy gitflow --hooks
/ai:development:git commit --hooks --semantic-version

# 3. 同期（全モード試行）
/ai:core:sync --scope all --mode share
/ai:core:sync --scope all --mode merge
/ai:core:sync --scope all --mode resolve --priority high

# 4. チーム編成（各サイズ）
/ai:core:team initial --size small --optimize cost --duration sprint
/ai:core:team development --size medium --optimize quality --duration sprint
/ai:core:team scaling --size large --optimize performance --duration epic
```

### プロンプト開発の完全フロー

```bash
# 1. 作成（全オプション）
/ai:prompt:create advanced --model all --chain --optimize --template

# 2. 評価（全メトリクス）
/ai:prompt:evaluate advanced --metrics all --compare baseline --improve

# 3. 差分分析（全機能）
/ai:prompt:intent-diff advanced --visualize --auto-fix --threshold 0.9 --interactive

# 4. スタイル適用（完全処理）
/ai:prompt:style-genome user --analyze history --extract --apply advanced --transfer

# 5. バージョン管理
/ai:development:git commit --hooks --semantic-version
/ai:development:git release v1.0.0 --semantic-version --hooks
```

### 開発ワークフローの完全フロー

```bash
# 1. ブランチ作成
/ai:development:git init --strategy github-flow --hooks

# 2. 実装
/ai:development:implement new-feature --tdd --coverage 90 --parallel

# 3. コミット
/ai:development:git commit --hooks --semantic-version

# 4. PR作成とマージ
/ai:development:git pr feature-branch --auto-merge
/ai:development:git merge feature-branch --auto-merge --strategy github-flow

# 5. リリース
/ai:development:git release v2.0.0 --semantic-version --hooks
```
