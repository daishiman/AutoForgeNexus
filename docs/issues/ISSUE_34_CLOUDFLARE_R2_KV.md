# Issue #34: Phase 2: Cloudflare R2バケット・KVネームスペース作成

## 📋 概要
Phase 2インフラ構築において、Cloudflare R2バケットとKVネームスペースの実際の作成が未完了です。設定ファイルは完備しているため、Cloudflare上でのリソース作成のみが必要です。

## 🚨 優先度
- **Medium**（アプリケーション動作には必須だが、開発環境では代替可能）

## 📊 現状評価
- **影響範囲**: ファイルストレージとキャッシュ機能
- **リスクレベル**: 低（設定は完了済み）
- **ブロッカー**: なし（Cloudflareアカウントがあれば即座に実行可能）

## ✅ 対応項目
- [ ] Cloudflare R2バケット作成（`autoforge-nexus-storage`）
- [ ] Cloudflare R2バケット作成（`autoforge-nexus-storage-staging`）
- [ ] KVネームスペース作成（production用 CACHE）
- [ ] KVネームスペース作成（staging用 CACHE）
- [ ] wrangler.tomlにKV/R2のIDを反映

## 🎯 成功基準
- R2バケットが作成され、wrangler.tomlに正しいIDが設定されている
- KVネームスペースが作成され、wrangler.tomlに正しいIDが設定されている
- デプロイ時にR2/KVへのアクセスが正常に動作する
- ステージング環境と本番環境で適切に分離されている

## 📅 推定工数
30分

## 🔧 実行コマンド

### 1. Cloudflare認証
```bash
# Cloudflare CLIログイン
wrangler login
```

### 2. KVネームスペース作成
```bash
# Production環境用
wrangler kv:namespace create "CACHE" --env production

# Staging環境用
wrangler kv:namespace create "CACHE" --env staging

# 作成されたIDをメモしておく
```

### 3. R2バケット作成
```bash
# Production用バケット
wrangler r2 bucket create autoforge-nexus-storage

# Staging用バケット
wrangler r2 bucket create autoforge-nexus-storage-staging

# バケット一覧確認
wrangler r2 bucket list
```

### 4. wrangler.toml更新
```toml
# infrastructure/cloudflare/workers/wrangler.toml を更新

[[env.production.kv_namespaces]]
binding = "CACHE"
id = "ここに取得したproduction用KV IDを設定"

[[env.staging.kv_namespaces]]
binding = "CACHE"
id = "ここに取得したstaging用KV IDを設定"
```

### 5. 動作確認
```bash
# KVの動作テスト
wrangler kv:key put --binding=CACHE "test-key" "test-value" --env production
wrangler kv:key get --binding=CACHE "test-key" --env production

# R2の動作テスト
echo "test" > test.txt
wrangler r2 object put autoforge-nexus-storage/test.txt --file test.txt
wrangler r2 object get autoforge-nexus-storage/test.txt
```

## 📝 備考
- Cloudflareアカウントが必要（無料プランで利用可能）
- wrangler loginでの認証が前提条件
- KVは最初の100,000読み取り/日が無料
- R2は10GB/月のストレージが無料
- 環境変数の設定も同時に確認すること

## 🔗 関連ドキュメント
- [Cloudflare KV Documentation](https://developers.cloudflare.com/kv/)
- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)
- [wrangler.toml設定](/infrastructure/cloudflare/workers/wrangler.toml)

## 📌 ラベル
- Phase 2
- Infrastructure
- Cloudflare
- Medium Priority