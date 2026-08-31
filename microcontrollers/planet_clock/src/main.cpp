/**
 * @file main.cpp
 * @brief Астрономические часы: три кольца WS2812 и MQTT-режимы ядра.
 *
 * Топик команд: astroc/devices/planet_clock/command
 * Топик статуса: astroc/devices/planet_clock/status
 *
 * Сборка: PlatformIO, плата Seeed XIAO ESP32-C3.
 * SSID и пароль Wi‑Fi задайте в platformio_override.ini (не в git).
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <FastLED.h>

#ifndef WIFI_SSID
#define WIFI_SSID "astrocosmos"
#endif
#ifndef WIFI_PASSWORD
#define WIFI_PASSWORD "changeme"
#endif
#ifndef MQTT_HOST
#define MQTT_HOST "192.168.1.10"
#endif
#ifndef MQTT_PORT
#define MQTT_PORT 1883
#endif
#ifndef MQTT_USER
#define MQTT_USER ""
#endif
#ifndef MQTT_PASSWORD
#define MQTT_PASSWORD ""
#endif

static const char *kDeviceId = "planet_clock";
static const char *kCommandTopic = "astroc/devices/planet_clock/command";
static const char *kStatusTopic = "astroc/devices/planet_clock/status";

static const uint8_t kLedPin = 10;
static const uint16_t kLedsPerRing = 60;
static const uint8_t kRingCount = 3;
static const uint16_t kLedCount = kLedsPerRing * kRingCount;

/** Кольца: 0 Земля, 1 Юпитер, 2 Венера — сценарии compare / retrograde. */
enum RingId : uint8_t { kRingEarth = 0, kRingJupiter = 1, kRingVenus = 2 };

enum ClockMode : uint8_t {
  kModeIdle = 0,
  kModeCompare = 1,
  kModeRetrograde = 2,
  kModeJupiter = 3
};

CRGB gLeds[kLedCount];
WiFiClient gWifi;
PubSubClient gMqtt(gWifi);
ClockMode gMode = kModeIdle;
uint32_t gLastStatusMs = 0;

static const uint32_t kStatusPeriodMs = 10000;
static const uint32_t kEarthPeriodMs = 12000;
static const uint32_t kJupiterPeriodMs = 5000;
static const uint32_t kVenusPeriodMs = 36000;

/**
 * @brief Собрать период оборота кольца в миллисекундах.
 */
uint32_t ringPeriodMs(uint8_t ring) {
  if (ring == kRingJupiter) {
    return kJupiterPeriodMs;
  }
  if (ring == kRingVenus) {
    return kVenusPeriodMs;
  }
  return kEarthPeriodMs;
}

/**
 * @brief Яркость кольца в текущем режиме.
 */
uint8_t ringBrightness(uint8_t ring) {
  switch (gMode) {
    case kModeCompare:
      return (ring == kRingEarth || ring == kRingJupiter) ? 180 : 28;
    case kModeRetrograde:
      return (ring == kRingVenus) ? 180 : 28;
    case kModeJupiter:
      return (ring == kRingJupiter) ? 200 : 22;
    case kModeIdle:
    default:
      return 90;
  }
}

/**
 * @brief Цвет кольца (Земля / Юпитер / Венера).
 */
CRGB ringColor(uint8_t ring) {
  if (ring == kRingJupiter) {
    return CRGB(212, 165, 116);
  }
  if (ring == kRingVenus) {
    return CRGB(232, 195, 106);
  }
  return CRGB(74, 163, 255);
}

/**
 * @brief Нарисовать три кольца: один яркий «луч» на каждое.
 */
void drawRings() {
  const uint32_t now = millis();
  fill_solid(gLeds, kLedCount, CRGB::Black);

  for (uint8_t ring = 0; ring < kRingCount; ring++) {
    const uint32_t period = ringPeriodMs(ring);
    uint32_t pos = (now / (period / kLedsPerRing)) % kLedsPerRing;

    // Венера в ретрограде и в idle крутится назад.
    const bool reverse = (ring == kRingVenus);
    if (reverse) {
      pos = (kLedsPerRing - 1) - pos;
    }

    const uint16_t index = ring * kLedsPerRing + pos;
    CRGB color = ringColor(ring);
    color.nscale8(ringBrightness(ring));
    gLeds[index] = color;

    // Хвост луча, чтобы движение читалось с расстояния.
    const uint16_t tail = ring * kLedsPerRing + ((pos + kLedsPerRing - 1) % kLedsPerRing);
    CRGB dim = color;
    dim.nscale8(70);
    gLeds[tail] = dim;
  }

  FastLED.show();
}

/**
 * @brief Разобрать JSON команды ядра.
 */
void applyCommand(const char *json) {
  JsonDocument doc;
  const DeserializationError err = deserializeJson(doc, json);
  if (err) {
    return;
  }

  const char *command = doc["command"] | "idle";
  if (strcmp(command, "idle") == 0) {
    gMode = kModeIdle;
    return;
  }
  if (strcmp(command, "set_mode") != 0) {
    return;
  }

  const char *mode = doc["mode"] | "idle";
  if (strcmp(mode, "compare") == 0) {
    gMode = kModeCompare;
  } else if (strcmp(mode, "retrograde") == 0) {
    gMode = kModeRetrograde;
  } else if (strcmp(mode, "jupiter") == 0) {
    gMode = kModeJupiter;
  } else {
    gMode = kModeIdle;
  }
}

void onMqttMessage(char *topic, byte *payload, unsigned int length) {
  (void)topic;
  char buffer[256];
  const unsigned int copy = length < sizeof(buffer) - 1 ? length : sizeof(buffer) - 1;
  memcpy(buffer, payload, copy);
  buffer[copy] = '\0';
  applyCommand(buffer);
}

/**
 * @brief Подключиться к брокеру ядра и подписаться на команды.
 */
void ensureMqtt() {
  if (gMqtt.connected()) {
    return;
  }
  const String clientId = String("astrocosmos-") + kDeviceId;
  bool ok = false;
  if (strlen(MQTT_USER) > 0) {
    ok = gMqtt.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD);
  } else {
    ok = gMqtt.connect(clientId.c_str());
  }
  if (!ok) {
    return;
  }
  gMqtt.subscribe(kCommandTopic, 1);
}

/**
 * @brief Сообщить ядру, что часы на связи.
 */
void publishStatus() {
  if (!gMqtt.connected()) {
    return;
  }
  JsonDocument doc;
  doc["status"] = "online";
  doc["deviceId"] = kDeviceId;
  doc["mode"] = static_cast<int>(gMode);
  char body[160];
  serializeJson(doc, body, sizeof(body));
  gMqtt.publish(kStatusTopic, body);
}

void setup() {
  Serial.begin(115200);
  FastLED.addLeds<WS2812B, kLedPin, GRB>(gLeds, kLedCount);
  FastLED.setBrightness(120);
  fill_solid(gLeds, kLedCount, CRGB::Black);
  FastLED.show();

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  gMqtt.setServer(MQTT_HOST, MQTT_PORT);
  gMqtt.setCallback(onMqttMessage);
}

void loop() {
  // Ждём Wi‑Fi, не блокируя ленту надолго.
  if (WiFi.status() != WL_CONNECTED) {
    drawRings();
    delay(20);
    return;
  }

  ensureMqtt();
  gMqtt.loop();
  drawRings();

  const uint32_t now = millis();
  if (now - gLastStatusMs >= kStatusPeriodMs) {
    gLastStatusMs = now;
    publishStatus();
  }
  delay(16);
}
