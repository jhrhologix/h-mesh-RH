#!/usr/bin/env python3
"""
Prime Mesh R2Q - H-Exc D_N residual component audit.

Decomposes the sampled bridge

    B_J(t) = D_N(t) - ell_J(t)

into centered composite and prime-shock bridges using the SR11 increment

    d_N(n) = C_N E_mod(n) - Lambda(n).

All outputs are written beside this script.
"""

from __future__ import annotations

import csv
import math
import time
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd


OUT_DIR = Path(__file__).resolve().parent
DEFAULT_C = 1.29340026
P0 = 500_000_000
RECON_TOL = 1.0e-5


def sieve_primes_upto(n: int) -> np.ndarray:
    n = int(n)
    if n < 2:
        return np.array([], dtype=np.int64)
    is_prime = np.ones(n + 1, dtype=np.bool_)
    is_prime[:2] = False
    for p in range(2, int(math.isqrt(n)) + 1):
        if is_prime[p]:
            is_prime[p * p : n + 1 : p] = False
    return np.nonzero(is_prime)[0].astype(np.int64)


def local_spf(lo: int, hi: int, base_primes: np.ndarray) -> np.ndarray:
    """Return smallest prime factor for every n in [lo, hi]."""
    size = hi - lo + 1
    vals = np.arange(lo, hi + 1, dtype=np.int64)
    spf = np.zeros(size, dtype=np.int64)
    limit = int(math.isqrt(hi)) + 1
    for p64 in base_primes:
        p = int(p64)
        if p > limit:
            break
        start = max(p * p, ((lo + p - 1) // p) * p)
        if start > hi:
            continue
        idxs = np.arange(start - lo, size, p, dtype=np.int64)
        unset = spf[idxs] == 0
        spf[idxs[unset]] = p
    unset = spf == 0
    spf[unset] = vals[unset]
    spf[vals <= 1] = 1
    return spf


def lambda_array(lo: int, hi: int, spf: np.ndarray) -> np.ndarray:
    """Von Mangoldt Lambda(n): log p if n is a prime power, otherwise 0."""
    vals = np.arange(lo, hi + 1, dtype=np.int64)
    lam = np.zeros(len(vals), dtype=np.float64)
    for i, n64 in enumerate(vals):
        n = int(n64)
        if n < 2:
            continue
        p = int(spf[i])
        m = n
        while m % p == 0:
            m //= p
        if m == 1:
            lam[i] = math.log(p)
    return lam


def compute_local_components(lo_step: int, hi_step: int, c_n: float, base_primes: np.ndarray):
    """
    Compute e_N(n)=C_N E_mod(n), Lambda(n), and d_N(n)=e_N(n)-Lambda(n)
    on [lo_step, hi_step].
    """
    lo_all = max(1, lo_step - 1)
    hi_all = hi_step
    spf_all = local_spf(lo_all, hi_all, base_primes)
    offset = lo_all
    n_values = np.arange(lo_step, hi_step + 1, dtype=np.int64)
    e_mod = np.zeros(len(n_values), dtype=np.float64)

    for idx, n64 in enumerate(n_values):
        n = int(n64)
        spf_n = int(spf_all[n - offset])
        if n - 1 < 1:
            spf_prev = 1
        else:
            spf_prev = int(spf_all[n - 1 - offset])
        if spf_prev <= 1:
            g = 0.0
        else:
            rem = spf_n % spf_prev
            dist = min(rem, spf_prev - rem)
            g = dist / spf_prev
        e_mod[idx] = g * g

    spf_steps = spf_all[(lo_step - offset) : (hi_step - offset + 1)]
    lam = lambda_array(lo_step, hi_step, spf_steps)
    comp = c_n * e_mod
    inc = comp - lam
    return n_values, comp, lam, inc


def bool_val(x) -> bool:
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if pd.isna(x):
        return False
    if isinstance(x, (int, float, np.integer, np.floating)):
        return bool(x)
    return str(x).strip().lower() in {"true", "1", "yes", "y"}


def safe_float(x, default=float("nan")) -> float:
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


def energy_stats(comp_bridge: np.ndarray, prime_bridge: np.ndarray, total_bridge: np.ndarray, h: int):
    e_comp = float(np.dot(comp_bridge, comp_bridge))
    e_prime = float(np.dot(prime_bridge, prime_bridge))
    inner = float(np.dot(comp_bridge, prime_bridge))
    e_total = float(np.dot(total_bridge, total_bridge))
    unreduced = e_comp + e_prime
    denom = math.sqrt(max(e_comp * e_prime, 0.0))
    cos = inner / denom if denom > 0 else float("nan")
    cancellation_fraction = 1.0 - e_total / unreduced if unreduced > 0 else float("nan")
    return {
        "E_comp": e_comp,
        "E_prime": e_prime,
        "inner_comp_prime": inner,
        "E_total": e_total,
        "E_unreduced": unreduced,
        "cancel_term_2inner": 2.0 * inner,
        "cos_comp_prime": cos,
        "cancellation_fraction": cancellation_fraction,
        "K_comp": e_comp / h if h > 0 else float("nan"),
        "K_prime": e_prime / h if h > 0 else float("nan"),
        "K_total": e_total / h if h > 0 else float("nan"),
        "K_unreduced": unreduced / h if h > 0 else float("nan"),
        "C_comp": math.sqrt(e_comp / h) if h > 0 and e_comp >= 0 else float("nan"),
        "C_prime": math.sqrt(e_prime / h) if h > 0 and e_prime >= 0 else float("nan"),
        "C_total": math.sqrt(e_total / h) if h > 0 and e_total >= 0 else float("nan"),
        "C_unreduced": math.sqrt(unreduced / h) if h > 0 and unreduced >= 0 else float("nan"),
    }


def classify_source(row: Dict[str, object]) -> str:
    if row["K_comp"] + row["K_prime"] <= 100.0:
        return "smallness_driven"
    if row["K_total"] <= 100.0 and row["inner_comp_prime"] > 0 and row["cancellation_fraction"] > 0.25:
        return "cancellation_driven"
    if row["K_total"] <= 100.0:
        return "mixed_safe"
    return "failure"


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


def aggregate_by(rows: pd.DataFrame, key: str) -> List[Dict[str, object]]:
    out = []
    if key not in rows.columns:
        return out
    for val, g in rows.groupby(key, dropna=False):
        out.append(
            {
                "group_field": key,
                "group_value": val,
                "rows": int(len(g)),
                "post_P0_rows": int(g["post_P0_flag"].sum()) if "post_P0_flag" in g else 0,
                "K_total_max": float(g["K_total"].max()),
                "K_unreduced_max": float(g["K_unreduced"].max()),
                "K_comp_max": float(g["K_comp"].max()),
                "K_prime_max": float(g["K_prime"].max()),
                "C_total_max": float(g["C_total"].max()),
                "cancellation_fraction_min": float(g["cancellation_fraction"].min()),
                "cancellation_fraction_mean": float(g["cancellation_fraction"].mean()),
                "cos_comp_prime_mean": float(g["cos_comp_prime"].mean()),
                "reconstruction_abs_error_max": float(g["reconstruction_abs_error_max"].max()),
                "failure_count": int(g["component_audit_failure_flag"].sum()),
            }
        )
    return out


def update_manifest(created: Iterable[Path]) -> None:
    manifest = OUT_DIR / "deposit_manifest.csv"
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    existing = pd.read_csv(manifest) if manifest.exists() else pd.DataFrame()
    rows = [] if existing.empty else existing.to_dict("records")
    by_name = {str(r.get("filename")): i for i, r in enumerate(rows)}
    for path in created:
        rec = {
            "filename": path.name,
            "path": str(path),
            "bytes": path.stat().st_size if path.exists() else 0,
            "status": "new",
            "updated_at": now,
            "note": "H-Exc D_N residual component audit output",
        }
        if path.name in by_name:
            rows[by_name[path.name]] = rec
        else:
            rows.append(rec)
    write_csv(manifest, rows)


def make_note(summary: Dict[str, object], paths: Dict[str, Path]) -> str:
    verdict = "PASS" if summary["pass_hexc_dn_residual_component_empirical"] else "REPAIR NEEDED"
    lines = [
        "# Prime Mesh R2Q - H-Exc D_N Residual Component Audit v1",
        "",
        f"**Status:** {verdict}",
        "",
        "## Purpose",
        "",
        "This audit decomposes the sampled H-Exc bridge residual",
        "",
        "```text",
        "B_J(t)=D_N(t)-ell_J(t)=B_comp(t)-B_prime(t)",
        "```",
        "",
        "using the SR11 increment definition",
        "",
        "```text",
        "d_N(n)=C_N E_mod(n)-Lambda(n).",
        "```",
        "",
        "## Main Results",
        "",
        "```text",
        f"rows = {summary['rows']}",
        f"post_P0_rows = {summary['post_P0_rows']}",
        f"C_N_used = {summary['C_N_used']}",
        f"path_reconstruction_abs_error_max = {summary['path_reconstruction_abs_error_max']}",
        f"post_P0_K_total_max = {summary['post_P0_K_total_max']}",
        f"post_P0_C_total_max = {summary['post_P0_C_total_max']}",
        f"post_P0_K_unreduced_max = {summary['post_P0_K_unreduced_max']}",
        f"post_P0_K_comp_max = {summary['post_P0_K_comp_max']}",
        f"post_P0_K_prime_max = {summary['post_P0_K_prime_max']}",
        f"post_P0_cancellation_fraction_min = {summary['post_P0_cancellation_fraction_min']}",
        f"post_P0_cancellation_fraction_mean = {summary['post_P0_cancellation_fraction_mean']}",
        f"post_P0_cos_comp_prime_mean = {summary['post_P0_cos_comp_prime_mean']}",
        f"post_P0_source_smallness_rows = {summary['post_P0_source_smallness_rows']}",
        f"post_P0_source_cancellation_rows = {summary['post_P0_source_cancellation_rows']}",
        f"post_P0_source_mixed_safe_rows = {summary['post_P0_source_mixed_safe_rows']}",
        f"component_identity_failures = {summary['component_identity_failures']}",
        f"post_P0_component_bound_failures = {summary['post_P0_component_bound_failures']}",
        f"best_proof_source_post_P0 = {summary['best_proof_source_post_P0']}",
        f"pass_hexc_dn_residual_component_empirical = {summary['pass_hexc_dn_residual_component_empirical']}",
        "```",
        "",
        "## Interpretation",
        "",
    ]
    source = summary["best_proof_source_post_P0"]
    if source == "smallness_driven":
        lines += [
            "The post-P0 H-Exc endpoint-residual bound is empirically component-smallness driven:",
            "both centered composite response and centered prime shock remain small enough that their",
            "unreduced energy already stays inside the `100h` budget.",
        ]
    elif source == "cancellation_driven":
        lines += [
            "The post-P0 H-Exc endpoint-residual bound is empirically cancellation-driven:",
            "the component energies can exceed the `100h` budget before subtraction, but",
            "the composite and prime bridges are positively aligned so `B_comp - B_prime` is small.",
        ]
    else:
        lines += [
            "The post-P0 H-Exc endpoint-residual bound appears mixed: component smallness alone",
            "does not uniformly explain the result, but the total centered bridge remains within",
            "the audited `100h` envelope.",
        ]
    lines += [
        "",
        "## Files",
        "",
    ]
    for label, path in paths.items():
        lines.append(f"- `{label}`: `{path.name}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    samples_path = OUT_DIR / "prime_mesh_r2q_hexc_bridge_path_samples_v1.csv"
    primitive_path = OUT_DIR / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv"
    energy_path = OUT_DIR / "prime_mesh_r2q_hexc_local_affinity_energybudget_rows.csv"

    for p in [samples_path, primitive_path, energy_path]:
        if not p.exists():
            raise FileNotFoundError(p)

    samples = pd.read_csv(samples_path)
    primitive = pd.read_csv(primitive_path)
    energy = pd.read_csv(energy_path)

    required_cols = {"candidate_id", "block_id", "p_star", "y", "h", "offset", "diff"}
    missing = required_cols - set(samples.columns)
    if missing:
        raise ValueError(f"Missing columns in path samples: {sorted(missing)}")

    max_hi = int((samples["y"] + samples["h"]).max())
    base_primes = sieve_primes_upto(int(math.isqrt(max_hi)) + 2)

    primitive_cols = [
        "candidate_id",
        "Q_R2Q",
        "Q_delta_D",
        "Q_exc",
        "E_theta",
        "E_theta_sign",
        "threshold_relevant_flag",
        "forbidden_flag",
        "finite_zone_flag",
        "post_P0_flag",
        "positive_harmless_flag",
        "negative_transfer_flag",
        "O2_B3_repaid_flag",
        "row_status",
    ]
    primitive_small = primitive[[c for c in primitive_cols if c in primitive.columns]].drop_duplicates("candidate_id")
    energy_cols = [
        "candidate_id",
        "K_R",
        "C_bridge",
        "C_end",
        "E_end_over_h",
        "eta_aff",
        "capture_aff",
        "row_regime",
        "h_bin_eb",
        "p_star_bin_eb",
    ]
    energy_small = energy[[c for c in energy_cols if c in energy.columns]].drop_duplicates("candidate_id")

    rows: List[Dict[str, object]] = []
    start = time.time()
    grouped = samples.groupby("candidate_id", sort=False)

    for idx, (candidate_id, g) in enumerate(grouped, start=1):
        g = g.sort_values("offset")
        y = int(g["y"].iloc[0])
        h = int(g["h"].iloc[0])
        p_star = int(g["p_star"].iloc[0])
        block_id = g["block_id"].iloc[0]
        offsets = g["offset"].astype(int).to_numpy()
        exported_diff = g["diff"].astype(float).to_numpy()

        if h <= 0:
            raise ValueError(f"Nonpositive h for {candidate_id}: {h}")
        if offsets[0] != 0:
            offsets = np.concatenate(([0], offsets))
            exported_diff = np.concatenate(([0.0], exported_diff))
        if offsets[-1] != h:
            raise ValueError(f"Endpoint offset mismatch for {candidate_id}: max offset {offsets[-1]} vs h {h}")

        _, comp_inc, prime_inc, total_inc = compute_local_components(y + 1, y + h, DEFAULT_C, base_primes)
        comp_prefix = np.concatenate(([0.0], np.cumsum(comp_inc)))
        prime_prefix = np.concatenate(([0.0], np.cumsum(prime_inc)))
        total_prefix = np.concatenate(([0.0], np.cumsum(total_inc)))

        comp_total = float(comp_prefix[h])
        prime_total = float(prime_prefix[h])
        total_total = float(total_prefix[h])
        frac = offsets.astype(float) / float(h)

        b_comp = comp_prefix[offsets] - frac * comp_total
        b_prime = prime_prefix[offsets] - frac * prime_total
        b_total = b_comp - b_prime

        stats = energy_stats(b_comp, b_prime, b_total, h)
        recon_error = b_total - exported_diff
        abs_recon = np.abs(recon_error)
        row = {
            "candidate_id": candidate_id,
            "block_id": block_id,
            "p_star": p_star,
            "y": y,
            "h": h,
            "sample_count": int(len(offsets)),
            "post_P0_flag": bool(p_star >= P0),
            "C_N_used": DEFAULT_C,
            "component_total_delta": total_total,
            "component_comp_delta": comp_total,
            "component_prime_delta": prime_total,
            "B_comp_abs_max": float(np.max(np.abs(b_comp))),
            "B_prime_abs_max": float(np.max(np.abs(b_prime))),
            "B_total_abs_max": float(np.max(np.abs(b_total))),
            "reconstruction_abs_error_max": float(abs_recon.max()),
            "reconstruction_abs_error_mean": float(abs_recon.mean()),
            "reconstruction_l2_error": float(math.sqrt(float(np.dot(recon_error, recon_error)))),
            "component_identity_pass_flag": bool(abs_recon.max() <= RECON_TOL),
        }
        row.update(stats)
        row["smallness_driven_flag"] = bool(row["K_comp"] + row["K_prime"] <= 100.0)
        row["cancellation_driven_flag"] = bool(row["K_comp"] + row["K_prime"] > 100.0 and row["K_total"] <= 100.0 and row["inner_comp_prime"] > 0)
        row["mixed_safe_flag"] = bool(row["K_total"] <= 100.0 and not row["smallness_driven_flag"] and not row["cancellation_driven_flag"])
        row["component_proof_source"] = classify_source(row)
        row["post_P0_component_bound_failure_flag"] = bool(row["post_P0_flag"] and row["K_total"] > 100.0)
        row["component_audit_failure_flag"] = bool((not row["component_identity_pass_flag"]) or row["post_P0_component_bound_failure_flag"])
        rows.append(row)

        if idx % 250 == 0:
            print(f"[progress] processed {idx}/{len(grouped)} candidates in {time.time()-start:.1f}s")

    rows_df = pd.DataFrame(rows)
    rows_df = rows_df.merge(primitive_small, on="candidate_id", how="left", suffixes=("", "_primitive"))
    rows_df = rows_df.merge(energy_small, on="candidate_id", how="left", suffixes=("", "_energy"))

    # Summary.
    post = rows_df[rows_df["post_P0_flag"] == True]
    source_counts = post["component_proof_source"].value_counts().to_dict()
    failures = rows_df[rows_df["component_audit_failure_flag"] == True].copy()
    best_source = "mixed"
    if len(post):
        if source_counts.get("smallness_driven", 0) == len(post):
            best_source = "smallness_driven"
        elif source_counts.get("cancellation_driven", 0) == len(post):
            best_source = "cancellation_driven"
        elif source_counts.get("smallness_driven", 0) + source_counts.get("cancellation_driven", 0) == len(post):
            best_source = "smallness_plus_cancellation"
        else:
            best_source = "mixed"

    summary = {
        "rows": int(len(rows_df)),
        "post_P0_rows": int(len(post)),
        "C_N_used": DEFAULT_C,
        "path_reconstruction_abs_error_max": float(rows_df["reconstruction_abs_error_max"].max()),
        "path_reconstruction_l2_error_max": float(rows_df["reconstruction_l2_error"].max()),
        "component_identity_failures": int((~rows_df["component_identity_pass_flag"]).sum()),
        "K_total_max": float(rows_df["K_total"].max()),
        "C_total_max": float(rows_df["C_total"].max()),
        "K_unreduced_max": float(rows_df["K_unreduced"].max()),
        "K_comp_max": float(rows_df["K_comp"].max()),
        "K_prime_max": float(rows_df["K_prime"].max()),
        "post_P0_K_total_max": float(post["K_total"].max()) if len(post) else float("nan"),
        "post_P0_C_total_max": float(post["C_total"].max()) if len(post) else float("nan"),
        "post_P0_K_unreduced_max": float(post["K_unreduced"].max()) if len(post) else float("nan"),
        "post_P0_C_unreduced_max": float(post["C_unreduced"].max()) if len(post) else float("nan"),
        "post_P0_K_comp_max": float(post["K_comp"].max()) if len(post) else float("nan"),
        "post_P0_K_prime_max": float(post["K_prime"].max()) if len(post) else float("nan"),
        "post_P0_cancellation_fraction_min": float(post["cancellation_fraction"].min()) if len(post) else float("nan"),
        "post_P0_cancellation_fraction_mean": float(post["cancellation_fraction"].mean()) if len(post) else float("nan"),
        "post_P0_cos_comp_prime_min": float(post["cos_comp_prime"].min()) if len(post) else float("nan"),
        "post_P0_cos_comp_prime_mean": float(post["cos_comp_prime"].mean()) if len(post) else float("nan"),
        "post_P0_source_smallness_rows": int(source_counts.get("smallness_driven", 0)),
        "post_P0_source_cancellation_rows": int(source_counts.get("cancellation_driven", 0)),
        "post_P0_source_mixed_safe_rows": int(source_counts.get("mixed_safe", 0)),
        "post_P0_component_bound_failures": int(post["post_P0_component_bound_failure_flag"].sum()) if len(post) else 0,
        "component_audit_failures": int(rows_df["component_audit_failure_flag"].sum()),
        "best_proof_source_post_P0": best_source,
        "pass_hexc_dn_residual_component_empirical": bool(rows_df["component_audit_failure_flag"].sum() == 0),
    }

    by_rows: List[Dict[str, object]] = []
    for key in ["post_P0_flag", "component_proof_source", "row_regime", "h_bin_eb", "p_star_bin_eb", "E_theta_sign"]:
        by_rows.extend(aggregate_by(rows_df, key))

    extremes = []
    for metric in [
        "K_total",
        "K_unreduced",
        "K_comp",
        "K_prime",
        "C_total",
        "cancellation_fraction",
        "cos_comp_prime",
        "reconstruction_abs_error_max",
    ]:
        if metric not in rows_df.columns:
            continue
        ascending = metric in {"cancellation_fraction", "cos_comp_prime"}
        take = rows_df.sort_values(metric, ascending=ascending).head(20)
        for rank, (_, r) in enumerate(take.iterrows(), start=1):
            extremes.append(
                {
                    "metric": metric,
                    "rank": rank,
                    "candidate_id": r.get("candidate_id"),
                    "block_id": r.get("block_id"),
                    "p_star": r.get("p_star"),
                    "h": r.get("h"),
                    "post_P0_flag": r.get("post_P0_flag"),
                    "value": r.get(metric),
                    "K_total": r.get("K_total"),
                    "K_unreduced": r.get("K_unreduced"),
                    "K_comp": r.get("K_comp"),
                    "K_prime": r.get("K_prime"),
                    "cancellation_fraction": r.get("cancellation_fraction"),
                    "cos_comp_prime": r.get("cos_comp_prime"),
                    "component_proof_source": r.get("component_proof_source"),
                }
            )

    paths = {
        "script": OUT_DIR / "prime_mesh_r2q_hexc_dn_residual_component_audit.py",
        "summary": OUT_DIR / "prime_mesh_r2q_hexc_dn_residual_component_summary.csv",
        "rows": OUT_DIR / "prime_mesh_r2q_hexc_dn_residual_component_rows.csv",
        "by_regime": OUT_DIR / "prime_mesh_r2q_hexc_dn_residual_component_by_regime.csv",
        "extremes": OUT_DIR / "prime_mesh_r2q_hexc_dn_residual_component_extremes.csv",
        "failures": OUT_DIR / "prime_mesh_r2q_hexc_dn_residual_component_failures.csv",
        "note": OUT_DIR / "Prime_Mesh_R2Q_HExc_DN_Residual_Component_Audit_v1.md",
    }

    write_csv(paths["summary"], [summary])
    rows_df.to_csv(paths["rows"], index=False)
    write_csv(paths["by_regime"], by_rows)
    write_csv(paths["extremes"], extremes)
    failures.to_csv(paths["failures"], index=False)
    paths["note"].write_text(make_note(summary, paths), encoding="utf-8")
    update_manifest(paths.values())

    print("Wrote outputs:")
    for path in paths.values():
        print(path)
    print("Summary:")
    for k, v in summary.items():
        print(f"{k}={v}")


if __name__ == "__main__":
    main()
