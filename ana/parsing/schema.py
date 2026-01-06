from dataclasses import dataclass
from typing import Dict, Any, Optional
import pandas as pd


@dataclass
class Event:
    ts: pd.Timestamp
    host: str
    source: str
    event_type: str
    action: str
    subject: str
    object: str
    raw: str
    extra: Dict[str, Any]

    # ---- optional join keys ----
    src_ip: Optional[str] = None
    src_port: Optional[str] = None
    dst_ip: Optional[str] = None
    dst_port: Optional[str] = None
    proto: Optional[str] = None
    uid: Optional[str] = None         # zeek uid
    flow_id: Optional[str] = None     # suricata flow_id
    tx_id: Optional[str] = None       # suricata http tx_id
    user: Optional[str] = None
    pid: Optional[str] = None
    cmdline: Optional[str] = None