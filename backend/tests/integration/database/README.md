# Database Integration Tests

Phase 4のデータベース統合テストガイド

## 🚀 クイックスタート

```bash
# すべてのデータベーステストを実行
pytest tests/integration/database/test_database_connection.py -v

# 特定のテストクラスのみ実行
pytest tests/integration/database/test_database_connection.py::TestPromptCRUD -v

# カバレッジレポート付きで実行
pytest tests/integration/database/ --cov=src/infrastructure --cov-report=html
```

## 📋 テストカテゴリ

### 1. データベース接続テスト
```bash
pytest tests/integration/database/test_database_connection.py::TestDatabaseConnection -v
```
- ローカル/本番環境の接続URL取得
- エンジン・セッション作成
- シングルトンパターン検証

### 2. テーブル存在確認テスト
```bash
pytest tests/integration/database/test_database_connection.py::TestTableExistence -v
```
- テーブル作成確認
- カラム構造検証
- インデックス確認

### 3. CRUD操作テスト
```bash
# プロンプトCRUD
pytest tests/integration/database/test_database_connection.py::TestPromptCRUD -v

# 評価CRUD
pytest tests/integration/database/test_database_connection.py::TestEvaluationCRUD -v

# テスト結果CRUD
pytest tests/integration/database/test_database_connection.py::TestTestResultCRUD -v
```

### 4. DDD境界テスト
```bash
pytest tests/integration/database/test_database_connection.py::TestDDDBoundaries -v
```
- 集約間のID参照
- 集約内relationship

### 5. パフォーマンステスト
```bash
pytest tests/integration/database/test_database_connection.py::TestDatabasePerformance -v
```
- バルクインサート（100件 < 1秒）
- インデックス付きクエリ（< 0.1秒）

## 🔧 環境設定

### 必須環境変数
```bash
# テスト用（自動設定）
export APP_ENV=local
export DATABASE_URL=sqlite:///./test_autoforge.db
```

### Redis接続テスト（オプション）
Redis実行中の場合のみ：
```bash
# Redisを起動
redis-server --daemonize yes

# Redis接続テストを有効化
export SKIP_REDIS_TESTS=false

# テスト実行
pytest tests/integration/database/test_database_connection.py::TestRedisConnection -v
```

## 📊 期待される結果

```
=================== 31 passed, 1 skipped, 1 warning in 1.33s ===================

テストサマリー:
- ✅ 31 テスト成功
- ⏭️ 1 テストスキップ（Redis接続テスト）
- ⚠️ 1 警告（TestResultModel命名の競合、影響なし）
```

## 🐛 トラブルシューティング

### エラー: `AttributeError: 'Settings' object has no attribute 'DEBUG'`
**原因**: 設定ファイルでは`debug`（小文字）を使用
**解決**: `turso_connection.py`で`self.settings.debug`を使用

### エラー: `ArgumentError: delete-orphan cascade`
**原因**: 自己参照関係での不適切なcascade設定
**解決**: `cascade="all, delete"`に変更（`delete-orphan`削除）

### エラー: 外部キー制約が機能しない
**原因**: SQLiteではデフォルトでFK制約が無効
**解決**: テストフィクスチャで`PRAGMA foreign_keys=ON`実行済み

## 📝 テストデータのクリーンアップ

```bash
# テストDB削除（自動実行）
rm -f ./test_autoforge.db

# すべてのテストDBファイル削除
find . -name "test_*.db" -delete
```

## 🎯 DDD原則の確認

### ✅ 正しい実装例
```python
# 集約間アクセスはIDで参照
prompt_id = evaluation.prompt_id
prompt = session.query(PromptModel).filter_by(id=prompt_id).first()

# 集約内relationshipは使用可能
test_results = evaluation.test_results
```

### ❌ 誤った実装例
```python
# 集約境界を越えるrelationship（使用禁止）
prompt = evaluation.prompt  # <- NG
```

## 📚 関連ドキュメント

- [Phase 4実装レポート](/docs/reports/phase4_database_integration_tests.md)
- [データベースセットアップガイド](/docs/setup/DATABASE_SETUP_GUIDE.md)
- [DDDアーキテクチャ](/docs/architecture/backend_architecture.md)

## 🚀 次のステップ

1. リポジトリパターン実装
2. Redis統合テスト
3. libSQL Vector検索テスト
4. マイグレーション自動化
