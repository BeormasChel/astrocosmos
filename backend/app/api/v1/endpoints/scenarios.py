"""Запуск и остановка образовательных занятий."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_mqtt, require_lesson_control
from app.deps import get_db
from app.models.user import User
from app.mqtt.bridge import MqttBridge
from app.schemas.lesson import LessonPublic, LessonRunPublic
from app.services import lesson_service

router = APIRouter()


@router.get("", response_model=list[LessonPublic])
async def list_lessons(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[LessonPublic]:
    """Каталог занятий."""

    items = await lesson_service.list_lessons(session)
    return [LessonPublic.model_validate(item) for item in items]


@router.get("/active", response_model=LessonRunPublic | None)
async def active_lesson(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> LessonRunPublic | None:
    """Занятие, которое сейчас идёт, или null."""

    item = await lesson_service.get_active_run(session)
    if item is None:
        return None
    return LessonRunPublic.model_validate(item)


@router.post("/{lesson_id}/start", response_model=LessonRunPublic)
async def start_lesson(
    lesson_id: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_lesson_control),
    mqtt: MqttBridge = Depends(get_mqtt),
) -> LessonRunPublic:
    """Включить программу на комплексах зала."""

    try:
        data = await lesson_service.start_lesson(session, lesson_id, user.login, mqtt)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого занятия нет",
        ) from None
    return LessonRunPublic.model_validate(data)


@router.post("/stop", response_model=LessonRunPublic | None)
async def stop_lesson(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_lesson_control),
    mqtt: MqttBridge = Depends(get_mqtt),
) -> LessonRunPublic | None:
    """Остановить текущее занятие."""

    data = await lesson_service.stop_active_lesson(session, mqtt, user.login)
    if data is None:
        return None
    return LessonRunPublic.model_validate(data)
