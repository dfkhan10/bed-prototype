"""Generate a diagnostic candidate beside untouched upstream StandardFirmata."""
from pathlib import Path
import hashlib
import shutil

base = Path(__file__).resolve().parent
source = base / "libraries/Firmata/examples/StandardFirmata/StandardFirmata.ino"
text = source.read_text()
prototype = "void sysexCallback(byte, byte, byte*);"
switch = "  switch (command) {"
if text.count(prototype) != 1 or text.count(switch) != 1:
    raise SystemExit("Unexpected upstream layout; no candidate generated")
text = text.replace(prototype, prototype + '\n#include "BedDiagnostics.h"')
text = text.replace(switch, switch + "\n    case 0x0e:\n      bedDiagnostic(argc, argv);\n      break;")
target = base / "DiagnosticFirmata"
target.mkdir(exist_ok=True)
(target / "DiagnosticFirmata.ino").write_text(text)
shutil.copy2(base / "BedDiagnostics.h", target / "BedDiagnostics.h")
print("upstream_sha256=" + hashlib.sha256(source.read_bytes()).hexdigest())
print(target)
