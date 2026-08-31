# Агент Иллюминатора (Raspberry Pi 5)

Программный плеер — Chromium kiosk + React (`kiosk/`, порт 3001), не VLC и не Unity.
Контент роликов приходит с ядра (`/api/v1/kiosk/illuminator/media/...`); в зале
файлы лежат на NFS, локально — в `backend/data/media`.

Heartbeat:

```
set DEVICE_ID=illuminator
set CORE_URL=http://127.0.0.1:8000
python -m raspberry_pi.illuminator.agent
```

Окно на Pi:

```
chromium --kiosk --app=http://127.0.0.1:3001/?kiosk
```

Пульт посетителя — ESP32 в `microcontrollers/illuminator_remote/` (пока заглушка).
При потере связи с ядром окно остаётся чёрным; локальный кэш Attract — следующий шаг.
