"""Схемы комплексов."""

from typing import Any

from pydantic import BaseModel


class DevicePublic(BaseModel):
    """Карточка комплекса для пульта."""

    id: str
    number: int
    name: str
    purpose: str
    platform: str
    status: str
    currentMode: str
    rfidPedestal: dict[str, Any] | None = None


class HeartbeatResponse(BaseModel):
    """Ответ агента киоска после ping."""

    id: str
    status: str
