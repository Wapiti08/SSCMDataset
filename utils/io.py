from pathlib import Path
import pandas as pd

def safe_parse(parser, path: str | None, name: str):
    ''' 
    try parsing a telemetry source.
    returns empty DataFrame if missing.
    
    '''
    if path is None:
        print(f"[INFO] {name}: not configured")
        return pd.DataFrame()
    
    if not Path(path).exists():
        print(f"[INFO] {name}: file not found ({path})")
        return pd.DataFrame()
    
    try:
        df = parser(path)
        print(f"[OK] {name}: loaded {len(df)} events")
        return df
    except Exception as e:
        print(f"[WARN] {name}: failed to parse ({e})")
        return pd.DataFrame()