# Обзор REST API ядра

Базовый путь: `/api/v1`. Спецификация генерируется FastAPI (`/docs`).

| Группа | Путь | Назначение |
|--------|------|------------|
| Health | `GET /health` | Живость процесса |
| Auth | `POST /auth/login` | JWT (роли: admin, educator, attendant) |
| Devices | `GET /devices` | Реестр и статусы |
| Lessons | `GET/POST /lessons` | Каталог, запуск, стоп |
| Materials | `GET/POST/PATCH/DELETE /materials` | Ролики, тексты, учёные, RFID, файлы |
| Schedule | `GET/POST/PATCH/DELETE /schedule` | Еженедельные слоты, автозапуск занятия |
| Hall | `GET /hall`, `POST /hall/pulse` | Стенд «на связи», пульс heartbeat |
| Comfort | `GET /comfort/status`, `POST /comfort/command` | Свет/жалюзи через HA (на стенде no-op) |
| Clocks | `GET /clocks`, `POST /clocks/mode` | Режимы астрономических часов, MQTT на ESP32 |
| Kiosk | `GET /kiosk/illuminator`, `GET /kiosk/illuminator/media/{clip}` | Окно иллюминатора, файлы роликов без JWT |
| Kiosk | `GET /kiosk/maly`, `GET /kiosk/maly/media/{section}` | Малый голобокс: разделы и ролики без JWT |
| Observatory | `GET /observatory/status` | Прокси к системе №8 |

Версионирование только через `/api/v1`. Ломающие изменения — `/api/v2`.
