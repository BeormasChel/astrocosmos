# Структура репозитория «Астрокосмос»

Ядро управляет комплексами **1–7**. Комплекс №8 — отдельный проект со **своим**
MQTT; здесь позже появится только адаптер. Тумба RFID — часть большого голобокса.

```
AI Astro206/
├── backend/                     # FastAPI, Celery, MQTT astroc/, адаптеры
│   └── app/integrations/
│       ├── observatory/         # №8, когда появится OpenAPI
│       └── home_assistant/      # свет и жалюзи
├── frontend/                    # Админка для педагога (React + Vite)
├── kiosk/                       # Тач-GUI киосков (React, Chromium на Pi)
│   └── README.md
├── raspberry_pi/
│   ├── shared/
│   ├── maly_golobox/            # №1 агент + запуск киоска
│   ├── bolshoy_golobox/         # №2 агент + PN532 тумбы
│   ├── illuminator/             # №5 Pi 5, 4K
│   └── astrovizor/              # №6 поток камеры на экран
├── microcontrollers/
│   ├── planet_clock/
│   ├── desktop_diptych/         # PN532 + голос
│   └── illuminator_remote/
├── docker/
├── tests/
└── docs/
    ├── architecture/            # ADR, UI/UX, runtime голобоксов
    ├── integration/             # HA, черновик API обсерватории
    └── project_management/
```

Unity-проекты и 4K-файлы в git не входят (контент-студия отдельно, медиа на NFS).

## Идентификаторы MQTT / реестра

| id | Что |
|----|-----|
| `maly_golobox` | №1 |
| `bolshoy_golobox` | №2 + события RFID тумбы |
| `desktop_diptych` | №3 |
| `planet_clock` | №4 |
| `illuminator` | №5 |
| `astrovizor` | №6 |
| `observatory` | №8, адаптер позже |
