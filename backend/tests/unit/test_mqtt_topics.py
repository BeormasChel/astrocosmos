"""Разбор MQTT-топиков зала."""

from app.mqtt.topics import parse_device_channel


def test_parse_hall_status_topic() -> None:
    """Топик статуса иллюминатора разбирается в id и канал."""

    parsed = parse_device_channel("astroc/devices/illuminator/status")
    assert parsed == ("illuminator", "status")


def test_parse_ignores_foreign_prefix() -> None:
    """Брокер обсерватории в astroc не подмешиваем."""

    assert parse_device_channel("diptich/devices/illuminator/status") is None
    assert parse_device_channel("astroc/other") is None
