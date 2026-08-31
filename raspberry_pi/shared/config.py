"""Конфиг агента RPi из переменных окружения и /etc/astrocosmos/device.env."""

from dataclasses import dataclass
import os


@dataclass
class DeviceConfig:
    """Параметры подключения агента к ядру."""

    device_id: str
    mqtt_host: str
    mqtt_port: int
    mqtt_prefix: str
    nfs_mount: str

    @classmethod
    def from_env(cls) -> "DeviceConfig":
        """Собрать конфиг из окружения."""

        return cls(
            device_id=os.getenv("DEVICE_ID", "unknown"),
            mqtt_host=os.getenv("MQTT_HOST", "192.168.1.10"),
            mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
            mqtt_prefix=os.getenv("MQTT_TOPIC_PREFIX", "astroc"),
            nfs_mount=os.getenv("NFS_MOUNT", "/mnt/content"),
        )
