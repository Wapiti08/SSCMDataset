'''
 # @ Create Time: 2025-12-21 19:31:26
 # @ Modified time: 2026-03-24 10:42:10
 # @ Description: reconstruct attack chain from event graph

 core functions:
        _choose_anchors: 
            input: dataframe with step tags and ts 
            output: sorted anchor list
        
        reconstruct_chain_detailed:
            for adjacent steps, choose responding anchor candidates, find shorted path

 '''

import networkx as nx
import pandas as pd

def _choose_anchors(step_events: pd.DataFrame, topk_per_step: int=1):
    ''' choose top-k anchor for every step

    return: [(step, [idx1, idx2, ...]), ...] according to min_ts in step
    '''
    se = step_events.dropna(subset=["step", "ts"]).copy()
    if len(se) == 0:
        return []
    
    anchors = []
    for step, df in se.groupby("step"):
        df = df.sort_values("ts")
        idxs = df.index.tolist()[:max(1, topk_per_step)]
        anchors.append((step, idxs, df["ts"].iloc[0]))
    anchors.sort(key=lambda x: x[2]) # by min_ts
    return [(s, idxs) for (s, idxs, _) in anchors]

def reconstruct_chain(graph, step_events, window_hops: int =8, max_bridge_seconds: int = 3600):
    '''
    return [(a, b, status)]
    - a/b is index of anchor events
    - status: connected / gap 
    '''
    detailed = reconstruct_chain_detailed(graph, step_events, 
                                          topk_per_step=1, 
                                          max_path_hops=window_hops,
                                          max_bridge_seconds=max_bridge_seconds,
                                        )
    out = []
    for link in detailed["links"]:
        out.append((link["a_idx"], link["b_idx"], link["status"]))
    return out

def reconstruct_chain_detailed(
        graph: nx.DiGraph, 
        step_events: pd.DataFrame, 
        topk_per_step: int=1, 
        max_path_hops: int=8,
        max_bridge_seconds: int=3600
        ):
    '''
    Three-level link status:
      - "connected":        a causal path of ≤ max_path_hops exists in the event graph.
      - "weakly_connected": no causal path, but anchor_b occurs after anchor_a within
                            max_bridge_seconds — temporal ordering is consistent even though
                            intermediate causality is not observable in the logs.
      - "gap":              neither causal path nor plausible temporal bridge.
 
    Parameters
    ----------
    graph : nx.DiGraph
        Temporal event graph built by build_event_graph().
    step_events : pd.DataFrame
        Must contain 'step' and 'ts' columns.
    topk_per_step : int
        Number of anchor candidates per step (default 1 = earliest event).
    max_path_hops : int
        Maximum hop count for a path to qualify as "connected" (default 8).
    max_bridge_seconds : int
        Maximum seconds between two anchors to qualify as "weakly_connected"
        when no graph path exists (default 3600 = 1 hour).
 
    Output:
    {
    "steps": [step1, step2, ...],
    "links": [
    { "a_step":..., "b_step":..., "a_idx":..., "b_idx":..., "status":"connected/gap",
    "path_len": int|None }
    ],
    "breakpoints": [ { "between": (a_step,b_step), "a_idx":..., "b_idx":... } ...]
    }
    '''
    anchors = _choose_anchors(step_events, topk_per_step=topk_per_step)
    steps = [s for (s, _) in anchors]

    # pre-fetch timestamps for all anchor candidates (avoid repeated .loc)
    _ts_cache = {}
    for _, candidates in anchors:
        for idx in candidates:
            if idx in step_events.index and "ts" in step_events.columns:
                t = step_events.at[idx, "ts"]
                if pd.notna(t):
                    _ts_cache[idx] = pd.Timestamp(t)

    links = []
    breakpoints = []

    for (a_step, a_candidates), (b_step, b_candidates) in zip(anchors, anchors[1:]):
        best = None  # (path_len, a_idx, b_idx)

        for a_idx in a_candidates:
            for b_idx in b_candidates:
                if a_idx == b_idx:
                    continue
                if nx.has_path(graph, a_idx, b_idx):
                    try:
                        # shortest path length in hops
                        plen = nx.shortest_path_length(graph, a_idx, b_idx)
                    except Exception:
                        plen = None
                    if plen is not None and plen <= max_path_hops:
                        cand = (plen, a_idx, b_idx)
                        if best is None or cand[0] < best[0]:
                            best = cand

        if best is not None:
            # ----- connected: causal path exists ------
            plen, a_idx, b_idx = best
            a_ts = _ts_cache.get(a_idx)
            b_ts = _ts_cache.get(b_idx)
            dt = (b_ts - a_ts).total_seconds() if (a_ts is not None and b_ts is not None) else None
 
            links.append({
                "a_step": a_step, "b_step": b_step,
                "a_idx": a_idx, "b_idx": b_idx,
                "status": "connected", 
                "path_len": int(plen),
                "dt_seconds": float(dt) if dt is not None else None,
            })

        else:
            # ---- no causal path: check temporal bridge ----
            a_idx = a_candidates[0] if a_candidates else None
            b_idx = b_candidates[0] if b_candidates else None
 
            a_ts = _ts_cache.get(a_idx)
            b_ts = _ts_cache.get(b_idx)
 
            if a_ts is not None and b_ts is not None and b_ts > a_ts:
                dt = (b_ts - a_ts).total_seconds()
                if dt <= max_bridge_seconds:
                    # WEAKLY CONNECTED: correct temporal order within bridge window
                    links.append({
                        "a_step": a_step, "b_step": b_step,
                        "a_idx": a_idx, "b_idx": b_idx,
                        "status": "weakly_connected",
                        "path_len": None,
                        "dt_seconds": float(dt),
                    })
                    # weakly_connected is NOT a breakpoint — ordering is plausible
                    continue
                else:
                    dt_val = float(dt)
            else:
                dt_val = float((b_ts - a_ts).total_seconds()) if (a_ts is not None and b_ts is not None) else None
 
            # GAP: no path and no temporal bridge
            links.append({
                "a_step": a_step, "b_step": b_step,
                "a_idx": a_idx, "b_idx": b_idx,
                "status": "gap", 
                "path_len": None,
                "dt_seconds": dt_val,
            })
            breakpoints.append({
                "between": (a_step, b_step), 
                "a_idx": a_idx, "b_idx": b_idx,
            })
 
    return {"steps": steps, "links": links, "breakpoints": breakpoints}


