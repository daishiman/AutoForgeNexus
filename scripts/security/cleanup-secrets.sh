#!/bin/bash
set -euo pipefail

# ========================================
# 秘密情報クリーンアップスクリプト
# ========================================
# 目的: TruffleHog検出後の環境ファイル整理
# 作成: 2025-10-08
# 責任者: version-control-specialist Agent
# ========================================

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ロギング関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# エラーハンドリング
trap 'log_error "スクリプト実行中にエラーが発生しました（Line: $LINENO）"; exit 1' ERR

# ========================================
# Phase 0: 事前確認
# ========================================
log_info "Phase 0: 事前確認開始"

# プロジェクトルート確認
if [[ ! -f "CLAUDE.md" ]] || [[ ! -d ".git" ]]; then
    log_error "プロジェクトルートディレクトリで実行してください"
    exit 1
fi

# バックアップディレクトリ作成
BACKUP_DIR="backup-secrets-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
log_success "バックアップディレクトリ作成: $BACKUP_DIR"

# ========================================
# Phase 1: バックアップ
# ========================================
log_info "Phase 1: 環境ファイルのバックアップ"

ENV_FILES=(
    ".env"
    "backend/.env"
    "backend/.env.local"
    "backend/.env.production"
    "backend/.env.staging"
    "backend/.env.test"
    "frontend/.env.local"
    "frontend/.env.production"
    "frontend/.env.staging"
)

for file in "${ENV_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        cp "$file" "$BACKUP_DIR/"
        log_success "バックアップ完了: $file"
    else
        log_warning "ファイルが存在しません: $file"
    fi
done

# ========================================
# Phase 2: 秘密情報の分析
# ========================================
log_info "Phase 2: 秘密情報の分析"

log_info "Discord Webhook URL検出箇所:"
grep -l "discord.com/api/webhooks" "${ENV_FILES[@]}" 2>/dev/null || log_warning "Discord Webhook未検出"

log_info "Cloudflare API Token検出箇所:"
grep -l "CLOUDFLARE_API_TOKEN" "${ENV_FILES[@]}" 2>/dev/null || log_warning "Cloudflare Token未検出"

# ========================================
# Phase 3: .envファイル削除確認
# ========================================
log_warning "Phase 3: .envファイル削除確認"
echo ""
echo "以下のファイルを削除します:"
for file in "${ENV_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  - $file"
    fi
done
echo ""
echo "バックアップは $BACKUP_DIR に保存されています"
echo ""

read -p "削除を実行しますか？ (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    log_warning "削除をキャンセルしました"
    exit 0
fi

# ========================================
# Phase 4: .envファイル削除
# ========================================
log_info "Phase 4: .envファイル削除実行"

for file in "${ENV_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        rm "$file"
        log_success "削除完了: $file"
    fi
done

# ========================================
# Phase 5: .env.exampleの最新化
# ========================================
log_info "Phase 5: .env.exampleファイルの検証"

EXAMPLE_FILES=(
    "backend/.env.example"
    "backend/.env.production.example"
    "frontend/.env.example"
    ".claude/.env.example"
    "infrastructure/cloudflare/workers/.env.example"
)

for file in "${EXAMPLE_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        log_success "存在確認OK: $file"

        # 秘密情報が含まれていないか確認
        if grep -qE "(discord\.com/api/webhooks|[A-Za-z0-9_-]{32,})" "$file" 2>/dev/null; then
            log_error "⚠️  警告: $file に秘密情報らしき文字列が含まれています"
        fi
    else
        log_warning "ファイルが存在しません: $file"
    fi
done

# ========================================
# Phase 6: .gitignore検証
# ========================================
log_info "Phase 6: .gitignore検証"

GITIGNORE_PATTERNS=(
    ".env"
    ".env.*"
    ".env.local"
    ".env.production.local"
    "secrets/"
    "*.key"
)

for pattern in "${GITIGNORE_PATTERNS[@]}"; do
    if grep -q "^$pattern$" .gitignore; then
        log_success ".gitignoreに含まれています: $pattern"
    else
        log_warning ".gitignoreに含まれていません: $pattern"
    fi
done

# ========================================
# Phase 7: Git状態確認
# ========================================
log_info "Phase 7: Git状態確認"

# ステージングエリア確認
if git diff --cached --name-only | grep -qE "\.env"; then
    log_error "⚠️  .envファイルがステージングされています"
    git diff --cached --name-only | grep "\.env"
else
    log_success "ステージングエリアに.envファイルなし"
fi

# 追跡ファイル確認
if git ls-files | grep -qE "\.env$"; then
    log_error "⚠️  .envファイルがGit追跡されています"
    git ls-files | grep "\.env"
else
    log_success "Git追跡対象に.envファイルなし"
fi

# ========================================
# Phase 8: 最終検証
# ========================================
log_info "Phase 8: TruffleHogで最終検証"

if command -v docker &> /dev/null; then
    log_info "TruffleHogスキャン開始..."

    if docker run --rm -v "$(pwd):/tmp" trufflesecurity/trufflehog:latest \
        git file:///tmp/ --only-verified --fail 2>&1 | tee "$BACKUP_DIR/trufflehog-final-scan.log"; then
        log_success "✅ TruffleHogスキャン: 検出なし"
    else
        log_warning "⚠️  TruffleHogが秘密情報を検出しました"
        log_info "詳細: $BACKUP_DIR/trufflehog-final-scan.log"
    fi
else
    log_warning "Dockerが利用できないため、TruffleHogスキャンをスキップ"
fi

# ========================================
# Phase 9: 次のステップ案内
# ========================================
log_success "=========================================="
log_success "🎉 秘密情報クリーンアップ完了"
log_success "=========================================="
echo ""
log_info "📋 次のステップ:"
echo ""
echo "1. Discord Webhookの再発行"
echo "   → https://discord.com/developers/applications"
echo ""
echo "2. Cloudflare API Tokenの再発行"
echo "   → https://dash.cloudflare.com/profile/api-tokens"
echo ""
echo "3. GitHub Secretsに新しいトークンを登録"
echo "   gh secret set DISCORD_WEBHOOK_URL"
echo "   gh secret set CLOUDFLARE_API_TOKEN"
echo ""
echo "4. .env.exampleから開発用.envを作成"
echo "   cp backend/.env.example backend/.env"
echo "   cp frontend/.env.example frontend/.env"
echo ""
echo "5. バックアップの確認"
echo "   ls -la $BACKUP_DIR"
echo ""

log_info "📝 詳細なドキュメント:"
echo "   docs/security/SECRET_REMEDIATION_PLAN.md"
echo ""

log_success "スクリプト実行完了"
