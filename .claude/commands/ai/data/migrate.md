---
name: migrate
description: "ゼロダウンタイムデータ移行"
category: data
complexity: extreme
agents:
  [
    data-migration-specialist,
    database-administrator,
    backend-developer,
    sre-agent,
    version-control-specialist,
  ]
---

# /ai:data:migrate - データ移行管理

## Triggers

- データベース移行計画
- スキーマアップグレード
- データ変換と ETL
- ゼロダウンタイム要求

## Context Trigger Pattern

```
/ai:data:migrate [source] [target] [--zero-downtime] [--validate] [--rollback-plan]
```

## Behavioral Flow

1. **評価**: 移行規模とリスク分析
2. **計画**: 移行戦略と段階定義
3. **準備**: バックアップと環境構築
4. **スキーマ移行**: DDL 実行と互換性確保
5. **データ移行**: 増分同期とバッチ処理
6. **検証**: 整合性チェックと差分確認
7. **切替**: トラフィックルーティング変更
8. **クリーンアップ**: 旧環境の後処理

Key behaviors:

- デュアルライト戦略
- CDC による増分同期
- カナリア移行
- 自動ロールバック

## Agent Coordination

- **data-migration-specialist** → 移行戦略主導
- **database-administrator** → DB 操作実行
- **backend-developer** → アプリ互換性確保
- **sre-agent** → ダウンタイム最小化

## Tool Coordination

- **bash_tool**: 移行スクリプト実行
- **create_file**: 移行計画書作成
- **view**: データ検証
- **str_replace**: 設定更新

## Key Patterns

- **Blue-Green**: データベース切替
- **増分同期**: CDC/バイナリログ
- **シャドウライト**: 並行書込み
- **検証**: チェックサム比較

## Examples

### PostgreSQL アップグレード

```
/ai:data:migrate postgres-14 postgres-16 --zero-downtime
# 論理レプリケーション設定
# 増分同期実行
# アトミック切替
```

### マイクロサービス分割

```
/ai:data:migrate monolith microservices --validate
# データ分割戦略
# 境界コンテキスト移行
# 整合性検証
```

### クラウド移行

```
/ai:data:migrate on-premise cloud --zero-downtime --rollback-plan
# ハイブリッド運用期間
# 段階的移行
# ロールバック準備
```

## Boundaries

**Will:**

- ゼロダウンタイム保証
- データ整合性確保
- 自動ロールバック
- 包括的検証

**Will Not:**

- データ損失リスク
- 未検証の移行
- 強制的な切替
- バックアップなし実行
