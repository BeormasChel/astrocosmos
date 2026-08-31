/**
 * Адрес окна иллюминатора на том же хосте, что пульт педагога.
 */
export function illuminatorWindowUrl(): string {
  return `http://${window.location.hostname}:3001`;
}

/**
 * Адрес киоска малого голобокса (тач-меню разделов).
 */
export function malyHoloboxUrl(): string {
  return `http://${window.location.hostname}:3001/maly`;
}
