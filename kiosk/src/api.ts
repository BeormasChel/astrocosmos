export interface IlluminatorClip {
  clipKey: string;
  title: string;
  hasFile: boolean;
  videoUrl: string | null;
}

export interface IlluminatorWindow {
  deviceId: string;
  mode: "attract" | "play" | string;
  clip: IlluminatorClip | null;
  attract: IlluminatorClip[];
}

const HEARTBEAT_MS = 10_000;
const POLL_MS = 2_000;

/**
 * Спросить ядро, что показывать в окне.
 */
export async function fetchIlluminatorWindow(): Promise<IlluminatorWindow> {
  const response = await fetch("/api/v1/kiosk/illuminator");
  if (!response.ok) {
    throw new Error("window");
  }
  return (await response.json()) as IlluminatorWindow;
}

/**
 * Сказать ядру, что иллюминатор жив.
 */
export async function sendIlluminatorHeartbeat(): Promise<void> {
  await fetch("/api/v1/devices/illuminator/heartbeat", { method: "POST" });
}

export interface HoloboxSection {
  id: string;
  title: string;
  hint: string;
  hasFile: boolean;
  videoUrl: string | null;
}

export interface HoloboxWindow {
  deviceId: string;
  mode: "attract" | "section" | string;
  lessonLocked: boolean;
  idleSeconds: number;
  section: HoloboxSection | null;
  sections: HoloboxSection[];
}

/**
 * Спросить ядро, какой раздел открыть на малом голобоксе.
 */
export async function fetchHoloboxWindow(): Promise<HoloboxWindow> {
  const response = await fetch("/api/v1/kiosk/maly");
  if (!response.ok) {
    throw new Error("holobox");
  }
  return (await response.json()) as HoloboxWindow;
}

/**
 * Сказать ядру, что малый голобокс жив.
 */
export async function sendHoloboxHeartbeat(): Promise<void> {
  await fetch("/api/v1/devices/maly_golobox/heartbeat", { method: "POST" });
}

export { HEARTBEAT_MS, POLL_MS };
