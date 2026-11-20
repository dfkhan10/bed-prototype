// Bounded D2+D4 opposite-pump test for Arduino UNO.
// D2 = inflate, D4 = deflate of group 1. Both commanded ON together,
// then both OFF. No other pins. Autostart after upload/power/reset.
// ON=180 / OFF=0 follow seller Servo commands; physical stop needs observation.

#include <Servo.h>

#if !defined(ARDUINO_AVR_UNO)
#error "This sketch targets the ATmega328P Arduino UNO."
#endif

constexpr uint8_t kInflatePin = 2;
constexpr uint8_t kDeflatePin = 4;
constexpr uint8_t kOn = 180;
constexpr uint8_t kOff = 0;
constexpr uint8_t kCycleCount = 2;
constexpr unsigned long kOnMs = 5000UL;
constexpr unsigned long kOffMs = 3000UL;

Servo inflatePump;
Servo deflatePump;

void setPair(uint8_t command) {
  inflatePump.write(command);
  deflatePump.write(command);
}

void setup() {
  inflatePump.write(kOff);
  deflatePump.write(kOff);
  inflatePump.attach(kInflatePin);
  deflatePump.attach(kDeflatePin);
  setPair(kOff);

  for (uint8_t cycle = 0; cycle < kCycleCount; ++cycle) {
    // Opposite roles, same time: D2 inflates while D4 deflates.
    setPair(kOn);
    delay(kOnMs);
    setPair(kOff);
    delay(kOffMs);
  }

  setPair(kOff);
}

void loop() {
  // Final OFF pulses continue; reset repeats the two cycles.
}
