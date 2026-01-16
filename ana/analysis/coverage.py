import pandas as pd

def step_coverage(events: pd.DataFrame):
    '''
    {source: unique_steps}
    '''
    if events is None or len(events) == 0:
        return {}
    if "source" not in events.columns or "step" not in events.columns:
        return {}
    return (
        events.dropna(subset=["step"])
        .groupby("source")["step"]
        .nunique()
        .to_dict()
    )

def step_coverage_report(events: pd.DataFrame, expected_steps: list | None = None) -> dict:
    '''
    - observed_steps
    - (optional) coverage_ratio vs expected_steps
    '''
    if events is None or len(events) == 0 or "step" not in events.columns:
        return {"observed_steps": [], "coverage_ratio": None}
    
    observed = sorted(events.dropna(subset=["step"])["step"].unique().tolist())
    if expected_steps:
        exp = set(expected_steps)
        ratio = (len(set(observed) & exp) / max(len(exp), 1))
    else:
        ratio = None
    return {"observed_steps": observed, "coverage_ratio": ratio}

def marginal_contribution(recon_with_all: float, recon_without: float) -> float:
    return float(recon_with_all - recon_without)

