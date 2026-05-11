#!/usr/bin/env python
"""Audit candidate reflected coordinates for positive local theta excess.

Input is the theta comparison row table, already self-checked against an
independent theta sieve.  We focus on intervals with

    E_theta(J) = theta(y+h)-theta(y)-h > 0

and ask which R2Q coordinate sees that positive side:
  - sign-reflected D_N coordinates;
  - local bridge increments;
  - prime/composite imbalance coordinates;
  - K4 response orientations;
  - simple delayed transport to subsequent negative local-theta intervals.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
DOCS = ROOT / "docs" / "RH" / "notes"

THETA_ROWS = NOTES / "prime_mesh_r2q_theta_comparison_audit_rows.csv"
INTERVALS = NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"

SUMMARY_OUT = NOTES / "prime_mesh_r2q_theta_positive_side_candidate_summary.csv"
COORDS_OUT = NOTES / "prime_mesh_r2q_theta_positive_side_candidate_coordinates.csv"
ROWS_OUT = NOTES / "prime_mesh_r2q_theta_positive_side_candidate_rows.csv"
TRANSPORT_OUT = NOTES / "prime_mesh_r2q_theta_positive_side_candidate_transport.csv"
DOC_OUT = DOCS / "Prime_Mesh_R2Q_Theta_Positive_Side_Candidate_Audit_v1.md"


def log(msg: str) -> None:
    from datetime import datetime

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def summarize_coord(df: pd.DataFrame, coord: str, target: str = "theta_local_norm_pos") -> dict[str, object]:
    d = df[[coord, target]].replace([np.inf, -np.inf], np.nan).dropna()
    pos = df[df[target] > 0]
    neg = df[df[target] <= 0]
    if len(d) > 2 and d[coord].std(ddof=0) > 0 and d[target].std(ddof=0) > 0:
        corr = d[coord].corr(d[target])
        abs_corr = d[coord].abs().corr(d[target].abs())
    else:
        corr = np.nan
        abs_corr = np.nan

    # Orientation score: larger coordinate should mean more positive theta.
    pos_median = pos[coord].median() if len(pos) else np.nan
    neg_median = neg[coord].median() if len(neg) else np.nan
    separation = pos_median - neg_median if pd.notna(pos_median) and pd.notna(neg_median) else np.nan
    if len(pos):
        threshold = pos[coord].quantile(0.10)
        recall_at_pos_q10 = float((pos[coord] >= threshold).mean())
        false_pos_at_pos_q10 = float((neg[coord] >= threshold).mean()) if len(neg) else np.nan
    else:
        threshold = np.nan
        recall_at_pos_q10 = np.nan
        false_pos_at_pos_q10 = np.nan

    return {
        "coordinate": coord,
        "rows_valid": len(d),
        "corr_with_positive_theta": corr,
        "abs_corr_with_abs_theta": abs_corr,
        "positive_median": pos_median,
        "nonpositive_median": neg_median,
        "median_separation_pos_minus_nonpos": separation,
        "positive_q90": pos[coord].quantile(0.90) if len(pos) else np.nan,
        "nonpositive_q90": neg[coord].quantile(0.90) if len(neg) else np.nan,
        "threshold_pos_q10": threshold,
        "recall_at_pos_q10": recall_at_pos_q10,
        "false_positive_at_pos_q10": false_pos_at_pos_q10,
        "max_on_positive": pos[coord].max() if len(pos) else np.nan,
        "min_on_positive": pos[coord].min() if len(pos) else np.nan,
    }


def main() -> None:
    log(f"Reading {THETA_ROWS}")
    theta = pd.read_csv(THETA_ROWS)
    log(f"Reading {INTERVALS}")
    intervals = pd.read_csv(INTERVALS)

    # Merge by stable identifying fields rather than index.
    keys = ["block_id", "p_star", "y", "h"]
    for df in [theta, intervals]:
        for c in keys:
            if c in df.columns:
                df[c] = num(df[c])
    df = theta.merge(intervals, on=keys, how="left", suffixes=("", "_src"))

    numeric_cols = [
        "theta_local_error",
        "theta_local_norm",
        "theta_end_error",
        "theta_end_norm",
        "theta_pstar_error",
        "theta_pstar_norm",
        "D_y",
        "D_y_plus_h",
        "observed_delta",
        "drift_term",
        "P_prime_shock",
        "R_eff_repayment",
        "R_eff_minus_P",
        "cp_residual",
        "cp_obstruction",
        "cp_ratio",
        "Q_max",
        "canonical_scaled_E_post",
        "canonical_scaled_response",
        "denom_sqrt_h_logB",
        "k4_sym_all",
        "k4_sym_comp",
        "response_used_k4_sym_all",
        "response_used_neg_k4_sym_all",
        "response_used_k4_sym_comp",
        "response_used_neg_k4_sym_comp",
        "fitted_response",
        "canonical_raw_response",
        "h",
        "p_star",
        "y",
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = num(df[c])

    denom = df["denom_sqrt_h_logB"].replace(0, np.nan)
    df["theta_local_norm_pos"] = df["theta_local_norm"].clip(lower=0)
    df["theta_local_norm_neg"] = (-df["theta_local_norm"]).clip(lower=0)
    df["is_theta_local_positive"] = df["theta_local_error"] > 0
    df["is_theta_local_negative"] = df["theta_local_error"] < 0

    # Candidate reflected coordinates.
    df["D_start_norm"] = df["D_y"] / np.sqrt(df["p_star"])
    df["neg_D_start_norm"] = -df["D_start_norm"]
    df["D_end_norm"] = df["D_y_plus_h"] / np.sqrt(df["p_star"])
    df["neg_D_end_norm"] = -df["D_end_norm"]
    df["delta_D_norm"] = (df["D_y_plus_h"] - df["D_y"]) / np.sqrt(df["p_star"])
    df["neg_delta_D_norm"] = -df["delta_D_norm"]
    df["prime_minus_repay_norm"] = (df["P_prime_shock"] - df["R_eff_repayment"]) / denom
    df["repay_minus_prime_norm"] = (df["R_eff_repayment"] - df["P_prime_shock"]) / denom
    df["cp_residual_norm"] = df["cp_residual"] / denom
    df["neg_cp_residual_norm"] = -df["cp_residual_norm"]
    df["cp_obstruction_norm"] = df["cp_obstruction"] / denom
    df["Qmax"] = df["Q_max"]
    df["neg_Qmax"] = -df["Q_max"]
    if "canonical_scaled_response" in df.columns:
        df["canonical_response_norm"] = df["canonical_scaled_response"] / denom
        df["neg_canonical_response_norm"] = -df["canonical_response_norm"]
    if "k4_sym_all" in df.columns:
        df["k4_sym_all_norm"] = df["k4_sym_all"] / denom
        df["neg_k4_sym_all_norm"] = -df["k4_sym_all_norm"]
    if "k4_sym_comp" in df.columns:
        df["k4_sym_comp_norm"] = df["k4_sym_comp"] / denom
        df["neg_k4_sym_comp_norm"] = -df["k4_sym_comp_norm"]

    candidate_cols = [
        "D_start_norm",
        "neg_D_start_norm",
        "D_end_norm",
        "neg_D_end_norm",
        "delta_D_norm",
        "neg_delta_D_norm",
        "prime_minus_repay_norm",
        "repay_minus_prime_norm",
        "cp_residual_norm",
        "neg_cp_residual_norm",
        "cp_obstruction_norm",
        "Qmax",
        "neg_Qmax",
        "canonical_response_norm",
        "neg_canonical_response_norm",
        "k4_sym_all_norm",
        "neg_k4_sym_all_norm",
        "k4_sym_comp_norm",
        "neg_k4_sym_comp_norm",
    ]
    candidate_cols = [c for c in candidate_cols if c in df.columns]
    coord_df = pd.DataFrame([summarize_coord(df, c) for c in candidate_cols])
    coord_df = coord_df.sort_values("corr_with_positive_theta", ascending=False)

    pos = df[df["is_theta_local_positive"]].copy()
    neg = df[df["is_theta_local_negative"]].copy()

    # Delayed transport: for each positive local theta row, find the next later
    # negative local theta row in the same block, if any.
    transport_rows = []
    for block_id, g in df.sort_values(["block_id", "y", "h"]).groupby("block_id", dropna=False):
        g = g.reset_index(drop=True)
        neg_indices = g.index[g["is_theta_local_negative"]].tolist()
        for i, row in g[g["is_theta_local_positive"]].iterrows():
            later = [j for j in neg_indices if g.loc[j, "y"] >= row["y"]]
            if later:
                j = later[0]
                nrow = g.loc[j]
                transport_rows.append(
                    {
                        "block_id": block_id,
                        "p_star": row["p_star"],
                        "pos_y": row["y"],
                        "pos_h": row["h"],
                        "pos_theta_local_norm": row["theta_local_norm"],
                        "neg_y": nrow["y"],
                        "neg_h": nrow["h"],
                        "neg_theta_local_norm": nrow["theta_local_norm"],
                        "lag": nrow["y"] - row["y"],
                        "neg_abs_over_pos": (-nrow["theta_local_norm"]) / row["theta_local_norm"]
                        if row["theta_local_norm"] > 0
                        else np.nan,
                    }
                )
            else:
                transport_rows.append(
                    {
                        "block_id": block_id,
                        "p_star": row["p_star"],
                        "pos_y": row["y"],
                        "pos_h": row["h"],
                        "pos_theta_local_norm": row["theta_local_norm"],
                        "neg_y": np.nan,
                        "neg_h": np.nan,
                        "neg_theta_local_norm": np.nan,
                        "lag": np.nan,
                        "neg_abs_over_pos": np.nan,
                    }
                )
    transport = pd.DataFrame(transport_rows)

    best = coord_df.iloc[0] if len(coord_df) else pd.Series(dtype=object)
    summary = {
        "rows": len(df),
        "positive_theta_rows": len(pos),
        "negative_theta_rows": len(neg),
        "positive_theta_frac": len(pos) / len(df) if len(df) else np.nan,
        "negative_theta_frac": len(neg) / len(df) if len(df) else np.nan,
        "best_positive_side_coordinate": best.get("coordinate", ""),
        "best_corr_positive_theta": best.get("corr_with_positive_theta", np.nan),
        "best_abs_corr_abs_theta": best.get("abs_corr_with_abs_theta", np.nan),
        "best_median_separation": best.get("median_separation_pos_minus_nonpos", np.nan),
        "positive_side_Qmax_current_R2Q": pos["Q_max"].max() if len(pos) and "Q_max" in pos else np.nan,
        "negative_side_Qmax_current_R2Q": neg["Q_max"].max() if len(neg) and "Q_max" in neg else np.nan,
        "positive_side_current_R2Q_pass_frac_Q_le_1": float((pos["Q_max"] <= 1).mean()) if len(pos) and "Q_max" in pos else np.nan,
        "positive_side_current_R2Q_pass_frac_Q_le_0p75": float((pos["Q_max"] <= 0.75).mean()) if len(pos) and "Q_max" in pos else np.nan,
        "transport_positive_rows": len(transport),
        "transport_has_later_negative_frac": float(transport["neg_y"].notna().mean()) if len(transport) else np.nan,
        "transport_median_lag": transport["lag"].median() if len(transport) else np.nan,
        "transport_median_neg_abs_over_pos": transport["neg_abs_over_pos"].median() if len(transport) else np.nan,
        "transport_cover_frac_neg_abs_ge_pos": float((transport["neg_abs_over_pos"] >= 1).mean()) if len(transport) else np.nan,
    }

    rows_keep = [
        "block_id",
        "p_star",
        "y",
        "h",
        "theta_local_error",
        "theta_local_norm",
        "theta_local_norm_pos",
        "Q_max",
        "D_start_norm",
        "D_end_norm",
        "delta_D_norm",
        "prime_minus_repay_norm",
        "repay_minus_prime_norm",
        "cp_residual_norm",
        "cp_obstruction_norm",
        "canonical_response_norm",
        "k4_sym_all_norm",
        "k4_sym_comp_norm",
        "is_tail",
        "scale_bin",
        "depth_bin",
        "mu_bin",
    ]
    rows_keep = [c for c in rows_keep if c in df.columns]

    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)
    coord_df.to_csv(COORDS_OUT, index=False)
    df.sort_values("theta_local_norm", ascending=False)[rows_keep].to_csv(ROWS_OUT, index=False)
    transport.to_csv(TRANSPORT_OUT, index=False)

    with DOC_OUT.open("w", encoding="utf-8") as f:
        f.write("# Prime Mesh R2Q - Theta Positive-Side Candidate Audit\n\n")
        f.write("**Document:** `Prime_Mesh_R2Q_Theta_Positive_Side_Candidate_Audit_v1.md`  \n")
        f.write("**Project:** Prime Mesh Theory - RH Programme  \n")
        f.write("**Date:** 2026-05-06  \n")
        f.write("**Status:** positive-side reflected-coordinate diagnostic\n\n")
        f.write("## 1. Purpose\n\n")
        f.write(
            "This audit searches for a reflected R2Q coordinate that detects "
            "local positive Chebyshev excess \\(E_\\theta(J)>0\\).  It also tests "
            "a simple transport idea: whether positive local excess is followed "
            "inside the same block by a negative local theta interval.\n\n"
        )
        f.write("## 2. Summary\n\n")
        f.write(pd.DataFrame([summary]).T.reset_index().rename(columns={"index": "metric", 0: "value"}).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 3. Candidate Coordinates\n\n")
        f.write(coord_df.to_markdown(index=False))
        f.write("\n\n")
        f.write("## 4. Transport Summary\n\n")
        f.write(transport.describe(include="all").to_markdown())
        f.write("\n\n")
        f.write("## 5. Interpretation\n\n")
        f.write(
            "The strongest coordinate by correlation is the first candidate "
            "for a positive-side dual.  If all correlations are weak or if "
            "transport coverage is poor, the positive side likely requires a "
            "new construction rather than a simple sign reversal.\n\n"
        )
        f.write("---\n\n")
        f.write("*Prime Mesh Theory - RH Programme*\n")

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {COORDS_OUT}")
    log(f"Wrote {ROWS_OUT}")
    log(f"Wrote {TRANSPORT_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k, v in summary.items():
        log(f"{k} = {v}")


if __name__ == "__main__":
    main()
