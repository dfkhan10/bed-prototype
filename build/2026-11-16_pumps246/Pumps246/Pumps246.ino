/*
 * Pumps246 — three-pump bench test
 * --------------------------------
 * Pins: D2, D4, D6  |  ON 10 s  |  then hard OFF
 *
 * TOP / SHIELD CONNECTED (required for pumps to move):
 *   1. Upper shield on UNO (stacked) OR DuPont: D2,D4,D6 + common GND
 *   2. One 3-wire plug (S/+/-) in shield columns 2, 4, and 6
 *   3. Each pump on the 2-pin end of its cable (not into UNO pins)
 *   4. 5 V adapter in the shield barrel jack (USB alone is not enough)
 *   5. After adapter is in: press UNO Reset (USB already on does not
 *      restart the sketch when you only plug the adapter)
 *
 * Behavior:
 *   - On power/Reset: 3x LED blink (alive) -> all three ON 10 s -> hard OFF
 *   - Serial 9600: GO (repeat), OFF (hard stop), HELP
 *   - Mistakes / bad commands are printed on Serial
 *
 * Stop: Serial OFF, or pull shield adapter immediately.
 */

#include <Servo.h>

static const uint8_t PINS[] = {2, 4, 6};
static const uint8_t PIN_COUNT = sizeof(PINS) / sizeof(PINS[0]);
static const unsigned ON_MS = 10000;
static const uint8_t LED = LED_BUILTIN;  // D13 "L"

Servo servos[PIN_COUNT];
bool attached = false;
bool runBusy = false;

static int indexOfPin(int pin) {
  for (uint8_t i = 0; i < PIN_COUNT; i++) {
    if (PINS[i] == (uint8_t)pin) return (int)i;
  }
  return -1;
}

static void reportMistake(const __FlashStringHelper *msg) {
  Serial.print(F("MISTAKE: "));
  Serial.println(msg);
  // fast LED chatter = error visible without Serial
  for (uint8_t i = 0; i < 6; i++) {
    digitalWrite(LED, HIGH);
    delay(60);
    digitalWrite(LED, LOW);
    delay(60);
  }
}

static void hardOff() {
  if (attached) {
    for (uint8_t i = 0; i < PIN_COUNT; i++) {
      servos[i].write(0);
    }
    delay(50);
    for (uint8_t i = 0; i < PIN_COUNT; i++) {
      servos[i].write(0);
    }
    delay(50);
    for (uint8_t i = 0; i < PIN_COUNT; i++) {
      servos[i].detach();
    }
    attached = false;
  }
  for (uint8_t i = 0; i < PIN_COUNT; i++) {
    pinMode(PINS[i], OUTPUT);
    digitalWrite(PINS[i], LOW);
  }
  digitalWrite(LED, LOW);
}

static void ensureAttached() {
  if (attached) return;
  for (uint8_t i = 0; i < PIN_COUNT; i++) {
    servos[i].attach(PINS[i]);
    servos[i].write(0);
  }
  attached = true;
  delay(120);
}

static bool wiringSelfCheck() {
  // Software can only catch logic mistakes, not missing adapter/pumps.
  if (PIN_COUNT != 3) {
    reportMistake(F("internal PIN_COUNT != 3"));
    return false;
  }
  for (uint8_t i = 0; i < PIN_COUNT; i++) {
    if (indexOfPin(PINS[i]) < 0) {
      reportMistake(F("pin list corrupt"));
      return false;
    }
  }
  // Duplicate pin check
  if (PINS[0] == PINS[1] || PINS[0] == PINS[2] || PINS[1] == PINS[2]) {
    reportMistake(F("duplicate pins in PINS[]"));
    return false;
  }
  Serial.println(F("CHECK: pin list OK (2,4,6). Hardware still needs:"));
  Serial.println(F("  - shield top connected / DuPont D2 D4 D6 + GND"));
  Serial.println(F("  - plugs in columns 2,4,6 ; pumps on 2-pin ends"));
  Serial.println(F("  - 5V adapter in shield jack"));
  return true;
}

static void runTenSeconds() {
  if (runBusy) {
    reportMistake(F("run already in progress — ignored"));
    return;
  }
  runBusy = true;

  if (!wiringSelfCheck()) {
    hardOff();
    runBusy = false;
    return;
  }

  Serial.println(F("RUN: hard OFF first"));
  hardOff();
  delay(100);

  Serial.println(F("RUN: D2+D4+D6 ON for 10 s (LED on)"));
  ensureAttached();
  for (uint8_t i = 0; i < PIN_COUNT; i++) {
    servos[i].write(180);
  }
  digitalWrite(LED, HIGH);

  // Chunked wait so Serial OFF can abort mid-run
  unsigned left = ON_MS;
  while (left > 0) {
    unsigned step = left > 50 ? 50 : left;
    delay(step);
    left -= step;
    if (Serial.available()) {
      String line = Serial.readStringUntil('\n');
      line.trim();
      line.toUpperCase();
      if (line == "OFF" || line == "0" || line == "STOP") {
        Serial.println(F("ABORT: OFF received during run"));
        hardOff();
        runBusy = false;
        return;
      }
    }
  }

  Serial.println(F("RUN: hard OFF"));
  hardOff();
  Serial.println(F("RUN: done"));
  runBusy = false;
}

static void printHelp() {
  Serial.println(F("Pumps246 — D2 D4 D6, 10 s ON then OFF"));
  Serial.println(F("Commands: GO | OFF | HELP"));
  Serial.println(F("Auto-runs once after power/Reset."));
  Serial.println(F("If pumps silent but LED blinked: wiring/adapter/plugs."));
}

void setup() {
  pinMode(LED, OUTPUT);
  digitalWrite(LED, LOW);
  hardOff();

  Serial.begin(9600);
  delay(200);

  Serial.println();
  Serial.println(F("=== Pumps246 boot ==="));
  printHelp();

  // Alive: 3 short blinks (visible without Serial)
  for (uint8_t i = 0; i < 3; i++) {
    digitalWrite(LED, HIGH);
    delay(150);
    digitalWrite(LED, LOW);
    delay(150);
  }

  runTenSeconds();
}

void loop() {
  if (!Serial.available()) return;

  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;
  line.toUpperCase();

  if (line == "HELP" || line == "?") {
    printHelp();
    return;
  }
  if (line == "OFF" || line == "0" || line == "STOP") {
    hardOff();
    Serial.println(F("ALL OFF"));
    return;
  }
  if (line == "GO" || line == "START" || line == "RUN") {
    runTenSeconds();
    return;
  }

  Serial.print(F("MISTAKE: unknown command '"));
  Serial.print(line);
  Serial.println(F("'. Use GO / OFF / HELP"));
  reportMistake(F("unknown serial command"));
}
