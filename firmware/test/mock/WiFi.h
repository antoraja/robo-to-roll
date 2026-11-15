#pragma once
#include "Arduino.h"
#define WIFI_AP 2
struct WiFiClass {
  void mode(int) {}
  bool softAP(const char* ssid, const char* pw, int channel = 1) { return ssid && pw && strlen(pw) >= 8 && channel >= 1 && channel <= 13; }
  bool softAPdisconnect(bool) { return true; }
  String softAPmacAddress() { return String("00:00:00:00:00:00"); }
  unsigned char softAPgetStationNum() { return 0; }
  IPAddress softAPIP() { return IPAddress(); }
};
extern WiFiClass WiFi;
