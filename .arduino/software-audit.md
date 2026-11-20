# Arduino software audit · 2026-11-20

Reviewed source: `7630116562879dbebada50a44ec1ab27cf331c73` in
`dfkhan10/bed-prototype` (fork of `ivanyalov/bed-prototype`).

## Result

The repository contains useful component tests and an idle phase-bank sketch,
but not a complete two-group, four-valve demonstration controller. These are
software findings, not evidence of faulty pumps, valves, power or wiring.

| Finding | Evidence and consequence |
| --- | --- |
| Newest sketch is intentionally idle | `build/2026-11-17_phase_banks/PhaseBanks/PhaseBanks.ino` sends OFF commands in `setup()`; `loop()` is empty. It does not implement a cycle, a serial command interface, or simulated feedback. |
| Reset can start the old cycle automatically | `build/2026-11-16_vendor_3zu/qiuqiu3zu/qiuqiu3zu.ino` runs three 8 s inflate / 8 s deflate cycles inside `setup()`. It starts without GO, including after a reset. Opening a serial connection can reset some UNO configurations; no port was opened in this audit. |
| Old cycle and newer wiring map are incompatible | Under the 17 November map, the old sketch's first phase sets D2/D3 high and D4 low (two inflation pumps), and D8 low with D10/D11 high (two extraction pumps). It also opens both fill-valve pins D6/D7. Thus using that sketch with that newer map does not produce the intended group-specific behavior. This is conditional on actual wiring matching the newer notes; current physical routing is unverified. |
| Vendor serial version has no mid-cycle stop | `VendorSerial6` waits for GO, but then blocks in six `delay(8000)` calls. An OFF line queued at the beginning remains unread until the full 48 s cycle ends. OFF is not implemented as a recognized command even afterward. |
| Pair serial test cannot honor its advertised immediate OFF during a phase | `Pair24Serial` advertises OFF now, but `IN` and `OUT` block in `delay(3000)` and only return to parsing commands after the phase and OFF sequence. The host reproduction leaves OFF unread for 3,200 virtual ms from the beginning of the energized phase. |

Other inspected diagnostics are also not a production controller: `Pumps246`
auto-runs at reset and uses `readStringUntil`, which can block awaiting a
newline. Its comments calling signal removal "hard OFF" do not establish the
actual driver's behavior when pulses disappear.

## Reproduction

Run from the repository root:

```sh
python3 .arduino/tests/run_control_flow.py
```

Four assertions-based reproductions passed using the unchanged sketches and a
C++17 host compiler. The runner substitutes Arduino/Servo/serial shims and
advances a virtual clock instead of sleeping. Its output confirms:

- `vendor-auto`: reset/startup executes 48,000 virtual ms of automatic cycling;
  the first phase conflicts with the newer bank mapping.
- `phase-idle`: 1,000 calls to `loop()` issue no further commands and do not
  consume GO.
- `vendor-stop`: OFF remains unread during all 48,000 virtual ms of the run.
- `pair-stop`: OFF remains unread through the 3,200 virtual ms phase sequence.

These successful tests reproduce limitations; they do not certify working
hardware. They are not an AVR firmware build or an electrical simulation.
PWM timing, Servo startup transients, supply isolation, load current, tubing,
air pressure, motion and physical stop behavior are outside this harness.

Arduino CLI was not found on PATH and no USB serial device matching
`/dev/cu.usb*` or `/dev/cu.wch*` was visible during this audit. No upload,
serial-port opening or pump operation was performed. The currently flashed
firmware cannot be established from the source repository.

## Basis for the physical demo

Keep the existing hardware and implement a controller for two independently
selected groups, three shared fill pumps, three shared extraction pumps and
four valves. Confirm the actual pin/function map first; Ivan's latest message
lists three inflate/valve/deflate triples, while the repository's newer notes
list shared banks and four valves. Neither source proves current wiring.

The controller should:

- remain idle at reset, with explicit activation of the bench demo;
- use a nonblocking timed state machine so stop commands can be handled;
- keep fill and extraction valves of the same group mutually exclusive;
- bound each actuation and the overall attempt, then command all outputs OFF;
- accept explicitly labeled simulated readings and faults, with a separate
  future interface for physical sensors;
- record commands, input provenance and stop reasons without claiming actual
  pressure relief or achieved movement from synthetic readings.

A software STOP cannot replace a confirmed way to remove actuator power.
Without pressure/tilt sensors, this demo cannot provide real pressure or tilt
limits, verify unloading, or claim human-use safety. Checkerboard support also
does not by itself establish left/right repositioning. Before a physical test,
check current power isolation and wiring; the supplier material saved in the
repository specifically warns about simultaneous USB/external supply without
appropriate isolation.
