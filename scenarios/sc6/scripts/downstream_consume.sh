#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

: "${AZURE_STORAGE_ACCOUNT:?need AZURE_STORAGE_ACCOUNT}"
: "${AZURE_CONTAINER:?need AZURE_CONTAINER}"

WORKDIR="artifact/downstream"
mkdir -p "$WORKDIR"

# build common auth args: perfer SAS, then Key, else login
AUTH_ARGS=()
if [[ -n "${AZURE_SAS_TOKEN:-}" ]];then
  AUTH_ARGS+=(--sas-token "$AZURE_SAS_TOKEN")
elif [[ -n "${AZURE_STORAGE_KEY:-}" ]];then
  AUTH_ARGS+=(--account-key "$AZURE_STORAGE_KEY")
else
  AUTH_ARGS+=(--auth-mode login)
fi

echo "=== [Try to download setup_pkg.zip (preferred) ==="
ZIP_BLOB="setup_pkg.zip"
PY_BLOB="setup.py"

got_zip=false
if az storage blob exists \
        --account-name "$AZURE_STORAGE_ACCOUNT" \
        --container-name "$AZURE_CONTAINER" \
        --name "$ZIP_BLOB" \
        "${AUTH_ARGS[@]}" \
        --query exists -o tsv | grep -qi true; then
    az storage blob download \
        --account-name "$AZURE_STORAGE_ACCOUNT" \
        --container-name "$AZURE_CONTAINER" \
        --name "$ZIP_BLOB" --file "$WORKDIR/$ZIP_BLOB" \
        --overwrite true \
        "${AUTH_ARGS[@]}"
    got_zip=true
    echo "[download] got $ZIP_BLOB"
else
    echo "[download] $ZIP_BLOB not found, will fall back to $PY_BLOB"
fi

echo "=== [stage4] Prepare files ==="
if $got_zip; then
    rm -rf "$WORKDIR/unpacked"
    mkdir -p "$WORKDIR/unpacked"
    unzip -q "$WORKDIR/$ZIP_BLOB" -d "$WORKDIR/unpacked"
    SETUP_PATH="$WORKDIR/unpacked/setup.py"
    if [[ ! -f "$SETUP_PATH" ]]; then
        echo "❌ setup.py not found in zip; abort"
        exit 1
    fi
else
    az storage blob download \
        --account-name "$AZURE_STORAGE_ACCOUNT" \
        --container-name "$AZURE_CONTAINER" \
        --name "$PY_BLOB" \
        --file "$WORKDIR/setup.py" \
        --overwrite true \
        "${AUTH_ARGS[@]}"
    SETUP_PATH="$WORKDIR/setup.py"
fi

echo "=== [Stage4] Execute setup.py code (no install) ==="
# Ensure python is available
python3 --version

# Make sure setuptools exists; if not, we still attempt to run (setup.py will likely error gracefully)
python3 - <<'PY'
try:
    import setuptools  # noqa: F401
    print("[check] setuptools available")
except Exception as e:
    print("[warn] setuptools not importable:", e)
PY

# (--name/--version/--help-commands) will execute top-level code and print metadata.
set +e
(
  cd "$(dirname "$SETUP_PATH")"
  echo "[exec] python3 setup.py --name"
  python3 setup.py --name
  status=$?
  echo "[exec] exit code: $status"
)
set -e 

echo "=== [Stage4] First lines of executed setup.py (for confirmation) ==="
head -n 20 "$SETUP_PATH" || true

echo "✅ Stage4 complete (decompressed and executed setup.py)"


