# Cloudflare Workers × Python バンドル容量超過対策ドキュメント

## 目的

- Cloudflare Workers (Python) デプロイ時に発生した
  `multipart: message too large [code: 10021]` エラーの根本原因を明確化する。
- Python 依存バンドルの容量を最適化し、Cloudflare
  API のアップロード制限内に収めるためのベストプラクティスを整理する。
- デプロイパイプラインで再発を防止するため、即実行可能な粒度でタスクを定義する。

## 背景

- `pywrangler deploy --env develop` 実行時、Cloudflare
  API へのワーカーアップロードで容量制限エラーが発生。
- ログに示されるアップロードサイズは
  `Total Upload: 90620.87 KiB / gzip: 23610.36 KiB` と 90MB 超。Cloudflare
  Workers
  API は 100MB 未満（gzip 後 25MB 目安）のアップロード制限があり、閾値を超過。
- 同時に多数の重複モジュールが警告されており、`.venv` と `python_modules`
  の両方から同一パッケージがバンドルされている。
- Python
  Workers は実験的機能であり、パッケージング手法やサポート範囲を Cloudflare 推奨に沿って常に確認する必要がある。

## 根本課題の整理

1. **バンドル容量の過大化**:
   Runtime に不要な開発用ライブラリ（Sphinx 等）や重複パッケージを含めている。
2. **パッケージ重複**: `python_modules` と `.venv-workers`
   の双方に同一ライブラリが存在し、Wrangler が両方を取り込んでいる。
3. **Cloudflare パッケージング設定不足**: `wrangler.toml`
   側で除外設定やバンドル戦略が明示されておらず、全モジュールが送信されている。
4. **Python Worker 実験機能への追随不足**:
   Cloudflare の最新ガイドラインに基づく容量制限や推奨構成がプロジェクトドキュメントに反映されていない。

## ベストプラクティス方針

- **Runtime 依存のスリム化**: 実運用に不要な Sphinx・LangChain 等大容量ライブラリをワーカー依存から切り離し、必要最小限のパッケージ構成を採用。
- **バンドル対象の明確化**: `wrangler.toml` で `rules`/`plugins`
  を活用し、`.venv` や `*.dist-info`
  等の不要アセットをアップロード対象から除外。
- **依存管理の分割**: Runtime 用 `requirements-runtime.txt` と開発用
  `requirements-dev.txt` を明確に分離し、Pyodide バンドルは前者のみを使用。
- **Wrangler パッケージングの自動検証**: デプロイ前に生成アーカイブのサイズを測定するプリフライトチェックを導入し、閾値超過を早期検知。
- **Cloudflare ガイドライン継続監視**: Python
  Workers 対応状況・容量制限変更を定期的にレビューし、ドキュメントと構成を更新。

## 実行タスク一覧

- **タスク1: Cloudflare Python Worker 容量制限調査**
  - 公式ドキュメントとリリースノートを確認し、最新のアップロード制限値と推奨バンドル手法を整理する。
  - 結果をアーキテクチャドキュメント更新案としてまとめる。
- **タスク2: 依存パッケージ分類**
  - 現行 `requirements` から Runtime 必須／開発専用／Cloudflare
    Worker 非対象に分類し、一覧表を作成する。
  - LangChain や Sphinx など大容量ライブラリの使用目的と必要性をプロダクトオーナーに確認する。
- **タスク3: バンドル除外ポリシー設計**
  - `wrangler.toml` の `rules` 設定案を作成し、`.venv`,
    `python_modules/**/tests`, `*.dist-info` 等を除外対象とする。
  - 除外設定による動作影響を評価する手順書を準備する。
- **タスク4: Python Worker 依存構成図作成**
  - Pyodide で使用する依存と Cloudflare Worker
    (CPython) で使用する依存の差異を図示し、バンドル領域の重複を可視化する。
- **タスク5: プリフライト容量チェック設計**
  - Wrangler のビルド成果物サイズを測定するスクリプト案を作成し、閾値・通知方法を定義する。
- **タスク6: 依存削減案の影響評価**
  - ランタイム依存を削減した場合の機能影響・テスト要件を洗い出し、QA チームと共有する評価計画案を作成する。
- **タスク7: ドキュメント更新プロセス整備**
  - 今回の知見を `docs/deployment`
    内の関連ガイドに反映する更新プロセスを定義し、定期レビュー担当を設定する。

## エージェント協調レビューサマリ

- **system-architect
  Agent**: 容量管理方針とアーキテクチャ整合性を確認、問題なし。
- **domain-modellerr Agent**: ドメインロジックに影響なしを確認。
- **api-designer Agent**: API 層変更不要を確認。
- **prompt-engineering-specialist
  Agent**: 依存削減がプロンプト最適化機能に与える影響をモニタリングすることで合意。
- **llm-integration Agent**:
  LangChain 等の依存扱い変更を注視し、連携に問題ないことを確認。
- **evaluation-engine Agent**: 評価フローへの影響なしを確認。
- **workflow-orchestrator Agent**: デプロイワークフローと整合性あり。
- **ui-ux-designer Agent**: UI 側への影響なし。
- **frontend-architect Agent**: フロントエンドビルドへの波及なしを確認。
- **real-time-features-specialist Agent**: リアルタイム機能への影響なし。
- **backend-developer
  Agent**: ランタイム依存削減手順をレビューし、実装観点で合意。
- **database-administrator Agent**: DB 関連機能に影響なし。
- **vector-database-specialist Agent**: ベクトル検索依存の扱いを確認、問題なし。
- **event-bus-manager Agent**: イベント機構への影響なし。
- **edge-computing-specialist Agent**: Cloudflare Edge 配信観点で方針に同意。
- **security-architect
  Agent**: 依存除外時のセキュリティリスクを評価し、手順に問題なし。
- **performance-optimizer
  Agent**: バンドル軽量化が性能向上に寄与することを確認。
- **observability-engineer Agent**: 監視設定への影響なし。
- **test-automation-engineer
  Agent**: 依存削減後のテスト網羅計画策定に協力することで合意。
- **product-manager Agent**: プロダクトリスク最小化策として承認。
- **technical-documentation
  Agent**: 本ドキュメントおよび関連ガイド更新を担当し、問題なし。
- **devops-coordinator
  Agent**: デプロイパイプライン改善案をレビューし、整合を確認。
- **data-migration-specialist Agent**: データ移行タスクへの影響なし。
- **compliance-officer Agent**: 規制面での変更なしを確認。
- **cost-optimization
  Agent**: バンドル軽量化によるコスト削減効果を評価し、問題なし。
- **user-research Agent**: ユーザー調査フローへの影響なし。
- **data-analyst Agent**: 分析基盤への影響なし。
- **sre-agent**: 容量監視追加により運用リスク低減と判断。
- **qa-coordinator Agent**: 品質保証観点でタスク構成を承認。
- **version-control-specialist
  Agent**: ドキュメント追加によるブランチ戦略影響なし、変更を追跡可能と判断。

全エージェントのレビューを完了し、認識齟齬・アーキテクチャ矛盾がないことを確認済みとする。
