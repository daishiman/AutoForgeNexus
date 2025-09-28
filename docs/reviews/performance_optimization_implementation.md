# パフォーマンス最適化実装ガイド

**実装対象**: AutoForgeNexus FastAPIバックエンド
**目標**: P95 < 200ms, WebSocket 10,000+接続, メモリ効率化

## 🔧 Critical Priority 実装

### 1. データベース接続プール実装

**問題**: 現在のsettings.pyで設定は定義されているが、実際の接続プール実装が不完全

**実装例**:

```python
# src/infrastructure/shared/database/connection.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import QueuePool
from ...core.config.settings import Settings

settings = Settings()

# 高パフォーマンス接続プール設定
DATABASE_CONFIG = {
    "pool_size": 20,                    # 基本接続数
    "max_overflow": 15,                 # 追加接続許可
    "pool_timeout": 10,                 # 接続取得タイムアウト
    "pool_recycle": 3600,              # 1時間で接続再生成
    "pool_pre_ping": True,             # 接続健全性チェック
}

# 非同期エンジン作成
async_engine = create_async_engine(
    settings.get_database_url(),
    **DATABASE_CONFIG,
    echo=settings.database_echo,
)

# セッションファクトリ
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """データベースセッション取得（依存性注入用）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# 接続プール監視機能
async def get_pool_status() -> dict:
    """接続プール状態取得"""
    pool = async_engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid()
    }
```

### 2. Redis 接続プール最適化

**実装例**:

```python
# src/infrastructure/shared/cache/redis_client.py
import redis.asyncio as redis
from typing import Optional, Any
import json
import pickle
from ...core.config.settings import Settings

settings = Settings()

class OptimizedRedisClient:
    def __init__(self):
        self.pool = None
        self.client = None

    async def initialize(self):
        """Redis接続プール初期化"""
        self.pool = redis.ConnectionPool.from_url(
            settings.get_redis_url(),
            max_connections=50,          # 高い同時接続数
            retry_on_timeout=True,
            decode_responses=False,       # バイナリデータ対応
            socket_keepalive=True,
            socket_keepalive_options={},
        )
        self.client = redis.Redis(connection_pool=self.pool)

    async def get_with_fallback(self, key: str, fallback_func=None) -> Optional[Any]:
        """キャッシュ取得（フォールバック機能付き）"""
        try:
            cached = await self.client.get(key)
            if cached:
                return pickle.loads(cached)
        except Exception as e:
            # Redis障害時のフォールバック
            if fallback_func:
                return await fallback_func()
        return None

    async def set_with_compression(self, key: str, value: Any, ttl: int):
        """圧縮キャッシュ設定"""
        try:
            serialized = pickle.dumps(value)
            # 大きなデータは圧縮
            if len(serialized) > 1024:
                import gzip
                serialized = gzip.compress(serialized)
                key += ":gz"

            await self.client.setex(key, ttl, serialized)
        except Exception as e:
            # キャッシュ失敗は非致命的
            pass

    async def get_pool_stats(self) -> dict:
        """接続プール統計"""
        info = await self.client.info()
        return {
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
        }

# グローバルインスタンス
redis_client = OptimizedRedisClient()
```

### 3. LLM レスポンスキャッシュ実装

**実装例**:

```python
# src/application/llm_integration/services/cached_llm_service.py
import hashlib
from typing import Optional, Dict, Any
from ...infrastructure.shared.cache.redis_client import redis_client

class CachedLLMService:
    def __init__(self):
        self.cache_ttls = {
            "prompt_response": 86400,    # 24時間
            "evaluation_result": 43200,  # 12時間
            "system_prompt": 604800,     # 1週間
        }

    def _generate_cache_key(self, prompt: str, model: str, params: Dict) -> str:
        """キャッシュキー生成（ハッシュベース）"""
        content = f"{prompt}:{model}:{sorted(params.items())}"
        return f"llm:{hashlib.md5(content.encode()).hexdigest()}"

    async def get_cached_response(self, prompt: str, model: str, params: Dict) -> Optional[str]:
        """キャッシュからLLMレスポンス取得"""
        cache_key = self._generate_cache_key(prompt, model, params)
        return await redis_client.get_with_fallback(cache_key)

    async def cache_response(self, prompt: str, model: str, params: Dict, response: str):
        """LLMレスポンスをキャッシュ"""
        cache_key = self._generate_cache_key(prompt, model, params)
        ttl = self.cache_ttls.get("prompt_response", 3600)
        await redis_client.set_with_compression(cache_key, response, ttl)

    async def get_cache_stats(self) -> Dict[str, int]:
        """キャッシュ統計取得"""
        stats = await redis_client.get_pool_stats()
        hit_rate = 0
        if stats["keyspace_hits"] + stats["keyspace_misses"] > 0:
            hit_rate = stats["keyspace_hits"] / (stats["keyspace_hits"] + stats["keyspace_misses"])

        return {
            "hit_rate_percent": round(hit_rate * 100, 2),
            "total_hits": stats["keyspace_hits"],
            "total_misses": stats["keyspace_misses"],
        }
```

## 🚀 High Priority 実装

### 4. WebSocket 接続管理システム

**実装例**:

```python
# src/presentation/websocket/connection_manager.py
import asyncio
import json
import logging
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict

logger = logging.getLogger(__name__)

class OptimizedConnectionManager:
    def __init__(self, max_connections: int = 15000):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)
        self.max_connections = max_connections
        self.connection_count = 0
        self.broadcast_queue = asyncio.Queue(maxsize=1000)

        # ブロードキャストワーカー開始
        asyncio.create_task(self._broadcast_worker())

    async def connect(self, websocket: WebSocket, client_id: str, user_id: Optional[str] = None):
        """WebSocket接続確立"""
        if self.connection_count >= self.max_connections:
            await websocket.close(code=1013, reason="Server overloaded")
            return False

        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_count += 1

        if user_id:
            self.user_connections[user_id].add(client_id)

        logger.info(f"Client {client_id} connected. Total: {self.connection_count}")
        return True

    async def disconnect(self, client_id: str, user_id: Optional[str] = None):
        """WebSocket接続切断"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            self.connection_count -= 1

        if user_id and client_id in self.user_connections[user_id]:
            self.user_connections[user_id].remove(client_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def send_to_user(self, user_id: str, message: dict):
        """特定ユーザーにメッセージ送信"""
        if user_id not in self.user_connections:
            return

        message_str = json.dumps(message)
        tasks = []

        for client_id in self.user_connections[user_id]:
            if client_id in self.active_connections:
                websocket = self.active_connections[client_id]
                tasks.append(self._safe_send(websocket, message_str, client_id))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def broadcast(self, message: dict):
        """全接続にブロードキャスト（非同期キュー使用）"""
        await self.broadcast_queue.put(message)

    async def _broadcast_worker(self):
        """ブロードキャスト処理ワーカー"""
        while True:
            try:
                message = await self.broadcast_queue.get()
                message_str = json.dumps(message)

                # バッチ処理で効率的にブロードキャスト
                batch_size = 100
                connection_items = list(self.active_connections.items())

                for i in range(0, len(connection_items), batch_size):
                    batch = connection_items[i:i + batch_size]
                    tasks = [
                        self._safe_send(websocket, message_str, client_id)
                        for client_id, websocket in batch
                    ]
                    await asyncio.gather(*tasks, return_exceptions=True)

                    # CPU負荷軽減のための短い休憩
                    if len(connection_items) > 1000:
                        await asyncio.sleep(0.001)

            except Exception as e:
                logger.error(f"Broadcast worker error: {e}")

    async def _safe_send(self, websocket: WebSocket, message: str, client_id: str):
        """安全なメッセージ送信（エラーハンドリング付き）"""
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            await self.disconnect(client_id)
        except Exception as e:
            logger.warning(f"Failed to send to {client_id}: {e}")
            await self.disconnect(client_id)

    def get_stats(self) -> dict:
        """接続統計取得"""
        return {
            "total_connections": self.connection_count,
            "unique_users": len(self.user_connections),
            "max_connections": self.max_connections,
            "utilization_percent": round((self.connection_count / self.max_connections) * 100, 2),
            "queue_size": self.broadcast_queue.qsize(),
        }

# グローバルインスタンス
connection_manager = OptimizedConnectionManager()
```

### 5. メモリ効率的なデータ処理

**実装例**:

```python
# src/application/shared/services/memory_optimizer.py
import gc
import asyncio
import psutil
import logging
from typing import AsyncGenerator, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MemoryStats:
    used_mb: float
    available_mb: float
    percent: float
    process_mb: float

class MemoryOptimizer:
    def __init__(self, memory_threshold: float = 85.0):
        self.memory_threshold = memory_threshold
        self.cleanup_interval = 300  # 5分間隔
        asyncio.create_task(self._periodic_cleanup())

    async def stream_large_data(self, data_source) -> AsyncGenerator[Any, None]:
        """大容量データのストリーミング処理"""
        chunk_size = 1000

        async for chunk in self._chunk_data(data_source, chunk_size):
            yield chunk

            # メモリ使用量チェック
            if await self._should_cleanup():
                await self._force_cleanup()

    async def _chunk_data(self, data_source, chunk_size: int):
        """データを指定サイズでチャンク分割"""
        chunk = []
        async for item in data_source:
            chunk.append(item)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []

        if chunk:
            yield chunk

    async def _should_cleanup(self) -> bool:
        """クリーンアップが必要かチェック"""
        memory_stats = await self.get_memory_stats()
        return memory_stats.percent > self.memory_threshold

    async def _force_cleanup(self):
        """強制メモリクリーンアップ"""
        logger.info("Performing memory cleanup")

        # Python GC実行
        collected = gc.collect()

        # プロセス固有のクリーンアップ
        await self._cleanup_application_cache()

        logger.info(f"Memory cleanup completed. Collected {collected} objects")

    async def _cleanup_application_cache(self):
        """アプリケーション固有キャッシュクリーンアップ"""
        # LLMレスポンスキャッシュのクリーンアップ
        # イベントストアの古いデータ削除
        # 一時的なファイルの削除
        pass

    async def _periodic_cleanup(self):
        """定期的なメモリクリーンアップ"""
        while True:
            await asyncio.sleep(self.cleanup_interval)
            if await self._should_cleanup():
                await self._force_cleanup()

    async def get_memory_stats(self) -> MemoryStats:
        """メモリ使用状況取得"""
        memory = psutil.virtual_memory()
        process = psutil.Process()

        return MemoryStats(
            used_mb=memory.used / 1024 / 1024,
            available_mb=memory.available / 1024 / 1024,
            percent=memory.percent,
            process_mb=process.memory_info().rss / 1024 / 1024
        )

# グローバルインスタンス
memory_optimizer = MemoryOptimizer()
```

## 📊 パフォーマンス監視強化

### 6. 詳細メトリクス収集

**実装例**:

```python
# src/monitoring/performance_monitor.py
import time
import asyncio
from typing import Dict, List
from dataclasses import dataclass, asdict
from collections import deque, defaultdict

@dataclass
class RequestMetrics:
    endpoint: str
    method: str
    status_code: int
    duration_ms: float
    timestamp: float
    user_id: str = None

class PerformanceMonitor:
    def __init__(self, max_metrics: int = 10000):
        self.request_metrics: deque = deque(maxlen=max_metrics)
        self.endpoint_stats: Dict[str, List[float]] = defaultdict(list)
        self.max_stats_per_endpoint = 1000

    def record_request(self, metrics: RequestMetrics):
        """リクエストメトリクス記録"""
        self.request_metrics.append(metrics)

        # エンドポイント別統計更新
        endpoint_key = f"{metrics.method} {metrics.endpoint}"
        self.endpoint_stats[endpoint_key].append(metrics.duration_ms)

        # 古いデータの削除
        if len(self.endpoint_stats[endpoint_key]) > self.max_stats_per_endpoint:
            self.endpoint_stats[endpoint_key] = self.endpoint_stats[endpoint_key][-self.max_stats_per_endpoint:]

    def get_performance_summary(self) -> Dict:
        """パフォーマンス統計サマリー"""
        summary = {}

        for endpoint, durations in self.endpoint_stats.items():
            if durations:
                sorted_durations = sorted(durations)
                count = len(sorted_durations)

                summary[endpoint] = {
                    "count": count,
                    "avg_ms": sum(sorted_durations) / count,
                    "p50_ms": sorted_durations[int(count * 0.5)],
                    "p90_ms": sorted_durations[int(count * 0.9)],
                    "p95_ms": sorted_durations[int(count * 0.95)],
                    "p99_ms": sorted_durations[int(count * 0.99)],
                    "max_ms": max(sorted_durations),
                    "min_ms": min(sorted_durations),
                }

        return summary

    def get_slow_requests(self, threshold_ms: float = 200) -> List[Dict]:
        """閾値を超える遅いリクエスト取得"""
        slow_requests = [
            asdict(metric) for metric in self.request_metrics
            if metric.duration_ms > threshold_ms
        ]
        return sorted(slow_requests, key=lambda x: x["duration_ms"], reverse=True)[:50]

# グローバルインスタンス
performance_monitor = PerformanceMonitor()
```

## 🧪 パフォーマンステスト実装

### 7. 負荷テストスイート

**実装例**:

```python
# tests/performance/test_load.py
import asyncio
import pytest
import aiohttp
import time
from typing import List, Dict

class LoadTestRunner:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict] = []

    async def run_concurrent_requests(self, endpoint: str, concurrent_users: int, requests_per_user: int):
        """並行リクエスト実行"""
        tasks = []

        for user_id in range(concurrent_users):
            task = asyncio.create_task(
                self._user_session(endpoint, requests_per_user, user_id)
            )
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def _user_session(self, endpoint: str, request_count: int, user_id: int):
        """個別ユーザーセッション"""
        async with aiohttp.ClientSession() as session:
            for i in range(request_count):
                start_time = time.time()

                try:
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        await response.text()
                        duration = time.time() - start_time

                        self.results.append({
                            "user_id": user_id,
                            "request_id": i,
                            "status_code": response.status,
                            "duration_ms": duration * 1000,
                            "timestamp": start_time
                        })

                except Exception as e:
                    duration = time.time() - start_time
                    self.results.append({
                        "user_id": user_id,
                        "request_id": i,
                        "status_code": 0,
                        "duration_ms": duration * 1000,
                        "error": str(e),
                        "timestamp": start_time
                    })

    def analyze_results(self) -> Dict:
        """負荷テスト結果分析"""
        if not self.results:
            return {}

        durations = [r["duration_ms"] for r in self.results if r.get("status_code", 0) == 200]
        errors = [r for r in self.results if r.get("status_code", 0) != 200]

        if durations:
            durations.sort()
            count = len(durations)

            return {
                "total_requests": len(self.results),
                "successful_requests": len(durations),
                "error_requests": len(errors),
                "success_rate": len(durations) / len(self.results) * 100,
                "avg_response_time_ms": sum(durations) / count,
                "p50_ms": durations[int(count * 0.5)],
                "p90_ms": durations[int(count * 0.9)],
                "p95_ms": durations[int(count * 0.95)],
                "p99_ms": durations[int(count * 0.99)],
                "max_ms": max(durations),
                "min_ms": min(durations),
            }

        return {"error": "No successful requests"}

@pytest.mark.asyncio
async def test_api_load_performance():
    """API負荷パフォーマンステスト"""
    runner = LoadTestRunner()

    # 100並行ユーザー、各10リクエスト
    await runner.run_concurrent_requests("/", 100, 10)

    results = runner.analyze_results()

    # パフォーマンス要件検証
    assert results["success_rate"] > 95, f"Success rate too low: {results['success_rate']}%"
    assert results["p95_ms"] < 200, f"P95 response time too high: {results['p95_ms']}ms"
    assert results["avg_response_time_ms"] < 100, f"Average response time too high: {results['avg_response_time_ms']}ms"
```

## 📈 実装優先順位と効果予測

| 優先度 | 実装項目 | 予想効果 | 実装時間 |
|-------|---------|---------|----------|
| 1 | データベース接続プール | P95: 300ms → 150ms | 2日 |
| 1 | Redis接続プール最適化 | キャッシュヒット率: 30% → 80% | 1日 |
| 2 | LLMレスポンスキャッシュ | LLM待機時間: 90%削減 | 3日 |
| 2 | WebSocket接続管理 | 同時接続: 500 → 10,000+ | 5日 |
| 3 | メモリ最適化 | メモリ使用量: 40%削減 | 3日 |
| 3 | パフォーマンス監視 | 問題検出時間: 90%短縮 | 2日 |

**総合予測効果**: P95レスポンス時間 60%改善、メモリ使用量40%削減、同時接続数20倍向上

---

**実装開始予定**: 2025-01-20
**完了目標**: 2025-02-15
**責任者**: バックエンド開発チーム