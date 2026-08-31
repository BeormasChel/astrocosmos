import type { ClockPlanet } from "../types/clock";

/**
 * Концентрические кольца: скорость луча = относительная длина суток.
 */
export function ClockDial({ planets }: { planets: ClockPlanet[] }) {
  const size = 420;
  const center = size / 2;
  const count = planets.length || 1;

  return (
    <div className="clock-dial" role="img" aria-label="Циферблат планет">
      <div className="clock-dial__stage" style={{ width: size, height: size }}>
        {/* Внешнее кольцо — Меркурий, к центру — Нептун. */}
        {planets.map((planet, index) => {
          const radius = 48 + ((count - 1 - index) * (center - 70)) / count;
          const duration = Math.max(4, planet.visualSeconds);
          return (
            <div
              key={planet.id}
              className={
                planet.highlighted
                  ? "clock-ring clock-ring--on"
                  : "clock-ring clock-ring--dim"
              }
              style={{
                width: radius * 2,
                height: radius * 2,
                left: center - radius,
                top: center - radius,
                borderColor: planet.color,
                animationDuration: `${duration}s`,
                animationDirection: planet.retrograde ? "reverse" : "normal",
              }}
            >
              <span
                className="clock-ring__hand"
                style={{ background: planet.color }}
              />
            </div>
          );
        })}
        <div className="clock-dial__core">Сутки</div>
      </div>
    </div>
  );
}
