'''
 # @ Create Time: 2025-11-26 14:43:53
 # @ Modified time: 2025-11-26 14:53:28
 # @ Description: automatically transfer local /var/log/audit/audit.log to compitable format for table in azure
 '''

import time
import re
import json
import datetime
import math
import os

AUDIT_FILE = "/var/log/audit/audit.log"
OUTPUT_FILE = "/var/log/audit/audit.ndjson"  


REMOVE_KEYS = set([
    "AUID","UID","GID","EUID","SUID","FSUID","EGID","SGID","FSGID",
    "ARCH","SYSCALL",
    "prog-id","old-auid","old-ses","OLD-AUID"
])

TYPE_RE = re.compile(r"type=([A-Z_]+)")
MSG_RE  = re.compile(r"msg=audit\((\d+(?:\.\d+)?):(\d+)\):")
KV_RE   = re.compile(r'\S+?=".*?"|\S+')

def parse_line(line: str):
    line = line.strip()
    if not line:
        return None

    result = {}

    # record type
    m_type = TYPE_RE.search(line)
    if m_type:
        result["recordType"] = m_type.group(1)
    
    # msg=audit(epoch:id)
    m_msg = MSG_RE.search(line)
    if m_msg:
        ts_float = float(m_msg.group(1))
        record_id = int(m_msg.group(2))
        result["recordId"] = record_id

        dt = datetime.datetime.fromtimestamp(ts_float)
        ms = int(round((ts_float - math.floor(ts_float)) * 1000))
        if ms:
            dt = dt.replace(microsecond=ms*1000)
            iso = dt.isoformat(timespec="milliseconds") + "Z"
        else:
            iso = dt.isoformat(timespec="seconds") + "Z"

        result["timestamp"] = iso
        result["TimeGenerated"] = iso

    # Parse key=value pairs AFTER msg()
    start_idx = m_msg.end() if m_msg else 0
    rest = line[start_idx:].strip()
    tokens = KV_RE.findall(rest)

    for tok in tokens:
        if "=" not in tok:
            continue

        key, val = tok.split("=", 1)

        if key in REMOVE_KEYS:
            continue

        # strip quotes
        if len(val) >= 2 and val[0] == '"' and val[-1] == '"':
            val_clean = val[1:-1]
        else:
            val_clean = val

        # try to convert to int
        try:
            if not val_clean.startswith("0x"):
                num = int(val_clean)
                result[key] = num
                continue
        except:
            pass

        # try float
        try:
            fp = float(val_clean)
            result[key] = fp
            continue
        except:
            pass

        result[key] = val_clean

    result["raw"] = line
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
            rec = parse_line(line)
            if rec:
                out.write(json.dumps(rec) + "\n")
                out.flush()  # 
                # print(json.dumps(rec))  


if __name__ == "__main__":
    main()

