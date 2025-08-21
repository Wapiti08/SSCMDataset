#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

: "${VWEB_HOST:=127.0.0.1}"
: "${VWEB_PORT:=8000}"

mkdir -p logs
LOG=logs/vweb.out.log
PIDFILE=.vweb.pid

# if it is running, bypass
if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "[vweb] already running (pid $(cat "$PIDFILE"))"
  exit 0
fi

echo "[vweb] starting vul_web/vweb.py on ${VWEB_HOST}:${VWEB_PORT} ..."
# run at backgroud
nohup python3 -u vul_web/vweb.py --host "$VWEB_HOST" --port "$VWEB_PORT" > "$LOG" 2>& 1 &
echo $! > "$PIDFILE"
sleep 1
if kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "[vweb] started (pid $(cat "$PIDFILE")), log: $LOG"
else
    echo "[vweb] failed to start; check $LOG" >&2
    exit 1
fi