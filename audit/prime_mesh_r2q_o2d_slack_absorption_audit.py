#!/usr/bin/env python
"""O2-D slack absorption audit.

Quantifies prime-power slack, local boundary/missing-shell exposure, projection
leakage, and finite-zone certificate slack in the same O2 normalization.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
DOCS = ROOT / "docs" / "RH" / "notes"

INPUT = NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"
SUMMARY_OUT = NOTES / "prime_mesh_r2q_o2d_slack_absorption_summary.csv"
COMPONENTS_OUT = NOTES / "prime_mesh_r2q_o2d_slack_absorption_components.csv"
WORST_OUT = NOTES / "prime_mesh_r2q_o2d_slack_absorption_worst_rows.csv"
DOC_OUT = DOCS / "Prime_Mesh_R2Q_O2D_Slack_Absorption_Audit_v1.md"


def log(msg: str) -> None:
    from datetime import datetime

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def shell_pattern(row: pd.Series) -> str:
    bits = []
    for j in range(5):
        v = row.get(f"shell_sym_all_{j}", np.nan)
        if pd.isna(v):
            bits.append("?")
        elif abs(v) <= 1e-12:
            bits.append("0")
        else:
            bits.append("1")
    return "".join(bits)


def component_summary(df: pd.DataFrame, name: str, col: str) -> dict[str, object]:
    tail = df[df["is_tail_bool"]]
    finite = df[~df["is_tail_bool"]]
    idx = df[col].idxmax() if len(df) and df[col].notna().any() else None
    worst = df.loc[idx] if idx is not None else None
    return {
        "component": name,
        "rows": len(df),
        "max": df[col].max(),
        "tail_max": tail[col].max() if len(tail) else np.nan,
        "finite_max": finite[col].max() if len(finite) else np.nan,
        "mean": df[col].mean(),
        "q95": df[col].quantile(0.95),
        "q99": df[col].quantile(0.99),
        "nonzero_frac": float((df[col] > 0).mean()) if len(df) else np.nan,
        "worst_block_id": worst.get("block_id", np.nan) if worst is not None else np.nan,
        "worst_p_star": worst.get("p_star", np.nan) if worst is not None else np.nan,
        "worst_h": worst.get("h", np.nan) if worst is not None else np.nan,
        "worst_is_tail": worst.get("is_tail", np.nan) if worst is not None else np.nan,
        "worst_shell_pattern": worst.get("shell_pattern", "") if worst is not None else "",
    }


def main() -> None:
    log(f"Reading {INPUT}")
    df = pd.read_csv(INPUT)

    numeric_cols = [
        "canonical_scaled_E_post",
        "canonical_raw_E_post",
        "fitted_E_post",
        "canonical_scaled_response",
        "canonical_raw_response",
        "fitted_response",
        "denom_sqrt_h_logB",
        "Q_pp",
        "Qpp_over_denom",
        "canonical_scaled_Q_post",
        "canonical_raw_Q_post",
        "fitted_Q_post",
        "p_star",
        "y",
        "h",
        "block_id",
        "cp_ratio",
        "d_worst",
        "mu_over_sqrt_p",
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = num(df[c])

    denom = df["denom_sqrt_h_logB"].replace(0, np.nan)
    df["post_z"] = df["canonical_scaled_E_post"] / denom
    df["post_Q"] = (-df["post_z"]).clip(lower=0)
    df["fitted_z"] = df["fitted_E_post"] / denom
    df["fitted_Q"] = (-df["fitted_z"]).clip(lower=0)

    # Projection leakage: canonical theorem response versus exact fitted
    # projection comparator.  We measure both signed residual leakage and
    # response-vector leakage.
    df["leak_E_z_abs"] = ((df["canonical_scaled_E_post"] - df["fitted_E_post"]) / denom).abs()
    df["leak_response_z_abs"] = ((df["canonical_scaled_response"] - df["fitted_response"]) / denom).abs()
    df["leak_negative_extra_Q"] = (df["post_Q"] - df["fitted_Q"]).clip(lower=0)

    df["Qpp_norm"] = df["Qpp_over_denom"].fillna(0.0)
    df["shell_pattern"] = df.apply(shell_pattern, axis=1)
    df["shell_active_count"] = sum(
        df.get(f"shell_sym_all_{j}", pd.Series(np.nan, index=df.index)).abs().gt(1e-12) for j in range(5)
    )
    df["is_longa"] = df["shell_pattern"].eq("11111")
    df["missing_shell_proxy"] = ~df["is_longa"]
    df["short_window_proxy"] = df["h"] <= 8
    df["boundary_local_proxy"] = df["missing_shell_proxy"] | df["short_window_proxy"]
    df["boundary_proxy_Q"] = np.where(df["boundary_local_proxy"], df["post_Q"], 0.0)

    df["is_tail_bool"] = df["is_tail"].astype(str).str.lower().isin(["true", "1"]) if "is_tail" in df.columns else False
    # Finite certificate proxy: rows below the tail handoff.  This is not a
    # mathematical certificate by itself; it reports how much of the observed
    # post-response envelope lives in the finite zone.
    df["finite_zone_proxy"] = ~df["is_tail_bool"]
    df["finite_zone_Q"] = np.where(df["finite_zone_proxy"], df["post_Q"], 0.0)

    # Simple total observed slack proxy.  This intentionally overcounts because
    # these components are not independent; O2-D only needs to show budget
    # absorbability.
    df["slack_proxy_sum"] = (
        df["Qpp_norm"].fillna(0.0)
        + df["leak_negative_extra_Q"].fillna(0.0)
        + np.where(df["boundary_local_proxy"], df["post_Q"], 0.0)
    )

    components = [
        component_summary(df, "post_Q", "post_Q"),
        component_summary(df, "Qpp_norm", "Qpp_norm"),
        component_summary(df, "projection_leak_E_abs", "leak_E_z_abs"),
        component_summary(df, "projection_leak_response_abs", "leak_response_z_abs"),
        component_summary(df, "projection_leak_negative_extra", "leak_negative_extra_Q"),
        component_summary(df, "boundary_local_proxy_Q", "boundary_proxy_Q"),
        component_summary(df, "finite_zone_Q", "finite_zone_Q"),
        component_summary(df, "slack_proxy_sum_overcount", "slack_proxy_sum"),
    ]
    comp_df = pd.DataFrame(components).sort_values("max", ascending=False)

    worst = df.sort_values("slack_proxy_sum", ascending=False).head(50).copy()
    keep = [
        "block_id",
        "p_star",
        "y",
        "h",
        "post_z",
        "post_Q",
        "is_tail",
        "is_longa",
        "shell_pattern",
        "boundary_local_proxy",
        "short_window_proxy",
        "missing_shell_proxy",
        "Qpp_norm",
        "leak_E_z_abs",
        "leak_response_z_abs",
        "leak_negative_extra_Q",
        "finite_zone_Q",
        "slack_proxy_sum",
        "scale_bin",
        "depth_bin",
        "mu_bin",
        "cp_ratio",
    ]
    keep = [c for c in keep if c in worst.columns]
    worst_out = worst[keep]

    qpp_max = df["Qpp_norm"].max()
    leak_max = df["leak_negative_extra_Q"].max()
    boundary_max = df["boundary_proxy_Q"].max()
    finite_max = df["finite_zone_Q"].max()
    c_slack_proxy = max(qpp_max, leak_max, boundary_max)
    c_slack_sum_proxy = df["slack_proxy_sum"].max()

    summary = {
        "rows": len(df),
        "global_Qpost_max": df["post_Q"].max(),
        "tail_Qpost_max": df.loc[df["is_tail_bool"], "post_Q"].max() if df["is_tail_bool"].any() else np.nan,
        "Qpp_max": qpp_max,
        "Qpp_tail_max": df.loc[df["is_tail_bool"], "Qpp_norm"].max() if df["is_tail_bool"].any() else np.nan,
        "Qpp_over_denom_max": qpp_max,
        "boundary_local_slack_max": boundary_max,
        "boundary_local_slack_tail_max": df.loc[df["is_tail_bool"], "boundary_proxy_Q"].max()
        if df["is_tail_bool"].any()
        else np.nan,
        "projection_leakage_E_abs_max": df["leak_E_z_abs"].max(),
        "projection_leakage_response_abs_max": df["leak_response_z_abs"].max(),
        "projection_leakage_Q_proxy_max": leak_max,
        "finite_zone_Qpost_max": finite_max,
        "finite_zone_rows": int(df["finite_zone_proxy"].sum()),
        "C_slack_proxy_max_component": c_slack_proxy,
        "C_slack_proxy_sum_overcount": c_slack_sum_proxy,
        "passes_Cslack_0p25_component": bool(c_slack_proxy <= 0.25),
        "passes_Cslack_0p50_component": bool(c_slack_proxy <= 0.50),
        "passes_total_budget_1_component_plus_O2B_O2C_obs": bool(c_slack_proxy + 0.0394632013 + 0.0343723532 <= 1.0),
        "passes_sum_overcount_0p25": bool(c_slack_sum_proxy <= 0.25),
        "passes_sum_overcount_0p50": bool(c_slack_sum_proxy <= 0.50),
        "passes_sum_overcount_plus_O2B_O2C_obs_le_1": bool(c_slack_sum_proxy + 0.0394632013 + 0.0343723532 <= 1.0),
        "worst_slack_component": comp_df.iloc[0]["component"] if len(comp_df) else "",
        "worst_slack_block_id": comp_df.iloc[0]["worst_block_id"] if len(comp_df) else np.nan,
        "worst_slack_p_star": comp_df.iloc[0]["worst_p_star"] if len(comp_df) else np.nan,
        "worst_slack_value": comp_df.iloc[0]["max"] if len(comp_df) else np.nan,
    }

    summary_df = pd.DataFrame([summary])
    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(SUMMARY_OUT, index=False)
    comp_df.to_csv(COMPONENTS_OUT, index=False)
    worst_out.to_csv(WORST_OUT, index=False)

    with DOC_OUT.open("w", encoding="utf-8") as f:
        f.write("# Prime Mesh R2Q - O2-D Slack Absorption Audit\n\n")
        f.write("**Document:** `Prime_Mesh_R2Q_O2D_Slack_Absorption_Audit_v1.md`  \n")
        f.write("**Project:** Prime Mesh Theory - RH Programme  \n")
        f.write("**Date:** 2026-05-06  \n")
        f.write("**Status:** O2-D slack absorption diagnostic\n\n")
        f.write("## 1. Purpose\n\n")
        f.write(
            "This audit measures prime-power slack, local boundary/missing-shell "
            "exposure, projection leakage, and finite-zone certificate slack in "
            "the same O2 normalization.\n\n"
        )
        f.write("The main normalization is \\(\\sqrt{|J|}\\log^2p^*\\).\n\n")
        f.write("## 2. Summary\n\n")
        f.write(summary_df.T.reset_index().rename(columns={"index": "metric", 0: "value"}).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 3. Component Table\n\n")
        f.write(comp_df.to_markdown(index=False))
        f.write("\n\n")
        f.write("## 4. Worst Slack Proxy Rows\n\n")
        f.write(worst_out.head(20).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 5. Interpretation\n\n")
        f.write(
            "The component maximum is the theorem-facing conservative slack "
            "proxy.  The sum proxy is an intentional overcount, useful as a "
            "stress test but not as the exact decomposition because several "
            "terms overlap by construction.\n\n"
        )
        f.write("---\n\n")
        f.write("*Prime Mesh Theory - RH Programme*\n")

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {COMPONENTS_OUT}")
    log(f"Wrote {WORST_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k, v in summary.items():
        if k in [
            "global_Qpost_max",
            "tail_Qpost_max",
            "Qpp_max",
            "boundary_local_slack_max",
            "projection_leakage_Q_proxy_max",
            "C_slack_proxy_max_component",
            "C_slack_proxy_sum_overcount",
            "passes_total_budget_1_component_plus_O2B_O2C_obs",
            "worst_slack_component",
        ]:
            log(f"{k} = {v}")


if __name__ == "__main__":
    main()
