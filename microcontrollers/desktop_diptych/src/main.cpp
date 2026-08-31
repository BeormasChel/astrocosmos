/**
 * @file main.cpp
 * @brief Заглушка прошивки настольного помощника «Диптих».
 *
 * Экран T-Panel, RFID (PN532/MFRC522), захват аудио. STT/TTS выполняются на сервере.
 * Не путать с T-Panel обсерваторного «Диптиха».
 */

#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  Serial.println("desktop_diptych firmware stub");
}

void loop() {
  delay(1000);
}
