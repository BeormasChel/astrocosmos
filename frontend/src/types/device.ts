/** Общие TypeScript-типы админки. */

export type DeviceStatus = "online" | "offline" | "degraded" | "unknown";

export interface Device {
  id: string;
  name: string;
  status: DeviceStatus;
}
