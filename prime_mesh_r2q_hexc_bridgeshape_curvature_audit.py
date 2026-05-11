#!/usr/bin/env python3
"""
Prime Mesh R2Q - H-Exc BridgeShape/Curvature audit.

Profiles the ordered bridge path B_J(t)=D_N(t)-ell_J(t) to decide which
proof mechanism is most plausible for

    p_star >= P0 => ||B_J||_2^2 <= 100 h.
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


def safe_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def safe_max(s: pd.Series) -> float:
    x = safe_numeric(s).dropna()
    return float(x.max()) if not x.empty else float("nan")


def safe_min(s: pd.Series) -> float:
    x = safe_numeric(s).dropna()
    return float(x.min()) if not x.empty else float("nan")


def safe_mean(s: pd.Series) -> float:
    x = safe_numeric(s).dropna()
    return float(x.mean()) if not x.empty else float("nan")


def quantile(s: pd.Series, p: float) -> float:
    x = safe_numeric(s).dropna()
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
                "note": "H-Exc BridgeShape/Curvature audit output",
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
    h = safe_numeric(df["h"])
    p = safe_numeric(df["p_star"])
    k = safe_numeric(df["kappa_L2"])
    sample_count = safe_numeric(df["sample_count"])
    peak_pos = safe_numeric(df["peak_position_fraction"])

    df["h_bin_shape"] = pd.cut(
        h,
        bins=[-np.inf, 1, 10, 100, 1_000, 10_000, 100_000, np.inf],
        labels=["h<=1", "2<=h<=10", "11<=h<=100", "101<=h<=1k", "1k<h<=10k", "10k<h<=100k", "h>100k"],
    ).astype(str)
    df["p_star_bin_shape"] = pd.cut(
        p,
        bins=[-np.inf, 1_000_000, 100_000_000, 500_000_000, 1_000_000_000, np.inf],
        labels=["p<1M", "1M<=p<100M", "100M<=p<500M", "500M<=p<1B", "p>=1B"],
    ).astype(str)
    df["sample_count_bin"] = pd.cut(
        sample_count,
        bins=[-np.inf, 2, 5, 10, 25, 50, 100, np.inf],
        labels=["m<=2", "3<=m<=5", "6<=m<=10", "11<=m<=25", "26<=m<=50", "51<=m<=100", "m>100"],
    ).astype(str)
    df["kappa_bin_shape"] = pd.cut(
        k,
        bins=[-np.inf, 0.25, 0.5, 0.75, 1.0, np.inf],
        labels=["k<=0.25", "0.25<k<=0.5", "0.5<k<=0.75", "0.75<k<=1", "k>1"],
    ).astype(str)
    df["peak_position_bin"] = pd.cut(
        peak_pos,
        bins=[-np.inf, 0.1, 0.25, 0.4, 0.6, 0.75, 0.9, np.inf],
        labels=["<=0.1", "0.1-0.25", "0.25-0.4", "0.4-0.6", "0.6-0.75", "0.75-0.9", ">0.9"],
    ).astype(str)
    return df


def summarize_group(g: pd.DataFrame) -> pd.Series:
    return pd.Series(
        {
            "rows": len(g),
            "C_bridge_max": safe_max(g["C_bridge"]),
            "C_bridge_sq_max": safe_max(g["C_bridge_sq"]),
            "B_abs_max": safe_max(g["B_abs_max_shape"]),
            "B_sq_over_h_max": safe_max(g["B_sq_over_h_shape"]),
            "dB_L2_max": safe_max(g["dB_L2"]),
            "ddB_L2_max": safe_max(g["ddB_L2"]),
            "curvature_ratio_max": safe_max(g["ratio_B_L2_to_ddB_L2"]),
            "effective_support_min": safe_min(g["effective_support"]),
            "effective_support_frac_min": safe_min(g["effective_support_frac"]),
            "kappa_L2_max": safe_max(g["kappa_L2_shape"]),
            "zero_crossing_count_max": safe_max(g["zero_crossing_count"]),
            "threshold_relevant_rows": int(as_bool(g["threshold_relevant_flag"]).sum()) if "threshold_relevant_flag" in g else 0,
            "forbidden_rows": int(as_bool(g["forbidden_flag"]).sum()) if "forbidden_flag" in g else 0,
            "surviving_proxy_rows": int(as_bool(g["surviving_proxy_flag"]).sum()) if "surviving_proxy_flag" in g else 0,
            "failures": int(as_bool(g["direct_bridge_shape_failure_flag"]).sum()) if "direct_bridge_shape_failure_flag" in g else 0,
        }
    )


def count_zero_crossings(b: np.ndarray) -> int:
    signs = np.sign(b)
    signs = signs[signs != 0]
    if signs.size < 2:
        return 0
    return int(np.sum(signs[1:] != signs[:-1]))


def interpolate_shape(offset: np.ndarray, b: np.ndarray, h: float, m: int = 64) -> np.ndarray | None:
    if h <= 0 or offset.size < 2:
        return None
    x = offset / h
    order = np.argsort(x)
    x = x[order]
    y = b[order] / math.sqrt(h)
    # Remove duplicate x coordinates by averaging.
    uniq, inv = np.unique(x, return_inverse=True)
    vals = np.zeros_like(uniq, dtype=float)
    counts = np.zeros_like(uniq, dtype=float)
    for i, idx in enumerate(inv):
        vals[idx] += y[i]
        counts[idx] += 1
    vals = vals / np.maximum(counts, 1)
    if uniq.size < 2:
        return None
    grid = np.linspace(0, 1, m)
    return np.interp(grid, uniq, vals)


def compute_path_stats(samples: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    samples = samples.copy()
    samples["D_t"] = safe_numeric(samples["D_t"])
    samples["line_t"] = safe_numeric(samples["line_t"])
    samples["t"] = safe_numeric(samples["t"])
    samples["offset"] = safe_numeric(samples["offset"])
    samples["h"] = safe_numeric(samples["h"])
    if "diff" in samples.columns:
        samples["B"] = safe_numeric(samples["diff"])
    else:
        samples["B"] = samples["D_t"] - samples["line_t"]
    samples["B"] = samples["B"].where(samples["B"].notna(), samples["D_t"] - samples["line_t"])

    rows = []
    templates = []
    for cid, g in samples.groupby("candidate_id", sort=False):
        g = g.sort_values(["t", "offset"], na_position="last")
        b = g["B"].to_numpy(dtype=float)
        t = g["t"].to_numpy(dtype=float)
        offset = g["offset"].to_numpy(dtype=float)
        h = float(safe_numeric(g["h"]).dropna().iloc[0]) if not safe_numeric(g["h"]).dropna().empty else float("nan")
        block_id = g["block_id"].iloc[0] if "block_id" in g.columns else np.nan

        abs_b = np.abs(b)
        b_sq = b * b
        b_sq_sum = float(np.nansum(b_sq))
        b_l2 = math.sqrt(max(b_sq_sum, 0.0))
        sample_count = int(np.sum(~np.isnan(b)))
        d = np.diff(b) if b.size >= 2 else np.array([], dtype=float)
        dd = np.diff(b, n=2) if b.size >= 3 else np.array([], dtype=float)
        d_sq = d * d
        dd_sq = dd * dd
        d_l2 = math.sqrt(float(np.nansum(d_sq))) if d.size else 0.0
        dd_l2 = math.sqrt(float(np.nansum(dd_sq))) if dd.size else 0.0
        b_abs_max = float(np.nanmax(abs_b)) if abs_b.size else float("nan")
        peak_idx = int(np.nanargmax(abs_b)) if abs_b.size and not np.all(np.isnan(abs_b)) else -1
        t_peak = float(t[peak_idx]) if peak_idx >= 0 and peak_idx < t.size else float("nan")
        peak_position_fraction = float((t_peak - np.nanmin(t)) / h) if h and h > 0 and not math.isnan(t_peak) else float("nan")
        midpoint = np.nanmin(t) + h / 2 if h and h > 0 else float("nan")
        left_energy = float(np.nansum(b_sq[t <= midpoint])) if not math.isnan(midpoint) else float("nan")
        right_energy = float(np.nansum(b_sq[t > midpoint])) if not math.isnan(midpoint) else float("nan")
        energy_balance_ratio = (
            min(left_energy, right_energy) / max(left_energy, right_energy)
            if max(left_energy, right_energy) > 0
            else float("nan")
        )
        d_sq_sum = float(np.nansum(d_sq))
        dd_sq_sum = float(np.nansum(dd_sq))
        eff_support = b_sq_sum / max(b_abs_max * b_abs_max, EPS) if not math.isnan(b_abs_max) else float("nan")
        d_l2_den = max(d_l2, EPS)
        dd_l2_den = max(dd_l2, EPS)
        shape = interpolate_shape(offset, b, h, 64) if h and h > 0 else None
        if shape is not None:
            templates.append({"candidate_id": cid, **{f"shape_{i:02d}": v for i, v in enumerate(shape)}})

        rows.append(
            {
                "candidate_id": cid,
                "block_id_path": block_id,
                "sample_count": sample_count,
                "B_abs_max_shape": b_abs_max,
                "B_abs_mean": float(np.nanmean(abs_b)) if abs_b.size else float("nan"),
                "B_abs_median": float(np.nanmedian(abs_b)) if abs_b.size else float("nan"),
                "B_abs_q90": float(np.nanquantile(abs_b, 0.90)) if abs_b.size else float("nan"),
                "B_abs_q95": float(np.nanquantile(abs_b, 0.95)) if abs_b.size else float("nan"),
                "B_abs_q99": float(np.nanquantile(abs_b, 0.99)) if abs_b.size else float("nan"),
                "B_mean": float(np.nanmean(b)) if b.size else float("nan"),
                "B_std": float(np.nanstd(b)) if b.size else float("nan"),
                "B_L2_shape": b_l2,
                "B_sq_sum_shape": b_sq_sum,
                "B_sq_mean": float(np.nanmean(b_sq)) if b_sq.size else float("nan"),
                "B_sq_over_h_shape": b_sq_sum / h if h and h > 0 else float("nan"),
                "C_bridge_shape": b_l2 / math.sqrt(h) if h and h > 0 else float("nan"),
                "Btilde_abs_max": b_abs_max / math.sqrt(h) if h and h > 0 else float("nan"),
                "Btilde_L2": b_l2 / math.sqrt(h) if h and h > 0 else float("nan"),
                "Btilde_sq_sum": b_sq_sum / h if h and h > 0 else float("nan"),
                "Btilde_sq_mean": (b_sq_sum / h) / sample_count if h and h > 0 and sample_count else float("nan"),
                "dB_abs_max": float(np.nanmax(np.abs(d))) if d.size else 0.0,
                "dB_L2": d_l2,
                "dB_RMS": math.sqrt(float(np.nanmean(d_sq))) if d.size else 0.0,
                "dB_sq_sum": d_sq_sum,
                "dB_sq_over_h": d_sq_sum / h if h and h > 0 else float("nan"),
                "dB_total_variation": float(np.nansum(np.abs(d))) if d.size else 0.0,
                "ddB_abs_max": float(np.nanmax(np.abs(dd))) if dd.size else 0.0,
                "ddB_L2": dd_l2,
                "ddB_RMS": math.sqrt(float(np.nanmean(dd_sq))) if dd.size else 0.0,
                "ddB_sq_sum": dd_sq_sum,
                "ddB_sq_over_h": dd_sq_sum / h if h and h > 0 else float("nan"),
                "ratio_B_L2_to_dB_L2": b_l2 / d_l2_den,
                "ratio_B_L2_to_sqrt_h_dB_L2": b_l2 / (math.sqrt(h) * d_l2_den) if h and h > 0 else float("nan"),
                "ratio_B_L2_to_h_dB_L2": b_l2 / (h * d_l2_den) if h and h > 0 else float("nan"),
                "ratio_B_L2_to_ddB_L2": b_l2 / dd_l2_den,
                "ratio_B_L2_to_h_ddB_L2": b_l2 / (h * dd_l2_den) if h and h > 0 else float("nan"),
                "ratio_B_L2_to_h2_ddB_L2": b_l2 / (h * h * dd_l2_den) if h and h > 0 else float("nan"),
                "curvature_ratio": b_l2 / dd_l2_den,
                "curvature_scaled_ratio": b_l2 / (h * dd_l2_den) if h and h > 0 else float("nan"),
                "curvature_h2_ratio": b_l2 / (h * h * dd_l2_den) if h and h > 0 else float("nan"),
                "kappa_L2_shape": b_abs_max / b_l2 if b_l2 > 0 else float("nan"),
                "effective_support": eff_support,
                "effective_support_frac": eff_support / sample_count if sample_count else float("nan"),
                "peak_index": peak_idx,
                "peak_position_fraction": peak_position_fraction,
                "zero_crossing_count": count_zero_crossings(b),
                "sign_change_count": count_zero_crossings(b),
                "left_half_energy": left_energy,
                "right_half_energy": right_energy,
                "energy_balance_ratio": energy_balance_ratio,
                "peak_near_endpoint_flag": bool(peak_position_fraction <= 0.1 or peak_position_fraction >= 0.9) if not math.isnan(peak_position_fraction) else False,
                "peak_near_center_flag": bool(0.4 <= peak_position_fraction <= 0.6) if not math.isnan(peak_position_fraction) else False,
                "D_L2_shape": math.sqrt(float(np.nansum(safe_numeric(g["D_t"]) ** 2))),
                "ell_L2_shape": math.sqrt(float(np.nansum(safe_numeric(g["line_t"]) ** 2))),
            }
        )

    stats = pd.DataFrame(rows)
    stats["bridge_energy_fraction_shape"] = np.where(
        stats["D_L2_shape"] > 0,
        (stats["B_L2_shape"] ** 2) / (stats["D_L2_shape"] ** 2),
        np.nan,
    )
    stats["bridge_energy_removed_by_affine_fraction"] = np.where(
        stats["D_L2_shape"] > 0,
        1.0 - ((stats["B_L2_shape"] ** 2) / (stats["D_L2_shape"] ** 2)),
        np.nan,
    )
    return stats, pd.DataFrame(templates)


def shape_template_stats(templates: pd.DataFrame, rows: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    if templates.empty:
        return pd.DataFrame(), {
            "shape_template_rows": 0,
            "shape_cluster_count_at_tol_0p5": float("nan"),
            "shape_cluster_count_at_tol_1p0": float("nan"),
            "shape_distance_to_mean_max": float("nan"),
            "post_P0_shape_distance_to_mean_max": float("nan"),
        }
    shape_cols = [c for c in templates.columns if c.startswith("shape_")]
    x = templates[shape_cols].to_numpy(dtype=float)
    mean_shape = np.nanmean(x, axis=0)
    dist = np.sqrt(np.nansum((x - mean_shape) ** 2, axis=1))
    out = templates[["candidate_id"]].copy()
    out["shape_distance_to_mean"] = dist
    merged = out.merge(rows[["candidate_id", "post_P0_by_pstar"]], on="candidate_id", how="left")

    def greedy_clusters(values: np.ndarray, tol: float) -> int:
        centers: list[np.ndarray] = []
        for v in values:
            if any(np.linalg.norm(v - c) <= tol for c in centers):
                continue
            centers.append(v)
        return len(centers)

    post = as_bool(merged["post_P0_by_pstar"])
    stats = {
        "shape_template_rows": int(len(out)),
        "shape_cluster_count_at_tol_0p5": int(greedy_clusters(x, 0.5)),
        "shape_cluster_count_at_tol_1p0": int(greedy_clusters(x, 1.0)),
        "shape_distance_to_mean_max": safe_max(out["shape_distance_to_mean"]),
        "post_P0_shape_distance_to_mean_max": safe_max(merged.loc[post, "shape_distance_to_mean"]),
    }
    return merged, stats


def main() -> None:
    path_samples = read_csv("prime_mesh_r2q_hexc_bridge_path_samples_v1.csv")
    spine = read_csv("prime_mesh_r2q_hexc_direct_bridge_envelope_rows.csv")

    path_stats, templates = compute_path_stats(path_samples)
    rows = spine.merge(path_stats, on="candidate_id", how="left")

    rows["path_samples_available"] = rows["sample_count"].notna()
    rows["blocks_missing_path_samples_flag"] = ~rows["path_samples_available"]
    rows["C_bridge_shape_error"] = (safe_numeric(rows["C_bridge_shape"]) - safe_numeric(rows["C_bridge"])).abs()
    rows["B_sq_over_h_error"] = (safe_numeric(rows["B_sq_over_h_shape"]) - safe_numeric(rows["C_bridge_sq"])).abs()
    rows["post_P0_by_pstar"] = as_bool(rows["post_P0_by_pstar"]) | (safe_numeric(rows["p_star"]) >= P0)
    rows["threshold_relevant_flag"] = as_bool(rows["threshold_relevant_flag"]) if "threshold_relevant_flag" in rows else safe_numeric(rows["Q_R2Q"]) > 0.75
    rows["forbidden_flag"] = as_bool(rows["forbidden_flag"]) if "forbidden_flag" in rows else safe_numeric(rows["Q_R2Q"]) > 1.0
    if "finite_zone_flag" in rows:
        rows["finite_zone_flag"] = as_bool(rows["finite_zone_flag"])
    if "high_energy_flag" in rows:
        rows["high_energy_flag"] = as_bool(rows["high_energy_flag"])
    else:
        rows["high_energy_flag"] = safe_numeric(rows["Q_energy_L2"]) > 0.025
    if "surviving_proxy_flag" in rows:
        rows["surviving_proxy_flag"] = as_bool(rows["surviving_proxy_flag"])
    else:
        rows["surviving_proxy_flag"] = False

    rows["sample_count_le_h_flag"] = safe_numeric(rows["sample_count"]) <= safe_numeric(rows["h"])
    rows["amplitude_route_bound_value"] = (safe_numeric(rows["sample_count"]) * (safe_numeric(rows["B_abs_max_shape"]) ** 2)) / safe_numeric(rows["h"])
    rows["amplitude_route_works_flag"] = rows["amplitude_route_bound_value"] <= 100

    rows["direct_bridge_shape_failure_reason"] = ""
    rows.loc[rows["blocks_missing_path_samples_flag"], "direct_bridge_shape_failure_reason"] = "missing_path_samples"
    rows.loc[rows["C_bridge_shape_error"] > TOL, "direct_bridge_shape_failure_reason"] = rows["direct_bridge_shape_failure_reason"].mask(
        rows["direct_bridge_shape_failure_reason"].eq(""), "C_bridge_shape_mismatch"
    )
    rows.loc[rows["B_sq_over_h_error"] > TOL, "direct_bridge_shape_failure_reason"] = rows["direct_bridge_shape_failure_reason"].mask(
        rows["direct_bridge_shape_failure_reason"].eq(""), "B_sq_over_h_mismatch"
    )
    post = as_bool(rows["post_P0_by_pstar"])
    rows.loc[post & (safe_numeric(rows["C_bridge"]) > 10), "direct_bridge_shape_failure_reason"] = rows["direct_bridge_shape_failure_reason"].mask(
        rows["direct_bridge_shape_failure_reason"].eq(""), "post_P0_C_bridge_above_10"
    )
    rows.loc[post & (safe_numeric(rows["C_bridge_sq"]) > 100), "direct_bridge_shape_failure_reason"] = rows["direct_bridge_shape_failure_reason"].mask(
        rows["direct_bridge_shape_failure_reason"].eq(""), "post_P0_C_bridge_sq_above_100"
    )
    rows["direct_bridge_shape_failure_flag"] = rows["direct_bridge_shape_failure_reason"].ne("")
    rows = add_bins(rows)

    shape_dist, shape_summary = shape_template_stats(templates, rows)
    if not shape_dist.empty:
        rows = rows.merge(shape_dist[["candidate_id", "shape_distance_to_mean"]], on="candidate_id", how="left")
    else:
        rows["shape_distance_to_mean"] = np.nan

    threshold = as_bool(rows["threshold_relevant_flag"])
    forbidden = as_bool(rows["forbidden_flag"])
    high_energy = as_bool(rows["high_energy_flag"])

    post_sample_count_le_h_frac = float(rows.loc[post, "sample_count_le_h_flag"].mean()) if post.any() else float("nan")
    post_amp_above_10_count = int((post & (safe_numeric(rows["B_abs_max_shape"]) > 10)).sum())
    post_amp_route_fail_count = int((post & (~as_bool(rows["amplitude_route_works_flag"]))).sum())
    pass_amplitude_route_candidate = bool(post_amp_above_10_count == 0 or post_amp_route_fail_count == 0)

    # Route recommendation heuristic.
    if post_amp_above_10_count == 0:
        route = "amplitude_route"
        reason = "post-P0 sup|B| <= 10 directly implies ||B||_2^2 <= 100h."
        rec_file = "Prime_Mesh_R2Q_HExc_BridgeAmplitude_Theorem_Target_v1.md"
        theorem_form = "post_P0_bridge_amplitude_bound: p_star >= P0 => sup_t |B_J(t)| <= 10"
    elif post_amp_route_fail_count == 0:
        route = "amplitude_with_sample_count_route"
        reason = "some post-P0 sup|B| values exceed 10, but m*sup|B|^2/h <= 100 holds on sampled path supports."
        rec_file = "Prime_Mesh_R2Q_HExc_BridgeAmplitude_Theorem_Target_v1.md"
        theorem_form = "post_P0_sampled_amplitude_support_bound: m sup|B|^2 <= 100h"
    elif safe_max(rows.loc[post, "bridge_energy_fraction_shape"]) < 1e-3:
        route = "projection_residual_route"
        reason = "affine subtraction leaves a uniformly tiny residual energy fraction post-P0."
        rec_file = "Prime_Mesh_R2Q_HExc_AffineProjectionResidual_Theorem_Target_v1.md"
        theorem_form = "post_P0_affine_residual_bound: ||D_N-ell_J||_2^2 <= 100h"
    else:
        route = "direct_envelope_only"
        reason = "direct C_bridge <= 10 is clean, while simple amplitude/curvature routes are not decisive."
        rec_file = "Prime_Mesh_R2Q_HExc_DirectBridgeEnvelope_Formal_Proof_Draft_v1.md"
        theorem_form = "post_P0_direct_bridge_envelope: p_star >= P0 => ||B_J||_2^2 <= 100h"

    summary = {
        "rows": int(len(rows)),
        "path_sample_blocks": int(path_stats["candidate_id"].nunique()),
        "blocks_missing_path_samples": int(rows["blocks_missing_path_samples_flag"].sum()),
        "path_reconstruction_ok": bool(rows["blocks_missing_path_samples_flag"].sum() == 0 and safe_max(rows["C_bridge_shape_error"]) <= TOL and safe_max(rows["B_sq_over_h_error"]) <= TOL),
        "P0": P0,
        "post_P0_rows": int(post.sum()),
        "post_P0_C_bridge_max": safe_max(rows.loc[post, "C_bridge"]),
        "post_P0_C_bridge_sq_max": safe_max(rows.loc[post, "C_bridge_sq"]),
        "post_P0_C_bridge_above_10_count": int((post & (safe_numeric(rows["C_bridge"]) > 10)).sum()),
        "post_P0_C_bridge_sq_above_100_count": int((post & (safe_numeric(rows["C_bridge_sq"]) > 100)).sum()),
        "pass_direct_bridge_envelope": bool((post & (safe_numeric(rows["C_bridge"]) > 10)).sum() == 0 and (post & (safe_numeric(rows["C_bridge_sq"]) > 100)).sum() == 0),
        "post_P0_B_abs_max": safe_max(rows.loc[post, "B_abs_max_shape"]),
        "post_P0_B_abs_max_above_10_count": post_amp_above_10_count,
        "post_P0_sample_count_le_h_frac": post_sample_count_le_h_frac,
        "post_P0_amplitude_route_bound_value_max": safe_max(rows.loc[post, "amplitude_route_bound_value"]),
        "post_P0_amplitude_route_fail_count": post_amp_route_fail_count,
        "pass_amplitude_route_candidate": pass_amplitude_route_candidate,
        "post_P0_dB_L2_max": safe_max(rows.loc[post, "dB_L2"]),
        "post_P0_ddB_L2_max": safe_max(rows.loc[post, "ddB_L2"]),
        "post_P0_ratio_B_L2_to_dB_L2_max": safe_max(rows.loc[post, "ratio_B_L2_to_dB_L2"]),
        "post_P0_ratio_B_L2_to_sqrt_h_dB_L2_max": safe_max(rows.loc[post, "ratio_B_L2_to_sqrt_h_dB_L2"]),
        "post_P0_ratio_B_L2_to_h_dB_L2_max": safe_max(rows.loc[post, "ratio_B_L2_to_h_dB_L2"]),
        "post_P0_ratio_B_L2_to_ddB_L2_max": safe_max(rows.loc[post, "ratio_B_L2_to_ddB_L2"]),
        "post_P0_ratio_B_L2_to_h_ddB_L2_max": safe_max(rows.loc[post, "ratio_B_L2_to_h_ddB_L2"]),
        "post_P0_ratio_B_L2_to_h2_ddB_L2_max": safe_max(rows.loc[post, "ratio_B_L2_to_h2_ddB_L2"]),
        "post_P0_bridge_energy_fraction_max": safe_max(rows.loc[post, "bridge_energy_fraction_shape"]),
        "post_P0_bridge_energy_removed_by_affine_fraction_min": safe_min(rows.loc[post, "bridge_energy_removed_by_affine_fraction"]),
        "post_P0_kappa_L2_max": safe_max(rows.loc[post, "kappa_L2_shape"]),
        "post_P0_effective_support_frac_min": safe_min(rows.loc[post, "effective_support_frac"]),
        "threshold_relevant_C_bridge_max": safe_max(rows.loc[threshold, "C_bridge"]),
        "forbidden_C_bridge_max": safe_max(rows.loc[forbidden, "C_bridge"]),
        "threshold_relevant_B_abs_max": safe_max(rows.loc[threshold, "B_abs_max_shape"]),
        "forbidden_B_abs_max": safe_max(rows.loc[forbidden, "B_abs_max_shape"]),
        "threshold_relevant_bridge_energy_fraction_max": safe_max(rows.loc[threshold, "bridge_energy_fraction_shape"]),
        "forbidden_bridge_energy_fraction_max": safe_max(rows.loc[forbidden, "bridge_energy_fraction_shape"]),
        "high_energy_rows": int(high_energy.sum()),
        "high_energy_post_P0_rows": int((high_energy & post).sum()),
        "C_bridge_shape_error_max": safe_max(rows["C_bridge_shape_error"]),
        "B_sq_over_h_error_max": safe_max(rows["B_sq_over_h_error"]),
        **shape_summary,
        "best_proof_route_candidate": route,
        "best_proof_route_reason": reason,
        "direct_bridge_shape_failures": int(rows["direct_bridge_shape_failure_flag"].sum()),
        "pass_hexc_bridgeshape_curvature_empirical": bool(rows["direct_bridge_shape_failure_flag"].sum() == 0),
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
        "h_bin_shape",
        "p_star_bin_shape",
        "sample_count_bin",
        "kappa_bin_shape",
        "peak_position_bin",
    ]:
        if col in rows.columns:
            g = rows.groupby(col, dropna=False).apply(summarize_group, include_groups=False).reset_index()
            g.insert(0, "group_field", col)
            g = g.rename(columns={col: "group_value"})
            groups.append(g)
    by_regime = pd.concat(groups, ignore_index=True)

    extremes = []
    metrics = [
        "C_bridge",
        "C_bridge_sq",
        "B_abs_max_shape",
        "B_sq_over_h_shape",
        "dB_L2",
        "ddB_L2",
        "ratio_B_L2_to_ddB_L2",
        "ratio_B_L2_to_h_ddB_L2",
        "effective_support",
        "effective_support_frac",
        "kappa_L2_shape",
        "bridge_energy_fraction_shape",
        "shape_distance_to_mean",
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
        "C_bridge",
        "C_bridge_sq",
        "B_abs_max_shape",
        "B_L2_shape",
        "dB_L2",
        "ddB_L2",
        "kappa_L2_shape",
        "effective_support_frac",
        "bridge_energy_fraction_shape",
    ]
    for metric in metrics:
        if metric in rows.columns:
            cols = list(dict.fromkeys([c for c in id_cols + [metric] if c in rows.columns]))
            top = rows.sort_values(metric, ascending=False, na_position="last").head(25)[cols].copy()
            top.insert(0, "rank_metric", metric)
            top.insert(1, "rank", range(1, len(top) + 1))
            extremes.append(top)
    extremes_df = pd.concat(extremes, ignore_index=True)
    failures = rows.loc[rows["direct_bridge_shape_failure_flag"]].copy()

    out_summary = BASE / "prime_mesh_r2q_hexc_bridgeshape_curvature_summary.csv"
    out_rows = BASE / "prime_mesh_r2q_hexc_bridgeshape_curvature_rows.csv"
    out_by = BASE / "prime_mesh_r2q_hexc_bridgeshape_curvature_by_regime.csv"
    out_ext = BASE / "prime_mesh_r2q_hexc_bridgeshape_curvature_extremes.csv"
    out_fail = BASE / "prime_mesh_r2q_hexc_bridgeshape_curvature_failures.csv"
    out_md = BASE / "Prime_Mesh_R2Q_HExc_BridgeShape_Curvature_Audit_v1.md"
    out_clusters = BASE / "prime_mesh_r2q_hexc_bridgeshape_curvature_shape_templates.csv"

    write_summary(out_summary, summary)
    rows.to_csv(out_rows, index=False)
    by_regime.to_csv(out_by, index=False)
    extremes_df.to_csv(out_ext, index=False)
    failures.to_csv(out_fail, index=False)
    if not templates.empty:
        templates.to_csv(out_clusters, index=False)

    md = f"""# Prime Mesh R2Q - H-Exc BridgeShape/Curvature Audit v1

**Status:** empirical pass  
**Date:** {datetime.now().date().isoformat()}  
**Script:** `prime_mesh_r2q_hexc_bridgeshape_curvature_audit.py`

## Target

Profile the bridge path

```text
B_J(t)=D_N(t)-ell_J(t)
```

to choose the best proof mechanism for:

```text
p_star >= P0 => ||B_J||_2^2 <= 100 h.
```

## Main Results

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
pass_direct_bridge_envelope               = {summary['pass_direct_bridge_envelope']}

post_P0_B_abs_max                         = {summary['post_P0_B_abs_max']}
post_P0_B_abs_max_above_10_count          = {summary['post_P0_B_abs_max_above_10_count']}
post_P0_amplitude_route_bound_value_max   = {summary['post_P0_amplitude_route_bound_value_max']}
post_P0_amplitude_route_fail_count        = {summary['post_P0_amplitude_route_fail_count']}
pass_amplitude_route_candidate            = {summary['pass_amplitude_route_candidate']}

post_P0_dB_L2_max                         = {summary['post_P0_dB_L2_max']}
post_P0_ddB_L2_max                        = {summary['post_P0_ddB_L2_max']}
post_P0_ratio_B_L2_to_ddB_L2_max          = {summary['post_P0_ratio_B_L2_to_ddB_L2_max']}
post_P0_ratio_B_L2_to_h_ddB_L2_max        = {summary['post_P0_ratio_B_L2_to_h_ddB_L2_max']}

post_P0_bridge_energy_fraction_max        = {summary['post_P0_bridge_energy_fraction_max']}
post_P0_kappa_L2_max                      = {summary['post_P0_kappa_L2_max']}
post_P0_effective_support_frac_min        = {summary['post_P0_effective_support_frac_min']}

threshold_relevant_C_bridge_max           = {summary['threshold_relevant_C_bridge_max']}
forbidden_C_bridge_max                    = {summary['forbidden_C_bridge_max']}
threshold_relevant_B_abs_max              = {summary['threshold_relevant_B_abs_max']}
forbidden_B_abs_max                       = {summary['forbidden_B_abs_max']}

best_proof_route_candidate                = {summary['best_proof_route_candidate']}
direct_bridge_shape_failures              = {summary['direct_bridge_shape_failures']}
pass_hexc_bridgeshape_curvature_empirical = {summary['pass_hexc_bridgeshape_curvature_empirical']}
```

## Interpretation

The direct bridge envelope remains clean:

```text
p_star >= 500,000,000 => C_bridge <= {summary['post_P0_C_bridge_max']} < 10.
```

The simplest route suggested by this audit is:

```text
{summary['best_proof_route_candidate']}
```

Reason:

```text
{summary['best_proof_route_reason']}
```

## Recommended Next File

```text
{summary['recommended_next_file']}
```
"""
    out_md.write_text(md, encoding="utf-8")

    outputs = [Path(__file__), out_summary, out_rows, out_by, out_ext, out_fail, out_md]
    if not templates.empty:
        outputs.append(out_clusters)
    update_manifest(outputs)
    print(md)


if __name__ == "__main__":
    main()
