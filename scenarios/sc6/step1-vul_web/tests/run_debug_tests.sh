#!/usr/bin/env bash
# certain common errors will cause the script to immediately fail, explicitly and loudly.
set -euo pipefail

APP_PORT="${APP_PORT:-5000}"
APP_HOST="${APP_HOST:-127.0.0.1}"

# Start the app with a specific env block, wait for readiness, run a test function, then stop.
run_case () {
    local title="$1"; shift
    echo "----- CASE: $title -----"

    # clean previous logs/PIDs
    rm -f app.pid

    # start app in background with an isolated env
    # shellcheck disable=SC2086
    env HOST="$APP_HOST" PORT="$APP_PORT" \
      LEAK_MODE="${LEAK_MODE:-mask}" \
      APP_ENV="${APP_ENV:-prod}" \
      TRUST_PROXY_HEADERS="${TRUST_PROXY_HEADERS:-false}" \
      DUMMY_TOKEN="DUMMY-EXAMPLE-TOKEN-1234567890" \
      AZURE_STORAGE_KEY_DEMO="STORAGE-KEY-DEMO-ABCDEF123456" \
      python3 vweb.py > /dev/null 2>&1 &
    echo $! > app.pid

    # wait for service
    for i in $(seq 1 60); do
        if curl -s "http://$APP_HOST:$APP_PORT/healthz" > /dev/null; then break; fi
        sleep 0.5
    done
    curl -s "http:$APP_HOST:$APP_PORT/healthz" > /dev/null || {
        echo "Service failed to start"; pkill -F app.pid || true; exit 1;
    }

    # run the test function passed in
    "$@"

    # stop app
    pkill -F app.pid || true
    sleep 0.5
}

# helpers
jq_field () { jp -r "$1"; }
assert_eq () {
    local got="$1“; local want="$2"; local msg="$3"
    if [["$got" != "$want"]]; then
        echo "ASSERT FAIL: $msg (got='$got', want='$want')"
        exit 1
    fi
    echo "OK: $msg"
}

test_mask_mode () {
    echo "Testing: mask mode returns leak=false"
    local resp
    resp="$(curl -s "http://$APP_HOST:$APP_PORT/debug")"
    local leak
    leak="$(jq_field '.leak' <<<"$resp")"
    assert_eq "$leak" "false" "mask mode should not leak"
}

test_auto_env_drift () {
    echo "Testing: auto mode + APP_ENV=dev triggers accidental leak"
    local resp
    resp="$(curl -s "http://$APP_HOST:$APP_PORT/debug")"
    local leak note
    leak="$(jq_field '.leak' <<<"$resp")"
    note="$(jq_field '.note' <<<"$resp")"
    assert_eq "$leak" "true" "auto+dev should leak"
    [[ "$note" == ACCIDENTAL* ]] && echo "OK: note indicates accidental leak" || { echo "Unexpected note: $note"; exit 1; }
}

test_auto_proxy_bug () {
    echo "Testing: auto mode + proxy trust bug (X-Forwarded-For last private IP)"
    local resp
    # simulate attacker-controlled header: last hop looks private due to bug
    resp = "$(curl -s -H "X-Forwarded-For: 203.0.113.10, 172.20.0.1" "http://$APP_HOST:$APP_PORT/debug")"
    local leak reason
    leak="$(jq_field '.leak' <<<"$resp")"
    note="$(jq_field '.note' <<<"$resp")"
    assert_eq "$leak" "true" "auto+proxy-bug should leak"
    echo "Reason: $reason"
}

test_auto_health_ua () {
    echo "Testing: auto mode + healthcheck UA triggers leak"
    local resp 
    resp="$(curl -s -A "kube-probe/1.27" "http://$APP_HOST:$APP_PORT/debug")"
    local leak
    leak="$(jq_field ".leak" <<<"$resp")"
    assert_eq "$leak" "true" "auto+health UA should leak"
}

test_auto_no_signals () {
    echo "Testing: auto mode but no internal signals -> mask"
    local resp 
    resp="$(curl -s -A "kube-probe/1.27" "http://$APP_HOST:$APP_PORT/debug")"
    local leak
    leak="$(jq_field ".leak" <<<"$resp")"
    assert_eq "$leak" "false" "auto+no-signals should not leak"
}

# ----- Execute scenarios -----
# 1) Mask (always masked)
LEAK_MODE=mask APP_ENV=prod TRUST_PROXY_HEADERS=false \ 
    run_case "mask/default" test_mask_mode

# 2) AUTO + ENV DRIFT
LEAK_MODE=auto APP_ENV=dev TRUST_PROXY_HEADERS=false \
    run_case "auto/env-drift" test_auto_env_drift

# 3) AUTO + PROXY BUG
LEAK_MODE=auto APP_ENV=prod TRUST_PROXY_HEADERS=true \
    run_case "auto/proxy-bug" test_auto_proxy_bug

# 4) AUTO + HEALTHCHECK UA
LEAK_MODE=auto APP_ENV=prod TRUST_PROXY_HEADERS=false \
    run_case "auto/healthcheck-ua" test_auto_health_ua

# 5) AUTO + NO INTERNAL SIGNALS
LEAK_MODE=auto APP_ENV=prod TRUST_PROXY_HEADERS=false \
    run_case "auto/no-internal-signals" test_auto_no_signals

echo "All tests passed!"

