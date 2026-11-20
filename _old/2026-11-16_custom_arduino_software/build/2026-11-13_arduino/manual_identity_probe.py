"""Operator-reset STK500 identity listener; no flash/EEPROM/fuse/GPIO writes."""
import argparse
import json
import time
from pathlib import Path
import serial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', required=True)
    parser.add_argument('--seconds', type=int, default=120)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.seconds <= 180:
        parser.error('window must be 1..180 seconds')
    result = {'port': args.port, 'mode': 'manual_reset_readonly',
              'window_seconds': args.seconds, 'valid_signature': False,
              'sync_count': 0, 'observations': [], 'memory_writes': False}
    connection = serial.Serial(port=None, baudrate=115200, timeout=0.025,
                               write_timeout=0.5, exclusive=True)
    connection.dtr = False
    connection.rts = False
    connection.port = args.port
    began = time.monotonic()
    try:
        connection.open()
        print('MANUAL_LISTENER_READY: hold lower RESET for one second, then release', flush=True)
        while time.monotonic() - began < args.seconds:
            for baud in (115200, 57600):
                connection.baudrate = baud
                connection.reset_input_buffer()
                connection.write(b'\x30\x20')  # GET_SYNC only
                connection.flush()
                reply = connection.read(2)
                if reply != b'\x14\x10':
                    continue
                result['sync_count'] += 1
                connection.timeout = 0.08
                connection.write(b'\x75\x20')  # READ_SIGN only
                connection.flush()
                frame = connection.read(5)
                observation = {'elapsed_s': round(time.monotonic() - began, 3),
                               'baud': baud, 'read_sign_hex': frame.hex()}
                signature = None
                if len(frame) == 5 and frame[0] == 0x14 and frame[-1] == 0x10:
                    signature = frame[1:4]
                else:
                    values = []
                    for index in range(3):
                        # UNIVERSAL whitelist: read each signature byte, never a write.
                        connection.write(bytes((0x56, 0x30, 0, index, 0, 0x20)))
                        connection.flush()
                        values.append(connection.read(3))
                    observation['universal_hex'] = [x.hex() for x in values]
                    if all(len(x) == 3 and x[0] == 0x14 and x[-1] == 0x10 for x in values):
                        signature = bytes(x[1] for x in values)
                if len(result['observations']) < 20:
                    result['observations'].append(observation)
                connection.timeout = 0.025
                if signature and signature not in (b'\x00\x00\x00', b'\xff\xff\xff'):
                    result.update(valid_signature=True, signature=signature.hex(), baud=baud)
                    print(json.dumps(result), flush=True)
                    return 0
    except (OSError, serial.SerialException) as error:
        result['error'] = str(error)
    finally:
        if connection.is_open:
            connection.close()
        result['elapsed_s'] = round(time.monotonic() - began, 3)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
