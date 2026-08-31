"""Первичное наполнение БД пользователями, комплексами и занятиями."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.device import Device
from app.models.lesson import Lesson, LessonStep
from app.models.material import Material
from app.models.user import User
from app.services.catalog import (
    DEVICE_CATALOG,
    EXAMPLE_MATERIALS,
    LESSON_CATALOG,
    USER_CATALOG,
)


async def seed_if_empty(session: AsyncSession) -> None:
    """Заполнить справочники, если таблица пользователей пуста."""

    existing = await session.scalar(select(User.id).limit(1))
    if existing is not None:
        return

    # Учётные записи пульта (пароли только для локального стенда).
    for item in USER_CATALOG:
        session.add(
            User(
                login=item["login"],
                full_name=item["full_name"],
                role=item["role"],
                password_hash=hash_password(item["password"]),
                is_active=True,
            )
        )

    for item in DEVICE_CATALOG:
        session.add(
            Device(
                id=item["id"],
                number=item["number"],
                name=item["name"],
                purpose=item["purpose"],
                platform=item["platform"],
                current_mode="Ещё не подключался",
                extras=item["extras"],
            )
        )

    await session.flush()

    for lesson_item in LESSON_CATALOG:
        lesson = Lesson(
            id=lesson_item["id"],
            title=lesson_item["title"],
            duration_min=lesson_item["duration_min"],
            for_whom=lesson_item["for_whom"],
        )
        session.add(lesson)
        for index, step in enumerate(lesson_item["steps"], start=1):
            session.add(
                LessonStep(
                    lesson_id=lesson.id,
                    sort_order=index,
                    device_id=step["device_id"],
                    command=step["command"],
                    payload=step["payload"],
                    mode_label=step["mode_label"],
                )
            )

    await session.commit()


async def seed_example_materials_if_empty(session: AsyncSession) -> None:
    """Положить примеры роликов и текстов, если полка материалов пуста."""

    existing = await session.scalar(select(Material.id).limit(1))
    if existing is not None:
        return

    now = datetime.now(timezone.utc)
    for item in EXAMPLE_MATERIALS:
        session.add(
            Material(
                id=item["id"],
                kind=item["kind"],
                title=item["title"],
                body=item["body"],
                device_id=item["device_id"],
                clip_key=item["clip_key"],
                rfid_uid=item["rfid_uid"],
                created_by=item["created_by"],
                created_at=now,
            )
        )
    await session.commit()
