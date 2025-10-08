#!/usr/bin/env python3
"""
Bandit JSON出力をGitHub Annotations形式に変換するスクリプト

使用方法:
    bandit -r src/ -f json -o bandit-report.json
    python .github/scripts/convert-bandit-to-github-annotations.py bandit-report.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def convert_severity(severity: str) -> str:
    """BanditのseverityをGitHub Annotationsレベルに変換"""
    severity_map = {
        "HIGH": "error",
        "MEDIUM": "warning",
        "LOW": "notice",
    }
    return severity_map.get(severity.upper(), "notice")


def convert_confidence(confidence: str) -> str:
    """Bandit confidenceを日本語で表現"""
    confidence_map = {
        "HIGH": "高",
        "MEDIUM": "中",
        "LOW": "低",
    }
    return confidence_map.get(confidence.upper(), "不明")


def format_github_annotation(issue: Dict) -> str:
    """
    GitHub Annotations形式のメッセージを生成

    形式: ::error file={name},line={line},endLine={endLine},title={title}::{message}
    """
    file_path = issue.get("filename", "unknown")
    line_number = issue.get("line_number", 1)
    severity = convert_severity(issue.get("issue_severity", "LOW"))
    confidence = convert_confidence(issue.get("issue_confidence", "LOW"))
    test_id = issue.get("test_id", "")
    test_name = issue.get("test_name", "Unknown Test")
    issue_text = issue.get("issue_text", "No description")

    # タイトル: [テストID] テスト名 (信頼度: 高/中/低)
    title = f"[{test_id}] {test_name} (信頼度: {confidence})"

    # メッセージ: 問題の詳細
    message = f"{issue_text}"

    # GitHub Annotations形式で出力
    annotation = f"::{severity} file={file_path},line={line_number},title={title}::{message}"

    return annotation


def process_bandit_report(report_path: str) -> int:
    """
    Bandit JSONレポートを読み込み、GitHub Annotations形式で出力

    Returns:
        エラー件数 (重大度がHIGHの問題数)
    """
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
    except FileNotFoundError:
        print(f"::error::Bandit report not found: {report_path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"::error::Invalid JSON in Bandit report: {e}", file=sys.stderr)
        return 1

    results = report.get("results", [])

    if not results:
        print("✅ Banditセキュリティスキャン: 問題は検出されませんでした")
        return 0

    # 問題をseverity別に集計
    high_count = 0
    medium_count = 0
    low_count = 0

    print(f"\n🔍 Banditセキュリティスキャン結果: {len(results)}件の問題を検出")
    print("=" * 80)

    for issue in results:
        severity = issue.get("issue_severity", "LOW").upper()

        # GitHub Annotationsとして出力
        annotation = format_github_annotation(issue)
        print(annotation)

        # 集計
        if severity == "HIGH":
            high_count += 1
        elif severity == "MEDIUM":
            medium_count += 1
        else:
            low_count += 1

    # サマリー出力
    print("\n" + "=" * 80)
    print(f"📊 セキュリティ問題サマリー:")
    print(f"  🔴 HIGH (重大):   {high_count}件")
    print(f"  🟡 MEDIUM (警告): {medium_count}件")
    print(f"  🔵 LOW (情報):    {low_count}件")
    print(f"  📋 合計:          {len(results)}件")

    # HIGHがある場合は非ゼロで終了
    return high_count


def main():
    if len(sys.argv) != 2:
        print(f"使用方法: {sys.argv[0]} <bandit-report.json>", file=sys.stderr)
        sys.exit(1)

    report_path = sys.argv[1]
    error_count = process_bandit_report(report_path)

    # HIGH severityの問題がある場合は終了コード1
    if error_count > 0:
        print(f"\n❌ {error_count}件の重大なセキュリティ問題が検出されました", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n✅ 重大なセキュリティ問題は検出されませんでした")
        sys.exit(0)


if __name__ == "__main__":
    main()
