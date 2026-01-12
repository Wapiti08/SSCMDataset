'''
 # @ Create Time: 2026-01-09 16:54:18
 # @ Modified time: 2026-01-09 16:56:18
 # @ Description: parsing tracee logs for ana module
 '''


from pathlib import Path
from typing import Any, Dict, Iterable, Tuple
from dataclasses import dataclass
import json
import pandas as pd
from .utils import _safe_str, _to_ts, _subset_raw

def is_tracee_event(obj: Dict[str, Any]) -> bool:
    return "timestamp" in obj and "eventName" in obj

def _args_to_dict(args: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if not isinstance(args, list):
        return out
    for a in args:
        if isinstance(a, dict) and "name" in a:
            out[a["name"]] = a.get("value")
    return out

def _sockaddr_to_str(v: Any) -> str:
    ''' 
    Convert a sockaddr structure to a human-readable string.
    format of tracee on sockaddr:
            {"sa_family":"AF_UNIX","sun_path":"/run/systemd/private"}
            {"sa_family":"AF_INET","sin_addr":"1.2.3.4","sin_port":"80"}
    '''
    if not isinstance(v, dict):
        return ""
    
    fam = v.get("sa_family", "")
    if fam == "AF_UNIX":
        return _safe_str(v.get("sun_path", ""))
    if fam == "AF_INET":
        ip = _safe_str(v.get("sin_addr", ""))
        port = _safe_str(v.get("sin_port", ""))
        if ip and port:
            return f"{ip}:{port}"
        return ip
    return ""

def _mk_subject_object(e: dict, argsd: dict) -> Tuple[str, str]:
    ''' convert subject/object to universal pivot
    - network: object = dst: port
    - file: object = pathname
    - socket: object = remote unix path
    - exec: object = argv or cmdpath/pathname
    - default: subject = pid/proc
    
    '''
    pid = _safe_str(e.get("processId", ""))
    proc = _safe_str(e.get("processName", ""))
    subject = f"pid={pid} proc={proc}".strip()

    ev = _safe_str(e.get("eventName", "'"))
    syscall = _safe_str(e.get("syscall", ""))

    # network (tracee net_tcp_connect)
    dst = _safe_str(argsd.get("dst", ""))
    dst_port = _safe_str(argsd.get("dst_port", ""))
    if dst or dst_port:
        obj = f"{dst}:{dst_port}".rstrip(":")
        return subject, obj
    
    # socket connect/bind (security_socket_connect / security_socket_bind)
    raddr = _sockaddr_to_str(argsd.get("remote_addr"))
    if raddr:
        return subject, raddr
    laddr = _sockaddr_to_str(argsd.get("local_addr"))
    if laddr:
        return subject, laddr
    
    # filesystem (unlink, open, rename...)
    pathname = _safe_str(argsd.get("pathname", ""))
    if pathname:
        return subject, pathname
    
    # exec (sched_process_exec / execve)
    argv = argsd.get("argv")
    # form string from a list-like command execution
    if isinstance(argv, list) and argv:
        return subject, " ".join([_safe_str(x) for x in argv if _safe_str(x)])
    
    cmdpath = _safe_str(argsd.get("cmdpath",""))
    if cmdpath:
        return subject, cmdpath
    
    # fallback to eventName/syscall
    fallback_obj = ev or syscall
    return subject, fallback_obj

# -------------------------------------
# main parsing function
# -------------------------------------
def parse_tracee_ndjson(path: str | Path) -> pd.DataFrame:
    '''
    Parse Tracee NDJSON (json-lines) to dataframe
        - process pivots: pid/ppid/tid/uid/proc/argv/pwd
        - container pivots: containerId/cgroupId/pid_ns/mountNamespace
        - event pivots: eventName/eventId/syscall/returnValue
        - resource pivots:
          fs: pathname
          net: dst/dst_port (and dst_dns if present)
          socket: remote_addr/local_addr (unix path or ip:port string)
        - detection pivots: signatureName/signatureID/ATT&CK external_id if present in metadata

    '''

    rows = []
    path = Path(path)

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue

            if not is_tracee_event(e):
                continue    

            ts = _to_ts(e.get("timestamp"))
            if pd.isna(ts):
                continue    

            argsd = _args_to_dict(e.get("args"))
            subject, obj = _mk_subject_object(e, argsd)

            evname = _safe_str(e.get("eventName", ""))
            syscall = _safe_str(e.get("syscall", ""))
            action = syscall or evname or "record"

            # extract from args
            argv = argsd.get("argv", [])
            cmdline = ""
            if isinstance(argv, list) and argv:
                cmdline = " ".join([_safe_str(x) for x in argv if _safe_str(x)])
            
            pathname = _safe_str(argsd.get("pathname", ""))
            pwd = _safe_str(argsd.get("pwd", ""))
            dst = _safe_str(argsd.get("dst", ""))
            dst_port = _safe_str(argsd.get("dst_port", ""))
            dst_dns = argsd.get("dst_dns") if isinstance(argsd.get("dst_dns"), list) else []

            remote_addr = _sockaddr_to_str(argsd.get("remote_addr"))
            local_addr = _sockaddr_to_str(argsd.get("local_addr"))

            # detection / signature / ATT&CK
            md = e.get("metadata") if isinstance(e.get("metadata"), dict) else {}
            props = (md.get("Properties") if isinstance(md, dict) else {}) or {}
            if not isinstance(props, dict):
                props = {}
            
            base = {
                "ts": ts,
                "host": _safe_str(e.get("hostName", "")),
                "source": "tracee",

                # keep native eventName
                "event_type": evname if evname else "tracee",
                "action": action,

                "subject": _safe_str(subject),
                "object": _safe_str(obj),

                # process pivots
                "process_name": _safe_str(e.get("processName", "")),
                "pid": _safe_str(e.get("processId", "")),
                "ppid": _safe_str(e.get("parentProcessId", "")),
                "tid": _safe_str(e.get("threadId", "")),
                "uid": _safe_str(e.get("userId", "")),

                # container pivots
                "container_id": _safe_str(e.get("containerId", "")),
                "cgroup_id": _safe_str(e.get("cgroupId", "")),
                "pid_ns": _safe_str(e.get("pid_ns", "")),
                "mnt_ns": _safe_str(e.get("mountNamespace", "")),

                # event pivots
                "event_id": _safe_str(e.get("eventId", "")),
                "syscall": syscall,
                "return_value": _safe_str(e.get("returnValue", "")),

                # resource pivots
                "pathname": pathname,
                "pwd": pwd,
                "cmdline": _safe_str(cmdline),

                "dst_ip": dst,
                "dst_port": _safe_str(dst_port),
                "dst_dns": ",".join([_safe_str(x) for x in dst_dns if _safe_str(x)]),

                "remote_addr": _safe_str(remote_addr),
                "local_addr": _safe_str(local_addr),

                # detection pivots
                "signature_id": _safe_str(props.get("signatureID", "")),
                "signature_name": _safe_str(props.get("signatureName", "")),
                "attack_external_id": _safe_str(props.get("external_id", "")),
                "attack_technique": _safe_str(props.get("Technique", "")),
                "alert_category": _safe_str(props.get("Category", "")),
                "alert_severity": _safe_str(props.get("Severity", "")),
            }

            # small raw (avoid huge)
            raw_small = _subset_raw(e, [
                "timestamp", "eventName", "eventId", "syscall", "returnValue",
                "processId", "parentProcessId", "threadId", "userId", "processName",
                "hostName", "containerId", "cgroupId", "pid_ns", "mountNamespace",
            ])

            raw_small["args"] = _subset_raw(argsd, [
                "cmdpath", "pathname", "pwd", "argv",
                "dst", "dst_port", "dst_dns",
                "remote_addr", "local_addr",
            ])
            if md:
                raw_small["metadata"] = _subset_raw(md, ["Version", "Description", "Properties"])

            base["raw"] = json.dumps(raw_small, ensure_ascii=False)

            rows.append(base)

    return pd.DataFrame(rows)

if __name__ == "__main__":
    # for quick testing
    # python3 -m parsing.syslog
    data_path = Path.cwd().parent.joinpath("data", "sc7")
    
    # test suricata eve.json
    sys_df = parse_tracee_ndjson(data_path.joinpath("tracee-events.json"))
    print(sys_df.head())
    print(sys_df.columns)
    print(sys_df["ts"].value_counts(dropna=False))
    print(sys_df["host"].value_counts(dropna=False))
    print(sys_df["source"].value_counts(dropna=False))
    print(sys_df["subject"].value_counts(dropna=False))
    print(sys_df["object"].value_counts(dropna=False))
    print(sys_df["attack_external_id"].value_counts(dropna=False))
    print(sys_df["attack_technique"].value_counts(dropna=False))
    print(sys_df["alert_category"].value_counts(dropna=False))
    print(sys_df["alert_severity"].value_counts(dropna=False))
    print(sys_df["pid_ns"].value_counts(dropna=False))

