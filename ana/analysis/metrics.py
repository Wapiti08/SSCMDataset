def continuity_proxy(step_events, max_gap_seconds=600):
    '''
    step time continuity proxy metric
    '''
    steps = (
        step_events.groupby("step")["ts"]
        .min()
        .sort_values()
        .tolist()
    )
    ok=0
    for a, b in zip(steps, steps[1:]):
        if (b - a).total_seconds() <= max_gap_seconds:
            ok += 1
    return ok / max(len(steps) - 1, 1)