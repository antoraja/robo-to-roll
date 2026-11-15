#pragma once
#include "Arduino.h"
#define WIFI_AP 2
#define WIFI_AP_STA 3
enum wifi_power_t { WIFI_POWER_19_5dBm = 78, WIFI_POWER_8_5dBm = 34 };
struct WiFiClass {
  void mode(int m) { lastMode = m; }
  bool softAP(const char* ssid, const char* pw, int channel = 1) { return ssid && pw && strlen(pw) >= 8 && channel >= 1 && channel <= 13; }
  bool softAPdisconnect(bool) { return true; }
  String softAPmacAddress() { return String("00:00:00:00:00:00"); }
  unsigned char softAPgetStationNum() { return 0; }
  IPAddress softAPIP() { return IPAddress(); }
  int lastMode = 0; wifi_power_t power = WIFI_POWER_19_5dBm;
  bool setTxPower(wifi_power_t p) { power = p; return true; }
  int scanNetworks() { return 2; }
  String SSID(int i) { return String(i ? "Neighbour" : "HomeWiFi"); }
  int RSSI(int i) { return i ? -80 : -45; }
  int channel(int i) { return i ? 11 : 1; }
  void scanDelete() {}
};
extern WiFiClass WiFi;
