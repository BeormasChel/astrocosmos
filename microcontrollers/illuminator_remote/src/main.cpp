/**
 * @file main.cpp
 * @brief Заглушка пульта Иллюминатора (выбор сценария 4K-видео).
 */

#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  Serial.println("illuminator_remote firmware stub");
}

void loop() {
  delay(1000);
}
