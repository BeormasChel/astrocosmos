export interface ClockPlanet {
  id: string;
  name: string;
  dayHours: number;
  retrograde: boolean;
  color: string;
  highlighted: boolean;
  visualSeconds: number;
  dayHint: string;
}

export interface ClockModeOption {
  id: string;
  label: string;
  hint: string;
}

export interface ClockState {
  deviceId: string;
  mode: string;
  label: string;
  title: string;
  hint: string;
  mqttConnected: boolean;
  planets: ClockPlanet[];
  modes: ClockModeOption[];
}
