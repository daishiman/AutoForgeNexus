---
name: git
description: '包括的なGit操作とバージョン管理戦略の統括'
category: development
complexity: medium
agents:
  [
    version-control-specialist,
    devops-coordinator,
    technical-documentation,
    test-automation-engineer,
    qa-coordinator,
    backend-developer,
  ]
---

# /ai:development:git - バージョン管理

## Triggers

- Git 操作の実行要求
- ブランチ管理とマージ戦略
- リリース準備とタグ付け
- コンフリクト解決支援
- コミット規約の強制
- バージョン戦略の実装

## Context Trigger Pattern

```
/ai:development:git [operation] [--strategy gitflow|github-flow|trunk-based] [--auto-merge] [--semantic-version] [--hooks]
```

## Behavioral Flow

1. **状態分析**: 現在のリポジトリ状態とブランチ構造の詳細分析
2. **戦略選択**: プロジェクトに適した Git 戦略の選定と適用
3. **前処理**: pre-commit フック、リンティング、フォーマット実行
4. **操作実行**: Git コマンドの安全な実行と自動化
5. **品質検証**: コミット品質、テスト結果、カバレッジ確認
6. **統合処理**: CI/CD トリガー、自動マージ条件評価
7. **文書同期**: ドキュメント更新と CHANGELOG 生成
8. **通知配信**: チーム全体への変更通知とレビュー要求

Key behaviors:

- Conventional Commits の厳格な適用
- ブランチ保護ルールの自動設定
- セマンティックバージョニングの一貫性
- コンフリクト予防と早期解決
- 自動化によるヒューマンエラー削減

## Agent Coordination

- **version-control-specialist** → Git 操作主導、ブランチ戦略設計
- **devops-coordinator** → CI/CD パイプライン統合、デプロイトリガー
- **technical-documentation** → ドキュメント同期、CHANGELOG 管理
- **test-automation-engineer** → マージ前テスト実行、品質ゲート
- **qa-coordinator** → レビュープロセス管理、マージ承認
- **backend-developer** → コード変更調整、コンフリクト解決

## Tool Coordination

- **bash_tool**: Git コマンド実行、フック管理
- **view**: リポジトリ状態確認、差分分析
- **str_replace**: コミットメッセージ修正、設定更新
- **create_file**: フック作成、テンプレート生成
- **web_search**: ベストプラクティス確認

## Key Patterns

- **ブランチ戦略**: Git Flow / GitHub Flow / Trunk-Based Development
- **マージ戦略**: Fast-forward / Squash / Rebase
- **バージョニング**: SemVer / CalVer / 独自規約
- **フック管理**: pre-commit / pre-push / commit-msg
- **自動化**: 自動マージ / 自動リリース / 自動タグ付け

## Examples

### ブランチ戦略実装

```
/ai:development:git init --strategy gitflow --hooks
# Git Flow戦略の完全セットアップ
# develop, release, hotfixブランチ作成
# 保護ルールとフックの自動設定
# CODEOWNERSファイル生成
```

### 自動マージと CI/CD 連携

```
/ai:development:git merge feature-branch --auto-merge --strategy github-flow
# テスト成功後の自動マージ
# コンフリクト自動解決試行
# CI/CDパイプライントリガー
# Slackへの完了通知
```

### セマンティックリリース

```
/ai:development:git release v1.2.0 --semantic-version --hooks
# バージョン番号の自動計算
# CHANGELOG自動生成（conventional-changelog）
# リリースノート作成
# タグ付けとGitHubリリース作成
# NPM/PyPI公開準備
```

### コンフリクト解決支援

```
/ai:development:git resolve-conflict feature-branch --strategy rebase
# インテリジェントコンフリクト分析
# 3-way マージ戦略適用
# テスト実行による検証
# コンフリクト解決レポート
```

### モノレポ管理

```
/ai:development:git monorepo --strategy trunk-based
# モノレポ用ブランチ戦略
# パッケージ別バージョニング
# 依存関係グラフ生成
# 選択的CI/CD実行
```

## Boundaries

**Will:**

- Git 操作の完全自動化とインテリジェント化
- ブランチ戦略の設計と一貫した適用
- 品質ゲートとマージ条件の厳格な管理
- CI/CD パイプラインとの深い統合
- チーム協調とコードレビューの効率化

**Will Not:**

- 破壊的な Git 操作の無断実行（force push 等）
- セキュリティポリシー違反のマージ
- テスト未実行でのマージ承認
- ドキュメント同期なしのリリース
- 承認なしの本番ブランチ変更

## CI/CD最適化との連携（2025年9月29日追加）

### GitHub Actions統合の効率化

**最適化成果:**

- **GitHub Actions使用量**: 52.3%削減達成
- **共有ワークフロー**: 3つの再利用可能ワークフローで重複削除
- **自動トリガー**: Git操作に連動した効率的なCI/CD実行

**このコマンドでのCI/CD活用:**

```bash
# PRマージ時の自動化
/ai:development:git merge --auto-merge
# → GitHub Actionsの品質チェック完了を待機
# → 共有ワークフローで効率的にテスト実行
# → 成功時のみマージ実行

# リリース時の自動化
/ai:development:git release --semantic-version
# → CHANGELOGとタグ生成
# → GitHub Actionsでのリリースビルド（最適化済み）
# → 無料枠内での効率的な処理
```

**コスト削減のポイント:**

- マトリクステストの最適化
- キャッシュ活用による実行時間短縮
- 不要なジョブのスキップ条件設定
