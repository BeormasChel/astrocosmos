"""Занятия, шаги и запуски."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Lesson(Base):
    """Готовая программа для группы."""

    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    duration_min: Mapped[int] = mapped_column(Integer)
    for_whom: Mapped[str] = mapped_column(String(200))
    steps: Mapped[list["LessonStep"]] = relationship(
        back_populates="lesson",
        order_by="LessonStep.sort_order",
        cascade="all, delete-orphan",
    )


class LessonStep(Base):
    """Одна команда комплексу внутри занятия."""

    __tablename__ = "lesson_steps"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lesson_id: Mapped[str] = mapped_column(ForeignKey("lessons.id"))
    sort_order: Mapped[int] = mapped_column(Integer)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"))
    command: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    mode_label: Mapped[str] = mapped_column(String(200))
    lesson: Mapped[Lesson] = relationship(back_populates="steps")


class LessonRun(Base):
    """Факт запуска занятия педагогом."""

    __tablename__ = "lesson_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    lesson_id: Mapped[str] = mapped_column(ForeignKey("lessons.id"))
    started_by: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="running")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    stopped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    lesson: Mapped[Lesson] = relationship()
