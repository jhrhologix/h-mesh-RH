#!/usr/bin/env python3
"""RawR2Q component-bounds audit.

Audits the v3 primitive decomposition

    Q_R2Q = Q_delta_D + Q_exc + epsilon

and checks the proof-facing empirical component bounds.
"""

from __future__ import annotations

import csv
import math
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent
ROWS_IN = OUT / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv"
SUMMARY_IN = OUT / "prime_mesh_r2q_rawr2q_primitive_decomposition_summary_v3.csv"
FULL_EXPORT_IN = OUT / "prime_mesh_r2q_rawr2q_full_primitive_export_rows.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_rawr2q_component_bounds_summary.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_rawr2q_component_bounds_rows.csv"
BY_REGIME_OUT = OUT / "prime_mesh_r2q_rawr2q_component_bounds_by_regime.csv"
EXTREMES_OUT = OUT / "prime_mesh_r2q_rawr2q_component_bounds_extremes.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_rawr2q_component_bounds_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_RawR2Q_Component_Bounds_Audit_v1.md"
MANIFEST = OUT / "deposit_manifest.csv"

Q_EXC_CAP = 0.025
EPS_CAP = 0.03
Q_POS_CAP = 0.25
Q_NEAR = 0.75
Q_FORBIDDEN = 1.0
FORMULA_RESIDUAL_CAP = 1e-10


def log(msg: str) -> None:
    print(f"[component-bounds {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def bool_series(s: pd.Series | None, index: pd.Index, default: bool = False) -> pd.Series:
    if s is None:
        return pd.Series(default, index=index)
    if s.dtype == bool:
        return s.fillna(default)
    return s.astype(str).str.lower().map(
        {"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False}
    ).fillna(default)


def num(df: pd.DataFrame, col: str, fallback: str | None = None) -> pd.Series:
    if col in df:
        return pd.to_numeric(df[col], errors="coerce")
    if fallback and fallback in df:
        return pd.to_numeric(df[fallback], errors="coerce")
    return pd.Series(np.nan, index=df.index)


def regime(row: pd.Series) -> str:
    if bool(row.get("finite_certificate_flag", False)):
        # Keep true high-Q finite rows visible; finite certificate is metadata,
        # not the analytic sign regime.
        if bool(row["forbidden_flag"]) and row["E_theta_sign"] == "negative":
            return "forbidden_negative"
        if bool(row["threshold_relevant_flag"]) and row["E_theta_sign"] == "negative":
            return "threshold_relevant_negative"
        if row["E_theta_sign"] == "positive":
            return "positive_harmless"
        if row["E_theta_sign"] == "negative":
            return "subthreshold_negative"
        return "finite_certificate"
    if bool(row["forbidden_flag"]) and row["E_theta_sign"] == "negative":
        return "forbidden_negative"
    if bool(row["threshold_relevant_flag"]) and row["E_theta_sign"] == "negative":
        return "threshold_relevant_negative"
    if row["E_theta_sign"] == "positive":
        return "positive_harmless"
    if row["E_theta_sign"] == "negative":
        return "subthreshold_negative"
    if row["E_theta_sign"] == "zero":
        return "neutral_or_zero"
    return "unknown"


def safe_max(s: pd.Series) -> float:
    return float(s.max()) if len(s.dropna()) else math.nan


def safe_mean(s: pd.Series) -> float:
    return float(s.mean()) if len(s.dropna()) else math.nan


def safe_quantile(s: pd.Series, q: float) -> float:
    return float(s.quantile(q)) if len(s.dropna()) else math.nan


def corr(a: pd.Series, b: pd.Series) -> float:
    part = pd.DataFrame({"a": a, "b": b}).dropna()
    if len(part) < 2:
        return math.nan
    if part["a"].nunique() <= 1 or part["b"].nunique() <= 1:
        return math.nan
    return float(part["a"].corr(part["b"]))


def load_rows() -> pd.DataFrame:
    if not ROWS_IN.exists():
        raise FileNotFoundError(f"Missing required input: {ROWS_IN}")
    log(f"Reading {ROWS_IN.name}")
    df = pd.read_csv(ROWS_IN)
    if FULL_EXPORT_IN.exists():
        log(f"Full primitive export found: {FULL_EXPORT_IN.name}")
    if SUMMARY_IN.exists():
        log(f"v3 summary found: {SUMMARY_IN.name}")
    return df


def build_audit_rows(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for c in ["candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta_sign", "DeltaD_sign"]:
        out[c] = df[c] if c in df else np.nan
    out["post_P0_flag"] = bool_series(df.get("post_P0_flag"), df.index)
    out["finite_zone_flag"] = bool_series(df.get("finite_zone_flag"), df.index, default=True)
    out["finite_certificate_flag"] = bool_series(df.get("finite_certificate_flag"), df.index)
    out["E_theta"] = num(df, "E_theta", "E_theta_local")
    out["Q_R2Q"] = num(df, "Q_R2Q")
    out["Q_delta_D"] = num(df, "Q_delta_D", "Q_delta_D_best")
    out["DeltaD"] = num(df, "DeltaD", "observed_delta")
    out["Q_exc"] = num(df, "Q_exc")
    out["epsilon"] = num(df, "formula_residual")
    out["abs_epsilon"] = out["epsilon"].abs()
    out["Q_reconstructed"] = out["Q_delta_D"] + out["Q_exc"] + out["epsilon"]
    out["formula_residual"] = out["Q_R2Q"] - out["Q_reconstructed"]
    out["abs_formula_residual"] = out["formula_residual"].abs()
    out["near_forbidden_flag"] = out["Q_R2Q"] > Q_NEAR
    out["forbidden_flag"] = out["Q_R2Q"] > Q_FORBIDDEN
    out["threshold_relevant_flag"] = out["near_forbidden_flag"]
    out["positive_harmless_flag"] = bool_series(df.get("positive_harmless_flag"), df.index) | out["E_theta_sign"].eq("positive")
    out["negative_transfer_flag"] = bool_series(df.get("negative_transfer_flag"), df.index) | (
        out["threshold_relevant_flag"] & out["E_theta_sign"].eq("negative")
    )
    out["channel_compatible_flag"] = bool_series(df.get("covered_flag"), df.index, default=True)
    out["O2_repaid_flag"] = bool_series(df.get("O2_B3_repaid_flag"), df.index, default=True)
    out["B3_no_accumulation_flag"] = bool_series(df.get("B3_block_pass"), df.index, default=True)
    out["primitive_available_flag"] = bool_series(df.get("primitive_available_flag"), df.index)
    out["row_regime"] = out.apply(regime, axis=1)

    missing_qd = out["Q_delta_D"].isna()
    missing_qexc = out["Q_exc"].isna()
    missing_eps = out["epsilon"].isna()
    formula_fail = out["abs_formula_residual"] > FORMULA_RESIDUAL_CAP
    qexc_fail = out["Q_exc"] > Q_EXC_CAP
    eps_fail = out["abs_epsilon"] > EPS_CAP
    positive_cap_fail = out["E_theta_sign"].eq("positive") & (out["Q_delta_D"] > Q_POS_CAP)
    neg_transfer_fail = (out["Q_delta_D"] > Q_NEAR) & ~out["E_theta_sign"].eq("negative")
    threshold_missing = out["threshold_relevant_flag"] & (missing_qd | missing_qexc | missing_eps)
    invalid_scale = out["Q_R2Q"].isna() | out["Q_delta_D"].lt(0) | out["Q_exc"].lt(0)

    failure_type = []
    for i in out.index:
        reasons: list[str] = []
        if missing_qd.loc[i]:
            reasons.append("missing_Q_delta_D")
        if missing_qexc.loc[i]:
            reasons.append("missing_Q_exc")
        if missing_eps.loc[i]:
            reasons.append("missing_epsilon")
        if formula_fail.loc[i]:
            reasons.append("formula_residual_cap_violation")
        if qexc_fail.loc[i]:
            reasons.append("Q_exc_cap_violation")
        if eps_fail.loc[i]:
            reasons.append("epsilon_cap_violation")
        if positive_cap_fail.loc[i]:
            reasons.append("positive_Q_delta_D_cap_violation")
        if neg_transfer_fail.loc[i]:
            reasons.append("Q_delta_D_threshold_negative_transfer_violation")
        if threshold_missing.loc[i]:
            reasons.append("threshold_relevant_missing_component")
        if invalid_scale.loc[i]:
            reasons.append("invalid_scale")
        failure_type.append(";".join(reasons))

    out["failure_type"] = failure_type
    out["component_bound_status"] = np.where(out["failure_type"].eq(""), "pass", "fail")
    out["status"] = out["component_bound_status"]
    return out


def summarize(rows: pd.DataFrame) -> dict[str, Any]:
    pos = rows[rows["E_theta_sign"].eq("positive")]
    neg = rows[rows["E_theta_sign"].eq("negative")]
    thresh = rows[rows["threshold_relevant_flag"]]
    forb = rows[rows["forbidden_flag"]]
    post = rows[rows["post_P0_flag"]]
    finite = rows[rows["finite_zone_flag"]]
    eps = rows["epsilon"]
    neg_eps = eps[eps < 0]
    pos_eps = eps[eps > 0]

    qd_gt_075 = rows["Q_delta_D"] > Q_NEAR
    qd_gt_075_viol = qd_gt_075 & ~rows["E_theta_sign"].eq("negative")
    pos_qd_above = pos["Q_delta_D"] > Q_POS_CAP
    qexc_above = rows["Q_exc"] > Q_EXC_CAP
    eps_above = rows["abs_epsilon"] > EPS_CAP
    formula_fail = rows["abs_formula_residual"] > FORMULA_RESIDUAL_CAP

    failure_rows = rows[rows["component_bound_status"].eq("fail")]

    summary: dict[str, Any] = {
        "rows": int(len(rows)),
        "primitive_full_rows": int(rows["primitive_available_flag"].sum()),
        "primitive_missing_rows": int((~rows["primitive_available_flag"]).sum()),
        "post_P0_rows": int(rows["post_P0_flag"].sum()),
        "finite_zone_rows": int(rows["finite_zone_flag"].sum()),
        "positive_rows": int(rows["E_theta_sign"].eq("positive").sum()),
        "negative_rows": int(rows["E_theta_sign"].eq("negative").sum()),
        "threshold_relevant_rows": int(rows["threshold_relevant_flag"].sum()),
        "forbidden_rows": int(rows["forbidden_flag"].sum()),
        "Q_R2Q_max": safe_max(rows["Q_R2Q"]),
        "Q_delta_D_max": safe_max(rows["Q_delta_D"]),
        "Q_exc_max": safe_max(rows["Q_exc"]),
        "abs_epsilon_max": safe_max(rows["abs_epsilon"]),
        "Q_delta_D_positive_max": safe_max(pos["Q_delta_D"]),
        "Q_delta_D_negative_max": safe_max(neg["Q_delta_D"]),
        "Q_delta_D_threshold_relevant_max": safe_max(thresh["Q_delta_D"]),
        "Q_delta_D_forbidden_max": safe_max(forb["Q_delta_D"]),
        "Q_delta_D_post_P0_max": safe_max(post["Q_delta_D"]),
        "Q_delta_D_finite_max": safe_max(finite["Q_delta_D"]),
        "Q_delta_D_above_0p25_count": int((rows["Q_delta_D"] > 0.25).sum()),
        "Q_delta_D_above_0p50_count": int((rows["Q_delta_D"] > 0.50).sum()),
        "Q_delta_D_above_0p75_count": int(qd_gt_075.sum()),
        "Q_delta_D_above_1p00_count": int((rows["Q_delta_D"] > 1.00).sum()),
        "Q_delta_D_gt_0p75_count": int(qd_gt_075.sum()),
        "Q_delta_D_gt_0p75_negative_count": int((qd_gt_075 & rows["E_theta_sign"].eq("negative")).sum()),
        "Q_delta_D_gt_0p75_positive_count": int((qd_gt_075 & rows["E_theta_sign"].eq("positive")).sum()),
        "Q_delta_D_gt_0p75_violations": int(qd_gt_075_viol.sum()),
        "pass_Q_delta_D_threshold_negative_transfer": bool(qd_gt_075_viol.sum() == 0),
        "positive_Q_delta_D_max": safe_max(pos["Q_delta_D"]),
        "positive_Q_delta_D_above_0p25_count": int(pos_qd_above.sum()),
        "pass_positive_Q_delta_D_cap_0p25": bool(pos_qd_above.sum() == 0),
        "Q_exc_mean": safe_mean(rows["Q_exc"]),
        "Q_exc_q95": safe_quantile(rows["Q_exc"], 0.95),
        "Q_exc_q99": safe_quantile(rows["Q_exc"], 0.99),
        "Q_exc_above_0p025_count": int(qexc_above.sum()),
        "Q_exc_above_0p05_count": int((rows["Q_exc"] > 0.05).sum()),
        "Q_exc_threshold_relevant_max": safe_max(thresh["Q_exc"]),
        "Q_exc_forbidden_max": safe_max(forb["Q_exc"]),
        "Q_exc_post_P0_max": safe_max(post["Q_exc"]),
        "pass_Q_exc_cap_0p025": bool(qexc_above.sum() == 0),
        "epsilon_min": float(rows["epsilon"].min()),
        "epsilon_max": float(rows["epsilon"].max()),
        "abs_epsilon_mean": safe_mean(rows["abs_epsilon"]),
        "abs_epsilon_q95": safe_quantile(rows["abs_epsilon"], 0.95),
        "abs_epsilon_q99": safe_quantile(rows["abs_epsilon"], 0.99),
        "abs_epsilon_above_0p01_count": int((rows["abs_epsilon"] > 0.01).sum()),
        "abs_epsilon_above_0p02_count": int((rows["abs_epsilon"] > 0.02).sum()),
        "abs_epsilon_above_0p03_count": int(eps_above.sum()),
        "abs_epsilon_threshold_relevant_max": safe_max(thresh["abs_epsilon"]),
        "abs_epsilon_forbidden_max": safe_max(forb["abs_epsilon"]),
        "pass_epsilon_cap_0p03": bool(eps_above.sum() == 0),
        "epsilon_positive_count": int((eps > 0).sum()),
        "epsilon_negative_count": int((eps < 0).sum()),
        "epsilon_positive_mean": safe_mean(pos_eps),
        "epsilon_negative_mean": safe_mean(neg_eps),
        "formula_rows": int(len(rows)),
        "formula_residual_max_abs": safe_max(rows["abs_formula_residual"]),
        "formula_residual_mean_abs": safe_mean(rows["abs_formula_residual"]),
        "formula_residual_q99_abs": safe_quantile(rows["abs_formula_residual"], 0.99),
        "formula_residual_cap": FORMULA_RESIDUAL_CAP,
        "formula_residual_cap_violations": int(formula_fail.sum()),
        "pass_formula_reconstruction": bool(formula_fail.sum() == 0),
        "corr_Q_R2Q_Q_delta_D": corr(rows["Q_R2Q"], rows["Q_delta_D"]),
        "corr_Q_R2Q_Q_exc": corr(rows["Q_R2Q"], rows["Q_exc"]),
        "corr_Q_R2Q_epsilon": corr(rows["Q_R2Q"], rows["epsilon"]),
        "corr_E_theta_Q_delta_D": corr(rows["E_theta"], rows["Q_delta_D"]),
        "corr_E_theta_Q_R2Q": corr(rows["E_theta"], rows["Q_R2Q"]),
        "corr_abs_E_theta_Q_delta_D": corr(rows["E_theta"].abs(), rows["Q_delta_D"]),
        "positive_Q_delta_D_q95": safe_quantile(pos["Q_delta_D"], 0.95),
        "positive_Q_delta_D_q99": safe_quantile(pos["Q_delta_D"], 0.99),
        "negative_Q_delta_D_q95": safe_quantile(neg["Q_delta_D"], 0.95),
        "negative_Q_delta_D_q99": safe_quantile(neg["Q_delta_D"], 0.99),
        "threshold_relevant_Q_delta_D_min": float(thresh["Q_delta_D"].min()) if len(thresh) else math.nan,
        "threshold_relevant_Q_delta_D_max": safe_max(thresh["Q_delta_D"]),
        "component_bound_failures": int(len(failure_rows)),
    }
    missing_components = rows["Q_delta_D"].isna() | rows["Q_exc"].isna() | rows["epsilon"].isna()
    threshold_missing = rows["threshold_relevant_flag"] & missing_components
    summary["missing_Q_delta_D_count"] = int(rows["Q_delta_D"].isna().sum())
    summary["missing_Q_exc_count"] = int(rows["Q_exc"].isna().sum())
    summary["missing_epsilon_count"] = int(rows["epsilon"].isna().sum())
    summary["threshold_relevant_missing_component_count"] = int(threshold_missing.sum())
    summary["pass_rawr2q_component_bounds_empirical"] = bool(
        summary["missing_Q_delta_D_count"] == 0
        and summary["missing_Q_exc_count"] == 0
        and summary["missing_epsilon_count"] == 0
        and summary["formula_residual_cap_violations"] == 0
        and summary["Q_exc_above_0p025_count"] == 0
        and summary["abs_epsilon_above_0p03_count"] == 0
        and summary["positive_Q_delta_D_above_0p25_count"] == 0
        and summary["Q_delta_D_gt_0p75_violations"] == 0
        and summary["threshold_relevant_missing_component_count"] == 0
    )
    summary["recommended_theorem_form"] = (
        "Q_exc_le_0p025_abs_epsilon_le_0p03_positive_endpoint_cap_negative_threshold_transfer"
        if summary["pass_rawr2q_component_bounds_empirical"]
        else "component_bounds_need_repair_or_relaxed_caps"
    )
    summary["recommended_next_file"] = (
        "Prime_Mesh_R2Q_RawR2Q_Component_Bounds_Theorem_Target_v1.md"
        if summary["pass_rawr2q_component_bounds_empirical"]
        else "Prime_Mesh_R2Q_RawR2Q_Component_Bounds_Repair_Map_v1.md"
    )
    return summary


def by_regime(rows: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for name, g in rows.groupby("row_regime", dropna=False):
        parts.append(
            {
                "row_regime": name,
                "rows": len(g),
                "Q_R2Q_max": safe_max(g["Q_R2Q"]),
                "Q_delta_D_max": safe_max(g["Q_delta_D"]),
                "Q_exc_max": safe_max(g["Q_exc"]),
                "abs_epsilon_max": safe_max(g["abs_epsilon"]),
                "positive_rows": int(g["E_theta_sign"].eq("positive").sum()),
                "negative_rows": int(g["E_theta_sign"].eq("negative").sum()),
                "threshold_relevant_rows": int(g["threshold_relevant_flag"].sum()),
                "failures": int(g["component_bound_status"].eq("fail").sum()),
            }
        )
    return pd.DataFrame(parts).sort_values(["failures", "Q_R2Q_max"], ascending=[False, False])


def extremes(rows: pd.DataFrame) -> pd.DataFrame:
    specs = [
        ("Q_R2Q_max", "Q_R2Q", False),
        ("Q_delta_D_max", "Q_delta_D", False),
        ("Q_exc_max", "Q_exc", False),
        ("abs_epsilon_max", "abs_epsilon", False),
        ("epsilon_min", "epsilon", True),
        ("epsilon_max", "epsilon", False),
        ("positive_Q_delta_D_max", "Q_delta_D", False),
    ]
    records = []
    for name, col, asc in specs:
        part = rows.copy()
        if name.startswith("positive_"):
            part = part[part["E_theta_sign"].eq("positive")]
        if len(part) == 0 or part[col].dropna().empty:
            continue
        r = part.sort_values(col, ascending=asc).iloc[0]
        records.append(
            {
                "extreme": name,
                "value": r[col],
                "candidate_id": r.get("candidate_id"),
                "block_id": r.get("block_id"),
                "x": r.get("x"),
                "y": r.get("y"),
                "h": r.get("h"),
                "p_star": r.get("p_star"),
                "E_theta_sign": r.get("E_theta_sign"),
                "Q_R2Q": r.get("Q_R2Q"),
                "Q_delta_D": r.get("Q_delta_D"),
                "Q_exc": r.get("Q_exc"),
                "epsilon": r.get("epsilon"),
                "row_regime": r.get("row_regime"),
                "status": r.get("status"),
            }
        )
    return pd.DataFrame(records)


def write_summary(summary: dict[str, Any]) -> None:
    with SUMMARY_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["field", "value"])
        for k, v in summary.items():
            w.writerow([k, v])


def write_doc(summary: dict[str, Any], regimes: pd.DataFrame, extremes_df: pd.DataFrame, failures: pd.DataFrame) -> None:
    verdict = "pass" if summary["pass_rawr2q_component_bounds_empirical"] else "repair needed"
    lines = [
        "# Prime Mesh R2Q - RawR2Q Component Bounds Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-08",
        f"**Status:** {verdict}",
        "",
        "## 1. Executive Verdict",
        "",
    ]
    if summary["pass_rawr2q_component_bounds_empirical"]:
        lines += [
            r"\[",
            r"\boxed{\text{RawR2Q component bounds pass empirically on the full v3 primitive inventory.}}",
            r"\]",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{At least one RawR2Q component bound failed and needs repair.}}",
            r"\]",
        ]
    lines += [
        "",
        "## 2. Inputs Used",
        "",
        f"- Primary rows: `{ROWS_IN}`.",
        f"- v3 summary: `{SUMMARY_IN}`.",
        f"- full primitive export: `{FULL_EXPORT_IN}`.",
        "",
        "## 3. Primitive Coverage",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| rows | {summary['rows']} |",
        f"| primitive_full_rows | {summary['primitive_full_rows']} |",
        f"| primitive_missing_rows | {summary['primitive_missing_rows']} |",
        f"| threshold_relevant_rows | {summary['threshold_relevant_rows']} |",
        f"| threshold_relevant_missing_component_count | {summary['threshold_relevant_missing_component_count']} |",
        "",
        "## 4. Component Ledger",
        "",
        "| component | bound | max/count | pass |",
        "|---|---:|---:|---:|",
        f"| `Q_exc` | <= {Q_EXC_CAP} | {summary['Q_exc_max']} / above cap {summary['Q_exc_above_0p025_count']} | {summary['pass_Q_exc_cap_0p025']} |",
        f"| `abs(epsilon)` | <= {EPS_CAP} | {summary['abs_epsilon_max']} / above cap {summary['abs_epsilon_above_0p03_count']} | {summary['pass_epsilon_cap_0p03']} |",
        f"| positive `Q_delta_D` | <= {Q_POS_CAP} | {summary['positive_Q_delta_D_max']} / above cap {summary['positive_Q_delta_D_above_0p25_count']} | {summary['pass_positive_Q_delta_D_cap_0p25']} |",
        f"| `Q_delta_D > 3/4` sign | negative theta | violations {summary['Q_delta_D_gt_0p75_violations']} | {summary['pass_Q_delta_D_threshold_negative_transfer']} |",
        "",
        "## 5. Endpoint-Motion Component",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| Q_delta_D_max | {summary['Q_delta_D_max']} |",
        f"| Q_delta_D_positive_max | {summary['Q_delta_D_positive_max']} |",
        f"| Q_delta_D_negative_max | {summary['Q_delta_D_negative_max']} |",
        f"| Q_delta_D_threshold_relevant_max | {summary['Q_delta_D_threshold_relevant_max']} |",
        f"| Q_delta_D_gt_0p75_count | {summary['Q_delta_D_gt_0p75_count']} |",
        f"| Q_delta_D_gt_0p75_violations | {summary['Q_delta_D_gt_0p75_violations']} |",
        "",
        "## 6. Bridge-Excursion Component",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| Q_exc_max | {summary['Q_exc_max']} |",
        f"| Q_exc_mean | {summary['Q_exc_mean']} |",
        f"| Q_exc_q95 | {summary['Q_exc_q95']} |",
        f"| Q_exc_q99 | {summary['Q_exc_q99']} |",
        f"| Q_exc_above_0p025_count | {summary['Q_exc_above_0p025_count']} |",
        "",
        "## 7. Residual Component",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| epsilon_min | {summary['epsilon_min']} |",
        f"| epsilon_max | {summary['epsilon_max']} |",
        f"| abs_epsilon_max | {summary['abs_epsilon_max']} |",
        f"| abs_epsilon_mean | {summary['abs_epsilon_mean']} |",
        f"| abs_epsilon_above_0p03_count | {summary['abs_epsilon_above_0p03_count']} |",
        f"| epsilon_positive_count | {summary['epsilon_positive_count']} |",
        f"| epsilon_negative_count | {summary['epsilon_negative_count']} |",
        "",
        "## 8. Formula Reconstruction",
        "",
        r"`epsilon` is the exported v3 formula residual. Therefore `Q_reconstructed = Q_delta_D + Q_exc + epsilon` should reproduce `Q_R2Q` up to floating tolerance.",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| formula_rows | {summary['formula_rows']} |",
        f"| formula_residual_max_abs | {summary['formula_residual_max_abs']} |",
        f"| formula_residual_mean_abs | {summary['formula_residual_mean_abs']} |",
        f"| formula_residual_cap_violations | {summary['formula_residual_cap_violations']} |",
        f"| pass_formula_reconstruction | {summary['pass_formula_reconstruction']} |",
        "",
        "## 9. Regime Decomposition",
        "",
        regimes.to_markdown(index=False),
        "",
        "## 10. Extremes",
        "",
        extremes_df.to_markdown(index=False),
        "",
        "## 11. Failures",
        "",
    ]
    if len(failures):
        lines += [failures.head(30).to_markdown(index=False)]
    else:
        lines += ["No component-bound failures."]
    lines += [
        "",
        "## 12. Recommended Theorem Form",
        "",
        f"`{summary['recommended_theorem_form']}`",
        "",
        "## 13. Recommended Next File",
        "",
        f"`{summary['recommended_next_file']}`",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
    ]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def refresh_manifest(paths: list[Path]) -> None:
    existing = pd.DataFrame()
    if MANIFEST.exists():
        try:
            existing = pd.read_csv(MANIFEST)
        except Exception:
            existing = pd.DataFrame()
    add = pd.DataFrame(
        [
            {
                "file": p.name,
                "path": str(p),
                "bytes": p.stat().st_size if p.exists() else 0,
                "status": "new_or_refreshed",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for p in paths
        ]
    )
    if len(existing):
        key = "file" if "file" in existing.columns else existing.columns[0]
        existing = existing[~existing[key].isin(add["file"])]
        out = pd.concat([existing, add], ignore_index=True, sort=False)
    else:
        out = add
    out.to_csv(MANIFEST, index=False)


def main() -> None:
    log("Starting RawR2Q component-bounds audit")
    df = load_rows()
    rows = build_audit_rows(df)
    summary = summarize(rows)
    regimes = by_regime(rows)
    extremes_df = extremes(rows)
    failures = rows[rows["component_bound_status"].eq("fail")].copy()

    rows.to_csv(ROWS_OUT, index=False)
    regimes.to_csv(BY_REGIME_OUT, index=False)
    extremes_df.to_csv(EXTREMES_OUT, index=False)
    failures.to_csv(FAILURES_OUT, index=False)
    write_summary(summary)
    write_doc(summary, regimes, extremes_df, failures)
    refresh_manifest([Path(__file__), SUMMARY_OUT, ROWS_OUT, BY_REGIME_OUT, EXTREMES_OUT, FAILURES_OUT, DOC_OUT])

    for k in [
        "rows",
        "primitive_full_rows",
        "primitive_missing_rows",
        "Q_exc_max",
        "Q_exc_above_0p025_count",
        "abs_epsilon_max",
        "abs_epsilon_above_0p03_count",
        "positive_Q_delta_D_max",
        "positive_Q_delta_D_above_0p25_count",
        "Q_delta_D_gt_0p75_count",
        "Q_delta_D_gt_0p75_violations",
        "component_bound_failures",
        "pass_rawr2q_component_bounds_empirical",
    ]:
        log(f"{k} = {summary[k]}")
    log(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
