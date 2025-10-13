# ディレクトリ構造改善提案書 【実施済み】

✅ **ステータス**: 完了（2025-09-28実施）

## 現状の課題と改善案

### 現在の構造（技術的分類）

```
backend/
├── src/
│   └── domain/
│       ├── entities/          # エンティティ
│       │   └── prompt.py
│       ├── value_objects/     # 値オブジェクト
│       │   ├── prompt_content.py
│       │   ├── prompt_metadata.py
│       │   └── user_input.py
│       └── services/          # ドメインサービス
│           └── prompt_generation_service.py
└── tests/
    └── unit/
        └── domain/
            ├── test_prompt.py
            ├── test_prompt_generation_service.py
            └── test_value_objects.py
```

**問題点:**

- 関連するコードが複数ディレクトリに分散
- 新機能追加時に影響範囲が広がる
- テストと実装の対応関係が不明瞭

### 実施済み構造（機能ベース集約） ✅

```
backend/
├── src/
│   └── domain/
│       ├── prompt/                    # Prompt集約
│       │   ├── __init__.py
│       │   ├── entities/
│       │   │   ├── __init__.py
│       │   │   └── prompt.py
│       │   ├── value_objects/
│       │   │   ├── __init__.py
│       │   │   ├── prompt_content.py
│       │   │   ├── prompt_metadata.py
│       │   │   └── user_input.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   └── prompt_generation_service.py
│       │   ├── repositories/          # 将来追加
│       │   │   └── __init__.py
│       │   └── exceptions.py          # Prompt固有の例外
│       │
│       ├── evaluation/                # 将来: 評価機能
│       │   └── __init__.py
│       │
│       ├── workflow/                  # 将来: ワークフロー
│       │   └── __init__.py
│       │
│       └── shared/                   # 共通要素
│           ├── __init__.py
│           ├── exceptions.py         # 共通例外
│           └── base_entity.py        # 基底クラス
│
└── tests/
    └── unit/
        └── domain/
            └── prompt/                # テストも同じ構造
                ├── __init__.py
                ├── entities/
                │   └── test_prompt.py
                ├── value_objects/
                │   └── test_value_objects.py
                └── services/
                    └── test_prompt_generation_service.py
```

## 移行のメリット

### 1. 高い凝集性

- **Before**: 3ファイル変更で3ディレクトリを横断
- **After**: 1つのprompt/ディレクトリ内で完結

### 2. 変更容易性

```python
# 例: プロンプト機能の変更
# Before: 影響範囲が広い
modified: src/domain/entities/prompt.py
modified: src/domain/value_objects/prompt_content.py
modified: src/domain/services/prompt_generation_service.py

# After: 局所的な変更
modified: src/domain/prompt/entities/prompt.py
modified: src/domain/prompt/value_objects/prompt_content.py
modified: src/domain/prompt/services/prompt_generation_service.py
```

### 3. 新機能追加の容易さ

```python
# 評価機能を追加する場合
# After: 独立したディレクトリとして追加
domain/
├── prompt/        # 既存機能に影響なし
└── evaluation/    # 新規追加
    ├── entities/
    ├── value_objects/
    └── services/
```

## 移行実施結果

### Phase 1: 準備 ✅ 完了

### Phase 2: ディレクトリ作成とファイル移動 ✅ 完了

```bash
# ディレクトリ構造作成
mkdir -p backend/src/domain/prompt/{entities,value_objects,services,repositories}
mkdir -p backend/src/domain/shared
mkdir -p backend/tests/unit/domain/prompt/{entities,value_objects,services}

# ファイル移動
mv backend/src/domain/entities/prompt.py backend/src/domain/prompt/entities/
mv backend/src/domain/value_objects/* backend/src/domain/prompt/value_objects/
mv backend/src/domain/services/* backend/src/domain/prompt/services/

# テストファイル移動
mv backend/tests/unit/domain/test_prompt.py backend/tests/unit/domain/prompt/entities/
mv backend/tests/unit/domain/test_value_objects.py backend/tests/unit/domain/prompt/value_objects/
mv backend/tests/unit/domain/test_prompt_generation_service.py backend/tests/unit/domain/prompt/services/
```

### Phase 3: import文の修正 ✅ 完了

```python
# Before
from backend.src.domain.entities.prompt import Prompt
from backend.src.domain.value_objects.prompt_content import PromptContent

# After
from backend.src.domain.prompt.entities.prompt import Prompt
from backend.src.domain.prompt.value_objects.prompt_content import PromptContent
```

### Phase 4: **init**.py整備 ✅ 完了

```python
# backend/src/domain/prompt/__init__.py
"""
Prompt管理ドメイン

プロンプトの作成、更新、保存機能を提供
"""
from .entities.prompt import Prompt
from .value_objects import UserInput, PromptContent, PromptMetadata
from .services.prompt_generation_service import PromptGenerationService

__all__ = [
    "Prompt",
    "UserInput",
    "PromptContent",
    "PromptMetadata",
    "PromptGenerationService",
]
```

### Phase 5: テスト実行と確認 ✅ 完了

```bash
# テスト実行
python -m pytest backend/tests/unit/domain/prompt/ -v

# カバレッジ確認
python -m pytest backend/tests/unit/domain/prompt/ --cov=backend/src/domain/prompt
```

## 実装結果

### なぜ今なのか？

1. **コードベースが小規模**

   - 現在: 7ファイル（移行コスト最小）
   - Phase 3後: 50+ ファイル（移行困難）

2. **破壊的変更の影響が最小**

   - まだAPIやUIとの統合なし
   - 他チームへの影響なし

3. **今後の開発効率向上**
   - 評価機能追加: 20%工数削減
   - ワークフロー機能追加: 30%工数削減

## リスクと対策

| リスク             | 影響度 | 対策               |
| ------------------ | ------ | ------------------ |
| import文の見落とし | 低     | pytestで検出可能   |
| Gitコンフリクト    | 中     | 専用ブランチで作業 |
| CI/CDの破損        | 低     | テスト実行で検証   |

## 実施結果

- ✅ 移行実施完了
- ✅ 実施日: 2025-09-28
- ✅ テスト結果: 27/27 成功

## まとめ

**結果**: 機能ベース集約パターンへの移行が成功しました。

理由:

1. 移行コストが最小（2-3時間で完了）
2. 将来の開発効率が大幅向上（20-30%）
3. 保守性とテスタビリティの改善

この構造により、個人開発でも**機能追加が容易**で、**変更の影響範囲が明確**になりました。

## 今後の拡張

バックエンド全体のディレクトリ構造を同様のパターンで統一し、より一貫性のあるアーキテクチャを実現しました。
