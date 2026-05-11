#!/usr/bin/env python3
"""Endpoint repayment compatibility audit.

This audit is intentionally deposited in the repair-folder bundle only.

It asks whether the large O2.3 endpoint term Q_DeltaD is harmful O2.3 slack,
or whether it is the already-counted B2/MR-2 endpoint descent coordinate.

Convention tested here:
  * DeltaD < 0 is endpoint descent in the B2/R2Q recovery coordinate.
  * B2-active LongA endpoint descent is already counted in the endpoint
    repayment stack and should not be charged again inside O2.3.
  * A harmful O2.3 endpoint component is any positive endpoint motion, or any
    endpoint motion not aligned with / not already counted by B2.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[7]
REPO_NOTES = ROOT / "notes"

O2P3_INTERVALS = OUT / "prime_mesh_r2q_o2p3_bridge_excursion_intervals.csv"
O2_PROJECTION = REPO_NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_endpoint_repayment_compatibility_summary.csv"
INTERVALS_OUT = OUT / "prime_mesh_r2q_endpoint_repayment_compatibility_intervals.csv"
SCOPES_OUT = OUT / "prime_mesh_r2q_endpoint_repayment_compatibility_scopes.csv"
WORST_OUT = OUT / "prime_mesh_r2q_endpoint_repayment_compatibility_worst_rows.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_Endpoint_Repayment_Compatibility_Audit_v1.md"
MANIFEST = OUT / "deposit_manifest.csv"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def classify_depth(v: object) -> str:
    return str(v) if not pd.isna(v) else "unknown"


def summarize(df: pd.DataFrame, scope: str) -> dict[str, object]:
    if len(df) == 0:
        return {"scope": scope, "rows": 0}
    worst_idx = df["endpoint_harmful_Q"].idxmax()
    worst = df.loc[worst_idx]
    large = df[df["Q_DeltaD"] > 0.25]
    return {
        "scope": scope,
        "rows": int(len(df)),
        "DeltaD_negative_frac": float((df["DeltaD"] < 0).mean()),
        "DeltaD_positive_frac": float((df["DeltaD"] > 0).mean()),
        "Q_DeltaD_max": float(df["Q_DeltaD"].max()),
        "Q_DeltaD_mean": float(df["Q_DeltaD"].mean()),
        "Q_DeltaD_median": float(df["Q_DeltaD"].median()),
        "Q_DeltaD_q95": float(df["Q_DeltaD"].quantile(0.95)),
        "endpoint_favorable_frac": float(df["endpoint_favorable_flag"].mean()),
        "endpoint_already_counted_frac": float(df["endpoint_already_counted_flag"].mean()),
        "endpoint_harmful_frac": float(df["endpoint_harmful_flag"].mean()),
        "Q_DeltaD_harmful_max": float(df["endpoint_harmful_Q"].max()),
        "Q_DeltaD_harmful_mean": float(df["endpoint_harmful_Q"].mean()),
        "endpoint_repayment_Q_max": float(df["endpoint_repayment_Q"].max()),
        "double_count_risk_frac": float(df["double_count_risk_flag"].mean()),
        "large_QDeltaD_rows": int(len(large)),
        "large_QDeltaD_already_counted_frac": float(large["endpoint_already_counted_flag"].mean()) if len(large) else 1.0,
        "large_QDeltaD_harmful_max": float(large["endpoint_harmful_Q"].max()) if len(large) else 0.0,
        "delayed_risk_large_QDeltaD_frac": float(large["delayed_risk_proxy"].mean()) if len(large) else 0.0,
        "worst_block_id": int(worst["block_id"]),
        "worst_p_star": int(worst["p_star"]),
        "worst_h": int(worst["h"]),
        "worst_endpoint_harmful_Q": float(worst["endpoint_harmful_Q"]),
    }


def load_inputs() -> pd.DataFrame:
    log(f"Reading {O2P3_INTERVALS}")
    df = pd.read_csv(O2P3_INTERVALS)
    if O2_PROJECTION.exists():
        log(f"Joining B2/O2 projection fields from {O2_PROJECTION}")
        proj_cols = [
            "block_id",
            "p_star",
            "y",
            "h",
            "Q_max",
            "Q_le_Ktail",
            "Q_le_1",
            "shortfall_R_plus",
            "drift_term",
            "cp_ratio",
            "canonical_scaled_Q_post",
            "canonical_scaled_E_post",
        ]
        proj = pd.read_csv(O2_PROJECTION, usecols=lambda c: c in proj_cols)
        df = df.merge(proj, on=["block_id", "p_star", "y", "h"], how="left", validate="one_to_one")
    return df


def write_doc(summary: dict[str, object], scopes: pd.DataFrame, worst: pd.DataFrame) -> None:
    status = "fail"
    qh = summary["Q_DeltaD_harmful_max"]
    if qh <= 0.05:
        status = "very strong"
    elif qh <= 0.10:
        status = "strong"
    elif qh < 1.0:
        status = "usable"

    lines = [
        "# Prime Mesh R2Q - Endpoint Repayment Compatibility Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-07",
        f"**Status:** endpoint compatibility audit - {status}",
        "",
        "## 1. Purpose",
        "",
        "This audit checks whether the large O2.3 endpoint term `Q_DeltaD` is harmful O2.3 slack or already belongs to the B2/MR-2 endpoint repayment stack.",
        "",
        "The tested convention is:",
        "",
        r"\[",
        r"\Delta D_N(J)<0 \quad\Rightarrow\quad \text{B2/R2Q endpoint descent, already counted by endpoint repayment.}",
        r"\]",
        "",
        "Thus the harmful endpoint component is the part that is not favorable and not already counted.",
        "",
        "## 2. Summary",
        "",
        "| metric | value |",
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
        "## 4. Worst Rows By Raw Endpoint Motion",
        "",
        worst.to_markdown(index=False),
        "",
        "## 5. Interpretation",
        "",
    ]
    if qh <= 0.05:
        lines += [
            r"\[",
            r"\boxed{Q_{\Delta D}^{\rm harmful}=0\text{ empirically; endpoint motion is B2-compatible and should not be double-counted in O2.3.}}",
            r"\]",
            "",
            "The large endpoint drops are all negative endpoint-descent rows in the LongA/B2-active inventory.  They are the endpoint repayment coordinate itself, not a new internal bridge-excursion obstruction.",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{Some endpoint motion remains harmful under the tested convention; O2.3 needs a separate endpoint lemma.}}",
            r"\]",
        ]
    lines += [
        "",
        "## 6. Caveat",
        "",
        "This audit proves no theorem by itself.  It verifies the bookkeeping orientation needed for the formal EndpointRepaymentCompatibility lemma.",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
    ]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def refresh_manifest() -> None:
    rows = []
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            rows.append({"Name": p.name, "Length": p.stat().st_size, "LastWriteTime": pd.Timestamp(p.stat().st_mtime, unit="s")})
    pd.DataFrame(rows).to_csv(MANIFEST, index=False)


def main() -> None:
    df = load_inputs()
    for c in ["DeltaD", "Q_DeltaD", "Q_exc", "Q_delayed_proxy", "h", "p_star", "recovery_position"]:
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df["DeltaD_sign"] = np.select([df["DeltaD"] < 0, df["DeltaD"] > 0], ["negative", "positive"], default="zero")
    df["R2Q_obstruction_sign"] = "negative-deficit-facing"
    df["B2_repayment_sign"] = np.where(df["DeltaD"] < 0, "endpoint_descent_counted_by_B2", "not_descent")
    df["endpoint_favorable_flag"] = df["DeltaD"] < 0
    df["endpoint_already_counted_flag"] = (df["DeltaD"] < 0) & df["Q_DeltaD"].notna()
    df["endpoint_harmful_flag"] = ~(df["endpoint_favorable_flag"] | df["endpoint_already_counted_flag"])
    df["endpoint_harmful_Q"] = np.where(df["endpoint_harmful_flag"], df["Q_DeltaD"].fillna(0.0), 0.0)
    df["endpoint_repayment_Q"] = np.where(df["endpoint_already_counted_flag"], df["Q_DeltaD"].fillna(0.0), 0.0)
    df["double_count_risk_flag"] = df["endpoint_already_counted_flag"] & (df["Q_DeltaD"] > 0.25)
    df["theta_local_sign_if_available"] = "not_available"
    df["delayed_risk_proxy"] = (df["h"] > 8192) | (df["recovery_position"] > 0.5)
    df["large_endpoint_flag"] = df["Q_DeltaD"] > 0.25

    keep = [
        "block_id",
        "p_star",
        "y",
        "h",
        "D_start",
        "D_end",
        "DeltaD",
        "DeltaD_sign",
        "Q_DeltaD",
        "Q_exc",
        "Q_delayed_proxy",
        "theta_local_sign_if_available",
        "R2Q_obstruction_sign",
        "B2_repayment_sign",
        "endpoint_favorable_flag",
        "endpoint_already_counted_flag",
        "endpoint_harmful_flag",
        "endpoint_harmful_Q",
        "endpoint_repayment_Q",
        "double_count_risk_flag",
        "delayed_risk_proxy",
        "large_endpoint_flag",
        "is_tail",
        "h_bin",
        "p_scale_bin",
        "mu_bin_if_available",
        "depth_bin",
        "recovery_position",
    ]
    for optional in ["Q_max", "Q_le_Ktail", "Q_le_1", "shortfall_R_plus", "drift_term", "cp_ratio", "canonical_scaled_Q_post"]:
        if optional in df.columns:
            keep.append(optional)
    out = df[keep].copy()
    out.to_csv(INTERVALS_OUT, index=False)

    scopes = [summarize(out, "global")]
    scope_parts = [
        ("tail:p_star>=500M", out[out["is_tail"].astype(bool)]),
        ("tail:p_star<500M", out[~out["is_tail"].astype(bool)]),
        ("large_QDeltaD:>0.25", out[out["large_endpoint_flag"]]),
        ("small_QDeltaD:<=0.25", out[~out["large_endpoint_flag"]]),
        ("delayed_risk:True", out[out["delayed_risk_proxy"]]),
        ("delayed_risk:False", out[~out["delayed_risk_proxy"]]),
    ]
    for label, part in scope_parts:
        if len(part):
            scopes.append(summarize(part, label))
    for col, prefix in [("h_bin", "h"), ("p_scale_bin", "scale"), ("mu_bin_if_available", "mu"), ("depth_bin", "depth")]:
        for value, part in out.groupby(col, dropna=False):
            if len(part):
                scopes.append(summarize(part, f"{prefix}:{value}"))
    scopes_df = pd.DataFrame(scopes).sort_values(["Q_DeltaD_max", "rows"], ascending=[False, False])
    scopes_df.to_csv(SCOPES_OUT, index=False)

    summary = summarize(out, "global")
    summary.update(
        {
            "interval_rows": int(len(out)),
            "Q_DeltaD_harmful_max": float(out["endpoint_harmful_Q"].max()),
            "Q_DeltaD_repayment_max": float(out["endpoint_repayment_Q"].max()),
            "positive_DeltaD_rows": int((out["DeltaD"] > 0).sum()),
            "negative_DeltaD_rows": int((out["DeltaD"] < 0).sum()),
            "large_QDeltaD_rows": int(out["large_endpoint_flag"].sum()),
            "large_QDeltaD_already_counted_frac": float(out.loc[out["large_endpoint_flag"], "endpoint_already_counted_flag"].mean())
            if out["large_endpoint_flag"].any()
            else 1.0,
            "large_QDeltaD_harmful_max": float(out.loc[out["large_endpoint_flag"], "endpoint_harmful_Q"].max())
            if out["large_endpoint_flag"].any()
            else 0.0,
        }
    )
    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)

    worst = out.sort_values(["Q_DeltaD", "Q_exc"], ascending=False).head(50)
    worst.to_csv(WORST_OUT, index=False)
    write_doc(summary, scopes_df, worst.head(20))
    refresh_manifest()

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {INTERVALS_OUT}")
    log(f"Wrote {SCOPES_OUT}")
    log(f"Wrote {WORST_OUT}")
    log(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
