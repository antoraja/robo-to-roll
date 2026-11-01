#pragma once
#include "Arduino.h"
#define WIFI_AP 2
struct WiFiClass {
  void mode(int) {}
  bool softAP(const char* ssid, const char* pw) { return ssid && pw && strlen(pw) >= 8; }
  IPAddress softAPIP() { return IPAddress(); }
};
extern WiFiClass WiFi;
