import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { ClockState } from "../types/clock";

/**
 * Состояние циферблата: занятие и ручные режимы с пульта.
 */
export function useClocks() {
  return useQuery({
    queryKey: ["clocks"],
    queryFn: async () => {
      const response = await apiClient.get<ClockState>("/clocks");
      return response.data;
    },
    refetchInterval: 2_000,
  });
}

/**
 * Смена режима часов (MQTT на ESP32, на стенде — журнал ядра).
 */
export function useClockMode() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (mode: string) => {
      const response = await apiClient.post<ClockState>("/clocks/mode", { mode });
      return response.data;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(["clocks"], data);
      await queryClient.invalidateQueries({ queryKey: ["devices"] });
    },
  });
}
