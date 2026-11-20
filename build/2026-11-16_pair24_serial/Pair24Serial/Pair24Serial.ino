#include <Servo.h>
// D2 = inflate, D4 = deflate. No auto-run. Serial 9600.
//   GO  -> OFF, 3s inflate, OFF, 3s deflate, hard OFF
//   IN  -> 3s inflate only, hard OFF
//   OUT -> 3s deflate only, hard OFF
//   OFF -> hard OFF now
// hard OFF: Servo 0 twice, then detach + pin LOW (stops stuck PWM).

Servo servo_2;
Servo servo_4;
bool attached = false;

static const unsigned PHASE_MS = 3000;

static void hardOff() {
  if (attached) {
    servo_2.write(0);
    servo_4.write(0);
    delay(50);
    servo_2.write(0);
    servo_4.write(0);
    delay(50);
    servo_2.detach();
    servo_4.detach();
    attached = false;
  }
  pinMode(2, OUTPUT);
  pinMode(4, OUTPUT);
  digitalWrite(2, LOW);
  digitalWrite(4, LOW);
}

static void ensureAttached() {
  if (!attached) {
    servo_2.attach(2);
    servo_4.attach(4);
    attached = true;
    servo_2.write(0);
    servo_4.write(0);
    delay(100);
  }
}

static void inflateOn() {
  ensureAttached();
  servo_2.write(180);
  servo_4.write(0);
}

static void deflateOn() {
  ensureAttached();
  servo_2.write(0);
  servo_4.write(180);
}

void setup() {
  Serial.begin(9600);
  hardOff();
  Serial.println(F("Pair24Serial v2. D2=inflate D4=deflate. GO / IN / OUT / OFF"));
}

void loop() {
  if (!Serial.available()) return;

  String line = Serial.readStringUntil('\n');
  line.trim();
  line.toUpperCase();
  if (line.length() == 0) return;

  if (line == "OFF" || line == "0") {
    hardOff();
    Serial.println(F("ALL OFF"));
    return;
  }

  if (line == "IN") {
    Serial.println(F("INFLATE 3s"));
    hardOff();
    inflateOn();
    delay(PHASE_MS);
    hardOff();
    Serial.println(F("OFF"));
    return;
  }

  if (line == "OUT") {
    Serial.println(F("DEFLATE 3s"));
    hardOff();
    deflateOn();
    delay(PHASE_MS);
    hardOff();
    Serial.println(F("OFF"));
    return;
  }

  if (line == "GO" || line == "START") {
    Serial.println(F("GO start OFF"));
    hardOff();
    Serial.println(F("GO inflate 3s"));
    inflateOn();
    delay(PHASE_MS);
    hardOff();
    Serial.println(F("GO mid OFF"));
    delay(200);
    Serial.println(F("GO deflate 3s"));
    deflateOn();
    delay(PHASE_MS);
    hardOff();
    Serial.println(F("GO done OFF"));
    return;
  }

  Serial.println(F("Unknown. Use GO IN OUT OFF"));
}
