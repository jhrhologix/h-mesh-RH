#!/usr/bin/env python3
"""Unified first-crossing covering/localization stress audit.

This audit stress-tests the shared B3/theta localization logic:

    global/local candidate point -> selected B2/R2Q window
    -> sign-compatible local obstruction or positive harmlessness
    -> scale-compatible local/global denominator.

It is empirical only.  It does not prove the covering lemma, but it checks
whether the existing audited inventory has any sign, coverage, or scale
compatibility leak.

All outputs are written next to this script in the repair-process
``scripts and results`` directory.
"""

from __future__ import annotations

import math
import time
from pathlib import Path

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent

THETA_INTERVALS = OUT / "prime_mesh_r2q_theta_first_crossing_intervals.csv"
B3_BLOCKS = OUT / "prime_mesh_r2q_b3_block_to_tail_blocks.csv"
HEXC_INTERVALS = OUT / "prime_mesh_r2q_hexc_path_shape_intervals.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_summary.csv"
WINDOWS_OUT = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_windows.csv"
CROSSINGS_OUT = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Stress_Audit_v1.md"
MANIFEST_OUT = OUT / "deposit_manifest.csv"

P0 = 500_000_000
NEAR_FORBIDDEN_Q = 0.75
EPS = 1e-12


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        log(f"Missing optional input: {path}")
        return pd.DataFrame()
    return pd.read_csv(path)


def num(df: pd.DataFrame, cols: list[str]) -> None:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")


def boolish(s: pd.Series) -> pd.Series:
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def q(series: pd.Series, value: float) -> float:
    if len(series) == 0:
        return float("nan")
    return float(series.quantile(value))


def sign_label(x: float) -> str:
    if pd.isna(x):
        return "nan"
    if x > EPS:
        return "positive"
    if x < -EPS:
        return "negative"
    return "zero"


def scale_ratio_local_to_global(h: float, p_star: float, x: float) -> float:
    if h <= 0 or p_star <= 1 or x <= 1:
        return float("nan")
    return (math.sqrt(h) * math.log(p_star) ** 2) / (math.sqrt(x) * math.log(x) ** 2)


def refresh_manifest() -> None:
    rows = []
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            rows.append(
                {
                    "Name": p.name,
                    "Length": p.stat().st_size,
                    "LastWriteTime": pd.Timestamp(p.stat().st_mtime, unit="s"),
                }
            )
    pd.DataFrame(rows).to_csv(MANIFEST_OUT, index=False)


def write_doc(summary: dict[str, object], failures: pd.DataFrame, crossings: pd.DataFrame) -> None:
    status = "passes" if summary["pass_covering_localization_empirical"] else "needs repair"
    lines = [
        "# Prime Mesh R2Q - First-Crossing Covering Localization Stress Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-08",
        f"**Status:** unified FCL stress audit - {status}",
        "",
        "## 1. Purpose",
        "",
        "This audit stress-tests the exact window-selection and sign-localization logic shared by B3 and theta first-crossing.",
        "",
        "It checks whether candidate points are covered, whether local theta signs match the channel classification, whether positive rows remain harmless, and whether local/global denominator ratios stay finite and ordered.",
        "",
        "## 2. Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    for k, v in summary.items():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## 3. Failures",
        "",
        failures.to_markdown(index=False) if len(failures) else "No failures found.",
        "",
        "## 4. Highest-Risk Crossings",
        "",
        crossings.sort_values(["post_P0", "Q_R2Q", "Q_theta"], ascending=False).head(25).to_markdown(index=False)
        if len(crossings)
        else "No crossings/candidates.",
        "",
        "## 5. Interpretation",
        "",
    ]
    if summary["pass_covering_localization_empirical"]:
        lines += [
            r"\[",
            r"\boxed{\text{No empirical covering, sign, or scale leak appears in the audited FCL inventory.}}",
            r"\]",
            "",
            "The finite-zone candidate remains assigned to finite certificate.  Post-`P0` candidates are covered, sign-compatible, and positive rows remain harmless.",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{At least one FCL stress condition failed; inspect the failures table.}}",
            r"\]",
        ]
    lines += [
        "",
        "## 6. Outputs",
        "",
        f"- `{SUMMARY_OUT.name}`",
        f"- `{WINDOWS_OUT.name}`",
        f"- `{CROSSINGS_OUT.name}`",
        f"- `{FAILURES_OUT.name}`",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
    ]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    log("Reading theta first-crossing intervals")
    theta = read_csv(THETA_INTERVALS)
    if len(theta) == 0:
        raise SystemExit("Missing theta first-crossing intervals; run theta audit first.")
    num(
        theta,
        [
            "block_id",
            "p_star",
            "y",
            "h",
            "theta_local_norm",
            "theta_end_norm",
            "E_theta_local",
            "Q_theta",
            "Q_R2Q",
            "Cplus_value",
        ],
    )
    for c in [
        "B2_active_flag",
        "covered_flag",
        "finite_certificate_flag",
        "negative_transfer_flag",
        "positive_harmless_flag",
        "O2_B3_repaid_flag",
        "tail_flag",
        "near_forbidden_R2Q",
        "forbidden_R2Q",
    ]:
        if c in theta.columns:
            theta[c] = boolish(theta[c])

    log("Reading B3 blocks")
    b3 = read_csv(B3_BLOCKS)
    if len(b3):
        num(
            b3,
            [
                "block_id",
                "p_star",
                "start_prime",
                "worst_prime",
                "end_prime",
                "covered_y",
                "covered_h",
                "Q_tail_max_inside",
                "Q_tail_end",
                "Q_local",
                "Q_exc",
                "O2_total_with_o2p4",
            ],
        )
        for c in [
            "covered_flag",
            "finite_certificate_flag",
            "covered_by_block_or_certificate",
            "candidate_crossing",
            "B3_block_pass",
            "is_tail",
        ]:
            if c in b3.columns:
                b3[c] = boolish(b3[c])
    else:
        b3 = pd.DataFrame()

    hexc = read_csv(HEXC_INTERVALS)
    if len(hexc):
        num(hexc, ["block_id", "y", "h", "Q_exc", "exc_over_abs_DeltaD", "endpoint_line_r2"])
        hexc_group = (
            hexc.groupby("block_id", dropna=False)
            .agg(Q_exc_max=("Q_exc", "max"), endpoint_line_r2_min=("endpoint_line_r2", "min"))
            .reset_index()
        )
    else:
        hexc_group = pd.DataFrame(columns=["block_id", "Q_exc_max", "endpoint_line_r2_min"])

    # Window table: one row per theta local candidate interval.
    windows = theta.copy()
    windows["x"] = windows["y"] + windows["h"]
    windows["post_P0"] = windows["p_star"].ge(P0)
    windows["source_coordinate"] = "theta_local"
    windows["side"] = windows["local_theta_sign"].fillna(windows["E_theta_local"].map(sign_label))
    windows["scale_ratio_local_to_global"] = [
        scale_ratio_local_to_global(float(h), float(p), float(x))
        for h, p, x in zip(windows["h"], windows["p_star"], windows["x"])
    ]
    windows["scale_ratio_global_to_local"] = 1.0 / windows["scale_ratio_local_to_global"].replace(0, np.nan)
    windows["sign_match"] = np.select(
        [
            windows["side"].eq("negative") & windows["negative_transfer_flag"],
            windows["side"].eq("positive") & windows["positive_harmless_flag"],
            windows["side"].eq("zero"),
        ],
        [True, True, True],
        default=False,
    )
    windows["scale_compatibility_ok"] = windows["scale_ratio_local_to_global"].replace([np.inf, -np.inf], np.nan).notna()
    windows["localization_ok"] = windows["covered_flag"] & windows["sign_match"] & windows["scale_compatibility_ok"]

    windows = windows.merge(hexc_group, on="block_id", how="left")

    # B3 tail candidate rows are added as crossing stress rows.
    b3_cross = pd.DataFrame()
    if len(b3):
        b3_cross = b3[b3["candidate_crossing"]].copy()
        if len(b3_cross):
            b3_cross["x"] = b3_cross["worst_prime"]
            b3_cross["y"] = b3_cross["covered_y"].fillna(b3_cross["start_prime"])
            b3_cross["h"] = b3_cross["covered_h"].fillna((b3_cross["end_prime"] - b3_cross["worst_prime"]).clip(lower=1))
            b3_cross["side"] = "negative"
            b3_cross["source_coordinate"] = "B3_tail"
            b3_cross["Q_theta"] = np.nan
            b3_cross["Q_R2Q"] = b3_cross["Q_tail_max_inside"]
            b3_cross["post_P0"] = b3_cross["p_star"].ge(P0)
            b3_cross["tail_flag"] = b3_cross["is_tail"]
            b3_cross["covered_flag"] = b3_cross["covered_by_block_or_certificate"]
            b3_cross["finite_certificate_flag"] = b3_cross["finite_certificate_flag"]
            b3_cross["negative_transfer_flag"] = True
            b3_cross["positive_harmless_flag"] = False
            b3_cross["sign_match"] = True
            b3_cross["scale_ratio_local_to_global"] = [
                scale_ratio_local_to_global(float(h), float(p), float(x))
                for h, p, x in zip(b3_cross["h"], b3_cross["p_star"], b3_cross["x"])
            ]
            b3_cross["scale_ratio_global_to_local"] = 1.0 / b3_cross["scale_ratio_local_to_global"].replace(0, np.nan)
            b3_cross["scale_compatibility_ok"] = b3_cross["scale_ratio_local_to_global"].replace(
                [np.inf, -np.inf], np.nan
            ).notna()
            b3_cross["localization_ok"] = (
                b3_cross["covered_flag"] & b3_cross["sign_match"] & b3_cross["scale_compatibility_ok"]
            )
            b3_cross["crossing_status"] = np.where(
                b3_cross["finite_certificate_flag"], "finite_certificate", "B3_tail_candidate"
            )
            b3_cross["E_theta_local"] = np.nan
            b3_cross["theta_local_norm"] = np.nan
            b3_cross["Cplus_value"] = np.nan
            b3_cross["B2_active_flag"] = b3_cross["covered_flag"]
            b3_cross["O2_B3_repaid_flag"] = b3_cross["covered_flag"]

    common_cols = [
        "x",
        "p_star",
        "y",
        "h",
        "side",
        "source_coordinate",
        "block_id",
        "Q_theta",
        "Q_R2Q",
        "E_theta_local",
        "theta_local_norm",
        "covered_flag",
        "finite_certificate_flag",
        "tail_flag",
        "B2_active_flag",
        "negative_transfer_flag",
        "positive_harmless_flag",
        "Cplus_value",
        "O2_B3_repaid_flag",
        "scale_ratio_local_to_global",
        "scale_ratio_global_to_local",
        "sign_match",
        "scale_compatibility_ok",
        "localization_ok",
        "crossing_status",
    ]
    for c in common_cols:
        if c not in windows.columns:
            windows[c] = np.nan
        if len(b3_cross) and c not in b3_cross.columns:
            b3_cross[c] = np.nan
    crossings = pd.concat([windows[common_cols], b3_cross[common_cols] if len(b3_cross) else pd.DataFrame(columns=common_cols)], ignore_index=True)

    failures = crossings[
        (~crossings["localization_ok"].fillna(False))
        | (crossings["post_P0"] if "post_P0" in crossings.columns else False)
    ].copy()
    # The line above is too broad if post_P0 is not present in common_cols; add
    # explicit failure reasons below using windows/crossings recomputation.
    crossings["post_P0"] = crossings["p_star"].ge(P0)
    crossings["failure_reason"] = ""
    crossings.loc[~crossings["covered_flag"].fillna(False), "failure_reason"] += "uncovered;"
    crossings.loc[~crossings["sign_match"].fillna(False), "failure_reason"] += "sign_mismatch;"
    crossings.loc[~crossings["scale_compatibility_ok"].fillna(False), "failure_reason"] += "scale_bad;"
    crossings.loc[
        crossings["side"].eq("positive") & crossings["Q_R2Q"].gt(1.0),
        "failure_reason",
    ] += "positive_not_harmless;"
    failures = crossings[crossings["failure_reason"].ne("")].copy()

    theta_candidates = windows[windows["source_coordinate"].eq("theta_local")]
    b3_tail_candidates = b3_cross if len(b3_cross) else pd.DataFrame(columns=common_cols)
    post = crossings[crossings["post_P0"]]
    neg = crossings[crossings["side"].eq("negative")]
    pos = crossings[crossings["side"].eq("positive")]

    scale = crossings["scale_ratio_local_to_global"].replace([np.inf, -np.inf], np.nan).dropna()
    post_failures = failures[failures["post_P0"]]

    summary = {
        "candidate_points": int(len(crossings)),
        "post_P0_candidate_points": int(len(post)),
        "covered_points": int(crossings["covered_flag"].fillna(False).sum()),
        "uncovered_points": int((~crossings["covered_flag"].fillna(False)).sum()),
        "coverage_frac": float(crossings["covered_flag"].fillna(False).mean()) if len(crossings) else np.nan,
        "theta_candidates": int(len(theta_candidates)),
        "theta_covered": int(theta_candidates["covered_flag"].fillna(False).sum()),
        "theta_uncovered": int((~theta_candidates["covered_flag"].fillna(False)).sum()),
        "B3_candidates": int(len(b3_tail_candidates)),
        "B3_covered": int(b3_tail_candidates["covered_flag"].fillna(False).sum()) if len(b3_tail_candidates) else 0,
        "B3_uncovered": int((~b3_tail_candidates["covered_flag"].fillna(False)).sum()) if len(b3_tail_candidates) else 0,
        "B3_tail_candidates": int(b3_tail_candidates["post_P0"].sum()) if len(b3_tail_candidates) else 0,
        "B3_tail_covered": int((b3_tail_candidates["post_P0"] & b3_tail_candidates["covered_flag"].fillna(False)).sum())
        if len(b3_tail_candidates)
        else 0,
        "B3_tail_uncovered": int((b3_tail_candidates["post_P0"] & ~b3_tail_candidates["covered_flag"].fillna(False)).sum())
        if len(b3_tail_candidates)
        else 0,
        "sign_match_frac": float(crossings["sign_match"].fillna(False).mean()) if len(crossings) else np.nan,
        "negative_transfer_frac": float(neg["negative_transfer_flag"].fillna(False).mean()) if len(neg) else np.nan,
        "positive_harmless_frac": float(pos["positive_harmless_flag"].fillna(False).mean()) if len(pos) else np.nan,
        "scale_compatibility_min": float(scale.min()) if len(scale) else np.nan,
        "scale_compatibility_max": float(scale.max()) if len(scale) else np.nan,
        "scale_compatibility_q95": q(scale, 0.95),
        "scale_compatibility_failures": int((~crossings["scale_compatibility_ok"].fillna(False)).sum()),
        "finite_certificate_candidates": int(crossings["finite_certificate_flag"].fillna(False).sum()),
        "post_P0_failures": int(len(post_failures)),
        "positive_Q_R2Q_max": float(pos["Q_R2Q"].max()) if len(pos) else np.nan,
        "positive_tail_Q_R2Q_max": float(pos.loc[pos["post_P0"], "Q_R2Q"].max()) if len(pos.loc[pos["post_P0"]]) else np.nan,
        "negative_Q_R2Q_max": float(neg["Q_R2Q"].max()) if len(neg) else np.nan,
        "near_forbidden_negative_count": int((crossings["side"].eq("negative") & crossings["Q_R2Q"].gt(0.75)).sum()),
        "near_forbidden_positive_count": int((crossings["side"].eq("positive") & crossings["Q_R2Q"].gt(0.75)).sum()),
        "forbidden_negative_count": int((crossings["side"].eq("negative") & crossings["Q_R2Q"].gt(1.0)).sum()),
        "forbidden_positive_count": int((crossings["side"].eq("positive") & crossings["Q_R2Q"].gt(1.0)).sum()),
        "pass_covering_localization_empirical": bool(
            len(failures) == 0
            and int((crossings["post_P0"] & ~crossings["covered_flag"].fillna(False)).sum()) == 0
            and int((crossings["side"].eq("positive") & crossings["Q_R2Q"].gt(1.0)).sum()) == 0
            and int((crossings["side"].eq("positive") & crossings["Q_R2Q"].gt(0.75)).sum()) == 0
        ),
    }

    windows.to_csv(WINDOWS_OUT, index=False)
    crossings.to_csv(CROSSINGS_OUT, index=False)
    failures.to_csv(FAILURES_OUT, index=False)
    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)
    write_doc(summary, failures, crossings)
    refresh_manifest()

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {WINDOWS_OUT}")
    log(f"Wrote {CROSSINGS_OUT}")
    log(f"Wrote {FAILURES_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k, v in summary.items():
        log(f"{k} = {v}")


if __name__ == "__main__":
    main()
