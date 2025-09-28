# Phase 3: バックエンド環境構築ガイド（DDD厳密準拠版）

## 📋 ドキュメント概要

**Phase 3はプロンプト管理機能のみに特化したAutoForgeNexusバックエンド環境構築ガイドです。**

### 🎯 Phase 3の範囲と制約

#### ✅ Phase 3実装範囲（プロンプト管理特化）
- **Prompt Management Bounded Context**のみ実装
- プロンプトCRUD操作（作成・読み取り・更新・削除）
- シンプルなバージョニング機能
- 基本的なプロンプト改善提案（LangChain最小限）
- SQLite/Turso基本データベース接続
- 認証なしの最小限API実装

#### ❌ Phase 3範囲外（将来実装予定）
- **認証・認可機能** (Issue #40)
- **評価システム** (Issue #41)
- **LLM統合機能** (Issue #42)
- **ユーザーインタラクション** (Issue #43)
- **ワークフロー管理** (Issue #44)

### 🏗️ DDD戦略的設計：Bounded Context

#### Prompt Management Context（Phase 3実装対象）

**ユビキタス言語:**
- **Prompt**: ユーザーが作成するAI向けの指示文
- **PromptContent**: プロンプトの実際のテキスト内容
- **PromptVersion**: プロンプトの特定バージョン
- **UserInput**: ユーザーの入力要求や条件
- **ImprovementSuggestion**: AIによる改善提案

**責務範囲:**
- プロンプトのライフサイクル管理
- バージョニングとバージョン履歴
- コンテンツ検証と妥当性チェック
- 改善提案の生成と管理

#### 将来実装予定のContext

```
┌─────────────────────────────────────────────────────────────┐
│                AutoForgeNexus System                        │
├─────────────────┬─────────────────┬─────────────────────────┤
│ Prompt          │ Evaluation      │ LLM Integration         │
│ Management      │ System          │ Context                 │
│ Context         │ Context         │                         │
│ [Phase 3]       │ [Issue #41]     │ [Issue #42]             │
├─────────────────┼─────────────────┼─────────────────────────┤
│ User            │ Workflow        │                         │
│ Interaction     │ Management      │                         │
│ Context         │ Context         │                         │
│ [Issue #43]     │ [Issue #44]     │                         │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## 🎯 DDD戦術的設計：Prompt集約

### Prompt集約（Aggregate）設計

```python
# 集約の一貫性境界とトランザクション境界
Prompt Aggregate {
    - PromptId (集約ルートID)
    - Title, Description
    - PromptContent (値オブジェクト)
    - PromptMetadata (値オブジェクト)
    - List<PromptVersion> (エンティティ集合)
    - CurrentVersion
    - トランザクション境界: 1プロンプト単位
}
```

#### 集約構成要素

**Prompt（集約ルート・エンティティ）**
- 責務: プロンプトのライフサイクル制御、不変条件維持
- ID: UUID型の一意識別子
- 不変条件: タイトル必須、コンテンツ1MB以下、バージョン履歴整合性

**PromptVersion（エンティティ）**
- 責務: 特定バージョンの管理、変更履歴
- ID: バージョン番号（集約内で一意）
- 親集約: Prompt

**PromptContent（値オブジェクト）**
- 責務: プロンプトテキストの不変性保証
- 不変条件: 空文字不可、最大長制限、特殊文字検証

**PromptMetadata（値オブジェクト）**
- 責務: 作成日時、更新日時、タグ等のメタ情報
- 不変性: 作成後変更不可（更新時は新インスタンス生成）

**UserInput（値オブジェクト）**
- 責務: ユーザー入力の構造化表現
- 不変条件: 入力種別の妥当性、必須項目チェック

### ドメインサービス

**PromptGenerationService（ドメインサービス）**
- 責務: プロンプト改善提案のビジネスロジック
- 複数集約を跨がない純粋なドメインロジック
- LLM統合のabstraction（実装はinfrastructure層）

**PromptVersioningService（ドメインサービス）**
- 責務: バージョニング戦略の実装
- セマンティックバージョニング、分岐、マージロジック

### ドメインイベント（集約内定義）

```python
# 各イベントは集約内で定義・発行
PromptCreated(prompt_id, title, created_at)
PromptUpdated(prompt_id, version, updated_at)
PromptVersionCreated(prompt_id, version_number, content)
ImprovementSuggestionGenerated(prompt_id, suggestion_content)
```

## 📁 厳密なDDDディレクトリ構造

### 全体構造概要

```
backend/src/
├── domain/                    # ドメイン層（外部依存なし）
│   ├── prompt/               # Prompt Bounded Context
│   └── shared/               # Shared Kernel
├── application/              # アプリケーション層（CQRS）
│   ├── prompt/              # Promptユースケース
│   └── shared/              # 共通アプリケーションサービス
├── infrastructure/          # インフラストラクチャ層
│   ├── database/           # データ永続化
│   ├── messaging/          # イベントバス・ストア
│   └── llm/               # LLM統合実装
├── presentation/           # プレゼンテーション層
│   ├── api/               # REST API
│   └── middleware/        # ミドルウェア
└── core/                  # アプリケーション横断関心事
    ├── config/           # 設定管理
    └── exceptions/       # 例外定義
```

### Domain層詳細構造

```
backend/src/domain/
├── prompt/                           # Prompt Bounded Context
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── prompt.py                # Prompt集約ルート
│   │   └── prompt_version.py        # PromptVersionエンティティ
│   ├── value_objects/
│   │   ├── __init__.py
│   │   ├── prompt_content.py        # プロンプト内容値オブジェクト
│   │   ├── prompt_metadata.py       # メタデータ値オブジェクト
│   │   └── user_input.py           # ユーザー入力値オブジェクト
│   ├── services/
│   │   ├── __init__.py
│   │   ├── prompt_generation_service.py    # 改善提案サービス
│   │   └── prompt_versioning_service.py    # バージョニングサービス
│   ├── events/                      # ドメインイベント（集約内）
│   │   ├── __init__.py
│   │   ├── prompt_created.py
│   │   ├── prompt_updated.py
│   │   └── prompt_version_created.py
│   ├── repositories/                # Repository interface
│   │   ├── __init__.py
│   │   └── prompt_repository.py     # IPromptRepository
│   ├── specifications/              # 仕様パターン
│   │   ├── __init__.py
│   │   └── prompt_specifications.py
│   └── exceptions.py               # ドメイン固有例外
└── shared/                         # Shared Kernel
    ├── __init__.py
    ├── base_entity.py             # 基底エンティティ
    ├── base_value_object.py       # 基底値オブジェクト
    ├── base_repository.py         # 基底リポジトリinterface
    ├── domain_event.py           # 基底ドメインイベント
    ├── types.py                  # 共通型定義
    └── exceptions.py             # 共通ドメイン例外
```

#### Domain層の責務とファイル例

**entities/prompt.py - Prompt集約ルート**
```python
from src.domain.shared.base_entity import BaseEntity
from src.domain.prompt.value_objects.prompt_content import PromptContent
from src.domain.prompt.events.prompt_created import PromptCreated

class Prompt(BaseEntity):
    """プロンプト集約ルート - 一貫性境界の制御"""

    def __init__(self, title: str, content: PromptContent):
        super().__init__()
        self._validate_business_rules(title, content)
        self.title = title
        self.content = content
        self.versions: List[PromptVersion] = []

        # ドメインイベント発行
        self._domain_events.append(
            PromptCreated(self.id, title, self.created_at)
        )

    def update_content(self, new_content: PromptContent) -> None:
        """ビジネスルール: コンテンツ更新時は新バージョン作成"""
        self._ensure_content_differs(new_content)
        version = self._create_new_version(new_content)
        self.versions.append(version)
        self.content = new_content

        self._domain_events.append(
            PromptUpdated(self.id, version.number, datetime.utcnow())
        )
```

**value_objects/prompt_content.py - 値オブジェクト**
```python
from src.domain.shared.base_value_object import BaseValueObject

class PromptContent(BaseValueObject):
    """プロンプト内容の値オブジェクト - 不変性保証"""

    def __init__(self, text: str):
        self._validate_content(text)
        self._text = text

    @property
    def text(self) -> str:
        return self._text

    def _validate_content(self, text: str) -> None:
        if not text or len(text.strip()) == 0:
            raise InvalidPromptContentError("プロンプト内容は空にできません")
        if len(text) > 1_000_000:  # 1MB制限
            raise InvalidPromptContentError("プロンプト内容が大きすぎます")
```

**services/prompt_generation_service.py - ドメインサービス**
```python
from abc import ABC, abstractmethod
from src.domain.prompt.entities.prompt import Prompt

class ILLMProvider(ABC):
    """LLM統合の抽象化（実装はinfrastructure層）"""
    @abstractmethod
    async def generate_improvement(self, prompt: str) -> str:
        pass

class PromptGenerationService:
    """プロンプト改善提案のドメインサービス"""

    def __init__(self, llm_provider: ILLMProvider):
        self._llm_provider = llm_provider

    async def suggest_improvements(
        self,
        prompt: Prompt,
        user_input: UserInput
    ) -> ImprovementSuggestion:
        """ビジネスロジック: 改善提案生成"""
        # ドメイン知識に基づく改善戦略
        context = self._build_improvement_context(prompt, user_input)
        suggestion = await self._llm_provider.generate_improvement(context)

        return ImprovementSuggestion(
            prompt_id=prompt.id,
            suggestion_content=suggestion,
            confidence_score=self._calculate_confidence(suggestion)
        )
```

### Application層詳細構造（CQRS実装）

```
backend/src/application/
├── prompt/                          # Promptユースケース
│   ├── commands/                    # コマンド（書き込み）
│   │   ├── __init__.py
│   │   ├── create_prompt_command.py
│   │   ├── update_prompt_command.py
│   │   └── generate_improvement_command.py
│   ├── command_handlers/            # コマンドハンドラー
│   │   ├── __init__.py
│   │   ├── create_prompt_handler.py
│   │   ├── update_prompt_handler.py
│   │   └── generate_improvement_handler.py
│   ├── queries/                     # クエリ（読み取り）
│   │   ├── __init__.py
│   │   ├── get_prompt_query.py
│   │   ├── list_prompts_query.py
│   │   └── get_prompt_versions_query.py
│   ├── query_handlers/              # クエリハンドラー
│   │   ├── __init__.py
│   │   ├── get_prompt_handler.py
│   │   ├── list_prompts_handler.py
│   │   └── get_prompt_versions_handler.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── prompt_application_service.py  # オーケストレーション
│   └── dto/                         # データ転送オブジェクト
│       ├── __init__.py
│       ├── prompt_dto.py
│       └── create_prompt_request.py
└── shared/                          # 共通アプリケーション基盤
    ├── __init__.py
    ├── base_command.py              # 基底コマンド
    ├── base_query.py                # 基底クエリ
    ├── base_handler.py              # 基底ハンドラー
    ├── cqrs_bus.py                  # CQRSバス
    ├── transaction_manager.py       # トランザクション管理
    └── exceptions.py                # アプリケーション例外
```

#### Application層の責務とファイル例

**commands/create_prompt_command.py - コマンド**
```python
from src.application.shared.base_command import BaseCommand

class CreatePromptCommand(BaseCommand):
    """プロンプト作成コマンド"""

    def __init__(
        self,
        title: str,
        content_text: str,
        user_input_data: dict
    ):
        self.title = title
        self.content_text = content_text
        self.user_input_data = user_input_data
```

**command_handlers/create_prompt_handler.py - コマンドハンドラー**
```python
from src.application.shared.base_handler import BaseCommandHandler
from src.domain.prompt.repositories.prompt_repository import IPromptRepository
from src.domain.prompt.entities.prompt import Prompt

class CreatePromptHandler(BaseCommandHandler[CreatePromptCommand, str]):
    """プロンプト作成ハンドラー - ユースケース実装"""

    def __init__(
        self,
        prompt_repository: IPromptRepository,
        transaction_manager: ITransactionManager
    ):
        self._prompt_repository = prompt_repository
        self._transaction_manager = transaction_manager

    async def handle(self, command: CreatePromptCommand) -> str:
        """アプリケーションサービス - ユースケースオーケストレーション"""
        async with self._transaction_manager.begin():
            # 1. 値オブジェクト生成
            content = PromptContent(command.content_text)
            user_input = UserInput.from_dict(command.user_input_data)

            # 2. 集約生成（ドメインロジック実行）
            prompt = Prompt.create(command.title, content, user_input)

            # 3. 永続化
            await self._prompt_repository.save(prompt)

            # 4. ドメインイベント発行（トランザクション外）
            await self._publish_domain_events(prompt.domain_events)

            return str(prompt.id)
```

**queries/get_prompt_query.py - クエリ**
```python
from src.application.shared.base_query import BaseQuery

class GetPromptQuery(BaseQuery):
    """プロンプト取得クエリ"""

    def __init__(self, prompt_id: str):
        self.prompt_id = prompt_id
```

**query_handlers/get_prompt_handler.py - クエリハンドラー**
```python
from src.application.shared.base_handler import BaseQueryHandler
from src.application.prompt.dto.prompt_dto import PromptDto

class GetPromptHandler(BaseQueryHandler[GetPromptQuery, PromptDto]):
    """プロンプト取得ハンドラー - 読み取り専用"""

    def __init__(self, prompt_repository: IPromptRepository):
        self._prompt_repository = prompt_repository

    async def handle(self, query: GetPromptQuery) -> PromptDto:
        """クエリ実行 - DTOで返却"""
        prompt = await self._prompt_repository.get_by_id(query.prompt_id)
        if not prompt:
            raise PromptNotFoundError(query.prompt_id)

        return PromptDto.from_entity(prompt)
```

### Infrastructure層詳細構造

```
backend/src/infrastructure/
├── database/                        # データ永続化
│   ├── __init__.py
│   ├── models/                     # SQLAlchemy ORM
│   │   ├── __init__.py
│   │   ├── prompt_model.py         # PromptテーブルORM
│   │   └── prompt_version_model.py # PromptVersionテーブルORM
│   ├── repositories/               # Repository実装
│   │   ├── __init__.py
│   │   └── prompt_repository_impl.py # SQLAlchemy実装
│   ├── migrations/                 # Alembicマイグレーション
│   └── session.py                  # DB接続・セッション管理
├── messaging/                      # イベング・メッセージング
│   ├── __init__.py
│   ├── event_bus.py               # イベントバス実装
│   ├── event_store.py             # イベントストア実装
│   └── redis_event_bus.py         # Redis実装
└── llm/                           # LLM統合実装
    ├── __init__.py
    ├── langchain_prompt_service.py # LangChain実装
    └── llm_provider_impl.py       # ILLMProvider実装
```

#### Infrastructure層の責務とファイル例

**repositories/prompt_repository_impl.py - Repository実装**
```python
from src.domain.prompt.repositories.prompt_repository import IPromptRepository
from src.infrastructure.database.models.prompt_model import PromptModel

class PromptRepositoryImpl(IPromptRepository):
    """SQLAlchemyを使ったRepository実装"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, prompt: Prompt) -> None:
        """集約の永続化 - ドメインオブジェクト→ORM変換"""
        model = PromptModel.from_entity(prompt)
        self._session.add(model)
        await self._session.flush()

    async def get_by_id(self, prompt_id: PromptId) -> Optional[Prompt]:
        """集約の復元 - ORM→ドメインオブジェクト変換"""
        model = await self._session.get(PromptModel, str(prompt_id))
        return model.to_entity() if model else None

    async def find_by_title(self, title: str) -> List[Prompt]:
        """タイトルでの検索"""
        result = await self._session.execute(
            select(PromptModel).where(PromptModel.title.contains(title))
        )
        models = result.scalars().all()
        return [model.to_entity() for model in models]
```

**messaging/event_bus.py - イベントバス実装**
```python
from src.domain.shared.domain_event import DomainEvent

class EventBus:
    """ドメインイベントバス - インフラ実装"""

    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[callable]] = {}

    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: callable
    ) -> None:
        """イベントハンドラー登録"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """イベント発行 - 非同期実行"""
        event_type = type(event)
        if event_type in self._handlers:
            tasks = [
                asyncio.create_task(handler(event))
                for handler in self._handlers[event_type]
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
```

**llm/llm_provider_impl.py - LLM統合実装**
```python
from src.domain.prompt.services.prompt_generation_service import ILLMProvider

class LangChainLLMProvider(ILLMProvider):
    """LangChainを使ったLLM統合実装"""

    def __init__(self, llm_config: LLMConfig):
        self._llm = ChatOpenAI(
            model=llm_config.model_name,
            temperature=llm_config.temperature
        )

    async def generate_improvement(self, prompt: str) -> str:
        """プロンプト改善提案生成"""
        template = PromptTemplate.from_template(
            "以下のプロンプトを改善してください：\n{prompt}\n\n改善提案："
        )
        chain = template | self._llm | StrOutputParser()
        return await chain.ainvoke({"prompt": prompt})
```

### Presentation層詳細構造

```
backend/src/presentation/
├── api/                            # REST API
│   ├── __init__.py
│   ├── v1/                         # APIバージョン1
│   │   ├── __init__.py
│   │   ├── prompt/                 # プロンプトAPI
│   │   │   ├── __init__.py
│   │   │   ├── router.py           # FastAPIルーター
│   │   │   └── schemas.py          # Pydanticスキーマ
│   │   └── dependencies.py        # DI設定
│   └── middleware/                 # ミドルウェア
│       ├── __init__.py
│       ├── error_handler.py        # エラーハンドリング
│       └── cors.py                 # CORS設定
└── schemas/                        # 共通スキーマ
    ├── __init__.py
    ├── base.py                     # 基底スキーマ
    └── error.py                    # エラーレスポンス
```

#### Presentation層の責務とファイル例

**api/v1/prompt/router.py - FastAPIルーター**
```python
from fastapi import APIRouter, Depends
from src.application.prompt.commands.create_prompt_command import CreatePromptCommand
from src.application.prompt.command_handlers.create_prompt_handler import CreatePromptHandler

router = APIRouter(prefix="/prompts", tags=["prompts"])

@router.post("/", response_model=CreatePromptResponse)
async def create_prompt(
    request: CreatePromptRequest,
    handler: CreatePromptHandler = Depends()
) -> CreatePromptResponse:
    """プロンプト作成API"""
    command = CreatePromptCommand(
        title=request.title,
        content_text=request.content,
        user_input_data=request.user_input
    )

    prompt_id = await handler.handle(command)

    return CreatePromptResponse(
        prompt_id=prompt_id,
        message="プロンプトが正常に作成されました"
    )

@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: str,
    handler: GetPromptHandler = Depends()
) -> PromptResponse:
    """プロンプト取得API"""
    query = GetPromptQuery(prompt_id=prompt_id)
    prompt_dto = await handler.handle(query)

    return PromptResponse(
        id=prompt_dto.id,
        title=prompt_dto.title,
        content=prompt_dto.content,
        created_at=prompt_dto.created_at,
        updated_at=prompt_dto.updated_at
    )
```

**api/v1/prompt/schemas.py - Pydanticスキーマ**
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any

class CreatePromptRequest(BaseModel):
    """プロンプト作成リクエスト"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=1000000)
    user_input: Dict[str, Any] = Field(default_factory=dict)

class PromptResponse(BaseModel):
    """プロンプトレスポンス"""
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

## 🚫 DDDアンチパターンと推奨パターン

### ❌ やってはいけないアンチパターン

#### 1. ドメインイベントの誤った配置
```python
# ❌ 間違い: infrastructure層からドメインイベントをimport
from src.infrastructure.messaging.event_bus import EventBus

class Prompt(BaseEntity):
    def __init__(self):
        EventBus().publish(PromptCreated())  # 依存関係違反
```

#### 2. 集約境界の違反
```python
# ❌ 間違い: 別集約の直接参照
class Prompt(BaseEntity):
    def assign_to_user(self, user: User):  # User集約の直接参照
        self.user = user  # 集約境界違反
```

#### 3. Repository実装の混在
```python
# ❌ 間違い: domain層でSQLAlchemyを直接使用
from sqlalchemy.orm import Session

class Prompt(BaseEntity):
    def save(self, session: Session):  # インフラ依存
        session.add(self)  # レイヤー違反
```

#### 4. アプリケーションサービスでのドメインロジック実装
```python
# ❌ 間違い: ハンドラーでビジネスルール実装
class CreatePromptHandler:
    async def handle(self, command):
        # ビジネスルールをハンドラーで実装（ドメイン層に移すべき）
        if len(command.content) > 1000000:
            raise ContentTooLargeError()
```

#### 5. トランザクション境界の違反
```python
# ❌ 間違い: 複数集約の同一トランザクション変更
async def handle(self, command):
    async with transaction:
        prompt = await prompt_repo.get(id)
        user = await user_repo.get(user_id)
        prompt.update(content)  # 集約1変更
        user.update_activity()  # 集約2変更 - 違反
```

### ✅ 推奨パターン

#### 1. 正しいドメインイベント設計
```python
# ✅ 正しい: 集約内でイベント生成、infrastructure層で発行
class Prompt(BaseEntity):
    def update_content(self, content: PromptContent):
        self.content = content
        self._domain_events.append(
            PromptUpdated(self.id, content, datetime.utcnow())
        )  # 集約内でイベント生成

# infrastructure層でイベント発行
class PromptRepositoryImpl:
    async def save(self, prompt: Prompt):
        await self._session.add(model)
        await self._event_bus.publish_all(prompt.domain_events)
```

#### 2. 集約間の疎結合
```python
# ✅ 正しい: IDによる参照とドメインイベント連携
class Prompt(BaseEntity):
    def __init__(self, title: str, creator_id: UserId):  # ID参照
        self.creator_id = creator_id
        self._domain_events.append(
            PromptCreated(self.id, creator_id)
        )

# 別の集約でイベント処理
class UserActivityHandler:
    async def handle(self, event: PromptCreated):
        user = await self._user_repo.get(event.creator_id)
        user.increment_prompt_count()  # 別トランザクション
```

#### 3. Repository パターンの正しい実装
```python
# ✅ 正しい: domain層でinterface定義
class IPromptRepository(ABC):
    @abstractmethod
    async def save(self, prompt: Prompt) -> None:
        pass

# infrastructure層で実装
class PromptRepositoryImpl(IPromptRepository):
    async def save(self, prompt: Prompt) -> None:
        model = PromptModel.from_entity(prompt)
        self._session.add(model)
```

#### 4. ドメインロジックの適切な配置
```python
# ✅ 正しい: ビジネスルールは集約内
class Prompt(BaseEntity):
    def update_content(self, new_content: PromptContent):
        self._validate_content_change(new_content)  # ドメインロジック
        self._create_new_version(new_content)
        self.content = new_content

# アプリケーション層はオーケストレーションのみ
class UpdatePromptHandler:
    async def handle(self, command):
        prompt = await self._repo.get(command.prompt_id)
        content = PromptContent(command.content)
        prompt.update_content(content)  # ドメインロジック呼び出し
        await self._repo.save(prompt)
```

#### 5. トランザクション境界の遵守
```python
# ✅ 正しい: 1集約1トランザクション + イベント連携
class CreatePromptHandler:
    async def handle(self, command):
        async with transaction:
            prompt = Prompt.create(command.title, command.content)
            await self._repo.save(prompt)  # 1集約のみ変更

        # トランザクション外でイベント発行
        await self._event_bus.publish_all(prompt.domain_events)
```

## 🔄 依存関係の方向性

### 正しい依存関係図

```
┌─────────────────┐    ┌─────────────────┐
│  Presentation   │───▶│   Application   │
│      層         │    │       層        │
└─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    Domain       │
                       │      層         │
                       └─────────────────┘
                                ▲
                                │
                       ┌─────────────────┐
                       │ Infrastructure  │
                       │      層         │
                       └─────────────────┘
```

**重要な原則:**
- **Domain層**: 他の層に依存しない
- **Application層**: Domain層のみに依存
- **Infrastructure層**: Domain層のinterfaceに依存（実装）
- **Presentation層**: Application層のみに依存

### インポートパス例

```python
# ✅ 正しいimport例

# Presentation層
from src.application.prompt.commands.create_prompt_command import CreatePromptCommand
from src.application.prompt.command_handlers.create_prompt_handler import CreatePromptHandler

# Application層
from src.domain.prompt.entities.prompt import Prompt
from src.domain.prompt.repositories.prompt_repository import IPromptRepository

# Infrastructure層
from src.domain.prompt.repositories.prompt_repository import IPromptRepository  # interface
from src.domain.prompt.entities.prompt import Prompt  # entity

# ❌ 間違いimport例
# Domain層からInfrastructure層
from src.infrastructure.database.session import SessionManager  # 依存関係違反

# Application層からInfrastructure層
from src.infrastructure.repositories.prompt_repository_impl import PromptRepositoryImpl  # DI違反
```

## 🧪 テスト戦略

### テスト構造

```
backend/tests/
├── unit/                           # 単体テスト（80%カバレッジ目標）
│   ├── domain/
│   │   ├── prompt/
│   │   │   ├── entities/
│   │   │   │   ├── test_prompt.py          # 集約ルートテスト
│   │   │   │   └── test_prompt_version.py  # エンティティテスト
│   │   │   ├── value_objects/
│   │   │   │   ├── test_prompt_content.py  # 値オブジェクトテスト
│   │   │   │   └── test_prompt_metadata.py
│   │   │   ├── services/
│   │   │   │   └── test_prompt_generation_service.py  # ドメインサービステスト
│   │   │   └── events/
│   │   │       └── test_prompt_events.py   # ドメインイベントテスト
│   │   └── shared/
│   │       └── test_base_entity.py         # 基底クラステスト
│   └── application/
│       └── prompt/
│           ├── command_handlers/
│           │   └── test_create_prompt_handler.py    # ハンドラーテスト
│           └── query_handlers/
│               └── test_get_prompt_handler.py
├── integration/                    # 統合テスト
│   ├── infrastructure/
│   │   ├── repositories/
│   │   │   └── test_prompt_repository_impl.py   # DB統合テスト
│   │   └── messaging/
│   │       └── test_event_bus.py             # イベントバステスト
│   └── api/
│       └── v1/
│           └── prompt/
│               └── test_prompt_api.py        # API統合テスト
└── e2e/                           # E2Eテスト
    └── test_prompt_workflow.py              # プロンプト管理フローテスト
```

### テストパターン例

#### ドメインエンティティテスト
```python
# tests/unit/domain/prompt/entities/test_prompt.py
import pytest
from src.domain.prompt.entities.prompt import Prompt
from src.domain.prompt.value_objects.prompt_content import PromptContent

class TestPrompt:
    def test_create_prompt_should_generate_domain_event(self):
        """プロンプト作成時のドメインイベント発行テスト"""
        # Arrange
        title = "Test Prompt"
        content = PromptContent("Test content")

        # Act
        prompt = Prompt.create(title, content)

        # Assert
        assert len(prompt.domain_events) == 1
        assert isinstance(prompt.domain_events[0], PromptCreated)
        assert prompt.domain_events[0].prompt_id == prompt.id

    def test_update_content_should_create_new_version(self):
        """コンテンツ更新時のバージョン作成テスト"""
        # Arrange
        prompt = Prompt.create("Test", PromptContent("Original"))
        new_content = PromptContent("Updated content")

        # Act
        prompt.update_content(new_content)

        # Assert
        assert len(prompt.versions) == 1
        assert prompt.content == new_content
        assert len(prompt.domain_events) == 2  # Created + Updated
```

#### アプリケーションハンドラーテスト
```python
# tests/unit/application/prompt/command_handlers/test_create_prompt_handler.py
import pytest
from unittest.mock import AsyncMock
from src.application.prompt.command_handlers.create_prompt_handler import CreatePromptHandler

class TestCreatePromptHandler:
    @pytest.fixture
    def handler(self):
        mock_repo = AsyncMock()
        mock_transaction = AsyncMock()
        return CreatePromptHandler(mock_repo, mock_transaction)

    async def test_handle_should_save_prompt(self, handler):
        """プロンプト作成コマンド処理テスト"""
        # Arrange
        command = CreatePromptCommand(
            title="Test Prompt",
            content_text="Test content",
            user_input_data={}
        )

        # Act
        result = await handler.handle(command)

        # Assert
        assert result is not None  # プロンプトID返却
        handler._prompt_repository.save.assert_called_once()
```

#### 統合テスト
```python
# tests/integration/infrastructure/repositories/test_prompt_repository_impl.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.repositories.prompt_repository_impl import PromptRepositoryImpl

class TestPromptRepositoryImpl:
    @pytest.fixture
    async def repository(self, async_session: AsyncSession):
        return PromptRepositoryImpl(async_session)

    async def test_save_and_get_prompt(self, repository):
        """プロンプトの永続化と取得テスト"""
        # Arrange
        prompt = Prompt.create("Test", PromptContent("Content"))

        # Act
        await repository.save(prompt)
        retrieved = await repository.get_by_id(prompt.id)

        # Assert
        assert retrieved is not None
        assert retrieved.title == "Test"
        assert retrieved.content.text == "Content"
```

## 🚀 実装セットアップコマンド

### Phase 3 ディレクトリ構造作成

```bash
# Domain層の構築
mkdir -p backend/src/domain/prompt/{entities,value_objects,services,events,repositories,specifications}
mkdir -p backend/src/domain/shared

# Application層の構築
mkdir -p backend/src/application/prompt/{commands,command_handlers,queries,query_handlers,services,dto}
mkdir -p backend/src/application/shared

# Infrastructure層の構築
mkdir -p backend/src/infrastructure/{database/models,database/repositories,messaging,llm}

# Presentation層の構築
mkdir -p backend/src/presentation/api/v1/prompt
mkdir -p backend/src/presentation/middleware
mkdir -p backend/src/presentation/schemas

# テスト構造の構築
mkdir -p backend/tests/{unit/domain/prompt,unit/application/prompt,integration/infrastructure,e2e}
```

### 基本ファイル作成

```bash
# Domain層基本ファイル作成
touch backend/src/domain/prompt/{entities,value_objects,services,events,repositories,specifications}/__init__.py
touch backend/src/domain/prompt/exceptions.py
touch backend/src/domain/shared/__init__.py

# Application層基本ファイル作成
touch backend/src/application/prompt/{commands,command_handlers,queries,query_handlers,services,dto}/__init__.py
touch backend/src/application/shared/__init__.py

# Infrastructure層基本ファイル作成
touch backend/src/infrastructure/{database,messaging,llm}/__init__.py

# Presentation層基本ファイル作成
touch backend/src/presentation/{api,middleware,schemas}/__init__.py
```

## 📋 実装チェックリスト

### Phase 3.1: Domain層実装
- [ ] Shared Kernel基底クラス実装
- [ ] Prompt集約ルート実装
- [ ] PromptVersion エンティティ実装
- [ ] 値オブジェクト（PromptContent, PromptMetadata, UserInput）実装
- [ ] ドメインサービス（PromptGenerationService, PromptVersioningService）実装
- [ ] ドメインイベント（PromptCreated, PromptUpdated等）実装
- [ ] Repository interface実装
- [ ] ドメイン例外実装

### Phase 3.2: Application層実装
- [ ] CQRS基盤（コマンド、クエリ、ハンドラー基底クラス）実装
- [ ] プロンプト管理コマンド・ハンドラー実装
- [ ] プロンプト取得クエリ・ハンドラー実装
- [ ] アプリケーションサービス実装
- [ ] DTO実装

### Phase 3.3: Infrastructure層実装
- [ ] SQLAlchemy ORM モデル実装
- [ ] Repository実装クラス実装
- [ ] イベントバス・イベントストア実装
- [ ] LLM統合サービス実装（LangChain）
- [ ] データベース設定・マイグレーション

### Phase 3.4: Presentation層実装
- [ ] FastAPI ルーター実装
- [ ] Pydantic スキーマ実装
- [ ] ミドルウェア（エラーハンドリング、CORS）実装
- [ ] 依存性注入設定

### Phase 3.5: テスト実装
- [ ] ドメイン層単体テスト（80%カバレッジ）
- [ ] アプリケーション層単体テスト
- [ ] インフラストラクチャ層統合テスト
- [ ] API統合テスト
- [ ] E2Eテスト

### Phase 3.6: 品質保証
- [ ] mypy strict モード対応
- [ ] Ruff linting/formatting
- [ ] pytest実行・カバレッジ確認
- [ ] Docker環境での動作確認
- [ ] API仕様書生成（OpenAPI）

## 📚 参考リソース

### DDD実装パターン
- [Implementing Domain-Driven Design](https://www.amazon.com/Implementing-Domain-Driven-Design-Vaughn-Vernon/dp/0321834577)
- [Architecture Patterns with Python](https://www.cosmicpython.com/)
- [Clean Architecture in Python](https://github.com/cosmic-python/book)

### FastAPI + DDD
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [Python Clean Architecture](https://github.com/pgorecki/python-clean-architecture)

### テスト戦略
- [Test Pyramid in Practice](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Domain-Driven Design Testing Strategies](https://github.com/ddd-crew/ddd-starter-modelling-process)

---

**重要**: このドキュメントは厳密なDDD原則に基づいて設計されています。実装時は各パターンの意図を理解し、アンチパターンを避けて実装してください。Phase 3はプロンプト管理機能のみに特化しており、他の機能は将来のPhaseで実装予定です。