export type DeviceStatus = "online" | "offline" | "degraded" | "unknown";

export interface RfidPedestal {
  name: string;
  reader: "PN532";
  attachedTo: "bolshoy_golobox";
}

export interface Complex {
  id: string;
  number: number | null;
  name: string;
  purpose: string;
  platform: string;
  status: DeviceStatus;
  currentMode: string;
  rfidPedestal?: RfidPedestal;
}

export interface Lesson {
  id: string;
  title: string;
  durationMin: number;
  forWhom: string;
  complexIds: string[];
}
