#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.."

: "${AZURE_STORAGE_ACCOUNT:?need AZURE_STORAGE_ACCOUNT}"
: "${AZURE_CONTAINER:?need AZURE_CONTAINER}"

echo "=== [Stage3] Publish setup_pkg.zip to Azure Blob ==="

  az storage blob upload --auth-mode login \
    --account-name "$AZURE_STORAGE_ACCOUNT" \
    --container-name "$AZURE_CONTAINER" \
    --file artifact/setup_pkg.zip --name setup_pkg.zip --overwrite true
fi

echo "[publish] uploaded setup_pkg.zip to azuze blob"
