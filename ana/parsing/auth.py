'''
 # @ Create Time: 2025-12-23 16:27:36
 # @ Modified time: 2025-12-23 17:36:29
 # @ Description: whether attacker has authenticated successfully
 '''

import re
import pandas as pd
from pathlib import Path

SSH_INVALID_USER = re.compile(r"Invalid user (?P<user>\S+) from (?P<src_ip>\d+\.\d+\.\d+\.\d+) port (?P<src_port>\d+)")
SSH_FAILED_PW = re.compile(r"Failed password for (invalid user )?(?P<user>\S+) from (?P<src_ip>\d+\.\d+\.\d+\.\d+) port (?P<src_port>\d+)")
SSH_ACCEPTED = re.compile(r"Accepted \S+ for (?P<user>\S+) from (?P<src_ip>\d+\.\d+\.\d+\.\d+) port (?P<src_port>\d+)")
SSH_CLOSED = re.compile(r"Connection closed by (invalid user )?(?P<src_ip>\d+\.\d+\.\d+\.\d+) port (?P<src_port>\d+)")

def parse_auth_log(path: str | Path) -> pd.DataFrame:
    rows = []
    with Path(path).open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            # check whether line is empty
            line = line.strip()
            if not line:
                continue
        
            # works for example like: 2025-12-07T08:12:34.186138-05:00 ...
            ts_token = line.split(" ", 1)[0]
            ts = pd.to_datetime(ts_token, utc=True, errors="coerce")
            if pd.isna(ts):
                continue

            # host usually follows timestamp
            parts = line.split()
            host = parts[1] if len(parts) > 1 else "unknown"

            action = "record"
            src_ip = src_port = user = ""
            obj = ""

            m = SSH_INVALID_USER.search(line)
            if m:
                action = "ssh_invalid_user"
                user = m.group("user")
                src_ip = m.group("src_ip")
                src_port = m.group("src_port")
                obj = user
            
            m = SSH_FAILED_PW.search(line) or m
            if m and action == "record":
                action = "ssh_failed_password"
                user = m.group("user")
                src_ip = m.group("src_ip")
                src_port = m.group("src_port")
                obj = user 
            
            m = SSH_ACCEPTED.search(line) or m
            if m and action == "record":
                action = "ssh_login_success"
                user = m.group("user")
                src_ip = m.group("src_ip")
                src_port = m.group("src_port")
                obj = user

            m = SSH_CLOSED.search(line) or m
            if m and action == "record":
                action = "ssh_conn_closed"
                src_ip = m.group("src_ip")
                src_port = m.group("src_port")
                obj = "sshd"

            rows.append({
                "ts": ts,
                "host": host,
                "source": "auth",
                "event_type": "auth",
                "action": action,
                "subject": src_ip if src_ip else "",   # join-friendly
                "object": obj,
                "src_ip": src_ip,
                "src_port": src_port,
                "user": user,
                "raw": line,
                "extra": {},  # keep small
            })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    # python3 -m parsing.auth
    data_path = Path.cwd().parent.joinpath("data", "sc3", "auth.log")
    auth_df = parse_auth_log(data_path)
    print(auth_df.head())
    print(auth_df.columns)
    print(auth_df['host'].value_counts())
    print(auth_df["src_ip"].value_counts().head(20))