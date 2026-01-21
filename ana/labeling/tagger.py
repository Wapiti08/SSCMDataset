import re
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

try:
    from .rules import STEP_RULES, FIELD_ALIASES
except Exception:  # standalone fallback
    from rules import STEP_RULES, FIELD_ALIASES


def _ensure_text(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("")


def _lower_col_map(columns: List[str]) -> Dict[str, str]:
    m = {}
    for c in columns:
        lc = str(c).lower()
        if lc not in m:
            m[lc] = c
    return m


def _resolve_col(df: pd.DataFrame, canonical: str) -> Optional[str]:
    """Resolve canonical field name -> existing dataframe column via FIELD_ALIASES."""
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
        if mode == "any":
            out |= m
        else:
            out &= m
    return out, len(masks)


def tag_steps(
    events: pd.DataFrame,
    *,
    keep_candidates: bool = True,
    debug: bool = False,
    return_stats: bool = False,
):
    """Rule-based coarse step tagging with schema-aliasing and diagnostics.

    Returns:
      - df (always)
      - (df, stats) if return_stats=True
    """
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

    for rule in STEP_RULES:
        rid = rule.get("id") or f"RULE_{rule.get('step','UNK')}"
        step = rule["step"]
        patterns = tuple(rule.get("patterns", []))
        fields = list(rule.get("fields", ["raw"]))
        sources = rule.get("sources", None)
        priority = int(rule.get("priority", 0))
        score = float(rule.get("score", 1.0))

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

        # structured prefilters
        mask = base_mask
        where_all = rule.get("where_all")
        where_any = rule.get("where_any")

        m_all, used_all = _apply_where(df, where_all, mode="all")
        if m_all is not None:
            mask &= m_all
            rstat["used_prefilter_conditions"] += used_all
        elif where_all:
            rstat["missing_prefilter_events"] += int(base_mask.sum())

        m_any, used_any = _apply_where(df, where_any, mode="any")
        if m_any is not None:
            mask &= m_any
            rstat["used_prefilter_conditions"] += used_any
        elif where_any:
            rstat["missing_prefilter_events"] += int(base_mask.sum())

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

    df.drop(columns=["_step_priority"], inplace=True)

    return (df, stats) if return_stats else df
