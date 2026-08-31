export type MaterialKind = "video" | "text" | "scientist";

export interface Material {
  id: string;
  kind: MaterialKind;
  kindLabel: string;
  title: string;
  body: string | null;
  deviceId: string | null;
  deviceName: string;
  clipKey: string | null;
  rfidUid: string | null;
  hasFile: boolean;
  originalName: string | null;
  mimeType: string | null;
  byteSize: number | null;
  createdBy: string;
  createdAt: string;
}

export const MATERIAL_KIND_OPTIONS: { id: MaterialKind; label: string; hint: string }[] = [
  { id: "video", label: "Ролик", hint: "Иллюминатор и голобоксы" },
  { id: "text", label: "Текст", hint: "Факт или подпись на экране" },
  { id: "scientist", label: "Учёный", hint: "Фигурка и метка RFID" },
];
