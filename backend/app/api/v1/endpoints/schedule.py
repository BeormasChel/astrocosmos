"""Расписание занятий и автоматический запуск сценариев."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_schedule() -> dict[str, list]:
    """Вернуть расписание.

    Returns:
        Пустой список до реализации планировщика.
    """

    return {"items": []}
