"""
イベントストア

イベントソーシングのためのイベント永続化レイヤー
"""

from abc import ABC, abstractmethod

from domain.shared.events.domain_event import DomainEvent


class EventStore(ABC):
    """
    イベントストアのインターフェース

    イベントの永続化と取得を管理する
    """

    @abstractmethod
    def append(self, event: DomainEvent) -> None:
        """
        イベントを追加

        Args:
            event: 追加するドメインイベント
        """
        pass

    @abstractmethod
    def get_events(self, aggregate_id: str) -> list[DomainEvent]:
        """
        集約IDに関連するすべてのイベントを取得

        Args:
            aggregate_id: 集約の識別子

        Returns:
            イベントのリスト（発生順）
        """
        pass

    @abstractmethod
    def get_events_after(self, aggregate_id: str, version: int) -> list[DomainEvent]:
        """
        特定バージョン以降のイベントを取得

        Args:
            aggregate_id: 集約の識別子
            version: バージョン番号

        Returns:
            指定バージョン以降のイベントのリスト
        """
        pass

    @abstractmethod
    def get_all_events(self) -> list[DomainEvent]:
        """
        すべてのイベントを取得

        Returns:
            全イベントのリスト
        """
        pass

    @abstractmethod
    def get_events_by_type(self, event_type: str) -> list[DomainEvent]:
        """
        特定タイプのイベントを取得

        Args:
            event_type: イベントタイプ

        Returns:
            指定タイプのイベントのリスト
        """
        pass


class InMemoryEventStore(EventStore):
    """
    インメモリイベントストア

    テストおよび開発環境用のイベントストア実装
    本番環境では永続化層（Redis, Turso等）を使用
    """

    def __init__(self) -> None:
        """イベントストアの初期化"""
        self._events: list[DomainEvent] = []
        self._events_by_aggregate: dict[str, list[DomainEvent]] = {}

    def append(self, event: DomainEvent) -> None:
        """
        イベントを追加

        Args:
            event: 追加するドメインイベント
        """
        self._events.append(event)

        # 集約IDごとにインデックス化
        if event.aggregate_id not in self._events_by_aggregate:
            self._events_by_aggregate[event.aggregate_id] = []
        self._events_by_aggregate[event.aggregate_id].append(event)

    def get_events(self, aggregate_id: str) -> list[DomainEvent]:
        """
        集約IDに関連するすべてのイベントを取得

        Args:
            aggregate_id: 集約の識別子

        Returns:
            イベントのリスト（発生順）
        """
        return self._events_by_aggregate.get(aggregate_id, [])

    def get_events_after(self, aggregate_id: str, version: int) -> list[DomainEvent]:
        """
        特定バージョン以降のイベントを取得

        Args:
            aggregate_id: 集約の識別子
            version: バージョン番号

        Returns:
            指定バージョン以降のイベントのリスト
        """
        events = self.get_events(aggregate_id)
        return [e for e in events if e.version > version]

    def get_all_events(self) -> list[DomainEvent]:
        """
        すべてのイベントを取得

        Returns:
            全イベントのリスト
        """
        return self._events.copy()

    def get_events_by_type(self, event_type: str) -> list[DomainEvent]:
        """
        特定タイプのイベントを取得

        Args:
            event_type: イベントタイプ

        Returns:
            指定タイプのイベントのリスト
        """
        return [e for e in self._events if e.event_type == event_type]

    def clear(self) -> None:
        """
        すべてのイベントをクリア（テスト用）
        """
        self._events.clear()
        self._events_by_aggregate.clear()

    def get_aggregate_version(self, aggregate_id: str) -> int:
        """
        集約の現在のバージョンを取得

        Args:
            aggregate_id: 集約の識別子

        Returns:
            現在のバージョン番号（イベントがない場合は0）
        """
        events = self.get_events(aggregate_id)
        if not events:
            return 0
        return max(e.version for e in events)
