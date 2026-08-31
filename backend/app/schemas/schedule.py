"""Схемы расписания для пульта педагога."""

from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    """Новый слот: какой день, во сколько, какая программа."""

    lessonId: str
    weekday: int
    time: str = Field(examples=["10:00"])
    isEnabled: bool = True


class ScheduleUpdate(BaseModel):
    """Частичное обновление слота."""

    lessonId: str | None = None
    weekday: int | None = None
    time: str | None = None
    isEnabled: bool | None = None


class ScheduleTickRequest(BaseModel):
    """Принудительная проверка слотов (стенд и тесты)."""

    at: str | None = None


class SchedulePublic(BaseModel):
    """Слот в списке пульта."""

    id: str
    lessonId: str
    lessonTitle: str
    weekday: int
    weekdayLabel: str
    time: str
    isEnabled: bool
    nextAt: str | None = None
    nextHint: str
    createdBy: str


class ScheduleTickResult(BaseModel):
    """Что сделала проверка расписания."""

    started: list[str]
    skipped: str | None = None
