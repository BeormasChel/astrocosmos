"""Состояние малого голобокса: разделы занятия и ролики для киоска."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import (
    DEVICE_MALY_GOLOBOX,
    HOLOBOX_IDLE_SECONDS,
    HOLOBOX_SECTION_COMPARE,
    HOLOBOX_SECTION_FALL,
    HOLOBOX_SECTION_HISTORY,
    HOLOBOX_SECTION_INTRO,
    HOLOBOX_SECTION_MAP,
    HOLOBOX_SECTION_STRUCTURE,
)
from app.models.lesson import Lesson, LessonRun
from app.services import material_service
from app.services.material_service import MaterialError

LESSON_RUNNING = "running"
KIOSK_MEDIA_PREFIX = "/api/v1/kiosk/maly/media"

# Шесть разделов экспоната. 3D-метеорит (glTF) — следующий срез, сейчас видео + тач.
HOLOBOX_SECTION_CATALOG: tuple[dict[str, str], ...] = (
    {
        "id": HOLOBOX_SECTION_INTRO,
        "title": "Введение",
        "hint": "Камень перед вами — осколок Челябинского метеорита.",
    },
    {
        "id": HOLOBOX_SECTION_STRUCTURE,
        "title": "Строение",
        "hint": "Из чего состоит метеорит: кора, хондры, металл.",
    },
    {
        "id": HOLOBOX_SECTION_FALL,
        "title": "Падение",
        "hint": "15 февраля 2013 года. Вспышка, ударная волна, озеро Чебаркуль.",
    },
    {
        "id": HOLOBOX_SECTION_HISTORY,
        "title": "История",
        "hint": "От вспышки над городом до витрины в зале.",
    },
    {
        "id": HOLOBOX_SECTION_MAP,
        "title": "Карта падений",
        "hint": "Где в России находили метеориты.",
    },
    {
        "id": HOLOBOX_SECTION_COMPARE,
        "title": "Размеры",
        "hint": "Челябинск рядом с Тунгуской и «большим» ударом.",
    },
)


async def current_lesson_section(session: AsyncSession) -> str | None:
    """Ключ раздела из занятия или None, если зал свободен."""

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
        if step.device_id != DEVICE_MALY_GOLOBOX:
            continue
        if step.command != "open_section":
            continue
        section = (step.payload or {}).get("section")
        if isinstance(section, str) and section.strip():
            return section.strip()
    return None


def _spec_by_id(section_id: str) -> dict[str, str] | None:
    """Найти описание раздела в каталоге."""

    for item in HOLOBOX_SECTION_CATALOG:
        if item["id"] == section_id:
            return item
    return None


async def _section_payload(session: AsyncSession, spec: dict[str, str]) -> dict[str, Any]:
    """Карточка раздела: подпись и ссылка на ролик, если файл есть."""

    section_id = spec["id"]
    material = await material_service.get_clip_for_device(
        session,
        section_id,
        DEVICE_MALY_GOLOBOX,
    )
    has_file = bool(material and material.stored_name)
    return {
        "id": section_id,
        "title": spec["title"],
        "hint": spec["hint"],
        "hasFile": has_file,
        "videoUrl": f"{KIOSK_MEDIA_PREFIX}/{section_id}" if has_file else None,
    }


async def holobox_window_state(session: AsyncSession) -> dict[str, Any]:
    """Собрать меню разделов и раздел занятия, если занятие идёт.

    Returns:
        Состояние киоска без JWT (локальная сеть зала).
    """

    sections = [await _section_payload(session, spec) for spec in HOLOBOX_SECTION_CATALOG]
    lesson_section = await current_lesson_section(session)
    current = None
    if lesson_section:
        current = next((item for item in sections if item["id"] == lesson_section), None)
        if current is None:
            spec = _spec_by_id(lesson_section)
            title = spec["title"] if spec else lesson_section
            hint = spec["hint"] if spec else ""
            current = {
                "id": lesson_section,
                "title": title,
                "hint": hint,
                "hasFile": False,
                "videoUrl": None,
            }

    return {
        "deviceId": DEVICE_MALY_GOLOBOX,
        "mode": "section" if lesson_section else "attract",
        "lessonLocked": bool(lesson_section),
        "idleSeconds": HOLOBOX_IDLE_SECONDS,
        "section": current,
        "sections": sections,
    }


async def open_holobox_section_file(session: AsyncSession, section_id: str):
    """Файл ролика раздела для HTML5-плеера.

    Raises:
        MaterialError: Нет ролика или нет файла.
    """

    material = await material_service.get_clip_for_device(
        session,
        section_id,
        DEVICE_MALY_GOLOBOX,
    )
    if material is None:
        raise MaterialError("Такого раздела нет", status_code=404)
    return material, material_service.open_material_file(material)
