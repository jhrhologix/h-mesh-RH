#!/usr/bin/env python3
"""EndpointMotion structure audit for RawR2Q v3."""

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
SUMMARY_OUT = OUT / "prime_mesh_r2q_endpoint_motion_structure_summary.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_endpoint_motion_structure_rows.csv"
REGIME_OUT = OUT / "prime_mesh_r2q_endpoint_motion_structure_by_regime.csv"
EXTREMES_OUT = OUT / "prime_mesh_r2q_endpoint_motion_structure_extremes.csv"
SEPARATORS_OUT = OUT / "prime_mesh_r2q_endpoint_motion_structure_separators.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_endpoint_motion_structure_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_EndpointMotion_Structure_Audit_v1.md"
MANIFEST = OUT / "deposit_manifest.csv"

Q_POS_CAP = 0.25
Q_NEAR = 0.75
Q_FORBIDDEN = 1.0
ENDPOINT_DOMINANCE = 0.90


def log(msg: str) -> None:
    print(f"[endpoint-motion {time.strftime('%H:%M:%S')}] {msg}", flush=True)


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
    if bool(row["sign_inconsistent_flag"]) and row["E_theta_sign"] == "positive":
        return "sign_inconsistent_positive_harmless"
    if bool(row["forbidden_flag"]) and row["E_theta_sign"] == "negative":
        return "forbidden_negative"
    if bool(row["threshold_relevant_flag"]) and row["E_theta_sign"] == "negative":
        return "threshold_relevant_negative"
    if row["E_theta_sign"] == "positive" and bool(row["finite_zone_flag"]) and bool(row["short_window_flag"]):
        return "finite_positive_short"
    if row["E_theta_sign"] == "positive" and bool(row["post_P0_flag"]):
        return "post_P0_positive_tail"
    if row["E_theta_sign"] == "positive":
        return "positive_harmless"
    if row["E_theta_sign"] == "negative" and bool(row["post_P0_flag"]):
        return "post_P0_negative_tail"
    if row["E_theta_sign"] == "negative" and bool(row["finite_zone_flag"]):
        return "finite_negative_repaid"
    if row["E_theta_sign"] == "negative":
        return "subthreshold_negative"
    return "unknown_or_boundary"


def safe_max(s: pd.Series) -> float:
    return float(s.max()) if len(s.dropna()) else math.nan


def safe_quantile(s: pd.Series, q: float) -> float:
    return float(s.quantile(q)) if len(s.dropna()) else math.nan


def build_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows = pd.DataFrame(index=df.index)
    for c in ["candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta_sign", "DeltaD_sign"]:
        rows[c] = df[c] if c in df else np.nan
    rows["post_P0_flag"] = bool_series(df.get("post_P0_flag"), df.index)
    rows["finite_zone_flag"] = bool_series(df.get("finite_zone_flag"), df.index, default=True)
    rows["finite_certified_flag"] = bool_series(df.get("finite_certificate_flag"), df.index)
    rows["E_theta"] = num(df, "E_theta", "E_theta_local")
    rows["DeltaD"] = num(df, "DeltaD", "observed_delta")
    rows["Q_delta_D"] = num(df, "Q_delta_D")
    rows["Q_R2Q"] = num(df, "Q_R2Q")
    rows["Q_exc"] = num(df, "Q_exc")
    rows["epsilon"] = num(df, "formula_residual")
    rows["near_forbidden_flag"] = rows["Q_R2Q"] > Q_NEAR
    rows["forbidden_flag"] = rows["Q_R2Q"] > Q_FORBIDDEN
    rows["threshold_relevant_flag"] = (rows["Q_R2Q"] > Q_NEAR) | (rows["Q_delta_D"] > Q_NEAR)
    rows["positive_harmless_flag"] = rows["E_theta_sign"].eq("positive") & (rows["Q_delta_D"] <= Q_POS_CAP)
    rows["negative_transfer_flag"] = rows["threshold_relevant_flag"] & rows["E_theta_sign"].eq("negative")
    rows["channel_compatible_flag"] = bool_series(df.get("covered_flag"), df.index, default=True)
    rows["O2_repaid_flag"] = bool_series(df.get("O2_B3_repaid_flag"), df.index, default=True)
    rows["B3_no_accumulation_flag"] = bool_series(df.get("B3_block_pass"), df.index, default=True)
    rows["endpoint_repaid_flag"] = rows["DeltaD"].lt(0)
    rows["E_theta_normalized"] = np.where(rows["p_star"] > 0, rows["E_theta"] / np.sqrt(rows["p_star"]), np.nan)
    rows["scale_ratio"] = np.where(rows["Q_R2Q"].abs() > 0, rows["Q_delta_D"] / rows["Q_R2Q"], np.nan)
    rows["h_over_x"] = rows["h"] / rows["x"]
    rows["pstar_over_x"] = rows["p_star"] / rows["x"]
    rows["log_pstar"] = np.log(rows["p_star"])
    rows["sqrt_h"] = np.sqrt(rows["h"])
    rows["normalizer"] = rows["sqrt_h"] * rows["log_pstar"] ** 2
    rows["Q_delta_D_share"] = rows["scale_ratio"]
    rows["Q_exc_share"] = np.where(rows["Q_R2Q"].abs() > 0, rows["Q_exc"] / rows["Q_R2Q"], np.nan)
    rows["epsilon_share"] = np.where(rows["Q_R2Q"].abs() > 0, rows["epsilon"] / rows["Q_R2Q"], np.nan)
    rows["h_bin"] = rows["h"].map(h_bin)
    rows["p_star_bin"] = rows["p_star"].map(p_bin)
    rows["window_class"] = rows["h_bin"]
    rows["short_window_flag"] = rows["h"] <= 4
    rows["single_step_flag"] = rows["h"] <= 1
    rows["finite_short_flag"] = rows["finite_zone_flag"] & rows["short_window_flag"]
    rows["post_P0_tail_flag"] = rows["post_P0_flag"]
    rows["sign_consistent"] = rows["DeltaD_sign"].eq(rows["E_theta_sign"])
    rows["sign_inconsistent_flag"] = ~rows["sign_consistent"]
    rows["sign_consistency_class"] = np.where(
        rows["sign_consistent"],
        "consistent",
        np.where(rows["E_theta_sign"].eq("positive"), "positive_harmless_inconsistent", "negative_inconsistent"),
    )
    rows["row_regime"] = rows.apply(row_regime, axis=1)

    positive_cap_fail = rows["E_theta_sign"].eq("positive") & (rows["Q_delta_D"] > Q_POS_CAP)
    threshold_transfer_fail = (rows["Q_delta_D"] > Q_NEAR) & ~rows["E_theta_sign"].eq("negative")
    sign_threshold_fail = rows["sign_inconsistent_flag"] & rows["threshold_relevant_flag"]
    sign_forbidden_fail = rows["sign_inconsistent_flag"] & rows["forbidden_flag"]
    missing_qd = rows["Q_delta_D"].isna()
    invalid_scale = rows["normalizer"].le(0) | rows["normalizer"].isna()

    failure_type = []
    for i in rows.index:
        reasons = []
        if missing_qd.loc[i]:
            reasons.append("missing_Q_delta_D")
        if positive_cap_fail.loc[i]:
            reasons.append("positive_endpoint_cap_violation")
        if threshold_transfer_fail.loc[i]:
            reasons.append("endpoint_threshold_transfer_violation")
        if sign_threshold_fail.loc[i]:
            reasons.append("sign_inconsistency_threshold_relevant")
        if sign_forbidden_fail.loc[i]:
            reasons.append("sign_inconsistency_forbidden")
        if invalid_scale.loc[i]:
            reasons.append("invalid_scale")
        failure_type.append(";".join(reasons))
    rows["failure_type"] = failure_type
    rows["endpoint_motion_pass_flag"] = rows["failure_type"].eq("")
    rows["status"] = np.where(rows["endpoint_motion_pass_flag"], "pass", "fail")
    return rows


def summarize(rows: pd.DataFrame) -> dict[str, Any]:
    pos = rows[rows["E_theta_sign"].eq("positive")]
    neg = rows[rows["E_theta_sign"].eq("negative")]
    thresh = rows[rows["threshold_relevant_flag"]]
    sign_inc = rows[rows["sign_inconsistent_flag"]]
    qd_gt = rows["Q_delta_D"] > Q_NEAR
    qd_gt_viol = qd_gt & ~rows["E_theta_sign"].eq("negative")
    endpoint_dom = thresh["Q_delta_D_share"] > ENDPOINT_DOMINANCE

    summary = {
        "rows": int(len(rows)),
        "primitive_full_rows": int(rows["Q_delta_D"].notna().sum()),
        "primitive_missing_rows": int(rows["Q_delta_D"].isna().sum()),
        "positive_rows": int(rows["E_theta_sign"].eq("positive").sum()),
        "negative_rows": int(rows["E_theta_sign"].eq("negative").sum()),
        "zero_rows": int(rows["E_theta_sign"].eq("zero").sum()),
        "unknown_rows": int((~rows["E_theta_sign"].isin(["positive", "negative", "zero"])).sum()),
        "post_P0_rows": int(rows["post_P0_flag"].sum()),
        "finite_zone_rows": int(rows["finite_zone_flag"].sum()),
        "threshold_relevant_rows": int(rows["threshold_relevant_flag"].sum()),
        "forbidden_rows": int(rows["forbidden_flag"].sum()),
        "Q_delta_D_max": safe_max(rows["Q_delta_D"]),
        "Q_delta_D_positive_max": safe_max(pos["Q_delta_D"]),
        "Q_delta_D_negative_max": safe_max(neg["Q_delta_D"]),
        "Q_delta_D_threshold_relevant_max": safe_max(thresh["Q_delta_D"]),
        "Q_delta_D_post_P0_max": safe_max(rows.loc[rows["post_P0_flag"], "Q_delta_D"]),
        "Q_delta_D_finite_max": safe_max(rows.loc[rows["finite_zone_flag"], "Q_delta_D"]),
        "positive_Q_delta_D_q95": safe_quantile(pos["Q_delta_D"], 0.95),
        "positive_Q_delta_D_q99": safe_quantile(pos["Q_delta_D"], 0.99),
        "positive_above_0p25_count": int((pos["Q_delta_D"] > Q_POS_CAP).sum()),
        "Q_delta_D_gt_0p75_rows": int(qd_gt.sum()),
        "Q_delta_D_gt_0p75_negative_rows": int((qd_gt & rows["E_theta_sign"].eq("negative")).sum()),
        "Q_delta_D_gt_0p75_positive_rows": int((qd_gt & rows["E_theta_sign"].eq("positive")).sum()),
        "Q_delta_D_gt_0p75_violations": int(qd_gt_viol.sum()),
        "threshold_relevant_endpoint_dominant_count": int(endpoint_dom.sum()),
        "threshold_relevant_endpoint_dominant_frac": float(endpoint_dom.mean()) if len(endpoint_dom) else 1.0,
        "min_Q_delta_D_share_threshold_relevant": float(thresh["Q_delta_D_share"].min()) if len(thresh) else math.nan,
        "sign_inconsistent_rows": int(len(sign_inc)),
        "sign_inconsistent_positive_rows": int(sign_inc["E_theta_sign"].eq("positive").sum()),
        "sign_inconsistent_Q_delta_D_max": safe_max(sign_inc["Q_delta_D"]),
        "sign_inconsistent_Q_R2Q_max": safe_max(sign_inc["Q_R2Q"]),
        "sign_inconsistent_threshold_relevant_rows": int((sign_inc["threshold_relevant_flag"]).sum()),
        "sign_inconsistent_forbidden_rows": int((sign_inc["forbidden_flag"]).sum()),
        "positive_short_window_max": safe_max(pos.loc[pos["short_window_flag"], "Q_delta_D"]),
        "positive_tail_max": safe_max(pos.loc[pos["post_P0_flag"], "Q_delta_D"]),
    }
    summary["pass_positive_endpoint_cap"] = summary["positive_above_0p25_count"] == 0
    summary["pass_endpoint_threshold_transfer"] = summary["Q_delta_D_gt_0p75_violations"] == 0
    summary["pass_threshold_endpoint_dominance"] = summary["threshold_relevant_endpoint_dominant_frac"] == 1.0
    summary["pass_sign_inconsistency_harmless"] = (
        summary["sign_inconsistent_threshold_relevant_rows"] == 0
        and summary["sign_inconsistent_forbidden_rows"] == 0
        and summary["sign_inconsistent_Q_delta_D_max"] <= Q_POS_CAP
        and summary["sign_inconsistent_Q_R2Q_max"] <= Q_POS_CAP
    )
    summary["endpoint_motion_structure_failures"] = int((~rows["endpoint_motion_pass_flag"]).sum())
    summary["pass_endpoint_motion_structure_empirical"] = bool(
        summary["primitive_missing_rows"] == 0
        and summary["positive_above_0p25_count"] == 0
        and summary["Q_delta_D_gt_0p75_violations"] == 0
        and summary["sign_inconsistent_threshold_relevant_rows"] == 0
        and summary["sign_inconsistent_forbidden_rows"] == 0
        and summary["endpoint_motion_structure_failures"] == 0
    )
    summary["recommended_theorem_form"] = "positive_endpoint_cap_plus_threshold_endpoint_transfer_with_harmless_sign_inconsistency"
    summary["recommended_next_file"] = (
        "Prime_Mesh_R2Q_EndpointMotion_Structure_Theorem_Target_v1.md"
        if summary["pass_endpoint_motion_structure_empirical"]
        else "Prime_Mesh_R2Q_EndpointMotion_Structure_Repair_Map_v1.md"
    )
    return summary


def by_regime(rows: pd.DataFrame) -> pd.DataFrame:
    records = []
    for name, g in rows.groupby("row_regime", dropna=False):
        records.append(
            {
                "row_regime": name,
                "rows": len(g),
                "Q_R2Q_max": safe_max(g["Q_R2Q"]),
                "Q_delta_D_max": safe_max(g["Q_delta_D"]),
                "Q_exc_max": safe_max(g["Q_exc"]),
                "epsilon_abs_max": safe_max(g["epsilon"].abs()),
                "threshold_relevant_rows": int(g["threshold_relevant_flag"].sum()),
                "sign_inconsistent_rows": int(g["sign_inconsistent_flag"].sum()),
                "failures": int((~g["endpoint_motion_pass_flag"]).sum()),
            }
        )
    return pd.DataFrame(records).sort_values(["failures", "Q_R2Q_max"], ascending=[False, False])


def separators(rows: pd.DataFrame) -> pd.DataFrame:
    records = []
    pos = rows[rows["E_theta_sign"].eq("positive")]
    for name, g in [
        ("all_positive", pos),
        ("positive_finite", pos[pos["finite_zone_flag"]]),
        ("positive_tail", pos[pos["post_P0_flag"]]),
    ]:
        records.append(
            {
                "separator": name,
                "rows": len(g),
                "Q_delta_D_max": safe_max(g["Q_delta_D"]),
                "Q_delta_D_q95": safe_quantile(g["Q_delta_D"], 0.95),
                "Q_delta_D_q99": safe_quantile(g["Q_delta_D"], 0.99),
                "above_0p25": int((g["Q_delta_D"] > Q_POS_CAP).sum()),
            }
        )
    for name, g in pos.groupby("h_bin"):
        records.append(
            {
                "separator": f"positive_h_bin:{name}",
                "rows": len(g),
                "Q_delta_D_max": safe_max(g["Q_delta_D"]),
                "Q_delta_D_q95": safe_quantile(g["Q_delta_D"], 0.95),
                "Q_delta_D_q99": safe_quantile(g["Q_delta_D"], 0.99),
                "above_0p25": int((g["Q_delta_D"] > Q_POS_CAP).sum()),
            }
        )
    for name, g in pos.groupby("p_star_bin"):
        records.append(
            {
                "separator": f"positive_p_bin:{name}",
                "rows": len(g),
                "Q_delta_D_max": safe_max(g["Q_delta_D"]),
                "Q_delta_D_q95": safe_quantile(g["Q_delta_D"], 0.95),
                "Q_delta_D_q99": safe_quantile(g["Q_delta_D"], 0.99),
                "above_0p25": int((g["Q_delta_D"] > Q_POS_CAP).sum()),
            }
        )
    return pd.DataFrame(records)


def extremes(rows: pd.DataFrame) -> pd.DataFrame:
    specs = [
        ("Q_delta_D_max", rows, "Q_delta_D"),
        ("positive_Q_delta_D_max", rows[rows["E_theta_sign"].eq("positive")], "Q_delta_D"),
        ("negative_Q_delta_D_max", rows[rows["E_theta_sign"].eq("negative")], "Q_delta_D"),
        ("threshold_Q_delta_D_share_min", rows[rows["threshold_relevant_flag"]], "Q_delta_D_share"),
        ("sign_inconsistent_Q_R2Q_max", rows[rows["sign_inconsistent_flag"]], "Q_R2Q"),
    ]
    records = []
    for name, g, col in specs:
        if not len(g) or g[col].dropna().empty:
            continue
        asc = name.endswith("_min")
        r = g.sort_values(col, ascending=asc).iloc[0]
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
                "DeltaD_sign": r.get("DeltaD_sign"),
                "Q_R2Q": r.get("Q_R2Q"),
                "Q_delta_D": r.get("Q_delta_D"),
                "Q_delta_D_share": r.get("Q_delta_D_share"),
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


def write_doc(summary: dict[str, Any], regimes: pd.DataFrame, ex: pd.DataFrame, sep: pd.DataFrame, fail: pd.DataFrame) -> None:
    verdict = "pass" if summary["pass_endpoint_motion_structure_empirical"] else "repair needed"
    lines = [
        "# Prime Mesh R2Q - EndpointMotion Structure Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-08",
        f"**Status:** {verdict}",
        "",
        "## 1. Executive Verdict",
        "",
    ]
    if summary["pass_endpoint_motion_structure_empirical"]:
        lines += [
            r"\[",
            r"\boxed{\text{EndpointMotion structure passes empirically: positive cap, threshold transfer, and harmless sign inconsistency all hold.}}",
            r"\]",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{EndpointMotion structure has failures requiring repair.}}",
            r"\]",
        ]
    lines += [
        "",
        "## 2. Inputs Used",
        "",
        f"- Primary inventory: `{INPUT}`.",
        "",
        "## 3. Primitive Coverage",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| rows | {summary['rows']} |",
        f"| primitive_full_rows | {summary['primitive_full_rows']} |",
        f"| primitive_missing_rows | {summary['primitive_missing_rows']} |",
        "",
        "## 4. Endpoint-Motion Cap Results",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| positive_rows | {summary['positive_rows']} |",
        f"| Q_delta_D_positive_max | {summary['Q_delta_D_positive_max']} |",
        f"| positive_Q_delta_D_q95 | {summary['positive_Q_delta_D_q95']} |",
        f"| positive_Q_delta_D_q99 | {summary['positive_Q_delta_D_q99']} |",
        f"| positive_above_0p25_count | {summary['positive_above_0p25_count']} |",
        f"| pass_positive_endpoint_cap | {summary['pass_positive_endpoint_cap']} |",
        "",
        "## 5. Threshold-Transfer Results",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| Q_delta_D_gt_0p75_rows | {summary['Q_delta_D_gt_0p75_rows']} |",
        f"| Q_delta_D_gt_0p75_negative_rows | {summary['Q_delta_D_gt_0p75_negative_rows']} |",
        f"| Q_delta_D_gt_0p75_positive_rows | {summary['Q_delta_D_gt_0p75_positive_rows']} |",
        f"| Q_delta_D_gt_0p75_violations | {summary['Q_delta_D_gt_0p75_violations']} |",
        f"| pass_endpoint_threshold_transfer | {summary['pass_endpoint_threshold_transfer']} |",
        "",
        "## 6. Threshold-Relevant Component Shares",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| threshold_relevant_rows | {summary['threshold_relevant_rows']} |",
        f"| threshold_relevant_endpoint_dominant_frac | {summary['threshold_relevant_endpoint_dominant_frac']} |",
        f"| min_Q_delta_D_share_threshold_relevant | {summary['min_Q_delta_D_share_threshold_relevant']} |",
        f"| pass_threshold_endpoint_dominance | {summary['pass_threshold_endpoint_dominance']} |",
        "",
        "## 7. Positive Short-Window / Tail Decomposition",
        "",
        sep.to_markdown(index=False),
        "",
        "## 8. Sign Inconsistency Harmlessness",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| sign_inconsistent_rows | {summary['sign_inconsistent_rows']} |",
        f"| sign_inconsistent_positive_rows | {summary['sign_inconsistent_positive_rows']} |",
        f"| sign_inconsistent_Q_delta_D_max | {summary['sign_inconsistent_Q_delta_D_max']} |",
        f"| sign_inconsistent_Q_R2Q_max | {summary['sign_inconsistent_Q_R2Q_max']} |",
        f"| sign_inconsistent_threshold_relevant_rows | {summary['sign_inconsistent_threshold_relevant_rows']} |",
        f"| sign_inconsistent_forbidden_rows | {summary['sign_inconsistent_forbidden_rows']} |",
        f"| pass_sign_inconsistency_harmless | {summary['pass_sign_inconsistency_harmless']} |",
        "",
        "## 9. Regime Decomposition",
        "",
        regimes.to_markdown(index=False),
        "",
        "## 10. Extremes",
        "",
        ex.to_markdown(index=False),
        "",
        "## 11. Failures",
        "",
    ]
    if len(fail):
        lines.append(fail.head(30).to_markdown(index=False))
    else:
        lines.append("No EndpointMotion structure failures.")
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
    log(f"Reading {INPUT.name}")
    df = pd.read_csv(INPUT)
    rows = build_rows(df)
    summary = summarize(rows)
    regimes = by_regime(rows)
    sep = separators(rows)
    ex = extremes(rows)
    fail = rows[~rows["endpoint_motion_pass_flag"]].copy()

    rows.to_csv(ROWS_OUT, index=False)
    regimes.to_csv(REGIME_OUT, index=False)
    ex.to_csv(EXTREMES_OUT, index=False)
    sep.to_csv(SEPARATORS_OUT, index=False)
    fail.to_csv(FAILURES_OUT, index=False)
    write_summary(summary)
    write_doc(summary, regimes, ex, sep, fail)
    refresh_manifest([Path(__file__), SUMMARY_OUT, ROWS_OUT, REGIME_OUT, EXTREMES_OUT, SEPARATORS_OUT, FAILURES_OUT, DOC_OUT])

    for k in [
        "rows",
        "positive_rows",
        "Q_delta_D_positive_max",
        "positive_above_0p25_count",
        "Q_delta_D_gt_0p75_rows",
        "Q_delta_D_gt_0p75_violations",
        "threshold_relevant_endpoint_dominant_frac",
        "sign_inconsistent_rows",
        "sign_inconsistent_threshold_relevant_rows",
        "sign_inconsistent_forbidden_rows",
        "endpoint_motion_structure_failures",
        "pass_endpoint_motion_structure_empirical",
    ]:
        log(f"{k} = {summary[k]}")
    log(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
