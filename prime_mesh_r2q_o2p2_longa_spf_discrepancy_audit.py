#!/usr/bin/env python
"""O2.2 LongA SPF discrepancy audit.

For LongA intervals, measure weighted SPF-class discrepancy:

    sum_q g(q)^2 |N_q(J) - d_q L_J|

normalized by sqrt(h) log^2(p*).  The empirical density d_q is estimated from
the full LongA carrier family, and q-classes are taken from shell-3 shifted
prime sites (spf_prev for p±3, where spf_n=2).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
DOCS = ROOT / "docs" / "RH" / "notes"
DEST = DOCS / "claude" / "repair and close process" / "scripts and results"

SITES = NOTES / "prime_mesh_r2q_longa_shell_size_source_audit_sites.csv"

SUMMARY_OUT = NOTES / "prime_mesh_r2q_o2p2_longa_spf_discrepancy_summary.csv"
CLASSES_OUT = NOTES / "prime_mesh_r2q_o2p2_longa_spf_discrepancy_classes.csv"
SCOPES_OUT = NOTES / "prime_mesh_r2q_o2p2_longa_spf_discrepancy_scopes.csv"
INTERVALS_OUT = NOTES / "prime_mesh_r2q_o2p2_longa_spf_discrepancy_intervals.csv"
DOC_OUT = DOCS / "Prime_Mesh_R2Q_O2p2_LongA_SPF_Discrepancy_Audit_v1.md"


def log(msg: str) -> None:
    from datetime import datetime

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def g_weight(q: float) -> float:
    if q <= 1:
        return 0.0
    return 1.0 / (q * (q - 1.0))


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


def summarize(df: pd.DataFrame, scope: str) -> dict[str, object]:
    return {
        "scope": scope,
        "rows": len(df),
        "Q_LAN_max": df["Q_LAN"].max() if len(df) else np.nan,
        "Q_LAN_mean": df["Q_LAN"].mean() if len(df) else np.nan,
        "Q_LAN_median": df["Q_LAN"].median() if len(df) else np.nan,
        "Q_LAN_q95": df["Q_LAN"].quantile(0.95) if len(df) else np.nan,
        "Q_LAN_q99": df["Q_LAN"].quantile(0.99) if len(df) else np.nan,
        "weighted_discrepancy_max": df["weighted_discrepancy"].max() if len(df) else np.nan,
        "carrier_count_median": df["carrier_count"].median() if len(df) else np.nan,
        "h_median": df["h"].median() if len(df) else np.nan,
        "p_star_median": df["p_star"].median() if len(df) else np.nan,
        "pass_Q_LAN_le_0p05_frac": float((df["Q_LAN"] <= 0.05).mean()) if len(df) else np.nan,
        "pass_Q_LAN_le_0p1_frac": float((df["Q_LAN"] <= 0.1).mean()) if len(df) else np.nan,
        "pass_Q_LAN_le_1_frac": float((df["Q_LAN"] <= 1).mean()) if len(df) else np.nan,
        "worst_block_id": df.loc[df["Q_LAN"].idxmax(), "block_id"] if len(df) else np.nan,
        "worst_p_star": df.loc[df["Q_LAN"].idxmax(), "p_star"] if len(df) else np.nan,
    }


def main() -> None:
    log(f"Reading {SITES}")
    sites = pd.read_csv(SITES)
    for c in ["block_id", "source_row", "p_star", "y", "h", "shell", "spf_prev"]:
        if c in sites.columns:
            sites[c] = num(sites[c])

    # O2.2 shell-3 shifted-prime SPF classes.  Each LongA prime contributes two
    # signed sites p-3 and p+3; q is the nontrivial SPF of the adjacent odd number.
    s3 = sites[sites["shell"] == 3].copy()
    s3["q"] = s3["spf_prev"].astype("Int64")
    s3 = s3[s3["q"].notna()].copy()
    s3["q"] = s3["q"].astype(int)
    s3["g"] = s3["q"].map(g_weight)
    s3["g2"] = s3["g"] ** 2

    total_sites = len(s3)
    class_counts = s3.groupby("q").size().rename("N_total").reset_index()
    class_counts["d_emp"] = class_counts["N_total"] / total_sites
    class_counts["g"] = class_counts["q"].map(g_weight)
    class_counts["g2"] = class_counts["g"] ** 2
    class_counts["weighted_mass"] = class_counts["g2"] * class_counts["d_emp"]
    d_map = dict(zip(class_counts["q"], class_counts["d_emp"]))
    g2_map = dict(zip(class_counts["q"], class_counts["g2"]))
    q_values = sorted(d_map)

    group_keys = ["block_id", "source_row", "p_star", "y", "h"]
    interval_counts = s3.groupby(group_keys + ["q"]).size().rename("N_q").reset_index()
    carriers = s3.groupby(group_keys).size().rename("carrier_count").reset_index()

    # Vectorized interval x SPF-class count matrix.
    count_matrix = (
        interval_counts.pivot_table(index=group_keys, columns="q", values="N_q", fill_value=0, aggfunc="sum")
        .reindex(columns=q_values, fill_value=0)
        .sort_index()
    )
    carriers_idx = carriers.set_index(group_keys).loc[count_matrix.index]
    L_vec = carriers_idx["carrier_count"].to_numpy(dtype=float)[:, None]
    d_vec = np.array([d_map[q] for q in q_values], dtype=float)[None, :]
    g2_vec = np.array([g2_map[q] for q in q_values], dtype=float)[None, :]
    observed = count_matrix.to_numpy(dtype=float)
    components = g2_vec * (observed - L_vec * d_vec)
    abs_components = np.abs(components)

    weighted_discrepancy = abs_components.sum(axis=1)
    signed_weighted_discrepancy = components.sum(axis=1)
    q_arr = np.array(q_values)
    small_mask = q_arr <= 13
    small_q_discrepancy = abs_components[:, small_mask].sum(axis=1)
    tail_q_discrepancy = abs_components[:, ~small_mask].sum(axis=1)
    top_idx = abs_components.argmax(axis=1)
    top_component_q = q_arr[top_idx]
    top_component_abs = abs_components[np.arange(abs_components.shape[0]), top_idx]

    intervals = carriers_idx.reset_index().copy()
    intervals["weighted_discrepancy"] = weighted_discrepancy
    intervals["signed_weighted_discrepancy"] = signed_weighted_discrepancy
    intervals["small_q_le_13_discrepancy"] = small_q_discrepancy
    intervals["tail_q_gt_13_discrepancy"] = tail_q_discrepancy
    intervals["top_component_q"] = top_component_q
    intervals["top_component_abs"] = top_component_abs
    p_vec = intervals["p_star"].to_numpy(dtype=float)
    h_vec = intervals["h"].to_numpy(dtype=float)
    intervals["denom_sqrt_h_log2p"] = np.sqrt(np.maximum(h_vec, 1.0)) * (np.log(np.maximum(p_vec, 3.0)) ** 2)
    intervals["Q_LAN"] = intervals["weighted_discrepancy"] / intervals["denom_sqrt_h_log2p"].replace(0, np.nan)
    intervals["h_bin"] = intervals["h"].map(h_bin)
    intervals["scale_bin"] = np.where(
        intervals["p_star"] < 100_000_000,
        "p<100M",
        np.where(intervals["p_star"] < 500_000_000, "100M<=p<500M", "p>=500M"),
    )

    # Class-level discrepancy contribution over intervals.
    total_abs_by_q = abs_components.sum(axis=0)
    max_abs_by_q = abs_components.max(axis=0)
    classes = class_counts.set_index("q").reindex(q_values).reset_index()
    classes["d_emp"] = classes["q"].map(d_map)
    classes["g"] = classes["q"].map(g_weight)
    classes["g2"] = classes["q"].map(g2_map)
    classes["total_abs_weighted_discrepancy"] = total_abs_by_q
    classes["max_interval_abs_component"] = max_abs_by_q
    classes = classes.sort_values("total_abs_weighted_discrepancy", ascending=False)

    scopes = [summarize(intervals, "global")]
    for col, prefix in [("scale_bin", "scale"), ("h_bin", "h")]:
        for key, g in intervals.groupby(col, dropna=False):
            scopes.append(summarize(g, f"{prefix}:{key}"))
    scopes_df = pd.DataFrame(scopes).sort_values("Q_LAN_max", ascending=False)

    summary = {
        "longA_intervals": len(intervals),
        "site_rows_shell3": total_sites,
        "q_classes": len(q_values),
        "Q_LAN_obs": intervals["Q_LAN"].max(),
        "Q_LAN_mean": intervals["Q_LAN"].mean(),
        "Q_LAN_median": intervals["Q_LAN"].median(),
        "Q_LAN_q95": intervals["Q_LAN"].quantile(0.95),
        "Q_LAN_q99": intervals["Q_LAN"].quantile(0.99),
        "pass_Q_LAN_le_0p05_frac": float((intervals["Q_LAN"] <= 0.05).mean()),
        "pass_Q_LAN_le_0p1_frac": float((intervals["Q_LAN"] <= 0.1).mean()),
        "pass_Q_LAN_le_1_frac": float((intervals["Q_LAN"] <= 1).mean()),
        "worst_block_id": intervals.loc[intervals["Q_LAN"].idxmax(), "block_id"],
        "worst_p_star": intervals.loc[intervals["Q_LAN"].idxmax(), "p_star"],
        "worst_h": intervals.loc[intervals["Q_LAN"].idxmax(), "h"],
        "worst_top_component_q": intervals.loc[intervals["Q_LAN"].idxmax(), "top_component_q"],
        "worst_small_q_le_13_discrepancy": intervals.loc[intervals["Q_LAN"].idxmax(), "small_q_le_13_discrepancy"],
        "worst_tail_q_gt_13_discrepancy": intervals.loc[intervals["Q_LAN"].idxmax(), "tail_q_gt_13_discrepancy"],
        "total_abs_discrepancy_top_q": classes.iloc[0]["q"],
        "total_abs_discrepancy_top_q_share": classes.iloc[0]["total_abs_weighted_discrepancy"]
        / classes["total_abs_weighted_discrepancy"].sum(),
    }

    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)
    classes.to_csv(CLASSES_OUT, index=False)
    scopes_df.to_csv(SCOPES_OUT, index=False)
    intervals.to_csv(INTERVALS_OUT, index=False)

    with DOC_OUT.open("w", encoding="utf-8") as f:
        f.write("# Prime Mesh R2Q - O2.2 LongA SPF Discrepancy Audit\n\n")
        f.write("**Document:** `Prime_Mesh_R2Q_O2p2_LongA_SPF_Discrepancy_Audit_v1.md`  \n")
        f.write("**Project:** Prime Mesh Theory - RH Programme  \n")
        f.write("**Date:** 2026-05-07  \n")
        f.write("**Status:** O2.2 LongA SPF discrepancy computation\n\n")
        f.write("## 1. Purpose\n\n")
        f.write(
            "This audit measures the weighted SPF discrepancy on LongA shell-3 "
            "shifted-prime sites.  The baseline density d_q is estimated from "
            "the full LongA carrier family, and each interval is normalized by "
            "\\(\\sqrt h\\log^2p^*\\).\n\n"
        )
        f.write("## 2. Summary\n\n")
        f.write(pd.DataFrame([summary]).T.reset_index().rename(columns={"index": "metric", 0: "value"}).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 3. Class Contributions\n\n")
        f.write(classes.head(30).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 4. Scope Table\n\n")
        f.write(scopes_df.to_markdown(index=False))
        f.write("\n\n")
        f.write("## 5. Interpretation\n\n")
        f.write(
            "The key value is Q_LAN_obs.  Values below 0.05 give a very strong "
            "empirical O2.2 LongA admissibility-neutrality result.\n\n"
        )
        f.write("---\n\n")
        f.write("*Prime Mesh Theory - RH Programme*\n")

    DEST.mkdir(parents=True, exist_ok=True)
    for path in [Path(__file__), SUMMARY_OUT, CLASSES_OUT, SCOPES_OUT, INTERVALS_OUT, DOC_OUT]:
        try:
            (DEST / path.name).write_bytes(path.read_bytes())
        except Exception:
            pass

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {CLASSES_OUT}")
    log(f"Wrote {SCOPES_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k, v in summary.items():
        log(f"{k} = {v}")


if __name__ == "__main__":
    main()
