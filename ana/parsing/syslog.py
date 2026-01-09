from pathlib import Path
from typing import Iterable
import re
import pandas as pd
from dataclasses import dataclass
from .utils import _read_csv, _s, _parse_ts, _subset_raw

# -----------------------
# Helpers
# -----------------------

def _na_empty(s: pd.Series) -> pd.Series:
    return s.replace(r"^\s*$", pd.NA, regex=True)

def _parse_ts(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip().str.replace(",", "", regex=False)
    return pd.to_datetime(s, utc=True, dayfirst=True, errors="coerce")

def _s(df: pd.DataFrame, col: str, default=None) -> pd.Series:
    if col in df.columns:
        return df[col]
    if default is None:
        return pd.Series([pd.NA] * len(df))
    if isinstance(default, pd.Series):
        return default
    return pd.Series([default] * len(df))

# -----------------------
# Rule engine
# -----------------------

@dataclass(frozen=True)
class Rule:
    name: str
    event_type: str
    action: str
    pattern: re.Pattern
    procs: tuple[str, ...] = ()  

_SSH_PREFIX = r"(?:sshd\[\d+\]:\s*)?"
_CRON_PREFIX = r"(?:CRON\[\d+\]:\s*)?"
_SUDO_PREFIX = r"(?:sudo:\s*)?"

RULES: list[Rule] = [
    Rule(
        name="ssh_invalid_user",
        event_type="auth",
        action="ssh_invalid_user",
        procs=("sshd",),
        pattern=re.compile(
            rf"{_SSH_PREFIX}Invalid user (?P<user>\S+) from (?P<src_ip>\d+\.\d+\.\d+\.\d+) port (?P<src_port>\d+)"
        ),
    ),
    Rule(
        name="ssh_failed_password",
        event_type="auth",
        action="ssh_failed_password",
        procs=("sshd",),
        pattern=re.compile(
            rf"{_SSH_PREFIX}Failed password for (?:invalid user )?(?P<user>\S+) from (?P<src_ip>\d+\.\d+\.\d+\.\d+) port (?P<src_port>\d+)"
        ),
    ),
    Rule(
        name="ssh_login_success",
        event_type="auth",
        action="ssh_login_success",
        procs=("sshd",),
        pattern=re.compile(
            rf"{_SSH_PREFIX}Accepted \S+ for (?P<user>\S+) from (?P<src_ip>\d+\.\d+\.\d+\.\d+) port (?P<src_port>\d+)"
        ),
    ),
    Rule(
        name="ssh_conn_closed",
        event_type="auth",
        action="ssh_conn_closed",
        procs=("sshd",),
        pattern=re.compile(
            rf"{_SSH_PREFIX}Connection closed by (?P<src_ip>\d+\.\d+\.\d+\.\d+) port (?P<src_port>\d+)"
        ),
    ),

    Rule(
        name="cron_cmd",
        event_type="execution",
        action="cron_cmd",
        procs=("CRON", "cron", "crontab"),
        pattern=re.compile(rf"{_CRON_PREFIX}\((?P<user>[^)]+)\)\s+CMD\s+\((?P<cmdline>.*)\)\s*$"),
    ),
    Rule(
        name="cron_activity",
        event_type="execution",
        action="cron_activity",
        procs=("CRON", "cron", "crontab"),
        pattern=re.compile(rf"{_CRON_PREFIX}\((?P<user>[^)]+)\)\s+(?P<cmdline>.+)\s*$"),
    ),
    Rule(
        name="cron_session_open",
        event_type="execution",
        action="cron_session_open",
        procs=("CRON", "cron"),
        pattern=re.compile(
            rf"{_CRON_PREFIX}pam_unix\(cron:session\): session opened for user (?P<user>\S+)"
        ),
    ),
    Rule(
        name="cron_session_close",
        event_type="execution",
        action="cron_session_close",
        procs=("CRON", "cron"),
        pattern=re.compile(
            rf"{_CRON_PREFIX}pam_unix\(cron:session\): session closed for user (?P<user>\S+)"
        ),
    ),

    # sudo
    Rule(
        name="sudo_command",
        event_type="privilege",
        action="sudo_command",
        procs=("sudo",),
        pattern=re.compile(rf"{_SUDO_PREFIX}(?P<user>\S+)\s*:\s.*\bCOMMAND=(?P<cmdline>.+)$"),
    ),

    # system sessions
    Rule(
        name="session_open",
        event_type="session",
        action="session_open",
        procs=("gdm", "systemd", "systemd-logind"),
        pattern=re.compile(
            r"pam_unix\((systemd-user|gdm-launch-environment):session\): session opened for user (?P<user>\S+)"
        ),
    ),
    Rule(
        name="session_close",
        event_type="session",
        action="session_close",
        procs=("gdm", "systemd", "systemd-logind"),
        pattern=re.compile(
            r"pam_unix\((systemd-user|gdm-launch-environment):session\): session closed for user (?P<user>\S+)"
        ),
    ),
]


def classify_syslog_df(proc: pd.Series, msg: pd.Series) -> pd.DataFrame:
    """
    vectorized syslog message classification.
    """
    n = len(msg)
    out = pd.DataFrame({
        "event_type": pd.Series(["syslog"] * n, dtype="string"),
        "action": pd.Series(["record"] * n, dtype="string"),
        "user": pd.Series([pd.NA] * n, dtype="string"),
        "src_ip": pd.Series([pd.NA] * n, dtype="string"),
        "src_port": pd.Series([pd.NA] * n, dtype="Int64"),
        "cmdline": pd.Series([pd.NA] * n, dtype="string"),
    })

    proc_s = proc.astype("string").fillna("")
    msg_s = msg.astype("string").fillna("")

    for rule in RULES:
        base_mask = out["action"].eq("record")

        if rule.procs:
            pset = set(rule.procs)
            base_mask &= proc_s.isin(pset)

        if not base_mask.any():
            continue

        extracted = msg_s[base_mask].str.extract(rule.pattern)
        matched = extracted.notna().any(axis=1)
        if not matched.any():
            continue

        idx = extracted.index[matched]
        out.loc[idx, "event_type"] = rule.event_type
        out.loc[idx, "action"] = rule.action

        for col in ["user", "src_ip", "src_port", "cmdline"]:
            if col in extracted.columns:
                if col == "src_port":
                    out.loc[idx, col] = pd.to_numeric(extracted.loc[idx, col], errors="coerce").astype("Int64")
                else:
                    out.loc[idx, col] = extracted.loc[idx, col].astype("string")

    return out


# -----------------------
# Main parser
# -----------------------

def parse_syslog_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["ts"] = _parse_ts(_s(df, "TimeGenerated [UTC]"))
    df = df.dropna(subset=["ts"]).reset_index(drop=True)

    host = _s(df, "HostName", default=_s(df, "Computer", default=pd.NA)).astype("string")
    proc = _s(df, "ProcessName", default=pd.NA).astype("string")
    pid = pd.to_numeric(_s(df, "ProcessID", default=pd.NA), errors="coerce").astype("Int64")
    msg = _s(df, "SyslogMessage", default=_s(df, "Message", default=pd.NA)).astype("string")

    cdf = classify_syslog_df(proc, msg)

    # subject/object：
    subject = pd.Series([pd.NA] * len(df), dtype="string")
    obj = pd.Series([pd.NA] * len(df), dtype="string")

    # ssh：subject=src_ip, object=user or sshd
    ssh_mask = cdf["action"].str.startswith("ssh_", na=False)
    subject[ssh_mask] = cdf.loc[ssh_mask, "src_ip"]
    obj[ssh_mask] = cdf.loc[ssh_mask, "user"].fillna("sshd")

    # cron：subject=user, object=cron
    cron_mask = cdf["action"].str.startswith("cron_", na=False)
    subject[cron_mask] = cdf.loc[cron_mask, "user"]
    obj[cron_mask] = "cron"

    # sudo：subject=user, object=cmdline
    sudo_mask = cdf["action"].eq("sudo_command")
    subject[sudo_mask] = cdf.loc[sudo_mask, "user"]
    obj[sudo_mask] = cdf.loc[sudo_mask, "cmdline"]

    # session：subject=user, object=pam_unix
    sess_mask = cdf["event_type"].eq("session")
    subject[sess_mask] = cdf.loc[sess_mask, "user"]
    obj[sess_mask] = "pam_unix"

    fallback = subject.isna()
    subject[fallback] = ("pid=" + pid.astype("string") + " proc=" + proc.fillna("")).astype("string")

    out = pd.DataFrame({
        "ts": df["ts"],
        "host": _na_empty(host),
        "source": "syslog",
        "event_type": cdf["event_type"],
        "action": cdf["action"],
        "subject": _na_empty(subject),
        "object": _na_empty(obj),
        "src_ip": _na_empty(cdf["src_ip"]),
        "src_port": cdf["src_port"],
        "user": _na_empty(cdf["user"]),
        "cmdline": _na_empty(cdf["cmdline"]),
        "raw": msg, 
        "process_name": proc,
        "pid": pid,
    })

    return out


if __name__ == "__main__":
    # for quick testing
    # python3 -m parsing.syslog
    data_path = Path.cwd().parent.joinpath("data", "sc4")
    
    # test suricata eve.json
    sys_df = parse_syslog_csv(data_path.joinpath("syslog.csv"))
    print(sys_df.head())
    print(sys_df.columns)
    print(sys_df["subject"].value_counts(dropna=False))
    print(sys_df["object"].value_counts(dropna=False))
    print(sys_df["src_ip"].value_counts(dropna=False))
    print(sys_df["src_port"].value_counts(dropna=False))
    print(sys_df["user"].value_counts(dropna=False))
    print(sys_df["cmdline"].value_counts(dropna=False))

