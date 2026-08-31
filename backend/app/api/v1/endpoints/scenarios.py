"""Запуск и остановка образовательных сценариев."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_scenarios() -> dict[str, list]:
    """Вернуть каталог сценариев.

    Returns:
        Пустой список до реализации движка сценариев.
    """

    return {"items": []}
