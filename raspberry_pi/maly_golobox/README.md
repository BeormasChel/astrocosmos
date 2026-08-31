# Малый Голобокс (Raspberry Pi)

Киоск: Chromium + React из `kiosk/` (путь `/maly`). Фон `#000000` — экран
прозрачный, виден камень в витрине. Контент разделов — видеофрагменты
(ключ ролика = id раздела: `intro`, `structure`, …). Unity на Pi не запускаем.

Команды ядра: `idle`, `open_section` `{"section": "structure"}`.

Heartbeat:

```
set DEVICE_ID=maly_golobox
set CORE_URL=http://127.0.0.1:8000
python -m raspberry_pi.maly_golobox.agent
```

Окно:

```
chromium --kiosk --app=http://127.0.0.1:3001/maly?kiosk
```

3D-метеорит (glTF / Three.js) — следующий срез, не этот.
