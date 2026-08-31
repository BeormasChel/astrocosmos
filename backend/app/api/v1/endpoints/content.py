"""Управление медиа и текстовым контентом."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_content() -> dict[str, list]:
    """Вернуть метаданные контента.

    Returns:
        Пустой список до реализации CMS.
    """

    return {"items": []}
