"""
プロンプト作成イベント

プロンプトが新規作成された際に発行されるイベント
"""

from datetime import datetime
from typing import Any

from domain.shared.events.domain_event import DomainEvent


class PromptCreatedEvent(DomainEvent):
    """
    プロンプト作成イベント

    新しいプロンプトが作成された際に発行される

    Attributes:
        prompt_id: プロンプトの一意識別子
        user_id: 作成者のユーザーID
        title: プロンプトのタイトル
        content: プロンプトの内容
        tags: プロンプトに関連付けられたタグ
        metadata: その他のメタデータ
    """

    def __init__(
        self,
        prompt_id: str,
        user_id: str,
        title: str,
        content: str,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """初期化"""
        self.prompt_id = prompt_id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.tags = tags or []
        self.metadata = metadata or {}

        # kwargsからaggregate_idを除外してから親クラスに渡す
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop("aggregate_id", None)  # 既にprompt_idから設定されているため除外

        # 親クラスの初期化
        super().__init__(
            aggregate_id=prompt_id, event_type="PromptCreated", **kwargs_copy
        )

    def to_dict(self) -> dict[str, Any]:
        """イベントを辞書形式に変換"""
        base_dict = super().to_dict()
        base_dict["payload"] = {
            "prompt_id": self.prompt_id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "metadata": self.metadata,
        }
        return base_dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptCreatedEvent":
        """辞書からイベントを復元"""
        payload = data.get("payload", {})
        occurred_at = data.get("occurred_at")

        if isinstance(occurred_at, str):
            occurred_at = datetime.fromisoformat(occurred_at)

        return cls(
            event_id=data["event_id"],
            prompt_id=payload["prompt_id"],
            user_id=payload["user_id"],
            title=payload["title"],
            content=payload["content"],
            tags=payload.get("tags", []),
            metadata=payload.get("metadata", {}),
            occurred_at=occurred_at,
            version=data.get("version", 1),
        )
