#!/usr/bin/env python3
"""
GitHub CLIを使用してConventional Commits準拠のプルリクエストを作成
"""

import subprocess
import sys
import json
import os
import re
from pathlib import Path
from datetime import datetime

def check_gh_cli() -> bool:
    """GitHub CLIがインストールされているか確認"""
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def generate_pr_title(branch_name: str, base_branch: str) -> str:
    """ブランチ名とコミット履歴からConventional Commits形式のPRタイトルを生成"""

    # コミット履歴から最新のコミットメッセージを取得
    result = subprocess.run(
        ['git', 'log', f'{base_branch}..{branch_name}', '--oneline', '-1'],
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        # コミットメッセージからタイトルを生成
        commit_msg = result.stdout.strip().split(' ', 1)[1] if ' ' in result.stdout.strip() else result.stdout.strip()

        # 既にConventional Commits形式の場合はそのまま
        if re.match(r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9-]+\))?: ', commit_msg):
            return commit_msg[:72]

        # そうでない場合はブランチ名から推測
        return generate_title_from_branch(branch_name)

    return generate_title_from_branch(branch_name)

def generate_title_from_branch(branch_name: str) -> str:
    """ブランチ名からConventional Commits形式のタイトルを生成"""

    # feature/xxx → feat: xxx
    if branch_name.startswith('feature/'):
        feature_name = branch_name.replace('feature/', '')
        description = feature_name.replace('-', ' ').replace('_', ' ').title()
        return f"feat: {description}"

    # bugfix/xxx → fix: xxx
    if branch_name.startswith('bugfix/'):
        bug_name = branch_name.replace('bugfix/', '')
        description = bug_name.replace('-', ' ').replace('_', ' ').title()
        return f"fix: {description}"

    # hotfix/xxx → fix: xxx
    if branch_name.startswith('hotfix/'):
        hotfix_name = branch_name.replace('hotfix/', '')
        description = hotfix_name.replace('-', ' ').replace('_', ' ').title()
        return f"fix: {description}"

    # docs/xxx → docs: xxx
    if branch_name.startswith('docs/'):
        docs_name = branch_name.replace('docs/', '')
        description = docs_name.replace('-', ' ').replace('_', ' ').title()
        return f"docs: {description}"

    # refactor/xxx → refactor: xxx
    if branch_name.startswith('refactor/'):
        refactor_name = branch_name.replace('refactor/', '')
        description = refactor_name.replace('-', ' ').replace('_', ' ').title()
        return f"refactor: {description}"

    # デフォルト
    return f"chore: Update from {branch_name}"

def generate_pr_body(branch_name: str, base_branch: str) -> str:
    """PR本文を生成"""

    # テンプレート読み込み
    template_path = Path(".claude/templates/pr-template.md")

    if template_path.exists():
        body_template = template_path.read_text()
    else:
        body_template = """## 📋 概要
Claude Codeによって自動生成されたプルリクエストです。

## 🔄 変更内容
{changes}

## ✅ チェックリスト
- [x] コードはプロジェクトのコーディング規約に従っている
- [x] Claude Codeによる自動レビュー完了
- [ ] 手動レビューが必要

## 🧪 テスト結果
{test_results}

## 📝 備考
このPRはClaude Code Hooksにより自動的に作成されました。

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
生成時刻: {timestamp}
"""

    # 変更内容の取得
    result = subprocess.run(
        ['git', 'diff', '--stat', f'{base_branch}..{branch_name}'],
        capture_output=True,
        text=True
    )
    changes = result.stdout.strip() if result.stdout.strip() else "変更なし"

    # コミット一覧の取得
    result = subprocess.run(
        ['git', 'log', f'{base_branch}..{branch_name}', '--oneline'],
        capture_output=True,
        text=True
    )
    commits = result.stdout.strip()

    # テスト結果（簡易版）
    test_results = "- CI/CD実行待ち"

    # プレースホルダー置換
    body = body_template.format(
        changes=changes,
        test_results=test_results,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    return body

def create_pr_with_cli(branch_name: str, base_branch: str) -> bool:
    """GitHub CLIを使用してPR作成"""

    title = generate_pr_title(branch_name, base_branch)
    body = generate_pr_body(branch_name, base_branch)

    print(f"📬 PRタイトル: {title}")
    print(f"📬 ベースブランチ: {base_branch}")
    print(f"📬 ヘッドブランチ: {branch_name}")

    # PR作成コマンド
    cmd = [
        'gh', 'pr', 'create',
        '--title', title[:100],
        '--body', body,
        '--base', base_branch,
        '--head', branch_name,
        '--label', 'automated-pr',
        '--label', 'claude-code'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        pr_url = result.stdout.strip()
        print(f"✅ プルリクエストを作成しました: {pr_url}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PR作成エラー: {e.stderr}")
        return False

def main():
    """メイン処理"""
    if len(sys.argv) != 3:
        print("Usage: python create_pull_request.py <branch_name> <base_branch>")
        sys.exit(1)

    branch_name = sys.argv[1]
    base_branch = sys.argv[2]

    # GitHub CLIが利用可能か確認
    if not check_gh_cli():
        print("❌ GitHub CLIがインストールされていません")
        print("インストール方法: brew install gh")
        sys.exit(1)

    # 認証確認
    result = subprocess.run(['gh', 'auth', 'status'], capture_output=True)
    if result.returncode != 0:
        print("❌ GitHub CLIの認証が必要です")
        print("実行してください: gh auth login")
        sys.exit(1)

    success = create_pr_with_cli(branch_name, base_branch)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
