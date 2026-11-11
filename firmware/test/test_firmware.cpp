// PC test of finger_control.ino: compiles the sketch with stand-in headers and checks behaviour.
#include "mock/Arduino.h"
#include "mock/WiFi.h"
#include "mock/WebServer.h"
#include "mock/ESP32Servo.h"
HardwareSerial Serial; WiFiClass WiFi;
#include "../finger_control/finger_control.ino"

static int fails = 0;
#define CHECK(c, msg) do { if (!(c)) { printf("FAIL: %s\n", msg); fails++; } else printf("ok:   %s\n", msg); } while (0)
static void run(unsigned long ms) { for (unsigned long t = 0; t < ms; t += 5) { delay(5); loop(); } }

int main() {
  setup();
  CHECK(NUM_FINGERS == 5, "5 fingers configured");
  int pins[5]; for (int i = 0; i < NUM_FINGERS; i++) pins[i] = servos[i].pin;
  CHECK(pins[0] == 25 && pins[1] == 13 && pins[2] == 14 && pins[3] == 27 && pins[4] == 26, "pins 25,13,14,27,26");
  // before calibration no finger may be driven past its end stop (spool groove 13.35 mm:
  // full curl = ~161 deg for a finger, ~107 deg for the thumb) and no pin may be a boot-strapping pin
  CHECK(abs(FINGERS[0].closedAngle - FINGERS[0].openAngle) <= 107, "thumb default range stays short of its end stop");
  bool safe = true; for (int i = 1; i < 5; i++) safe &= abs(FINGERS[i].closedAngle - FINGERS[i].openAngle) <= 155;
  CHECK(safe, "finger default ranges stay short of their end stops (<= 155 deg of 161)");
  bool noStrap = true; for (int i = 0; i < 5; i++) noStrap &= !(pins[i] == 0 || pins[i] == 2 || pins[i] == 5 || pins[i] == 12 || pins[i] == 15 || pins[i] >= 34);
  CHECK(noStrap, "no servo on a boot-strapping or input-only pin (0, 2, 5, 12, 15, 34-39)");
  for (int i = 0; i < NUM_FINGERS; i++) CHECK(servos[i].angle == FINGERS[i].openAngle, "servo starts at its open angle");
  CHECK(server.request("/") == 200 && server.lastBody.find("Fist") != std::string::npos, "web page has gesture buttons");
  CHECK(server.request("/set", {{"f", "1"}, {"v", "100"}}) == 200, "/set accepted");
  run(3000);
  CHECK(servos[1].angle == FINGERS[1].closedAngle, "index reaches closed angle smoothly");
  CHECK(server.request("/set", {{"f", "9"}, {"v", "50"}}) == 200, "/set with bad finger ignored (no crash)");
  CHECK(server.request("/set", {{"f", "1"}}) == 400, "/set without value rejected");
  CHECK(server.request("/set", {{"f", "2"}, {"v", "999"}}) == 200, "/set out-of-range value clamped");
  run(3000);
  CHECK(servos[2].angle == FINGERS[2].closedAngle, "clamped to 100 %");
  CHECK(server.request("/g", {{"n", "2"}}) == 200 && server.lastBody == "70,0,100,100,100", "gesture 'Point' returns its %");
  run(4000);
  CHECK(servos[1].angle == FINGERS[1].openAngle, "Point: index open");
  CHECK(servos[0].angle == percentToAngle(0, 70), "Point: thumb at 70 %");
  CHECK(server.request("/g", {{"n", "99"}}) == 400, "bad gesture rejected");
  CHECK(server.request("/all", {{"v", "0"}}) == 200, "/all open");
  run(4000);
  for (int i = 0; i < 5; i++) CHECK(servos[i].angle == FINGERS[i].openAngle, "all open");
  Serial.in = "a 1 90\n"; run(50); run(3000);
  CHECK(servos[1].angle == 90, "serial: raw angle command");
  Serial.in = "a 1 400\n"; run(3000);
  CHECK(servos[1].angle == 180, "serial: raw angle clamped to 180");
  Serial.in = "close\n"; run(4000);
  for (int i = 0; i < 5; i++) CHECK(servos[i].angle == FINGERS[i].closedAngle, "serial close all");
  printf("\n%s (%d failures)\n", fails ? "FIRMWARE TEST FAILED" : "FIRMWARE TEST PASSED", fails);
  return fails ? 1 : 0;
}
