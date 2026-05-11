#!/usr/bin/env python3
"""
Prime Mesh R2Q - H-Exc PrimeShockBridge RayleighCoupling audit.

Profiles the coupling K_prime = rho_J * W_J and searches for proof-friendly
regime splits.
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


def corr(a: pd.Series, b: pd.Series, method: str = "pearson") -> float:
    x = pd.to_numeric(a, errors="coerce")
    y = pd.to_numeric(b, errors="coerce")
    m = x.notna() & y.notna() & np.isfinite(x) & np.isfinite(y)
    if m.sum() < 2:
        return math.nan
    return float(x[m].corr(y[m], method=method))


def bin_numeric(values: pd.Series, bins: List[float], labels: List[str]) -> pd.Series:
    return pd.cut(values, bins=bins, labels=labels, include_lowest=True, right=True).astype(str)


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
            "note": "H-Exc PrimeShockBridge RayleighCoupling audit output",
        }
        if path.name in by_name:
            rows[by_name[path.name]] = rec
        else:
            rows.append(rec)
    write_csv(manifest, rows)


def make_note(summary: Dict[str, object], paths: Dict[str, Path]) -> str:
    status = "PASS" if summary["pass_rayleighcoupling_empirical"] else "REPAIR NEEDED"
    lines = [
        "# Prime Mesh R2Q - H-Exc PrimeShockBridge RayleighCoupling Audit v1",
        "",
        f"**Status:** {status}",
        "",
        "## Purpose",
        "",
        "This audit profiles the coupling",
        "",
        "```text",
        "K_prime = rho_J W_J",
        "rho_J = w^T G_J w / (h ||w||_2^2)",
        "W_J = ||w||_2^2.",
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
        "post_P0_product_margin_min",
        "post_P0_corr_rho_W",
        "post_P0_corr_logrho_logW",
        "post_P0_spearman_rho_W",
        "post_P0_W_large_rows",
        "post_P0_W_large_rho_max",
        "post_P0_rho_large_rows",
        "post_P0_rho_large_W_max",
        "regime_split_candidate",
        "best_theorem_form_recommended",
        "pass_rayleighcoupling_empirical",
    ]:
        lines.append(f"{key} = {summary.get(key)}")
    lines += [
        "```",
        "",
        "## Interpretation",
        "",
    ]
    form = summary.get("best_theorem_form_recommended")
    if form == "two_regime_coupling":
        lines.append("A two-regime coupling theorem is supported: high weight forces tiny Rayleigh, while high Rayleigh occurs only at low weight.")
    elif form == "multi_regime_envelope":
        lines.append("A multi-regime envelope is supported more cleanly than a single two-regime split.")
    else:
        lines.append("The direct product bound remains the clean theorem object; simple regime splits are informative but not yet a full proof replacement.")
    lines += ["", "## Files", ""]
    for label, path in paths.items():
        lines.append(f"- `{label}`: `{path.name}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    rows_path = OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighweight_rows.csv"
    if not rows_path.exists():
        raise FileNotFoundError(rows_path)
    df = pd.read_csv(rows_path)
    df["post_P0_flag"] = df["p_star"].ge(P0)
    df["rho"] = df["rayleigh_over_h"]
    df["W"] = df["weight_l2_sq"]
    df["K"] = df["product_actual"]
    df["product_margin_to_65"] = K_TARGET - df["K"]
    df["rho_times_16"] = 16.0 * df["rho"]
    df["rho_times_15"] = 15.0 * df["rho"]
    df["weight_concentration"] = (df["weight_max"] ** 2) / df["W"].replace(0, np.nan)
    df["log_rho"] = np.log10(df["rho"].where(df["rho"] > 0))
    df["log_W"] = np.log10(df["W"].where(df["W"] > 0))

    rho_bins = [0.0, 1e-8, 1e-5, 1e-4, 1e-3, 1e-2, 1.0 / 16.0, 0.063, 0.07, 1.0]
    rho_labels = ["0", "1e-8..1e-5", "1e-5..1e-4", "1e-4..1e-3", "1e-3..1e-2", "1e-2..1/16", "1/16..0.063", "0.063..0.07", ">0.07"]
    W_bins = [0.0, 100.0, 400.0, 800.0, 1040.0, 2000.0, 10000.0, 100000.0, 1000000.0, float("inf")]
    W_labels = ["<=100", "100..400", "400..800", "800..1040", "1040..2k", "2k..10k", "10k..100k", "100k..1M", ">1M"]
    K_bins = [0.0, 1.0, 5.0, 10.0, 25.0, 50.0, 65.0, float("inf")]
    K_labels = ["<=1", "1..5", "5..10", "10..25", "25..50", "50..65", ">65"]
    df["rho_bin"] = bin_numeric(df["rho"], rho_bins, rho_labels)
    df["W_bin"] = bin_numeric(df["W"], W_bins, W_labels)
    df["K_bin"] = bin_numeric(df["K"], K_bins, K_labels)

    post = df[df["post_P0_flag"] == True].copy()
    W_large = post[post["W"] > 1040.0]
    rho_large = post[post["rho"] > 1.0 / 16.0]

    envelope_rows: List[Dict[str, object]] = []
    for wbin, g in post.groupby("W_bin", dropna=False, sort=False):
        if len(g) == 0:
            continue
        W_upper = float(g["W"].max())
        envelope_rows.append(
            {
                "W_bin": wbin,
                "rows": int(len(g)),
                "W_min": float(g["W"].min()),
                "W_max": W_upper,
                "rho_max": float(g["rho"].max()),
                "rho_q95": float(g["rho"].quantile(0.95)),
                "K_max": float(g["K"].max()),
                "required_rho_for_65_at_Wmax": K_TARGET / W_upper if W_upper > 0 else math.inf,
                "rho_margin_to_required": (K_TARGET / W_upper - float(g["rho"].max())) if W_upper > 0 else math.inf,
                "passes_bin_envelope": bool(float(g["K"].max()) <= K_TARGET),
            }
        )

    rho_envelope_rows: List[Dict[str, object]] = []
    for rbin, g in post.groupby("rho_bin", dropna=False, sort=False):
        if len(g) == 0:
            continue
        rho_max = float(g["rho"].max())
        rho_envelope_rows.append(
            {
                "rho_bin": rbin,
                "rows": int(len(g)),
                "rho_min": float(g["rho"].min()),
                "rho_max": rho_max,
                "W_max": float(g["W"].max()),
                "K_max": float(g["K"].max()),
                "required_W_for_65_at_rhomax": K_TARGET / rho_max if rho_max > 0 else math.inf,
                "W_margin_to_required": (K_TARGET / rho_max - float(g["W"].max())) if rho_max > 0 else math.inf,
                "passes_bin_envelope": bool(float(g["K"].max()) <= K_TARGET),
            }
        )

    # Candidate simple splits.
    split_rows = []
    W_cuts = [1040.0, 2000.0, 10000.0, 100000.0]
    rho_cuts = [1.0 / 16.0, 0.063, 1.0 / 15.0, 0.07]
    for Wcut in W_cuts:
        highW = post[post["W"] > Wcut]
        lowW = post[post["W"] <= Wcut]
        for rhocut in rho_cuts:
            highW_pass = bool(len(highW) == 0 or highW["rho"].max() <= rhocut)
            lowW_pass = bool(Wcut * rhocut <= K_TARGET) if rhocut * Wcut <= K_TARGET else False
            split_rows.append(
                {
                    "W_cut": Wcut,
                    "rho_cut": rhocut,
                    "highW_rows": int(len(highW)),
                    "highW_rho_max": float(highW["rho"].max()) if len(highW) else math.nan,
                    "lowW_rows": int(len(lowW)),
                    "lowW_Kmax_by_cut": Wcut * rhocut,
                    "highW_pass_rho_cut": highW_pass,
                    "lowW_independent_product_pass": lowW_pass,
                    "two_regime_closes": bool(highW_pass and lowW_pass),
                }
            )

    two_regime = any(r["two_regime_closes"] for r in split_rows)
    multi_regime = all(r["passes_bin_envelope"] for r in envelope_rows)
    recommended = "two_regime_coupling" if two_regime else ("multi_regime_envelope" if multi_regime else "direct_product_bound")

    summary = {
        "rows": int(len(df)),
        "post_P0_rows": int(len(post)),
        "post_P0_K_prime_max": float(post["K"].max()),
        "post_P0_K_prime_above_65_count": int(post["K"].gt(K_TARGET).sum()),
        "post_P0_product_margin_min": float(post["product_margin_to_65"].min()),
        "post_P0_corr_rho_W": corr(post["rho"], post["W"]),
        "post_P0_corr_logrho_logW": corr(post["log_rho"], post["log_W"]),
        "post_P0_spearman_rho_W": corr(post["rho"], post["W"], method="spearman"),
        "post_P0_corr_K_rho": corr(post["K"], post["rho"]),
        "post_P0_corr_K_W": corr(post["K"], post["W"]),
        "post_P0_W_large_rows": int(len(W_large)),
        "post_P0_W_large_rho_max": float(W_large["rho"].max()) if len(W_large) else math.nan,
        "post_P0_W_large_K_max": float(W_large["K"].max()) if len(W_large) else math.nan,
        "post_P0_rho_large_rows": int(len(rho_large)),
        "post_P0_rho_large_W_max": float(rho_large["W"].max()) if len(rho_large) else math.nan,
        "post_P0_rho_large_K_max": float(rho_large["K"].max()) if len(rho_large) else math.nan,
        "post_P0_W_max": float(post["W"].max()),
        "post_P0_rho_max": float(post["rho"].max()),
        "post_P0_K_q99": float(post["K"].quantile(0.99)),
        "threshold_relevant_rows": int(df.get("threshold_relevant_flag", pd.Series(False, index=df.index)).map(boolish).sum()),
        "threshold_relevant_K_max": float(df[df.get("threshold_relevant_flag", pd.Series(False, index=df.index)).map(boolish)]["K"].max())
        if "threshold_relevant_flag" in df and df["threshold_relevant_flag"].map(boolish).any()
        else math.nan,
        "forbidden_rows": int(df.get("forbidden_flag", pd.Series(False, index=df.index)).map(boolish).sum()),
        "forbidden_K_max": float(df[df.get("forbidden_flag", pd.Series(False, index=df.index)).map(boolish)]["K"].max())
        if "forbidden_flag" in df and df["forbidden_flag"].map(boolish).any()
        else math.nan,
        "regime_split_candidate": "two_regime" if two_regime else ("W_bin_envelope" if multi_regime else "none"),
        "best_theorem_form_recommended": recommended,
        "pass_direct_product_bound": bool(post["K"].le(K_TARGET).all()),
        "pass_rayleighcoupling_empirical": bool(post["K"].le(K_TARGET).all()),
    }

    by_rows = []
    for key in ["post_P0_flag", "rho_bin", "W_bin", "K_bin", "E_theta_sign", "threshold_relevant_flag", "forbidden_flag", "finite_zone_flag", "row_status"]:
        if key not in df.columns:
            continue
        for value, g in df.groupby(key, dropna=False):
            by_rows.append(
                {
                    "group_field": key,
                    "group_value": value,
                    "rows": int(len(g)),
                    "post_P0_rows": int(g["post_P0_flag"].sum()),
                    "rho_max": float(g["rho"].max()),
                    "W_max": float(g["W"].max()),
                    "K_max": float(g["K"].max()),
                    "product_margin_min": float(g["product_margin_to_65"].min()),
                }
            )

    extremes = []
    for metric in ["K", "rho", "W", "product_margin_to_65", "top_eigenvector_alignment", "spectral_tightness"]:
        ascending = metric == "product_margin_to_65"
        take = df.replace([np.inf, -np.inf], np.nan).sort_values(metric, ascending=ascending).head(20)
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
                    "rho": r["rho"],
                    "W": r["W"],
                    "K": r["K"],
                    "rho_bin": r["rho_bin"],
                    "W_bin": r["W_bin"],
                    "event_count": r["event_count"],
                    "sample_count": r["sample_count"],
                }
            )

    failures = post[post["K"] > K_TARGET].copy()

    paths = {
        "script": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighcoupling_audit.py",
        "summary": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighcoupling_summary.csv",
        "rows": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighcoupling_rows.csv",
        "W_envelope": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighcoupling_W_envelope.csv",
        "rho_envelope": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighcoupling_rho_envelope.csv",
        "split_candidates": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighcoupling_split_candidates.csv",
        "by_regime": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighcoupling_by_regime.csv",
        "extremes": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighcoupling_extremes.csv",
        "failures": OUT_DIR / "prime_mesh_r2q_hexc_primeshock_rayleighcoupling_failures.csv",
        "note": OUT_DIR / "Prime_Mesh_R2Q_HExc_PrimeShockBridge_RayleighCoupling_Audit_v1.md",
    }

    write_csv(paths["summary"], [summary])
    df.to_csv(paths["rows"], index=False)
    write_csv(paths["W_envelope"], envelope_rows)
    write_csv(paths["rho_envelope"], rho_envelope_rows)
    write_csv(paths["split_candidates"], split_rows)
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
