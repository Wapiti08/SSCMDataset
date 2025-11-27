'''
 # @ Create Time: 2025-11-27 14:44:41
 # @ Modified time: 2025-11-27 14:44:43
 # @ Description: convert zeek files logs into compatible format for table in azure
 '''

import json
import time
import datetime
import re

INPUT_FILE = "/opt/zeek/spool/zeek/files.log"
OUTPUT_FILE = "/opt/zeek/spool/zeek/files.ndjson"

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


def sanitize_field_name(name, log_type = "files"):
    ''' Convert Zeek field names into Azure-safe column names.

    Rules:
    - Replace '.' with '_'
    
    '''
    # Replace "." with "_"
    name = name.replace(".", "_")

    # avoid single-letter columns
    if len(name) == 1:
        name = f"{log_type}_{name}"

    # remove illegal characters
    name = re.sub(r"[^A-Za-z0-9_]", "_", name)

    return name


def convert_value(val, field_type):
    """Convert Zeek value into Python/Azure-compatible types."""
    if val in ("-", "(empty)", ""):
        return None

    if field_type == "bool":
        return True if val == "T" else False

    # set[string] / vector[string] → list[str]
    if field_type.startswith("set[string]") or field_type.startswith("vector[string]"):
        return val.split(",") if val != "-" else []

    if field_type.startswith("vector[") or field_type.startswith("set["):
        return [float(v) for v in val.split(",")] if val != "-" else []

    if field_type in ("count", "port"):
        try:
            return int(val)
        except Exception:
            return None

    if field_type in ("interval", "time"):
        try:
            return float(val)
        except Exception:
            return None

    return val


def parse_zeek_line(line, fields, types):
    """Convert one Zeek files.log line into Azure JSON."""
    parts = line.split("\t")
    if len(parts) != len(fields):
        return None

    record = {}

    for key, raw_val, ftype in zip(fields, parts, types):
        safe_key = sanitize_field_name(key, log_type="files")
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

            rec = parse_zeek_line(line, fields, types)
            if rec:
                out.write(json.dumps(rec) + "\n")
                out.flush()


if __name__ == "__main__":
    main()
