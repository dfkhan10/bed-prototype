#!/bin/zsh
# Fast-retry UNO upload aligned to a manual RESET release.
# Uses avrdude -x noautoreset so DTR does not steal the bootloader window,
# and -x attempts=1 so each miss returns in ~1s instead of ~45s.
set -eu

PORT="${1:-/dev/cu.usbmodem1101}"
HEX="${2:-/Users/ivanyalov/Desktop/bed-prototype/.cache/2026-11-16_pair24/Pair24Opp.ino.hex}"
LOG="${3:-/Users/ivanyalov/Desktop/bed-prototype/.arduino/evidence/hardware/2026-11-16_Pair24Opp-upload-waitreset.log}"
WINDOW_SEC="${WINDOW_SEC:-60}"
BAUD="${BAUD:-115200}"

AVRDUDE="/Users/ivanyalov/Library/Arduino15/packages/arduino/tools/avrdude/8.0.0-arduino1/bin/avrdude"
CONF="/Users/ivanyalov/Library/Arduino15/packages/arduino/tools/avrdude/8.0.0-arduino1/etc/avrdude.conf"

if [[ ! -c "$PORT" ]]; then
  echo "NO_PORT $PORT"
  exit 2
fi
if [[ ! -f "$HEX" ]]; then
  echo "NO_HEX $HEX"
  exit 2
fi

: > "$LOG"
echo "LISTEN_START window=${WINDOW_SEC}s port=$PORT baud=$BAUD noautoreset attempts=1"
echo "OPERATOR_PROTOCOL: 1) hold UNO RESET  2) release once  3) if miss, hold+release again"

start=$(date +%s)
attempt=0
while (( $(date +%s) - start < WINDOW_SEC )); do
  attempt=$((attempt + 1))
  echo "TRY $attempt t=$(( $(date +%s) - start ))s"
  set +e
  "$AVRDUDE" -C "$CONF" -patmega328p -carduino -P "$PORT" -b "$BAUD" -D \
    -x noautoreset -x attempts=1 \
    "-Uflash:w:${HEX}:i" >>"$LOG" 2>&1
  rc=$?
  set -e
  if (( rc == 0 )); then
    echo "UPLOAD_OK attempt=$attempt"
    exit 0
  fi
done

echo "UPLOAD_FAIL tries=$attempt after ${WINDOW_SEC}s"
exit 1
