"""Асинхронный SQLAlchemy: движок и сессии."""

from collections.abc import AsyncIterator
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.models.base import Base

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _ensure_sqlite_directory(url: str) -> None:
    """Создать папку для файла SQLite, если URL указывает на файл."""

    if not url.startswith("sqlite") or ":memory:" in url:
        return
    prefix = "sqlite+aiosqlite:///"
    if url.startswith(prefix):
        relative = url.removeprefix(prefix)
        path = Path(relative)
        if str(path.parent) not in ("", "."):
            path.parent.mkdir(parents=True, exist_ok=True)


def reset_engine() -> None:
    """Сбросить движок (нужно тестам после смены DATABASE_URL)."""

    global _engine, _session_factory
    _engine = None
    _session_factory = None


def get_engine() -> AsyncEngine:
    """Вернуть (или создать) async-движок."""

    global _engine, _session_factory
    if _engine is None:
        settings = get_settings()
        _ensure_sqlite_directory(settings.database_url)
        _engine = create_async_engine(settings.database_url, echo=False)
        _session_factory = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Фабрика сессий, привязанная к текущему движку."""

    get_engine()
    assert _session_factory is not None
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """Выдать сессию БД для запроса FastAPI."""

    factory = get_session_factory()
    async with factory() as session:
        yield session


async def init_database() -> None:
    """Создать таблицы при старте (локальный SQLite и первый деплой)."""

    from app import models  # noqa: F401

    engine = get_engine()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
