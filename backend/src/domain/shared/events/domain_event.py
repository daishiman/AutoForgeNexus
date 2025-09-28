"""
ドメインイベントベースクラス

すべてのドメインイベントの基底クラス
イベント駆動アーキテクチャの中核となるクラス
"""

from datetime import datetime
from typing import Any
from uuid import uuid4


class DomainEvent:
    """
    ドメインイベントの基底クラス

    すべてのドメインイベントはこのクラスを継承する

    Attributes:
        event_id: イベントの一意識別子
        aggregate_id: 集約の識別子
        event_type: イベントタイプ
        occurred_at: イベント発生時刻
        version: イベントスキーマバージョン
        payload: イベントに関連するデータ
    """

    def __init__(
        self,
        aggregate_id: str,
        event_type: str,
        event_id: str | None = None,
        occurred_at: datetime | None = None,
        version: int = 1,
        payload: dict[str, Any] | None = None,
    ):
        """初期化"""
        self.aggregate_id = aggregate_id
        self.event_type = event_type
        self.event_id = event_id or str(uuid4())
        self.occurred_at = occurred_at or datetime.utcnow()
        self.version = version
        self.payload = payload or {}

    def to_dict(self) -> dict[str, Any]:
        """
        イベントを辞書形式に変換

        永続化やシリアライズのために使用

        Returns:
            イベント情報を含む辞書
        """
        return {
            "event_id": self.event_id,
            "aggregate_id": self.aggregate_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "version": self.version,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DomainEvent":
        """
        辞書からイベントを復元

        永続化されたイベントの復元に使用

        Args:
            data: イベント情報を含む辞書

        Returns:
            復元されたドメインイベント
        """
        occurred_at = data.get("occurred_at")
        if isinstance(occurred_at, str):
            occurred_at = datetime.fromisoformat(occurred_at)

        return cls(
            aggregate_id=data["aggregate_id"],
            event_type=data["event_type"],
            event_id=data["event_id"],
            occurred_at=occurred_at,
            version=data.get("version", 1),
            payload=data.get("payload", {}),
        )

    def __repr__(self) -> str:
        """イベントの文字列表現"""
        return f"{self.event_type}(aggregate_id={self.aggregate_id}, occurred_at={self.occurred_at})"
