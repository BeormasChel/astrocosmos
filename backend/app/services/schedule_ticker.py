"""Фоновая проверка расписания внутри процесса ядра."""

from __future__ import annotations

import asyncio
import logging

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.database import get_session_factory
from app.services import schedule_service

logger = logging.getLogger(__name__)


async def run_schedule_ticker(app: FastAPI, stop: asyncio.Event) -> None:
    """Раз в несколько секунд смотреть, не пора ли включить занятие.

    Args:
        app: Приложение с MQTT в state.
        stop: Событие остановки lifespan.
    """

    interval = max(5, get_settings().schedule_tick_seconds)
    while not stop.is_set():
        try:
            factory = get_session_factory()
            async with factory() as session:
                outcome = await schedule_service.fire_due_slots(session, app.state.mqtt)
            if outcome["started"]:
                logger.info("Расписание запустило: %s", ", ".join(outcome["started"]))
            elif outcome["skipped"] == "occupied":
                logger.info("Расписание пропустило слот: в зале уже идёт занятие")
        except Exception:
            logger.exception("Не удалось проверить расписание")

        try:
            await asyncio.wait_for(stop.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue
