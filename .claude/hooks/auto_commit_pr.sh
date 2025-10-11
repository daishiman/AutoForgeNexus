#!/bin/bash
# AutoForgeNexus 自動コミット・PR作成スクリプト
# Claude Code Stopイベントで実行

set -e

# 設定
COMMIT_PREFIX="[Claude Code]"
PR_LABEL="automated-pr,claude-code"
BASE_BRANCH="${1:-develop}"
COMMIT_TEMPLATE=".claude/templates/commit-template.txt"

# 環境変数チェック
if [ -z "$CLAUDE_PROJECT_DIR" ]; then
    CLAUDE_PROJECT_DIR=$(pwd)
fi

cd "$CLAUDE_PROJECT_DIR"

# Git状態確認
if ! git diff --quiet || ! git diff --staged --quiet; then
    echo "📝 変更を検出しました。自動コミット処理を開始します..."

    # 現在のブランチ取得
    CURRENT_BRANCH=$(git branch --show-current)

    # develop/mainブランチの場合は新規ブランチ作成
    if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "develop" ]; then
        BRANCH_NAME="claude-code/$(date +%Y%m%d-%H%M%S)"
        echo "🌿 新規ブランチ作成: $BRANCH_NAME"
        git checkout -b "$BRANCH_NAME" || exit 1
    else
        BRANCH_NAME="$CURRENT_BRANCH"
        echo "🌿 現在のブランチを使用: $BRANCH_NAME"
    fi

    # 全ての変更をステージング
    git add -A

    # コミットメッセージ生成
    if [ -f ".claude/hooks/generate_commit_message.py" ]; then
        python3 .claude/hooks/generate_commit_message.py > /tmp/commit_msg.txt
        COMMIT_MSG=$(cat /tmp/commit_msg.txt)
    else
        # フォールバック: シンプルなメッセージ
        COMMIT_MSG="$COMMIT_PREFIX Automated commit at $(date +%Y-%m-%d\ %H:%M:%S)"
    fi

    # コミット実行
    git commit -F /tmp/commit_msg.txt || git commit -m "$COMMIT_MSG"

    echo "✅ コミット完了: $COMMIT_MSG"

    # リモートにプッシュ（オプション）
    read -p "🚀 リモートにプッシュしますか? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin "$BRANCH_NAME" || git push -u origin "$BRANCH_NAME"

        # プルリクエスト作成（オプション）
        read -p "📬 プルリクエストを作成しますか? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [ -f ".claude/hooks/create_pull_request.py" ]; then
                python3 .claude/hooks/create_pull_request.py "$BRANCH_NAME" "$BASE_BRANCH"
            else
                echo "⚠️ create_pull_request.py が見つかりません"
            fi
        fi
    fi
else
    echo "ℹ️ 変更がないためスキップします"
fi
