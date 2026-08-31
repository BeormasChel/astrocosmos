/**
 * @file main.cpp
 * @brief Заглушка прошивки астрономических часов (Planet Clock).
 *
 * Управление кольцами WS2812, NTP, MQTT-команды смены режима.
 * Реализация — первый физический комплекс в плане MVP.
 */

#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  Serial.println("planet_clock firmware stub");
}

void loop() {
  delay(1000);
}
