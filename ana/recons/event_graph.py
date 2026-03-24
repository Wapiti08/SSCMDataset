'''
 # @ Create Time: 2025-12-21 19:31:12
 # @ Modified time: 2026-03-24 10:22:10
 # @ Description: reconstruct timeline-based event graph

core functions:
    build_event_graph:
        input: event dataframe
            every row: ts, host, pid, ppid, user, conn_id, src_ip/dst_ip
        output: directed networkx graph (the edge includes reason and dt_seconds)

 '''


import networkx as nx
from collections import deque, defaultdict
import pandas as pd

def build_event_graph(
        events: pd.DataFrame, 
        window_seconds=600,
        host_key: str = "host",
        ts_key: str= "ts",
        entity_keys=("pid", "ppid", "user"),
        flow_keys=("conn_id", "uid", "flow_id"),
        ip_pair_keys=(("src_ip", "dst_ip"),),
        add_prev_edge: bool = True,
    ):
    '''
    event-level temporal dependency graph
    - use sliding windows on each host to connect events
    - on the basis of adjacent hosts, prioritize entity consisteny to connect edges
    - add reason + dt_seconds on edges, better for analysis for failure

    compatible: there are ts and host columns in events
    '''
    g = nx.DiGraph()

    if events is None or len(events) == 0:
        return g
    if ts_key not in events.columns:
        raise ValueError(f"events missing required column: {ts_key}")

    # add nodes
    for i, r in events.iterrows():
        g.add_node(i, **r.to_dict())

    # group by host or default
    if host_key in events.columns:
        groups = events.groupby(host_key)
    else:
        groups = [(None, events)]
    
    # global last-seen (to correlate across-host conn_id/uid/flow_id/ip pair)
    global_last_seen = {}  # (k, value) -> (idx, ts)
    global_last_seen_pair = {}  # (("src_ip","dst_ip"), (a,b)) -> (idx, ts)

    for _, df in groups:
        df = df.dropna(subset=[ts_key]).sort_values(ts_key)

        # sliding window queue
        win = deque() # elements: (idx, ts)
        # last-seen inside host
        last_seen = defaultdict(dict) # key -> value -> (idx, ts)

        prev_idx = None
        prev_ts = None

        for idx, row in df.iterrows():
            ts = row[ts_key]

            # pop old events out of window
            while win and (ts-win[0][1]).total_seconds() > window_seconds:
                win.popleft()
            
            # 1) optional: always connect to immediate previous event on same host within window
            if add_prev_edge and prev_idx is not None and prev_ts is not None:
                dt = (ts - prev_ts).total_seconds()
                if 0 < dt <= window_seconds:
                    g.add_edge(prev_idx, idx, reason="time_prev", dt_seconds=float(dt))
            
            # 2) entity-based edges (host-local) --- a series of actions by same process/user 
            added_from = set()
            for k in entity_keys:
                if k in df.columns:
                    v = row.get(k, None)

                    # robust missing check: works for None, NaN, pd.NA
                    if v is None or pd.isna(v) or v == "":
                        continue
                    if v in last_seen[k]:
                        j, jts = last_seen[k][v]
                        dt = (ts - jts).total_seconds()
                        if 0 < dt <= window_seconds and j != idx:
                            g.add_edge(j, idx, reason=f"entity:{k}", dt_seconds=float(dt))
                            added_from.add(j)
                    last_seen[k][v] = (idx, ts)

            # 3) flow-id edges (global) --- lateral movement
            for k in flow_keys:
                if k in df.columns:
                    v = row.get(k, None)
                    if v is None or (isinstance(v, float) and pd.isna(v)) or v == "":
                        continue
                    kk = (k, v)
                    if kk in global_last_seen:
                        j, jts = global_last_seen[kk]
                        dt = (ts - jts).total_seconds()
                        if 0 < dt <= window_seconds and j != idx:
                            g.add_edge(j, idx, reason=f"flow:{k}", dt_seconds=float(dt))
                    global_last_seen[kk] = (idx, ts)
            
            # 4) ip-pair edges (global) --- process network-layer without flow ID
            for (a, b) in ip_pair_keys:
                if a in df.columns and b in df.columns:
                    va, vb = row.get(a, None), row.get(b, None)
                    # robust missing check (works for None, NaN, pd.NA, empty string)
                    if va is None or vb is None:
                        continue
                    if pd.isna(va) or pd.isna(vb):
                        continue
                    if va == "" or vb == "":
                        continue
                    pair = ((a, b), (va, vb))
                    if pair in global_last_seen_pair:
                        j, jts = global_last_seen_pair[pair]
                        dt = (ts - jts).total_seconds()
                        if 0 < dt <= window_seconds and j != idx:
                            g.add_edge(j, idx, reason=f"ip_pair:{a}->{b}", dt_seconds=float(dt))
                    global_last_seen_pair[pair] = (idx, ts)

            win.append((idx, ts))
            prev_idx, prev_ts = idx, ts

    return g