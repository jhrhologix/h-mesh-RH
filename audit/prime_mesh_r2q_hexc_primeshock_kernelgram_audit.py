#!/usr/bin/env python3
"""
Prime Mesh R2Q - H-Exc PrimeShockBridge KernelGram audit.

Represents the sampled prime-shock bridge as

    B_prime(r) = sum_i w_i k_{a_i}(r),
    k_a(r) = 1_{a <= r} - r/h,

and profiles the quadratic form E = w^T G w = ||K w||^2.
"""

from __future__ import annotations

import csv
import math
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd


OUT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT_DIR))

import prime_mesh_r2q_hexc_dn_residual_component_audit as dncomp  # noqa: E402


P0 = 500_000_000
K_TARGET = 65.0


def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: List[str] = []
    seen = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def boolish(x) -> bool:
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if pd.isna(x):
        return False
    if isinstance(x, (int, float, np.integer, np.floating)):
        return bool(x)
    return str(x).strip().lower() in {"true", "1", "yes", "y"}


def exact_abs_gram_stats(kmat: np.ndarray, diag_sum: float, chunk_size: int = 1024):
    """Compute max |G_ij| and sum |offdiag(G)| without storing full G."""
    m = kmat.shape[1]
    if m == 0:
        return 0.0, 0.0
    max_abs = 0.0
    abs_sum = 0.0
    for start in range(0, m, chunk_size):
        stop = min(m, start + chunk_size)
        block = kmat[:, start:stop].T @ kmat
        abs_block = np.abs(block)
        max_abs = max(max_abs, float(abs_block.max()))
        abs_sum += float(abs_block.sum())
    offdiag_abs_sum = abs_sum - diag_sum
    return max_abs, offdiag_abs_sum


def update_manifest(paths: Iterable[Path]) -> None:
    manifest = OUT_DIR / "deposit_manifest.csv"
    existing = pd.read_csv(manifest) if manifest.exists() else pd.DataFrame()
    rows = [] if existing.empty else existing.to_dict("records")
    by_name = {str(r.get("filename")): i for i, r in enumerate(rows)}
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    for path in paths:
        rec = {
            "filename": path.name,
            "path": str(path),
            "bytes": path.stat().st_size if path.exists() else 0,
            "status": "new",
            "updated_at": now,
            "note": "H-Exc PrimeShockBridge KernelGram audit output",
        }
        if path.name in by_name:
            rows[by_name[path.name]] = rec
        else:
            rows.append(rec)
    write_csv(manifest, rows)


def make_note(summary: Dict[str, object], paths: Dict[str, Path]) -> str:
    status = "PASS" if summary["pass_kernelgram_empirical"] else "REPAIR NEEDED"
    lines = [
        "# Prime Mesh R2Q - H-Exc PrimeShockBridge KernelGram Audit v1",
        "",
        f"**Status:** {status}",
        "",
        "## Purpose",
        "",
        "This audit represents the sampled prime-shock bridge as a kernel quadratic form:",
        "",
        "```text",
        "B_prime(r)=sum_i w_i k_ai(r),  k_a(r)=1_{a<=r}-r/h",
        "E_prime=w^T G w=||K w||^2.",
        "```",
        "",
        "## Summary",
        "",
        "```text",
    ]
    for key in [
        "rows",
        "post_P0_rows",
        "post_P0_K_prime_max",
        "post_P0_K_prime_above_65_count",
        "post_P0_gram_reconstruction_error_max",
        "post_P0_spectral_bound_over_h_max",
        "post_P0_spectral_tightness_max",
        "post_P0_spectral_tightness_median",
        "post_P0_rayleigh_over_h_max",
        "post_P0_top_eigenvalue_over_h_max",
        "post_P0_top_eigenvector_alignment_max",
        "post_P0_effective_rank_min",
        "post_P0_effective_rank_median",
        "best_proof_route_candidate",
        "pass_kernelgram_empirical",
    ]:
        lines.append(f"{key} = {summary.get(key)}")
    lines += [
        "```",
        "",
        "## Interpretation",
        "",
    ]
    route = summary.get("best_proof_route_candidate")
    if route == "rayleigh_structural_bound":
        lines.append("The most promising route is a Rayleigh-quotient structural bound for the actual Lambda weight vector on the Route-A grid.")
    elif route == "spectral_bound":
        lines.append("The spectral bound itself is tight enough to explain the theorem.")
    else:
        lines.append("The Gram identity is exact, but crude spectral/diagonal/l1 bounds remain too loose; the proof needs the actual Rayleigh/alignment structure, not only operator-norm control.")
    lines += ["", "## Files", ""]
    for label, path in paths.items():
        lines.append(f"- `{label}`: `{path.name}`")
    lines.append("")
    return "\n".join(lines)


def aggregate(rows_df: pd.DataFrame, key: str) -> List[Dict[str, object]]:
    if key not in rows_df.columns:
        return []
    out: List[Dict[str, object]] = []
    for value, g in rows_df.groupby(key, dropna=False):
        out.append(
            {
                "group_field": key,
                "group_value": value,
                "rows": int(len(g)),
                "post_P0_rows": int(g["post_P0_flag"].sum()),
                "K_prime_max": float(g["K_prime"].max()),
                "spectral_bound_over_h_max": float(g["spectral_bound_over_h"].max()),
                "spectral_tightness_median": float(g["spectral_tightness"].median()),
                "rayleigh_over_h_max": float(g["rayleigh_over_h"].max()),
                "top_eigenvector_alignment_max": float(g["top_eigenvector_alignment"].max()),
                "effective_rank_median": float(g["effective_rank"].median()),
                "failure_count": int(g["kernelgram_failure_flag"].sum()),
            }
        )
    return out


def main() -> None:
    samples_path = OUT_DIR / "prime_mesh_r2q_hexc_bridge_path_samples_v1.csv"
    profile_path = OUT_DIR / "prime_mesh_r2q_hexc_primeshock_bridge_profile_rows.csv"
    samplegrid_path = OUT_DIR / "prime_mesh_r2q_hexc_primeshock_samplegrid_structure_rows.csv"
    primitive_path = OUT_DIR / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv"
    for path in [samples_path, profile_path, samplegrid_path, primitive_path]:
        if not path.exists():
            raise FileNotFoundError(path)

    samples = pd.read_csv(samples_path)
    profile = pd.read_csv(profile_path)
    samplegrid = pd.read_csv(samplegrid_path)
    primitive = pd.read_csv(primitive_path)

    max_hi = int((samples["y"] + samples["h"]).max())
    base_primes = dncomp.sieve_primes_upto(int(math.isqrt(max_hi)) + 2)

    profile_small = profile[[c for c in [
        "candidate_id", "K_prime", "E_prime", "C_prime", "lambda_event_count",
        "prime_event_count", "prime_power_event_count", "lambda_event_weight_sum",
        "lambda_event_weight_sq_sum", "lambda_event_weight_max",
    ] if c in profile.columns]].drop_duplicates("candidate_id")
    grid_small = samplegrid[[c for c in [
        "candidate_id", "optional_K_prime_full", "optional_full_to_sampled_energy_ratio",
        "sample_count", "event_to_sample_alignment_score",
    ] if c in samplegrid.columns]].drop_duplicates("candidate_id")
    prim_small = primitive[[c for c in [
        "candidate_id", "Q_exc", "Q_energy_L2", "Q_R2Q", "Q_delta_D",
        "threshold_relevant_flag", "forbidden_flag", "finite_zone_flag", "row_status",
    ] if c in primitive.columns]].drop_duplicates("candidate_id")

    rows: List[Dict[str, object]] = []
    start_time = time.time()
    for idx, (candidate_id, g) in enumerate(samples.groupby("candidate_id", sort=False), start=1):
        g = g.sort_values("offset")
        y = int(g["y"].iloc[0])
        h = int(g["h"].iloc[0])
        p_star = int(g["p_star"].iloc[0])
        block_id = int(g["block_id"].iloc[0])
        r_offsets = sorted(set(int(x) for x in g["offset"].to_numpy()))
        r = np.array(r_offsets, dtype=np.float64)

        n_values, _comp_inc, lam, _inc = dncomp.compute_local_components(y + 1, y + h, dncomp.DEFAULT_C, base_primes)
        event_mask = lam > 0
        a_offsets = (n_values[event_mask] - y).astype(np.int64)
        weights = lam[event_mask].astype(np.float64)
        m = len(a_offsets)

        if m:
            kmat = (a_offsets[None, :] <= r[:, None]).astype(np.float64) - (r[:, None] / float(h))
            b = kmat @ weights
            e_gram = float(np.dot(b, b))
            small_s = kmat @ kmat.T
            evals, evecs = np.linalg.eigh(small_s)
            evals = np.maximum(evals, 0.0)
            top_eigenvalue = float(evals[-1]) if len(evals) else 0.0
            top_vec_sample = evecs[:, -1] if len(evals) else np.zeros(kmat.shape[0])
            kw = b
            kw_norm = float(np.linalg.norm(kw))
            top_alignment_output = abs(float(np.dot(kw / kw_norm, top_vec_sample))) if kw_norm > 0 else 0.0
            # Equivalent alignment of w with the top right singular direction.
            top_right = kmat.T @ top_vec_sample
            tr_norm = float(np.linalg.norm(top_right))
            w_norm = float(np.linalg.norm(weights))
            top_alignment_weight = abs(float(np.dot(weights / w_norm, top_right / tr_norm))) if w_norm > 0 and tr_norm > 0 else 0.0
            trace_g = float(np.trace(small_s))
            frob_g = float(math.sqrt(np.sum(evals * evals)))
            effective_rank = (trace_g * trace_g / (frob_g * frob_g)) if frob_g > 0 else 0.0
            col_norm_sq = np.sum(kmat * kmat, axis=0)
            diag_max = float(col_norm_sq.max()) if len(col_norm_sq) else 0.0
            diag_sum = float(col_norm_sq.sum())
            col_sum = np.sum(kmat, axis=1)
            all_entries_sum = float(np.dot(col_sum, col_sum))
            offdiag_sum = all_entries_sum - diag_sum
            g_max_abs, offdiag_abs_sum = exact_abs_gram_stats(kmat, diag_sum)
        else:
            kmat = np.zeros((len(r), 0))
            e_gram = 0.0
            top_eigenvalue = 0.0
            top_alignment_output = 0.0
            top_alignment_weight = 0.0
            trace_g = 0.0
            frob_g = 0.0
            effective_rank = 0.0
            diag_max = 0.0
            diag_sum = 0.0
            offdiag_sum = 0.0
            offdiag_abs_sum = 0.0
            g_max_abs = 0.0

        weight_l1 = float(np.sum(np.abs(weights)))
        weight_l2_sq = float(np.dot(weights, weights))
        weight_l2 = math.sqrt(weight_l2_sq)
        weight_max = float(np.max(np.abs(weights))) if len(weights) else 0.0
        weight_sum = float(np.sum(weights))

        spectral_bound = top_eigenvalue * weight_l2_sq
        diag_bound = diag_max * weight_l2_sq
        l1_bound = g_max_abs * weight_l1 * weight_l1
        rayleigh = e_gram / weight_l2_sq if weight_l2_sq > 0 else 0.0

        # Direct bridge recomputation from prefix, used as a guard.
        lam_prefix = np.concatenate(([0.0], np.cumsum(lam)))
        direct_b = lam_prefix[np.array(r_offsets, dtype=np.int64)] - (r / float(h)) * float(lam_prefix[h])
        e_direct = float(np.dot(direct_b, direct_b))
        gram_error = abs(e_direct - e_gram)

        rows.append(
            {
                "candidate_id": candidate_id,
                "block_id": block_id,
                "x": p_star,
                "y": y,
                "h": h,
                "p_star": p_star,
                "post_P0_flag": bool(p_star >= P0),
                "sample_count": int(len(r_offsets)),
                "event_count": int(m),
                "prime_event_count": int(m),
                "prime_power_event_count": 0,
                "R_offsets": ",".join(str(x) for x in r_offsets[:80]),
                "event_offsets": ",".join(str(int(x)) for x in a_offsets[:80]),
                "weights": ",".join(f"{float(x):.12g}" for x in weights[:80]),
                "E_prime_direct": e_direct,
                "E_prime_gram": e_gram,
                "gram_reconstruction_error": gram_error,
                "K_prime": e_gram / h if h else math.nan,
                "G_trace": trace_g,
                "G_frobenius_norm": frob_g,
                "G_operator_norm": top_eigenvalue,
                "G_operator_norm_over_h": top_eigenvalue / h if h else math.nan,
                "G_max_entry_abs": g_max_abs,
                "G_diag_max": diag_max,
                "G_diag_sum": diag_sum,
                "G_offdiag_sum": offdiag_sum,
                "G_offdiag_abs_sum": offdiag_abs_sum,
                "weight_l1": weight_l1,
                "weight_l2_sq": weight_l2_sq,
                "weight_l2": weight_l2,
                "weight_max": weight_max,
                "weight_sum": weight_sum,
                "spectral_bound": spectral_bound,
                "spectral_bound_over_h": spectral_bound / h if h else math.nan,
                "spectral_tightness": spectral_bound / e_gram if e_gram > 0 else math.nan,
                "diag_bound": diag_bound,
                "diag_bound_over_h": diag_bound / h if h else math.nan,
                "diag_tightness": diag_bound / e_gram if e_gram > 0 else math.nan,
                "l1_bound": l1_bound,
                "l1_bound_over_h": l1_bound / h if h else math.nan,
                "l1_tightness": l1_bound / e_gram if e_gram > 0 else math.nan,
                "rayleigh_quotient": rayleigh,
                "rayleigh_over_h": rayleigh / h if h else math.nan,
                "top_eigenvalue": top_eigenvalue,
                "top_eigenvalue_over_h": top_eigenvalue / h if h else math.nan,
                "top_eigenvector_alignment": top_alignment_weight,
                "top_output_alignment": top_alignment_output,
                "effective_rank": effective_rank,
                "event_weight_effective_support": (weight_l1 * weight_l1 / weight_l2_sq) if weight_l2_sq > 0 else 0.0,
                "kernelgram_failure_flag": bool(p_star >= P0 and e_gram / h > K_TARGET),
            }
        )
        if idx % 250 == 0:
            print(f"[progress] processed {idx}/{len(samples.groupby('candidate_id'))} candidates in {time.time()-start_time:.1f}s")

    rows_df = pd.DataFrame(rows)
    rows_df = rows_df.merge(profile_small, on="candidate_id", how="left", suffixes=("", "_profile"))
    rows_df = rows_df.merge(grid_small, on="candidate_id", how="left", suffixes=("", "_grid"))
    rows_df = rows_df.merge(prim_small, on="candidate_id", how="left", suffixes=("", "_primitive"))

    if "K_prime_profile" in rows_df:
        rows_df["K_prime_profile_delta"] = rows_df["K_prime"] - rows_df["K_prime_profile"]
        profile_delta = float(rows_df["K_prime_profile_delta"].abs().max())
    else:
        profile_delta = math.nan

    post = rows_df[rows_df["post_P0_flag"] == True]
    if int(post["spectral_bound_over_h"].le(K_TARGET).sum()) == len(post):
        route = "spectral_bound"
    elif int(post["rayleigh_over_h"].le(K_TARGET / np.maximum(post["weight_l2_sq"], 1e-300)).sum()) == len(post):
        route = "rayleigh_structural_bound"
    else:
        route = "rayleigh_alignment_needed"

    summary = {
        "rows": int(len(rows_df)),
        "post_P0_rows": int(len(post)),
        "K_target": K_TARGET,
        "K_prime_profile_delta_abs_max": profile_delta,
        "post_P0_K_prime_max": float(post["K_prime"].max()),
        "post_P0_K_prime_above_65_count": int(post["kernelgram_failure_flag"].sum()),
        "post_P0_gram_reconstruction_error_max": float(post["gram_reconstruction_error"].max()),
        "post_P0_spectral_bound_over_h_max": float(post["spectral_bound_over_h"].max()),
        "post_P0_spectral_bound_over_h_median": float(post["spectral_bound_over_h"].median()),
        "post_P0_spectral_tightness_max": float(post["spectral_tightness"].max()),
        "post_P0_spectral_tightness_median": float(post["spectral_tightness"].median()),
        "post_P0_diag_bound_over_h_max": float(post["diag_bound_over_h"].max()),
        "post_P0_l1_bound_over_h_max": float(post["l1_bound_over_h"].max()),
        "post_P0_rayleigh_over_h_max": float(post["rayleigh_over_h"].max()),
        "post_P0_rayleigh_over_h_median": float(post["rayleigh_over_h"].median()),
        "post_P0_top_eigenvalue_over_h_max": float(post["top_eigenvalue_over_h"].max()),
        "post_P0_top_eigenvalue_over_h_median": float(post["top_eigenvalue_over_h"].median()),
        "post_P0_top_eigenvector_alignment_max": float(post["top_eigenvector_alignment"].max()),
        "post_P0_top_eigenvector_alignment_median": float(post["top_eigenvector_alignment"].median()),
        "post_P0_top_output_alignment_max": float(post["top_output_alignment"].max()),
        "post_P0_effective_rank_min": float(post["effective_rank"].min()),
        "post_P0_effective_rank_median": float(post["effective_rank"].median()),
        "post_P0_event_weight_effective_support_min": float(post["event_weight_effective_support"].min()),
        "post_P0_event_weight_effective_support_median": float(post["event_weight_effective_support"].median()),
        "threshold_relevant_rows": int(rows_df.get("threshold_relevant_flag", pd.Series(False, index=rows_df.index)).map(boolish).sum()),
        "threshold_relevant_K_prime_max": float(rows_df[rows_df.get("threshold_relevant_flag", pd.Series(False, index=rows_df.index)).map(boolish)]["K_prime"].max())
        if "threshold_relevant_flag" in rows_df and rows_df["threshold_relevant_flag"].map(boolish).any()
        else math.nan,
        "forbidden_rows": int(rows_df.get("forbidden_flag", pd.Series(False, index=rows_df.index)).map(boolish).sum()),
        "forbidden_K_prime_max": float(rows_df[rows_df.get("forbidden_flag", pd.Series(False, index=rows_df.index)).map(boolish)]["K_prime"].max())
        if "forbidden_flag" in rows_df and rows_df["forbidden_flag"].map(boolish).any()
        else math.nan,
        "best_proof_route_candidate": route,
        "kernelgram_failures": int(rows_df["kernelgram_failure_flag"].sum()),
        "post_P0_kernelgram_failures": int(post["kernelgram_failure_flag"].sum()),
        "pass_kernelgram_empirical": bool(post["kernelgram_failure_flag"].sum() == 0 and (not math.isfinite(profile_delta) or profile_delta <= 1e-8)),
    }

    by_rows: List[Dict[str, object]] = []
    for key in ["post_P0_flag", "E_theta_sign", "threshold_relevant_flag", "forbidden_flag", "finite_zone_flag", "row_status"]:
        by_rows.extend(aggregate(rows_df, key))

    extremes = []
    for metric in [
        "K_prime",
        "spectral_bound_over_h",
        "spectral_tightness",
        "rayleigh_over_h",
        "top_eigenvalue_over_h",
        "top_eigenvector_alignment",
        "effective_rank",
        "event_weight_effective_support",
    ]:
        ascending = metric in {"effective_rank", "event_weight_effective_support"}
        take = rows_df.replace([np.inf, -np.inf], np.nan).sort_values(metric, ascending=ascending).head(20)
        for rank, (_, r) in enumerate(take.iterrows(), start=1):
            extremes.append(
                {
                    "metric": metric,
                    "rank": rank,
                    "candidate_id": r["candidate_id"],
                    "block_id": r["block_id"],
                    "p_star": r["p_star"],
                    "h": r["h"],
                    "post_P0_flag": r["post_P0_flag"],
                    "value": r[metric],
                    "K_prime": r["K_prime"],
                    "spectral_bound_over_h": r["spectral_bound_over_h"],
                    "spectral_tightness": r["spectral_tightness"],
                    "rayleigh_over_h": r["rayleigh_over_h"],
                    "top_eigenvalue_over_h": r["top_eigenvalue_over_h"],
                    "top_eigenvector_alignment": r["top_eigenvector_alignment"],
                    "effective_rank": r["effective_rank"],
                    "event_count": r["event_count"],
                    "sample_count": r["sample_count"],
                }
            )

    failures = post[post["kernelgram_failure_flag"] == True].copy()

    paths = {
        "script": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_kernelgram_audit.py",
        "summary": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_kernelgram_summary.csv",
        "rows": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_kernelgram_rows.csv",
        "by_regime": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_kernelgram_by_regime.csv",
        "extremes": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_kernelgram_extremes.csv",
        "failures": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_kernelgram_failures.csv",
        "note": OUT_DIR / "Prime_Mesh_R2Q_HExc_PrimeShockBridge_KernelGram_Audit_v1.md",
    }
    write_csv(paths["summary"], [summary])
    rows_df.to_csv(paths["rows"], index=False)
    write_csv(paths["by_regime"], by_rows)
    write_csv(paths["extremes"], extremes)
    failures.to_csv(paths["failures"], index=False)
    paths["note"].write_text(make_note(summary, paths), encoding="utf-8")
    update_manifest(paths.values())

    print("Wrote outputs:")
    for p in paths.values():
        print(p)
    print("Summary:")
    for k, v in summary.items():
        print(f"{k}={v}")


if __name__ == "__main__":
    main()
