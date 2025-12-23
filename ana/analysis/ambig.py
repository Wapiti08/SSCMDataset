def ambiguity(events):
    '''
    step ambiguity metric
    '''
    return (
        events.dropna(subset=["step"])
        .groupby("step")
        .size()
        .to_dict()
    )