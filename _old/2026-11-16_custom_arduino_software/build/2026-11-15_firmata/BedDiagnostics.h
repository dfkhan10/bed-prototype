// Diagnostic extension for UNO/ATmega328P, AVR 1.8.8, Servo 1.3.0.
// Reads the physical MCU pad through PIND; NOT feedback from the driver.
// Private SysEx 0x0e; request: 'B','D',1,op. Pulse adds pin=3,key=42.
// op0=status, op1=passive 250ms capture, op2=one bounded D3 experiment.
// No custom action at startup. No physical-OFF guarantee is implied.
#if !defined(__AVR_ATmega328P__)
#error "BedDiagnostics is restricted to the ATmega328P UNO reference target"
#endif

void attachServo(byte pin, int minPulse, int maxPulse);

struct BedPulseStats {
  uint32_t count, minHigh, maxHigh, minPeriod, maxPeriod, maxGap;
};

static bool bedProbeUsed = false;

static void bedU32(uint32_t value) {
  for (byte i = 0; i < 5; ++i) {
    Firmata.write(static_cast<byte>(value & 0x7f));
    value >>= 7;
  }
}

static void bedBegin(byte op, byte phase, byte error) {
  Firmata.write(START_SYSEX);
  Firmata.write(static_cast<byte>(0x0e));
  Firmata.write(static_cast<byte>(1));
  Firmata.write(op);
  Firmata.write(phase);
  Firmata.write(error);
}

static BedPulseStats bedCapture(uint32_t durationUs) {
  BedPulseStats s = {0, 0xffffffffUL, 0, 0xffffffffUL, 0, 0};
  const uint32_t start = micros();
  uint32_t lastSample = start, rise = 0, previousRise = 0;
  bool hadRise = false, hadPreviousRise = false;
  byte previous = (PIND >> PD3) & 1;
  while (true) {
    const uint32_t now = micros();
    if (static_cast<uint32_t>(now - start) >= durationUs) break;
    const byte level = (PIND >> PD3) & 1;
    const uint32_t gap = now - lastSample;
    if (gap > s.maxGap) s.maxGap = gap;
    lastSample = now;
    if (level != previous) {
      if (level) {
        if (hadPreviousRise) {
          const uint32_t period = now - previousRise;
          if (period < s.minPeriod) s.minPeriod = period;
          if (period > s.maxPeriod) s.maxPeriod = period;
        }
        rise = previousRise = now;
        hadRise = hadPreviousRise = true;
      } else if (hadRise) {
        const uint32_t high = now - rise;
        if (high < s.minHigh) s.minHigh = high;
        if (high > s.maxHigh) s.maxHigh = high;
        ++s.count;
        hadRise = false;
      }
      previous = level;
    }
  }
  if (s.minHigh == 0xffffffffUL) s.minHigh = 0;
  if (s.minPeriod == 0xffffffffUL) s.minPeriod = 0;
  return s;
}

static void bedSendStats(byte op, byte phase, const BedPulseStats &s) {
  bedBegin(op, phase, 0);
  bedU32(s.count); bedU32(s.minHigh); bedU32(s.maxHigh);
  bedU32(s.minPeriod); bedU32(s.maxPeriod); bedU32(s.maxGap);
  Firmata.write(END_SYSEX);
}

static void bedDiagnostic(byte argc, byte *argv) {
  if (argc < 4 || argv[0] != 'B' || argv[1] != 'D' || argv[2] != 1) return;
  const byte op = argv[3];
  if (op == 0 && argc == 4) {
    bedBegin(op, 0, 0);
    bedU32(PIND); bedU32(DDRD); bedU32(PORTD);
    bedU32(TIMSK1); bedU32(TCCR1A); bedU32(TCCR1B);
    bedU32(bedProbeUsed ? 1 : 0);
    Firmata.write(END_SYSEX);
    return;
  }
  if (op == 1 && argc == 4) {
    const BedPulseStats stats = bedCapture(250000UL);
    bedSendStats(op, 0, stats);
    return;
  }
  if (op != 2 || argc != 6 || argv[4] != 3 || argv[5] != 42) {
    bedBegin(op, 0, 1); Firmata.write(END_SYSEX); return;
  }
  // One experiment per boot, from an untouched Servo configuration.
  if (bedProbeUsed || servoCount || detachedServoCount) {
    bedBegin(op, 0, 2); Firmata.write(END_SYSEX); return;
  }
  const byte pins[] = {3, 4, 5, 6, 7, 8, 10, 11, 12};
  for (byte i = 0; i < sizeof(pins); ++i) {
    if (Firmata.getPinMode(pins[i]) != OUTPUT || Firmata.getPinState(pins[i]) != 0) {
      bedBegin(op, 0, 3); Firmata.write(END_SYSEX); return;
    }
  }
  bedProbeUsed = true;
  // All global Servo objects have default endpoint offsets at this point.
  // Preload 544us before attach to avoid an initial default 1500us command.
  servos[0].writeMicroseconds(544);
  attachServo(3, 544, 2400);
  setPinModeCallback(3, PIN_MODE_SERVO);
  const byte index = servoPinMap[3];
  if (index >= MAX_SERVOS || !servos[index].attached()) {
    bedBegin(op, 0, 4); Firmata.write(END_SYSEX); return;
  }
  servos[index].write(0);
  Firmata.setPinState(3, 0);
  const BedPulseStats offBefore = bedCapture(250000UL);
  servos[index].write(180);
  Firmata.setPinState(3, 180);
  const BedPulseStats on = bedCapture(500000UL);
  // Device-timed candidate OFF precedes any serial output from this test.
  servos[index].write(0);
  Firmata.setPinState(3, 0);
  const BedPulseStats offAfter = bedCapture(250000UL);
  bedSendStats(op, 0, offBefore);
  bedSendStats(op, 1, on);
  bedSendStats(op, 2, offAfter);
}
