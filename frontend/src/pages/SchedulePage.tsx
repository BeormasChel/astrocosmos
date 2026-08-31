import { FormEvent, useState } from "react";
import { isAxiosError } from "axios";
import { PageHeader } from "../components/PageHeader";
import { useLessons } from "../hooks/useLessons";
import { useSchedule, useScheduleActions, type SchedulePayload } from "../hooks/useSchedule";
import { useAuthStore } from "../stores/authStore";
import { WEEKDAY_OPTIONS, type ScheduleSlot } from "../types/schedule";

const EMPTY_FORM: SchedulePayload = {
  lessonId: "welcome",
  weekday: 0,
  time: "10:00",
  isEnabled: true,
};

/**
 * Текст ошибки API без технического жаргона.
 */
function explainError(error: unknown): string {
  if (isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
  }
  return "Не получилось сохранить слот. Проверьте поля и что ядро запущено.";
}

/**
 * Расписание: когда занятие начнётся само, без педагога у планшета.
 */
export function SchedulePage() {
  const role = useAuthStore((state) => state.user?.role);
  const canEdit = role === "admin" || role === "educator";
  const { data: lessons = [] } = useLessons();
  const { data: slots = [], isLoading } = useSchedule();
  const { create, update, remove } = useScheduleActions();
  const [formOpen, setFormOpen] = useState(false);
  const [form, setForm] = useState<SchedulePayload>(EMPTY_FORM);
  const [formError, setFormError] = useState<string | null>(null);
  const busy = create.isPending || update.isPending;

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setFormError(null);
    try {
      await create.mutateAsync(form);
      setFormOpen(false);
      setForm(EMPTY_FORM);
    } catch (error) {
      setFormError(explainError(error));
    }
  };

  const onToggle = async (slot: ScheduleSlot) => {
    try {
      await update.mutateAsync({ id: slot.id, payload: { isEnabled: !slot.isEnabled } });
    } catch (error) {
      setFormError(explainError(error));
    }
  };

  const onDelete = async (slot: ScheduleSlot) => {
    const confirmed = window.confirm(
      `Убрать «${slot.lessonTitle}» из расписания (${slot.weekdayLabel}, ${slot.time})?`,
    );
    if (!confirmed) {
      return;
    }
    try {
      await remove.mutateAsync(slot.id);
    } catch (error) {
      setFormError(explainError(error));
    }
  };

  return (
    <section className="page">
      <PageHeader
        title="Расписание"
        lead="Занятие начнётся само к приходу группы. Время — челябинское. Если вы уже ведёте программу вручную, автозапуск подождёт."
        action={
          canEdit ? (
            <button type="button" className="btn btn--primary" onClick={() => setFormOpen(true)}>
              Добавить слот
            </button>
          ) : null
        }
      />

      {formOpen && canEdit ? (
        <form className="material-form" onSubmit={onSubmit}>
          <h2 className="section-title">Когда включить занятие</h2>
          <div className="filters" role="radiogroup" aria-label="День недели">
            {WEEKDAY_OPTIONS.map((day) => (
              <button
                key={day.id}
                type="button"
                role="radio"
                aria-checked={form.weekday === day.id}
                className={`chip ${form.weekday === day.id ? "chip--on" : ""}`}
                onClick={() => setForm((current) => ({ ...current, weekday: day.id }))}
              >
                {day.label}
              </button>
            ))}
          </div>
          <label className="login__field">
            Занятие
            <select
              value={form.lessonId}
              onChange={(event) =>
                setForm((current) => ({ ...current, lessonId: event.target.value }))
              }
              required
            >
              {lessons.map((lesson) => (
                <option key={lesson.id} value={lesson.id}>
                  {lesson.title}
                </option>
              ))}
            </select>
          </label>
          <label className="login__field">
            Во сколько
            <input
              type="time"
              value={form.time}
              onChange={(event) => setForm((current) => ({ ...current, time: event.target.value }))}
              required
            />
          </label>
          <label className="schedule-check">
            <input
              type="checkbox"
              checked={form.isEnabled}
              onChange={(event) =>
                setForm((current) => ({ ...current, isEnabled: event.target.checked }))
              }
            />
            Включить сразу
          </label>
          {formError ? <p className="login__error">{formError}</p> : null}
          <div className="material-form__actions">
            <button className="btn btn--primary" type="submit" disabled={busy}>
              {busy ? "Сохраняем…" : "Сохранить"}
            </button>
            <button
              className="btn btn--ghost"
              type="button"
              onClick={() => {
                setFormOpen(false);
                setFormError(null);
              }}
            >
              Отмена
            </button>
          </div>
        </form>
      ) : null}

      {formError && !formOpen ? <p className="login__error">{formError}</p> : null}

      {isLoading ? <p className="muted">Загружаем расписание…</p> : null}

      {!isLoading && slots.length === 0 ? (
        <div className="empty">
          <p className="empty__title">Нет автоматических запусков</p>
          <p>
            Добавьте слот: день, время и программу. Пока список пуст — ничего само не
            включится.
          </p>
        </div>
      ) : (
        <ul className="lesson-list">
          {slots.map((slot) => (
            <li key={slot.id} className="lesson-card">
              <div>
                <h2 className="lesson-card__title">{slot.lessonTitle}</h2>
                <p className="lesson-card__meta">
                  {slot.weekdayLabel}, {slot.time}
                  {" · "}
                  {slot.nextHint}
                </p>
              </div>
              {canEdit ? (
                <div className="material-card__actions">
                  <button
                    type="button"
                    className="btn btn--ghost"
                    onClick={() => void onToggle(slot)}
                    disabled={update.isPending}
                  >
                    {slot.isEnabled ? "Выключить" : "Включить"}
                  </button>
                  <button type="button" className="btn btn--ghost" onClick={() => void onDelete(slot)}>
                    Убрать
                  </button>
                </div>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
