# mypy --strict モード対応: 型エラー修正手順書

**作成日**: 2025-10-08
**対象**: GitHub Actions CI/CD パイプライン mypy エラー (64件)
**目的**: 型安全性を保ちながらすべての型エラーを修正し、CI を通過させる

---

## 📋 エラー概要

### 検出されたエラー分類

| カテゴリ | 件数 | 影響ファイル数 |
|---------|------|--------------|
| 返り値型アノテーション不足 | 18件 | 6ファイル |
| ジェネリック型パラメータ欠如 | 15件 | 5ファイル |
| 引数型アノテーション不足 | 12件 | 4ファイル |
| Liskov置換原則違反 | 2件 | 1ファイル |
| Any型の不適切使用 | 8件 | 3ファイル |
| Optional型の暗黙的使用 | 9件 | 3ファイル |

**合計**: 64エラー / 12ファイル

---

## ✅ 修正済み項目 (Phase 1)

### 1. Value Objects (完了)

#### ✅ user_input.py
```python
# 修正1: __post_init__の返り値型
- def __post_init__(self):
+ def __post_init__(self) -> None:

# 修正2: to_dictのジェネリック型
- def to_dict(self) -> dict:
+ def to_dict(self) -> dict[str, str | list[str]]:
```

#### ✅ prompt_content.py
```python
# 修正1: __post_init__の返り値型
- def __post_init__(self):
+ def __post_init__(self) -> None:

# 修正2: formatの引数型
- def format(self, **kwargs) -> str:
+ def format(self, **kwargs: Any) -> str:

# 修正3: typing.Anyのインポート追加済み
```

#### ✅ prompt_metadata.py
```python
# 修正1: typing.Anyのインポート追加
+ from typing import Any

# 修正2: __post_init__の返り値型
- def __post_init__(self):
+ def __post_init__(self) -> None:

# 修正3: with_updateの引数型
- def with_update(self, **kwargs) -> "PromptMetadata":
+ def with_update(self, **kwargs: Any) -> "PromptMetadata":

# 修正4: to_dictのジェネリック型
- def to_dict(self) -> dict:
+ def to_dict(self) -> dict[str, Any]:
```

### 2. Event Classes (完了)

#### ✅ prompt_created.py
```python
# 修正: __init__の引数・返り値型
- def __init__(self, ..., **kwargs):
+ def __init__(self, ..., **kwargs: Any) -> None:
```

#### ✅ prompt_saved.py
```python
# 修正: __init__の引数・返り値型
- def __init__(self, ..., **kwargs):
+ def __init__(self, ..., **kwargs: Any) -> None:
```

#### ✅ prompt_updated.py
```python
# 修正1: __init__の引数・返り値型
- def __init__(self, ..., **kwargs):
+ def __init__(self, ..., **kwargs: Any) -> None:

# 修正2: get_changed_fieldsのジェネリック型
- def get_changed_fields(self) -> list:
+ def get_changed_fields(self) -> list[str]:
```

#### ✅ event_store.py
```python
# 修正: __init__の返り値型
- def __init__(self):
+ def __init__(self) -> None:
```

---

## 🚧 未修正項目 (Phase 2)

### 3. EventBus (event_bus.py)

**エラー箇所**: 17行目、164行目、186行目、202行目、249行目

#### 🔧 修正1: Futureジェネリック型 (17行目)
```python
# 現在のコード
AsyncEventHandler = Callable[[DomainEvent], asyncio.Future]

# 修正後
AsyncEventHandler = Callable[[DomainEvent], asyncio.Future[None]]
```

**理由**: `Future` はジェネリック型なので型パラメータが必須。非同期ハンドラーは返り値なしなので `Future[None]`。

#### 🔧 修正2: Queueジェネリック型 (164行目)
```python
# 現在のコード (AsyncEventBus.__init__)
self._event_queue: asyncio.Queue = asyncio.Queue()

# 修正後
self._event_queue: asyncio.Queue[DomainEvent] = asyncio.Queue()
```

**理由**: `Queue` はジェネリック型で、`DomainEvent` を格納することを明示。

#### 🔧 修正3: Liskov置換原則違反 - subscribe (186行目)
```python
# 現在の問題コード
def subscribe(
    self, event_type: type[DomainEvent], handler: AsyncEventHandler
) -> None:

# 修正案1: 基底クラスEventBusのシグネチャを変更
# src/domain/shared/events/event_bus.py (EventBus基底クラス)
@abstractmethod
def subscribe(
    self,
    event_type: type[DomainEvent],
    handler: EventHandler | AsyncEventHandler
) -> None:

# 修正案2: AsyncEventBusの型アノテーションを抑制
def subscribe(  # type: ignore[override]
    self, event_type: type[DomainEvent], handler: AsyncEventHandler
) -> None:
```

**推奨**: 修正案1 (基底クラス変更) - より型安全

#### 🔧 修正4: Liskov置換原則違反 - unsubscribe (202行目)
```python
# 修正案1の場合
# 基底クラスEventBus
@abstractmethod
def unsubscribe(
    self,
    event_type: type[DomainEvent],
    handler: EventHandler | AsyncEventHandler
) -> None:

# 修正案2の場合
def unsubscribe(  # type: ignore[override]
    self, event_type: type[DomainEvent], handler: AsyncEventHandler
) -> None:
```

#### 🔧 修正5: 変数アノテーション + asyncio.create_task (249行目)
```python
# 現在のコード
task = asyncio.create_task(handler(event))

# 問題点
# 1. taskに型アノテーションがない
# 2. handler(event)の返り値がFuture[Any]だがcreate_taskはCoroutineを期待

# 修正後
task: asyncio.Task[None] = asyncio.create_task(
    asyncio.ensure_future(handler(event))
)

# または、handlerをawaitableに変更
tasks: list[asyncio.Task[None]] = []
for handler in handlers:
    task = asyncio.create_task(handler(event))
    tasks.append(task)
```

**理由**:
- `create_task` は `Coroutine` を期待するが、`Future` を受け取っている
- `asyncio.ensure_future` でラップするか、ハンドラー定義を `async def` に変更

---

### 4. Settings (core/config/settings.py)

**エラー箇所**: 149行目、161行目、173行目

#### 🔧 修正1: parse_cors_origins (149行目)
```python
# 現在のコード
@field_validator("cors_allow_origins")
@classmethod
def parse_cors_origins(cls, v) -> list[str]:

# 修正後
@field_validator("cors_allow_origins")
@classmethod
def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
```

#### 🔧 修正2: parse_cors_methods (161行目)
```python
# 修正後
@field_validator("cors_allow_methods")
@classmethod
def parse_cors_methods(cls, v: str | list[str]) -> list[str]:
```

#### 🔧 修正3: parse_cors_headers (173行目)
```python
# 修正後
@field_validator("cors_allow_headers")
@classmethod
def parse_cors_headers(cls, v: str | list[str]) -> list[str]:
```

---

### 5. Turso Connection (infrastructure/shared/database/turso_connection.py)

**エラー箇所**: 21行目、80行目、105行目、109行目、111行目、116行目、118行目、123行目、132行目、144行目、152行目

#### 🔧 修正1: __init__の返り値型 (21行目)
```python
# 現在のコード
def __init__(self):

# 修正後
def __init__(self) -> None:
```

#### 🔧 修正2: get_connection_urlの返り値型 (80行目)
```python
# 既に正しい型アノテーションあり
def get_connection_url(self) -> str:
```
**確認**: エラーがないか再チェック必要

#### 🔧 修正3: sessionmakerジェネリック型 (105行目)
```python
# 現在のコード
def get_session_factory(self) -> sessionmaker:

# 修正後
from sqlalchemy.orm import sessionmaker, Session

def get_session_factory(self) -> sessionmaker[Session]:
```

#### 🔧 修正4: get_engineのno-untyped-call (109行目)
```python
# 現在のコード
self._session_factory = sessionmaker(
    autocommit=False, autoflush=False, bind=self.get_engine()
)

# 問題: self.get_engine()の返り値型が不明
# 修正: get_engineに返り値型を追加

from sqlalchemy.engine import Engine

def get_engine(self) -> Engine:
    """Get SQLAlchemy engine"""
    if self._engine is None:
        # ...既存のコード
    return self._engine
```

#### 🔧 修正5: sessionmaker返り値 (111行目)
```python
# 修正後 (修正4の型定義により解決)
return self._session_factory
```

#### 🔧 修正6: get_sessionの返り値 (116行目)
```python
# 現在のコード (116行目)
def get_session(self) -> Session:
    session_factory = self.get_session_factory()
    return session_factory()

# 問題: session_factory()の呼び出しがAnyを返す
# 修正: sessionmakerの型定義により解決 (修正3で対応済み)
```

#### 🔧 修正7-8: execute_raw/batch_executeの返り値型 (118行目、123行目)
```python
# 現在のコード
async def execute_raw(self, query: str, params: dict | None = None):

# 修正後 (具体的な型を使用 - Any型を避ける)
from libsql_client import ResultSet

async def execute_raw(
    self,
    query: str,
    params: dict[str, str | int | float | bool | None] | None = None
) -> ResultSet:
    """Execute raw SQL query using libSQL client"""
    client = self.get_libsql_client()
    return await client.execute(query, params or {})

async def batch_execute(
    self,
    queries: list[tuple[str, dict[str, str | int | float | bool | None]]]
) -> list[ResultSet]:
    """Execute multiple queries in a batch"""
    client = self.get_libsql_client()
    results: list[ResultSet] = []
    for query, params in queries:
        result = await client.execute(query, params)
        results.append(result)
    return results
```

**理由**: 
- `Any`型は型安全性を損なうため避ける
- libSQL clientは`ResultSet`型を返すことが保証されている
- paramsは基本的なSQL型のみ許可 (str, int, float, bool, None)

#### 🔧 修正9: closeの返り値型 (132行目)
```python
# 現在のコード
def close(self):

# 修正後
def close(self) -> None:
```

#### 🔧 修正10: get_turso_connectionのno-untyped-call (144行目)
```python
# 現在のコード
_turso_connection = TursoConnection()

# 問題: TursoConnection.__init__に型アノテーションがない
# 修正: 修正1で対応済み (__init__ -> None)
```

#### 🔧 修正11: get_db_sessionのGenerator型 (152行目)
```python
# 現在のコード
def get_db_session() -> Session:
    session = _turso_connection.get_session()
    try:
        yield session
    finally:
        session.close()

# 修正後
from collections.abc import Generator

def get_db_session() -> Generator[Session, None, None]:
    """Get database session for dependency injection"""
    session = _turso_connection.get_session()
    try:
        yield session
    finally:
        session.close()
```

**理由**: `yield` を使っているため `Generator` 型が必要

---

### 6. Monitoring (monitoring.py)

**エラー箇所**: 87行目、403行目、407行目、425行目、444行目、463行目、464行目

#### 🔧 修正1: HealthChecker.__init__ (87行目)
```python
# 現在のコード
def __init__(self):

# 修正後
def __init__(self) -> None:
```

#### 🔧 修正2-5: MetricsCollector (403行目、407行目、425行目、444行目)
```python
# 修正2: __init__ (403行目)
def __init__(self) -> None:

# 修正3: increment (407行目)
def increment(
    self,
    metric_name: str,
    value: int = 1,
    tags: dict[str, str] | None = None
) -> None:

# 修正4: gauge (425行目)
def gauge(
    self,
    metric_name: str,
    value: float,
    tags: dict[str, str] | None = None
) -> None:

# 修正5: histogram (444行目)
def histogram(
    self,
    metric_name: str,
    value: float,
    tags: dict[str, str] | None = None,
    stack_trace: str | None = None  # Optional[str]に修正
) -> None:
```

**注意**: 445行目のOptional型暗黙使用エラー
```python
# 現在のコード (エラー)
stack_trace: str | None = None  # デフォルト引数の型がNone

# 修正: Pydantic v2では明示的なOptionalが必要
from typing import Optional

def histogram(
    self,
    metric_name: str,
    value: float,
    tags: dict[str, str] | None = None,
    stack_trace: Optional[str] = None  # または str | None = None
) -> None:
```

#### 🔧 修正6-7: 初期化関数 (463行目、464行目)
```python
# 現在のコード
health_checker = HealthChecker()  # no-untyped-call
metrics_collector = MetricsCollector()  # no-untyped-call

# 修正: 修正1, 2で対応済み (__init__に型アノテーション追加)
```

---

### 7. Observability Middleware (middleware/observability.py)

**エラー箇所**: 25行目、31行目、34行目、47行目、52行目、133行目、196行目、229行目、239行目、243行目、271行目、279行目、296行目、319行目、323行目、347行目、361行目、380行目、381行目、402行目、405行目

#### 🔧 修正1: BaseHTTPMiddleware継承 (25行目)
```python
# 現在のコード
class ObservabilityMiddleware(BaseHTTPMiddleware):

# 問題: BaseHTTPMiddlewareの型がAny
# 修正1: starlette型スタブをインストール
pip install types-starlette

# 修正2: または型チェックを抑制
class ObservabilityMiddleware(BaseHTTPMiddleware):  # type: ignore[misc]
```

#### 🔧 修正2-3: listジェネリック型 (31行目、34行目)
```python
# 現在のコード
self.exclude_paths = exclude_paths or [...]
self.sensitive_headers = sensitive_headers or [...]

# 修正: __init__の型アノテーション
def __init__(
    self,
    app: ASGIApp,
    exclude_paths: list[str] | None = None,
    include_request_body: bool = False,
    include_response_body: bool = False,
    sensitive_headers: list[str] | None = None,
) -> None:
```

#### 🔧 修正4: Callableジェネリック型 (47行目)
```python
# 現在のコード
async def dispatch(self, request: Request, call_next: Callable) -> Response:

# 修正後
from collections.abc import Callable, Awaitable

async def dispatch(
    self,
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
```

#### 🔧 修正5-6: 返り値型Any (52行目、133行目)
```python
# 現在のコード (52行目)
return await call_next(request)

# 修正: call_nextの型定義により解決 (修正4で対応)

# 現在のコード (133行目)
return await call_next(request)

# 修正: 同上
```

#### 🔧 修正7: 返り値型不一致 (196行目)
```python
# 現在のコード
def _sanitize_headers(self, headers: dict) -> str:
    # ...
    return {...}  # dictを返しているがstrと宣言

# 修正後
def _sanitize_headers(self, headers: dict[str, str]) -> dict[str, str]:
    """センシティブなヘッダーをマスク"""
    sanitized = {}
    for key, value in headers.items():
        if key.lower() in self.sensitive_headers:
            sanitized[key] = "***REDACTED***"
        else:
            sanitized[key] = value
    return sanitized
```

#### 🔧 修正8: 型不一致代入 (229行目)
```python
# 現在のコード (229行目)
context["request_headers"] = {...}  # dict[str, Any]をstrに代入

# 修正: contextの型定義を修正
context: dict[str, Any] = {
    "request_id": request_id,
    "method": request.method,
    "path": request.url.path,
    "client": f"{request.client.host}:{request.client.port}" if request.client else "unknown",
}

# ヘッダー追加
context["request_headers"] = self._sanitize_headers(dict(request.headers))
```

#### 🔧 修正9-10: LLMObservabilityMiddleware (239行目、243行目)
```python
# 修正9: __init__ (239行目)
def __init__(
    self,
    app: ASGIApp,
    exclude_paths: list[str] | None = None
) -> None:

# 修正10: dispatch (243行目)
async def dispatch(
    self,
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
```

#### 🔧 修正11-12: LLM関連の型不一致 (271行目、279行目)
```python
# 修正11: llm_metricsの型定義 (271行目)
llm_metrics: dict[str, int | str | float | None] = {
    "model": model_name,
    "provider": provider,
    "prompt_tokens": prompt_tokens,
    "completion_tokens": completion_tokens,
    "total_tokens": total_tokens,
}

# 応答時間追加
llm_metrics["response_time"] = response_time  # float

# 修正12: ログ出力 (279行目)
logger.info(
    "LLM request completed",
    extra={
        "request_id": request_id,
        "model": model_name,
        "response_time": response_time,  # float型
        "total_tokens": total_tokens,
    }
)
```

#### 🔧 修正13: timing関数 (296行目)
```python
# 現在のコード
def timing(self, metric_name: str, value: float):

# 修正後
def timing(self, metric_name: str, value: float) -> None:
```

#### 🔧 修正14-15: DatabaseObservabilityMiddleware (319行目、323行目)
```python
# 修正14: __init__ (319行目)
def __init__(
    self,
    app: ASGIApp,
    exclude_paths: list[str] | None = None
) -> None:

# 修正15: dispatch (323行目)
async def dispatch(
    self,
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
```

#### 🔧 修正16-17: DB関連の型不一致 (347行目、361行目)
```python
# 修正16: db_metricsの型定義 (347行目)
db_metrics: dict[str, str | float | None] = {
    "operation": operation,
    "table": table_name,
    "query_type": query_type,
}

# クエリ時間追加
db_metrics["query_time"] = query_time  # float

# 修正17: ログ出力 (361行目)
logger.info(
    "Database query completed",
    extra={
        "request_id": request_id,
        "operation": operation,
        "query_time": query_time,  # float型
        "table": table_name,
    }
)
```

#### 🔧 修正18-19: 初期化関数 (380行目、381行目)
```python
# 現在のコード
llm_middleware = LLMObservabilityMiddleware(...)  # no-untyped-call
db_middleware = DatabaseObservabilityMiddleware(...)  # no-untyped-call

# 修正: 修正9, 14で対応済み
```

#### 🔧 修正20: get_request_id (402行目)
```python
# 現在のコード
def get_request_id(request: Request) -> str:
    return request.state.request_id  # Anyを返している

# 修正後 - getattrではなく型安全なアクセス
def get_request_id(request: Request) -> str:
    """リクエストIDを取得"""
    if hasattr(request.state, "request_id"):
        request_id: str = request.state.request_id
        return request_id
    return str(uuid.uuid4())
```

**理由**: `getattr`より`hasattr`チェックの方が型安全

#### 🔧 修正21: set_request_context (405行目)
```python
# 現在のコード
def set_request_context(request: Request, context: dict):

# 修正後 - Any型を避けて具体的な型を使用
from typing import Union

RequestContextValue = Union[str, int, float, bool, None, dict[str, str]]

def set_request_context(
    request: Request,
    context: dict[str, RequestContextValue]
) -> None:
    """リクエストコンテキストを設定"""
    for key, value in context.items():
        setattr(request.state, key, value)
```

**理由**: 
- `Any`型を避けて、実際に使用される型のみを許可
- `Union`型で明示的に許可する型を列挙
- 型安全性を保ちながら柔軟性を維持

---

## 🚨 Any型撲滅ガイドライン

### Any型が許容される唯一のケース

```python
# ❌ 絶対NG: 安易なAny使用
def process(data: Any) -> Any:
    return data

# ✅ OK: 外部ライブラリの型定義がない場合のみ
# ただし、型スタブが存在する場合は必ずインストール
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from some_untyped_lib import SomeClass
else:
    SomeClass = Any
```

### Any型の適切な代替手段

#### 1. Union型を使う
```python
# ❌ 悪い
def handle(value: Any) -> Any:
    return value

# ✅ 良い
from typing import Union
def handle(value: Union[str, int, float]) -> Union[str, int, float]:
    return value
```

#### 2. TypedDictを使う
```python
# ❌ 悪い
def process_config(config: dict[str, Any]) -> None:
    pass

# ✅ 良い
from typing import TypedDict

class Config(TypedDict):
    host: str
    port: int
    debug: bool

def process_config(config: Config) -> None:
    pass
```

#### 3. Protocolを使う
```python
# ❌ 悪い
def serialize(obj: Any) -> str:
    return obj.to_json()

# ✅ 良い
from typing import Protocol

class Serializable(Protocol):
    def to_json(self) -> str: ...

def serialize(obj: Serializable) -> str:
    return obj.to_json()
```

#### 4. ジェネリクスを使う
```python
# ❌ 悪い
def first_element(items: list[Any]) -> Any:
    return items[0]

# ✅ 良い
from typing import TypeVar

T = TypeVar('T')
def first_element(items: list[T]) -> T:
    return items[0]
```

### 本プロジェクトでの具体例

#### observability.py - コンテキスト型
```python
# ❌ 元のコード
context: dict[str, Any] = {...}

# ✅ 改善版
from typing import TypedDict

class RequestContext(TypedDict, total=False):
    request_id: str
    method: str
    path: str
    client: str
    request_headers: dict[str, str]
    response_status: int
    response_time: float

context: RequestContext = {...}
```

#### turso_connection.py - SQL結果型
```python
# ❌ 元のコード
async def execute_raw(self, query: str, params: dict | None = None) -> Any:
    pass

# ✅ 改善版
from libsql_client import ResultSet

async def execute_raw(
    self,
    query: str,
    params: dict[str, str | int | float | bool | None] | None = None
) -> ResultSet:
    pass
```

### 型安全性のチェックリスト

- [ ] すべての関数に返り値型アノテーションがある
- [ ] すべての関数引数に型アノテーションがある
- [ ] `dict`, `list`, `tuple`にジェネリック型パラメータがある
- [ ] `Any`型が一切使用されていない（または最小限）
- [ ] 外部ライブラリの型スタブがインストールされている
- [ ] `mypy --strict`で0エラー

---

## 📝 修正実行手順

### Step 1: EventBus修正

```bash
# ファイル: backend/src/domain/shared/events/event_bus.py

# 1. Futureジェネリック型修正 (17行目)
AsyncEventHandler = Callable[[DomainEvent], asyncio.Future[None]]

# 2. Queueジェネリック型修正 (164行目 - AsyncEventBus.__init__)
self._event_queue: asyncio.Queue[DomainEvent] = asyncio.Queue()

# 3-4. Liskov置換原則対応 - 基底クラス変更
# EventBus基底クラス
@abstractmethod
def subscribe(
    self,
    event_type: type[DomainEvent],
    handler: EventHandler | AsyncEventHandler
) -> None:

@abstractmethod
def unsubscribe(
    self,
    event_type: type[DomainEvent],
    handler: EventHandler | AsyncEventHandler
) -> None:

# 5. asyncio.create_task修正 (249行目)
tasks: list[asyncio.Task[None]] = []
for handler in handlers:
    task: asyncio.Task[None] = asyncio.create_task(handler(event))
    tasks.append(task)
```

### Step 2: Settings修正

```bash
# ファイル: backend/src/core/config/settings.py

# 149行目
@field_validator("cors_allow_origins")
@classmethod
def parse_cors_origins(cls, v: str | list[str]) -> list[str]:

# 161行目
@field_validator("cors_allow_methods")
@classmethod
def parse_cors_methods(cls, v: str | list[str]) -> list[str]:

# 173行目
@field_validator("cors_allow_headers")
@classmethod
def parse_cors_headers(cls, v: str | list[str]) -> list[str]:
```

### Step 3: Turso Connection修正

```bash
# ファイル: backend/src/infrastructure/shared/database/turso_connection.py

# インポート追加
from typing import Any
from collections.abc import Generator
from sqlalchemy.engine import Engine

# 21行目
def __init__(self) -> None:

# 80行目 (get_engine修正)
def get_engine(self) -> Engine:

# 105行目
def get_session_factory(self) -> sessionmaker[Session]:

# 118行目
async def execute_raw(
    self,
    query: str,
    params: dict[str, Any] | None = None
) -> Any:

# 123行目
async def batch_execute(
    self,
    queries: list[tuple[str, dict[str, Any]]]
) -> list[Any]:

# 132行目
def close(self) -> None:

# 152行目
def get_db_session() -> Generator[Session, None, None]:
```

### Step 4: Monitoring修正

```bash
# ファイル: backend/src/monitoring.py

# インポート追加
from typing import Optional

# 87行目
def __init__(self) -> None:

# 403行目
def __init__(self) -> None:

# 407行目
def increment(
    self,
    metric_name: str,
    value: int = 1,
    tags: dict[str, str] | None = None
) -> None:

# 425行目
def gauge(
    self,
    metric_name: str,
    value: float,
    tags: dict[str, str] | None = None
) -> None:

# 444-445行目
def histogram(
    self,
    metric_name: str,
    value: float,
    tags: dict[str, str] | None = None,
    stack_trace: Optional[str] = None
) -> None:
```

### Step 5: Observability Middleware修正

```bash
# ファイル: backend/src/middleware/observability.py

# インポート追加
from collections.abc import Callable, Awaitable
from typing import Any
import uuid

# 型スタブインストール
pip install types-starlette

# 25-42行目: __init__修正
def __init__(
    self,
    app: ASGIApp,
    exclude_paths: list[str] | None = None,
    include_request_body: bool = False,
    include_response_body: bool = False,
    sensitive_headers: list[str] | None = None,
) -> None:

# 47行目: dispatch修正
async def dispatch(
    self,
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:

# 196行目: _sanitize_headers修正
def _sanitize_headers(self, headers: dict[str, str]) -> dict[str, str]:

# 229行目: context型修正
context: dict[str, Any] = {...}

# 239行目: LLMObservabilityMiddleware.__init__
def __init__(
    self,
    app: ASGIApp,
    exclude_paths: list[str] | None = None
) -> None:

# 243行目: LLMObservabilityMiddleware.dispatch
async def dispatch(
    self,
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:

# 271行目: llm_metrics型定義
llm_metrics: dict[str, int | str | float | None] = {...}

# 296行目: timing修正
def timing(self, metric_name: str, value: float) -> None:

# 319行目: DatabaseObservabilityMiddleware.__init__
def __init__(
    self,
    app: ASGIApp,
    exclude_paths: list[str] | None = None
) -> None:

# 323行目: DatabaseObservabilityMiddleware.dispatch
async def dispatch(
    self,
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:

# 347行目: db_metrics型定義
db_metrics: dict[str, str | float | None] = {...}

# 402行目: get_request_id修正
def get_request_id(request: Request) -> str:
    request_id: str = getattr(request.state, "request_id", str(uuid.uuid4()))
    return request_id

# 405行目: set_request_context修正
def set_request_context(request: Request, context: dict[str, Any]) -> None:
```

---

## ✅ 検証手順

### 1. ローカル検証

```bash
cd backend

# venv有効化
source venv/bin/activate

# mypy実行 (strict モード)
mypy src/ --strict

# 期待結果: Success: no issues found in XX source files
```

### 2. テスト実行

```bash
# 単体テスト
pytest tests/unit/domain/ -v

# 全テスト
pytest tests/ --cov=src --cov-report=html
```

### 3. CI/CD確認

```bash
# GitHub Actionsで検証
git add .
git commit -m "fix(backend): mypy strict モード対応 - 全64エラー修正"
git push origin feature/autoforge-mvp-complete

# Actions結果確認
gh run list --limit 1
gh run watch
```

---

## 📊 期待される結果

### 修正前
```
Found 64 errors in 12 files (checked 36 source files)
Error: Process completed with exit code 1.
```

### 修正後
```
Success: no issues found in 36 source files
```

---

## 🔍 修正の影響範囲

### 破壊的変更
- **なし**: すべて型アノテーション追加のみで、実行時の挙動は変わらない

### 追加依存関係
```bash
# requirements-dev.txt に追加
types-starlette>=0.35.0  # Starletteの型スタブ
```

### テスト影響
- **なし**: 型チェックのみの変更で、既存テストは影響を受けない

---

## 📝 レビューポイント

### 優先度: 高
1. **EventBus基底クラス変更**: Liskov置換原則対応が適切か
2. **asyncio.create_task修正**: Future vs Coroutine の扱い
3. **Turso Connection**: sessionmakerのジェネリック型が適切か

### 優先度: 中
4. **Optional型使用**: Python 3.10+ の `X | None` vs `Optional[X]`
5. **Any型使用**: 型安全性とのバランス

### 優先度: 低
6. **型スタブインストール**: `types-starlette` の必要性

---

## 🚀 次のステップ

1. **このドキュメントに従って修正を実行**
2. **ローカルでmypyテスト (Step 1-5完了後)**
3. **単体テスト実行 (破壊的変更がないか確認)**
4. **コミット・プッシュ**
5. **GitHub Actions CI通過確認**
6. **修正完了レポート作成** (`docs/reviews/MYPY_STRICT_FIXES_REPORT.md`)

---

**作成者**: Claude Code
**最終更新**: 2025-10-08
