import { PageHeader } from "../components/PageHeader";
import { useActiveRun, useLessonActions, useLessons } from "../hooks/useLessons";
import { useAuthStore } from "../stores/authStore";

/**
 * Занятия — главный рабочий экран педагога.
 */
export function ScenariosPage() {
  const { data: lessons = [] } = useLessons();
  const { data: active } = useActiveRun();
  const { start, stop } = useLessonActions();
  const role = useAuthStore((state) => state.user?.role);
  const canControl = role === "admin" || role === "educator";
  const errorText =
    start.error || stop.error
      ? "Не удалось отдать команду. Если вы смотритель — запуск недоступен."
      : null;

  return (
    <section className="page">
      <PageHeader
        title="Занятия"
        lead="Нажмите «Начать» — ядро отправит команды комплексам. Сейчас без железа это видно по смене режима на карточках."
        action={
          active && canControl ? (
            <button
              type="button"
              className="btn btn--ghost"
              onClick={() => stop.mutate()}
              disabled={stop.isPending}
            >
              Остановить текущее
            </button>
          ) : null
        }
      />
      {errorText ? <p className="login__error">{errorText}</p> : null}
      <ul className="lesson-list">
        {lessons.map((lesson) => {
          const isCurrent = active?.lessonId === lesson.id;
          return (
            <li key={lesson.id} className="lesson-card">
              <div>
                <h2 className="lesson-card__title">{lesson.title}</h2>
                <p className="lesson-card__meta">
                  {lesson.durationMin} мин · {lesson.forWhom}
                  {isCurrent ? " · сейчас в зале" : ""}
                </p>
              </div>
              {canControl ? (
                <button
                  type="button"
                  className="btn btn--primary"
                  disabled={start.isPending}
                  onClick={() => start.mutate(lesson.id)}
                >
                  {isCurrent ? "Ещё раз" : "Начать"}
                </button>
              ) : (
                <span className="lesson-card__meta">Только просмотр</span>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
