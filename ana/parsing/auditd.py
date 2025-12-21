import re
import pandas as pd

_AUDIT_TS = re.compile(r"audit\((\d+)\.")

def parse_audit_log(path: str) -> pd.DataFrame:
    rows = []
    with open(path, "r", errors="ignore") as f:
        for line in f:
            m = _AUDIT_TS.search(line)
            if not m:
                continue
            ts = pd.to_datetime(int(m.group(1)), unit="s", utc=True)

            def grab(k):
                m = re.search(rf"{k}=([^\s]+)", line)
                return m.group(1).strip('"') if m else ""

            rows.append({
                "ts": ts,
                "host": grab("hostname") or "unknown",
                "source": "auditd",
                "event_type": grab("type"),
                "action": grab("syscall"),
                "subject": f"pid={grab('pid')} exe={grab('exe')}",
                "object": grab("addr"),
                "raw": line.strip(),
                "extra": {},
            })

    return pd.DataFrame(rows)
