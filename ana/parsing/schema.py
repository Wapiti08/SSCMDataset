from dataclasses import dataclass
from typing import Dict, Any
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