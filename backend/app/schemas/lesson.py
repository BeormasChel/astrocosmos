"""Схемы занятий."""

from pydantic import BaseModel


class LessonPublic(BaseModel):
    """Программа занятия в списке пульта."""

    id: str
    title: str
    durationMin: int
    forWhom: str
    complexIds: list[str]


class LessonRunPublic(BaseModel):
    """Текущий или остановленный запуск."""

    id: str
    lessonId: str
    title: str
    status: str
    startedBy: str
    startedAt: str
    stoppedAt: str | None = None
    commandsSent: list[str] | None = None
