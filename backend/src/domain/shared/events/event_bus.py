"""
イベントバスの実装

イベントの発行と購読を管理する基本的なイベントバス実装。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Type
from dataclasses import dataclass, field
import asyncio
import logging

from src.domain.shared.events.domain_event import DomainEvent

logger = logging.getLogger(__name__)


# イベントハンドラーの型定義
EventHandler = Callable[[DomainEvent], None]
AsyncEventHandler = Callable[[DomainEvent], asyncio.Future]


class EventBus(ABC):
    """
    イベントバスの抽象基底クラス

    イベントの発行と購読を管理する。
    """

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """
        イベントを発行する

        Args:
            event: 発行するドメインイベント
        """
        pass

    @abstractmethod
    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """
        イベントタイプに対してハンドラーを登録する

        Args:
            event_type: 購読するイベントタイプ
            handler: イベントハンドラー
        """
        pass

    @abstractmethod
    def unsubscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """
        イベントタイプからハンドラーを削除する

        Args:
            event_type: 購読解除するイベントタイプ
            handler: 削除するイベントハンドラー
        """
        pass


@dataclass
class InMemoryEventBus(EventBus):
    """
    メモリ内でイベントを管理するイベントバス実装

    開発・テスト用の簡易実装。
    """

    _handlers: Dict[Type[DomainEvent], List[EventHandler]] = field(default_factory=dict)
    _event_history: List[DomainEvent] = field(default_factory=list)
    _enable_history: bool = field(default=False)

    def publish(self, event: DomainEvent) -> None:
        """
        イベントを発行し、登録されたハンドラーを実行する

        Args:
            event: 発行するドメインイベント
        """
        event_type = type(event)

        # イベント履歴を記録
        if self._enable_history:
            self._event_history.append(event)

        # 該当するハンドラーを取得
        handlers = self._handlers.get(event_type, [])

        # ベースクラスのハンドラーも取得
        for base_class in event_type.__bases__:
            if issubclass(base_class, DomainEvent):
                handlers.extend(self._handlers.get(base_class, []))

        # ハンドラーを実行
        for handler in handlers:
            try:
                logger.debug(
                    f"Executing handler {handler.__name__} for event {event.event_type}"
                )
                handler(event)
            except Exception as e:
                logger.error(
                    f"Error executing handler {handler.__name__}: {e}", exc_info=True
                )
                # エラーが発生してもその他のハンドラーは実行を継続

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """
        イベントタイプに対してハンドラーを登録する

        Args:
            event_type: 購読するイベントタイプ
            handler: イベントハンドラー
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logger.debug(
                f"Handler {handler.__name__} subscribed to {event_type.__name__}"
            )

    def unsubscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """
        イベントタイプからハンドラーを削除する

        Args:
            event_type: 購読解除するイベントタイプ
            handler: 削除するイベントハンドラー
        """
        if event_type in self._handlers:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                logger.debug(
                    f"Handler {handler.__name__} unsubscribed from {event_type.__name__}"
                )

    def clear_handlers(self) -> None:
        """すべてのハンドラーをクリアする（テスト用）"""
        self._handlers.clear()
        logger.debug("All handlers cleared")

    def get_event_history(self) -> List[DomainEvent]:
        """イベント履歴を取得する（テスト用）"""
        return self._event_history.copy()

    def clear_history(self) -> None:
        """イベント履歴をクリアする（テスト用）"""
        self._event_history.clear()


class AsyncEventBus(EventBus):
    """
    非同期イベントバスの実装

    非同期ハンドラーをサポートするイベントバス。
    """

    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[AsyncEventHandler]] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    async def publish_async(self, event: DomainEvent) -> None:
        """
        イベントを非同期で発行する

        Args:
            event: 発行するドメインイベント
        """
        await self._event_queue.put(event)

    def publish(self, event: DomainEvent) -> None:
        """
        イベントを発行する（同期インターフェース）

        Args:
            event: 発行するドメインイベント
        """
        asyncio.create_task(self.publish_async(event))

    def subscribe(
        self, event_type: Type[DomainEvent], handler: AsyncEventHandler
    ) -> None:
        """
        イベントタイプに対してハンドラーを登録する

        Args:
            event_type: 購読するイベントタイプ
            handler: 非同期イベントハンドラー
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)

    def unsubscribe(
        self, event_type: Type[DomainEvent], handler: AsyncEventHandler
    ) -> None:
        """
        イベントタイプからハンドラーを削除する

        Args:
            event_type: 購読解除するイベントタイプ
            handler: 削除する非同期イベントハンドラー
        """
        if event_type in self._handlers:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)

    async def start(self) -> None:
        """イベント処理ループを開始する"""
        self._running = True
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._process_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)

    async def stop(self) -> None:
        """イベント処理ループを停止する"""
        self._running = False

    async def _process_event(self, event: DomainEvent) -> None:
        """
        イベントを処理する

        Args:
            event: 処理するドメインイベント
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        # ベースクラスのハンドラーも取得
        for base_class in event_type.__bases__:
            if issubclass(base_class, DomainEvent):
                handlers.extend(self._handlers.get(base_class, []))

        # ハンドラーを並列実行
        tasks = []
        for handler in handlers:
            task = asyncio.create_task(handler(event))
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
