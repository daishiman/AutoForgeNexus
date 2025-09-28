"""
PromptMetadata値オブジェクト

プロンプトのメタデータを表現する不変の値オブジェクト。
バージョン、ステータス、作成日時などを管理します。
"""

from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True)
class PromptMetadata:
    """
    プロンプトのメタデータを表現する値オブジェクト

    Attributes:
        version: プロンプトのバージョン番号
        status: プロンプトのステータス（draft, saved, published）
        created_at: 作成日時
        updated_at: 更新日時（オプション）
        created_by: 作成者ID
    """

    version: int
    status: str
    created_at: datetime
    updated_at: datetime | None
    created_by: str

    # 有効なステータス
    VALID_STATUSES = {"draft", "saved", "published"}

    def __post_init__(self):
        """初期化後のバリデーション"""
        if self.version < 1:
            raise ValueError("バージョンは1以上である必要があります")

        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"無効なステータス: {self.status}")

    def with_update(self, **kwargs) -> "PromptMetadata":
        """
        更新された新しいインスタンスを作成

        Args:
            **kwargs: 更新する属性

        Returns:
            更新されたPromptMetadataインスタンス
        """
        # 更新日時を自動設定
        if "updated_at" not in kwargs:
            kwargs["updated_at"] = datetime.now()

        return replace(self, **kwargs)

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "version": self.version,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
