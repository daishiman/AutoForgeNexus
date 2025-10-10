# Phase 3: プロンプト管理API仕様書（認証なし・最小限実装）

## 📋 概要

Phase 3では認証なしの開発環境で、プロンプト管理機能のみの最小限APIを実装します。

## 🚨 重要な制約事項

- **認証なし**: 開発・テスト環境専用（Issue #40で将来実装）
- **シンプルCRUD**: 基本的なプロンプト操作のみ
- **最小限LLM統合**: 改善提案機能のみ（Issue #42で本格実装）
- **評価機能なし**: Issue #41で将来実装
- **リアルタイム機能なし**: WebSocketはIssue #43で将来実装

## 🎯 実装対象API エンドポイント

### Base URL

```
開発環境: http://localhost:8000/api/v1
```

### 1. プロンプト作成

```http
POST /api/v1/prompts
Content-Type: application/json

{
  "title": "商品説明文生成プロンプト",
  "content": "以下の商品情報を基に、魅力的な説明文を200字以内で作成してください。\n\n商品名: {product_name}\n特徴: {features}\n価格: {price}",
  "description": "ECサイト用の商品説明文を生成するプロンプト",
  "tags": ["ecommerce", "product", "marketing"],
  "category": "marketing",
  "parameters": {
    "product_name": {
      "type": "string",
      "required": true,
      "description": "商品名"
    },
    "features": {
      "type": "string",
      "required": true,
      "description": "商品の特徴"
    },
    "price": {
      "type": "number",
      "required": true,
      "description": "価格"
    }
  }
}
```

**レスポンス:**

```json
{
  "id": "prompt_01JBQR8X9M3KTDZP9QS8V5N2WH",
  "title": "商品説明文生成プロンプト",
  "content": "以下の商品情報を基に、魅力的な説明文を200字以内で作成してください。\n\n商品名: {product_name}\n特徴: {features}\n価格: {price}",
  "description": "ECサイト用の商品説明文を生成するプロンプト",
  "tags": ["ecommerce", "product", "marketing"],
  "category": "marketing",
  "parameters": {
    /* パラメータ定義 */
  },
  "version": 1,
  "status": "active",
  "created_at": "2025-09-28T10:30:00Z",
  "updated_at": "2025-09-28T10:30:00Z",
  "created_by": null, // 認証なしのためnull
  "metadata": {
    "word_count": 45,
    "parameter_count": 3,
    "estimated_tokens": 60
  }
}
```

### 2. プロンプト取得

```http
GET /api/v1/prompts/{prompt_id}
```

**レスポンス:**

```json
{
  "id": "prompt_01JBQR8X9M3KTDZP9QS8V5N2WH",
  "title": "商品説明文生成プロンプト",
  "content": "以下の商品情報を基に、魅力的な説明文を200字以内で作成してください。\n\n商品名: {product_name}\n特徴: {features}\n価格: {price}",
  "description": "ECサイト用の商品説明文を生成するプロンプト",
  "tags": ["ecommerce", "product", "marketing"],
  "category": "marketing",
  "parameters": {
    /* パラメータ定義 */
  },
  "version": 1,
  "status": "active",
  "created_at": "2025-09-28T10:30:00Z",
  "updated_at": "2025-09-28T10:30:00Z",
  "created_by": null,
  "metadata": {
    "word_count": 45,
    "parameter_count": 3,
    "estimated_tokens": 60
  }
}
```

### 3. プロンプト更新

```http
PUT /api/v1/prompts/{prompt_id}
Content-Type: application/json

{
  "title": "商品説明文生成プロンプト（改良版）",
  "content": "以下の商品情報を基に、魅力的で具体的な説明文を200字以内で作成してください。顧客の購買意欲を高める表現を心がけてください。\n\n商品名: {product_name}\n特徴: {features}\n価格: {price}\n対象顧客: {target_audience}",
  "description": "ECサイト用の商品説明文を生成するプロンプト（顧客ターゲティング機能追加）",
  "tags": ["ecommerce", "product", "marketing", "targeting"],
  "category": "marketing",
  "parameters": {
    "product_name": {
      "type": "string",
      "required": true,
      "description": "商品名"
    },
    "features": {
      "type": "string",
      "required": true,
      "description": "商品の特徴"
    },
    "price": {
      "type": "number",
      "required": true,
      "description": "価格"
    },
    "target_audience": {
      "type": "string",
      "required": false,
      "description": "対象顧客層"
    }
  }
}
```

**レスポンス:**

```json
{
  "id": "prompt_01JBQR8X9M3KTDZP9QS8V5N2WH",
  "title": "商品説明文生成プロンプト（改良版）",
  "content": "以下の商品情報を基に、魅力的で具体的な説明文を200字以内で作成してください。顧客の購買意欲を高める表現を心がけてください。\n\n商品名: {product_name}\n特徴: {features}\n価格: {price}\n対象顧客: {target_audience}",
  "description": "ECサイト用の商品説明文を生成するプロンプト（顧客ターゲティング機能追加）",
  "tags": ["ecommerce", "product", "marketing", "targeting"],
  "category": "marketing",
  "parameters": {
    /* 更新されたパラメータ定義 */
  },
  "version": 2, // バージョンが自動的にインクリメント
  "status": "active",
  "created_at": "2025-09-28T10:30:00Z",
  "updated_at": "2025-09-28T11:15:00Z",
  "created_by": null,
  "metadata": {
    "word_count": 58,
    "parameter_count": 4,
    "estimated_tokens": 75
  }
}
```

### 4. プロンプト一覧取得

```http
GET /api/v1/prompts?limit=10&offset=0&category=marketing&status=active
```

**クエリパラメータ:**

- `limit`: 取得件数（デフォルト: 20、最大: 100）
- `offset`: オフセット（デフォルト: 0）
- `category`: カテゴリフィルター（オプション）
- `status`: ステータスフィルター（active, draft, archived）
- `tags`: タグフィルター（カンマ区切り）
- `search`: タイトル・説明文での部分一致検索

**レスポンス:**

```json
{
  "prompts": [
    {
      "id": "prompt_01JBQR8X9M3KTDZP9QS8V5N2WH",
      "title": "商品説明文生成プロンプト（改良版）",
      "description": "ECサイト用の商品説明文を生成するプロンプト（顧客ターゲティング機能追加）",
      "category": "marketing",
      "tags": ["ecommerce", "product", "marketing", "targeting"],
      "version": 2,
      "status": "active",
      "created_at": "2025-09-28T10:30:00Z",
      "updated_at": "2025-09-28T11:15:00Z",
      "metadata": {
        "word_count": 58,
        "parameter_count": 4,
        "estimated_tokens": 75
      }
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0,
  "has_more": false
}
```

### 5. プロンプト削除

```http
DELETE /api/v1/prompts/{prompt_id}
```

**レスポンス:**

```json
{
  "message": "プロンプトが正常に削除されました",
  "deleted_id": "prompt_01JBQR8X9M3KTDZP9QS8V5N2WH",
  "deleted_at": "2025-09-28T12:00:00Z"
}
```

### 6. バージョン履歴取得

```http
GET /api/v1/prompts/{prompt_id}/versions
```

**レスポンス:**

```json
{
  "prompt_id": "prompt_01JBQR8X9M3KTDZP9QS8V5N2WH",
  "versions": [
    {
      "version": 2,
      "title": "商品説明文生成プロンプト（改良版）",
      "content": "以下の商品情報を基に、魅力的で具体的な説明文を200字以内で作成してください。顧客の購買意欲を高める表現を心がけてください。\n\n商品名: {product_name}\n特徴: {features}\n価格: {price}\n対象顧客: {target_audience}",
      "created_at": "2025-09-28T11:15:00Z",
      "changes": [
        "対象顧客パラメータを追加",
        "より具体的な指示に改良",
        "購買意欲向上の表現を追加"
      ]
    },
    {
      "version": 1,
      "title": "商品説明文生成プロンプト",
      "content": "以下の商品情報を基に、魅力的な説明文を200字以内で作成してください。\n\n商品名: {product_name}\n特徴: {features}\n価格: {price}",
      "created_at": "2025-09-28T10:30:00Z",
      "changes": ["初期バージョン"]
    }
  ],
  "total_versions": 2
}
```

### 7. プロンプト改善提案（最小限LLM統合）

```http
POST /api/v1/prompts/{prompt_id}/improve
Content-Type: application/json

{
  "improvement_type": "clarity",  // clarity, specificity, effectiveness
  "context": "ECサイトでのコンバージョン率向上が目標",
  "target_audience": "20-30代女性"
}
```

**レスポンス:**

```json
{
  "original_prompt": {
    "id": "prompt_01JBQR8X9M3KTDZP9QS8V5N2WH",
    "content": "以下の商品情報を基に、魅力的な説明文を200字以内で作成してください。\n\n商品名: {product_name}\n特徴: {features}\n価格: {price}"
  },
  "suggestions": [
    {
      "type": "clarity",
      "priority": "high",
      "suggestion": "「魅力的な」を「購買意欲を高める」などより具体的な表現に変更",
      "improved_content": "以下の商品情報を基に、購買意欲を高める説明文を200字以内で作成してください。\n\n商品名: {product_name}\n特徴: {features}\n価格: {price}",
      "reason": "より明確な目的を示すことで、LLMが適切な表現を選択しやすくなります"
    },
    {
      "type": "specificity",
      "priority": "medium",
      "suggestion": "対象顧客層の情報を追加",
      "improved_content": "以下の商品情報を基に、{target_audience}に響く魅力的な説明文を200字以内で作成してください。\n\n商品名: {product_name}\n特徴: {features}\n価格: {price}\n対象顧客: {target_audience}",
      "reason": "ターゲット顧客を明確にすることで、より効果的な訴求が可能になります"
    }
  ],
  "improvement_score": 7.5,
  "generated_at": "2025-09-28T12:30:00Z"
}
```

## 📊 データモデル

### Prompt Entity

```typescript
interface Prompt {
  id: string; // ULID形式
  title: string; // プロンプトタイトル
  content: string; // プロンプト本文
  description?: string; // 説明文
  tags: string[]; // タグ配列
  category: string; // カテゴリ
  parameters: ParameterDefinition; // パラメータ定義
  version: number; // バージョン番号
  status: PromptStatus; // ステータス
  created_at: string; // 作成日時（ISO 8601）
  updated_at: string; // 更新日時（ISO 8601）
  created_by: string | null; // 作成者ID（Phase 3ではnull）
  metadata: PromptMetadata; // メタデータ
}

interface ParameterDefinition {
  [key: string]: {
    type: 'string' | 'number' | 'boolean' | 'array';
    required: boolean;
    description: string;
    default?: any;
    enum?: any[];
  };
}

type PromptStatus = 'active' | 'draft' | 'archived';

interface PromptMetadata {
  word_count: number; // 文字数
  parameter_count: number; // パラメータ数
  estimated_tokens: number; // 推定トークン数
  last_used_at?: string; // 最終使用日時
  usage_count?: number; // 使用回数
}
```

## 🔧 エラーハンドリング

### エラーレスポンス形式

```json
{
  "error": {
    "code": "PROMPT_NOT_FOUND",
    "message": "指定されたプロンプトが見つかりません",
    "details": {
      "prompt_id": "prompt_01JBQR8X9M3KTDZP9QS8V5N2WH",
      "timestamp": "2025-09-28T12:00:00Z"
    }
  }
}
```

### エラーコード一覧

- `PROMPT_NOT_FOUND` (404): プロンプトが見つからない
- `INVALID_PROMPT_DATA` (400): プロンプトデータが無効
- `PROMPT_TITLE_REQUIRED` (400): タイトルが必須
- `PROMPT_CONTENT_REQUIRED` (400): コンテンツが必須
- `INVALID_PARAMETER_DEFINITION` (400): パラメータ定義が無効
- `PROMPT_TOO_LONG` (400): プロンプトが長すぎる（最大10,000文字）
- `VERSION_CONFLICT` (409): バージョン競合
- `RATE_LIMIT_EXCEEDED` (429): レート制限超過
- `INTERNAL_SERVER_ERROR` (500): 内部サーバーエラー

## 🚀 Phase 3実装範囲まとめ

### ✅ 実装対象

- プロンプトCRUD操作
- バージョニング機能
- 基本的な検索・フィルタリング
- 簡単なメタデータ管理
- 最小限の改善提案機能（LangChain使用）

### 🚧 実装除外（将来実装）

- **認証・認可** → Issue #40
- **詳細な評価機能** → Issue #41
- **高度なLLM統合** → Issue #42
- **リアルタイム機能** → Issue #43
- **ワークフロー管理** → Issue #44

## 📝 開発ガイドライン

### API設計原則

1. **RESTful設計**: HTTP動詞とステータスコードの適切な使用
2. **一貫性**: レスポンス形式とエラーハンドリングの統一
3. **バージョニング**: APIバージョンをURLパスに含める
4. **ページネーション**: 大量データの効率的な取得
5. **フィルタリング**: 柔軟な検索・絞り込み機能

### セキュリティ考慮事項（認証なし環境）

1. **入力検証**: すべての入力データの検証
2. **SQLインジェクション対策**: パラメータ化クエリの使用
3. **XSS対策**: 出力時のエスケープ処理
4. **レート制限**: 基本的なレート制限の実装
5. **CORS設定**: 開発環境用の適切なCORS設定

## 🔗 関連ドキュメント

- [Phase 3 バックエンド環境構築ガイド](../setup/PHASE3_BACKEND_ENVIRONMENT_SETUP.md)
- [保留機能Issueリスト](../issues/PHASE3_DEFERRED_FEATURES.md)
- [プロジェクトCLAUDE.md](../../CLAUDE.md)
