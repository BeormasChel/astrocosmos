"""Расписание зала: еженедельные слоты и автозапуск занятий."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import (
    HALL_TIMEZONE,
    SCHEDULE_ACTOR,
    SCHEDULE_GRACE_SECONDS,
    WEEKDAY_LABELS,
)
from app.models.lesson import Lesson
from app.models.schedule import ScheduleSlot
from app.mqtt.bridge import MqttBridge
from app.services import lesson_service


class ScheduleError(Exception):
    """Ошибка слота с текстом для педагога."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def hall_timezone() -> ZoneInfo:
    """Часовой пояс площадки (Челябинск)."""

    return ZoneInfo(HALL_TIMEZONE)


def hall_now(moment: datetime | None = None) -> datetime:
    """Текущее (или переданное) время в часовом поясе зала.

    Args:
        moment: Если задано, перевести в время зала; иначе взять сейчас.

    Returns:
        Aware-datetime в Asia/Yekaterinburg.
    """

    tz = hall_timezone()
    if moment is None:
        return datetime.now(tz)
    if moment.tzinfo is None:
        return moment.replace(tzinfo=tz)
    return moment.astimezone(tz)


def parse_clock(raw: str) -> str:
    """Проверить время вида 09:30 (секунды из браузера отбрасываем)."""

    value = (raw or "").strip()
    if re.match(r"^([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$", value):
        return value[:5]
    raise ScheduleError("Укажите время как часы:минуты, например 10:00")


def parse_weekday(value: int) -> int:
    """День недели: 0 понедельник … 6 воскресенье."""

    if value < 0 or value > 6:
        raise ScheduleError("Выберите день недели")
    return value


def _clock_parts(time_local: str) -> tuple[int, int]:
    """Часы и минуты слота."""

    hour_s, minute_s = time_local.split(":", maxsplit=1)
    return int(hour_s), int(minute_s)


def next_occurrence(weekday: int, time_local: str, now: datetime | None = None) -> datetime:
    """Ближайший момент слота, не раньше текущей минуты.

    Args:
        weekday: 0–6, понедельник — воскресенье.
        time_local: «HH:MM» по времени зала.
        now: Точка отсчёта.

    Returns:
        Aware-datetime следующего срабатывания.
    """

    local = hall_now(now)
    hour, minute = _clock_parts(time_local)
    candidate = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    days_ahead = (weekday - local.weekday()) % 7
    # Если сегодняшнее окно уже прошло, берём следующую неделю.
    if days_ahead == 0 and (local - candidate).total_seconds() >= SCHEDULE_GRACE_SECONDS:
        days_ahead = 7
    return candidate + timedelta(days=days_ahead)


def format_next_hint(next_at: datetime, now: datetime | None = None) -> str:
    """Человеческая подпись «сегодня в 10:00»."""

    local_now = hall_now(now)
    local_next = next_at.astimezone(hall_timezone())
    clock = local_next.strftime("%H:%M")
    if local_next.date() == local_now.date():
        return f"сегодня в {clock}"
    if local_next.date() == local_now.date() + timedelta(days=1):
        return f"завтра в {clock}"
    return f"{WEEKDAY_LABELS[local_next.weekday()]} в {clock}"


def slot_to_dict(slot: ScheduleSlot, now: datetime | None = None) -> dict:
    """Собрать JSON слота для пульта."""

    nxt = next_occurrence(slot.weekday, slot.time_local, now)
    title = slot.lesson.title if slot.lesson is not None else slot.lesson_id
    hint = format_next_hint(nxt, now)
    if not slot.is_enabled:
        hint = f"выключен · {hint}"
    return {
        "id": slot.id,
        "lessonId": slot.lesson_id,
        "lessonTitle": title,
        "weekday": slot.weekday,
        "weekdayLabel": WEEKDAY_LABELS[slot.weekday],
        "time": slot.time_local,
        "isEnabled": slot.is_enabled,
        "nextAt": nxt.isoformat(),
        "nextHint": hint,
        "createdBy": slot.created_by,
    }


async def _get_slot(session: AsyncSession, slot_id: str) -> ScheduleSlot | None:
    """Найти слот вместе с занятием."""

    return await session.scalar(
        select(ScheduleSlot)
        .options(selectinload(ScheduleSlot.lesson))
        .where(ScheduleSlot.id == slot_id)
    )


async def _ensure_lesson(session: AsyncSession, lesson_id: str) -> Lesson:
    """Проверить, что программа есть в каталоге."""

    lesson = await session.get(Lesson, lesson_id)
    if lesson is None:
        raise ScheduleError("Такого занятия нет")
    return lesson


async def list_slots(session: AsyncSession, now: datetime | None = None) -> list[dict]:
    """Все слоты: по дням недели, затем по времени."""

    result = await session.scalars(
        select(ScheduleSlot)
        .options(selectinload(ScheduleSlot.lesson))
        .order_by(ScheduleSlot.weekday, ScheduleSlot.time_local)
    )
    return [slot_to_dict(item, now) for item in result.all()]


async def upcoming_slot(session: AsyncSession, now: datetime | None = None) -> dict | None:
    """Ближайший включённый слот или None."""

    items = await list_slots(session, now)
    enabled = [item for item in items if item["isEnabled"]]
    if not enabled:
        return None
    return min(enabled, key=lambda item: item["nextAt"] or "")


async def create_slot(
    session: AsyncSession,
    *,
    lesson_id: str,
    weekday: int,
    time_local: str,
    created_by: str,
    is_enabled: bool = True,
) -> dict:
    """Добавить еженедельный запуск."""

    await _ensure_lesson(session, lesson_id)
    clean_day = parse_weekday(weekday)
    clean_time = parse_clock(time_local)
    item = ScheduleSlot(
        id=str(uuid.uuid4()),
        lesson_id=lesson_id,
        weekday=clean_day,
        time_local=clean_time,
        is_enabled=is_enabled,
        created_by=created_by,
        created_at=datetime.now(timezone.utc),
    )
    session.add(item)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ScheduleError(
            "Такой запуск уже есть: тот же день, время и занятие",
            status_code=409,
        ) from None
    loaded = await _get_slot(session, item.id)
    assert loaded is not None
    return slot_to_dict(loaded)


async def update_slot(
    session: AsyncSession,
    slot_id: str,
    *,
    lesson_id: str | None = None,
    weekday: int | None = None,
    time_local: str | None = None,
    is_enabled: bool | None = None,
) -> dict:
    """Изменить слот или включить/выключить его."""

    item = await _get_slot(session, slot_id)
    if item is None:
        raise ScheduleError("Такого слота нет", status_code=404)
    if lesson_id is not None:
        await _ensure_lesson(session, lesson_id)
        item.lesson_id = lesson_id
    if weekday is not None:
        item.weekday = parse_weekday(weekday)
    if time_local is not None:
        item.time_local = parse_clock(time_local)
    if is_enabled is not None:
        item.is_enabled = is_enabled
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ScheduleError(
            "Такой запуск уже есть: тот же день, время и занятие",
            status_code=409,
        ) from None
    loaded = await _get_slot(session, slot_id)
    assert loaded is not None
    return slot_to_dict(loaded)


async def delete_slot(session: AsyncSession, slot_id: str) -> None:
    """Убрать слот из расписания."""

    item = await _get_slot(session, slot_id)
    if item is None:
        raise ScheduleError("Такого слота нет", status_code=404)
    await session.delete(item)
    await session.commit()


def _already_fired_this_occurrence(slot: ScheduleSlot, local_now: datetime) -> bool:
    """Не запускать повторно то же утреннее/дневное окно."""

    if slot.last_started_at is None:
        return False
    last = slot.last_started_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    last_local = last.astimezone(local_now.tzinfo)
    hour, minute = _clock_parts(slot.time_local)
    planned = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return last_local.date() == planned.date() and last_local >= planned


def is_slot_due(slot: ScheduleSlot, local_now: datetime) -> bool:
    """Попадает ли текущая минута в окно запуска слота."""

    if not slot.is_enabled:
        return False
    if local_now.weekday() != slot.weekday:
        return False
    hour, minute = _clock_parts(slot.time_local)
    planned = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    elapsed = (local_now - planned).total_seconds()
    if elapsed < 0 or elapsed >= SCHEDULE_GRACE_SECONDS:
        return False
    return not _already_fired_this_occurrence(slot, local_now)


async def fire_due_slots(
    session: AsyncSession,
    mqtt: MqttBridge,
    now: datetime | None = None,
) -> dict:
    """Запустить занятия, чьё время подошло.

    Если педагог уже ведёт занятие вручную, автозапуск пропускаем.

    Args:
        session: Сессия БД.
        mqtt: Мост команд комплексам.
        now: Подмена часов для тестов.

    Returns:
        started — id занятий, skipped — причина пропуска или None.
    """

    local_now = hall_now(now)
    active = await lesson_service.get_active_run(session)
    result = await session.scalars(
        select(ScheduleSlot)
        .options(selectinload(ScheduleSlot.lesson))
        .order_by(ScheduleSlot.weekday, ScheduleSlot.time_local)
    )
    due = [item for item in result.all() if is_slot_due(item, local_now)]
    if not due:
        return {"started": [], "skipped": None}

    # Один автозапуск за тик: не сменять две программы в одну минуту.
    slot = due[0]
    if active is not None:
        slot.last_started_at = datetime.now(timezone.utc)
        await session.commit()
        return {"started": [], "skipped": "occupied"}

    await lesson_service.start_lesson(session, slot.lesson_id, SCHEDULE_ACTOR, mqtt)
    fresh = await session.get(ScheduleSlot, slot.id)
    if fresh is not None:
        fresh.last_started_at = datetime.now(timezone.utc)
        await session.commit()
    return {"started": [slot.lesson_id], "skipped": None}
