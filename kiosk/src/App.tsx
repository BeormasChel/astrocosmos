import { IlluminatorWindow } from "./IlluminatorWindow";
import { MalyHolobox } from "./MalyHolobox";

/**
 * Один пакет киосков: иллюминатор на /, малый голобокс на /maly.
 */
export function App() {
  const path = window.location.pathname.replace(/\/$/, "") || "/";
  if (path.endsWith("/maly")) {
    return <MalyHolobox />;
  }
  return <IlluminatorWindow />;
}
