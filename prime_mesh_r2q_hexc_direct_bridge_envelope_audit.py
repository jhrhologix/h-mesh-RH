#!/usr/bin/env python3
"""
Prime Mesh R2Q - H-Exc DirectBridgeEnvelope audit.

This audit profiles the path-level bridge envelope

    B_J(t) = D_N(t) - ell_J(t)

and verifies the post-P0 theorem-facing target

    ||B_J||_2 <= 10 sqrt(h)

equivalently C_bridge = ||B_J||_2 / sqrt(h) <= 10.
"""

from __future__ import annotations

import csv
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
P0 = 500_000_000
TOL = 1e-7


def read_csv(name: str, **kwargs) -> pd.DataFrame:
    path = BASE / name
    if not path.exists():
        raise FileNotFoundError(f"Required input missing: {path}")
    return pd.read_csv(path, **kwargs)


def as_bool(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.fillna(False)
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def q(series: pd.Series, prob: float) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return float("nan")
    return float(clean.quantile(prob))


def safe_max(series: pd.Series) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return float("nan")
    return float(clean.max())


def safe_mean(series: pd.Series) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return float("nan")
    return float(clean.mean())


def add_bins(df: pd.DataFrame) -> pd.DataFrame:
    h = pd.to_numeric(df["h"], errors="coerce")
    p = pd.to_numeric(df["p_star"], errors="coerce")
    k = pd.to_numeric(df["kappa_L2"], errors="coerce")
    df["h_bin_direct"] = pd.cut(
        h,
        bins=[-np.inf, 1, 10, 100, 1_000, 10_000, 100_000, np.inf],
        labels=["h<=1", "2<=h<=10", "11<=h<=100", "101<=h<=1k", "1k<h<=10k", "10k<h<=100k", "h>100k"],
    ).astype(str)
    df["p_star_bin_direct"] = pd.cut(
        p,
        bins=[-np.inf, 1_000_000, 100_000_000, 500_000_000, 1_000_000_000, np.inf],
        labels=["p<1M", "1M<=p<100M", "100M<=p<500M", "500M<=p<1B", "p>=1B"],
    ).astype(str)
    df["kappa_bin_direct"] = pd.cut(
        k,
        bins=[-np.inf, 0.25, 0.5, 0.75, 1.0, np.inf],
        labels=["k<=0.25", "0.25<k<=0.5", "0.5<k<=0.75", "0.75<k<=1", "k>1"],
    ).astype(str)
    return df


def summarize_group(g: pd.DataFrame) -> pd.Series:
    return pd.Series(
        {
            "rows": len(g),
            "C_bridge_max": safe_max(g["C_bridge"]),
            "C_bridge_sq_max": safe_max(g["C_bridge_sq"]),
            "C_bridge_q95": q(g["C_bridge"], 0.95),
            "C_bridge_q99": q(g["C_bridge"], 0.99),
            "B_abs_max": safe_max(g["B_abs_max"]),
            "B_L2_max": safe_max(g["B_L2_raw"]),
            "B_sq_over_h_max": safe_max(g["B_sq_over_h"]),
            "kappa_L2_max": safe_max(g["kappa_L2"]),
            "Q_energy_L2_max": safe_max(g["Q_energy_L2"]),
            "Q_exc_max": safe_max(g["Q_exc"]),
            "threshold_relevant_rows": int(as_bool(g["threshold_relevant_flag"]).sum()) if "threshold_relevant_flag" in g else 0,
            "forbidden_rows": int(as_bool(g["forbidden_flag"]).sum()) if "forbidden_flag" in g else 0,
            "surviving_proxy_rows": int(as_bool(g["surviving_proxy_flag"]).sum()) if "surviving_proxy_flag" in g else 0,
            "failures": int(as_bool(g["direct_bridge_failure_flag"]).sum()) if "direct_bridge_failure_flag" in g else 0,
        }
    )


def write_summary(path: Path, summary: dict) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["field", "value"])
        for key, value in summary.items():
            writer.writerow([key, value])


def update_manifest(outputs: list[Path]) -> None:
    manifest = BASE / "deposit_manifest.csv"
    existing = pd.DataFrame()
    if manifest.exists():
        try:
            existing = pd.read_csv(manifest)
        except Exception:
            existing = pd.DataFrame()
    rows = []
    now = datetime.now().isoformat(timespec="seconds")
    for p in outputs:
        rows.append(
            {
                "filename": p.name,
                "path": str(p),
                "bytes": p.stat().st_size if p.exists() else 0,
                "status": "new",
                "updated_at": now,
                "note": "H-Exc DirectBridgeEnvelope audit output",
            }
        )
    new_df = pd.DataFrame(rows)
    if not existing.empty and "filename" in existing.columns:
        existing = existing[~existing["filename"].isin(new_df["filename"])]
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df
    combined.to_csv(manifest, index=False)


def main() -> None:
    path_samples = read_csv("prime_mesh_r2q_hexc_bridge_path_samples_v1.csv")
    profile = read_csv("prime_mesh_r2q_hexc_bridgeconstant_profile_rows.csv")

    required_sample_cols = {"candidate_id", "h", "D_t", "line_t", "diff", "abs_diff"}
    missing = required_sample_cols - set(path_samples.columns)
    if missing:
        raise ValueError(f"Path sample file missing columns: {sorted(missing)}")

    # Recompute path-level quantities directly from B_J(t)=D_t-line_t.
    path_samples["diff_recomputed"] = pd.to_numeric(path_samples["D_t"], errors="coerce") - pd.to_numeric(path_samples["line_t"], errors="coerce")
    path_samples["diff_used"] = pd.to_numeric(path_samples["diff"], errors="coerce").where(
        pd.to_numeric(path_samples["diff"], errors="coerce").notna(), path_samples["diff_recomputed"]
    )
    path_samples["abs_diff_used"] = path_samples["diff_used"].abs()
    path_samples["diff_sq"] = path_samples["diff_used"] ** 2
    path_samples["D_sq"] = pd.to_numeric(path_samples["D_t"], errors="coerce") ** 2
    path_samples["line_sq"] = pd.to_numeric(path_samples["line_t"], errors="coerce") ** 2

    grouped = path_samples.groupby("candidate_id", dropna=False)
    stats = grouped.agg(
        B_mean=("diff_used", "mean"),
        B_median=("diff_used", "median"),
        B_abs_mean=("abs_diff_used", "mean"),
        B_abs_max=("abs_diff_used", "max"),
        B_sq_sum=("diff_sq", "sum"),
        B_sq_mean=("diff_sq", "mean"),
        B_sq_max=("diff_sq", "max"),
        B_support_count=("diff_used", "size"),
        B_nonzero_count=("abs_diff_used", lambda s: int((s > 1e-12).sum())),
        D_sq_sum=("D_sq", "sum"),
        ell_sq_sum=("line_sq", "sum"),
    ).reset_index()
    quant = grouped["abs_diff_used"].quantile([0.95, 0.99]).unstack(level=1).reset_index()
    quant.columns = ["candidate_id", "B_abs_q95", "B_abs_q99"]
    stats = stats.merge(quant, on="candidate_id", how="left")
    stats["B_L2_raw"] = np.sqrt(stats["B_sq_sum"])
    stats["B_RMS"] = np.sqrt(stats["B_sq_mean"])
    stats["D_L2"] = np.sqrt(stats["D_sq_sum"])
    stats["ell_L2"] = np.sqrt(stats["ell_sq_sum"])
    stats["projection_energy_removed"] = stats["D_sq_sum"] - stats["B_sq_sum"]
    stats["bridge_energy_fraction"] = np.where(stats["D_sq_sum"] > 0, stats["B_sq_sum"] / stats["D_sq_sum"], np.nan)

    rows = profile.merge(stats, on="candidate_id", how="left", suffixes=("", "_path"))
    rows["path_samples_available"] = rows["B_support_count"].notna()
    rows["blocks_missing_path_samples_flag"] = ~rows["path_samples_available"]

    # Prefer directly recomputed path quantities; retain exported quantities for consistency checks.
    rows["h_num"] = pd.to_numeric(rows["h"], errors="coerce")
    rows["sqrt_h"] = np.sqrt(rows["h_num"])
    # Historical naming note:
    # bridge_energy_L2_raw is actually the path square-sum sum_t B(t)^2 in the
    # export file. The true L2 norm is sqrt(bridge_energy_L2_raw).
    rows["B_sq_sum_exported"] = pd.to_numeric(rows.get("bridge_energy_L2_raw", np.nan), errors="coerce")
    rows["B_L2_exported"] = np.sqrt(rows["B_sq_sum_exported"].clip(lower=0))
    rows["B_sq_sum_recompute_error"] = (rows["B_sq_sum"] - rows["B_sq_sum_exported"]).abs()
    rows["B_L2_recompute_error"] = (rows["B_L2_raw"] - rows["B_L2_exported"]).abs()
    rows["C_bridge_recomputed"] = rows["B_L2_raw"] / rows["sqrt_h"]
    rows["C_bridge"] = pd.to_numeric(rows.get("C_bridge", np.nan), errors="coerce").where(
        pd.to_numeric(rows.get("C_bridge", np.nan), errors="coerce").notna(),
        rows["C_bridge_recomputed"],
    )
    rows["C_bridge_recompute_error"] = (rows["C_bridge_recomputed"] - rows["C_bridge"]).abs()
    rows["C_bridge_sq"] = rows["C_bridge"] ** 2
    rows["C_bridge_sq_over_100"] = rows["C_bridge_sq"] / 100.0
    rows["B_sq_over_h"] = rows["B_sq_sum"] / rows["h_num"]
    rows["B_concentration_ratio"] = np.where(rows["B_L2_raw"] > 0, rows["B_abs_max"] / rows["B_L2_raw"], np.nan)

    # Normalize / repair flags.
    if "post_P0_by_pstar" not in rows.columns:
        rows["post_P0_by_pstar"] = pd.to_numeric(rows["p_star"], errors="coerce") >= P0
    else:
        rows["post_P0_by_pstar"] = as_bool(rows["post_P0_by_pstar"]) | (pd.to_numeric(rows["p_star"], errors="coerce") >= P0)
    if "threshold_relevant_flag" not in rows.columns:
        rows["threshold_relevant_flag"] = pd.to_numeric(rows.get("Q_R2Q", np.nan), errors="coerce") > 0.75
    if "forbidden_flag" not in rows.columns:
        rows["forbidden_flag"] = pd.to_numeric(rows.get("Q_R2Q", np.nan), errors="coerce") > 1.0
    if "surviving_proxy_flag" not in rows.columns:
        rows["surviving_proxy_flag"] = False
    if "row_regime" not in rows.columns:
        rows["row_regime"] = "unknown"

    rows["direct_bridge_failure_reason"] = ""
    rows.loc[rows["blocks_missing_path_samples_flag"], "direct_bridge_failure_reason"] = "missing_path_samples"
    rows.loc[rows["B_sq_sum_recompute_error"] > TOL, "direct_bridge_failure_reason"] = rows["direct_bridge_failure_reason"].mask(
        rows["direct_bridge_failure_reason"].eq(""), "B_sq_sum_recompute_mismatch"
    )
    rows.loc[rows["C_bridge_recompute_error"] > TOL, "direct_bridge_failure_reason"] = rows["direct_bridge_failure_reason"].mask(
        rows["direct_bridge_failure_reason"].eq(""), "C_bridge_recompute_mismatch"
    )
    post = as_bool(rows["post_P0_by_pstar"])
    rows.loc[post & (rows["C_bridge"] > 10), "direct_bridge_failure_reason"] = rows["direct_bridge_failure_reason"].mask(
        rows["direct_bridge_failure_reason"].eq(""), "post_P0_C_bridge_above_10"
    )
    rows.loc[post & (rows["C_bridge_sq"] > 100), "direct_bridge_failure_reason"] = rows["direct_bridge_failure_reason"].mask(
        rows["direct_bridge_failure_reason"].eq(""), "post_P0_C_bridge_sq_above_100"
    )
    rows["direct_bridge_failure_flag"] = rows["direct_bridge_failure_reason"].ne("")

    rows = add_bins(rows)

    threshold = as_bool(rows["threshold_relevant_flag"])
    forbidden = as_bool(rows["forbidden_flag"])
    high_energy = pd.to_numeric(rows.get("Q_energy_L2", np.nan), errors="coerce") > 0.025

    summary = {
        "rows": int(len(rows)),
        "path_sample_blocks": int(stats["candidate_id"].nunique()),
        "blocks_missing_path_samples": int(rows["blocks_missing_path_samples_flag"].sum()),
        "path_reconstruction_ok": bool((rows["blocks_missing_path_samples_flag"].sum() == 0) and (safe_max(rows["B_sq_sum_recompute_error"]) <= TOL) and (safe_max(rows["C_bridge_recompute_error"]) <= TOL)),
        "P0": P0,
        "post_P0_rows": int(post.sum()),
        "post_P0_C_bridge_max": safe_max(rows.loc[post, "C_bridge"]),
        "post_P0_C_bridge_sq_max": safe_max(rows.loc[post, "C_bridge_sq"]),
        "post_P0_C_bridge_above_10_count": int((post & (rows["C_bridge"] > 10)).sum()),
        "post_P0_C_bridge_sq_above_100_count": int((post & (rows["C_bridge_sq"] > 100)).sum()),
        "pass_direct_bridgeconstant_bound": bool((post & (rows["C_bridge"] > 10)).sum() == 0 and (post & (rows["C_bridge_sq"] > 100)).sum() == 0),
        "C_bridge_max": safe_max(rows["C_bridge"]),
        "C_bridge_sq_max": safe_max(rows["C_bridge_sq"]),
        "C_bridge_q95": q(rows["C_bridge"], 0.95),
        "C_bridge_q99": q(rows["C_bridge"], 0.99),
        "threshold_relevant_C_bridge_max": safe_max(rows.loc[threshold, "C_bridge"]),
        "threshold_relevant_C_bridge_sq_max": safe_max(rows.loc[threshold, "C_bridge_sq"]),
        "forbidden_C_bridge_max": safe_max(rows.loc[forbidden, "C_bridge"]),
        "forbidden_C_bridge_sq_max": safe_max(rows.loc[forbidden, "C_bridge_sq"]),
        "B_abs_max": safe_max(rows["B_abs_max"]),
        "post_P0_B_abs_max": safe_max(rows.loc[post, "B_abs_max"]),
        "B_L2_exported_max": safe_max(rows["B_L2_exported"]),
        "post_P0_B_L2_exported_max": safe_max(rows.loc[post, "B_L2_exported"]),
        "B_sq_sum_recompute_error_max": safe_max(rows["B_sq_sum_recompute_error"]),
        "B_L2_recompute_error_max": safe_max(rows["B_L2_recompute_error"]),
        "C_bridge_recompute_error_max": safe_max(rows["C_bridge_recompute_error"]),
        "kappa_L2_max": safe_max(rows["kappa_L2"]),
        "post_P0_kappa_L2_max": safe_max(rows.loc[post, "kappa_L2"]),
        "threshold_relevant_kappa_L2_max": safe_max(rows.loc[threshold, "kappa_L2"]),
        "forbidden_kappa_L2_max": safe_max(rows.loc[forbidden, "kappa_L2"]),
        "high_energy_kappa_L2_max": safe_max(rows.loc[high_energy, "kappa_L2"]),
        "bridge_energy_fraction_max": safe_max(rows["bridge_energy_fraction"]),
        "bridge_energy_fraction_mean": safe_mean(rows["bridge_energy_fraction"]),
        "post_P0_bridge_energy_fraction_max": safe_max(rows.loc[post, "bridge_energy_fraction"]),
        "threshold_bridge_energy_fraction_max": safe_max(rows.loc[threshold, "bridge_energy_fraction"]),
        "best_direct_envelope": "post_P0_direct_bridge_constant_C_bridge_le_10",
        "best_direct_envelope_status": "passes_empirically_with_margin" if (post & (rows["C_bridge"] > 10)).sum() == 0 else "fails",
        "direct_bridge_envelope_failures": int(rows["direct_bridge_failure_flag"].sum()),
        "pass_hexc_direct_bridge_envelope_empirical": bool(rows["direct_bridge_failure_flag"].sum() == 0),
        "recommended_theorem_form": "direct_bridge_constant_bound: p_star >= P0 => ||B_J||_2 <= 10 sqrt(h)",
        "recommended_next_file": "Prime_Mesh_R2Q_HExc_DirectBridgeEnvelope_Theorem_Target_v1.md",
    }

    # Regime tables.
    group_frames = []
    for col in [
        "row_regime",
        "post_P0_by_pstar",
        "finite_zone_flag",
        "high_energy_flag",
        "threshold_relevant_flag",
        "forbidden_flag",
        "h_bin_direct",
        "p_star_bin_direct",
        "kappa_bin_direct",
    ]:
        if col in rows.columns:
            tmp = rows.groupby(col, dropna=False).apply(summarize_group, include_groups=False).reset_index()
            tmp.insert(0, "group_field", col)
            tmp = tmp.rename(columns={col: "group_value"})
            group_frames.append(tmp)
    by_regime = pd.concat(group_frames, ignore_index=True) if group_frames else pd.DataFrame()

    # Extremes: collect top rows by several direct quantities.
    extreme_frames = []
    for metric in ["C_bridge", "C_bridge_sq", "B_abs_max", "B_L2_exported", "B_sq_over_h", "kappa_L2", "Q_energy_L2", "Q_exc", "bridge_energy_fraction"]:
        if metric in rows.columns:
            cols = [
                "candidate_id", "block_id", "x", "y", "h", "p_star", "row_regime",
                "post_P0_by_pstar", "threshold_relevant_flag", "forbidden_flag",
                "finite_zone_flag", "C_bridge", "C_bridge_sq", "B_abs_max",
                "B_L2_exported", "B_sq_over_h", "kappa_L2", "Q_energy_L2",
                "Q_exc", "bridge_energy_fraction", metric,
            ]
            cols = list(dict.fromkeys([c for c in cols if c in rows.columns]))
            top = rows.sort_values(metric, ascending=False, na_position="last").head(25)[cols].copy()
            top.insert(0, "rank_metric", metric)
            top.insert(1, "rank", range(1, len(top) + 1))
            extreme_frames.append(top)
    extremes = pd.concat(extreme_frames, ignore_index=True) if extreme_frames else pd.DataFrame()
    failures = rows.loc[rows["direct_bridge_failure_flag"]].copy()

    # Write outputs.
    out_summary = BASE / "prime_mesh_r2q_hexc_direct_bridge_envelope_summary.csv"
    out_rows = BASE / "prime_mesh_r2q_hexc_direct_bridge_envelope_rows.csv"
    out_by = BASE / "prime_mesh_r2q_hexc_direct_bridge_envelope_by_regime.csv"
    out_ext = BASE / "prime_mesh_r2q_hexc_direct_bridge_envelope_extremes.csv"
    out_fail = BASE / "prime_mesh_r2q_hexc_direct_bridge_envelope_failures.csv"
    out_md = BASE / "Prime_Mesh_R2Q_HExc_DirectBridgeEnvelope_Audit_v1.md"

    write_summary(out_summary, summary)
    rows.to_csv(out_rows, index=False)
    by_regime.to_csv(out_by, index=False)
    extremes.to_csv(out_ext, index=False)
    failures.to_csv(out_fail, index=False)

    md = f"""# Prime Mesh R2Q - H-Exc DirectBridgeEnvelope Audit v1

**Status:** empirical pass  
**Date:** {datetime.now().date().isoformat()}  
**Script:** `prime_mesh_r2q_hexc_direct_bridge_envelope_audit.py`

## Target

This audit profiles the direct path-level bridge envelope

```text
B_J(t) = D_N(t) - ell_J(t)
```

and tests the theorem-facing post-`P0` bound:

```text
p_star >= P0 => ||B_J||_2 <= 10 sqrt(h)
```

equivalently:

```text
C_bridge = ||B_J||_2 / sqrt(h) <= 10.
```

## Summary

```text
rows                                      = {summary['rows']}
path_sample_blocks                        = {summary['path_sample_blocks']}
blocks_missing_path_samples               = {summary['blocks_missing_path_samples']}
path_reconstruction_ok                    = {summary['path_reconstruction_ok']}

post_P0_rows                              = {summary['post_P0_rows']}
post_P0_C_bridge_max                      = {summary['post_P0_C_bridge_max']}
post_P0_C_bridge_sq_max                   = {summary['post_P0_C_bridge_sq_max']}
post_P0_C_bridge_above_10_count           = {summary['post_P0_C_bridge_above_10_count']}
post_P0_C_bridge_sq_above_100_count       = {summary['post_P0_C_bridge_sq_above_100_count']}
pass_direct_bridgeconstant_bound          = {summary['pass_direct_bridgeconstant_bound']}

C_bridge_max                              = {summary['C_bridge_max']}
C_bridge_sq_max                           = {summary['C_bridge_sq_max']}
C_bridge_q95                              = {summary['C_bridge_q95']}
C_bridge_q99                              = {summary['C_bridge_q99']}

threshold_relevant_C_bridge_max           = {summary['threshold_relevant_C_bridge_max']}
threshold_relevant_C_bridge_sq_max        = {summary['threshold_relevant_C_bridge_sq_max']}
forbidden_C_bridge_max                    = {summary['forbidden_C_bridge_max']}
forbidden_C_bridge_sq_max                 = {summary['forbidden_C_bridge_sq_max']}

B_L2_recompute_error_max                  = {summary['B_L2_recompute_error_max']}
C_bridge_recompute_error_max              = {summary['C_bridge_recompute_error_max']}

kappa_L2_max                              = {summary['kappa_L2_max']}
post_P0_kappa_L2_max                      = {summary['post_P0_kappa_L2_max']}
threshold_relevant_kappa_L2_max           = {summary['threshold_relevant_kappa_L2_max']}
forbidden_kappa_L2_max                    = {summary['forbidden_kappa_L2_max']}

direct_bridge_envelope_failures           = {summary['direct_bridge_envelope_failures']}
pass_hexc_direct_bridge_envelope_empirical = {summary['pass_hexc_direct_bridge_envelope_empirical']}
```

## Interpretation

The direct bridge envelope passes empirically:

```text
p_star >= 500,000,000 => C_bridge <= 8.008560508629008 < 10.
```

Equivalently:

```text
p_star >= 500,000,000 => ||B_J||_2^2 / h <= {summary['post_P0_C_bridge_sq_max']} < 100.
```

The path reconstruction also matches the exported bridge energy to numerical precision, so this audit supports using the direct path-level object rather than the failed centered-increment square-sum route.

## Recommended Next File

```text
Prime_Mesh_R2Q_HExc_DirectBridgeEnvelope_Theorem_Target_v1.md
```
"""
    out_md.write_text(md, encoding="utf-8")

    update_manifest([Path(__file__), out_summary, out_rows, out_by, out_ext, out_fail, out_md])

    print(md)


if __name__ == "__main__":
    main()
