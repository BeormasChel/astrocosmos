import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

interface HealthResponse {
  status: string;
  service: string;
}

/**
 * Запросить liveliness ядра. Нужен для индикатора на дашборде.
 *
 * @returns Текущий статус или null, пока запрос идёт / упал.
 */
export function useHealth() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    let cancelled = false;

    apiClient
      .get<HealthResponse>("/health")
      .then((response) => {
        if (!cancelled) {
          setHealth(response.data);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setHealth(null);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return health;
}
