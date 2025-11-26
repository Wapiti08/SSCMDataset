'''
 # @ Create Time: 2025-11-26 15:39:00
 # @ Modified time: 2025-11-26 15:40:28
 # @ Description: transform suricate events into compitable format for table in azure
 '''

#!/usr/bin/env python3
import time
import json
from datetime import datetime
import os

INPUT_FILE = "/var/log/suricata/eve.json"   # NDJSON
OUTPUT_FILE = "/var/log/suricata/events.json"  # JSON Array


def follow_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:   
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line


def to_iso8601(ts: str):
    # Example: "2025-11-24T06:36:11.802689-0500"
    # Remove timezone, produce ...Z
    if ts.endswith("Z"):
        return ts
    if "+" in ts:
        ts = ts.split("+")[0]
    if "-" in ts[20:]:
        ts = ts.rsplit("-", 1)[0]

    try:
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
    except:
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")

    return dt.isoformat(timespec="milliseconds") + "Z"


def flatten(prefix, data, out):
    for k, v in data.items():
        key = f"{prefix}_{k}" if prefix else k
        if isinstance(v, dict):
            flatten(key, v, out)
        else:
            out[key] = v

def parse_event(line: str):
    try:
        data = json.loads(line)
    except:
        return None

    out = {}

    # Required DCR fields
    recordType = data.get("event_type", "unknown")
    recordId = data.get("flow_id", 0)

    iso = to_iso8601(data["timestamp"])

    out["recordType"] = recordType
    out["recordId"] = recordId
    out["timestamp"] = iso
    out["TimeGenerated"] = iso

    # Flatten nested fields (http, fileinfo, dns, tls…)
    for k, v in data.items():
        if isinstance(v, dict):
            flatten(k, v, out)
        else:
            out[k] = v

    # Raw as string
    out["raw"] = line.strip()
    return out


def main():
    print(f"[INFO] Tailing Suricata EVE: {INPUT_FILE}")

    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        for line in follow_file(INPUT_FILE):
            if not line.strip():
                continue

            rec = parse_event(line)
            if rec:
                out.write(json.dumps(rec) + "\n")
                out.flush()


if __name__ == "__main__":
    main()
