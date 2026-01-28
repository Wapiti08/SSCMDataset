import re
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple
import ipaddress

import pandas as pd

try:
    from .rules import STEP_RULES, FIELD_ALIASES
except Exception:  # standalone fallback
    from rules import STEP_RULES, FIELD_ALIASES


def _ensure_text(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("")


def _lower_col_map(columns: List[str]) -> Dict[str, str]:
    m: Dict[str, str] = {}
    for c in columns:
        lc = str(c).lower()
        if lc not in m:
            m[lc] = c
    return m


def _resolve_col(df: pd.DataFrame, canonical: str) -> Optional[str]:
    """Resolve canonical field name -> dataframe column via FIELD_ALIASES."""
    if canonical in df.columns:
        return canonical

    candidates = [canonical] + FIELD_ALIASES.get(canonical, [])
    for c in candidates:
        if c in df.columns:
            return c

    lmap = _lower_col_map(list(df.columns))
    for c in candidates:
        lc = str(c).lower()
        if lc in lmap:
            return lmap[lc]
    return None


def _resolve_fields(df: pd.DataFrame, fields: List[str]) -> List[str]:
    cols: List[str] = []
    seen = set()
    for f in fields:
        col = _resolve_col(df, f)
        if col and col not in seen:
            cols.append(col)
            seen.add(col)
    return cols


def _build_text_blob(df: pd.DataFrame, resolved_cols: List[str]) -> pd.Series:
    if not resolved_cols:
        return pd.Series([""] * len(df), index=df.index, dtype="string")
    blob = _ensure_text(df[resolved_cols[0]])
    for c in resolved_cols[1:]:
        blob = blob + " | " + _ensure_text(df[c])
    return blob


@lru_cache(maxsize=256)
def _compile_rx(patterns: Tuple[str, ...]) -> Optional[re.Pattern]:
    if not patterns:
        return None
    combined = "(?:" + ")|(?:".join(patterns) + ")"
    try:
        return re.compile(combined, flags=re.IGNORECASE)
    except re.error:
        return None


def _eval_prefilter(df: pd.DataFrame, cond: Dict[str, Any]) -> Optional[pd.Series]:
    field = cond.get("field")
    if not field:
        return None
    col = _resolve_col(df, field)
    if not col:
        return None

    s = _ensure_text(df[col])

    if "in" in cond:
        vals = cond.get("in") or []
        vset = {str(v).lower() for v in vals}
        return s.str.lower().isin(vset)

    if "regex" in cond:
        try:
            rx = re.compile(str(cond["regex"]), flags=re.IGNORECASE)
        except re.error:
            return None
        return s.str.contains(rx, na=False)

    if cond.get("exists"):
        return s.ne("")

    return None


def _apply_where(df: pd.DataFrame, where: Optional[List[Dict[str, Any]]], mode: str) -> Tuple[Optional[pd.Series], int]:
    if not where:
        return None, 0
    masks: List[pd.Series] = []
    for cond in where:
        m = _eval_prefilter(df, cond)
        if m is not None:
            masks.append(m)
    if not masks:
        return None, 0
    out = masks[0].copy()
    for m in masks[1:]:
        out = (out | m) if mode == "any" else (out & m)
    return out, len(masks)


def _is_public_ip(ip: Any) -> bool:
    try:
        a = ipaddress.ip_address(str(ip))
        return not (
            a.is_private
            or a.is_loopback
            or a.is_link_local
            or a.is_multicast
            or a.is_reserved
        )
    except Exception:
        return False


def _apply_azure_conn_heuristics(
    df: pd.DataFrame,
    *,
    allowed_set: Optional[set],
    keep_candidates: bool,
    stats: Dict[str, Any],
    debug: bool,
):
    """Azure connection heuristics to rescue SC1-like cases.

    Robust to schema differences:
      - OUTBOUND_CONN requires only dst + dst_port
      - DOWNLOAD/EXFIL require bytes_in/out if available
    """
    if df is None or len(df) == 0 or "source" not in df.columns:
        return

    src_mask = df["source"].astype("string").str.lower().eq("azure_conn")
    if not src_mask.any():
        return

    dst_col = _resolve_col(df, "dst")
    port_col = _resolve_col(df, "dst_port")
    bi_col = _resolve_col(df, "bytes_in")
    bo_col = _resolve_col(df, "bytes_out")
    dir_col = _resolve_col(df, "direction")

    missing = []
    if not dst_col:
        missing.append("dst")
    if not port_col:
        missing.append("dst_port")

    # If we can't even get dst+port, nothing we can do
    if missing:
        st = stats.setdefault("rules", {}).setdefault(
            "HEUR_AZURE_CONN_SKIPPED",
            {"step": "(heuristic)", "hits": 0, "missing_fields_events": 0, "missing_prefilter_events": 0, "used_prefilter_conditions": 0},
        )
        st["missing_fields_events"] += int(src_mask.sum())
        return

    sub = df.loc[src_mask]
    dst = sub[dst_col].astype("string").fillna("")
    port = sub[port_col].astype("string").fillna("")

    # direction optional
    if dir_col:
        direc = sub[dir_col].astype("string").fillna("").str.lower()
        outbound_dir = direc.str.contains("out") | direc.str.contains("egress")
    else:
        outbound_dir = pd.Series([True] * len(sub), index=sub.index)

    is_pub = dst.apply(_is_public_ip)
    ports_ok = port.isin(["22", "80", "443", "8080", "8443"])

    outbound = dst.ne("") & port.ne("") & is_pub & outbound_dir & ports_ok

    # bytes optional: only compute download/exfil when both exist
    one_mb = 1 * 1024 * 1024
    if bi_col and bo_col:
        bi = pd.to_numeric(sub[bi_col], errors="coerce").fillna(0).astype("int64")
        bo = pd.to_numeric(sub[bo_col], errors="coerce").fillna(0).astype("int64")
        download = (bi >= one_mb) & (bi >= 3 * bo.clip(lower=1))
        exfil = (bo >= one_mb) & (bo >= 3 * bi.clip(lower=1))
    else:
        download = pd.Series([False] * len(sub), index=sub.index)
        exfil = pd.Series([False] * len(sub), index=sub.index)

    def _set_step(hit_mask: pd.Series, step: str, priority: int, score: float, rid: str):
        if allowed_set is not None and step.upper() not in allowed_set:
            return
        if not hit_mask.any():
            return

        better = hit_mask & (
            (priority > df["_step_priority"])
            | ((priority == df["_step_priority"]) & (score > df["step_score"]))
        )
        if not better.any():
            return

        df.loc[better, "step"] = step
        df.loc[better, "step_score"] = score
        df.loc[better, "step_reason"] = f"heuristic(id={rid},step={step},priority={priority})"
        df.loc[better, "_step_priority"] = priority

        if keep_candidates and "step_candidates" in df.columns:
            for i in df.index[better]:
                df.at[i, "step_candidates"] = df.at[i, "step_candidates"] + [step]

        if debug:
            if "step_rule_id" in df.columns:
                df.loc[better, "step_rule_id"] = rid
            if "step_blob_fields" in df.columns:
                fields = [dst_col, port_col]
                if bi_col: fields.append(bi_col)
                if bo_col: fields.append(bo_col)
                if dir_col: fields.append(dir_col)
                df.loc[better, "step_blob_fields"] = ",".join(fields)

        st = stats.setdefault("rules", {}).setdefault(
            rid,
            {"step": step, "hits": 0, "missing_fields_events": 0, "missing_prefilter_events": 0, "used_prefilter_conditions": 0},
        )
        st["hits"] += int(better.sum())

    # order: EXFIL/DOWNLOAD first, then OUTBOUND_CONN
    _set_step(exfil.reindex(df.index, fill_value=False) & src_mask, "EXFIL", priority=18, score=0.95, rid="HEUR_AZURE_EXFIL")
    _set_step(download.reindex(df.index, fill_value=False) & src_mask, "DOWNLOAD", priority=20, score=0.95, rid="HEUR_AZURE_DOWNLOAD")
    _set_step(outbound.reindex(df.index, fill_value=False) & src_mask, "OUTBOUND_CONN", priority=15, score=0.90, rid="HEUR_AZURE_OUTBOUND")

    # If bytes are missing, record it (useful for diagnosing SC1)
    if not bi_col or not bo_col:
        st = stats.setdefault("rules", {}).setdefault(
            "HEUR_AZURE_CONN_PARTIAL",
            {"step": "(heuristic)", "hits": 0, "missing_fields_events": 0, "missing_prefilter_events": 0, "used_prefilter_conditions": 0},
        )
        st["missing_fields_events"] += int(src_mask.sum())


def tag_steps(
    events: pd.DataFrame,
    *,
    allowed_steps: Optional[List[str]] = None,
    keep_candidates: bool = True,
    debug: bool = False,
    return_stats: bool = False,
):
    """Rule-based coarse step tagging with schema-aliasing and diagnostics."""
    if events is None or len(events) == 0:
        return (events, {"rules": {}}) if return_stats else events

    df = events.copy()
    df["step"] = None
    df["step_score"] = 0.0
    df["step_reason"] = None
    df["_step_priority"] = -10**9

    if keep_candidates:
        df["step_candidates"] = [[] for _ in range(len(df))]
    if debug:
        df["step_rule_id"] = None
        df["step_blob_fields"] = None

    has_source = "source" in df.columns

    stats: Dict[str, Any] = {"rules": {}}
    blob_cache: Dict[Tuple[str, ...], pd.Series] = {}

    allowed_set = None
    if allowed_steps is not None:
        allowed_set = {str(s).strip().upper() for s in allowed_steps if str(s).strip()}

    for rule in STEP_RULES:
        rid = rule.get("id") or f"RULE_{rule.get('step','UNK')}"
        step = rule["step"]

        # Gate by allowed steps (keeps AUTH out of non-SC6 scenarios in your evaluation setup)
        if allowed_set is not None and str(step).upper() not in allowed_set:
            continue

        patterns = tuple(rule.get("patterns", []))
        fields = list(rule.get("fields", ["raw"]))
        sources = rule.get("sources", None)
        priority = int(rule.get("priority", 0))
        score = float(rule.get("score", 1.0))
        strict_prefilter = bool(rule.get("strict_prefilter", False))

        rstat = stats["rules"].setdefault(
            rid,
            {
                "step": step,
                "hits": 0,
                "missing_fields_events": 0,
                "missing_prefilter_events": 0,
                "used_prefilter_conditions": 0,
            },
        )

        # source filter
        if sources is not None and has_source:
            base_mask = df["source"].astype("string").str.lower().isin([s.lower() for s in sources])
        else:
            base_mask = pd.Series([True] * len(df), index=df.index)

        mask = base_mask

        where_all = rule.get("where_all")
        where_any = rule.get("where_any")

        m_all, used_all = _apply_where(df, where_all, mode="all")
        if m_all is not None:
            mask &= m_all
            rstat["used_prefilter_conditions"] += used_all
        elif where_all:
            rstat["missing_prefilter_events"] += int(base_mask.sum())
            if strict_prefilter:
                continue

        m_any, used_any = _apply_where(df, where_any, mode="any")
        if m_any is not None:
            mask &= m_any
            rstat["used_prefilter_conditions"] += used_any
        elif where_any:
            rstat["missing_prefilter_events"] += int(base_mask.sum())
            if strict_prefilter:
                continue

        if not mask.any():
            continue

        resolved_cols = _resolve_fields(df, fields)
        if not resolved_cols:
            rstat["missing_fields_events"] += int(mask.sum())
            continue

        key = tuple(resolved_cols)
        if key not in blob_cache:
            blob_cache[key] = _build_text_blob(df, resolved_cols)
        blob = blob_cache[key]

        rx = _compile_rx(patterns)
        if not rx:
            continue

        hit = mask & blob.str.contains(rx, na=False)
        if not hit.any():
            continue

        rstat["hits"] += int(hit.sum())

        if keep_candidates:
            for i in df.index[hit]:
                df.at[i, "step_candidates"] = df.at[i, "step_candidates"] + [step]

        better = hit & (
            (priority > df["_step_priority"])
            | ((priority == df["_step_priority"]) & (score > df["step_score"]))
        )
        if better.any():
            df.loc[better, "step"] = step
            df.loc[better, "step_score"] = score
            df.loc[better, "step_reason"] = f"rule(id={rid},step={step},priority={priority})"
            df.loc[better, "_step_priority"] = priority
            if debug:
                df.loc[better, "step_rule_id"] = rid
                df.loc[better, "step_blob_fields"] = ",".join(resolved_cols)

    # Post-pass: Azure connection heuristics
    _apply_azure_conn_heuristics(
        df,
        allowed_set=allowed_set,
        keep_candidates=keep_candidates,
        stats=stats,
        debug=debug,
    )

    df.drop(columns=["_step_priority"], inplace=True)

    return (df, stats) if return_stats else df
