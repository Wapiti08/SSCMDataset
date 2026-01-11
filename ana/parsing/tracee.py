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
        
