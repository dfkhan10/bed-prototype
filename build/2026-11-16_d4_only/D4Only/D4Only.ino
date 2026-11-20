#include <Servo.h>
// Only D4 + onboard LED L (D13) as proof the sketch runs.
// Auto once on power/reset: OFF -> D4+L ON 3s -> hard OFF.
// If L blinks but pump silent: wiring/plug/pump on channel 4.
// If L never blinks after Reset: not this firmware or no UNO reset.

Servo servo_4;

static const unsigned PHASE_MS = 3000;
static const uint8_t LED = 13;

static void hardOff() {
  servo_4.write(0);
  delay(50);
  servo_4.write(0);
  delay(50);
  servo_4.detach();
  pinMode(4, OUTPUT);
  digitalWrite(4, LOW);
  digitalWrite(LED, LOW);
}

void setup() {
  pinMode(LED, OUTPUT);
  digitalWrite(LED, LOW);
  pinMode(4, OUTPUT);
  digitalWrite(4, LOW);

  // 3 short LED blinks = sketch started
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED, HIGH);
    delay(150);
    digitalWrite(LED, LOW);
    delay(150);
  }
  delay(300);

  servo_4.attach(4);
  servo_4.write(0);
  delay(150);

  digitalWrite(LED, HIGH);
  servo_4.write(180);
  delay(PHASE_MS);

  hardOff();
}

void loop() {
}
