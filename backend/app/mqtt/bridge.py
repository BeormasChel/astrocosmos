"""Асинхронный MQTT-мост на paho-mqtt. Заглушка до этапа MVP-2."""

from __future__ import annotations

import logging
from typing import Callable

from app.core.config import get_settings

logger = logging.getLogger(__name__)

MessageHandler = Callable[[str, bytes], None]


class MqttBridge:
    """Обёртка над брокером Mosquitto для ядра.

    На этапе MVP подключается в lifespan FastAPI и держит одно соединение.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._connected = False

    def connect(self) -> None:
        """Установить соединение с брокером (пока только логирует)."""

        logger.info(
            "MQTT stub: host=%s port=%s prefix=%s",
            self._settings.mqtt_host,
            self._settings.mqtt_port,
            self._settings.mqtt_topic_prefix,
        )
        self._connected = True

    def publish_command(self, device_id: str, payload: str) -> None:
        """Опубликовать команду устройству в `astroc/devices/{id}/command`.

        Args:
            device_id: Идентификатор комплекса из реестра.
            payload: JSON-строка команды.
        """

        topic = f"{self._settings.mqtt_topic_prefix}/devices/{device_id}/command"
        logger.info("MQTT stub publish %s: %s", topic, payload)
