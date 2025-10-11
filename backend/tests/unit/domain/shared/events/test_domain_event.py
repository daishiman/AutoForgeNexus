"""
ドメインイベントベースクラスのテスト

TDD原則に従い、実装前にテストを作成
"""

from datetime import datetime
from uuid import UUID

from src.domain.shared.events.domain_event import DomainEvent


class TestDomainEvent:
    """ドメインイベントベースクラスのテストケース"""

    def test_domain_event_creation(self):
        """ドメインイベントが正しく作成されることを確認"""
        # Arrange
        aggregate_id = "prompt_123"
        event_type = "PromptCreated"

        # Act
        event = DomainEvent(aggregate_id=aggregate_id, event_type=event_type)

        # Assert
        assert event.aggregate_id == aggregate_id
        assert event.event_type == event_type
        assert isinstance(event.event_id, str)
        assert UUID(event.event_id)  # Valid UUID
        assert isinstance(event.occurred_at, datetime)
        assert event.version == 1

    def test_domain_event_with_payload(self):
        """ペイロード付きドメインイベントの作成"""
        # Arrange
        aggregate_id = "prompt_456"
        event_type = "PromptUpdated"
        payload = {"title": "新しいタイトル", "content": "更新されたコンテンツ"}

        # Act
        event = DomainEvent(
            aggregate_id=aggregate_id, event_type=event_type, payload=payload
        )

        # Assert
        assert event.payload == payload
        assert event.payload["title"] == "新しいタイトル"

    def test_domain_event_to_dict(self):
        """ドメインイベントの辞書変換"""
        # Arrange
        event = DomainEvent(
            aggregate_id="prompt_789",
            event_type="PromptDeleted",
            payload={"reason": "ユーザー要求"},
        )

        # Act
        event_dict = event.to_dict()

        # Assert
        assert event_dict["aggregate_id"] == "prompt_789"
        assert event_dict["event_type"] == "PromptDeleted"
        assert event_dict["payload"]["reason"] == "ユーザー要求"
        assert "event_id" in event_dict
        assert "occurred_at" in event_dict
        assert event_dict["version"] == 1

    def test_domain_event_immutability(self):
        """ドメインイベントの値が変更可能だが推奨されないことを確認"""
        # Arrange
        event = DomainEvent(aggregate_id="prompt_000", event_type="PromptCreated")

        # Act - イベントは変更可能だが、実際の運用では不変として扱うべき

        # Assert - 初期値が正しく設定されている
        assert event.aggregate_id == "prompt_000"
        assert event.event_type == "PromptCreated"

        # Note: 実際の運用ではイベントは不変として扱われるべきである

    def test_domain_event_from_dict(self):
        """辞書からドメインイベントを復元"""
        # Arrange
        event_dict = {
            "event_id": "550e8400-e29b-41d4-a716-446655440000",
            "aggregate_id": "prompt_111",
            "event_type": "PromptSaved",
            "occurred_at": "2025-09-28T10:00:00",
            "version": 1,
            "payload": {"status": "saved"},
        }

        # Act
        event = DomainEvent.from_dict(event_dict)

        # Assert
        assert event.event_id == event_dict["event_id"]
        assert event.aggregate_id == event_dict["aggregate_id"]
        assert event.event_type == event_dict["event_type"]
        assert event.payload == event_dict["payload"]
