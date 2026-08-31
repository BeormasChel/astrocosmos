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

## Обсерватория

Топики Diptich_hub **не** публикуем в `astroc/#`. Статусы №8 попадают в БД
через адаптер; админка читает REST `/api/v1/observatory/status`.
