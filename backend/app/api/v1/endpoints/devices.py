"""Реестр и мониторинг комплексов."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_devices() -> dict[str, list]:
    """Вернуть список зарегистрированных устройств.

    Returns:
        Пустой список до реализации сервиса устройств.
    """

    return {"items": []}
