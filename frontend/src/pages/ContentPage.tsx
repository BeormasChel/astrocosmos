import { FormEvent, useMemo, useState } from "react";
import { isAxiosError } from "axios";
import { PageHeader } from "../components/PageHeader";
import { useDevices } from "../hooks/useDevices";
import { useMaterialActions, useMaterials, type MaterialPayload } from "../hooks/useMaterials";
import { readStoredToken } from "../api/client";
import { useAuthStore } from "../stores/authStore";
import { MATERIAL_KIND_OPTIONS, type Material, type MaterialKind } from "../types/material";

const EMPTY_FORM: MaterialPayload = {
  title: "",
  kind: "video",
  deviceId: "illuminator",
  body: "",
  clipKey: "",
  rfidUid: "",
  file: null,
};

/**
 * Текст ошибки API для педагога, без жаргона.
 */
function explainError(error: unknown): string {
  if (isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
  }
  return "Не получилось сохранить. Проверьте поля и что ядро запущено.";
}

/**
 * Подставить комплекс по виду материала, чтобы не думать про id.
 */
function suggestedDevice(kind: MaterialKind): string {
  if (kind === "scientist") {
    return "bolshoy_golobox";
  }
  if (kind === "text") {
    return "maly_golobox";
  }
  return "illuminator";
}

/**
 * Открыть файл ролика или портрета в новой вкладке.
 */
async function openMaterialFile(id: string): Promise<void> {
  const token = readStoredToken();
  const response = await fetch(`/api/v1/materials/${id}/file`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) {
    throw new Error("file");
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  window.open(url, "_blank", "noopener");
}

function formatSize(bytes: number | null): string {
  if (!bytes) {
    return "";
  }
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))} КБ`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
}

/**
 * Материалы: ролики, тексты и учёные с метками RFID.
 */
export function ContentPage() {
  const role = useAuthStore((state) => state.user?.role);
  const canEdit = role === "admin" || role === "educator";
  const [kindFilter, setKindFilter] = useState<MaterialKind | "">("");
  const [deviceFilter, setDeviceFilter] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<MaterialPayload>(EMPTY_FORM);
  const [formError, setFormError] = useState<string | null>(null);
  const [fileKey, setFileKey] = useState(0);

  const { data: devices = [] } = useDevices();
  const { data: materials = [], isLoading } = useMaterials({
    kind: kindFilter,
    deviceId: deviceFilter,
  });
  const { create, update, remove } = useMaterialActions();
  const busy = create.isPending || update.isPending;

  const complexes = useMemo(
    () => devices.map((item) => ({ id: item.id, name: item.name })),
    [devices],
  );

  const resetForm = () => {
    setForm(EMPTY_FORM);
    setEditingId(null);
    setFormError(null);
    setFileKey((value) => value + 1);
  };

  const openCreate = () => {
    resetForm();
    setFormOpen(true);
  };

  const openEdit = (item: Material) => {
    setEditingId(item.id);
    setForm({
      title: item.title,
      kind: item.kind,
      deviceId: item.deviceId ?? "",
      body: item.body ?? "",
      clipKey: item.clipKey ?? "",
      rfidUid: item.rfidUid ?? "",
      file: null,
    });
    setFormError(null);
    setFileKey((value) => value + 1);
    setFormOpen(true);
  };

  const onKindChange = (kind: MaterialKind) => {
    setForm((current) => ({
      ...current,
      kind,
      deviceId: suggestedDevice(kind),
    }));
  };

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setFormError(null);
    try {
      if (editingId) {
        await update.mutateAsync({ id: editingId, payload: form });
      } else {
        await create.mutateAsync(form);
      }
      setFormOpen(false);
      resetForm();
    } catch (error) {
      setFormError(explainError(error));
    }
  };

  const onDelete = async (item: Material) => {
    const confirmed = window.confirm(`Убрать «${item.title}» с полки? Файл тоже удалится с сервера.`);
    if (!confirmed) {
      return;
    }
    try {
      await remove.mutateAsync(item.id);
      if (editingId === item.id) {
        setFormOpen(false);
        resetForm();
      }
    } catch (error) {
      setFormError(explainError(error));
    }
  };

  return (
    <section className="page">
      <PageHeader
        title="Материалы"
        lead="Сюда складываете ролики для иллюминатора и голобоксов, тексты и учёных с метками на фигурках. Файлы лежат на сервере зала, не на компьютере педагога."
        action={
          canEdit ? (
            <button type="button" className="btn btn--primary" onClick={openCreate}>
              Добавить материал
            </button>
          ) : null
        }
      />

      <div className="filters" role="group" aria-label="Что показать">
        <button
          type="button"
          className={`chip ${kindFilter === "" ? "chip--on" : ""}`}
          onClick={() => setKindFilter("")}
        >
          Все
        </button>
        {MATERIAL_KIND_OPTIONS.map((option) => (
          <button
            key={option.id}
            type="button"
            className={`chip ${kindFilter === option.id ? "chip--on" : ""}`}
            onClick={() => setKindFilter(option.id)}
          >
            {option.label}
          </button>
        ))}
        <label className="filters__select">
          Комплекс
          <select value={deviceFilter} onChange={(event) => setDeviceFilter(event.target.value)}>
            <option value="">Все комплексы</option>
            {complexes.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {formOpen && canEdit ? (
        <form className="material-form" onSubmit={onSubmit}>
          <h2 className="section-title">
            {editingId ? "Изменить материал" : "Новый материал"}
          </h2>
          <div className="kind-pills" role="radiogroup" aria-label="Вид материала">
            {MATERIAL_KIND_OPTIONS.map((option) => (
              <button
                key={option.id}
                type="button"
                role="radio"
                aria-checked={form.kind === option.id}
                className={`kind-pill ${form.kind === option.id ? "kind-pill--on" : ""}`}
                disabled={Boolean(editingId)}
                onClick={() => onKindChange(option.id)}
              >
                <span>{option.label}</span>
                <small>{option.hint}</small>
              </button>
            ))}
          </div>
          <label className="login__field">
            Как назвать
            <input
              value={form.title}
              onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
              placeholder="Например: Вид с МКС"
              required
            />
          </label>
          <label className="login__field">
            Для какого комплекса
            <select
              value={form.deviceId}
              onChange={(event) =>
                setForm((current) => ({ ...current, deviceId: event.target.value }))
              }
            >
              <option value="">Все комплексы</option>
              {complexes.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
          {form.kind === "video" ? (
            <label className="login__field">
              Короткое имя для занятия
              <input
                value={form.clipKey}
                onChange={(event) =>
                  setForm((current) => ({ ...current, clipKey: event.target.value }))
                }
                placeholder="welcome или impact"
              />
            </label>
          ) : null}
          {form.kind === "scientist" ? (
            <label className="login__field">
              UID метки на фигурке
              <input
                value={form.rfidUid}
                onChange={(event) =>
                  setForm((current) => ({ ...current, rfidUid: event.target.value }))
                }
                placeholder="Как на считывателе, например 04AA1122"
                required
              />
            </label>
          ) : null}
          {form.kind !== "video" ? (
            <label className="login__field">
              {form.kind === "scientist" ? "Что рассказать про учёного" : "Текст"}
              <textarea
                rows={4}
                value={form.body}
                onChange={(event) => setForm((current) => ({ ...current, body: event.target.value }))}
                required={form.kind === "text"}
              />
            </label>
          ) : null}
          {form.kind !== "text" ? (
            <label className="login__field">
              {form.kind === "video" ? "Видеофайл (можно позже)" : "Портрет или ролик (необязательно)"}
              <input
                key={fileKey}
                type="file"
                accept={form.kind === "video" ? "video/mp4,video/webm,video/quicktime" : "image/*,video/mp4"}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    file: event.target.files?.[0] ?? null,
                  }))
                }
              />
            </label>
          ) : null}
          {formError ? <p className="login__error">{formError}</p> : null}
          <div className="material-form__actions">
            <button className="btn btn--primary" type="submit" disabled={busy}>
              {busy ? "Сохраняем…" : "Сохранить"}
            </button>
            <button
              className="btn btn--ghost"
              type="button"
              onClick={() => {
                setFormOpen(false);
                resetForm();
              }}
            >
              Отмена
            </button>
          </div>
        </form>
      ) : null}

      {isLoading ? <p className="muted">Загружаем полку…</p> : null}

      {!isLoading && materials.length === 0 ? (
        <div className="empty">
          <p className="empty__title">Пока пусто</p>
          <p>
            Нажмите «Добавить материал», выберите комплекс и дайте ролику понятное
            имя. Детям на экране это имя показывать не обязательно.
          </p>
        </div>
      ) : (
        <ul className="lesson-list">
          {materials.map((item) => (
            <li key={item.id} className="lesson-card material-card">
              <div>
                <p className="material-card__kind">{item.kindLabel}</p>
                <h2 className="lesson-card__title">{item.title}</h2>
                <p className="lesson-card__meta">
                  {item.deviceName}
                  {item.clipKey && item.kind === "video" ? ` · ключ ${item.clipKey}` : ""}
                  {item.rfidUid ? ` · метка ${item.rfidUid}` : ""}
                  {item.hasFile && item.byteSize ? ` · ${formatSize(item.byteSize)}` : ""}
                  {!item.hasFile && item.kind === "video" ? " · файл ещё не загружен" : ""}
                </p>
                {item.body ? <p className="material-card__body">{item.body}</p> : null}
              </div>
              <div className="material-card__actions">
                {item.hasFile ? (
                  <button
                    type="button"
                    className="btn btn--ghost"
                    onClick={() => {
                      void openMaterialFile(item.id).catch(() => {
                        setFormError("Не получилось открыть файл.");
                      });
                    }}
                  >
                    Открыть файл
                  </button>
                ) : null}
                {canEdit ? (
                  <>
                    <button type="button" className="btn btn--ghost" onClick={() => openEdit(item)}>
                      Изменить
                    </button>
                    <button type="button" className="btn btn--ghost" onClick={() => void onDelete(item)}>
                      Убрать
                    </button>
                  </>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
