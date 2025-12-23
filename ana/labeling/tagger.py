import re
from rules import RULES

def tag_steps(events):
    events = events.copy()
    events["step"] = None

    for step, pats in RULES.items():
        mask = False
        for p in pats:
            mask |= events["raw"].str.contains(p, case=False, na=False)
        events.loc[mask, "step"] = step

    return events
