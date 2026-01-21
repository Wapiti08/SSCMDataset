'''
 # @ Create Time: 2026-01-21 10:02:41
 # @ Modified time: 2026-01-21 10:02:44
 # @ Description: extract ttps from different scenarios and do stastical analysis, provide evidence for ttps alignment
 '''

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import re

SCENARIO_ORDER = ["Stegano", "Starter", "Parallel", "NPMEX", "3CX", "CloudEX", "LayerInj"]

TID_RE = re.compile(r"^T\d{4}(\.\d{3})?$") 

def normalize_tactic(t: str) -> str:
    # unify "Defense Evasion" -> "defense-evasion"
    t = t.strip().lower()
    t = t.replace("_", "-").replace(" ", "-")
    t = re.sub(r"-+", "-", t)
    return t

def safe_load_json(p: Path) -> Optional[Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def extract_ttps_recursive(obj: Any) -> List[Tuple[str, Optional[str]]]:
    """
    Recursively find techniqueID fields anywhere in JSON.
    Returns list of (technique_id, tactic_or_none)
    """
    hits: List[Tuple[str, Optional[str]]] = []

    if isinstance(obj, dict):
        # direct hit: {"techniqueID": "Txxxx", "tactic": "..."}
        if "techniqueID" in obj and isinstance(obj["techniqueID"], str):
            tid = obj["techniqueID"].strip()
            if TID_RE.match(tid):
                tactic = None
                # ATT&CK Navigator layer often has "tactic"
                if isinstance(obj.get("tactic"), str) and obj.get("tactic").strip():
                    tactic = normalize_tactic(obj["tactic"])
                hits.append((tid, tactic))

        # recurse
        for v in obj.values():
            hits.extend(extract_ttps_recursive(v))

    elif isinstance(obj, list):
        for it in obj:
            hits.extend(extract_ttps_recursive(it))

    return hits

def scenario_dir_mapping(root: Path) -> Dict[str, Path]:
    """
    Map scenario name -> directory path.
    Supports:
      - directories named like stegano/starter/... (case-insensitive)
      - directories named sc1..sc7 (mapped by numeric order to SCENARIO_ORDER)
    """
    dirs = [d for d in root.iterdir() if d.is_dir()]
    name_to_dir = {d.name.lower(): d for d in dirs}

    # prefer exact scenario-name directories if present
    if any(s.lower() in name_to_dir for s in SCENARIO_ORDER):
        out: Dict[str, Path] = {}
        for s in SCENARIO_ORDER:
            if s.lower() in name_to_dir:
                out[s] = name_to_dir[s.lower()]
        return out

    # otherwise fall back to sc* directories
    sc_dirs = [d for d in dirs if d.name.lower().startswith("sc")]
    def sc_key(d: Path):
        m = re.search(r"(\d+)", d.name)
        return int(m.group(1)) if m else 10**9
    sc_dirs = sorted(sc_dirs, key=sc_key)

    out = {}
    for i, d in enumerate(sc_dirs[:len(SCENARIO_ORDER)]):
        out[SCENARIO_ORDER[i]] = d
    return out

def collect_scenario_ttps(sc_dir: Path) -> Tuple[Set[str], Set[str], Dict[str, Set[str]]]:
    """
    Returns:
      tactics_set, techniques_set, tid_to_sources (optional use)
    """
    tactics: Set[str] = set()
    techniques: Set[str] = set()
    tid_to_sources: Dict[str, Set[str]] = {}

    for p in sc_dir.rglob("*.json"):
        j = safe_load_json(p)
        if j is None:
            continue

        hits = extract_ttps_recursive(j)
        if not hits:
            continue

        for tid, tact in hits:
            techniques.add(tid)
            if tact:
                tactics.add(tact)
            tid_to_sources.setdefault(tid, set()).add(str(p))
    return tactics, techniques, tid_to_sources

def shorten_list(items: List[str], limit: int = 25) -> str:
    if len(items) <= limit:
        return ", ".join(items) if items else "—"
    head = items[:limit]
    return f"{', '.join(head)}, …(+{len(items)-limit})"


def main():
    ROOT = Path(r"../sanidata") 

    mapping = scenario_dir_mapping(ROOT)
    if not mapping:
        raise SystemExit(f"No scenario folders found under: {ROOT.resolve()}")

    rows_for_report = []
    rows_full_csv = []

    for scenario, sc_dir in mapping.items():
        tactics, techniques, tid_sources = collect_scenario_ttps(sc_dir)

        tactics_sorted = sorted(tactics)
        techniques_sorted = sorted(techniques)

        rows_for_report.append({
            "Scenario": scenario,
            "Tactics": ", ".join(tactics_sorted) if tactics_sorted else "—",
            "Techniques": shorten_list(techniques_sorted, limit=25),
            "Count": str(len(techniques_sorted)),
            "Time Span": "—",  # 你说先不做
        })

        # full export (1 row per technique)
        for tid in techniques_sorted:
            rows_full_csv.append({
                "Scenario": scenario,
                "Technique": tid,
                "Tactics": ";".join(sorted(tactics)) if tactics else "",
                "SourceFiles": ";".join(sorted(tid_sources.get(tid, []))),
            })

    # print markdown table for report
    headers = ["Scenario", "Tactics", "Techniques", "Count", "Time Span"]
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join(["---"] * len(headers)) + "|")
    for r in rows_for_report:
        print("| " + " | ".join(r[h] for h in headers) + " |")

    # write full csv
    out_csv = Path("scenario_ttps_full.csv")
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Scenario", "Technique", "Tactics", "SourceFiles"])
        w.writeheader()
        w.writerows(rows_full_csv)

    print(f"\n[OK] Wrote full technique list -> {out_csv.resolve()}")

if __name__ == "__main__":
    main()