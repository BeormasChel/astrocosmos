"""Хеширование паролей (PBKDF2) и JWT."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import get_settings

ALGORITHM = "HS256"
_PBKDF2_ITERATIONS = 120_000
_HASH_PREFIX = "pbkdf2_sha256"


def hash_password(plain_password: str) -> str:
    """Посчитать устойчивый хеш пароля.

    Args:
        plain_password: Пароль в открытом виде.

    Returns:
        Строка ``pbkdf2_sha256$iterations$salt$digest``.
    """

    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        _PBKDF2_ITERATIONS,
    )
    return f"{_HASH_PREFIX}${_PBKDF2_ITERATIONS}${salt}${digest.hex()}"


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Сверить пароль с сохранённым хешем.

    Args:
        plain_password: Введённый пароль.
        password_hash: Хеш из базы.

    Returns:
        True, если пароль совпадает.
    """

    try:
        scheme, iter_s, salt, digest_hex = password_hash.split("$")
        if scheme != _HASH_PREFIX:
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iter_s),
        )
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Собрать JWT для пользователя с идентификатором `subject`.

    Args:
        subject: Логин пользователя.
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


def decode_access_token(token: str) -> str | None:
    """Извлечь логин из JWT.

    Args:
        token: Строка Bearer-токена.

    Returns:
        Логин или None, если токен невалиден.
    """

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return None
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        return None
    return subject
