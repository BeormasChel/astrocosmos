"""Разбор MQTT-топиков ядра `astroc/devices/{id}/…`."""

from __future__ import annotations

from app.core.constants import HALL_DEVICE_IDS, MQTT_TOPIC_PREFIX

STATUS_CHANNEL = "status"
EVENTS_CHANNEL = "events"
COMMAND_CHANNEL = "command"


def device_channel_topic(device_id: str, channel: str, prefix: str = MQTT_TOPIC_PREFIX) -> str:
    """Собрать топик комплекса.

    Args:
        device_id: Идентификатор из реестра зала.
        channel: status, events, command, ack, telemetry.
        prefix: Префикс брокера ядра.

    Returns:
        Полный топик.
    """

    return f"{prefix}/devices/{device_id}/{channel}"


def parse_device_channel(topic: str, prefix: str = MQTT_TOPIC_PREFIX) -> tuple[str, str] | None:
    """Достать id комплекса и канал из топика.

    Args:
        topic: Входящий MQTT-топик.
        prefix: Ожидаемый префикс.

    Returns:
        (device_id, channel) или None, если топик не наш.
    """

    parts = topic.split("/")
    if len(parts) < 4:
        return None
    if parts[0] != prefix or parts[1] != "devices":
        return None
    device_id, channel = parts[2], parts[3]
    if not device_id or not channel:
        return None
    return device_id, channel


def is_hall_device(device_id: str) -> bool:
    """Проверить, что это комплекс зала, а не обсерватория и не тумба."""

    return device_id in HALL_DEVICE_IDS
