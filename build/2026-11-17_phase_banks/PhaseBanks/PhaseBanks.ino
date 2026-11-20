#include <Servo.h>
// Phase banks, 2026-11-17. Shield stays beside the UNO, not stacked.
// Signal and GND only between boards. Do not tie shield 5V to UNO 5V.
// On power/Reset every channel is OFF. This sketch does not run a cycle.

// Phase 1, inflate: D2 D3 D4 pumps, D6 D7 valves.
// Phase 2, deflate: D8 D10 D11 pumps, D12 valve, D9 valve when it arrives.
// D5 and D13 are unused.

static const uint8_t INFLATE_PINS[] = {2, 3, 4, 6, 7};
static const uint8_t DEFLATE_PINS[] = {8, 10, 11, 12, 9};
static const uint8_t PHASE_COUNT = 5;

Servo inflateServo[PHASE_COUNT];
Servo deflateServo[PHASE_COUNT];

static void drive(Servo *bank, uint8_t angle) {
  for (uint8_t i = 0; i < PHASE_COUNT; i++) {
    bank[i].write(angle);
  }
}

static void allOff() {
  drive(inflateServo, 0);
  drive(deflateServo, 0);
  delay(50);
  drive(inflateServo, 0);
  drive(deflateServo, 0);
}

void setup() {
  for (uint8_t i = 0; i < PHASE_COUNT; i++) {
    inflateServo[i].attach(INFLATE_PINS[i]);
    deflateServo[i].attach(DEFLATE_PINS[i]);
  }
  allOff();
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
}
