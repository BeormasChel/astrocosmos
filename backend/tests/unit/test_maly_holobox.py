"""Киоск малого голобокса: разделы занятия и ролики."""

from io import BytesIO

from tests.conftest import auth_header


def test_maly_attract_lists_six_sections(client) -> None:
    """Без занятия киоск в Attract: шесть разделов, intro и structure на полке."""

    response = client.get("/api/v1/kiosk/maly")
    assert response.status_code == 200
    body = response.json()
    assert body["deviceId"] == "maly_golobox"
    assert body["mode"] == "attract"
    assert body["lessonLocked"] is False
    assert body["idleSeconds"] == 60
    ids = {item["id"] for item in body["sections"]}
    assert ids == {"intro", "structure", "fall", "history", "map", "compare"}
    by_id = {item["id"]: item for item in body["sections"]}
    assert by_id["intro"]["hasFile"] is False
    assert by_id["structure"]["title"] == "Строение"


def test_welcome_lesson_opens_intro(client) -> None:
    """Занятие «Знакомство» открывает раздел Введение."""

    headers = auth_header(client)
    started = client.post("/api/v1/lessons/welcome/start", headers=headers)
    assert started.status_code == 200

    window = client.get("/api/v1/kiosk/maly")
    assert window.status_code == 200
    body = window.json()
    assert body["mode"] == "section"
    assert body["lessonLocked"] is True
    assert body["section"]["id"] == "intro"

    client.post("/api/v1/lessons/stop", headers=headers)
    idle = client.get("/api/v1/kiosk/maly").json()
    assert idle["mode"] == "attract"
    assert idle["lessonLocked"] is False


def test_meteorite_lesson_opens_structure(client) -> None:
    """Занятие про метеорит открывает «Строение»."""

    headers = auth_header(client)
    started = client.post("/api/v1/lessons/meteorite/start", headers=headers)
    assert started.status_code == 200
    body = client.get("/api/v1/kiosk/maly").json()
    assert body["section"]["id"] == "structure"
    client.post("/api/v1/lessons/stop", headers=headers)


def test_maly_media_after_upload(client) -> None:
    """После загрузки файла киоск отдаёт ролик раздела без JWT."""

    headers = auth_header(client)
    uploaded = client.post(
        "/api/v1/materials",
        headers=headers,
        data={
            "title": "Строение, ролик",
            "kind": "video",
            "device_id": "maly_golobox",
            "clip_key": "structure",
        },
        files={"file": ("layer.mp4", BytesIO(b"\x00\x00maly-mp4"), "video/mp4")},
    )
    assert uploaded.status_code == 201, uploaded.text

    media = client.get("/api/v1/kiosk/maly/media/structure")
    assert media.status_code == 200
    assert media.content.startswith(b"\x00\x00maly-mp4")

    missing = client.get("/api/v1/kiosk/maly/media/intro")
    assert missing.status_code == 404
