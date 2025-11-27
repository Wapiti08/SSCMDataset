'''
 # @ Create Time: 2025-11-27 12:09:37
 # @ Modified time: 2025-11-27 13:00:57
 # @ Description: transfer zeek conn logs into compatible format for table in azure
 '''

import json
import time
import datetime
import sys

# --- Zeek conn.log field list, matching your sample #fields ---
ZEEK_FIELDS = [
    "ts", "uid", "id.orig_h", "id.orig_p",
    "id.resp_h", "id.resp_p", "proto", "service",
    "duration", "orig_bytes", "resp_bytes", "conn_state",
    "local_orig", "local_resp", "missed_bytes", "history",
    "orig_pkts", "orig_ip_bytes", "resp_pkts", "resp_ip_bytes",
    "tunnel_parents", "ip_proto"
]


INPUT_FILE = "/opt/zeek/spool/zeek/conn.log"      
OUTPUT_FILE = "/opt/zeek/spool/zeek/conn.ndjson"


def zeek_value_convert(key, value):
    """
    Convert Zeek types to Python types
    """
    if value in ("(empty)", "-", ""):
        return None

    if value == "T":
        return True
    if value == "F":
        return False

    # Try float or int conversion
    try:
        if "." in value:
            return float(value)
        return int(value)
    except:
        return value


def unix_ts_to_iso(ts):
    """
    Convert Zeek ts (Unix epoch float) → ISO8601 with Z suffix
    """
    dt = datetime.datetime.utcfromtimestamp(ts)
    return dt.isoformat() + "Z"


def tail_f(filename):
    """
    Tail -f implementation
    """
    with open(filename, "r") as f:
        f.seek(0, 2)  # go to end of file

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
            yield line.strip()


def process_line(line):
    """
    Convert one Zeek log line to Azure JSON
    """
    parts = line.split("\t")

    if len(parts) != len(ZEEK_FIELDS):
        return None  # skip invalid lines

    record = {}

    for key, raw_val in zip(ZEEK_FIELDS, parts):
        py_val = zeek_value_convert(key, raw_val)

        # Zeek column names with "." must be replaced
        safe_key = key.replace(".", "_")

        record[safe_key] = py_val

    # Insert Azure-compatible TimeGenerated
    if "ts" in record:
        record["TimeGenerated"] = unix_ts_to_iso(record["ts"])

    return record


def main():
    print(f"[INFO] Tailing log file: {INPUT_FILE}")

    fields = []
    types = []

    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        for line in tail_f(INPUT_FILE):
            if not line:
                continue

            # handle headers
            if line.startswith("#fields"):
                fields = line.split("\t")[1:]
                print(f"[INFO] Parsed fields: {fields}")
                continue

            if line.startswith("#types"):
                types = line.split("\t")[1:]
                print(f"[INFO] Parsed types: {types}")
                continue

            if line.startswith("#"):
                continue

            if not fields or not types:
                continue

            rec = process_line(line, fields, types)
            if rec:
                out.write(json.dumps(rec) + "\n")
                out.flush()

if __name__ == "__main__":
    main()