# Обзор REST API ядра

Базовый путь: `/api/v1`. Спецификация генерируется FastAPI (`/docs`).

| Группа | Путь | Назначение |
|--------|------|------------|
| Health | `GET /health` | Живость процесса |
| Auth | `POST /auth/login` | JWT (роли: admin, educator, attendant) |
| Devices | `GET /devices` | Реестр и статусы |
| Scenarios | `GET/POST /scenarios` | Каталог, запуск, стоп |
| Content | `GET/POST /content` | Метаданные медиа |
| Schedule | `GET/POST /schedule` | Расписание Celery Beat |
| Observatory | `GET /observatory/status` | Прокси к системе №8 |

Версионирование только через `/api/v1`. Ломающие изменения — `/api/v2`.
