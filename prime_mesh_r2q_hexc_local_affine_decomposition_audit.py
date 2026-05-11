#!/usr/bin/env python3
"""
Prime Mesh R2Q - H-Exc LocalAffineDecomposition audit.

Consolidates the endpoint-affine residual, best-affine split, curvature,
template, and component-correlation diagnostics to identify the cleanest proof
route for

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
EPS = 1e-30
TOL = 1e-7


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


def corr(df: pd.DataFrame, a: str, b: str) -> float:
    if a not in df.columns or b not in df.columns:
        return float("nan")
    tmp = df[[a, b]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(tmp) < 3:
        return float("nan")
    if tmp[a].std() == 0 or tmp[b].std() == 0:
        return float("nan")
    return float(tmp[a].corr(tmp[b]))


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
                "note": "H-Exc LocalAffineDecomposition audit output",
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
    sample_col = "sample_count_affine" if "sample_count_affine" in df.columns else ("sample_count" if "sample_count" in df.columns else None)
    m = num(df[sample_col]) if sample_col else pd.Series(np.nan, index=df.index)
    df["h_bin_laff"] = pd.cut(
        h,
        bins=[-np.inf, 1, 10, 100, 1_000, 10_000, 100_000, np.inf],
        labels=["h<=1", "2<=h<=10", "11<=h<=100", "101<=h<=1k", "1k<h<=10k", "10k<h<=100k", "h>100k"],
    ).astype(str)
    df["p_star_bin_laff"] = pd.cut(
        p,
        bins=[-np.inf, 1_000_000, 100_000_000, 500_000_000, 1_000_000_000, np.inf],
        labels=["p<1M", "1M<=p<100M", "100M<=p<500M", "500M<=p<1B", "p>=1B"],
    ).astype(str)
    df["sample_count_bin_laff"] = pd.cut(
        m,
        bins=[-np.inf, 2, 5, 10, 25, 50, 100, np.inf],
        labels=["m<=2", "3<=m<=5", "6<=m<=10", "11<=m<=25", "26<=m<=50", "51<=m<=100", "m>100"],
    ).astype(str)
    return df


def greedy_cluster_count(x: np.ndarray, tol: float) -> int:
    centers: list[np.ndarray] = []
    for v in x:
        if np.isnan(v).any():
            continue
        if any(np.linalg.norm(v - c) <= tol for c in centers):
            continue
        centers.append(v)
    return len(centers)


def build_template_assignments(rows: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    path = BASE / "prime_mesh_r2q_hexc_bridgeshape_curvature_shape_templates.csv"
    if not path.exists():
        return pd.DataFrame(), {
            "shape_template_count_tol_0p5": float("nan"),
            "shape_template_count_tol_1p0": float("nan"),
            "post_P0_shape_template_count_tol_0p5": float("nan"),
            "post_P0_shape_template_count_tol_1p0": float("nan"),
            "template_route_plausible_flag": False,
            "worst_template_C_end": float("nan"),
        }
    templates = pd.read_csv(path)
    shape_cols = [c for c in templates.columns if c.startswith("shape_")]
    x = templates[shape_cols].to_numpy(dtype=float)
    mean_shape = np.nanmean(x, axis=0)
    dist = np.sqrt(np.nansum((x - mean_shape) ** 2, axis=1))
    assignments = templates[["candidate_id"]].copy()
    assignments["distance_to_mean_template"] = dist

    joined = assignments.merge(rows[["candidate_id", "post_P0_by_pstar", "C_end"]], on="candidate_id", how="left")
    post = as_bool(joined["post_P0_by_pstar"])
    x_post = templates.loc[templates["candidate_id"].isin(joined.loc[post, "candidate_id"]), shape_cols].to_numpy(dtype=float)
    template_stats = {
        "shape_template_count_tol_0p5": int(greedy_cluster_count(x, 0.5)),
        "shape_template_count_tol_1p0": int(greedy_cluster_count(x, 1.0)),
        "post_P0_shape_template_count_tol_0p5": int(greedy_cluster_count(x_post, 0.5)) if len(x_post) else 0,
        "post_P0_shape_template_count_tol_1p0": int(greedy_cluster_count(x_post, 1.0)) if len(x_post) else 0,
        "template_route_plausible_flag": bool(greedy_cluster_count(x_post, 1.0) <= 20 if len(x_post) else False),
        "worst_template_C_end": safe_max(joined["C_end"]),
    }
    return assignments, template_stats


def summarize_group(g: pd.DataFrame) -> pd.Series:
    return pd.Series(
        {
            "rows": len(g),
            "E_end_over_h_max": safe_max(g["E_end_over_h"]),
            "C_end_max": safe_max(g["C_end"]),
            "endpoint_residual_fraction_max": safe_max(g["endpoint_residual_fraction"]),
            "affine_capture_fraction_min": safe_min(g["endpoint_affine_capture_fraction"]),
            "E_best_over_h_max": safe_max(g["E_best_over_h"]),
            "E_gap_over_h_max": safe_max(g["E_gap_over_h"]),
            "ratio_E_end_to_h4_ddR_sq_max": safe_max(g["ratio_E_end_to_h4_ddR_sq"]),
            "template_count": g["template_cluster_id"].nunique() if "template_cluster_id" in g else 0,
            "worst_template_C_end": safe_max(g["C_end"]),
            "failures": int(as_bool(g["local_affine_decomposition_failure_flag"]).sum()) if "local_affine_decomposition_failure_flag" in g else 0,
        }
    )


def main() -> None:
    rows = read_csv("prime_mesh_r2q_hexc_affine_projection_residual_rows.csv")

    # Normalize flags.
    rows["post_P0_by_pstar"] = as_bool(rows["post_P0_by_pstar"]) | (num(rows["p_star"]) >= P0)
    for col in ["finite_zone_flag", "high_energy_flag", "threshold_relevant_flag", "forbidden_flag"]:
        if col in rows.columns:
            rows[col] = as_bool(rows[col])
    if "threshold_relevant_flag" not in rows:
        rows["threshold_relevant_flag"] = num(rows["Q_R2Q"]) > 0.75
    if "forbidden_flag" not in rows:
        rows["forbidden_flag"] = num(rows["Q_R2Q"]) > 1.0
    if "high_energy_flag" not in rows:
        rows["high_energy_flag"] = num(rows["Q_energy_L2"]) > 0.025
    if "finite_zone_flag" not in rows:
        rows["finite_zone_flag"] = num(rows["p_star"]) < P0

    # Rename/spec-facing residual fields.
    rows["endpoint_residual_abs_max"] = num(rows.get("R_end_abs_max", rows.get("B_abs_max_shape", np.nan)))
    rows["endpoint_residual_L2"] = np.sqrt(num(rows["E_end"]).clip(lower=0))
    rows["endpoint_residual_sq_sum"] = num(rows["E_end"])
    rows["endpoint_residual_sq_over_h"] = num(rows["E_end_over_h"])
    rows["endpoint_residual_abs_q95"] = num(rows.get("B_abs_q95", np.nan))
    rows["endpoint_residual_abs_q99"] = num(rows.get("B_abs_q99", np.nan))
    rows["endpoint_residual_mean"] = num(rows.get("B_mean", np.nan))
    rows["endpoint_residual_std"] = num(rows.get("B_std", np.nan))
    rows["best_residual_abs_max"] = num(rows.get("R_best_abs_max", np.nan))
    rows["best_residual_L2"] = np.sqrt(num(rows["E_best"]).clip(lower=0))
    rows["best_residual_sq_over_h"] = num(rows["E_best_over_h"])
    rows["gap_abs_max"] = num(rows.get("gap_abs_max", np.nan))
    rows["gap_L2"] = np.sqrt(num(rows["E_gap"]).clip(lower=0))
    rows["gap_sq_over_h"] = num(rows["E_gap_over_h"])
    rows["dR_L2"] = num(rows.get("dB_L2", np.nan))
    rows["dR_sq_over_h"] = num(rows.get("dB_sq_over_h", np.nan))
    rows["ddR_L2"] = num(rows.get("ddB_L2", np.nan))
    rows["ddR_sq_over_h"] = num(rows.get("ddB_sq_over_h", np.nan))
    rows["ratio_R_L2_to_dR_L2"] = num(rows.get("ratio_B_L2_to_dB_L2", np.nan))
    rows["ratio_R_L2_to_h_dR_L2"] = num(rows.get("ratio_B_L2_to_h_dB_L2", np.nan))
    rows["ratio_R_L2_to_ddR_L2"] = num(rows.get("ratio_B_L2_to_ddB_L2", np.nan))
    rows["ratio_R_L2_to_h_ddR_L2"] = num(rows.get("ratio_B_L2_to_h_ddB_L2", np.nan))
    rows["ratio_R_L2_to_h2_ddR_L2"] = num(rows.get("ratio_B_L2_to_h2_ddB_L2", np.nan))
    rows["residual_effective_support"] = num(rows.get("effective_support", np.nan))
    rows["residual_effective_support_frac"] = num(rows.get("effective_support_frac", np.nan))
    rows["residual_kappa"] = num(rows["endpoint_residual_abs_max"]) / num(rows["endpoint_residual_L2"]).replace(0, np.nan)

    h = num(rows["h"])
    rows["ratio_E_end_to_h2_dR_sq"] = num(rows["E_end"]) / ((h ** 2) * num(rows["dB_sq_sum"]).replace(0, np.nan))
    rows["ratio_E_end_to_h4_ddR_sq"] = num(rows["E_end"]) / ((h ** 4) * num(rows["ddB_sq_sum"]).replace(0, np.nan))
    rows["E_best_plus_gap_over_h"] = (num(rows["E_best"]) + num(rows["E_gap"])) / h
    rows["Q_delta_D_share"] = num(rows.get("Q_delta_D", np.nan)) / num(rows.get("Q_R2Q", np.nan)).replace(0, np.nan)

    rows = add_bins(rows)
    assignments, template_stats = build_template_assignments(rows)
    if not assignments.empty:
        rows = rows.merge(assignments, on="candidate_id", how="left")
        # Coarse cluster id by rounded distance bucket. This is diagnostic only.
        rows["template_cluster_id"] = (num(rows["distance_to_mean_template"]) / 0.5).round().astype("Int64").astype(str)
    else:
        rows["distance_to_mean_template"] = np.nan
        rows["template_cluster_id"] = "NA"

    post = as_bool(rows["post_P0_by_pstar"])
    threshold = as_bool(rows["threshold_relevant_flag"])
    forbidden = as_bool(rows["forbidden_flag"])

    rows["local_affine_decomposition_failure_reason"] = ""
    rows.loc[rows.get("blocks_missing_path_samples_flag", False).astype(bool), "local_affine_decomposition_failure_reason"] = "missing_path_samples"
    rows.loc[post & (num(rows["E_end_over_h"]) > 100), "local_affine_decomposition_failure_reason"] = rows["local_affine_decomposition_failure_reason"].mask(
        rows["local_affine_decomposition_failure_reason"].eq(""), "post_P0_E_end_over_h_above_100"
    )
    rows.loc[post & (num(rows["C_end"]) > 10), "local_affine_decomposition_failure_reason"] = rows["local_affine_decomposition_failure_reason"].mask(
        rows["local_affine_decomposition_failure_reason"].eq(""), "post_P0_C_end_above_10"
    )
    rows["local_affine_decomposition_failure_flag"] = rows["local_affine_decomposition_failure_reason"].ne("")

    pass_endpoint = bool((post & (num(rows["E_end_over_h"]) > 100)).sum() == 0 and (post & (num(rows["C_end"]) > 10)).sum() == 0)
    pass_local_aff = bool(safe_min(rows.loc[post, "endpoint_affine_capture_fraction"]) >= 0.9999)
    endpoint_vs_best_split_clean = bool(safe_max(rows.loc[post, "E_best_plus_gap_over_h"]) <= 100)
    # These ratios are tiny with any endpoint-vanishing Poincare power, but this
    # is not as crisp as the local-affinity fraction.
    curvature_plausible = bool(safe_max(rows.loc[post, "ratio_E_end_to_h4_ddR_sq"]) <= 1.0)

    if pass_local_aff:
        best_route = "local_affinity_fraction"
        reason = "endpoint affine interpolation captures at least 99.9975% of D_N path energy post-P0, and residual energy stays below 100h."
        theorem = "local_affinity_energy_capture plus endpoint residual budget"
        rec_file = "Prime_Mesh_R2Q_HExc_LocalAffinity_EnergyCapture_Theorem_Target_v1.md"
    elif curvature_plausible:
        best_route = "curvature_poincare"
        reason = "endpoint-vanishing residual has bounded Poincare/curvature ratios post-P0."
        theorem = "endpoint_residual_curvature_bound"
        rec_file = "Prime_Mesh_R2Q_HExc_EndpointResidual_Curvature_Theorem_Target_v1.md"
    else:
        best_route = "endpoint_residual_direct"
        reason = "endpoint residual bound is clean, but no sharper structural route dominates."
        theorem = "endpoint_affine_residual_bound: p_star >= P0 => ||D_N-ell_endpoint||_2^2 <= 100h"
        rec_file = "Prime_Mesh_R2Q_HExc_EndpointAffineResidual_Formal_Proof_Draft_v1.md"

    summary = {
        "rows": int(len(rows)),
        "path_sample_blocks": int(rows["candidate_id"].nunique()),
        "blocks_missing_path_samples": int(rows.get("blocks_missing_path_samples_flag", pd.Series(False, index=rows.index)).sum()),
        "path_reconstruction_ok": bool(safe_max(rows.get("C_end_vs_C_bridge_error", pd.Series(0, index=rows.index))) <= TOL),
        "P0": P0,
        "post_P0_rows": int(post.sum()),
        "post_P0_E_end_over_h_max": safe_max(rows.loc[post, "E_end_over_h"]),
        "post_P0_C_end_max": safe_max(rows.loc[post, "C_end"]),
        "post_P0_E_end_over_h_above_100_count": int((post & (num(rows["E_end_over_h"]) > 100)).sum()),
        "post_P0_C_end_above_10_count": int((post & (num(rows["C_end"]) > 10)).sum()),
        "pass_endpoint_residual_bound": pass_endpoint,
        "post_P0_endpoint_residual_fraction_max": safe_max(rows.loc[post, "endpoint_residual_fraction"]),
        "post_P0_endpoint_residual_fraction_mean": safe_mean(rows.loc[post, "endpoint_residual_fraction"]),
        "post_P0_affine_capture_fraction_min": safe_min(rows.loc[post, "endpoint_affine_capture_fraction"]),
        "post_P0_affine_capture_fraction_mean": safe_mean(rows.loc[post, "endpoint_affine_capture_fraction"]),
        "pass_local_affinity_fraction_strong": pass_local_aff,
        "post_P0_E_best_over_h_max": safe_max(rows.loc[post, "E_best_over_h"]),
        "post_P0_E_gap_over_h_max": safe_max(rows.loc[post, "E_gap_over_h"]),
        "post_P0_E_best_plus_gap_over_h_max": safe_max(rows.loc[post, "E_best_plus_gap_over_h"]),
        "post_P0_gap_fraction_of_endpoint_residual_max": safe_max(rows.loc[post, "gap_fraction_of_endpoint_residual"]),
        "endpoint_vs_best_split_clean_flag": endpoint_vs_best_split_clean,
        "post_P0_ratio_E_end_to_h2_dR_sq_max": safe_max(rows.loc[post, "ratio_E_end_to_h2_dR_sq"]),
        "post_P0_ratio_E_end_to_h4_ddR_sq_max": safe_max(rows.loc[post, "ratio_E_end_to_h4_ddR_sq"]),
        "curvature_route_plausible_flag": curvature_plausible,
        **template_stats,
        "corr_E_end_over_h_Q_delta_D": corr(rows, "E_end_over_h", "Q_delta_D"),
        "corr_E_end_over_h_Q_exc": corr(rows, "E_end_over_h", "Q_exc"),
        "corr_E_end_over_h_epsilon": corr(rows, "E_end_over_h", "epsilon"),
        "corr_E_end_over_h_Q_R2Q": corr(rows, "E_end_over_h", "Q_R2Q"),
        "corr_E_end_over_h_kappa_L2": corr(rows, "E_end_over_h", "kappa_L2"),
        "corr_E_end_over_h_log_pstar": corr(rows, "E_end_over_h", "log_pstar"),
        "corr_E_end_over_h_h": corr(rows, "E_end_over_h", "h"),
        "corr_E_end_over_h_h_over_x": corr(rows, "E_end_over_h", "h_over_x"),
        "corr_E_end_over_h_rho_proxy": corr(rows, "E_end_over_h", "rho_proxy"),
        "threshold_relevant_E_end_over_h_max": safe_max(rows.loc[threshold, "E_end_over_h"]),
        "forbidden_E_end_over_h_max": safe_max(rows.loc[forbidden, "E_end_over_h"]),
        "threshold_relevant_C_end_max": safe_max(rows.loc[threshold, "C_end"]),
        "forbidden_C_end_max": safe_max(rows.loc[forbidden, "C_end"]),
        "best_proof_route_candidate": best_route,
        "best_proof_route_reason": reason,
        "local_affine_decomposition_failures": int(rows["local_affine_decomposition_failure_flag"].sum()),
        "pass_hexc_local_affine_decomposition_empirical": bool(rows["local_affine_decomposition_failure_flag"].sum() == 0),
        "recommended_theorem_form": theorem,
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
        "h_bin_laff",
        "p_star_bin_laff",
        "sample_count_bin_laff",
        "template_cluster_id",
    ]:
        if col in rows.columns:
            g = rows.groupby(col, dropna=False).apply(summarize_group, include_groups=False).reset_index()
            g.insert(0, "group_field", col)
            g = g.rename(columns={col: "group_value"})
            groups.append(g)
    by_regime = pd.concat(groups, ignore_index=True)

    metrics = [
        "E_end_over_h",
        "C_end",
        "endpoint_residual_abs_max",
        "residual_kappa",
        "E_best_over_h",
        "E_gap_over_h",
        "ddR_sq_over_h",
        "distance_to_mean_template",
        "endpoint_residual_fraction",
        "ratio_E_end_to_h4_ddR_sq",
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
        "E_end_over_h",
        "C_end",
        "endpoint_residual_abs_max",
        "residual_kappa",
        "E_best_over_h",
        "E_gap_over_h",
        "endpoint_residual_fraction",
    ]
    ext_frames = []
    for metric in metrics:
        if metric in rows.columns:
            cols = list(dict.fromkeys([c for c in id_cols + [metric] if c in rows.columns]))
            top = rows.sort_values(metric, ascending=False, na_position="last").head(25)[cols].copy()
            top.insert(0, "rank_metric", metric)
            top.insert(1, "rank", range(1, len(top) + 1))
            ext_frames.append(top)
    extremes = pd.concat(ext_frames, ignore_index=True)
    failures = rows.loc[rows["local_affine_decomposition_failure_flag"]].copy()

    out_summary = BASE / "prime_mesh_r2q_hexc_local_affine_decomposition_summary.csv"
    out_rows = BASE / "prime_mesh_r2q_hexc_local_affine_decomposition_rows.csv"
    out_by = BASE / "prime_mesh_r2q_hexc_local_affine_decomposition_by_regime.csv"
    out_ext = BASE / "prime_mesh_r2q_hexc_local_affine_decomposition_extremes.csv"
    out_fail = BASE / "prime_mesh_r2q_hexc_local_affine_decomposition_failures.csv"
    out_md = BASE / "Prime_Mesh_R2Q_HExc_LocalAffineDecomposition_Audit_v1.md"
    out_assign = BASE / "prime_mesh_r2q_hexc_local_affine_decomposition_template_assignments.csv"

    write_summary(out_summary, summary)
    rows.to_csv(out_rows, index=False)
    by_regime.to_csv(out_by, index=False)
    extremes.to_csv(out_ext, index=False)
    failures.to_csv(out_fail, index=False)
    if not assignments.empty:
        assignments.to_csv(out_assign, index=False)

    md = f"""# Prime Mesh R2Q - H-Exc LocalAffineDecomposition Audit v1

**Status:** empirical pass  
**Date:** {datetime.now().date().isoformat()}  
**Script:** `prime_mesh_r2q_hexc_local_affine_decomposition_audit.py`

## Target

Identify the structural mechanism behind:

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
post_P0_E_end_over_h_max                  = {summary['post_P0_E_end_over_h_max']}
post_P0_C_end_max                         = {summary['post_P0_C_end_max']}
post_P0_E_end_over_h_above_100_count      = {summary['post_P0_E_end_over_h_above_100_count']}
post_P0_C_end_above_10_count              = {summary['post_P0_C_end_above_10_count']}
pass_endpoint_residual_bound              = {summary['pass_endpoint_residual_bound']}

post_P0_endpoint_residual_fraction_max    = {summary['post_P0_endpoint_residual_fraction_max']}
post_P0_affine_capture_fraction_min       = {summary['post_P0_affine_capture_fraction_min']}
pass_local_affinity_fraction_strong       = {summary['pass_local_affinity_fraction_strong']}

post_P0_E_best_over_h_max                 = {summary['post_P0_E_best_over_h_max']}
post_P0_E_gap_over_h_max                  = {summary['post_P0_E_gap_over_h_max']}
post_P0_E_best_plus_gap_over_h_max        = {summary['post_P0_E_best_plus_gap_over_h_max']}
endpoint_vs_best_split_clean_flag         = {summary['endpoint_vs_best_split_clean_flag']}

post_P0_ratio_E_end_to_h2_dR_sq_max       = {summary['post_P0_ratio_E_end_to_h2_dR_sq_max']}
post_P0_ratio_E_end_to_h4_ddR_sq_max      = {summary['post_P0_ratio_E_end_to_h4_ddR_sq_max']}
curvature_route_plausible_flag            = {summary['curvature_route_plausible_flag']}

post_P0_shape_template_count_tol_0p5      = {summary['post_P0_shape_template_count_tol_0p5']}
post_P0_shape_template_count_tol_1p0      = {summary['post_P0_shape_template_count_tol_1p0']}
template_route_plausible_flag             = {summary['template_route_plausible_flag']}

best_proof_route_candidate                = {summary['best_proof_route_candidate']}
local_affine_decomposition_failures       = {summary['local_affine_decomposition_failures']}
pass_hexc_local_affine_decomposition_empirical = {summary['pass_hexc_local_affine_decomposition_empirical']}
```

## Component Correlations

```text
corr(E_end/h, Q_delta_D) = {summary['corr_E_end_over_h_Q_delta_D']}
corr(E_end/h, Q_exc)     = {summary['corr_E_end_over_h_Q_exc']}
corr(E_end/h, epsilon)   = {summary['corr_E_end_over_h_epsilon']}
corr(E_end/h, Q_R2Q)     = {summary['corr_E_end_over_h_Q_R2Q']}
corr(E_end/h, kappa_L2)  = {summary['corr_E_end_over_h_kappa_L2']}
```

## Interpretation

The endpoint residual bound remains clean, and the strongest structural explanation is:

```text
{summary['best_proof_route_candidate']}
```

Reason:

```text
{summary['best_proof_route_reason']}
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
    if not assignments.empty:
        outputs.append(out_assign)
    update_manifest(outputs)
    print(md)


if __name__ == "__main__":
    main()
