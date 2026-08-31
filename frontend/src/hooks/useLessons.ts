import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { Lesson } from "../types/device";

export interface LessonRun {
  id: string;
  lessonId: string;
  title: string;
  status: string;
  startedBy: string;
  startedAt: string;
  stoppedAt: string | null;
}

/**
 * Каталог занятий.
 */
export function useLessons() {
  return useQuery({
    queryKey: ["lessons"],
    queryFn: async () => {
      const response = await apiClient.get<Lesson[]>("/lessons");
      return response.data;
    },
  });
}

/**
 * Занятие, которое сейчас идёт в зале.
 */
export function useActiveRun() {
  return useQuery({
    queryKey: ["lessons", "active"],
    queryFn: async () => {
      const response = await apiClient.get<LessonRun | null>("/lessons/active");
      return response.data;
    },
    refetchInterval: 5_000,
  });
}

/**
 * Старт и стоп занятия с обновлением карточек комплексов.
 */
export function useLessonActions() {
  const queryClient = useQueryClient();

  const invalidateHall = async () => {
    await queryClient.invalidateQueries({ queryKey: ["lessons"] });
    await queryClient.invalidateQueries({ queryKey: ["devices"] });
    await queryClient.invalidateQueries({ queryKey: ["clocks"] });
  };

  const start = useMutation({
    mutationFn: async (lessonId: string) => {
      const response = await apiClient.post<LessonRun>(`/lessons/${lessonId}/start`);
      return response.data;
    },
    onSuccess: invalidateHall,
  });

  const stop = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post<LessonRun | null>("/lessons/stop");
      return response.data;
    },
    onSuccess: invalidateHall,
  });

  return { start, stop };
}
