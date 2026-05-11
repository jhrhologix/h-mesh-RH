#!/usr/bin/env python
"""O2-C delayed/nonlocal recovery bookkeeping audit.

O2-C is not a new repayment theorem: the exact bridge identity already gives
total repayment.  This audit asks whether the post-response leftover shows a
delayed/nonlocal negative obstruction pattern after the O1 local shell response
has been installed.

We therefore examine the canonical post-response residual by recovery position,
interval length, scale, LongA/non-LongA channel, and repayment ratios.  A true
delayed-recovery obstruction would show up as growth in late recovery bins,
long windows, or large-h/nonlocal regimes.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
DOCS = ROOT / "docs" / "RH" / "notes"

INPUT = NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"

SUMMARY_OUT = NOTES / "prime_mesh_r2q_o2c_delayed_recovery_bookkeeping_summary.csv"
SCOPES_OUT = NOTES / "prime_mesh_r2q_o2c_delayed_recovery_bookkeeping_scopes.csv"
WORST_OUT = NOTES / "prime_mesh_r2q_o2c_delayed_recovery_bookkeeping_worst_rows.csv"
DOC_OUT = DOCS / "Prime_Mesh_R2Q_O2C_Delayed_Recovery_Bookkeeping_Audit_v1.md"


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


def summarize(df: pd.DataFrame, scope: str) -> dict[str, object]:
    neg = df[df["post_z"] < 0]
    return {
        "scope": scope,
        "rows": len(df),
        "neg_rows": len(neg),
        "neg_frac": len(neg) / len(df) if len(df) else 0.0,
        "mean_post_z": df["post_z"].mean(),
        "std_post_z": df["post_z"].std(ddof=0),
        "min_post_z": df["post_z"].min(),
        "max_post_z": df["post_z"].max(),
        "neg_max": (-neg["post_z"]).max() if len(neg) else 0.0,
        "q05_post_z": df["post_z"].quantile(0.05) if len(df) else np.nan,
        "q95_post_z": df["post_z"].quantile(0.95) if len(df) else np.nan,
        "median_h": df["h"].median() if "h" in df else np.nan,
        "median_recovery_position": df["recovery_position"].median() if "recovery_position" in df else np.nan,
        "median_cp_ratio": df["cp_ratio"].median() if "cp_ratio" in df else np.nan,
        "median_R_eff_over_P": df["R_eff_over_P"].median() if "R_eff_over_P" in df else np.nan,
        "median_response_over_obstruction": df["response_over_obstruction"].median()
        if "response_over_obstruction" in df
        else np.nan,
        "median_Qpp_over_denom": df["Qpp_over_denom"].median() if "Qpp_over_denom" in df else np.nan,
    }


def corr_pair(df: pd.DataFrame, x: str, y: str) -> float:
    if x not in df.columns or y not in df.columns:
        return np.nan
    d = df[[x, y]].dropna()
    if len(d) < 3:
        return np.nan
    if d[x].std(ddof=0) == 0 or d[y].std(ddof=0) == 0:
        return np.nan
    return float(d[x].corr(d[y]))


def main() -> None:
    log(f"Reading {INPUT}")
    df = pd.read_csv(INPUT)

    for c in [
        "canonical_scaled_E_post",
        "canonical_scaled_response",
        "denom_sqrt_h_logB",
        "cp_obstruction",
        "cp_residual",
        "cp_ratio",
        "R_eff_repayment",
        "R_eff_over_P",
        "P_prime_shock",
        "Q_pp",
        "Qpp_over_denom",
        "h",
        "y",
        "p_star",
        "block_id",
        "worst_prime",
        "end_prime",
        "L_recovery",
        "mu_over_sqrt_p",
        "d_worst",
    ]:
        if c in df.columns:
            df[c] = num(df[c])

    denom = df["denom_sqrt_h_logB"].replace(0, np.nan)
    df["post_z"] = df["canonical_scaled_E_post"] / denom
    df["neg_Q"] = (-df["post_z"]).clip(lower=0)

    if "cp_obstruction" in df.columns:
        obstruction = df["cp_obstruction"].replace(0, np.nan)
        df["response_over_obstruction"] = df["canonical_scaled_response"] / obstruction
        df["post_over_obstruction"] = df["canonical_scaled_E_post"] / obstruction
    else:
        df["response_over_obstruction"] = np.nan
        df["post_over_obstruction"] = np.nan

    if {"y", "worst_prime", "L_recovery"}.issubset(df.columns):
        df["recovery_position"] = (df["y"] - df["worst_prime"]) / df["L_recovery"].replace(0, np.nan)
    else:
        df["recovery_position"] = np.nan

    df["recovery_pos_bin"] = pd.cut(
        df["recovery_position"],
        [-np.inf, 0.0, 0.05, 0.25, 0.50, 0.75, 0.95, np.inf],
        labels=["<=0", "0-0.05", "0.05-0.25", "0.25-0.50", "0.50-0.75", "0.75-0.95", ">=0.95"],
    ).astype(str)
    df["h_bin"] = df["h"].map(h_bin)
    df["shell_pattern"] = df.apply(shell_pattern, axis=1)
    df["is_longa"] = df["shell_pattern"].eq("11111")
    df["delayed_risk_proxy"] = df["h"].gt(8192) | df["recovery_position"].gt(0.50)
    df["late_recovery_proxy"] = df["recovery_position"].gt(0.50)
    df["long_window_proxy"] = df["h"].gt(8192)

    scopes: list[dict[str, object]] = [summarize(df, "global")]
    for col, prefix in [
        ("is_tail", "tail"),
        ("is_longa", "LongA"),
        ("delayed_risk_proxy", "delayed_risk_proxy"),
        ("late_recovery_proxy", "late_recovery_proxy"),
        ("long_window_proxy", "long_window_proxy"),
        ("recovery_pos_bin", "recovery_position"),
        ("h_bin", "h"),
        ("scale_bin", "scale"),
        ("decade", "decade"),
        ("depth_bin", "depth"),
        ("mu_bin", "mu"),
        ("shell_pattern", "shell_pattern"),
    ]:
        if col in df.columns:
            for key, g in df.groupby(col, dropna=False):
                scopes.append(summarize(g, f"{prefix}:{key}"))

    scopes_df = pd.DataFrame(scopes).sort_values(["neg_max", "rows"], ascending=[False, False])

    worst = df.sort_values("neg_Q", ascending=False).head(50).copy()
    keep = [
        "block_id",
        "p_star",
        "y",
        "h",
        "post_z",
        "neg_Q",
        "is_tail",
        "is_longa",
        "scale_bin",
        "decade",
        "depth_bin",
        "mu_bin",
        "h_bin",
        "recovery_position",
        "recovery_pos_bin",
        "delayed_risk_proxy",
        "late_recovery_proxy",
        "long_window_proxy",
        "cp_ratio",
        "R_eff_over_P",
        "response_over_obstruction",
        "post_over_obstruction",
        "Q_pp",
        "Qpp_over_denom",
        "shell_pattern",
        "canonical_scaled_E_post",
        "canonical_scaled_response",
        "denom_sqrt_h_logB",
    ]
    keep = [c for c in keep if c in worst.columns]
    worst_out = worst[keep]

    tail = df[df["is_tail"].astype(str).str.lower().isin(["true", "1"])] if "is_tail" in df.columns else df.iloc[0:0]
    delayed = df[df["delayed_risk_proxy"]]
    late = df[df["late_recovery_proxy"]]
    longw = df[df["long_window_proxy"]]

    summary = {
        "rows": len(df),
        "global_neg_max": df["neg_Q"].max(),
        "global_neg_frac": float((df["post_z"] < 0).mean()),
        "tail_neg_max": tail["neg_Q"].max() if len(tail) else np.nan,
        "tail_neg_frac": float((tail["post_z"] < 0).mean()) if len(tail) else np.nan,
        "longa_neg_max": df.loc[df["is_longa"], "neg_Q"].max() if df["is_longa"].any() else np.nan,
        "non_longa_neg_max": df.loc[~df["is_longa"], "neg_Q"].max() if (~df["is_longa"]).any() else np.nan,
        "delayed_risk_rows": len(delayed),
        "delayed_risk_neg_max": delayed["neg_Q"].max() if len(delayed) else np.nan,
        "delayed_risk_neg_frac": float((delayed["post_z"] < 0).mean()) if len(delayed) else np.nan,
        "late_recovery_rows": len(late),
        "late_recovery_neg_max": late["neg_Q"].max() if len(late) else np.nan,
        "late_recovery_neg_frac": float((late["post_z"] < 0).mean()) if len(late) else np.nan,
        "long_window_rows": len(longw),
        "long_window_neg_max": longw["neg_Q"].max() if len(longw) else np.nan,
        "long_window_neg_frac": float((longw["post_z"] < 0).mean()) if len(longw) else np.nan,
        "corr_negQ_h": corr_pair(df, "neg_Q", "h"),
        "corr_negQ_recovery_position": corr_pair(df, "neg_Q", "recovery_position"),
        "corr_negQ_cp_ratio": corr_pair(df, "neg_Q", "cp_ratio"),
        "corr_negQ_R_eff_over_P": corr_pair(df, "neg_Q", "R_eff_over_P"),
        "corr_negQ_response_over_obstruction": corr_pair(df, "neg_Q", "response_over_obstruction"),
        "pass_global_Q_le_1": float((df["neg_Q"] <= 1).mean()),
        "pass_global_Q_le_0p1": float((df["neg_Q"] <= 0.1).mean()),
        "pass_global_Q_le_0p05": float((df["neg_Q"] <= 0.05).mean()),
        "worst_block_id": worst.iloc[0]["block_id"] if len(worst) else np.nan,
        "worst_p_star": worst.iloc[0]["p_star"] if len(worst) else np.nan,
        "worst_h": worst.iloc[0]["h"] if len(worst) else np.nan,
        "worst_recovery_position": worst.iloc[0]["recovery_position"] if len(worst) else np.nan,
        "worst_delayed_risk_proxy": worst.iloc[0]["delayed_risk_proxy"] if len(worst) else np.nan,
        "worst_is_longa": worst.iloc[0]["is_longa"] if len(worst) else np.nan,
        "worst_Qpp_over_denom": worst.iloc[0].get("Qpp_over_denom", np.nan) if len(worst) else np.nan,
    }

    summary_df = pd.DataFrame([summary])
    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(SUMMARY_OUT, index=False)
    scopes_df.to_csv(SCOPES_OUT, index=False)
    worst_out.to_csv(WORST_OUT, index=False)

    with DOC_OUT.open("w", encoding="utf-8") as f:
        f.write("# Prime Mesh R2Q - O2-C Delayed Recovery Bookkeeping Audit\n\n")
        f.write("**Document:** `Prime_Mesh_R2Q_O2C_Delayed_Recovery_Bookkeeping_Audit_v1.md`  \n")
        f.write("**Project:** Prime Mesh Theory - RH Programme  \n")
        f.write("**Date:** 2026-05-06  \n")
        f.write("**Status:** O2-C delayed/nonlocal source diagnostic\n\n")
        f.write("## 1. Purpose\n\n")
        f.write(
            "This audit checks whether delayed or nonlocal recovery creates a "
            "new negative obstruction after the local O1/O2-A response is "
            "installed.  It does not attempt to prove repayment exists; total "
            "repayment is already fixed by the bridge identity.\n\n"
        )
        f.write("The measured obstruction is\n\n")
        f.write("\\[\n")
        f.write("[-\\mathcal E_{\\rm post}(J)]_+/\\left(\\sqrt{|J|}\\log^2p^*\\right).\n")
        f.write("\\]\n\n")
        f.write("Delayed-risk proxy rows are intervals with either long windows ")
        f.write("\\(h>8192\\) or recovery position \\(>0.50\\).\n\n")
        f.write("## 2. Summary\n\n")
        f.write(summary_df.T.reset_index().rename(columns={"index": "metric", 0: "value"}).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 3. Worst Rows\n\n")
        f.write(worst_out.head(15).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 4. Scope Table\n\n")
        f.write(scopes_df.head(35).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 5. Interpretation\n\n")
        f.write(
            "If delayed/nonlocal recovery were a separate obstruction, the "
            "negative envelope should grow in late recovery bins, long-window "
            "bins, or the delayed-risk proxy.  The audit should be read through "
            "that lens.\n\n"
        )
        f.write("---\n\n")
        f.write("*Prime Mesh Theory - RH Programme*\n")

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {SCOPES_OUT}")
    log(f"Wrote {WORST_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k in [
        "global_neg_max",
        "tail_neg_max",
        "delayed_risk_neg_max",
        "late_recovery_neg_max",
        "long_window_neg_max",
        "corr_negQ_recovery_position",
        "pass_global_Q_le_0p05",
        "worst_delayed_risk_proxy",
    ]:
        log(f"{k} = {summary[k]}")


if __name__ == "__main__":
    main()
