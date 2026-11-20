// Candidate for UNO ATmega328P, Arduino AVR 1.8.8, Servo 1.3.0.
// D3 only. Upload with pump/driver and external supply DISCONNECTED.
// Planned physical test uses external 5 V only, with USB disconnected.
// On EVERY boot/reset: proposed OFF for 3 s, proposed ON for 300 ms,
// then proposed OFF continuously. No automatic repetition within a boot.
// Driver identity, pulse endpoints and OFF polarity are NOT established.
// Operator must remove external power if pump keeps running.
#include <Arduino.h>
#include <Servo.h>

#if !defined(ARDUINO_AVR_UNO)
#error "This candidate targets the ATmega328P UNO only."
#endif

constexpr uint8_t kPumpPin = 3;
constexpr int kProposedOffUs = 544;
constexpr int kProposedOnUs = 2400;
Servo pumpSignal;

void setup() {
  pinMode(kPumpPin, INPUT);
  // Preload before attach to avoid the library's default 1500 us pulse.
  pumpSignal.writeMicroseconds(kProposedOffUs);
  if (pumpSignal.attach(kPumpPin) == INVALID_SERVO) {
    pinMode(kPumpPin, INPUT);
    return;
  }
  pumpSignal.writeMicroseconds(kProposedOffUs);
  delay(3000);
  pumpSignal.writeMicroseconds(kProposedOnUs);
  delay(300);
  pumpSignal.writeMicroseconds(kProposedOffUs);
}

void loop() {
  // Servo interrupt continues the proposed OFF pulses. Reset repeats test.
}
