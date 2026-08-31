"""Публичные схемы материалов для пульта педагога."""

from pydantic import BaseModel


class MaterialPublic(BaseModel):
    """Карточка материала в списке и после сохранения."""

    id: str
    kind: str
    kindLabel: str
    title: str
    body: str | None = None
    deviceId: str | None = None
    deviceName: str
    clipKey: str | None = None
    rfidUid: str | None = None
    hasFile: bool
    originalName: str | None = None
    mimeType: str | None = None
    byteSize: int | None = None
    createdBy: str
    createdAt: str
