"""Query-only StandardFirmata audit. Opening UNO serial may reset the board.

No servo configuration, pin-mode changes, output writes, or reporting changes.
Pin-state replies are firmware bookkeeping, never driver acknowledgements.
"""
import datetime as dt
import hashlib
import json
import time
from pathlib import Path

import serial
from serial.tools import list_ports

ROOT = Path(__file__).resolve().parents[2]
TZ = dt.timezone(dt.timedelta(hours=8))
EXPECTED_SERIAL = "24238313635351910130"
PINS = (3, 4, 5, 6, 7, 8, 10, 11, 12)


def run():
    now = dt.datetime.now(TZ)
    output = ROOT / ".arduino/evidence/hardware" / (now.strftime("%Y-%m-%d_query-only-audit_%H%M%S") + ".json")
    report = {"time": now.isoformat(), "board_serial": EXPECTED_SERIAL,
              "proof_scope": "UNO serial and firmware state only; not driver feedback",
              "baud": 57600, "actuator_commands_sent": False,
              "serial_open_may_reset": True, "events": [], "checks": []}
    ser = None
    pending = bytearray()
    frames = []

    def record(event, **fields):
        report["events"].append({"t": round(time.monotonic(), 6), "event": event, **fields})

    def receive(seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            data = ser.read(ser.in_waiting or 1)
            if data:
                record("rx", hex=data.hex())
            for b in data:
                if b == 0xF0:
                    pending.clear()
                    pending.append(b)
                elif pending:
                    pending.append(b)
                    if b == 0xF7:
                        frames.append(bytes(pending))
                        pending.clear()

    def query(packet, response_command):
        allowed = {bytes.fromhex("f079f7"), bytes.fromhex("f06bf7"), bytes.fromhex("f069f7")}
        allowed.update(bytes((0xF0, 0x6D, pin, 0xF7)) for pin in PINS)
        if packet not in allowed:
            raise ValueError("Packet outside query-only allowlist")
        start = len(frames)
        t0 = time.monotonic()
        record("tx_query", hex=packet.hex())
        if ser.write(packet) != len(packet):
            raise RuntimeError("Short write")
        while time.monotonic() - t0 < 1.5:
            receive(0.015)
            for frame in frames[start:]:
                if frame[1] == response_command and (response_command != 0x6E or frame[2] == packet[2]):
                    report["checks"].append({"query": packet.hex(), "response": frame.hex(), "latency_ms": round((time.monotonic()-t0)*1000, 2)})
                    return frame
        raise RuntimeError("Query timeout: " + packet.hex())

    try:
        ports = [p for p in list_ports.comports() if (p.vid, p.pid, p.serial_number) == (0x2341, 0x0043, EXPECTED_SERIAL)]
        if len(ports) != 1:
            raise RuntimeError("Expected exactly one identified UNO")
        report["port"] = ports[0].device
        ser = serial.Serial(ports[0].device, 57600, timeout=0.015, write_timeout=0.5, exclusive=True)
        receive(6)
        fw = query(bytes.fromhex("f079f7"), 0x79)
        name = "".join(chr(fw[i] | (fw[i+1] << 7)) for i in range(4, len(fw)-1, 2))
        report["firmware"] = {"name": name, "version": list(fw[2:4])}
        if name != "StandardFirmata.ino" or fw[2:4] != bytes((2, 5)):
            raise RuntimeError("Unexpected firmware")
        caps = query(bytes.fromhex("f06bf7"), 0x6C)
        capabilities = []
        current = {}
        payload = caps[2:-1]
        i = 0
        while i < len(payload):
            if payload[i] == 127:
                capabilities.append(current)
                current = {}
                i += 1
            else:
                current[payload[i]] = payload[i+1]
                i += 2
        report["capabilities"] = capabilities
        report["analog_mapping"] = list(query(bytes.fromhex("f069f7"), 0x6A)[2:-1])
        samples = []
        baseline_frame_count = len(frames)
        for cycle in range(4):
            states = []
            for pin in PINS:
                f = query(bytes((0xF0, 0x6D, pin, 0xF7)), 0x6E)
                states.append({"pin": pin, "mode": f[3], "stored_value": sum(b << (7*i) for i, b in enumerate(f[4:-1]))})
            samples.append({"cycle": cycle, "states": states})
            receive(3)
        report["samples"] = samples
        unsolicited = [f.hex() for f in frames[baseline_frame_count:] if f[1] not in (0x6E,)]
        report["unexpected_sysex_after_baseline"] = unsolicited
        report["servo_capability_all_actuators"] = all(4 in capabilities[p] for p in PINS)
        report["result"] = "PASS"
    except BaseException as exc:
        report["result"] = "FAIL"
        report["error"] = repr(exc)
        raise
    finally:
        if ser is not None:
            ser.close()
        report["serial_closed"] = True
        report["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"result": report.get("result"), "path": str(output), "queries": len(report["checks"]), "firmware": report.get("firmware"), "servo_capability_all_actuators": report.get("servo_capability_all_actuators"), "serial_closed": True}))


if __name__ == "__main__":
    run()
