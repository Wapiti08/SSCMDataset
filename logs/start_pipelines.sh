#!/bin/bash

echo "[INFO] Starting all ingestion pipelines..."
echo "[INFO] Timestamp: $(date)"

# Function to start a pipeline in background and log
start_pipeline() {
    local cmd="$1"
    local name="$2"

    echo "[INFO] Starting $name ..."
    nohup sudo python3 $cmd >> /var/log/pipeline_$name.log 2>&1 &
    echo "[INFO]   → Log: /var/log/pipeline_$name.log"
}

# Create log directory if not exists
sudo mkdir -p /var/log
sudo touch /var/log/pipeline_audit.log

# Start each pipeline
start_pipeline "auditpip/audit.py" "audit"
start_pipeline "suricatapip/suricata_events_trans.py" "suricata_events"
start_pipeline "suricatepip/suricata_logs_trans.py" "suricata_logs"
start_pipeline "traceepip/tracee.py" "tracee"
start_pipeline "zeekpip/zeek_conn.py" "zeek_conn"
start_pipeline "zeekpip/zeek_dns.py" "zeek_dns"
start_pipeline "zeekpip/zeek_files.py" "zeek_files"
start_pipeline "zeekpip/zeek_http.py" "zeek_http"

echo "[INFO] All pipelines started."
echo "[INFO] Check logs under: /var/log/pipeline_*.log"
