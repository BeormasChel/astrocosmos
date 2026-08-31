# Астрономические часы (ESP32-C3 + WS2812)

Программный циферблат педагога — в админке, маршрут `/clocks`.
Эта прошивка — ленты в корпусе.

## Что умеет

- Подписка `astroc/devices/planet_clock/command`.
- Команды: `{"command":"idle"}` и `{"command":"set_mode","mode":"compare"|"retrograde"|"jupiter"}`.
- Три кольца по 60 LED (GPIO 10): Земля, Юпитер, Венера.
- Статус раз в 10 с: `astroc/devices/planet_clock/status`.

Брокер ядра не сливать с брокером обсерватории.

## Сборка

Плата: Seeed XIAO ESP32-C3. Wi‑Fi задаётся build_flags (см. `platformio_override.ini.example`).
Скопируйте флаги в `platformio.ini` локально или передайте `-DWIFI_SSID=...` при сборке.
Пароли в git не кладём.

```
pio run -e planet_clock
pio run -e planet_clock -t upload
```

На учебном стенде без железа режимы проверяются на странице «Часы».
