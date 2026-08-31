"""Заготовки аутентификации (JWT). Реализация — этап MVP-1."""

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import get_settings

ALGORITHM = "HS256"


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Собрать JWT для пользователя с идентификатором `subject`.

    Args:
        subject: Уникальный идентификатор пользователя.
        expires_delta: Срок жизни токена. Если не задан, берётся из настроек.

    Returns:
        Строка JWT.
    """

    settings = get_settings()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
