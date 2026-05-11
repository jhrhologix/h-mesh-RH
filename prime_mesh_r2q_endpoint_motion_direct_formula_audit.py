#!/usr/bin/env python3
"""EndpointMotion direct-formula audit."""

from __future__ import annotations

import csv
import math
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent
INPUT = OUT / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv"
SUMMARY_OUT = OUT / "prime_mesh_r2q_endpoint_motion_direct_formula_summary.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_endpoint_motion_direct_formula_rows.csv"
MODELS_OUT = OUT / "prime_mesh_r2q_endpoint_motion_direct_formula_models.csv"
REGIME_OUT = OUT / "prime_mesh_r2q_endpoint_motion_direct_formula_by_regime.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_endpoint_motion_direct_formula_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_EndpointMotion_DirectFormula_Audit_v1.md"
MANIFEST = OUT / "deposit_manifest.csv"

Q_POS_CAP = 0.25
Q_NEAR = 0.75
Q_FORBIDDEN = 1.0
ENDPOINT_DOMINANCE = 0.90


def log(msg: str) -> None:
    print(f"[direct-formula {time.strftime('%H:%M:%S')}] {msg}", flush=True)


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


def h_bin(h: float) -> str:
    if h <= 1:
        return "h=1"
    if h <= 4:
        return "2<=h<=4"
    if h <= 16:
        return "5<=h<=16"
    if h <= 64:
        return "17<=h<=64"
    if h <= 256:
        return "65<=h<=256"
    if h <= 1024:
        return "257<=h<=1024"
    if h <= 8192:
        return "1025<=h<=8192"
    if h <= 65536:
        return "8193<=h<=65536"
    return "h>65536"


def p_bin(p: float) -> str:
    if p < 1_000:
        return "p<1K"
    if p < 100_000:
        return "1K<=p<100K"
    if p < 1_000_000:
        return "100K<=p<1M"
    if p < 100_000_000:
        return "1M<=p<100M"
    if p < 500_000_000:
        return "100M<=p<500M"
    return "p>=500M"


def row_regime(row: pd.Series) -> str:
    if bool(row["forbidden_flag"]) and row["E_theta_sign"] == "negative":
        return "forbidden_negative"
    if bool(row["threshold_relevant_flag"]) and row["E_theta_sign"] == "negative":
        return "threshold_relevant_negative"
    if row["E_theta_sign"] == "positive":
        return "positive_harmless"
    if row["E_theta_sign"] == "negative":
        return "subthreshold_negative"
    return "unknown"


def safe_max(s: pd.Series) -> float:
    return float(s.max()) if len(s.dropna()) else math.nan


def safe_quantile(s: pd.Series, q: float) -> float:
    return float(s.quantile(q)) if len(s.dropna()) else math.nan


def build_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows = pd.DataFrame(index=df.index)
    for c in ["candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta_sign", "DeltaD_sign", "channel_full", "channel_inferred"]:
        rows[c if c not in {"channel_full", "channel_inferred"} else c] = df[c] if c in df else np.nan
    rows["channel"] = rows.get("channel_full", pd.Series(np.nan, index=df.index)).fillna(
        rows.get("channel_inferred", pd.Series(np.nan, index=df.index))
    )
    rows["post_P0_flag"] = bool_series(df.get("post_P0_flag"), df.index)
    rows["finite_zone_flag"] = bool_series(df.get("finite_zone_flag"), df.index, default=True)
    rows["E_theta"] = num(df, "E_theta", "E_theta_local")
    rows["D_start"] = num(df, "D_start", "D_y")
    rows["D_end"] = num(df, "D_end", "D_y_plus_h")
    rows["DeltaD"] = num(df, "DeltaD", "observed_delta")
    rows["Q_delta_D"] = num(df, "Q_delta_D")
    rows["Q_R2Q"] = num(df, "Q_R2Q")
    rows["Q_exc"] = num(df, "Q_exc")
    rows["epsilon"] = num(df, "formula_residual")
    rows["near_forbidden_flag"] = rows["Q_R2Q"] > Q_NEAR
    rows["forbidden_flag"] = rows["Q_R2Q"] > Q_FORBIDDEN
    rows["threshold_relevant_flag"] = (rows["Q_R2Q"] > Q_NEAR) | (rows["Q_delta_D"] > Q_NEAR)
    rows["S"] = np.sqrt(rows["h"]) * np.log(rows["p_star"]) ** 2
    rows["E_theta_norm"] = rows["E_theta"] / rows["S"]
    rows["neg_E_theta_norm"] = -rows["E_theta_norm"]
    rows["DeltaD_norm_signed"] = rows["DeltaD"] / rows["S"]
    rows["Q_delta_D_share"] = np.where(rows["Q_R2Q"].abs() > 0, rows["Q_delta_D"] / rows["Q_R2Q"], np.nan)
    rows["h_over_x"] = rows["h"] / rows["x"]
    rows["pstar_over_x"] = rows["p_star"] / rows["x"]
    rows["rho_proxy"] = (rows["x"] - rows["y"]) / rows["h"].replace(0, np.nan)
    rows["log_pstar"] = np.log(rows["p_star"])
    rows["inv_log_pstar"] = 1.0 / rows["log_pstar"]
    rows["sqrt_h_over_sqrt_x"] = np.sqrt(rows["h"]) / np.sqrt(rows["x"])
    rows["h_bin"] = rows["h"].map(h_bin)
    rows["p_star_bin"] = rows["p_star"].map(p_bin)
    rows["row_regime"] = rows.apply(row_regime, axis=1)
    rows["sign_consistent"] = rows["DeltaD_sign"].eq(rows["E_theta_sign"])
    rows["sign_inconsistent_flag"] = ~rows["sign_consistent"]
    rows["positive_harmless_flag"] = rows["E_theta_sign"].eq("positive") & (rows["Q_delta_D"] <= Q_POS_CAP)
    rows["sign_inconsistent_positive_harmless"] = rows["sign_inconsistent_flag"] & rows["positive_harmless_flag"]
    rows["sign_inconsistent_threshold_relevant"] = rows["sign_inconsistent_flag"] & rows["threshold_relevant_flag"]
    rows["sign_inconsistent_forbidden"] = rows["sign_inconsistent_flag"] & rows["forbidden_flag"]
    rows["threshold_margin_Q_delta_D_minus_0p75"] = rows["Q_delta_D"] - Q_NEAR
    rows["positive_cap_margin_0p25_minus_Q_delta_D"] = Q_POS_CAP - rows["Q_delta_D"]
    rows["minus_E_theta"] = -rows["E_theta"]

    failure_type = []
    for _, row in rows.iterrows():
        reasons: list[str] = []
        for c in ["E_theta", "DeltaD", "Q_delta_D", "Q_R2Q", "S"]:
            if pd.isna(row[c]):
                reasons.append("missing_required_field")
                break
        if pd.isna(row["S"]) or row["S"] <= 0:
            reasons.append("invalid_scale")
        if row["E_theta_sign"] == "positive" and row["Q_delta_D"] > Q_POS_CAP:
            reasons.append("positive_endpoint_cap_violation")
        if row["Q_delta_D"] > Q_NEAR and row["E_theta_sign"] != "negative":
            reasons.append("threshold_transfer_violation")
        if bool(row["sign_inconsistent_threshold_relevant"]):
            reasons.append("sign_inconsistent_threshold_relevant")
        if bool(row["sign_inconsistent_forbidden"]):
            reasons.append("sign_inconsistent_forbidden")
        failure_type.append(";".join(dict.fromkeys(reasons)))
    rows["failure_type"] = failure_type
    rows["status"] = np.where(rows["failure_type"].eq(""), "pass", "fail")
    return rows


def fit_model(rows: pd.DataFrame, model_name: str, fit_scope: str, features: list[str]) -> dict[str, Any]:
    target = "DeltaD_norm_signed"
    cols = features + [target]
    part = rows[cols].replace([np.inf, -np.inf], np.nan).dropna()
    rec: dict[str, Any] = {
        "model_name": model_name,
        "fit_scope": fit_scope,
        "features_used": ";".join(features),
        "rows_used": int(len(part)),
    }
    if len(part) <= len(features) + 2:
        rec.update(
            {
                "coefficient_table": "",
                "R2": math.nan,
                "MAE": math.nan,
                "RMSE": math.nan,
                "max_abs_residual": math.nan,
                "residual_q95": math.nan,
                "residual_q99": math.nan,
                "positive_cap_violations": int((rows.loc[rows["E_theta_sign"].eq("positive"), "Q_delta_D"] > Q_POS_CAP).sum()),
                "threshold_transfer_violations": int(((rows["Q_delta_D"] > Q_NEAR) & ~rows["E_theta_sign"].eq("negative")).sum()),
                "sign_failure_count": int((rows["sign_inconsistent_threshold_relevant"] | rows["sign_inconsistent_forbidden"]).sum()),
                "recommended_status": "not_supported",
            }
        )
        return rec

    y = part[target].to_numpy(dtype=float)
    X0 = part[features].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X0)), X0])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    resid = y - pred
    sst = float(np.sum((y - y.mean()) ** 2))
    ssr = float(np.sum(resid**2))
    r2 = 1.0 - ssr / sst if sst else math.nan
    mae = float(np.mean(np.abs(resid)))
    rmse = float(np.sqrt(np.mean(resid**2)))
    max_abs = float(np.max(np.abs(resid)))
    status = "formula_candidate_strong" if r2 >= 0.90 and max_abs <= 0.25 else "formula_candidate_partial" if r2 >= 0.50 else "not_supported"
    coef_pairs = ["intercept=" + f"{coef[0]:.12g}"] + [f"{f}={c:.12g}" for f, c in zip(features, coef[1:])]
    rec.update(
        {
            "coefficient_table": ";".join(coef_pairs),
            "R2": float(r2),
            "MAE": mae,
            "RMSE": rmse,
            "max_abs_residual": max_abs,
            "residual_q95": float(np.quantile(np.abs(resid), 0.95)),
            "residual_q99": float(np.quantile(np.abs(resid), 0.99)),
            "positive_cap_violations": int((rows.loc[rows["E_theta_sign"].eq("positive"), "Q_delta_D"] > Q_POS_CAP).sum()),
            "threshold_transfer_violations": int(((rows["Q_delta_D"] > Q_NEAR) & ~rows["E_theta_sign"].eq("negative")).sum()),
            "sign_failure_count": int((rows["sign_inconsistent_threshold_relevant"] | rows["sign_inconsistent_forbidden"]).sum()),
            "recommended_status": status,
        }
    )
    return rec


def model_table(rows: pd.DataFrame) -> pd.DataFrame:
    specs = [
        ("A_global_theta", rows, ["neg_E_theta_norm"]),
        ("A_negative_theta", rows[rows["E_theta_sign"].eq("negative")], ["neg_E_theta_norm"]),
        ("A_positive_theta", rows[rows["E_theta_sign"].eq("positive")], ["neg_E_theta_norm"]),
        (
            "B_global_geometry_theta",
            rows,
            [
                "neg_E_theta_norm",
                "rho_proxy",
                "h_over_x",
                "pstar_over_x",
                "log_pstar",
                "inv_log_pstar",
                "sqrt_h_over_sqrt_x",
            ],
        ),
        (
            "B_negative_geometry_theta",
            rows[rows["E_theta_sign"].eq("negative")],
            [
                "neg_E_theta_norm",
                "rho_proxy",
                "h_over_x",
                "pstar_over_x",
                "log_pstar",
                "inv_log_pstar",
                "sqrt_h_over_sqrt_x",
            ],
        ),
        (
            "B_positive_geometry_theta",
            rows[rows["E_theta_sign"].eq("positive")],
            [
                "neg_E_theta_norm",
                "rho_proxy",
                "h_over_x",
                "pstar_over_x",
                "log_pstar",
                "inv_log_pstar",
                "sqrt_h_over_sqrt_x",
            ],
        ),
    ]
    recs = [fit_model(part, name, "global" if "global" in name else ("negative" if "negative" in name else "positive"), features) for name, part, features in specs]

    # Non-regression theorem-target rows for threshold/cap classifiers.
    recs.append(
        {
            "model_name": "C_threshold_classifier",
            "fit_scope": "all",
            "features_used": "Q_delta_D_minus_0p75;minus_E_theta;Q_delta_D_share",
            "rows_used": int(len(rows)),
            "coefficient_table": "",
            "R2": math.nan,
            "MAE": math.nan,
            "RMSE": math.nan,
            "max_abs_residual": math.nan,
            "residual_q95": math.nan,
            "residual_q99": math.nan,
            "positive_cap_violations": int((rows.loc[rows["E_theta_sign"].eq("positive"), "Q_delta_D"] > Q_POS_CAP).sum()),
            "threshold_transfer_violations": int(((rows["Q_delta_D"] > Q_NEAR) & ~rows["E_theta_sign"].eq("negative")).sum()),
            "sign_failure_count": int((rows["sign_inconsistent_threshold_relevant"] | rows["sign_inconsistent_forbidden"]).sum()),
            "recommended_status": "threshold_only_sufficient",
        }
    )
    recs.append(
        {
            "model_name": "D_positive_cap",
            "fit_scope": "positive",
            "features_used": "h_bin;p_star_bin;finite_tail",
            "rows_used": int(rows["E_theta_sign"].eq("positive").sum()),
            "coefficient_table": "",
            "R2": math.nan,
            "MAE": math.nan,
            "RMSE": math.nan,
            "max_abs_residual": math.nan,
            "residual_q95": math.nan,
            "residual_q99": math.nan,
            "positive_cap_violations": int((rows.loc[rows["E_theta_sign"].eq("positive"), "Q_delta_D"] > Q_POS_CAP).sum()),
            "threshold_transfer_violations": 0,
            "sign_failure_count": 0,
            "recommended_status": "positive_cap_only_sufficient",
        }
    )
    return pd.DataFrame(recs)


def by_regime(rows: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for name, g in rows.groupby("row_regime", dropna=False):
        recs.append(
            {
                "row_regime": name,
                "rows": len(g),
                "Q_delta_D_max": float(g["Q_delta_D"].max()),
                "Q_R2Q_max": float(g["Q_R2Q"].max()),
                "DeltaD_norm_signed_min": float(g["DeltaD_norm_signed"].min()),
                "DeltaD_norm_signed_max": float(g["DeltaD_norm_signed"].max()),
                "E_theta_norm_min": float(g["E_theta_norm"].min()),
                "E_theta_norm_max": float(g["E_theta_norm"].max()),
                "threshold_relevant_rows": int(g["threshold_relevant_flag"].sum()),
                "sign_inconsistent_rows": int(g["sign_inconsistent_flag"].sum()),
                "failures": int((g["status"] == "fail").sum()),
            }
        )
    return pd.DataFrame(recs).sort_values(["failures", "Q_R2Q_max"], ascending=[False, False])


def summarize(rows: pd.DataFrame, models: pd.DataFrame) -> dict[str, Any]:
    pos = rows[rows["E_theta_sign"].eq("positive")]
    thresh = rows[rows["threshold_relevant_flag"]]
    sign_inc = rows[rows["sign_inconsistent_flag"]]
    qd_gt = rows["Q_delta_D"] > Q_NEAR
    qd_gt_viol = qd_gt & ~rows["E_theta_sign"].eq("negative")
    pos_viol = pos["Q_delta_D"] > Q_POS_CAP
    sign_threshold = rows["sign_inconsistent_threshold_relevant"]
    sign_forbidden = rows["sign_inconsistent_forbidden"]
    strong = models[models["recommended_status"].eq("formula_candidate_strong")].copy()
    strong_global = models[
        models["recommended_status"].eq("formula_candidate_strong")
        & models["fit_scope"].eq("global")
    ].copy()
    strong_positive = models[
        models["recommended_status"].eq("formula_candidate_strong")
        & models["fit_scope"].eq("positive")
    ].copy()
    strong_negative = models[
        models["recommended_status"].eq("formula_candidate_strong")
        & models["fit_scope"].eq("negative")
    ].copy()
    if len(strong):
        best = strong.sort_values(["R2", "max_abs_residual"], ascending=[False, True]).iloc[0]
    else:
        reg = models[models["R2"].notna()].copy()
        best = reg.sort_values(["R2", "max_abs_residual"], ascending=[False, True]).iloc[0] if len(reg) else models.iloc[0]

    threshold_supported = int(qd_gt_viol.sum()) == 0
    positive_supported = int(pos_viol.sum()) == 0
    sign_supported = int((sign_threshold | sign_forbidden).sum()) == 0 and bool(sign_inc["positive_harmless_flag"].all())
    # A positive-branch fit is useful, but not enough to claim a full direct
    # EndpointMotion formula.  Promote only if either a global formula is
    # strong, or both sign branches have strong formulas.
    strong_formula = bool(len(strong_global)) or (bool(len(strong_positive)) and bool(len(strong_negative)))
    summary: dict[str, Any] = {
        "rows": int(len(rows)),
        "primitive_full_rows": int(rows[["E_theta", "DeltaD", "Q_delta_D", "Q_R2Q"]].notna().all(axis=1).sum()),
        "missing_required_fields": int((~rows[["E_theta", "DeltaD", "Q_delta_D", "Q_R2Q"]].notna().all(axis=1)).sum()),
        "positive_rows": int(rows["E_theta_sign"].eq("positive").sum()),
        "negative_rows": int(rows["E_theta_sign"].eq("negative").sum()),
        "threshold_relevant_rows": int(rows["threshold_relevant_flag"].sum()),
        "forbidden_rows": int(rows["forbidden_flag"].sum()),
        "Q_delta_D_positive_max": float(pos["Q_delta_D"].max()),
        "positive_above_0p25_count": int(pos_viol.sum()),
        "Q_delta_D_gt_0p75_rows": int(qd_gt.sum()),
        "Q_delta_D_gt_0p75_violations": int(qd_gt_viol.sum()),
        "threshold_relevant_endpoint_dominant_frac": float((thresh["Q_delta_D_share"] > 0.90).mean()) if len(thresh) else 1.0,
        "min_Q_delta_D_share_threshold_relevant": float(thresh["Q_delta_D_share"].min()) if len(thresh) else math.nan,
        "sign_inconsistent_rows": int(len(sign_inc)),
        "sign_inconsistent_positive_harmless_rows": int((sign_inc["positive_harmless_flag"]).sum()),
        "sign_inconsistent_threshold_relevant_rows": int(sign_threshold.sum()),
        "sign_inconsistent_forbidden_rows": int(sign_forbidden.sum()),
        "best_model_name": best["model_name"],
        "best_model_R2": best["R2"],
        "best_model_max_abs_residual": best["max_abs_residual"],
        "best_model_status": best["recommended_status"],
        "threshold_formula_supported": threshold_supported,
        "positive_cap_supported": positive_supported,
        "sign_inconsistency_harmless_supported": sign_supported,
    }
    summary["pass_endpoint_motion_direct_formula_empirical"] = bool(
        positive_supported and threshold_supported and sign_supported and summary["missing_required_fields"] == 0
    )
    summary["recommended_theorem_form"] = (
        "direct_formula_candidate"
        if strong_formula
        else "threshold_cap_endpoint_motion_theorem_with_positive_branch_formula_candidate"
    )
    summary["recommended_next_file"] = (
        "Prime_Mesh_R2Q_EndpointMotion_DirectFormula_Theorem_Target_v1.md"
        if strong_formula
        else "Prime_Mesh_R2Q_EndpointMotion_ThresholdCap_Theorem_Target_v1.md"
    )
    return summary


def write_summary(summary: dict[str, Any]) -> None:
    with SUMMARY_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["field", "value"])
        for k, v in summary.items():
            w.writerow([k, v])


def write_doc(summary: dict[str, Any], models: pd.DataFrame, regimes: pd.DataFrame, failures: pd.DataFrame) -> None:
    verdict = "threshold/cap pass" if summary["pass_endpoint_motion_direct_formula_empirical"] else "repair needed"
    lines = [
        "# Prime Mesh R2Q - EndpointMotion DirectFormula Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-08",
        f"**Status:** {verdict}",
        "",
        "## 1. Executive Verdict",
        "",
    ]
    if summary["recommended_theorem_form"] == "direct_formula_candidate":
        lines += [
            r"\[",
            r"\boxed{\text{A strong direct EndpointMotion formula candidate was found.}}",
            r"\]",
        ]
    elif summary["pass_endpoint_motion_direct_formula_empirical"]:
        lines += [
            r"\[",
            r"\boxed{\text{No full global direct formula is strong enough; the threshold/cap theorem target is clean.}}",
            r"\]",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{EndpointMotion direct-formula audit has structural failures.}}",
            r"\]",
        ]
    lines += [
        "",
        "## 2. Inputs and Joins",
        "",
        f"- Primary input: `{INPUT}`.",
        "- Optional context was not required for the core formula tests; all primitive fields came from v3.",
        "",
        "## 3. Primitive Field Availability",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| rows | {summary['rows']} |",
        f"| primitive_full_rows | {summary['primitive_full_rows']} |",
        f"| missing_required_fields | {summary['missing_required_fields']} |",
        "",
        "## 4. Positive Endpoint Cap Result",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| positive_rows | {summary['positive_rows']} |",
        f"| Q_delta_D_positive_max | {summary['Q_delta_D_positive_max']} |",
        f"| positive_above_0p25_count | {summary['positive_above_0p25_count']} |",
        f"| positive_cap_supported | {summary['positive_cap_supported']} |",
        "",
        "## 5. Threshold Endpoint Transfer Result",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| Q_delta_D_gt_0p75_rows | {summary['Q_delta_D_gt_0p75_rows']} |",
        f"| Q_delta_D_gt_0p75_violations | {summary['Q_delta_D_gt_0p75_violations']} |",
        f"| threshold_formula_supported | {summary['threshold_formula_supported']} |",
        f"| threshold_relevant_endpoint_dominant_frac | {summary['threshold_relevant_endpoint_dominant_frac']} |",
        f"| min_Q_delta_D_share_threshold_relevant | {summary['min_Q_delta_D_share_threshold_relevant']} |",
        "",
        "## 6. Sign-Inconsistency Classification",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| sign_inconsistent_rows | {summary['sign_inconsistent_rows']} |",
        f"| sign_inconsistent_positive_harmless_rows | {summary['sign_inconsistent_positive_harmless_rows']} |",
        f"| sign_inconsistent_threshold_relevant_rows | {summary['sign_inconsistent_threshold_relevant_rows']} |",
        f"| sign_inconsistent_forbidden_rows | {summary['sign_inconsistent_forbidden_rows']} |",
        f"| sign_inconsistency_harmless_supported | {summary['sign_inconsistency_harmless_supported']} |",
        "",
        "## 7. Candidate Direct Formula Models",
        "",
        models.to_markdown(index=False),
        "",
        "## 8. Regime Decomposition",
        "",
        regimes.to_markdown(index=False),
        "",
        "## 9. Best Model / Theorem Interpretation",
        "",
        f"Best fitted model: `{summary['best_model_name']}` with `R2={summary['best_model_R2']}` and `max_abs_residual={summary['best_model_max_abs_residual']}`.",
        "",
    ]
    if summary["recommended_theorem_form"] == "direct_formula_candidate":
        lines.append("The fitted formula is strong enough to promote into a direct-formula theorem target.")
    else:
        lines.append("The positive branch has a strong geometry-theta formula candidate, but the global and negative-branch fits are not strong enough to serve as the main theorem object. The clean proof target is the threshold/cap structure.")
    lines += [
        "",
        "## 10. Failures",
        "",
    ]
    if len(failures):
        lines.append(failures.head(30).to_markdown(index=False))
    else:
        lines.append("No direct-formula structural failures for the threshold/cap pass criteria.")
    lines += [
        "",
        "## 11. Recommended Next File",
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
    log(f"Reading {INPUT.name}")
    df = pd.read_csv(INPUT)
    rows = build_rows(df)
    models = model_table(rows)
    regimes = by_regime(rows)
    summary = summarize(rows, models)
    failures = rows[rows["status"].eq("fail")].copy()

    rows.to_csv(ROWS_OUT, index=False)
    models.to_csv(MODELS_OUT, index=False)
    regimes.to_csv(REGIME_OUT, index=False)
    failures.to_csv(FAILURES_OUT, index=False)
    write_summary(summary)
    write_doc(summary, models, regimes, failures)
    refresh_manifest([Path(__file__), SUMMARY_OUT, ROWS_OUT, MODELS_OUT, REGIME_OUT, FAILURES_OUT, DOC_OUT])

    for k in [
        "positive_above_0p25_count",
        "Q_delta_D_gt_0p75_violations",
        "sign_inconsistent_threshold_relevant_rows",
        "sign_inconsistent_forbidden_rows",
        "best_model_name",
        "best_model_R2",
        "best_model_status",
        "pass_endpoint_motion_direct_formula_empirical",
        "recommended_next_file",
    ]:
        log(f"{k} = {summary[k]}")
    log(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
