"""Аутентификация администраторов и педагогов. Заглушка MVP."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login() -> dict[str, str]:
    """Выдать JWT (пока заглушка).

    Returns:
        Сообщение о том, что эндпоинт ещё не реализован.
    """

    return {"detail": "not_implemented"}
