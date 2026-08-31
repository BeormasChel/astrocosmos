# Киоски зала

React + Chromium `--kiosk` на Raspberry Pi. Админка педагога — отдельное
приложение в `frontend/` (порт 3000). Здесь другой масштаб: одно окно, чёрный
фон `#000000`, без меню.

## Иллюминатор (этап B)

[http://localhost:3001](http://localhost:3001) — Attract / ролик занятия.
На Pi: `chromium --kiosk --app=http://127.0.0.1:3001/?kiosk`.

## Малый голобокс (этап D)

[http://localhost:3001/maly](http://localhost:3001/maly) — касание → меню
из шести разделов → ролик (или подпись, пока файла нет). Через 60 с без
касания — снова Attract (виден камень за стеклом).

Занятие «Знакомство» открывает «Введение», «Челябинский метеорит» —
«Строение». На Pi: `chromium --kiosk --app=http://127.0.0.1:3001/maly?kiosk`.

Ролик раздела: в материалах загрузите mp4 с `device_id=maly_golobox` и
`clip_key` равным id раздела (`intro`, `structure`, `fall`, `history`,
`map`, `compare`).

API без JWT:

- `GET /api/v1/kiosk/maly`
- `GET /api/v1/kiosk/maly/media/{section}`

Unity и glTF на Pi в этом срезе нет.
