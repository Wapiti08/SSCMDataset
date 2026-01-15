import networkx as nx
import pandas as pd

def _choose_anchors(step_events: pd.DataFrame, topk_per_step: int=1):
    '''
    
    '''



def reconstruct_chain(graph, step_events):
    anchors = (
        step_events.groupby("step")["ts"]
        .idxmin()
        .tolist()
    )
    anchors = sorted(anchors)

    chain = []
    for a, b in zip(anchors, anchors[1:]):
        if nx.has_path(graph, a, b):
            chain.append((a, b, "connected"))
        else:
            chain.append((a, b, "gap"))
    return chain