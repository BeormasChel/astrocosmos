"""Состояние окна иллюминатора для киоска Pi."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import DEVICE_ILLUMINATOR
from app.models.lesson import Lesson, LessonRun
from app.services import material_service
from app.services.lesson_service import RUN_RUNNING
from app.services.material_service import MaterialError

KIOSK_MEDIA_PREFIX = "/api/v1/kiosk/illuminator/media"


def _clip_payload(material) -> dict:
    """Карточка ролика для киоска."""

    clip_key = material.clip_key or material.id
    has_file = bool(material.stored_name)
    return {
        "clipKey": clip_key,
        "title": material.title,
        "hasFile": has_file,
        "videoUrl": f"{KIOSK_MEDIA_PREFIX}/{clip_key}" if has_file else None,
    }


async def current_play_clip(session: AsyncSession) -> str | None:
    """Ключ ролика из текущего занятия или None в Attract Mode."""

    result = await session.scalars(
        select(LessonRun)
        .options(selectinload(LessonRun.lesson).selectinload(Lesson.steps))
        .where(LessonRun.status == RUN_RUNNING)
        .order_by(LessonRun.started_at.desc())
    )
    run = result.first()
    if run is None or run.lesson is None:
        return None
    for step in run.lesson.steps:
        if step.device_id != DEVICE_ILLUMINATOR:
            continue
        if step.command != "play":
            continue
        clip = (step.payload or {}).get("clip")
        if isinstance(clip, str) and clip.strip():
            return clip.strip()
    return None


async def illuminator_window_state(session: AsyncSession) -> dict:
    """Собрать, что должно быть в окне: attract или ролик занятия.

    Returns:
        Состояние киоска без JWT (локальная сеть зала).
    """

    play_key = await current_play_clip(session)
    catalog = await material_service.list_video_clips_for_device(
        session,
        DEVICE_ILLUMINATOR,
    )
    attract = [_clip_payload(item) for item in catalog]
    current = None
    mode = "attract"
    if play_key:
        mode = "play"
        material = await material_service.get_clip_for_device(
            session,
            play_key,
            DEVICE_ILLUMINATOR,
        )
        if material is not None:
            current = _clip_payload(material)
        else:
            current = {
                "clipKey": play_key,
                "title": play_key,
                "hasFile": False,
                "videoUrl": None,
            }
    elif attract:
        current = attract[0]

    return {
        "deviceId": DEVICE_ILLUMINATOR,
        "mode": mode,
        "clip": current,
        "attract": attract,
    }


async def open_illuminator_clip_file(session: AsyncSession, clip_key: str):
    """Файл ролика для <video> без входа в пульт.

    Raises:
        MaterialError: Нет ролика или нет файла.
    """

    material = await material_service.get_clip_for_device(
        session,
        clip_key,
        DEVICE_ILLUMINATOR,
    )
    if material is None:
        raise MaterialError("Такого ролика нет", status_code=404)
    return material, material_service.open_material_file(material)
