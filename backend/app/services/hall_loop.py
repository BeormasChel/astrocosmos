"""Фоновый цикл зала: MQTT inbound и пульс учебного стенда."""

from __future__ import annotations

import asyncio
import logging
import time

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.database import get_session_factory
from app.services import hall_service

logger = logging.getLogger(__name__)


async def run_hall_loop(app: FastAPI, stop: asyncio.Event) -> None:
    """Раз в секунду разобрать MQTT; при стенде — пульс heartbeat.

    Args:
        app: Приложение с MQTT в state.
        stop: Событие остановки lifespan.
    """

    settings = get_settings()
    interval = max(5, settings.hall_emulator_seconds)
    last_pulse = 0.0
    first_pulse = True

    while not stop.is_set():
        try:
            factory = get_session_factory()
            async with factory() as session:
                await hall_service.apply_inbound_messages(session, app.state.mqtt)
                now = time.monotonic()
                should_pulse = settings.hall_emulator_enabled and (
                    first_pulse or now - last_pulse >= interval
                )
                if should_pulse:
                    pulsed = await hall_service.pulse_stand(session, app.state.mqtt)
                    last_pulse = now
                    if first_pulse:
                        logger.info("Стенд: комплексы зала на связи (%s)", len(pulsed))
                    first_pulse = False
        except Exception:
            logger.exception("Не удалось обновить статусы комплексов")

        try:
            await asyncio.wait_for(stop.wait(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
