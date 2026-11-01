#pragma once
#include "Arduino.h"
struct ESP32PWM { static void allocateTimer(int) {} };
struct Servo {
  int pin = -1, angle = -1, writes = 0;
  void setPeriodHertz(int) {}
  int attach(int p, int, int) { pin = p; return 1; }
  void write(int a) { if (a < 0 || a > 180) { printf("BAD ANGLE %d\n", a); exit(3); } angle = a; writes++; }
};
