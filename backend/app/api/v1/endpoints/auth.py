"""Вход в пульт педагога."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models.user import User
from app.core.security import create_access_token, verify_password
from app.schemas.auth import LoginRequest, TokenResponse, UserPublic

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Проверить логин/пароль и выдать JWT.

    Args:
        body: Учётные данные.
        session: Сессия БД.

    Returns:
        Токен и профиль.
    """

    user = await session.scalar(select(User).where(User.login == body.login))
    if (
        user is None
        or not user.is_active
        or not verify_password(body.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    token = create_access_token(user.login)
    return TokenResponse(
        access_token=token,
        user=UserPublic(login=user.login, full_name=user.full_name, role=user.role),
    )


@router.get("/me", response_model=UserPublic)
async def read_me(user: User = Depends(get_current_user)) -> UserPublic:
    """Вернуть профиль текущей сессии."""

    return UserPublic(login=user.login, full_name=user.full_name, role=user.role)
