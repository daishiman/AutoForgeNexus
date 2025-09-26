# AutoForgeNexus ドメインモデル

## 境界付きコンテキスト

### 1. Prompt Context (プロンプトコンテキスト) - コアドメイン
- プロンプト作成・編集・削除
- バージョン管理
- テンプレート管理

### 2. Evaluation Context (評価コンテキスト) - コアドメイン
- 多層評価メトリクス
- A/Bテスト実行
- パフォーマンス測定

### 3. LLM Integration Context (LLM統合コンテキスト) - サポートドメイン
- マルチプロバイダー管理（100+）
- API統合
- コスト管理

### 4. User Management Context (ユーザー管理コンテキスト) - 汎用ドメイン
- ユーザー管理
- 権限管理（Clerk統合）
- 組織管理

### 5. Analytics Context (分析コンテキスト) - サポートドメイン
- 使用統計
- トレンド分析
- 推奨エンジン

## 主要集約
- **Prompt Aggregate**: プロンプトのライフサイクル管理
- **Evaluation Aggregate**: プロンプト品質評価
- **LLMProvider Aggregate**: 外部LLMプロバイダー統合
- **User Aggregate**: ユーザー・認証・認可管理