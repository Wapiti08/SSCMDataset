#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

SETUP="$(cygpath -w "$(pwd)/artifact/setup.py")"
ZIP=artifact/setup_pkg.zip

echo "=== [Stage3] Package setup.py (optional) ==="
if [[ -f "$SETUP" ]]; then
  rm -f "$ZIP"
  (cd artifact && zip -q setup_pkg.zip setup.py)
  echo "[package] created $ZIP"
else
  echo "[package] $SETUP not found, skip zip"
fi