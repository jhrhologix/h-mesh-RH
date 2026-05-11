#!/usr/bin/env python
"""Scale-law audit for the O2-B centered LongA fluctuation.

The previous source audit showed that the remaining negative O2 residuals are
concentrated in the fully active shell pattern, not in prime-power/boundary
bookkeeping.  This script restricts to that LongA channel and asks whether the
normalized negative constant is stable or shrinking across p*, h, depth, and mu.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
DOCS = ROOT / "docs" / "RH" / "notes"

INPUT = NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"

SUMMARY_OUT = NOTES / "prime_mesh_r2q_o2_longa_fluctuation_scale_law_summary.csv"
SCOPES_OUT = NOTES / "prime_mesh_r2q_o2_longa_fluctuation_scale_law_scopes.csv"
WORST_OUT = NOTES / "prime_mesh_r2q_o2_longa_fluctuation_scale_law_worst_rows.csv"
DOC_OUT = DOCS / "Prime_Mesh_R2Q_O2_LongA_Fluctuation_Scale_Law_Audit_v1.md"


def log(msg: str) -> None:
    from datetime import datetime

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def h_bin(h: float) -> str:
    if h <= 4:
        return "h<=4"
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


def shell_pattern(row: pd.Series) -> str:
    vals = []
    for j in range(5):
        v = row.get(f"shell_sym_all_{j}", np.nan)
        if pd.isna(v):
            vals.append("?")
        elif abs(v) <= 1e-12:
            vals.append("0")
        else:
            vals.append("1")
    return "".join(vals)


def summarize_scope(df: pd.DataFrame, scope: str) -> dict[str, object]:
    neg = df[df["z"] < 0]
    return {
        "scope": scope,
        "rows": len(df),
        "neg_rows": len(neg),
        "neg_frac": len(neg) / len(df) if len(df) else 0.0,
        "mean_z": df["z"].mean(),
        "median_z": df["z"].median(),
        "std_z": df["z"].std(ddof=0),
        "min_z": df["z"].min(),
        "max_z": df["z"].max(),
        "neg_max": (-neg["z"]).max() if len(neg) else 0.0,
        "neg_median": (-neg["z"]).median() if len(neg) else 0.0,
        "q01_z": df["z"].quantile(0.01) if len(df) else np.nan,
        "q05_z": df["z"].quantile(0.05) if len(df) else np.nan,
        "q10_z": df["z"].quantile(0.10) if len(df) else np.nan,
        "q90_z": df["z"].quantile(0.90) if len(df) else np.nan,
        "q95_z": df["z"].quantile(0.95) if len(df) else np.nan,
        "median_p_star": df["p_star"].median() if "p_star" in df else np.nan,
        "median_h": df["h"].median() if "h" in df else np.nan,
        "median_mu_over_sqrt_p": df["mu_over_sqrt_p"].median() if "mu_over_sqrt_p" in df else np.nan,
        "median_cp_ratio": df["cp_ratio"].median() if "cp_ratio" in df else np.nan,
    }


def slope_fit(df: pd.DataFrame, xcol: str, ycol: str) -> tuple[float, float, int]:
    """Fit log(y) = a + b log(x) for positive y."""
    d = df[[xcol, ycol]].dropna()
    d = d[(d[xcol] > 0) & (d[ycol] > 0)]
    if len(d) < 3:
        return np.nan, np.nan, len(d)
    x = np.log(d[xcol].to_numpy(dtype=float))
    y = np.log(d[ycol].to_numpy(dtype=float))
    b, a = np.polyfit(x, y, 1)
    yhat = a + b * x
    ss_res = float(((y - yhat) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return float(b), float(r2), len(d)


def main() -> None:
    log(f"Reading {INPUT}")
    df = pd.read_csv(INPUT)

    for c in [
        "canonical_scaled_E_post",
        "denom_sqrt_h_logB",
        "p_star",
        "h",
        "y",
        "block_id",
        "d_worst",
        "mu_over_sqrt_p",
        "cp_ratio",
        "Q_pp",
        "Qpp_over_denom",
    ]:
        if c in df.columns:
            df[c] = num(df[c])

    df["z"] = df["canonical_scaled_E_post"] / df["denom_sqrt_h_logB"].replace(0, np.nan)
    df["neg_Q"] = (-df["z"]).clip(lower=0)
    df["shell_pattern"] = df.apply(shell_pattern, axis=1)
    df["is_longa"] = df["shell_pattern"].eq("11111")
    df["h_bin"] = df["h"].map(h_bin)
    df["pstar_mod_30"] = (df["p_star"].astype("Int64") % 30).astype(str)
    df["y_mod_30"] = (df["y"].astype("Int64") % 30).astype(str)
    if {"y", "worst_prime", "L_recovery"}.issubset(df.columns):
        df["worst_prime"] = num(df["worst_prime"])
        df["L_recovery"] = num(df["L_recovery"])
        df["recovery_position"] = (df["y"] - df["worst_prime"]) / df["L_recovery"].replace(0, np.nan)
        df["recovery_pos_bin"] = pd.cut(
            df["recovery_position"],
            [-np.inf, 0.05, 0.25, 0.50, 0.75, 0.95, np.inf],
            labels=["<=0.05", "0.05-0.25", "0.25-0.50", "0.50-0.75", "0.75-0.95", ">=0.95"],
        ).astype(str)
    else:
        df["recovery_position"] = np.nan
        df["recovery_pos_bin"] = "unknown"

    longa = df[df["is_longa"]].copy()
    neg_longa = longa[longa["z"] < 0].copy()

    scopes: list[dict[str, object]] = []
    scopes.append(summarize_scope(longa, "LongA:global"))
    if "is_tail" in longa.columns:
        for key, g in longa.groupby("is_tail", dropna=False):
            scopes.append(summarize_scope(g, f"LongA:tail:{key}"))
    for col, prefix in [
        ("scale_bin", "scale"),
        ("decade", "decade"),
        ("h_bin", "h"),
        ("depth_bin", "depth"),
        ("mu_bin", "mu"),
        ("pstar_mod_30", "pstar_mod_30"),
        ("y_mod_30", "y_mod_30"),
        ("recovery_pos_bin", "recovery_position"),
    ]:
        if col in longa.columns:
            for key, g in longa.groupby(col, dropna=False):
                scopes.append(summarize_scope(g, f"{prefix}:{key}"))

    scopes_df = pd.DataFrame(scopes).sort_values(["neg_max", "rows"], ascending=[False, False])

    # Coarse trend checks on the negative envelope.
    # Use per-scope maxima to avoid fitting every row's zero-heavy neg_Q values.
    by_scale = (
        longa.groupby("scale_bin", dropna=False)
        .agg(p_star_median=("p_star", "median"), h_median=("h", "median"), neg_max=("neg_Q", "max"), rows=("z", "size"))
        .reset_index()
        if "scale_bin" in longa.columns
        else pd.DataFrame()
    )
    p_slope, p_r2, p_n = slope_fit(by_scale, "p_star_median", "neg_max") if len(by_scale) else (np.nan, np.nan, 0)

    by_h = (
        longa.groupby("h_bin", dropna=False)
        .agg(h_median=("h", "median"), neg_max=("neg_Q", "max"), rows=("z", "size"))
        .reset_index()
    )
    h_slope, h_r2, h_n = slope_fit(by_h, "h_median", "neg_max")

    worst = longa.sort_values("neg_Q", ascending=False).head(50).copy()
    keep = [
        "block_id",
        "p_star",
        "y",
        "h",
        "z",
        "neg_Q",
        "is_tail",
        "scale_bin",
        "decade",
        "depth_bin",
        "mu_bin",
        "h_bin",
        "d_worst",
        "mu_over_sqrt_p",
        "cp_ratio",
        "Q_pp",
        "Qpp_over_denom",
        "pstar_mod_30",
        "y_mod_30",
        "recovery_position",
        "recovery_pos_bin",
        "canonical_scaled_E_post",
        "denom_sqrt_h_logB",
    ]
    keep = [c for c in keep if c in worst.columns]
    worst_out = worst[keep]

    tail = longa[longa["is_tail"].astype(str).str.lower().isin(["true", "1"])] if "is_tail" in longa.columns else longa.iloc[0:0]
    summary = {
        "rows_all": len(df),
        "rows_longa": len(longa),
        "longa_frac": len(longa) / len(df) if len(df) else 0.0,
        "longa_neg_rows": len(neg_longa),
        "longa_neg_frac": len(neg_longa) / len(longa) if len(longa) else 0.0,
        "longa_mean_z": longa["z"].mean(),
        "longa_std_z": longa["z"].std(ddof=0),
        "longa_neg_max": longa["neg_Q"].max() if len(longa) else np.nan,
        "longa_q01_z": longa["z"].quantile(0.01) if len(longa) else np.nan,
        "longa_q05_z": longa["z"].quantile(0.05) if len(longa) else np.nan,
        "tail_longa_rows": len(tail),
        "tail_longa_neg_rows": int((tail["z"] < 0).sum()) if len(tail) else 0,
        "tail_longa_neg_frac": float((tail["z"] < 0).mean()) if len(tail) else np.nan,
        "tail_longa_neg_max": tail["neg_Q"].max() if len(tail) else np.nan,
        "all_pass_Q_le_1_frac": float((longa["neg_Q"] <= 1.0).mean()) if len(longa) else np.nan,
        "all_pass_Q_le_0p1_frac": float((longa["neg_Q"] <= 0.1).mean()) if len(longa) else np.nan,
        "all_pass_Q_le_0p05_frac": float((longa["neg_Q"] <= 0.05).mean()) if len(longa) else np.nan,
        "p_scale_negmax_loglog_slope": p_slope,
        "p_scale_negmax_loglog_r2": p_r2,
        "p_scale_fit_n": p_n,
        "h_bin_negmax_loglog_slope": h_slope,
        "h_bin_negmax_loglog_r2": h_r2,
        "h_bin_fit_n": h_n,
        "worst_block_id": worst.iloc[0]["block_id"] if len(worst) else np.nan,
        "worst_p_star": worst.iloc[0]["p_star"] if len(worst) else np.nan,
        "worst_h": worst.iloc[0]["h"] if len(worst) else np.nan,
        "worst_is_tail": worst.iloc[0].get("is_tail", np.nan) if len(worst) else np.nan,
        "worst_z": worst.iloc[0]["z"] if len(worst) else np.nan,
        "worst_neg_Q": worst.iloc[0]["neg_Q"] if len(worst) else np.nan,
        "worst_scale_bin": worst.iloc[0].get("scale_bin", "") if len(worst) else "",
        "worst_depth_bin": worst.iloc[0].get("depth_bin", "") if len(worst) else "",
        "worst_mu_bin": worst.iloc[0].get("mu_bin", "") if len(worst) else "",
    }

    summary_df = pd.DataFrame([summary])
    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(SUMMARY_OUT, index=False)
    scopes_df.to_csv(SCOPES_OUT, index=False)
    worst_out.to_csv(WORST_OUT, index=False)

    with DOC_OUT.open("w", encoding="utf-8") as f:
        f.write("# Prime Mesh R2Q - O2 LongA Fluctuation Scale-Law Audit\n\n")
        f.write("**Document:** `Prime_Mesh_R2Q_O2_LongA_Fluctuation_Scale_Law_Audit_v1.md`  \n")
        f.write("**Project:** Prime Mesh Theory - RH Programme  \n")
        f.write("**Date:** 2026-05-06  \n")
        f.write("**Status:** O2-B LongA scale-law diagnostic\n\n")
        f.write("## 1. Purpose\n\n")
        f.write(
            "This audit restricts to the fully active LongA shell channel "
            "`11111` and checks whether the negative normalized post-response "
            "residual is stable or shrinking across scale, interval length, "
            "depth, and mu.\n\n"
        )
        f.write("The quantity measured is\n\n")
        f.write("\\[\n")
        f.write("z(J)=\\frac{\\mathcal Z_{\\rm LongA}(J)}{\\sqrt{|J|}\\log^2p^*},\n")
        f.write("\\qquad [-z(J)]_+.\n")
        f.write("\\]\n\n")
        f.write("## 2. Summary\n\n")
        f.write(summary_df.T.reset_index().rename(columns={"index": "metric", 0: "value"}).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 3. Largest LongA Negative Rows\n\n")
        f.write(worst_out.head(15).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 4. Scope Maxima\n\n")
        f.write(scopes_df.head(30).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 5. Interpretation\n\n")
        f.write(
            "The audit is designed to decide whether O2-B needs an additional "
            "scale or interval-length side case.  If the LongA negative envelope "
            "stays far below 1 and does not grow in the tail, then O2-B remains "
            "a centered bounded fluctuation theorem.\n\n"
        )
        f.write("---\n\n")
        f.write("*Prime Mesh Theory - RH Programme*\n")

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {SCOPES_OUT}")
    log(f"Wrote {WORST_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k in [
        "rows_longa",
        "longa_neg_frac",
        "longa_neg_max",
        "tail_longa_neg_max",
        "all_pass_Q_le_0p05_frac",
        "p_scale_negmax_loglog_slope",
        "h_bin_negmax_loglog_slope",
        "worst_block_id",
        "worst_p_star",
        "worst_h",
    ]:
        log(f"{k} = {summary[k]}")


if __name__ == "__main__":
    main()
