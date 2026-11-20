"""Read-only STK500v1 sync/signature probe using a longer DTR/RTS reset.

The probe resets the MCU. It sends only synchronization, parameter and
signature reads; universal commands are limited to the three signature bytes.
It never writes flash, fuses, EEPROM or actuator GPIOs. Reset may restart
an installed sketch; USB power can also reach attached driver modules.
"""

import argparse
import json
import time

import serial


def probe(port: str, baud: int) -> dict:
    result = {"port": port, "baud": baud, "reset": "legacy_held_dtr_rts"}
    connection = serial.Serial(
        port=None, baudrate=baud, timeout=0.35, write_timeout=0.5, exclusive=True
    )
    connection.dtr = False
    connection.rts = False
    connection.port = port
    try:
        connection.open()
        time.sleep(0.25)
        connection.dtr = True
        connection.rts = True
        time.sleep(0.05)
        connection.reset_input_buffer()
        samples = []
        for _ in range(12):
            connection.write(b"\x30\x20")  # STK_GET_SYNC, CRC_EOP
            connection.flush()
            reply = connection.read(2)
            if reply == b"\x14\x10":  # STK_INSYNC, STK_OK
                result["synchronized"] = True
                parameters = {}
                for parameter in (0x80, 0x81, 0x82):
                    connection.write(bytes((0x41, parameter, 0x20)))
                    connection.flush()
                    parameters[hex(parameter)] = connection.read(3).hex()
                result["parameters"] = parameters
                connection.write(b"\x75\x20")  # STK_READ_SIGN, CRC_EOP
                connection.flush()
                signature = connection.read(5)
                result["signature_response"] = signature.hex()
                result["signature_valid_frame"] = (
                    len(signature) == 5
                    and signature[0] == 0x14
                    and signature[-1] == 0x10
                )
                if result["signature_valid_frame"]:
                    result["signature"] = signature[1:4].hex()
                else:
                    universal = []
                    for index in range(3):
                        # STK_UNIVERSAL: read signature only, never a write opcode.
                        connection.write(bytes((0x56, 0x30, 0, index, 0, 0x20)))
                        connection.flush()
                        universal.append(connection.read(3))
                    result["universal_signature_responses"] = [
                        value.hex() for value in universal
                    ]
                    if all(len(value) == 3 and value[0] == 0x14 and value[2] == 0x10
                           for value in universal):
                        result["signature"] = bytes(value[1] for value in universal).hex()
                        result["signature_valid_frame"] = True
                return result
            if reply:
                samples.append(reply.hex())
            time.sleep(0.03)
        result.update(synchronized=False, received_samples=samples)
        return result
    except (serial.SerialException, OSError) as error:
        result["error"] = str(error)
        return result
    finally:
        if connection.is_open:
            connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--baud", type=int, nargs="+", default=(115200, 57600))
    parser.add_argument("--manual-reset", action="store_true")
    args = parser.parse_args()
    if args.manual_reset:
        connection = serial.Serial(
            port=None, baudrate=args.baud[0], timeout=0.08,
            write_timeout=0.5, exclusive=True,
        )
        connection.dtr = False
        connection.rts = False
        connection.port = args.port
        with connection:
            print('MANUAL_RESET_WINDOW_OPEN 45 seconds; no GPIO or memory writes', flush=True)
            deadline = time.monotonic() + 45
            sync_count = 0
            while time.monotonic() < deadline:
                for baud in args.baud:
                    connection.baudrate = baud
                    connection.reset_input_buffer()
                    connection.write(b"\x30\x20")
                    connection.flush()
                    if connection.read(2) != b"\x14\x10":
                        continue
                    sync_count += 1
                    connection.write(b"\x75\x20")
                    connection.flush()
                    response = connection.read(5)
                    if len(response) == 5 and response[0] == 0x14 and response[-1] == 0x10:
                        print(json.dumps({"baud": baud, "signature": response[1:4].hex(),
                                          "reset": "manual", "signature_valid_frame": True}), flush=True)
                        return 0
            print(json.dumps({"manual_window_closed": True, "sync_frames": sync_count,
                              "signature_valid_frame": False}), flush=True)
            return 2
    for baud in args.baud:
        result = probe(args.port, baud)
        print(json.dumps(result), flush=True)
        if result.get("signature_valid_frame"):
            return 0
        if result.get("error"):
            return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
