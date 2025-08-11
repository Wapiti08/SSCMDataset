'''
 # @ Create Time: 2025-05-28 17:33:25
 # @ Modified time: 2025-08-11 11:51:55
 # @ Description: 
 
    training_app.py - public-facing web service

    - serve a normal homepage and health checks

    - expose a /debug endpoint that *simulate* a credential leak

 
 '''

from flask import Flask
from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Tuple

from flask import Flask, Response, abort, has_request_context, jsonify, request

try:
    from dotenv import load_dotenv, dotenv_values

    load_dotenv(override=False)
except Exception:
    pass


app = Flask(__name__)


# -------------------------
# Configuration (safe defaults)
# -------------------------
SERVICE_NAME = os.environ.get("SERVICE_NAME", "sc6-stage1")
LEAK_MODE = os.environ.get("LEAK_MODE", "mask").lower()  # "mask" | "auto"
APP_ENV = os.environ.get("APP_ENV", "prod").lower()  # "prod" | "staging" | "dev"
TRUST_PROXY_HEADERS = os.environ.get("TRUST_PROXY_HEADERS", "false").lower() == "true"
AUDIT_LOG_PATH = os.environ.get("AUDIT_LOG_PATH", "audit.log")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN") 

# Rate limiting (naive, in-memory; per-process)
RATE_MAX = int(os.environ.get("RATE_MAX", "30"))  # 30 requests
RATE_WINDOW = int(os.environ.get("RATE_WINDOW", "60"))  # per 60 seconds

START_TS = time.time()

# -------------------------
# Logging & metrics
# -------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

_RATE: Dict[str, List[float]] = {}
DEBUG_HITS_TOTAL = 0
DEBUG_LEAKS_TOTAL = 0

def get_request_id() -> str:
    return request.headers.get("X-Request-ID", str(uuid.uuid4()))

def _safe_remote_addr() -> str:
    if not has_request_context():
        return "-"

    return request.headers.get("X-Forwarded-For", request.remote_addr or "-") or "-"

def audit(event: str, **fields: Any) -> None:
    ''' best-effort JSONL audit log + stdout.
    
    '''
    base = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event": event
    }

    if has_request_context():
        base.update({
            "request_id": get_request_id(),
            "remote_addr": _safe_remote_addr(),
            "path": request.path,
            "user_agent": request.headers.get("User-Agent", "-"),
        })
    
    base.update(fields)
    line = json.dumps(base, ensure_ascii=False)
    logging.info(line)
    try:
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def mask_secret(value: str, keep_start: int=4, keep_end: int =4) -> str:
    if not value:
        return ""
    if len(value) <= keep_start + keep_end:
        return "*" * len(value)
    
    return value[:keep_start] + "*" * (len(value) - keep_start - keep_end) + value[-keep_end:]


def read_env_file(path: str=".env") -> dict:
    # returns {} if no file, handles quotes/comments
    data = dotenv_values(path) or {}
    # ensure everything is stringy for JSON serialization
    return {k: ("" if v is None else str(v)) for k, v in data.items()}

def current_demo_secrets() -> dict:
    env_map = {
        "DUMMY_TOKEN": os.environ.get("DUMMY_TOKEN", "DUMMY-EXAMPLE-TOKEN-1234567890"),
        "AZURE_STORAGE_KEY_DEMO": os.environ.get("AZURE_STORAGE_KEY_DEMO", "STORAGE-KEY-DEMO-ABCDEF123456"),
    }

    file_map = read_env_file()
    # Only add keys not already in env_map (env takes precedence)
    for k, v in file_map.items():
        env_map.setdefault(k, v)
    return env_map

def rate_limit_ok(ip: str) -> bool:
    now = time.time()
    window = _RATE.setdefault(ip, [])
    # keep only recent timestamps
    _RATE[ip] = [ts for ts in window if ts > now - RATE_WINDOW]

    if len(_RATE[ip]) >= RATE_MAX:
        return False
    
    _RATE[ip].append(now)
    return True

# ------------ Unintentional Leak ----------------
def _client_ip() -> str:
    '''
    BUGGY trust model when Trust_proxy_headers is true:
    - takes the *last* value from X-Forwarded-For header

    '''
    if TRUST_PROXY_HEADERS:
        # trust the last value in X-Forwarded-For
        xff = request.headers.get("X-Forwarded-For", "")
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if parts:
            return parts[-1]

    return request.remote_addr or "0.0.0.0"

def _looks_private_ip(ip: str) -> bool:
    '''
    naive 'private' IP check that over-matches 
    '''
    return (
        ip.startswith("10.")
        or ip.startswith("192.168.")
        or ip.startswith("172.")  # intentionally too broad
        or ip.startswith("127.")
        or ip == "::1" 
    )

def _is_internal_request() -> Tuple[bool, str]:
    ''' decide if a request 'look internal' using easy-to-misconfigure signals
    Any True result triggers a leak in LEAK_MODE == "auto".
        1) Environment drift: APP_ENV in {dev, staging}
        2) Proxy/IP trust bug
        3) Over-permissive health-check UA allowlist
    
    '''
    # 1) environment drift
    if APP_ENV in {"dev", "staging"}:
        return True, "env={APP_ENV}"
    
    # 2) proxy/IP trust bug
    ip = _client_ip()
    if _looks_private_ip(ip):
        return True, f"private_ip={ip}"
    # 3) 'trusted' health-check/monitoring agents
    ua = (request.headers.get("User-Agent") or "").lower()
    if "kube-probe" in ua or "health" in ua or "prometheus" in ua:
        return True, f"ua={ua}"
    
    return False, "no_internal_signals"

# -------------------------
# Middleware-ish Hooks
# -------------------------
@app.before_request
def _before():
    ip = request.remote_addr or "unknown"
    if not rate_limit_ok(ip):
        audit("rate_limit_block", path=request.path, ip = ip)
        return jsonify({
            "error": "Rate limit exceeded. Try again later."
        }), 429

@app.after_request
def _after(resp: Response):
    resp.headers["X-Request-ID"] = get_request_id()
    resp.headers["Cache-Control"] = "no-store"
    return resp

# ------------------------
# Endpoints
# ------------------------
@app.route("/")
def index():
    '''
    Serve a normal homepage.
    '''
    return jsonify({
        "service": SERVICE_NAME,
        "message": "This is a Health Check Service",
        "endpoints": [
            "/",
            "/healthz",
            "/readyz",
            "/metrics",
            "/debug",
            "/rotate-demo-secret",
            "/.wel-known/security.txt",
        ],
        "mode": {"LEAK_MODE": LEAK_MODE, "APP_ENV": APP_ENV, "TRUST_PROXY_HEADERS": TRUST_PROXY_HEADERS},
    })

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok", "uptime_s": round(time.time() - START_TS, 3)})

@app.route("/readyz")
def readyz():
    return jsonify({"ready": True})

@app.route("/metrics")
def metrics():
    '''
    Expose basic metrics in Prometheus format.
    '''
    uptime = round(time.time() - START_TS, 3)
    total_requests = sum(len(ts) for ts in _RATE.values())
    body = []
    body.append("# HELP app_uptime_seconds Uptime of the service")
    body.append("# TYPE app_uptime_seconds gauge")
    body.append(f"app_uptime_seconds {uptime}")
    body.append("# HELP app_requests_total Total HTTP requests observed (naive, per-process)")
    body.append("# TYPE app_requests_total counter")
    body.append(f"app_requests_total {total_requests}")
    body.append("# HELP app_debug_hits_total Total hits to /debug")
    body.append("# TYPE app_debug_hits_total counter")
    body.append(f"app_debug_hits_total {DEBUG_HITS_TOTAL}")
    body.append("# HELP app_debug_leaks_total Total simulated leaks from /debug")
    body.append("# TYPE app_debug_leaks_total counter")
    body.append(f"app_debug_leaks_total {DEBUG_LEAKS_TOTAL}")
    return Response("\n".join(body) + "\n", mimetype="text/plain")


@app.route("/.well-known/security.txt")
def security_txt():
    '''
    Serve a security.txt file for responsible disclosure.
    '''
    text = (
        "Contact: mailto:security@example.org\n"
        "Policy: https://example.org/security\n"
        "Preferred-Languages: en\n"
        "Hiring: https://example.org/careers\n"
    )
    return Response(text, mimetype="text/plain")


@app.route("/debug")
def debug():
    