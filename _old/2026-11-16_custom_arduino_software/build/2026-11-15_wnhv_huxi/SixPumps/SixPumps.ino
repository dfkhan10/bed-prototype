// Based on the seller's qiuqiu4zu.ino, retained unchanged beside this sketch.
// Target: Arduino UNO / ATmega328P, AVR core 1.8.8, Servo 1.3.0, 5 V logic.
// Starts automatically after upload, power-up or reset.
// Six pumps: 8 seconds ON, 8 seconds OFF, three cycles; then stays OFF.
// 180/0 retain the seller's ON/OFF commands; physical response needs observation.
// Connected valves on D10/D11/D12 are not controlled by this sketch.
// Motors can receive power from USB in the present wiring. Do not use the
// computer's USB supply for this six-pump test. External/USB isolation is unverified.

#include <Servo.h>

#if !defined(ARDUINO_AVR_UNO)
#error "This sketch targets the ATmega328P Arduino UNO."
#endif

constexpr uint8_t kPinA1 = 4;
constexpr uint8_t kPinA2 = 5;
constexpr uint8_t kPinB1 = 3;
constexpr uint8_t kPinA3 = 7;
constexpr uint8_t kPinA4 = 8;
constexpr uint8_t kPinB2 = 6;

constexpr uint8_t kPumpPins[] = {
  kPinA1, kPinA2, kPinB1, kPinA3, kPinA4, kPinB2
};
constexpr uint8_t kPumpCount = sizeof(kPumpPins) / sizeof(kPumpPins[0]);
constexpr uint8_t kCycleCount = 3;
constexpr unsigned long kPhaseMs = 8000UL;
constexpr uint8_t kOn = 180;
constexpr uint8_t kOff = 0;

Servo pumps[kPumpCount];

void setAllPumps(uint8_t command) {
  for (uint8_t pump = 0; pump < kPumpCount; ++pump) {
    pumps[pump].write(command);
  }
}

void setup() {
  for (uint8_t pump = 0; pump < kPumpCount; ++pump) {
    // Preload OFF before attach, avoiding the library's default 1500 us pulse.
    pumps[pump].write(kOff);
    pumps[pump].attach(kPumpPins[pump]);
  }

  for (uint8_t cycle = 0; cycle < kCycleCount; ++cycle) {
    setAllPumps(kOn);
    delay(kPhaseMs);
    setAllPumps(kOff);
    delay(kPhaseMs);
  }
}

void loop() {
  // Servo continues the final OFF pulses. Reset repeats the three cycles.
}
