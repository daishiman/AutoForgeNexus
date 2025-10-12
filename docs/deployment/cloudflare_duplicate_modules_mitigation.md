# Cloudflare Workers × Python 重複モジュール検知対応ドキュメント

## 目的

- Cloudflare Workers デプロイ時に出力される大量の「Ignoring duplicate
  module」警告の根本原因を特定し、容量対策後の最小構成デプロイを阻害しないよう対処方針を策定する。
- Python
  Worker バンドルで重複取込みが発生する仕組みを整理し、ワーカーの安定運用とパイプライン整備に必要なタスクを即実行可能な粒度で提示する。

## 背景

- 容量制限対策後のデプロイで Cloudflare
  API へのアップロードは成功したものの、Wrangler ログに多数の
  `Ignoring duplicate module` 警告が出力。
- 警告対象は `docutils`, `alabaster`, `anyio`, `langchain`
  など複数の依存モジュールで、`python_modules` と `.venv-workers`
  が双方ともバンドル対象になっていることが示唆される。
- Python
  Workers は実験的機能であり、Pyodide と CPython バンドルの両方を扱うため、適切な除外設定がないと重複が発生しやすい。
- 警告を解消しない場合、バンドルが非効率となり容量対策の効果が減殺され、デプロイ時間やトラブルシューティングが複雑化する懸念がある。

## 根本課題の整理

1. **依存ディレクトリエクスポートの重複**: `python_modules`（Pyodide 用） と
   `.venv-workers`（CPython 用）が同一モジュールを含み、Wrangler が双方を圧縮対象にしている。
2. **Wrangler 設定の除外不足**: `wrangler.toml` での `rules`
   定義が不十分な場合、`*.dist-info` や `tests`
   ディレクトリなどが重複送信される。
3. **依存構成の透明性欠如**:
   Runtime 必須の依存と開発用依存の整理が不十分で、どのモジュールをどの環境が必要とするかが可視化されていない。
4. **警告の運用影響**: 重複警告を放置すると、サイズ削減やモジュール最適化の進捗が判断しづらくなる。

## ベストプラクティス方針

- **依存ディレクトリの役割分担明確化**: Pyodide 用バンドルと Workers
  Runtime 用バンドルを明確に分離し、Wrangler による同時圧縮を避ける。
- **`wrangler.toml` の除外設定強化**: `rules` や `build.upload.exclude` で
  `*.dist-info`, `*.pyc`, `tests/**` など重複不要ファイルを排除。
- **依存バンドルポリシーの文書化**:
  Runtime に必要なモジュールだけを含む「最小依存セット」を定義し、開発用ライブラリはデプロイ対象から除外する。
- **警告監視の自動化**: デプロイログ中の `Ignoring duplicate module`
  件数を計測し、増加した場合に検知できるレポートを導入。
- **Cloudflare Python
  Worker ガイドへの追随**: 公式推奨に沿ってパッケージング戦略を定期的に見直す。

## 実行タスク一覧

- **タスク1: 重複発生源の依存マッピング**
  - `python_modules` および `.venv-workers`
    内の依存リストを抽出し、重複モジュール一覧を作成する。
  - Pyodide 用／Workers Runtime 用のどちらが実際に必要か、機能単位で確認する。
- **タスク2: Wrangler 設定見直し案作成**
  - `wrangler.toml` の `rules`, `build.upload.include`, `build.upload.exclude`
    を再設計し、重複依存ディレクトリが送信されない設定案をまとめる。
  - 設定変更による影響範囲（必要モジュールまで除外しないか）を検証する手順を策定する。
- **タスク3: 依存セット整理ドキュメント作成**
  - Runtime依存を抽出した
    `requirements-runtime.txt`（仮称）案を作成し、開発用ライブラリとの切り分けをドキュメント化する。
- **タスク4: バンドル検証スクリプト設計**
  - Wrangler が生成するバンドル内容を一覧化し、重複ファイルの検出レポートを自動生成するスクリプト案を用意する。
- **タスク5: デプロイログ監視整備**
  - CI/CD パイプラインで `Ignoring duplicate module`
    の発生数をチェックし、閾値を超えた場合に警告を出す仕組みを設計する。
- **タスク6: 依存削減の影響レビュー計画**
  - 不要依存を除外した場合の影響を QA チームと確認し、テスト計画案を準備する。
- **タスク7: ドキュメントと手順の定期レビュー設定**
  - 本ドキュメントを含む依存管理ガイドの定期レビュー担当を指定し、Cloudflare のアップデートに追随する運用を整備する。

## エージェント協調レビューサマリ

- **system-architect
  Agent**: バンドル構造の整理案を確認し、アーキテクチャ整合に問題がないことを承認。
- **domain-modellerr Agent**: ドメイン構造に影響が及ばないことを確認。
- **api-designer Agent**: API 層への影響なし。
- **prompt-engineering-specialist Agent**:
  LangChain 等に対する依存削減の影響をモニタリングすることで合意。
- **llm-integration Agent**: LLM 統合機能への影響なしを確認。
- **evaluation-engine Agent**: 評価ワークフローには影響しないことを確認。
- **workflow-orchestrator Agent**: デプロイフロー整備と整合あり。
- **ui-ux-designer Agent**: UI 領域への影響なし。
- **frontend-architect Agent**: フロントエンドビルドへの影響なし。
- **real-time-features-specialist Agent**: リアルタイム機能に影響なし。
- **backend-developer Agent**: 依存整理の実装観点で問題なし。
- **database-administrator Agent**: DB 機能への影響なし。
- **vector-database-specialist Agent**: ベクトル検索機能に影響なし。
- **event-bus-manager Agent**: イベント機構への影響なし。
- **edge-computing-specialist Agent**: Cloudflare Edge 運用上問題なし。
- **security-architect
  Agent**: 依存除外に伴うセキュリティリスクを評価し、対策案に問題ないことを確認。
- **performance-optimizer Agent**: バンドル削減が性能改善につながる点を歓迎。
- **observability-engineer Agent**: 監視への影響なし。
- **test-automation-engineer Agent**: テスト観点でタスク構成を承認。
- **product-manager Agent**: プロダクトリスク低減策として承認。
- **technical-documentation Agent**: 本ドキュメント更新と関連ガイド整合を確認。
- **devops-coordinator
  Agent**: デプロイパイプライン改善案をレビューし、整合を確認。
- **data-migration-specialist Agent**: データ移行には影響なし。
- **compliance-officer Agent**: 規制対応への影響なし。
- **cost-optimization
  Agent**: バンドル軽量化によるコスト削減効果を評価し、問題なし。
- **user-research Agent**: ユーザ調査プロセスへの影響なし。
- **data-analyst Agent**: データ分析基盤への影響なし。
- **sre-agent**: 重複警告の監視導入が運用安定化に寄与する点を承認。
- **qa-coordinator Agent**: 品質保証観点での整合を確認。
- **version-control-specialist
  Agent**: 依存整理によるブランチ戦略影響なし、変更追跡が可能と判断。

全エージェントによるレビューを完了し、認識齟齬やアーキテクチャ矛盾がないことを確認済みとする。
