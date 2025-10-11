# AutoForgeNexus 環境構築トラブルシューティングガイド

このドキュメントは、環境構築中に発生する可能性のある問題とその解決方法を提供します。

## 🚨 緊急時AI コマンド

```bash
# 緊急時の包括的診断
/ai security-engineer --validate --safe-mode "全フェーズの環境構築状態を診断し、問題を特定して解決策を提供してください"
```

## Phase 1: Git・基盤環境構築のトラブルシューティング

### 1.1 Git設定エラー

**症状**: git commit時の認証エラー

```bash
fatal: unable to access 'https://github.com/user/repo.git/': The requested URL returned error: 403
```

**AI解決コマンド**:

```bash
/ai devops-coordinator --git-auth "GitHubの認証設定を修正し、SSH鍵またはPersonal Access Tokenを正しく設定してください。現在のgit設定を診断し、最適な認証方法を実装してください"
```

**手動解決**:

```bash
# SSH鍵の生成と設定
ssh-keygen -t ed25519 -C "your_email@example.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
# 公開鍵をGitHubに追加
cat ~/.ssh/id_ed25519.pub
```

### 1.2 Python 3.13インストールエラー

**症状**: Python 3.13が見つからない、または古いバージョンがデフォルト

```bash
python3 --version
Python 3.9.7  # 古いバージョン
```

**AI解決コマンド**:

```bash
/ai backend-developer --python-setup "Python 3.13の完全インストールと環境設定を行ってください。pyenvまたはシステムパッケージマネージャーを使用し、仮想環境も設定してください"
```

### 1.3 Docker権限エラー

**症状**: Docker操作時の権限エラー

```bash
Got permission denied while trying to connect to the Docker daemon socket
```

**AI解決コマンド**:

```bash
/ai devops-coordinator --docker-permissions "Docker権限エラーを解決し、現在のユーザーでDockerを使用できるように設定してください。セキュリティベストプラクティスに従ってください"
```

## Phase 2: インフラ・DevOps環境構築のトラブルシューティング

### 2.1 Cloudflare Workers Python実行エラー

**症状**: Workers Pythonランタイムエラー

```bash
Error: Could not resolve "python3.11" from "package.json"
```

**AI解決コマンド**:

```bash
/ai edge-computing-specialist --workers-python "Cloudflare Workers Pythonの実行環境を修正し、正しいランタイム設定とwrangler.tomlの設定を行ってください"
```

### 2.2 GitHub Actions権限エラー

**症状**: CI/CDパイプラインでの権限エラー

```bash
Error: Resource not accessible by integration
```

**AI解決コマンド**:

```bash
/ai devops-coordinator --github-actions "GitHub Actionsの権限設定を修正し、必要なシークレットとパーミッションを正しく設定してください。セキュリティベストプラクティスに従ってください"
```

## Phase 3: バックエンド環境構築のトラブルシューティング

### 3.1 FastAPI起動エラー

**症状**: FastAPIサーバーが起動しない

```bash
ModuleNotFoundError: No module named 'fastapi'
```

**AI解決コマンド**:

```bash
/ai backend-developer --fastapi-setup "FastAPI環境の問題を診断し、依存関係の問題を解決してください。requirements.txtの確認、仮想環境の設定、Pythonパス問題を修正してください"
```

### 3.2 SQLAlchemy接続エラー

**症状**: データベース接続エラー

```bash
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

**AI解決コマンド**:

```bash
/ai backend-architect --database-connection "SQLAlchemyデータベース接続エラーを解決し、Turso接続設定を修正してください。認証トークンと接続文字列を確認してください"
```

### 3.3 pydantic ValidationError

**症状**: Pydanticスキーマ検証エラー

```bash
pydantic.error_wrappers.ValidationError: 1 validation error for UserCreate
```

**AI解決コマンド**:

```bash
/ai backend-developer --pydantic-validation "Pydantic検証エラーを解決し、スキーマ定義とデータ型を修正してください。API リクエスト/レスポンスモデルの整合性を確保してください"
```

## Phase 4: データベース・ベクトル環境構築のトラブルシューティング

### 4.1 Turso認証エラー

**症状**: Tursoデータベースへの接続が失敗

```bash
Error: Authentication failed: invalid token
```

**AI解決コマンド**:

```bash
/ai edge-database-administrator --turso-auth "Turso認証問題を解決し、データベーストークンと接続設定を修正してください。リージョン設定も確認してください"
```

### 4.2 libSQL Vector検索エラー

**症状**: ベクトル検索が動作しない

```bash
Error: no such function: vector_distance
```

**AI解決コマンド**:

```bash
/ai vector-database-specialist --libsql-vector "libSQL Vectorエクステンションの問題を解決し、ベクトル検索機能を正しく設定してください。1536次元の埋め込み対応を確認してください"
```

### 4.3 Redis接続エラー

**症状**: Redisへの接続が失敗

```bash
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379
```

**AI解決コマンド**:

```bash
/ai backend-architect --redis-connection "Redis接続エラーを解決し、キャッシュ設定を修正してください。Docker環境でのRedis設定も確認してください"
```

## Phase 5: フロントエンド環境構築のトラブルシューティング

### 5.1 Next.js 15.5ビルドエラー

**症状**: Next.jsビルドが失敗

```bash
Error: Module not found: Can't resolve 'react' in '/app/components'
```

**AI解決コマンド**:

```bash
/ai frontend-architect --nextjs-build "Next.js 15.5ビルドエラーを解決し、依存関係とReact 19の互換性問題を修正してください。pnpmロックファイルも確認してください"
```

### 5.2 TypeScript型エラー

**症状**: TypeScript型チェックエラー

```bash
Type 'string' is not assignable to type 'CollaborationEvent'
```

**AI解決コマンド**:

```bash
/ai frontend-architect --typescript-types "TypeScript型エラーを解決し、CRDT関連の型定義を修正してください。WebSocket通信の型安全性も確保してください"
```

### 5.3 Tailwind CSS 4.0設定エラー

**症状**: Tailwind CSSが適用されない

```bash
Error: Cannot find module '@tailwindcss/typography'
```

**AI解決コマンド**:

```bash
/ai ui-ux-designer --tailwind-setup "Tailwind CSS 4.0の設定エラーを解決し、必要なプラグインとconfiguration設定を修正してください"
```

### 5.4 WebSocket接続エラー

**症状**: リアルタイム協調機能が動作しない

```bash
WebSocket connection failed: Error during WebSocket handshake
```

**AI解決コマンド**:

```bash
/ai real-time-features-specialist --websocket-debug "WebSocket接続エラーを解決し、リアルタイム協調編集機能を修復してください。CRDT同期も確認してください"
```

## Phase 6: 統合・品質保証のトラブルシューティング

### 6.1 E2Eテスト失敗

**症状**: Playwrightテストが失敗

```bash
TimeoutError: Waiting for selector ".prompt-editor" failed: timeout 30000ms exceeded
```

**AI解決コマンド**:

```bash
/ai test-automation-engineer --e2e-debug "E2Eテスト失敗を解決し、セレクター問題とタイミング問題を修正してください。テスト安定性を向上させてください"
```

### 6.2 セキュリティ監査エラー

**症状**: セキュリティスキャンでの問題

```bash
High severity vulnerability found in dependency: jsonwebtoken@8.5.1
```

**AI解決コマンド**:

```bash
/ai security-engineer --vulnerability-fix "セキュリティ脆弱性を解決し、依存関係を安全なバージョンに更新してください。JWT実装のセキュリティも強化してください"
```

### 6.3 パフォーマンステスト失敗

**症状**: Lighthouseスコアが基準を下回る

```bash
Performance score: 65/100 (Target: 90+)
```

**AI解決コマンド**:

```bash
/ai performance-engineer --optimize-metrics "パフォーマンス問題を解決し、Core Web Vitalsを改善してください。Next.js 15.5の最適化機能を活用してください"
```

## 一般的なトラブルシューティング

### 環境変数エラー

**症状**: 環境変数が読み込まれない

```bash
Error: Required environment variable TURSO_AUTH_TOKEN is not set
```

**解決手順**:

1. `.env.local`ファイルの存在確認
2. 変数名のスペルチェック
3. `next.config.js`の環境変数設定確認

**AI解決コマンド**:

```bash
/ai devops-coordinator --env-variables "環境変数の設定問題を解決し、開発環境と本番環境の変数管理を最適化してください"
```

### ポート競合エラー

**症状**: ポートがすでに使用されている

```bash
Error: listen EADDRINUSE: address already in use :::3000
```

**AI解決コマンド**:

```bash
/ai devops-coordinator --port-management "ポート競合を解決し、開発環境のポート管理を最適化してください。Docker環境との競合も確認してください"
```

### メモリ不足エラー

**症状**: Node.jsメモリ不足

```bash
FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed
```

**AI解決コマンド**:

```bash
/ai performance-engineer --memory-optimization "メモリ使用量を最適化し、Node.jsヒープサイズ設定を調整してください。メモリリークも確認してください"
```

## ログ分析のためのAIコマンド

### 包括的ログ分析

```bash
/ai root-cause-analyst --log-analysis "すべてのログファイルを分析し、エラーパターンと根本原因を特定してください。優先順位付きの解決策を提供してください"
```

### パフォーマンス問題診断

```bash
/ai performance-engineer --comprehensive-audit "システム全体のパフォーマンスボトルネックを特定し、最適化計画を策定してください"
```

### セキュリティ問題診断

```bash
/ai security-engineer --security-audit "包括的なセキュリティ監査を実行し、脆弱性と改善策を報告してください"
```

## 予防的メンテナンス

### 定期的な環境健全性チェック

```bash
/ai sre-agent-agent --health-check "全システムの健全性チェックを実行し、潜在的な問題を予防的に特定してください"
```

### 依存関係の更新

```bash
/ai devops-coordinator --dependency-update "すべての依存関係を安全に更新し、互換性問題を事前にチェックしてください"
```

### 設定ドリフトの検出

```bash
/ai devops-coordinator --config-drift "設定ドリフトを検出し、標準設定からの逸脱を修正してください"
```

## サポート連絡先

### 技術サポート

- **緊急時**: `emergency-support@autoforgenexus.com`
- **一般サポート**: `support@autoforgenexus.com`
- **開発者サポート**: `dev-support@autoforgenexus.com`

### コミュニティリソース

- **GitHub Issues**: `https://github.com/autoforgenexus/autoforgenexus/issues`
- **Discord サーバー**: `https://discord.gg/autoforgenexus`
- **ドキュメンテーション**: `https://docs.autoforgenexus.com`

## 診断データ収集

### システム情報収集スクリプト

```bash
#!/bin/bash
# diagnostic_info.sh - 診断情報を収集

echo "=== AutoForgeNexus 診断情報 ===" > diagnostic_report.txt
echo "Date: $(date)" >> diagnostic_report.txt
echo "System: $(uname -a)" >> diagnostic_report.txt
echo "Python: $(python3 --version)" >> diagnostic_report.txt
echo "Node: $(node --version)" >> diagnostic_report.txt
echo "Docker: $(docker --version)" >> diagnostic_report.txt
echo "Git: $(git --version)" >> diagnostic_report.txt

# 環境変数チェック
echo -e "\n=== 環境変数 ===" >> diagnostic_report.txt
env | grep -E "(TURSO|CLERK|NEXT)" >> diagnostic_report.txt

# ポート使用状況
echo -e "\n=== ポート使用状況 ===" >> diagnostic_report.txt
lsof -i :3000,8000,5432,6379 >> diagnostic_report.txt

# ディスク使用量
echo -e "\n=== ディスク使用量 ===" >> diagnostic_report.txt
df -h >> diagnostic_report.txt

echo "診断レポートが diagnostic_report.txt に保存されました"
```

### AIを使用した自動診断

```bash
/ai root-cause-analyst --auto-diagnosis "システム全体の自動診断を実行し、問題の優先順位付きリストと解決手順を提供してください"
```

---

**注意**: このトラブルシューティングガイドは定期的に更新されます。最新バージョンは常にドキュメンテーションサイトで確認してください。
