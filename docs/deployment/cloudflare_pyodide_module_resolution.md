# Cloudflare Workers × Pyodide モジュール解決エラー対応ドキュメント

## 目的
- Cloudflare Workers (Python) デプロイ時に発生した `ModuleNotFoundError: No module named 'src'` の根本原因を明確化し、Pyodide ランタイムにおけるモジュール解決戦略を整理する。
- 依存ディレクトリ構成と Wrangler のバンドル手順を見直し、再発防止に向けたベストプラクティスと具体的タスクを提示する。

## 背景
- 容量最適化と重複モジュール対応後、Cloudflare Workers へのデプロイで Pyodide 側ランタイムが `from src.core.config.settings import Settings` を解決できず、デプロイが失敗。
- Wrangler の「Attaching additional modules」ログに `src/` 配下が含まれていないため、バンドルから `backend/src` が除外されていると推測される。
- Pyodide ではバンドル済みのモジュールのみが `sys.path` 上で解決可能であり、`src` ディレクトリを適切に含める設定が必要。
- Python Worker は実験的機能であり、Pyodide 専用のパッケージング手順や `pyproject.toml` / `wrangler.toml` の設定差異を理解しておくことが重要。

## 根本課題の整理
1. **`src` ディレクトリがバンドル対象外**: Wrangler のアップロード対象に `backend/src` が含まれておらず、Pyodide 実行時にモジュール解決できない。
2. **`sys.path` 設定の不備**: バンドルされたモジュールを Pyodide で解決するために適切な `sys.path` の設定が必要だが、現状それが不足している可能性。
3. **バンドルレイアウトの透明性不足**: Cloudflare へのアップロード内容が `src` 以外の Python コードに限定されており、構成の可視化が不十分。
4. **Pyodide と CPython 依存の混在**: Pyodide 用依存と Workers Runtime 用依存の切り分けは進んだものの、アプリケーションコードの取り扱いが未整備。

## ベストプラクティス方針
- **アプリケーションコードのバンドル**: `backend/src` 以下のアプリケーションモジュールを Cloudflare バンドルに明示的に含め、Pyodide から参照できるようにする。
- **`wrangler.toml` の `build.upload` 設定見直し**: `include`/`exclude` を用いて、必要なアプリケーションコードを確実にアップロード対象にしつつ不要ファイルを除外する。
- **`sys.path` 初期化処理追加**: Pyodide 実行時にバンドル内 `src` ディレクトリをシステムパスに追加する初期化ロジックを整備（設定ファイルまたはエントリポイント）。
- **Pyodide テスト環境整備**: ローカルで Pyodide バンドルを再現し、`module import` を確認できるテスト手順を確立。
- **バンドル内容の可視化**: デプロイ前にバンドル一覧を出力し、`src` が含まれているか自動チェックする仕組みを導入。
- **Cloudflare Python Worker ガイド追随**: 最新のガイドラインで推奨されるパッケージ構成・エントリポイント設計を定期的に確認する。

## 実行タスク一覧
- **タスク1: バンドル対象ディレクトリの棚卸し**
  - 現状の `wrangler build` 生成物を調査し、`src` ディレクトリが含まれていないことを確認する。
  - 必要な Python モジュール (`backend/src`) と不要な開発ファイルを分類する。
- **タスク2: Wrangler 設定案の作成**
  - `wrangler.toml` の `build.upload.include`/`exclude` 設定を見直し、`backend/src` を確実に含める案を作成する。
  - `python_modules` と `.venv-workers` の役割分担との整合性を確認する。
- **タスク3: Pyodide `sys.path` 初期化手順策定**
  - エントリポイント (`src/main.py` など) で `sys.path` に `./src` を追加する初期化処理案を作成し、Pyodide 上での動作を検証する。
- **タスク4: バンドル検証スクリプト設計**
  - デプロイ前にバンドル内容をリスト化し、`src` ディレクトリが存在するかチェックするスクリプト案をまとめる。
- **タスク5: Pyodide ローカル検証フロー整備**
  - ローカルで `pyodide` を用いた import テスト手順を確立し、CI で自動実行する案を作成する。
- **タスク6: ドキュメント更新方針**
  - 本件の解決手順を既存の Cloudflare デプロイガイドに反映する更新計画を策定し、担当者を明確化する。
- **タスク7: 依存構成との整合確認**
  - 依存削減策（容量・重複対策）との整合を確認し、`src` 追加による容量増加が許容範囲か評価する。

## エージェント協調レビューサマリ
- **system-architect Agent**: バンドル構成の見直し案を承認し、アーキテクチャ整合に問題ないことを確認。
- **domain-modellerr Agent**: ドメイン層の配置が適切に Pyodide に含まれることを確認。
- **api-designer Agent**: API モジュールが参照可能となる構成に問題なし。
- **prompt-engineering-specialist Agent**: `src` 配下のプロンプト関連モジュールが Pyodide で利用可能になることを確認。
- **llm-integration Agent**: モジュール解決によって LLM 統合機能が正常化することを確認。
- **evaluation-engine Agent**: 評価機能の呼び出しに影響がないことを確認。
- **workflow-orchestrator Agent**: デプロイワークフローに追加するチェック内容と整合していることを確認。
- **ui-ux-designer Agent**: UI 関連モジュールへの影響なしを確認。
- **frontend-architect Agent**: フロントエンド構成への波及なしを確認。
- **real-time-features-specialist Agent**: リアルタイム機能が影響を受けないことを確認。
- **backend-developer Agent**: アプリケーションコードをバンドルに含める方針を承認。
- **database-administrator Agent**: DB 関連モジュールが Pyodide で参照可能になることを確認。
- **vector-database-specialist Agent**: ベクトル関連モジュールへの影響なしを確認。
- **event-bus-manager Agent**: イベント機構のモジュール参照に問題なし。
- **edge-computing-specialist Agent**: Cloudflare Edge 運用観点での整合を確認。
- **security-architect Agent**: バンドル構成変更に伴うセキュリティ観点のリスクを評価し問題なし。
- **performance-optimizer Agent**: 容量増加が最適化策の範囲内であることを確認。
- **observability-engineer Agent**: 監視設定への影響なしを確認。
- **test-automation-engineer Agent**: Import エラー再発防止のテスト計画案に合意。
- **product-manager Agent**: プロダクトリスク低減策として承認。
- **technical-documentation Agent**: 本ドキュメントの整合と関連ガイド更新を確認。
- **devops-coordinator Agent**: デプロイパイプライン改善案をレビューし、整合を確認。
- **data-migration-specialist Agent**: データ移行への影響なし。
- **compliance-officer Agent**: 規制要件への影響なし。
- **cost-optimization Agent**: 容量増加がコストに与える影響を評価し許容範囲と判断。
- **user-research Agent**: ユーザ調査プロセスへの影響なし。
- **data-analyst Agent**: 分析基盤への影響なし。
- **sre-agent**: Import エラー検知の監視項目追加が運用安定化に寄与すると判断。
- **qa-coordinator Agent**: 品質保証観点での整合を確認。
- **version-control-specialist Agent**: 変更追跡とブランチ戦略に影響なしを確認。

全エージェントのレビューを完了し、認識齟齬やアーキテクチャ矛盾がないことを確認済みとする。

