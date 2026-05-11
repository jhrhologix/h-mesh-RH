#!/usr/bin/env python3
"""Endpoint path D_N construction consistency audit."""

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
SUMMARY_OUT = OUT / "prime_mesh_r2q_endpoint_path_DN_construction_summary.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_endpoint_path_DN_construction_rows.csv"
REGIME_OUT = OUT / "prime_mesh_r2q_endpoint_path_DN_construction_by_regime.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_endpoint_path_DN_construction_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_EndpointPath_DN_Construction_Audit_v1.md"
MANIFEST = OUT / "deposit_manifest.csv"

TOL_DELTA = 1e-8
TOL_Q = 1e-10
TOL_FORMULA = 1e-10
Q_NEAR = 0.75
Q_FORBIDDEN = 1.0


def log(msg: str) -> None:
    print(f"[dn-construction {time.strftime('%H:%M:%S')}] {msg}", flush=True)


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
    if bool(row["forbidden_flag"]) and row["E_theta_sign"] == "negative":
        return "forbidden_negative"
    if bool(row["threshold_relevant_flag"]) and row["E_theta_sign"] == "negative":
        return "threshold_relevant_negative"
    if row["E_theta_sign"] == "negative":
        return "subthreshold_negative"
    if row["E_theta_sign"] == "positive":
        return "positive_harmless"
    if bool(row["finite_zone_flag"]):
        return "finite_certificate"
    return "unknown"


def safe_max(s: pd.Series) -> float:
    return float(s.max()) if len(s.dropna()) else math.nan


def build_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows = pd.DataFrame(index=df.index)
    for c in ["candidate_id", "block_id", "x", "y", "h", "right_endpoint", "p_star", "E_theta_sign", "DeltaD_sign"]:
        rows[c] = df[c] if c in df else np.nan
    rows["post_P0_flag"] = bool_series(df.get("post_P0_flag"), df.index)
    rows["finite_zone_flag"] = bool_series(df.get("finite_zone_flag"), df.index, default=True)
    rows["E_theta"] = num(df, "E_theta", "E_theta_local")
    rows["Q_R2Q"] = num(df, "Q_R2Q")
    rows["Q_delta_D"] = num(df, "Q_delta_D")
    rows["Q_exc"] = num(df, "Q_exc")
    rows["epsilon"] = num(df, "formula_residual")
    rows["D_start"] = num(df, "D_start", "D_y")
    rows["D_end"] = num(df, "D_end", "D_y_plus_h")
    rows["DeltaD"] = num(df, "DeltaD", "observed_delta")
    rows["bridge_excursion_raw"] = num(df, "bridge_excursion_raw")
    rows["bridge_excursion_argmax"] = num(df, "bridge_excursion_argmax")
    rows["threshold_relevant_flag"] = rows["Q_R2Q"] > Q_NEAR
    rows["forbidden_flag"] = rows["Q_R2Q"] > Q_FORBIDDEN
    rows["row_regime"] = rows.apply(regime, axis=1)

    rows["scale_denominator"] = np.sqrt(rows["h"]) * np.log(rows["p_star"]) ** 2
    rows["DeltaD_recomputed"] = rows["D_end"] - rows["D_start"]
    rows["DeltaD_recompute_error"] = rows["DeltaD"] - rows["DeltaD_recomputed"]
    rows["Q_delta_D_recomputed"] = rows["DeltaD"].abs() / rows["scale_denominator"]
    rows["Q_delta_D_recompute_error"] = rows["Q_delta_D"] - rows["Q_delta_D_recomputed"]
    rows["Q_exc_recomputed"] = rows["bridge_excursion_raw"] / rows["scale_denominator"]
    rows["Q_exc_recompute_error"] = rows["Q_exc"] - rows["Q_exc_recomputed"]
    rows["line_slope_D"] = rows["DeltaD"] / rows["h"]
    rows["Q_R2Q_recomputed"] = rows["Q_delta_D"] + rows["Q_exc"] + rows["epsilon"]
    rows["formula_reconstruction_error"] = rows["Q_R2Q"] - rows["Q_R2Q_recomputed"]

    rows["endpoint_path_valid_flag"] = rows["D_start"].notna() & rows["D_end"].notna()
    rows["endpoint_delta_valid_flag"] = rows["DeltaD"].notna() & (rows["DeltaD_recompute_error"].abs() <= TOL_DELTA)
    rows["normalization_valid_flag"] = (
        rows["Q_delta_D"].notna()
        & rows["scale_denominator"].gt(0)
        & (rows["Q_delta_D_recompute_error"].abs() <= TOL_Q)
    )
    rows["bridge_excursion_valid_flag"] = (
        rows["bridge_excursion_raw"].notna()
        & rows["Q_exc"].notna()
        & rows["scale_denominator"].gt(0)
        & (rows["Q_exc_recompute_error"].abs() <= TOL_Q)
    )
    rows["formula_reconstruction_valid_flag"] = rows["formula_reconstruction_error"].abs() <= TOL_FORMULA

    failure_type = []
    for i, row in rows.iterrows():
        reasons = []
        if pd.isna(row["D_start"]):
            reasons.append("missing_D_start")
        if pd.isna(row["D_end"]):
            reasons.append("missing_D_end")
        if pd.isna(row["DeltaD"]):
            reasons.append("missing_DeltaD")
        if not pd.isna(row["DeltaD_recompute_error"]) and abs(row["DeltaD_recompute_error"]) > TOL_DELTA:
            reasons.append("DeltaD_recompute_mismatch")
        if pd.isna(row["Q_delta_D"]):
            reasons.append("missing_Q_delta_D")
        if not pd.isna(row["Q_delta_D_recompute_error"]) and abs(row["Q_delta_D_recompute_error"]) > TOL_Q:
            reasons.append("Q_delta_D_recompute_mismatch")
        if pd.isna(row["bridge_excursion_raw"]):
            reasons.append("missing_bridge_excursion_raw")
        if pd.isna(row["Q_exc"]):
            reasons.append("missing_Q_exc")
        if not pd.isna(row["Q_exc_recompute_error"]) and abs(row["Q_exc_recompute_error"]) > TOL_Q:
            reasons.append("Q_exc_recompute_mismatch")
        if pd.isna(row["scale_denominator"]) or row["scale_denominator"] <= 0:
            reasons.append("invalid_scale")
        if not pd.isna(row["formula_reconstruction_error"]) and abs(row["formula_reconstruction_error"]) > TOL_FORMULA:
            reasons.append("formula_reconstruction_mismatch")
        if bool(row["threshold_relevant_flag"]) and (
            not bool(row["endpoint_path_valid_flag"])
            or not bool(row["endpoint_delta_valid_flag"])
            or not bool(row["normalization_valid_flag"])
            or not bool(row["bridge_excursion_valid_flag"])
            or not bool(row["formula_reconstruction_valid_flag"])
        ):
            reasons.append("threshold_relevant_DN_failure")
        if bool(row["forbidden_flag"]) and (
            not bool(row["endpoint_path_valid_flag"])
            or not bool(row["endpoint_delta_valid_flag"])
            or not bool(row["normalization_valid_flag"])
            or not bool(row["bridge_excursion_valid_flag"])
            or not bool(row["formula_reconstruction_valid_flag"])
        ):
            reasons.append("forbidden_DN_failure")
        failure_type.append(";".join(reasons))
    rows["failure_type"] = failure_type
    rows["status"] = np.where(rows["failure_type"].eq(""), "pass", "fail")
    return rows


def summarize(rows: pd.DataFrame) -> dict[str, Any]:
    fail = rows[rows["status"].eq("fail")]
    threshold = rows[rows["threshold_relevant_flag"]]
    forbidden = rows[rows["forbidden_flag"]]
    pos = rows[rows["E_theta_sign"].eq("positive")]
    summary: dict[str, Any] = {
        "rows": int(len(rows)),
        "primitive_full_rows": int(rows["endpoint_path_valid_flag"].sum()),
        "missing_D_endpoint_rows": int((~rows["endpoint_path_valid_flag"]).sum()),
        "missing_DeltaD_rows": int(rows["DeltaD"].isna().sum()),
        "missing_Q_delta_D_rows": int(rows["Q_delta_D"].isna().sum()),
        "missing_bridge_excursion_rows": int(rows["bridge_excursion_raw"].isna().sum()),
        "missing_Q_exc_rows": int(rows["Q_exc"].isna().sum()),
        "invalid_scale_rows": int((rows["scale_denominator"].isna() | rows["scale_denominator"].le(0)).sum()),
        "max_abs_DeltaD_recompute_error": safe_max(rows["DeltaD_recompute_error"].abs()),
        "max_abs_Q_delta_D_recompute_error": safe_max(rows["Q_delta_D_recompute_error"].abs()),
        "max_abs_Q_exc_recompute_error": safe_max(rows["Q_exc_recompute_error"].abs()),
        "max_formula_reconstruction_error": safe_max(rows["formula_reconstruction_error"].abs()),
        "formula_reconstruction_failures": int((~rows["formula_reconstruction_valid_flag"]).sum()),
        "threshold_relevant_rows": int(len(threshold)),
        "threshold_relevant_DN_failures": int((threshold["status"] == "fail").sum()),
        "forbidden_rows": int(len(forbidden)),
        "forbidden_DN_failures": int((forbidden["status"] == "fail").sum()),
        "positive_rows": int(len(pos)),
        "positive_DN_failures": int((pos["status"] == "fail").sum()),
        "endpoint_path_construction_failures": int(len(fail)),
    }
    summary["pass_endpoint_path_DN_construction_empirical"] = bool(
        summary["endpoint_path_construction_failures"] == 0
        and summary["threshold_relevant_DN_failures"] == 0
        and summary["forbidden_DN_failures"] == 0
    )
    summary["recommended_theorem_form"] = "DN_endpoint_path_construction_verified_for_full_primitive_inventory"
    summary["recommended_next_file"] = (
        "Prime_Mesh_R2Q_EndpointPath_DN_Construction_Closure_Update_v1.md"
        if summary["pass_endpoint_path_DN_construction_empirical"]
        else "Prime_Mesh_R2Q_EndpointPath_DN_Construction_Repair_Map_v1.md"
    )
    return summary


def by_regime(rows: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for name, g in rows.groupby("row_regime", dropna=False):
        recs.append(
            {
                "row_regime": name,
                "rows": len(g),
                "threshold_relevant_rows": int(g["threshold_relevant_flag"].sum()),
                "forbidden_rows": int(g["forbidden_flag"].sum()),
                "max_abs_DeltaD_error": safe_max(g["DeltaD_recompute_error"].abs()),
                "max_abs_Q_delta_D_error": safe_max(g["Q_delta_D_recompute_error"].abs()),
                "max_abs_Q_exc_error": safe_max(g["Q_exc_recompute_error"].abs()),
                "max_formula_error": safe_max(g["formula_reconstruction_error"].abs()),
                "failures": int((g["status"] == "fail").sum()),
            }
        )
    return pd.DataFrame(recs).sort_values(["failures", "threshold_relevant_rows"], ascending=[False, False])


def write_summary(summary: dict[str, Any]) -> None:
    with SUMMARY_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["field", "value"])
        for k, v in summary.items():
            w.writerow([k, v])


def write_doc(summary: dict[str, Any], regimes: pd.DataFrame, failures: pd.DataFrame) -> None:
    verdict = "pass" if summary["pass_endpoint_path_DN_construction_empirical"] else "repair needed"
    lines = [
        "# Prime Mesh R2Q - EndpointPath D_N Construction Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-08",
        f"**Status:** {verdict}",
        "",
        "## 1. Executive Verdict",
        "",
    ]
    if summary["pass_endpoint_path_DN_construction_empirical"]:
        lines += [
            r"\[",
            r"\boxed{\text{EndpointPath }D_N\text{ construction is internally consistent on the full primitive inventory.}}",
            r"\]",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{EndpointPath }D_N\text{ construction has consistency failures requiring repair.}}",
            r"\]",
        ]
    lines += [
        "",
        "## 2. Inputs Used",
        "",
        f"- Primary inventory: `{INPUT}`.",
        "",
        "## 3. Construction Checks",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    for k in [
        "rows",
        "primitive_full_rows",
        "missing_D_endpoint_rows",
        "missing_DeltaD_rows",
        "missing_Q_delta_D_rows",
        "missing_bridge_excursion_rows",
        "missing_Q_exc_rows",
        "invalid_scale_rows",
        "max_abs_DeltaD_recompute_error",
        "max_abs_Q_delta_D_recompute_error",
        "max_abs_Q_exc_recompute_error",
        "max_formula_reconstruction_error",
        "formula_reconstruction_failures",
        "threshold_relevant_rows",
        "threshold_relevant_DN_failures",
        "forbidden_rows",
        "forbidden_DN_failures",
        "positive_rows",
        "positive_DN_failures",
        "endpoint_path_construction_failures",
        "pass_endpoint_path_DN_construction_empirical",
    ]:
        lines.append(f"| `{k}` | {summary[k]} |")
    lines += [
        "",
        "## 4. Regime Table",
        "",
        regimes.to_markdown(index=False),
        "",
        "## 5. Failures",
        "",
    ]
    if len(failures):
        lines.append(failures.head(30).to_markdown(index=False))
    else:
        lines.append("No EndpointPath construction failures.")
    lines += [
        "",
        "## 6. Recommended Theorem Form",
        "",
        f"`{summary['recommended_theorem_form']}`",
        "",
        "## 7. Recommended Next File",
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
    failures = rows[rows["status"].eq("fail")].copy()

    rows.to_csv(ROWS_OUT, index=False)
    regimes.to_csv(REGIME_OUT, index=False)
    failures.to_csv(FAILURES_OUT, index=False)
    write_summary(summary)
    write_doc(summary, regimes, failures)
    refresh_manifest([Path(__file__), SUMMARY_OUT, ROWS_OUT, REGIME_OUT, FAILURES_OUT, DOC_OUT])

    for k in [
        "rows",
        "missing_D_endpoint_rows",
        "max_abs_DeltaD_recompute_error",
        "max_abs_Q_delta_D_recompute_error",
        "max_abs_Q_exc_recompute_error",
        "max_formula_reconstruction_error",
        "threshold_relevant_DN_failures",
        "endpoint_path_construction_failures",
        "pass_endpoint_path_DN_construction_empirical",
    ]:
        log(f"{k} = {summary[k]}")
    log(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
