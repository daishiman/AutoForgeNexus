# バックエンドアーキテクチャ包括的レビュー

**レビュー日**: 2025年10月1日 **対象フェーズ**: Phase 3 Task 3.1完了時点
**レビュアー**: Backend Architect Agent **評価基準**: DDD + Clean
Architecture厳格準拠

---

## 📊 アーキテクチャスコア: **72/100** (C評価)

| カテゴリ                     | スコア | 評価 | 備考                               |
| ---------------------------- | ------ | ---- | ---------------------------------- |
| **DDD準拠性**                | 65/100 | D+   | 集約境界は明確だが実装不完全       |
| **Clean Architecture準拠性** | 78/100 | C+   | レイヤー分離は良好、依存性注入未完 |
| **機能ベース集約パターン**   | 85/100 | B    | 構造は優秀、実装が不足             |
| **データ整合性**             | 60/100 | D    | トランザクション境界未実装         |
| **スケーラビリティ**         | 70/100 | C    | 準備は整っているが実証なし         |

---

## 1. DDD準拠性評価: **65/100** (D+)

### ✅ 優れている点

#### 1.1 境界づけられたコンテキストの明確性 ✅ (90点)

```
✅ 明確な境界設定
- prompt/: プロンプト管理機能
- evaluation/: 評価機能
- llm_integration/: LLM統合
- user_interaction/: ユーザー操作
- workflow/: ワークフロー管理
```

**評価**:
5つのコンテキストが適切に分離され、ユビキタス言語が確立されている。集約間の境界がディレクトリ構造として物理的に表現されている点が優秀。

#### 1.2 値オブジェクトの設計 ✅ (85点)

```python
# backend/src/domain/prompt/value_objects/prompt_content.py
@dataclass(frozen=True)
class PromptContent:
    template: str
    variables: list[str] = field(default_factory=list)
    system_message: str | None = None

    def __post_init__(self):
        if not self.template or not self.template.strip():
            raise ValueError("テンプレートは必須です")
```

**評価**:

- ✅ `frozen=True`による不変性保証
- ✅ `__post_init__`での自己検証
- ✅ ビジネスルール内包（変数整合性チェック）
- ⚠️ 等価性判定が未実装（`__eq__`, `__hash__`）

### ❌ 致命的な問題点

#### 1.3 集約ルートの実装不完全 ❌ (40点)

```python
# backend/src/domain/prompt/entities/prompt.py
class Prompt:  # ❌ BaseEntityを継承していない
    def __init__(self, id: UUID, content: PromptContent, ...):
        self.id = id
        self.content = content
        self.metadata = metadata
        self.history = history or []
```

**問題点**:

1. ❌ **エンティティ基底クラス未継承**:
   `BaseEntity`が定義されているが使用されていない
2. ❌ **ドメインイベント発行未実装**:
   `create_from_user_input()`でイベント発行がない
3. ❌ **不変条件保護不足**: `content`, `metadata`がミュータブル（直接変更可能）
4. ❌ **集約境界違反の可能性**: `history`がリスト直接公開で外部変更可能

**修正案**:

```python
from src.domain.shared.base_entity import BaseEntity
from src.domain.prompt.events.prompt_created import PromptCreatedEvent

class Prompt(BaseEntity):
    def __init__(
        self,
        id: UUID,
        content: PromptContent,
        metadata: PromptMetadata,
        history: list[dict[str, Any]] | None = None,
    ):
        super().__init__(id)
        self._content = content  # プライベート化
        self._metadata = metadata
        self._history = history or []

    @property
    def content(self) -> PromptContent:
        return self._content

    @classmethod
    def create_from_user_input(cls, user_input: UserInput) -> "Prompt":
        prompt = cls(id=uuid4(), content=content, metadata=metadata)

        # ドメインイベント発行
        event = PromptCreatedEvent(
            prompt_id=str(prompt.id),
            user_id="system",
            title=f"Prompt for {user_input.goal}",
            content=content.template,
        )
        prompt._domain_events.append(event)

        return prompt
```

#### 1.4 リポジトリパターン未実装 ❌ (30点)

```python
# backend/src/domain/shared/base_repository.py
# ❌ ファイルが空（1行のみ）
```

**問題点**:

- ❌ **インターフェース定義なし**: リポジトリの抽象基底クラスが存在しない
- ❌ **集約永続化契約未定義**: 保存・取得・削除の標準インターフェースなし
- ❌ **仕様パターン未実装**: 複雑なクエリ条件の表現方法なし

**修正案**:

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def save(self, entity: T) -> T:
        """集約を永続化"""
        pass

    @abstractmethod
    async def find_by_id(self, id: UUID) -> T | None:
        """IDで集約を取得"""
        pass

    @abstractmethod
    async def delete(self, entity: T) -> None:
        """集約を削除"""
        pass

    @abstractmethod
    async def find_all(self, specification: Specification | None = None) -> list[T]:
        """仕様に基づいて集約を検索"""
        pass
```

#### 1.5 ドメインサービスの責務不明確 ⚠️ (50点)

```python
# backend/src/domain/prompt/services/prompt_generation_service.py
# ❌ ファイルが空（__init__.pyのみ）
```

**問題点**:

- ⚠️
  **ドメインロジックの置き場所不明**: 複数エンティティにまたがるロジックをどこに書くか不明
- ⚠️ **アプリケーションサービスとの境界曖昧**: 責務分離の基準が不明確

---

## 2. Clean Architecture準拠性評価: **78/100** (C+)

### ✅ 優れている点

#### 2.1 レイヤー分離の適切性 ✅ (90点)

```
✅ 4層構造の明確な分離
backend/src/
├── domain/           # ビジネスロジック（依存なし）
├── application/      # ユースケース（ドメインに依存）
├── infrastructure/   # 外部技術（ドメイン・アプリに依存）
└── presentation/     # API（全層に依存可能）
```

**評価**: 依存性の方向が内側（domain）に向かっている正しい構造。

#### 2.2 Core層の横断的関心事分離 ✅ (85点)

```python
# backend/src/core/config/settings.py
class Settings(BaseSettings):
    # Pydantic v2による型安全な設定管理
    app_env: str = Field(default="local")
    database_url: str | None = Field(default=None)

    @field_validator("app_env")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        valid_envs = ["local", "development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"app_env must be one of {valid_envs}")
        return v
```

**評価**:

- ✅ Pydantic v2による型安全性
- ✅ 階層的環境変数読み込み（.env.common → .env.{env} → .env.local）
- ✅ バリデーション実装
- ✅ 環境別設定の完全分離

### ❌ 致命的な問題点

#### 2.3 依存性注入機構未実装 ❌ (50点)

```python
# backend/src/core/dependencies/
# ❌ ディレクトリが空
```

**問題点**:

1. ❌ **DIコンテナ不在**: リポジトリやサービスのインスタンス管理方法が不明
2. ❌ **ライフサイクル管理なし**: シングルトン・スコープドなどの管理なし
3. ❌ **テスタビリティ低下**: モックへの差し替えが困難

**修正案**:

```python
# backend/src/core/dependencies/container.py
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Database
    database = providers.Singleton(
        Database,
        connection_string=config.database_url,
    )

    # Repositories
    prompt_repository = providers.Factory(
        PromptRepositoryImpl,
        session_factory=database.provided.session,
    )

    # Services
    prompt_service = providers.Factory(
        PromptService,
        prompt_repository=prompt_repository,
        event_bus=event_bus,
    )
```

#### 2.4 インターフェース分離原則違反 ⚠️ (65点)

```python
# backend/src/infrastructure/prompt/models/prompt_model.py
class PromptModel(Base, TimestampMixin, SoftDeleteMixin):
    # SQLAlchemyモデルとドメインモデルの混在
    versions: Mapped[list["PromptModel"]] = relationship(...)
```

**問題点**:

- ⚠️
  **ドメインモデルとORMモデルの未分離**: インフラ層のSQLAlchemyモデルが直接使用される可能性
- ⚠️ **マッパー未実装**: ドメインエンティティ ↔ ORMモデルの変換ロジックなし

**修正案**:

```python
# backend/src/infrastructure/prompt/mappers/prompt_mapper.py
class PromptMapper:
    @staticmethod
    def to_domain(model: PromptModel) -> Prompt:
        """ORMモデル → ドメインエンティティ"""
        content = PromptContent(
            template=model.content,
            variables=model.meta_data.get("variables", []),
            system_message=model.system_message,
        )
        metadata = PromptMetadata(
            version=model.version,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.user_id,
        )
        return Prompt(
            id=UUID(model.id),
            content=content,
            metadata=metadata,
        )

    @staticmethod
    def to_persistence(prompt: Prompt) -> PromptModel:
        """ドメインエンティティ → ORMモデル"""
        return PromptModel(
            id=str(prompt.id),
            content=prompt.content.template,
            system_message=prompt.content.system_message,
            version=prompt.metadata.version,
            status=prompt.metadata.status,
            user_id=prompt.metadata.created_by,
        )
```

---

## 3. 機能ベース集約パターン評価: **85/100** (B)

### ✅ 優れている点

#### 3.1 変更範囲の局所化 ✅ (90点)

```
✅ 優れた構造
src/domain/prompt/
├── entities/          # プロンプトエンティティ
├── value_objects/     # 値オブジェクト
├── events/           # ドメインイベント
├── services/         # ドメインサービス
├── repositories/     # リポジトリインターフェース
└── exceptions.py     # ドメイン例外

src/application/prompt/
├── commands/         # コマンド（書き込み）
├── queries/          # クエリ（読み取り）
├── services/         # アプリケーションサービス
└── dto/             # データ転送オブジェクト

src/infrastructure/prompt/
├── repositories/     # リポジトリ実装
├── models/          # ORMモデル
└── adapters/        # 外部サービスアダプター
```

**評価**: 各機能が完全に独立したディレクトリ構造を持ち、変更が他の機能に波及しない優れた設計。

#### 3.2 凝集度の高さ ✅ (85点)

- ✅ **単一責任**: 各ディレクトリが明確な責務を持つ
- ✅ **関連性**: 関連するクラスが同一ディレクトリに配置
- ✅ **マイクロサービス化可能**: 各機能を独立サービスに分離可能な構造

### ⚠️ 改善すべき点

#### 3.3 結合度の分析 ⚠️ (75点)

```python
# backend/src/domain/prompt/events/prompt_created.py
from src.domain.shared.events.domain_event import DomainEvent  # ✅ 適切

# backend/src/infrastructure/prompt/models/prompt_model.py
# ❌ 他ドメインへの直接参照の可能性
# evaluations: Mapped[list["EvaluationModel"]] = relationship(...)
# → 集約境界を越えるため、リポジトリ層で管理
```

**問題点**:

- ⚠️ **暗黙的依存**: コメントで「リポジトリ層で管理」と書かれているが実装なし
- ⚠️ **集約間参照の実装未完**: IDベース参照のベストプラクティスが未確立

**修正案**:

```python
# backend/src/domain/prompt/entities/prompt.py
class Prompt(BaseEntity):
    # ✅ 集約間参照はIDのみ
    evaluation_ids: list[UUID] = field(default_factory=list)

    def associate_evaluation(self, evaluation_id: UUID) -> None:
        """評価IDを関連付け（集約境界を越えない）"""
        if evaluation_id not in self.evaluation_ids:
            self.evaluation_ids.append(evaluation_id)
            event = EvaluationAssociatedEvent(
                prompt_id=self.id,
                evaluation_id=evaluation_id,
            )
            self._domain_events.append(event)
```

---

## 4. データ整合性評価: **60/100** (D)

### ❌ 致命的な問題点

#### 4.1 トランザクション境界未定義 ❌ (40点)

```python
# backend/src/infrastructure/shared/database/
# ❌ トランザクション管理機構なし
```

**問題点**:

1. ❌ **ユニット・オブ・ワーク未実装**: 複数エンティティの一括コミット機能なし
2. ❌ **トランザクション境界不明**: どこでcommit/rollbackするか定義なし
3. ❌ **整合性保証なし**: 部分的な更新が発生する可能性

**修正案**:

```python
# backend/src/infrastructure/shared/database/unit_of_work.py
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

class UnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass

class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session: Session | None = None

    async def __aenter__(self):
        self.session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

# 使用例
async with SQLAlchemyUnitOfWork(session_factory) as uow:
    prompt = await uow.prompt_repository.find_by_id(prompt_id)
    prompt.update_content(new_content)
    await uow.prompt_repository.save(prompt)
    # ここで自動コミット
```

#### 4.2 楽観的ロック未実装 ❌ (50点)

```python
# backend/src/infrastructure/prompt/models/prompt_model.py
class PromptModel(Base, TimestampMixin, SoftDeleteMixin):
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # ❌ 楽観的ロックの仕組みなし
```

**問題点**:

- ❌ **同時更新競合未検出**: 2人が同時に更新するとデータ不整合発生
- ❌ **バージョンチェックなし**: `version`カラムはあるが検証ロジックなし

**修正案**:

```python
# backend/src/infrastructure/prompt/repositories/prompt_repository.py
class PromptRepositoryImpl(PromptRepository):
    async def save(self, prompt: Prompt) -> Prompt:
        model = self._mapper.to_persistence(prompt)

        # 楽観的ロックチェック
        existing = await self.session.get(PromptModel, model.id)
        if existing and existing.version != model.version:
            raise OptimisticLockException(
                f"Prompt {model.id} has been modified by another user"
            )

        model.version += 1  # バージョンインクリメント
        await self.session.merge(model)
        return self._mapper.to_domain(model)
```

#### 4.3 イベントソーシング準備不完全 ⚠️ (70点)

```python
# backend/src/domain/shared/events/event_store.py
# ❌ ファイルが空（__init__.pyのみ）
```

**問題点**:

- ⚠️ **イベントストア未実装**: イベント永続化の仕組みなし
- ⚠️ **再構築機能なし**: イベントから集約を再構築する機能なし

**修正案**:

```python
# backend/src/infrastructure/shared/events/redis_event_store.py
class RedisEventStore:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def append(self, aggregate_id: str, event: DomainEvent):
        """イベントをストリームに追加"""
        stream_key = f"events:{aggregate_id}"
        await self.redis.xadd(
            stream_key,
            {"event": json.dumps(event.to_dict())}
        )

    async def get_events(self, aggregate_id: str) -> list[DomainEvent]:
        """集約のイベント履歴を取得"""
        stream_key = f"events:{aggregate_id}"
        events = await self.redis.xrange(stream_key)
        return [DomainEvent.from_dict(json.loads(e[1]["event"])) for e in events]

    async def rebuild_aggregate(self, aggregate_id: str, aggregate_class):
        """イベントから集約を再構築"""
        events = await self.get_events(aggregate_id)
        aggregate = aggregate_class.create_empty()
        for event in events:
            aggregate.apply_event(event)
        return aggregate
```

---

## 5. スケーラビリティ評価: **70/100** (C)

### ✅ 優れている点

#### 5.1 水平スケール準備 ✅ (80点)

```python
# backend/src/core/config/settings.py
class Settings(BaseSettings):
    database_pool_size: int = Field(default=10)
    redis_pool_size: int = Field(default=10)
    litellm_max_retries: int = Field(default=3)
```

**評価**: 接続プーリング、リトライ設定など水平スケールの基礎は整っている。

### ⚠️ 改善すべき点

#### 5.2 キャッシュ戦略未実装 ⚠️ (60点)

```python
# backend/src/core/config/settings.py
cache_ttl: int = Field(default=3600)
cache_enabled: bool = Field(default=True)
# ❌ 設定はあるが実装なし
```

**問題点**:

- ⚠️ **キャッシュレイヤーなし**: Redisは設定されているが使用ロジックなし
- ⚠️ **キャッシュ無効化戦略なし**: データ更新時のキャッシュクリア方法が不明

**修正案**:

```python
# backend/src/infrastructure/shared/cache/redis_cache.py
class RedisCache:
    def __init__(self, redis_client, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl

    async def get(self, key: str) -> Any | None:
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any, ttl: int | None = None):
        await self.redis.setex(
            key,
            ttl or self.ttl,
            json.dumps(value)
        )

    async def invalidate(self, pattern: str):
        """パターンに一致するキーを削除"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

# 使用例：リポジトリでのキャッシュ活用
class CachedPromptRepository(PromptRepository):
    def __init__(self, repository: PromptRepository, cache: RedisCache):
        self._repository = repository
        self._cache = cache

    async def find_by_id(self, id: UUID) -> Prompt | None:
        cache_key = f"prompt:{id}"
        cached = await self._cache.get(cache_key)
        if cached:
            return Prompt.from_dict(cached)

        prompt = await self._repository.find_by_id(id)
        if prompt:
            await self._cache.set(cache_key, prompt.to_dict())
        return prompt

    async def save(self, prompt: Prompt) -> Prompt:
        result = await self._repository.save(prompt)
        # 保存時にキャッシュ無効化
        await self._cache.invalidate(f"prompt:{prompt.id}")
        return result
```

#### 5.3 非同期処理設計未完成 ⚠️ (65点)

```python
# backend/src/domain/shared/events/event_bus.py
class AsyncEventBus(EventBus):
    async def publish_async(self, event: DomainEvent) -> None:
        await self._event_queue.put(event)
```

**評価**:

- ✅ **非同期イベントバス実装済み**: 基本構造は存在
- ⚠️ **ワーカー実装なし**: バックグラウンド処理のワーカー未実装
- ⚠️ **リトライ戦略なし**: 失敗時の再試行ロジックなし

---

## 6. パフォーマンス最適化評価: **65/100** (D+)

### ⚠️ 改善すべき点

#### 6.1 N+1問題対策なし ⚠️ (50点)

```python
# backend/src/infrastructure/prompt/models/prompt_model.py
versions: Mapped[list["PromptModel"]] = relationship(
    "PromptModel",
    foreign_keys=[parent_id],
    remote_side=[id],
    cascade="all, delete",
)
```

**問題点**:

- ⚠️ **Eager Loading未設定**: 遅延読み込みでN+1クエリ発生の可能性
- ⚠️ **Join戦略不明**: リレーションの取得方法が不明確

**修正案**:

```python
versions: Mapped[list["PromptModel"]] = relationship(
    "PromptModel",
    foreign_keys=[parent_id],
    remote_side=[id],
    cascade="all, delete",
    lazy="selectin",  # N+1問題回避
)

# またはクエリ時に明示的にjoin
query = select(PromptModel).options(
    selectinload(PromptModel.versions)
).where(PromptModel.id == prompt_id)
```

#### 6.2 インデックス戦略 ✅ (80点)

```python
# backend/src/infrastructure/prompt/models/prompt_model.py
__table_args__ = (
    Index("idx_prompts_user_id", "user_id"),
    Index("idx_prompts_status", "status"),
    Index("idx_prompts_created_at", "created_at"),
    Index("idx_prompts_parent_id", "parent_id"),
    Index("idx_prompts_deleted_at", "deleted_at"),
)
```

**評価**: 適切なインデックスが設定されている。ただし複合インデックスの検討余地あり。

---

## 7. テスト基盤評価: **55/100** (D)

### 現状分析

```bash
実装ファイル: 40ファイル (3,373行)
テストファイル: 18ファイル
テストカバレッジ: 未計測（目標80%）
```

### ❌ 致命的な問題点

#### 7.1 単体テスト不足 ❌ (40点)

```
tests/unit/domain/prompt/  # テスト構造はあるが実装少数
tests/integration/         # 統合テストなし
tests/e2e/                # E2Eテストなし
```

**問題点**:

- ❌ **カバレッジ未達**: 目標80%に対して現状不明（推定20-30%）
- ❌ **重要パスの未テスト**: 集約ルート、値オブジェクトの主要メソッド未テスト

#### 7.2 テストダブル戦略なし ⚠️ (50点)

**問題点**:

- ⚠️ **モック/スタブ未整備**: リポジトリやサービスのモック実装なし
- ⚠️ **テストフィクスチャ不足**: テストデータ生成の共通機構なし

---

## 8. 設計上の問題点サマリー

### 🔴 Critical（即座に対応必須）

1. **BaseEntity未使用** (スコア影響: -10点)

   - エンティティが基底クラスを継承していない
   - ドメインイベント発行機構が機能していない

2. **リポジトリインターフェース未定義** (スコア影響: -15点)

   - `base_repository.py`が空ファイル
   - 永続化の標準契約なし

3. **トランザクション境界未実装** (スコア影響: -20点)

   - Unit of Work未実装
   - データ整合性保証なし

4. **依存性注入機構なし** (スコア影響: -12点)
   - DIコンテナ不在
   - テスタビリティ低下

### 🟡 High（Phase 3.2-3.3で対応）

5. **ドメインモデル⇔ORMマッパー未実装** (スコア影響: -8点)

   - インフラ層とドメイン層の結合度高い

6. **楽観的ロック未実装** (スコア影響: -10点)

   - 同時更新競合検出なし

7. **キャッシュレイヤー未実装** (スコア影響: -7点)

   - パフォーマンス最適化の機会損失

8. **イベントストア未実装** (スコア影響: -6点)
   - イベントソーシング準備不完全

### 🟢 Medium（Phase 3.4-3.7で対応）

9. **N+1問題対策不足** (スコア影響: -5点)
10. **テストカバレッジ不足** (スコア影響: -5点)
11. **仕様パターン未実装** (スコア影響: -4点)
12. **ドメインサービス未実装** (スコア影響: -4点)

---

## 9. 改善推奨事項（優先順位順）

### Priority 1: 即座に実施（Task 3.2）

#### 1.1 BaseEntity実装と適用

```python
# backend/src/domain/shared/base_entity.py
from abc import ABC
from uuid import UUID
from typing import List

class BaseEntity(ABC):
    def __init__(self, id: UUID):
        self._id = id
        self._domain_events: List[DomainEvent] = []

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()

    def clear_domain_events(self):
        self._domain_events.clear()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
```

**実装手順**:

1. `base_entity.py`に上記実装を追加
2. `Prompt`エンティティを`BaseEntity`継承に変更
3. `create_from_user_input()`でドメインイベント発行を追加
4. 単体テスト作成（`tests/unit/domain/shared/test_base_entity.py`）

#### 1.2 BaseRepository実装

```python
# backend/src/domain/shared/base_repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from uuid import UUID

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def save(self, entity: T) -> T:
        """集約を永続化"""
        pass

    @abstractmethod
    async def find_by_id(self, id: UUID) -> Optional[T]:
        """IDで集約を取得"""
        pass

    @abstractmethod
    async def find_all(self) -> List[T]:
        """全集約を取得"""
        pass

    @abstractmethod
    async def delete(self, entity: T) -> None:
        """集約を削除"""
        pass
```

**実装手順**:

1. `base_repository.py`に上記実装を追加
2. `PromptRepository`インターフェース作成（`src/domain/prompt/repositories/prompt_repository.py`）
3. `PromptRepositoryImpl`実装（`src/infrastructure/prompt/repositories/prompt_repository_impl.py`）
4. マッパークラス作成（`src/infrastructure/prompt/mappers/prompt_mapper.py`）

#### 1.3 Unit of Work実装

```python
# backend/src/infrastructure/shared/database/unit_of_work.py
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager

class UnitOfWork(ABC):
    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None

    async def __aenter__(self):
        self.session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
```

### Priority 2: Phase 3.3-3.4で実施

#### 2.1 依存性注入コンテナ実装

- `dependency-injector`ライブラリ導入
- `Container`クラス作成（`src/core/dependencies/container.py`）
- リポジトリ・サービスの登録

#### 2.2 楽観的ロック実装

- `OptimisticLockException`追加
- リポジトリでバージョンチェック実装
- 単体テストで競合検証

#### 2.3 キャッシュレイヤー実装

- `RedisCache`クラス作成
- `CachedPromptRepository`デコレーター実装
- キャッシュ無効化戦略確立

### Priority 3: Phase 3.5-3.7で実施

#### 3.1 イベントソーシング完成

- `RedisEventStore`実装
- 集約再構築機能実装
- イベントバージョニング機構

#### 3.2 テストカバレッジ80%達成

- ドメイン層単体テスト充実
- 統合テスト実装（リポジトリ・イベントバス）
- E2Eテスト基盤構築

#### 3.3 パフォーマンス最適化

- N+1問題対策（Eager Loading）
- 複合インデックス追加
- クエリパフォーマンス計測

---

## 10. 将来的なリスク評価

### 🔴 High Risk（早期対応必須）

#### 10.1 データ不整合リスク

**現状**: トランザクション境界未実装、楽観的ロック未実装
**リスク**: 複数ユーザーの同時更新でデータ破損
**影響範囲**: プロンプト管理、評価機能全般 **対策**: Priority 1の1.3（Unit of
Work）、Priority 2の2.2（楽観的ロック）実装

#### 10.2 テスタビリティ低下

**現状**: DI機構なし、モック実装なし
**リスク**: バグ混入率増加、リファクタリング困難 **影響範囲**: 全機能の品質保証
**対策**: Priority 2の2.1（DIコンテナ）、Priority 3の3.2（テスト充実）

### 🟡 Medium Risk（Phase 4-5で対応）

#### 10.3 パフォーマンス劣化

**現状**: キャッシュ未実装、N+1問題対策なし
**リスク**: ユーザー増加でレスポンス遅延 **影響範囲**: 全API **対策**: Priority
2の2.3（キャッシュ）、Priority 3の3.3（最適化）

#### 10.4 スケーラビリティ限界

**現状**: 非同期処理未完成、ワーカー未実装
**リスク**: 並列評価実行時のリソース枯渇 **影響範囲**: 評価機能 **対策**: Phase
4でワーカー実装、Redis Streams活用

### 🟢 Low Risk（Phase 6で対応）

#### 10.5 保守性低下

**現状**: ドメインサービス未実装、仕様パターンなし
**リスク**: ビジネスロジックの重複・散在 **影響範囲**: 新機能追加時の開発速度
**対策**: Phase 6で戦略パターン、仕様パターン導入

---

## 11. アクションプラン（次の3タスク）

### Task 3.2: ドメイン層完成（Priority 1）

**期間**: 2-3日 **成果物**:

- ✅ `BaseEntity`完全実装と`Prompt`への適用
- ✅ `BaseRepository`完全実装
- ✅ `PromptRepository`インターフェース定義
- ✅ ドメインイベント発行機構の動作確認
- ✅ 単体テスト20件追加（カバレッジ50%達成）

**完了基準**:

- [ ] すべてのエンティティが`BaseEntity`継承
- [ ] ドメインイベントが正しく発行される
- [ ] リポジトリインターフェースが定義されている
- [ ] `pytest tests/unit/domain/` がすべてパス

### Task 3.3: インフラ層実装（Priority 1-2）

**期間**: 3-4日 **成果物**:

- ✅ `Unit of Work`実装
- ✅ `PromptRepositoryImpl`実装（Turso接続）
- ✅ `PromptMapper`実装（ドメイン⇔ORM変換）
- ✅ 楽観的ロック実装
- ✅ 統合テスト10件追加

**完了基準**:

- [ ] プロンプトの永続化が動作する
- [ ] トランザクション境界が正しく機能
- [ ] 同時更新競合が検出される
- [ ] `pytest tests/integration/` がすべてパス

### Task 3.4: アプリケーション層実装（Priority 2）

**期間**: 3-4日 **成果物**:

- ✅ DIコンテナ実装（`dependency-injector`）
- ✅ `CreatePromptCommand`/`CreatePromptHandler`実装
- ✅ `GetPromptQuery`/`GetPromptHandler`実装
- ✅ キャッシュレイヤー実装（Redis）
- ✅ E2Eテスト5件追加

**完了基準**:

- [ ] プロンプト作成APIが動作する（POST /api/v1/prompts）
- [ ] プロンプト取得APIが動作する（GET /api/v1/prompts/{id}）
- [ ] キャッシュが機能する
- [ ] 全テストカバレッジ > 70%

---

## 12. 結論

### 総合評価: **72/100 (C評価)** - 「基礎は良好、実装未完成」

#### ✅ 強み

1. **アーキテクチャ構造**: DDD + Clean Architectureの構造は優秀（85点）
2. **機能分離**: 機能ベース集約パターンが適切に適用（85点）
3. **設定管理**: Pydantic v2による型安全な設定管理（85点）
4. **レイヤー分離**: 依存性の方向が正しい（90点）

#### ❌ 弱み

1. **実装不完全**: 構造はあるが実装が空ファイル多数（-28点）
2. **データ整合性**: トランザクション・ロック機構なし（-20点）
3. **テスタビリティ**: DI機構なし、テスト不足（-17点）
4. **パフォーマンス**: キャッシュ・最適化未実装（-13点）

#### 🎯 次のステップ

**Task 3.2-3.4の完了でスコア目標: 85/100 (B評価)**

- Priority 1の3項目実装でCritical問題解消: +13点（→85点）
- テストカバレッジ80%達成: +5点（→90点）
- キャッシュ・最適化実装: +5点（→95点）

#### 📊 達成可能な最終目標

**Phase 3完了時: 90-95/100 (A-評価)**

- DDD/Clean Architecture完全準拠
- データ整合性保証
- 80%以上のテストカバレッジ
- 本番環境レディな品質

---

## 13. レビュー所見

### 評価コメント

Task 3.1でのディレクトリ構造設計は**非常に優秀**。DDD + Clean
Architectureの理論的理解が深く、機能ベース集約パターンが適切に適用されている。ただし、**実装が構造に追いついていない**状態。

特に、`base_repository.py`や`event_store.py`などの重要なファイルが空（1行のみ）なのは、**設計フェーズとしては合格だが、実装フェーズとしては不完全**。

Task 3.2-3.4で上記の**Priority 1項目（BaseEntity, BaseRepository, Unit of
Work）を実装すれば、アーキテクチャスコアは85点以上に到達**すると評価する。

### 技術的推奨

1. **段階的実装**: 一度にすべて実装せず、Prompt集約を完全に仕上げてから他集約に展開
2. **テストファースト**: リポジトリ・サービス実装前に単体テスト作成
3. **統合テスト重視**: ドメイン層とインフラ層の境界テストを充実

### プロジェクト管理

- **現実的なスケジュール**: Task 3.2-3.4で合計8-11日必要
- **品質ゲート**: 各タスク完了時にテストカバレッジ確認必須
- **リスク管理**: データ整合性問題はMVP前に必ず解決すること

---

**レビュー担当**: Backend Architect Agent **次回レビュー**: Task
3.4完了時（Application層実装後）
**署名**: 厳格な基準に基づき、改善可能性を重視した評価を実施
