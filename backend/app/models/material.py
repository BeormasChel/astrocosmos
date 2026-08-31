"""Материалы зала: ролики, тексты, карточки учёных."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.device import Device


class Material(Base):
    """Единица контента, которую педагог кладёт в пульт."""

    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    device_id: Mapped[str | None] = mapped_column(
        ForeignKey("devices.id"),
        nullable=True,
        index=True,
    )
    clip_key: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    rfid_uid: Mapped[str | None] = mapped_column(String(32), nullable=True, unique=True)
    stored_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    original_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    byte_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    device: Mapped[Device | None] = relationship()
