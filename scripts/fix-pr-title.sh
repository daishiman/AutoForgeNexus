#!/bin/bash

# PRタイトル修正スクリプト
# 先頭・末尾の空白を削除し、Conventional Commits形式を検証

set -euo pipefail

# 色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  PRタイトル修正ツール${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# GitHub CLIが利用可能か確認
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) がインストールされていません${NC}"
    echo "インストール方法: brew install gh"
    exit 1
fi

# 現在のブランチ名を取得
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}📍 現在のブランチ: ${CURRENT_BRANCH}${NC}"

# 現在のブランチに関連するPRを検索
PR_NUMBER=$(gh pr list --head "$CURRENT_BRANCH" --json number -q '.[0].number' 2>/dev/null || echo "")

if [ -z "$PR_NUMBER" ]; then
    echo -e "${YELLOW}⚠️  現在のブランチに関連するPRが見つかりません${NC}"
    echo ""
    echo "以下のいずれかを実行してください:"
    echo "1. PR番号を指定: $0 <PR番号>"
    echo "2. PR作成: gh pr create"
    exit 1
fi

echo -e "${GREEN}✅ PR #${PR_NUMBER} を発見${NC}"
echo ""

# 現在のPRタイトルを取得
CURRENT_TITLE=$(gh pr view "$PR_NUMBER" --json title -q '.title')
echo -e "${BLUE}📝 現在のタイトル:${NC}"
echo "   '$CURRENT_TITLE'"
echo ""

# タイトルから先頭・末尾の空白を削除
SANITIZED_TITLE=$(echo "$CURRENT_TITLE" | xargs)

# 変更があるかチェック
if [ "$CURRENT_TITLE" = "$SANITIZED_TITLE" ]; then
    echo -e "${GREEN}✅ タイトルに修正は不要です${NC}"
    echo ""

    # Conventional Commits形式を検証
    if echo "$SANITIZED_TITLE" | grep -qE '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?:.+'; then
        echo -e "${GREEN}✅ Conventional Commits形式に準拠しています${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  Conventional Commits形式ではありません${NC}"
        echo ""
        echo "推奨形式:"
        echo "  feat: 新機能追加"
        echo "  fix: バグ修正"
        echo "  docs: ドキュメント更新"
        echo "  style: コードフォーマット"
        echo "  refactor: リファクタリング"
        echo "  perf: パフォーマンス改善"
        echo "  test: テスト追加・修正"
        echo "  build: ビルドシステム変更"
        echo "  ci: CI/CD設定変更"
        echo "  chore: その他の変更"
        echo ""
        read -p "タイトルを修正しますか？ (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi
fi

# タイトル修正
echo -e "${YELLOW}🔧 タイトルを修正します...${NC}"
echo -e "${BLUE}新しいタイトル:${NC}"
echo "   '$SANITIZED_TITLE'"
echo ""

# 確認
read -p "この変更を適用しますか？ (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  キャンセルしました${NC}"
    exit 0
fi

# PRタイトルを更新
gh pr edit "$PR_NUMBER" --title "$SANITIZED_TITLE"

echo -e "${GREEN}✅ PRタイトルを更新しました${NC}"
echo ""

# Conventional Commits形式を検証
if echo "$SANITIZED_TITLE" | grep -qE '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?:.+'; then
    echo -e "${GREEN}✅ Conventional Commits形式に準拠しています${NC}"
    echo ""
    echo -e "${BLUE}📝 次のステップ:${NC}"
    echo "1. GitHub Actions → PR Check ワークフローを再実行"
    echo "2. すべてのチェックが成功することを確認"
else
    echo -e "${YELLOW}⚠️  Conventional Commits形式ではありません${NC}"
    echo ""
    echo "タイトルを以下の形式に変更してください:"
    echo "  <type>: <description>"
    echo ""
    echo "利用可能なtype:"
    echo "  feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert"
    echo ""
    echo "例:"
    echo "  feat: ユーザー認証機能追加"
    echo "  fix: ログイン時のバリデーションエラー修正"
fi
