"""
SQLAlchemy Base Model
すべてのモデルの基底クラスとMixin定義

DDDアーキテクチャ準拠:
- 各ドメインモデルはこのBaseを継承
- 共通Mixinで横断的関心事を実装
"""
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    すべてのSQLAlchemyモデルの基底クラス

    Usage:
        from src.infrastructure.shared.database.base import Base

        class PromptModel(Base):
            __tablename__ = "prompts"
            ...
    """

    pass


class TimestampMixin:
    """
    タイムスタンプミックスイン

    自動的にcreated_atとupdated_atを管理
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="作成日時",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新日時",
    )


class SoftDeleteMixin:
    """
    論理削除ミックスイン

    deleted_atにNULL以外が入っている場合は削除済みとみなす
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, comment="削除日時（論理削除）"
    )

    @property
    def is_deleted(self) -> bool:
        """削除済みかどうか"""
        return self.deleted_at is not None


__all__ = [
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
]
