#!/usr/bin/env bash
# ==========================================
# Pre-commit Hooks セットアップスクリプト
# ==========================================
# AutoForgeNexus - AI Prompt Optimization System
# セキュリティファーストな開発環境構築
# ==========================================

set -euo pipefail

# 色定義
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# エラーハンドリング
error_exit() {
    log_error "$1"
    exit "${2:-1}"
}

# ==========================================
# 前提条件チェック
# ==========================================
check_prerequisites() {
    log_info "前提条件をチェック中..."

    # Git確認
    if ! command -v git &> /dev/null; then
        error_exit "Git がインストールされていません。" 1
    fi
    log_success "✓ Git: $(git --version)"

    # Python確認
    if ! command -v python3 &> /dev/null; then
        error_exit "Python 3 がインストールされていません。" 1
    fi
    log_success "✓ Python: $(python3 --version)"

    # pip確認
    if ! command -v pip3 &> /dev/null; then
        error_exit "pip3 がインストールされていません。" 1
    fi
    log_success "✓ pip: $(pip3 --version)"

    # Gitリポジトリ確認
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error_exit "このディレクトリはGitリポジトリではありません。" 1
    fi
    log_success "✓ Gitリポジトリ確認完了"
}

# ==========================================
# pre-commit インストール
# ==========================================
install_pre_commit() {
    log_info "pre-commit をインストール中..."

    if command -v pre-commit &> /dev/null; then
        log_warning "pre-commit は既にインストールされています: $(pre-commit --version)"
        return 0
    fi

    pip3 install --user pre-commit || error_exit "pre-commit のインストールに失敗しました。" 1
    log_success "✓ pre-commit インストール完了"
}

# ==========================================
# TruffleHog インストール
# ==========================================
install_trufflehog() {
    log_info "TruffleHog をインストール中..."

    if command -v trufflehog &> /dev/null; then
        log_warning "TruffleHog は既にインストールされています: $(trufflehog --version)"
        return 0
    fi

    # macOS (Homebrew)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install trufflehog || log_warning "Homebrew経由のインストールに失敗しました。"
        else
            log_warning "Homebrew がインストールされていません。手動でTruffleHogをインストールしてください。"
        fi
    # Linux
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "TruffleHogをバイナリからインストール中..."
        curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin
    else
        log_warning "このOSでは自動インストールがサポートされていません。手動でインストールしてください。"
    fi

    if command -v trufflehog &> /dev/null; then
        log_success "✓ TruffleHog インストール完了: $(trufflehog --version)"
    else
        log_warning "TruffleHogのインストールを確認できませんでした。"
    fi
}

# ==========================================
# Gitleaks インストール
# ==========================================
install_gitleaks() {
    log_info "Gitleaks をインストール中..."

    if command -v gitleaks &> /dev/null; then
        log_warning "Gitleaks は既にインストールされています: $(gitleaks version)"
        return 0
    fi

    # macOS (Homebrew)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install gitleaks || log_warning "Homebrew経由のインストールに失敗しました。"
        fi
    # Linux
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "Gitleaksをバイナリからインストール中..."
        curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.21.2/gitleaks_8.21.2_linux_x64.tar.gz | tar -xz -C /usr/local/bin gitleaks
    fi

    if command -v gitleaks &> /dev/null; then
        log_success "✓ Gitleaks インストール完了: $(gitleaks version)"
    else
        log_warning "Gitleaksのインストールを確認できませんでした。"
    fi
}

# ==========================================
# pre-commit フックインストール
# ==========================================
install_hooks() {
    log_info "pre-commit フックをインストール中..."

    # .pre-commit-config.yamlの存在確認
    if [[ ! -f ".pre-commit-config.yaml" ]]; then
        error_exit ".pre-commit-config.yaml が見つかりません。" 1
    fi

    # フックインストール
    pre-commit install --hook-type pre-commit --hook-type commit-msg || error_exit "フックのインストールに失敗しました。" 1
    log_success "✓ pre-commit フックインストール完了"

    # 依存関係インストール
    log_info "pre-commit 依存関係をインストール中..."
    pre-commit install-hooks || error_exit "依存関係のインストールに失敗しました。" 1
    log_success "✓ 依存関係インストール完了"
}

# ==========================================
# 初回スキャン実行
# ==========================================
run_initial_scan() {
    log_info "初回スキャンを実行中..."

    log_warning "既存のすべてのファイルに対してpre-commitを実行します。"
    log_warning "これには数分かかる場合があります。"

    if pre-commit run --all-files; then
        log_success "✓ 初回スキャン完了: 問題は検出されませんでした"
    else
        log_warning "⚠ 初回スキャンで問題が検出されました。"
        log_warning "修正可能な問題は自動修正されました。"
        log_warning "手動修正が必要な問題がある場合は、上記のログを確認してください。"
    fi
}

# ==========================================
# 設定ファイルバックアップ
# ==========================================
backup_config() {
    local config_file=".pre-commit-config.yaml"
    local backup_file=".pre-commit-config.yaml.backup"

    if [[ -f "$backup_file" ]]; then
        log_info "既存のバックアップファイルを削除中..."
        rm -f "$backup_file"
    fi

    cp "$config_file" "$backup_file"
    log_success "✓ 設定ファイルをバックアップしました: $backup_file"
}

# ==========================================
# 使用方法表示
# ==========================================
show_usage() {
    cat <<EOF

${GREEN}✅ セットアップが完了しました！${NC}

${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
${YELLOW}📝 使用方法${NC}
${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${GREEN}1. 自動実行（推奨）${NC}
   git commit 時に自動でスキャンが実行されます。

${GREEN}2. 手動実行${NC}
   pre-commit run --all-files

${GREEN}3. 特定のファイルのみスキャン${NC}
   pre-commit run --files backend/src/main.py

${GREEN}4. 特定のフックのみ実行${NC}
   pre-commit run trufflehog-git --all-files

${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
${YELLOW}🔧 主要コマンド${NC}
${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

  pre-commit autoupdate      # フックを最新版に更新
  pre-commit clean           # キャッシュをクリア
  pre-commit uninstall       # フックをアンインストール

${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
${YELLOW}🛡️ セキュリティツール${NC}
${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

  TruffleHog  - 秘密情報検出（Git履歴+ファイルシステム）
  Gitleaks    - Git秘密情報検出
  Bandit      - Python セキュリティスキャナ
  Safety      - Python 依存関係脆弱性スキャン

${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${GREEN}🎯 次のステップ${NC}
  1. git commit でコミット時の自動スキャンを体験
  2. .env ファイルの秘密情報を GitHub Secrets に移行
  3. 定期的に pre-commit autoupdate でツールを最新化

${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

EOF
}

# ==========================================
# メイン処理
# ==========================================
main() {
    echo -e "${BLUE}"
    cat <<'EOF'
╔═══════════════════════════════════════════╗
║   🛡️  Pre-commit セキュリティ設定      ║
║   AutoForgeNexus - Security-First        ║
╚═══════════════════════════════════════════╝
EOF
    echo -e "${NC}"

    check_prerequisites
    echo ""

    backup_config
    echo ""

    install_pre_commit
    echo ""

    install_trufflehog
    echo ""

    install_gitleaks
    echo ""

    install_hooks
    echo ""

    # 初回スキャンをスキップする場合
    if [[ "${SKIP_INITIAL_SCAN:-false}" == "true" ]]; then
        log_warning "初回スキャンをスキップしました（SKIP_INITIAL_SCAN=true）"
    else
        run_initial_scan
    fi
    echo ""

    show_usage
}

# スクリプト実行
main "$@"
