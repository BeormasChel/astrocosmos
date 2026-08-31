"""Сервис комплексов: статусы и heartbeat."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEVICE_OFFLINE_AFTER_SECONDS, HALL_DEVICE_IDS
from app.models.device import Device


def compute_status(device: Device) -> str:
    """Вычислить статус по последнему heartbeat.

    Args:
        device: Запись комплекса.

    Returns:
        online, offline или unknown.
    """

    if device.last_seen_at is None:
        return "unknown"
    seen = device.last_seen_at
    if seen.tzinfo is None:
        seen = seen.replace(tzinfo=timezone.utc)
    elapsed = datetime.now(timezone.utc) - seen
    if elapsed <= timedelta(seconds=DEVICE_OFFLINE_AFTER_SECONDS):
        return "online"
    return "offline"


def device_to_dict(device: Device) -> dict:
    """Собрать JSON карточки комплекса для админки."""

    extras = device.extras or {}
    return {
        "id": device.id,
        "number": device.number,
        "name": device.name,
        "purpose": device.purpose,
        "platform": device.platform,
        "status": compute_status(device),
        "currentMode": device.current_mode,
        "rfidPedestal": extras.get("rfidPedestal"),
    }


async def list_devices(session: AsyncSession) -> list[dict]:
    """Вернуть комплексы по номеру."""

    result = await session.scalars(select(Device).order_by(Device.number))
    return [device_to_dict(item) for item in result.all()]


async def mark_heartbeat(session: AsyncSession, device_id: str) -> Device | None:
    """Отметить, что комплекс на связи.

    Args:
        session: Сессия БД.
        device_id: Идентификатор из реестра.

    Returns:
        Устройство или None, если id неизвестен.
    """

    device = await session.get(Device, device_id)
    if device is None:
        return None
    device.last_seen_at = datetime.now(timezone.utc)
    if device.current_mode == "Ещё не подключался":
        device.current_mode = "Ожидание"
    await session.commit()
    await session.refresh(device)
    return device


async def mark_offline(session: AsyncSession, device_id: str) -> Device | None:
    """Пометить комплекс как пропавший с связи.

    Args:
        session: Сессия БД.
        device_id: Идентификатор из реестра.

    Returns:
        Устройство или None.
    """

    device = await session.get(Device, device_id)
    if device is None:
        return None
    # Сдвигаем last_seen за порог offline, не трогая режим занятия.
    device.last_seen_at = datetime.now(timezone.utc) - timedelta(
        seconds=DEVICE_OFFLINE_AFTER_SECONDS + 1
    )
    await session.commit()
    await session.refresh(device)
    return device


async def pulse_hall_devices(session: AsyncSession) -> list[str]:
    """Отметить все комплексы зала на связи (учебный стенд без железа).

    Returns:
        id комплексов, которым обновили heartbeat.
    """

    now = datetime.now(timezone.utc)
    result = await session.scalars(select(Device).where(Device.id.in_(HALL_DEVICE_IDS)))
    pulsed: list[str] = []
    for device in result.all():
        device.last_seen_at = now
        if device.current_mode == "Ещё не подключался":
            device.current_mode = "Ожидание"
        pulsed.append(device.id)
    await session.commit()
    return pulsed
