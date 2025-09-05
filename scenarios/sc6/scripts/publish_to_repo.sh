#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.."

# Auto-load .env if present
if [[ -f ".env" ]]; then
  set -a; source .env; set +a
fi

: "${AZURE_STORAGE_ACCOUNT:?need AZURE_STORAGE_ACCOUNT}"
: "${AZURE_CONTAINER:?need AZURE_CONTAINER}"

SRC_FILE="artifact/setup_pkg.zip"
[[ -f "$SRC_FILE" ]] || { echo "❌ Not found: $SRC_FILE"; exit 1; }

# auth preference: SAS > KEY > login
AUTH_ARGS=()
if [[ -n "${AZURE_SAS_TOKEN:-}" ]];then
  AUTH_ARGS+=(--sas-token "$AZURE_SAS_TOKEN")
elif [[ -n "${AZURE_STORAGE_KEY:-}" ]];then
  AUTH_ARGS+=(--account-key "$AZURE_STORAGE_KEY")
else
  AUTH_ARGS+=(--auth-mode login)
fi

echo "===== Publish $SRC_FILE to Azure Blob ====="

az storage blob upload \
  --account-name "$AZURE_STORAGE_ACCOUNT" \
  --container-name "$AZURE_CONTAINER" \
  "${AUTH_ARGS[@]}" \
  --file "$SRC_FILE" \
  --name setup_pkg.zip --overwrite true

echo "[publish] uploaded setup_pkg.zip to https://$AZURE_STORAGE_ACCOUNT.blob.core.windows.net/$AZURE_CONTAINER/setup_pkg.zip"
