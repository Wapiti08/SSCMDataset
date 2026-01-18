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
    # Azure exports contain many empty fields and quoted strings; keep them as strings
    return pd.read_csv(path, dtype=str, keep_default_na=False)

def _parse_ts(series: pd.Series) -> pd.Series:
    s = series.astype("string").str.strip().str.strip('"')
    ts = pd.to_datetime(s, utc=True, dayfirst=True, errors="coerce")
    return ts.dt.tz_convert(None)   # <- make tz-naive (UTC-normalized)

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

def _ensure_ts_datetime(df: pd.DataFrame, *, path: Path) -> pd.DataFrame:
    """
    Ensure df has a usable datetime column 'ts'.
    Accepts:
      - ts (epoch seconds, numeric or str)
      - ts_utc (ISO string or datetime)
      - ts_rel_s (relative seconds)  -> anchor to 1970-01-01
    """
    if df is None or len(df) == 0:
        return df

    # Case 1: already has datetime ts
    if "ts" in df.columns:
        # ts might be epoch seconds (float/int/str) or already datetime-like
        if pd.api.types.is_datetime64_any_dtype(df["ts"]):
            return df

        # try epoch seconds
        ts_num = pd.to_numeric(df["ts"], errors="coerce")
        if ts_num.notna().any():
            df = df.copy()
            df["ts"] = pd.to_datetime(ts_num, unit="s", utc=True, errors="coerce").dt.tz_convert(None)
            return df

        # try parse as datetime string
        ts_dt = pd.to_datetime(df["ts"], utc=True, errors="coerce")
        if ts_dt.notna().any():
            df = df.copy()
            df["ts"] = ts_dt.dt.tz_convert(None)
            return df

    # Case 2: ts_utc exists
    if "ts_utc" in df.columns:
        ts_dt = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce")
        if ts_dt.notna().any():
            df = df.copy()
            df["ts"] = ts_dt.dt.tz_convert(None)
            return df

    # Case 3: relative seconds
    if "ts_rel_s" in df.columns:
        rel = pd.to_numeric(df["ts_rel_s"], errors="coerce")
        if rel.notna().any():
            base = pd.Timestamp("1970-01-01")
            df = df.copy()
            df["ts"] = base + pd.to_timedelta(rel.fillna(0), unit="s")
            return df

    raise ValueError(f"Zeek log has no usable timestamp column (need ts/ts_utc/ts_rel_s). file={path}, cols={list(df.columns)}")


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

        if "ts" not in df.columns and getattr(df.index, "name", None) == "ts":
            df = df.reset_index()

        df.columns = [str(c).strip() for c in df.columns]

        return _ensure_ts_datetime(df, path=path)

    if suf == ".csv":
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        df.columns = [str(c).strip() for c in df.columns]
        return _ensure_ts_datetime(df, path=path)

    if suf == ".parquet":
        df = pd.read_parquet(path)
        df.columns = [str(c).strip() for c in df.columns]
        return _ensure_ts_datetime(df, path=path)

    raise ValueError(f"Unsupported Zeek input format: {path} (suffix={suf})")