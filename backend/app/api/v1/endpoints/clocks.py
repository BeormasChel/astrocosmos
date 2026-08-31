"""Астрономические часы: режимы с пульта и MQTT на ESP32."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db, get_mqtt, require_lesson_control
from app.models.user import User
from app.mqtt.bridge import MqttBridge
from app.services.clock_service import ClockError, apply_mode, clock_state

router = APIRouter()


class ClockPlanetPublic(BaseModel):
    """Одна планета на циферблате."""

    id: str
    name: str
    dayHours: float
    retrograde: bool
    color: str
    highlighted: bool
    visualSeconds: float
    dayHint: str


class ClockModePublic(BaseModel):
    """Кнопка режима для педагога."""

    id: str
    label: str
    hint: str


class ClockStatePublic(BaseModel):
    """Что показывают часы прямо сейчас."""

    deviceId: str
    mode: str
    label: str
    title: str
    hint: str
    mqttConnected: bool
    planets: list[ClockPlanetPublic]
    modes: list[ClockModePublic]


class ClockModeCommand(BaseModel):
    """Смена режима с пульта."""

    mode: str = Field(examples=["compare"])


def _raise_clock(error: ClockError) -> None:
    """Отдать текст ошибки педагогу без стека."""

    raise HTTPException(status_code=error.status_code, detail=error.message) from error


@router.get("", response_model=ClockStatePublic)
async def get_clocks(
    session: AsyncSession = Depends(get_db),
    mqtt: MqttBridge = Depends(get_mqtt),
    _: User = Depends(get_current_user),
) -> ClockStatePublic:
    """Состояние циферблата и список режимов."""

    data = await clock_state(session, mqtt.connected)
    return ClockStatePublic.model_validate(data)


@router.post("/mode", response_model=ClockStatePublic)
async def set_clock_mode(
    body: ClockModeCommand,
    session: AsyncSession = Depends(get_db),
    mqtt: MqttBridge = Depends(get_mqtt),
    _: User = Depends(require_lesson_control),
) -> ClockStatePublic:
    """Отправить set_mode/idle на часы. Без брокера команда пишется в журнал."""

    try:
        data = await apply_mode(session, mqtt, body.mode.strip())
    except ClockError as error:
        _raise_clock(error)
    return ClockStatePublic.model_validate(data)
