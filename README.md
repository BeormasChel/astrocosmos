# Астрокосмос

Интерактивный образовательный комплекс для детей и подростков (6–17 лет):
восемь физических экспонатов под управлением единого ядра.

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
- Киоски: Raspberry Pi (Иллюминатор, Астровизор, тумба)
- Голобоксы: Windows + Unity (отдельные ПК, интеграция по HTTP/MQTT)
- МК: ESP32 (часы, настольный Диптих, пульт Иллюминатора, механика Астровизора)

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
- Решения до старта разработки: [`docs/architecture/pre_dev_decisions.md`](docs/architecture/pre_dev_decisions.md)
- План MVP: [`docs/project_management/roadmap.md`](docs/project_management/roadmap.md)
- Интеграция с обсерваторией: [`docs/integration/observatory_api.md`](docs/integration/observatory_api.md)

## Ветки Git

- `main` — стабильная версия, готовая к развёртыванию
- `develop` — активная разработка; все фичи идут сюда
