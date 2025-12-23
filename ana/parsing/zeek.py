from zat.log_to_dataframe import LogToDataFrame
import pandas as pd
from pathlib import Path
from typing import List

_parser = LogToDataFrame()

def _load_zeek_log(path: str | Path) -> pd.DataFrame:
    df = _parser.create_dataframe(str(path))
    df['ts'] = pd.to_datetime(df['ts'], unit='s', utc=True)
    return df.drop(subset=["ts"])

def parse_conn_log(path: str | Path) -> pd.DataFrame:
    ''' network connection and lateral movement events from Zeek conn.log
    
    '''
    df = _load_zeek_log(path)

    out = pd.DataFrame({
        "ts": df["ts"],
        "host": "network_sensor",
        "source": "zeek",
        "event_type": "network",
        "action": "connect",
        "subject": df["id.orig_h"].astype(str) + ":" + df["id.orig_p"].astype(str),
        "object": df["id.resp_h"].astype(str) + ":" + df["id.resp_p"].astype(str),
        "raw": "",
    })

    out["extra"] = df.to_dict(orient="records")
    return out

def parse_dns_log(path: str | Path) -> pd.DataFrame:
    ''' beacon/staging at domain level
    
    '''
    df = _load_zeek_log(path)

    out = pd.DataFrame({
        "ts": df["ts"],
        "host": "network_sensor",
        "source": "zeek",
        "event_type": "dns",
        "action": "query",
        "subject": df["id.orig_h"].astype(str),
        "object": df["query"].astype(str),
        "raw": "",
    })
    out["extra"] = df.to_dict(orient="records")
    return out

def parse_http_log(path: str | Path) -> pd.DataFrame:
    ''' payload download and exfiltration via HTTP(S)
    
    '''
    df = _load_zeek_log(path)

    out = pd.DataFrame({
        "ts": df["ts"],
        "host": "network_sensor",
        "source": "zeek",
        "event_type": "http",
        "action": df["method"].astype(str),
        "subject": df["id.orig_h"].astype(str),
        "object": (
            df["host"].astype(str)
            + df["uri"].astype(str)
        ),
        "raw": df.get("user_agent", "").astype(str),
    })
    out["extra"] = df.to_dict(orient="records")
    return out

def parse_ssl_log(path: str | Path) -> pd.DataFrame:
    ''' TLS / C2 fingerprinting
    
    '''
    df = _load_zeek_log(path)

    out = pd.DataFrame({
        "ts": df["ts"],
        "host": "network_sensor",
        "source": "zeek",
        "event_type": "tls",
        "action": "handshake",
        "subject": df["id.orig_h"].astype(str),
        "object": df["server_name"].astype(str),
        "raw": df.get("ja3", "").astype(str),
    })
    out["extra"] = df.to_dict(orient="records")
    return out

def parse_files_log(path: str | Path) -> pd.DataFrame:
    ''' payload download / stage drop / exfil artifact
    
    '''
    df = _load_zeek_log(path)

    out = pd.DataFrame({
        "ts": df["ts"],
        "host": "network_sensor",
        "source": "zeek",
        "event_type": "file",
        "action": "transfer",
        "subject": df["tx_hosts"].astype(str),
        "object": df["filename"].astype(str),
        "raw": df.get("mime_type", "").astype(str),
        "proto": df.get("source", "").astype(str),   # HTTP/FTP/etc
    })
    out["extra"] = df.to_dict(orient="records")
    return out.dropna(subset=["ts"])

def parse_ssh_log(path: str | Path) -> pd.DataFrame:
    '''
    
    '''
    df = _load_zeek_log(path)

    out = pd.DataFrame({
        "ts": df["ts"],
        "host": "network_sensor",
        "source": "zeek",
        "event_type": "auth",
        "action": "ssh_login",
        "subject": df["id.orig_h"].astype(str),
        "object": (
            df["id.resp_h"].astype(str)
            + ":" + df["user"].astype(str)
        ),
        "raw": df.get("auth_success", "").astype(str),
    })
    out["extra"] = df.to_dict(orient="records")
    return out.dropna(subset=["ts"])
