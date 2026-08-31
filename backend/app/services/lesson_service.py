"""Движок занятий: старт, стоп, MQTT-команды комплексам."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import DEVICE_PLANET_CLOCK
from app.models.device import Device
from app.models.lesson import Lesson, LessonRun
from app.mqtt.bridge import MqttBridge
from app.services import clock_service

RUN_RUNNING = "running"
RUN_STOPPED = "stopped"


async def list_lessons(session: AsyncSession) -> list[dict]:
    """Вернуть каталог занятий с задействованными комплексами."""

    result = await session.scalars(
        select(Lesson).options(selectinload(Lesson.steps)).order_by(Lesson.title)
    )
    lessons = []
    for lesson in result.all():
        lessons.append(
            {
                "id": lesson.id,
                "title": lesson.title,
                "durationMin": lesson.duration_min,
                "forWhom": lesson.for_whom,
                "complexIds": [step.device_id for step in lesson.steps],
            }
        )
    return lessons


async def get_active_run(session: AsyncSession) -> dict | None:
    """Найти занятие, которое сейчас идёт в зале."""

    result = await session.scalars(
        select(LessonRun)
        .options(selectinload(LessonRun.lesson))
        .where(LessonRun.status == RUN_RUNNING)
        .order_by(LessonRun.started_at.desc())
    )
    run = result.first()
    if run is None:
        return None
    return _run_to_dict(run)


async def start_lesson(
    session: AsyncSession,
    lesson_id: str,
    started_by: str,
    mqtt: MqttBridge,
) -> dict:
    """Запустить занятие: остановить предыдущее и разослать команды.

    Args:
        session: Сессия БД.
        lesson_id: Идентификатор программы.
        started_by: Логин педагога.
        mqtt: Мост команд.

    Returns:
        Описание запуска.

    Raises:
        KeyError: Занятие не найдено.
    """

    lesson = await session.scalar(
        select(Lesson).options(selectinload(Lesson.steps)).where(Lesson.id == lesson_id)
    )
    if lesson is None:
        raise KeyError(lesson_id)

    # Останавливаем то, что уже идёт, чтобы зал не играл две программы.
    await stop_active_lesson(session, mqtt, started_by, quiet=True)

    run = LessonRun(
        id=str(uuid.uuid4()),
        lesson_id=lesson.id,
        started_by=started_by,
        status=RUN_RUNNING,
        started_at=datetime.now(timezone.utc),
    )
    session.add(run)

    commands: list[str] = []
    for step in lesson.steps:
        payload = {
            "command": step.command,
            "lesson_id": lesson.id,
            "run_id": run.id,
            **(step.payload or {}),
        }
        mqtt.publish_command(step.device_id, json.dumps(payload, ensure_ascii=False))
        commands.append(step.device_id)

        device = await session.get(Device, step.device_id)
        if device is not None:
            device.current_mode = step.mode_label
            if step.device_id == DEVICE_PLANET_CLOCK:
                clock_service.remember_step(device, step.command, step.payload)

    await session.commit()
    await session.refresh(run)
    run.lesson = lesson
    data = _run_to_dict(run)
    data["commandsSent"] = commands
    return data


async def stop_active_lesson(
    session: AsyncSession,
    mqtt: MqttBridge,
    stopped_by: str,
    quiet: bool = False,
) -> dict | None:
    """Вернуть зал в ожидание.

    Args:
        session: Сессия БД.
        mqtt: Мост команд.
        stopped_by: Кто остановил.
        quiet: Не создавать запись, если запуска не было (для смены занятия).

    Returns:
        Остановленный запуск или None.
    """

    result = await session.scalars(
        select(LessonRun)
        .options(selectinload(LessonRun.lesson).selectinload(Lesson.steps))
        .where(LessonRun.status == RUN_RUNNING)
    )
    run = result.first()
    if run is None:
        if quiet:
            return None
        return None

    idle = json.dumps(
        {"command": "idle", "lesson_id": run.lesson_id, "run_id": run.id},
        ensure_ascii=False,
    )
    for step in run.lesson.steps:
        mqtt.publish_command(step.device_id, idle)
        device = await session.get(Device, step.device_id)
        if device is not None:
            device.current_mode = "Ожидание"
            if step.device_id == DEVICE_PLANET_CLOCK:
                clock_service.remember_step(device, "idle", {})

    run.status = RUN_STOPPED
    run.stopped_at = datetime.now(timezone.utc)
    run.notes = f"stopped_by={stopped_by}"
    await session.commit()
    return _run_to_dict(run)


def _run_to_dict(run: LessonRun) -> dict:
    """Сериализовать запуск для API."""

    title = run.lesson.title if run.lesson is not None else run.lesson_id
    return {
        "id": run.id,
        "lessonId": run.lesson_id,
        "title": title,
        "status": run.status,
        "startedBy": run.started_by,
        "startedAt": run.started_at.isoformat(),
        "stoppedAt": run.stopped_at.isoformat() if run.stopped_at else None,
    }
