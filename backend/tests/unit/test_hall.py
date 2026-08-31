"""Учебный стенд: комплексы зала на связи без железа."""

from tests.conftest import auth_header


def test_hall_stand_is_off_in_tests(client) -> None:
    """В автотестах стенд выключен, чтобы статусы не зеленели сами."""

    headers = auth_header(client)
    hall = client.get("/api/v1/hall", headers=headers)
    assert hall.status_code == 200
    body = hall.json()
    assert body["standEnabled"] is False
    assert body["hallCount"] == 6
    assert body["onlineCount"] == 0


def test_pulse_marks_all_hall_devices_online(client) -> None:
    """Пульс стенда включает шесть комплексов зала, тумбу отдельно не создаёт."""

    headers = auth_header(client)
    pulse = client.post("/api/v1/hall/pulse", headers=headers)
    assert pulse.status_code == 200, pulse.text
    pulsed = set(pulse.json()["pulsed"])
    assert pulsed == {
        "maly_golobox",
        "bolshoy_golobox",
        "desktop_diptych",
        "planet_clock",
        "illuminator",
        "astrovizor",
    }
    assert "observatory" not in pulsed

    devices = client.get("/api/v1/devices", headers=headers).json()
    assert len(devices) == 6
    assert all(item["status"] == "online" for item in devices)
    hall = client.get("/api/v1/hall", headers=headers).json()
    assert hall["onlineCount"] == 6


def test_attendant_cannot_pulse(client) -> None:
    """Смотритель видит зал, но не запускает стенд."""

    headers = auth_header(client, login="attendant", password="attendant")
    listing = client.get("/api/v1/hall", headers=headers)
    assert listing.status_code == 200
    pulse = client.post("/api/v1/hall/pulse", headers=headers)
    assert pulse.status_code == 403
