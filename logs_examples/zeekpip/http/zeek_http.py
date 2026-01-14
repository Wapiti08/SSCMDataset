'''
 # @ Create Time: 2025-11-27 15:04:55
 # @ Modified time: 2025-11-27 15:04:57
 # @ Description: convert zeek http logs into compatible format for table in azure
 '''

import json
import time
import datetime
import re

INPUT_FILE = "/opt/zeek/spool/zeek/http.log"
OUTPUT_FILE = "/opt/zeek/spool/zeek/http.ndjson"

def tail_f(filename):
    """Tail -f implementation."""
    with open(filename, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
            yield line.strip()


def unix_ts_to_iso(ts):
    """Convert Zeek ts (epoch float) → ISO8601."""
    dt = datetime.datetime.fromtimestamp(float(ts))
    return dt.isoformat() + "Z"


def sanitize_field_name(name, log_type="http"):
    """Convert Zeek field name into Azure-safe column name."""
    name = name.replace(".", "_")

    # Avoid single-character columns
    if len(name) == 1:
        name = f"{log_type}_{name}"

    # Remove invalid chars
    name = re.sub(r"[^A-Za-z0-9_]", "_", name)

    return name


def convert_value(val, field_type):
    """Convert Zeek values into Azure JSON-safe types."""
    if val in ("-", "(empty)", ""):
        return None

    if field_type == "bool":
        return True if val == "T" else False

    # set[string]  → list[str]
    if field_type.startswith("set[string]"):
        return val.split(",") if val != "-" else []

    # vector[string] → list[str]
    if field_type.startswith("vector[string]"):
        return val.split(",") if val != "-" else []

    # vector / set (non-string) → list of floats
    if field_type.startswith("vector[") or field_type.startswith("set["):
        return [float(v) for v in val.split(",")] if val != "-" else []

    # integer types
    if field_type in ("count", "port"):
        try:
            return int(val)
        except:
            return None

    # float types: time / interval
    if field_type in ("time", "interval"):
        try:
            return float(val)
        except:
            return None

    # default: return string
    return val


def parse_zeek_line(line, fields, types):
    """Convert one Zeek http.log line into Azure JSON."""
    parts = line.split("\t")
    if len(parts) != len(fields):
        return None

    record = {}

    for key, raw_val, ftype in zip(fields, parts, types):
        safe_key = sanitize_field_name(key, log_type="http")
        record[safe_key] = convert_value(raw_val, ftype)

    # Add TimeGenerated
    if "ts" in fields:
        ts_index = fields.index("ts")
        record["TimeGenerated"] = unix_ts_to_iso(parts[ts_index])

    return record


def main():
    print(f"[INFO] Tailing log file: {INPUT_FILE}")

    fields = []
    types = []

    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        for line in tail_f(INPUT_FILE):
            if not line:
                continue

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
                continue  # wait until both are loaded

            rec = parse_zeek_line(line, fields, types)
            if rec:
                out.write(json.dumps(rec) + "\n")
                out.flush()


if __name__ == "__main__":
    main()