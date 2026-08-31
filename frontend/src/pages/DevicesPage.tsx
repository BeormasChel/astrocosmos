import { Link } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { StandNotice } from "../components/StandNotice";
import { StatusBadge } from "../components/StatusBadge";
import { useDevices } from "../hooks/useDevices";
import { useHall } from "../hooks/useHall";
import { illuminatorWindowUrl, malyHoloboxUrl } from "../lib/illuminator";

/**
 * Список комплексов 1–6; тумба описана у большого голобокса.
 */
export function DevicesPage() {
  const { data: complexes = [] } = useDevices();
  const { data: hall } = useHall();

  return (
    <section className="page">
      <PageHeader
        title="Комплексы"
        lead="Шесть точек в зале. Седьмая «тумба» — это считыватель фигурок у большого голобокса, не отдельный экран."
      />
      <StandNotice visible={Boolean(hall?.standEnabled)} />
      <ul className="complex-list">
        {complexes.map((complex) => (
          <li key={complex.id} className="complex-row">
            <div>
              <p className="complex-row__name">
                №{complex.number} · {complex.name}
              </p>
              <p className="complex-row__meta">
                {complex.purpose} · {complex.platform}
              </p>
              {complex.rfidPedestal ? (
                <p className="complex-row__meta">
                  Периферия: {complex.rfidPedestal.name} ({complex.rfidPedestal.reader})
                </p>
              ) : null}
              <p className="complex-row__meta">{complex.currentMode}</p>
              {complex.id === "illuminator" ? (
                <p className="complex-row__meta">
                  <a href={illuminatorWindowUrl()} target="_blank" rel="noreferrer">
                    Открыть окно
                  </a>
                </p>
              ) : null}
              {complex.id === "maly_golobox" ? (
                <p className="complex-row__meta">
                  <a href={malyHoloboxUrl()} target="_blank" rel="noreferrer">
                    Открыть киоск
                  </a>
                </p>
              ) : null}
              {complex.id === "planet_clock" ? (
                <p className="complex-row__meta">
                  <Link to="/clocks">Открыть циферблат</Link>
                </p>
              ) : null}
            </div>
            <StatusBadge status={complex.status} />
          </li>
        ))}
      </ul>
    </section>
  );
}
