"""Реестр комплексов зала."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Device(Base):
    """Комплекс 1–6. Тумба RFID хранится в extras большого голобокса."""

    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(120))
    purpose: Mapped[str] = mapped_column(Text)
    platform: Mapped[str] = mapped_column(String(120))
    current_mode: Mapped[str] = mapped_column(String(200), default="Ещё не подключался")
    extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
