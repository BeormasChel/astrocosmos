/**
 * @file main.cpp
 * @brief Заглушка управления поворотным механизмом Астровизора (Az/El).
 *
 * Купольные Vizor-1/2 обсерватории сюда не входят — они в проекте Diptich_hub.
 */

#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  Serial.println("astrovizor_gimbal firmware stub");
}

void loop() {
  delay(1000);
}
