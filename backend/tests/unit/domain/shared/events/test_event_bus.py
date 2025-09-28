"""
イベントバスのテスト
"""

import pytest
import asyncio
from typing import List

from src.domain.shared.events import InMemoryEventBus, AsyncEventBus, DomainEvent
from src.domain.prompt.events import PromptCreatedEvent, PromptSavedEvent


class TestInMemoryEventBus:
    """InMemoryEventBusのテスト"""

    def test_publish_and_subscribe(self):
        """イベントの発行と購読が正しく動作すること"""
        # Arrange
        bus = InMemoryEventBus()
        received_events: List[DomainEvent] = []

        def handler(event: DomainEvent):
            received_events.append(event)

        bus.subscribe(PromptCreatedEvent, handler)

        # Act
        event = PromptCreatedEvent(
            aggregate_id="prompt-123",
            prompt_id="prompt-123",
            user_id="user-456",
            title="Test Prompt",
            content="This is a test prompt",
        )
        bus.publish(event)

        # Assert
        assert len(received_events) == 1
        assert received_events[0] == event

    def test_multiple_handlers(self):
        """複数のハンドラーが登録できること"""
        # Arrange
        bus = InMemoryEventBus()
        handler1_events: List[DomainEvent] = []
        handler2_events: List[DomainEvent] = []

        def handler1(event: DomainEvent):
            handler1_events.append(event)

        def handler2(event: DomainEvent):
            handler2_events.append(event)

        bus.subscribe(PromptCreatedEvent, handler1)
        bus.subscribe(PromptCreatedEvent, handler2)

        # Act
        event = PromptCreatedEvent(
            aggregate_id="prompt-123",
            prompt_id="prompt-123",
            user_id="user-456",
            title="Test Prompt",
            content="This is a test prompt",
        )
        bus.publish(event)

        # Assert
        assert len(handler1_events) == 1
        assert len(handler2_events) == 1
        assert handler1_events[0] == event
        assert handler2_events[0] == event

    def test_different_event_types(self):
        """異なるイベントタイプごとにハンドラーが動作すること"""
        # Arrange
        bus = InMemoryEventBus()
        created_events: List[PromptCreatedEvent] = []
        saved_events: List[PromptSavedEvent] = []

        def created_handler(event: PromptCreatedEvent):
            created_events.append(event)

        def saved_handler(event: PromptSavedEvent):
            saved_events.append(event)

        bus.subscribe(PromptCreatedEvent, created_handler)
        bus.subscribe(PromptSavedEvent, saved_handler)

        # Act
        created_event = PromptCreatedEvent(
            aggregate_id="prompt-123",
            prompt_id="prompt-123",
            user_id="user-456",
            title="Test Prompt",
            content="This is a test prompt",
        )
        saved_event = PromptSavedEvent(
            aggregate_id="prompt-123",
            prompt_id="prompt-123",
            saved_by="user-456",
            saved_version=1,
        )

        bus.publish(created_event)
        bus.publish(saved_event)

        # Assert
        assert len(created_events) == 1
        assert len(saved_events) == 1
        assert created_events[0] == created_event
        assert saved_events[0] == saved_event

    def test_unsubscribe(self):
        """ハンドラーの購読解除が正しく動作すること"""
        # Arrange
        bus = InMemoryEventBus()
        received_events: List[DomainEvent] = []

        def handler(event: DomainEvent):
            received_events.append(event)

        bus.subscribe(PromptCreatedEvent, handler)

        # Act
        event1 = PromptCreatedEvent(
            aggregate_id="prompt-123",
            prompt_id="prompt-123",
            user_id="user-456",
            title="Test Prompt 1",
            content="This is a test prompt",
        )
        bus.publish(event1)

        bus.unsubscribe(PromptCreatedEvent, handler)

        event2 = PromptCreatedEvent(
            aggregate_id="prompt-456",
            prompt_id="prompt-456",
            user_id="user-456",
            title="Test Prompt 2",
            content="This is another test prompt",
        )
        bus.publish(event2)

        # Assert
        assert len(received_events) == 1
        assert received_events[0] == event1

    def test_base_class_subscription(self):
        """ベースクラスへの購読が動作すること"""
        # Arrange
        bus = InMemoryEventBus()
        all_events: List[DomainEvent] = []

        def handler(event: DomainEvent):
            all_events.append(event)

        # DomainEventベースクラスに購読
        bus.subscribe(DomainEvent, handler)

        # Act
        created_event = PromptCreatedEvent(
            aggregate_id="prompt-123",
            prompt_id="prompt-123",
            user_id="user-456",
            title="Test Prompt",
            content="This is a test prompt",
        )
        saved_event = PromptSavedEvent(
            aggregate_id="prompt-123",
            prompt_id="prompt-123",
            saved_by="user-456",
            saved_version=1,
        )

        bus.publish(created_event)
        bus.publish(saved_event)

        # Assert
        assert len(all_events) == 2
        assert created_event in all_events
        assert saved_event in all_events

    def test_event_history(self):
        """イベント履歴が記録されること"""
        # Arrange
        bus = InMemoryEventBus(_enable_history=True)

        # Act
        event1 = PromptCreatedEvent(
            aggregate_id="prompt-123",
            prompt_id="prompt-123",
            user_id="user-456",
            title="Test Prompt",
            content="This is a test prompt",
        )
        event2 = PromptSavedEvent(
            aggregate_id="prompt-123",
            prompt_id="prompt-123",
            saved_by="user-456",
            saved_version=1,
        )

        bus.publish(event1)
        bus.publish(event2)

        # Assert
        history = bus.get_event_history()
        assert len(history) == 2
        assert history[0] == event1
        assert history[1] == event2

    def test_handler_error_handling(self):
        """ハンドラーでエラーが発生しても他のハンドラーが実行されること"""
        # Arrange
        bus = InMemoryEventBus()
        handler1_called = False
        handler3_called = False

        def handler1(event: DomainEvent):
            nonlocal handler1_called
            handler1_called = True

        def handler2(event: DomainEvent):
            raise ValueError("Handler error")

        def handler3(event: DomainEvent):
            nonlocal handler3_called
            handler3_called = True

        bus.subscribe(PromptCreatedEvent, handler1)
        bus.subscribe(PromptCreatedEvent, handler2)
        bus.subscribe(PromptCreatedEvent, handler3)

        # Act
        event = PromptCreatedEvent(
            aggregate_id="prompt-123",
            prompt_id="prompt-123",
            user_id="user-456",
            title="Test Prompt",
            content="This is a test prompt",
        )
        bus.publish(event)

        # Assert
        assert handler1_called
        assert handler3_called


class TestAsyncEventBus:
    """AsyncEventBusのテスト"""

    @pytest.mark.asyncio
    async def test_async_publish_and_subscribe(self):
        """非同期イベントの発行と購読が正しく動作すること"""
        # Arrange
        bus = AsyncEventBus()
        received_events: List[DomainEvent] = []

        async def handler(event: DomainEvent):
            received_events.append(event)
            await asyncio.sleep(0.01)  # 非同期処理のシミュレーション

        bus.subscribe(PromptCreatedEvent, handler)

        # イベント処理ループを開始
        processing_task = asyncio.create_task(bus.start())

        # Act
        event = PromptCreatedEvent(
            aggregate_id="prompt-123",
            prompt_id="prompt-123",
            user_id="user-456",
            title="Test Prompt",
            content="This is a test prompt",
        )
        await bus.publish_async(event)

        # イベント処理を待つ
        await asyncio.sleep(0.1)

        # Clean up
        await bus.stop()
        processing_task.cancel()
        try:
            await processing_task
        except asyncio.CancelledError:
            pass

        # Assert
        assert len(received_events) == 1
        assert received_events[0] == event

    @pytest.mark.asyncio
    async def test_parallel_handler_execution(self):
        """複数のハンドラーが並列実行されること"""
        # Arrange
        bus = AsyncEventBus()
        handler_order: List[str] = []

        async def slow_handler(event: DomainEvent):
            await asyncio.sleep(0.05)
            handler_order.append("slow")

        async def fast_handler(event: DomainEvent):
            await asyncio.sleep(0.01)
            handler_order.append("fast")

        bus.subscribe(PromptCreatedEvent, slow_handler)
        bus.subscribe(PromptCreatedEvent, fast_handler)

        # イベント処理ループを開始
        processing_task = asyncio.create_task(bus.start())

        # Act
        event = PromptCreatedEvent(
            aggregate_id="prompt-123",
            prompt_id="prompt-123",
            user_id="user-456",
            title="Test Prompt",
            content="This is a test prompt",
        )
        await bus.publish_async(event)

        # イベント処理を待つ
        await asyncio.sleep(0.1)

        # Clean up
        await bus.stop()
        processing_task.cancel()
        try:
            await processing_task
        except asyncio.CancelledError:
            pass

        # Assert
        # 並列実行なので、速いハンドラーが先に完了するはず
        assert handler_order == ["fast", "slow"]
