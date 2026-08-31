import { Link } from "react-router-dom";
import { illuminatorWindowUrl, malyHoloboxUrl } from "../lib/illuminator";
import type { Complex } from "../types/device";
import { StatusBadge } from "./StatusBadge";

/**
 * Карточка комплекса: имя, зачем нужен, статус, тумба как часть №2.
 */
export function ComplexCard({ complex }: { complex: Complex }) {
  return (
    <article className="complex-card">
      <div className="complex-card__top">
        <span className="complex-card__num">
          {complex.number ? `№${complex.number}` : ""}
        </span>
        <StatusBadge status={complex.status} />
      </div>
      <h3 className="complex-card__name">{complex.name}</h3>
      <p className="complex-card__purpose">{complex.purpose}</p>
      <p className="complex-card__mode">{complex.currentMode}</p>
      <p className="complex-card__platform">{complex.platform}</p>
      {complex.rfidPedestal ? (
        <p className="complex-card__peripheral">
          Тумба RFID ({complex.rfidPedestal.reader}): фигурки открывают сюжет
          на этом экране
        </p>
      ) : null}
      {complex.id === "illuminator" ? (
        <a
          className="complex-card__link"
          href={illuminatorWindowUrl()}
          target="_blank"
          rel="noreferrer"
        >
          Открыть окно
        </a>
      ) : complex.id === "maly_golobox" ? (
        <a
          className="complex-card__link"
          href={malyHoloboxUrl()}
          target="_blank"
          rel="noreferrer"
        >
          Открыть киоск
        </a>
      ) : complex.id === "planet_clock" ? (
        <Link className="complex-card__link" to="/clocks">
          Открыть циферблат
        </Link>
      ) : (
        <Link className="complex-card__link" to="/complexes">
          Открыть комплексы
        </Link>
      )}
    </article>
  );
}
