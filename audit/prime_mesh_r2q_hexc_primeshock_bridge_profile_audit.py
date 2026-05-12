#!/usr/bin/env python3
"""
Prime Mesh R2Q - H-Exc PrimeShockBridge profile audit.

Profiles the centered von Mangoldt bridge

    B_prime(t) = sum_{y<n<=t} Lambda(n) - ((t-y)/h) sum_{y<n<=y+h} Lambda(n)

behind the post-P0 target E_prime/h <= 65.
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
K_PRIME_TARGET = 65.0
EPS = 1.0e-300


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


def qtile(values: np.ndarray, q: float) -> float:
    if len(values) == 0:
        return float("nan")
    return float(np.quantile(values, q))


def boolish(x) -> bool:
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if pd.isna(x):
        return False
    if isinstance(x, (int, float, np.integer, np.floating)):
        return bool(x)
    return str(x).strip().lower() in {"true", "1", "yes", "y"}


def make_note(summary: Dict[str, object], paths: Dict[str, Path]) -> str:
    status = "PASS" if summary["pass_primeshock_bridge_profile_empirical"] else "REPAIR NEEDED"
    lines = [
        "# Prime Mesh R2Q - H-Exc PrimeShockBridge Profile Audit v1",
        "",
        f"**Status:** {status}",
        "",
        "## Purpose",
        "",
        "This audit profiles the dominant H-Exc component",
        "",
        "```text",
        "B_prime(t)=sum_{y<n<=t} Lambda(n)-((t-y)/h)sum_{y<n<=y+h} Lambda(n)",
        "```",
        "",
        "with theorem-facing target:",
        "",
        "```text",
        "p_star >= P0 => ||B_prime||^2_{2,T_J}/h <= 65.",
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
        "post_P0_C_prime_max",
        "post_P0_K_prime_above_65_count",
        "post_P0_lambda_event_count_max",
        "post_P0_prime_event_count_max",
        "post_P0_prime_power_event_count_max",
        "post_P0_lambda_weight_sum_max",
        "post_P0_lambda_weight_sq_sum_max",
        "post_P0_lambda_event_weight_max",
        "post_P0_max_lambda_gap_max",
        "post_P0_sample_count_max",
        "post_P0_sample_count_over_h_max",
        "post_P0_effective_support_frac_max",
        "post_P0_effective_support_frac_mean",
        "post_P0_single_shock_bound_pass_count",
        "post_P0_event_l2_bound_pass_count",
        "post_P0_total_mass_bound_pass_count",
        "best_proof_route_candidate",
        "pass_primeshock_bridge_profile_empirical",
    ]:
        lines.append(f"{key} = {summary.get(key)}")
    lines += [
        "```",
        "",
        "## Interpretation",
        "",
    ]
    route = str(summary.get("best_proof_route_candidate"))
    if route == "sampled_bridge_direct":
        lines.append(
            "The clean route is the direct sampled prime-shock bridge bound: "
            "the audited `K_prime` itself stays below 65 post-P0, while crude event-count bounds are too loose."
        )
    elif route == "event_l2_bound":
        lines.append(
            "The event-weight square-sum bound appears strong enough to explain the post-P0 target."
        )
    elif route == "single_shock_bound":
        lines.append(
            "The single-shock/max-event bound appears strong enough to explain the post-P0 target."
        )
    else:
        lines.append(
            "The profile supports the post-P0 target empirically, but no simple crude event bound fully explains it."
        )
    lines += [
        "",
        "## Files",
        "",
    ]
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
            "note": "H-Exc PrimeShockBridge profile audit output",
        }
        if path.name in by_name:
            rows[by_name[path.name]] = rec
        else:
            rows.append(rec)
    write_csv(manifest, rows)


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
                "K_prime_mean": float(g["K_prime"].mean()),
                "lambda_event_count_max": int(g["lambda_event_count"].max()),
                "prime_event_count_max": int(g["prime_event_count"].max()),
                "lambda_weight_sum_max": float(g["lambda_event_weight_sum"].max()),
                "max_lambda_gap_max": float(g["max_lambda_gap"].max()),
                "sample_count_over_h_max": float(g["sample_count_over_h"].max()),
                "effective_support_frac_max": float(g["B_prime_effective_support_frac"].max()),
                "target_failure_count": int(g["K_prime_above_65_flag"].sum()),
            }
        )
    return out


def main() -> None:
    samples_path = OUT_DIR / "prime_mesh_r2q_hexc_bridge_path_samples_v1.csv"
    component_path = OUT_DIR / "prime_mesh_r2q_hexc_dn_residual_component_rows.csv"
    primitive_path = OUT_DIR / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv"
    for path in [samples_path, component_path, primitive_path]:
        if not path.exists():
            raise FileNotFoundError(path)

    samples = pd.read_csv(samples_path)
    component = pd.read_csv(component_path)
    primitive = pd.read_csv(primitive_path)

    max_hi = int((samples["y"] + samples["h"]).max())
    base_primes = dncomp.sieve_primes_upto(int(math.isqrt(max_hi)) + 2)

    component_cols = [
        "candidate_id",
        "K_prime",
        "E_prime",
        "C_prime",
        "B_prime_abs_max",
        "K_comp",
        "K_total",
        "post_P0_flag",
        "component_proof_source",
    ]
    comp_small = component[[c for c in component_cols if c in component.columns]].drop_duplicates("candidate_id")
    primitive_cols = [
        "candidate_id",
        "Q_R2Q",
        "Q_delta_D",
        "Q_exc",
        "epsilon",
        "E_theta",
        "E_theta_sign",
        "threshold_relevant_flag",
        "forbidden_flag",
        "finite_zone_flag",
        "positive_harmless_flag",
        "negative_transfer_flag",
        "O2_B3_repaid_flag",
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
        offsets = g["offset"].astype(int).to_numpy()
        if offsets[0] != 0:
            offsets = np.concatenate(([0], offsets))
        if offsets[-1] != h:
            raise ValueError(f"Endpoint offset mismatch for {candidate_id}: {offsets[-1]} != {h}")

        n_values, _comp_inc, lam, _inc = dncomp.compute_local_components(y + 1, y + h, dncomp.DEFAULT_C, base_primes)
        lam_prefix = np.concatenate(([0.0], np.cumsum(lam)))
        lam_total = float(lam_prefix[h])
        frac = offsets.astype(float) / float(h)
        b_prime = lam_prefix[offsets] - frac * lam_total
        e_prime = float(np.dot(b_prime, b_prime))
        k_prime = e_prime / h
        c_prime = math.sqrt(k_prime)

        event_mask = lam > 0
        event_offsets = n_values[event_mask] - y
        event_weights = lam[event_mask]
        prime_mask = np.zeros_like(event_mask, dtype=np.bool_)
        if event_mask.any():
            event_n = n_values[event_mask].astype(np.float64)
            prime_mask_events = np.isclose(event_weights, np.log(event_n), rtol=0.0, atol=1.0e-12)
            prime_mask[event_mask] = prime_mask_events

        if len(event_offsets):
            gaps = np.diff(event_offsets)
            first_event = int(event_offsets[0])
            last_event = int(event_offsets[-1])
            span = int(last_event - first_event) if len(event_offsets) > 1 else 0
            max_gap = int(gaps.max()) if len(gaps) else int(h)
            mean_gap = float(gaps.mean()) if len(gaps) else float("nan")
            min_gap = int(gaps.min()) if len(gaps) else int(h)
        else:
            first_event = -1
            last_event = -1
            span = 0
            max_gap = h
            mean_gap = float("nan")
            min_gap = h

        abs_b = np.abs(b_prime)
        abs_max = float(abs_b.max()) if len(abs_b) else 0.0
        effective_support = e_prime / max(abs_max * abs_max, EPS) if abs_max > 0 else 0.0
        peak_idx = int(abs_b.argmax()) if len(abs_b) else 0
        peak_offset = int(offsets[peak_idx]) if len(offsets) else 0

        event_count = int(event_mask.sum())
        prime_count = int(prime_mask.sum())
        prime_power_count = event_count - prime_count
        weight_sum = float(event_weights.sum()) if len(event_weights) else 0.0
        weight_sq_sum = float(np.dot(event_weights, event_weights)) if len(event_weights) else 0.0
        weight_max = float(event_weights.max()) if len(event_weights) else 0.0
        sample_count = int(len(offsets))

        # Crude candidate bounds. These are intentionally simple diagnostics,
        # not claimed sharp inequalities.
        single_shock_bound_K = sample_count * (weight_max**2) / h if h else float("nan")
        event_l2_bound_K = sample_count * weight_sq_sum / h if h else float("nan")
        total_mass_bound_K = sample_count * (weight_sum**2) / h if h else float("nan")
        event_count_log_bound_K = sample_count * event_count * (math.log(max(p_star, 3)) ** 2) / h if h else float("nan")

        rows.append(
            {
                "candidate_id": candidate_id,
                "block_id": block_id,
                "x": p_star,
                "y": y,
                "h": h,
                "p_star": p_star,
                "post_P0_flag": bool(p_star >= P0),
                "sample_count": sample_count,
                "sample_count_over_h": sample_count / h if h else float("nan"),
                "L_total": lam_total,
                "lambda_event_count": event_count,
                "prime_event_count": prime_count,
                "prime_power_event_count": prime_power_count,
                "lambda_event_weight_sum": weight_sum,
                "lambda_event_weight_sq_sum": weight_sq_sum,
                "lambda_event_weight_max": weight_max,
                "first_lambda_event_offset": first_event,
                "last_lambda_event_offset": last_event,
                "lambda_event_span": span,
                "max_lambda_gap": max_gap,
                "mean_lambda_gap": mean_gap,
                "min_lambda_gap": min_gap,
                "K_prime": k_prime,
                "E_prime": e_prime,
                "C_prime": c_prime,
                "B_prime_abs_max": abs_max,
                "B_prime_abs_mean": float(abs_b.mean()) if len(abs_b) else 0.0,
                "B_prime_abs_q95": qtile(abs_b, 0.95),
                "B_prime_abs_q99": qtile(abs_b, 0.99),
                "B_prime_effective_support": effective_support,
                "B_prime_effective_support_frac": effective_support / sample_count if sample_count else float("nan"),
                "B_prime_peak_offset": peak_offset,
                "B_prime_peak_position_fraction": peak_offset / h if h else float("nan"),
                "linear_mass_slope": lam_total / h if h else float("nan"),
                "lambda_density": event_count / h if h else float("nan"),
                "prime_density": prime_count / h if h else float("nan"),
                "single_shock_bound_K": single_shock_bound_K,
                "event_l2_bound_K": event_l2_bound_K,
                "total_mass_bound_K": total_mass_bound_K,
                "event_count_log_bound_K": event_count_log_bound_K,
                "single_shock_bound_pass_flag": bool(single_shock_bound_K <= K_PRIME_TARGET),
                "event_l2_bound_pass_flag": bool(event_l2_bound_K <= K_PRIME_TARGET),
                "total_mass_bound_pass_flag": bool(total_mass_bound_K <= K_PRIME_TARGET),
                "event_count_log_bound_pass_flag": bool(event_count_log_bound_K <= K_PRIME_TARGET),
                "K_prime_above_65_flag": bool(k_prime > K_PRIME_TARGET),
            }
        )

        if idx % 250 == 0:
            print(f"[progress] processed {idx}/{len(grouped)} candidates in {time.time()-start:.1f}s")

    rows_df = pd.DataFrame(rows)
    rows_df = rows_df.merge(comp_small, on="candidate_id", how="left", suffixes=("", "_component"))
    rows_df = rows_df.merge(prim_small, on="candidate_id", how="left", suffixes=("", "_primitive"))

    # Reconcile with component audit K_prime.
    if "K_prime_component" in rows_df:
        rows_df["K_prime_component_delta"] = rows_df["K_prime"] - rows_df["K_prime_component"]
        k_delta_max = float(rows_df["K_prime_component_delta"].abs().max())
    else:
        k_delta_max = float("nan")

    post = rows_df[rows_df["post_P0_flag"] == True]
    if len(post) == 0:
        raise RuntimeError("No post-P0 rows found")

    if int(post["event_l2_bound_pass_flag"].sum()) == len(post):
        route = "event_l2_bound"
    elif int(post["single_shock_bound_pass_flag"].sum()) == len(post):
        route = "single_shock_bound"
    elif int(post["K_prime_above_65_flag"].sum()) == 0:
        route = "sampled_bridge_direct"
    else:
        route = "repair_needed"

    summary = {
        "rows": int(len(rows_df)),
        "post_P0_rows": int(len(post)),
        "K_prime_target": K_PRIME_TARGET,
        "K_prime_component_delta_abs_max": k_delta_max,
        "K_prime_max": float(rows_df["K_prime"].max()),
        "post_P0_K_prime_max": float(post["K_prime"].max()),
        "post_P0_C_prime_max": float(post["C_prime"].max()),
        "post_P0_K_prime_above_65_count": int(post["K_prime_above_65_flag"].sum()),
        "post_P0_lambda_event_count_max": int(post["lambda_event_count"].max()),
        "post_P0_prime_event_count_max": int(post["prime_event_count"].max()),
        "post_P0_prime_power_event_count_max": int(post["prime_power_event_count"].max()),
        "post_P0_lambda_weight_sum_max": float(post["lambda_event_weight_sum"].max()),
        "post_P0_lambda_weight_sq_sum_max": float(post["lambda_event_weight_sq_sum"].max()),
        "post_P0_lambda_event_weight_max": float(post["lambda_event_weight_max"].max()),
        "post_P0_max_lambda_gap_max": int(post["max_lambda_gap"].max()),
        "post_P0_sample_count_max": int(post["sample_count"].max()),
        "post_P0_sample_count_over_h_max": float(post["sample_count_over_h"].max()),
        "post_P0_effective_support_frac_max": float(post["B_prime_effective_support_frac"].max()),
        "post_P0_effective_support_frac_mean": float(post["B_prime_effective_support_frac"].mean()),
        "post_P0_single_shock_bound_K_max": float(post["single_shock_bound_K"].max()),
        "post_P0_event_l2_bound_K_max": float(post["event_l2_bound_K"].max()),
        "post_P0_total_mass_bound_K_max": float(post["total_mass_bound_K"].max()),
        "post_P0_event_count_log_bound_K_max": float(post["event_count_log_bound_K"].max()),
        "post_P0_single_shock_bound_pass_count": int(post["single_shock_bound_pass_flag"].sum()),
        "post_P0_event_l2_bound_pass_count": int(post["event_l2_bound_pass_flag"].sum()),
        "post_P0_total_mass_bound_pass_count": int(post["total_mass_bound_pass_flag"].sum()),
        "post_P0_event_count_log_bound_pass_count": int(post["event_count_log_bound_pass_flag"].sum()),
        "threshold_relevant_rows": int(rows_df.get("threshold_relevant_flag", pd.Series(False, index=rows_df.index)).map(boolish).sum()),
        "threshold_relevant_K_prime_max": float(rows_df[rows_df.get("threshold_relevant_flag", False).map(boolish)]["K_prime"].max())
        if "threshold_relevant_flag" in rows_df and rows_df.get("threshold_relevant_flag", False).map(boolish).any()
        else float("nan"),
        "forbidden_rows": int(rows_df.get("forbidden_flag", pd.Series(False, index=rows_df.index)).map(boolish).sum()),
        "forbidden_K_prime_max": float(rows_df[rows_df.get("forbidden_flag", False).map(boolish)]["K_prime"].max())
        if "forbidden_flag" in rows_df and rows_df.get("forbidden_flag", False).map(boolish).any()
        else float("nan"),
        "best_proof_route_candidate": route,
        "primeshock_bridge_failures": int(rows_df["K_prime_above_65_flag"].sum()),
        "post_P0_primeshock_bridge_failures": int(post["K_prime_above_65_flag"].sum()),
        "pass_primeshock_bridge_profile_empirical": bool(int(post["K_prime_above_65_flag"].sum()) == 0 and (not math.isfinite(k_delta_max) or k_delta_max <= 1.0e-8)),
    }

    by_rows: List[Dict[str, object]] = []
    for key in ["post_P0_flag", "E_theta_sign", "threshold_relevant_flag", "forbidden_flag", "finite_zone_flag", "row_status"]:
        by_rows.extend(aggregate(rows_df, key))

    extremes = []
    metrics = [
        "K_prime",
        "lambda_event_count",
        "lambda_event_weight_sum",
        "lambda_event_weight_sq_sum",
        "lambda_event_weight_max",
        "max_lambda_gap",
        "sample_count_over_h",
        "B_prime_effective_support_frac",
        "single_shock_bound_K",
        "event_l2_bound_K",
        "total_mass_bound_K",
    ]
    for metric in metrics:
        ascending = False
        take = rows_df.sort_values(metric, ascending=ascending).head(20)
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
                    "lambda_event_count": r["lambda_event_count"],
                    "prime_event_count": r["prime_event_count"],
                    "prime_power_event_count": r["prime_power_event_count"],
                    "sample_count": r["sample_count"],
                    "B_prime_effective_support_frac": r["B_prime_effective_support_frac"],
                }
            )

    failures = rows_df[(rows_df["post_P0_flag"] == True) & (rows_df["K_prime_above_65_flag"] == True)].copy()

    paths = {
        "script": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_bridge_profile_audit.py",
        "summary": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_bridge_profile_summary.csv",
        "rows": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_bridge_profile_rows.csv",
        "by_regime": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_bridge_profile_by_regime.csv",
        "extremes": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_bridge_profile_extremes.csv",
        "failures": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_bridge_profile_failures.csv",
        "note": OUT_DIR / "Prime_Mesh_R2Q_HExc_PrimeShockBridge_Profile_Audit_v1.md",
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
