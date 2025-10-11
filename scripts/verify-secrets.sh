#!/bin/bash
# -*- coding: utf-8 -*-

# GitHub Secrets 検証スクリプト
# Phase別段階的環境構築対応

set -euo pipefail

# 色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GitHub Secrets 検証ツール${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 現在のPhase（各Phase進行でdocs/更新）
CURRENT_PHASE=3  # 現在はPhase 3

echo -e "${BLUE}現在の環境: Phase ${CURRENT_PHASE}${NC}"
echo ""

# GitHub CLIインストール確認
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI (gh) がインストールされていません${NC}"
    echo "インストール方法: brew install gh"
    echo ""
    echo "GitHub CLIなしでも以下のURLから確認できます:"
    echo "https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/settings/secrets/actions"
    exit 1
fi

# GitHub CLI認証確認
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLIが認証されていません${NC}"
    echo "認証方法: gh auth login"
    exit 1
fi

echo -e "${GREEN}✅ GitHub CLI認証済み${NC}"
echo ""

# 現在のリポジトリ取得
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo -e "${BLUE}対象リポジトリ: ${REPO}${NC}"
echo ""

# Secrets 一覧取得
SECRETS=$(gh secret list --json name -q '.[].name')

# シークレット検証関数
check_secret() {
    local secret_name=$1
    local phase=$2
    local required=$3  # "required" or "optional"

    if echo "$SECRETS" | grep -q "^${secret_name}$"; then
        echo -e "${GREEN}✅ ${secret_name}${NC}: 設定済み"
        return 0
    else
        if [ "$required" = "required" ]; then
            echo -e "${RED}❌ ${secret_name}${NC}: 未設定（Phase ${phase}で必須）"
            return 1
        else
            echo -e "${YELLOW}⚠️  ${secret_name}${NC}: 未設定（Phase ${phase}で将来必須）"
            return 0
        fi
    fi
}

# Phase 3必須シークレット検証
echo -e "${BLUE}=== Phase 3必須シークレット（品質保証基盤） ===${NC}"
PHASE3_FAILED=0

if ! check_secret "SONAR_TOKEN" 3 "required"; then
    PHASE3_FAILED=1
    echo -e "  ${YELLOW}設定方法: docs/setup/GITHUB_SECRETS_SETUP.md 参照${NC}"
fi

echo ""

# Phase 4必須シークレット（現在は任意）
echo -e "${BLUE}=== Phase 4必須シークレット（データベース基盤；現在任意） ===${NC}"
check_secret "TURSO_AUTH_TOKEN" 4 "optional"
check_secret "TURSO_DATABASE_URL" 4 "optional"
check_secret "REDIS_PASSWORD" 4 "optional"
echo ""

# Phase 5必須シークレット（現在は任意）
echo -e "${BLUE}=== Phase 5必須シークレット（認証基盤；現在任意） ===${NC}"
check_secret "CLERK_SECRET_KEY" 5 "optional"
check_secret "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" 5 "optional"
echo ""

# 将来的に必要なシークレット
echo -e "${BLUE}=== 将来的に必要なシークレット（機能拡張時） ===${NC}"
check_secret "CLOUDFLARE_API_TOKEN" "2-6" "optional"
check_secret "LANGFUSE_SECRET_KEY" "6" "optional"
check_secret "OPENAI_API_KEY" "3-6" "optional"
check_secret "ANTHROPIC_API_KEY" "3-6" "optional"
echo ""

# 検証結果サマリー
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  検証結果サマリー${NC}"
echo -e "${BLUE}========================================${NC}"

if [ $PHASE3_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Phase 3必須シークレット: すべて設定済み${NC}"
    echo -e "${GREEN}✅ CI/CDパイプラインは正常に動作できます${NC}"
else
    echo -e "${RED}❌ Phase 3必須シークレット: 未設定あり${NC}"
    echo -e "${YELLOW}⚠️  CI/CDパイプラインが一部失敗する可能性があります${NC}"
    echo ""
    echo -e "${BLUE}対応手順:${NC}"
    echo "   docs/setup/GITHUB_SECRETS_SETUP.md を参照"
    echo "   または以下のコマンドで設定:"
    echo "   gh secret set SONAR_TOKEN"
    exit 1
fi

echo ""
echo -e "${BLUE}次のステップ:${NC}"
echo "1. Phase 3完了後、Phase 4へ進む際にデータベースシークレット設定"
echo "2. シークレットは90日毎にローテーション推奨"
echo "3. 監査ログで定期的にアクセス履歴を確認"
