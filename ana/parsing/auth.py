'''
 # @ Create Time: 2025-12-23 16:27:36
 # @ Modified time: 2025-12-23 17:36:29
 # @ Description: whether attacker has authenticated successfully
 '''

import re
import pandas as pd

SSH_PATTERNS = {
    "ssh_fail": r"(Failed password|Invalid user)",
    "ssh_success": r"Accepted password",
    "ssh_close": r"Connection closed",
}

def parse_auth_log(path: str) -> pd.DataFrame:
    rows = []
    with open(path, "r", errors="ignore") as f:
        for line in f:
            ts = pd.to_datetime(line[:32], errors="coerce", utc=True)
            if pd.isna(ts):
                continue

            action = None
            for k, pat in SSH_PATTERNS.items():
                if re.search(pat, line):
                    action = k
                    break

            rows.append({
                "ts": ts,
                "host": line.split()[2],
                "source": "auth",
                "event_type": "auth",
                "action": action or "other",
                "subject": line,
                "object": "",
                "raw": line.strip(),
                "extra": {},
            })

    return pd.DataFrame(rows)