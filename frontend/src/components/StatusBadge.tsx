import type { DeviceStatus } from "../types/device";

const LABELS: Record<DeviceStatus, string> = {
  online: "На связи",
  offline: "Нет связи",
  degraded: "Работает с оговоркой",
  unknown: "Ждёт включения",
};

/**
 * Цвет + текст статуса: не только цвет, чтобы не терять смотрителя.
 */
export function StatusBadge({ status }: { status: DeviceStatus }) {
  return (
    <span className={`status-badge status-badge--${status}`}>
      <span className="status-badge__dot" aria-hidden />
      {LABELS[status]}
    </span>
  );
}
