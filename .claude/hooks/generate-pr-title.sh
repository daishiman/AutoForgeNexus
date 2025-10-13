#!/bin/bash
# AutoForgeNexus PR Title自動生成スクリプト
# Claude Codeフック用

set -e

# 現在のブランチ名取得
CURRENT_BRANCH=$(git branch --show-current)
BASE_BRANCH="${1:-develop}"

# ブランチ名からPRタイトルを生成
generate_pr_title() {
    local branch="$1"

    # feature/xxx → feat: xxx
    if [[ $branch =~ ^feature/(.+)$ ]]; then
        local feature_name="${BASH_REMATCH[1]}"
        # ハイフンをスペースに変換、先頭を大文字に
        local description=$(echo "$feature_name" | tr '-' ' ' | sed 's/\b\(.\)/\u\1/g')
        echo "feat: ${description}"
        return
    fi

    # bugfix/xxx → fix: xxx
    if [[ $branch =~ ^bugfix/(.+)$ ]]; then
        local bug_name="${BASH_REMATCH[1]}"
        local description=$(echo "$bug_name" | tr '-' ' ' | sed 's/\b\(.\)/\u\1/g')
        echo "fix: ${description}"
        return
    fi

    # hotfix/xxx → fix: xxx (緊急修正)
    if [[ $branch =~ ^hotfix/(.+)$ ]]; then
        local hotfix_name="${BASH_REMATCH[1]}"
        local description=$(echo "$hotfix_name" | tr '-' ' ' | sed 's/\b\(.\)/\u\1/g')
        echo "fix: ${description}"
        return
    fi

    # docs/xxx → docs: xxx
    if [[ $branch =~ ^docs/(.+)$ ]]; then
        local docs_name="${BASH_REMATCH[1]}"
        local description=$(echo "$docs_name" | tr '-' ' ' | sed 's/\b\(.\)/\u\1/g')
        echo "docs: ${description}"
        return
    fi

    # refactor/xxx → refactor: xxx
    if [[ $branch =~ ^refactor/(.+)$ ]]; then
        local refactor_name="${BASH_REMATCH[1]}"
        local description=$(echo "$refactor_name" | tr '-' ' ' | sed 's/\b\(.\)/\u\1/g')
        echo "refactor: ${description}"
        return
    fi

    # それ以外: コミット履歴から推測
    local commit_msg=$(git log --oneline -1 --format=%s)

    # 既にConventional Commits形式の場合はそのまま
    if [[ $commit_msg =~ ^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9-]+\))?: ]]; then
        echo "$commit_msg"
        return
    fi

    # デフォルト: chore
    echo "chore: ${branch}"
}

# 最近のコミットメッセージからスコープを推測
detect_scope() {
    local commits=$(git log --oneline "$BASE_BRANCH..$CURRENT_BRANCH" --format=%s | head -5)

    # コミットメッセージから頻出スコープを抽出
    if echo "$commits" | grep -q "(frontend)"; then
        echo "frontend"
    elif echo "$commits" | grep -q "(backend)"; then
        echo "backend"
    elif echo "$commits" | grep -q "(ci)"; then
        echo "ci"
    elif echo "$commits" | grep -q "(docs)"; then
        echo "docs"
    elif echo "$commits" | grep -q "(test)"; then
        echo "test"
    else
        echo ""
    fi
}

# PRタイトル生成
PR_TITLE=$(generate_pr_title "$CURRENT_BRANCH")
SCOPE=$(detect_scope)

# スコープがあれば追加
if [ -n "$SCOPE" ]; then
    # feat: xxx → feat(scope): xxx に変換
    PR_TITLE=$(echo "$PR_TITLE" | sed "s/^\([a-z]*\): /\1($SCOPE): /")
fi

# PRタイトルを出力（Claude Codeが読み取る）
echo "$PR_TITLE"

# デバッグ情報（stderr）
echo "Generated PR title: $PR_TITLE" >&2
echo "Branch: $CURRENT_BRANCH" >&2
echo "Base: $BASE_BRANCH" >&2
