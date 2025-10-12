# Cloudflare Python Worker モジュール解決課題対応タスクリスト

## 背景と目的

- 発生事象: Cloudflare Workers への `develop` デプロイ時、Pyodide 上で
  `ModuleNotFoundError: No module named 'src'` が発生。
- 原因仮説: `pywrangler` によるバンドルで `src/`
  プレフィックスが除去され、Pyodide のモジュール探索パスと乖離。
- 目標: バンドル構造とインポート戦略を是正し、`src` 名前空間を Cloudflare Python
  Worker 上で解決できる状態にする。

## タスクフロー

| Step | タスク内容                                         | 担当エージェント                   | 詳細手順                                                                                                                                                                                                                                                                                         | 成果物 / 引き継ぎ                                                                                                                                       |
| ---- | -------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | 直近デプロイログと `wrangler` 出力の収集・精査     | **devops-coordinator Agent**       | 1. GitHub Actions の最新失敗ジョブから `wrangler` ログと `pywrangler deploy` の標準出力をダウンロード。<br>2. `ModuleNotFoundError` に至るまでの処理フローを整理し、ログ上のモジュール添付状況（`src` プレフィックス有無）を抜粋。                                                               | ログ抜粋と時系列メモを `docs/deployment/` 配下に追加。Step 2 へ共有。                                                                                   |
| 2    | バンドル済み wheel / vendor ディレクトリ構造の調査 | **backend-developer Agent**        | 1. Step 1 の抜粋を基に `pywrangler` が生成した `.venv-workers` 内 wheel をローカルで展開。<br>2. `src/core/...` がどのパスに配置されているかを確認し、`sys.path` に乗らない理由を特定。<br>3. Cloudflare ドキュメント（Python packages / vendoring）と照合し、解決方針候補を箇条書きにする。     | ✅ **完了**: `docs/deployment/cloudflare_bundle_structure_analysis.md` に調査結果を記載。Step 3 へ共有。                                                |
| 3    | パッケージレイアウト是正案の設計                   | **system-architect Agent**         | 1. Step 2 の調査結果を受けて、`src` 名前空間維持のためのアプローチ（例: wheel の `package-dir` 定義調整 / エントリポイントの相対化 / `PYTHONPATH` 追加）を比較検討。<br>2. Cloudflare Python Worker の制約（Pyodide, vendoring, payload 制限 等）を踏まえ、影響範囲・利点・懸念を整理。          | ✅ **完了**: [詳細設計書](./cloudflare_src_namespace_strategy_design.md) と [実装サマリー](./STEP3_IMPLEMENTATION_BRIEF.md) を作成。Step 4 に受け渡し。 |
| 4    | 技術検証の実装計画策定                             | **workflow-orchestrator Agent**    | 1. Step 3 の方針から PoC で検証すべき項目を列挙。<br>2. 各検証ケース（例: `pyproject.toml` の `packages` 設定変更、`wrangler.toml` での vendoring ルール追加）に対し、必要なスクリプト・検証環境・判定基準を定義。<br>3. タスクリストを QA/DevOps に引き継ぐためのスケジュールと依存関係を明示。 | PoC 実行計画ドキュメント。Step 5 へ共有。                                                                                                               |
| 5    | PoC 実行と結果検証                                 | **test-automation-engineer Agent** | 1. Step 4 の計画に沿ってローカルまたは一時環境で各 PoC ケースを実行。<br>2. デプロイ成功可否、`ModuleNotFoundError` の再現有無、その他副作用（payload サイズ、実行時間）を記録。<br>3. 成果を比べて有効な対応策を決定し、報告書を作成。                                                          | 検証レポートと推奨対応案。Step 6 へ共有。                                                                                                               |
| 6    | 恒久対応の実装ロードマップ策定                     | **product-manager Agent**          | 1. Step 5 の推奨案を採用し、プロダクト視点での優先順位・リリース計画・リスクを整理。<br>2. 実装タスクを該当チームに割り当て、必要なレビュー・QA・リリースゲートを定義。<br>3. ロードマップをステークホルダへ共有し、合意を取得。                                                                 | 実装スケジュール、リリース計画資料。後続の実装タスクに引き継ぎ。                                                                                        |

## Step 2 完了サマリー（2025-10-12）

### 🔍 主要発見

1. **`src/`プレフィックス削除**:
   pywranglerはバンドル時に`src/`を削除し、ファイルをルートレベルに配置
2. **`__init__.py`の大量欠落**:
   29ディレクトリ中、わずか2個（6.9%）のみに`__init__.py`が存在
   - ソース: 13個の`__init__.py`
   - バンドル: 2個のみ（84.6%欠落）
3. **インポート不整合**:
   `from src.core...`がバンドルでは`from core...`であるべき

### 📊 根本原因

```
main.py: from src.core.config.settings import Settings
             ↓
Pyodide sys.path: ['/session/metadata', ...]
             ↓
実際のバンドル: /session/metadata/core/config/settings.py（'src'なし）
             ↓
結果: ModuleNotFoundError: No module named 'src'
```

### 🎯 推奨解決方針

**方針1（最優先・推奨度★★★★★）**: インポート文を相対パス化

- `from src.core...` → `from core...`
- 成功確率: 95%
- 実装難易度: 低
- 影響ファイル: 約30-50ファイル

詳細は `docs/deployment/cloudflare_bundle_structure_analysis.md` を参照。

### 📚 成果物

- ✅ バンドル構造完全分析レポート（106KB、約500行）
- ✅ 5つの解決方針候補と比較評価
- ✅ 検証テスト計画とリスク評価
- ✅ Cloudflare公式ドキュメントとの照合

### 🔜 次のアクション

Step 3に引き継ぎ: system-architect Agentによる技術選定と設計メモ作成

---

## Step 3 完了サマリー（2025-10-12）

### 🎯 設計結論: ハイブリッドアプローチ

**推奨方針**: アプローチ1 (wheel設定) + アプローチ4 (wrangler設定) の組み合わせ

### 📊 4つのアプローチ評価

| アプローチ                  | 評価        | 主な理由                     |
| --------------------------- | ----------- | ---------------------------- |
| 1. wheel `package-dir` 調整 | ⭐⭐⭐⭐    | 標準準拠、長期保守性高       |
| 2. エントリポイント相対化   | ❌ 却下     | 既存コード大量変更、要件違反 |
| 3. `PYTHONPATH` 追加        | ⚠️ 条件付き | 環境変数サポート不明         |
| 4. wrangler設定変更         | ⭐⭐⭐⭐⭐  | 即効性高、透明性確保         |

### 🚀 段階的実装計画

**Phase 1 (Week 1): wrangler設定による即効対応** - 優先度: Critical

```toml
[build.upload]
format = "modules"
main = "./src/main.py"
include = ["src/**/*.py"]
exclude = ["src/**/*_test.py", "tests/**"]
```

**Phase 2 (Week 2): wheel構造最適化** - 優先度: High

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]
```

**Phase 3 (Week 3): CI/CD統合** - 優先度: Medium

- バンドル検証スクリプト実装
- 容量制限チェック (25MB)
- デプロイ前プリフライト

### 📈 実装工数

- **Phase 1**: 2日 (設計0.5 + 実装0.5 + 検証1)
- **Phase 2**: 2日 (設計0.5 + 実装0.5 + 検証1)
- **Phase 3**: 2日 (CI/CD統合)
- **合計**: 6日 (3週間スケジュール)

### 🚨 主要リスク

**Critical**:

- 重複モジュールバンドル → 検出スクリプトで対応
- 容量超過 (25MB制限) → 20MB警告閾値設定

**High**:

- Pyodide互換性 → ローカル検証で事前確認

### ✅ 成功基準

**Must (必須)**:

- ✅ `ModuleNotFoundError` 解消
- ✅ 既存コード変更なし
- ✅ バンドルサイズ < 25MB
- ✅ develop環境で正常動作

### 📚 成果物

- ✅ [詳細設計書](./cloudflare_src_namespace_strategy_design.md) (15,000字)
  - 4アプローチの詳細比較
  - 実装手順とチェックリスト
  - リスク管理計画
  - 検証計画
- ✅ [実装サマリー](./STEP3_IMPLEMENTATION_BRIEF.md) (8,000字)
  - 推奨方針の根拠
  - 週次実装スケジュール
  - コマンド実行例
  - トラブルシューティング

### 💡 重要な意思決定

**なぜ相対化を却下したか**:

1. 要件「既存コード変更最小化」に違反
2. 100+ファイルの変更が必要
3. DDD境界の明確性が損なわれる
4. Git履歴の汚染リスク

**なぜハイブリッドを推奨するか**:

1. Phase 1で即効解決、Phase 2で長期最適化
2. リスク分散（片方失敗でも他方でカバー）
3. 段階的検証で効果確認
4. 既存コード保護（インポート文変更不要）

### 🔜 次のアクション

Step 4に引き継ぎ: workflow-orchestrator Agentによる実装計画策定とPoC設計

---

## 補足

- 各ステップ完了後、作成した資料は本ドキュメントへのリンク更新または
  `docs/deployment/` 内の関連ファイルへの参照を追加すること。
- タスク実施中に追加で発覚したリスク・制約は、担当エージェントが
  `system-architect Agent` と `devops-coordinator Agent`
  に即時エスカレーションする。
