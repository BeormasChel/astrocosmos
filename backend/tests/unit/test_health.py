"""Проверка health-эндпоинта без БД и MQTT."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    """Healthcheck должен отвечать 200 и status=ok."""

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
