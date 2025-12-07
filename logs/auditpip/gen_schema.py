'''
 # @ Create Time: 2025-12-07 12:26:17
 # @ Modified time: 2025-12-07 12:27:20
 # @ Description: parse example audit, generate unified and stable schema for Azure Log Analytics
 '''


import json
import re
from pathlib import Path

audit_line_re = re.compile(
    r'^type=\w+\s+msg=audit\([0-9\.]+:[0-9]+\):\s*(?P<body>.*)'
)
kv_re = re.compile(r'(\w+)=(".*?"|\S+)')


def collect_schema(infile, outfile="schema.json"):
    keys = set()

    with open(infile, "r") as f:
        for line in f:
            m = audit_line_re.match(line)
            if not m:
                continue
            body = m.group("body")
            for key, _ in kv_re.findall(body):
                keys.add(key.lower())
    
    schema = sorted(keys)
    with open(outfile, "w") as f:
        json.dump(schema, f, indent=2)

    print(f"Schema written to {outfile} with {len(schema)} keys.")

if __name__ == "__main__":

    infile = Path.cwd() / "audit.log"
    collect_schema(infile)