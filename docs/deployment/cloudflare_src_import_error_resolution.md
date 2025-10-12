# Cloudflare Python Worker `src` 名前空間解決ドキュメント

## 目的

- デプロイ中に発生する `ModuleNotFoundError: No module named 'src'`
  の根本原因分析を行い、解決策の実装手順をまとめる。
- 解決策を段階的に進めるためのタスクを定義。
- 各タスクに担当エージェントを割り当て、具体的なアクションと成果物を明示する。

## 背景

- Cloudflare Workers ベータ版の Python
  Worker は Pyodide を使用し、Pyodide のモジュール探索パスに依存する。
- `pywrangler` によってバンドルされたファイルでは `src/`
  プレフィックスが取り除かれ、Pyodide 上では `core/config/settings.py`
  のように展開される。
- エントリポイント `main.py` を含むコードは
  `from src.core.config.settings import Settings` のように `src`
  を含む絶対パスでインポートしている。
- この整合性の欠如により `ModuleNotFoundError` が発生している。

## 根本原因

1. **バンドル構造**: バンドルされたモジュールのパスが `src/`
   プレフィックスを持たない。
   - 例: `/session/metadata/core/config/settings.py`。
2. **`__init__.py` の欠落**: バンドルされたディレクトリ内に多数の `__init__.py`
   が存在せず、パッケージとして認識されない。
3. **`wrangler.toml` の設定不足**: `build.upload`
   設定が wrangler で無視されており、`src`
   ディレクトリを意図した形でアップロードできていない。

## 解決策の概要

- **Phase 1: wrangler 設定の調整**
  - `wrangler.toml` の `build.upload` 設定を公式推奨構成に合わせる。
  - `[[routes]]` や `services` に依存しない構成にする。
- **Phase 2: パッケージレイアウトの見直し**
  - `pyproject.toml` の `package-dir` を確認し、`src`
    ディレクトリを適切にパッケージ化する。
  - `__init__.py` を欠落しているすべてのディレクトリに追加する。
- **Phase 3: CI/CD での検証手順の確立**
  - バンドル後に重要なモジュールが `src`
    を前提としたインポートで解決できるかを TTY で検証するスクリプトを追加。
  - 重複モジュール警告や容量超過の監視を統合する。

## タスク一覧

| Step | タスク内容                 | 担当エージェント                   | 詳細手順                                                                               | 成果物                   |
| ---- | -------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------- | ------------------------ |
| 1    | 現状の wrangler 設定の確認 | **devops-coordinator Agent**       | wrangler デプロイログと Config の差異を確認する。                                      | Gap 分析メモ             |
| 2    | バンドル構造の分析         | **backend-developer Agent**        | `pywrangler` が生成する wheel を展開し、モジュール構造を確認する。                     | バンドル構造分析レポート |
| 3    | `wrangler.toml` の見直し   | **system-architect Agent**         | `build.upload` から公式対策（`modules` 形式）へ変更する案を検討し実装する。            | wrangler 設定変更案      |
| 4    | `__init__.py` 配置         | **backend-developer Agent**        | すべてのフォルダに `__init__.py` が存在するか確認し、不足を補完。                      | `__init__.py` リスト     |
| 5    | インポート整合性検証       | **test-automation-engineer Agent** | ローカル/CI で `python -c "from core.config import settings"` を実行し成功するか確認。 | テストログ               |
| 6    | 継続的なモニタリング設定   | **observability-engineer Agent**   | Cloudflare デプロイ時にこのエラーが再発した場合アラートが出るよう監視を設定。          | アラートルール           |

## 参考資料

- `docs/deployment/cloudflare_python_module_resolution_action_plan.md`
- `docs/deployment/cloudflare_bundle_structure_analysis.md`
- `docs/deployment/cloudflare_src_namespace_strategy_design.md`
- Cloudflare Workers 公式ドキュメント（Python 52）
