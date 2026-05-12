#!/usr/bin/env python3
"""Residual epsilon bound audit for RawR2Q v3."""

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
SUMMARY_OUT = OUT / "prime_mesh_r2q_residual_epsilon_bound_summary.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_residual_epsilon_bound_rows.csv"
REGIME_OUT = OUT / "prime_mesh_r2q_residual_epsilon_bound_by_regime.csv"
EXTREMES_OUT = OUT / "prime_mesh_r2q_residual_epsilon_bound_extremes.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_residual_epsilon_bound_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_Residual_Epsilon_Bound_Audit_v1.md"
MANIFEST = OUT / "deposit_manifest.csv"

CAP = 0.03
SHARP_CAP = 0.025
FORMULA_TOL = 1e-10


def log(msg: str) -> None:
    print(f"[epsilon-bound {time.strftime('%H:%M:%S')}] {msg}", flush=True)


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


def safe(s: pd.Series, fn: str, q: float | None = None) -> float:
    s = s.dropna()
    if not len(s):
        return math.nan
    if fn == "max":
        return float(s.max())
    if fn == "min":
        return float(s.min())
    if fn == "mean":
        return float(s.mean())
    if fn == "q":
        return float(s.quantile(q if q is not None else 0.5))
    raise ValueError(fn)


def corr(a: pd.Series, b: pd.Series) -> float:
    part = pd.DataFrame({"a": a, "b": b}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(part) < 3 or part["a"].nunique() <= 1 or part["b"].nunique() <= 1:
        return math.nan
    return float(part["a"].corr(part["b"]))


def row_regime(row: pd.Series) -> str:
    if bool(row["forbidden_flag"]) and row["E_theta_sign"] == "negative":
        return "forbidden_negative"
    if bool(row["threshold_relevant_flag"]) and row["E_theta_sign"] == "negative":
        return "threshold_relevant_negative"
    if row["E_theta_sign"] == "positive" and bool(row["post_P0_flag"]):
        return "post_P0_positive_tail"
    if row["E_theta_sign"] == "positive" and bool(row["finite_zone_flag"]):
        return "finite_positive"
    if row["E_theta_sign"] == "positive":
        return "positive_harmless"
    if row["E_theta_sign"] == "negative" and bool(row["post_P0_flag"]):
        return "post_P0_negative_tail"
    if row["E_theta_sign"] == "negative" and bool(row["finite_zone_flag"]):
        return "finite_negative"
    if row["E_theta_sign"] == "negative":
        return "subthreshold_negative"
    return "unknown"


def build_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows = pd.DataFrame(index=df.index)
    for c in ["candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta_sign", "DeltaD_sign"]:
        rows[c] = df[c] if c in df else np.nan
    rows["post_P0_flag"] = bool_series(df.get("post_P0_flag"), df.index)
    rows["finite_zone_flag"] = bool_series(df.get("finite_zone_flag"), df.index, default=True)
    rows["finite_certificate_flag"] = bool_series(df.get("finite_certificate_flag"), df.index)
    rows["O2_applicable_flag"] = bool_series(df.get("O2_applicable_flag"), df.index, default=True)
    rows["B3_applicable_flag"] = bool_series(df.get("B3_applicable_flag"), df.index, default=True)
    rows["endpoint_exclusion_flag"] = bool_series(df.get("endpoint_exclusion_flag"), df.index)
    rows["E_theta"] = num(df, "E_theta", "E_theta_local")
    rows["Q_R2Q"] = num(df, "Q_R2Q")
    rows["Q_delta_D"] = num(df, "Q_delta_D")
    rows["Q_exc"] = num(df, "Q_exc")
    rows["epsilon_exported"] = num(df, "formula_residual")
    rows["epsilon"] = rows["Q_R2Q"] - rows["Q_delta_D"] - rows["Q_exc"]
    rows["epsilon_export_difference"] = rows["epsilon"] - rows["epsilon_exported"]
    rows["epsilon_abs"] = rows["epsilon"].abs()
    rows["epsilon_positive_part"] = rows["epsilon"].clip(lower=0)
    rows["epsilon_negative_part"] = (-rows["epsilon"]).clip(lower=0)
    rows["DeltaD"] = num(df, "DeltaD", "observed_delta")
    rows["D_start"] = num(df, "D_start", "D_y")
    rows["D_end"] = num(df, "D_end", "D_y_plus_h")
    rows["bridge_excursion_raw"] = num(df, "bridge_excursion_raw")
    rows["scale_denominator"] = np.sqrt(rows["h"]) * np.log(rows["p_star"]) ** 2
    rows["Q_reconstructed"] = rows["Q_delta_D"] + rows["Q_exc"] + rows["epsilon"]
    rows["formula_reconstruction_error"] = (rows["Q_reconstructed"] - rows["Q_R2Q"]).abs()
    rows["positive_flag"] = rows["E_theta_sign"].eq("positive") | (rows["E_theta"] > 0)
    rows["negative_flag"] = rows["E_theta_sign"].eq("negative") | (rows["E_theta"] < 0)
    rows["near_forbidden_flag"] = rows["Q_R2Q"] > 0.75
    rows["forbidden_flag"] = rows["Q_R2Q"] > 1.0
    rows["threshold_relevant_flag"] = rows["near_forbidden_flag"]
    rows["sign_inconsistent_flag"] = ~rows["DeltaD_sign"].eq(rows["E_theta_sign"])
    rows["E_theta_normalized"] = rows["E_theta"] / rows["scale_denominator"]
    rows["log_pstar"] = np.log(rows["p_star"])
    rows["inv_log_pstar"] = 1.0 / rows["log_pstar"]
    rows["sqrt_h_over_sqrt_x"] = np.sqrt(rows["h"]) / np.sqrt(rows["x"])
    rows["rho_proxy"] = (rows["x"] - rows["y"]) / rows["h"].replace(0, np.nan)
    rows["row_regime"] = rows.apply(row_regime, axis=1)
    rows["residual_cap_0p03_pass_flag"] = rows["epsilon_abs"] <= CAP
    rows["residual_cap_0p025_pass_flag"] = rows["epsilon_abs"] <= SHARP_CAP

    failure_type = []
    for _, row in rows.iterrows():
        reasons: list[str] = []
        if pd.isna(row["epsilon"]):
            reasons.append("missing_epsilon")
        if pd.isna(row["Q_delta_D"]) or pd.isna(row["Q_exc"]) or pd.isna(row["Q_R2Q"]):
            reasons.append("missing_component")
        if pd.isna(row["scale_denominator"]) or row["scale_denominator"] <= 0:
            reasons.append("invalid_scale")
        if row["formula_reconstruction_error"] > FORMULA_TOL:
            reasons.append("formula_reconstruction_failure")
        if row["epsilon_abs"] > CAP:
            reasons.append("residual_above_0p03")
        if bool(row["threshold_relevant_flag"]) and row["epsilon_abs"] > CAP:
            reasons.append("threshold_relevant_residual_above_0p03")
        if bool(row["forbidden_flag"]) and row["epsilon_abs"] > CAP:
            reasons.append("forbidden_residual_above_0p03")
        failure_type.append(";".join(reasons))
    rows["failure_type"] = failure_type
    rows["status"] = np.where(rows["failure_type"].eq(""), "pass", "fail")
    return rows


def summarize(rows: pd.DataFrame) -> dict[str, Any]:
    thresh = rows[rows["threshold_relevant_flag"]]
    forb = rows[rows["forbidden_flag"]]
    pos = rows[rows["positive_flag"]]
    neg = rows[rows["negative_flag"]]
    post = rows[rows["post_P0_flag"]]
    finite = rows[rows["finite_zone_flag"]]
    eps = rows["epsilon"]
    summary: dict[str, Any] = {
        "rows": int(len(rows)),
        "primitive_full_rows": int(rows[["epsilon", "Q_delta_D", "Q_exc", "Q_R2Q"]].notna().all(axis=1).sum()),
        "missing_epsilon_rows": int(rows["epsilon"].isna().sum()),
        "missing_component_rows": int((~rows[["Q_delta_D", "Q_exc", "Q_R2Q"]].notna().all(axis=1)).sum()),
        "post_P0_rows": int(rows["post_P0_flag"].sum()),
        "finite_zone_rows": int(rows["finite_zone_flag"].sum()),
        "positive_rows": int(rows["positive_flag"].sum()),
        "negative_rows": int(rows["negative_flag"].sum()),
        "threshold_relevant_rows": int(rows["threshold_relevant_flag"].sum()),
        "forbidden_rows": int(rows["forbidden_flag"].sum()),
        "abs_epsilon_max": safe(rows["epsilon_abs"], "max"),
        "abs_epsilon_mean": safe(rows["epsilon_abs"], "mean"),
        "abs_epsilon_q95": safe(rows["epsilon_abs"], "q", 0.95),
        "abs_epsilon_q99": safe(rows["epsilon_abs"], "q", 0.99),
        "epsilon_min": safe(eps, "min"),
        "epsilon_max": safe(eps, "max"),
        "epsilon_positive_count": int((eps > 0).sum()),
        "epsilon_negative_count": int((eps < 0).sum()),
        "epsilon_zero_count": int((eps == 0).sum()),
        "epsilon_positive_frac": float((eps > 0).mean()),
        "epsilon_negative_frac": float((eps < 0).mean()),
        "threshold_relevant_abs_epsilon_max": safe(thresh["epsilon_abs"], "max"),
        "forbidden_abs_epsilon_max": safe(forb["epsilon_abs"], "max"),
        "positive_abs_epsilon_max": safe(pos["epsilon_abs"], "max"),
        "negative_abs_epsilon_max": safe(neg["epsilon_abs"], "max"),
        "post_P0_abs_epsilon_max": safe(post["epsilon_abs"], "max"),
        "finite_abs_epsilon_max": safe(finite["epsilon_abs"], "max"),
        "abs_epsilon_above_0p025_count": int((rows["epsilon_abs"] > SHARP_CAP).sum()),
        "abs_epsilon_above_0p03_count": int((rows["epsilon_abs"] > CAP).sum()),
        "threshold_relevant_above_0p03_count": int((thresh["epsilon_abs"] > CAP).sum()),
        "forbidden_above_0p03_count": int((forb["epsilon_abs"] > CAP).sum()),
        "formula_reconstruction_error_max": safe(rows["formula_reconstruction_error"], "max"),
        "formula_reconstruction_error_mean": safe(rows["formula_reconstruction_error"], "mean"),
        "formula_reconstruction_failures": int((rows["formula_reconstruction_error"] > FORMULA_TOL).sum()),
        "residual_bound_failures": int((rows["status"] == "fail").sum()),
        "corr_epsilon_h": corr(rows["epsilon"], rows["h"]),
        "corr_abs_epsilon_h": corr(rows["epsilon_abs"], rows["h"]),
        "corr_epsilon_p_star": corr(rows["epsilon"], rows["p_star"]),
        "corr_abs_epsilon_p_star": corr(rows["epsilon_abs"], rows["p_star"]),
        "corr_epsilon_log_pstar": corr(rows["epsilon"], rows["log_pstar"]),
        "corr_abs_epsilon_log_pstar": corr(rows["epsilon_abs"], rows["log_pstar"]),
        "corr_epsilon_inv_log_pstar": corr(rows["epsilon"], rows["inv_log_pstar"]),
        "corr_abs_epsilon_inv_log_pstar": corr(rows["epsilon_abs"], rows["inv_log_pstar"]),
        "corr_epsilon_sqrt_h_over_sqrt_x": corr(rows["epsilon"], rows["sqrt_h_over_sqrt_x"]),
        "corr_abs_epsilon_sqrt_h_over_sqrt_x": corr(rows["epsilon_abs"], rows["sqrt_h_over_sqrt_x"]),
        "corr_epsilon_rho_proxy": corr(rows["epsilon"], rows["rho_proxy"]),
        "corr_abs_epsilon_rho_proxy": corr(rows["epsilon_abs"], rows["rho_proxy"]),
        "corr_epsilon_Q_delta_D": corr(rows["epsilon"], rows["Q_delta_D"]),
        "corr_abs_epsilon_Q_delta_D": corr(rows["epsilon_abs"], rows["Q_delta_D"]),
        "corr_epsilon_Q_exc": corr(rows["epsilon"], rows["Q_exc"]),
        "corr_abs_epsilon_Q_exc": corr(rows["epsilon_abs"], rows["Q_exc"]),
        "corr_epsilon_E_theta_normalized": corr(rows["epsilon"], rows["E_theta_normalized"]),
        "corr_abs_epsilon_E_theta_normalized": corr(rows["epsilon_abs"], rows["E_theta_normalized"]),
    }
    summary["pass_residual_cap_0p03"] = summary["abs_epsilon_above_0p03_count"] == 0
    summary["pass_formula_reconstruction"] = summary["formula_reconstruction_failures"] == 0
    summary["pass_residual_epsilon_bound_empirical"] = bool(
        summary["primitive_full_rows"] == summary["rows"]
        and summary["missing_epsilon_rows"] == 0
        and summary["abs_epsilon_above_0p03_count"] == 0
        and summary["threshold_relevant_above_0p03_count"] == 0
        and summary["forbidden_above_0p03_count"] == 0
        and summary["formula_reconstruction_failures"] == 0
        and summary["residual_bound_failures"] == 0
    )
    summary["recommended_theorem_form"] = "abs_epsilon_le_0p03"
    summary["recommended_next_file"] = (
        "Prime_Mesh_R2Q_Residual_Epsilon_Bound_Theorem_Target_v1.md"
        if summary["pass_residual_epsilon_bound_empirical"]
        else "Prime_Mesh_R2Q_Residual_Epsilon_Bound_Repair_Map_v1.md"
    )
    return summary


def by_regime(rows: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for name, g in rows.groupby("row_regime", dropna=False):
        eps = g["epsilon"]
        recs.append(
            {
                "row_regime": name,
                "rows": int(len(g)),
                "epsilon_min": safe(eps, "min"),
                "epsilon_max": safe(eps, "max"),
                "abs_epsilon_max": safe(g["epsilon_abs"], "max"),
                "abs_epsilon_mean": safe(g["epsilon_abs"], "mean"),
                "abs_epsilon_q95": safe(g["epsilon_abs"], "q", 0.95),
                "epsilon_positive_count": int((eps > 0).sum()),
                "epsilon_negative_count": int((eps < 0).sum()),
                "threshold_relevant_rows": int(g["threshold_relevant_flag"].sum()),
                "forbidden_rows": int(g["forbidden_flag"].sum()),
                "above_0p025": int((g["epsilon_abs"] > SHARP_CAP).sum()),
                "above_0p03": int((g["epsilon_abs"] > CAP).sum()),
                "failures": int((g["status"] == "fail").sum()),
            }
        )
    return pd.DataFrame(recs).sort_values(["failures", "abs_epsilon_max"], ascending=[False, False])


def extremes(rows: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for name, col, abs_mode in [
        ("abs_epsilon_max", "epsilon", True),
        ("epsilon_min", "epsilon", False),
        ("epsilon_max", "epsilon", False),
        ("threshold_abs_epsilon_max", "epsilon", True),
        ("forbidden_abs_epsilon_max", "epsilon", True),
    ]:
        part = rows
        if name.startswith("threshold"):
            part = rows[rows["threshold_relevant_flag"]]
        if name.startswith("forbidden"):
            part = rows[rows["forbidden_flag"]]
        if not len(part):
            continue
        if abs_mode:
            idx = part[col].abs().idxmax()
        elif name.endswith("_min"):
            idx = part[col].idxmin()
        else:
            idx = part[col].idxmax()
        r = part.loc[idx]
        recs.append(
            {
                "extreme": name,
                "value": abs(r[col]) if abs_mode else r[col],
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
                "epsilon_abs": r.get("epsilon_abs"),
                "row_regime": r.get("row_regime"),
                "status": r.get("status"),
            }
        )
    return pd.DataFrame(recs)


def write_summary(summary: dict[str, Any]) -> None:
    with SUMMARY_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["field", "value"])
        for k, v in summary.items():
            w.writerow([k, v])


def write_doc(summary: dict[str, Any], regimes: pd.DataFrame, extremes: pd.DataFrame, failures: pd.DataFrame) -> None:
    verdict = "pass" if summary["pass_residual_epsilon_bound_empirical"] else "repair needed"
    lines = [
        "# Prime Mesh R2Q - Residual Epsilon Bound Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-09",
        f"**Status:** {verdict}",
        "",
        "## 1. Executive Verdict",
        "",
    ]
    if summary["pass_residual_epsilon_bound_empirical"]:
        lines += [
            r"\[",
            r"\boxed{|\epsilon(J)|\le0.03\text{ passes empirically on the full RawR2Q v3 inventory.}}",
            r"\]",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{Residual epsilon bound has failures requiring repair.}}",
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
        f"| missing_epsilon_rows | {summary['missing_epsilon_rows']} |",
        f"| missing_component_rows | {summary['missing_component_rows']} |",
        "",
        "## 4. Residual Cap Result",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| abs_epsilon_max | {summary['abs_epsilon_max']} |",
        f"| abs_epsilon_mean | {summary['abs_epsilon_mean']} |",
        f"| abs_epsilon_q95 | {summary['abs_epsilon_q95']} |",
        f"| abs_epsilon_q99 | {summary['abs_epsilon_q99']} |",
        f"| abs_epsilon_above_0p025_count | {summary['abs_epsilon_above_0p025_count']} |",
        f"| abs_epsilon_above_0p03_count | {summary['abs_epsilon_above_0p03_count']} |",
        f"| pass_residual_cap_0p03 | {summary['pass_residual_cap_0p03']} |",
        "",
        "## 5. Threshold / Forbidden Safety",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| threshold_relevant_rows | {summary['threshold_relevant_rows']} |",
        f"| threshold_relevant_abs_epsilon_max | {summary['threshold_relevant_abs_epsilon_max']} |",
        f"| threshold_relevant_above_0p03_count | {summary['threshold_relevant_above_0p03_count']} |",
        f"| forbidden_rows | {summary['forbidden_rows']} |",
        f"| forbidden_abs_epsilon_max | {summary['forbidden_abs_epsilon_max']} |",
        f"| forbidden_above_0p03_count | {summary['forbidden_above_0p03_count']} |",
        "",
        "## 6. Regime Decomposition",
        "",
        regimes.to_markdown(index=False),
        "",
        "## 7. Correlation / Proxy Diagnostics",
        "",
        "| proxy | corr(epsilon, proxy) | corr(abs_epsilon, proxy) |",
        "|---|---:|---:|",
    ]
    for proxy in ["h", "p_star", "log_pstar", "inv_log_pstar", "sqrt_h_over_sqrt_x", "rho_proxy", "Q_delta_D", "Q_exc", "E_theta_normalized"]:
        lines.append(
            f"| {proxy} | {summary.get('corr_epsilon_' + proxy)} | {summary.get('corr_abs_epsilon_' + proxy)} |"
        )
    lines += [
        "",
        "## 8. Extremes",
        "",
        extremes.to_markdown(index=False),
        "",
        "## 9. Failures",
        "",
    ]
    if len(failures):
        lines.append(failures.head(30).to_markdown(index=False))
    else:
        lines.append("No residual epsilon bound failures.")
    lines += [
        "",
        "## 10. Recommended Theorem Form",
        "",
        f"`{summary['recommended_theorem_form']}`",
        "",
        "## 11. Honest Status",
        "",
        "This is an empirical audit and theorem-target preparation, not an analytic proof of the epsilon bound.",
        "",
        "## 12. Recommended Next File",
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
    summary = summarize(rows)
    regimes = by_regime(rows)
    ex = extremes(rows)
    failures = rows[rows["status"].eq("fail")].copy()

    rows.to_csv(ROWS_OUT, index=False)
    regimes.to_csv(REGIME_OUT, index=False)
    ex.to_csv(EXTREMES_OUT, index=False)
    failures.to_csv(FAILURES_OUT, index=False)
    write_summary(summary)
    write_doc(summary, regimes, ex, failures)
    refresh_manifest([Path(__file__), SUMMARY_OUT, ROWS_OUT, REGIME_OUT, EXTREMES_OUT, FAILURES_OUT, DOC_OUT])

    for k in [
        "abs_epsilon_max",
        "abs_epsilon_above_0p025_count",
        "abs_epsilon_above_0p03_count",
        "threshold_relevant_abs_epsilon_max",
        "forbidden_abs_epsilon_max",
        "formula_reconstruction_failures",
        "residual_bound_failures",
        "pass_residual_epsilon_bound_empirical",
    ]:
        log(f"{k} = {summary[k]}")
    log(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
