# タスク管理モード

**目的**: 複雑な多段階操作のための永続メモリを伴う階層的タスク組織化

## 活性化トリガー

- 協調を必要とする3段階超の操作
- 複数ファイル/ディレクトリスコープ（2ディレクトリ超または3ファイル超）
- フェーズを必要とする複雑な依存関係
- 手動フラグ: `--task-manage`、`--delegate`
- 品質改善要求: polish、refine、enhance

## メモリ付きタスク階層

📋 **計画** → write_memory("plan", goal_statement) → 🎯 **フェーズ** →
write_memory("phase_X", milestone) → 📦 **タスク** → write_memory("task_X.Y",
deliverable) → ✓ **Todo** → TodoWrite + write_memory("todo_X.Y.Z", status)

## メモリ操作

### セッション開始

```
1. list_memories() → 既存のタスク状態を表示
2. read_memory("current_plan") → コンテキストを再開
3. think_about_collected_information() → 中断箇所を理解
```

### 実行中

```
1. write_memory("task_2.1", "completed: auth middleware")
2. think_about_task_adherence() → 軌道に乗っているか検証
3. TodoWriteステータスを並列更新
4. write_memory("checkpoint", current_state) 30分毎
```

### セッション終了

```
1. think_about_whether_you_are_done() → 完了度を評価
2. write_memory("session_summary", outcomes)
3. delete_memory() 完了した一時項目を削除
```

## 実行パターン

1. **読み込み**: list_memories() → read_memory() → 状態再開
2. **計画**: 階層作成 → 各レベルでwrite_memory()
3. **追跡**: TodoWrite + メモリ更新を並列実行
4. **実行**: タスク完了時にメモリ更新
5. **チェックポイント**: 状態保存のため定期的にwrite_memory()
6. **完了**: 結果を伴う最終メモリ更新

## ツール選択

| タスクタイプ         | プライマリツール   | メモリキー         |
| -------------------- | ------------------ | ------------------ |
| 分析                 | Sequential MCP     | "analysis_results" |
| 実装                 | MultiEdit/Morphllm | "code_changes"     |
| UIコンポーネント     | Magic MCP          | "ui_components"    |
| テスト               | Playwright MCP     | "test_results"     |
| ドキュメンテーション | Context7 MCP       | "doc_patterns"     |

## メモリスキーマ

```
plan_[timestamp]: 全体目標ステートメント
phase_[1-5]: 主要マイルストーン記述
task_[phase].[number]: 特定の成果物ステータス
todo_[task].[number]: アトミックアクション完了
checkpoint_[timestamp]: 現在状態スナップショット
blockers: 注意を要する積極的な阻害要因
decisions: 行われた主要なアーキテクチャ/設計選択
```

## 例

### セッション1: 認証タスク開始

```
list_memories() → 空
write_memory("plan_auth", "JWT認証システムを実装")
write_memory("phase_1", "分析 - セキュリティ要件レビュー")
write_memory("task_1.1", "pending: 既存認証パターンをレビュー")
TodoWrite: 5つの具体的なtodoを作成
task 1.1を実行 → write_memory("task_1.1", "completed: 3つのパターンを発見")
```

### セッション2: 中断後の再開

```
list_memories() → plan_auth、phase_1、task_1.1を表示
read_memory("plan_auth") → "JWT認証システムを実装"
think_about_collected_information() → "分析完了、実装開始"
think_about_task_adherence() → "軌道に乗っている、フェーズ2に移行"
write_memory("phase_2", "実装 - ミドルウェアとエンドポイント")
実装タスクを継続...
```

### セッション3: 完了チェック

```
think_about_whether_you_are_done() → "テストフェーズが未完了"
残りテストタスクを完了
write_memory("outcome_auth", "95%テストカバレッジで実装成功")
delete_memory("checkpoint_*") → 一時状態をクリーン
write_memory("session_summary", "認証システム完了・検証済")
```
