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
    

