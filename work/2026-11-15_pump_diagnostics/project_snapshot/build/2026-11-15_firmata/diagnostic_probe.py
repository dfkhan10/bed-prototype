"""Host for DiagnosticFirmata. Default: status only; --pulse is explicit.

Requires the operator's physical setup/cutoff to be established before --pulse.
The resulting log is from the UNO pad sampler, never from the inline driver.
"""
import argparse
import datetime as dt
import json
import time
from pathlib import Path

import serial
from serial.tools import list_ports

ROOT = Path(__file__).resolve().parents[2]
TZ = dt.timezone(dt.timedelta(hours=8))
EXPECTED = "24238313635351910130"


def decode(frame):
    if len(frame) < 7 or frame[:2] != bytes((0xF0, 0x0E)) or frame[-1] != 0xF7:
        raise ValueError("Invalid diagnostic frame")
    payload = frame[6:-1]
    if len(payload) % 5 or frame[2] != 1 or any(b > 127 for b in frame[2:-1]):
        raise ValueError("Invalid diagnostic payload/version")
    values = [sum(b << (7*i) for i, b in enumerate(payload[j:j+5])) for j in range(0, len(payload), 5)]
    return {"op": frame[3], "phase": frame[4], "error": frame[5], "values": values}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--pulse", action="store_true", help="one device-timed candidate ON=180 for 500ms on B1/D3")
    action.add_argument("--capture", action="store_true", help="250ms passive D3 capture; no output change")
    action.add_argument("--pulse-seconds", type=int, choices=(10,), help="explicit 10-second host-timed D3 experiment with pad captures; no on-device 10s cutoff")
    parser.add_argument("--servo-range", choices=("seller", "rc"), default="seller", help="seller=544/2400us; rc=1000/2000us compatibility hypothesis, not driver identification")
    args = parser.parse_args()
    if args.servo_range != "seller" and not args.pulse_seconds:
        parser.error("--servo-range rc requires --pulse-seconds 10")
    now = dt.datetime.now(TZ)
    output = ROOT / ".arduino/evidence/hardware" / now.strftime("%Y-%m-%d_DiagnosticFirmata_%H%M%S.json")
    report = {"time": now.isoformat(), "board_serial": EXPECTED, "events": [], "responses": [],
              "proof_scope": "MCU pad digital levels; not driver acknowledgement or motor operation",
              "requested_action": "host_timed_10s_pulse" if args.pulse_seconds else "pulse" if args.pulse else "capture" if args.capture else "status",
              "physical_start": "unverified", "physical_stop": "unverified"}
    frames, pending = [], bytearray()
    ser = None
    pulse_attempted = False

    def receive(seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            raw = ser.read(ser.in_waiting or 1)
            if raw:
                report["events"].append({"event": "rx", "hex": raw.hex(), "t": time.monotonic()})
            for b in raw:
                if b == 0xF0:
                    pending.clear()
                    pending.append(b)
                elif pending:
                    pending.append(b)
                    if b == 0xF7:
                        frames.append(bytes(pending))
                        pending.clear()

    def send(data):
        report["events"].append({"event": "tx", "hex": data.hex(), "t": time.monotonic()})
        if ser.write(data) != len(data):
            raise RuntimeError("Short write")

    try:
        ports = [p for p in list_ports.comports() if (p.vid, p.pid, p.serial_number) == (0x2341, 0x0043, EXPECTED)]
        if len(ports) != 1:
            raise RuntimeError("Expected exactly one identified UNO")
        report["port"] = ports[0].device
        ser = serial.Serial(ports[0].device, 57600, timeout=0.015, write_timeout=0.5, exclusive=True)
        receive(6)
        index = len(frames)
        send(bytes.fromhex("f079f7"))
        receive(0.5)
        firmware = next((f for f in frames[index:] if f[1] == 0x79), None)
        if firmware is None or len(firmware) < 5:
            raise RuntimeError("Missing firmware identity")
        name = "".join(chr(firmware[i] | (firmware[i+1] << 7)) for i in range(4, len(firmware)-1, 2))
        report["firmware"] = name
        if name != "DiagnosticFirmata.ino" or firmware[2:4] != bytes((2, 5)):
            raise RuntimeError("Expected DiagnosticFirmata.ino 2.5; no experiment sent")
        if args.pulse_seconds:
            report["duration_owner"] = "host; no on-device 10-second cutoff"
            def pin_state(pin):
                first = len(frames)
                send(bytes((0xF0, 0x6D, pin, 0xF7)))
                receive(0.12)
                f = next((f for f in frames[first:] if len(f) >= 6 and f[1:3] == bytes((0x6E, pin))), None)
                if f is None:
                    raise RuntimeError("Missing pin-state response")
                return {"pin": pin, "mode": f[3], "stored_value": sum(b << (7*i) for i,b in enumerate(f[4:-1]))}

            baseline = [pin_state(p) for p in (3,4,5,6,7,8,10,11,12)]
            report["baseline"] = baseline
            if any(s["mode"] != 1 or s["stored_value"] != 0 for s in baseline):
                raise RuntimeError("Expected untouched OUTPUT/stored-0 baseline")
            captures = []
            def capture(label):
                first = len(frames)
                send(bytes.fromhex("f00e42440101f7"))
                receive(0.36)
                found = [decode(f) for f in frames[first:] if f[1] == 0x0E]
                if len(found) != 1 or found[0]["op"] != 1 or found[0]["error"] or len(found[0]["values"]) != 6:
                    raise RuntimeError("Invalid or missing pad capture")
                names = ("count", "min_high_us", "max_high_us", "min_period_us", "max_period_us", "max_sampling_gap_us")
                captures.append({"label": label, **dict(zip(names, found[0]["values"]))})
                report["captures"] = captures

            # Same stock configuration used before. Attach can briefly emit its
            # default 1500us before the immediately following candidate OFF.
            report["initial_attach"] = "possible default 1500us transient, as with stock Firmata"
            minimum, maximum = (1000, 2000) if args.servo_range == "rc" else (544, 2400)
            report["servo_endpoints_us"] = [minimum, maximum]
            report["range_basis"] = "Unverified RC-range compatibility hypothesis" if args.servo_range == "rc" else "Seller-example mapping"
            pulse_attempted = True  # cleanup also covers partial configuration
            configuration = bytes((0xF0, 0x70, 3, minimum & 127, minimum >> 7, maximum & 127, maximum >> 7, 0xF7, 0xE3, 0, 0))
            send(configuration)
            receive(0.25)
            capture("candidate_OFF_before")
            t0 = time.monotonic()
            try:
                send(bytes.fromhex("e33401"))
                for offset in (0, 2, 4, 6, 8):
                    while time.monotonic() < t0 + offset:
                        receive(min(0.03, t0 + offset - time.monotonic()))
                    capture("candidate_ON_at_" + str(offset) + "s")
                while time.monotonic() < t0 + 10:
                    receive(min(0.015, t0 + 10 - time.monotonic()))
            finally:
                send(bytes.fromhex("e30000"))
                report["host_on_interval_ms"] = round((time.monotonic()-t0)*1000, 2)
            receive(0.12)
            capture("candidate_OFF_after")
            report["after_state"] = pin_state(3)
            report["result"] = "PAD_CAPTURES_RECEIVED"
            print(json.dumps({"captures": captures, "host_on_interval_ms": report["host_on_interval_ms"]}))
            return
        op = 2 if args.pulse else 1 if args.capture else 0
        packet = bytes((0xF0, 0x0E, 66, 68, 1, op)) + (bytes((3, 42)) if args.pulse else b"") + bytes((0xF7,))
        index = len(frames)
        pulse_attempted = args.pulse
        send(packet)
        receive(2)
        responses = [decode(f) for f in frames[index:] if f[1] == 0x0E]
        report["responses"] = responses
        expected_phases = [0, 1, 2] if args.pulse else [0]
        if [r["phase"] for r in responses] != expected_phases or any(r["error"] or r["op"] != op for r in responses):
            raise RuntimeError("Missing or rejected diagnostic response")
        if op == 0 and len(responses[0]["values"]) != 7:
            raise RuntimeError("Malformed status response")
        if op in (1, 2):
            if any(len(r["values"]) != 6 for r in responses):
                raise RuntimeError("Malformed capture response")
            names = ("count", "min_high_us", "max_high_us", "min_period_us", "max_period_us", "max_sampling_gap_us")
            report["captures"] = [{"phase": r["phase"], **dict(zip(names, r["values"]))} for r in responses]
        report["result"] = "RESPONSES_RECEIVED"
    except BaseException as exc:
        report["result"] = "FAIL"
        report["error"] = repr(exc)
        raise
    finally:
        if ser is not None:
            if pulse_attempted:
                try:
                    send(bytes.fromhex("e30000"))
                except Exception as exc:
                    report["fallback_off_error"] = repr(exc)
            ser.close()
        report["serial_closed"] = True
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"result": report.get("result"), "log": str(output), "responses": report["responses"]}))


if __name__ == "__main__":
    main()
