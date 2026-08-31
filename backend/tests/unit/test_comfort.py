"""Заглушка комфорта: без URL Home Assistant шаги пропускаются."""

from tests.conftest import auth_header


def test_comfort_disabled_on_stand(client) -> None:
    """Пустой HA_BASE_URL — свет и жалюзи не подключены."""

    headers = auth_header(client)
    status = client.get("/api/v1/comfort/status", headers=headers)
    assert status.status_code == 200
    body = status.json()
    assert body["enabled"] is False
    assert "не подключены" in body["hint"]


def test_comfort_command_skipped(client) -> None:
    """Команда комфорта на стенде не падает и помечается как пропуск."""

    headers = auth_header(client)
    response = client.post(
        "/api/v1/comfort/command",
        headers=headers,
        json={"domain": "light", "service": "turn_off", "payload": {"entity_id": "light.hall"}},
    )
    assert response.status_code == 200, response.text
    assert response.json()["ok"] is True
    assert response.json()["skipped"] is True


def test_attendant_cannot_command_comfort(client) -> None:
    """Смотритель не гасит свет из пульта."""

    headers = auth_header(client, login="attendant", password="attendant")
    response = client.post(
        "/api/v1/comfort/command",
        headers=headers,
        json={"domain": "light", "service": "turn_off", "payload": {}},
    )
    assert response.status_code == 403
