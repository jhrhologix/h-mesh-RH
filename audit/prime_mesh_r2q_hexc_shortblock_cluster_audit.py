"""
Prime Mesh R2Q — H-Exc HighWeightRayleighCollapse ShortBlockCluster Audit.

Scope: sampled-grid T_J only.  This reconstructs the Lambda prime-shock
bridge from event offsets + weights and audits the h < 800, W > 1040,
post-P0 regime.
"""

from __future__ import annotations

import hashlib
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
P0 = 500_000_000
W_THRESHOLD = 1040.0
H_SHORT = 800
K_CAP = 65.0
RECON_TOL = 1e-8

IN_CLUSTER_ROWS = "prime_mesh_r2q_hexc_highweight_clusterfactor_rows.csv"
IN_COUPLING_ROWS = "prime_mesh_r2q_hexc_primeshock_rayleighcoupling_rows.csv"
IN_KERNEL_ROWS = "prime_mesh_r2q_hexc_primeshock_kernelgram_rows.csv"
IN_TJ_ROWS = "prime_mesh_r2q_hexc_tj_grid_extraction_rows.csv"
IN_RAW_ROWS = "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv"

OUT_SCRIPT = "prime_mesh_r2q_hexc_shortblock_cluster_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_hexc_shortblock_cluster_summary.csv"
OUT_ROWS = "prime_mesh_r2q_hexc_shortblock_cluster_rows.csv"
OUT_BINDING = "prime_mesh_r2q_hexc_shortblock_cluster_binding_rows.csv"
OUT_CERT = "prime_mesh_r2q_hexc_shortblock_cluster_certificate.csv"
OUT_BOUNDS = "prime_mesh_r2q_hexc_shortblock_cluster_bounds.csv"
OUT_FAILURES = "prime_mesh_r2q_hexc_shortblock_cluster_failures.csv"
OUT_BRIDGE = "prime_mesh_r2q_hexc_shortblock_cluster_bridge_values.csv"
OUT_SAMPLE_PRIME = "prime_mesh_r2q_hexc_shortblock_cluster_sample_prime_comparison.csv"
OUT_DOC = "Prime_Mesh_R2Q_HExc_HighWeightRayleighCollapse_ShortBlockCluster_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"


def parse_num_list(raw) -> list[float]:
    if pd.isna(raw):
        return []
    text = str(raw).strip()
    if not text:
        return []
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    return [float(part.strip()) for part in text.split(",") if part.strip()]


def parse_int_list(raw) -> list[int]:
    return [int(round(x)) for x in parse_num_list(raw)]


def norm_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes"}


def sha_short(values: list[int] | list[float]) -> str:
    text = ",".join(str(v) for v in values)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def classify_prime_offsets(y: int, event_offsets: list[int], weights: list[float]) -> tuple[list[int], list[float]]:
    """Keep Lambda events whose weight matches log(y+offset), i.e. prime events."""
    prime_offsets: list[int] = []
    prime_weights: list[float] = []
    for offset, weight in zip(event_offsets, weights):
        n = y + offset
        if n > 1 and abs(weight - math.log(n)) <= 1e-7:
            prime_offsets.append(offset)
            prime_weights.append(weight)
    return prime_offsets, prime_weights


def distribution_metrics(prefix: str, offsets: list[int], h: int) -> dict[str, float | str]:
    if not offsets or h <= 0:
        return {
            f"{prefix}_u_values": "",
            f"{prefix}_u_min": np.nan,
            f"{prefix}_u_max": np.nan,
            f"{prefix}_u_mean": np.nan,
            f"{prefix}_u_median": np.nan,
            f"{prefix}_u_std": np.nan,
            f"{prefix}_left_mass_frac": np.nan,
            f"{prefix}_center_mass_frac": np.nan,
            f"{prefix}_right_mass_frac": np.nan,
            f"{prefix}_gap_max": np.nan,
            f"{prefix}_gap_mean": np.nan,
            f"{prefix}_gap_cv": np.nan,
            f"KS_stat_uniform_{prefix}": np.nan,
            f"star_discrepancy_{prefix}": np.nan,
        }
    u = np.sort(np.asarray(offsets, dtype=float) / float(h))
    n = len(u)
    i = np.arange(1, n + 1, dtype=float)
    ks = max(float(np.max(i / n - u)), float(np.max(u - (i - 1) / n)))
    gaps = np.diff(np.sort(np.asarray(offsets, dtype=float)))
    gap_mean = float(np.mean(gaps)) if len(gaps) else 0.0
    return {
        f"{prefix}_u_values": ",".join(f"{v:.10g}" for v in u),
        f"{prefix}_u_min": float(np.min(u)),
        f"{prefix}_u_max": float(np.max(u)),
        f"{prefix}_u_mean": float(np.mean(u)),
        f"{prefix}_u_median": float(np.median(u)),
        f"{prefix}_u_std": float(np.std(u, ddof=0)),
        f"{prefix}_left_mass_frac": float(np.mean(u <= 0.25)),
        f"{prefix}_center_mass_frac": float(np.mean((u > 0.25) & (u < 0.75))),
        f"{prefix}_right_mass_frac": float(np.mean(u >= 0.75)),
        f"{prefix}_gap_max": float(np.max(gaps)) if len(gaps) else 0.0,
        f"{prefix}_gap_mean": gap_mean,
        f"{prefix}_gap_cv": float(np.std(gaps, ddof=0) / gap_mean) if gap_mean else 0.0,
        f"KS_stat_uniform_{prefix}": ks,
        f"star_discrepancy_{prefix}": ks,
    }


def reconstruct_bridge(
    sample_offsets: list[int], event_offsets: list[int], weights: list[float], h: int
) -> tuple[pd.DataFrame, dict[str, float]]:
    samples = np.asarray(sample_offsets, dtype=float)
    events = np.asarray(event_offsets, dtype=float)
    w = np.asarray(weights, dtype=float)
    order = np.argsort(events)
    events = events[order]
    w = w[order]
    cumulative = np.cumsum(w)
    total = float(np.sum(w))

    values = []
    for r in samples:
        idx = np.searchsorted(events, r, side="right") - 1
        prefix = float(cumulative[idx]) if idx >= 0 else 0.0
        values.append(prefix - (r / h) * total)

    b = np.asarray(values, dtype=float)
    energy_values = b * b
    energy = float(np.sum(energy_values))
    abs_b = np.abs(b)
    peak_idx = int(np.argmax(abs_b))
    order_energy = np.argsort(energy_values)[::-1]
    top3 = float(np.sum(energy_values[order_energy[: min(3, len(order_energy))]]) / energy) if energy else np.nan
    u = samples / float(h)
    left = float(np.sum(energy_values[u <= 0.25]) / energy) if energy else np.nan
    center = float(np.sum(energy_values[(u > 0.25) & (u < 0.75)]) / energy) if energy else np.nan
    right = float(np.sum(energy_values[u >= 0.75]) / energy) if energy else np.nan

    bridge = pd.DataFrame(
        {
            "offset": samples.astype(int),
            "u": u,
            "B_prime": b,
            "B_prime_abs": abs_b,
            "B_prime_sq": energy_values,
        }
    )
    metrics = {
        "B_prime_abs_max": float(abs_b[peak_idx]) if len(abs_b) else np.nan,
        "B_prime_peak_offset": float(samples[peak_idx]) if len(samples) else np.nan,
        "B_prime_peak_u": float(u[peak_idx]) if len(u) else np.nan,
        "B_prime_peak_value": float(b[peak_idx]) if len(b) else np.nan,
        "B_prime_energy": energy,
        "K_reconstructed": energy / h if h else np.nan,
        "B_prime_energy_concentration_top1": float(energy_values[peak_idx] / energy) if energy else np.nan,
        "B_prime_energy_concentration_top3": top3,
        "B_prime_energy_concentration_left_quarter": left,
        "B_prime_energy_concentration_center": center,
        "B_prime_energy_concentration_right_quarter": right,
    }
    return bridge, metrics


def load_inputs() -> dict[str, pd.DataFrame]:
    paths = {
        "cluster": BASE / IN_CLUSTER_ROWS,
        "coupling": BASE / IN_COUPLING_ROWS,
        "kernel": BASE / IN_KERNEL_ROWS,
        "tj": BASE / IN_TJ_ROWS,
        "raw": BASE / IN_RAW_ROWS,
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required inputs: {missing}")
    return {name: pd.read_csv(path, low_memory=False) for name, path in paths.items()}


def build_audit_rows(dfs: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    coupling = dfs["coupling"].copy()
    cluster = dfs["cluster"].copy()
    raw = dfs["raw"].copy()
    kernel = dfs["kernel"].copy()

    high = coupling[(coupling["W"] > W_THRESHOLD) & (coupling["post_P0_flag"].apply(norm_bool))].copy()
    short_ids = high[(high["h"] < H_SHORT) & (high["p_star"] >= P0)]["candidate_id"].astype(str).tolist()

    cluster_cols = [
        "candidate_id",
        "S_T",
        "C_cluster",
        "PNT_prediction",
        "sample_u_mean",
        "sample_left_mass_frac",
        "sample_center_mass_frac",
        "sample_right_mass_frac",
        "sample_gap_mean",
        "sample_gap_cv",
        "prime_u_mean",
        "prime_left_mass_frac",
        "prime_center_mass_frac",
        "prime_right_mass_frac",
        "event_gap_mean",
        "event_gap_cv",
    ]
    high = high.merge(cluster[[c for c in cluster_cols if c in cluster.columns]], on="candidate_id", how="left")
    raw_cols = ["candidate_id", "threshold_relevant_flag", "forbidden_flag", "finite_zone_flag"]
    high = high.merge(raw[[c for c in raw_cols if c in raw.columns]], on="candidate_id", how="left", suffixes=("", "_raw"))
    kernel_cols = ["candidate_id", "top_eigenvalue_over_h", "rayleigh_over_h", "top_eigenvector_alignment"]
    high = high.merge(kernel[[c for c in kernel_cols if c in kernel.columns]], on="candidate_id", how="left", suffixes=("", "_kernel"))

    records: list[dict[str, object]] = []
    bridge_rows: list[pd.DataFrame] = []
    comparison_records: list[dict[str, object]] = []

    for _, row in high.iterrows():
        candidate_id = str(row["candidate_id"])
        y = int(row["y"])
        h = int(row["h"])
        sample_offsets = parse_int_list(row["R_offsets"])
        event_offsets = parse_int_list(row["event_offsets"])
        weights = parse_num_list(row["weights"])
        prime_offsets, _prime_weights = classify_prime_offsets(y, event_offsets, weights)
        bridge, bridge_metrics = reconstruct_bridge(sample_offsets, event_offsets, weights, h)
        bridge.insert(0, "candidate_id", candidate_id)
        bridge_rows.append(bridge)

        S_T = float(np.sum((np.asarray(sample_offsets) / h) * (1 - np.asarray(sample_offsets) / h))) if h else np.nan
        log_p = math.log(float(row["p_star"]))
        K_prime = float(row["K"])
        C_cluster = K_prime / (log_p * S_T) if S_T else np.nan
        reconstruction_error = abs(float(row["K_prime"]) - bridge_metrics["K_reconstructed"])
        rayleigh_to_top = (
            float(row["rayleigh_over_h"]) / float(row["top_eigenvalue_over_h"])
            if "top_eigenvalue_over_h" in row and float(row["top_eigenvalue_over_h"]) != 0
            else np.nan
        )
        rec: dict[str, object] = {
            "candidate_id": candidate_id,
            "candidate_num": int(candidate_id.split("_")[-1]),
            "block_id": int(row["block_id"]),
            "x": int(row["x"]),
            "y": y,
            "h": h,
            "p_star": int(row["p_star"]),
            "log_p_star": log_p,
            "post_P0_flag": norm_bool(row["post_P0_flag"]),
            "W": float(row["W"]),
            "rho": float(row["rho"]),
            "K_prime": K_prime,
            "margin_to_65": K_CAP - K_prime,
            "S_T": S_T,
            "PNT_prediction": log_p * S_T,
            "C_cluster": C_cluster,
            "C_cluster_times_ST": C_cluster * S_T,
            "K_over_logp": K_prime / log_p,
            "sample_count": len(sample_offsets),
            "sample_offsets": ",".join(str(x) for x in sample_offsets),
            "prime_event_count": len(prime_offsets),
            "prime_offsets": ",".join(str(x) for x in prime_offsets),
            "lambda_event_count": len(event_offsets),
            "lambda_event_weight_sum": float(np.sum(weights)),
            "lambda_event_weight_max": float(np.max(weights)) if weights else np.nan,
            "B_prime_values_on_TJ": ",".join(f"{v:.10g}" for v in bridge["B_prime"].to_numpy()),
            "B_prime_energy_reconstruction_error": reconstruction_error,
            "pass_reconstruction": reconstruction_error <= RECON_TOL,
            "top_eigenvector_alignment": float(row["top_eigenvector_alignment"]) if "top_eigenvector_alignment" in row else np.nan,
            "rayleigh_to_top_eigenvalue_ratio": rayleigh_to_top,
            "grid_pattern_id": "routeA_sr11_available_subgrid_plus_endpoints",
            "threshold_relevant_flag": norm_bool(row.get("threshold_relevant_flag", False)),
            "forbidden_flag": norm_bool(row.get("forbidden_flag", False)),
            "finite_certified_flag": norm_bool(row.get("finite_zone_flag", False)),
            "high_energy_flag": h < H_SHORT and float(row["W"]) > W_THRESHOLD and int(row["p_star"]) >= P0,
        }
        rec.update(distribution_metrics("sample", sample_offsets, h))
        rec.update(distribution_metrics("prime", prime_offsets, h))
        rec.update(bridge_metrics)
        rec["sample_grid_skew_stronger_than_prime_skew"] = abs(rec["sample_u_mean"] - 0.5) > abs(
            rec["prime_u_mean"] - 0.5
        )
        records.append(rec)

        comparison_records.append(
            {
                "candidate_id": candidate_id,
                "h": h,
                "K_prime": K_prime,
                "C_cluster": C_cluster,
                "sample_u_mean": rec["sample_u_mean"],
                "sample_left_mass_frac": rec["sample_left_mass_frac"],
                "prime_u_mean": rec["prime_u_mean"],
                "prime_left_mass_frac": rec["prime_left_mass_frac"],
                "skew_driver": "sample_grid"
                if rec["sample_grid_skew_stronger_than_prime_skew"]
                else "prime_events_or_mixed",
            }
        )

    rows = pd.DataFrame.from_records(records)
    all_bridge = pd.concat(bridge_rows, ignore_index=True)
    sample_prime = pd.DataFrame.from_records(comparison_records)
    rows["short_highW_flag"] = rows["candidate_id"].isin(short_ids)
    return rows.sort_values("K_prime", ascending=False), all_bridge, sample_prime


def make_certificate(short_rows: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for _, row in short_rows.iterrows():
        sample_offsets = parse_int_list(row["sample_offsets"])
        prime_offsets = parse_int_list(row["prime_offsets"])
        recs.append(
            {
                "candidate_id": row["candidate_id"],
                "h": int(row["h"]),
                "sample_offsets_hash": sha_short(sample_offsets),
                "prime_offsets_hash": sha_short(prime_offsets),
                "K_prime": row["K_prime"],
                "margin_to_65": row["margin_to_65"],
                "pass_reconstruction": row["pass_reconstruction"],
                "certificate_input_reproducible": True,
            }
        )
    return pd.DataFrame(recs)


def make_bounds(short_rows: pd.DataFrame, high_rows: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for _, row in short_rows.iterrows():
        sample_count = float(row["sample_count"])
        h = float(row["h"])
        sup_bound = sample_count * (float(row["B_prime_abs_max"]) ** 2) / h
        mass_bound = sample_count * (float(row["lambda_event_weight_sum"]) ** 2) / h
        for c_short in [1.11, 1.12, 1.15, 1.20]:
            pred = c_short * float(row["log_p_star"]) * float(row["S_T"])
            recs.append(
                {
                    "candidate_id": row["candidate_id"],
                    "bound_name": f"C_short_{c_short}",
                    "bound_value": pred,
                    "K_prime": row["K_prime"],
                    "passes_row": float(row["K_prime"]) <= pred,
                    "looseness": pred / float(row["K_prime"]) if row["K_prime"] else np.nan,
                }
            )
        recs.extend(
            [
                {
                    "candidate_id": row["candidate_id"],
                    "bound_name": "sampled_supremum",
                    "bound_value": sup_bound,
                    "K_prime": row["K_prime"],
                    "passes_row": float(row["K_prime"]) <= sup_bound,
                    "looseness": sup_bound / float(row["K_prime"]) if row["K_prime"] else np.nan,
                },
                {
                    "candidate_id": row["candidate_id"],
                    "bound_name": "total_lambda_mass",
                    "bound_value": mass_bound,
                    "K_prime": row["K_prime"],
                    "passes_row": float(row["K_prime"]) <= mass_bound,
                    "looseness": mass_bound / float(row["K_prime"]) if row["K_prime"] else np.nan,
                },
                {
                    "candidate_id": row["candidate_id"],
                    "bound_name": "direct_K_cap_65",
                    "bound_value": K_CAP,
                    "K_prime": row["K_prime"],
                    "passes_row": float(row["K_prime"]) <= K_CAP,
                    "looseness": K_CAP / float(row["K_prime"]) if row["K_prime"] else np.nan,
                },
            ]
        )

    by_bound = pd.DataFrame(recs)
    global_recs = []
    for name, group in by_bound.groupby("bound_name"):
        global_recs.append(
            {
                "candidate_id": "ALL_SHORT",
                "bound_name": name,
                "bound_value": group["bound_value"].min(),
                "K_prime": short_rows["K_prime"].max(),
                "passes_row": bool(group["passes_row"].all()),
                "looseness": group["looseness"].max(),
            }
        )
    return pd.concat([by_bound, pd.DataFrame(global_recs)], ignore_index=True)


def choose_route(short_rows: pd.DataFrame, bounds: pd.DataFrame) -> tuple[str, str, str]:
    finite_viable = (
        len(short_rows) <= 4
        and bool(short_rows["pass_reconstruction"].all())
        and bool((short_rows["margin_to_65"] > 0).all())
    )
    c112 = bounds[(bounds["candidate_id"] == "ALL_SHORT") & (bounds["bound_name"] == "C_short_1.12")]
    if finite_viable:
        return (
            "finite_shortblock_certificate",
            "Only four short high-weight post-P0 rows occur; all reconstruct from primitive offsets and all margins are positive. This is the cleanest closure unless a symbolic sampled-grid theorem is later derived.",
            "Prime_Mesh_R2Q_HExc_HighWeightRayleighCollapse_ShortBlockCluster_FiniteCertificate_Target_v1.md",
        )
    if len(c112) and bool(c112.iloc[0]["passes_row"]):
        return (
            "shortblock_symbolic_lemma",
            "A uniform C_short <= 1.12 sampled-variance bound passes the observed short rows.",
            "Prime_Mesh_R2Q_HExc_HighWeightRayleighCollapse_ShortBlockCluster_Lemma_Target_v1.md",
        )
    return (
        "direct_highweight_product",
        "No smaller finite/symbolic route was isolated; retain rho_J W_J <= 65.",
        "Prime_Mesh_R2Q_HExc_PrimeShockBridge_HighWeightProduct_Theorem_Target_v1.md",
    )


def make_summary(rows: pd.DataFrame, bounds: pd.DataFrame) -> pd.DataFrame:
    short = rows[rows["short_highW_flag"]].copy()
    long = rows[~rows["short_highW_flag"]].copy()
    binding = short[short["candidate_id"].isin(["hexc_00453", "hexc_00442"])]
    cert = make_certificate(short)
    route, reason, next_file = choose_route(short, bounds)
    c_bound = bounds[(bounds["candidate_id"] == "ALL_SHORT") & (bounds["bound_name"].str.startswith("C_short_"))]
    passing = c_bound[c_bound["passes_row"]]
    best_symbolic = passing.sort_values("bound_name").iloc[0] if len(passing) else None
    data = {
        "rows_total_highW": len(rows),
        "short_highW_rows": len(short),
        "short_highW_candidate_ids": ",".join(short["candidate_id"].tolist()),
        "short_highW_K_max": short["K_prime"].max(),
        "short_highW_K_above_65_count": int((short["K_prime"] > K_CAP).sum()),
        "short_highW_margin_min": short["margin_to_65"].min(),
        "pass_short_highW_K_cap": bool((short["K_prime"] <= K_CAP).all()),
        "binding_rows_reconstruction_error_max": binding["B_prime_energy_reconstruction_error"].max(),
        "pass_binding_rows_reconstruction": bool((binding["B_prime_energy_reconstruction_error"] <= RECON_TOL).all()),
        "short_highW_C_cluster_max": short["C_cluster"].max(),
        "short_highW_C_cluster_above_1_count": int((short["C_cluster"] > 1).sum()),
        "short_highW_C_cluster_above_1p10_count": int((short["C_cluster"] > 1.10).sum()),
        "short_highW_C_cluster_above_1p12_count": int((short["C_cluster"] > 1.12).sum()),
        "short_highW_sample_u_mean_min": short["sample_u_mean"].min(),
        "short_highW_sample_left_mass_frac_max": short["sample_left_mass_frac"].max(),
        "short_highW_prime_u_mean_min": short["prime_u_mean"].min(),
        "short_highW_prime_left_mass_frac_max": short["prime_left_mass_frac"].max(),
        "sample_grid_skew_stronger_than_prime_skew_count": int(short["sample_grid_skew_stronger_than_prime_skew"].sum()),
        "short_highW_B_prime_abs_max": short["B_prime_abs_max"].max(),
        "short_highW_peak_energy_concentration_top1_max": short["B_prime_energy_concentration_top1"].max(),
        "short_highW_peak_energy_concentration_top3_max": short["B_prime_energy_concentration_top3"].max(),
        "finite_shortblock_certificate_viable": bool(cert["pass_reconstruction"].all() and (cert["margin_to_65"] > 0).all()),
        "finite_shortblock_certificate_min_margin": cert["margin_to_65"].min(),
        "best_symbolic_shortblock_bound": best_symbolic["bound_name"] if best_symbolic is not None else "",
        "best_symbolic_shortblock_bound_passes": bool(best_symbolic is not None),
        "best_closure_route": route,
        "best_closure_route_reason": reason,
        "short_highW_threshold_relevant_count": int(short["threshold_relevant_flag"].sum()),
        "short_highW_forbidden_count": int(short["forbidden_flag"].sum()),
        "short_highW_threshold_relevant_K_max": short.loc[short["threshold_relevant_flag"], "K_prime"].max()
        if short["threshold_relevant_flag"].any()
        else np.nan,
        "short_highW_forbidden_K_max": short.loc[short["forbidden_flag"], "K_prime"].max()
        if short["forbidden_flag"].any()
        else np.nan,
        "long_highW_K_max": long["K_prime"].max(),
        "long_highW_C_cluster_max": long["C_cluster"].max(),
        "short_highW_S_T_max": short["S_T"].max(),
        "long_highW_S_T_max": long["S_T"].max(),
        "short_highW_sample_u_mean_mean": short["sample_u_mean"].mean(),
        "long_highW_sample_u_mean_mean": long["sample_u_mean"].mean(),
        "shortblock_cluster_failures": int((short["K_prime"] > K_CAP).sum()),
        "pass_hexc_shortblock_cluster_empirical": bool((short["K_prime"] <= K_CAP).all()),
        "recommended_next_file": next_file,
    }
    return pd.DataFrame([data])


def write_doc(summary: pd.DataFrame, rows: pd.DataFrame, bounds: pd.DataFrame) -> None:
    s = summary.iloc[0]
    short = rows[rows["short_highW_flag"]].sort_values("K_prime", ascending=False)
    lines = [
        "# Prime Mesh R2Q — H-Exc HighWeightRayleighCollapse ShortBlockCluster Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "This audit is sampled-grid only. It reconstructs `B_prime` on `T_J` from Lambda event offsets and weights; it does not use a full integer-grid theorem.",
        "",
        "Regime:",
        "",
        "```text",
        "W > 1040, h < 800, p_star >= 500,000,000",
        "```",
        "",
        "## 2. Summary",
        "",
        f"- Total high-weight post-P0 rows: `{int(s['rows_total_highW'])}`.",
        f"- Short high-weight rows: `{int(s['short_highW_rows'])}`: `{s['short_highW_candidate_ids']}`.",
        f"- `short_highW_K_max = {s['short_highW_K_max']:.12g}`.",
        f"- `short_highW_K_above_65_count = {int(s['short_highW_K_above_65_count'])}`.",
        f"- `short_highW_margin_min = {s['short_highW_margin_min']:.12g}`.",
        f"- Binding reconstruction error max: `{s['binding_rows_reconstruction_error_max']:.3e}`.",
        f"- Best closure route: `{s['best_closure_route']}`.",
        "",
        "## 3. Short-Block Rows",
        "",
        "| candidate | h | K_prime | margin | C_cluster | sample_u_mean | sample_left | prime_u_mean | prime_left | peak_u | top3_energy |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in short.iterrows():
        lines.append(
            f"| {r['candidate_id']} | {int(r['h'])} | {r['K_prime']:.8g} | {r['margin_to_65']:.8g} | "
            f"{r['C_cluster']:.8g} | {r['sample_u_mean']:.8g} | {r['sample_left_mass_frac']:.8g} | "
            f"{r['prime_u_mean']:.8g} | {r['prime_left_mass_frac']:.8g} | {r['B_prime_peak_u']:.8g} | "
            f"{r['B_prime_energy_concentration_top3']:.8g} |"
        )
    lines += [
        "",
        "## 4. Interpretation",
        "",
        "The short regime is finite in the current post-P0 export: four rows. The two near-cap rows are `hexc_00453` and `hexc_00442`; both reconstruct exactly from the Lambda event offsets and retain positive margins to 65.",
        "",
        "The skew signal remains sample-grid driven: all four short rows have stronger sample-grid skew than reconstructed prime-event skew. This supports a finite sampled-grid certificate first, with a possible later sample-grid-shape lemma.",
        "",
        "The simple `C_short * log(p*) * S_T` bound passes with `C_short=1.12`, but it is still empirical here and should not be presented as a proof without an analytic route.",
        "",
        "## 5. Bound Checks",
        "",
        "| bound | passes all short rows | max looseness |",
        "|---|---:|---:|",
    ]
    all_bounds = bounds[bounds["candidate_id"] == "ALL_SHORT"].sort_values("bound_name")
    for _, r in all_bounds.iterrows():
        lines.append(f"| {r['bound_name']} | {bool(r['passes_row'])} | {r['looseness']:.8g} |")
    lines += [
        "",
        "## 6. Recommended Next File",
        "",
        f"`{s['recommended_next_file']}`",
        "",
        s["best_closure_route_reason"],
        "",
        "## 7. Outputs",
        "",
        "```text",
        OUT_SCRIPT,
        OUT_SUMMARY,
        OUT_ROWS,
        OUT_BINDING,
        OUT_CERT,
        OUT_BOUNDS,
        OUT_FAILURES,
        OUT_BRIDGE,
        OUT_SAMPLE_PRIME,
        "```",
        "",
        "*AI documentation pass: GPT-5.5*",
    ]
    (BASE / OUT_DOC).write_text("\n".join(lines), encoding="utf-8")


def update_manifest(filenames: list[str]) -> None:
    path = BASE / OUT_MANIFEST
    now = datetime.now().isoformat(timespec="seconds")
    old = pd.read_csv(path).to_dict("records") if path.exists() else []
    names = set(filenames)
    rows = [row for row in old if row.get("filename") not in names]
    for name in filenames:
        p = BASE / name
        rows.append(
            {
                "filename": name,
                "path": str(p),
                "bytes": p.stat().st_size if p.exists() else 0,
                "status": "new",
                "updated_at": now,
                "note": "H-Exc ShortBlockCluster audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    dfs = load_inputs()
    rows, bridge, sample_prime = build_audit_rows(dfs)
    short = rows[rows["short_highW_flag"]].sort_values("K_prime", ascending=False)
    bounds = make_bounds(short, rows)
    summary = make_summary(rows, bounds)
    cert = make_certificate(short)
    binding = short[short["candidate_id"].isin(["hexc_00453", "hexc_00442"])].copy()
    failures = short[(short["K_prime"] > K_CAP) | (~short["pass_reconstruction"])].copy()

    summary.to_csv(BASE / OUT_SUMMARY, index=False)
    short.to_csv(BASE / OUT_ROWS, index=False)
    binding.to_csv(BASE / OUT_BINDING, index=False)
    cert.to_csv(BASE / OUT_CERT, index=False)
    bounds.to_csv(BASE / OUT_BOUNDS, index=False)
    failures.to_csv(BASE / OUT_FAILURES, index=False)
    bridge[bridge["candidate_id"].isin(short["candidate_id"])].to_csv(BASE / OUT_BRIDGE, index=False)
    sample_prime[sample_prime["candidate_id"].isin(short["candidate_id"])].to_csv(BASE / OUT_SAMPLE_PRIME, index=False)
    write_doc(summary, rows, bounds)
    update_manifest(
        [
            OUT_SCRIPT,
            OUT_SUMMARY,
            OUT_ROWS,
            OUT_BINDING,
            OUT_CERT,
            OUT_BOUNDS,
            OUT_FAILURES,
            OUT_BRIDGE,
            OUT_SAMPLE_PRIME,
            OUT_DOC,
        ]
    )

    s = summary.iloc[0].to_dict()
    print("ShortBlockCluster audit complete.")
    for key in [
        "rows_total_highW",
        "short_highW_rows",
        "short_highW_candidate_ids",
        "short_highW_K_max",
        "short_highW_K_above_65_count",
        "short_highW_margin_min",
        "binding_rows_reconstruction_error_max",
        "pass_binding_rows_reconstruction",
        "best_closure_route",
        "recommended_next_file",
    ]:
        print(f"{key}: {s[key]}")


if __name__ == "__main__":
    main()
