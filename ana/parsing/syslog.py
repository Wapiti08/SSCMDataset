from pathlib import Path
from typing import Iterable
import re
import pandas as pd
from .utils import _read_csv, _s, _parse_ts, _subset_raw

# -----------------------------
# message classifiers (lightweight, regex-based)
# -----------------------------

SSH_INVALID_USER = re.compile(r"sshd\[\d+\]: Invalid user (?P<user>\S+) from (?P<src_ip>\d+\.\d+\.\d+\.\d+) port (?P<src_port>\d+)")
SSH_FAILED_PW = re.compile(r"sshd\[\d+\]: Failed password for (invalid user )?(?P<user>\S+) from (?P<src_ip>\d+\.\d+\.\d+\.\d+) port (?P<src_port>\d+)")
SSH_CLOSED = re.compile(r"sshd\[\d+\]: Connection closed by (?P<src_ip>\d+\.\d+\.\d+\.\d+) port (?P<src_port>\d+)")
SSH_ACCEPTED = re.compile(r"sshd\[\d+\]: Accepted \S+ for (?P<user>\S+) from (?P<src_ip>\d+\.\d+\.\d+\.\d+) port (?P<src_port>\d+)")

CRON_OPEN = re.compile(r"CRON\[\d+\]: pam_unix\(cron:session\): session opened for user (?P<user>\S+)")
CRON_CLOSE = re.compile(r"CRON\[\d+\]: pam_unix\(cron:session\): session closed for user (?P<user>\S+)")

SUDO = re.compile(r"sudo: (?P<user>\S+) : .*COMMAND=(?P<cmd>.+)$")

SYSTEMD_SESSION_OPEN = re.compile(r"pam_unix\((systemd-user|gdm-launch-environment):session\): session opened for user (?P<user>\S+)")
SYSTEMD_SESSION_CLOSE = re.compile(r"pam_unix\((systemd-user|gdm-launch-environment):session\): session closed for user (?P<user>\S+)")

def _classify_syslog(msg: str) -> dict:
    '''
    Return a normalized (event_type, action, subject, object, src_ip, src_port, user, cmd)
    best-effort extraction.
    '''
    # ssh auth/brute force
    m = SSH_INVALID_USER.search(msg)
    if m:
        return dict(event_type="auth", action="ssh_invalid_user",
                    subject=m.group("src_ip"), object=m.group("user"),
                    src_ip=m.group("src_ip"), src_port=m.group("src_port"),
                    user=m.group("user"), cmd="")
    
    m = SSH_FAILED_PW.search(msg)
    if m:
        return dict(event_type="auth", action="ssh_failed_password",
                    subject=m.group("src_ip"), object=m.group("user"),
                    src_ip=m.group("src_ip"), src_port=m.group("src_port"),
                    user=m.group("user"), cmd="")
    
    m = SSH_ACCEPTED.search(msg)
    if m:
        return dict(event_type="auth", action="ssh_login_success",
                subject=m.group("src_ip"), object=m.group("user"),
                src_ip=m.group("src_ip"), src_port=m.group("src_port"),
                user=m.group("user"), cmd="")

    m = SSH_CLOSED.search(msg)
    if m:
        return dict(event_type="auth", action="ssh_conn_closed",
                    subject=m.group("src_ip"), object="sshd",
                    src_ip=m.group("src_ip"), src_port=m.group("src_port"),
                    user="", cmd="")

    # Cron job
    m = CRON_OPEN.search(msg)
    if m:
        return dict(event_type="execution", action="cron_session_open",
                    subject=m.group("user"), object="cron",
                    src_ip="", src_port="", user=m.group("user"), cmd="")

    m = CRON_CLOSE.search(msg)
    if m:
        return dict(event_type="execution", action="cron_session_close",
                    subject=m.group("user"), object="cron",
                    src_ip="", src_port="", user=m.group("user"), cmd="")

    # sudo 
    m = SUDO.search(msg)
    if m:
        return dict(event_type="privilege", action="sudo_command",
                    subject=m.group("user"), object=m.group("cmd").strip(),
                    src_ip="", src_port="", user=m.group("user"), cmd=m.group("cmd").strip())

    # system sessions (gdm/systemd)
    m = SYSTEMD_SESSION_OPEN.search(msg)
    if m:
        return dict(event_type="session", action="session_open",
                    subject=m.group("user"), object="pam_unix",
                    src_ip="", src_port="", user=m.group("user"), cmd="")

    m = SYSTEMD_SESSION_CLOSE.search(msg)
    if m:
        return dict(event_type="session", action="session_close",
                    subject=m.group("user"), object="pam_unix",
                    src_ip="", src_port="", user=m.group("user"), cmd="")

    # Default fallback
    return dict(event_type="syslog", action="record",
                subject="", object="", src_ip="", src_port="", user="", cmd="")

# -----------------------
# Main Parser
# -----------------------

def parse_syslog_csv(path: str | Path) -> pd.DataFrame:
    '''
    Parse syslog CSV log file.
    '''
    df = _read_csv(path)
    df["ts"] = _parse_ts(df)
    df = df.dropna(subset=["ts"])

    host = _s(df, "Computer", default=_s(df, "HostName", default="unknown"))
    proc = _s(df, "ProcessName", default="")
    pid = _s(df, "ProcessID", default="")
    msg = _s(df, "SyslogMessage", default=_s(df, "Message", default=""))

    # classify row by row
    classified = [ _classify_syslog(m) for m in msg.tolist() ]
    cdf = pd.DataFrame(classified)

    out = pd.DataFrame({
        "ts": df["ts"],
        "host": host,
        "source": "syslog",
        "event_type": cdf["event_type"].astype(str),
        "action": cdf["action"].astype(str),
        "subject": cdf["subject"].astype(str),
        "object": cdf["object"].astype(str),
    })

    # optional structured columns for joining
    out["src_ip"] = cdf["src_ip"].astype(str)
    out["src_port"] = cdf["src_port"].astype(str)
    out["user"] = cdf["user"].astype(str)
    out["cmdline"] = cdf["cmd"].astype(str)

    # keep minimal raw context only
    out["raw"] = _subset_raw(df, [
        "Facility", "SeverityLevel", "ProcessName", "ProcessID", "HostIP", "SyslogMessage"
    ])
    out["process_name"] = proc
    out["pid"] = pid

    return out