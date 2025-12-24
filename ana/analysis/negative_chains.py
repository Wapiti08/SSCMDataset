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
                "trigger_source": e["source"],
                "trigger_action": e["action"],
                "evidence": e["raw"],
            })

    return pd.DataFrame(failed)


