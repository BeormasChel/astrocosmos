"""Каталог материалов: ролики, тексты, учёные."""

from io import BytesIO

from tests.conftest import auth_header


def test_list_seeded_materials(client) -> None:
    """На пустой полке сразу видны примеры для педагога."""

    headers = auth_header(client)
    response = client.get("/api/v1/materials", headers=headers)
    assert response.status_code == 200
    titles = {item["title"] for item in response.json()}
    assert "Знакомство с кораблём" in titles
    assert "Юрий Гагарин" in titles


def test_create_text_and_upload_video(client) -> None:
    """Педагог добавляет текст и ролик с файлом."""

    headers = auth_header(client)
    text = client.post(
        "/api/v1/materials",
        headers=headers,
        data={
            "title": "Почему небо чёрное",
            "kind": "text",
            "device_id": "maly_golobox",
            "body": "В космосе нет воздуха, который рассеивал бы свет.",
        },
    )
    assert text.status_code == 201, text.text
    assert text.json()["kindLabel"] == "Текст"
    assert text.json()["hasFile"] is False

    video = client.post(
        "/api/v1/materials",
        headers=headers,
        data={
            "title": "Вид с МКС",
            "kind": "video",
            "device_id": "illuminator",
            "clip_key": "iss_view",
        },
        files={"file": ("iss.mp4", BytesIO(b"\x00\x00fake-mp4"), "video/mp4")},
    )
    assert video.status_code == 201, video.text
    body = video.json()
    assert body["hasFile"] is True
    assert body["clipKey"] == "iss_view"
    material_id = body["id"]

    downloaded = client.get(f"/api/v1/materials/{material_id}/file", headers=headers)
    assert downloaded.status_code == 200
    assert downloaded.content.startswith(b"\x00\x00fake-mp4")


def test_scientist_needs_rfid_and_unique(client) -> None:
    """Учёный без метки не сохраняется, повтор UID отклоняется."""

    headers = auth_header(client)
    missing = client.post(
        "/api/v1/materials",
        headers=headers,
        data={"title": "Циолковский", "kind": "scientist", "device_id": "bolshoy_golobox"},
    )
    assert missing.status_code == 400

    created = client.post(
        "/api/v1/materials",
        headers=headers,
        data={
            "title": "Циолковский",
            "kind": "scientist",
            "device_id": "bolshoy_golobox",
            "rfid_uid": "04:aa:11:22",
            "body": "Константин Эдуардович Циолковский.",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["rfidUid"] == "04AA1122"

    duplicate = client.post(
        "/api/v1/materials",
        headers=headers,
        data={
            "title": "Другой",
            "kind": "scientist",
            "rfid_uid": "04AA1122",
        },
    )
    assert duplicate.status_code == 409


def test_attendant_can_read_not_write(client) -> None:
    """Смотритель видит полку, но не добавляет и не удаляет."""

    headers = auth_header(client, login="attendant", password="attendant")
    listing = client.get("/api/v1/materials", headers=headers)
    assert listing.status_code == 200

    created = client.post(
        "/api/v1/materials",
        headers=headers,
        data={"title": "Секрет", "kind": "text", "body": "нельзя"},
    )
    assert created.status_code == 403

    deleted = client.delete("/api/v1/materials/text-meteorite", headers=headers)
    assert deleted.status_code == 403


def test_update_rfid_and_delete(client) -> None:
    """Педагог меняет UID метки и может убрать материал."""

    headers = auth_header(client)
    patched = client.patch(
        "/api/v1/materials/scientist-gagarin",
        headers=headers,
        data={"rfid_uid": "DEADBEEF"},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["rfidUid"] == "DEADBEEF"

    removed = client.delete("/api/v1/materials/clip-welcome", headers=headers)
    assert removed.status_code == 204
    gone = client.get("/api/v1/materials/clip-welcome", headers=headers)
    assert gone.status_code == 404
