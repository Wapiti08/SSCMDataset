'''
 # @ Create Time: 2025-08-13 16:00:05
 # @ Modified time: 2025-08-13 16:01:24
 # @ Description: stage1 payload and execute as a monitoring process, wait for certain time to download stage 2 payload
 '''


from __future__ import annotations
import json, os, time, signal, base64, random
from pathlib import Path
from typing import Any, Dict, List
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

LOG_DIR = Path("logs"); LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT = LOG_DIR / "stage1_random_wait.jsonl"  # JSON Lines
RUN   = LOG_DIR / "stage2_run_summary.json"   # one-shot summary

# ---------------- Logging ----------------
def audit(event: str, **fields: Any) -> None:
    rec = {"ts": int(time.time()), "event": event}
    rec.update(fields)
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def mask(v: str) -> str:
    if not v: return ""
    v = str(v)
    return (v[:4] + "*" * max(0, len(v) - 8) + v[-4:]) if len(v) > 8 else "*" * len(v)

# --------- Networking -----------
def fetch_url(url: str, max_bytes: int = 1 << 20) -> bytes:
    req = Request(url, headers={"User-Agent": "sc6-stage1-randwait/1.0"})
    with urlopen(req, timeout=15) as resp:
        body = resp.read(max_bytes + 1)
    if len(body)   > max_bytes:
        raise ValueError(f"Response too large: {len(body)} bytes")
    return body


# ------- Tiny interpreter ----------

