"""One explicitly requested B1/D3 Firmata pulse; no firmware changes."""
import datetime
import json
import os
import select
import sys
import threading
import time
from pathlib import Path

import serial
from serial.tools import list_ports

ROOT = Path(__file__).resolve().parents[2]
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%H%M%S')
log_path = ROOT / '.arduino/evidence/hardware' / f'2026-11-15_B1-D3-bounded-test_{stamp}.jsonl'
log_file = log_path.open('x', buffering=1)


def record(event, **data):
    entry = dict(time=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(), event=event, **data)
    line = json.dumps(entry)
    log_file.write(line + '\n')
    print(line, flush=True)


ser = None
frames = []
pending = bytearray()
preflight_done = threading.Event()


def preflight_watchdog():
    if not preflight_done.wait(18):
        record('preflight_timeout', seconds=18, actuator_commands_sent=False)
        os._exit(2)


def receive(seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        readable, _, _ = select.select([ser.fileno()], [], [], min(0.05, max(0, deadline - time.monotonic())))
        if not readable:
            continue
        data = os.read(ser.fileno(), 4096)
        if not data:
            raise RuntimeError('USB EOF')
        record('rx', hex=data.hex())
        for value in data:
            if value == 0xF0:
                pending.clear()
                pending.append(value)
            elif pending:
                pending.append(value)
                if value == 0xF7:
                    frames.append(bytes(pending))
                    pending.clear()


def send(data, event):
    count = ser.write(data)
    record(event, hex=data.hex(), written=count)
    if count != len(data):
        raise RuntimeError('Short USB write')


def query(data, predicate):
    start = len(frames)
    send(data, 'query')
    deadline = time.monotonic() + 1.2
    while time.monotonic() < deadline:
        receive(0.05)
        matches = [frame for frame in frames[start:] if predicate(frame)]
        if matches:
            return matches[-1]
    raise RuntimeError('No matching Firmata response')


def state(pin):
    response = query(bytes([0xF0, 0x6D, pin, 0xF7]), lambda f: len(f) >= 6 and f[:3] == bytes([0xF0, 0x6E, pin]))
    value = sum(part << (7 * i) for i, part in enumerate(response[4:-1]))
    return dict(pin=pin, mode=response[3], stored_value=value)


configured = False
on_attempted = False
try:
    targets = [p for p in list_ports.comports() if p.vid == 0x2341 and p.pid == 0x0043 and p.serial_number == '24238313635351910130']
    if len(targets) != 1:
        raise RuntimeError('Expected exactly one known UNO')
    record('start', port=targets[0].device, board_serial=targets[0].serial_number, baud=57600, requested_on_ms=10000, target='B1/D3', log=str(log_path), physical_observation='pending operator', initial_attach='StandardFirmata Servo attach may briefly emit its default 1500 us pulse')
    threading.Thread(target=preflight_watchdog, daemon=True).start()
    record('serial_open_start')
    ser = serial.Serial(targets[0].device, 57600, timeout=0.05, write_timeout=0.5, exclusive=True)
    record('serial_open_complete')
    receive(6)
    firmware = query(bytes.fromhex('f079f7'), lambda f: len(f) > 5 and f[:2] == bytes.fromhex('f079'))
    name = ''.join(chr(firmware[i] | (firmware[i + 1] << 7)) for i in range(4, len(firmware) - 1, 2))
    if name != 'StandardFirmata.ino' or firmware[2:4] != bytes([2, 5]):
        raise RuntimeError(f'Unexpected firmware {name!r}')
    record('firmware_verified', name=name, major=firmware[2], minor=firmware[3])
    states = [state(pin) for pin in (3, 4, 5, 6, 7, 8, 10, 11, 12)]
    record('baseline', states=states)
    if any(s['stored_value'] != 0 or s['mode'] not in (1, 4) for s in states):
        raise RuntimeError('Unexpected baseline; no pulse')
    preflight_done.set()
    if '--pulse' not in sys.argv:
        record('query_only_complete')
    else:
        configured = True
        send(bytes.fromhex('f0700320046012f7e30000'), 'configure_D3_servo_and_candidate_OFF')
        receive(0.25)
        if state(3) != dict(pin=3, mode=4, stored_value=0):
            raise RuntimeError('Candidate OFF not reflected by firmware')
        record('pulse_starting_now', target='B1/D3', seconds=10)
        on_attempted = True
        t0 = time.monotonic()
        try:
            send(bytes.fromhex('e33401'), 'candidate_ON')
            deadline = t0 + 10
            # Query while ON, not only after our own OFF command. Keep the
            # 1.2-second query deadline clear of the scheduled OFF deadline.
            for sample_at in (0, 1, 3, 5, 7):
                while time.monotonic() < t0 + sample_at:
                    receive(min(0.05, t0 + sample_at - time.monotonic()))
                active = state(3)
                record('during_pulse', elapsed_ms=round((time.monotonic() - t0) * 1000, 2), state=active)
                if active != dict(pin=3, mode=4, stored_value=180):
                    raise RuntimeError('D3 lost ON state during pulse; possible reset or command failure')
            while time.monotonic() < deadline:
                receive(min(0.02, max(0, deadline - time.monotonic())))
        finally:
            send(bytes.fromhex('e30000'), 'candidate_OFF')
        record('pulse_commands_complete', host_interval_ms=round((time.monotonic() - t0) * 1000, 2), physical_start='unverified', physical_stop='unverified')
        after = state(3)
        record('after_pulse', state=after)
        if after != dict(pin=3, mode=4, stored_value=0):
            raise RuntimeError('Firmware did not report candidate OFF; remove physical power')
        record('holding_port', seconds=120, message='No further ON commands; waiting for operator observation')
        end = time.monotonic() + 120
        while time.monotonic() < end:
            time.sleep(0.2)
except BaseException as exc:
    record('error', message=repr(exc), on_attempted=on_attempted, action='Remove adapter and USB if pump continues')
    raise
finally:
    preflight_done.set()
    if ser is not None:
        if configured:
            try:
                send(bytes.fromhex('e30000'), 'final_candidate_OFF')
            except BaseException as exc:
                record('final_OFF_failed', message=repr(exc))
        ser.close()
        record('serial_closed')
