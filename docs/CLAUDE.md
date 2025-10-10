# Documentation CLAUDE.md

このファイルは、AutoForgeNexusのドキュメント管理に関するClaude Code
(claude.ai/code) へのガイダンスを提供します。

## 📁 ドキュメント構造

```
docs/
├── reports/           # 実装レポート・成果報告
│   ├── security/     # セキュリティ関連レポート
│   └── *.md          # タスク完了レポート
├── reviews/          # コードレビュー・評価レポート
│   ├── security/     # セキュリティレビュー
│   └── *.md          # 各種レビュー結果
├── issues/           # Issue管理・追跡
│   ├── ISSUE_TRACKING.md  # Issue管理ガイド
│   └── *.md          # Issue詳細文書
├── setup/            # セットアップガイド
│   ├── environment_setup.md
│   └── PHASE2_*.md   # フェーズ別ガイド
├── development/      # 開発ガイド
├── security/         # セキュリティポリシー
└── README.md         # ドキュメントインデックス
```

## 📝 ドキュメント作成ガイドライン

### 1. レポート作成（reports/）

#### 命名規則

```
TASK_[番号]_[内容]_REPORT.md
例: TASK_2.4.1_MONITORING_REPORT.md
```

#### テンプレート

```markdown
# [タスク名] 実装レポート

## 📋 概要

- **タスク番号**: Task X.X.X
- **実装日**: YYYY-MM-DD
- **担当エージェント**: [agent-name]

## ✅ 実装内容

- 実装項目1
- 実装項目2

## 📊 成果物

- ファイルパス1
- ファイルパス2

## 🎯 達成基準

- [x] 基準1
- [x] 基準2

## 📝 備考

追加情報
```

### 2. レビュー作成（reviews/）

#### 命名規則

```
[対象]_[種類]_REVIEW.md
例: MONITORING_SECURITY_REVIEW.md
```

#### レビュー種類

- **SECURITY_REVIEW**: セキュリティレビュー
- **SRE_REVIEW**: SRE観点レビュー
- **PERFORMANCE_REVIEW**: パフォーマンスレビュー
- **CODE_REVIEW**: コードレビュー

### 3. Issue管理（issues/）

#### Issue作成時の記載項目

```markdown
## 📋 概要

問題の簡潔な説明

## 🚨 優先度

- Critical / High / Medium / Low

## 📊 現状評価

- 影響範囲
- リスクレベル

## ✅ 対応項目

- [ ] タスク1
- [ ] タスク2

## 🎯 成功基準

明確な完了条件

## 📅 推定工数

X週間
```

### 4. セットアップガイド（setup/）

#### フェーズ別ドキュメント

- **PHASE1\_**: Git・基盤環境
- **PHASE2\_**: インフラ・監視
- **PHASE3\_**: バックエンド
- **PHASE4\_**: データベース
- **PHASE5\_**: フロントエンド
- **PHASE6\_**: 統合・品質

## 📊 現在のドキュメント状況

### 完了済みドキュメント ✅

#### Phase 1

- ✅ Git環境セットアップガイド
- ✅ GitHub Actions設定ドキュメント
- ✅ CI/CDパイプライン説明

#### Phase 2

- ✅ Cloudflare設定ガイド
- ✅ 監視実装レポート（Task 2.4.1）
- ✅ セキュリティレビュー（GitHub Actions最適化）
- ✅ SRE評価レポート
- ✅ CI/CD最適化サマリー（52.3%コスト削減達成）
- ✅ 共有ワークフロー実装ドキュメント

### 作成予定ドキュメント 📝

#### Phase 3（バックエンド）

- [ ] FastAPI実装ガイド
- [ ] DDD境界コンテキスト定義
- [ ] API仕様書

#### Phase 4（データベース）

- [ ] Turso設定ガイド
- [ ] マイグレーション手順
- [ ] バックアップ・リストア

#### Phase 5（フロントエンド）

- [ ] Next.js 15.5.4実装ガイド
- [ ] React 19.0.0新機能活用
- [ ] Cloudflare Pages設定

## 🔍 ドキュメント検索

### 最新レポート

```bash
ls -lt docs/reports/*.md | head -5
```

### セキュリティ関連

```bash
find docs -name "*SECURITY*.md"
```

### 特定タスク

```bash
grep -r "Task 2.4" docs/
```

## 📝 ドキュメント更新ルール

1. **即時更新**: タスク完了時に必ずレポート作成
2. **レビュー記録**: すべてのレビュー結果を保存
3. **Issue追跡**: GitHub Issueと連動
4. **バージョン管理**: 重要変更はGitで管理

## 🚨 重要な注意事項

### やってはいけないこと ❌

1. **直接削除禁止**: 古いドキュメントも履歴として保持
2. **上書き禁止**: 新バージョンは別ファイルで作成
3. **分散配置禁止**: 必ずdocs/配下に集約

### 必須事項 ✅

1. **マークダウン形式**: 全ドキュメント.md形式
2. **日本語優先**: 技術用語以外は日本語
3. **相対パス使用**: リンクは相対パス
4. **メタデータ記載**: 作成日、更新日、作成者

## 📈 ドキュメントメトリクス

### 現在の統計

- **総ドキュメント数**: 30+
- **レポート数**: 15+
- **レビュー数**: 10+
- **Issue文書**: 5+

### カバレッジ

- Phase 1: 100% 文書化完了
- Phase 2: 90% 文書化完了
- Phase 3-6: 0% （未着手）

## 🔗 関連リンク

### 内部リンク

- [プロジェクトCLAUDE.md](../CLAUDE.md)
- [README.md](README.md)
- [ISSUE_TRACKING.md](issues/ISSUE_TRACKING.md)

### 外部リンク

- [GitHub Issues](https://github.com/daishiman/AutoForgeNexus/issues)
- [GitHub Wiki](https://github.com/daishiman/AutoForgeNexus/wiki)

## 📚 ドキュメント作成支援

### テンプレート利用

```bash
# レポートテンプレート
cp docs/templates/report_template.md docs/reports/NEW_REPORT.md

# レビューテンプレート
cp docs/templates/review_template.md docs/reviews/NEW_REVIEW.md
```

### 自動生成

```bash
# API仕様書生成
cd backend && python -m src.main --generate-openapi > ../docs/api_spec.json
```

## 🎯 今後の改善計画

1. **自動化**: ドキュメント生成の自動化
2. **検索性向上**: 全文検索機能の追加
3. **多言語対応**: 英語版ドキュメント
4. **ビジュアル化**: アーキテクチャ図の追加
5. **動的更新**: リアルタイムステータス表示
