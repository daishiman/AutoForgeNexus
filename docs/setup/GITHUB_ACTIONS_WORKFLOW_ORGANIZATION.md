# GitHub Actions ワークフロー組織化ガイド

## 概要

GitHub Actionsワークフローを明確に分離し、責務を明確化することで、重複を排除し保守性を向上させました。

## ワークフロー構成

### 1. backend-ci.yml
**責務**: バックエンド専用のCI/CD

**トリガー条件**:
- `backend/**` パスの変更
- `requirements*.txt` の変更
- `pyproject.toml` の変更

**主要ジョブ**:
- 品質チェック（Ruff、Black、mypy）
- ユニットテスト（pytest、カバレッジ80%）
- 統合テスト
- セキュリティスキャン（Bandit、Safety）
- ドメイン層テスト
- Docker イメージビルド
- API仕様生成
- パフォーマンステスト（Locust）

### 2. frontend-ci.yml
**責務**: フロントエンド専用のCI/CD

**トリガー条件**:
- `frontend/**` パスの変更
- `package.json` の変更
- `pnpm-lock.yaml` の変更

**主要ジョブ**:
- 品質チェック（ESLint、Prettier、TypeScript）
- ユニットテスト（Jest、カバレッジ75%）
- E2Eテスト（Playwright）
- ビルドテスト（Next.js）
- バンドル分析
- Lighthouse CI
- Docker イメージビルド

### 3. integration-ci.yml
**責務**: フロントエンド・バックエンド統合テスト

**トリガー条件**:
- main、developブランチへのpush
- main、developブランチへのPR

**主要ジョブ**:
- 統合テスト（フロントエンド⇔バックエンド）
- Docker Compose統合
- 全体セキュリティスキャン（Trivy、OWASP）
- パフォーマンステスト（Lighthouse、k6）
- E2E統合テスト

## 重複排除の詳細

### 排除された重複

1. **ビルド処理**
   - 以前: ci.yml と frontend-ci.yml の両方でフロントエンドビルド
   - 現在: frontend-ci.yml のみでフロントエンドビルド

2. **テスト実行**
   - 以前: ci.yml でバックエンド・フロントエンド両方のテスト
   - 現在: 各ワークフローで専用のテストのみ実行

3. **Docker ビルド**
   - 以前: 複数のワークフローで同じイメージをビルド
   - 現在: 各ワークフローで必要なイメージのみビルド

4. **セキュリティスキャン**
   - 以前: 各ワークフローで全体スキャン
   - 現在:
     - backend-ci.yml: Python専用スキャン
     - frontend-ci.yml: Node.js専用スキャン
     - integration-ci.yml: 全体スキャンのみ

## トリガー戦略

### パス based トリガー
```yaml
# backend-ci.yml
on:
  push:
    paths:
      - 'backend/**'
      - '.github/workflows/backend-ci.yml'

# frontend-ci.yml
on:
  push:
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci.yml'
```

### ブランチ based トリガー
```yaml
# integration-ci.yml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

## 並列実行最適化

### 独立実行可能
- backend-ci.yml と frontend-ci.yml は完全に独立
- 並列実行により全体のCI時間を短縮

### 依存関係
- integration-ci.yml は両方のコンポーネントが必要
- Docker Compose で統合環境を構築

## 実行時間の目安

| ワークフロー | 平均実行時間 | 最大実行時間 |
|------------|-----------|------------|
| backend-ci.yml | 3-4分 | 5分 |
| frontend-ci.yml | 4-5分 | 7分 |
| integration-ci.yml | 6-8分 | 10分 |

## メンテナンス指針

### 新機能追加時
1. 機能がバックエンド専用 → backend-ci.yml に追加
2. 機能がフロントエンド専用 → frontend-ci.yml に追加
3. 機能が両方に関係 → integration-ci.yml に追加

### ワークフロー修正時
- 単一責任の原則を維持
- 重複を避ける
- 明確なトリガー条件を設定

## トラブルシューティング

### ワークフローが実行されない
```bash
# トリガー条件を確認
gh workflow view backend-ci.yml
gh workflow view frontend-ci.yml
gh workflow view integration-ci.yml
```

### ワークフロー失敗の調査
```bash
# 最新の実行を確認
gh run list --workflow=backend-ci.yml
gh run list --workflow=frontend-ci.yml
gh run list --workflow=integration-ci.yml

# ログを確認
gh run view <RUN_ID> --log
```

## まとめ

この組織化により：
- ✅ 責務が明確に分離された
- ✅ 重複が排除された
- ✅ 並列実行により高速化された
- ✅ メンテナンスが容易になった
- ✅ トリガー条件が最適化された