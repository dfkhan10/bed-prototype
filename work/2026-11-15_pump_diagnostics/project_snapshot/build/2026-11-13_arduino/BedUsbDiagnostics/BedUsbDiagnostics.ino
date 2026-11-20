// USB diagnostics only. This sketch contains no actuator commands.
// INPUT is high impedance; it is NOT a verified OFF state for an unknown driver.
// The roles below are proposed wiring labels, not detected hardware identities.

#include <Arduino.h>
#include <string.h>

#if !defined(__AVR_ATmega328P__)
#error "This diagnostic build currently supports only the ATmega328P target."
#endif

const uint8_t kPins[] = {3, 5, 6};
const char *const kRoles[] = {"pump_1", "pump_2", "valve_1"};
char command[24];
uint8_t commandLength = 0;
bool commandOverflow = false;

void printStatus() {
  Serial.println(F("BED_USB_DIAGNOSTICS 2026-11-13 v1"));
  Serial.print(F("build_target=arduino:avr:uno; F_CPU="));
  Serial.println(F_CPU);
  Serial.println(F("actuator_commands=disabled; wiring_identity=unverified"));
  Serial.println(F("mode=INPUT; pullups=disabled; high_impedance_is_not_verified_OFF"));
  for (uint8_t i = 0; i < sizeof(kPins) / sizeof(kPins[0]); ++i) {
    Serial.print('D');
    Serial.print(kPins[i]);
    Serial.print(F(" proposed_role="));
    Serial.print(kRoles[i]);
    Serial.print(F(" input_level="));
    Serial.println(digitalRead(kPins[i]));
  }
  Serial.println(F("Input levels do not identify connected loads or prove wiring."));
}

void processCommand() {
  command[commandLength] = '\0';
  if (commandOverflow) {
    Serial.println(F("ERROR command_too_long"));
  } else if (!strcmp(command, "INFO") || !strcmp(command, "STATUS")) {
    printStatus();
  } else if (!strcmp(command, "HELP")) {
    Serial.println(F("Commands: INFO STATUS HELP. No actuator control."));
  } else if (commandLength) {
    Serial.println(F("ERROR unsupported_command; actuator_commands=disabled"));
  }
  commandLength = 0;
  commandOverflow = false;
}

void setup() {
  for (uint8_t i = 0; i < sizeof(kPins) / sizeof(kPins[0]); ++i) {
    pinMode(kPins[i], INPUT);
  }
  Serial.begin(115200);
  printStatus();
}

void loop() {
  while (Serial.available()) {
    const char next = static_cast<char>(Serial.read());
    if (next == '\n' || next == '\r') {
      processCommand();
    } else if (next >= 32 && next <= 126) {
      if (commandLength < sizeof(command) - 1) {
        command[commandLength++] = next;
      } else {
        commandOverflow = true;
      }
    }
  }
}
