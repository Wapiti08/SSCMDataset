import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, Iterable
import pandas as pd
from .utils import _extract_from_eventdata_xml
from .utils import _read_csv, _parse_ts, _safe_col, _to_str, _subset_raw

def _mk_df(
    *,
    ts: pd.Series, host: pd.Series, source: str, event_type: str, action: str,
    subject: pd.Series, obj: pd.Series, pid: Optional[pd.Series] = None,
    proc_guid: Optional[pd.Series] = None, user: Optional[pd.Series] = None,
    dst: Optional[pd.Series] = None, src: Optional[pd.Series] = None,
    extra: Optional[list[dict]] = None,          
    ) -> pd.DataFrame:
    out = pd.DataFrame({
        "ts": ts,
        "host": host,
        "source": source,
        "event_type": event_type,
        "action": action,
        "subject": subject,
        "object": obj,
    })

    if pid is not None:
        out["pid"] = pid
    if proc_guid is not None:
        out["proc_guid"] = proc_guid
    if user is not None:
        out["user"] = user
    if src is not None:
        out["src"] = src
    if dst is not None:
        out["dst"] = dst
    if extra is not None:
        out["raw"] = extra  # keep small subset only
    return out

# -----------------------------
# parsers: conn / process / security
# -----------------------------

def parse_azure_conn(path: str | Path) -> pd.DataFrame:
    df = _read_csv(path)

    ts = _parse_ts(_safe_col(df, "TimeGenerated [UTC]"))
    host = _safe_col(df, "Computer")
    src_ip = _to_str(_safe_col(df, "SourceIp"))
    dst_ip = _to_str(_safe_col(df, "DestinationIp"))
    dst_port = _to_str(_safe_col(df, "DestinationPort"))
    proto = _to_str(_safe_col(df, "Protocol"))

    # subject = source ip; ojbect = dst ip:port/proto
    subject = src_ip
    obj = dst_ip + ":" + dst_port

    extra = _subset_raw(df, [
        "Direction", "ProcessName", "SourceIp", "DestinationIp", "DestinationPort",
        "Protocol", "RemoteIp", "RemoteDnsQuestions", "RemoteDnsCanonicalNames",
        "BytesSent", "BytesReceived", "ConnectionId"
    ])

    return _mk_df(
        ts=ts,
        host=host,
        source="azure_conn",
        event_type="network",
        action="connect",
        subject=subject,
        obj=obj,
        src=src_ip,
        dst=obj + "/" + proto,
        extra=extra,
    )


def parse_azure_process(path: str | Path) -> pd.DataFrame:
    df = _read_csv(path)

    ts = _parse_ts(_safe_col(df, "TimeGenerated [UTC]"))
    host = _safe_col(df, "Computer")

    user = _to_str(_safe_col(df, "UserName"))
    exe = _to_str(_safe_col(df, "ExecutablePath"))
    cmd = _to_str(_safe_col(df, "CommandLine"))

    # Azure VMProcess doesn't always have a PID in this export;
    pid = _to_str(_safe_col(df, "FirstPid", default=""))

    # subject = user, object = exe, raw = cmd
    subject = user
    obj = exe

    extra = _subset_raw(df, [
        "ExecutableName", "DisplayName", "StartTime [UTC]",
        "FirstPid", "ExecutablePath", "CommandLine", "WorkingDirectory",
        "Services", "UserName", "CompanyName", "ProductName", "FileVersion"
    ])

    out = _mk_df(
        ts=ts,
        host=host,
        source="azure_process",
        event_type="process",
        action="start",
        subject=subject,
        obj=obj,
        pid=pid,
        user=user,
        extra=extra,
    )
    out["cmdline"] = cmd
    return out

def parse_azure_security(path: str | Path) -> pd.DataFrame:
    df = _read_csv(path)

    ts = _parse_ts(_safe_col(df, "TimeGenerated [UTC]"))
    host = _safe_col(df, "Computer")
    event_id = _to_str(_safe_col(df, "EventID"))

    # This export is extremely wide; prefer stable columns if present.
    subject_user = _to_str(_safe_col(df, "SubjectUserName", default=""))
    target_user = _to_str(_safe_col(df, "TargetUserName", default=""))
    ip = _to_str(_safe_col(df, "IpAddress", default=_safe_col(df, "ClientIPAddress", default="")))

    # minimal semantics
    subject = subject_user.where(subject_user != "", other=target_user)
    obj = "EventID=" + event_id

    extra = _subset_raw(df, [
        "EventID", "Activity", "SubjectUserName", "TargetUserName",
        "LogonType", "LogonTypeName", "IpAddress", "WorkstationName",
        "ProcessName", "CommandLine"
    ])

    return _mk_df(
        ts=ts,
        host=host,
        source="azure_security",
        event_type="auth",
        action="security_event",
        subject=subject,
        obj=obj,
        src=ip,
        extra=extra,
    )

# -----------------------------
# parsers: events (Sysmon/Security-Auditing/RDP CoreTS)
# -----------------------------

def parse_azure_events(path: str | Path) -> pd.DataFrame:
    """
    Azure 'Event' export that contains multiple channels/sources:
      - Microsoft-Windows-Sysmon (e.g., EventID 3 network connection)
      - Microsoft-Windows-Security-Auditing (e.g., 4624/4625 logon)
      - Microsoft-Windows-RemoteDesktopServices-RdpCoreTS (RDP state)
    We normalize them into a few event_type/action buckets.
    extract join keys from EventData XML for stronger reconstruction.

    """
    df = _read_csv(path)
    ts = _parse_ts(_safe_col(df, "TimeGenerated [UTC]"))
    host = _safe_col(df, "Computer")

    src = _to_str(_safe_col(df, "Source"))
    channel = _to_str(_safe_col(df, "EventLog"))
    event_id = _to_str(_safe_col(df, "EventID"))
    msg = _to_str(_safe_col(df, "RenderedDescription", default=_safe_col(df, "Message", default="")))

    # ---------- parse EventData XML ----------
    ev_xml = _to_str(_safe_col(df, "EventData", default=""))
    ed_list = [_extract_from_eventdata_xml(x) for x in ev_xml.tolist()]
    ed = pd.DataFrame(ed_list)

    def ed_col(name: str) -> pd.Series:
        if name in ed.columns:
            return ed[name].fillna("").astype(str)
        return pd.Series([""] * len(df))

    # sysmon fields
    process_guid = ed_col("ProcessGuid")
    process_id = ed_col("ProcessId")
    image = ed_col("Image")
    user = ed_col("User")
    proto = ed_col("Protocol")
    src_ip = ed_col("SourceIp")
    src_port = ed_col("SourcePort")
    dst_ip = ed_col("DestinationIp")
    dst_port = ed_col("DestinationPort")

    # Security auditing fields (4624/4625)
    ip_addr = ed_col("IpAddress")  
    target_user = ed_col("TargetUserName")
    logon_type = ed_col("LogonType")
    status = ed_col("Status")
    sub_status = ed_col("SubStatus")
    auth_pkg = ed_col("AuthenticationPackageName")

    # RDP core fields
    rdp_ip = ed_col("IPString")                # 140
    rdp_client = ed_col("ClientIP")            # 131 has "ip:port" sometimes

    # ----------- bucket -----------
    event_type = pd.Series(["event"] * len(df))
    action = pd.Series(["record"] * len(df))

    # Heuristics that are safe (bucketing only; not "detection")
    is_sysmon = src.str.contains("Sysmon", case=False, na=False) | channel.str.contains("Sysmon", case=False, na=False)
    is_sec_audit = src.str.contains("Security-Auditing", case=False, na=False) | channel.str.contains("Security", case=False, na=False)
    is_rdp = src.str.contains("RdpCoreTS", case=False, na=False) | channel.str.contains("RdpCoreTS", case=False, na=False)

    # Sysmon EventID 3 is network connection; extremely useful for ingress attempt chains.
    sysmon_net = is_sysmon & (event_id == "3")
    event_type.loc[sysmon_net] = "network"
    action.loc[sysmon_net] = "connect"

    # Security-Auditing: 4624/4625 logon success/fail (classic)
    logon_fail = is_sec_audit & (event_id == "4625")
    logon_succ = is_sec_audit & (event_id == "4624")
    event_type.loc[logon_fail | logon_succ] = "auth"
    action.loc[logon_fail] = "logon_failed"
    action.loc[logon_succ] = "logon_success"

    # RDP core: keep as auth/session-ish (it's session-layer behavior)
    event_type.loc[is_rdp] = "rdp"
    action.loc[is_rdp] = "rdp_event"

    # ---------- subject/object (join-friendly) ----------
    subject = _to_str(_safe_col(df, "UserName", default=""))
    subject = subject.where(subject != "", other=user.where(user != "", other=src))

    obj = "EventID=" + event_id

    # network
    net_subject = (src_ip + ":" + src_port).where(src_ip != "", other="")
    net_object = (dst_ip + ":" + dst_port).where(dst_ip != "", other="")
    subject.loc[sysmon_net] = net_subject.loc[sysmon_net].where(net_subject.loc[sysmon_net] != "", other=subject.loc[sysmon_net])
    obj.loc[sysmon_net] = net_object.loc[sysmon_net].where(net_object.loc[sysmon_net] != "", other=obj.loc[sysmon_net])

    # auth: remote ip -> target user
    remote = ip_addr.where(ip_addr != "", other=rdp_ip.where(rdp_ip != "", other=""))
    subject.loc[logon_fail | logon_succ] = remote.loc[logon_fail | logon_succ].where(remote.loc[logon_fail | logon_succ] != "", other=subject.loc[logon_fail | logon_succ])
    obj.loc[logon_fail | logon_succ] = target_user.loc[logon_fail | logon_succ].where(target_user.loc[logon_fail | logon_succ] != "", other=obj.loc[logon_fail | logon_succ])

    # rdp: prefer IPString / ClientIP
    rdp_remote = rdp_ip.where(rdp_ip != "", other=rdp_client)
    subject.loc[is_rdp] = rdp_remote.loc[is_rdp].where(rdp_remote.loc[is_rdp] != "", other=subject.loc[is_rdp])

    # ---------- extra/raw ----------
    extra = _subset_raw(df, [
        "Source", "EventLog", "EventLevelName", "EventID", "RenderedDescription",
        "UserName", "ParameterXml"
    ])

    out = _mk_df(
        ts = ts,
        host=host,
        source = "azure_events",
        event_type = _to_str(event_type),
        action=_to_str(action),
        subject=subject,
        obj=obj,
        extra=extra,
    )

    out["messages"] = msg
    out["channel"] = channel
    out["provider"] = src
    out["event_id"] = event_id 

    # ---------- expose join keys (critical for reconstruction + RQ2/RQ3) ----------
    out["process_guid"] = process_guid
    out["process_id"] = process_id
    out["image"] = image
    out["user"] = user

    # Normalize remote fields into generic join columns
    out["src_ip"] = src_ip.where(src_ip != "", other=ip_addr.where(ip_addr != "", other=rdp_ip))
    out["src_port"] = src_port
    out["dst_ip"] = dst_ip
    out["dst_port"] = dst_port
    out["proto"] = proto

    out["target_user"] = target_user
    out["logon_type"] = logon_type
    out["status"] = status
    out["sub_status"] = sub_status
    out["auth_pkg"] = auth_pkg

    return out.dropna(subset=["ts"])

# -----------------------------
# parsers: port (VMBoundPort)
# -----------------------------

def parse_azure_port(path: str | Path) -> pd.DataFrame:
    df = _read_csv(path)
    ts = _parse_ts(_safe_col(df, "TimeGenerated [UTC]"))
    host = _safe_col(df, "Computer")

    proc = _to_str(_safe_col(df, "ProcessName"))
    ip = _to_str(_safe_col(df, "Ip"))
    port = _to_str(_safe_col(df, "Port"))
    proto = _to_str(_safe_col(df, "Protocol"))
    wildcard = _to_str(_safe_col(df, "IsWildcardBind"))

    # This is posture/state, not action. Keep distinct.
    subject = proc
    obj = ip + ":" + port + "/" + proto

    extra = _subset_raw(df, [
        "ProcessName", "Ip", "Port", "Protocol", "IsWildcardBind",
        "BytesSent", "BytesReceived", "LinksEstablished"
    ])

    out = _mk_df(
        ts=ts,
        host=host,
        source="azure_port",
        event_type="posture",
        action="listen",
        subject=subject,
        obj=obj,
        extra=extra,
    )
    out["is_wildcard"] = wildcard
    return out


# -----------------------------
# parsers: perf (Perf counters)
# -----------------------------

def parse_azure_perf(path: str | Path) -> pd.DataFrame:
    """
    Perf is context. Keep it, but mark event_type=context so you can exclude it from reconstruction by default.
    """
    df = _read_csv(path)
    ts = _parse_ts(_safe_col(df, "TimeGenerated [UTC]"))
    host = _safe_col(df, "Computer")

    obj_name = _to_str(_safe_col(df, "ObjectName"))
    counter = _to_str(_safe_col(df, "CounterName"))
    inst = _to_str(_safe_col(df, "InstanceName"))
    val = _to_str(_safe_col(df, "CounterValue"))

    subject = obj_name
    obj = counter + (("[" + inst + "]") if (inst != "").any() else "")

    extra = _subset_raw(df, [
        "ObjectName", "CounterName", "InstanceName", "CounterValue",
        "Min", "Max", "SampleCount", "StandardDeviation"
    ])

    out = _mk_df(
        ts=ts,
        host=host,
        source="azure_perf",
        event_type="context",
        action="perf_sample",
        subject=subject,
        obj=obj,
        extra=extra,
    )
    out["value"] = val
    return out

