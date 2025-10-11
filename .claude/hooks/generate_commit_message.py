#!/usr/bin/env python3
"""
Claudeの作業内容を分析してConventional Commits形式のメッセージを生成
"""

import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

def get_changed_files() -> Dict[str, List[str]]:
    """変更されたファイルのリストを取得"""
    result = subprocess.run(
        ['git', 'diff', '--staged', '--name-status'],
        capture_output=True,
        text=True
    )

    changes = {
        'added': [],
        'modified': [],
        'deleted': []
    }

    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            continue
        status, filename = parts[0], parts[1]

        if status == 'A':
            changes['added'].append(filename)
        elif status == 'M':
            changes['modified'].append(filename)
        elif status == 'D':
            changes['deleted'].append(filename)

    return changes

def analyze_changes(changes: Dict[str, List[str]]) -> str:
    """変更内容を分析して変更タイプを判定"""
    all_files = changes['added'] + changes['modified'] + changes['deleted']

    # ファイルパスから変更タイプを推定
    file_type_patterns = {
        'feat': [r'src/.+\.(py|ts|tsx|js|jsx)$', r'components/', r'pages/', r'api/'],
        'fix': [r'bugfix/', r'hotfix/', r'fix/'],
        'docs': [r'README', r'docs/', r'\.md$'],
        'style': [r'\.(css|scss|less)$', r'styles/'],
        'refactor': [r'refactor/'],
        'test': [r'test', r'spec', r'__tests__/'],
        'ci': [r'\.github/workflows/', r'\.yml$', r'\.yaml$', r'docker-compose'],
        'chore': [r'package\.json$', r'requirements\.txt$', r'Dockerfile', r'\.gitignore$'],
        'perf': [r'performance/', r'optimize/'],
        'build': [r'build/', r'dist/', r'webpack', r'vite']
    }

    # 各タイプのマッチ数をカウント
    type_scores = {t: 0 for t in file_type_patterns}

    for file in all_files:
        for change_type, patterns in file_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, file, re.IGNORECASE):
                    type_scores[change_type] += 1
                    break

    # 最もスコアが高いタイプを返す
    max_type = max(type_scores, key=type_scores.get)

    # スコアが0の場合はデフォルト
    if type_scores[max_type] == 0:
        return 'chore'

    return max_type

def detect_scope(changes: Dict[str, List[str]]) -> str:
    """変更範囲からスコープを推測"""
    all_files = changes['added'] + changes['modified'] + changes['deleted']

    # スコープパターン
    scope_patterns = {
        'frontend': [r'^frontend/', r'\.tsx?$', r'components/', r'pages/'],
        'backend': [r'^backend/', r'\.py$', r'api/', r'src/'],
        'ci': [r'\.github/workflows/', r'\.ya?ml$'],
        'docs': [r'^docs/', r'README'],
        'test': [r'tests?/', r'__tests__/', r'spec/'],
        'docker': [r'Dockerfile', r'docker-compose'],
        'db': [r'migrations/', r'alembic/', r'database/'],
        'auth': [r'auth', r'clerk', r'security/']
    }

    scope_scores = {s: 0 for s in scope_patterns}

    for file in all_files:
        for scope, patterns in scope_patterns.items():
            for pattern in patterns:
                if re.search(pattern, file, re.IGNORECASE):
                    scope_scores[scope] += 1
                    break

    max_scope = max(scope_scores, key=scope_scores.get)

    if scope_scores[max_scope] > 0:
        return max_scope

    return ""

def generate_summary(changes: Dict[str, List[str]]) -> str:
    """変更サマリーを生成"""
    parts = []

    if changes['added']:
        parts.append(f"{len(changes['added'])}ファイル追加")
    if changes['modified']:
        parts.append(f"{len(changes['modified'])}ファイル更新")
    if changes['deleted']:
        parts.append(f"{len(changes['deleted'])}ファイル削除")

    return "、".join(parts) if parts else "変更なし"

def generate_conventional_commit(changes: Dict[str, List[str]]) -> str:
    """Conventional Commits形式のメッセージを生成"""
    change_type = analyze_changes(changes)
    scope = detect_scope(changes)
    summary = generate_summary(changes)

    # タイトル行（72文字以内推奨）
    title_parts = [change_type]
    if scope:
        title_parts.append(f"({scope})")
    title_parts.append(f": Claude Code自動変更 - {summary}")

    title = "".join(title_parts)[:72]

    # 本文を生成
    body = []
    body.append("")  # 空行
    body.append("## 変更内容")
    body.append("")

    if changes['added']:
        body.append("### 追加ファイル:")
        for file in changes['added'][:10]:
            body.append(f"  - {file}")
        if len(changes['added']) > 10:
            body.append(f"  ... 他 {len(changes['added']) - 10}件")
        body.append("")

    if changes['modified']:
        body.append("### 更新ファイル:")
        for file in changes['modified'][:10]:
            body.append(f"  - {file}")
        if len(changes['modified']) > 10:
            body.append(f"  ... 他 {len(changes['modified']) - 10}件")
        body.append("")

    if changes['deleted']:
        body.append("### 削除ファイル:")
        for file in changes['deleted'][:10]:
            body.append(f"  - {file}")
        if len(changes['deleted']) > 10:
            body.append(f"  ... 他 {len(changes['deleted']) - 10}件")
        body.append("")

    # フッター
    body.append("🤖 Generated with [Claude Code](https://claude.com/claude-code)")
    body.append(f"Co-Authored-By: Claude <noreply@anthropic.com>")
    body.append(f"Timestamp: {datetime.now().isoformat()}")

    return title + "\n" + "\n".join(body)

def main():
    """メイン処理"""
    changes = get_changed_files()

    if not any(changes.values()):
        print("chore: empty commit")
        return

    commit_message = generate_conventional_commit(changes)
    print(commit_message)

if __name__ == "__main__":
    main()
