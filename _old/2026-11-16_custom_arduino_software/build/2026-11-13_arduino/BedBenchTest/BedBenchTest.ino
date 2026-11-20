// Bench candidate for arduino:avr:uno, Arduino AVR 1.8.8, Servo 1.3.0.
// Seller example uses 0/180 servo commands; this implementation uses the
// standard Servo endpoints (544/2400 us). The seller's NRRobot library mapping
// and actual switch polarity, signal-loss/reset behavior remain UNVERIFIED.
// Therefore command 0 is a PROPOSED OFF signal, not verified electrical OFF.
// Boot/DISABLE uses high impedance, which is also NOT a guaranteed OFF state.
// Physically disconnect loads for firmware identification and initial upload.
// Serial: 115200; ARM 3|5|6; RUN 100..500; STOP (or !); DISABLE; STATUS; HELP.
// One selected channel, explicit re-arm for every run, no automatic cycling.
// STOP/deadline continues the proposed OFF pulse train. DISABLE removes it.
// Timer1 is used by Servo; no physical or watchdog-based power cutoff exists.

#include <Arduino.h>
#include <Servo.h>
#include <string.h>

#if !defined(ARDUINO_AVR_UNO) && !defined(BED_HOST_TEST)
#error "Reference build supports the ATmega328P Arduino Uno target only."
#endif

constexpr int kPump1Pin = 3;
constexpr int kPump2Pin = 5;
constexpr int kValve1Pin = 6;
constexpr uint16_t kMinRunMs = 100;
constexpr uint16_t kMaxRunMs = 500;
constexpr uint8_t kProposedOffAngle = 0;
constexpr uint8_t kProposedOnAngle = 180;
constexpr uint8_t kInputBudget = 16;

Servo switchSignal;
int8_t selectedPin = -1;
bool armed = false;
bool running = false;
uint32_t startedAt = 0;
uint16_t runDuration = 0;
char inputLine[40];
uint8_t inputLength = 0;
bool badLine = false;

void proposedOff() {
  running = false;
  armed = false;
  if (selectedPin >= 0) switchSignal.write(kProposedOffAngle);
}

void rejectCommand() {
  proposedOff();
  Serial.println(F("ERROR rejected; armed=0; physical_OFF=unverified"));
}

void serviceDeadline() {
  if (running && static_cast<uint32_t>(millis() - startedAt) >= runDuration) {
    proposedOff();
    Serial.println(F("DONE proposed_OFF_sent; rearm_required=1"));
  }
}

bool parseNumber(const char *token, uint16_t &value) {
  if (!token || !*token) return false;
  uint32_t parsed = 0;
  for (const char *p = token; *p; ++p) {
    if (*p < '0' || *p > '9') return false;
    parsed = parsed * 10 + static_cast<uint8_t>(*p - '0');
    if (parsed > 65535UL) return false;
  }
  value = static_cast<uint16_t>(parsed);
  return true;
}

bool validPin(uint16_t pin) {
  return pin == kPump1Pin || pin == kPump2Pin || pin == kValve1Pin;
}

void printStatus() {
  Serial.println(F("BED_BENCH_TEST 2026-11-13 candidate1"));
  Serial.print(F("pin=")); Serial.print(selectedPin);
  Serial.print(F(" armed=")); Serial.print(armed);
  Serial.print(F(" running=")); Serial.println(running);
  Serial.println(F("protocol=servo; proposed_OFF=0; proposed_ON=180"));
  Serial.println(F("endpoints_us=544,2400; switch_identity_and_OFF=unverified"));
}

void processLine() {
  if (badLine) { rejectCommand(); return; }
  inputLine[inputLength] = '\0';
  char *context = nullptr;
  char *name = strtok_r(inputLine, " \t", &context);
  if (!name) return;
  char *argument = strtok_r(nullptr, " \t", &context);
  char *extra = strtok_r(nullptr, " \t", &context);
  if (extra) { rejectCommand(); return; }

  if (!strcmp(name, "ARM")) {
    uint16_t pin = 0;
    if (running || !parseNumber(argument, pin) || !validPin(pin) ||
        (selectedPin >= 0 && selectedPin != static_cast<int8_t>(pin))) {
      rejectCommand(); return;
    }
    if (selectedPin < 0) {
      // Servo 1.3.0 preserves preloaded ticks on attach. Global Servo's min/max
      // start at zero, matching the default endpoints used here. Avoid its
      // default 1500 us pulse on the first attach.
      switchSignal.write(kProposedOffAngle);
      if (switchSignal.attach(pin) == INVALID_SERVO) {
        pinMode(pin, INPUT);
        rejectCommand(); return;
      }
      selectedPin = static_cast<int8_t>(pin);
    }
    switchSignal.write(kProposedOffAngle);
    armed = true;
    Serial.println(F("ARMED proposed_OFF_sent; hardware_observation_required=1"));
  } else if (!strcmp(name, "RUN")) {
    uint16_t duration = 0;
    if (!armed || running || !parseNumber(argument, duration) ||
        duration < kMinRunMs || duration > kMaxRunMs) {
      rejectCommand(); return;
    }
    runDuration = duration;
    startedAt = static_cast<uint32_t>(millis());
    armed = false;
    running = true;
    switchSignal.write(kProposedOnAngle);
    Serial.println(F("RUNNING one_channel_only=1"));
  } else if (!argument && !strcmp(name, "STOP")) {
    proposedOff();
    Serial.println(F("STOP proposed_OFF_sent; armed=0"));
  } else if (!argument && !strcmp(name, "DISABLE")) {
    proposedOff();
    if (selectedPin >= 0) {
      switchSignal.detach();
      pinMode(selectedPin, INPUT);
      digitalWrite(selectedPin, LOW);  // input pull-up disabled
      selectedPin = -1;
    }
    Serial.println(F("DISABLED no_signal_is_not_verified_OFF"));
  } else if (!argument && !strcmp(name, "STATUS")) {
    printStatus();
  } else if (!argument && !strcmp(name, "HELP")) {
    Serial.println(F("ARM 3|5|6; RUN 100..500; STOP or !; DISABLE; STATUS"));
  } else {
    rejectCommand();
  }
}

void setup() {
  pinMode(kPump1Pin, INPUT);
  pinMode(kPump2Pin, INPUT);
  pinMode(kValve1Pin, INPUT);
  Serial.begin(115200);
  printStatus();
}

void loop() {
  serviceDeadline();
  uint8_t remaining = kInputBudget;
  while (remaining-- && Serial.available()) {
    const char c = static_cast<char>(Serial.read());
    if (c == '!') {
      proposedOff();
      inputLength = 0;
      badLine = true;  // discard the rest of this command until newline
      Serial.println(F("STOP proposed_OFF_sent; armed=0"));
    } else if (c == '\n' || c == '\r') {
      if (inputLength || badLine) processLine();
      inputLength = 0;
      badLine = false;
    } else if ((c >= 32 && c <= 126) || c == '\t') {
      if (!badLine && inputLength < sizeof(inputLine) - 1) {
        inputLine[inputLength++] = c;
      } else {
        badLine = true;
      }
    } else {
      badLine = true;
    }
    serviceDeadline();
  }
}
