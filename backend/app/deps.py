"""Зависимости FastAPI: сессия, текущий пользователь, MQTT."""

from collections.abc import AsyncIterator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ROLE_ADMIN, ROLE_EDUCATOR
from app.core.database import get_session_factory
from app.core.security import decode_access_token
from app.models.user import User
from app.mqtt.bridge import MqttBridge

bearer_scheme = HTTPBearer(auto_error=False)

CAN_START_LESSON = {ROLE_ADMIN, ROLE_EDUCATOR}
CAN_EDIT_MATERIALS = {ROLE_ADMIN, ROLE_EDUCATOR}


async def get_db() -> AsyncIterator[AsyncSession]:
    """Сессия БД на время HTTP-запроса."""

    factory = get_session_factory()
    async with factory() as session:
        yield session


def get_mqtt(request: Request) -> MqttBridge:
    """Мост MQTT, созданный в lifespan."""

    return request.app.state.mqtt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Прочитать Bearer JWT и найти активного пользователя.

    Raises:
        HTTPException: 401 если токена нет или он просрочен.
    """

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Нужен вход",
        )
    login = decode_access_token(credentials.credentials)
    if login is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сессия истекла, войдите снова",
        )
    user = await session.scalar(select(User).where(User.login == login))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь недоступен",
        )
    return user


async def require_lesson_control(user: User = Depends(get_current_user)) -> User:
    """Разрешить старт/стоп занятий педагогу и администратору."""

    if user.role not in CAN_START_LESSON:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Смотритель может смотреть зал, но не запускать занятия",
        )
    return user


async def require_material_edit(user: User = Depends(get_current_user)) -> User:
    """Разрешить добавление и правку материалов педагогу и администратору."""

    if user.role not in CAN_EDIT_MATERIALS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Смотритель может смотреть материалы, но не менять их",
        )
    return user
