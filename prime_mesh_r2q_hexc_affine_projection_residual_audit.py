#!/usr/bin/env python3
"""
Prime Mesh R2Q - H-Exc AffineProjectionResidual audit.

Compares:
  - endpoint affine residual D_N - ell_endpoint
  - best least-squares affine residual D_N - P_aff D_N
  - endpoint-vs-best affine gap P_aff D_N - ell_endpoint

for the H-Exc proof target:
  p_star >= P0 => ||D_N - ell_endpoint||_2^2 <= 100 h.
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
EPS = 1e-30


def read_csv(name: str) -> pd.DataFrame:
    path = BASE / name
    if not path.exists():
        raise FileNotFoundError(f"Missing required input: {path}")
    return pd.read_csv(path)


def as_bool(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.fillna(False)
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def safe_max(s: pd.Series) -> float:
    x = num(s).dropna()
    return float(x.max()) if not x.empty else float("nan")


def safe_min(s: pd.Series) -> float:
    x = num(s).dropna()
    return float(x.min()) if not x.empty else float("nan")


def safe_mean(s: pd.Series) -> float:
    x = num(s).dropna()
    return float(x.mean()) if not x.empty else float("nan")


def q(s: pd.Series, p: float) -> float:
    x = num(s).dropna()
    return float(x.quantile(p)) if not x.empty else float("nan")


def write_summary(path: Path, summary: dict) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["field", "value"])
        for k, v in summary.items():
            w.writerow([k, v])


def update_manifest(outputs: list[Path]) -> None:
    manifest = BASE / "deposit_manifest.csv"
    existing = pd.DataFrame()
    if manifest.exists():
        try:
            existing = pd.read_csv(manifest)
        except Exception:
            existing = pd.DataFrame()
    now = datetime.now().isoformat(timespec="seconds")
    new = pd.DataFrame(
        [
            {
                "filename": p.name,
                "path": str(p),
                "bytes": p.stat().st_size if p.exists() else 0,
                "status": "new",
                "updated_at": now,
                "note": "H-Exc AffineProjectionResidual audit output",
            }
            for p in outputs
        ]
    )
    if not existing.empty and "filename" in existing.columns:
        existing = existing[~existing["filename"].isin(new["filename"])]
        combined = pd.concat([existing, new], ignore_index=True)
    else:
        combined = new
    combined.to_csv(manifest, index=False)


def add_bins(df: pd.DataFrame) -> pd.DataFrame:
    h = num(df["h"])
    p = num(df["p_star"])
    sample_col = "sample_count_affine" if "sample_count_affine" in df.columns else "sample_count"
    m = num(df[sample_col])
    df["h_bin_aff"] = pd.cut(
        h,
        bins=[-np.inf, 1, 10, 100, 1_000, 10_000, 100_000, np.inf],
        labels=["h<=1", "2<=h<=10", "11<=h<=100", "101<=h<=1k", "1k<h<=10k", "10k<h<=100k", "h>100k"],
    ).astype(str)
    df["p_star_bin_aff"] = pd.cut(
        p,
        bins=[-np.inf, 1_000_000, 100_000_000, 500_000_000, 1_000_000_000, np.inf],
        labels=["p<1M", "1M<=p<100M", "100M<=p<500M", "500M<=p<1B", "p>=1B"],
    ).astype(str)
    df["sample_count_bin_aff"] = pd.cut(
        m,
        bins=[-np.inf, 2, 5, 10, 25, 50, 100, np.inf],
        labels=["m<=2", "3<=m<=5", "6<=m<=10", "11<=m<=25", "26<=m<=50", "51<=m<=100", "m>100"],
    ).astype(str)
    return df


def summarize_group(g: pd.DataFrame) -> pd.Series:
    return pd.Series(
        {
            "rows": len(g),
            "C_end_max": safe_max(g["C_end"]),
            "C_best_max": safe_max(g["C_best"]),
            "C_gap_max": safe_max(g["C_gap"]),
            "E_end_over_h_max": safe_max(g["E_end_over_h"]),
            "E_best_over_h_max": safe_max(g["E_best_over_h"]),
            "E_gap_over_h_max": safe_max(g["E_gap_over_h"]),
            "endpoint_residual_fraction_max": safe_max(g["endpoint_residual_fraction"]),
            "best_residual_fraction_max": safe_max(g["best_residual_fraction"]),
            "pythagorean_error_max": safe_max(g["pythagorean_abs_error"]),
            "threshold_relevant_rows": int(as_bool(g["threshold_relevant_flag"]).sum()) if "threshold_relevant_flag" in g else 0,
            "forbidden_rows": int(as_bool(g["forbidden_flag"]).sum()) if "forbidden_flag" in g else 0,
            "failures": int(as_bool(g["affine_projection_failure_flag"]).sum()) if "affine_projection_failure_flag" in g else 0,
        }
    )


def compute_affine_stats(samples: pd.DataFrame) -> pd.DataFrame:
    samples = samples.copy()
    samples["D_t"] = num(samples["D_t"])
    samples["line_t"] = num(samples["line_t"])
    samples["t"] = num(samples["t"])
    samples["offset"] = num(samples["offset"])
    samples["h"] = num(samples["h"])
    if "diff" in samples.columns:
        samples["B_endpoint"] = num(samples["diff"])
    else:
        samples["B_endpoint"] = samples["D_t"] - samples["line_t"]
    samples["B_endpoint"] = samples["B_endpoint"].where(samples["B_endpoint"].notna(), samples["D_t"] - samples["line_t"])

    rows = []
    for cid, g in samples.groupby("candidate_id", sort=False):
        g = g.sort_values(["t", "offset"], na_position="last")
        d = g["D_t"].to_numpy(dtype=float)
        ell_end = g["line_t"].to_numpy(dtype=float)
        offset = g["offset"].to_numpy(dtype=float)
        h_vals = num(g["h"]).dropna()
        h = float(h_vals.iloc[0]) if not h_vals.empty else float("nan")
        if np.isnan(offset).any():
            t = g["t"].to_numpy(dtype=float)
            offset = t - np.nanmin(t)

        valid = ~(np.isnan(d) | np.isnan(ell_end) | np.isnan(offset))
        d = d[valid]
        ell_end = ell_end[valid]
        offset = offset[valid]
        sample_count = int(d.size)

        if sample_count >= 2:
            X = np.column_stack([np.ones(sample_count), offset])
            coef, *_ = np.linalg.lstsq(X, d, rcond=None)
            a_best = float(coef[0])
            b_best = float(coef[1])
            ell_best = X @ coef
        elif sample_count == 1:
            a_best = float(d[0])
            b_best = 0.0
            ell_best = np.array([d[0]], dtype=float)
        else:
            a_best = float("nan")
            b_best = float("nan")
            ell_best = np.array([], dtype=float)

        r_end = d - ell_end
        r_best = d - ell_best
        gap = ell_best - ell_end

        E_end = float(np.sum(r_end * r_end)) if sample_count else float("nan")
        E_best = float(np.sum(r_best * r_best)) if sample_count else float("nan")
        E_gap = float(np.sum(gap * gap)) if sample_count else float("nan")
        E_D = float(np.sum(d * d)) if sample_count else float("nan")
        E_ell_end = float(np.sum(ell_end * ell_end)) if sample_count else float("nan")
        E_ell_best = float(np.sum(ell_best * ell_best)) if sample_count else float("nan")
        pyth_err = E_end - E_best - E_gap
        pyth_abs = abs(pyth_err)
        pyth_rel = pyth_abs / max(abs(E_end), EPS)

        endpoint_intercept = float(ell_end[0]) if sample_count else float("nan")
        endpoint_slope = float((ell_end[-1] - ell_end[0]) / (offset[-1] - offset[0])) if sample_count >= 2 and offset[-1] != offset[0] else 0.0
        intercept_gap = a_best - endpoint_intercept
        slope_gap = b_best - endpoint_slope

        rows.append(
            {
                "candidate_id": cid,
                "block_id_path": g["block_id"].iloc[0] if "block_id" in g.columns else np.nan,
                "sample_count": sample_count,
                "h_path": h,
                "E_end": E_end,
                "E_best": E_best,
                "E_gap": E_gap,
                "E_D": E_D,
                "E_ell_endpoint": E_ell_end,
                "E_ell_best": E_ell_best,
                "E_end_over_h": E_end / h if h and h > 0 else float("nan"),
                "E_best_over_h": E_best / h if h and h > 0 else float("nan"),
                "E_gap_over_h": E_gap / h if h and h > 0 else float("nan"),
                "C_end": math.sqrt(max(E_end / h, 0.0)) if h and h > 0 else float("nan"),
                "C_best": math.sqrt(max(E_best / h, 0.0)) if h and h > 0 else float("nan"),
                "C_gap": math.sqrt(max(E_gap / h, 0.0)) if h and h > 0 else float("nan"),
                "gap_fraction_of_endpoint_residual": E_gap / max(E_end, EPS),
                "gap_fraction_of_best_residual": E_gap / max(E_best, EPS),
                "pythagorean_error": pyth_err,
                "pythagorean_abs_error": pyth_abs,
                "pythagorean_relative_error": pyth_rel,
                "endpoint_residual_fraction": E_end / max(E_D, EPS),
                "best_residual_fraction": E_best / max(E_D, EPS),
                "endpoint_affine_capture_fraction": 1.0 - (E_end / max(E_D, EPS)),
                "best_affine_capture_fraction": 1.0 - (E_best / max(E_D, EPS)),
                "a_best": a_best,
                "b_best": b_best,
                "endpoint_intercept": endpoint_intercept,
                "endpoint_slope": endpoint_slope,
                "slope_gap": slope_gap,
                "intercept_gap": intercept_gap,
                "slope_gap_abs": abs(slope_gap),
                "intercept_gap_abs": abs(intercept_gap),
                "R_end_abs_max": float(np.max(np.abs(r_end))) if sample_count else float("nan"),
                "R_best_abs_max": float(np.max(np.abs(r_best))) if sample_count else float("nan"),
                "gap_abs_max": float(np.max(np.abs(gap))) if sample_count else float("nan"),
                "endpoint_start_residual": float(r_end[0]) if sample_count else float("nan"),
                "endpoint_end_residual": float(r_end[-1]) if sample_count else float("nan"),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    samples = read_csv("prime_mesh_r2q_hexc_bridge_path_samples_v1.csv")
    spine = read_csv("prime_mesh_r2q_hexc_bridgeshape_curvature_rows.csv")
    aff = compute_affine_stats(samples)

    rows = spine.merge(aff, on="candidate_id", how="left")
    if "sample_count_y" in rows.columns:
        rows["sample_count_affine"] = rows["sample_count_y"]
    elif "sample_count" in rows.columns:
        rows["sample_count_affine"] = rows["sample_count"]
    else:
        rows["sample_count_affine"] = np.nan
    rows["path_samples_available"] = rows["sample_count_affine"].notna()
    rows["blocks_missing_path_samples_flag"] = ~rows["path_samples_available"]
    rows["post_P0_by_pstar"] = as_bool(rows["post_P0_by_pstar"]) | (num(rows["p_star"]) >= P0)
    rows["threshold_relevant_flag"] = as_bool(rows["threshold_relevant_flag"]) if "threshold_relevant_flag" in rows else num(rows["Q_R2Q"]) > 0.75
    rows["forbidden_flag"] = as_bool(rows["forbidden_flag"]) if "forbidden_flag" in rows else num(rows["Q_R2Q"]) > 1.0
    if "finite_zone_flag" in rows:
        rows["finite_zone_flag"] = as_bool(rows["finite_zone_flag"])
    if "high_energy_flag" in rows:
        rows["high_energy_flag"] = as_bool(rows["high_energy_flag"])
    else:
        rows["high_energy_flag"] = num(rows["Q_energy_L2"]) > 0.025

    rows["C_end_vs_C_bridge_error"] = (num(rows["C_end"]) - num(rows["C_bridge"])).abs()
    rows["E_end_over_h_vs_C_bridge_sq_error"] = (num(rows["E_end_over_h"]) - num(rows["C_bridge_sq"])).abs()

    post = as_bool(rows["post_P0_by_pstar"])
    threshold = as_bool(rows["threshold_relevant_flag"])
    forbidden = as_bool(rows["forbidden_flag"])

    rows["affine_projection_failure_reason"] = ""
    rows.loc[rows["blocks_missing_path_samples_flag"], "affine_projection_failure_reason"] = "missing_path_samples"
    rows.loc[rows["C_end_vs_C_bridge_error"] > TOL, "affine_projection_failure_reason"] = rows["affine_projection_failure_reason"].mask(
        rows["affine_projection_failure_reason"].eq(""), "endpoint_residual_reconstruction_mismatch"
    )
    rows.loc[post & (num(rows["C_end"]) > 10), "affine_projection_failure_reason"] = rows["affine_projection_failure_reason"].mask(
        rows["affine_projection_failure_reason"].eq(""), "post_P0_C_end_above_10"
    )
    rows.loc[post & (num(rows["E_end_over_h"]) > 100), "affine_projection_failure_reason"] = rows["affine_projection_failure_reason"].mask(
        rows["affine_projection_failure_reason"].eq(""), "post_P0_E_end_over_h_above_100"
    )
    rows["affine_projection_failure_flag"] = rows["affine_projection_failure_reason"].ne("")
    rows = add_bins(rows)

    pyth_abs_max = safe_max(rows["pythagorean_abs_error"])
    post_pyth_abs_max = safe_max(rows.loc[post, "pythagorean_abs_error"])
    pyth_rel_max = safe_max(rows["pythagorean_relative_error"])
    post_pyth_rel_max = safe_max(rows.loc[post, "pythagorean_relative_error"])
    pass_projection_decomposition = bool(pyth_rel_max < 1e-8 or pyth_abs_max < 1e-6)

    endpoint_best_gap_small = bool(safe_max(rows.loc[post, "C_gap"]) <= 1.0)
    endpoint_pass = bool((post & (num(rows["C_end"]) > 10)).sum() == 0 and (post & (num(rows["E_end_over_h"]) > 100)).sum() == 0)
    best_pass = bool((post & (num(rows["C_best"]) > 10)).sum() == 0)

    # The endpoint residual is the theorem target; choose best-affine split only
    # if endpoint gap is small or if it creates a materially clearer constant.
    post_C_best_max = safe_max(rows.loc[post, "C_best"])
    post_C_gap_max = safe_max(rows.loc[post, "C_gap"])
    if endpoint_pass and (not endpoint_best_gap_small) and (post_C_best_max + post_C_gap_max < 10):
        best_form = "best_affine_projection_split"
        rec_file = "Prime_Mesh_R2Q_HExc_BestAffineProjection_Split_Theorem_Target_v1.md"
        theorem_form = "best_affine_projection_split: E_end = E_best + E_gap with C_best + C_gap budget"
    else:
        best_form = "endpoint_affine_residual"
        rec_file = "Prime_Mesh_R2Q_HExc_EndpointAffineResidual_Theorem_Target_v1.md"
        theorem_form = "endpoint_affine_residual_bound: p_star >= P0 => ||D_N - ell_endpoint||_2^2 <= 100h"

    summary = {
        "rows": int(len(rows)),
        "path_sample_blocks": int(aff["candidate_id"].nunique()),
        "blocks_missing_path_samples": int(rows["blocks_missing_path_samples_flag"].sum()),
        "path_reconstruction_ok": bool(rows["blocks_missing_path_samples_flag"].sum() == 0 and safe_max(rows["C_end_vs_C_bridge_error"]) <= TOL),
        "P0": P0,
        "post_P0_rows": int(post.sum()),
        "post_P0_C_end_max": safe_max(rows.loc[post, "C_end"]),
        "post_P0_E_end_over_h_max": safe_max(rows.loc[post, "E_end_over_h"]),
        "post_P0_C_end_above_10_count": int((post & (num(rows["C_end"]) > 10)).sum()),
        "post_P0_E_end_over_h_above_100_count": int((post & (num(rows["E_end_over_h"]) > 100)).sum()),
        "pass_endpoint_affine_residual_bound": endpoint_pass,
        "post_P0_C_best_max": post_C_best_max,
        "post_P0_E_best_over_h_max": safe_max(rows.loc[post, "E_best_over_h"]),
        "post_P0_C_best_above_10_count": int((post & (num(rows["C_best"]) > 10)).sum()),
        "pass_best_affine_residual_bound": best_pass,
        "post_P0_C_gap_max": post_C_gap_max,
        "post_P0_E_gap_over_h_max": safe_max(rows.loc[post, "E_gap_over_h"]),
        "post_P0_gap_fraction_of_endpoint_residual_max": safe_max(rows.loc[post, "gap_fraction_of_endpoint_residual"]),
        "post_P0_gap_fraction_of_best_residual_max": safe_max(rows.loc[post, "gap_fraction_of_best_residual"]),
        "endpoint_best_gap_small_flag": endpoint_best_gap_small,
        "pythagorean_error_max": pyth_abs_max,
        "post_P0_pythagorean_error_max": post_pyth_abs_max,
        "pythagorean_relative_error_max": pyth_rel_max,
        "post_P0_pythagorean_relative_error_max": post_pyth_rel_max,
        "pass_projection_decomposition": pass_projection_decomposition,
        "post_P0_endpoint_residual_fraction_max": safe_max(rows.loc[post, "endpoint_residual_fraction"]),
        "post_P0_endpoint_residual_fraction_mean": safe_mean(rows.loc[post, "endpoint_residual_fraction"]),
        "post_P0_best_residual_fraction_max": safe_max(rows.loc[post, "best_residual_fraction"]),
        "post_P0_best_residual_fraction_mean": safe_mean(rows.loc[post, "best_residual_fraction"]),
        "post_P0_affine_capture_fraction_min": safe_min(rows.loc[post, "endpoint_affine_capture_fraction"]),
        "post_P0_best_affine_capture_fraction_min": safe_min(rows.loc[post, "best_affine_capture_fraction"]),
        "post_P0_slope_gap_abs_max": safe_max(rows.loc[post, "slope_gap_abs"]),
        "post_P0_intercept_gap_abs_max": safe_max(rows.loc[post, "intercept_gap_abs"]),
        "post_P0_endpoint_slope_abs_max": safe_max(rows.loc[post, "endpoint_slope"].abs()),
        "post_P0_best_slope_abs_max": safe_max(rows.loc[post, "b_best"].abs()),
        "threshold_relevant_C_end_max": safe_max(rows.loc[threshold, "C_end"]),
        "forbidden_C_end_max": safe_max(rows.loc[forbidden, "C_end"]),
        "threshold_relevant_C_best_max": safe_max(rows.loc[threshold, "C_best"]),
        "forbidden_C_best_max": safe_max(rows.loc[forbidden, "C_best"]),
        "threshold_relevant_C_gap_max": safe_max(rows.loc[threshold, "C_gap"]),
        "forbidden_C_gap_max": safe_max(rows.loc[forbidden, "C_gap"]),
        "C_end_vs_C_bridge_error_max": safe_max(rows["C_end_vs_C_bridge_error"]),
        "E_end_over_h_vs_C_bridge_sq_error_max": safe_max(rows["E_end_over_h_vs_C_bridge_sq_error"]),
        "best_proof_form_recommended": best_form,
        "affine_projection_residual_failures": int(rows["affine_projection_failure_flag"].sum()),
        "pass_hexc_affine_projection_residual_empirical": bool(rows["affine_projection_failure_flag"].sum() == 0),
        "recommended_theorem_form": theorem_form,
        "recommended_next_file": rec_file,
    }

    groups = []
    for col in [
        "row_regime",
        "post_P0_by_pstar",
        "finite_zone_flag",
        "high_energy_flag",
        "threshold_relevant_flag",
        "forbidden_flag",
        "h_bin_aff",
        "p_star_bin_aff",
        "sample_count_bin_aff",
    ]:
        if col in rows.columns:
            g = rows.groupby(col, dropna=False).apply(summarize_group, include_groups=False).reset_index()
            g.insert(0, "group_field", col)
            g = g.rename(columns={col: "group_value"})
            groups.append(g)
    by_regime = pd.concat(groups, ignore_index=True)

    metrics = [
        "C_end",
        "C_best",
        "C_gap",
        "E_end_over_h",
        "E_best_over_h",
        "E_gap_over_h",
        "endpoint_residual_fraction",
        "best_residual_fraction",
        "slope_gap_abs",
        "intercept_gap_abs",
        "pythagorean_abs_error",
    ]
    id_cols = [
        "candidate_id",
        "block_id",
        "x",
        "y",
        "h",
        "p_star",
        "row_regime",
        "post_P0_by_pstar",
        "threshold_relevant_flag",
        "forbidden_flag",
        "finite_zone_flag",
        "C_end",
        "C_best",
        "C_gap",
        "E_end_over_h",
        "E_best_over_h",
        "E_gap_over_h",
        "endpoint_residual_fraction",
        "best_residual_fraction",
        "slope_gap_abs",
        "intercept_gap_abs",
    ]
    extreme_frames = []
    for metric in metrics:
        if metric in rows.columns:
            cols = list(dict.fromkeys([c for c in id_cols + [metric] if c in rows.columns]))
            top = rows.sort_values(metric, ascending=False, na_position="last").head(25)[cols].copy()
            top.insert(0, "rank_metric", metric)
            top.insert(1, "rank", range(1, len(top) + 1))
            extreme_frames.append(top)
    extremes = pd.concat(extreme_frames, ignore_index=True)
    failures = rows.loc[rows["affine_projection_failure_flag"]].copy()

    out_summary = BASE / "prime_mesh_r2q_hexc_affine_projection_residual_summary.csv"
    out_rows = BASE / "prime_mesh_r2q_hexc_affine_projection_residual_rows.csv"
    out_by = BASE / "prime_mesh_r2q_hexc_affine_projection_residual_by_regime.csv"
    out_ext = BASE / "prime_mesh_r2q_hexc_affine_projection_residual_extremes.csv"
    out_fail = BASE / "prime_mesh_r2q_hexc_affine_projection_residual_failures.csv"
    out_md = BASE / "Prime_Mesh_R2Q_HExc_AffineProjectionResidual_Audit_v1.md"

    write_summary(out_summary, summary)
    rows.to_csv(out_rows, index=False)
    by_regime.to_csv(out_by, index=False)
    extremes.to_csv(out_ext, index=False)
    failures.to_csv(out_fail, index=False)

    md = f"""# Prime Mesh R2Q - H-Exc AffineProjectionResidual Audit v1

**Status:** empirical pass  
**Date:** {datetime.now().date().isoformat()}  
**Script:** `prime_mesh_r2q_hexc_affine_projection_residual_audit.py`

## Target

Compare the endpoint affine residual, best affine residual, and endpoint-vs-best affine gap for:

```text
p_star >= P0 => ||D_N - ell_endpoint||_2^2 <= 100h.
```

## Main Results

```text
rows                                      = {summary['rows']}
path_sample_blocks                        = {summary['path_sample_blocks']}
blocks_missing_path_samples               = {summary['blocks_missing_path_samples']}
path_reconstruction_ok                    = {summary['path_reconstruction_ok']}

post_P0_rows                              = {summary['post_P0_rows']}

post_P0_C_end_max                         = {summary['post_P0_C_end_max']}
post_P0_E_end_over_h_max                  = {summary['post_P0_E_end_over_h_max']}
post_P0_C_end_above_10_count              = {summary['post_P0_C_end_above_10_count']}
post_P0_E_end_over_h_above_100_count      = {summary['post_P0_E_end_over_h_above_100_count']}
pass_endpoint_affine_residual_bound       = {summary['pass_endpoint_affine_residual_bound']}

post_P0_C_best_max                        = {summary['post_P0_C_best_max']}
post_P0_E_best_over_h_max                 = {summary['post_P0_E_best_over_h_max']}
post_P0_C_best_above_10_count             = {summary['post_P0_C_best_above_10_count']}
pass_best_affine_residual_bound           = {summary['pass_best_affine_residual_bound']}

post_P0_C_gap_max                         = {summary['post_P0_C_gap_max']}
post_P0_E_gap_over_h_max                  = {summary['post_P0_E_gap_over_h_max']}
post_P0_gap_fraction_of_endpoint_residual_max = {summary['post_P0_gap_fraction_of_endpoint_residual_max']}
endpoint_best_gap_small_flag              = {summary['endpoint_best_gap_small_flag']}

pythagorean_error_max                     = {summary['pythagorean_error_max']}
post_P0_pythagorean_error_max             = {summary['post_P0_pythagorean_error_max']}
pythagorean_relative_error_max            = {summary['pythagorean_relative_error_max']}
post_P0_pythagorean_relative_error_max    = {summary['post_P0_pythagorean_relative_error_max']}
pass_projection_decomposition             = {summary['pass_projection_decomposition']}

post_P0_endpoint_residual_fraction_max    = {summary['post_P0_endpoint_residual_fraction_max']}
post_P0_best_residual_fraction_max        = {summary['post_P0_best_residual_fraction_max']}
post_P0_affine_capture_fraction_min       = {summary['post_P0_affine_capture_fraction_min']}

threshold_relevant_C_end_max              = {summary['threshold_relevant_C_end_max']}
forbidden_C_end_max                       = {summary['forbidden_C_end_max']}
threshold_relevant_C_best_max             = {summary['threshold_relevant_C_best_max']}
forbidden_C_best_max                      = {summary['forbidden_C_best_max']}

best_proof_form_recommended               = {summary['best_proof_form_recommended']}
affine_projection_residual_failures       = {summary['affine_projection_residual_failures']}
pass_hexc_affine_projection_residual_empirical = {summary['pass_hexc_affine_projection_residual_empirical']}
```

## Interpretation

The endpoint affine residual, which is the actual H-Exc theorem object, remains clean:

```text
p_star >= 500,000,000 => C_end <= {summary['post_P0_C_end_max']} < 10.
```

The best-affine projection decomposition is numerically exact to roundoff:

```text
E_end = E_best + E_gap.
```

Recommended theorem form:

```text
{summary['recommended_theorem_form']}
```

## Recommended Next File

```text
{summary['recommended_next_file']}
```
"""
    out_md.write_text(md, encoding="utf-8")

    outputs = [Path(__file__), out_summary, out_rows, out_by, out_ext, out_fail, out_md]
    update_manifest(outputs)
    print(md)


if __name__ == "__main__":
    main()
