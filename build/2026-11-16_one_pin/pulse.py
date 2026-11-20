#!/usr/bin/env python3
"""Agent helper: send one-pin pulse to OnePinTest firmware."""
import argparse
import sys
import time

import serial


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("pin", type=int, help="Arduino pin, e.g. 2")
    p.add_argument("--sec", type=float, default=3.0, help="ON time seconds (max 8)")
    p.add_argument("--port", default="/dev/cu.usbmodem1101")
    p.add_argument("--baud", type=int, default=9600)
    args = p.parse_args()

    ser = serial.Serial(args.port, args.baud, timeout=1)
    time.sleep(2.2)  # UNO auto-reset on open
    ser.reset_input_buffer()
    # drain boot banner
    deadline = time.time() + 1.5
    boot = b""
    while time.time() < deadline:
        chunk = ser.read(256)
        if chunk:
            boot += chunk
        else:
            time.sleep(0.05)
    if boot:
        sys.stdout.write(boot.decode("utf-8", errors="replace"))

    cmd = f"{args.pin} {args.sec}\n"
    ser.write(cmd.encode("ascii"))
    ser.flush()

    # wait for ON + OFF lines; allow ON time + margin
    wait_s = max(args.sec, 0.2) + 2.5
    deadline = time.time() + wait_s
    buf = b""
    while time.time() < deadline:
        chunk = ser.read(256)
        if chunk:
            buf += chunk
            text = buf.decode("utf-8", errors="replace")
            if "OFF D" in text:
                break
        else:
            time.sleep(0.05)

    ser.close()
    sys.stdout.write(buf.decode("utf-8", errors="replace"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
