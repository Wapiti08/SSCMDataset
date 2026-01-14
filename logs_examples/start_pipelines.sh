#!/bin/bash

echo "[INFO] Starting all ingestion pipelines from current directory: $(pwd)"
echo "[INFO] Timestamp: $(date)"

LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

start_pipeline() {
    local script_path="$1"
    local name="$2"

    echo "[INFO] Starting $name ..."
    nohup sudo python3 "$script_path" >> "$LOG_DIR/${name}.log" 2>&1 &
    echo "[INFO]   → Log: $LOG_DIR/${name}.log"
}

# Start each pipeline from current directory
start_pipeline "auditpip/audit.py" "audit"
start_pipeline "suricatapip/suricata_events_trans.py" "suricata_events"
start_pipeline "suricatepip/suricata_logs_trans.py" "suricata_logs"
start_pipeline "traceepip/tracee.py" "tracee"
start_pipeline "zeekpip/conn/zeek_conn.py" "zeek_conn"
start_pipeline "zeekpip/dns/zeek_dns.py" "zeek_dns"
start_pipeline "zeekpip/files/zeek_files.py" "zeek_files"
start_pipeline "zeekpip/http/zeek_http.py" "zeek_http"

echo "[INFO] All pipelines started successfully."
echo "[INFO] Check logs under: $(pwd)/logs/"
