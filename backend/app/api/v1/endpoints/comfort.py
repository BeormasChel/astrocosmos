"""Комфорт зала: свет и жалюзи через Home Assistant."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.deps import get_current_user, require_lesson_control
from app.integrations.home_assistant.client import HomeAssistantClient
from app.models.user import User

router = APIRouter()


class ComfortStatus(BaseModel):
    """Состояние интеграции комфорта для пульта."""

    enabled: bool
    hint: str


class ComfortCommand(BaseModel):
    """Команда свету или жалюзи."""

    domain: str = Field(examples=["light"])
    service: str = Field(examples=["turn_off"])
    payload: dict = Field(default_factory=dict)


class ComfortResult(BaseModel):
    """Ответ шага комфорта."""

    ok: bool
    skipped: bool = False
    data: dict | None = None


@router.get("/status", response_model=ComfortStatus)
async def comfort_status(_: User = Depends(get_current_user)) -> ComfortStatus:
    """Свет и жалюзи: подключены или ждут настройки."""

    client = HomeAssistantClient()
    if client.enabled:
        return ComfortStatus(
            enabled=True,
            hint="Свет и жалюзи можно гасить из занятия.",
        )
    return ComfortStatus(
        enabled=False,
        hint="Свет и жалюзи пока не подключены — на стенде это нормально.",
    )


@router.post("/command", response_model=ComfortResult)
async def comfort_command(
    body: ComfortCommand,
    _: User = Depends(require_lesson_control),
) -> ComfortResult:
    """Вызвать сервис Home Assistant или тихо пропустить, если URL пустой."""

    client = HomeAssistantClient()
    raw = await client.call_service(body.domain, body.service, body.payload)
    return ComfortResult(
        ok=bool(raw.get("ok", True)),
        skipped=bool(raw.get("skipped", False)),
        data=raw.get("data") if isinstance(raw.get("data"), dict) else None,
    )
