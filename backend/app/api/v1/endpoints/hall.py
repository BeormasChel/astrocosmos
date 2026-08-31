"""Сводка зала: учебный стенд и ручной пульс heartbeat."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.constants import HALL_DEVICE_IDS
from app.deps import get_current_user, get_db, get_mqtt, require_lesson_control
from app.models.user import User
from app.mqtt.bridge import MqttBridge
from app.services import device_service, hall_service

router = APIRouter()


class HallPublic(BaseModel):
    """Состояние стенда для пульта."""

    standEnabled: bool
    mqttConnected: bool
    onlineCount: int
    hallCount: int


class HallPulseResult(BaseModel):
    """Результат ручного пульса стенда."""

    pulsed: list[str]


@router.get("", response_model=HallPublic)
async def hall_state(
    session: AsyncSession = Depends(get_db),
    mqtt: MqttBridge = Depends(get_mqtt),
    _: User = Depends(get_current_user),
) -> HallPublic:
    """Сказать пульту, учебный ли это стенд и сколько комплексов на связи."""

    devices = await device_service.list_devices(session)
    online = sum(1 for item in devices if item["status"] == "online")
    return HallPublic(
        standEnabled=get_settings().hall_emulator_enabled,
        mqttConnected=mqtt.connected,
        onlineCount=online,
        hallCount=len(HALL_DEVICE_IDS),
    )


@router.post("/pulse", response_model=HallPulseResult)
async def pulse_hall(
    session: AsyncSession = Depends(get_db),
    mqtt: MqttBridge = Depends(get_mqtt),
    _: User = Depends(require_lesson_control),
) -> HallPulseResult:
    """Пометить комплексы зала на связи (кнопка стенда и автотест)."""

    pulsed = await hall_service.pulse_stand(session, mqtt)
    return HallPulseResult(pulsed=pulsed)
