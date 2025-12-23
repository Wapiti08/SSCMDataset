def failure_taxonomy(events):
    out = []
    for src, df in events.groupby("source"):
        out.append({
            "source": src,
            "missing_subject_ratio": (df["subject"] == "").mean(),
            "missing_object_ratio": (df["object"] == "").mean(),
        })
    return out
