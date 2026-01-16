import re
from .rules import STEP_RULES
import pandas as pd

def _ensure_text(series: pd.Series) -> pd.Series:
    if series is None:
        return pd.Series([], dtype="string")
    return series.astype("string").fillna("")

def _build_text_blob(events: pd.DataFrame, fields: list[str]) -> pd.Series:
    '''
    concate existing fields into a text blob
    '''
    cols = [c for c in fields if c in events.columns]
    if not cols:
        return pd.Series([""] * len(events), index=events.index, dtype="string")
    blob = _ensure_text(events[cols[0]])
    for c in cols[1:]:
        blob = blob + " | " + _ensure_text(events[c])
    return blob

def tag_steps(events: pd.DataFrame) -> pd.DataFrame:
    '''
    Add a "step" tag to events (enhanced version)

    Returns: events + step/step_candidates/step_score/step_reason
    '''
    if events is None or len(events) == 0:
        return events

    df = events.copy()
    df["step"] = None
    df["step_candidates"] = [[] for _ in range(len(df))]
    df["step_score"] = 0.0
    df["step_reason"] = None

    has_source = "source" in df.columns

    blob_cache = {}

    for rule in STEP_RULES:
        step = rule["step"]
        patterns = rule.get("patterns", [])
        fields = rule.get("fields", ["raw"])
        sources = rule.get("sources", None)
        priority = int(rule.get("priority", 0))
        score = float(rule.get("score", 1.0))

        # filter source
        if sources is not None and has_source:
            rule_mask = df["source"].isin(sources)
        else:
            rule_mask = pd.Series([True] * len(df), index=df.index)

        # construct/reuse blob
        key = tuple(fields)
        if key not in blob_cache:
            blob_cache[key] = _build_text_blob(df, fields)
        blob = blob_cache[key]

        # pattern matching
        if not patterns:
            continue
        combined = "(" + ")|(".join(patterns) + ")"
        try:
            rx = re.compile(combined, flags=re.IGNORECASE)
        except re.error:
            continue

        hit = rule_mask & blob.str.contains(rx, na=False)

        if not hit.any():
            continue
        
        # update candidates
        hit_idx = df.index[hit]
        for i in hit_idx:
            df.at[i, "step_candidates"] = df.at[i, "step_candidates"] + [step]

        # decision: update step if higher score/priority
        if "_step_priority" not in df.columns:
            df["_step_priority"] = -10**9
        
        better = hit & (
            (priority > df["_step_priority"]) |
            ((priority == df["_step_priority"]) & (score > df["step_score"]))
        )

        df.loc[better, "step"] = step
        df.loc[better, "step_score"] = score
        df.loc[better, "step_reason"] = f"rule(step={step},priority={priority})"
        df.loc[better, "_step_priority"] = priority

    if "_step_priority" in df.columns:
        df.drop(columns=["_step_priority"], inplace=True)

    return df
