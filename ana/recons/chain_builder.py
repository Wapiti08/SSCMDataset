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

def reconstruct_chain(graph, step_events, window_hops: int =8):
    '''
    return [(a, b, status)]
    - a/b is index of anchor events
    - status: connected / gap 
    '''
    detailed = reconstruct_chain_detailed(graph, step_events, topk_per_step=1, max_path_hops=window_hops)
    out = []
    for link in detailed["links"]:
        out.append((link["a_idx"], link["b_idx"], link["status"]))
    return out

def reconstruct_chain_detailed(
        graph: nx.DiGraph, 
        step_events: pd.DataFrame, 
        topk_per_step: int=1, 
        max_path_hops: int=8):
    '''
    - For each step, select the top-k anchors (based on the earliest time step).
    - Between adjacent steps, select anchor pairs with the shortest reachable path; otherwise, gap them.
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

        if best is None:
            # pick the earliest candidates as representative
            a_idx = a_candidates[0] if a_candidates else None
            b_idx = b_candidates[0] if b_candidates else None

            links.append({
                "a_step": a_step, "b_step": b_step,
                "a_idx": a_idx, "b_idx": b_idx,
                "status": "gap", "path_len": None
            })
            breakpoints.append({"between": (a_step, b_step), "a_idx": a_idx, "b_idx": b_idx})
        else:
            plen, a_idx, b_idx = best
            links.append({
                "a_step": a_step, "b_step": b_step,
                "a_idx": a_idx, "b_idx": b_idx,
                "status": "connected", "path_len": int(plen)
            })

    return {"steps": steps, "links": links, "breakpoints": breakpoints}





