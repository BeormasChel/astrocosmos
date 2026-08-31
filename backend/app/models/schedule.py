"""Еженедельный слот автозапуска занятия."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.lesson import Lesson


class ScheduleSlot(Base):
    """День недели и время, когда ядро само включает программу."""

    __tablename__ = "schedule_slots"
    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "weekday",
            "time_local",
            name="uq_schedule_lesson_day_time",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    lesson_id: Mapped[str] = mapped_column(ForeignKey("lessons.id"), index=True)
    weekday: Mapped[int] = mapped_column(Integer)
    time_local: Mapped[str] = mapped_column(String(5))
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    lesson: Mapped[Lesson] = relationship()
