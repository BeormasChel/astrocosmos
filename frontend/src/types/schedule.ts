export interface ScheduleSlot {
  id: string;
  lessonId: string;
  lessonTitle: string;
  weekday: number;
  weekdayLabel: string;
  time: string;
  isEnabled: boolean;
  nextAt: string | null;
  nextHint: string;
  createdBy: string;
}

export const WEEKDAY_OPTIONS = [
  { id: 0, label: "Пн", full: "Понедельник" },
  { id: 1, label: "Вт", full: "Вторник" },
  { id: 2, label: "Ср", full: "Среда" },
  { id: 3, label: "Чт", full: "Четверг" },
  { id: 4, label: "Пт", full: "Пятница" },
  { id: 5, label: "Сб", full: "Суббота" },
  { id: 6, label: "Вс", full: "Воскресенье" },
];
