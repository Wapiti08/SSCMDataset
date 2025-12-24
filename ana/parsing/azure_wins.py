import pandas as pd

def parse_azure_conn(path):
    df = pd.read_csv(path)

    return pd.DataFrame({
        "ts": pd.to_datetime(df["TimeGenerated [UTC]"], utc=True),
        "host": df["Computer"],
        "source": "azure_conn",
        "event_type": "network",
        "action": "connect",
        "subject": df["SourceIp"],
        "object": df["DestinationIp"].astype(str) + ":" + df["DestinationPort"].astype(str),
        "raw": df.to_dict(orient="records"),
        "extra": df.to_dict(orient="records"),
    })

def parse_azure_process(path):
    df = pd.read_csv(path)

    return pd.DataFrame({
        "ts": pd.to_datetime(df["TimeGenerated [UTC]"], utc=True),
        "host": df["Computer"],
        "source": "azure_process",
        "event_type": "process",
        "action": "start",
        "subject": df["UserName"],
        "object": df["ExecutablePath"],
        "raw": df["CommandLine"],
        "extra": df.to_dict(orient="records"),
    })

def parse_azure_security(path):
    df = pd.read_csv(path)
    return pd.DataFrame({
        "ts": pd.to_datetime(df["TimeGenerated [UTC]"], utc=True),
        "host": df["Computer"],
        "source": "azure_security",
        "event_type": "auth",
        "action": "security_event",
        "subject": df.get("SubjectUserName", ""),
        "object": df.get("TargetUserName", ""),
        "raw": df["EventID"].astype(str),
        "extra": df.to_dict(orient="records"),
    })
