"""
イベントストアのテスト

イベントの永続化とリトリーブのテスト
"""

from src.domain.prompt.events import PromptCreatedEvent
from src.domain.shared.events import DomainEvent, InMemoryEventStore


class TestEventStore:
    """イベントストアのテストケース"""

    def test_append_event(self):
        """イベントの追加"""
        # Arrange
        store = InMemoryEventStore()
        event = PromptCreatedEvent(
            prompt_id="prompt_001",
            user_id="user_123",
            title="テストプロンプト",
            content="テスト内容",
        )

        # Act
        store.append(event)

        # Assert
        events = store.get_events("prompt_001")
        assert len(events) == 1
        assert events[0].prompt_id == "prompt_001"

    def test_get_events_by_aggregate_id(self):
        """集約IDによるイベント取得"""
        # Arrange
        store = InMemoryEventStore()
        event1 = PromptCreatedEvent(
            prompt_id="prompt_001",
            user_id="user_123",
            title="プロンプト1",
            content="内容1",
        )
        event2 = PromptCreatedEvent(
            prompt_id="prompt_002",
            user_id="user_123",
            title="プロンプト2",
            content="内容2",
        )

        # Act
        store.append(event1)
        store.append(event2)

        # Assert
        events1 = store.get_events("prompt_001")
        events2 = store.get_events("prompt_002")
        assert len(events1) == 1
        assert len(events2) == 1
        assert events1[0].prompt_id == "prompt_001"
        assert events2[0].prompt_id == "prompt_002"

    def test_get_events_after_version(self):
        """特定バージョン以降のイベント取得"""
        # Arrange
        store = InMemoryEventStore()

        # 複数のイベントを追加
        for i in range(5):
            event = DomainEvent(
                aggregate_id="prompt_001", event_type=f"Event{i}", version=i + 1
            )
            store.append(event)

        # Act
        events = store.get_events_after("prompt_001", version=3)

        # Assert
        assert len(events) == 2
        assert events[0].version == 4
        assert events[1].version == 5

    def test_get_all_events(self):
        """全イベントの取得"""
        # Arrange
        store = InMemoryEventStore()
        event1 = DomainEvent(aggregate_id="agg_1", event_type="Type1")
        event2 = DomainEvent(aggregate_id="agg_2", event_type="Type2")

        # Act
        store.append(event1)
        store.append(event2)
        all_events = store.get_all_events()

        # Assert
        assert len(all_events) == 2
        assert any(e.aggregate_id == "agg_1" for e in all_events)
        assert any(e.aggregate_id == "agg_2" for e in all_events)

    def test_get_events_by_type(self):
        """イベントタイプによる取得"""
        # Arrange
        store = InMemoryEventStore()
        created_event = PromptCreatedEvent(
            prompt_id="prompt_001", user_id="user_123", title="テスト", content="内容"
        )
        generic_event = DomainEvent(aggregate_id="prompt_001", event_type="OtherEvent")

        # Act
        store.append(created_event)
        store.append(generic_event)
        prompt_created_events = store.get_events_by_type("PromptCreated")

        # Assert
        assert len(prompt_created_events) == 1
        assert prompt_created_events[0].event_type == "PromptCreated"
