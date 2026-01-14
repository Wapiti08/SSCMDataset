#!/usr/bin/python3
'''
 # @ Create Time: 2025-11-26 15:58:16
 # @ Modified time: 2025-11-26 15:58:19
 # @ Description: unified interface to convert transformed ndjson logs into array format
 '''

import json
import sys

def convert_ndjson_to_array(ndjson_path, output_path):
    records = []
    with open(ndjson_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except:
                continue
            records.append(obj)

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(records, out, indent=2)

    print(f"[OK] Converted {len(records)} lines → {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ndjson_to_array.py <input.ndjson> <output.json>")
        sys.exit(1)

    ndjson_path = sys.argv[1]
    output_path = sys.argv[2]
    convert_ndjson_to_array(ndjson_path, output_path)