---
name: security
description: "包括的セキュリティ監査と脆弱性対策"
category: quality
complexity: extreme
agents:
  [
    security-architect,
    test-automation-engineer,
    compliance-officer,
    devops-coordinator,
    version-control-specialist,
  ]
---

# /ai:quality:security - セキュリティ監査

## Triggers

- セキュリティ監査の実施
- 脆弱性スキャンの要求
- ペネトレーションテスト
- コンプライアンス評価

## Context Trigger Pattern

```
/ai:quality:security [scope] [--scan static|dynamic|both] [--pentest] [--compliance gdpr|soc2]
```

## Behavioral Flow

1. **脅威モデリング**: STRIDE 分析実施
2. **静的分析(SAST)**: ソースコード脆弱性検出
3. **動的分析(DAST)**: 実行時脆弱性テスト
4. **依存関係スキャン**: サプライチェーン評価
5. **ペネトレーション**: 侵入テスト実施
6. **コンプライアンス**: 規制要件確認
7. **リスク評価**: CVSS スコアリング
8. **修復計画**: 優先順位付き対策

Key behaviors:

- OWASP Top 10 準拠
- ゼロトラストアプローチ
- 継続的セキュリティ
- DevSecOps 統合

## Agent Coordination

- **security-architect** → セキュリティ評価主導
- **test-automation-engineer** → セキュリティテスト
- **compliance-officer** → 規制遵守確認
- **devops-coordinator** → 修正デプロイ

## Tool Coordination

- **bash_tool**: セキュリティスキャナー実行
- **create_file**: 監査レポート生成
- **view**: 脆弱性詳細確認
- **str_replace**: セキュリティ修正適用

## Key Patterns

- **Defense in Depth**: 多層防御
- **Shift Left**: 早期セキュリティ
- **Zero Trust**: 信頼しない前提
- **Least Privilege**: 最小権限

## Examples

### 総合セキュリティ監査

```
/ai:quality:security --scan both --pentest --compliance soc2
# SAST+DAST実行
# ペネトレーションテスト
# SOC2準拠確認
```

### API セキュリティ

```
/ai:quality:security api --scan dynamic --pentest
# APIエンドポイントテスト
# 認証/認可検証
# インジェクション攻撃
```

### コンプライアンス監査

```
/ai:quality:security --compliance gdpr
# GDPR要件チェック
# データ保護評価
# プライバシー監査
```

## Boundaries

**Will:**

- 包括的脆弱性評価
- 実用的修復提案
- コンプライアンス確保
- 継続的セキュリティ

**Will Not:**

- 実際の攻撃実行
- データの外部送信
- 過度なリスク受容
- セキュリティの後回し
