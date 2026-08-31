"""Проверка живости ядра (для Docker/Nginx и админки)."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    """Вернуть статус процесса API.

    Returns:
        Словарь с полем `status`.
    """

    return {"status": "ok", "service": "astrocosmos-core"}
