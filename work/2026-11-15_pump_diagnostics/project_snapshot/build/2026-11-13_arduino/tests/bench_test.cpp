#define BED_HOST_TEST
#include <Arduino.h>
#include <Servo.h>
#include <cassert>
#include <iostream>
uint32_t fakeNow = 0;
int pinModes[20] = {};
FakeSerial Serial;
std::vector<int> attachAngles;
#include "../BedBenchTest/BedBenchTest.ino"
void send(const std::string &s) {
  for (unsigned char c : s) Serial.incoming.push_back(c);
  while (Serial.available()) loop();
}
void command(const std::string &s) { send(s + "\n"); }
int main() {
  setup();
  assert(selectedPin == -1 && !armed && !running && !switchSignal.active);
  assert(pinModes[3] == INPUT && pinModes[5] == INPUT && pinModes[6] == INPUT);
  command("RUN 100"); assert(!running && !switchSignal.active);
  command("ARM 4"); assert(!armed && !switchSignal.active);
  command("ARM 3");
  assert(armed && selectedPin == 3 && attachAngles.size() == 1 && attachAngles[0] == 0);
  command("RUN 99"); assert(!running && !armed);
  command("ARM 3"); command("RUN 250");
  assert(running && !armed && switchSignal.angle == 180);
  fakeNow = 249; loop(); assert(running);
  fakeNow = 250; loop(); assert(!running && !armed && switchSignal.angle == 0);
  command("RUN 250"); assert(!running);
  command("ARM 5"); assert(selectedPin == 3 && !armed);
  command("DISABLE"); assert(selectedPin == -1 && !switchSignal.active && pinModes[3] == INPUT);
  command("ARM 5"); fakeNow = UINT32_MAX - 15; command("RUN 100");
  fakeNow = 83; loop(); assert(running);
  fakeNow = 84; loop(); assert(!running && switchSignal.angle == 0);
  command("ARM 5"); command("RUN 500");
  command("RUN 500"); assert(!running && !armed && switchSignal.angle == 0);
  command("ARM 5"); command("RUN 500");
  fakeNow += 500;
  send(std::string(150, 'X')); assert(!running && switchSignal.angle == 0);
  send("\nARM 5\n"); assert(armed);
  command("RUN 100"); send("!"); assert(!running && !armed && switchSignal.angle == 0);
  send("\nDISABLE\n");
  send(std::string("ARM 3\0ignored\n", 14)); assert(!armed && selectedPin == -1);
  command("ARM 65536000000000000000000000000"); assert(!armed && selectedPin == -1);
  command("ARM -3"); command("ARM 3 extra"); assert(!armed);
  send("ARM 6\r\n"); assert(armed && selectedPin == 6);
  command("RUN 100"); command("STOP"); assert(!running && !armed && switchSignal.angle == 0);
  command("DISABLE"); assert(!switchSignal.active);
  std::cout << "PASS: boot inhibit, allowed pins, preload, range/parser rejection, one-shot arming, one channel, deadline, millis wrap, input flood, STOP and DISABLE\n";
}
