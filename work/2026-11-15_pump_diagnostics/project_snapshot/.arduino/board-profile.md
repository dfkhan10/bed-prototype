## Передача и пауза · 2026-11-15

Аппаратная диагностика приостановлена пользователем. Текущая прошивка остаётся
DiagnosticFirmata.ino 2.5. После её загрузки оператор подключил адаптер обратно;
выполнены два 10-секундных теста B1/D3. Последний диапазон 1000/2000мкс.
Все команды завершены, serial закрыт. Актуальные результаты и границы
доказательств: верхний раздел next-todo.md. Упоминания «адаптер отключён» ниже
описывают состояние во время загрузки, не текущее подтверждение питания.

## Current diagnostic firmware · 2026-11-15 17:46 HKT

DiagnosticFirmata.ino 2.5 is installed on the same UNO, superseding stock
StandardFirmata below. Firmata 2.5.9 plus private SysEx 0x0e; 57600 baud;
AVR core 1.8.8 and Servo 1.3.0. Verified upload and live status response.
No automatic diagnostic pulse. New host and proof boundaries: next-todo.md.
External adapter currently disconnected by operator; USB retained.
Rollback stock HEX retained. Driver model/return protocol still unidentified.

# Current board · 2026-11-15

Replacement board enumerates as Arduino UNO, FQBN arduino:avr:uno, VID 2341 / PID 0043, serial 24238313635351910130, /dev/cu.usbmodem1201. Valid STK500 chip signature 1e950f. This supports ATmega328P-compatible target communication; physical revision and manufacturing authenticity are not independently verified. USB-only with no shield or wiring was the replacement-board communication-test setup, not a claim about the present setup; see next-todo.md for later connections.

Arduino CLI 1.5.1, Arduino AVR Boards 1.8.8, avrdude 8.0-arduino.1, pyserial 3.5. BedUsbDiagnostics compiled (2932 B flash, 262 B static RAM), uploaded and flash-verified. Four serial request/reply checks at 115200 passed: HELP, INFO, MAC_TEST_1511 rejected as expected, STATUS. Startup text captured. Serial port closed after testing. No actuator testing performed.

Evidence: evidence/hardware/2026-11-15_new-uno-serial-roundtrip.json, 2026-11-15_new-uno-upload.log; evidence/build/2026-11-15_new-uno-build-report.json and uploaded HEX. Previous flash backup: evidence/hardware/2026-11-15_new-uno-flash-backup.hex. Restore only to this board through its bootloader if needed; backup includes the complete 32768-byte readable flash, not EEPROM or fuses.

## Current firmware update · 2026-11-15
StandardFirmata from upstream Firmata 2.5.9 is now installed on the same UNO
at Ivan's explicit request, replacing BedBenchTest and earlier diagnostics.
Project-local source is under `build/2026-11-15_firmata/libraries/Firmata/`.
Baud **57600**, protocol 2.5. Upload `--verify` passed; firmware name, capabilities,
analog mapping and selected pin-state queries passed. Allow 6 seconds after
port open/reset for standard startup/version blinking. Default digital outputs
are LOW; analog pins default to analog input; D13 blinks at boot. No pump command
sent. Evidence: `evidence/hardware/2026-11-15_StandardFirmata-query-check.json`;
full source/build identity: `evidence/build/2026-11-15_StandardFirmata-build.json`.
Earlier firmware descriptions above are historical. Next-todo records current setup.

## Inline driver research · 2026-11-15

Scope: identify the two pictured kits and their control interface. No device
communication, upload or actuator command was performed for this research.

- Full kit: inputs/2026-11-08_selected_kit_contents.jpg shows three inline
  electronic switches in black heatshrink, each between a three-pin control/
  power connector and a two-pin load connector. No manufacturer, SKU or chip
  marking is readable. Functional identification: servo-signal-controlled
  electronic load switch, supported by the pictured code, not an identified
  MOSFET/MCU model or verified current rating.
- Qing Yu Dian Zi self-assembly kit: the user's second screenshot shows two
  pumps, one valve and three similar inline switches; the selected variant is
  “With Electronic Switch Kit[Self Assembly]”. Exact switch identity and
  electrical/protocol equivalence to the full kit are not established.
- Correction: the full-kit screenshot reads **DFRobot_Servo.h**, not the
  previously recorded NRRobot_Servo.h. Searching the latter was based on a
  transcription error. This correction supersedes historical comments in the
  retained firmware sources; no firmware source or uploaded image was changed.
- Seller example attaches Servo objects at D8, D9 and D10, and alternates pump 1
  at 180/pump 2 at 0/valve at 0 with pump 1 at 0/pump 2 at 180/valve at 180.
  Captions identify 180 as working and 0 as stopped for the shown kit. These
  are seller instructions, not a physical result on Ivan's parts.

The official DFRobot_MAX AVR implementation maps `angle(0)` to a nominal
544 us pulse and `angle(180)` to 2400 us, with a 20000 us refresh interval
(about 50 Hz). The exact library version used in the seller screenshot is
unknown. The inspected official implementation supports these candidate
endpoints; it does not establish the driver's complete accepted range.

Installed Arduino Servo 1.3.0 was inspected at
`/Users/ivanyalov/Documents/Arduino/libraries/Servo/src/Servo.h` and
`src/avr/Servo.cpp`: its default endpoints, refresh interval and AVR angle
mapping agree. Thus `write(0)` / `write(180)` or explicit
`writeMicroseconds(544)` / `writeMicroseconds(2400)` reproduce the intended
commands for the full-kit test without installing another library. Do not
substitute `digitalWrite` or `analogWrite` for this timed servo signal.

Power/control interpretation: orange signal to the selected S row (current
bench assignment D3), red supply to + and brown ground to minus, matching the
previous operator map. The load takes power through the inline switch, not
from GPIO. The full-kit supply is advertised as 5 V / 5 A; this is not a
per-switch rating. Shield rail routing, USB isolation, switch current and
flyback protection remain unverified. No exact high-side/low-side topology is
inferred from the cable photograph.

First physical acceptance still needs observed start and stop on one unloaded
pump, a resolved power path and operator-accessible power removal. Startup,
reset and signal-loss behavior are unknown. The libraries initialize a default
1500 us setpoint; careless attach-before-OFF may therefore emit an intermediate
command. Existing BedBenchTest preloads the proposed OFF command before attach.
No claim is made that reset/high impedance or a transmitted OFF guarantees
physical shutdown. No device-identification exchange is present in the
inspected servo library; this does not exclude an undocumented module protocol.

Primary source, checked 2026-11-15, DFRobot_MAX library-path commit
`188017577d1fce4c3312e74d4b6203e563c7d570`:
- [DFRobot_Servo.h: pulse constants and API](https://github.com/DFRobot/DFRobot_MAX/blob/188017577d1fce4c3312e74d4b6203e563c7d570/DFRobot_Servo/DFRobot_Servo.h)
- [DFRobot_Servo.cpp: attach, angle mapping and output](https://github.com/DFRobot/DFRobot_MAX/blob/188017577d1fce4c3312e74d4b6203e563c7d570/DFRobot_Servo/DFRobot_Servo.cpp)

## Previous board history, retained for reference

# Board and peripheral intake · 2026-11-13

```yaml
resolution_status: needs-disambiguation
board_id: arduino-uno-r3
profile: references/boards/arduino-uno-r3.md
identity:
  profile_type: exact-board
  variant: photographed UNO SMD clone; exact MCU marking unreadable
  revision: unknown
required_disambiguators: [valid_mcu_signature_or_readable_marking, shield_power_routing, driver_behavior]
framework_core: Arduino AVR Boards 1.8.8
physical_status: USB enumeration verified; MCU identity and output behavior unverified
```

Current operator-reported setup: bare lower Uno on USB only, upper board removed, all pumps and valve disconnected, 5 V adapter disconnected. User reports board power LED on and LED blink when pressing RESET. Tested original cable, an SSD data cable, original Mac port and another direct Mac port.

Latest serial path: /dev/cu.usbserial-110, VID 0x1A86 / PID 0x7523; USB product USB Serial. Driver AppleUSBCHCOM, bundle com.apple.DriverKit-AppleUSBCHCOM, is loaded. Previous path on original Mac port was /dev/cu.usbserial-10. These identify USB transport only, not the main MCU.

Host tools verified: macOS 26.6.2 arm64; Arduino CLI 1.5.1; Arduino AVR Boards 1.8.8; Servo 1.3.0; project .venv pyserial 3.5; Apple clang 21.0.0. No dependency or global driver has been installed in this chat.

Uno R3 is a reference build target only. BedUsbDiagnostics compiles: 2932 B program / 262 B static RAM. BedBenchTest candidate compiles: 4854 B program / 315 B static RAM. Host tests pass for its actual command/state implementation. Build proof and hashes: evidence/build/2026-11-13_build-report.json. No upload has been attempted because a valid target signature has not been obtained.

Device evidence: read-only STK500 queries and avrdude -n with versions 8.0-arduino.1 and 6.3 fail at 115200 and 57600. A partial sync/version response at 57600 is insufficient to establish the MCU identity or working bootloader. Removing shield, manual RESET, SSD cable and second Mac port have not yielded a valid chip signature. Raw avrdude logs are under evidence/hardware/. No flash, EEPROM, fuse, erase or actuator command was sent.

Connected subset user map: D3 pump 1; D5 pump 2; D6 valve 1. Full project: six pumps and four valves, planned as two pump banks plus four valve channels. Photo confirms header labels S / + / -; orange/red/brown leads appear aligned respectively. Exact board rail routing and current capacity are unverified.

Adapter label supplied by user: 5 V DC, up to 5 A, centre-positive. Upper jack is a working hypothesis for the matched kit, not measured circuit proof. Simultaneous external power and USB has not been qualified. Keep external adapter disconnected during USB diagnostics.

Seller source inputs/2026-11-08_selected_kit_contents.jpg shows DFRobot_Servo.h (corrected from the earlier misreading NRRobot_Servo.h), Servo objects, and .angle(abs(0)) / .angle(abs(180)); pump-on/stop captions support 0=OFF / 180=ON for the pictured kit. See the 2026-11-15 research above for the now-inspected library mapping. Actual ON/OFF, startup and loss-of-signal behavior must still be observed on one isolated load before expanding.

Recovery: original board firmware remains unchanged; no backup can yet be read through the nonresponding bootloader. Do not force a chip signature or burn a bootloader as an automatic fix. A vendor driver compatibility test is being investigated; global activation requires a separate user decision. No networking or credentials are used by this bench firmware.

Sources: project docs/TUBE_ROUTING.md and docs/HARDWARE_DIMENSIONS.md; work/2026-11-08_hardware_shopping_list.md; user photographs and current operator replies; https://support.arduino.cc/hc/en-us/articles/4401874331410--Error-avrdude-when-uploading ; https://github.com/WCHSoftGroup/ch34xser_macos .

## Vendor driver candidate inspected

Official WCH CH34xVCPDriver 2.1/build 7, native arm64 + x86_64. Deep/strict signature verifies, notarized Developer ID accepted by Gatekeeper, publisher Nanjing Qinheng Microelectronics Co., Ltd., Team ID 5JZGQTGU4W. Package inspected read-only and unmounted; no app installation/execution or driver activation. See evidence/build/2026-11-13_vendor-driver-assessment.json and next-todo.md. Runtime compatibility remains unverified.

## WCH activated and bound; controller still unverified

User approved WCH, systemextensionsctl reports activated enabled, and IORegistry confirms CH34xVCPDriver owns /dev/cu.wchusbserial110 after USB reconnect. User reattached both boards, both LEDs on. Read-only ID probes at 115200/57600 and signature burst return no valid MCU identity. A read-only TIOCMGET succeeds, so WCH issue 50's driver-2.0 ENOTTY result is not reproduced on installed app 2.1; physical reset operation remains unmeasured. Next gate: bare lower Uno and a coordinated manual reset. No upload, flash/EEPROM/fuse write, erase or actuator command has occurred.

## Shield fitted · 2026-11-15

Operator reports shield connected and fits perfectly. Repeat USB test passed 3/3 request/reply checks with the same device serial and firmware. Evidence: evidence/hardware/2026-11-15_shield-serial-roundtrip.json. Does not validate shield rail routing, connector continuity, driver protocol or load-current capability. No actuator commands sent.

## Retained operator shield photograph · 2026-11-15

Operator supplied this same upper-shield photograph previously and again on
2026-11-15. Retained at `../inputs/2026-11-15_upper-shield_reference.png`. Reuse it; do not request this
same overview again. It shows the shield signal/power header labels and SW1.
The headers are unoccupied in this photograph; it does not establish the
current connected arrangement. The inline electronic switches and their chip
markings are outside the frame. Exact inline-switch model remains unidentified;
servo-signal behavior is a seller-example hypothesis, not physical acceptance.
