'''
 # @ Create Time: 2025-12-24 09:51:17
 # @ Modified time: 2025-12-24 09:51:26
 # @ Description: provide evidence for negative chains when comparing multi-source and single-source events
 '''

import pandas as pd

def detect_failed_entry_chains(
    events: pd.DataFrame,
    window_seconds: int = 300
):
    '''
    Detect chains with:
      - auth / network activity
      - but no process execution in a time window
    '''
    if events is None or len(events) == 0:
        return pd.DataFrame([])
    
    required = {"ts", "host", "source", "event_type"}
    if not required.issubset(set(events.columns)):
        return pd.DataFrame([])

    failed = []

    auth_like = events[
        (events["source"].isin(["auth", "zeek", "suricata"])) &
        (events["event_type"].isin(["auth", "network"]))
    ]

    exec_events = events[
        (events["source"] == "auditd") &
        (events["event_type"] == "process")
    ]

    for _, e in auth_like.iterrows():
        t0 = e["ts"]
        t1 = t0 + pd.Timedelta(seconds=window_seconds)

        has_exec = exec_events[
            (exec_events["host"] == e["host"]) &
            (exec_events["ts"] >= t0) &
            (exec_events["ts"] <= t1)
        ]

        if has_exec.empty:
            failed.append({
                "ts": e["ts"],
                "host": e["host"],
                "trigger_source": e.get("source"),
                "trigger_event_type": e.get("event_type"),
                "trigger_action": e.get("action"),
                "evidence": e.get("raw"),
            })

    return pd.DataFrame(failed)


def detect_step_gap_evidence(
    tagged: pd.DataFrame,
    step_order: list | None = None,
    window_seconds: int = 600,
    group_keys=("host", "user", "src_ip", "dst_ip"),
):
    '''
    general step-gap probe
    - Divide events into several "chain candidate entities" based on group_keys.
    - Within each group, extract the step sequence by time (deduplicating).
    - If step_order is given: check for "step segments that should appear but are missing".
    Otherwise: check if the time gap between adjacent steps exceeds a threshold (continuity breakpoint).

    Output: DataFrame, containing breakpoints, missing steps, and evidence events (first/last).
    '''
    if tagged is None or len(tagged) == 0:
        return pd.DataFrame([])
    
    if "ts" not in tagged.columns or "step" not in tagged.columns:
        return pd.DataFrame([])

    df = tagged.dropna(subset=["ts"]).copy()

    # use existing group keys
    gks = [k for k in group_keys if k in df.columns]
    if not gks:
        gks = ["__all__"]
        df["__all__"] = "ALL"

    out = []

    for gvals, gdf in df.groupby(gks):
        gdf = gdf.sort_values("ts")
        step_df = gdf.dropna(subset=["step"])

        if len(step_df) == 0:
            continue

        # unique steps in time order
        seq = step_df[["ts", "step"]].drop_duplicates(subset=["step"], keep="first").sort_values("ts")
        steps = seq["step"].tolist()
        times = seq["ts"].tolist()

        # A) expected order provided: find missing blocks
        if step_order:
            present = set(steps)
            missing = [s for s in step_order if s not in present]
            if missing:
                out.append({
                    "group": gvals,
                    "type": "missing_steps",
                    "missing_steps": missing,
                    "first_ts": times[0],
                    "last_ts": times[-1],
                    "first_step": steps[0],
                    "last_step": steps[-1],
                })
        
        # B) gap detection between consecutive observed steps
        for (sa, ta), (sb, tb) in zip(zip(steps, times), zip(steps[1:], times[1:])):
            gap = (tb - ta).total_seconds()
            if gap > window_seconds:
                out.append({
                    "group": gvals,
                    "type": "time_gap",
                    "a_step": sa,
                    "b_step": sb,
                    "a_ts": ta,
                    "b_ts": tb,
                    "gap_seconds": float(gap),
                })

    return pd.DataFrame(out)

        
