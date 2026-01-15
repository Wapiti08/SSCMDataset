import pandas as pd

def step_continuity_proxy(step_events: pd.DataFrame, max_gap_seconds: int = 600) -> float:
    '''
    step-level time continuity proxy metric.
    - extact time windows for each step [min_ts, max_ts]
    - the gap of adjacent steps uses next_min_ts - prev_max_ts
    '''
    if step_events is None or len(step_events) == 0:
        return 0.0
    if "step" not in step_events.columns or "ts" not in step_events.columns:
        return 0.0
    
    se = step_events.dropna(subset=["step", "ts"]).copy()
    if len(se) == 0:
        return 0.0
    
    per_step = (
        se.groupby("step")["ts"]
            .agg(min_ts="min", max_ts="max")
            .sort_values("min_ts")
    )
    # if only one step, return perfect score
    if len(per_step) <= 1:
        return 1.0 
    
    ok = 0
    mins = per_step["min_ts"].tolist()
    maxs = per_step["max_ts"].tolist()

    for prev_max, next_min in zip(maxs, mins[1:]):
        gap = (next_min - prev_max).total_seconds()
        if gap <= max_gap_seconds:
            ok += 1

    return ok / (len(per_step) - 1)


def chain_continuity_proxy(tagged: pd.DataFrame, chain, max_gap_seconds: int = 600) -> float:
    '''
    Chain-level continuity proxy (based the reconstruct chain order)
    - extract time windows for each step in chain [min_ts, max_ts] 
    - Adjacent step gaps still use next_min_ts - prev_max_ts
    - If chain is empty or step cannot find an event, automatically downgrade/skip.
    '''
    if tagged is None or len(tagged) == 0:
        return 0.0
    if "step" not in tagged.columns or "ts" not in tagged.columns:
        return 0.0
    if not chain:
        return 0.0
    
    # compitable with chain list[str] or list[dict]
    if isinstance(chain, list) and len(chain) >0 and isinstance(chain[0], dict):
        chain_steps = [x.get("step") for x in chain if x.get("step") is not None]
    else:
        chain_steps = [x for x in chain if x is not None]
    
    chain_steps = [s for s in chain_steps if isinstance(s, str) and s.strip() != ""]

    if len(chain_steps) <= 1:
        return 1.0 if len(chain_steps) == 1 else 0.0

    se = tagged.dropna(subset=["step", "ts"]).copy()
    if len(se) == 0:
        return 0.0

    # extract per-step time windows
    per_step = (
        se.groupby("step")["ts"]
            .agg(min_ts="min", max_ts="max")
            .to_dict(orient="index")
    )

    # Only retain steps that actually appear in the data (avoid steps in the chain that don't have any events).
    chain_steps_present = [s for s in chain_steps if s in per_step]
    if len(chain_steps_present) <= 1:
        return 0.0 if len(chain_steps) > 1 else 1.0

    ok = 0
    total = 0
    for a, b in zip(chain_steps_present, chain_steps_present[1:]):
        total += 1
        prev_max = per_step[a]["max_ts"]
        next_min = per_step[b]["min_ts"]
        gap = (next_min - prev_max).total_seconds()
        if gap <= max_gap_seconds:
            ok += 1

    return ok / max(total, 1)


def compute_metrics(tagged: pd.DataFrame, chain=None, max_gap_seconds: int=600) -> dict:
    '''
    Compute a set of metrics for the tagged events.
    '''
    if tagged is None or len(tagged) == 0:
        return {
            "n_events": 0,
            "n_step_events": 0,
            "n_steps_observed": 0,
            "step_continuity_proxy": 0.0,
            "chain_continuity_proxy": 0.0,
        }

    n_events = int(len(tagged))
    if "step" in tagged.columns:
        step_events = tagged.dropna(subset=["step"]).copy()
        n_step_events = int(len(step_events))
        n_steps_observed = int(step_events["step"].nunique()) if len(step_events) else 0
    else:
        step_events = tagged.iloc[0:0].copy()
        n_step_events = 0
        n_steps_observed = 0
    
    step_c = step_continuity_proxy(step_events, max_gap_seconds=max_gap_seconds) if n_step_events else 0.0
    chain_c = chain_continuity_proxy(tagged, chain, max_gap_seconds=max_gap_seconds) if chain else 0.0

    return {
        "n_events": n_events,
        "n_step_events": n_step_events,
        "n_steps_observed": n_steps_observed,
        "step_continuity_proxy": float(step_c),
        "chain_continuity_proxy": float(chain_c),
    }