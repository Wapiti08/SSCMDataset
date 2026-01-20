import re
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# Support both package and standalone execution
try:
    from .rules import STEP_RULES, FIELD_ALIASES
except Exception:  # pragma: no cover
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
    """Resolve a canonical field name to an actual column in df via FIELD_ALIASES."""
    if canonical in df.columns:
        return canonical

    candidates = [canonical] + FIELD_ALIASES.get(canonical, [])

    # exact match
    for c in candidates:
        if c in df.columns:
            return c

    # case-insensitive match
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
        c = _resolve_col(df, f)
        if c and c not in seen:
            cols.append(c)
            seen.add(c)
    return cols


def _build_text_blob(df: pd.DataFrame, resolved_cols: List[str]) -> pd.Series:
    if not resolved_cols:
        return pd.Series([""] * len(df), index=df.index, dtype="string")

    blob = _ensure_text(df[resolved_cols[0]])
    for c in resolved_cols[1:]:
        blob = blob + " | " + _ensure_text(df[c])
    return blob


@lru_cache(maxsize=256)
def _compile_combined(patterns: Tuple[str, ...]) -> Optional[re.Pattern]:
    if not patterns:
        return None
    combined = "(?:" + ")|(?:".join(patterns) + ")"
    try:
        return re.compile(combined, flags=re.IGNORECASE)
    except re.error:
        return None


@lru_cache(maxsize=256)
def _compile_single(pattern: str) -> Optional[re.Pattern]:
    try:
        return re.compile(pattern, flags=re.IGNORECASE)
    except re.error:
        return None


def _eval_prefilter(df: pd.DataFrame, cond: Dict[str, Any]) -> Optional[pd.Series]:
    """Evaluate a structured prefilter condition.

    Supported:
      - {"field": "...", "in": ["a","b"]}
      - {"field": "...", "regex": "..."}
      - {"field": "...", "exists": True}

    Returns a boolean Series, or None if the required field is missing.
    """
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
        rx = _compile_single(str(cond["regex"]))
        if not rx:
            return None
        return s.str.contains(rx, na=False)

    if cond.get("exists"):
        return s.ne("")

    return None


def _apply_where(df: pd.DataFrame, where: Optional[List[Dict[str, Any]]], mode: str) -> Tuple[Optional[pd.Series], int]:
    """Apply where_any/where_all.

    Returns:
      (mask_or_None, n_usable_conditions)

    If no conditions are usable (e.g., missing columns), returns (None, 0).
    """
    if not where:
        return None, 0

    masks: List[pd.Series] = []
    for cond in where:
        m = _eval_prefilter(df, cond)
        if m is not None:
            masks.append(m)

    if not masks:
        return None, 0

    if mode == "any":
        out = masks[0].copy()
        for m in masks[1:]:
            out |= m
        return out, len(masks)

    out = masks[0].copy()
    for m in masks[1:]:
        out &= m
    return out, len(masks)


def tag_steps(
    events: pd.DataFrame,
    *,
    keep_candidates: bool = True,
    debug: bool = False,
    return_stats: bool = False,
) -> Any:
    """Tag events with coarse step labels.

    Always adds:
      - step
      - step_score
      - step_reason

    If keep_candidates=True, adds:
      - step_candidates

    If debug=True, adds:
      - step_rule_id
      - step_blob_fields

    If return_stats=True, returns (df, stats) where stats includes rule-level counts
    for hits and schema/prefilter usability.
    """
    if events is None or len(events) == 0:
        return (events, {}) if return_stats else events

    df = events.copy()
    df["step"] = None
    df["step_score"] = 0.0
    df["step_reason"] = None

    if keep_candidates:
        df["step_candidates"] = [[] for _ in range(len(df))]

    if debug:
        df["step_rule_id"] = None
        df["step_blob_fields"] = None

    has_source = "source" in df.columns

    # For priority tie-breaking
    df["_step_priority"] = -10**9

    stats: Dict[str, Any] = {"rules": {}}

    # Cache blobs by resolved column tuple for speed
    blob_cache: Dict[Tuple[str, ...], pd.Series] = {}

    for rule in STEP_RULES:
        rid = rule.get("id", rule.get("step", "RULE"))
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

        # source filter (case-insensitive for robustness)
        if sources is not None and has_source:
            src_series = _ensure_text(df["source"]).str.lower()
            src_allowed = {str(s).lower() for s in sources}
            base_mask = src_series.isin(src_allowed)
        else:
            base_mask = pd.Series([True] * len(df), index=df.index)

        mask = base_mask

        # structured prefilters (optional)
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

        # resolve fields -> build blob
        resolved_cols = _resolve_fields(df, fields)
        if not resolved_cols:
            rstat["missing_fields_events"] += int(mask.sum())
            continue

        key = tuple(resolved_cols)
        if key not in blob_cache:
            blob_cache[key] = _build_text_blob(df, resolved_cols)
        blob = blob_cache[key]

        rx = _compile_combined(patterns)
        if not rx:
            continue

        hit = mask & blob.str.contains(rx, na=False)
        if not hit.any():
            continue

        rstat["hits"] += int(hit.sum())

        if keep_candidates:
            hit_idx = df.index[hit]
            for i in hit_idx:
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
