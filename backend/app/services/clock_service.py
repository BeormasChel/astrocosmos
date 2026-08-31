"""Астрономические часы: режимы, планеты и команда MQTT."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified

from app.core.constants import (
    CLOCK_EXTRAS_MODE_KEY,
    CLOCK_MODE_COMPARE,
    CLOCK_MODE_IDLE,
    CLOCK_MODE_JUPITER,
    CLOCK_MODE_RETROGRADE,
    CLOCK_MODES,
    DEVICE_PLANET_CLOCK,
)
from app.models.device import Device
from app.models.lesson import Lesson, LessonRun
from app.mqtt.bridge import MqttBridge

LESSON_RUNNING = "running"

# Земля ≈ 24 ч → 12 с на оборот циферблата; крайние планеты не замирают и не мелькают.
EARTH_DAY_HOURS = 23.93
EARTH_VISUAL_SECONDS = 12.0
MIN_VISUAL_SECONDS = 4.0
MAX_VISUAL_SECONDS = 36.0

CLOCK_MODE_CATALOG: dict[str, dict[str, str]] = {
    CLOCK_MODE_IDLE: {
        "label": "Ожидание",
        "title": "Свободное посещение",
        "hint": "Все планеты идут в своём темпе. Дети сами замечают, где быстро, а где медленно.",
    },
    CLOCK_MODE_COMPARE: {
        "label": "Сравнение планет",
        "title": "Земля и Юпитер",
        "hint": "Сутки на Юпитере около 10 часов, на Земле — сутки. Луч Юпитера бежит заметно быстрее.",
    },
    CLOCK_MODE_RETROGRADE: {
        "label": "Ретроградное вращение",
        "title": "Венера и Уран",
        "hint": "Эти планеты вращаются «назад» относительно Земли — лучи идут против остальных.",
    },
    CLOCK_MODE_JUPITER: {
        "label": "Сутки Юпитера",
        "title": "Самый короткий день",
        "hint": "Среди планет зала у Юпитера самые короткие сутки. Квест: найдите самый быстрый луч.",
    },
}

# Сидерические сутки (часы). Знак минус — обратное вращение для детей.
PLANET_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "id": "mercury",
        "name": "Меркурий",
        "dayHours": 1407.6,
        "retrograde": False,
        "color": "#b8b8c8",
    },
    {
        "id": "venus",
        "name": "Венера",
        "dayHours": -5832.5,
        "retrograde": True,
        "color": "#e8c36a",
    },
    {
        "id": "earth",
        "name": "Земля",
        "dayHours": EARTH_DAY_HOURS,
        "retrograde": False,
        "color": "#4aa3ff",
    },
    {
        "id": "mars",
        "name": "Марс",
        "dayHours": 24.6,
        "retrograde": False,
        "color": "#d4653a",
    },
    {
        "id": "jupiter",
        "name": "Юпитер",
        "dayHours": 9.93,
        "retrograde": False,
        "color": "#d4a574",
    },
    {
        "id": "saturn",
        "name": "Сатурн",
        "dayHours": 10.7,
        "retrograde": False,
        "color": "#e6d9a8",
    },
    {
        "id": "uranus",
        "name": "Уран",
        "dayHours": -17.2,
        "retrograde": True,
        "color": "#7ee0d6",
    },
    {
        "id": "neptune",
        "name": "Нептун",
        "dayHours": 16.1,
        "retrograde": False,
        "color": "#5b7cff",
    },
)

MODE_HIGHLIGHTS: dict[str, frozenset[str]] = {
    CLOCK_MODE_IDLE: frozenset(),
    CLOCK_MODE_COMPARE: frozenset({"earth", "jupiter"}),
    CLOCK_MODE_RETROGRADE: frozenset({"venus", "uranus"}),
    CLOCK_MODE_JUPITER: frozenset({"jupiter"}),
}


class ClockError(Exception):
    """Ошибка режима часов с текстом для педагога."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def visual_seconds_for_day(day_hours: float) -> float:
    """Сжать реальные сутки в понятный оборот на экране.

    Args:
        day_hours: Сидерические сутки в часах (модуль).

    Returns:
        Длительность CSS/LED оборота в секундах.
    """

    raw = EARTH_VISUAL_SECONDS * (abs(day_hours) / EARTH_DAY_HOURS)
    return min(MAX_VISUAL_SECONDS, max(MIN_VISUAL_SECONDS, raw))


def day_hint(day_hours: float, retrograde: bool) -> str:
    """Короткая подпись длительности суток."""

    hours = abs(day_hours)
    if hours >= 48:
        days = hours / 24.0
        text = f"≈ {days:.0f} земных суток"
    else:
        text = f"≈ {hours:.1f} ч"
    if retrograde:
        return f"{text}, назад"
    return text


def remember_mode(device: Device, mode: str) -> None:
    """Записать ключ режима в extras, не затирая прочие поля.

    Args:
        device: Запись комплекса часов.
        mode: Ключ из CLOCK_MODES.
    """

    extras = dict(device.extras or {})
    extras[CLOCK_EXTRAS_MODE_KEY] = mode
    device.extras = extras
    flag_modified(device, "extras")


def remember_step(device: Device, command: str, payload: dict | None) -> None:
    """Запомнить команду занятия (set_mode или idle)."""

    if command == "idle":
        remember_mode(device, CLOCK_MODE_IDLE)
        return
    if command != "set_mode":
        return
    mode = (payload or {}).get("mode")
    if isinstance(mode, str) and mode in CLOCK_MODES:
        remember_mode(device, mode)


def _mode_from_extras(device: Device | None) -> str | None:
    """Ключ режима из extras или None."""

    if device is None or not device.extras:
        return None
    raw = device.extras.get(CLOCK_EXTRAS_MODE_KEY)
    if isinstance(raw, str) and raw in CLOCK_MODES:
        return raw
    return None


async def _mode_from_lesson(session: AsyncSession) -> str | None:
    """Ключ режима из шага текущего занятия или None."""

    result = await session.scalars(
        select(LessonRun)
        .options(selectinload(LessonRun.lesson).selectinload(Lesson.steps))
        .where(LessonRun.status == LESSON_RUNNING)
        .order_by(LessonRun.started_at.desc())
    )
    run = result.first()
    if run is None or run.lesson is None:
        return None
    for step in run.lesson.steps:
        if step.device_id != DEVICE_PLANET_CLOCK:
            continue
        if step.command == "idle":
            return CLOCK_MODE_IDLE
        if step.command != "set_mode":
            continue
        mode = (step.payload or {}).get("mode")
        if isinstance(mode, str) and mode in CLOCK_MODES:
            return mode
    return None


def planet_payloads(mode: str) -> list[dict[str, Any]]:
    """Планеты с подсветкой и скоростью луча для выбранного режима."""

    highlights = MODE_HIGHLIGHTS.get(mode, frozenset())
    idle = mode == CLOCK_MODE_IDLE
    planets: list[dict[str, Any]] = []
    for item in PLANET_CATALOG:
        planet_id = str(item["id"])
        highlighted = idle or planet_id in highlights
        planets.append(
            {
                "id": planet_id,
                "name": item["name"],
                "dayHours": item["dayHours"],
                "retrograde": bool(item["retrograde"]),
                "color": item["color"],
                "highlighted": highlighted,
                "visualSeconds": visual_seconds_for_day(float(item["dayHours"])),
                "dayHint": day_hint(float(item["dayHours"]), bool(item["retrograde"])),
            }
        )
    return planets


def modes_public() -> list[dict[str, str]]:
    """Кнопки режимов для пульта."""

    items: list[dict[str, str]] = []
    for mode_id in CLOCK_MODES:
        meta = CLOCK_MODE_CATALOG[mode_id]
        items.append(
            {
                "id": mode_id,
                "label": meta["title"],
                "hint": meta["hint"],
            }
        )
    return items


async def resolve_mode(session: AsyncSession) -> str:
    """Текущий режим: ручная команда, иначе шаг занятия, иначе ожидание."""

    device = await session.get(Device, DEVICE_PLANET_CLOCK)
    extras_mode = _mode_from_extras(device)
    if extras_mode is not None:
        return extras_mode
    lesson_mode = await _mode_from_lesson(session)
    if lesson_mode is not None:
        return lesson_mode
    return CLOCK_MODE_IDLE


async def clock_state(session: AsyncSession, mqtt_connected: bool) -> dict[str, Any]:
    """Собрать состояние циферблата для пульта.

    Args:
        session: Сессия БД.
        mqtt_connected: Жив ли брокер ядра.

    Returns:
        JSON-словарь для API.
    """

    mode = await resolve_mode(session)
    meta = CLOCK_MODE_CATALOG[mode]
    return {
        "deviceId": DEVICE_PLANET_CLOCK,
        "mode": mode,
        "label": meta["label"],
        "title": meta["title"],
        "hint": meta["hint"],
        "mqttConnected": mqtt_connected,
        "planets": planet_payloads(mode),
        "modes": modes_public(),
    }


def command_payload(mode: str) -> dict[str, str]:
    """Тело MQTT-команды для ESP32."""

    if mode == CLOCK_MODE_IDLE:
        return {"command": "idle"}
    return {"command": "set_mode", "mode": mode}


async def apply_mode(session: AsyncSession, mqtt: MqttBridge, mode: str) -> dict[str, Any]:
    """Переключить часы с пульта: MQTT + режим на карточке.

    Args:
        session: Сессия БД.
        mqtt: Мост команд.
        mode: Ключ режима.

    Returns:
        Новое состояние циферблата.

    Raises:
        ClockError: Неизвестный режим или нет часов в реестре.
    """

    if mode not in CLOCK_MODES:
        raise ClockError("Такого режима у часов нет")

    device = await session.get(Device, DEVICE_PLANET_CLOCK)
    if device is None:
        raise ClockError("Часы не найдены в реестре", status_code=404)

    # Пишем ключ и подпись, как после шага занятия.
    remember_mode(device, mode)
    device.current_mode = CLOCK_MODE_CATALOG[mode]["label"]
    mqtt.publish_command(
        DEVICE_PLANET_CLOCK,
        json.dumps(command_payload(mode), ensure_ascii=False),
    )
    await session.commit()
    return await clock_state(session, mqtt.connected)
