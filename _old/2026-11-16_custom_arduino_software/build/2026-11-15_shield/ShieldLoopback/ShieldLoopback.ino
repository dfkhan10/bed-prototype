// UNO / ATmega328P, Arduino AVR 1.8.8, no external libraries.
// Shield-only diagnostic: disconnect ALL peripherals and external power.
// USB only. Jumper, when requested: D3 S to D4 S. Never + or -.
// Boot leaves both pins as inputs; commands: BASELINE, TEST, HELP.
// TEST releases each output before reversing direction, then releases both.
#include <Arduino.h>
#include <string.h>

#if !defined(ARDUINO_AVR_UNO)
#error "This sketch targets the ATmega328P UNO only."
#endif

constexpr uint8_t kA = 3;
constexpr uint8_t kB = 4;
char command[16];
uint8_t used = 0;
bool overflow = false;

void releasePins() {
  pinMode(kA, INPUT);
  pinMode(kB, INPUT);
  digitalWrite(kA, LOW);
  digitalWrite(kB, LOW);
}

uint8_t testDirection(uint8_t outputPin, uint8_t inputPin) {
  releasePins();
  pinMode(inputPin, INPUT_PULLUP);
  digitalWrite(outputPin, LOW);
  pinMode(outputPin, OUTPUT);
  uint8_t failures = 0;
  for (uint8_t cycle = 0; cycle < 10; ++cycle) {
    digitalWrite(outputPin, LOW);
    delay(2);
    if (digitalRead(inputPin) != LOW) ++failures;
    digitalWrite(outputPin, HIGH);
    delay(2);
    if (digitalRead(inputPin) != HIGH) ++failures;
  }
  releasePins();
  Serial.print(F("D")); Serial.print(outputPin);
  Serial.print(F("->D")); Serial.print(inputPin);
  Serial.print(F(" mismatches=")); Serial.print(failures);
  Serial.println(F("/20"));
  return failures;
}

void processCommand() {
  command[used] = '\0';
  if (overflow) {
    Serial.println(F("ERROR command_too_long"));
  } else if (!strcmp(command, "BASELINE")) {
    releasePins();
    pinMode(kA, INPUT_PULLUP);
    pinMode(kB, INPUT_PULLUP);
    delay(2);
    Serial.print(F("BASELINE D3=")); Serial.print(digitalRead(kA));
    Serial.print(F(" D4=")); Serial.println(digitalRead(kB));
    releasePins();
  } else if (!strcmp(command, "TEST")) {
    uint8_t failures = testDirection(kA, kB);
    failures += testDirection(kB, kA);
    Serial.print(F("TOTAL mismatches=")); Serial.print(failures);
    Serial.println(F("/40; pins_released=1"));
  } else if (!strcmp(command, "HELP")) {
    Serial.println(F("SHIELD_LOOPBACK 2026-11-15; BASELINE TEST HELP"));
  } else if (used) {
    Serial.println(F("ERROR unknown_command"));
  }
  used = 0;
  overflow = false;
}

void setup() {
  releasePins();
  Serial.begin(115200);
  Serial.println(F("SHIELD_LOOPBACK 2026-11-15; ready; inputs_only"));
}

void loop() {
  while (Serial.available()) {
    char c = static_cast<char>(Serial.read());
    if (c == '\r' || c == '\n') {
      if (used || overflow) processCommand();
    } else if (c >= 32 && c <= 126 && !overflow) {
      if (used < sizeof(command) - 1) command[used++] = c;
      else overflow = true;
    } else {
      overflow = true;
    }
  }
}
