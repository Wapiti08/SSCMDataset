#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Recompute LaTeX Table: Cross-scenario summary by *source-budget* (paper-facing).

Key change (requested):
- Treat `azure_events` as a composite telemetry stream (multiple evidence channels). Therefore it must NOT
  be treated as a true single-source baseline nor a true 2-source pair when paired with syslog, etc.

Implementation:
- We compute an *effective* source count:
    effective_n_sources = len(source_set.split("+")) + sum((w-1) for each composite source present)
  with COMPOSITE_SOURCE_WEIGHTS = {"azure_events": 3} by default.
- Then define the *budget mode*:
    single if effective_n_sources==1
    combo2 if effective_n_sources==2
    multi  if effective_n_sources>=3

This lets rows like:
- source_set="azure_events"            -> effective_n_sources=3 -> budget_mode="multi"
- source_set="syslog+azure_events"     -> effective_n_sources=1+3=4 -> budget_mode="multi"

Metrics (same as before):
- Tag Cov (wtd.)   = sum(n_tagged_steps) / sum(n_expected_steps)
- Chain Cov (wtd.) = sum(n_chain_steps) / sum(n_expected_steps)
- StepR (wtd.)     = weighted avg(step_recall, weights=n_expected_steps)
- ChainR (wtd.)    = weighted avg(chain_recall, weights=n_expected_steps)
- StepP/ChainP     = mean precision across scenarios (NaN -> 0)
- Recon (mean)     = mean reconstructability across scenarios (NaN -> 0)

Avg rows are computed "scenario-first" to avoid overweighting scenarios that have many configs.

Usage:
  python calc_source_budget_table_budgeted.py /path/to/total_scenarios.csv
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

# ---- composite stream budgeting ----
COMPOSITE_SOURCE_WEIGHTS: Dict[str, int] = {
    "azure_events": 3,   # counts as 3 sources total for budgeting
}

def parse_sources(source_set: str) -> List[str]:
    return [s for s in str(source_set).split("+") if s]

def effective_n_sources(source_set: str, weights: Dict[str, int] = COMPOSITE_SOURCE_WEIGHTS) -> int:
    srcs = parse_sources(source_set)
    n = len(srcs)
    for src, w in (weights or {}).items():
        if src in srcs:
            n += (int(w) - 1)
    return n

def budget_mode_from_source_set(source_set: str) -> str:
    n = effective_n_sources(source_set)
    if n <= 1:
        return "single"
    if n == 2:
        return "combo2"
    return "multi"

# ---- aggregation helpers ----
NUM_COLS = [
    "n_expected_steps","n_tagged_steps","n_chain_steps",
    "step_recall","chain_recall","step_precision","chain_precision",
    "reconstructability"
]

def wtd_avg(values: pd.Series, weights: pd.Series) -> float:
    v = pd.to_numeric(values, errors="coerce").fillna(0.0).to_numpy(dtype=float)
    w = pd.to_numeric(weights, errors="coerce").fillna(0.0).to_numpy(dtype=float)
    denom = w.sum()
    return float((v * w).sum() / denom) if denom > 0 else float("nan")

def summarize(rows: pd.DataFrame) -> dict:
    rows = rows.copy()
    for c in NUM_COLS:
        if c in rows.columns:
            rows[c] = pd.to_numeric(rows[c], errors="coerce")

    rows["n_expected_steps"] = rows["n_expected_steps"].fillna(0).astype(int)
    rows["n_tagged_steps"] = rows["n_tagged_steps"].fillna(0.0)
    rows["n_chain_steps"] = rows["n_chain_steps"].fillna(0.0)

    w = rows["n_expected_steps"].astype(float)
    denom = float(w.sum())

    tag_cov = float(rows["n_tagged_steps"].sum() / denom) if denom > 0 else float("nan")
    chain_cov = float(rows["n_chain_steps"].sum() / denom) if denom > 0 else float("nan")

    return {
        "Scn.": int(rows["scenario"].nunique()),
        "Tag Cov. (wtd.)": tag_cov,
        "Chain Cov. (wtd.)": chain_cov,
        "StepR (wtd.)": wtd_avg(rows["step_recall"], w),
        "ChainR (wtd.)": wtd_avg(rows["chain_recall"], w),
        "StepP (mean)": pd.to_numeric(rows["step_precision"], errors="coerce").fillna(0.0).mean(),
        "ChainP (mean)": pd.to_numeric(rows["chain_precision"], errors="coerce").fillna(0.0).mean(),
        "Recon. (mean)": pd.to_numeric(rows["reconstructability"], errors="coerce").fillna(0.0).mean(),
    }

def summarize_by_scenario_then_aggregate(rows: pd.DataFrame) -> dict:
    r = rows.copy()
    for c in NUM_COLS:
        if c in r.columns:
            r[c] = pd.to_numeric(r[c], errors="coerce")

    per = (r.groupby("scenario", as_index=False)
             .agg(
                 n_expected_steps=("n_expected_steps","max"),
                 n_tagged_steps=("n_tagged_steps","mean"),
                 n_chain_steps=("n_chain_steps","mean"),
                 step_recall=("step_recall","mean"),
                 chain_recall=("chain_recall","mean"),
                 step_precision=("step_precision","mean"),
                 chain_precision=("chain_precision","mean"),
                 reconstructability=("reconstructability","mean"),
             ))
    return summarize(per)

def select_best_per_scenario(rows: pd.DataFrame, key: str = "reconstructability") -> pd.DataFrame:
    r = rows.copy()
    for c in ["reconstructability","step_recall","chain_recall","step_precision","chain_precision","n_tagged_steps"]:
        if c in r.columns:
            r[c] = pd.to_numeric(r[c], errors="coerce").fillna(0.0)

    r = r.sort_values(
        ["scenario", key, "step_recall", "chain_recall", "step_precision", "chain_precision", "n_tagged_steps"],
        ascending=[True, False, False, False, False, False, False],
    )
    return r.groupby("scenario", as_index=False).head(1).reset_index(drop=True)

def dedupe_by_scenario_source_set(df: pd.DataFrame) -> pd.DataFrame:
    """If a scenario accidentally outputs duplicate rows for the same source_set (e.g., SC5 azure_events),
    keep the best one to avoid double-counting.
    """
    d = df.copy()
    for c in ["reconstructability","step_recall","chain_recall","step_precision","chain_precision","n_tagged_steps"]:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0.0)

    d = d.sort_values(
        ["scenario", "source_set", "reconstructability","step_recall","chain_recall","step_precision","chain_precision","n_tagged_steps"],
        ascending=[True, True, False, False, False, False, False, False]
    )
    return d.drop_duplicates(subset=["scenario","source_set"], keep="first").reset_index(drop=True)

# ---- LaTeX helpers ----
METRIC_COLS = [
    "Tag Cov. (wtd.)","Chain Cov. (wtd.)",
    "StepR (wtd.)","ChainR (wtd.)",
    "StepP (mean)","ChainP (mean)",
    "Recon. (mean)",
]

def mark_best_second(summary_df: pd.DataFrame) -> dict:
    best = {}
    second = {}
    for col in METRIC_COLS:
        vals = pd.to_numeric(summary_df[col], errors="coerce").astype(float)
        maxv = float(vals.max())
        best[col] = maxv

        uniq = sorted(set(vals.tolist()), reverse=True)
        sec = None
        for v in uniq:
            if v < maxv - 1e-12:
                sec = float(v)
                break
        second[col] = sec
    return {"best": best, "second": second}

def fmt_cell(val: float, col: str, marks: dict) -> str:
    if pd.isna(val):
        return "--"
    v = float(val)
    s = f"{v:.3f}"
    if abs(v - marks["best"][col]) < 1e-6:
        return f"\\textbf{{{s}}}"
    sec = marks["second"][col]
    if sec is not None and abs(v - sec) < 1e-6:
        return f"\\underline{{{s}}}"
    return s

def build_latex_table(summary_df: pd.DataFrame) -> str:
    marks = mark_best_second(summary_df)

    def nm(k: str) -> str:
        if k == "Single (1): audit/provenance":
            return r"Single (1): audit/provenance \cite{ProGrapher2023,NODLINK2024}"
        if k == "Single (1): Zeek":
            return r"Single (1): Zeek \cite{ZeekBeaconing2025,CobaltStrikeMetadata2025}"
        if k == "Combo (2): audit+Zeek":
            return r"Combo (2): audit+Zeek \cite{APTMCL2026,LOTLHunter2026}"
        if k == "Multi (>=3): syslog+events":
            return r"Multi ($\ge$3): syslog+events \cite{MultiSourceLogSemantic2025}"
        return k

    def scn_cell(k: str, scn: int) -> str:
        # keep the paper style: avg rows show "--"
        if "avg over" in k:
            return "--"
        return str(int(scn))

    order = [
        "Single (1): avg over all single sources",
        "Single (1): best single-source",
        "Single (1): audit/provenance",
        "Single (1): Zeek",
        "Combo (2): avg over 2-source pair",
        "Combo (2): best 2-source pair",
        "Combo (2): audit+Zeek",
        "Multi (>=3): syslog+events",
        "Multi (>=3): avg full telemetry",
        "Multi (>=3): best full telemetry",
    ]

    lines = []
    for k in order:
        r = summary_df.loc[k]
        line = (
            f"{nm(k)}\n"
            f"& {scn_cell(k, int(r['Scn.']))} "
            f"& {fmt_cell(r['Tag Cov. (wtd.)'], 'Tag Cov. (wtd.)', marks)} "
            f"& {fmt_cell(r['Chain Cov. (wtd.)'], 'Chain Cov. (wtd.)', marks)} "
            f"& {fmt_cell(r['StepR (wtd.)'], 'StepR (wtd.)', marks)} "
            f"& {fmt_cell(r['ChainR (wtd.)'], 'ChainR (wtd.)', marks)} "
            f"& {fmt_cell(r['StepP (mean)'], 'StepP (mean)', marks)} "
            f"& {fmt_cell(r['ChainP (mean)'], 'ChainP (mean)', marks)} "
            f"& {fmt_cell(r['Recon. (mean)'], 'Recon. (mean)', marks)} \\\\"
        )
        lines.append(line)

        if k == "Single (1): Zeek":
            lines.append(r"\midrule")
        if k == "Combo (2): audit+Zeek":
            lines.append(r"\midrule")

    # remove trailing midrule if any
    while lines and lines[-1].strip() == r"\midrule":
        lines.pop()

    header = r"""\begin{table*}[htbp]
\centering
\caption{Cross-scenario summary by source budget and representative combinations. Coverage/recall are weighted by expected steps (wtd.). \textbf{Bold} indicates the best value and \underline{underline} indicates the second-best value in each metric column.}
\label{tab:source-budget-summary}
\small
\setlength{\tabcolsep}{2.8pt}
\renewcommand{\arraystretch}{1.15}
\begin{tabular}{p{4.6cm}rrrrrrrr}
\toprule
Category & \makecell[r]{Scn.} &
\makecell[r]{Tag Cov.\\(wtd.)} &
\makecell[r]{Chain Cov.\\(wtd.)} &
\makecell[r]{StepR\\(wtd.)} &
\makecell[r]{ChainR\\(wtd.)} &
\makecell[r]{StepP\\(mean)} &
\makecell[r]{ChainP\\(mean)} &
\makecell[r]{Recon.\\(mean)} \\
\midrule
"""
    footer = r"""\bottomrule
\end{tabular}
\vspace{2pt}
{\footnotesize\textit{Note:} We treat \texttt{azure\_events} as a composite telemetry stream (multiple evidence channels). For budgeting, \texttt{azure\_events} counts as 3 sources, so any configuration including \texttt{azure\_events} is assigned to the multi-source bucket.}
\end{table*}
"""
    return header + "\n".join(lines) + "\n" + footer

# ---- main computation ----
def compute_table(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ensure required columns exist
    required = ["scenario","source_set","n_expected_steps","n_tagged_steps","n_chain_steps",
                "step_recall","chain_recall","step_precision","chain_precision","reconstructability"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")

    # dedupe accidental duplicates (e.g. SC5 azure_events in both single/multi)
    df = dedupe_by_scenario_source_set(df)

    # compute budget mode from source_set (ignore df['mode'])
    df["budget_mode"] = df["source_set"].apply(budget_mode_from_source_set)

    single = df[df["budget_mode"]=="single"].copy()
    combo2 = df[df["budget_mode"]=="combo2"].copy()
    multi  = df[df["budget_mode"]=="multi"].copy()

    # representative subsets
    audit_single = single[single["source_set"]=="auditd"]
    zeek_single  = single[single["source_set"]=="zeek"]
    audit_zeek   = combo2[combo2["source_set"]=="auditd+zeek"]
    syslog_events = multi[multi["source_set"]=="syslog+azure_events"]

    rows = {}
    rows["Single (1): avg over all single sources"] = summarize_by_scenario_then_aggregate(single)
    rows["Single (1): best single-source"] = summarize(select_best_per_scenario(single))
    rows["Single (1): audit/provenance"] = summarize(audit_single)
    rows["Single (1): Zeek"] = summarize(zeek_single)

    rows["Combo (2): avg over 2-source pair"] = summarize_by_scenario_then_aggregate(combo2)
    rows["Combo (2): best 2-source pair"] = summarize(select_best_per_scenario(combo2))
    rows["Combo (2): audit+Zeek"] = summarize(audit_zeek)

    rows["Multi (>=3): syslog+events"] = summarize(syslog_events)
    rows["Multi (>=3): avg full telemetry"] = summarize_by_scenario_then_aggregate(multi)
    rows["Multi (>=3): best full telemetry"] = summarize(select_best_per_scenario(multi))

    return pd.DataFrame.from_dict(rows, orient="index")

def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) >= 2 else None
    if not csv_path or not csv_path.exists():
        raise SystemExit("Usage: python calc_source_budget_table_budgeted.py /path/to/total_scenarios.csv")

    df = pd.read_csv(csv_path)
    summary_df = compute_table(df)

    with pd.option_context("display.max_columns", 999, "display.width", 160):
        print("\n=== Summary (raw numbers) ===")
        print(summary_df)

    print("\n=== LaTeX table ===")
    print(build_latex_table(summary_df))

if __name__ == "__main__":
    main()
