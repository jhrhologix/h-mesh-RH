#!/usr/bin/env python
"""Stability audit for positive theta side harmlessness.

Checks whether local positive Chebyshev excess rows remain safely below the
R2Q forbidden margin across scale, h, depth, mu, tail/finite scopes, and
residue/proxy slices.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
DOCS = ROOT / "docs" / "RH" / "notes"

INPUT = NOTES / "prime_mesh_r2q_theta_positive_side_candidate_rows.csv"
SUMMARY_OUT = NOTES / "prime_mesh_r2q_theta_positive_harmlessness_stability_summary.csv"
SCOPES_OUT = NOTES / "prime_mesh_r2q_theta_positive_harmlessness_stability_scopes.csv"
WORST_OUT = NOTES / "prime_mesh_r2q_theta_positive_harmlessness_stability_worst_rows.csv"
DOC_OUT = DOCS / "Prime_Mesh_R2Q_Theta_Positive_Harmlessness_Stability_Audit_v1.md"


def log(msg: str) -> None:
    from datetime import datetime

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def h_bin(h: float) -> str:
    if h <= 1:
        return "h=1"
    if h <= 4:
        return "2<=h<=4"
    if h <= 16:
        return "5<=h<=16"
    if h <= 64:
        return "17<=h<=64"
    if h <= 256:
        return "65<=h<=256"
    if h <= 1024:
        return "257<=h<=1024"
    if h <= 8192:
        return "1025<=h<=8192"
    if h <= 65536:
        return "8193<=h<=65536"
    return "h>65536"


def summarize(df: pd.DataFrame, scope: str) -> dict[str, object]:
    return {
        "scope": scope,
        "rows": len(df),
        "Qmax": df["Q_max"].max() if len(df) else np.nan,
        "Qmean": df["Q_max"].mean() if len(df) else np.nan,
        "Qmedian": df["Q_max"].median() if len(df) else np.nan,
        "Q95": df["Q_max"].quantile(0.95) if len(df) else np.nan,
        "Q99": df["Q_max"].quantile(0.99) if len(df) else np.nan,
        "pass_Q_le_1_frac": float((df["Q_max"] <= 1).mean()) if len(df) else np.nan,
        "pass_Q_le_0p75_frac": float((df["Q_max"] <= 0.75).mean()) if len(df) else np.nan,
        "pass_Q_le_0p5_frac": float((df["Q_max"] <= 0.5).mean()) if len(df) else np.nan,
        "pass_Q_le_0p25_frac": float((df["Q_max"] <= 0.25).mean()) if len(df) else np.nan,
        "theta_local_norm_max": df["theta_local_norm"].max() if len(df) else np.nan,
        "theta_local_norm_median": df["theta_local_norm"].median() if len(df) else np.nan,
        "median_h": df["h"].median() if len(df) else np.nan,
        "median_p_star": df["p_star"].median() if len(df) else np.nan,
        "best_k4_corr_proxy_median": df["k4_sym_comp_norm"].median() if "k4_sym_comp_norm" in df else np.nan,
        "worst_block_id": df.loc[df["Q_max"].idxmax(), "block_id"] if len(df) else np.nan,
        "worst_p_star": df.loc[df["Q_max"].idxmax(), "p_star"] if len(df) else np.nan,
        "worst_h": df.loc[df["Q_max"].idxmax(), "h"] if len(df) else np.nan,
    }


def main() -> None:
    log(f"Reading {INPUT}")
    df = pd.read_csv(INPUT)

    for c in [
        "block_id",
        "p_star",
        "y",
        "h",
        "theta_local_error",
        "theta_local_norm",
        "Q_max",
        "D_start_norm",
        "D_end_norm",
        "delta_D_norm",
        "prime_minus_repay_norm",
        "cp_residual_norm",
        "k4_sym_comp_norm",
    ]:
        if c in df.columns:
            df[c] = num(df[c])

    pos = df[df["theta_local_error"] > 0].copy()
    pos["h_bin"] = pos["h"].map(h_bin)
    pos["pstar_mod_30"] = (pos["p_star"].astype("Int64") % 30).astype(str)
    pos["y_mod_30"] = (pos["y"].astype("Int64") % 30).astype(str)
    pos["tail_bool"] = pos["is_tail"].astype(str).str.lower().isin(["true", "1"]) if "is_tail" in pos else False

    scopes: list[dict[str, object]] = [summarize(pos, "positive:global")]
    for col, prefix in [
        ("tail_bool", "tail"),
        ("scale_bin", "scale"),
        ("depth_bin", "depth"),
        ("mu_bin", "mu"),
        ("h_bin", "h"),
        ("pstar_mod_30", "pstar_mod_30"),
        ("y_mod_30", "y_mod_30"),
    ]:
        if col in pos.columns:
            for key, g in pos.groupby(col, dropna=False):
                scopes.append(summarize(g, f"{prefix}:{key}"))

    scopes_df = pd.DataFrame(scopes).sort_values(["Qmax", "rows"], ascending=[False, False])
    worst = pos.sort_values("Q_max", ascending=False).head(50)

    summary = {
        "rows_all": len(df),
        "positive_rows": len(pos),
        "positive_frac": len(pos) / len(df) if len(df) else np.nan,
        "C_plus_Qmax": pos["Q_max"].max() if len(pos) else np.nan,
        "C_plus_Q95": pos["Q_max"].quantile(0.95) if len(pos) else np.nan,
        "C_plus_Q99": pos["Q_max"].quantile(0.99) if len(pos) else np.nan,
        "pass_Q_le_1_frac": float((pos["Q_max"] <= 1).mean()) if len(pos) else np.nan,
        "pass_Q_le_0p75_frac": float((pos["Q_max"] <= 0.75).mean()) if len(pos) else np.nan,
        "pass_Q_le_0p5_frac": float((pos["Q_max"] <= 0.5).mean()) if len(pos) else np.nan,
        "pass_Q_le_0p25_frac": float((pos["Q_max"] <= 0.25).mean()) if len(pos) else np.nan,
        "tail_positive_rows": int(pos["tail_bool"].sum()) if "tail_bool" in pos else 0,
        "tail_C_plus_Qmax": pos.loc[pos["tail_bool"], "Q_max"].max() if "tail_bool" in pos and pos["tail_bool"].any() else np.nan,
        "finite_C_plus_Qmax": pos.loc[~pos["tail_bool"], "Q_max"].max() if "tail_bool" in pos and (~pos["tail_bool"]).any() else np.nan,
        "worst_block_id": worst.iloc[0]["block_id"] if len(worst) else np.nan,
        "worst_p_star": worst.iloc[0]["p_star"] if len(worst) else np.nan,
        "worst_h": worst.iloc[0]["h"] if len(worst) else np.nan,
        "worst_theta_local_norm": worst.iloc[0]["theta_local_norm"] if len(worst) else np.nan,
        "worst_scale_bin": worst.iloc[0].get("scale_bin", "") if len(worst) else "",
        "worst_depth_bin": worst.iloc[0].get("depth_bin", "") if len(worst) else "",
        "worst_mu_bin": worst.iloc[0].get("mu_bin", "") if len(worst) else "",
        "scopes_Qmax_gt_0p25": int((scopes_df["Qmax"] > 0.25).sum()),
        "scopes_Qmax_gt_0p5": int((scopes_df["Qmax"] > 0.5).sum()),
        "scopes_Qmax_gt_0p75": int((scopes_df["Qmax"] > 0.75).sum()),
        "scopes_Qmax_gt_1": int((scopes_df["Qmax"] > 1).sum()),
    }

    keep = [
        "block_id",
        "p_star",
        "y",
        "h",
        "theta_local_error",
        "theta_local_norm",
        "Q_max",
        "D_start_norm",
        "D_end_norm",
        "delta_D_norm",
        "prime_minus_repay_norm",
        "cp_residual_norm",
        "k4_sym_comp_norm",
        "is_tail",
        "scale_bin",
        "depth_bin",
        "mu_bin",
        "h_bin",
        "pstar_mod_30",
        "y_mod_30",
    ]
    keep = [c for c in keep if c in worst.columns]

    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)
    scopes_df.to_csv(SCOPES_OUT, index=False)
    worst[keep].to_csv(WORST_OUT, index=False)

    with DOC_OUT.open("w", encoding="utf-8") as f:
        f.write("# Prime Mesh R2Q - Theta Positive Harmlessness Stability Audit\n\n")
        f.write("**Document:** `Prime_Mesh_R2Q_Theta_Positive_Harmlessness_Stability_Audit_v1.md`  \n")
        f.write("**Project:** Prime Mesh Theory - RH Programme  \n")
        f.write("**Date:** 2026-05-06  \n")
        f.write("**Status:** positive-side harmlessness stability diagnostic\n\n")
        f.write("## 1. Purpose\n\n")
        f.write(
            "This audit tests whether the empirical positive-side bound "
            "\\(E_\\theta(J)>0\\Rightarrow Q_{\\rm R2Q}(J)<1\\) remains stable "
            "across scale, interval length, depth, mu, and tail/finite scopes.\n\n"
        )
        f.write("## 2. Summary\n\n")
        f.write(pd.DataFrame([summary]).T.reset_index().rename(columns={"index": "metric", 0: "value"}).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 3. Scope Table\n\n")
        f.write(scopes_df.to_markdown(index=False))
        f.write("\n\n")
        f.write("## 4. Worst Positive Rows\n\n")
        f.write(worst[keep].head(20).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 5. Interpretation\n\n")
        f.write(
            "If every populated scope remains below 1, the positive theta side "
            "can be treated as harmless for R2Q tail closure.  A stronger "
            "uniform constant below 0.25 would give a large safety margin.\n\n"
        )
        f.write("---\n\n")
        f.write("*Prime Mesh Theory - RH Programme*\n")

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {SCOPES_OUT}")
    log(f"Wrote {WORST_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k, v in summary.items():
        log(f"{k} = {v}")


if __name__ == "__main__":
    main()
