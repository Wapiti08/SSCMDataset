'''
 # @ Create Time: 2025-12-21 19:30:55
 # @ Modified time: 2026-01-16 11:58:30
 # @ Description: 

 classify failure modes of event extraction: missing context, not able to correlate, weak evidence

 '''

import pandas as pd

def _missing_ratio(series: pd.Series) -> float:
    if series is None:
        return 1.0
    s = series
    return float((s.isna() | (s.astype(str).str.len() == 0)).mean())

def failure_taxonomy(events: pd.DataFrame):
    ''' return list[dict]

    - missing_field_ratio: subject/object/user/ip/pid/host/ts
    - unlinkable_ratio: the ratio of indeg + outdeg ==0
    - weak_step_evidence_ratio: the ratio of step with only one item
    '''
    if events is None or len(events) == 0:
        return []
    
    rows = []
    cols = set(events.columns)

    has_degree = "node_degree" in cols

    for src, df in events.groupby("source") if "source" in cols else [("ALL", events)]:
        out = {"source": src, "n_events": int(len(df))}

        # missing fields
        for c in ["subject", "object", "user", "src_ip", "dst_ip", "pid", "host", "ts"]:
            out[f"missing_{c}_ratio"] = _missing_ratio(df[c]) if c in cols else None

        # unlinkable proxy (optional)
        if has_degree:
            out["unlinkable_ratio"] = float((df["node_degree"].fillna(0) == 0).mean())
        else:
            out["unlinkable_ratio"] = None
        
        # weak step evidence
        if "step" in cols:
            step_counts = df.dropna(subset=["step"]).groupby("step").size()
            if len(step_counts) > 0:
                out["weak_step_evidence_ratio"] = float((step_counts == 1).mean())
                out["n_steps"] = int(step_counts.index.nunique())
            else:
                out["weak_step_evidence_ratio"] = None
                out["n_steps"] = 0
        else:
            out["weak_step_evidence_ratio"] = None
            out["n_steps"] = None

        rows.append(out)

    return rows

def failure_taxonomy_report(events: pd.DataFrame) -> dict:
    ''' 
    return dict, covering:
    - by_source: {src: {...}}
    - by_source_by_step: {src: {step: {...}}}
    - global: {...}
    
    '''
    if events is None or len(events) == 0:
        return {"by_source": {}, "by_source_by_step": {}, "global": {}}

    cols = set(events.columns)
    by_source = {}
    by_source_by_step = {}

    sources = events["source"].unique().tolist() if "source" in cols else ["ALL"]

    for src in sources:
        df = events[events["source"] == src] if "source" in cols else events
        by_source[src] = (failure_taxonomy(df)[0] if failure_taxonomy(df) else {"source": src})

        if "step" in cols:
            ss = {}
            for step, sdf in df.dropna(subset=["step"]).groupby("step"):
                ss[step] = {
                    "n_events": int(len(sdf)),
                    "missing_subject_ratio": _missing_ratio(sdf["subject"]) if "subject" in cols else None,
                    "missing_object_ratio": _missing_ratio(sdf["object"]) if "object" in cols else None,
                    "missing_user_ratio": _missing_ratio(sdf["user"]) if "user" in cols else None,
                    "missing_pid_ratio": _missing_ratio(sdf["pid"]) if "pid" in cols else None,
                    "missing_src_ip_ratio": _missing_ratio(sdf["src_ip"]) if "src_ip" in cols else None,
                    "missing_dst_ip_ratio": _missing_ratio(sdf["dst_ip"]) if "dst_ip" in cols else None,
                }
            by_source_by_step[src] = ss

    # global summary
    global_rows = failure_taxonomy(events)
    global_summary = {"n_sources": len(global_rows), "sources": [r["source"] for r in global_rows]}
    return {"by_source": by_source, "by_source_by_step": by_source_by_step, "global": global_summary}