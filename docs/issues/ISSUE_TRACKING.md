# Issue Tracking Guidelines

## 📋 Issue作成ガイドライン

### Issue作成時の記載項目

```markdown
## 📋 概要
問題の簡潔な説明

## 🚨 優先度
- Critical / High / Medium / Low

## 📊 現状評価
- 影響範囲
- リスクレベル
- 発見元（レビュー/テスト/本番）

## ✅ 対応項目
- [ ] タスク1
- [ ] タスク2
- [ ] タスク3

## 🎯 成功基準
明確な完了条件

## 📅 推定工数
X日 / X週間

## 🏷️ ラベル
- bug / enhancement / security / performance / documentation
- priority-critical / priority-high / priority-medium / priority-low
- phase-3 / phase-4 / phase-5
```

## 優先度定義

- **Critical**: 本番環境のブロッカー、セキュリティ脆弱性
- **High**: MVP必須機能、重要な品質問題
- **Medium**: パフォーマンス改善、コード品質
- **Low**: ドキュメント改善、将来的な拡張

## Issue番号体系

- セキュリティ: SEC-XXX
- バグ: BUG-XXX
- 機能改善: ENH-XXX
- パフォーマンス: PERF-XXX
- ドキュメント: DOC-XXX