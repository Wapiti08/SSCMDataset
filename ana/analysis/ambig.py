import pandas as pd

def ambiguity(events):
    '''
    step ambiguity metric
    '''
    if events is None or len(events) == 0 or "step" not in events.columns:
        return {}
    return (
        events.dropna(subset=["step"])
        .groupby("step")
        .size()
        .to_dict()
    )

def ambiguity_report(events: pd.DataFrame) -> dict:
    """
    - count_by_step
    - time_span_seconds_by_step
    - entity_spread_by_step（how many host/user/ip can be covered in one step）
    """
    if events is None or len(events) == 0 or "step" not in events.columns or "ts" not in events.columns:
        return {"count_by_step": {}, "time_span_seconds_by_step": {}, "entity_spread_by_step": {}}

    df = events.dropna(subset=["step", "ts"]).copy()

    count = df.groupby("step").size().to_dict()
    span = (df.groupby("step")["ts"].max() - df.groupby("step")["ts"].min()).dt.total_seconds().to_dict()

    spread = {}
    for step, sdf in df.groupby("step"):
        spread[step] = {
            "hosts": int(sdf["host"].nunique()) if "host" in sdf.columns else None,
            "users": int(sdf["user"].nunique()) if "user" in sdf.columns else None,
            "src_ips": int(sdf["src_ip"].nunique()) if "src_ip" in sdf.columns else None,
            "dst_ips": int(sdf["dst_ip"].nunique()) if "dst_ip" in sdf.columns else None,
        }

    return {
        "count_by_step": count,
        "time_span_seconds_by_step": span,
        "entity_spread_by_step": spread,
    }


