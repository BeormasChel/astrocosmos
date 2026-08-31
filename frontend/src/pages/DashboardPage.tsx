import { Link } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { ComplexCard } from "../components/ComplexCard";
import { StandNotice } from "../components/StandNotice";
import { useDevices } from "../hooks/useDevices";
import { useActiveRun, useLessonActions } from "../hooks/useLessons";
import { useUpcomingSlot } from "../hooks/useSchedule";
import { useHall } from "../hooks/useHall";
import { useAuthStore } from "../stores/authStore";

/**
 * Домашний экран педагога: одно действие и понятные статусы.
 */
export function DashboardPage() {
  const { data: complexes = [], isError } = useDevices();
  const { data: active } = useActiveRun();
  const { data: upcoming } = useUpcomingSlot();
  const { data: hall } = useHall();
  const { stop } = useLessonActions();
  const role = useAuthStore((state) => state.user?.role);
  const canControl = role === "admin" || role === "educator";

  return (
    <section className="page">
      <PageHeader
        eyebrow="Сегодня"
        title={active ? `Идёт: ${active.title}` : "Зал готов к занятию"}
        lead={
          active
            ? "Комплексы выполняют программу. Можно остановить или перейти к другому занятию."
            : "Запустите программу для группы или посмотрите, какие комплексы уже на связи."
        }
        action={
          active && canControl ? (
            <button
              type="button"
              className="btn btn--primary"
              onClick={() => stop.mutate()}
              disabled={stop.isPending}
            >
              Остановить
            </button>
          ) : (
            <Link className="btn btn--primary" to="/lessons">
              Запустить занятие
            </Link>
          )
        }
      />

      {isError ? (
        <div className="notice">
          <p>Не удалось загрузить комплексы. Проверьте, что ядро запущено на порту 8000.</p>
        </div>
      ) : null}

      <StandNotice visible={Boolean(hall?.standEnabled)} />

      {!active && upcoming?.isEnabled ? (
        <div className="notice">
          <p>
            Ближайшее по расписанию: {upcoming.nextHint} — {upcoming.lessonTitle}.{" "}
            <Link to="/schedule">Открыть расписание</Link>
          </p>
        </div>
      ) : null}

      <h2 className="section-title">Комплексы в зале</h2>
      <div className="card-grid">
        {complexes.map((complex) => (
          <ComplexCard key={complex.id} complex={complex} />
        ))}
      </div>
    </section>
  );
}
