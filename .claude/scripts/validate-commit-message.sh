#!/bin/bash
# AutoForgeNexus Commit Message検証スクリプト
# Claude Codeフック用

set -e

# 最後のコミットメッセージ取得
COMMIT_MSG=$(git log -1 --pretty=%B)

# Conventional Commits形式の検証
CONVENTIONAL_REGEX="^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9-]+\))?: .+"

if ! echo "$COMMIT_MSG" | grep -qE "$CONVENTIONAL_REGEX"; then
    echo "⚠️ Warning: Commit message does not follow Conventional Commits format" >&2
    echo "Current message: $COMMIT_MSG" >&2
    echo "" >&2
    echo "Expected format: <type>[(scope)]: <description>" >&2
    echo "Example: feat(auth): Add login functionality" >&2
    exit 0  # 警告のみ、失敗させない
fi

echo "✅ Commit message is valid" >&2
