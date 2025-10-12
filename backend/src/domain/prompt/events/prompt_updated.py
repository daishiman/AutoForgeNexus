"""
プロンプト更新イベント

プロンプトが更新された際に発行されるイベント
"""

from datetime import datetime
from typing import Any

from src.domain.shared.events.domain_event import DomainEvent


class PromptUpdatedEvent(DomainEvent):
    """
    プロンプト更新イベント

    既存のプロンプトが更新された際に発行される

    Attributes:
        prompt_id: プロンプトの一意識別子
        updated_by: 更新を実行したユーザーID
        changes: 変更内容のマップ（フィールド名: {"old": 旧値, "new": 新値}）
        previous_version: 更新前のバージョン番号
        new_version: 更新後のバージョン番号
    """

    def __init__(
        self,
        prompt_id: str,
        updated_by: str,
        changes: dict[str, dict[str, Any]],
        previous_version: int | None = None,
        new_version: int | None = None,
        **kwargs: Any,
    ) -> None:
        """初期化"""
        self.prompt_id = prompt_id
        self.updated_by = updated_by
        self.changes = changes
        self.previous_version = previous_version
        self.new_version = new_version

        # kwargsからaggregate_idを除外してから親クラスに渡す
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop("aggregate_id", None)  # 既にprompt_idから設定されているため除外

        # 親クラスの初期化
        super().__init__(
            aggregate_id=prompt_id, event_type="PromptUpdated", **kwargs_copy
        )

    def to_dict(self) -> dict[str, Any]:
        """イベントを辞書形式に変換"""
        base_dict = super().to_dict()
        base_dict["payload"] = {
            "prompt_id": self.prompt_id,
            "updated_by": self.updated_by,
            "changes": self.changes,
            "previous_version": self.previous_version,
            "new_version": self.new_version,
        }
        return base_dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptUpdatedEvent":
        """辞書からイベントを復元"""
        payload = data.get("payload", {})
        occurred_at = data.get("occurred_at")

        if isinstance(occurred_at, str):
            occurred_at = datetime.fromisoformat(occurred_at)

        return cls(
            event_id=data["event_id"],
            prompt_id=payload["prompt_id"],
            updated_by=payload["updated_by"],
            changes=payload["changes"],
            previous_version=payload.get("previous_version"),
            new_version=payload.get("new_version"),
            occurred_at=occurred_at,
            version=data.get("version", 1),
        )

    def get_changed_fields(self) -> list[str]:
        """変更されたフィールド名のリストを返す"""
        return list(self.changes.keys())

    def was_field_changed(self, field_name: str) -> bool:
        """特定のフィールドが変更されたかを確認"""
        return field_name in self.changes
