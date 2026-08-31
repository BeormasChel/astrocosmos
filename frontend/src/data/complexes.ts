import type { Complex, Lesson } from "../types/device";

/**
 * Каталог комплексов 1–6 для админки до появления MQTT.
 * Тумба не отдельная карточка — поле rfidPedestal у большого голобокса.
 */
export const COMPLEXES: Complex[] = [
  {
    id: "maly_golobox",
    number: 1,
    name: "Малый Голобокс",
    purpose: "Метеорит: касания, видеофрагменты, простая 3D-модель",
    platform: "Raspberry Pi",
    status: "unknown",
    currentMode: "Ещё не подключался",
  },
  {
    id: "bolshoy_golobox",
    number: 2,
    name: "Большой Голобокс",
    purpose: "Групповой экран: разделы астрономии и учёные",
    platform: "Raspberry Pi",
    status: "unknown",
    currentMode: "Ещё не подключался",
    rfidPedestal: {
      name: "Тумба с фигурками",
      reader: "PN532",
      attachedTo: "bolshoy_golobox",
    },
  },
  {
    id: "desktop_diptych",
    number: 3,
    name: "Настольный Диптих",
    purpose: "Голос, метки PN532, свет и жалюзи через ядро",
    platform: "ESP32-S3",
    status: "unknown",
    currentMode: "Ещё не подключался",
  },
  {
    id: "planet_clock",
    number: 4,
    name: "Астрономические часы",
    purpose: "Как течёт время на разных планетах",
    platform: "ESP32",
    status: "unknown",
    currentMode: "Ещё не подключался",
  },
  {
    id: "illuminator",
    number: 5,
    name: "Иллюминатор",
    purpose: "Окно в космос, 4K-видео",
    platform: "Raspberry Pi 5",
    status: "unknown",
    currentMode: "Ещё не подключался",
  },
  {
    id: "astrovizor",
    number: 6,
    name: "Астровизор",
    purpose: "Картинка с камеры купола на экран (не Vizor)",
    platform: "Raspberry Pi",
    status: "unknown",
    currentMode: "Ещё не подключался",
  },
];

/** Примеры занятий — чтобы педагог сразу видел модель, не пустой список. */
export const SAMPLE_LESSONS: Lesson[] = [
  {
    id: "welcome",
    title: "Знакомство с кораблём",
    durationMin: 8,
    forWhom: "Экскурсия, 6–10 лет",
    complexIds: ["illuminator", "planet_clock", "maly_golobox"],
  },
  {
    id: "meteorite",
    title: "Челябинский метеорит",
    durationMin: 12,
    forWhom: "Занятие, 9–14 лет",
    complexIds: ["maly_golobox", "illuminator"],
  },
  {
    id: "scientists",
    title: "Встреча с учёными",
    durationMin: 15,
    forWhom: "Группа у большого экрана",
    complexIds: ["bolshoy_golobox"],
  },
];
