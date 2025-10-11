"""
プロンプト保存イベント

プロンプトが永続化された際に発行されるイベント
"""

from datetime import datetime
from typing import Any

from src.domain.shared.events.domain_event import DomainEvent


class PromptSavedEvent(DomainEvent):
    """
    プロンプト保存イベント

    プロンプトがデータストアに保存された際に発行される

    Attributes:
        prompt_id: プロンプトの一意識別子
        saved_by: 保存を実行したユーザーID
        saved_version: 保存されたバージョン番号
        metadata: 保存に関するメタデータ（保存場所など）
    """

    def __init__(
        self,
        prompt_id: str,
        saved_by: str,
        saved_version: int,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """初期化"""
        self.prompt_id = prompt_id
        self.saved_by = saved_by
        self.saved_version = saved_version
        self.metadata = metadata or {}

        # kwargsからaggregate_idを除外してから親クラスに渡す
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop("aggregate_id", None)  # 既にprompt_idから設定されているため除外

        # 親クラスの初期化
        super().__init__(
            aggregate_id=prompt_id, event_type="PromptSaved", **kwargs_copy
        )

    def to_dict(self) -> dict[str, Any]:
        """イベントを辞書形式に変換"""
        base_dict = super().to_dict()
        base_dict["payload"] = {
            "prompt_id": self.prompt_id,
            "saved_by": self.saved_by,
            "saved_version": self.saved_version,
            "metadata": self.metadata,
        }
        return base_dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptSavedEvent":
        """辞書からイベントを復元"""
        payload = data.get("payload", {})
        occurred_at = data.get("occurred_at")

        if isinstance(occurred_at, str):
            occurred_at = datetime.fromisoformat(occurred_at)

        return cls(
            event_id=data["event_id"],
            prompt_id=payload["prompt_id"],
            saved_by=payload["saved_by"],
            saved_version=payload["saved_version"],
            metadata=payload.get("metadata", {}),
            occurred_at=occurred_at,
            version=data.get("version", 1),
        )
