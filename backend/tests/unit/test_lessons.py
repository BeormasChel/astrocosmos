"""Запуск и остановка занятий."""

from tests.conftest import auth_header


def test_list_devices(client) -> None:
    """В реестре шесть комплексов зала."""

    headers = auth_header(client)
    response = client.get("/api/v1/devices", headers=headers)
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()}
    assert "maly_golobox" in ids
    assert "bolshoy_golobox" in ids
    assert len(ids) == 6


def test_start_and_stop_lesson(client) -> None:
    """Педагог запускает занятие — комплексы меняют режим — затем стоп."""

    headers = auth_header(client)
    started = client.post("/api/v1/lessons/welcome/start", headers=headers)
    assert started.status_code == 200
    body = started.json()
    assert body["status"] == "running"
    assert body["lessonId"] == "welcome"

    devices = client.get("/api/v1/devices", headers=headers).json()
    by_id = {item["id"]: item for item in devices}
    assert by_id["illuminator"]["currentMode"] == "Ролик «Знакомство»"

    active = client.get("/api/v1/lessons/active", headers=headers)
    assert active.json()["lessonId"] == "welcome"

    stopped = client.post("/api/v1/lessons/stop", headers=headers)
    assert stopped.status_code == 200
    assert stopped.json()["status"] == "stopped"

    after = client.get("/api/v1/devices", headers=headers).json()
    by_id = {item["id"]: item for item in after}
    assert by_id["illuminator"]["currentMode"] == "Ожидание"


def test_heartbeat_marks_online(client) -> None:
    """Агент киоска помечает комплекс на связи."""

    headers = auth_header(client)
    ping = client.post("/api/v1/devices/planet_clock/heartbeat")
    assert ping.status_code == 200
    devices = client.get("/api/v1/devices", headers=headers).json()
    clock = next(item for item in devices if item["id"] == "planet_clock")
    assert clock["status"] == "online"
