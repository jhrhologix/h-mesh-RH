#!/usr/bin/env python3
"""
Prime Mesh R2Q - H-Exc PrimeShockBridge RayleighWeight audit.

Tests K_prime = rho_J * W_J where

    rho_J = (w^T G_J w)/(h ||w||_2^2)
    W_J = ||w||_2^2.
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
P0 = 500_000_000
K_TARGET = 65.0
RHO_CANDIDATES = [
    ("1_over_16", 1.0 / 16.0),
    ("0p063", 0.063),
    ("1_over_15", 1.0 / 15.0),
    ("0p07", 0.07),
    ("0p08", 0.08),
]
W0_CANDIDATES = [1000.0, 1024.0, 1040.0, 1100.0, 1200.0, 1500.0, 2048.0]


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
            "note": "H-Exc PrimeShockBridge RayleighWeight audit output",
        }
        if path.name in by_name:
            rows[by_name[path.name]] = rec
        else:
            rows.append(rec)
    write_csv(manifest, rows)


def make_note(summary: Dict[str, object], paths: Dict[str, Path]) -> str:
    status = "PASS" if summary["pass_rayleighweight_empirical"] else "REPAIR NEEDED"
    lines = [
        "# Prime Mesh R2Q - H-Exc PrimeShockBridge RayleighWeight Audit v1",
        "",
        f"**Status:** {status}",
        "",
        "## Purpose",
        "",
        "This audit tests the factorization:",
        "",
        "```text",
        "K_prime = (w^T G w / (h ||w||_2^2)) * ||w||_2^2 = rho_J * W_J.",
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
        "post_P0_rayleigh_over_h_max",
        "post_P0_weight_l2_sq_max",
        "post_P0_product_reconstruction_error_max",
        "independent_constants_close",
        "best_independent_rho",
        "best_independent_W0",
        "best_independent_product",
        "direct_product_max",
        "direct_product_margin_to_65",
        "best_theorem_form_recommended",
        "pass_rayleighweight_empirical",
    ]:
        lines.append(f"{key} = {summary.get(key)}")
    lines += [
        "```",
        "",
        "## Interpretation",
        "",
    ]
    if summary["independent_constants_close"]:
        lines.append("Independent constants `rho` and `W0` close the post-P0 theorem empirically.")
    else:
        lines.append(
            "Independent constants do not close cleanly: the worst Rayleigh factor and worst weight energy occur in different regimes, "
            "and their independent product is too large. The proof-facing theorem should use a direct Rayleigh-product bound."
        )
    lines += ["", "## Files", ""]
    for label, path in paths.items():
        lines.append(f"- `{label}`: `{path.name}`")
    lines.append("")
    return "\n".join(lines)


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
                "K_prime_max": float(g["K_prime"].max()),
                "rayleigh_over_h_max": float(g["rayleigh_over_h"].max()),
                "weight_l2_sq_max": float(g["weight_l2_sq"].max()),
                "direct_product_max": float(g["product_actual"].max()),
                "rho_1_over_16_fail_count": int(g["rayleigh_over_h"].gt(1.0 / 16.0).sum()),
                "W0_1040_fail_count": int(g["weight_l2_sq"].gt(1040.0).sum()),
            }
        )
    return out


def main() -> None:
    kernel_path = OUT_DIR / "prime_mesh_r2q_hexc_primeshock_kernelgram_rows.csv"
    primitive_path = OUT_DIR / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv"
    if not kernel_path.exists():
        raise FileNotFoundError(kernel_path)
    if not primitive_path.exists():
        raise FileNotFoundError(primitive_path)

    df = pd.read_csv(kernel_path)
    primitive = pd.read_csv(primitive_path)
    prim_small = primitive[[c for c in [
        "candidate_id", "Q_exc", "Q_energy_L2", "Q_R2Q", "Q_delta_D",
        "threshold_relevant_flag", "forbidden_flag", "finite_zone_flag", "row_status",
    ] if c in primitive.columns]].drop_duplicates("candidate_id")
    df = df.merge(prim_small, on="candidate_id", how="left", suffixes=("", "_primitive"))

    df["post_P0_flag"] = df["p_star"].ge(P0)
    df["weight_mean"] = df["weight_l1"] / df["event_count"].replace(0, np.nan)
    df["weight_sq_max"] = df["weight_max"] ** 2
    df["weight_l2_sq_over_event_count"] = df["weight_l2_sq"] / df["event_count"].replace(0, np.nan)
    df["rayleigh_over_h_times_16"] = df["rayleigh_over_h"] * 16.0
    df["rayleigh_margin_to_1_over_16"] = (1.0 / 16.0) - df["rayleigh_over_h"]
    df["rayleigh_margin_to_0p063"] = 0.063 - df["rayleigh_over_h"]
    df["rayleigh_margin_to_1_over_15"] = (1.0 / 15.0) - df["rayleigh_over_h"]
    df["product_1over16"] = (1.0 / 16.0) * df["weight_l2_sq"]
    df["product_0p063"] = 0.063 * df["weight_l2_sq"]
    df["product_1over15"] = (1.0 / 15.0) * df["weight_l2_sq"]
    df["product_0p07"] = 0.07 * df["weight_l2_sq"]
    df["product_actual"] = df["rayleigh_over_h"] * df["weight_l2_sq"]
    df["product_reconstruction_error"] = (df["product_actual"] - df["K_prime"]).abs()

    for name, rho in RHO_CANDIDATES:
        df[f"rho_pass_{name}"] = df["rayleigh_over_h"] <= rho
        df[f"product_bound_{name}"] = rho * df["weight_l2_sq"]
        df[f"product_bound_pass_{name}"] = df[f"product_bound_{name}"] <= K_TARGET
    for w0 in W0_CANDIDATES:
        label = str(w0).replace(".", "p")
        df[f"W0_pass_{label}"] = df["weight_l2_sq"] <= w0

    post = df[df["post_P0_flag"] == True].copy()
    constant_rows = []
    best = None
    for rho_name, rho in RHO_CANDIDATES:
        rho_pass_count = int(post["rayleigh_over_h"].le(rho).sum())
        for w0 in W0_CANDIDATES:
            W0_pass_count = int(post["weight_l2_sq"].le(w0).sum())
            product = rho * w0
            closes = bool(rho_pass_count == len(post) and W0_pass_count == len(post) and product <= K_TARGET)
            rec = {
                "rho_name": rho_name,
                "rho": rho,
                "W0": w0,
                "rho_W0": product,
                "rho_pass_count": rho_pass_count,
                "W0_pass_count": W0_pass_count,
                "post_P0_rows": int(len(post)),
                "closes_65": closes,
                "rho_fail_count": int(len(post) - rho_pass_count),
                "W0_fail_count": int(len(post) - W0_pass_count),
            }
            constant_rows.append(rec)
            if closes and (best is None or product < best["rho_W0"]):
                best = rec

    independent_close = best is not None
    summary = {
        "rows": int(len(df)),
        "post_P0_rows": int(len(post)),
        "post_P0_K_prime_max": float(post["K_prime"].max()),
        "post_P0_rayleigh_over_h_max": float(post["rayleigh_over_h"].max()),
        "post_P0_rayleigh_over_h_q99": float(post["rayleigh_over_h"].quantile(0.99)),
        "post_P0_weight_l2_sq_max": float(post["weight_l2_sq"].max()),
        "post_P0_weight_l2_sq_q99": float(post["weight_l2_sq"].quantile(0.99)),
        "post_P0_product_reconstruction_error_max": float(post["product_reconstruction_error"].max()),
        "rho_1_over_16_pass_count": int(post["rayleigh_over_h"].le(1.0 / 16.0).sum()),
        "rho_0p063_pass_count": int(post["rayleigh_over_h"].le(0.063).sum()),
        "rho_1_over_15_pass_count": int(post["rayleigh_over_h"].le(1.0 / 15.0).sum()),
        "W0_1000_pass_count": int(post["weight_l2_sq"].le(1000.0).sum()),
        "W0_1024_pass_count": int(post["weight_l2_sq"].le(1024.0).sum()),
        "W0_1040_pass_count": int(post["weight_l2_sq"].le(1040.0).sum()),
        "W0_1100_pass_count": int(post["weight_l2_sq"].le(1100.0).sum()),
        "independent_constants_close": independent_close,
        "best_independent_rho": best["rho"] if best else float("nan"),
        "best_independent_W0": best["W0"] if best else float("nan"),
        "best_independent_product": best["rho_W0"] if best else float("nan"),
        "direct_product_max": float(post["product_actual"].max()),
        "direct_product_margin_to_65": float(K_TARGET - post["product_actual"].max()),
        "threshold_relevant_rows": int(df.get("threshold_relevant_flag", pd.Series(False, index=df.index)).map(boolish).sum()),
        "threshold_relevant_product_actual_max": float(df[df.get("threshold_relevant_flag", pd.Series(False, index=df.index)).map(boolish)]["product_actual"].max())
        if "threshold_relevant_flag" in df and df["threshold_relevant_flag"].map(boolish).any()
        else math.nan,
        "forbidden_rows": int(df.get("forbidden_flag", pd.Series(False, index=df.index)).map(boolish).sum()),
        "forbidden_product_actual_max": float(df[df.get("forbidden_flag", pd.Series(False, index=df.index)).map(boolish)]["product_actual"].max())
        if "forbidden_flag" in df and df["forbidden_flag"].map(boolish).any()
        else math.nan,
        "best_theorem_form_recommended": "independent_rayleigh_weight_constants" if independent_close else "direct_rayleigh_product_bound",
        "rayleighweight_failures": int(post["product_actual"].gt(K_TARGET).sum()),
        "pass_rayleighweight_empirical": bool(post["product_actual"].le(K_TARGET).all() and post["product_reconstruction_error"].max() <= 1e-8),
    }

    by_rows: List[Dict[str, object]] = []
    for key in ["post_P0_flag", "E_theta_sign", "threshold_relevant_flag", "forbidden_flag", "finite_zone_flag", "row_status"]:
        by_rows.extend(aggregate(df, key))

    extremes = []
    for metric in [
        "product_actual",
        "rayleigh_over_h",
        "weight_l2_sq",
        "rayleigh_over_h_times_16",
        "product_1over16",
        "product_0p063",
        "top_eigenvector_alignment",
        "spectral_tightness",
    ]:
        take = df.replace([np.inf, -np.inf], np.nan).sort_values(metric, ascending=False).head(20)
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
                    "product_actual": r["product_actual"],
                    "rayleigh_over_h": r["rayleigh_over_h"],
                    "weight_l2_sq": r["weight_l2_sq"],
                    "event_count": r["event_count"],
                    "sample_count": r["sample_count"],
                }
            )

    failures = post[post["product_actual"] > K_TARGET].copy()

    paths = {
        "script": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighweight_audit.py",
        "summary": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighweight_summary.csv",
        "rows": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighweight_rows.csv",
        "constants": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighweight_constants.csv",
        "by_regime": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighweight_by_regime.csv",
        "extremes": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighweight_extremes.csv",
        "failures": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighweight_failures.csv",
        "note": OUT_DIR / "Prime_Mesh_R2Q_HExc_PrimeShockBridge_RayleighWeight_Audit_v1.md",
    }
    write_csv(paths["summary"], [summary])
    df.to_csv(paths["rows"], index=False)
    write_csv(paths["constants"], constant_rows)
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
