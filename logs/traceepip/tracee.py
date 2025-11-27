'''
 # @ Create Time: 2025-11-27 10:45:00
 # @ Modified time: 2025-11-27 10:45:11
 # @ Description: transform tracee logs into compitable format for table in azure
 '''


import time
import json
import datetime

INPUT_FILE = "/tmp/tracee-events.json"      
OUTPUT_FILE = "/tmp/tracee.ndjson"

def follow_file(filename):
    ''' tail node to continuously read new lines from a file '''
    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        # move to the end of file
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line


def parse_line(raw_line: str):
    raw = raw_line.strip()

    # bypass blank lines
    if not raw:
        return None
    
    # bypass lines starting with level
    if raw.startswith('{"level"'):
        return None

    # parse JSON
    try:
        record = json.loads(raw)
    except:
        return None

    # create TimeGenerated field
    if "timestamp" in record:
        try:
            ts_ns = int(record["timestamp"])
            ts_s = ts_ns / 1_000_000_000  
            record["TimeGenerated"] = datetime.datetime.fromtimestamp(ts_s).isoformat() + "Z"
        except:
            record["TimeGenerated"] = datetime.datetime.now().isoformat() + "Z"
    else:
        record["TimeGenerated"] = datetime.datetime.now().isoformat() + "Z"

    return record

def main():
    print(f"[INFO] Tailing log file: {INPUT_FILE}")

    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        for line in follow_file(INPUT_FILE):
            rec = parse_line(line)
            if rec:
                out.write(json.dumps(rec) + "\n")
                out.flush()

if __name__ == "__main__":
    main()