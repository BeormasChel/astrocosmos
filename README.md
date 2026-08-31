# Астрокосмос

Интерактивный образовательный комплекс для детей и подростков (6–17 лет):
семь интерактивных контуров (1–7) под единой админкой; обсерватория — отдельный контур.

> **Принцип:** не просто показать, а вовлечь. Не просто рассказать, а дать
> потрогать, услышать, увидеть и прочувствовать.

## Что это за репозиторий

Это **ядро управления** и клиентский код комплексов «Астрокосмоса».
Система автоматизации обсерватории («Диптих» №8) **уже существует отдельно**
и подключается через API — её прошивки и админка сюда не копируются.

Два разных «Диптиха»:

| Комплекс | Что это | Как интегрируется |
|----------|---------|-------------------|
| №3 Настольный помощник | Голос, RFID, доступ | MQTT-клиент ядра |
| №8 Обсерватория | Купол, телескоп, климат | Внешний REST API |

## Стек

- Backend: Python 3.10+, FastAPI, PostgreSQL, Celery, Redis, MQTT (Mosquitto)
- Frontend: React 18, TypeScript, Vite
- Киоски: Raspberry Pi (голобоксы, Иллюминатор Pi 5, Астровизор)
- Тумба RFID: PN532 на Pi большого голобокса
- МК: ESP32 (часы, настольный Диптих, пульт Иллюминатора)
- Комфорт: Home Assistant через ядро; обсерватория — свой MQTT

## Быстрый старт (после наполнения заглушек)

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000/docs
- Админка: http://localhost:3000

## Документация

- Контекст проекта: [`docs/context/00_README.md`](docs/context/00_README.md)
- Структура репозитория: [`docs/architecture/project_structure.md`](docs/architecture/project_structure.md)
- Решения до старта: [`docs/architecture/pre_dev_decisions.md`](docs/architecture/pre_dev_decisions.md)
- UI/UX: [`docs/architecture/ui_ux.md`](docs/architecture/ui_ux.md)
- Голобоксы на Pi: [`docs/architecture/holobox_runtime.md`](docs/architecture/holobox_runtime.md)
- План: [`docs/project_management/roadmap.md`](docs/project_management/roadmap.md)
- Интеграция с обсерваторией: [`docs/integration/observatory_api.md`](docs/integration/observatory_api.md)

## Ветки Git

- `main` — стабильная версия, готовая к развёртыванию
- `develop` — активная разработка; все фичи идут сюда
