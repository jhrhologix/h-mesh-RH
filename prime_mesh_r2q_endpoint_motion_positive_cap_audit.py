#!/usr/bin/env python3
"""EndpointMotion positive-cap audit."""

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
SUMMARY_OUT = OUT / "prime_mesh_r2q_endpoint_motion_positive_cap_summary.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_endpoint_motion_positive_cap_rows.csv"
REGIME_OUT = OUT / "prime_mesh_r2q_endpoint_motion_positive_cap_by_regime.csv"
MODELS_OUT = OUT / "prime_mesh_r2q_endpoint_motion_positive_cap_models.csv"
EXTREMES_OUT = OUT / "prime_mesh_r2q_endpoint_motion_positive_cap_extremes.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_endpoint_motion_positive_cap_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_EndpointMotion_PositiveCap_Audit_v1.md"
MANIFEST = OUT / "deposit_manifest.csv"

CAP = 0.25


def log(msg: str) -> None:
    print(f"[positive-cap {time.strftime('%H:%M:%S')}] {msg}", flush=True)


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
    return "h>1024"


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


def safe(s: pd.Series, fn: str, q: float | None = None) -> float:
    s = s.dropna()
    if not len(s):
        return math.nan
    if fn == "min":
        return float(s.min())
    if fn == "max":
        return float(s.max())
    if fn == "mean":
        return float(s.mean())
    if fn == "median":
        return float(s.median())
    if fn == "q":
        return float(s.quantile(q if q is not None else 0.5))
    raise ValueError(fn)


def build_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows = pd.DataFrame(index=df.index)
    for c in ["candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta_sign", "DeltaD_sign"]:
        rows[c] = df[c] if c in df else np.nan
    rows["post_P0_flag"] = bool_series(df.get("post_P0_flag"), df.index)
    rows["finite_zone_flag"] = bool_series(df.get("finite_zone_flag"), df.index, default=True)
    rows["source"] = df.get("source_coordinate", pd.Series("v3", index=df.index))
    rows["E_theta"] = num(df, "E_theta", "E_theta_local")
    rows["DeltaD"] = num(df, "DeltaD", "observed_delta")
    rows["Q_delta_D"] = num(df, "Q_delta_D")
    rows["Q_R2Q"] = num(df, "Q_R2Q")
    rows["Q_exc"] = num(df, "Q_exc")
    rows["epsilon"] = num(df, "formula_residual")
    rows["S"] = np.sqrt(rows["h"]) * np.log(rows["p_star"]) ** 2
    rows["E_theta_normalized"] = rows["E_theta"] / rows["S"]
    rows["positive_flag"] = rows["E_theta_sign"].eq("positive") | (rows["E_theta"] > 0)
    rows["negative_flag"] = rows["E_theta_sign"].eq("negative") | (rows["E_theta"] < 0)
    rows["threshold_relevant_flag"] = rows["Q_R2Q"] > 0.75
    rows["forbidden_flag"] = rows["Q_R2Q"] > 1.0
    rows["positive_above_0p20_flag"] = rows["positive_flag"] & (rows["Q_delta_D"] > 0.20)
    rows["positive_above_0p225_flag"] = rows["positive_flag"] & (rows["Q_delta_D"] > 0.225)
    rows["positive_above_0p24_flag"] = rows["positive_flag"] & (rows["Q_delta_D"] > 0.24)
    rows["positive_above_0p25_flag"] = rows["positive_flag"] & (rows["Q_delta_D"] > 0.25)
    rows["positive_cap_pass_flag"] = ~rows["positive_flag"] | (rows["Q_delta_D"] <= CAP)
    rows["h_bin"] = rows["h"].map(h_bin)
    rows["p_star_bin"] = rows["p_star"].map(p_bin)
    rows["finite_tail_regime"] = np.where(rows["post_P0_flag"], "post_P0_tail", "finite_zone")
    rows["short_window_flag"] = rows["h"] <= 4
    rows["single_step_flag"] = rows["h"] <= 1
    rows["sign_consistent"] = rows["DeltaD_sign"].eq(rows["E_theta_sign"])
    rows["sign_inconsistent_positive_harmless"] = rows["positive_flag"] & ~rows["sign_consistent"] & rows["positive_cap_pass_flag"]

    rows["neg_E_theta_norm"] = -rows["E_theta_normalized"]
    rows["rho_proxy"] = (rows["x"] - rows["y"]) / rows["h"].replace(0, np.nan)
    rows["h_over_x"] = rows["h"] / rows["x"]
    rows["pstar_over_x"] = rows["p_star"] / rows["x"]
    rows["log_pstar"] = np.log(rows["p_star"])
    rows["inv_log_pstar"] = 1.0 / rows["log_pstar"]
    rows["sqrt_h_over_sqrt_x"] = np.sqrt(rows["h"]) / np.sqrt(rows["x"])

    pos = rows[rows["positive_flag"]].copy()
    features = [
        "neg_E_theta_norm",
        "rho_proxy",
        "h_over_x",
        "pstar_over_x",
        "log_pstar",
        "inv_log_pstar",
        "sqrt_h_over_sqrt_x",
    ]
    model_part = pos[features + ["Q_delta_D"]].replace([np.inf, -np.inf], np.nan).dropna()
    rows["positive_formula_prediction"] = np.nan
    rows["positive_formula_residual"] = np.nan
    if len(model_part) > len(features) + 2:
        X0 = model_part[features].to_numpy()
        X = np.column_stack([np.ones(len(X0)), X0])
        y = model_part["Q_delta_D"].to_numpy()
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        all_pos = rows.loc[rows["positive_flag"], features].replace([np.inf, -np.inf], np.nan)
        ok = all_pos.notna().all(axis=1)
        Xp = np.column_stack([np.ones(int(ok.sum())), all_pos.loc[ok].to_numpy()])
        pred = Xp @ coef
        rows.loc[all_pos.loc[ok].index, "positive_formula_prediction"] = pred
        rows.loc[all_pos.loc[ok].index, "positive_formula_residual"] = (
            rows.loc[all_pos.loc[ok].index, "Q_delta_D"] - pred
        )

    failure_type = []
    for _, row in rows.iterrows():
        reasons = []
        if pd.isna(row["E_theta"]):
            reasons.append("missing_E_theta")
        if pd.isna(row["Q_delta_D"]):
            reasons.append("missing_Q_delta_D")
        if pd.isna(row["DeltaD"]):
            reasons.append("missing_DeltaD")
        if pd.isna(row["S"]) or row["S"] <= 0:
            reasons.append("invalid_scale")
        if bool(row["positive_above_0p25_flag"]):
            reasons.append("positive_above_0p25")
        if bool(row["positive_flag"]) and pd.isna(row["Q_delta_D"]):
            reasons.append("positive_missing_primitive")
        if bool(row["positive_flag"]) and pd.isna(row["positive_formula_prediction"]):
            reasons.append("formula_feature_missing")
        if bool(row["positive_flag"]) and bool(row["threshold_relevant_flag"]):
            reasons.append("unexpected_positive_threshold_relevant")
        failure_type.append(";".join(reasons))
    rows["failure_type"] = failure_type
    rows["status"] = np.where(rows["failure_type"].eq(""), "pass", "fail")
    return rows


def fit_positive_model(rows: pd.DataFrame) -> pd.DataFrame:
    pos = rows[rows["positive_flag"]].copy()
    features = [
        "neg_E_theta_norm",
        "rho_proxy",
        "h_over_x",
        "pstar_over_x",
        "log_pstar",
        "inv_log_pstar",
        "sqrt_h_over_sqrt_x",
    ]
    part = pos[features + ["Q_delta_D"]].replace([np.inf, -np.inf], np.nan).dropna()
    rec: dict[str, Any] = {
        "model_name": "B_positive_geometry_theta",
        "rows_used": int(len(part)),
        "features_used": ";".join(features),
    }
    if len(part) <= len(features) + 2:
        rec.update(
            {
                "R2": math.nan,
                "MAE": math.nan,
                "RMSE": math.nan,
                "max_abs_residual": math.nan,
                "residual_q95": math.nan,
                "residual_q99": math.nan,
                "positive_cap_violations_after_model_bound": int((pos["Q_delta_D"] > CAP).sum()),
                "recommended_status": "not_supported",
            }
        )
    else:
        X0 = part[features].to_numpy()
        X = np.column_stack([np.ones(len(X0)), X0])
        y = part["Q_delta_D"].to_numpy()
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        pred = X @ coef
        resid = y - pred
        sst = float(np.sum((y - y.mean()) ** 2))
        ssr = float(np.sum(resid**2))
        r2 = 1.0 - ssr / sst if sst else math.nan
        rec.update(
            {
                "R2": float(r2),
                "MAE": float(np.mean(np.abs(resid))),
                "RMSE": float(np.sqrt(np.mean(resid**2))),
                "max_abs_residual": float(np.max(np.abs(resid))),
                "residual_q95": float(np.quantile(np.abs(resid), 0.95)),
                "residual_q99": float(np.quantile(np.abs(resid), 0.99)),
                "positive_cap_violations_after_model_bound": int((pos["Q_delta_D"] > CAP).sum()),
                "recommended_status": "formula_candidate_strong" if r2 >= 0.90 and float(np.max(np.abs(resid))) < 0.03 else "formula_candidate_partial",
            }
        )
    return pd.DataFrame([rec])


def group_stats(rows: pd.DataFrame) -> pd.DataFrame:
    pos = rows[rows["positive_flag"]].copy()
    groups: list[tuple[str, pd.DataFrame]] = [
        ("all_positive", pos),
        ("finite_zone", pos[pos["finite_zone_flag"]]),
        ("post_P0_tail", pos[pos["post_P0_flag"]]),
        ("sign_inconsistent_positive_harmless", pos[pos["sign_inconsistent_positive_harmless"]]),
    ]
    groups += [(f"h_bin:{k}", g) for k, g in pos.groupby("h_bin")]
    groups += [(f"p_star_bin:{k}", g) for k, g in pos.groupby("p_star_bin")]
    recs = []
    for name, g in groups:
        recs.append(
            {
                "regime": name,
                "rows": int(len(g)),
                "Q_delta_D_min": safe(g["Q_delta_D"], "min"),
                "Q_delta_D_max": safe(g["Q_delta_D"], "max"),
                "Q_delta_D_mean": safe(g["Q_delta_D"], "mean"),
                "Q_delta_D_median": safe(g["Q_delta_D"], "median"),
                "Q_delta_D_q95": safe(g["Q_delta_D"], "q", 0.95),
                "Q_delta_D_q99": safe(g["Q_delta_D"], "q", 0.99),
                "above_0p20": int((g["Q_delta_D"] > 0.20).sum()),
                "above_0p225": int((g["Q_delta_D"] > 0.225).sum()),
                "above_0p24": int((g["Q_delta_D"] > 0.24).sum()),
                "above_0p25": int((g["Q_delta_D"] > 0.25).sum()),
                "Q_R2Q_max": safe(g["Q_R2Q"], "max"),
                "Q_exc_max": safe(g["Q_exc"], "max"),
                "abs_epsilon_max": safe(g["epsilon"].abs(), "max"),
            }
        )
    return pd.DataFrame(recs)


def extremes(rows: pd.DataFrame) -> pd.DataFrame:
    pos = rows[rows["positive_flag"]].copy()
    recs = []
    for name, col, asc in [
        ("positive_Q_delta_D_max", "Q_delta_D", False),
        ("positive_Q_R2Q_max", "Q_R2Q", False),
        ("positive_Q_exc_max", "Q_exc", False),
        ("positive_abs_epsilon_max", "epsilon", False),
        ("positive_formula_residual_abs_max", "positive_formula_residual", False),
    ]:
        if not len(pos) or pos[col].dropna().empty:
            continue
        if name.endswith("abs_max"):
            idx = pos[col].abs().idxmax()
            r = pos.loc[idx]
            val = abs(r[col])
        else:
            r = pos.sort_values(col, ascending=asc).iloc[0]
            val = r[col]
        recs.append(
            {
                "extreme": name,
                "value": val,
                "candidate_id": r.get("candidate_id"),
                "block_id": r.get("block_id"),
                "x": r.get("x"),
                "y": r.get("y"),
                "h": r.get("h"),
                "p_star": r.get("p_star"),
                "Q_delta_D": r.get("Q_delta_D"),
                "Q_R2Q": r.get("Q_R2Q"),
                "Q_exc": r.get("Q_exc"),
                "epsilon": r.get("epsilon"),
                "h_bin": r.get("h_bin"),
                "p_star_bin": r.get("p_star_bin"),
                "status": r.get("status"),
            }
        )
    return pd.DataFrame(recs)


def summarize(rows: pd.DataFrame, model: pd.DataFrame) -> dict[str, Any]:
    pos = rows[rows["positive_flag"]].copy()
    sign_inc = pos[pos["sign_inconsistent_positive_harmless"]]
    positive_failures = rows[rows["positive_above_0p25_flag"]]
    summary: dict[str, Any] = {
        "rows": int(len(rows)),
        "primitive_full_rows": int(rows[["E_theta", "DeltaD", "Q_delta_D"]].notna().all(axis=1).sum()),
        "primitive_missing_rows": int((~rows[["E_theta", "DeltaD", "Q_delta_D"]].notna().all(axis=1)).sum()),
        "positive_rows": int(len(pos)),
        "negative_rows": int(rows["negative_flag"].sum()),
        "zero_rows": int((rows["E_theta"] == 0).sum()),
        "unknown_sign_rows": int((~rows["E_theta_sign"].isin(["positive", "negative", "zero"])).sum()),
        "post_P0_positive_rows": int((pos["post_P0_flag"]).sum()),
        "finite_positive_rows": int((pos["finite_zone_flag"]).sum()),
        "positive_Q_delta_D_min": safe(pos["Q_delta_D"], "min"),
        "positive_Q_delta_D_max": safe(pos["Q_delta_D"], "max"),
        "positive_Q_delta_D_mean": safe(pos["Q_delta_D"], "mean"),
        "positive_Q_delta_D_median": safe(pos["Q_delta_D"], "median"),
        "positive_Q_delta_D_q95": safe(pos["Q_delta_D"], "q", 0.95),
        "positive_Q_delta_D_q99": safe(pos["Q_delta_D"], "q", 0.99),
        "positive_Q_R2Q_max": safe(pos["Q_R2Q"], "max"),
        "positive_Q_exc_max": safe(pos["Q_exc"], "max"),
        "positive_abs_epsilon_max": safe(pos["epsilon"].abs(), "max"),
        "positive_above_0p20_count": int((pos["Q_delta_D"] > 0.20).sum()),
        "positive_above_0p225_count": int((pos["Q_delta_D"] > 0.225).sum()),
        "positive_above_0p24_count": int((pos["Q_delta_D"] > 0.24).sum()),
        "positive_above_0p25_count": int((pos["Q_delta_D"] > 0.25).sum()),
        "positive_above_0p25_frac": float((pos["Q_delta_D"] > 0.25).mean()) if len(pos) else math.nan,
        "positive_cap_margin_to_0p25": float(CAP - pos["Q_delta_D"].max()),
        "positive_tail_Q_delta_D_max": safe(pos.loc[pos["post_P0_flag"], "Q_delta_D"], "max"),
        "positive_finite_Q_delta_D_max": safe(pos.loc[pos["finite_zone_flag"], "Q_delta_D"], "max"),
        "sign_inconsistent_positive_rows": int(len(sign_inc)),
        "sign_inconsistent_positive_Q_delta_D_max": safe(sign_inc["Q_delta_D"], "max"),
        "sign_inconsistent_threshold_relevant_rows": int((pos["threshold_relevant_flag"] & ~pos["sign_consistent"]).sum()),
        "sign_inconsistent_forbidden_rows": int((pos["forbidden_flag"] & ~pos["sign_consistent"]).sum()),
        "positive_formula_model": model.iloc[0]["model_name"],
        "positive_formula_R2": model.iloc[0]["R2"],
        "positive_formula_max_abs_residual": model.iloc[0]["max_abs_residual"],
        "positive_cap_failures": int(len(positive_failures)),
    }
    summary["pass_endpoint_motion_positive_cap_empirical"] = bool(
        summary["primitive_missing_rows"] == 0
        and summary["positive_above_0p25_count"] == 0
        and summary["positive_cap_failures"] == 0
    )
    summary["recommended_theorem_form"] = "E_theta_positive_implies_Q_delta_D_le_1_over_4"
    summary["recommended_next_file"] = (
        "Prime_Mesh_R2Q_EndpointMotion_PositiveCap_Theorem_Target_v1.md"
        if summary["pass_endpoint_motion_positive_cap_empirical"]
        else "Prime_Mesh_R2Q_EndpointMotion_PositiveCap_Repair_Map_v1.md"
    )
    return summary


def write_summary(summary: dict[str, Any]) -> None:
    with SUMMARY_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["field", "value"])
        for k, v in summary.items():
            w.writerow([k, v])


def write_doc(summary: dict[str, Any], groups: pd.DataFrame, model: pd.DataFrame, ex: pd.DataFrame, failures: pd.DataFrame) -> None:
    verdict = "pass" if summary["pass_endpoint_motion_positive_cap_empirical"] else "repair needed"
    lines = [
        "# Prime Mesh R2Q - EndpointMotion PositiveCap Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-09",
        f"**Status:** {verdict}",
        "",
        "## 1. Executive Verdict",
        "",
    ]
    if summary["pass_endpoint_motion_positive_cap_empirical"]:
        lines += [
            r"\[",
            r"\boxed{E_\theta(J)>0\Rightarrow Q_{\Delta D}(J)\le1/4\text{ passes empirically on the full v3 inventory.}}",
            r"\]",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{Positive endpoint-motion cap has failures requiring repair.}}",
            r"\]",
        ]
    lines += [
        "",
        "## 2. Inputs Used",
        "",
        f"- Primary input: `{INPUT}`.",
        "",
        "## 3. Primitive Coverage",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| rows | {summary['rows']} |",
        f"| primitive_full_rows | {summary['primitive_full_rows']} |",
        f"| primitive_missing_rows | {summary['primitive_missing_rows']} |",
        "",
        "## 4. Positive Cap Result",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| positive_rows | {summary['positive_rows']} |",
        f"| positive_Q_delta_D_max | {summary['positive_Q_delta_D_max']} |",
        f"| positive_Q_delta_D_q95 | {summary['positive_Q_delta_D_q95']} |",
        f"| positive_Q_delta_D_q99 | {summary['positive_Q_delta_D_q99']} |",
        f"| positive_above_0p20_count | {summary['positive_above_0p20_count']} |",
        f"| positive_above_0p225_count | {summary['positive_above_0p225_count']} |",
        f"| positive_above_0p24_count | {summary['positive_above_0p24_count']} |",
        f"| positive_above_0p25_count | {summary['positive_above_0p25_count']} |",
        f"| positive_cap_margin_to_0p25 | {summary['positive_cap_margin_to_0p25']} |",
        "",
        "## 5. Regime Decomposition",
        "",
        groups.to_markdown(index=False),
        "",
        "## 6. Sign-Inconsistency Harmlessness",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| sign_inconsistent_positive_rows | {summary['sign_inconsistent_positive_rows']} |",
        f"| sign_inconsistent_positive_Q_delta_D_max | {summary['sign_inconsistent_positive_Q_delta_D_max']} |",
        f"| sign_inconsistent_threshold_relevant_rows | {summary['sign_inconsistent_threshold_relevant_rows']} |",
        f"| sign_inconsistent_forbidden_rows | {summary['sign_inconsistent_forbidden_rows']} |",
        "",
        "## 7. Positive Formula Candidate Result",
        "",
        model.to_markdown(index=False),
        "",
        "This model is supporting evidence only. The audit pass depends on the actual cap.",
        "",
        "## 8. Extremes",
        "",
        ex.to_markdown(index=False),
        "",
        "## 9. Failures",
        "",
    ]
    if len(failures):
        lines.append(failures.head(30).to_markdown(index=False))
    else:
        lines.append("No positive-cap failures.")
    lines += [
        "",
        "## 10. Recommended Theorem Form",
        "",
        f"`{summary['recommended_theorem_form']}`",
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
    model = fit_positive_model(rows)
    groups = group_stats(rows)
    ex = extremes(rows)
    failures = rows[rows["failure_type"].ne("")]
    summary = summarize(rows, model)

    rows.to_csv(ROWS_OUT, index=False)
    groups.to_csv(REGIME_OUT, index=False)
    model.to_csv(MODELS_OUT, index=False)
    ex.to_csv(EXTREMES_OUT, index=False)
    failures.to_csv(FAILURES_OUT, index=False)
    write_summary(summary)
    write_doc(summary, groups, model, ex, failures)
    refresh_manifest([Path(__file__), SUMMARY_OUT, ROWS_OUT, REGIME_OUT, MODELS_OUT, EXTREMES_OUT, FAILURES_OUT, DOC_OUT])

    for k in [
        "positive_rows",
        "positive_Q_delta_D_max",
        "positive_above_0p20_count",
        "positive_above_0p225_count",
        "positive_above_0p24_count",
        "positive_above_0p25_count",
        "positive_tail_Q_delta_D_max",
        "positive_formula_R2",
        "positive_cap_failures",
        "pass_endpoint_motion_positive_cap_empirical",
    ]:
        log(f"{k} = {summary[k]}")
    log(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
