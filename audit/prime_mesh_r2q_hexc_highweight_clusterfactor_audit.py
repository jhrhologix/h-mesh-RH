"""
Prime Mesh R2Q — H-Exc HighWeightRayleighCollapse ClusterFactor Audit.

Runs in the repair folder and writes all outputs next to this script.
The theorem scope is sampled-grid T_J only; no full-grid lifting is used.
"""

from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
P0 = 500_000_000
W_THRESHOLD = 1040.0
K_CAP = 65.0

FILES = {
    "pnt": "prime_mesh_r2q_hexc_highweight_pnt_mechanism_rows.csv",
    "coupling": "prime_mesh_r2q_hexc_primeshock_rayleighcoupling_rows.csv",
    "kernel": "prime_mesh_r2q_hexc_primeshock_kernelgram_rows.csv",
    "tj": "prime_mesh_r2q_hexc_tj_grid_extraction_rows.csv",
    "raw": "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv",
}

OUT_SCRIPT = "prime_mesh_r2q_hexc_highweight_clusterfactor_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_hexc_highweight_clusterfactor_summary.csv"
OUT_ROWS = "prime_mesh_r2q_hexc_highweight_clusterfactor_rows.csv"
OUT_BY_REGIME = "prime_mesh_r2q_hexc_highweight_clusterfactor_by_regime.csv"
OUT_EXTREMES = "prime_mesh_r2q_hexc_highweight_clusterfactor_extremes.csv"
OUT_FAILURES = "prime_mesh_r2q_hexc_highweight_clusterfactor_failures.csv"
OUT_COMPARE = "prime_mesh_r2q_hexc_highweight_clusterfactor_comparison_453_442.csv"
OUT_EXCEPTIONS = "prime_mesh_r2q_hexc_highweight_clusterfactor_exceptions.csv"
OUT_DOC = "Prime_Mesh_R2Q_HExc_HighWeightRayleighCollapse_ClusterFactor_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"


def parse_num_list(raw) -> list[float]:
    if pd.isna(raw):
        return []
    s = str(raw).strip()
    if not s:
        return []
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def parse_int_list(raw) -> list[int]:
    return [int(round(x)) for x in parse_num_list(raw)]


def safe_float(row, name: str, default=np.nan) -> float:
    return float(row[name]) if name in row and not pd.isna(row[name]) else default


def norm_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes"}


def corr(x: pd.Series, y: pd.Series, method: str = "pearson") -> float:
    xy = pd.DataFrame({"x": x, "y": y}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(xy) < 2 or xy["x"].nunique() < 2 or xy["y"].nunique() < 2:
        return float("nan")
    return float(xy["x"].corr(xy["y"], method=method))


def percentile(series: pd.Series, q: float) -> float:
    s = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return float(np.percentile(s.to_numpy(), q)) if len(s) else float("nan")


def classify_prime_offsets(y: int, event_offsets: list[int], weights: list[float]) -> tuple[list[int], list[float]]:
    """Keep Lambda events whose weight matches log(y+offset), i.e. actual primes."""
    prime_offsets: list[int] = []
    prime_weights: list[float] = []
    for off, weight in zip(event_offsets, weights):
        n = y + off
        if n > 1 and abs(weight - math.log(n)) <= 1e-7:
            prime_offsets.append(off)
            prime_weights.append(weight)
    return prime_offsets, prime_weights


def sample_variance_sum(offsets: list[int], h: int) -> float:
    if h <= 0:
        return float("nan")
    u = np.asarray(offsets, dtype=float) / float(h)
    return float(np.sum(u * (1.0 - u)))


def prime_distribution_metrics(prime_offsets: list[int], h: int) -> dict[str, float | str]:
    if not prime_offsets or h <= 0:
        return {
            "prime_u_values": "",
            "prime_u_min": np.nan,
            "prime_u_max": np.nan,
            "prime_u_mean": np.nan,
            "prime_u_median": np.nan,
            "prime_u_std": np.nan,
            "prime_u_iqr": np.nan,
            "prime_u_skew_proxy": np.nan,
            "prime_left_mass_frac": np.nan,
            "prime_right_mass_frac": np.nan,
            "prime_center_mass_frac": np.nan,
            "KS_stat_uniform": np.nan,
            "star_discrepancy": np.nan,
            "max_prefix_excess": np.nan,
            "max_prefix_deficit": np.nan,
            "event_gap_max": np.nan,
            "event_gap_mean": np.nan,
            "event_gap_median": np.nan,
            "event_gap_cv": np.nan,
        }

    u = np.sort(np.asarray(prime_offsets, dtype=float) / float(h))
    k = len(u)
    i = np.arange(1, k + 1, dtype=float)
    left_excess = i / k - u
    right_deficit = u - (i - 1) / k
    gaps = np.diff(np.sort(np.asarray(prime_offsets, dtype=float)))
    gap_mean = float(np.mean(gaps)) if len(gaps) else 0.0
    return {
        "prime_u_values": ",".join(f"{v:.10g}" for v in u),
        "prime_u_min": float(np.min(u)),
        "prime_u_max": float(np.max(u)),
        "prime_u_mean": float(np.mean(u)),
        "prime_u_median": float(np.median(u)),
        "prime_u_std": float(np.std(u, ddof=0)),
        "prime_u_iqr": float(np.percentile(u, 75) - np.percentile(u, 25)),
        "prime_u_skew_proxy": float(np.mean(u) - 0.5),
        "prime_left_mass_frac": float(np.mean(u <= 0.25)),
        "prime_right_mass_frac": float(np.mean(u >= 0.75)),
        "prime_center_mass_frac": float(np.mean((u > 0.25) & (u < 0.75))),
        "KS_stat_uniform": float(max(np.max(left_excess), np.max(right_deficit))),
        "star_discrepancy": float(max(np.max(left_excess), np.max(right_deficit))),
        "max_prefix_excess": float(np.max(left_excess)),
        "max_prefix_deficit": float(np.max(right_deficit)),
        "event_gap_max": float(np.max(gaps)) if len(gaps) else 0.0,
        "event_gap_mean": gap_mean,
        "event_gap_median": float(np.median(gaps)) if len(gaps) else 0.0,
        "event_gap_cv": float(np.std(gaps, ddof=0) / gap_mean) if gap_mean else 0.0,
    }


def prefixed_metrics(prefix: str, offsets: list[int], h: int) -> dict[str, float | str]:
    raw = prime_distribution_metrics(offsets, h)
    rename = {
        "prime_u_values": f"{prefix}_u_values",
        "prime_u_min": f"{prefix}_u_min",
        "prime_u_max": f"{prefix}_u_max",
        "prime_u_mean": f"{prefix}_u_mean",
        "prime_u_median": f"{prefix}_u_median",
        "prime_u_std": f"{prefix}_u_std",
        "prime_u_iqr": f"{prefix}_u_iqr",
        "prime_u_skew_proxy": f"{prefix}_u_skew_proxy",
        "prime_left_mass_frac": f"{prefix}_left_mass_frac",
        "prime_right_mass_frac": f"{prefix}_right_mass_frac",
        "prime_center_mass_frac": f"{prefix}_center_mass_frac",
        "KS_stat_uniform": f"{prefix}_KS_stat_uniform",
        "star_discrepancy": f"{prefix}_star_discrepancy",
        "max_prefix_excess": f"{prefix}_max_prefix_excess",
        "max_prefix_deficit": f"{prefix}_max_prefix_deficit",
        "event_gap_max": f"{prefix}_gap_max",
        "event_gap_mean": f"{prefix}_gap_mean",
        "event_gap_median": f"{prefix}_gap_median",
        "event_gap_cv": f"{prefix}_gap_cv",
    }
    return {rename[k]: v for k, v in raw.items()}


def bridge_metrics(sample_offsets: list[int], h: int, prime_offsets: list[int], weights: list[float]) -> dict[str, float]:
    if h <= 0 or not sample_offsets or not prime_offsets:
        return {
            "bridge_peak_offset": np.nan,
            "bridge_peak_u": np.nan,
            "bridge_peak_value": np.nan,
            "bridge_energy_concentration": np.nan,
        }
    samples = np.asarray(sample_offsets, dtype=float)
    events = np.asarray(prime_offsets, dtype=float)
    w = np.asarray(weights, dtype=float)
    order = np.argsort(events)
    events = events[order]
    w = w[order]
    total = float(np.sum(w))
    csum = np.cumsum(w)
    vals = []
    for r in samples:
        idx = np.searchsorted(events, r, side="right") - 1
        prefix = float(csum[idx]) if idx >= 0 else 0.0
        vals.append(prefix - (float(r) / h) * total)
    arr = np.asarray(vals, dtype=float)
    energy = float(np.sum(arr * arr))
    peak_idx = int(np.argmax(np.abs(arr)))
    return {
        "bridge_peak_offset": float(samples[peak_idx]),
        "bridge_peak_u": float(samples[peak_idx] / h),
        "bridge_peak_value": float(arr[peak_idx]),
        "bridge_energy_concentration": float((arr[peak_idx] ** 2) / energy) if energy else np.nan,
    }


def read_inputs() -> dict[str, pd.DataFrame]:
    missing = [name for name in FILES.values() if not (BASE / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing required input files: {missing}")
    return {key: pd.read_csv(BASE / name, low_memory=False) for key, name in FILES.items()}


def build_rows(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pnt = dfs["pnt"].copy()
    coupling = dfs["coupling"].copy()
    kernel = dfs["kernel"].copy()
    tj = dfs["tj"].copy()

    # Work from RayleighCoupling because it has full offsets/weights and canonical K=rho*W columns.
    base = coupling[(coupling["W"] > W_THRESHOLD) & (coupling["post_P0_flag"].apply(norm_bool))].copy()
    base = base.merge(
        pnt[["candidate_id", "S_T", "K_over_logpstar_ST", "PNT_prediction", "pnt_density_ratio"]].rename(
            columns={
                "S_T": "S_T_pnt",
                "K_over_logpstar_ST": "C_cluster_pnt",
                "PNT_prediction": "PNT_prediction_pnt",
                "pnt_density_ratio": "pnt_density_ratio_pnt",
            }
        ),
        on="candidate_id",
        how="left",
    )
    kernel_cols = [
        "candidate_id",
        "top_eigenvector_alignment",
        "event_weight_effective_support",
        "weight_concentration",
        "effective_rank",
    ]
    base = base.merge(kernel[[c for c in kernel_cols if c in kernel.columns]], on="candidate_id", how="left")
    tj_cols = [
        "candidate_id",
        "sample_count_over_h",
        "sample_offset_gaps_max",
        "grid_origin_rule",
        "offset_gap_pattern",
    ]
    base = base.merge(tj[[c for c in tj_cols if c in tj.columns]], on="candidate_id", how="left")

    records: list[dict[str, object]] = []
    for _, row in base.iterrows():
        candidate_id = str(row["candidate_id"])
        y = int(row["y"])
        h = int(row["h"])
        p_star = int(row["p_star"])
        sample_offsets = parse_int_list(row.get("R_offsets", ""))
        event_offsets = parse_int_list(row.get("event_offsets", ""))
        weights = parse_num_list(row.get("weights", ""))
        prime_offsets, prime_weights = classify_prime_offsets(y, event_offsets, weights)

        S_T = sample_variance_sum(sample_offsets, h)
        log_p_star = math.log(p_star)
        K_prime = safe_float(row, "K")
        W = safe_float(row, "W")
        rho = safe_float(row, "rho")
        PNT_prediction = log_p_star * S_T
        C_cluster = K_prime / PNT_prediction if PNT_prediction else np.nan
        k = len(prime_offsets)

        rec: dict[str, object] = {
            "candidate_id": candidate_id,
            "candidate_num": int(candidate_id.split("_")[-1]) if "_" in candidate_id else np.nan,
            "block_id": int(row["block_id"]),
            "x": int(row["x"]),
            "y": y,
            "h": h,
            "p_star": p_star,
            "log_p_star": log_p_star,
            "post_P0_by_pstar": p_star >= P0,
            "post_P0_flag": norm_bool(row["post_P0_flag"]),
            "W": W,
            "rho": rho,
            "K_prime": K_prime,
            "margin_to_65": K_CAP - K_prime,
            "S_T": S_T,
            "S_T_pnt": safe_float(row, "S_T_pnt"),
            "PNT_prediction": PNT_prediction,
            "PNT_prediction_pnt": safe_float(row, "PNT_prediction_pnt"),
            "C_cluster": C_cluster,
            "C_cluster_pnt": safe_float(row, "C_cluster_pnt"),
            "C_cluster_margin_to_1": 1.0 - C_cluster,
            "C_cluster_margin_to_1p05": 1.05 - C_cluster,
            "C_cluster_margin_to_1p10": 1.10 - C_cluster,
            "C_cluster_margin_to_1p12": 1.12 - C_cluster,
            "k_prime_count": k,
            "prime_event_count_source": int(row["prime_event_count"]),
            "prime_event_count_match": k == int(row["prime_event_count"]),
            "k_over_h": k / h if h else np.nan,
            "pnt_density_ratio": (k / h) * log_p_star if h else np.nan,
            "pnt_density_ratio_pnt": safe_float(row, "pnt_density_ratio_pnt"),
            "sample_count": int(row["sample_count"]),
            "sample_count_over_h": safe_float(row, "sample_count_over_h", int(row["sample_count"]) / h if h else np.nan),
            "sample_gap_max": safe_float(row, "sample_offset_gaps_max"),
            "grid_pattern_id": str(row.get("grid_origin_rule", "")),
            "prime_offsets": ",".join(str(x) for x in prime_offsets),
            "sample_offsets_summary": f"n={len(sample_offsets)} min={min(sample_offsets) if sample_offsets else ''} max={max(sample_offsets) if sample_offsets else ''}",
            "prime_offsets_summary": f"n={len(prime_offsets)} min={min(prime_offsets) if prime_offsets else ''} max={max(prime_offsets) if prime_offsets else ''}",
            "top_eigenvector_alignment": safe_float(row, "top_eigenvector_alignment"),
            "weight_concentration": safe_float(row, "weight_concentration"),
            "effective_support": safe_float(row, "event_weight_effective_support"),
            "effective_rank": safe_float(row, "effective_rank"),
            "anomalous_flag": C_cluster > 1.0,
            "near_miss_flag": K_prime > 60.0,
            "short_block_flag": h < 1000,
            "exceeds_cap_flag": K_prime > K_CAP,
            "clusterfactor_failure_flag": K_prime > K_CAP,
        }
        rec.update(prime_distribution_metrics(prime_offsets, h))
        rec.update(prefixed_metrics("sample", sample_offsets, h))
        rec.update(bridge_metrics(sample_offsets, h, prime_offsets, prime_weights))
        records.append(rec)

    return pd.DataFrame.from_records(records).sort_values(["K_prime"], ascending=False)


def regime_summary(rows: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    group_defs = {
        "short_block_flag": rows["short_block_flag"],
        "anomalous_flag": rows["anomalous_flag"],
        "near_miss_flag": rows["near_miss_flag"],
        "C_cluster_bin": pd.cut(rows["C_cluster"], [-np.inf, 0.5, 0.8, 1.0, 1.05, 1.10, 1.12, np.inf]),
        "h_bin": pd.cut(rows["h"], [-np.inf, 500, 800, 1000, 1500, 2000, np.inf]),
        "KS_bin": pd.cut(rows["KS_stat_uniform"], [-np.inf, 0.15, 0.25, 0.35, 0.5, np.inf]),
        "u_mean_bin": pd.cut(rows["prime_u_mean"], [-np.inf, 0.2, 0.25, 0.35, 0.5, np.inf]),
    }
    for group_name, group_values in group_defs.items():
        tmp = rows.copy()
        tmp[group_name] = group_values.astype(str)
        agg = tmp.groupby(group_name, dropna=False).agg(
            rows=("candidate_id", "count"),
            K_max=("K_prime", "max"),
            C_cluster_max=("C_cluster", "max"),
            S_T_max=("S_T", "max"),
            C_cluster_times_ST_max=("C_cluster_times_ST", "max"),
            h_min=("h", "min"),
            h_max=("h", "max"),
            u_mean_mean=("prime_u_mean", "mean"),
            KS_max=("KS_stat_uniform", "max"),
            left_mass_frac_max=("prime_left_mass_frac", "max"),
            failures=("clusterfactor_failure_flag", "sum"),
        )
        agg = agg.reset_index().rename(columns={group_name: "regime_value"})
        agg.insert(0, "regime_field", group_name)
        frames.append(agg)
    return pd.concat(frames, ignore_index=True)


def extremes(rows: pd.DataFrame) -> pd.DataFrame:
    items = [
        ("max_K_prime", rows["K_prime"].idxmax()),
        ("max_C_cluster", rows["C_cluster"].idxmax()),
        ("max_C_cluster_times_ST", rows["C_cluster_times_ST"].idxmax()),
        ("max_KS_stat", rows["KS_stat_uniform"].idxmax()),
        ("min_u_mean", rows["prime_u_mean"].idxmin()),
        ("max_left_mass_frac", rows["prime_left_mass_frac"].idxmax()),
        ("max_bridge_peak_abs", rows["bridge_peak_value"].abs().idxmax()),
        ("max_S_T", rows["S_T"].idxmax()),
    ]
    cols = [
        "candidate_id",
        "h",
        "k_prime_count",
        "p_star",
        "K_prime",
        "rho",
        "W",
        "S_T",
        "C_cluster",
        "PNT_prediction",
        "prime_u_mean",
        "prime_u_std",
        "KS_stat_uniform",
        "prime_left_mass_frac",
        "bridge_peak_u",
        "bridge_peak_value",
        "sample_offsets_summary",
        "prime_offsets_summary",
    ]
    recs = []
    for label, idx in items:
        rec = {"extreme_type": label}
        rec.update(rows.loc[idx, cols].to_dict())
        recs.append(rec)
    return pd.DataFrame(recs)


def threshold_table(rows: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for threshold in [500, 800, 1000, 1500, 2000]:
        inside = rows[rows["h"] < threshold]
        outside = rows[rows["h"] >= threshold]
        recs.append(
            {
                "test": f"h < {threshold}",
                "rows_inside": len(inside),
                "C_cluster_max_inside": inside["C_cluster"].max() if len(inside) else np.nan,
                "C_cluster_max_outside": outside["C_cluster"].max() if len(outside) else np.nan,
                "K_max_inside": inside["K_prime"].max() if len(inside) else np.nan,
                "K_max_outside": outside["K_prime"].max() if len(outside) else np.nan,
            }
        )
    return pd.DataFrame(recs)


def choose_recommendation(rows: pd.DataFrame) -> tuple[str, str, str]:
    exceptions = rows[rows["C_cluster"] > 1.0]
    near = rows[rows["K_prime"] > 55.0]
    all_exceptions_short = len(exceptions) > 0 and bool((exceptions["h"] < 1000).all())
    few_exceptions = len(exceptions) <= 3
    if all_exceptions_short and few_exceptions:
        return (
            "short_block_cluster_lemma",
            "All C_cluster>1 rows are few and have h<1000; the binding rows are short-block cases. The left-skew signal is strongest in the sampled grid rather than the reconstructed prime-event offsets.",
            "Prime_Mesh_R2Q_HExc_HighWeightRayleighCollapse_ShortBlockCluster_Theorem_Target_v1.md",
        )
    if few_exceptions and len(near) <= 5:
        return (
            "finite_high_cluster_certificate",
            "High-cluster/near-miss rows are sparse enough for a certificate-style finite family.",
            "Prime_Mesh_R2Q_HExc_HighWeightRayleighCollapse_FiniteClusterCertificate_Target_v1.md",
        )
    return (
        "direct_highweight_product",
        "Cluster structure does not isolate cleanly enough; retain the coupled product theorem form.",
        "Prime_Mesh_R2Q_HExc_PrimeShockBridge_HighWeightProduct_Theorem_Target_v1.md",
    )


def summary(rows: pd.DataFrame) -> pd.DataFrame:
    rows = rows.copy()
    max_k = rows.loc[rows["K_prime"].idxmax()]
    exceptions = rows[rows["C_cluster"] > 1.0]
    theorem, reason, next_file = choose_recommendation(rows)
    best_threshold = 1000 if len(exceptions) and bool((exceptions["h"] < 1000).all()) else np.nan
    data = {
        "rows": len(rows),
        "K_prime_max": rows["K_prime"].max(),
        "K_prime_above_65_count": int((rows["K_prime"] > K_CAP).sum()),
        "margin_to_65_min": rows["margin_to_65"].min(),
        "pass_highweight_K_cap": bool((rows["K_prime"] <= K_CAP).all()),
        "C_cluster_min": rows["C_cluster"].min(),
        "C_cluster_median": rows["C_cluster"].median(),
        "C_cluster_q95": percentile(rows["C_cluster"], 95),
        "C_cluster_max": rows["C_cluster"].max(),
        "C_cluster_above_1_count": int((rows["C_cluster"] > 1.0).sum()),
        "C_cluster_above_1p05_count": int((rows["C_cluster"] > 1.05).sum()),
        "C_cluster_above_1p10_count": int((rows["C_cluster"] > 1.10).sum()),
        "C_cluster_above_1p12_count": int((rows["C_cluster"] > 1.12).sum()),
        "pass_C_cluster_le_1p12": bool((rows["C_cluster"] <= 1.12).all()),
        "S_T_min": rows["S_T"].min(),
        "S_T_median": rows["S_T"].median(),
        "S_T_max": rows["S_T"].max(),
        "C_cluster_times_ST_max": rows["C_cluster_times_ST"].max(),
        "maxK_candidate_id": max_k["candidate_id"],
        "maxK_h": int(max_k["h"]),
        "maxK_k": int(max_k["k_prime_count"]),
        "maxK_C_cluster": max_k["C_cluster"],
        "maxK_S_T": max_k["S_T"],
        "maxK_u_mean": max_k["prime_u_mean"],
        "maxK_sample_u_mean": max_k["sample_u_mean"],
        "maxK_KS_stat": max_k["KS_stat_uniform"],
        "maxK_sample_KS_stat": max_k["sample_KS_stat_uniform"],
        "maxK_left_mass_frac": max_k["prime_left_mass_frac"],
        "maxK_sample_left_mass_frac": max_k["sample_left_mass_frac"],
        "corr_C_cluster_KS_stat": corr(rows["C_cluster"], rows["KS_stat_uniform"]),
        "corr_C_cluster_KS_stat_spearman": corr(rows["C_cluster"], rows["KS_stat_uniform"], "spearman"),
        "corr_C_cluster_u_mean": corr(rows["C_cluster"], rows["prime_u_mean"]),
        "corr_C_cluster_u_mean_spearman": corr(rows["C_cluster"], rows["prime_u_mean"], "spearman"),
        "corr_C_cluster_sample_KS_stat": corr(rows["C_cluster"], rows["sample_KS_stat_uniform"]),
        "corr_C_cluster_sample_u_mean": corr(rows["C_cluster"], rows["sample_u_mean"]),
        "corr_C_cluster_sample_left_mass_frac": corr(rows["C_cluster"], rows["sample_left_mass_frac"]),
        "corr_C_cluster_abs_u_mean_minus_0p5": corr(rows["C_cluster"], (rows["prime_u_mean"] - 0.5).abs()),
        "corr_C_cluster_left_mass_frac": corr(rows["C_cluster"], rows["prime_left_mass_frac"]),
        "corr_C_cluster_right_mass_frac": corr(rows["C_cluster"], rows["prime_right_mass_frac"]),
        "corr_C_cluster_event_gap_cv": corr(rows["C_cluster"], rows["event_gap_cv"]),
        "corr_C_cluster_h": corr(rows["C_cluster"], rows["h"]),
        "corr_C_cluster_k": corr(rows["C_cluster"], rows["k_prime_count"]),
        "corr_C_cluster_S_T": corr(rows["C_cluster"], rows["S_T"]),
        "corr_C_cluster_sample_count": corr(rows["C_cluster"], rows["sample_count"]),
        "short_block_threshold_best": best_threshold,
        "cluster_exception_count": len(exceptions),
        "cluster_exception_candidate_ids": ",".join(exceptions["candidate_id"].astype(str).tolist()),
        "cluster_exception_h_max": exceptions["h"].max() if len(exceptions) else np.nan,
        "cluster_exception_pstar_range": f"{exceptions['p_star'].min()}..{exceptions['p_star'].max()}" if len(exceptions) else "",
        "recommended_exception_handling": theorem,
        "best_clusterfactor_theorem_form": theorem,
        "best_clusterfactor_theorem_reason": reason,
        "clusterfactor_failures": int(rows["clusterfactor_failure_flag"].sum()),
        "pass_hexc_highweight_clusterfactor_empirical": bool((rows["K_prime"] <= K_CAP).all()),
        "recommended_next_file": next_file,
    }
    return pd.DataFrame([data])


def write_doc(rows: pd.DataFrame, summ: pd.DataFrame, regimes: pd.DataFrame, extremes_df: pd.DataFrame) -> None:
    s = summ.iloc[0]
    top = rows.sort_values("K_prime", ascending=False).head(6)
    exceptions = rows[(rows["C_cluster"] > 1.0) | (rows["K_prime"] > 55.0)].sort_values("K_prime", ascending=False)
    threshold = threshold_table(rows)
    lines = [
        "# Prime Mesh R2Q — H-Exc HighWeightRayleighCollapse ClusterFactor Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "This audit analyzes only the sampled-grid bridge energy on `T_J`. It does not assert or use a full-grid lifting theorem.",
        "",
        "Target regime:",
        "",
        "```text",
        "post_P0_flag = True, W > 1040",
        "K_prime = rho * W <= 65",
        "C_cluster = K_prime / (log(p_star) * S_T)",
        "```",
        "",
        "## 2. Summary",
        "",
        f"- Rows: `{int(s['rows'])}`.",
        f"- `K_prime_max = {s['K_prime_max']:.12g}` with margin `{s['margin_to_65_min']:.12g}`.",
        f"- `K_prime_above_65_count = {int(s['K_prime_above_65_count'])}`.",
        f"- `C_cluster_median = {s['C_cluster_median']:.12g}`, `C_cluster_max = {s['C_cluster_max']:.12g}`.",
        f"- `C_cluster > 1`: `{int(s['C_cluster_above_1_count'])}` rows; `>1.05`: `{int(s['C_cluster_above_1p05_count'])}`; `>1.10`: `{int(s['C_cluster_above_1p10_count'])}`; `>1.12`: `{int(s['C_cluster_above_1p12_count'])}`.",
        f"- Empirical pass: `{bool(s['pass_hexc_highweight_clusterfactor_empirical'])}`.",
        "",
        "## 3. Binding Rows",
        "",
        "| candidate | h | k | K_prime | C_cluster | S_T | prime_u_mean | sample_u_mean | sample_left_mass |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in top.iterrows():
        lines.append(
            f"| {r['candidate_id']} | {int(r['h'])} | {int(r['k_prime_count'])} | "
            f"{r['K_prime']:.8g} | {r['C_cluster']:.8g} | {r['S_T']:.8g} | "
            f"{r['prime_u_mean']:.8g} | {r['sample_u_mean']:.8g} | {r['sample_left_mass_frac']:.8g} |"
        )
    lines += [
        "",
        "## 4. Exception Family",
        "",
        f"`C_cluster > 1` rows: `{s['cluster_exception_candidate_ids']}`.",
        "",
        "| candidate | h | K_prime | C_cluster | prime_u_mean | sample_u_mean | sample_left_mass | bridge_peak_u |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in exceptions.iterrows():
        lines.append(
            f"| {r['candidate_id']} | {int(r['h'])} | {r['K_prime']:.8g} | {r['C_cluster']:.8g} | "
            f"{r['prime_u_mean']:.8g} | {r['sample_u_mean']:.8g} | "
            f"{r['sample_left_mass_frac']:.8g} | {r['bridge_peak_u']:.8g} |"
        )
    lines += [
        "",
        "## 5. Correlations",
        "",
        "| metric | Pearson | Spearman |",
        "|---|---:|---:|",
        f"| KS statistic | {s['corr_C_cluster_KS_stat']:.8g} | {s['corr_C_cluster_KS_stat_spearman']:.8g} |",
        f"| u_mean | {s['corr_C_cluster_u_mean']:.8g} | {s['corr_C_cluster_u_mean_spearman']:.8g} |",
        f"| left_mass_frac | {s['corr_C_cluster_left_mass_frac']:.8g} |  |",
        f"| sample_u_mean | {s['corr_C_cluster_sample_u_mean']:.8g} |  |",
        f"| sample_left_mass_frac | {s['corr_C_cluster_sample_left_mass_frac']:.8g} |  |",
        f"| h | {s['corr_C_cluster_h']:.8g} |  |",
        f"| S_T | {s['corr_C_cluster_S_T']:.8g} |  |",
        "",
        "## 6. Short-Block Isolation",
        "",
        "| threshold | rows_inside | Cmax_inside | Cmax_outside | Kmax_inside | Kmax_outside |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, r in threshold.iterrows():
        lines.append(
            f"| {r['test']} | {int(r['rows_inside'])} | {r['C_cluster_max_inside']:.8g} | "
            f"{r['C_cluster_max_outside']:.8g} | {r['K_max_inside']:.8g} | {r['K_max_outside']:.8g} |"
        )
    lines += [
        "",
        "## 7. Recommended Theorem Form",
        "",
        f"`{s['best_clusterfactor_theorem_form']}`.",
        "",
        s["best_clusterfactor_theorem_reason"],
        "",
        f"Recommended next file: `{s['recommended_next_file']}`.",
        "",
        "## 8. Outputs",
        "",
        "```text",
        OUT_SCRIPT,
        OUT_SUMMARY,
        OUT_ROWS,
        OUT_BY_REGIME,
        OUT_EXTREMES,
        OUT_FAILURES,
        OUT_COMPARE,
        OUT_EXCEPTIONS,
        "```",
        "",
        "*AI documentation pass: GPT-5.5*",
    ]
    (BASE / OUT_DOC).write_text("\n".join(lines), encoding="utf-8")


def update_manifest(filenames: list[str]) -> None:
    path = BASE / OUT_MANIFEST
    now = datetime.now().isoformat(timespec="seconds")
    rows = []
    if path.exists():
        rows = pd.read_csv(path).to_dict("records")
    keep = [r for r in rows if r.get("filename") not in set(filenames)]
    for name in filenames:
        p = BASE / name
        keep.append(
            {
                "filename": name,
                "path": str(p),
                "bytes": p.stat().st_size if p.exists() else 0,
                "status": "new",
                "updated_at": now,
                "note": "H-Exc HighWeightRayleighCollapse ClusterFactor audit output",
            }
        )
    pd.DataFrame(keep).to_csv(path, index=False)


def main() -> None:
    dfs = read_inputs()
    rows = build_rows(dfs)
    rows["C_cluster_times_ST"] = rows["C_cluster"] * rows["S_T"]

    summ = summary(rows)
    regimes = regime_summary(rows)
    ext = extremes(rows)
    failures = rows[rows["clusterfactor_failure_flag"]].copy()
    compare = rows[rows["candidate_num"].isin([453, 442])].sort_values("candidate_num")
    exceptions = rows[(rows["C_cluster"] > 1.0) | (rows["K_prime"] > 55.0)].sort_values("K_prime", ascending=False)

    rows.to_csv(BASE / OUT_ROWS, index=False)
    summ.to_csv(BASE / OUT_SUMMARY, index=False)
    regimes.to_csv(BASE / OUT_BY_REGIME, index=False)
    ext.to_csv(BASE / OUT_EXTREMES, index=False)
    failures.to_csv(BASE / OUT_FAILURES, index=False)
    compare.to_csv(BASE / OUT_COMPARE, index=False)
    exceptions.to_csv(BASE / OUT_EXCEPTIONS, index=False)
    write_doc(rows, summ, regimes, ext)
    update_manifest(
        [
            OUT_SCRIPT,
            OUT_SUMMARY,
            OUT_ROWS,
            OUT_BY_REGIME,
            OUT_EXTREMES,
            OUT_FAILURES,
            OUT_COMPARE,
            OUT_EXCEPTIONS,
            OUT_DOC,
        ]
    )

    s = summ.iloc[0].to_dict()
    print("ClusterFactor audit complete.")
    for key in [
        "rows",
        "K_prime_max",
        "K_prime_above_65_count",
        "margin_to_65_min",
        "C_cluster_max",
        "C_cluster_above_1_count",
        "C_cluster_above_1p05_count",
        "C_cluster_above_1p10_count",
        "C_cluster_above_1p12_count",
        "cluster_exception_candidate_ids",
        "best_clusterfactor_theorem_form",
        "recommended_next_file",
    ]:
        print(f"{key}: {s[key]}")


if __name__ == "__main__":
    main()
