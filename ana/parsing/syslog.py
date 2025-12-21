import pandas as pd

def parse_syslog_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    ts_col = "EventTime [UTC]" if "EventTime [UTC]" in df.columns else "TimeGenerated [UTC]"
    df["ts"] = pd.to_datetime(df[ts_col], errors="coerce", utc=True)

    out = pd.DataFrame({
        "ts": df["ts"],
        "host": df.get("Computer", "unknown"),
        "source": "syslog",
        "event_type": df.get("Facility", "").astype(str),
        "action": df.get("ProcessName", "").astype(str),
        "subject": df.get("ProcessID", "").astype(str),
        "object": df.get("HostIP", "").astype(str),
        "raw": df.get("SyslogMessage", "").astype(str),
    })
    out["extra"] = df.to_dict(orient="records")
    return out.dropna(subset=["ts"])