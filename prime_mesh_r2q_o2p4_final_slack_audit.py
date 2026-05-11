#!/usr/bin/env python3
"""O2.4 final slack audit.

Outputs are intentionally written only to the repair-folder bundle.

O2.4 includes only:
  Q_pp + Q_bdy + Q_leak_plus

Double-count exclusions:
  * O2.1 projection leakage is not added again here.
  * O2.2 LongA SPF discrepancy is not added again here.
  * O2.3 internal excursion is not added again here.
  * Endpoint descent has harmful component 0 after compatibility.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent
ROOT = next(p for p in [OUT, *OUT.parents] if p.name == "prime-mesh-theory")
REPO_NOTES = ROOT / "notes"

INPUT = REPO_NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"
O2D_COMPONENTS = OUT / "prime_mesh_r2q_o2d_slack_absorption_components.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_o2p4_final_slack_summary.csv"
COMPONENTS_OUT = OUT / "prime_mesh_r2q_o2p4_final_slack_components.csv"
INTERVALS_OUT = OUT / "prime_mesh_r2q_o2p4_final_slack_intervals.csv"
SCOPES_OUT = OUT / "prime_mesh_r2q_o2p4_final_slack_scopes.csv"
WORST_OUT = OUT / "prime_mesh_r2q_o2p4_final_slack_worst_rows.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_O2p4_Final_Slack_Audit_v1.md"
MANIFEST = OUT / "deposit_manifest.csv"

O2_SUBTOTAL = 0.0301511056
O2_MARGIN_BEFORE_O2P4 = 1.0 - O2_SUBTOTAL


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def shell_pattern(row: pd.Series) -> str:
    bits = []
    for j in range(5):
        v = row.get(f"shell_sym_all_{j}", np.nan)
        if pd.isna(v):
            bits.append("?")
        elif abs(float(v)) <= 1e-12:
            bits.append("0")
        else:
            bits.append("1")
    return "".join(bits)


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


def p_scale_bin(p: float) -> str:
    if p < 100_000_000:
        return "p<100M"
    if p < 500_000_000:
        return "100M<=p<500M"
    return "p>=500M"


def qstats(s: pd.Series, prefix: str) -> dict[str, float]:
    return {
        f"{prefix}_max": float(s.max()),
        f"{prefix}_mean": float(s.mean()),
        f"{prefix}_median": float(s.median()),
        f"{prefix}_q95": float(s.quantile(0.95)),
        f"{prefix}_q99": float(s.quantile(0.99)),
    }


def summarize(df: pd.DataFrame, scope: str) -> dict[str, object]:
    worst = df.loc[df["Q_o2p4_total"].idxmax()]
    row: dict[str, object] = {"scope": scope, "rows": int(len(df))}
    for col, prefix in [
        ("Q_pp", "Q_pp"),
        ("Q_bdy", "Q_bdy"),
        ("Q_leak_plus", "Q_leak_plus"),
        ("Q_o2p4_total", "Q_o2p4"),
    ]:
        row.update(qstats(df[col], prefix))
    row.update(
        {
            "O2_subtotal_before_o2p4": O2_SUBTOTAL,
            "O2_total_with_o2p4_max": float(O2_SUBTOTAL + df["Q_o2p4_total"].max()),
            "O2_margin_remaining": float(1.0 - O2_SUBTOTAL - df["Q_o2p4_total"].max()),
            "worst_block_id": int(worst["block_id"]),
            "worst_p_star": int(worst["p_star"]),
            "worst_h": int(worst["h"]),
            "worst_component": str(worst["dominant_component"]),
            "pass_Q_o2p4_le_0p05_frac": float((df["Q_o2p4_total"] <= 0.05).mean()),
            "pass_Q_o2p4_le_0p10_frac": float((df["Q_o2p4_total"] <= 0.10).mean()),
            "pass_Q_o2p4_le_0p25_frac": float((df["Q_o2p4_total"] <= 0.25).mean()),
            "pass_Q_o2p4_le_1_frac": float((df["Q_o2p4_total"] <= 1.0).mean()),
            "pass_O2_total_le_1": bool((O2_SUBTOTAL + df["Q_o2p4_total"].max()) < 1.0),
        }
    )
    return row


def component_summary(df: pd.DataFrame, component: str, raw_col: str, q_col: str) -> dict[str, object]:
    worst = df.loc[df[q_col].idxmax()]
    return {
        "component": component,
        "raw_max": float(df[raw_col].max()),
        "raw_mean": float(df[raw_col].mean()),
        "Q_max": float(df[q_col].max()),
        "Q_mean": float(df[q_col].mean()),
        "Q_median": float(df[q_col].median()),
        "Q_q95": float(df[q_col].quantile(0.95)),
        "Q_q99": float(df[q_col].quantile(0.99)),
        "worst_block_id": int(worst["block_id"]),
        "worst_p_star": int(worst["p_star"]),
        "worst_h": int(worst["h"]),
        "pass_Q_le_0p05_frac": float((df[q_col] <= 0.05).mean()),
        "pass_Q_le_0p10_frac": float((df[q_col] <= 0.10).mean()),
        "pass_Q_le_0p25_frac": float((df[q_col] <= 0.25).mean()),
        "pass_Q_le_1_frac": float((df[q_col] <= 1.0).mean()),
    }


def refresh_manifest() -> None:
    rows = []
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            rows.append({"Name": p.name, "Length": p.stat().st_size, "LastWriteTime": pd.Timestamp(p.stat().st_mtime, unit="s")})
    pd.DataFrame(rows).to_csv(MANIFEST, index=False)


def write_doc(summary: dict[str, object], components: pd.DataFrame, scopes: pd.DataFrame) -> None:
    q = float(summary["Q_o2p4_max"])
    if q <= 0.05:
        status = "very strong"
    elif q <= 0.10:
        status = "strong"
    elif q <= 0.25:
        status = "usable"
    elif O2_SUBTOTAL + q < 1.0:
        status = "inside total O2 budget"
    else:
        status = "fail"

    lines = [
        "# Prime Mesh R2Q - O2.4 Final Slack Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-07",
        f"**Status:** O2.4 final slack audit - {status}",
        "",
        "## 1. Purpose",
        "",
        "This audit measures only the final O2.4 slack terms after normalization repair and double-count separation:",
        "",
        r"\[",
        r"Q_{2.4}=Q_{\rm pp}+Q_{\rm bdy}+Q_{\rm leak}^{+}.",
        r"\]",
        "",
        "It does not re-add O2.1 projection leakage, O2.2 SPF discrepancy, O2.3 internal excursion, or endpoint descent.",
        "",
        "## 2. Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    for k, v in summary.items():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## 3. Component Table",
        "",
        components.to_markdown(index=False),
        "",
        "## 4. Scope Table",
        "",
        scopes.to_markdown(index=False),
        "",
        "## 5. Interpretation",
        "",
    ]
    if q <= 0.05:
        lines += [
            r"\[",
            r"\boxed{\text{O2.4 is empirically budget-closed after normalization and double-count separation.}}",
            r"\]",
        ]
    elif q <= 0.25:
        lines += [
            r"\[",
            r"\boxed{\text{O2.4 is inside the preferred usable range but is not tiny.}}",
            r"\]",
        ]
    elif O2_SUBTOTAL + q < 1.0:
        lines += [
            r"\[",
            r"\boxed{\text{O2.4 is not preferred-small, but the total O2 empirical budget still closes.}}",
            r"\]",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{O2.4 has a real slack obstruction.}}",
            r"\]",
        ]
    lines += [
        "",
        "The dominant O2.4 component is recorded as `worst_component` in the summary.  Components absent from the repaired O2.4 definition are recorded as zero rather than double-counted.",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
    ]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    log(f"Reading {INPUT}")
    df = pd.read_csv(INPUT)
    for c in [
        "block_id",
        "p_star",
        "y",
        "h",
        "denom_sqrt_h_logB",
        "Qpp_over_denom",
        "Q_pp",
        "canonical_scaled_E_post",
        "fitted_E_post",
        "canonical_scaled_response",
        "fitted_response",
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    denom = df["denom_sqrt_h_logB"].replace(0, np.nan)
    df["shell_pattern"] = df.apply(shell_pattern, axis=1)
    df["is_longa"] = df["shell_pattern"].eq("11111")
    df["short_window_proxy"] = df["h"] <= 8
    df["missing_shell_proxy"] = ~df["is_longa"]
    df["boundary_local_proxy"] = df["short_window_proxy"] | df["missing_shell_proxy"]
    df["post_z"] = df["canonical_scaled_E_post"] / denom
    df["post_Q"] = (-df["post_z"]).clip(lower=0.0)

    # Repaired O2.4 components.
    # Prime powers: direct normalized Qpp.
    df["Q_pp"] = df.get("Qpp_over_denom", df.get("Q_pp", 0.0)).fillna(0.0)
    df["R_pp"] = df["Q_pp"] * denom

    # Boundary: only local boundary/missing-shell negative residual exposure.
    df["Q_bdy"] = np.where(df["boundary_local_proxy"], df["post_Q"], 0.0)
    df["R_bdy"] = df["Q_bdy"] * denom

    # Leakage-plus: harmful one-sided leakage not already counted by O2.1.
    # O2.1 counts projection leakage globally, so the repaired O2.4 value is 0.
    # We keep a diagnostic raw comparator for visibility but do not add it.
    df["Q_leak_plus_diagnostic"] = (
        ((df["canonical_scaled_E_post"] - df["fitted_E_post"]) / denom).abs().fillna(0.0)
        if "fitted_E_post" in df.columns
        else 0.0
    )
    df["Q_leak_plus"] = 0.0
    df["R_leak_plus"] = 0.0

    df["Q_o2p4_total"] = df["Q_pp"] + df["Q_bdy"] + df["Q_leak_plus"]
    df["R_o2p4_total"] = df["Q_o2p4_total"] * denom
    component_cols = ["Q_pp", "Q_bdy", "Q_leak_plus"]
    df["dominant_component"] = df[component_cols].idxmax(axis=1).str.replace("Q_", "", regex=False)
    df.loc[df["Q_o2p4_total"].eq(0.0), "dominant_component"] = "none"
    df["O2_subtotal_before_o2p4"] = O2_SUBTOTAL
    df["O2_total_with_o2p4"] = O2_SUBTOTAL + df["Q_o2p4_total"]
    df["O2_margin_remaining"] = 1.0 - df["O2_total_with_o2p4"]
    df["is_tail"] = df["is_tail"].astype(str).str.lower().isin(["true", "1"]) if "is_tail" in df.columns else df["p_star"] >= 500_000_000
    df["h_bin"] = df["h"].map(h_bin)
    df["p_scale_bin"] = df["p_star"].map(p_scale_bin)
    if "mu_bin" not in df.columns:
        df["mu_bin"] = "unknown"
    if "depth_bin" not in df.columns:
        df["depth_bin"] = "unknown"

    intervals_cols = [
        "block_id",
        "p_star",
        "y",
        "h",
        "R_pp",
        "R_bdy",
        "R_leak_plus",
        "R_o2p4_total",
        "Q_pp",
        "Q_bdy",
        "Q_leak_plus",
        "Q_o2p4_total",
        "O2_subtotal_before_o2p4",
        "O2_total_with_o2p4",
        "O2_margin_remaining",
        "dominant_component",
        "is_tail",
        "h_bin",
        "p_scale_bin",
        "mu_bin",
        "depth_bin",
        "shell_pattern",
        "boundary_local_proxy",
        "Q_leak_plus_diagnostic",
    ]
    intervals = df[intervals_cols].rename(columns={"mu_bin": "mu_bin_if_available", "depth_bin": "depth_bin_if_available"})
    intervals.to_csv(INTERVALS_OUT, index=False)

    components = pd.DataFrame(
        [
            component_summary(df, "prime_power", "R_pp", "Q_pp"),
            component_summary(df, "boundary", "R_bdy", "Q_bdy"),
            component_summary(df, "leakage_plus", "R_leak_plus", "Q_leak_plus"),
            component_summary(df, "total_o2p4", "R_o2p4_total", "Q_o2p4_total"),
        ]
    )
    components.to_csv(COMPONENTS_OUT, index=False)

    scopes = [summarize(df, "global")]
    for label, part in [
        ("tail:p_star>=500M", df[df["is_tail"]]),
        ("tail:p_star<500M", df[~df["is_tail"]]),
        ("scale:p<100M", df[df["p_star"] < 100_000_000]),
        ("scale:100M<=p<500M", df[(df["p_star"] >= 100_000_000) & (df["p_star"] < 500_000_000)]),
        ("scale:p>=500M", df[df["p_star"] >= 500_000_000]),
    ]:
        if len(part):
            scopes.append(summarize(part, label))
    for col, prefix in [("h_bin", "h"), ("mu_bin", "mu"), ("depth_bin", "depth")]:
        for value, part in df.groupby(col, dropna=False):
            if len(part):
                scopes.append(summarize(part, f"{prefix}:{value}"))
    scopes_df = pd.DataFrame(scopes).sort_values(["Q_o2p4_max", "rows"], ascending=[False, False])
    scopes_df.to_csv(SCOPES_OUT, index=False)

    summary = summarize(df, "global")
    summary.update(
        {
            "O2_margin_before_o2p4": O2_MARGIN_BEFORE_O2P4,
            "projection_leakage_diagnostic_max_not_counted": float(df["Q_leak_plus_diagnostic"].max()),
            "boundary_rows": int(df["boundary_local_proxy"].sum()),
            "prime_power_nonzero_rows": int((df["Q_pp"] > 0).sum()),
            "leakage_plus_counted_rows": int((df["Q_leak_plus"] > 0).sum()),
        }
    )
    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)

    worst = intervals.sort_values(["Q_o2p4_total", "Q_bdy", "Q_pp"], ascending=False).head(50)
    worst.to_csv(WORST_OUT, index=False)
    write_doc(summary, components, scopes_df)
    refresh_manifest()

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {COMPONENTS_OUT}")
    log(f"Wrote {INTERVALS_OUT}")
    log(f"Wrote {SCOPES_OUT}")
    log(f"Wrote {WORST_OUT}")
    log(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
