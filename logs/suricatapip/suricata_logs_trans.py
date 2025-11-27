'''
 # @ Create Time: 2025-11-26 15:38:48
 # @ Modified time: 2025-11-26 15:39:15
 # @ Description: transform suricate logs into compitable format for table in azure
 '''

#!/usr/bin/env python3
import json
import re
from datetime import datetime
import os
import time

INPUT_FILE = "/var/log/suricata/suricata.log"
OUTPUT_FILE = "/var/log/suricata/suricata.ndjson"

LOG_RE = re.compile(
    r"\[(\d+)\s*-\s*([A-Za-z0-9\-_]+)\]\s+(\d{4}-\d{2}-\d{2})\s+"
    r"(\d{2}:\d{2}:\d{2})\s+([A-Za-z]+):\s+(.*)"
)

def follow_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line


def parse_line(line: str):
    m = LOG_RE.match(line)
    if not m:
        return None

    pid       = int(m.group(1))
    recordType = m.group(2)
    date      = m.group(3)
    time      = m.group(4)
    level     = m.group(5)
    message   = m.group(6)

    # Convert timestamp → ISO8601 Zulu
    timestamp = datetime.fromisoformat(f"{date} {time}")
    iso = timestamp.isoformat() + "Z"

    obj = {
        "recordType": recordType,
        "recordId": pid,
        "pid": pid,
        "level": level,
        "timestamp": iso,
        "TimeGenerated": iso,
        "message": message,
        "raw": line.strip()
    }
    return obj


def main():
    print(f"[INFO] Tailing Suricata log: {INPUT_FILE}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for line in follow_file(INPUT_FILE):
            rec = parse_line(line)
            if rec:
                out.write(json.dumps(rec) + "\n")
                out.flush()

if __name__ == "__main__":
    main()