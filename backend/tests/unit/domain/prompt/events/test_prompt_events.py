"""
プロンプト関連ドメインイベントのテスト

TDD原則に従い、実装前にテストを作成
"""
from datetime import datetime
from src.domain.prompt.events import (
    PromptCreatedEvent,
    PromptSavedEvent,
    PromptUpdatedEvent,
)


class TestPromptCreatedEvent:
    """プロンプト作成イベントのテストケース"""

    def test_prompt_created_event_creation(self):
        """プロンプト作成イベントが正しく生成される"""
        # Arrange
        prompt_id = "prompt_001"
        user_id = "user_123"
        title = "プロンプトタイトル"
        content = "これはプロンプトの内容です"
        tags = ["AI", "自動化"]

        # Act
        event = PromptCreatedEvent(
            prompt_id=prompt_id,
            user_id=user_id,
            title=title,
            content=content,
            tags=tags,
        )

        # Assert
        assert event.aggregate_id == prompt_id
        assert event.event_type == "PromptCreated"
        assert event.prompt_id == prompt_id
        assert event.user_id == user_id
        assert event.title == title
        assert event.content == content
        assert event.tags == tags
        assert isinstance(event.occurred_at, datetime)

    def test_prompt_created_event_to_dict(self):
        """プロンプト作成イベントの辞書変換"""
        # Arrange
        event = PromptCreatedEvent(
            prompt_id="prompt_002",
            user_id="user_456",
            title="テストプロンプト",
            content="テスト内容",
        )

        # Act
        event_dict = event.to_dict()

        # Assert
        assert event_dict["event_type"] == "PromptCreated"
        assert event_dict["payload"]["prompt_id"] == "prompt_002"
        assert event_dict["payload"]["user_id"] == "user_456"
        assert event_dict["payload"]["title"] == "テストプロンプト"


class TestPromptSavedEvent:
    """プロンプト保存イベントのテストケース"""

    def test_prompt_saved_event_creation(self):
        """プロンプト保存イベントが正しく生成される"""
        # Arrange
        prompt_id = "prompt_003"
        saved_by = "user_789"
        saved_version = 2

        # Act
        event = PromptSavedEvent(
            prompt_id=prompt_id, saved_by=saved_by, saved_version=saved_version
        )

        # Assert
        assert event.aggregate_id == prompt_id
        assert event.event_type == "PromptSaved"
        assert event.prompt_id == prompt_id
        assert event.saved_by == saved_by
        assert event.saved_version == saved_version

    def test_prompt_saved_event_with_metadata(self):
        """メタデータ付きプロンプト保存イベント"""
        # Arrange
        metadata = {"storage_location": "s3://bucket/prompt.json", "size_bytes": 1024}

        # Act
        event = PromptSavedEvent(
            prompt_id="prompt_004",
            saved_by="user_000",
            saved_version=1,
            metadata=metadata,
        )

        # Assert
        assert event.metadata == metadata
        assert event.metadata["storage_location"] == "s3://bucket/prompt.json"


class TestPromptUpdatedEvent:
    """プロンプト更新イベントのテストケース"""

    def test_prompt_updated_event_creation(self):
        """プロンプト更新イベントが正しく生成される"""
        # Arrange
        prompt_id = "prompt_005"
        updated_by = "user_111"
        changes = {
            "title": {"old": "古いタイトル", "new": "新しいタイトル"},
            "content": {"old": "古い内容", "new": "新しい内容"},
        }

        # Act
        event = PromptUpdatedEvent(
            prompt_id=prompt_id, updated_by=updated_by, changes=changes
        )

        # Assert
        assert event.aggregate_id == prompt_id
        assert event.event_type == "PromptUpdated"
        assert event.prompt_id == prompt_id
        assert event.updated_by == updated_by
        assert event.changes == changes
        assert event.changes["title"]["new"] == "新しいタイトル"

    def test_prompt_updated_event_from_dict(self):
        """辞書からプロンプト更新イベントを復元"""
        # Arrange
        event_dict = {
            "event_id": "550e8400-e29b-41d4-a716-446655440000",
            "aggregate_id": "prompt_006",
            "event_type": "PromptUpdated",
            "occurred_at": "2025-09-28T10:00:00",
            "version": 1,
            "payload": {
                "prompt_id": "prompt_006",
                "updated_by": "user_222",
                "changes": {"title": {"old": "A", "new": "B"}},
                "previous_version": 3,
                "new_version": 4,
            },
        }

        # Act
        event = PromptUpdatedEvent.from_dict(event_dict)

        # Assert
        assert event.prompt_id == "prompt_006"
        assert event.updated_by == "user_222"
        assert event.previous_version == 3
        assert event.new_version == 4
