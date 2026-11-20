#include <Arduino.h>
#line 1 "/Users/ivanyalov/Desktop/bed-prototype/build/2026-11-16_vendor_3zu/qiuqiu3zu/qiuqiu3zu.ino"
#include <Servo.h>
// Vendor qiuqiu4zu, first three groups only. Group 4 (D11/D12/D13) omitted.
// 180 = ON, 0 = OFF. Auto 3 cycles in setup(), then stop. No serial commands.
Servo servo_2;
Servo servo_3;
Servo servo_4;
Servo servo_5;
Servo servo_6;
Servo servo_7;
Servo servo_8;
Servo servo_9;
Servo servo_10;
// Group 1: D2 inflate, D3 valve, D4 deflate
// Group 2: D5 inflate, D6 valve, D7 deflate
// Group 3: D8 inflate, D9 valve, D10 deflate

#line 17 "/Users/ivanyalov/Desktop/bed-prototype/build/2026-11-16_vendor_3zu/qiuqiu3zu/qiuqiu3zu.ino"
void setup();
#line 73 "/Users/ivanyalov/Desktop/bed-prototype/build/2026-11-16_vendor_3zu/qiuqiu3zu/qiuqiu3zu.ino"
void loop();
#line 17 "/Users/ivanyalov/Desktop/bed-prototype/build/2026-11-16_vendor_3zu/qiuqiu3zu/qiuqiu3zu.ino"
void setup() {
  servo_2.attach(2);
  servo_3.attach(3);
  servo_4.attach(4);

  servo_5.attach(5);
  servo_6.attach(6);
  servo_7.attach(7);

  servo_8.attach(8);
  servo_9.attach(9);
  servo_10.attach(10);

  for (int index = 0; index < 3; index++) {
    servo_2.write(180);
    servo_3.write(180);
    servo_4.write(0);

    servo_5.write(180);
    servo_6.write(180);
    servo_7.write(0);

    servo_8.write(180);
    servo_9.write(180);
    servo_10.write(0);

    delay(8000);

    servo_2.write(0);
    servo_3.write(0);
    servo_4.write(180);

    servo_5.write(0);
    servo_6.write(0);
    servo_7.write(180);

    servo_8.write(0);
    servo_9.write(0);
    servo_10.write(180);

    delay(8000);

    servo_2.write(0);
    servo_3.write(0);
    servo_4.write(0);

    servo_5.write(0);
    servo_6.write(0);
    servo_7.write(0);

    servo_8.write(0);
    servo_9.write(0);
    servo_10.write(0);
  }
}

void loop() {
}

