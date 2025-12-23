'''
 # @ Create Time: 2025-12-21 19:30:19
 # @ Modified time: 2025-12-23 16:30:21
 # @ Description: as network semantic enrichment & corroboration source
 '''

import json
import pandas as pd

def parse_suricata_eve(path: str) -> pd.DataFrame:
    '''
    for cross-correlating network events with host events
    '''
    rows = []
    with open(path, 'r', erros="ignore") as f:
        for line in f:
            try:
                e = json.loads(line)
            except Exception:
                continue

            ts = pd.to_datetime(e.get("timestamp"), utc=True, errors="coerce")
            if pd.isna(ts):
                continue

            etype = e.get("event_type")

            # ------- HTTP/ fileinfo only --------
            if etype in {"http", "fileinfo"}:
                rows.append({
                    "ts": ts,
                    "host": "network_sensor",
                    "source": "suricata",
                    "event_type": "network",
                    "action": etype,
                    "subject": f"{e.get('src_ip')}:{e.get('src_port')}",
                    "object": f"{e.get('dest_ip')}:{e.get('dest_port')}",
                    "proto": e.get("proto"),
                    "raw": json.dumps(e.get(etype, {})),
                    "extra": e,
                })

    return pd.DataFrame(rows)

