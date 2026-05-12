#!/usr/bin/env python
"""Audit arithmetic sources of negative O2 post-response residuals.

This diagnostic follows O2-B.  The centered residual bound is already very
small; here we ask whether the remaining negative rows cluster around a
recognizable source: scale, interval length, depth, mu, residue class,
prime-power slack, shell pattern, or recovery-block position.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
DOCS = ROOT / "docs" / "RH" / "notes"

INPUT = NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"

SUMMARY_OUT = NOTES / "prime_mesh_r2q_o2_negative_tail_source_audit_summary.csv"
FEATURES_OUT = NOTES / "prime_mesh_r2q_o2_negative_tail_source_audit_features.csv"
ROWS_OUT = NOTES / "prime_mesh_r2q_o2_negative_tail_source_audit_worst_rows.csv"
DOC_OUT = DOCS / "Prime_Mesh_R2Q_O2_Negative_Tail_Source_Audit_v1.md"


def log(msg: str) -> None:
    from datetime import datetime

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def safe_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def bin_h(h: float) -> str:
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
    return "h>8192"


def summarize_group(df: pd.DataFrame, label: str, col: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key, g in df.groupby(col, dropna=False):
        neg = g[g["canonical_z"] < 0]
        rows.append(
            {
                "feature": label,
                "value": key,
                "rows": len(g),
                "neg_rows": len(neg),
                "neg_frac": len(neg) / len(g) if len(g) else 0.0,
                "mean_z": g["canonical_z"].mean(),
                "min_z": g["canonical_z"].min(),
                "neg_max": (-neg["canonical_z"]).max() if len(neg) else 0.0,
                "median_h": g["h"].median(),
                "median_qpp_over_denom": g["Qpp_over_denom"].median()
                if "Qpp_over_denom" in g
                else np.nan,
                "median_cp_ratio": g["cp_ratio"].median() if "cp_ratio" in g else np.nan,
            }
        )
    return rows


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


def main() -> None:
    log(f"Reading {INPUT}")
    df = pd.read_csv(INPUT)

    required = [
        "canonical_scaled_E_post",
        "denom_sqrt_h_logB",
        "p_star",
        "y",
        "h",
        "block_id",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing required columns: {missing}")

    for c in [
        "canonical_scaled_E_post",
        "canonical_raw_E_post",
        "fitted_E_post",
        "denom_sqrt_h_logB",
        "p_star",
        "y",
        "h",
        "block_id",
        "Q_pp",
        "Qpp_over_denom",
        "cp_ratio",
        "prime_count",
        "local_prime_count",
        "L_recovery",
        "worst_prime",
        "end_prime",
        "d_worst",
        "mu_over_sqrt_p",
    ]:
        if c in df.columns:
            df[c] = safe_num(df[c])

    denom = df["denom_sqrt_h_logB"].replace(0, np.nan)
    df["canonical_z"] = df["canonical_scaled_E_post"] / denom
    if "canonical_raw_E_post" in df.columns:
        df["canonical_raw_z"] = df["canonical_raw_E_post"] / denom
    if "fitted_E_post" in df.columns:
        df["fitted_z"] = df["fitted_E_post"] / denom
    df["neg_Q"] = (-df["canonical_z"]).clip(lower=0)
    df["is_negative"] = df["canonical_z"] < 0

    df["h_bin"] = df["h"].map(bin_h)
    df["pstar_mod_30"] = (df["p_star"].astype("Int64") % 30).astype(str)
    df["y_mod_30"] = (df["y"].astype("Int64") % 30).astype(str)
    df["h_mod_30"] = (df["h"].astype("Int64") % 30).astype(str)
    df["short_boundary_proxy"] = df["h"] <= 8
    if {"y", "worst_prime", "L_recovery"}.issubset(df.columns):
        length = df["L_recovery"].replace(0, np.nan)
        df["recovery_position"] = (df["y"] - df["worst_prime"]) / length
        df["recovery_pos_bin"] = pd.cut(
            df["recovery_position"],
            [-np.inf, 0.05, 0.25, 0.50, 0.75, 0.95, np.inf],
            labels=["<=0.05", "0.05-0.25", "0.25-0.50", "0.50-0.75", "0.75-0.95", ">=0.95"],
        ).astype(str)
    else:
        df["recovery_pos_bin"] = "unknown"

    shell_cols = [f"shell_sym_all_{j}" for j in range(5) if f"shell_sym_all_{j}" in df.columns]
    if shell_cols:
        df["shell_pattern"] = df.apply(shell_pattern, axis=1)
        df["shell_active_count"] = df[shell_cols].abs().gt(1e-12).sum(axis=1)
    else:
        df["shell_pattern"] = "unknown"
        df["shell_active_count"] = np.nan

    features: list[dict[str, object]] = []
    for label, col in [
        ("tail", "is_tail"),
        ("scale", "scale_bin"),
        ("decade", "decade"),
        ("h", "h_bin"),
        ("mu", "mu_bin"),
        ("depth", "depth_bin"),
        ("pstar_mod_30", "pstar_mod_30"),
        ("y_mod_30", "y_mod_30"),
        ("h_mod_30", "h_mod_30"),
        ("short_boundary_proxy", "short_boundary_proxy"),
        ("recovery_position", "recovery_pos_bin"),
        ("shell_pattern", "shell_pattern"),
        ("shell_active_count", "shell_active_count"),
    ]:
        if col in df.columns:
            features.extend(summarize_group(df, label, col))

    features_df = pd.DataFrame(features)
    features_df = features_df.sort_values(["neg_max", "neg_frac"], ascending=[False, False])

    worst = df.sort_values("neg_Q", ascending=False).head(50).copy()
    keep_cols = [
        "block_id",
        "p_star",
        "y",
        "h",
        "canonical_z",
        "neg_Q",
        "is_tail",
        "scale_bin",
        "decade",
        "depth_bin",
        "mu_bin",
        "h_bin",
        "pstar_mod_30",
        "y_mod_30",
        "h_mod_30",
        "Q_pp",
        "Qpp_over_denom",
        "cp_ratio",
        "prime_count",
        "local_prime_count",
        "d_worst",
        "mu_over_sqrt_p",
        "recovery_position",
        "recovery_pos_bin",
        "shell_pattern",
        "shell_active_count",
        "canonical_scaled_E_post",
        "denom_sqrt_h_logB",
    ]
    keep_cols = [c for c in keep_cols if c in worst.columns]
    worst_out = worst[keep_cols]

    neg = df[df["is_negative"]].copy()
    tail = df[df["is_tail"].astype(str).str.lower().isin(["true", "1"])] if "is_tail" in df.columns else df.iloc[0:0]
    tail_neg = tail[tail["is_negative"]].copy()

    # Concentration check: if a small number of feature values carry most of the
    # negative mass, it points at a coherent arithmetic source.
    concentration = {}
    for col in ["scale_bin", "h_bin", "mu_bin", "depth_bin", "pstar_mod_30", "y_mod_30", "shell_pattern"]:
        if col in df.columns and len(neg):
            mass = neg.groupby(col)["neg_Q"].sum().sort_values(ascending=False)
            concentration[f"top_neg_mass_{col}"] = mass.index[0] if len(mass) else ""
            concentration[f"top_neg_mass_frac_{col}"] = (
                mass.iloc[0] / neg["neg_Q"].sum() if len(mass) and neg["neg_Q"].sum() else 0.0
            )

    summary = {
        "rows": len(df),
        "negative_rows": len(neg),
        "negative_frac": len(neg) / len(df) if len(df) else 0.0,
        "global_neg_max": df["neg_Q"].max(),
        "global_mean_z": df["canonical_z"].mean(),
        "global_std_z": df["canonical_z"].std(ddof=0),
        "tail_rows": len(tail),
        "tail_negative_rows": len(tail_neg),
        "tail_negative_frac": len(tail_neg) / len(tail) if len(tail) else 0.0,
        "tail_neg_max": tail["neg_Q"].max() if len(tail) else np.nan,
        "worst_block_id": worst.iloc[0]["block_id"] if len(worst) else np.nan,
        "worst_p_star": worst.iloc[0]["p_star"] if len(worst) else np.nan,
        "worst_y": worst.iloc[0]["y"] if len(worst) else np.nan,
        "worst_h": worst.iloc[0]["h"] if len(worst) else np.nan,
        "worst_is_tail": worst.iloc[0].get("is_tail", np.nan) if len(worst) else np.nan,
        "worst_scale_bin": worst.iloc[0].get("scale_bin", "") if len(worst) else "",
        "worst_mu_bin": worst.iloc[0].get("mu_bin", "") if len(worst) else "",
        "worst_depth_bin": worst.iloc[0].get("depth_bin", "") if len(worst) else "",
        "worst_h_bin": worst.iloc[0].get("h_bin", "") if len(worst) else "",
        "worst_Q_pp": worst.iloc[0].get("Q_pp", np.nan) if len(worst) else np.nan,
        "worst_Qpp_over_denom": worst.iloc[0].get("Qpp_over_denom", np.nan) if len(worst) else np.nan,
        "worst_shell_pattern": worst.iloc[0].get("shell_pattern", "") if len(worst) else "",
        "tail_worst_block_id": tail.sort_values("neg_Q", ascending=False).iloc[0]["block_id"] if len(tail) else np.nan,
        "tail_worst_p_star": tail.sort_values("neg_Q", ascending=False).iloc[0]["p_star"] if len(tail) else np.nan,
        "tail_worst_y": tail.sort_values("neg_Q", ascending=False).iloc[0]["y"] if len(tail) else np.nan,
        "tail_worst_h": tail.sort_values("neg_Q", ascending=False).iloc[0]["h"] if len(tail) else np.nan,
    }
    summary.update(concentration)
    summary_df = pd.DataFrame([summary])

    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(SUMMARY_OUT, index=False)
    features_df.to_csv(FEATURES_OUT, index=False)
    worst_out.to_csv(ROWS_OUT, index=False)

    top_features = features_df.head(20).copy()
    top_worst = worst_out.head(12).copy()

    with DOC_OUT.open("w", encoding="utf-8") as f:
        f.write("# Prime Mesh R2Q - O2 Negative Tail Source Audit\n\n")
        f.write("**Document:** `Prime_Mesh_R2Q_O2_Negative_Tail_Source_Audit_v1.md`  \n")
        f.write("**Project:** Prime Mesh Theory - RH Programme  \n")
        f.write("**Date:** 2026-05-06  \n")
        f.write("**Status:** O2-B source diagnostic\n\n")
        f.write("## 1. Purpose\n\n")
        f.write(
            "This audit asks whether the small negative values of the canonical "
            "post-response residual have a coherent arithmetic source.  The "
            "diagnostic classifies negative rows by scale, interval length, "
            "mu-bin, depth, residues, shell pattern, prime-power slack, and "
            "recovery-block position.\n\n"
        )
        f.write("The normalized residual is\n\n")
        f.write("\\[\n")
        f.write("z(J)=\\frac{\\mathcal E_{\\rm post}(J)}{\\sqrt{|J|}\\log^2 p^*}.\n")
        f.write("\\]\n\n")
        f.write("The negative obstruction size is \\([-z(J)]_+\\).\n\n")
        f.write("## 2. Summary\n\n")
        f.write(summary_df.T.reset_index().rename(columns={"index": "metric", 0: "value"}).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 3. Largest Negative Rows\n\n")
        f.write(top_worst.to_markdown(index=False))
        f.write("\n\n")
        f.write("## 4. Strongest Feature Concentrations\n\n")
        f.write(top_features.to_markdown(index=False))
        f.write("\n\n")
        f.write("## 5. Interpretation\n\n")
        f.write(
            "The purpose of this audit is source detection, not a new bound.  "
            "If the worst negative rows concentrate in one small arithmetic "
            "regime, O2-B should be split around that regime.  If the negative "
            "mass remains diffuse and below the existing envelope, O2-B should "
            "be treated as a centered fluctuation theorem plus finite-certificate "
            "support.\n\n"
        )
        f.write("---\n\n")
        f.write("*Prime Mesh Theory - RH Programme*\n")

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {FEATURES_OUT}")
    log(f"Wrote {ROWS_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k, v in summary.items():
        if k in [
            "negative_frac",
            "global_neg_max",
            "tail_negative_frac",
            "tail_neg_max",
            "worst_block_id",
            "worst_p_star",
            "worst_h",
            "worst_Qpp_over_denom",
            "worst_shell_pattern",
        ]:
            log(f"{k} = {v}")


if __name__ == "__main__":
    main()
