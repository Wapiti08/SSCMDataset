from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import pandas as pd


_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def _is_valid_ipv4(ip: str) -> bool:
    try:
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        for p in parts:
            if p == "" or (len(p) > 1 and p.startswith("0")):
                # reject ambiguous octets like 001
                return False
            n = int(p)
            if n < 0 or n > 255:
                return False
        return True
    except Exception:
        return False


@dataclass(frozen=True)
class ScenarioIOCs:
    scenario_id: str
    ips: Tuple[str, ...] = ()
    ports: Tuple[int, ...] = ()
    package_names: Tuple[str, ...] = ()


def extract_iocs_from_readme(readme_path: str | Path) -> ScenarioIOCs:
    """
    Best-effort IoC extraction from scenario readme.md.

    The README formats vary, so this parser is intentionally conservative:
    - IPs: all valid IPv4 addresses found anywhere in the file
    - Ports: parses lines containing "suspicious port"
    - Package names: parses lines around "package name"
    """
    p = Path(readme_path)
    txt = p.read_text(errors="ignore")

    # scenario id like "sc1" from path
    scenario_id = p.parent.name

    ips: Set[str] = set()
    for m in _IPV4_RE.findall(txt):
        if _is_valid_ipv4(m):
            ips.add(m)

    ports: Set[int] = set()
    pkg: Set[str] = set()

    lines = txt.splitlines()
    for ln in lines:
        low = ln.lower()
        if "suspicious port" in low:
            # e.g. "- suspicious port: 443 (HTTPS ...)"
            m = re.search(r"(\d{2,5})", ln)
            if m:
                try:
                    v = int(m.group(1))
                    if 0 < v < 65536:
                        ports.add(v)
                except Exception:
                    pass

        if "package name" in low:
            # e.g. "- package name: colorsapi-6.6.7 (with setup.py)"
            if ":" in ln:
                after = ln.split(":", 1)[1]
            else:
                after = ln
            # split by common delimiters and keep token-like pieces
            cand = (
                after.replace("(", ",")
                .replace(")", ",")
                .replace("—", ",")
                .replace(";", ",")
            )
            for t in cand.split(","):
                t = t.strip().strip("`").strip()
                if not t:
                    continue
                # keep moderately strict "name-version" tokens
                if re.fullmatch(r"[A-Za-z0-9_]+-[A-Za-z0-9_.]+", t):
                    pkg.add(t)

    return ScenarioIOCs(
        scenario_id=scenario_id,
        ips=tuple(sorted(ips)),
        ports=tuple(sorted(ports)),
        package_names=tuple(sorted(pkg)),
    )


def load_iocs_from_scenarios_readmes(
    scenarios_root: str | Path,
    scenario_glob: str = "sc*/readme.md",
) -> Dict[str, ScenarioIOCs]:
    root = Path(scenarios_root)
    out: Dict[str, ScenarioIOCs] = {}
    for p in sorted(root.glob(scenario_glob)):
        try:
            iocs = extract_iocs_from_readme(p)
            out[iocs.scenario_id] = iocs
        except Exception:
            # keep best-effort; caller can log if needed
            continue
    return out


def _duration_hours_from_ts(df: pd.DataFrame, ts_col: str = "ts") -> Optional[float]:
    if df is None or len(df) == 0 or ts_col not in df.columns:
        return None
    s = pd.to_datetime(df[ts_col], errors="coerce")
    s = s.dropna()
    if len(s) == 0:
        return None
    dt = (s.max() - s.min()).total_seconds()
    if dt <= 0:
        return None
    return float(dt / 3600.0)


def eval_step_false_positives_on_benign(
    tagged: pd.DataFrame,
    *,
    run_id: str = "benign",
    ts_col: str = "ts",
    step_col: str = "step",
) -> pd.DataFrame:
    """
    Step-level FP evaluation on pure benign data (all-negative ground truth).

    Returns a single-row DataFrame with:
      - n_events, n_fp_events, fp_rate
      - duration_hours, fp_per_hour (if ts available)
      - fp_by_step_json (compact dict serialized as JSON-like string)
    """
    if tagged is None:
        tagged = pd.DataFrame()

    n_events = int(len(tagged))
    if n_events and step_col in tagged.columns:
        fp_events = tagged.dropna(subset=[step_col]).copy()
        fp_events = fp_events[fp_events[step_col].astype(str).str.strip() != ""]
    else:
        fp_events = tagged.iloc[0:0].copy()

    n_fp = int(len(fp_events))
    fp_rate = (n_fp / n_events) if n_events else 0.0

    duration_h = _duration_hours_from_ts(tagged, ts_col=ts_col)
    fp_per_hour = (n_fp / duration_h) if duration_h and duration_h > 0 else None

    by_step = {}
    if n_fp and step_col in fp_events.columns:
        by_step = fp_events[step_col].astype(str).value_counts().to_dict()

    # stable ordering for readability
    by_step_items = ", ".join([f"{k}:{int(v)}" for k, v in sorted(by_step.items(), key=lambda x: (-x[1], x[0]))])
    by_step_str = "{" + by_step_items + "}"

    return pd.DataFrame(
        [
            {
                "run_id": run_id,
                "n_events": n_events,
                "n_fp_events": n_fp,
                "fp_rate": float(fp_rate),
                "duration_hours": float(duration_h) if duration_h is not None else None,
                "fp_per_hour": float(fp_per_hour) if fp_per_hour is not None else None,
                "fp_by_step": by_step_str,
            }
        ]
    )


def eval_attack_ioc_matches_in_benign(
    events: pd.DataFrame,
    iocs: Sequence[ScenarioIOCs] | Dict[str, ScenarioIOCs],
    *,
    run_id: str = "benign",
    max_samples: int = 5,
) -> pd.DataFrame:
    """
    Sanity check: benign data should NOT match attack IoCs (IPs/ports/package names).

    Output is a row-per-ioc-type table with counts + small samples.
    """
    if events is None:
        events = pd.DataFrame()

    if isinstance(iocs, dict):
        ioc_list = list(iocs.values())
    else:
        ioc_list = list(iocs)

    all_ips: Set[str] = set()
    all_ports: Set[int] = set()
    all_pkgs: Set[str] = set()
    for sc in ioc_list:
        all_ips.update(sc.ips)
        all_ports.update(sc.ports)
        all_pkgs.update(sc.package_names)

    def _collect_text_columns(df: pd.DataFrame) -> List[str]:
        # prefer canonical/log-like fields but remain schema tolerant
        preferred = [
            "raw",
            "_raw",
            "message",
            "Message",
            "cmdline",
            "CommandLine",
            "process",
            "ProcessName",
            "exe",
            "Executable",
            "dst_ip",
            "dest_ip",
            "DestinationIP",
            "RemoteIP",
            "src_ip",
            "SourceIP",
            "uri",
            "url",
            "hostname",
            "host",
        ]
        cols = [c for c in preferred if c in df.columns]
        if cols:
            return cols
        # fallback: small set of object-like columns
        return [c for c in df.columns if df[c].dtype == object][:12]

    text_cols = _collect_text_columns(events)

    out_rows: List[dict] = []

    # --- IP matches ---
    ip_hits = 0
    ip_samples: List[str] = []
    if len(all_ips):
        if "dst_ip" in events.columns:
            mask = events["dst_ip"].astype(str).isin(all_ips)
            hits_df = events.loc[mask]
            ip_hits = int(mask.sum())
        else:
            pat = re.compile("|".join(re.escape(x) for x in sorted(all_ips)))
            joined = events[text_cols].astype(str).agg(" | ".join, axis=1) if len(events) else pd.Series([], dtype=str)
            mask = joined.str.contains(pat, na=False)
            hits_df = events.loc[mask]
            ip_hits = int(mask.sum())
        for _, r in hits_df.head(max_samples).iterrows():
            ip_samples.append(" | ".join(str(r.get(c, ""))[:120] for c in text_cols))

    out_rows.append(
        {
            "run_id": run_id,
            "ioc_type": "attack_ip",
            "n_iocs": int(len(all_ips)),
            "n_matches": int(ip_hits),
            "samples": " || ".join(ip_samples),
        }
    )

    # --- Port matches ---
    port_hits = 0
    port_samples: List[str] = []
    if len(all_ports):
        port_cols = [c for c in ["dst_port", "dest_port", "DestinationPort", "RemotePort"] if c in events.columns]
        if port_cols:
            col = port_cols[0]
            s = pd.to_numeric(events[col], errors="coerce").astype("Int64")
            mask = s.isin(list(all_ports))
            hits_df = events.loc[mask]
            port_hits = int(mask.sum())
        else:
            pat = re.compile(r"\b(" + "|".join(str(p) for p in sorted(all_ports)) + r")\b")
            joined = events[text_cols].astype(str).agg(" | ".join, axis=1) if len(events) else pd.Series([], dtype=str)
            mask = joined.str.contains(pat, na=False)
            hits_df = events.loc[mask]
            port_hits = int(mask.sum())

        for _, r in hits_df.head(max_samples).iterrows():
            port_samples.append(" | ".join(str(r.get(c, ""))[:120] for c in text_cols))

    out_rows.append(
        {
            "run_id": run_id,
            "ioc_type": "attack_port",
            "n_iocs": int(len(all_ports)),
            "n_matches": int(port_hits),
            "samples": " || ".join(port_samples),
        }
    )

    # --- Package name matches (best-effort text search) ---
    pkg_hits = 0
    pkg_samples: List[str] = []
    if len(all_pkgs) and len(events):
        pat = re.compile("|".join(re.escape(x) for x in sorted(all_pkgs)), flags=re.IGNORECASE)
        joined = events[text_cols].astype(str).agg(" | ".join, axis=1)
        mask = joined.str.contains(pat, na=False)
        hits_df = events.loc[mask]
        pkg_hits = int(mask.sum())
        for _, r in hits_df.head(max_samples).iterrows():
            pkg_samples.append(" | ".join(str(r.get(c, ""))[:120] for c in text_cols))

    out_rows.append(
        {
            "run_id": run_id,
            "ioc_type": "attack_package_name",
            "n_iocs": int(len(all_pkgs)),
            "n_matches": int(pkg_hits),
            "samples": " || ".join(pkg_samples),
        }
    )

    return pd.DataFrame(out_rows)

