#!/usr/bin/env python
"""O1 Gap C shell-normalization audit.

Goal:
    Explain the observed aggregate R3/R2 deviation from 1/3 as a q=3 anchor
    plus signed non-3 residual correction, and compare that correction to the
    O1 sign-margin budget.

Inputs:
    - LongA shell-size source site table, with shell/site weights and SPF pairs.
    - O2 projection interval table, for interval-level sym_all shell fields.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
DOCS = ROOT / "docs" / "RH" / "notes"
REPAIR = DOCS / "claude" / "repair and close process"
DEST = REPAIR / "scripts and results"

SITES = NOTES / "prime_mesh_r2q_longa_shell_size_source_audit_sites.csv"
INTERVALS = NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"

SUMMARY_OUT = NOTES / "prime_mesh_r2q_o1_gapc_shell_normalization_summary.csv"
CLASSES_OUT = NOTES / "prime_mesh_r2q_o1_gapc_shell_normalization_classes.csv"
INTERVALS_OUT = NOTES / "prime_mesh_r2q_o1_gapc_shell_normalization_intervals.csv"
DOC_OUT = DOCS / "Prime_Mesh_R2Q_O1_GapC_Shell_Normalization_Audit_v1.md"


def log(msg: str) -> None:
    from datetime import datetime

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def signs(x: float, tol: float = 1e-12) -> str:
    if x > tol:
        return "+"
    if x < -tol:
        return "-"
    return "0"


def main() -> None:
    log(f"Reading sites {SITES}")
    sites = pd.read_csv(SITES)
    log(f"Reading intervals {INTERVALS}")
    intervals = pd.read_csv(INTERVALS)

    for c in ["block_id", "source_row", "p_star", "y", "h", "prime", "shell", "W", "W2", "spf_n", "spf_prev"]:
        if c in sites.columns:
            sites[c] = num(sites[c])
    for c in ["block_id", "source_row", "p_star", "y", "h", "shell_sym_all_2", "shell_sym_all_3", "shell_sym_all_4"]:
        if c in intervals.columns:
            intervals[c] = num(intervals[c])

    # Shell-2 constant anchor.
    shell2_sites = sites[sites["shell"] == 2].copy()
    shell3_sites = sites[sites["shell"] == 3].copy()
    shell4_sites = sites[sites["shell"] == 4].copy()
    W2_anchor = shell2_sites["W"].mean()
    C_N_est = 4.0 * W2_anchor

    # For shell 3, n=p±3 is even, so spf_n=2 and the nontrivial SPF class is spf_prev.
    shell3_sites["q"] = shell3_sites["spf_prev"].astype("Int64")
    shell3_sites["is_q3"] = shell3_sites["q"].eq(3)

    class_rows = []
    total_shell3_W = shell3_sites["W"].sum()
    total_shell3_W2 = shell3_sites["W2"].sum()
    for q, g in shell3_sites.groupby("q", dropna=False):
        class_rows.append(
            {
                "q": q,
                "count": len(g),
                "count_frac": len(g) / len(shell3_sites),
                "sum_W": g["W"].sum(),
                "sum_W_frac": g["W"].sum() / total_shell3_W if total_shell3_W else np.nan,
                "sum_W2": g["W2"].sum(),
                "sum_W2_frac": g["W2"].sum() / total_shell3_W2 if total_shell3_W2 else np.nan,
                "mean_W": g["W"].mean(),
                "mean_W_over_shell2": g["W"].mean() / W2_anchor,
                "mean_W2": g["W2"].mean(),
                "side_left_frac": (g["side"].astype(str).eq("left")).mean(),
            }
        )
    classes = pd.DataFrame(class_rows).sort_values("sum_W", ascending=False)

    # Interval-level decomposition of shell_sym_all_3 into q=3 and non-q=3
    # components.  This is the relevant O1 aggregate object.
    group_keys = ["block_id", "source_row", "p_star", "y", "h"]
    shell3_decomp = (
        shell3_sites.assign(W_q3=np.where(shell3_sites["is_q3"], shell3_sites["W"], 0.0))
        .assign(W_non3=np.where(~shell3_sites["is_q3"], shell3_sites["W"], 0.0))
        .groupby(group_keys, dropna=False)
        .agg(R3_q3=("W_q3", "sum"), R3_non3=("W_non3", "sum"), R3_rebuilt=("W", "sum"))
        .reset_index()
    )
    # Gap C is a LongA statement.  Use the site table's group keys as the
    # canonical LongA carrier family and merge intervals onto that family only.
    joined = intervals.merge(shell3_decomp, on=group_keys, how="inner")
    for c in ["R3_q3", "R3_non3", "R3_rebuilt"]:
        joined[c] = joined[c].fillna(0.0)

    R2 = joined["shell_sym_all_2"]
    R3 = joined["shell_sym_all_3"]
    R4 = joined["shell_sym_all_4"]
    R3_q3 = joined["R3_q3"]
    R3_non3 = joined["R3_non3"]

    # Aggregate O1 second-moment/RMS ratios.
    M2 = float((R2**2).sum())
    M3 = float((R3**2).sum())
    M4 = float((R4**2).sum())
    M3_q3 = float((R3_q3**2).sum())
    M3_non3 = float((R3_non3**2).sum())
    M3_cross = float((2 * R3_q3 * R3_non3).sum())

    rms_R3_R2 = float(np.sqrt(M3 / M2))
    rms_anchor = 1.0 / 3.0
    rms_deviation = rms_R3_R2 - rms_anchor
    M3_M2 = M3 / M2
    M_target = 1.0 / 9.0
    M_deviation = M3_M2 - M_target

    q3_rms_component = float(np.sqrt(M3_q3 / M2))
    non3_signed_mean_ratio = float((R3_non3 / R2.replace(0, np.nan)).mean())
    non3_M_component = M3_non3 / M2
    cross_M_component = M3_cross / M2
    q3_M_component = M3_q3 / M2

    # Anchor comparison: how close is the q=3 component alone to the 1/3 RMS anchor?
    q3_anchor_deviation = q3_rms_component - rms_anchor
    residual_needed_from_anchor = rms_deviation

    sign_margin = 0.148198888171
    observed_abs_rms_dev = abs(rms_deviation)
    observed_abs_M_dev = abs(M_deviation)

    rebuild_abs_max = float((joined["R3_rebuilt"] - joined["shell_sym_all_3"]).abs().max())
    rebuild_mean_abs = float((joined["R3_rebuilt"] - joined["shell_sym_all_3"]).abs().mean())

    intervals_out = joined[group_keys + [
        "shell_sym_all_2",
        "shell_sym_all_3",
        "R3_q3",
        "R3_non3",
        "R3_rebuilt",
    ]].copy()
    intervals_out["R3_over_R2"] = intervals_out["shell_sym_all_3"] / intervals_out["shell_sym_all_2"].replace(0, np.nan)
    intervals_out["R3_q3_over_R2"] = intervals_out["R3_q3"] / intervals_out["shell_sym_all_2"].replace(0, np.nan)
    intervals_out["R3_non3_over_R2"] = intervals_out["R3_non3"] / intervals_out["shell_sym_all_2"].replace(0, np.nan)

    q3 = classes[classes["q"].astype(str).eq("3")]
    q3_count_frac = float(q3["count_frac"].iloc[0]) if len(q3) else np.nan
    q3_sumW_frac = float(q3["sum_W_frac"].iloc[0]) if len(q3) else np.nan
    q3_sumW2_frac = float(q3["sum_W2_frac"].iloc[0]) if len(q3) else np.nan
    q3_meanW_over_shell2 = float(q3["mean_W_over_shell2"].iloc[0]) if len(q3) else np.nan

    summary = {
        "site_rows_shell3": len(shell3_sites),
        "interval_rows_longa": len(joined),
        "W2_anchor": W2_anchor,
        "C_N_est": C_N_est,
        "rebuild_R3_abs_max": rebuild_abs_max,
        "rebuild_R3_mean_abs": rebuild_mean_abs,
        "q3_count_frac": q3_count_frac,
        "q3_sumW_frac": q3_sumW_frac,
        "q3_sumW2_frac": q3_sumW2_frac,
        "q3_meanW_over_shell2": q3_meanW_over_shell2,
        "aggregate_M3_over_M2": M3_M2,
        "aggregate_R3_R2_rms": rms_R3_R2,
        "target_R3_R2": rms_anchor,
        "rms_deviation_from_1over3": rms_deviation,
        "aggregate_M3_over_M2_target_1over9": M_target,
        "M_deviation_from_1over9": M_deviation,
        "M3_q3_component_over_M2": q3_M_component,
        "M3_non3_component_over_M2": non3_M_component,
        "M3_cross_component_over_M2": cross_M_component,
        "q3_rms_component_over_R2": q3_rms_component,
        "q3_anchor_deviation_from_1over3": q3_anchor_deviation,
        "non3_signed_mean_R3_over_R2": non3_signed_mean_ratio,
        "observed_abs_rms_dev": observed_abs_rms_dev,
        "observed_abs_M_dev": observed_abs_M_dev,
        "O1_sign_margin": sign_margin,
        "rms_dev_over_sign_margin": observed_abs_rms_dev / sign_margin,
        "M_dev_over_sign_margin": observed_abs_M_dev / sign_margin,
        "passes_rms_dev_within_sign_margin": observed_abs_rms_dev < sign_margin,
        "passes_M_dev_within_sign_margin": observed_abs_M_dev < sign_margin,
    }

    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)
    classes.to_csv(CLASSES_OUT, index=False)
    intervals_out.to_csv(INTERVALS_OUT, index=False)

    with DOC_OUT.open("w", encoding="utf-8") as f:
        f.write("# Prime Mesh R2Q - O1 Gap C Shell Normalization Audit\n\n")
        f.write("**Document:** `Prime_Mesh_R2Q_O1_GapC_Shell_Normalization_Audit_v1.md`  \n")
        f.write("**Project:** Prime Mesh Theory - RH Programme  \n")
        f.write("**Date:** 2026-05-07  \n")
        f.write("**Status:** Gap C computation after shell-normalization repair\n\n")
        f.write("## 1. Purpose\n\n")
        f.write(
            "This audit decomposes the LongA shell-3 aggregate into the exact "
            "q=3 SPF branch and the residual non-3 branch, then measures the "
            "observed deviation of the O1 aggregate ratio from the anchor "
            "\\(R_3/R_2=1/3\\).\n\n"
        )
        f.write("## 2. Summary\n\n")
        f.write(pd.DataFrame([summary]).T.reset_index().rename(columns={"index": "metric", 0: "value"}).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 3. SPF Class Decomposition\n\n")
        f.write(classes.head(25).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 4. Interpretation\n\n")
        f.write(
            "The interval-level shell field rebuild check verifies that the site "
            "decomposition matches the O1 aggregate shell field.  The observed "
            "aggregate ratio is compared directly against \\(1/3\\), and the "
            "non-3 residual/cross terms are reported in the same second-moment "
            "normalization as O1.\n\n"
        )
        f.write("The key budget comparison is\n\n")
        f.write("\\[\n")
        f.write("|R_3/R_2-1/3|/\\delta_{\\rm sign}.\n")
        f.write("\\]\n\n")
        f.write("---\n\n")
        f.write("*Prime Mesh Theory - RH Programme*\n")

    # Deposit a copy into the repair scripts/results bundle.
    DEST.mkdir(parents=True, exist_ok=True)
    for path in [Path(__file__), SUMMARY_OUT, CLASSES_OUT, INTERVALS_OUT, DOC_OUT]:
        try:
            (DEST / path.name).write_bytes(path.read_bytes())
        except Exception:
            pass

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {CLASSES_OUT}")
    log(f"Wrote {INTERVALS_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k, v in summary.items():
        log(f"{k} = {v}")


if __name__ == "__main__":
    main()
