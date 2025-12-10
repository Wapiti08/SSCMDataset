#!/bin/bash

# ===== get system info =====
HOSTNAME=$(hostname)
KERNEL=$(uname -a)
CPU=$(lscpu | sed 's/"/\\"/g')
MEM=$(free -h)
DISK=$(df -h)

# ===== build JSON for audit=====
DATA=$(cat <<EOF
{
  "hostname": "$HOSTNAME",
  "kernel": "$KERNEL",
  "cpu": "$(echo "$CPU" | tr '\n' ' ' )",
  "memory": "$(echo "$MEM" | tr '\n' ' ' )",
  "disk": "$(echo "$DISK" | tr '\n' ' ' )"
}
EOF
)

# ===== send to server =====
curl -X POST \
     -H "Content-Type: application/json" \
     -d "$DATA" \
     http://20.93.23.234:8081/upload
