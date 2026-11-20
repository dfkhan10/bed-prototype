#!/usr/bin/env python3
"""Execute unchanged repository sketches against host-only Arduino/Servo shims.

No USB/serial port is opened. No hardware upload or operation is performed.
Uses a C++17 host compiler; this is NOT an Arduino AVR compilation.
"""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CASES = {
    'vendor-auto': 'build/2026-11-16_vendor_3zu/qiuqiu3zu/qiuqiu3zu.ino',
    'phase-idle': 'build/2026-11-17_phase_banks/PhaseBanks/PhaseBanks.ino',
    'vendor-stop': 'build/2026-11-16_vendor_serial/VendorSerial6/VendorSerial6.ino',
    'pair-stop': 'build/2026-11-16_pair24_serial/Pair24Serial/Pair24Serial.ino',
}

def main():
    compiler = shutil.which('clang++') or shutil.which('g++')
    if not compiler:
        raise SystemExit('A C++17 host compiler is required.')
    results = []
    with tempfile.TemporaryDirectory(prefix='bed-control-flow-') as folder:
        for name, relative in CASES.items():
            binary = str(Path(folder) / name)
            subprocess.run([compiler, '-std=c++17', '-I', str(HERE / 'shims'),
                            '-DSKETCH="' + str(ROOT / relative) + '"',
                            str(HERE / 'control_flow.cpp'), '-o', binary], check=True)
            result = subprocess.run([binary, name], check=True, capture_output=True, text=True)
            results.append(json.loads(result.stdout))
    print(json.dumps({'scope': 'host control-flow reproduction; no hardware',
                      'cases_passed': len(results), 'results': results}, indent=2))

if __name__ == '__main__':
    main()
