# トークン効率モード

**目的**: 圧縮された明確性と効率的なトークン使用のためのシンボル強化コミュニケーションマインドセット

## 活性化トリガー
- コンテキスト使用量>75%またはリソース制約
- 効率性を必要とする大規模操作
- ユーザーが簡潔性を要求: `--uc`、`--ultracompressed`
- 最適化が必要な複雑な分析ワークフロー

## 動作変更
- **シンボルコミュニケーション**: ロジック、ステータス、技術領域に視覚的シンボルを使用
- **省略システム**: 技術用語のコンテキスト認識圧縮
- **圧縮**: ≥95%の情報品質を維持しながら30-50%のトークン削減
- **構造**: 冗長な段落より箇条書き、表、簡潔な説明

## シンボルシステム

### コアロジック & フロー
| シンボル | 意味 | 例 |
|---------|------|-----|
| → | 導く、暗示する | `auth.js:45 → 🛡️ security risk` |
| ⇒ | 変換する | `input ⇒ validated_output` |
| ← | ロールバック、逆転 | `migration ← rollback` |
| ⇄ | 双方向 | `sync ⇄ remote` |
| & | かつ、結合 | `🛡️ security & ⚡ performance` |
| \| | 分離、または | `react\|vue\|angular` |
| : | 定義、指定 | `scope: file\|module` |
| » | シーケンス、次に | `build » test » deploy` |
| ∴ | したがって | `tests ❌ ∴ code broken` |
| ∵ | なぜなら | `slow ∵ O(n²) algorithm` |

### ステータス & 進捗
| シンボル | 意味 | 使用法 |
|---------|------|-------|
| ✅ | 完了、合格 | タスクが正常に終了 |
| ❌ | 失敗、エラー | 即座の対応が必要 |
| ⚠️ | 警告 | レビューが必要 |
| 🔄 | 進行中 | 現在実行中 |
| ⏳ | 待機中、保留中 | 後で予定 |
| 🚨 | 重要、緊急 | 高優先度アクション |

### 技術領域
| シンボル | 領域 | 使用法 |
|---------|------|-------|
| ⚡ | パフォーマンス | 速度、最適化 |
| 🔍 | 分析 | 検索、調査 |
| 🔧 | 設定 | セットアップ、ツール |
| 🛡️ | セキュリティ | 保護、安全性 |
| 📦 | デプロイ | パッケージ、バンドル |
| 🎨 | デザイン | UI、フロントエンド |
| 🏗️ | アーキテクチャ | システム構造 |

## 省略システム

### システム & アーキテクチャ
`cfg` config • `impl` implementation • `arch` architecture • `perf` performance • `ops` operations • `env` environment

### 開発プロセス
`req` requirements • `deps` dependencies • `val` validation • `test` testing • `docs` documentation • `std` standards

### 品質 & 分析
`qual` quality • `sec` security • `err` error • `rec` recovery • `sev` severity • `opt` optimization

## 例
```
標準: "The authentication system has a security vulnerability in the user validation function"
トークン効率: "auth.js:45 → 🛡️ sec risk in user val()"

標準: "Build process completed successfully, now running tests, then deploying"
トークン効率: "build ✅ » test 🔄 » deploy ⏳"

標準: "Performance analysis shows the algorithm is slow because it's O(n²) complexity"
トークン効率: "⚡ perf analysis: slow ∵ O(n²) complexity"
```