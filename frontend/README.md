# Пульт педагога «Астрокосмос»

Интерфейс для непрограммистов: обзор зала, запуск занятий, комплексы,
материалы, расписание. Принципы: `docs/architecture/ui_ux.md`.

```bash
npm install
npm run dev
```

http://localhost:3000

Ядро: `cd backend` → `uvicorn app.main:app --reload --port 8000`.
Вход: `educator` / `educator`.

| Адрес | Экран |
|-------|--------|
| `/login` | Вход |
| `/` | Обзор зала и текущее занятие |
| `/lessons` | Запуск и остановка занятий |
| `/complexes` | Комплексы 1–6 и тумба как часть №2 |
| `/materials` | Материалы |
| `/schedule` | Расписание |
