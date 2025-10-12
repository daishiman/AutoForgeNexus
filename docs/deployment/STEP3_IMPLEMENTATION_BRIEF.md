# Step 3 実装方針サマリー - `src` 名前空間維持戦略

## 🎯 結論: ハイブリッドアプローチを推奨

**Phase 1 (即効対応)**: `wrangler.toml` 設定変更でsrcを明示的にアップロード
**Phase 2 (長期最適化)**: `pyproject.toml` のwheel構造調整

---

## 📋 4つのアプローチ比較

### ⭐ **推奨: アプローチ1 + 4 (ハイブリッド)**

#### Phase 1: wrangler.toml設定 (優先度: Critical)

```toml
# wrangler.toml に追加
[build.upload]
format = "modules"
main = "./src/main.py"
include = ["src/**/*.py"]
exclude = ["src/**/*_test.py", "src/**/test_*.py", "tests/**"]
```

**メリット**:
- ✅ 即効性: 1日で実装可能
- ✅ 非侵襲的: 既存コード変更なし
- ✅ 可逆性: 設定削除で元に戻る

**デメリット**:
- ⚠️ 容量増加: +400KB (gzip後)
- ⚠️ 重複リスク: wheelとの二重バンドル可能性

**実装工数**: 2日 (設計0.5 + 実装0.5 + 検証1)

---

#### Phase 2: pyproject.toml wheel最適化 (優先度: High)

```toml
# pyproject.toml
[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]

[tool.setuptools.package-dir]
"" = "."
```

**メリット**:
- ✅ 標準準拠: Pythonパッケージングのベストプラクティス
- ✅ 長期保守性: wheel構造の最適化

**デメリット**:
- ⚠️ Pyodide互換性: 動作検証が必要
- ⚠️ pywrangler依存: ツールの挙動が不透明

**実装工数**: 2日 (設計0.5 + 実装0.5 + 検証1)

---

### ❌ **非推奨: アプローチ2 (エントリポイント相対化)**

```python
# 全インポート文を変更
from src.core.config import Settings  # Before
from .core.config import Settings     # After
```

**致命的欠陥**:
- ❌ 大規模変更: 100+ファイルの変更必要
- ❌ 既存コード破壊: ローカル開発環境への影響
- ❌ 保守性低下: インポート文の可読性悪化
- ❌ 要件違反: 「既存コード変更最小化」に反する

**実装工数**: 4.5日 (大量変更によるリスク大)

**評価**: **却下 - 最終手段としてのみ検討**

---

### ⚠️ **条件付き: アプローチ3 (PYTHONPATH追加)**

```python
# src/main.py 冒頭
import sys, os
if "pyodide" in sys.version.lower():
    sys.path.insert(0, os.path.join(os.getcwd(), "src"))
```

**メリット**:
- ✅ 非侵襲的: 既存コード変更なし
- ✅ 即効性: 1ファイル変更のみ

**致命的懸念**:
- ❌ 環境変数サポート不明: CloudflareがPyodideに渡すか未確認
- ❌ デバッグ困難: 実行時エラーの原因特定が困難
- ❌ 暗黙的依存: ランタイム設定に依存

**実装工数**: 2日

**評価**: **Pyodide環境変数サポートの確認が前提**

---

### ⚠️ **選択肢: アプローチ4 (wrangler設定のみ)**

Phase 1の設定のみで運用完結。

**選定条件**:
- Phase 1で完全解決した場合
- wheel変更リスクを回避したい場合
- 容量+400KBが許容範囲内

---

## 📊 総合比較マトリクス

| 観点 | ハイブリッド | 相対化 | PYTHONPATH | wrangler単独 |
|------|------------|--------|------------|--------------|
| **既存コード変更** | なし ✅ | 大 ❌ | なし ✅ | なし ✅ |
| **技術リスク** | 中 ⚠️ | 低 ✅ | 高 ❌ | 中 ⚠️ |
| **工数** | 4日 | 4.5日 | 2日 | 2日 |
| **可逆性** | 高 ✅ | 低 ❌ | 高 ✅ | 高 ✅ |
| **保守性** | 高 ✅ | 低 ❌ | 中 ⚠️ | 高 ✅ |

---

## 🚀 推奨実装手順

### Week 1: Phase 1実装 (Critical)

**Day 1-2: wrangler設定変更**
```bash
# 1. wrangler.toml編集
vim backend/wrangler.toml

# 2. ローカルビルド確認
cd backend
wrangler build --env develop --dry-run

# 3. srcディレクトリ存在確認
find .wrangler/tmp/ -name "src" -type d

# 4. バンドルサイズ測定
du -sh .wrangler/tmp/bundle/
gzip -c .wrangler/tmp/bundle/* | wc -c
```

**Day 3: develop環境デプロイ検証**
```bash
# 1. テストデプロイ
wrangler deploy --env develop

# 2. ログ確認 (importエラー解消確認)
wrangler tail --env develop

# 3. 動作確認
curl https://autoforgenexus-api-develop.workers.dev/
curl https://autoforgenexus-api-develop.workers.dev/api/v1/health
```

---

### Week 2: Phase 2実装 (High)

**Day 1: wheel設定調整**
```bash
# 1. pyproject.toml編集
vim backend/pyproject.toml

# 2. wheelビルド
cd backend
python -m build

# 3. wheel内部構造確認
unzip -l dist/*.whl | grep "src/"
```

**Day 2: Pyodide検証**
```bash
# 1. ローカルPyodideテスト
python -m pyodide run --packages src src/main.py

# 2. importテスト
python -c "import sys; sys.path.insert(0, '.'); from src.core.config import Settings"
```

**Day 3: 重複削除・最適化**
```bash
# 1. バンドル内重複確認
find .wrangler/tmp -name "settings.py" | wc -l

# 2. 重複排除設定調整
# 3. 最終デプロイ検証
```

---

### Week 3: CI/CD統合 (Medium)

**Day 1-2: 検証スクリプト実装**
```yaml
# .github/workflows/cd.yml に追加
- name: Verify src in bundle
  run: |
    wrangler build --env develop --dry-run
    if ! find .wrangler/tmp/ -name "src" -type d | grep -q .; then
      echo "ERROR: src directory not found in bundle"
      exit 1
    fi

- name: Check bundle size
  run: |
    SIZE=$(gzip -c .wrangler/tmp/bundle/* | wc -c)
    LIMIT=26214400  # 25MB
    if [ $SIZE -gt $LIMIT ]; then
      echo "ERROR: Bundle size ${SIZE} exceeds 25MB limit"
      exit 1
    fi
```

**Day 3: ドキュメント更新**
- 設定ガイド作成
- トラブルシューティング追加
- デプロイ手順更新

---

## 🧪 検証チェックリスト

### Phase 1検証

- [ ] `wrangler.toml` に `[build.upload]` 追加
- [ ] ローカルビルドで `src/` 存在確認
- [ ] バンドルサイズ測定 (25MB以内)
- [ ] develop環境デプロイ成功
- [ ] importエラー解消確認
- [ ] API動作確認 (`/`, `/api/v1/health`)

### Phase 2検証

- [ ] `pyproject.toml` 設定調整
- [ ] wheelビルド成功
- [ ] wheel内に `src/` 存在確認
- [ ] Pyodide importテスト通過
- [ ] 重複モジュールなし確認
- [ ] 容量最適化完了

### CI/CD統合

- [ ] バンドル検証スクリプト実装
- [ ] 容量チェック追加
- [ ] プリフライト動作確認
- [ ] GitHub Actions成功

---

## 🚨 リスク管理

### Critical

**重複モジュールバンドル**
- **症状**: wheelとwrangler両方でsrcが含まれる
- **検出**: `find .wrangler/tmp -name "settings.py" | wc -l > 1`
- **対策**: Phase 2でwheel設定を調整し、wrangler側のincludeを削除

**容量超過 (25MB制限)**
- **警告閾値**: 20MB (80%)
- **検出**: CI/CDでgzipサイズを自動測定
- **対策**: 不要ファイル除外、最小依存セット

### High

**Pyodide互換性**
- **症状**: wheel構造がPyodideで解釈されない
- **検出**: ローカルPyodideテスト失敗
- **フォールバック**: wrangler設定のみで運用

---

## 📈 成功基準

### Must (必須)

- ✅ `ModuleNotFoundError: No module named 'src'` 解消
- ✅ 既存コード変更なし
- ✅ バンドルサイズ < 25MB
- ✅ develop環境で正常動作

### Should (推奨)

- ✅ デプロイ時間 +30秒以内
- ✅ 重複モジュールなし
- ✅ ローカル開発環境との整合性維持

### Could (期待)

- ✅ wheel構造最適化完了
- ✅ CI/CD統合完了
- ✅ ドキュメント更新完了

---

## 🎓 意思決定の根拠

### なぜハイブリッドアプローチか

1. **即効性と正攻法の両立**: Phase 1で迅速に問題解決、Phase 2で長期保守性確保
2. **リスク分散**: 片方が失敗しても他方でカバー可能
3. **段階的検証**: 各段階で効果を確認しながら進行
4. **既存コード保護**: インポート文の変更不要

### なぜ相対化を却下したか

1. **要件違反**: 「既存コード変更最小化」に真っ向から反する
2. **保守性悪化**: 将来のリファクタリング負債を生む
3. **アーキテクチャ劣化**: DDD境界の明確性が損なわれる
4. **Git履歴汚染**: 実質的な機能変更なしに大量コミット

### なぜPYTHONPATHを条件付きとしたか

1. **環境変数サポート不明**: Cloudflare WorkersがPyodideに環境変数を渡すか未確認
2. **デバッグ困難**: 実行時エラーの原因特定が困難
3. **暗黙的依存**: ランタイム設定に依存し、透明性が低い

---

## 🔗 関連ドキュメント

- [詳細設計書](./cloudflare_src_namespace_strategy_design.md)
- [Pyodide Module Resolution](./cloudflare_pyodide_module_resolution.md)
- [Payload Limit Strategy](./cloudflare_worker_payload_limit_strategy.md)

---

**作成日**: 2025-10-12
**作成者**: system-architect Agent
**ステータス**: 設計完了 - 実装承認待ち
