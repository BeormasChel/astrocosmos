"""Проверка health-эндпоинта."""


def test_health_returns_ok(client) -> None:
    """Healthcheck должен отвечать 200 и status=ok."""

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
