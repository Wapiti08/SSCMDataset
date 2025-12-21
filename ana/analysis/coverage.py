def step_coverage(events):
    return (
        events.dropna(subset=["step"])
        .groupby("source")["step"]
        .nunique()
        .to_dict()
    )