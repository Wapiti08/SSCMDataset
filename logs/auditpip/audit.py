'''
 # @ Create Time: 2025-12-07 11:52:45
 # @ Modified time: 2025-12-07 13:32:11
 # @ Description:
 '''

import json
import re
import binascii
from datetime import datetime, timezone
import time
import os

AUDIT_FILE = "/var/log/audit/audit.log"
OUTPUT_FILE = "/var/log/audit/audit.ndjson"  

# -------------------------------
# Load fixed schema once
# -------------------------------
with open("schema.json", "r") as f:
    FIXED_KEYS = set(json.load(f))

audit_line_re = re.compile(
    r'^type=(?P<type>\w+)\s+msg=audit\((?P<ts>[0-9\.]+):(?P<eid>[0-9]+)\):\s*(?P<body>.*)'
)

kv_re = re.compile(r'(\w+)=(".*?"|\S+)')


def decode_hex_or_empty(value: str):
    is_hex = len(value) % 2 == 0 and all(c in "0123456789abcdefABCDEF" for c in value)
    if not is_hex:
        return value
    try:
        decoded = binascii.unhexlify(value).decode("utf-8", errors="ignore")
        return decoded if decoded.strip() else ""
    except Exception:
        return ""
    
def to_timegenerated(ts_str: str):
    try:
        ts = float(ts_str)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")
    except Exception:
        return ""


def parse_audit_line(line: str):
    m = audit_line_re.match(line)
    if not m:
        return None
    
    body = m.group("body")

    result = {  
        "TimeGenerated": to_timegenerated(m.group("ts")),
        "audit_type": m.group("type"),
        "timestamp": m.group("ts"),
        "event_id": m.group("eid"),
        "raw": line.strip()
    }

    # Insert empty schema fields
    for key in FIXED_KEYS:
        result[key] = ""

    # Populate allowed keys
    for key, raw_val in kv_re.findall(body):
        key = key.lower()  # normalize to lowercase (必需）

        if key not in FIXED_KEYS:
            continue  # DROP unknown keys

        val = raw_val.strip('"')
        val = decode_hex_or_empty(val)

        result[key] = val

    return result


def follow_file(path):
    """ Tail -F equivalent
    
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

def main():
    print("[INFO] Real-time monitoring started:", AUDIT_FILE)
    print("[INFO] Writing to:", OUTPUT_FILE)

    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        for line in follow_file(AUDIT_FILE):
            rec = parse_audit_line(line)
            if rec:
                out.write(json.dumps(rec) + "\n")
                out.flush()  # 
                # print(json.dumps(rec))  

if __name__ == "__main__":
    main()
