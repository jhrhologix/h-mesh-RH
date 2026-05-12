#!/usr/bin/env python3
"""Audit centered distribution of O2 post-response residuals."""

from __future__ import annotations

import argparse
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_INPUT = "notes/prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"
DEFAULT_OUT_DIR = "notes"
DEFAULT_DOC = "docs/RH/notes/Prime_Mesh_R2Q_O2_Centered_Residual_Distribution_Audit_v1.md"
RESIDUALS = ["fitted", "canonical_scaled", "canonical_raw"]


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def quantile(series: pd.Series, q: float) -> float:
    return float(series.quantile(q))


def summarize(df: pd.DataFrame, label: str, residual: str) -> dict[str, object]:
    e = df[f"{residual}_E_post"].astype(float)
    denom = df["denom_sqrt_h_logB"].astype(float)
    z = e / denom
    neg = np.maximum(0.0, -z)
    row: dict[str, object] = {
        "scope": label,
        "residual": residual,
        "rows": int(len(df)),
        "mean_z": float(z.mean()),
        "median_z": float(z.median()),
        "std_z": float(z.std(ddof=0)),
        "rms_z": float(np.sqrt(np.mean(z * z))),
        "min_z": float(z.min()),
        "max_z": float(z.max()),
        "neg_frac": float((z < 0).mean()),
        "neg_mean": float(neg.mean()),
        "neg_max": float(neg.max()),
        "q01_z": quantile(z, 0.01),
        "q05_z": quantile(z, 0.05),
        "q10_z": quantile(z, 0.10),
        "q90_z": quantile(z, 0.90),
        "q95_z": quantile(z, 0.95),
        "q99_z": quantile(z, 0.99),
        "pass_Q_le_1_frac": float((neg <= 1.0).mean()),
        "pass_Q_le_0p1_frac": float((neg <= 0.1).mean()),
        "pass_Q_le_0p05_frac": float((neg <= 0.05).mean()),
    }
    worst_idx = neg.idxmax()
    worst = df.loc[worst_idx]
    row.update(
        {
            "worst_block_id": int(worst["block_id"]),
            "worst_p_star": int(worst["p_star"]),
            "worst_y": int(worst["y"]),
            "worst_h": int(worst["h"]),
            "worst_is_tail": bool(worst["is_tail"]),
            "worst_neg_Q": float(neg.loc[worst_idx]),
            "worst_z": float(z.loc[worst_idx]),
        }
    )
    return row


def build_summaries(df: pd.DataFrame, min_rows: int) -> pd.DataFrame:
    scopes: list[tuple[str, pd.DataFrame]] = [("global", df)]
    if "is_tail" in df.columns:
        for value, part in df.groupby("is_tail", dropna=False):
            scopes.append((f"tail:{value}", part))
    for col in ["depth_bin", "scale_bin", "mu_bin", "decade"]:
        if col in df.columns:
            for value, part in df.groupby(col, dropna=False):
                if len(part) >= min_rows:
                    scopes.append((f"{col}:{value}", part))
    rows = []
    for label, part in scopes:
        if len(part) == 0:
            continue
        for residual in RESIDUALS:
            if f"{residual}_E_post" in part.columns:
                rows.append(summarize(part, label, residual))
    return pd.DataFrame(rows)


def write_doc(doc_path: Path, summary: dict[str, object], scopes: pd.DataFrame) -> None:
    lines = [
        "# Prime Mesh R2Q - O2 Centered Residual Distribution Audit",
        "",
        f"**Document:** `{doc_path.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-06",
        "**Status:** O2-B centered residual distribution audit",
        "",
        "## 1. Purpose",
        "",
        "This audit checks whether the post-response residual normalized by \\(\\sqrt h\\log^2p^*\\) behaves like a centered bounded fluctuation.",
        "",
        "## 2. Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in summary.items():
        lines.append(f"| `{key}` | {value} |")
    lines += [
        "",
        "## 3. Scope Table",
        "",
        scopes.to_markdown(index=False),
        "",
        "## 4. Interpretation",
        "",
        "Small negative maxima and stable quantiles support O2-B. The canonical scaled residual is the theorem-facing object; fitted residual is the exact orthogonal projection comparator.",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
    ]
    doc_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    parser.add_argument("--doc", default=DEFAULT_DOC)
    parser.add_argument("--min-rows", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    input_path = (root / args.input).resolve()
    out_dir = (root / args.out_dir).resolve()
    doc_path = (root / args.doc).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    doc_path.parent.mkdir(parents=True, exist_ok=True)

    log(f"Reading {input_path}")
    df = pd.read_csv(input_path)
    scopes = build_summaries(df, args.min_rows)
    canonical_global = scopes[(scopes["scope"] == "global") & (scopes["residual"] == "canonical_scaled")].iloc[0]
    fitted_global = scopes[(scopes["scope"] == "global") & (scopes["residual"] == "fitted")].iloc[0]
    canonical_tail = scopes[(scopes["scope"] == "tail:True") & (scopes["residual"] == "canonical_scaled")]
    summary = {
        "rows": int(len(df)),
        "canonical_global_mean_z": float(canonical_global["mean_z"]),
        "canonical_global_std_z": float(canonical_global["std_z"]),
        "canonical_global_min_z": float(canonical_global["min_z"]),
        "canonical_global_neg_max": float(canonical_global["neg_max"]),
        "canonical_global_neg_frac": float(canonical_global["neg_frac"]),
        "canonical_tail_neg_max": float(canonical_tail.iloc[0]["neg_max"]) if len(canonical_tail) else math.nan,
        "fitted_global_mean_z": float(fitted_global["mean_z"]),
        "fitted_global_neg_max": float(fitted_global["neg_max"]),
        "fitted_global_neg_frac": float(fitted_global["neg_frac"]),
        "canonical_pass_Q_le_1_frac": float(canonical_global["pass_Q_le_1_frac"]),
        "canonical_pass_Q_le_0p1_frac": float(canonical_global["pass_Q_le_0p1_frac"]),
        "canonical_pass_Q_le_0p05_frac": float(canonical_global["pass_Q_le_0p05_frac"]),
        "worst_canonical_block_id": int(canonical_global["worst_block_id"]),
        "worst_canonical_p_star": int(canonical_global["worst_p_star"]),
        "worst_canonical_h": int(canonical_global["worst_h"]),
    }
    prefix = out_dir / "prime_mesh_r2q_o2_centered_residual_distribution_audit"
    summary_path = prefix.with_name(prefix.name + "_summary.csv")
    scopes_path = prefix.with_name(prefix.name + "_scopes.csv")
    pd.DataFrame([summary]).to_csv(summary_path, index=False)
    scopes.to_csv(scopes_path, index=False)
    write_doc(doc_path, summary, scopes)

    log(f"Wrote {summary_path}")
    log(f"Wrote {scopes_path}")
    log(f"Wrote {doc_path}")
    for key, value in summary.items():
        log(f"{key} = {value}")


if __name__ == "__main__":
    main()
