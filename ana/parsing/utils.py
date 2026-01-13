'''
 # @ Create Time: 2026-01-06 12:02:09
 # @ Modified time: 2026-01-06 12:02:11
 # @ Description: support functions for parsing modules like XML format data
 '''

from pathlib import Path
from typing import Optional, Dict, Any, Iterable
import pandas as pd
import xml.etree.ElementTree as ET
from zat.log_to_dataframe import LogToDataFrame

_parser = LogToDataFrame()
# -------------------------------
# helper functions for azure logs
# -------------------------------

def _read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)

def _parse_ts(series: pd.Series) -> pd.Series:
    # Azure exports usually: "22/04/2025, 13:03:00.020" or "10/12/2025, 15:19:20.067"
    # dayfirst=True is safer for these exports.
    return pd.to_datetime(series, utc=True, dayfirst=True, errors="coerce")

def _s(df: pd.DataFrame, col: str, default="") -> pd.Series:
    s = _safe_col(df, col, default=pd.NA)
    default = "" if default is None else str(default)

    s = s.astype("string")   # s.astype(object)
    return s.fillna(default).astype(str)

def _safe_col(df: pd.DataFrame, col: str, default="") -> pd.Series:
    if col in df.columns:
        return df[col]
    return pd.Series([default] * len(df))

def _to_str(s: pd.Series, default="") -> pd.Series:
    s = s.fillna(default)
    return s.astype(str)

def _subset_raw(df: pd.DataFrame, keep: Iterable[str])-> list[dict]:
    # keep only a small subset for debugging
    cols = [c for c in keep if c in df.columns]
    if not cols:
        return [{} for _ in range(len(df))]
    return df[cols].to_dict(orient="records")

# -------------------------------
# helper functions for suricata logs
# -------------------------------

def _to_ts(v) -> pd.Timestamp:
    return pd.to_datetime(v, utc=True, errors="coerce")

def _subset_raw(e: dict, keep: Iterable[str]) -> dict:
    return {k: e.get(k) for k in keep if k in e}

def _safe_str(x, default="") -> str:
    if x is None:
        return default
    return str(x)

# ---------------------------------
# helper functions for windows event logs
# ---------------------------------

def _strip_ns(tag: str) -> str:
    return tag.split('}', 1)[-1] if '}' in tag else tag

def _extract_from_eventdata_xml(xml_text: str) -> Dict[str, Any]:
    '''
    Extract <Data Name="X">VALUE</Data> into dict X->VALUE.
    Compatible with:
      - <EventData>...</EventData>
      - <DataItem ...><EventData>...</EventData></DataItem>
    '''    
    if not isinstance(xml_text, str):
        return {}
    s = xml_text.strip()
    if not s or "<" not in s:
        return {}
    
    # find first '<' to avoid leading junk
    s = s[s.find("<") :]

    root = None
    try:
        root = ET.fromstring(s)
    except Exception:
        # sometimes multiple roots -> wrap
        try:
            root = ET.fromstring(f"<Root>{s}</Root>")
        except Exception:
            return {}

    eventdata = None
    if _strip_ns(root.tag).lower() == "eventdata":
        eventdata = root
    else:
        for node in root.iter():
            if _strip_ns(node.tag).lower() == "eventdata":
                eventdata = node
                break
    if eventdata is None:
        return {}
    
    out: Dict[str, Any] = {}
    for child in list(eventdata):
        if _strip_ns(child.tag).lower() != "data":
            continue
        name = child.attrib.get("Name") or child.attrib.get("name") or ""
        if not name:
            continue
        out[name] = (child.text or "").strip()
    return out

# --------------------------------
# Helper functions for zeek logs
# --------------------------------

def _load_zeek_log(path: str | Path) -> pd.DataFrame:
    '''
    load zeek data from:
        - native zeek .log (via zat)
        - sanitized .csv
        - sanitized .parquet
    
    Assumption: CSV/Parquet preserve Zeek column names (e.g., ts, id.orig_h, uid, ...)
    '''
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(path)

    suf = path.suffix.lower()

    if suf == ".log":
        # zat returns (df, types); handle both cases robustly
        out = _parser.create_dataframe(str(path))
        df = out[0] if isinstance(out, tuple) else out
        return df

    if suf == ".csv":
        # Keep raw strings; don't coerce too early
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        # If ts exists, make sure it's numeric for downstream dropna/subset operations
        if "ts" in df.columns:
            df["ts"] = pd.to_numeric(df["ts"], errors="coerce")
        return df

    if suf == ".parquet":
        df = pd.read_parquet(path)
        if "ts" in df.columns:
            df["ts"] = pd.to_numeric(df["ts"], errors="coerce")
        return df

    raise ValueError(f"Unsupported Zeek input format: {path} (suffix={suf})")