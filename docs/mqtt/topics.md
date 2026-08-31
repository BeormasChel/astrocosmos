# Карта MQTT-топиков ядра

Префикс: `astroc` (переменная `MQTT_TOPIC_PREFIX`).
QoS 1 для команд и статусов. Payload — JSON UTF-8.

## Устройства

| Топик | Направление | Назначение |
|-------|-------------|------------|
| `astroc/devices/{id}/status` | устройство → ядро | online/offline, версия прошивки, uptime |
| `astroc/devices/{id}/telemetry` | устройство → ядро | датчики, режим, температура |
| `astroc/devices/{id}/events` | устройство → ядро | RFID, касание, ошибка |
| `astroc/devices/{id}/command` | ядро → устройство | команда сценария |
| `astroc/devices/{id}/ack` | устройство → ядро | подтверждение команды |

`{id}` — из таблицы в `docs/architecture/project_structure.md`.

Heartbeat не реже 10 с. Если тишина > 30 с (`DEVICE_OFFLINE_AFTER_SECONDS`) —
устройство offline в админке.

## Сценарии

| Топик | Назначение |
|-------|------------|
| `astroc/scenarios/active` | id текущего сценария или `null` |
| `astroc/scenarios/events` | старт/шаг/стоп для всех подписчиков |

## Речь (настольный Диптих)

Аудио по MQTT не гоняем. Терминал отдаёт чанки на STT-сервис ядра по HTTP
(или отдельный внутренний порт). В MQTT только события: `wake`, `listening`,
`tts_playing`, `rfid_uid`.

## RFID тумбы

Тумба не имеет своего `device_id`. Событие публикует большой голобокс:

`astroc/devices/bolshoy_golobox/events` → `{ "type": "rfid_scan", "uid": "..." }`.

## Комфорт

Ядро шлёт команды в Home Assistant по HTTP, не в брокер обсерватории.
Опционально дублирует результат в `astroc/comfort/state` для админки.

## Обсерватория

У комплекса №8 **свой** MQTT-брокер. Его топики **не** публикуем в `astroc/#`.
Сейчас полезная связь с ядром — URL видеопотока камеры для Астровизора.
OpenAPI ещё не задан.
