#pragma once
#include <cstdint>
#include <vector>
#define INVALID_SERVO 255
extern std::vector<int> attachAngles;
struct Servo {
  bool active = false;
  int angle = 90;
  int pin = -1;
  void write(int n) { angle = n; }
  uint8_t attach(int p) {
    attachAngles.push_back(angle);
    pin = p; active = true; return 0;
  }
  void detach() { active = false; }
};
