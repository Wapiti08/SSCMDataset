from pathlib import Path
from typing import Dict, Iterable, Optional
import pandas as pd
from zat.log_to_dataframe import LogToDataFrame
from .utils import _s, _subset_raw, _load_zeek_log

_parser = LogToDataFrame()

def _mk_network_base(df: pd.DataFrame) -> Dict[str, pd.Series]:
    # strandard 5-tuple fields if present
    src_ip = _s(df, "id.orig_h")
    src_port = _s(df, "id.orig_p")
    dst_ip = _s(df, "id.resp_h")
    dst_port = _s(df, "id.resp_p")
    proto = _s(df, "proto", default=_s(df, "transport_proto", default=""))
    uid = _s(df, "uid", default="")
    return dict(src_ip=src_ip, src_port=src_port, dst_ip=dst_ip, dst_port=dst_port, proto=proto, uid=uid)

def _standard_out(
    *,
    df: pd.DataFrame,
    source: str,
    event_type: str,
    action: str | pd.Series,
    subject: pd.Series,
    obj: pd.Series,
    host: str="network_sensor",
    extra_keep: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    out = pd.DataFrame({
        "ts": df["ts"],
        "host": host,
        "source": source,
        "event_type": event_type,
        "action": action if isinstance(action, pd.Series) else pd.Series([action] * len(df)),
        "subject": subject,
        "object": obj,
    })

    # attach normalized network tuple when available
    base = _mk_network_base(df)
    for k, v in base.items():
        out[k] = v

    if extra_keep is not None:
        out["raw"] = _subset_raw(df, extra_keep)
    else:
        out["raw"] = [{} for _ in range(len(df))]

    return out

# -----------------------
# different Zeek log parsers
# -----------------------

def parse_conn_log(path: str | Path) -> pd.DataFrame:
    ''' 
    Zeek conn.log: baseline network connectivity.
    Used for chain skeleton + join keys (uid / 5-tuple).    
    '''
    df = _load_zeek_log(path)
    base = _mk_network_base(df)

    subject = base["src_ip"] + ":" + base["src_port"]
    obj = base["dst_ip"] + ":" + base["dst_port"]

    return _standard_out(
        df=df,
        source="zeek",
        event_type="network",
        action="connect",
        subject=subject,
        obj=obj,
        extra_keep=[
            "uid", "proto", "service", "duration",
            "orig_bytes", "resp_bytes", "conn_state", "history"
        ],
    )


def parse_dns_log(path: str | Path) -> pd.DataFrame:
    ''' 
        dns.log: domain-level resolution (beacon/staging).

    '''
    df = _load_zeek_log(path)
    base = _mk_network_base(df)

    query = _s(df, "query")
    qtype = _s(df, "qtype_name")
    answers = _s(df, "answers", default=_s(df, "answers[0]", default=""))

    subject = base["src_ip"] + ":" + base["src_port"]
    obj = query

    out = _standard_out(
        df = df,
        source="zeek",
        event_type="dns",
        action="query",
        subject=subject,
        obj=obj,
        extra_keep=["uid", "query", "qtype_name", "rcode_name", "answers", "TTLs"],
    )

    out["dns_qtype"] = qtype
    out["dns_answers"] = answers
    return out

def parse_http_log(path: str | Path) -> pd.DataFrame:
    ''' 
    http.log: HTTP requests; useful for download/exfil pivots.

    '''
    df = _load_zeek_log(path)
    base = _mk_network_base(df)

    method = _s(df, "method")
    host = _s(df, "host")
    uri = _s(df, "uri") 

    # include delimiter to avoid ambiguity
    obj = host + uri

    subject = base["src_ip"].astype(str) + ":" + base["src_port"].astype(str)
    out = _standard_out(
        df=df,
        source="zeek",
        event_type="http",
        action=method,
        subject=subject,
        obj=obj,
        extra_keep=["uid", "method", "host", "uri", "status_code", "user_agent", "referrer"],
    )

    out["http_host"] = host
    out["http_uri"] = uri
    out["http_status"] = _s(df, "status_code")
    out["user_agent"] = _s(df, "user_agent")
    return out


def parse_ssl_log(path: str | Path) -> pd.DataFrame:
    ''' TLS / SNI / JA3 fingerprinting
        - server_name (SNI) if present
      - version/cipher/curve
      - cert_chain_fps (certificate chain fingerprints)
      - established/resumed/validation_status/ssl_history
    Strong join keys:
      - uid (join to conn/http/files/dns)
      - 5-tuple
    '''
    df = _load_zeek_log(path)
    base = _mk_network_base(df)

    sni = _s(df, "server_name")
    subject = base["src_ip"] + ":" + base["src_port"]
    obj = sni

    out = _standard_out(
        df=df,
        source="zeek",
        event_type="tls",
        action="handshake",
        subject=subject,
        obj=obj,
        extra_keep=["uid", "server_name", "version", "cipher", "ja3", "ja3s", "resumed"],
    )

    return out

def parse_files_log(path: str | Path) -> pd.DataFrame:
    ''' 
    files.log: file transfers observed by Zeek analyzers (HTTP/FTP/SMB, etc.)
    '''
    df = _load_zeek_log(path)
    base = _mk_network_base(df)

    fuid = _s(df, "fuid", default="")
    mime = _s(df, "mime_type", default="")
    fname = _s(df, "filename", default="")

    # object: filename if meaningful, else use fuid anchor
    fname_ok = (fname != "") & (fname != "-") & (fname != "(empty)")
    obj = fname.where(fname_ok, other=("fuid:" + fuid))

    subject = base["src_ip"].astype(str) + ":" + base["src_port"].astype(str)

    out = _standard_out(
        df=df,
        source="zeek",
        event_type="file",
        action="transfer",
        subject=subject.astype(str),
        obj=obj.astype(str),
        extra_keep=[
            # join
            "uid", "fuid", "id.orig_h", "id.orig_p", "id.resp_h", "id.resp_p",
            # pivots
            "source", "analyzers", "mime_type", "filename",
            "seen_bytes", "total_bytes",
            # hashes (if present)
            "md5", "sha1", "sha256",
            # extraction markers
            "extracted", "extracted_cutoff", "extracted_size",
            "parent_fuid",
        ],
    )

    # Promote a few pivots to top-level (makes analysis easier without scanning raw dicts)
    out["fuid"] = fuid.astype(str)
    out["mime_type"] = mime.astype(str)
    out["file_name"] = fname.astype(str)
    out["app_proto"] = _s(df, "source", default="").astype(str)  # HTTP/FTP/SMB analyzer source

    # Optional sizes (string safe; your schema has '-' sometimes)
    out["seen_bytes"] = _s(df, "seen_bytes", default="").astype(str)
    out["total_bytes"] = _s(df, "total_bytes", default="").astype(str)

    return out.dropna(subset=["ts"])

def parse_ssh_log(path: str | Path) -> pd.DataFrame:
    '''
    
    '''
    df = _load_zeek_log(path)
    base = _mk_network_base(df)

    # common-ish fields (may be absent)
    user = _s(df, "user", default=_s(df, "username", default=""))
    auth_success = _s(df, "auth_success", default=_s(df, "success", default=""))
    client = _s(df, "client", default="")
    server = _s(df, "server", default="")
    direction = _s(df, "direction", default="")

    # action inference (best-effort, not "detection")
    # auth_success could be T/F, true/false, 1/0, or "-" (string)
    as_norm = auth_success.astype(str).str.lower()
    is_true = as_norm.isin(["t", "true", "1", "yes"])
    is_false = as_norm.isin(["f", "false", "0", "no"])

    action = pd.Series(["ssh_session"] * len(df))
    action.loc[is_true] = "ssh_login_success"
    action.loc[is_false] = "ssh_login_fail"

    subject = base["src_ip"].astype(str) + ":" + base["src_port"].astype(str)

    # object: dst + user if available
    dst = base["dst_ip"].astype(str) + ":" + base["dst_port"].astype(str)
    user_ok = (user != "") & (user != "-") & (user != "(empty)")
    obj = (dst + " user=" + user).where(user_ok, other=dst)

    out = _standard_out(
        df=df,
        source="zeek",
        event_type="auth",
        action=action.astype(str),
        subject=subject.astype(str),
        obj=obj.astype(str),
        extra_keep=[
            "uid", "id.orig_h", "id.orig_p", "id.resp_h", "id.resp_p", "proto",
            "user", "username",
            "auth_success", "success",
            "client", "server", "direction",
            "cipher_alg", "mac_alg", "compression_alg", "kex_alg", "host_key_alg",
        ],
    )

    # promote pivots
    out["user"] = user.astype(str)
    out["auth_success"] = auth_success.astype(str)
    out["ssh_client"] = client.astype(str)
    out["ssh_server"] = server.astype(str)
    out["direction"] = direction.astype(str)

    return out.dropna(subset=["ts"])


if __name__ == "__main__":
    # quick test
    # python3 -m parsing.zeek
    data_path = Path.cwd().parent.joinpath("data", "sc4")
    conn_df = parse_conn_log(data_path.joinpath("conn.log"))
    print(conn_df.head())

    dns_df = parse_dns_log(data_path.joinpath("dns.log"))
    print(dns_df.head())

    http_df = parse_http_log(data_path.joinpath("http.log"))
    print(http_df.head())

    ssl_df = parse_ssl_log(data_path.joinpath("ssl.log"))
    print(ssl_df.head())

    files_df = parse_files_log(data_path.joinpath("files.log"))
    print(files_df.head())

    ssh_df = parse_ssh_log(data_path.joinpath("ssh.log"))
    print(ssh_df.head())

