import re
import pandas as pd
from pathlib import Path
import ipaddress

# audit(SECONDS.MICROS:ID)
_AUDIT_TS = re.compile(r"audit\((\d+)\.(\d+):(\d+)\)")

def _grab(line: str, k: str) -> str:
    ''' extract corresponding key's value from audit log line
    
    '''
    m = re.search(rf"(?:^|\s){re.escape(k)}=([^\s]+)", line)
    return m.group(1).strip('"') if m else ""

def _norm_missing(s: str) -> str:
    s = (s or "").strip()
    return "" if s in {"", "?", "(null)", "unknown"} else s

def _as_ip(s: str) -> str:
    if not s or s in {"?", "(null)"}:
        return ""
    try:
        return str(ipaddress.ip_address(s))
    except ValueError:
        return ""
    
def normalize_host_and_src(line: str) -> tuple[str, str]:
    node = _norm_missing(_grab(line, "node"))
    addr = _grab(line, "addr")          
    hostname = _grab(line, "hostname") 

    host = node or  "unknown"

    src_ip = _as_ip(addr) or _as_ip(hostname)

    host_ip = _as_ip(host)
    if host_ip and not src_ip:
        src_ip = host_ip
        host = "unknown"

    return host, src_ip

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
            src_ip = _as_ip(addr)

            success = _grab(line, "success")
            auid = _grab(line, "auid")
            uid = _grab(line, "uid")
            key = _grab(line, "key")

            host, src_ip = normalize_host_and_src(line)

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
                "src_ip": src_ip,   
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

if __name__ == "__main__":
    # for quick testing
    # python3 -m parsing.auditd
    data_path = Path.cwd().parent.joinpath("data", "sc3", "audit.log")
    audit_df = parse_audit_log(data_path)
    print(audit_df.head())
    print(audit_df.columns)
    print(audit_df['host'].value_counts())
    print(audit_df["src_ip"].value_counts().head(20))