#include <Servo.h>
// One pin at a time. No auto-run. Seller-style Servo 180=ON, 0=OFF.
// Allowed signal pins (3 groups): 2,3,4,5,6,7,9,10,11
// Serial 9600. Examples:
//   2       -> D2 ON 3s, then OFF
//   5 5     -> D5 ON 5s, then OFF
//   OFF     -> all OFF now
//   HELP

static const uint8_t PINS[] = {2, 3, 4, 5, 6, 7, 9, 10, 11};
static const uint8_t PIN_COUNT = sizeof(PINS) / sizeof(PINS[0]);
static const unsigned DEFAULT_MS = 3000;
static const unsigned MAX_MS = 8000;

Servo servos[PIN_COUNT];

static int indexOfPin(uint8_t pin) {
  for (uint8_t i = 0; i < PIN_COUNT; i++) {
    if (PINS[i] == pin) return i;
  }
  return -1;
}

static void allOff() {
  for (uint8_t i = 0; i < PIN_COUNT; i++) {
    servos[i].write(0);
  }
}

static void pulseOne(uint8_t pin, unsigned ms) {
  int idx = indexOfPin(pin);
  if (idx < 0) {
    Serial.println(F("BAD pin. Use 2,3,4,5,6,7,9,10,11"));
    return;
  }
  if (ms < 200) ms = 200;
  if (ms > MAX_MS) ms = MAX_MS;

  allOff();
  Serial.print(F("ON D"));
  Serial.print(pin);
  Serial.print(F(" "));
  Serial.print(ms);
  Serial.println(F(" ms"));
  servos[idx].write(180);
  delay(ms);
  servos[idx].write(0);
  Serial.print(F("OFF D"));
  Serial.println(pin);
}

static void printHelp() {
  Serial.println(F("OnePinTest: one channel. Commands:"));
  Serial.println(F("  <pin>       ON 3s then OFF  e.g. 2"));
  Serial.println(F("  <pin> <sec> ON N s then OFF e.g. 5 5  (max 8s)"));
  Serial.println(F("  OFF"));
  Serial.println(F("Map: G1 D2/D3/D4  G2 D5/D6/D7  G3 D9/D10/D11"));
}

void setup() {
  Serial.begin(9600);
  for (uint8_t i = 0; i < PIN_COUNT; i++) {
    servos[i].attach(PINS[i]);
  }
  allOff();
  Serial.println(F("OnePinTest ready. Connect ONE pump, then send pin number."));
  printHelp();
}

void loop() {
  if (!Serial.available()) return;

  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;

  String upper = line;
  upper.toUpperCase();
  if (upper == "HELP" || upper == "?") {
    printHelp();
    return;
  }
  if (upper == "OFF" || upper == "0") {
    allOff();
    Serial.println(F("ALL OFF"));
    return;
  }

  int pin = 0;
  float sec = 0;
  int n = sscanf(line.c_str(), "%d %f", &pin, &sec);
  if (n < 1) {
    Serial.println(F("Parse fail. HELP"));
    return;
  }
  unsigned ms = DEFAULT_MS;
  if (n >= 2 && sec > 0) {
    ms = (unsigned)(sec * 1000.0f + 0.5f);
  }
  pulseOne((uint8_t)pin, ms);
}
