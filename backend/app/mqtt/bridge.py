"""MQTT-клиент ядра: команды комплексам, префикс astroc/."""

from __future__ import annotations

import json
import logging
import queue

from app.core.config import get_settings
from app.mqtt.topics import COMMAND_CHANNEL, STATUS_CHANNEL, device_channel_topic, parse_device_channel

logger = logging.getLogger(__name__)

InboundMessage = tuple[str, str, str]


class MqttBridge:
    """Обёртка над Mosquitto. Если брокер недоступен, команды пишутся в лог."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._connected = False
        self._client = None
        self._inbound: queue.SimpleQueue[InboundMessage] = queue.SimpleQueue()

    @property
    def connected(self) -> bool:
        """Есть ли живой брокер ядра."""

        return self._connected

    def connect(self) -> None:
        """Подключиться к брокеру; ошибка сети не валит ядро."""

        try:
            import socket

            import paho.mqtt.client as mqtt

            # Быстрая проверка порта, чтобы тесты и стенд без брокера не ждали.
            with socket.create_connection(
                (self._settings.mqtt_host, self._settings.mqtt_port),
                timeout=0.4,
            ):
                pass

            client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id="astrocosmos-core",
            )
            if self._settings.mqtt_username:
                client.username_pw_set(
                    self._settings.mqtt_username,
                    self._settings.mqtt_password or None,
                )
            client.on_message = self._on_message
            client.connect(self._settings.mqtt_host, self._settings.mqtt_port, 60)
            client.loop_start()
            prefix = self._settings.mqtt_topic_prefix
            client.subscribe(f"{prefix}/devices/+/status", qos=1)
            client.subscribe(f"{prefix}/devices/+/events", qos=1)
            self._client = client
            self._connected = True
            logger.info(
                "MQTT подключён: %s:%s",
                self._settings.mqtt_host,
                self._settings.mqtt_port,
            )
        except Exception as exc:  # noqa: BLE001 — брокер опционален на этапе A
            logger.warning("MQTT недоступен, команды только в журнал: %s", exc)
            self._connected = False

    def _on_message(self, _client, _userdata, message) -> None:
        """Положить входящее сообщение в очередь для async-цикла ядра."""

        topic = str(message.topic)
        parsed = parse_device_channel(topic, self._settings.mqtt_topic_prefix)
        if parsed is None:
            return
        device_id, channel = parsed
        payload = message.payload.decode("utf-8", errors="replace")
        self._inbound.put((device_id, channel, payload))

    def drain_inbound(self) -> list[InboundMessage]:
        """Забрать накопившиеся status/events без блокировки."""

        items: list[InboundMessage] = []
        while True:
            try:
                items.append(self._inbound.get_nowait())
            except queue.Empty:
                break
        return items

    def publish_command(self, device_id: str, payload: str) -> None:
        """Опубликовать команду в `astroc/devices/{id}/command`.

        Args:
            device_id: Идентификатор комплекса.
            payload: JSON-строка команды.
        """

        topic = device_channel_topic(
            device_id,
            COMMAND_CHANNEL,
            self._settings.mqtt_topic_prefix,
        )
        logger.info("MQTT command %s %s", topic, payload)
        if self._connected and self._client is not None:
            self._client.publish(topic, payload, qos=1)

    def publish_status(self, device_id: str, payload: dict) -> None:
        """Опубликовать статус комплекса (стенд или прокси агента).

        Args:
            device_id: Идентификатор комплекса.
            payload: Словарь статуса.
        """

        topic = device_channel_topic(
            device_id,
            STATUS_CHANNEL,
            self._settings.mqtt_topic_prefix,
        )
        body = json.dumps(payload, ensure_ascii=False)
        logger.info("MQTT status %s %s", topic, body)
        if self._connected and self._client is not None:
            self._client.publish(topic, body, qos=1)
