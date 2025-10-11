# GitHub テンプレート活用ワークフローガイド

## 🎯 個人開発での具体的な使用例

### シナリオ1: バグを発見した場合

```bash
# 1. バグを発見
# 例: プロンプト保存機能が動作しない

# 2. GitHubでIssueを作成
# → Issues → New issue → 🐛 Bug Report を選択

# 3. テンプレートに従って詳細を記入
# - バグの説明: "プロンプト保存ボタンが機能しない"
# - 再現手順: 明確に記載
# - 深刻度: Critical（サービスが使用不可）

# 4. Issueが作成される → Issue番号が発行される（例: #15）

# 5. 修正用ブランチを作成
git checkout -b fix/prompt-save-issue-15

# 6. 修正を実装
# コードを修正...

# 7. コミット（Issue番号を含める）
git commit -m "fix: プロンプト保存機能のバグを修正 #15"

# 8. プッシュしてPR作成
git push origin fix/prompt-save-issue-15

# 9. PRテンプレートを記入
# - 概要: "Issue #15 のバグを修正"
# - 変更タイプ: [x] 🐛 バグ修正
# - 関連Issue: Resolves #15

# 10. Claude Codeでレビュー
# PRのURLをClaude Codeに共有してレビューを依頼
```

### シナリオ2: 新機能を追加する場合

```bash
# 1. アイデアをIssueとして記録
# → Issues → New issue → ✨ Feature Request を選択

# 2. 機能の詳細を記入
# - 解決したい問題: "マルチLLMの切り替えが面倒"
# - 提案する解決策: "ドロップダウンで簡単切り替え"
# - 優先度: Must Have

# 3. Issue番号が発行される（例: #20）

# 4. 実装開始
git checkout -b feature/llm-switcher-20

# 5. 実装...

# 6. PR作成時
# テンプレートの全項目を埋める
# 特に重要：
# - テスト手順（Claude Codeが再現できるように）
# - スクリーンショット（UI変更の場合）
# - セキュリティ考慮事項
```

### シナリオ3: 質問や相談がある場合

```bash
# 1. Issueで質問
# → Issues → New issue → ❓ Question を選択

# 2. 詳細を記入
# - 質問カテゴリー: "設定・カスタマイズ"
# - 質問内容: "Turso DBの接続設定方法"
# - 試したこと: "ドキュメント確認、環境変数設定"

# 3. Claude Codeに相談
# IssueのURLを共有して解決策を相談
```

## 🔄 GitHubとClaude Codeの連携フロー

### 1. **Issue作成 → Claude Code分析**

```
あなた: GitHubでIssue作成
↓
Claude Code: "Issue #25を確認しました。実装方針を提案します..."
↓
あなた: 実装開始
```

### 2. **PR作成 → Claude Codeレビュー**

```
あなた: PR作成（テンプレート記入）
↓
Claude Code: PRレビュー
- コード品質チェック
- セキュリティ確認
- テスト確認
↓
あなた: フィードバックに基づいて修正
```

### 3. **継続的な改善サイクル**

```
Issue（問題・アイデア）
  ↓
ブランチ作成・実装
  ↓
PR作成（テンプレート活用）
  ↓
Claude Codeレビュー
  ↓
マージ・デプロイ
  ↓
次のIssueへ
```

## 📋 テンプレート活用のベストプラクティス

### Issue管理

1. **すべてのタスクをIssue化**

   - 思いついたアイデア → Feature Request
   - 見つけたバグ → Bug Report
   - わからないこと → Question

2. **Issue番号の活用**

   ```bash
   # ブランチ名に含める
   git checkout -b feature/search-42

   # コミットメッセージに含める
   git commit -m "feat: 検索機能を追加 #42"

   # PRで自動クローズ
   "Resolves #42" # PRマージ時にIssueが自動クローズ
   ```

3. **ラベルの活用**
   - 自動的に付与: `bug`, `enhancement`, `question`
   - 追加可能: `priority:high`, `in-progress`, `blocked`

### PR管理

1. **小さく頻繁にPR**

   - 大きな変更を避ける
   - レビューしやすいサイズに分割

2. **テンプレートは必ず埋める**

   - 空欄を残さない
   - 特にテスト手順は詳細に

3. **スクリーンショットの活用**
   - UI変更は必ず画像添付
   - Before/After を明確に

## 🚀 GitHub Projects との連携

### かんばんボード設定

```
1. GitHub → Projects → New project
2. テンプレート選択: "Basic kanban"
3. カラム設定:
   - 📋 Backlog（アイデア・未着手）
   - 🚀 Todo（次に実装）
   - 🔄 In Progress（作業中）
   - 👀 Review（レビュー中）
   - ✅ Done（完了）

4. 自動化ルール:
   - Issue作成 → Backlog
   - PR作成 → In Progress
   - PR承認 → Review
   - PRマージ → Done
```

### マイルストーン活用

```
1. Milestones → New milestone
2. 例: "v1.0.0 - MVP Release"
3. 期限設定: 2週間後
4. IssueとPRに紐付け
5. 進捗を可視化
```

## 💡 Tips & Tricks

### 1. テンプレートのカスタマイズ

```yaml
# .github/ISSUE_TEMPLATE/custom.yml
name: 🔧 技術的負債
description: リファクタリングや改善が必要な箇所
labels: ['technical-debt', 'refactoring']
```

### 2. 自動化の活用

```yaml
# .github/workflows/auto-assign.yml
name: Auto Assign
on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]

jobs:
  assign:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.addAssignees({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              assignees: [context.actor]
            })
```

### 3. Claude Codeとの効率的な連携

```bash
# セッション開始時
"以下のIssueを確認してください: #15, #20, #25"

# PR作成後
"PR #30 をレビューしてください。特にセキュリティとパフォーマンスの観点から"

# 実装前の相談
"Issue #35 の実装方針について相談です。どのアプローチが良いでしょうか？"
```

## 📊 効果測定

### メトリクス

- Issue解決時間の短縮
- PRレビュー時間の短縮
- バグ報告の品質向上
- 実装の手戻り削減

### 改善サイクル

1. 週次でIssue/PRを振り返り
2. テンプレートの改善点を特定
3. 必要に応じてテンプレート更新
4. Claude Codeのフィードバック反映
