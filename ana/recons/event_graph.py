import networkx as nx

def build_event_graph(events, window_seconds=60):
    '''
    event-level temporal dependency graph'''
    g = nx.DiGraph()
    for i, r in events.iterrows():
        g.add_node(i, **r.to_dict())

    for host, df in events.groupby("host"):
        df = df.sort_values("ts")
        for i in range(len(df)):
            for j in range(i):
                dt = (df.iloc[i]["ts"] - df.iloc[j]["ts"]).total_seconds()
                if 0 < dt <= window_seconds:
                    g.add_edge(df.index[j], df.index[i])
    return g