"""Вход и роли пульта."""

from tests.conftest import auth_header


def test_login_educator(client) -> None:
    """Педагог входит с демо-паролем."""

    response = client.post(
        "/api/v1/auth/login",
        json={"login": "educator", "password": "educator"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["role"] == "educator"
    assert body["access_token"]


def test_login_rejects_bad_password(client) -> None:
    """Неверный пароль не выдаёт токен."""

    response = client.post(
        "/api/v1/auth/login",
        json={"login": "educator", "password": "wrong"},
    )
    assert response.status_code == 401


def test_attendant_cannot_start_lesson(client) -> None:
    """Смотритель видит зал, но не запускает занятие."""

    headers = auth_header(client, "attendant", "attendant")
    response = client.post("/api/v1/lessons/welcome/start", headers=headers)
    assert response.status_code == 403
