import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";

export interface HallState {
  standEnabled: boolean;
  mqttConnected: boolean;
  onlineCount: number;
  hallCount: number;
}

/**
 * Сводка зала: учебный стенд и сколько комплексов на связи.
 */
export function useHall() {
  return useQuery({
    queryKey: ["hall"],
    queryFn: async () => {
      const response = await apiClient.get<HallState>("/hall");
      return response.data;
    },
    refetchInterval: 10_000,
  });
}
