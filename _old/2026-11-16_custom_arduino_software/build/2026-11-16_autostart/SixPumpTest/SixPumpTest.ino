// Arduino UNO / ATmega328P, 5 V logic, AVR core 1.8.8, Servo 1.3.0.
// Explicitly requested autonomous test: after each power-up/reset, all six ON
// for 3 seconds, then permanent candidate OFF. No serial command protocol.
// Upload with shield removed. Refit shield only with USB and adapter unplugged.
// Operate from the matched adapter with USB disconnected; remove adapter if
// a pump fails to stop. Signal OFF is not an independent power cutoff.
// The pins follow the new map confirmed by the operator on 2026-11-16.

#include <Servo.h>

#if !defined(ARDUINO_AVR_UNO)
#error "This sketch targets Arduino UNO / ATmega328P."
#endif

// All editable test settings are here. Valves D10-D12 are not controlled.
constexpr uint8_t kPumpPins[] = {3, 4, 5, 6, 7, 8};
constexpr uint8_t kPumpCount = sizeof(kPumpPins) / sizeof(kPumpPins[0]);
constexpr uint8_t kOn = 180;
constexpr uint8_t kOff = 0;
constexpr unsigned long kStartupMs = 2000UL;
constexpr unsigned long kRunMs = 3000UL;

Servo pumps[kPumpCount];
enum class Phase : uint8_t { Waiting, Running, Finished };
Phase phase = Phase::Waiting;
unsigned long phaseStartedMs;

void setAll(uint8_t command) {
  for (uint8_t i = 0; i < kPumpCount; ++i) {
    pumps[i].write(command);
  }
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  bool attached = true;
  for (uint8_t i = 0; i < kPumpCount; ++i) {
    // Preload OFF before attach: avoid the default 1500 us Servo setpoint.
    pumps[i].write(kOff);
    if (pumps[i].attach(kPumpPins[i]) == INVALID_SERVO) {
      attached = false;
    }
  }
  setAll(kOff);
  if (!attached) {
    phase = Phase::Finished;
  }
  phaseStartedMs = millis();
}

void loop() {
  const unsigned long now = millis();
  if (phase == Phase::Waiting && now - phaseStartedMs >= kStartupMs) {
    setAll(kOn);
    digitalWrite(LED_BUILTIN, HIGH);  // commanded ON phase, not pump feedback
    phaseStartedMs = now;
    phase = Phase::Running;
  } else if (phase == Phase::Running && now - phaseStartedMs >= kRunMs) {
    setAll(kOff);
    digitalWrite(LED_BUILTIN, LOW);
    phase = Phase::Finished;
  }
  // Servo keeps transmitting OFF in Finished; only power-up/reset repeats.
}
