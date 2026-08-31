import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { Complex } from "../types/device";

/**
 * Список комплексов с живыми статусами ядра.
 */
export function useDevices() {
  return useQuery({
    queryKey: ["devices"],
    queryFn: async () => {
      const response = await apiClient.get<Complex[]>("/devices");
      return response.data;
    },
    refetchInterval: 10_000,
  });
}
