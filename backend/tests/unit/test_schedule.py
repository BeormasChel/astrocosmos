"""Еженедельное расписание автозапуска занятий."""

from datetime import datetime
from zoneinfo import ZoneInfo

from tests.conftest import auth_header

HALL_TZ = ZoneInfo("Asia/Yekaterinburg")
MONDAY_MORNING = datetime(2026, 8, 31, 10, 0, 20, tzinfo=HALL_TZ)


def test_create_and_list_slot(client) -> None:
    """Педагог добавляет слот и видит его в списке на русском."""

    headers = auth_header(client)
    created = client.post(
        "/api/v1/schedule",
        headers=headers,
        json={
            "lessonId": "welcome",
            "weekday": 0,
            "time": "10:00",
            "isEnabled": True,
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["lessonTitle"] == "Знакомство с кораблём"
    assert body["weekdayLabel"] == "Понедельник"
    assert body["time"] == "10:00"

    listing = client.get("/api/v1/schedule", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_due_starts_lesson_once(client) -> None:
    """В нужную минуту занятие включается само и не дублируется."""

    headers = auth_header(client)
    client.post(
        "/api/v1/schedule",
        headers=headers,
        json={"lessonId": "welcome", "weekday": 0, "time": "10:00"},
    )
    first = client.post(
        "/api/v1/schedule/due",
        headers=headers,
        json={"at": MONDAY_MORNING.isoformat()},
    )
    assert first.status_code == 200, first.text
    assert first.json()["started"] == ["welcome"]

    active = client.get("/api/v1/lessons/active", headers=headers)
    assert active.json()["lessonId"] == "welcome"
    assert active.json()["startedBy"] == "schedule"

    second = client.post(
        "/api/v1/schedule/due",
        headers=headers,
        json={"at": MONDAY_MORNING.replace(second=40).isoformat()},
    )
    assert second.json()["started"] == []


def test_due_does_not_interrupt_manual_lesson(client) -> None:
    """Если педагог уже ведёт занятие, расписание молчит."""

    headers = auth_header(client)
    client.post(
        "/api/v1/schedule",
        headers=headers,
        json={"lessonId": "welcome", "weekday": 0, "time": "10:00"},
    )
    started = client.post("/api/v1/lessons/meteorite/start", headers=headers)
    assert started.status_code == 200

    due = client.post(
        "/api/v1/schedule/due",
        headers=headers,
        json={"at": MONDAY_MORNING.isoformat()},
    )
    assert due.json()["skipped"] == "occupied"
    active = client.get("/api/v1/lessons/active", headers=headers)
    assert active.json()["lessonId"] == "meteorite"


def test_attendant_cannot_edit_schedule(client) -> None:
    """Смотритель видит расписание, но не меняет его."""

    educator = auth_header(client)
    client.post(
        "/api/v1/schedule",
        headers=educator,
        json={"lessonId": "welcome", "weekday": 1, "time": "12:00"},
    )
    attendant = auth_header(client, login="attendant", password="attendant")
    listing = client.get("/api/v1/schedule", headers=attendant)
    assert listing.status_code == 200
    assert listing.json()

    created = client.post(
        "/api/v1/schedule",
        headers=attendant,
        json={"lessonId": "welcome", "weekday": 2, "time": "09:00"},
    )
    assert created.status_code == 403


def test_toggle_and_delete_slot(client) -> None:
    """Выключенный слот не стреляет, удаление убирает его с полки."""

    headers = auth_header(client)
    created = client.post(
        "/api/v1/schedule",
        headers=headers,
        json={"lessonId": "scientists", "weekday": 0, "time": "10:00"},
    )
    slot_id = created.json()["id"]
    patched = client.patch(
        f"/api/v1/schedule/{slot_id}",
        headers=headers,
        json={"isEnabled": False},
    )
    assert patched.status_code == 200
    assert patched.json()["isEnabled"] is False

    due = client.post(
        "/api/v1/schedule/due",
        headers=headers,
        json={"at": MONDAY_MORNING.isoformat()},
    )
    assert due.json()["started"] == []

    removed = client.delete(f"/api/v1/schedule/{slot_id}", headers=headers)
    assert removed.status_code == 204
    listing = client.get("/api/v1/schedule", headers=headers)
    assert listing.json() == []
