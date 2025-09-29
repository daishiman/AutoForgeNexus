# Claude Code 設定 - AutoForgeNexus

このディレクトリには、AutoForgeNexusプロジェクト専用のClaude Code設定が含まれています。

## 設定ファイル概要

### `.superclaude-metadata.json`
- **目的**: プロジェクト専用のSuperClaude Framework設定
- **内容**: 27の専門エージェント、コマンド、コア設定、MCPサーバー情報
- **技術スタック**: Python 3.13, FastAPI 0.116.1, Next.js 15.5, React 19, TypeScript 5.x

### `settings.local.json`
- **目的**: プロジェクト専用のMCPサーバー設定
- **設定サーバー**:
  - `context7`: ライブラリドキュメント検索とフレームワークパターンガイダンス
  - `sequential-thinking`: 複雑な分析と多段階推論エンジン
  - `playwright`: ブラウザ自動化とE2Eテスト
  - `serena`: プロジェクトメモリとセマンティックコード理解

## 重要なセキュリティ注意事項

⚠️ **このファイルはGitにコミットしないでください**: `settings.local.json`

このファイルには、将来的にAPIキーやトークンが含まれる可能性があります。
`.gitignore`に以下のパターンが追加されています：

```
.claude/settings.local.json
.claude/secrets/
.claude/*.key
.claude/api_keys.*
.claude/tokens.*
.claude/credentials.*
```

## 使用方法

### 1. Claude Code起動時の自動読み込み
このディレクトリの設定は、AutoForgeNexusプロジェクトでClaude Codeを使用する際に自動的に読み込まれます。

### 2. 推奨モデル
プロジェクト設定では`claude-3-5-sonnet-20241022`が推奨モデルとして設定されています。

### 3. パッケージマネージャー
プロジェクト全体でpnpm（PAPN）を使用することが設定されています。

## 開発ワークフロー

### MCPサーバーの活用
- **UI コンポーネント開発**: Context7でフレームワークパターンを検索
- **複雑な分析タスク**: Sequential-thinkingで体系的推論
- **ブラウザテスト**: Playwrightで自動化テスト実行
- **プロジェクト理解**: Serenaでセマンティックコード分析

### 専門エージェントの活用
SuperClaude Frameworkの27の専門エージェントが利用可能：
- `backend-developer`: FastAPIとPython 3.13専門
- `frontend-architect`: Next.js 15.5とReact 19専門
- `database-administrator`: PostgreSQL/Turso専門
- その他、セキュリティ、パフォーマンス、テスト等の専門エージェント

## トラブルシューティング

### MCPサーバー接続問題
もしMCPサーバーの接続に問題がある場合：

1. **Context7**: `claude mcp add context7`
2. **Sequential-thinking**: `claude mcp add sequential-thinking`
3. **Playwright**: `claude mcp add playwright`
4. **Serena**: `claude mcp add serena "uvx --from git+https://github.com/oraios/serena serena start-mcp-server"`

### 設定の確認
現在のClaude Code設定を確認：
```bash
claude config list
claude mcp list
```

## 関連ドキュメント

- `/CLAUDE.md`: プロジェクト全体のClaude Code ガイダンス
- `/package.json`: pnpm workspace設定
- `/pyproject.toml`: Python 3.13とツール設定
- `/tsconfig.json`: TypeScript 5.x設定

## CI/CD最適化の成果（2025年9月29日追加）

### GitHub Actions使用量削減
- **達成削減率**: 52.3%（3,200分/月 → 1,525分/月）
- **無料枠使用率**: 36.5%（730分/2,000分）
- **年間節約額**: $115.2

### 最適化実装内容
- 共有ワークフロー（Python/Node.js/ビルドキャッシュ）
- スケジュール頻度最適化（監視・セキュリティチェック）
- 並列実行による時間短縮（30分 → 15分）

### 今後の改善提案
Claude Codeエージェントによる継続的な最適化：
- `devops-coordinator`: CI/CDパイプラインのさらなる効率化
- `cost-optimization`: リソース使用量の継続的モニタリング
- `performance-optimizer`: ビルド時間のさらなる短縮