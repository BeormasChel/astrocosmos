"""Режимы астрономических часов с пульта и из занятия."""

from tests.conftest import auth_header


def test_clocks_idle_by_default(client) -> None:
    """Без занятия циферблат в свободном посещении."""

    headers = auth_header(client)
    response = client.get("/api/v1/clocks", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["deviceId"] == "planet_clock"
    assert body["mode"] == "idle"
    ids = {item["id"] for item in body["planets"]}
    assert "earth" in ids
    assert "jupiter" in ids
    assert {item["id"] for item in body["modes"]} >= {"idle", "compare", "retrograde"}


def test_welcome_lesson_sets_compare_mode(client) -> None:
    """Занятие «Знакомство» подсвечивает Землю и Юпитер."""

    headers = auth_header(client)
    started = client.post("/api/v1/lessons/welcome/start", headers=headers)
    assert started.status_code == 200

    clocks = client.get("/api/v1/clocks", headers=headers)
    assert clocks.status_code == 200
    body = clocks.json()
    assert body["mode"] == "compare"
    by_id = {item["id"]: item for item in body["planets"]}
    assert by_id["earth"]["highlighted"] is True
    assert by_id["jupiter"]["highlighted"] is True
    assert by_id["venus"]["highlighted"] is False

    devices = client.get("/api/v1/devices", headers=headers).json()
    clock = next(item for item in devices if item["id"] == "planet_clock")
    assert clock["currentMode"] == "Сравнение планет"

    client.post("/api/v1/lessons/stop", headers=headers)
    idle = client.get("/api/v1/clocks", headers=headers).json()
    assert idle["mode"] == "idle"


def test_educator_sets_retrograde_from_panel(client) -> None:
    """Педагог с пульта включает ретроград без занятия."""

    headers = auth_header(client)
    response = client.post("/api/v1/clocks/mode", headers=headers, json={"mode": "retrograde"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["mode"] == "retrograde"
    by_id = {item["id"]: item for item in body["planets"]}
    assert by_id["venus"]["highlighted"] is True
    assert by_id["uranus"]["highlighted"] is True
    assert by_id["venus"]["retrograde"] is True

    devices = client.get("/api/v1/devices", headers=headers).json()
    clock = next(item for item in devices if item["id"] == "planet_clock")
    assert clock["currentMode"] == "Ретроградное вращение"


def test_unknown_clock_mode_rejected(client) -> None:
    """Неизвестный режим не уходит на ленту."""

    headers = auth_header(client)
    response = client.post("/api/v1/clocks/mode", headers=headers, json={"mode": "pluto"})
    assert response.status_code == 400


def test_attendant_cannot_set_clock_mode(client) -> None:
    """Смотритель смотрит циферблат, но не переключает режим."""

    headers = auth_header(client, login="attendant", password="attendant")
    visible = client.get("/api/v1/clocks", headers=headers)
    assert visible.status_code == 200
    forbidden = client.post("/api/v1/clocks/mode", headers=headers, json={"mode": "compare"})
    assert forbidden.status_code == 403
