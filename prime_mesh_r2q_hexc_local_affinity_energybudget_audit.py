#!/usr/bin/env python3
"""
Prime Mesh R2Q - H-Exc LocalAffinity EnergyBudget audit.

Tests whether the endpoint residual budget can be split into clean constants

    eta_aff = ||D_N - ell||_2^2 / ||D_N||_2^2
    K_D     = ||D_N||_2^2 / h

with eta_aff * K_D <= 100 post-P0.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
P0 = 500_000_000
TOL = 1e-7
ETA_CANDIDATES = [2.5e-5, 3e-5, 5e-5, 1e-4]
KD_CANDIDATES = [2.5e6, 3e6, 4e6, 5e6, 1e7]


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


def safe_mean(s: pd.Series) -> float:
    x = num(s).dropna()
    return float(x.mean()) if not x.empty else float("nan")


def q(s: pd.Series, p: float) -> float:
    x = num(s).dropna()
    return float(x.quantile(p)) if not x.empty else float("nan")


def corr(df: pd.DataFrame, a: str, b: str) -> float:
    if a not in df.columns or b not in df.columns:
        return float("nan")
    tmp = df[[a, b]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(tmp) < 3 or tmp[a].std() == 0 or tmp[b].std() == 0:
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
                "note": "H-Exc LocalAffinity EnergyBudget audit output",
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
    df["eta_bin"] = pd.cut(
        num(df["eta_aff"]),
        bins=[-np.inf, 1e-6, 5e-6, 1e-5, 2.5e-5, 5e-5, 1e-4, np.inf],
        labels=["<=1e-6", "1e-6..5e-6", "5e-6..1e-5", "1e-5..2.5e-5", "2.5e-5..5e-5", "5e-5..1e-4", ">1e-4"],
    ).astype(str)
    df["K_D_bin"] = pd.cut(
        num(df["K_D"]),
        bins=[-np.inf, 1e5, 5e5, 1e6, 2.5e6, 3e6, 5e6, 1e7, np.inf],
        labels=["<=1e5", "1e5..5e5", "5e5..1e6", "1e6..2.5e6", "2.5e6..3e6", "3e6..5e6", "5e6..1e7", ">1e7"],
    ).astype(str)
    h = num(df["h"])
    p = num(df["p_star"])
    df["h_bin_eb"] = pd.cut(
        h,
        bins=[-np.inf, 1, 10, 100, 1_000, 10_000, 100_000, np.inf],
        labels=["h<=1", "2<=h<=10", "11<=h<=100", "101<=h<=1k", "1k<h<=10k", "10k<h<=100k", "h>100k"],
    ).astype(str)
    df["p_star_bin_eb"] = pd.cut(
        p,
        bins=[-np.inf, 1_000_000, 100_000_000, 500_000_000, 1_000_000_000, np.inf],
        labels=["p<1M", "1M<=p<100M", "100M<=p<500M", "500M<=p<1B", "p>=1B"],
    ).astype(str)
    return df


def summarize_group(g: pd.DataFrame) -> pd.Series:
    return pd.Series(
        {
            "rows": len(g),
            "K_R_max": safe_max(g["K_R"]),
            "eta_aff_max": safe_max(g["eta_aff"]),
            "K_D_max": safe_max(g["K_D"]),
            "eta_times_KD_max": safe_max(g["eta_times_KD"]),
            "capture_aff_min": float(num(g["capture_aff"]).min()) if num(g["capture_aff"]).notna().any() else float("nan"),
            "Q_exc_max": safe_max(g["Q_exc"]) if "Q_exc" in g else float("nan"),
            "Q_energy_L2_max": safe_max(g["Q_energy_L2"]) if "Q_energy_L2" in g else float("nan"),
            "failures": int(as_bool(g["local_affinity_energybudget_failure_flag"]).sum()) if "local_affinity_energybudget_failure_flag" in g else 0,
        }
    )


def choose_pair(post_rows: pd.DataFrame) -> tuple[float | None, float | None, float | None, bool]:
    for eta0 in ETA_CANDIDATES:
        for kd0 in KD_CANDIDATES:
            if eta0 * kd0 > 100:
                continue
            if (num(post_rows["eta_aff"]) <= eta0).all() and (num(post_rows["K_D"]) <= kd0).all():
                return eta0, kd0, eta0 * kd0, True
    return None, None, None, False


def main() -> None:
    rows = read_csv("prime_mesh_r2q_hexc_local_affine_decomposition_rows.csv")

    # Normalize and compute budget terms.
    rows["post_P0_by_pstar"] = as_bool(rows["post_P0_by_pstar"]) | (num(rows["p_star"]) >= P0)
    for col in ["finite_zone_flag", "high_energy_flag", "threshold_relevant_flag", "forbidden_flag", "surviving_proxy_flag"]:
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
    if "surviving_proxy_flag" not in rows:
        rows["surviving_proxy_flag"] = False

    rows["E_R"] = num(rows["E_end"])
    rows["E_ell"] = num(rows.get("E_ell_endpoint", rows.get("E_ell", np.nan)))
    rows["K_D"] = num(rows["E_D"]) / num(rows["h"])
    rows["K_R"] = num(rows["E_R"]) / num(rows["h"])
    rows["K_ell"] = num(rows["E_ell"]) / num(rows["h"]) if "E_ell" in rows.columns else np.nan
    rows["eta_aff"] = num(rows["E_R"]) / num(rows["E_D"]).replace(0, np.nan)
    rows["capture_aff"] = 1.0 - rows["eta_aff"]
    rows["eta_times_KD"] = rows["eta_aff"] * rows["K_D"]
    rows["product_reconstruction_error"] = (rows["eta_times_KD"] - rows["K_R"]).abs()

    for eta0 in ETA_CANDIDATES:
        rows[f"eta_aff_above_{eta0:g}"] = rows["eta_aff"] > eta0
    for kd0 in KD_CANDIDATES:
        rows[f"K_D_above_{kd0:g}"] = rows["K_D"] > kd0

    rows = add_bins(rows)
    post = as_bool(rows["post_P0_by_pstar"])
    threshold = as_bool(rows["threshold_relevant_flag"])
    forbidden = as_bool(rows["forbidden_flag"])

    eta0, kd0, pair_prod, pass_pair = choose_pair(rows.loc[post].copy())
    if eta0 is None:
        eta0 = float("nan")
        kd0 = float("nan")
        pair_prod = float("nan")

    pass_product_identity = bool(safe_max(rows["product_reconstruction_error"]) <= TOL)
    pass_endpoint_residual_budget = bool((post & (num(rows["K_R"]) > 100)).sum() == 0)
    pass_direct_product_budget = bool((post & (num(rows["eta_times_KD"]) > 100)).sum() == 0)
    pass_eta_cap = bool((num(rows.loc[post, "eta_aff"]) <= eta0).all()) if not np.isnan(eta0) else False
    pass_kd_cap = bool((num(rows.loc[post, "K_D"]) <= kd0).all()) if not np.isnan(kd0) else False

    if pass_pair:
        theorem = "local_affinity_energy_capture: eta_aff <= eta0, K_D <= K0, eta0*K0 <= 100"
        best_form = "local_affinity_energy_capture"
        rec_file = "Prime_Mesh_R2Q_HExc_LocalAffinity_EnergyBudget_Theorem_Target_v1.md"
    elif pass_direct_product_budget:
        theorem = "direct_local_affinity_product: eta_aff*K_D <= 100"
        best_form = "direct_local_affinity_product"
        rec_file = "Prime_Mesh_R2Q_HExc_EndpointAffineResidual_Formal_Proof_Draft_v1.md"
    else:
        theorem = "endpoint_affine_residual_bound"
        best_form = "endpoint_affine_residual_bound"
        rec_file = "Prime_Mesh_R2Q_HExc_LocalAffinity_EnergyBudget_Repair_Map_v1.md"

    rows["local_affinity_energybudget_failure_reason"] = ""
    rows.loc[rows["product_reconstruction_error"] > TOL, "local_affinity_energybudget_failure_reason"] = "product_identity_failure"
    rows.loc[post & (num(rows["K_R"]) > 100), "local_affinity_energybudget_failure_reason"] = rows["local_affinity_energybudget_failure_reason"].mask(
        rows["local_affinity_energybudget_failure_reason"].eq(""), "post_P0_K_R_above_100"
    )
    rows["local_affinity_energybudget_failure_flag"] = rows["local_affinity_energybudget_failure_reason"].ne("")

    summary = {
        "rows": int(len(rows)),
        "path_sample_blocks": int(rows["candidate_id"].nunique()),
        "blocks_missing_path_samples": int(rows.get("blocks_missing_path_samples_flag", pd.Series(False, index=rows.index)).sum()),
        "path_reconstruction_ok": bool(safe_max(rows.get("C_end_vs_C_bridge_error", pd.Series(0, index=rows.index))) <= TOL),
        "P0": P0,
        "post_P0_rows": int(post.sum()),
        "product_reconstruction_error_max": safe_max(rows["product_reconstruction_error"]),
        "post_P0_product_reconstruction_error_max": safe_max(rows.loc[post, "product_reconstruction_error"]),
        "pass_product_identity": pass_product_identity,
        "post_P0_K_R_max": safe_max(rows.loc[post, "K_R"]),
        "post_P0_K_R_above_100_count": int((post & (num(rows["K_R"]) > 100)).sum()),
        "pass_endpoint_residual_budget": pass_endpoint_residual_budget,
        "post_P0_eta_aff_max": safe_max(rows.loc[post, "eta_aff"]),
        "post_P0_eta_aff_q95": q(rows.loc[post, "eta_aff"], 0.95),
        "post_P0_eta_aff_q99": q(rows.loc[post, "eta_aff"], 0.99),
        "post_P0_eta_aff_above_2p5e_minus_5_count": int((post & (num(rows["eta_aff"]) > 2.5e-5)).sum()),
        "post_P0_eta_aff_above_3e_minus_5_count": int((post & (num(rows["eta_aff"]) > 3e-5)).sum()),
        "post_P0_eta_aff_above_5e_minus_5_count": int((post & (num(rows["eta_aff"]) > 5e-5)).sum()),
        "post_P0_eta_aff_above_1e_minus_4_count": int((post & (num(rows["eta_aff"]) > 1e-4)).sum()),
        "recommended_eta0": eta0,
        "pass_eta_aff_cap": pass_eta_cap,
        "post_P0_K_D_max": safe_max(rows.loc[post, "K_D"]),
        "post_P0_K_D_q95": q(rows.loc[post, "K_D"], 0.95),
        "post_P0_K_D_q99": q(rows.loc[post, "K_D"], 0.99),
        "post_P0_K_D_above_2p5e6_count": int((post & (num(rows["K_D"]) > 2.5e6)).sum()),
        "post_P0_K_D_above_3e6_count": int((post & (num(rows["K_D"]) > 3e6)).sum()),
        "post_P0_K_D_above_4e6_count": int((post & (num(rows["K_D"]) > 4e6)).sum()),
        "post_P0_K_D_above_5e6_count": int((post & (num(rows["K_D"]) > 5e6)).sum()),
        "post_P0_K_D_above_1e7_count": int((post & (num(rows["K_D"]) > 1e7)).sum()),
        "recommended_K0": kd0,
        "pass_K_D_cap": pass_kd_cap,
        "recommended_eta0_times_K0": pair_prod,
        "pass_two_part_energy_budget": pass_pair,
        "post_P0_eta_times_KD_max": safe_max(rows.loc[post, "eta_times_KD"]),
        "post_P0_eta_times_KD_above_100_count": int((post & (num(rows["eta_times_KD"]) > 100)).sum()),
        "pass_direct_product_budget": pass_direct_product_budget,
        "threshold_relevant_eta_aff_max": safe_max(rows.loc[threshold, "eta_aff"]),
        "threshold_relevant_K_D_max": safe_max(rows.loc[threshold, "K_D"]),
        "threshold_relevant_eta_times_KD_max": safe_max(rows.loc[threshold, "eta_times_KD"]),
        "threshold_relevant_K_R_max": safe_max(rows.loc[threshold, "K_R"]),
        "forbidden_eta_aff_max": safe_max(rows.loc[forbidden, "eta_aff"]),
        "forbidden_K_D_max": safe_max(rows.loc[forbidden, "K_D"]),
        "forbidden_eta_times_KD_max": safe_max(rows.loc[forbidden, "eta_times_KD"]),
        "forbidden_K_R_max": safe_max(rows.loc[forbidden, "K_R"]),
        "corr_K_R_eta_aff": corr(rows, "K_R", "eta_aff"),
        "corr_K_R_K_D": corr(rows, "K_R", "K_D"),
        "corr_K_R_Q_exc": corr(rows, "K_R", "Q_exc"),
        "corr_K_R_Q_delta_D": corr(rows, "K_R", "Q_delta_D"),
        "corr_K_R_Q_R2Q": corr(rows, "K_R", "Q_R2Q"),
        "corr_eta_aff_log_pstar": corr(rows, "eta_aff", "log_pstar"),
        "corr_K_D_log_pstar": corr(rows, "K_D", "log_pstar"),
        "corr_K_D_h": corr(rows, "K_D", "h"),
        "corr_K_D_h_over_x": corr(rows, "K_D", "h_over_x"),
        "best_theorem_form_recommended": best_form,
        "local_affinity_energybudget_failures": int(rows["local_affinity_energybudget_failure_flag"].sum()),
        "pass_hexc_local_affinity_energybudget_empirical": bool(rows["local_affinity_energybudget_failure_flag"].sum() == 0),
        "recommended_next_file": rec_file,
        "recommended_theorem_form": theorem,
    }

    group_cols = [
        "row_regime",
        "post_P0_by_pstar",
        "finite_zone_flag",
        "high_energy_flag",
        "threshold_relevant_flag",
        "forbidden_flag",
        "h_bin_eb",
        "p_star_bin_eb",
        "eta_bin",
        "K_D_bin",
    ]
    groups = []
    for col in group_cols:
        if col in rows.columns:
            g = rows.groupby(col, dropna=False).apply(summarize_group, include_groups=False).reset_index()
            g.insert(0, "group_field", col)
            g = g.rename(columns={col: "group_value"})
            groups.append(g)
    by_regime = pd.concat(groups, ignore_index=True)

    metrics = ["K_R", "eta_aff", "K_D", "eta_times_KD", "Q_exc", "Q_energy_L2", "C_end"]
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
        "K_R",
        "eta_aff",
        "K_D",
        "eta_times_KD",
        "Q_exc",
        "Q_energy_L2",
        "C_end",
    ]
    ext_frames = []
    for metric in metrics:
        cols = list(dict.fromkeys([c for c in id_cols + [metric] if c in rows.columns]))
        top = rows.sort_values(metric, ascending=False, na_position="last").head(25)[cols].copy()
        top.insert(0, "rank_metric", metric)
        top.insert(1, "rank", range(1, len(top) + 1))
        ext_frames.append(top)
    extremes = pd.concat(ext_frames, ignore_index=True)
    failures = rows.loc[rows["local_affinity_energybudget_failure_flag"]].copy()

    out_summary = BASE / "prime_mesh_r2q_hexc_local_affinity_energybudget_summary.csv"
    out_rows = BASE / "prime_mesh_r2q_hexc_local_affinity_energybudget_rows.csv"
    out_by = BASE / "prime_mesh_r2q_hexc_local_affinity_energybudget_by_regime.csv"
    out_ext = BASE / "prime_mesh_r2q_hexc_local_affinity_energybudget_extremes.csv"
    out_fail = BASE / "prime_mesh_r2q_hexc_local_affinity_energybudget_failures.csv"
    out_md = BASE / "Prime_Mesh_R2Q_HExc_LocalAffinity_EnergyBudget_Audit_v1.md"

    write_summary(out_summary, summary)
    rows.to_csv(out_rows, index=False)
    by_regime.to_csv(out_by, index=False)
    extremes.to_csv(out_ext, index=False)
    failures.to_csv(out_fail, index=False)

    if pass_pair:
        interp = f"""The energy budget closes with separate constants:

```text
eta_aff <= {summary['recommended_eta0']}
K_D     <= {summary['recommended_K0']}
eta0*K0 = {summary['recommended_eta0_times_K0']} <= 100.
```"""
    else:
        interp = f"""The direct product budget closes, but the attempted separate constants do not:

```text
max_post_P0 eta_aff*K_D = {summary['post_P0_eta_times_KD_max']} <= 100
max_post_P0 eta_aff     = {summary['post_P0_eta_aff_max']}
max_post_P0 K_D         = {summary['post_P0_K_D_max']}
```

So the proof-facing object should stay the direct product / endpoint residual bound, with local-affinity used as explanatory structure rather than as two independent caps."""

    md = f"""# Prime Mesh R2Q - H-Exc LocalAffinity EnergyBudget Audit v1

**Status:** empirical pass  
**Date:** {datetime.now().date().isoformat()}  
**Script:** `prime_mesh_r2q_hexc_local_affinity_energybudget_audit.py`

## Target

Test the local-affinity energy budget:

```text
eta_aff = ||D_N - ell_endpoint||_2^2 / ||D_N||_2^2
K_D     = ||D_N||_2^2 / h
K_R     = ||D_N - ell_endpoint||_2^2 / h
```

with:

```text
K_R = eta_aff * K_D.
```

## Main Results

```text
rows                                      = {summary['rows']}
path_sample_blocks                        = {summary['path_sample_blocks']}
blocks_missing_path_samples               = {summary['blocks_missing_path_samples']}
path_reconstruction_ok                    = {summary['path_reconstruction_ok']}

post_P0_rows                              = {summary['post_P0_rows']}

product_reconstruction_error_max          = {summary['product_reconstruction_error_max']}
post_P0_product_reconstruction_error_max  = {summary['post_P0_product_reconstruction_error_max']}
pass_product_identity                     = {summary['pass_product_identity']}

post_P0_K_R_max                           = {summary['post_P0_K_R_max']}
post_P0_K_R_above_100_count               = {summary['post_P0_K_R_above_100_count']}
pass_endpoint_residual_budget             = {summary['pass_endpoint_residual_budget']}

post_P0_eta_aff_max                       = {summary['post_P0_eta_aff_max']}
post_P0_eta_aff_q95                       = {summary['post_P0_eta_aff_q95']}
post_P0_eta_aff_q99                       = {summary['post_P0_eta_aff_q99']}
recommended_eta0                          = {summary['recommended_eta0']}
pass_eta_aff_cap                          = {summary['pass_eta_aff_cap']}

post_P0_K_D_max                           = {summary['post_P0_K_D_max']}
post_P0_K_D_q95                           = {summary['post_P0_K_D_q95']}
post_P0_K_D_q99                           = {summary['post_P0_K_D_q99']}
recommended_K0                            = {summary['recommended_K0']}
pass_K_D_cap                              = {summary['pass_K_D_cap']}

recommended_eta0_times_K0                 = {summary['recommended_eta0_times_K0']}
pass_two_part_energy_budget               = {summary['pass_two_part_energy_budget']}

post_P0_eta_times_KD_max                  = {summary['post_P0_eta_times_KD_max']}
post_P0_eta_times_KD_above_100_count      = {summary['post_P0_eta_times_KD_above_100_count']}
pass_direct_product_budget                = {summary['pass_direct_product_budget']}

threshold_relevant_eta_times_KD_max       = {summary['threshold_relevant_eta_times_KD_max']}
forbidden_eta_times_KD_max                = {summary['forbidden_eta_times_KD_max']}
threshold_relevant_K_R_max                = {summary['threshold_relevant_K_R_max']}
forbidden_K_R_max                         = {summary['forbidden_K_R_max']}

best_theorem_form_recommended             = {summary['best_theorem_form_recommended']}
local_affinity_energybudget_failures      = {summary['local_affinity_energybudget_failures']}
pass_hexc_local_affinity_energybudget_empirical = {summary['pass_hexc_local_affinity_energybudget_empirical']}
```

## Interpretation

{interp}

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
    update_manifest(outputs)
    print(md)


if __name__ == "__main__":
    main()
