"""Киоск иллюминатора: Attract Mode и ролик занятия."""

from io import BytesIO

from tests.conftest import auth_header


def test_illuminator_attract_when_idle(client) -> None:
    """Без занятия окно в Attract: в каталоге ключи welcome и impact."""

    response = client.get("/api/v1/kiosk/illuminator")
    assert response.status_code == 200
    body = response.json()
    assert body["deviceId"] == "illuminator"
    assert body["mode"] == "attract"
    keys = {item["clipKey"] for item in body["attract"]}
    assert "welcome" in keys
    assert "impact" in keys


def test_illuminator_plays_clip_from_lesson(client) -> None:
    """Старт занятия переключает окно на ролик welcome."""

    headers = auth_header(client)
    started = client.post("/api/v1/lessons/welcome/start", headers=headers)
    assert started.status_code == 200

    window = client.get("/api/v1/kiosk/illuminator")
    assert window.status_code == 200
    body = window.json()
    assert body["mode"] == "play"
    assert body["clip"]["clipKey"] == "welcome"
    assert body["clip"]["hasFile"] is False

    client.post("/api/v1/lessons/stop", headers=headers)
    idle = client.get("/api/v1/kiosk/illuminator").json()
    assert idle["mode"] == "attract"


def test_illuminator_media_after_upload(client) -> None:
    """После загрузки файла киоск отдаёт ролик без JWT."""

    headers = auth_header(client)
    uploaded = client.post(
        "/api/v1/materials",
        headers=headers,
        data={
            "title": "Вид с МКС",
            "kind": "video",
            "device_id": "illuminator",
            "clip_key": "iss_view",
        },
        files={"file": ("iss.mp4", BytesIO(b"\x00\x00kiosk-mp4"), "video/mp4")},
    )
    assert uploaded.status_code == 201, uploaded.text

    media = client.get("/api/v1/kiosk/illuminator/media/iss_view")
    assert media.status_code == 200
    assert media.content.startswith(b"\x00\x00kiosk-mp4")

    missing = client.get("/api/v1/kiosk/illuminator/media/welcome")
    assert missing.status_code == 404
