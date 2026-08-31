"""Общие фикстуры pytest: временная SQLite и TestClient с lifespan."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Поднять приложение на чистой БД для каждого теста."""

    database_path = tmp_path / "test.db"
    media_path = tmp_path / "media"
    media_path.mkdir()
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path.as_posix()}")
    monkeypatch.setenv("MEDIA_ROOT", str(media_path))
    monkeypatch.setenv("SCHEDULE_TICKER_ENABLED", "false")
    monkeypatch.setenv("HALL_EMULATOR_ENABLED", "false")

    from app.core.config import get_settings
    from app.core.database import reset_engine

    get_settings.cache_clear()
    reset_engine()

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    reset_engine()
    get_settings.cache_clear()


def auth_header(client: TestClient, login: str = "educator", password: str = "educator") -> dict[str, str]:
    """Получить заголовок Authorization для роли."""

    response = client.post("/api/v1/auth/login", json={"login": login, "password": password})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
