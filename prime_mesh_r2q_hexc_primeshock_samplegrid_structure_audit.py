#!/usr/bin/env python3
"""
Prime Mesh R2Q - H-Exc PrimeShockBridge SampleGridStructure audit.

Inspects whether the sampled-grid prime-shock bridge bound

    E_T/h <= 65

is sampled-only, sample-RMS driven, event-alignment driven, or plausibly
liftable to a full integer-grid statement.
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


def nearest_distances(points: np.ndarray, anchors: np.ndarray) -> np.ndarray:
    """Distance from each point to the nearest anchor."""
    if len(points) == 0:
        return np.array([], dtype=np.float64)
    if len(anchors) == 0:
        return np.full(len(points), np.nan, dtype=np.float64)
    idx = np.searchsorted(anchors, points)
    left = np.where(idx > 0, anchors[np.maximum(idx - 1, 0)], anchors[0])
    right = np.where(idx < len(anchors), anchors[np.minimum(idx, len(anchors) - 1)], anchors[-1])
    return np.minimum(np.abs(points - left), np.abs(points - right)).astype(np.float64)


def sample_event_position_counts(sample_offsets: np.ndarray, event_offsets: np.ndarray) -> Dict[str, int]:
    if len(event_offsets) == 0:
        return {
            "samples_on_event_count": 0,
            "samples_after_event_count": 0,
            "samples_between_events_count": int(len(sample_offsets)),
            "samples_in_large_gap_count": 0,
        }
    event_set = set(int(x) for x in event_offsets)
    samples_on = int(sum(int(u) in event_set for u in sample_offsets))
    # Strictly after at least one event.
    samples_after = int(sum(int(u) > int(event_offsets[0]) for u in sample_offsets))
    gaps = np.diff(event_offsets)
    if len(gaps):
        large_threshold = float(np.quantile(gaps, 0.90))
        large_gap_count = 0
        for u64 in sample_offsets:
            u = int(u64)
            pos = np.searchsorted(event_offsets, u)
            if 0 < pos < len(event_offsets):
                gap = int(event_offsets[pos] - event_offsets[pos - 1])
                if gap >= large_threshold:
                    large_gap_count += 1
    else:
        large_gap_count = 0
    return {
        "samples_on_event_count": samples_on,
        "samples_after_event_count": samples_after,
        "samples_between_events_count": int(len(sample_offsets) - samples_on),
        "samples_in_large_gap_count": int(large_gap_count),
    }


def make_note(summary: Dict[str, object], paths: Dict[str, Path]) -> str:
    status = "PASS" if summary["pass_samplegrid_structure_empirical"] else "REPAIR NEEDED"
    lines = [
        "# Prime Mesh R2Q - H-Exc PrimeShockBridge SampleGridStructure Audit v1",
        "",
        f"**Status:** {status}",
        "",
        "## Purpose",
        "",
        "This audit inspects the SR11/H-Exc sample grid behind the sampled prime-shock bridge bound:",
        "",
        "```text",
        "p_star >= P0 => ||B_prime||^2_{2,T_J}/h <= 65.",
        "```",
        "",
        "It compares sampled-grid energy to the optional full integer-grid energy and profiles event/sample alignment.",
        "",
        "## Summary",
        "",
        "```text",
    ]
    for key in [
        "rows",
        "post_P0_rows",
        "post_P0_K_sampled_max",
        "post_P0_K_sampled_above_65_count",
        "post_P0_K_full_max",
        "post_P0_full_to_sampled_energy_ratio_max",
        "post_P0_full_to_sampled_absmax_ratio_max",
        "post_P0_sample_count_max",
        "post_P0_sample_offset_gap_max",
        "post_P0_sample_count_over_h_max",
        "post_P0_event_to_sample_alignment_score_min",
        "post_P0_event_to_sample_alignment_score_mean",
        "post_P0_nearest_sample_distance_to_event_max",
        "post_P0_samples_on_event_count_max",
        "post_P0_samples_between_events_count_max",
        "lifting_plausible_empirical",
        "sampled_only_warning",
        "best_theorem_form_recommended",
        "pass_samplegrid_structure_empirical",
    ]:
        lines.append(f"{key} = {summary.get(key)}")
    lines += [
        "```",
        "",
        "## Interpretation",
        "",
    ]
    if summary["sampled_only_warning"]:
        lines.append(
            "The bound is clean on the SR11/H-Exc sampled grid, but the full integer-grid energy is much larger. "
            "A full-grid lifting lemma is not supported by this audit; the theorem should remain sampled-grid unless a different lifting mechanism is supplied."
        )
    elif summary["lifting_plausible_empirical"]:
        lines.append(
            "Sampled and full-grid profiles are close enough that a lifting lemma looks plausible empirically."
        )
    else:
        lines.append(
            "The sampled theorem passes, but the sample-grid explanation needs a dedicated structural theorem."
        )
    lines += ["", "## Files", ""]
    for label, path in paths.items():
        lines.append(f"- `{label}`: `{path.name}`")
    lines.append("")
    return "\n".join(lines)


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
            "note": "H-Exc PrimeShockBridge SampleGridStructure audit output",
        }
        if path.name in by_name:
            rows[by_name[path.name]] = rec
        else:
            rows.append(rec)
    write_csv(manifest, rows)


def aggregate(rows_df: pd.DataFrame, key: str) -> List[Dict[str, object]]:
    if key not in rows_df.columns:
        return []
    out = []
    for value, g in rows_df.groupby(key, dropna=False):
        out.append(
            {
                "group_field": key,
                "group_value": value,
                "rows": int(len(g)),
                "post_P0_rows": int(g["post_P0_flag"].sum()),
                "K_prime_sampled_max": float(g["K_prime_sampled"].max()),
                "K_prime_full_max": float(g["optional_K_prime_full"].max()),
                "full_to_sampled_energy_ratio_max": float(g["optional_full_to_sampled_energy_ratio"].max()),
                "sample_count_max": int(g["sample_count"].max()),
                "sample_offset_gaps_max": int(g["sample_offset_gaps_max"].max()),
                "alignment_score_mean": float(g["event_to_sample_alignment_score"].mean()),
                "target_failure_count": int(g["sampled_target_failure_flag"].sum()),
            }
        )
    return out


def main() -> None:
    samples_path = OUT_DIR / "prime_mesh_r2q_hexc_bridge_path_samples_v1.csv"
    profile_path = OUT_DIR / "prime_mesh_r2q_hexc_primeshock_bridge_profile_rows.csv"
    primitive_path = OUT_DIR / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv"
    for path in [samples_path, profile_path, primitive_path]:
        if not path.exists():
            raise FileNotFoundError(path)

    samples = pd.read_csv(samples_path)
    profile = pd.read_csv(profile_path)
    primitive = pd.read_csv(primitive_path)

    max_hi = int((samples["y"] + samples["h"]).max())
    base_primes = dncomp.sieve_primes_upto(int(math.isqrt(max_hi)) + 2)

    profile_cols = [
        "candidate_id",
        "K_prime",
        "E_prime",
        "C_prime",
        "lambda_event_count",
        "prime_event_count",
        "prime_power_event_count",
        "lambda_event_weight_sum",
        "lambda_event_weight_max",
        "lambda_event_weight_sq_sum",
        "max_lambda_gap",
        "B_prime_effective_support_frac",
    ]
    profile_small = profile[[c for c in profile_cols if c in profile.columns]].drop_duplicates("candidate_id")
    primitive_cols = [
        "candidate_id",
        "Q_exc",
        "Q_energy_L2",
        "Q_R2Q",
        "Q_delta_D",
        "epsilon",
        "threshold_relevant_flag",
        "forbidden_flag",
        "finite_zone_flag",
        "positive_harmless_flag",
        "negative_transfer_flag",
        "row_status",
    ]
    prim_small = primitive[[c for c in primitive_cols if c in primitive.columns]].drop_duplicates("candidate_id")

    rows: List[Dict[str, object]] = []
    grouped = samples.groupby("candidate_id", sort=False)
    start = time.time()
    for idx, (candidate_id, g) in enumerate(grouped, start=1):
        g = g.sort_values("offset")
        y = int(g["y"].iloc[0])
        h = int(g["h"].iloc[0])
        p_star = int(g["p_star"].iloc[0])
        block_id = g["block_id"].iloc[0]
        sample_offsets = g["offset"].astype(int).to_numpy()
        if sample_offsets[0] != 0:
            sample_offsets = np.concatenate(([0], sample_offsets))
        if sample_offsets[-1] != h:
            raise ValueError(f"Endpoint offset mismatch for {candidate_id}: {sample_offsets[-1]} != {h}")

        n_values, _comp_inc, lam, _inc = dncomp.compute_local_components(y + 1, y + h, dncomp.DEFAULT_C, base_primes)
        lam_prefix = np.concatenate(([0.0], np.cumsum(lam)))
        lam_total = float(lam_prefix[h])

        sample_frac = sample_offsets.astype(float) / float(h)
        b_sample = lam_prefix[sample_offsets] - sample_frac * lam_total
        e_sample = float(np.dot(b_sample, b_sample))
        k_sample = e_sample / h
        abs_sample = np.abs(b_sample)
        sample_peak_idx = int(abs_sample.argmax())
        sample_peak_offset = int(sample_offsets[sample_peak_idx])

        full_offsets = np.arange(0, h + 1, dtype=np.int64)
        full_frac = full_offsets.astype(float) / float(h)
        b_full = lam_prefix - full_frac * lam_total
        e_full = float(np.dot(b_full, b_full))
        k_full = e_full / h
        abs_full = np.abs(b_full)
        full_peak_idx = int(abs_full.argmax())
        full_peak_offset = int(full_offsets[full_peak_idx])

        event_mask = lam > 0
        event_offsets = (n_values[event_mask] - y).astype(np.int64)
        event_weights = lam[event_mask]
        event_gaps = np.diff(event_offsets) if len(event_offsets) > 1 else np.array([], dtype=np.int64)
        sample_gaps = np.diff(sample_offsets) if len(sample_offsets) > 1 else np.array([], dtype=np.int64)

        dist_event_to_sample = nearest_distances(event_offsets, sample_offsets)
        dist_sample_to_event = nearest_distances(sample_offsets, event_offsets)
        alignment_den = max(float(np.mean(event_gaps)) if len(event_gaps) else float(h), 1.0)
        mean_event_dist = float(np.nanmean(dist_event_to_sample)) if len(dist_event_to_sample) else float("nan")
        max_event_dist = float(np.nanmax(dist_event_to_sample)) if len(dist_event_to_sample) else float("nan")
        alignment_score = 1.0 / (1.0 + mean_event_dist / alignment_den) if math.isfinite(mean_event_dist) else float("nan")

        counts = sample_event_position_counts(sample_offsets, event_offsets)
        row = {
            "candidate_id": candidate_id,
            "block_id": block_id,
            "x": p_star,
            "y": y,
            "h": h,
            "p_star": p_star,
            "post_P0_flag": bool(p_star >= P0),
            "sample_count": int(len(sample_offsets)),
            "sample_count_over_h": float(len(sample_offsets) / h),
            "sample_offsets_min": int(sample_offsets.min()),
            "sample_offsets_max": int(sample_offsets.max()),
            "sample_offset_gaps_max": int(sample_gaps.max()) if len(sample_gaps) else 0,
            "sample_offset_gaps_mean": float(sample_gaps.mean()) if len(sample_gaps) else float("nan"),
            "sample_offset_gaps_median": float(np.median(sample_gaps)) if len(sample_gaps) else float("nan"),
            "endpoint_left_sampled": bool(sample_offsets[0] == 0),
            "endpoint_right_sampled": bool(sample_offsets[-1] == h),
            "lambda_event_count": int(len(event_offsets)),
            "prime_event_count": int(len(event_offsets)),  # post-P0 has no powers in the current profile; exact class retained below.
            "prime_power_event_count": 0,
            "lambda_weight_sum": lam_total,
            "lambda_weight_max": float(event_weights.max()) if len(event_weights) else 0.0,
            "lambda_weight_sq_sum": float(np.dot(event_weights, event_weights)) if len(event_weights) else 0.0,
            "event_offsets_min": int(event_offsets.min()) if len(event_offsets) else -1,
            "event_offsets_max": int(event_offsets.max()) if len(event_offsets) else -1,
            "event_gap_max": int(event_gaps.max()) if len(event_gaps) else h,
            "event_gap_mean": float(event_gaps.mean()) if len(event_gaps) else float("nan"),
            "K_prime_sampled": k_sample,
            "E_prime_sampled": e_sample,
            "B_prime_sampled_abs_max": float(abs_sample.max()) if len(abs_sample) else 0.0,
            "B_prime_sampled_RMS": math.sqrt(float(np.mean(abs_sample * abs_sample))) if len(abs_sample) else 0.0,
            "sampled_peak_offset": sample_peak_offset,
            "sampled_peak_position_fraction": sample_peak_offset / h,
            "nearest_sample_distance_to_event_max": max_event_dist,
            "nearest_sample_distance_to_event_mean": mean_event_dist,
            "nearest_event_distance_to_sample_max": float(np.nanmax(dist_sample_to_event)) if len(dist_sample_to_event) else float("nan"),
            "nearest_event_distance_to_sample_mean": float(np.nanmean(dist_sample_to_event)) if len(dist_sample_to_event) else float("nan"),
            "event_to_sample_alignment_score": alignment_score,
            "optional_K_prime_full": k_full,
            "optional_E_prime_full": e_full,
            "optional_B_prime_full_abs_max": float(abs_full.max()) if len(abs_full) else 0.0,
            "optional_full_peak_offset": full_peak_offset,
            "optional_full_peak_position_fraction": full_peak_offset / h,
            "optional_full_to_sampled_energy_ratio": e_full / e_sample if e_sample > 0 else float("inf"),
            "optional_full_to_sampled_absmax_ratio": float(abs_full.max() / abs_sample.max()) if len(abs_sample) and abs_sample.max() > 0 else float("inf"),
            "sampled_target_failure_flag": bool(p_star >= P0 and k_sample > K_TARGET),
            "full_grid_target_failure_flag": bool(p_star >= P0 and k_full > K_TARGET),
        }
        row.update(counts)
        rows.append(row)
        if idx % 250 == 0:
            print(f"[progress] processed {idx}/{len(grouped)} candidates in {time.time()-start:.1f}s")

    rows_df = pd.DataFrame(rows)
    rows_df = rows_df.merge(profile_small, on="candidate_id", how="left", suffixes=("", "_profile"))
    rows_df = rows_df.merge(prim_small, on="candidate_id", how="left", suffixes=("", "_primitive"))

    if "K_prime" in rows_df.columns:
        rows_df["K_prime_profile_delta"] = rows_df["K_prime_sampled"] - rows_df["K_prime"]
        profile_delta_max = float(rows_df["K_prime_profile_delta"].abs().max())
    else:
        profile_delta_max = float("nan")

    post = rows_df[rows_df["post_P0_flag"] == True]
    lifting_plausible = bool(
        post["optional_full_to_sampled_energy_ratio"].replace([np.inf, -np.inf], np.nan).max() <= 4.0
        and post["full_grid_target_failure_flag"].sum() == 0
    )
    sampled_only_warning = bool(post["full_grid_target_failure_flag"].sum() > 0 or post["optional_full_to_sampled_energy_ratio"].max() > 10.0)
    if sampled_only_warning:
        best_form = "sampled_grid_only_with_no_full_lifting"
    elif lifting_plausible:
        best_form = "sampled_grid_with_possible_lifting"
    else:
        best_form = "sampled_grid_structural"

    summary = {
        "rows": int(len(rows_df)),
        "post_P0_rows": int(len(post)),
        "K_target": K_TARGET,
        "K_prime_profile_delta_abs_max": profile_delta_max,
        "post_P0_K_sampled_max": float(post["K_prime_sampled"].max()),
        "post_P0_K_sampled_above_65_count": int(post["sampled_target_failure_flag"].sum()),
        "post_P0_K_full_max": float(post["optional_K_prime_full"].max()),
        "post_P0_full_grid_above_65_count": int(post["full_grid_target_failure_flag"].sum()),
        "post_P0_full_to_sampled_energy_ratio_max": float(post["optional_full_to_sampled_energy_ratio"].replace([np.inf, -np.inf], np.nan).max()),
        "post_P0_full_to_sampled_energy_ratio_median": float(post["optional_full_to_sampled_energy_ratio"].replace([np.inf, -np.inf], np.nan).median()),
        "post_P0_full_to_sampled_absmax_ratio_max": float(post["optional_full_to_sampled_absmax_ratio"].replace([np.inf, -np.inf], np.nan).max()),
        "post_P0_sample_count_max": int(post["sample_count"].max()),
        "post_P0_sample_count_min": int(post["sample_count"].min()),
        "post_P0_sample_offset_gap_max": int(post["sample_offset_gaps_max"].max()),
        "post_P0_sample_count_over_h_max": float(post["sample_count_over_h"].max()),
        "post_P0_event_to_sample_alignment_score_min": float(post["event_to_sample_alignment_score"].min()),
        "post_P0_event_to_sample_alignment_score_mean": float(post["event_to_sample_alignment_score"].mean()),
        "post_P0_nearest_sample_distance_to_event_max": float(post["nearest_sample_distance_to_event_max"].max()),
        "post_P0_nearest_sample_distance_to_event_mean_max": float(post["nearest_sample_distance_to_event_mean"].max()),
        "post_P0_samples_on_event_count_max": int(post["samples_on_event_count"].max()),
        "post_P0_samples_between_events_count_max": int(post["samples_between_events_count"].max()),
        "threshold_relevant_rows": int(rows_df.get("threshold_relevant_flag", pd.Series(False, index=rows_df.index)).map(boolish).sum()),
        "threshold_relevant_K_sampled_max": float(rows_df[rows_df.get("threshold_relevant_flag", pd.Series(False, index=rows_df.index)).map(boolish)]["K_prime_sampled"].max())
        if "threshold_relevant_flag" in rows_df and rows_df["threshold_relevant_flag"].map(boolish).any()
        else float("nan"),
        "forbidden_rows": int(rows_df.get("forbidden_flag", pd.Series(False, index=rows_df.index)).map(boolish).sum()),
        "forbidden_K_sampled_max": float(rows_df[rows_df.get("forbidden_flag", pd.Series(False, index=rows_df.index)).map(boolish)]["K_prime_sampled"].max())
        if "forbidden_flag" in rows_df and rows_df["forbidden_flag"].map(boolish).any()
        else float("nan"),
        "lifting_plausible_empirical": lifting_plausible,
        "sampled_only_warning": sampled_only_warning,
        "best_theorem_form_recommended": best_form,
        "samplegrid_structure_failures": int(post["sampled_target_failure_flag"].sum()),
        "pass_samplegrid_structure_empirical": bool(post["sampled_target_failure_flag"].sum() == 0 and (not math.isfinite(profile_delta_max) or profile_delta_max <= 1.0e-8)),
    }

    by_rows: List[Dict[str, object]] = []
    for key in ["post_P0_flag", "E_theta_sign", "threshold_relevant_flag", "forbidden_flag", "finite_zone_flag", "row_status"]:
        by_rows.extend(aggregate(rows_df, key))

    extremes = []
    for metric in [
        "K_prime_sampled",
        "optional_K_prime_full",
        "optional_full_to_sampled_energy_ratio",
        "sample_offset_gaps_max",
        "nearest_sample_distance_to_event_max",
        "event_to_sample_alignment_score",
        "samples_on_event_count",
    ]:
        ascending = metric == "event_to_sample_alignment_score"
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
                    "K_prime_sampled": r["K_prime_sampled"],
                    "optional_K_prime_full": r["optional_K_prime_full"],
                    "optional_full_to_sampled_energy_ratio": r["optional_full_to_sampled_energy_ratio"],
                    "sample_count": r["sample_count"],
                    "sample_offset_gaps_max": r["sample_offset_gaps_max"],
                    "lambda_event_count": r["lambda_event_count"],
                    "event_to_sample_alignment_score": r["event_to_sample_alignment_score"],
                }
            )

    failures = post[post["sampled_target_failure_flag"] == True].copy()

    paths = {
        "script": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_samplegrid_structure_audit.py",
        "summary": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_samplegrid_structure_summary.csv",
        "rows": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_samplegrid_structure_rows.csv",
        "by_regime": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_samplegrid_structure_by_regime.csv",
        "extremes": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_samplegrid_structure_extremes.csv",
        "failures": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_samplegrid_structure_failures.csv",
        "note": OUT_DIR / "Prime_Mesh_R2Q_HExc_PrimeShockBridge_SampleGridStructure_Audit_v1.md",
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
