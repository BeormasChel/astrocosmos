import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { Material, MaterialKind } from "../types/material";

export interface MaterialFilters {
  kind?: MaterialKind | "";
  deviceId?: string;
}

export interface MaterialPayload {
  title: string;
  kind: MaterialKind;
  deviceId: string;
  body: string;
  clipKey: string;
  rfidUid: string;
  file?: File | null;
}

/**
 * Собрать multipart-форму без пустого файла (иначе сервер думает, что файл есть).
 */
function toFormData(payload: MaterialPayload): FormData {
  const form = new FormData();
  form.append("title", payload.title);
  form.append("kind", payload.kind);
  form.append("device_id", payload.deviceId);
  form.append("body", payload.body);
  form.append("clip_key", payload.clipKey);
  form.append("rfid_uid", payload.rfidUid);
  if (payload.file) {
    form.append("file", payload.file);
  }
  return form;
}

/**
 * Полка материалов с фильтрами по виду и комплексу.
 */
export function useMaterials(filters: MaterialFilters) {
  return useQuery({
    queryKey: ["materials", filters],
    queryFn: async () => {
      const response = await apiClient.get<Material[]>("/materials", {
        params: {
          kind: filters.kind || undefined,
          device_id: filters.deviceId || undefined,
        },
      });
      return response.data;
    },
  });
}

/**
 * Добавление, правка и удаление материалов педагогом.
 */
export function useMaterialActions() {
  const queryClient = useQueryClient();
  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["materials"] });

  const create = useMutation({
    mutationFn: async (payload: MaterialPayload) => {
      const response = await apiClient.post<Material>("/materials", toFormData(payload), {
        timeout: 120_000,
      });
      return response.data;
    },
    onSuccess: invalidate,
  });

  const update = useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: MaterialPayload }) => {
      const response = await apiClient.patch<Material>(
        `/materials/${id}`,
        toFormData(payload),
        { timeout: 120_000 },
      );
      return response.data;
    },
    onSuccess: invalidate,
  });

  const remove = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/materials/${id}`);
    },
    onSuccess: invalidate,
  });

  return { create, update, remove };
}
