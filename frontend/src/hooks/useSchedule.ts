import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { ScheduleSlot } from "../types/schedule";

export interface SchedulePayload {
  lessonId: string;
  weekday: number;
  time: string;
  isEnabled: boolean;
}

/**
 * Недельное расписание автозапуска.
 */
export function useSchedule() {
  return useQuery({
    queryKey: ["schedule"],
    queryFn: async () => {
      const response = await apiClient.get<ScheduleSlot[]>("/schedule");
      return response.data;
    },
  });
}

/**
 * Ближайший включённый слот для обзора.
 */
export function useUpcomingSlot() {
  return useQuery({
    queryKey: ["schedule", "upcoming"],
    queryFn: async () => {
      const response = await apiClient.get<ScheduleSlot | null>("/schedule/upcoming");
      return response.data;
    },
    refetchInterval: 30_000,
  });
}

/**
 * Добавление, включение и удаление слотов.
 */
export function useScheduleActions() {
  const queryClient = useQueryClient();

  const invalidate = async () => {
    await queryClient.invalidateQueries({ queryKey: ["schedule"] });
    await queryClient.invalidateQueries({ queryKey: ["lessons"] });
    await queryClient.invalidateQueries({ queryKey: ["devices"] });
  };

  const create = useMutation({
    mutationFn: async (payload: SchedulePayload) => {
      const response = await apiClient.post<ScheduleSlot>("/schedule", payload);
      return response.data;
    },
    onSuccess: invalidate,
  });

  const update = useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: Partial<SchedulePayload> }) => {
      const response = await apiClient.patch<ScheduleSlot>(`/schedule/${id}`, payload);
      return response.data;
    },
    onSuccess: invalidate,
  });

  const remove = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/schedule/${id}`);
    },
    onSuccess: invalidate,
  });

  return { create, update, remove };
}
