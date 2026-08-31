# Структура репозитория «Астрокосмос»

Репозиторий содержит **ядро управления** и клиентский код комплексов 1–7.
Комплекс №8 (обсерваторный «Диптих») живёт в отдельном проекте; здесь только
HTTP-адаптер и контракт API.

```
AI Astro206/
├── .env.example                 # Шаблон секретов (копировать в .env)
├── .gitignore
├── docker-compose.yml           # Postgres, Redis, Mosquitto, API, Celery, Nginx
├── README.md
│
├── backend/                     # FastAPI + Celery
│   ├── app/
│   │   ├── main.py              # Точка входа ASGI
│   │   ├── core/                # Config, JWT, константы устройств
│   │   ├── api/v1/endpoints/    # REST /api/v1/*
│   │   ├── models/              # SQLAlchemy (этап MVP-1)
│   │   ├── schemas/             # Pydantic
│   │   ├── services/            # Сценарии, контент, устройства
│   │   ├── mqtt/                # Мост к Mosquitto (префикс astroc/)
│   │   ├── workers/             # Celery app + задачи расписания
│   │   └── integrations/observatory/  # Клиент внешней системы №8
│   ├── alembic/                 # Миграции PostgreSQL
│   └── tests/                   # pytest: unit + integration
│
├── frontend/                    # Админка React + TypeScript (Vite)
│   └── src/
│       ├── api/                 # Axios к /api/v1
│       ├── pages/               # Дашборд, комплексы, сценарии, CMS, расписание
│       ├── components/layout/
│       ├── stores/              # Zustand (сессия)
│       └── types/
│
├── raspberry_pi/                # Агенты киосков (не голобоксы)
│   ├── shared/                  # MQTT heartbeat, конфиг, NFS
│   ├── illuminator/             # 4K-плеер
│   ├── astrovizor/              # Уличный киоск + видеопоток
│   └── pedestal/                # Тумба + RFID
│
├── microcontrollers/            # PlatformIO, только «наши» ESP32
│   ├── shared/
│   ├── planet_clock/            # WS2812, NTP, MQTT
│   ├── desktop_diptych/         # Настольный помощник №3
│   ├── illuminator_remote/      # Пульт посетителя
│   └── astrovizor_gimbal/       # Az/El, не путать с Vizor купола
│
├── clients/holobox/             # Контракт Unity (Windows), без бинарников
│   ├── maly_golobox/
│   └── bolshoy_golobox/
│
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   ├── nginx/
│   └── mosquitto/
│
├── tests/                       # Межсервисные и e2e
│   ├── integration/
│   └── e2e/
│
├── scripts/                     # Деплой, бэкап, провижининг RPi
│
└── docs/
    ├── context/                 # Концепция и ТЗ комплексов
    ├── architecture/            # Структура и решения до старта
    ├── integration/             # Контракт API обсерватории
    ├── mqtt/                    # Карта топиков astroc/
    ├── api/                     # Обзор REST ядра
    ├── project_management/      # Роадмап и задачи
    ├── development/             # Стандарты кода
    └── scenarios/               # Педагогические сценарии
```

## Что сюда не кладём

- Прошивки MCC-1, Vizor-1/2/3, T-Connect, T-Panel купола
- Исходники Diptich_hub и MongoDB обсерватории
- Unity-проекты и AssetBundles (ссылка и контракт — в `clients/holobox/`)
- Медиафайлы 4K (`/media/content` на NFS)

## Идентификаторы устройств

| id | Комплекс |
|----|----------|
| `maly_golobox` | №1 Малый Голобокс |
| `bolshoy_golobox` | №2 Большой Голобокс |
| `desktop_diptych` | №3 Настольный Диптих |
| `planet_clock` | №4 Астрономические часы |
| `illuminator` | №5 Иллюминатор |
| `astrovizor` | №6 Астровизор |
| `pedestal` | №7 Интерактивная тумба |
| `observatory` | №8 Виртуальный адаптер к Diptich_hub |
