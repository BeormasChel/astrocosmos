# Backend ядра «Астрокосмос»

FastAPI-приложение: REST API `/api/v1/`, MQTT-мост к устройствам, адаптер
к обсерваторному «Диптиху», планировщик сценариев (Celery).

## Запуск (разработка)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Документация OpenAPI: http://localhost:8000/docs

## Тесты

```bash
pytest
```

## Куда класть новый код

| Задача | Путь |
|--------|------|
| HTTP-эндпоинты | `app/api/v1/endpoints/` |
| ORM-модели | `app/models/` |
| Pydantic-схемы | `app/schemas/` |
| Бизнес-логика | `app/services/` |
| MQTT publish/subscribe | `app/mqtt/` |
| Обсерватория (клиент API) | `app/integrations/observatory/` |
| Фоновые задачи | `app/workers/` |
