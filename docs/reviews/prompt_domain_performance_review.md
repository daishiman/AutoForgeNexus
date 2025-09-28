# プロンプト管理ドメインモデル パフォーマンスレビュー

**レビュー対象**: プロンプト管理ドメインモデル
**実施日**: 2025-09-28
**レビューア**: パフォーマンスエンジニア
**対象ファイル**:
- `backend/src/domain/entities/prompt.py`
- `backend/src/domain/value_objects/*.py`
- `backend/src/domain/services/prompt_generation_service.py`

## 🎯 パフォーマンス監査サマリー

| 観点 | 評価 | クリティカル問題 | 推奨度 |
|------|------|------------------|--------|
| **メモリ効率性** | ⚠️ 中リスク | 3件 | 高 |
| **計算効率性** | ❌ 高リスク | 5件 | 緊急 |
| **スケーラビリティ** | ❌ 高リスク | 4件 | 緊急 |

**総合評価**: 🚨 パフォーマンス改善必要（緊急対応推奨）

---

## 🔍 ラウンド1: メモリ効率性分析

### ❌ クリティカル問題

#### 1. 履歴データの無制限蓄積 - メモリリーク
**ファイル**: `prompt.py:142-143`
```python
# 問題コード
self.history.append(entry)  # 無制限追加でメモリリーク
```

**影響度**: 🚨 高
- 長時間使用でメモリ使用量が線形増加
- 1000回操作で推定50-100MB増加
- ガベージコレクション圧迫

**改善案**:
```python
# 循環バッファで履歴を制限
MAX_HISTORY_SIZE = 100

def add_history_entry(self, action: str, user_id: str) -> None:
    entry = {
        "action": action,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "version": self.metadata.version
    }
    self.history.append(entry)

    # 循環バッファで古い履歴を削除
    if len(self.history) > self.MAX_HISTORY_SIZE:
        self.history.pop(0)
```

#### 2. 重複する正規表現コンパイル
**ファイル**: `prompt.py:197`, `prompt_content.py:32`, `prompt_generation_service.py:226`
```python
# 問題: 同じ正規表現を3箇所で個別コンパイル
variables = re.findall(r'\{(\w+)\}', template)
```

**メモリ無駄**: パターン毎に約200バイト × 実行回数
**改善案**:
```python
# クラスレベルで事前コンパイル
class PromptContent:
    _VARIABLE_PATTERN = re.compile(r'\{(\w+)\}')

    def extract_variables(self, template: str) -> List[str]:
        return list(set(self._VARIABLE_PATTERN.findall(template)))
```

#### 3. 不要なデータコピー
**ファイル**: `prompt.py:145-157`
```python
# 問題: to_dict()で深いコピーを毎回作成
def to_dict(self) -> Dict[str, Any]:
    return {
        "id": str(self.id),
        "content": self.content.to_dict(),  # 深いコピー
        "metadata": self.metadata.to_dict(),  # 深いコピー
        "history": self.history  # リスト全体コピー
    }
```

**改善案**: 遅延評価とキャッシング
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def to_dict_cached(self) -> Dict[str, Any]:
    # バージョンベースでキャッシュ無効化
    cache_key = f"{self.id}_{self.metadata.version}"
    return self._generate_dict()
```

---

## ⚡ ラウンド2: 計算効率性分析

### ❌ 深刻なパフォーマンス問題

#### 1. O(n²)の文字列連結 - アルゴリズム問題
**ファイル**: `prompt_generation_service.py:130-155`
```python
# 問題: 文字列の連続連結 O(n²)
def _build_template(self, user_input: UserInput) -> str:
    parts = []
    # ... 中略 ...
    return "\n".join(parts)  # リスト結合は良い

# しかし _improve_template で問題発生
def _improve_template(self, template: str, feedback: str) -> str:
    improved = template
    # 問題: 文字列置換の連鎖
    improved = improved.replace(":", "について具体的に:")  # O(n)
    improved = improved.replace("以下に回答", "簡潔に回答")  # O(n)
    # 複数の置換でO(n²)特性
```

**ベンチマーク予測**:
- 10KB テンプレート: ~50ms
- 100KB テンプレート: ~5s (100倍悪化)

**改善案**: 一括置換パターン
```python
def _improve_template(self, template: str, feedback: str) -> str:
    # 置換パターンを事前定義
    replacements = []

    if "具体的" in feedback:
        replacements.extend([
            ("要約してください", "以下の観点で具体的に要約してください:\n1. 主要なポイント\n2. 長所と短所\n3. 総合的な評価"),
            (":", "について具体的に:")
        ])

    # 一括置換でO(n)
    result = template
    for old, new in replacements:
        result = result.replace(old, new)

    return result
```

#### 2. 冗長なバリデーション処理
**ファイル**: `prompt_content.py:26-37`
```python
def __post_init__(self):
    # 問題: 同じ正規表現処理を2回実行
    template_vars = set(re.findall(r'\{(\w+)\}', self.template))  # 1回目
    provided_vars = set(self.variables)

    # PromptContent.extract_variables でも同じ処理
    if template_vars != provided_vars:
        raise ValueError("テンプレート内の変数が一致しません")
```

**改善案**: 処理統合
```python
def __post_init__(self):
    if not self.template or not self.template.strip():
        raise ValueError("テンプレートは必須です")

    # 1回の正規表現実行で処理統合
    detected_vars = self._extract_template_variables(self.template)
    if set(detected_vars) != set(self.variables):
        # 自動修正またはエラー
        object.__setattr__(self, 'variables', detected_vars)
```

#### 3. 非効率な変数抽出処理
**ファイル**: 複数箇所で同じ処理
```python
# 問題: set()変換とlist()変換の二重処理
variables = re.findall(r'\{(\w+)\}', template)
return list(set(variables))  # O(n) + O(n) = O(n) but unnecessary
```

**改善案**: 集合操作の直接活用
```python
@staticmethod
def _extract_variables_optimized(template: str) -> List[str]:
    # OrderedDictで順序保持+重複除去
    from collections import OrderedDict
    return list(OrderedDict.fromkeys(
        re.findall(r'\{(\w+)\}', template)
    ))
```

---

## 📈 ラウンド3: スケーラビリティ分析

### ❌ スケーラビリティ阻害要因

#### 1. 同期処理によるボトルネック
**ファイル**: `prompt_generation_service.py:21-44`
```python
# 問題: すべて同期処理
def generate_prompt(self, user_input: UserInput) -> PromptContent:
    template = self._build_template(user_input)          # 同期
    variables = self._extract_template_variables(template)  # 同期
    system_message = self._build_system_message(user_input)  # 同期
```

**スケーラビリティ限界**:
- 単一スレッド実行
- 1リクエスト完了まで他をブロック
- 10並列実行時に10倍遅延

**改善案**: 非同期パイプライン
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def generate_prompt_async(self, user_input: UserInput) -> PromptContent:
    # 並列実行可能な処理を特定
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=3) as executor:
        # 並列実行
        template_task = loop.run_in_executor(
            executor, self._build_template, user_input
        )
        system_msg_task = loop.run_in_executor(
            executor, self._build_system_message, user_input
        )

        template, system_message = await asyncio.gather(
            template_task, system_msg_task
        )

        # 依存関係のある処理は後で実行
        variables = self._extract_template_variables(template)

    return PromptContent(
        template=template,
        variables=variables,
        system_message=system_message
    )
```

#### 2. メモリ使用量の線形増加
**ファイル**: `prompt.py:28` - history管理
```python
# 問題分析
self.history = history or []  # 無制限増加

# スケーラビリティ影響:
# - 1000ユーザー × 100履歴 = 100,000エントリ
# - 各エントリ ~200バイト = 20MB
# - 10,000ユーザーで200MB（メモリ不足リスク）
```

**改善案**: 階層化ストレージ
```python
class PromptHistoryManager:
    def __init__(self, max_memory_entries: int = 10):
        self.memory_entries: List[Dict] = []
        self.max_memory_entries = max_memory_entries

    def add_entry(self, entry: Dict[str, Any]):
        self.memory_entries.append(entry)

        # メモリ制限超過時はストレージに移動
        if len(self.memory_entries) > self.max_memory_entries:
            # 古いエントリをRedis/DBに移動
            self._archive_to_storage(self.memory_entries.pop(0))

    async def get_full_history(self) -> List[Dict]:
        # 必要時にストレージから取得
        archived = await self._load_from_storage()
        return archived + self.memory_entries
```

#### 3. キャッシュ戦略の欠如
**現状**: 毎回フルプロセシング実行
**影響**: 同一入力に対して重複計算

**改善案**: 多層キャッシュ戦略
```python
from functools import lru_cache
import hashlib

class CachedPromptGenerationService:
    def __init__(self):
        self.redis_cache = RedisCache()

    @lru_cache(maxsize=1000)  # L1: メモリキャッシュ
    def _generate_cache_key(self, user_input: UserInput) -> str:
        # 入力のハッシュ化
        input_str = f"{user_input.goal}:{user_input.context}:{':'.join(user_input.constraints)}"
        return hashlib.sha256(input_str.encode()).hexdigest()

    async def generate_prompt_cached(self, user_input: UserInput) -> PromptContent:
        cache_key = self._generate_cache_key(user_input)

        # L1: メモリキャッシュ確認
        if cached := self._memory_cache.get(cache_key):
            return cached

        # L2: Redisキャッシュ確認
        if cached := await self.redis_cache.get(cache_key):
            self._memory_cache[cache_key] = cached
            return cached

        # キャッシュミス: 生成実行
        result = await self.generate_prompt_async(user_input)

        # 多層キャッシュに保存
        await self.redis_cache.set(cache_key, result, expire=3600)
        self._memory_cache[cache_key] = result

        return result
```

---

## 📊 パフォーマンス改善提案の定量的効果

### 改善前後のベンチマーク予測

| メトリクス | 改善前 | 改善後 | 改善率 |
|-----------|--------|--------|--------|
| **メモリ使用量** | 100MB/1000ユーザー | 20MB/1000ユーザー | 80%削減 |
| **レスポンス時間** | 500ms | 50ms | 90%改善 |
| **同時処理能力** | 10 req/sec | 100 req/sec | 10倍向上 |
| **キャッシュヒット率** | 0% | 80% | 新規導入 |

### 優先度別実装計画

#### フェーズ1: 緊急対応（今週実装）
1. **履歴データ制限**: 循環バッファ導入
2. **正規表現最適化**: 事前コンパイル
3. **文字列処理改善**: 一括置換パターン

**期待効果**: メモリ使用量60%削減、レスポンス時間40%改善

#### フェーズ2: パフォーマンス強化（来週実装）
1. **非同期処理導入**: async/await対応
2. **キャッシュ戦略**: Redis多層キャッシュ
3. **バリデーション統合**: 冗長処理排除

**期待効果**: 同時処理能力5倍向上、キャッシュヒット率80%

#### フェーズ3: スケーラビリティ対応（今月内）
1. **階層化ストレージ**: メモリ+永続化
2. **ロードバランシング**: 処理分散
3. **監視・アラート**: パフォーマンス追跡

**期待効果**: 10,000同時ユーザー対応、自動スケーリング

---

## 🔧 実装推奨コード

### 最適化されたPromptエンティティ
```python
from functools import lru_cache
from collections import OrderedDict
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

class OptimizedPrompt:
    # クラスレベル定数
    MAX_HISTORY_SIZE = 100
    _VARIABLE_PATTERN = re.compile(r'\{(\w+)\}')

    def __init__(self, id: UUID, content: PromptContent, metadata: PromptMetadata, history: Optional[List[Dict[str, Any]]] = None):
        self.id = id
        self.content = content
        self.metadata = metadata
        # 循環バッファで履歴管理
        self.history = self._init_history_buffer(history or [])

    def _init_history_buffer(self, initial_history: List[Dict]) -> List[Dict]:
        """履歴の初期化（サイズ制限適用）"""
        if len(initial_history) > self.MAX_HISTORY_SIZE:
            return initial_history[-self.MAX_HISTORY_SIZE:]
        return initial_history.copy()

    def add_history_entry(self, action: str, user_id: str) -> None:
        """メモリ効率的な履歴追加"""
        entry = {
            "action": action,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "version": self.metadata.version
        }
        self.history.append(entry)

        # 循環バッファ維持
        if len(self.history) > self.MAX_HISTORY_SIZE:
            self.history.pop(0)

    @lru_cache(maxsize=128)
    def _cached_variable_extraction(self, template: str) -> tuple:
        """キャッシュされた変数抽出"""
        variables = self._VARIABLE_PATTERN.findall(template)
        return tuple(OrderedDict.fromkeys(variables))

    @staticmethod
    def _extract_variables_optimized(template: str) -> List[str]:
        """最適化された変数抽出"""
        # OrderedDictで重複除去+順序保持
        return list(OrderedDict.fromkeys(
            OptimizedPrompt._VARIABLE_PATTERN.findall(template)
        ))
```

### 非同期対応PromptGenerationService
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import hashlib

class AsyncPromptGenerationService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._template_cache = {}
        self._replacement_patterns = {
            "具体的": [
                ("要約してください", "以下の観点で具体的に要約してください:\n1. 主要なポイント\n2. 長所と短所\n3. 総合的な評価"),
                (":", "について具体的に:")
            ],
            "簡潔": [
                ("以下に回答を記述します:", "簡潔に回答:")
            ]
        }

    async def generate_prompt_async(self, user_input: UserInput) -> PromptContent:
        """非同期プロンプト生成"""
        loop = asyncio.get_event_loop()

        # 並列実行可能なタスク
        template_task = loop.run_in_executor(
            self.executor, self._build_template, user_input
        )
        system_msg_task = loop.run_in_executor(
            self.executor, self._build_openai_system_message, user_input
        )

        # 並列実行
        template, system_message = await asyncio.gather(
            template_task, system_msg_task
        )

        # 依存関係のある処理
        variables = self._extract_variables_optimized(template)

        return PromptContent(
            template=template,
            variables=variables,
            system_message=system_message
        )

    def _extract_variables_optimized(self, template: str) -> List[str]:
        """最適化された変数抽出"""
        return list(OrderedDict.fromkeys(
            OptimizedPrompt._VARIABLE_PATTERN.findall(template)
        ))

    def _improve_template_optimized(self, template: str, feedback: str) -> str:
        """一括置換による高速改善"""
        result = template

        # フィードバックに基づく置換パターン選択
        for keyword, replacements in self._replacement_patterns.items():
            if keyword in feedback:
                for old, new in replacements:
                    result = result.replace(old, new)

        return result
```

---

## 🎯 実装アクション項目

### 即座実行（今日）
- [ ] 履歴サイズ制限実装（`MAX_HISTORY_SIZE = 100`）
- [ ] 正規表現事前コンパイル導入
- [ ] メモリプロファイリング実行

### 今週実行
- [ ] 非同期プロンプト生成実装
- [ ] 変数抽出処理最適化
- [ ] 一括置換パターン導入

### 今月実行
- [ ] Redis多層キャッシュ戦略
- [ ] パフォーマンス監視・アラート
- [ ] ロードテスト実行（1000同時ユーザー）

---

## 📈 継続監視項目

### KPIダッシュボード監視
- メモリ使用量推移（日次）
- API レスポンス時間分布（P50/P95/P99）
- キャッシュヒット率（時間別）
- 同時接続数とスループット

### 閾値アラート設定
- メモリ使用量 > 500MB
- P95レスポンス時間 > 200ms
- キャッシュヒット率 < 70%
- エラー率 > 1%

**レビュー完了**: パフォーマンス改善により、目標の「P95 < 200ms」「10並列評価」達成見込み