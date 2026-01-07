import re
import pandas as pd
from pathlib import Path

# audit(SECONDS.MICROS:ID)
_AUDIT_TS = re.compile(r"audit\((\d+)\.(\d+):(\d+)\)")

def _grab(line: str, k: str) -> str:
    ''' extract corresponding key's value from audit log line
    
    '''
    m = re.search(rf"{k}=([^\s]+)", line)
    return m.group(1).strip('"') if m else ""


def parse_audit_log(path: str | Path) -> pd.DataFrame:
    rows = []
    with Path(path).open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # locate timestamp
            m = _AUDIT_TS.search(line)
            if not m:
                continue

            sec = int(m.group(1))
            micros = int(m.group(2))
            ts = pd.to_datetime(sec, unit="s", utc=True) + pd.to_timedelta(micros, unit="us")

            etype = _grab(line, "type") or _grab(line, "msg")
            syscall = _grab(line, "syscall")
            pid = _grab(line, "pid")
            ppid = _grab(line, "ppid")
            exe = _grab(line, "exe")
            comm = _grab(line, "comm")
            addr = _grab(line, "addr")
            success = _grab(line, "success")
            auid = _grab(line, "auid")
            uid = _grab(line, "uid")
            key = _grab(line, "key")

            host = _grab(line, "node") or _grab(line, "hostname") or "unknown"

            # join-friendly subject/object
            # subject = process identity, object = remote addr or target path if present
            subject = f"pid={pid} exe={exe or comm}"
            obj = addr

            rows.append({
                "ts": ts,
                "host": host,
                "source": "auditd",
                "event_type": etype or "audit",
                "action": syscall or "syscall",
                "subject": subject,
                "object": obj,
                "pid": pid,
                "ppid": ppid,
                "user": uid or auid,
                "src_ip": addr,   # if addr is IP (often is)
                "raw": line,
                "extra": {
                    "comm": comm,
                    "exe": exe,
                    "syscall": syscall,
                    "success": success,
                    "uid": uid,
                    "auid": auid,
                    "key": key,
                },
            })

    return pd.DataFrame(rows)
