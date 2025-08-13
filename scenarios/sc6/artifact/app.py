'''
 # @ Create Time: 2025-08-13 11:47:46
 # @ Modified time: 2025-08-13 13:32:11
 # @ Description: simulated benign payload
 '''

from __future__ import annotations
import json, os, time, platform, sys
from pathlib import Path

ART = Path(__file__).parent
REPORT = ART.joinpath("artifact_execution_report.json")

def mask(v: str) -> str:
    if v is None: return ""
    v=str(v); return (v[:4]+"*"*(len(v)-8)+v[-4:]) if len(v)>8 else "*"*len(v)

def env_redacted():
    out={}
    for k,v in os.environ.items():
        K=k.upper()
        if K in {"GITHUB_RUN_ID","GITHUB_REPOSITORY","CI","MODE"}:
            out[k]=v
        elif any(t in K for t in ("TOKEN","KEY","SECRET","PASSWORD","SAS")):
            out[k]=mask(v)
    return out

def main():
    # first stage: write mark
    (ART/"_first_stage_done").write_text("FIRST_STAGE_SIMULATED\n","utf-8")
    time.sleep(0.2)
    # second stage: write second mark
    (ART/"_second_stage_done").write_text("SECOND_STAGE_SIMULATED\n","utf-8")

    # read manifest
    manifest={}
    if (ART/"manifest.json").exists():
        manifest=json.loads((ART/"manifest.json").read_text("utf-8"))

    # write a report
    report={
        "action":"simulated_deploy",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "mode": os.getenv("MODE","unknown"),
        "manifest": manifest,
        "tamper_detected": "SIMULATED_INJECTION" in (ART/"malicious.py").read_text("utf-8", errors="ignore"),
        "env": env_redacted(),
        "cwd": os.getcwd(),
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), "utf-8")
    print("OK: simulated deploy done ->", REPORT)
    
if __name__=="__main__": 
    main()
