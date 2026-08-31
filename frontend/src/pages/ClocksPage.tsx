import { PageHeader } from "../components/PageHeader";
import { ClockDial } from "../components/ClockDial";
import { StandNotice } from "../components/StandNotice";
import { useClockMode, useClocks } from "../hooks/useClocks";
import { useHall } from "../hooks/useHall";
import { useAuthStore } from "../stores/authStore";

/**
 * Планетарное время: режимы с пульта и циферблат без ESP32.
 */
export function ClocksPage() {
  const { data: clocks, isError } = useClocks();
  const setMode = useClockMode();
  const { data: hall } = useHall();
  const role = useAuthStore((state) => state.user?.role);
  const canControl = role === "admin" || role === "educator";

  return (
    <section className="page">
      <PageHeader
        eyebrow="Комплекс №4"
        title="Астрономические часы"
        lead="Лучи — это сутки планет. Педагог включает сравнение или ретроград; занятие «Знакомство» само ставит Землю и Юпитер."
      />
      <StandNotice visible={Boolean(hall?.standEnabled)} />

      {isError ? (
        <div className="notice">
          <p>Не удалось загрузить часы. Проверьте, что ядро запущено на порту 8000.</p>
        </div>
      ) : null}

      {clocks ? (
        <>
          <p className="clock-status">
            Сейчас: {clocks.title}. {clocks.hint}
            {clocks.mqttConnected
              ? " Команда уходит на ленту по MQTT."
              : " Брокера нет — команда записана в журнал ядра, лента на стенде не нужна."}
          </p>

          <div className="clock-layout">
            <ClockDial planets={clocks.planets} />
            <div>
              {canControl ? (
                <div className="clock-modes" role="group" aria-label="Режимы часов">
                  {clocks.modes.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      className={
                        clocks.mode === item.id
                          ? "btn btn--primary"
                          : "btn btn--ghost"
                      }
                      disabled={setMode.isPending}
                      onClick={() => setMode.mutate(item.id)}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              ) : (
                <p className="muted">Смотритель видит циферблат, режимы меняет педагог.</p>
              )}
              <ul className="clock-legend">
                {clocks.planets.map((planet) => (
                  <li
                    key={planet.id}
                    className={
                      planet.highlighted
                        ? "clock-legend__item clock-legend__item--on"
                        : "clock-legend__item"
                    }
                  >
                    <span
                      className="clock-legend__swatch"
                      style={{ background: planet.color }}
                    />
                    <span>
                      {planet.name}
                      {planet.retrograde ? " ←" : ""} · {planet.dayHint}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </>
      ) : null}
    </section>
  );
}
