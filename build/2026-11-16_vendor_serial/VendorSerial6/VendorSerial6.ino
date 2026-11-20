#include <Servo.h>
// Seller multi-group example (qiuqiu4zu): inflate / 3-way valve / deflate.
// Max 4 groups in original; we keep 3 groups for 6 pumps + valves.
// Board power note from seller: upper expansion needs independent 5V >10A supply;
// jumper on expansion must be removed or high current can backfeed the main board.
// Pin map (Ivan 2026-11-16): D8 unused; group 3 on D9/D10/D11; group 4 removed.
// Group 1: inflate D2, valve D3, deflate D4.
// Group 2: inflate D5, valve D6, deflate D7.
// Group 3: inflate D9, valve D10, deflate D11.
// Timing and 180/0 commands match the seller example.
// Change from seller: do NOT auto-run on power/reset. Wait for serial "GO".

Servo servo_2;
Servo servo_3;
Servo servo_4;
Servo servo_5;
Servo servo_6;
Servo servo_7;
Servo servo_9;
Servo servo_10;
Servo servo_11;

static void allOff() {
  servo_2.write(0);
  servo_3.write(0);
  servo_4.write(0);
  servo_5.write(0);
  servo_6.write(0);
  servo_7.write(0);
  servo_9.write(0);
  servo_10.write(0);
  servo_11.write(0);
}

static void runSellerCycles() {
  for (int index = 0; index < 3; index++) {
    // Inflate + valves ON, deflate OFF — 8 s (seller)
    servo_2.write(180);
    servo_3.write(180);
    servo_4.write(0);

    servo_5.write(180);
    servo_6.write(180);
    servo_7.write(0);

    servo_9.write(180);
    servo_10.write(180);
    servo_11.write(0);

    delay(8000);

    // Inflate OFF, valves OFF, deflate ON — 8 s (seller)
    servo_2.write(0);
    servo_3.write(0);
    servo_4.write(180);

    servo_5.write(0);
    servo_6.write(0);
    servo_7.write(180);

    servo_9.write(0);
    servo_10.write(0);
    servo_11.write(180);

    delay(8000);

    // All OFF (seller end of cycle)
    allOff();
  }
}

void setup() {
  Serial.begin(9600);

  servo_2.attach(2);
  servo_3.attach(3);
  servo_4.attach(4);
  servo_5.attach(5);
  servo_6.attach(6);
  servo_7.attach(7);
  servo_9.attach(9);
  servo_10.attach(10);
  servo_11.attach(11);

  allOff();
  Serial.println(F("VendorSerial6 ready. Type GO then Enter to run 3x(8s inflate + 8s deflate)."));
}

void loop() {
  if (!Serial.available()) {
    return;
  }

  String line = Serial.readStringUntil('\n');
  line.trim();
  line.toUpperCase();

  if (line == "GO" || line == "START") {
    Serial.println(F("RUN begin"));
    runSellerCycles();
    allOff();
    Serial.println(F("RUN done; all OFF. Send GO again to repeat."));
  } else if (line.length() > 0) {
    Serial.println(F("Unknown. Send GO"));
  }
}
