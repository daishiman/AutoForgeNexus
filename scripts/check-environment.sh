#!/bin/bash
# 環境確認スクリプト
set -e

echo "=== AutoForgeNexus Phase1 環境確認 ==="

# 必須ツール確認
check_tool() {
    local tool=$1
    local version_cmd=$2
    local required=$3

    if command -v $(echo $version_cmd | cut -d' ' -f1) >/dev/null 2>&1; then
        echo "✅ $tool: $($version_cmd 2>/dev/null || echo 'バージョン取得失敗')"
    else
        echo "❌ $tool: 未インストール (必須: $required)"
        echo "   インストール方法:"
        case "$(uname -s)" in
            Darwin*) echo "   brew install $(echo $tool | tr '[:upper:]' '[:lower:]')" ;;
            Linux*)  echo "   apt-get install $(echo $tool | tr '[:upper:]' '[:lower:]') または yum install $(echo $tool | tr '[:upper:]' '[:lower:]')" ;;
        esac
    fi
}

check_tool "Git" "git --version" "2.40+"
check_tool "Node.js" "node --version" "20.0+"
check_tool "pnpm" "pnpm --version" "8.0+"
check_tool "Docker" "docker --version" "24.0+"
check_tool "GitHub CLI" "gh --version" "最新版"

# GitHub認証確認
if gh auth status >/dev/null 2>&1; then
    echo "✅ GitHub認証: 済み"
else
    echo "⚠️ GitHub認証: 未設定"
    echo "   設定方法: gh auth login"
fi

echo "=== 環境確認完了 ==="