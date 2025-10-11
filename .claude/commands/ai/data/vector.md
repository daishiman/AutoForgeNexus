---
name: vector
description: 'libSQL Vectorによるベクトルデータベース管理'
category: data
complexity: high
agents:
  [
    vector-database-specialist,
    database-administrator,
    data-analyst,
    prompt-engineering-specialist,
    version-control-specialist,
  ]
---

# /ai:data:vector - ベクトル DB 管理

## Triggers

- ベクトル埋め込みの生成
- 類似度検索の実装
- インデックス最適化
- ベクトルデータ分析

## Context Trigger Pattern

```
/ai:data:vector [operation embed|search|optimize|analyze] [--dimension 1536] [--index hnsw|ivfflat]
```

## Behavioral Flow

1. **スキーマ設計**: libSQL Vector 拡張設定
2. **埋め込み生成**: テキストのベクトル化
3. **データ投入**: バッチ処理と並列化
4. **インデックス構築**: HNSW/IVFFlat 選択
5. **クエリ最適化**: 検索パフォーマンス調整
6. **類似度計算**: コサイン/ユークリッド距離
7. **分析**: クラスタリングと可視化
8. **監視**: メトリクスとパフォーマンス

Key behaviors:

- 高次元ベクトル処理
- 近似最近傍探索
- ハイブリッド検索
- インデックス自動選択

## Agent Coordination

- **vector-database-specialist** → libSQL Vector 管理主導
- **database-administrator** → DB 統合とパフォーマンス
- **data-analyst** → ベクトル分析と可視化
- **prompt-engineering-specialist** → 埋め込み戦略

## Tool Coordination

- **bash_tool**: libSQL Vector セットアップ
- **create_file**: スキーマ定義とクエリ
- **view**: ベクトルデータ確認
- **str_replace**: インデックス設定更新

## Key Patterns

- **埋め込みモデル**: OpenAI/Cohere/Local
- **検索戦略**: ANN/Exact/Hybrid
- **インデックス**: HNSW(精度)/IVFFlat(速度)
- **次元削減**: PCA/UMAP

## Examples

### プロンプト埋め込み管理

```
/ai:data:vector embed --dimension 1536 --index hnsw
# プロンプトのベクトル化
# HNSW インデックス構築
# 類似プロンプト検索準備
```

### 類似度検索実装

```
/ai:data:vector search --dimension 1536
# k-NN検索実装
# リランキング処理
# ハイブリッド検索
```

### ベクトル分析

```
/ai:data:vector analyze
# クラスタリング実行
# t-SNE可視化
# 異常検出
```

## Boundaries

**Will:**

- 効率的なベクトル管理
- 高速類似度検索
- スケーラブルな設計
- 継続的最適化

**Will Not:**

- 次元数の無制限拡大
- インデックスなし検索
- 不適切な距離関数
- メモリ制限無視
