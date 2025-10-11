# AutoForgeNexus システムアーキテクチャ設計書

## 🎯 アーキテクチャ概要

AutoForgeNexusは**DDD + イベント駆動 + クリーンアーキテクチャ**を採用し、複雑なプロンプトエンジニアリングドメインを効率的かつ保守しやすい形で実装します。

## 🏗️ 全体アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │   Next.js UI    │  │   REST API      │  │   GraphQL    │  │
│  │   (React 19)    │  │   (FastAPI)     │  │   (Strawberry)│  │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │  Command Bus    │  │   Query Bus     │  │  Event Bus   │  │
│  │   (CQRS)        │  │    (CQRS)       │  │  (AsyncIO)   │  │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │ Command Handlers│  │ Query Handlers  │  │Event Handlers│  │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                     Domain Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │   Aggregates    │  │ Domain Services │  │Domain Events │  │
│  │ • Prompt        │  │ • Optimization  │  │• Created     │  │
│  │ • Evaluation    │  │ • Analysis      │  │• Updated     │  │
│  │ • LLMProvider   │  │ • Cost Calc     │  │• Evaluated   │  │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │      Turso      │  │      Redis      │  │   Vector DB  │  │
│  │ (Edge SQLite)   │  │   (Cache/Queue) │  │  (libSQL Vec)│  │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │  LLM Providers  │  │  Event Store    │  │  Monitoring  │  │
│  │ • OpenAI        │  │  (EventSourcing)│  │ • Prometheus │  │
│  │ • Anthropic     │  │                 │  │ • Grafana    │  │
│  │ • 100+ others   │  │                 │  │ • Jaeger     │  │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🎨 クリーンアーキテクチャレイヤー

### 1. Presentation Layer (プレゼンテーション層)

#### Frontend (Next.js 15.5 + React 19)

```typescript
// App Router構成
app/
├── (dashboard)/
│   ├── prompts/
│   │   ├── page.tsx           // プロンプト一覧
│   │   ├── [id]/
│   │   │   ├── page.tsx       // プロンプト詳細
│   │   │   └── edit/page.tsx  // プロンプト編集
│   │   └── create/page.tsx    // プロンプト作成
│   ├── evaluations/
│   │   ├── page.tsx           // 評価一覧
│   │   └── [id]/page.tsx      // 評価詳細
│   └── analytics/
│       └── page.tsx           // 分析ダッシュボード
├── api/
│   ├── prompts/
│   │   └── route.ts           // プロンプトAPI
│   └── evaluations/
│       └── route.ts           // 評価API
└── globals.css
```

#### Backend API (FastAPI 0.116.1)

```python
# API構成
api/
├── v1/
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── router.py          # プロンプトエンドポイント
│   │   ├── schemas.py         # Pydanticスキーマ
│   │   └── dependencies.py    # 依存性注入
│   ├── evaluations/
│   │   ├── router.py
│   │   └── schemas.py
│   └── llm/
│       ├── router.py
│       └── schemas.py
├── middleware/
│   ├── auth.py                # 認証ミドルウェア
│   ├── cors.py                # CORS設定
│   └── rate_limiting.py       # レート制限
└── main.py                    # FastAPIアプリケーション
```

### 2. Application Layer (アプリケーション層)

#### CQRS実装

```python
# Command側
@dataclass
class CreatePromptCommand:
    user_id: UserId
    content: str
    template_id: Optional[TemplateId] = None

class CreatePromptCommandHandler:
    def __init__(self,
                 prompt_repo: PromptRepository,
                 event_bus: EventBus):
        self.prompt_repo = prompt_repo
        self.event_bus = event_bus

    async def handle(self, command: CreatePromptCommand) -> PromptId:
        prompt = Prompt.create(
            content=command.content,
            user_id=command.user_id,
            template_id=command.template_id
        )

        await self.prompt_repo.save(prompt)

        # イベント発行
        await self.event_bus.publish(
            PromptCreated(
                prompt_id=prompt.id,
                user_id=command.user_id,
                occurred_at=datetime.utcnow()
            )
        )

        return prompt.id

# Query側
@dataclass
class GetPromptQuery:
    prompt_id: PromptId
    user_id: UserId

class GetPromptQueryHandler:
    def __init__(self, prompt_query_service: PromptQueryService):
        self.query_service = prompt_query_service

    async def handle(self, query: GetPromptQuery) -> PromptDetailDto:
        return await self.query_service.get_prompt_detail(
            query.prompt_id,
            query.user_id
        )
```

#### Event Bus実装

```python
class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._middleware: List[EventMiddleware] = []

    def subscribe(self, event_type: str, handler: EventHandler):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent):
        # ミドルウェア実行
        for middleware in self._middleware:
            event = await middleware.process(event)

        # イベントハンドラー実行
        handlers = self._handlers.get(event.event_type(), [])

        # 並列実行
        tasks = [handler.handle(event) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)

        # イベントストア保存
        await self._save_to_event_store(event)
```

### 3. Domain Layer (ドメイン層)

#### 集約実装例

```python
class Prompt(AggregateRoot):
    def __init__(self,
                 id: PromptId,
                 content: PromptContent,
                 user_id: UserId,
                 created_at: datetime):
        super().__init__(id)
        self._content = content
        self._user_id = user_id
        self._created_at = created_at
        self._versions: List[PromptVersion] = []
        self._evaluations: List[Evaluation] = []

    @classmethod
    def create(cls,
               content: str,
               user_id: UserId,
               template_id: Optional[TemplateId] = None) -> 'Prompt':
        prompt_id = PromptId.generate()
        prompt_content = PromptContent.of(content)

        prompt = cls(
            id=prompt_id,
            content=prompt_content,
            user_id=user_id,
            created_at=datetime.utcnow()
        )

        # ドメインイベント追加
        prompt._add_domain_event(
            PromptCreated(
                prompt_id=prompt_id,
                user_id=user_id,
                template_id=template_id,
                occurred_at=datetime.utcnow()
            )
        )

        return prompt

    def update_content(self, new_content: str) -> None:
        old_content = self._content
        self._content = PromptContent.of(new_content)

        # バージョン作成
        version = PromptVersion.create(
            prompt_id=self.id,
            content=old_content,
            version_number=len(self._versions) + 1
        )
        self._versions.append(version)

        # イベント追加
        self._add_domain_event(
            PromptUpdated(
                prompt_id=self.id,
                old_content=old_content.value,
                new_content=new_content,
                occurred_at=datetime.utcnow()
            )
        )
```

#### ドメインサービス実装

```python
class PromptOptimizationService:
    def __init__(self,
                 llm_clients: Dict[str, LLMClient],
                 evaluation_service: EvaluationService):
        self.llm_clients = llm_clients
        self.evaluation_service = evaluation_service

    async def optimize_prompt(self,
                             prompt: Prompt,
                             strategy: OptimizationStrategy) -> OptimizedPrompt:

        # 現在の評価取得
        current_evaluation = await self.evaluation_service.evaluate(prompt)

        # 最適化戦略に応じた改善案生成
        if strategy == OptimizationStrategy.GENETIC_ALGORITHM:
            return await self._genetic_optimization(prompt, current_evaluation)
        elif strategy == OptimizationStrategy.REINFORCEMENT_LEARNING:
            return await self._rl_optimization(prompt, current_evaluation)
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")

    async def _genetic_optimization(self,
                                   prompt: Prompt,
                                   baseline: Evaluation) -> OptimizedPrompt:
        # 遺伝的アルゴリズムによる最適化
        population = self._generate_initial_population(prompt)

        for generation in range(50):  # 50世代実行
            # 評価
            evaluations = await asyncio.gather(*[
                self.evaluation_service.evaluate(candidate)
                for candidate in population
            ])

            # 選択・交叉・突然変異
            population = self._evolve_population(population, evaluations)

        # 最優秀個体選択
        best_candidate = max(population,
                           key=lambda p: p.fitness_score)

        return OptimizedPrompt(
            original=prompt,
            optimized=best_candidate,
            improvement_score=best_candidate.fitness_score - baseline.overall_score
        )
```

### 4. Infrastructure Layer (インフラ層)

#### リポジトリ実装

```python
class SqlPromptRepository(PromptRepository):
    def __init__(self, session_factory: SessionFactory):
        self.session_factory = session_factory

    async def save(self, prompt: Prompt) -> None:
        async with self.session_factory() as session:
            # ORMエンティティに変換
            prompt_entity = PromptEntity.from_domain(prompt)

            session.merge(prompt_entity)
            await session.commit()

            # ドメインイベント発行
            for event in prompt.get_domain_events():
                await self._event_bus.publish(event)

            prompt.clear_domain_events()

    async def find_by_id(self, prompt_id: PromptId) -> Optional[Prompt]:
        async with self.session_factory() as session:
            prompt_entity = await session.get(PromptEntity, prompt_id.value)

            if prompt_entity is None:
                return None

            return prompt_entity.to_domain()
```

#### イベントストア実装

```python
class TursoEventStore(EventStore):
    def __init__(self, session_factory: SessionFactory):
        self.session_factory = session_factory

    async def save_events(self,
                         stream_id: str,
                         events: List[DomainEvent]) -> None:
        async with self.session_factory() as session:
            event_entities = [
                EventEntity(
                    stream_id=stream_id,
                    event_type=event.event_type(),
                    event_data=json.dumps(event.to_dict()),
                    occurred_at=event.occurred_at,
                    version=await self._get_next_version(session, stream_id)
                )
                for event in events
            ]

            session.add_all(event_entities)
            await session.commit()

    async def get_events(self, stream_id: str) -> List[DomainEvent]:
        async with self.session_factory() as session:
            entities = await session.execute(
                select(EventEntity)
                .where(EventEntity.stream_id == stream_id)
                .order_by(EventEntity.version)
            )

            return [
                self._deserialize_event(entity)
                for entity in entities.scalars()
            ]
```

## 📊 データベース選定: Turso vs Supabase

### Turso選定の決定理由

**検証結果: Turso > Supabase**

#### Turso優位性

- **エッジパフォーマンス**:

  - Cloudflare Workers統合で50ms以下のレイテンシ
  - 東京リージョン対応で日本からのアクセス最適化
  - SQLite基盤でクエリ実行が高速

- **コスト効率性**:

  - 無料枠: 100データベース
  - 月額$5で無制限データベース
  - トラフィック課金なし

- **開発効率性**:

  - Docker不要のローカル開発環境
  - ブランチ機能でGit-likeなデータベース管理
  - 標準SQLのシンプルな操作

- **AI/ML特化機能**:
  - libSQL Vector拡張でネイティブベクトル検索
  - 埋め込み検索が従来のベクトルDBより高速
  - RAG用途に最適化

#### Supabase比較

| 機能               | Turso            | Supabase     | 勝者      |
| ------------------ | ---------------- | ------------ | --------- |
| エッジレイテンシ   | <50ms            | 100-200ms    | **Turso** |
| 無料データベース数 | 100個            | 2個          | **Turso** |
| ベクトル検索       | ネイティブlibSQL | pgvector拡張 | **Turso** |
| 認証機能           | 外部統合推奨     | 内蔵         | Supabase  |
| 管理UI             | シンプル         | 豊富         | Supabase  |
| エコシステム       | 新興             | 成熟         | Supabase  |

**総合判定**:
AutoForgeNexusの要件（エッジパフォーマンス、ベクトル検索、コスト効率）においてTursoが優位

### Turso実装詳細

#### データベース接続設定

```python
# Turso SQLAlchemy設定
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import libsql_client

# Turso接続設定
TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")  # libsql://...
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

# SQLAlchemy Engine (libSQL)
async_engine = create_async_engine(
    f"sqlite+aiosqlite:///{TURSO_DATABASE_URL}",
    connect_args={
        "auth_token": TURSO_AUTH_TOKEN,
        "sync_url": TURSO_DATABASE_URL,
        "check_same_thread": False
    },
    echo=True,  # 開発時のSQL確認用
    pool_pre_ping=True
)

# セッションファクトリ
async_session_factory = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Turso直接クライアント（高度な操作用）
turso_client = libsql_client.create_client(
    url=TURSO_DATABASE_URL,
    auth_token=TURSO_AUTH_TOKEN
)
```

#### ベクトル検索実装

```python
# libSQL Vector統合
class TursoVectorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_prompt_embedding(self, prompt_id: str, embedding: List[float], metadata: dict):
        """プロンプト埋め込みベクトルの保存"""
        vector_data = {
            "prompt_id": prompt_id,
            "embedding": embedding,  # libSQLが自動でベクトル型に変換
            "metadata": json.dumps(metadata),
            "created_at": datetime.utcnow()
        }

        # libSQL Vectorテーブルに挿入
        await self.session.execute(
            text("""
                INSERT INTO prompt_embeddings (prompt_id, embedding, metadata, created_at)
                VALUES (:prompt_id, vector(:embedding), :metadata, :created_at)
            """),
            vector_data
        )
        await self.session.commit()

    async def search_similar_prompts(self, query_embedding: List[float], limit: int = 10) -> List[dict]:
        """類似プロンプト検索（コサイン類似度）"""
        result = await self.session.execute(
            text("""
                SELECT
                    prompt_id,
                    metadata,
                    vector_distance_cos(embedding, vector(:query)) as similarity
                FROM prompt_embeddings
                WHERE vector_distance_cos(embedding, vector(:query)) > 0.7
                ORDER BY similarity DESC
                LIMIT :limit
            """),
            {"query": query_embedding, "limit": limit}
        )

        return [
            {
                "prompt_id": row.prompt_id,
                "metadata": json.loads(row.metadata),
                "similarity": row.similarity
            }
            for row in result.fetchall()
        ]
```

#### マイグレーション管理

```python
# Turso対応マイグレーション
class TursoMigrationManager:
    def __init__(self, database_url: str, auth_token: str):
        self.client = libsql_client.create_client(
            url=database_url,
            auth_token=auth_token
        )

    async def create_tables(self):
        """初期テーブル作成"""
        migrations = [
            # プロンプトテーブル
            """
            CREATE TABLE IF NOT EXISTS prompts (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                user_id TEXT NOT NULL,
                template_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # ベクトル埋め込みテーブル
            """
            CREATE TABLE IF NOT EXISTS prompt_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id TEXT NOT NULL,
                embedding VECTOR(1536),  -- OpenAI ada-002 dimension
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prompt_id) REFERENCES prompts (id)
            )
            """,

            # ベクトル検索インデックス
            """
            CREATE INDEX IF NOT EXISTS idx_prompt_embeddings_vector
            ON prompt_embeddings (embedding)
            """,

            # 評価結果テーブル
            """
            CREATE TABLE IF NOT EXISTS evaluations (
                id TEXT PRIMARY KEY,
                prompt_id TEXT NOT NULL,
                accuracy_score REAL,
                hallucination_rate REAL,
                style_consistency REAL,
                evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prompt_id) REFERENCES prompts (id)
            )
            """
        ]

        for migration in migrations:
            await self.client.execute(migration)

    async def create_branch(self, branch_name: str, from_branch: str = "main"):
        """Tursoブランチ機能の活用"""
        # Note: ブランチ作成はTurso CLIまたはAPIで実行
        # ここではブランチ情報の記録のみ
        await self.client.execute(
            """
            INSERT INTO migration_branches (name, source_branch, created_at)
            VALUES (?, ?, ?)
            """,
            [branch_name, from_branch, datetime.utcnow()]
        )
```

## 🚀 デプロイメントアーキテクチャ

### Cloudflare統合アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare Edge Network                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │ Cloudflare Pages│  │ Cloudflare      │  │   R2 Object  │  │
│  │  (Next.js SSG)  │  │  Workers        │  │   Storage    │  │
│  │   + Clerk Auth  │  │  (Python/WASM)  │  │              │  │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                      Core Services                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │     Turso       │  │     Redis       │  │   LangFuse   │  │
│  │ (Edge SQLite    │  │   (Upstash)     │  │ (LLM Observe)│  │
│  │  + libSQL Vec)  │  │                 │  │ + Grafana    │  │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Turso統合開発環境

```yaml
# docker-compose.yml
version: '3.8'
services:
  # Backend API
  api:
    build: ./backend
    environment:
      - TURSO_DATABASE_URL=libsql://...
      - TURSO_AUTH_TOKEN=...
      - REDIS_URL=redis://redis:6379
      - CLERK_SECRET_KEY=...
    depends_on:
      - redis
    # Tursoはクラウドベースなのでローカルコンテナ不要

  # Frontend (development)
  frontend:
    build: ./frontend
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
      - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=...
    depends_on:
      - api

  # Cache & Message Queue
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  # LangFuse (オプション：ローカル開発用)
  langfuse:
    image: langfuse/langfuse:latest
    environment:
      - DATABASE_URL=postgresql://langfuse:password@langfuse-db:5432/langfuse
      - NEXTAUTH_SECRET=your-secret
      - NEXTAUTH_URL=http://localhost:3001
    ports:
      - '3001:3000'
    depends_on:
      - langfuse-db

  langfuse-db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=langfuse
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=langfuse
    volumes:
      - langfuse_data:/var/lib/postgresql/data

volumes:
  redis_data:
  langfuse_data:
```

## 📊 パフォーマンス要件実装

### スケーラビリティ対応

```python
# 接続プール設定
async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,              # 基本接続数
    max_overflow=30,           # 最大オーバーフロー
    pool_pre_ping=True,        # 接続確認
    pool_recycle=3600,         # 1時間で接続再作成
)

# キャッシュ戦略
class CachedPromptQueryService:
    def __init__(self,
                 base_service: PromptQueryService,
                 cache: RedisClient):
        self.base_service = base_service
        self.cache = cache

    async def get_prompt_detail(self, prompt_id: PromptId) -> PromptDetailDto:
        cache_key = f"prompt:detail:{prompt_id.value}"

        # キャッシュ確認
        cached = await self.cache.get(cache_key)
        if cached:
            return PromptDetailDto.from_json(cached)

        # データベースクエリ
        result = await self.base_service.get_prompt_detail(prompt_id)

        # キャッシュ保存（1時間）
        await self.cache.setex(
            cache_key,
            3600,
            result.to_json()
        )

        return result
```

### 非同期処理設計

```python
# バックグラウンドタスク
class EvaluationTaskProcessor:
    def __init__(self, task_queue: TaskQueue):
        self.task_queue = task_queue

    async def process_evaluation_tasks(self):
        while True:
            try:
                task = await self.task_queue.get()
                await self._process_evaluation_task(task)
                await self.task_queue.ack(task)
            except Exception as e:
                logger.error(f"Task processing failed: {e}")
                await self.task_queue.nack(task)

    async def _process_evaluation_task(self, task: EvaluationTask):
        prompt = await self.prompt_repo.find_by_id(task.prompt_id)
        evaluation = await self.evaluation_service.evaluate(
            prompt,
            task.metrics
        )

        await self.evaluation_repo.save(evaluation)

        # イベント発行
        await self.event_bus.publish(
            EvaluationCompleted(
                evaluation_id=evaluation.id,
                prompt_id=task.prompt_id,
                metrics=evaluation.metrics,
                occurred_at=datetime.utcnow()
            )
        )
```

## 🔒 セキュリティ実装

### 認証・認可

#### 認証ライブラリ選定: **Clerk**

**選定理由**:

- Tursoとの公式統合とベストプラクティス
- 包括的な認証機能（OAuth、MFA、組織管理）
- Edge-firstアーキテクチャでCloudflare Workersと最適化
- 無料枠: 10,000 MAU
- 日本語対応とエンタープライズ準備

**実装例**:

```python
# Clerk統合認証
class ClerkAuthenticationService:
    def __init__(self, clerk_secret_key: str):
        self.clerk_secret_key = clerk_secret_key
        self.clerk_client = ClerkBackend(api_key=clerk_secret_key)

    async def authenticate(self, session_token: str) -> Optional[User]:
        try:
            # Clerkセッション検証
            session = await self.clerk_client.sessions.verify_session(
                session_id=session_token
            )

            # ユーザー情報取得
            clerk_user = await self.clerk_client.users.get_user(
                user_id=session.user_id
            )

            # ドメインUserオブジェクトに変換
            return User(
                id=UserId(clerk_user.id),
                email=clerk_user.email_addresses[0].email_address,
                name=f"{clerk_user.first_name} {clerk_user.last_name}",
                organization_id=clerk_user.organization_memberships[0].organization.id if clerk_user.organization_memberships else None
            )
        except ClerkAPIException:
            return None

# ロールベースアクセス制御
class RBACAuthorizationService:
    async def can_access_prompt(self, user: User, prompt_id: PromptId) -> bool:
        prompt = await self.prompt_repo.find_by_id(prompt_id)

        # 所有者チェック
        if prompt.user_id == user.id:
            return True

        # 組織メンバーチェック
        if user.organization_id and prompt.is_shared_with_organization():
            return True

        # 公開プロンプトチェック
        if prompt.is_public():
            return True

        return False
```

## 🔍 LLM観測性・評価統合 (LangFuse)

### LangFuse統合概要

**LangFuse**は、AutoForgeNexusの全LLM実行を観測・分析・評価するコア観測ツールとして統合します。

#### 主要統合機能

- **LLMトレーシング**: 全プロンプト実行の完全トレース
- **評価メトリクス**: 17の革新機能の効果測定
- **プロンプト管理**: バージョニングと実験管理
- **コスト監視**: 100+プロバイダーのコスト最適化

### LangFuse実装詳細

#### Python SDK統合

```python
# LangFuse Client設定
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

# プロンプト実行トレーシング
@observe(name="prompt_optimization")
async def optimize_prompt_with_tracing(
    prompt: Prompt,
    strategy: OptimizationStrategy
) -> OptimizedPrompt:

    # LangFuseトレース開始
    with langfuse_context.get_current_trace() as trace:
        trace.update(
            name="AutoForgeNexus Prompt Optimization",
            input={"prompt_content": prompt.content, "strategy": strategy.value},
            tags=["optimization", strategy.value]
        )

        # 意図差分ビューワー実行
        intent_gap = await analyze_intent_gap(prompt)
        trace.span(
            name="intent_diffoscope",
            input={"prompt": prompt.content},
            output={"gap_score": intent_gap.score, "suggestions": intent_gap.suggestions}
        )

        # LLMプロバイダー実行
        for provider in ["openai", "anthropic", "gemini"]:
            with trace.span(name=f"llm_call_{provider}") as span:
                result = await call_llm_provider(provider, prompt)
                span.update(
                    input={"provider": provider, "prompt": prompt.content},
                    output={"response": result.content},
                    metadata={
                        "tokens_input": result.usage.input_tokens,
                        "tokens_output": result.usage.output_tokens,
                        "cost_usd": result.usage.cost
                    }
                )

        # 評価実行
        evaluation = await evaluate_prompt(prompt)
        trace.span(
            name="prompt_evaluation",
            input={"prompt": prompt.content},
            output={
                "accuracy_score": evaluation.accuracy,
                "hallucination_rate": evaluation.hallucination_rate,
                "style_consistency": evaluation.style_consistency
            }
        )

        return optimized_prompt

# プロンプトSLO監視
@observe(name="prompt_slo_monitoring")
async def monitor_prompt_slo(prompt_id: str, slo_config: SLOConfig):
    """プロンプトSLO違反の監視とアラート"""

    # 過去24時間のメトリクス取得
    metrics = await langfuse.get_traces(
        name="prompt_execution",
        tags=[f"prompt_id:{prompt_id}"],
        from_timestamp=datetime.now() - timedelta(hours=24)
    )

    # SLO違反チェック
    slo_violations = []

    accuracy_scores = [m.output.get('accuracy_score', 0) for m in metrics]
    avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0

    if avg_accuracy < slo_config.accuracy_threshold:
        slo_violations.append({
            "metric": "accuracy",
            "current": avg_accuracy,
            "threshold": slo_config.accuracy_threshold,
            "severity": "high"
        })

    # アラート送信
    if slo_violations:
        await send_slo_alert(prompt_id, slo_violations)

    return slo_violations
```

#### React/Next.js統合

```typescript
// LangFuse Frontend統合
import { LangfuseWeb } from "langfuse";

export const langfuseWeb = new LangfuseWeb({
  publicKey: process.env.NEXT_PUBLIC_LANGFUSE_PUBLIC_KEY!,
  baseUrl: process.env.NEXT_PUBLIC_LANGFUSE_HOST || "https://cloud.langfuse.com"
});

// プロンプト実行の可視化コンポーネント
export function PromptExecutionTrace({ traceId }: { traceId: string }) {
  const [trace, setTrace] = useState<Trace | null>(null);

  useEffect(() => {
    const fetchTrace = async () => {
      const traceData = await langfuseWeb.getTrace(traceId);
      setTrace(traceData);
    };
    fetchTrace();
  }, [traceId]);

  return (
    <div className="prompt-trace">
      <h3>実行トレース</h3>

      {/* 意図差分ビューワー結果 */}
      <div className="intent-gap-section">
        <h4>意図差分分析</h4>
        <div className="gap-score">
          スコア: {trace?.spans?.find(s => s.name === 'intent_diffoscope')?.output?.gap_score}
        </div>
      </div>

      {/* LLMプロバイダー比較 */}
      <div className="llm-providers">
        <h4>プロバイダー比較</h4>
        {trace?.spans?.filter(s => s.name.startsWith('llm_call_')).map(span => (
          <div key={span.id} className="provider-result">
            <span>{span.name.replace('llm_call_', '')}</span>
            <span>コスト: ${span.metadata?.cost_usd}</span>
            <span>トークン: {span.metadata?.tokens_output}</span>
          </div>
        ))}
      </div>

      {/* 評価結果 */}
      <div className="evaluation-results">
        <h4>品質評価</h4>
        <div className="metrics">
          <span>正確性: {trace?.spans?.find(s => s.name === 'prompt_evaluation')?.output?.accuracy_score}</span>
          <span>ハルシネーション: {trace?.spans?.find(s => s.name === 'prompt_evaluation')?.output?.hallucination_rate}</span>
        </div>
      </div>
    </div>
  );
}
```

### LangFuse評価パイプライン

#### 17革新機能の評価実装

```python
# AutoForgeNexus専用評価メトリクス
class AutoForgeNexusEvaluator:
    def __init__(self, langfuse_client: Langfuse):
        self.langfuse = langfuse_client

    @observe(name="innovative_features_evaluation")
    async def evaluate_innovative_features(self, prompt: Prompt, execution_result: dict) -> EvaluationResult:
        """17の革新機能の効果を評価"""

        evaluations = {}

        # 1. 意図差分ビューワー評価
        intent_diffoscope_score = await self._evaluate_intent_diffoscope(
            prompt, execution_result.get('intent_analysis')
        )
        evaluations['intent_diffoscope'] = intent_diffoscope_score

        # 2. プロンプトSLO評価
        slo_compliance = await self._evaluate_slo_compliance(
            prompt, execution_result.get('slo_metrics')
        )
        evaluations['prompt_slo'] = slo_compliance

        # 3. スタイル・ゲノム評価
        style_consistency = await self._evaluate_style_genome(
            prompt, execution_result.get('style_analysis')
        )
        evaluations['style_genome'] = style_consistency

        # LangFuseに評価結果送信
        await self.langfuse.score(
            name="autoforgenexus_innovative_features",
            value=sum(evaluations.values()) / len(evaluations),
            data_type="NUMERIC",
            config={
                "feature_scores": evaluations,
                "evaluation_timestamp": datetime.utcnow().isoformat()
            }
        )

        return EvaluationResult(
            overall_score=sum(evaluations.values()) / len(evaluations),
            feature_scores=evaluations,
            recommendations=await self._generate_improvement_recommendations(evaluations)
        )
```

### LangFuseデータセット管理

#### プロンプトテンプレートの管理

```python
# プロンプトデータセット管理
class PromptDatasetManager:
    def __init__(self, langfuse_client: Langfuse):
        self.langfuse = langfuse_client

    async def create_prompt_template(self, template: PromptTemplate) -> str:
        """LangFuseにプロンプトテンプレートを登録"""

        prompt_template = await self.langfuse.create_prompt(
            name=template.name,
            prompt=template.content,
            config={
                "template_type": template.type,
                "parameters": template.parameters,
                "optimization_strategy": template.optimization_strategy
            },
            labels=template.tags,
            version=template.version
        )

        return prompt_template.id

    async def create_evaluation_dataset(self, dataset_name: str, test_cases: List[TestCase]) -> str:
        """評価用データセットの作成"""

        dataset = await self.langfuse.create_dataset(name=dataset_name)

        for test_case in test_cases:
            await self.langfuse.create_dataset_item(
                dataset_id=dataset.id,
                input=test_case.input,
                expected_output=test_case.expected_output,
                metadata={
                    "category": test_case.category,
                    "difficulty": test_case.difficulty,
                    "features_tested": test_case.features_tested
                }
            )

        return dataset.id
```

### LangFuse設定・デプロイ

#### 環境変数設定

```env
# LangFuse 設定
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

# Self-hosted option
# LANGFUSE_HOST=http://localhost:3001
```

#### Docker Compose統合

```yaml
# LangFuse Self-hosted (オプション)
langfuse:
  image: langfuse/langfuse:latest
  environment:
    - DATABASE_URL=postgresql://langfuse:password@langfuse-db:5432/langfuse
    - NEXTAUTH_SECRET=your-secret
    - NEXTAUTH_URL=http://localhost:3001
    - LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES=true
  ports:
    - '3001:3000'
  depends_on:
    - langfuse-db

langfuse-db:
  image: postgres:16-alpine
  environment:
    - POSTGRES_USER=langfuse
    - POSTGRES_PASSWORD=password
    - POSTGRES_DB=langfuse
  volumes:
    - langfuse_data:/var/lib/postgresql/data
```

## 📈 監視・ロギング

### 分散トレーシング

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

tracer = trace.get_tracer(__name__)

class TracedPromptService:
    async def create_prompt(self, command: CreatePromptCommand) -> PromptId:
        with tracer.start_as_current_span("create_prompt") as span:
            span.set_attribute("user_id", str(command.user_id))
            span.set_attribute("content_length", len(command.content))

            try:
                prompt_id = await self._create_prompt_internal(command)
                span.set_attribute("prompt_id", str(prompt_id))
                return prompt_id
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR))
                raise
```

### メトリクス収集

```python
from prometheus_client import Counter, Histogram, Gauge

# カスタムメトリクス
prompt_created_total = Counter(
    'prompts_created_total',
    'Total number of prompts created',
    ['user_id', 'template_id']
)

evaluation_duration = Histogram(
    'evaluation_duration_seconds',
    'Time spent evaluating prompts',
    ['metric_type']
)

active_users = Gauge(
    'active_users',
    'Number of currently active users'
)
```

## 📊 詳細技術スタック

### バックエンド技術

| カテゴリ        | 技術           | バージョン | 用途                   |
| --------------- | -------------- | ---------- | ---------------------- |
| 言語            | Python         | 3.13       | 主要言語               |
| フレームワーク  | FastAPI        | 0.116.1    | Web API                |
| DB              | Turso (libSQL) | latest     | エッジデータ永続化     |
| ベクトルDB      | libSQL Vector  | latest     | 埋め込み検索           |
| キャッシュ      | Redis          | 7          | セッション・キャッシュ |
| ORM             | SQLAlchemy     | 2.0.32     | データマッピング       |
| 認証            | Clerk          | latest     | 認証・認可             |
| タスクキュー    | Celery         | 5.4.0      | 非同期処理             |
| LLM統合         | LangChain      | 0.3.27     | LLMチェーン            |
| ワークフロー    | LangGraph      | 0.6.7      | フロー管理             |
| LLMゲートウェイ | LiteLLM        | 1.76.1     | 統一API                |
| LLM観測         | LangFuse       | 2.0+       | トレーシング・評価     |

### フロントエンド技術

| カテゴリ       | 技術           | バージョン | 用途              |
| -------------- | -------------- | ---------- | ----------------- |
| フレームワーク | Next.js        | 15.5.0     | SSR/SSG           |
| UI ライブラリ  | React          | 19.0.0     | UIコンポーネント  |
| 言語           | TypeScript     | 5.x        | 型安全性          |
| スタイリング   | Tailwind CSS   | 4.0.0      | ユーティリティCSS |
| コンポーネント | shadcn/ui      | latest     | UIキット          |
| 状態管理       | Zustand        | 5.0.0      | グローバル状態    |
| データフェッチ | TanStack Query | 5.87.4     | サーバー状態      |
| エディタ       | Monaco Editor  | latest     | コードエディタ    |
| フロー図       | React Flow     | 11.11.0    | ワークフロー表示  |

### インフラストラクチャ

| カテゴリ                 | 技術               | 用途                      |
| ------------------------ | ------------------ | ------------------------- |
| データベース             | Turso              | Edge SQLite、ベクトル検索 |
| 認証プラットフォーム     | Clerk              | 認証・認可・組織管理      |
| エッジコンピューティング | Cloudflare Workers | Python実行環境            |
| CDN                      | Cloudflare Pages   | 静的ホスティング          |
| オブジェクトストレージ   | Cloudflare R2      | ファイル保存              |
| ベクトルDB               | libSQL Vector      | 埋め込み検索              |
| コンテナ                 | Docker             | 開発・本番環境            |
| オーケストレーション     | Docker Compose     | ローカル開発              |
| CI/CD                    | GitHub Actions     | 自動化パイプライン        |

### 観測・評価ツール

| カテゴリ         | 技術          | 用途               |
| ---------------- | ------------- | ------------------ |
| LLM観測          | LangFuse      | トレーシング・評価 |
| 品質評価         | DeepEval      | 単体テスト         |
| RAG評価          | Ragas         | RAG特化メトリクス  |
| リアルタイム分析 | TruLens       | 品質監視           |
| メトリクス       | Prometheus    | 時系列データ       |
| 可視化           | Grafana       | ダッシュボード     |
| トレーシング     | OpenTelemetry | 分散トレース       |

## 🎯 パフォーマンス要件

### レスポンスタイム目標

- **p50**: < 200ms
- **p95**: < 500ms
- **p99**: < 1000ms

### スループット目標

- **API**: 1000 req/sec
- **WebSocket**: 10000 同時接続
- **バッチ処理**: 100000 records/hour

### 可用性目標

- **SLA**: 99.9% (月間43分以内のダウンタイム)
- **RTO**: 2時間
- **RPO**: 1時間
- **MTTR**: 30分

---

**ドキュメント情報**

- 作成日: 2025-09-22
- バージョン: 1.0
- アーキテクチャパターン: DDD + Event-Driven + Clean Architecture
- 目標性能: 99.9% availability, <2s response time

🤖 Generated with AutoForgeNexus System
