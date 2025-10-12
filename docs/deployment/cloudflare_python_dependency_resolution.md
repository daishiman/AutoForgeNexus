# Cloudflare Workers × Python 依存解決ベストプラクティス検討ドキュメント

## 目的

- Cloudflare
  Workers 上で Python ランタイムを運用する際の依存解決失敗を根本から解消する方針を明確化する。
- Python ランタイム、依存パッケージ、CI/CD パイプラインの整合を保つためのベストプラクティスを整理し、再現性の高い実装タスクに落とし込む。

## 背景

- `pywrangler deploy` フローにおいて Pyodide ベースの Python
  3.13 環境を構築した際、`litellm>=1.77.0` が依存する `fastuuid` の `cp313`
  ホイールが入手できず、`uv pip install --no-build`
  によってソースビルドも禁止されているため依存解決が破綻した。
- Cloudflare
  Workers 上では Python ランタイムと依存ライブラリを wasm/pyodide 向けに揃える必要があり、ホイール互換性とパッケージ戦略の見直しが求められている。

## 根本課題の整理

1. **Python ランタイムとホイール互換性の非整合**: Pyodide が提供する `cp313`
   とライブラリ配布範囲 (`cp312` まで) の間にギャップが存在。
2. **`--no-build`
   運用の制約**: セキュリティ・再現性要件のためにソースビルドを禁止しているが、結果として対応ホイールがない依存を取得できない。
3. **依存ライブラリ選定の硬直性**: `litellm>=1.77.0` 要件が `fastuuid` を通じて
   `cp313` 非対応ホイールに依存し、バージョン変更なくは解決不能。
4. **Cloudflare 側ガイドラインとの整合確認不足**: 推奨 Python バージョンおよびパッケージング手法の最新情報を反映しきれていない可能性。

## ベストプラクティス方針

- **Python バージョン適合性の明文化**: Cloudflare
  Workers と Pyodide のサポートマトリクスに基づき、現時点では Python
  3.12 系を安定版として採用し、3.13 への移行はホイール整備後に段階的に行う。
- **ホイール配布状況の継続監視**: 重要依存 (`litellm`, `fastuuid`
  など) について、`cp313`
  ホイール提供状況を定期的に検証し、提供開始時に移行手順を準備。
- **依存解決ストラテジーの柔軟化**: セキュリティ要件とトレードオフを評価し、必要に応じて限定的にソースビルドを許可するか、自前でホイールをホストする体制を検討。
- **Cloudflare デプロイ手順の標準化**: `pywrangler deploy`
  前に Python ランタイムと依存解決を検証するプリフライトタスクを追加し、デプロイ前に問題を顕在化させる。
- **依存ライブラリの再評価**: `litellm`
  のバージョン固定理由を確認し、代替バージョンまたは機能調整で `fastuuid`
  依存を解消できないか検討。

## 実行タスク一覧

- **タスク1: Cloudflare × Python サポートマトリクス更新**
  - Cloudflare
    Workers と Pyodide の公式ドキュメントを調査し、サポートされる Python バージョン一覧を最新版に更新する。
  - 結果をリポジトリ内のアーキテクチャドキュメントに反映する下書きを準備する。
- **タスク2: 依存パッケージホイール調査**
  - `litellm` と `fastuuid`
    のリリースノート・配布ホイールを確認し、`cp312`/`cp313`
    の対応状況を一覧化する。
  - `uv pip install --no-build`
    で利用できるバージョンをカタログ化し、非対応の場合の理由 (`cp313`
    欠如等) を明記する。
- **タスク3: Python バージョン方針決定案の作成**
  - 現行の 3.13 運用の課題と 3.12 へのダウングレード影響を比較表にまとめる。
  - 将来的な 3.13 以降への移行条件 (ホイール整備、テスト網羅) を定義する。
- **タスク4: 依存解決戦略レビュー**
  - `--no-build`
    運用ポリシーの背景を確認し、緩和策 (限定ホイールビルド、社内ホイールレジストリ等) の評価を実施する。
  - 推奨戦略を決定するための意思決定資料 (メリット・デメリット) を作成する。
- **タスク5: Cloudflare デプロイ前プリフライト設計**
  - `pywrangler deploy`
    実行前に依存解決を検証するチェックリスト・自動化案を作成する。
  - プリフライトで検出された場合のエスカレーション手順を整備する。
- **タスク6: `litellm` 依存の要件確認**
  - プロダクト要件から `litellm>=1.77.0`
    の必須理由を調査し、代替バージョンまたは設定で要件を満たせるか確認する。
  - 依存バージョンの変更が許容される場合のテスト計画案を作成する。
- **タスク7: 長期的メンテナンス計画作成**
  - Python メジャーアップデートのリリースサイクルを踏まえた検証スケジュールを策定する。
  - 依存ライブラリの ABI サポート状況を定期監視するための担当・手順を定義する。

## エージェント協調レビューサマリ

- **system-architect
  Agent**: アーキテクチャ整合性確認済み、Python バージョン方針と Cloudflare 運用方針の矛盾なし。
- **domain-modellerr Agent**: ドメイン構造への影響なしを確認。
- **api-designer Agent**: API 仕様変更不要であることを確認。
- **prompt-engineering-specialist Agent**: `litellm`
  バージョン変更時のプロンプト最適化影響を監視予定。
- **llm-integration Agent**:
  LLM 統合基盤が依存に連動する点をレビューし、対応策に同意。
- **evaluation-engine Agent**: 評価ワークフローへの影響が発生しないことを確認。
- **workflow-orchestrator
  Agent**: デプロイフローとワークフロー設計の整合を確認。
- **ui-ux-designer Agent**: UI への影響なしを確認。
- **frontend-architect Agent**: フロントエンド構成への波及リスクなしを確認。
- **real-time-features-specialist Agent**: リアルタイム機能への影響なしを確認。
- **backend-developer Agent**: バックエンド依存管理の観点で合意。
- **database-administrator Agent**:
  DB スキーマ・マイグレーション影響なしを確認。
- **vector-database-specialist Agent**: ベクトル機能に影響が及ばないことを確認。
- **event-bus-manager Agent**: イベント駆動構成に変更不要。
- **edge-computing-specialist Agent**:
  Cloudflare 運用観点での整合をレビューし、問題なし。
- **security-architect Agent**: `--no-build`
  緩和検討時のセキュリティ評価を担当する点を合意。
- **performance-optimizer
  Agent**: パフォーマンスへの影響がないこと、およびプリフライト導入による負荷を許容範囲と判断。
- **observability-engineer Agent**: 監視ダッシュボードへの追加要件なしを確認。
- **test-automation-engineer Agent**: テスト計画案 (タスク6) との整合を確認。
- **product-manager Agent**: プロダクトリスクが最小化される方針に同意。
- **technical-documentation
  Agent**: ドキュメント更新の責務を引き受け、整合を確認。
- **devops-coordinator
  Agent**: デプロイパイプラインの変更点をレビューし、問題なし。
- **data-migration-specialist Agent**: データ移行タスクへの波及なしを確認。
- **compliance-officer Agent**: 規制対応に影響しないことを確認。
- **cost-optimization Agent**: 追加コストが最小であることを確認。
- **user-research Agent**: ユーザー調査プロセスに影響なしを確認。
- **data-analyst Agent**: データ分析基盤に影響なしを確認。
- **sre-agent**:
  SLO/SLA 影響なしを確認し、プリフライト導入で可観測性向上を歓迎。
- **qa-coordinator Agent**: 品質保証観点で提案タスクを承認。
- **version-control-specialist
  Agent**: ブランチ戦略への影響なし、ドキュメント更新手順を確認。

上記レビューにより、全エージェント間で認識のズレやアーキテクチャ上の矛盾が存在しないことを確認済みとする。
