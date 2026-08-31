"""Каталог комплексов и демо-занятий для первичного наполнения БД."""

from __future__ import annotations

from typing import Any

from app.core.constants import (
    DEVICE_ASTROVIZOR,
    DEVICE_BOLSHOY_GOLOBOX,
    DEVICE_DESKTOP_DIPTYCH,
    DEVICE_ILLUMINATOR,
    DEVICE_MALY_GOLOBOX,
    DEVICE_PLANET_CLOCK,
    MATERIAL_KIND_SCIENTIST,
    MATERIAL_KIND_TEXT,
    MATERIAL_KIND_VIDEO,
    ROLE_ADMIN,
    ROLE_ATTENDANT,
    ROLE_EDUCATOR,
)

DEVICE_CATALOG: list[dict[str, Any]] = [
    {
        "id": DEVICE_MALY_GOLOBOX,
        "number": 1,
        "name": "Малый Голобокс",
        "purpose": "Метеорит: касания, видеофрагменты, простая 3D-модель",
        "platform": "Raspberry Pi",
        "extras": None,
    },
    {
        "id": DEVICE_BOLSHOY_GOLOBOX,
        "number": 2,
        "name": "Большой Голобокс",
        "purpose": "Групповой экран: разделы астрономии и учёные",
        "platform": "Raspberry Pi",
        "extras": {
            "rfidPedestal": {
                "name": "Тумба с фигурками",
                "reader": "PN532",
                "attachedTo": DEVICE_BOLSHOY_GOLOBOX,
            }
        },
    },
    {
        "id": DEVICE_DESKTOP_DIPTYCH,
        "number": 3,
        "name": "Настольный Диптих",
        "purpose": "Голос, метки PN532, свет и жалюзи через ядро",
        "platform": "ESP32-S3",
        "extras": None,
    },
    {
        "id": DEVICE_PLANET_CLOCK,
        "number": 4,
        "name": "Астрономические часы",
        "purpose": "Как течёт время на разных планетах",
        "platform": "ESP32",
        "extras": None,
    },
    {
        "id": DEVICE_ILLUMINATOR,
        "number": 5,
        "name": "Иллюминатор",
        "purpose": "Окно в космос, 4K-видео",
        "platform": "Raspberry Pi 5",
        "extras": None,
    },
    {
        "id": DEVICE_ASTROVIZOR,
        "number": 6,
        "name": "Астровизор",
        "purpose": "Картинка с камеры купола на экран (не Vizor)",
        "platform": "Raspberry Pi",
        "extras": None,
    },
]

USER_CATALOG: list[dict[str, str]] = [
    {
        "login": "admin",
        "full_name": "Администратор зала",
        "role": ROLE_ADMIN,
        "password": "admin",
    },
    {
        "login": "educator",
        "full_name": "Педагог",
        "role": ROLE_EDUCATOR,
        "password": "educator",
    },
    {
        "login": "attendant",
        "full_name": "Смотритель",
        "role": ROLE_ATTENDANT,
        "password": "attendant",
    },
]

LESSON_CATALOG: list[dict[str, Any]] = [
    {
        "id": "welcome",
        "title": "Знакомство с кораблём",
        "duration_min": 8,
        "for_whom": "Экскурсия, 6–10 лет",
        "steps": [
            {
                "device_id": DEVICE_ILLUMINATOR,
                "command": "play",
                "payload": {"clip": "welcome"},
                "mode_label": "Ролик «Знакомство»",
            },
            {
                "device_id": DEVICE_PLANET_CLOCK,
                "command": "set_mode",
                "payload": {"mode": "compare"},
                "mode_label": "Сравнение планет",
            },
            {
                "device_id": DEVICE_MALY_GOLOBOX,
                "command": "open_section",
                "payload": {"section": "intro"},
                "mode_label": "Раздел «Введение»",
            },
        ],
    },
    {
        "id": "meteorite",
        "title": "Челябинский метеорит",
        "duration_min": 12,
        "for_whom": "Занятие, 9–14 лет",
        "steps": [
            {
                "device_id": DEVICE_MALY_GOLOBOX,
                "command": "open_section",
                "payload": {"section": "structure"},
                "mode_label": "Строение метеорита",
            },
            {
                "device_id": DEVICE_ILLUMINATOR,
                "command": "play",
                "payload": {"clip": "impact"},
                "mode_label": "Падение с орбиты",
            },
        ],
    },
    {
        "id": "scientists",
        "title": "Встреча с учёными",
        "duration_min": 15,
        "for_whom": "Группа у большого экрана",
        "steps": [
            {
                "device_id": DEVICE_BOLSHOY_GOLOBOX,
                "command": "await_rfid",
                "payload": {},
                "mode_label": "Ждём фигурку на тумбе",
            },
        ],
    },
]

# Примеры, чтобы пульт не встречал пустую полку на первом входе.
EXAMPLE_MATERIALS: list[dict[str, Any]] = [
    {
        "id": "clip-welcome",
        "kind": MATERIAL_KIND_VIDEO,
        "title": "Знакомство с кораблём",
        "body": None,
        "device_id": DEVICE_ILLUMINATOR,
        "clip_key": "welcome",
        "rfid_uid": None,
        "created_by": "educator",
    },
    {
        "id": "clip-impact",
        "kind": MATERIAL_KIND_VIDEO,
        "title": "Падение с орбиты",
        "body": None,
        "device_id": DEVICE_ILLUMINATOR,
        "clip_key": "impact",
        "rfid_uid": None,
        "created_by": "educator",
    },
    {
        "id": "clip-maly-intro",
        "kind": MATERIAL_KIND_VIDEO,
        "title": "Введение к метеориту",
        "body": None,
        "device_id": DEVICE_MALY_GOLOBOX,
        "clip_key": "intro",
        "rfid_uid": None,
        "created_by": "educator",
    },
    {
        "id": "clip-maly-structure",
        "kind": MATERIAL_KIND_VIDEO,
        "title": "Строение метеорита",
        "body": None,
        "device_id": DEVICE_MALY_GOLOBOX,
        "clip_key": "structure",
        "rfid_uid": None,
        "created_by": "educator",
    },
    {
        "id": "text-meteorite",
        "kind": MATERIAL_KIND_TEXT,
        "title": "Челябинский метеорит",
        "body": (
            "15 февраля 2013 года над Челябинском взорвался метеорит. "
            "Осколки упали в озеро Чебаркуль. На малом голобоксе дети "
            "могут рассмотреть, из чего он состоит."
        ),
        "device_id": DEVICE_MALY_GOLOBOX,
        "clip_key": None,
        "rfid_uid": None,
        "created_by": "educator",
    },
    {
        "id": "scientist-gagarin",
        "kind": MATERIAL_KIND_SCIENTIST,
        "title": "Юрий Гагарин",
        "body": (
            "Первый человек в космосе (12 апреля 1961 года). "
            "Замените UID метки на настоящий, когда привяжете фигурку на тумбе."
        ),
        "device_id": DEVICE_BOLSHOY_GOLOBOX,
        "clip_key": "gagarin",
        "rfid_uid": "AABBCC11",
        "created_by": "educator",
    },
]

