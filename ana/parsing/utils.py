'''
 # @ Create Time: 2026-01-06 12:02:09
 # @ Modified time: 2026-01-06 12:02:11
 # @ Description: support functions for parsing modules like XML format data
 '''

from pathlib import Path
from typing import Dict, Any
import pandas as pd
import xml.etree.ElementTree as ET

def _strip_ns(tag: str) -> str:
    return tag.split('}', 1)[-1] if '}' in tag else tag

def _extract_from_eventdata_xml(xml_text: str) -> Dict[str, Any]:
    '''
    Extract <Data Name="X">VALUE</Data> into dict X->VALUE.
    Compatible with:
      - <EventData>...</EventData>
      - <DataItem ...><EventData>...</EventData></DataItem>
    '''    
    if not isinstance(xml_text, str):
        return {}
    s = xml_text.strip()
    if not s or "<" not in s:
        return {}
    
    # find first '<' to avoid leading junk
    s = s[s.find("<") :]

    root = None
    try:
        root = ET.fromstring(s)
    except Exception:
        # sometimes multiple roots -> wrap
        try:
            root = ET.fromstring(f"<Root>{s}</Root>")
        except Exception:
            return {}

    eventdata = None
    if _strip_ns(root.tag).lower() == "eventdata":
        eventdata = root
    else:
        for node in root.iter():
            if _strip_ns(node.tag).lower() == "eventdata":
                eventdata = node
                break
    if eventdata is None:
        return {}
    
    out: Dict[str, Any] = {}
    for child in list(eventdata):
        if _strip_ns(child.tag).lower() != "data":
            continue
        name = child.attrib.get("Name") or child.attrib.get("name") or ""
        if not name:
            continue
        out[name] = (child.text or "").strip()
    return out


def parse_azure_events(path: str | Path) -> pd.DataFrame:
    
