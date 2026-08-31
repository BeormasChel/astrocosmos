"""Учебный стенд зала: heartbeat без Raspberry Pi и разбор MQTT status."""

from __future__ import annotations

import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.mqtt.bridge import MqttBridge
from app.mqtt.topics import EVENTS_CHANNEL, STATUS_CHANNEL, is_hall_device
from app.services import device_service

logger = logging.getLogger(__name__)


def payload_says_offline(raw: str) -> bool:
    """Понять по JSON статуса, что комплекс сам сказал «нет связи»."""

    text = (raw or "").strip()
    if not text:
        return False
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return text.lower() in {"offline", "down"}
    if not isinstance(data, dict):
        return False
    if data.get("online") is False:
        return True
    status = str(data.get("status") or data.get("state") or "").lower()
    return status in {"offline", "down"}


async def apply_inbound_messages(session: AsyncSession, mqtt: MqttBridge) -> int:
    """Применить накопившиеся MQTT status/events к реестру.

    Args:
        session: Сессия БД.
        mqtt: Мост с очередью входящих.

    Returns:
        Сколько сообщений разобрали.
    """

    messages = mqtt.drain_inbound()
    for device_id, channel, payload in messages:
        if not is_hall_device(device_id):
            logger.info("MQTT вне зала пропущен: %s %s", device_id, channel)
            continue
        if channel == STATUS_CHANNEL:
            if payload_says_offline(payload):
                await device_service.mark_offline(session, device_id)
            else:
                await device_service.mark_heartbeat(session, device_id)
        elif channel == EVENTS_CHANNEL:
            logger.info("MQTT event %s %s", device_id, payload)
    return len(messages)


async def pulse_stand(session: AsyncSession, mqtt: MqttBridge) -> list[str]:
    """Пометить комплексы зала на связи и при наличии брокера объявить status.

    Args:
        session: Сессия БД.
        mqtt: Мост команд/статусов.

    Returns:
        id комплексов, которым отправили пульс.
    """

    pulsed = await device_service.pulse_hall_devices(session)
    for device_id in pulsed:
        mqtt.publish_status(
            device_id,
            {"status": "online", "source": "stand"},
        )
    return pulsed
