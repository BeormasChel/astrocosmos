"""Расписание занятий: еженедельные слоты и автозапуск."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db, get_mqtt, require_lesson_control
from app.models.user import User
from app.mqtt.bridge import MqttBridge
from app.schemas.schedule import (
    ScheduleCreate,
    SchedulePublic,
    ScheduleTickRequest,
    ScheduleTickResult,
    ScheduleUpdate,
)
from app.services import schedule_service
from app.services.schedule_service import ScheduleError

router = APIRouter()


def _raise_schedule_error(error: ScheduleError) -> None:
    """Отдать текст ошибки педагогу."""

    raise HTTPException(status_code=error.status_code, detail=error.message) from error


def _parse_tick_moment(raw: str | None) -> datetime | None:
    """Разобрать ISO-время для стендовых проверок."""

    if not raw:
        return None
    try:
        moment = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Непонятное время проверки") from None
    return moment


@router.get("", response_model=list[SchedulePublic])
async def list_schedule(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[SchedulePublic]:
    """Список слотов на неделю."""

    items = await schedule_service.list_slots(session)
    return [SchedulePublic.model_validate(item) for item in items]


@router.get("/upcoming", response_model=SchedulePublic | None)
async def upcoming_schedule(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> SchedulePublic | None:
    """Ближайший включённый запуск — для обзора."""

    item = await schedule_service.upcoming_slot(session)
    if item is None:
        return None
    return SchedulePublic.model_validate(item)


@router.post("/due", response_model=ScheduleTickResult)
async def run_due_slots(
    body: ScheduleTickRequest | None = None,
    session: AsyncSession = Depends(get_db),
    mqtt: MqttBridge = Depends(get_mqtt),
    _: User = Depends(require_lesson_control),
) -> ScheduleTickResult:
    """Проверить слоты сейчас (ядро делает это само, кнопка — для стенда)."""

    payload = body or ScheduleTickRequest()
    data = await schedule_service.fire_due_slots(
        session,
        mqtt,
        now=_parse_tick_moment(payload.at),
    )
    return ScheduleTickResult.model_validate(data)


@router.post("", response_model=SchedulePublic, status_code=201)
async def create_schedule_slot(
    body: ScheduleCreate,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(require_lesson_control),
) -> SchedulePublic:
    """Добавить автоматический запуск."""

    try:
        data = await schedule_service.create_slot(
            session,
            lesson_id=body.lessonId,
            weekday=body.weekday,
            time_local=body.time,
            created_by=user.login,
            is_enabled=body.isEnabled,
        )
    except ScheduleError as error:
        _raise_schedule_error(error)
    return SchedulePublic.model_validate(data)


@router.patch("/{slot_id}", response_model=SchedulePublic)
async def update_schedule_slot(
    slot_id: str,
    body: ScheduleUpdate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_lesson_control),
) -> SchedulePublic:
    """Включить, выключить или поправить слот."""

    try:
        data = await schedule_service.update_slot(
            session,
            slot_id,
            lesson_id=body.lessonId,
            weekday=body.weekday,
            time_local=body.time,
            is_enabled=body.isEnabled,
        )
    except ScheduleError as error:
        _raise_schedule_error(error)
    return SchedulePublic.model_validate(data)


@router.delete("/{slot_id}", status_code=204)
async def delete_schedule_slot(
    slot_id: str,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_lesson_control),
) -> None:
    """Убрать слот, чтобы занятие больше не включалось само."""

    try:
        await schedule_service.delete_slot(session, slot_id)
    except ScheduleError as error:
        _raise_schedule_error(error)
