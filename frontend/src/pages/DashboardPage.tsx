import { useHealth } from "../hooks/useHealth";

/**
 * Дашборд состояния всех комплексов.
 */
export function DashboardPage() {
  const health = useHealth();

  return (
    <section>
      <h2>Мониторинг</h2>
      <p>
        Ядро API: {health ? health.status : "нет связи (ожидается /api/v1/health)"}
      </p>
      <p>Карточки комплексов появятся после подключения MQTT-устройств.</p>
    </section>
  );
}
