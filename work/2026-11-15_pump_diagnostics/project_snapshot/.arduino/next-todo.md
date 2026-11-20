# Диагностика приостановлена; передача · 2026-11-15

Иван приостановил аппаратную цель и поручил собрать описание, софт и все логи.
Новых тестов не запускать. Последние завершённые тесты:

- `evidence/hardware/2026-11-15_DiagnosticFirmata_174934.json`: D3/B1,
  10 секунд, диапазон 544/2400 мкс; реальные PIND-записи подтверждают импульсы
  2376–2428 мкс при команде ON. Иван явно сообщил: «Нет, никакой реакции».
- `evidence/hardware/2026-11-15_DiagnosticFirmata_175110.json`: тот же D3/B1,
  10 секунд, изменён только диапазон на 1000/2000 мкс. При ON измерено
  1980–2028 мкс, после OFF 984–1024 мкс. Отдельного однозначного ответа о
  физической реакции именно на этот тест нет; общий результат по словам
  Ивана: ничего не получается. Успешный запуск/остановка не подтверждены.
- Предложение попробовать «б4» не выполнялось; такого установленного
  обозначения в карте нет. D4 в карте означает A1. Не угадывать канал.
- Текущая прошивка: DiagnosticFirmata.ino 2.5, загружена с проверкой 17:45 HKT.
  Внешний адаптер был затем подключён пользователем обратно для тестов.
  Последнее известное состояние не является свежим измерением питания.
- Последний скрипт отправил candidate OFF=0, прочитал D3 servo/stored=0 и
  закрыл serial. При подготовке передачи активных диагностических процессов
  не найдено; порт заново не открывался.

Обратный лог от самого драйвера/насоса не получен; интерфейс обратной связи не
идентифицирован. Ответы Firmata и измерения PIND сформированы UNO. Модель
inline-драйвера, питание/общий провод на его входе, сигнал на его разъёме и
напряжение на моторе остаются непроверенными.

Передача: `../work/2026-11-15_pump_diagnostics/`.
После возобновления выбрать проверку питания/входа/выхода одного драйвера,
либо сначала установить его точную модель. Повторение неизменной команды не
заменит измерение. Все прежние записи ниже исторические, в том числе строки
«in progress», ожидание фото и упоминания 500мс как следующего теста.

# Live D3 waveform result · 2026-11-15 17:50 HKT

Operator reconnected external adapter and confirmed readiness. At operator's
request performed a **10-second host-timed** D3 experiment, not the custom
500ms on-device request. No new firmware was needed. Actual PIND captures on
real UNO measured ON pulses 2376–2428us, period 19980–20028us, in five windows
at 0/2/4/6/8 seconds. Before/after candidate OFF measured 528–568us. Maximum
sampling gap 36us; this is a digital MCU-pad sample, not analog voltage or a
probe at the driver connector. Host interval 10009.33ms. Afterward stored D3
state servo/0. Serial closed. Operator reports **no physical pump response**.
Evidence: evidence/hardware/2026-11-15_DiagnosticFirmata_174934.json.

This narrows the failure beyond simple absence of MCU output pulses. Driver
input wiring, its power/ground, accepted pulse range/protocol, and driver/load
output remain unresolved. No return telemetry interface identified. Do not
represent the pad sampler as a driver log. User wants the pump working and
repeated stop warnings are not useful substitutes for diagnosis.

Next experiment now in progress: same D3 and 10-second duration, change only
the Servo endpoints to 1000/2000us. This is an unverified RC-range hypothesis
because the earlier 544/2400us mapping has not made B1 respond. Capture real
PIND before/during/after; obtain operator response before another experiment.

# Active diagnosis · 2026-11-15 17:46 HKT

This section supersedes the older firmware and repeated-photo next steps below.
Do not ask again for the retained upper-shield overview photo. Operator confirmed
external adapter disconnected, USB retained, for this diagnostic upload.

## Current firmware and results
- Same UNO serial 24238313635351910130, /dev/cu.usbmodem1201.
- **DiagnosticFirmata.ino 2.5**, Firmata 2.5.9 + local diagnostic SysEx 0x0e,
  AVR 1.8.8, Servo 1.3.0, 57600 baud. Uploaded with verification; live status
  replied. Source: build/2026-11-15_firmata/DiagnosticFirmata/.
- No custom diagnostic action or automatic pump pulse on boot. Stock Firmata
  startup LOW outputs/D13 blinking are retained; LOW is not proven physical OFF.
- Live stock audit passed 39/39 queries. Before changing firmware, read-only
  flash verification matched all 13184 bytes of retained StandardFirmata HEX.
- Offline execution of that exact HEX produced D3 544/2400us pulse trains,
  period about 20ms. This is simulation, not a connector measurement.
- Diagnostic build: 14620 bytes flash, 1136 bytes static RAM. Simulation passed
  normal waveform capture, forced PIND-low detection, wrong-key rejection,
  duplicate-run rejection and absence of an initial default 1500us pulse.
- First live diagnostic status: PIND=1, DDRD=252, PORTD=0, TIMSK1=0. D3's
  sampled pad logic was LOW, D3 was output, Servo timer interrupt not enabled.
  No new pump ON command has been sent in this diagnosis.

## Next action
Finish passive capture (no output change), then ask the operator to reconnect
the external adapter and be ready to remove it for one explicitly announced
B1/D3 diagnostic request. The keyed request has a 500ms device-timed candidate
ON, followed by candidate OFF. No all-channel test and no valve actuation.
Physical start/stop must be observed; a software timeout is not a power cutoff.
Do not run with adapter disconnected and assume USB cannot feed the load rail.

Host: `.venv/bin/python build/2026-11-15_firmata/diagnostic_probe.py` for status,
`--capture` for passive D3 capture, `--pulse` only for the prepared physical test.
The previous bench_pulse.py rejects DiagnosticFirmata by firmware name.
The custom log reads the actual MCU PIND buffer, not the PORT output latch or
Firmata stored value. It does NOT prove connector voltage, driver reception,
driver power, motor voltage or motion. No driver telemetry interface identified.
No arbitrary serial/I2C probing of the driver has been attempted.

Evidence:
- evidence/hardware/2026-11-15_query-only-audit_173639.json
- evidence/hardware/2026-11-15_Firmata-flash-verify_173736.json
- evidence/hardware/2026-11-15_DiagnosticFirmata-upload_174546.json
- evidence/hardware/2026-11-15_DiagnosticFirmata_174612.json
- evidence/build/2026-11-15_DiagnosticFirmata-build.json
- evidence/build/2026-11-15_Firmata-hex-waveform-simulation.json
- evidence/build/2026-11-15_DiagnosticFirmata-hex-waveform-simulation.json
- evidence/build/2026-11-15_DiagnosticFirmata-pad-low-fault-hex-waveform-simulation.json

Rollback: evidence/build/2026-11-15_StandardFirmata-uploaded.hex. Restore with
external adapter disconnected, verify upload, then query firmware identity.

# Earlier results (historical)

# Continue here · 2026-11-15

## Active-state diagnosis · 2026-11-15 17:22 HKT
Operator reports no response to the earlier 17:19 ten-second pulse; external
adapter power remains present and wiring unchanged. Do not ask for this again.
Inspected host encoding, StandardFirmata SERVO_CONFIG/analogWriteCallback and
linked Servo 1.3.0 source against saved seller example. No encoding discrepancy
found: D3, servo endpoints 544/2400 us, angle 180 ON and 0 candidate OFF.
Host script now queries D3 during ON instead of only after its own OFF.
Same-board/firmware repeat: ON 17:22:20.886; readbacks at 0.053, 1.060, 3.054,
5.054 and 7.059 seconds all mode=4/stored=180. OFF sent 17:22:30.889;
readback mode=4/stored=0. No observed startup frames or communication loss
during the pulse. Interval 10003.99 ms. This is firmware state, not measured
signal, power or motor feedback. Physical response to this diagnostic pulse
has not yet been reported. Firmware unchanged.
Evidence: `evidence/hardware/2026-11-15_B1-D3-bounded-test_172214.jsonl`.
Session 32446 holds the port for 120 seconds after OFF then closes without
further ON commands. Next: one clear top-down photo of upper shield showing
D3 S/+/- connector orientation, power jack/terminal and rail-selection jumpers,
plus connected B1 inline driver. Use it to resolve physical topology before
another command or a targeted voltage measurement. Existing local photographs
are seller listing images, not a current bench wiring photograph.

## Latest B1/D3 repeat · 2026-11-15 17:19 HKT
User explicitly requested repeat for 10 seconds, confirmed external adapter
power present and wiring unchanged. Same UNO serial and StandardFirmata.ino 2.5
verified. Only D3 configured; ON=180 at 17:19:11.762, OFF=0 at 17:19:21.761.
Host interval 10002.37 ms. Afterward D3 reported servo mode/stored 0.
Evidence: `evidence/hardware/2026-11-15_B1-D3-bounded-test_171904.jsonl`.
Physical response pending operator observation. Session 35624 holds port for
120 seconds after pulse then sends candidate OFF and closes; no repeat ON.
Next: operator reports whether B1 started and stopped. External power presence
is confirmed by operator; do not ask again absent a relevant change.

## Latest B1/D3 test · 2026-11-15 17:15 HKT
USB reconnected; same UNO serial 24238313635351910130 opened successfully.
StandardFirmata.ino 2.5 identity and all nine actuator baseline states queried.
D3 alone configured servo 544/2400 us; candidate ON=180 sent at 17:15:45.820,
candidate OFF=0 at 17:15:48.821, host interval 3001.45 ms.
Afterward Firmata reported D3 mode servo, stored value 0. Other channels unchanged.
Evidence: `evidence/hardware/2026-11-15_B1-D3-bounded-test_171538.jsonl`.
Operator reports no physical response: nothing happened during the three-second test.
B1 operation failed to demonstrate; inlet/outlet remain unidentified.
Serial session 68256 holds the port for 120 seconds after the pulse, then sends
candidate OFF again and closes; no automatic further ON commands.
Next action: establish whether the external 5 V adapter remained connected to
the upper shield and powered after USB reconnection. No further pulse yet.
Firmata stored value does not establish driver power or signal at the connector.
This result supersedes the earlier pending three-second USB attempts below.

## Requested outcome
1. Verify shield signal output and input.
2. Test one pump/driver at row labelled 3 (D3).
Exact driver models have not been identified. Full-kit seller code supports servo-signal switching; DFRobot library mapping was inspected on 2026-11-15 (see board-profile.md). Actual operation remains untested. Two pump types may have different drivers; qualify each pair separately.

## Verified now
Replacement UNO serial 24238313635351910130, VID:PID 2341:0043, ATmega328P signature 1e950f, port /dev/cu.usbmodem1201. Bare and unloaded-shield USB communication previously passed.

Shield D3 and D4 signal paths PASS: operator connected jumper S at row 3 to S at row 4, with all pump/driver and external power disconnected, USB only. TEST returned D3->D4 0/20 mismatches and D4->D3 0/20 mismatches. Previous no-jumper control returned expected 10/20 mismatches in each direction, so passing depends on the external jumper. This verifies the two tested shield/UNO signal paths for HIGH/LOW output and input; not every connector, power rail, analog accuracy or load capacity.
Evidence: evidence/hardware/2026-11-15_shield-loopback-open.json and 2026-11-15_shield-loopback-connected.json. Serial closed; D3/D4 returned to inputs without pullups.

## Current firmware · StandardFirmata installed 2026-11-15
At Ivan's explicit request, replaced BedBenchTest with the unmodified upstream
StandardFirmata sketch from Firmata library **2.5.9**, tag commit
`c285135275c4dd4f0d0bbf82da3c5844a29eaf07`.
Source: `build/2026-11-15_firmata/libraries/Firmata/examples/StandardFirmata/StandardFirmata.ino`.
Project-local library, Arduino AVR 1.8.8, Servo 1.3.0, UNO serial
24238313635351910130 at /dev/cu.usbmodem1201. Compile: 13184 B flash,
1125 B static RAM. Upload with `--verify` succeeded.

Read-only Firmata queries at **57600 baud** confirmed firmware
`StandardFirmata.ino` (reported major/minor 2.5), protocol 2.5, a 20-entry
pin capability map (D0/D1 reserved for serial), analog mapping A0–A5,
and reported D3/D4/D5/D6 mode OUTPUT with stored value LOW.
These values report firmware state, not measured voltages or physical pump OFF.
No servo configuration or actuator command sent. Serial is closed.
The old STATUS text protocol is no longer valid. The former STATUS polling
monitor was stopped before upload. After opening the port, allow **6 seconds**
for bootloader and standard version-blink startup before queries; shorter
initial waits missed the first response. Default startup blinks D13; digital
pins default to OUTPUT LOW and analog pins to analog input. Do not attach a
load assuming reset means no output signal.

Evidence:
- evidence/build/2026-11-15_StandardFirmata-build.json
- evidence/build/2026-11-15_StandardFirmata-uploaded.hex
- evidence/hardware/2026-11-15_StandardFirmata-upload.log
- evidence/hardware/2026-11-15_StandardFirmata-query-check.json
Rollback: evidence/build/2026-11-15_BedBenchTest-uploaded.hex retained.

## Current setup and next action
Latest operator wiring report (2026-11-15), superseding the unloaded photo:
six pump/driver assemblies connected in order B1, A1, A2, B2, A3, A4, starting
at the previously assigned D3. A1–A4 are four pumps of one kind; B1–B2 are two
of another. Thus the physical signal assignment is:

| Shield row | Pump | Proposed pneumatic role |
| --- | --- | --- |
| D3 | B1 | Inflation |
| D4 | A1 | Inflation |
| D5 | A2 | Inflation |
| D6 | B2 | Extraction |
| D7 | A3 | Extraction |
| D8 | A4 | Extraction |

Operator confirmed: D9 empty; three valve driver inputs at D10/D11/D12.
Do not use the old D9–D12 valve plan. Fourth valve reported different/problematic; attached photo
shows loose stripped wire ends, but does not establish its model, pinout,
voltage or pneumatic function. User will ask a friend for a matching valve.
Do not energize the loose-ended assembly or infer that its wiring is complete.
Three connected valves remain unidentified as to 2/2 vs 3/2 and normally-closed
function. User will obtain/adapt the fourth later; proceed with three for now.
Pump/valve start and physical stop remain untested.

## First B1/D3 powered command · 2026-11-15 16:56 HKT
At user's explicit "all connected, start" instruction, verified same UNO serial
and StandardFirmata identity; D3–D8 and D10–D12 reported OUTPUT/stored 0.
Configured only D3 as servo 544/2400 us, sent proposed OFF=0, ON=180 for a
computer-timed 505.49 ms interval, then proposed OFF=0. Query returned D3
mode=4 (servo), stored value=0. Other actuator channels were not configured.
Physical start, identity of moving pump and physical stop await operator report.
Do not equate the stored value with observed stop or repeat a pulse without
that report. Serial session 6731 is held open for up to 10 minutes following
command completion, preserving proposed OFF; no automatic further actuation.
Check its status before reuse. Operator was instructed to remove both adapter
and USB if a pump continues. StandardFirmata has no on-device timed stop.
Evidence: `evidence/hardware/2026-11-15_B1-D3-first-pulse_165650.jsonl`.
Next action: obtain observed start/stop result for B1 on D3.

Historical preparation before this first commanded pulse:
Latest requested next experiment: test pump/driver operation before plumbing.
Recommended first observation is one open-port B1 pump on D3: bounded candidate
ON command followed by candidate OFF, observe actual start, actual stop, and
identify inlet/outlet. No tubing, bladder or pressurized circuit in this first
trial. Do not start all six or energize valves as part of the first pulse.
Arduino CLI discovery in this turn found no UNO USB device (only debug-console
and Bluetooth ports). No serial port was opened and no output command sent.
Next physical action: reconnect UNO USB with external adapter off before
establishing present setup and operator-accessible power removal. StandardFirmata
has no configured on-device timed pump stop; a computer-timed pulse cannot be
represented as a guaranteed hardware duration/cutoff. Candidate servo 0/180
polarity remains unverified for each actual driver, including B1's kit variant.

Each pump bank now has two A pumps plus one B pump: symmetric composition,
not demonstrated equal pressure/suction performance. Do not combine multiple
motors on one driver without combined-current qualification.

Earlier user report was USB to UNO plus kit 5 V adapter to upper shield;
that was the monitored setup below, not fresh proof of the present power state
after rewiring. Photos show wiring on the bench, not verified supply routing or
USB isolation. No serial session or actuator command was started in response
to the latest wiring/photo report. Before a first powered pulse, establish the
present power state and readily accessible physical cutoff.

Firmata query-only monitoring started in this reported dual-power setup at
15:53 HKT. Startup identified StandardFirmata.ino/protocol 2.5; D3/D4/D5/D6
reported OUTPUT with stored value 0; the first firmware poll replied.
Opening serial can reset UNO, so the initial startup frames are not evidence
of supply-induced resets. Monitor is bounded to about 10 minutes and logs to
`evidence/hardware/2026-11-15_Firmata-dual-power-monitor_155333.jsonl`.
Do not claim ongoing monitoring without checking whether this bounded process
is still running. No pin mode, servo configuration or actuator command sent.

Next: use standard Firmata for subsequent computer control. No pump has yet
been observed running or stopping. Before a powered pump test, resolve the
shield's external-power routing and operator-accessible power cutoff.
The user also asked which barrel jack accepts the kit's 5 V adapter. UNO's
lower barrel input is specified for 7–12 V, not the 5 V adapter. Upper shield
jack remains the kit-input hypothesis; shield routing and USB isolation are
unverified. Do not infer them from Firmata replies.

## Historical standalone pump candidate (not selected)
`build/2026-11-15_pump/OnePumpPulse/OnePumpPulse.ino` was compiled only and
never uploaded. Its reset-triggered automatic pulse is NOT the current plan;
Ivan explicitly chose unmodified StandardFirmata. Do not upload this older
candidate or introduce automatic actuation on reset.

## Pump test preparation and uncertainties
Pump has two power wires and inline driver with orange signal / red supply / brown ground plug. No feedback output or readback protocol identified. Static input readings cannot identify driver or confirm pump running. A commanded start/stop must be observed by operator.

Seller image inputs/2026-11-08_selected_kit_contents.jpg reads DFRobot_Servo.h, not the previously misread NRRobot_Servo.h. The official DFRobot AVR implementation maps 0/180 to nominal 544/2400 us pulses, refreshed about every 20 ms. Installed Servo 1.3.0 uses the same mapping; the existing bench candidate can produce those commands without a new library. Seller captions support 0=stopped / 180=working for the pictured full kit; actual OFF/reset/signal-loss behavior and equivalence of the Qing Yu self-assembly kit remain unverified. See board-profile.md for sources. Adapter previously reported 5 V DC / 5 A / centre-positive; shield power routing, row supply under external power, USB backfeed and load capability remain unverified.

Historical BedBenchTest was uploaded and STATUS-verified before replacement by StandardFirmata; it has not actuated a pump. ARM proposes OFF=0, RUN 100..500 ms proposes ON=180 then OFF. Its 544/2400 us endpoints agree with the inspected official DFRobot AVR mapping; acceptance and physical ON/OFF on the connected switch remain unverified. No pump command or actuation has occurred. Keep external supply disconnected for uploads; do not power pump from USB or combine USB/external power until the power routing is resolved. Before first pump actuation, establish power path and use an operator-controlled power cutoff; observe actual stop, not just firmware timeout.
