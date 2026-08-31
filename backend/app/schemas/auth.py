"""Схемы входа."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Логин и пароль пульта."""

    login: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class UserPublic(BaseModel):
    """Публичный профиль без пароля."""

    login: str
    full_name: str
    role: str


class TokenResponse(BaseModel):
    """JWT и сведения о пользователе после входа."""

    access_token: str
    token_type: str = "bearer"
    user: UserPublic
