#!/usr/bin/env python3
"""RawR2Q full primitive export, Route A.

This script promotes RawR2Q from the v2 partial primitive export to a v3
full-inventory primitive export by re-entering the SR11/O2 projection
coordinate.  The proof-facing point is that the 1302 positive short rows
were not mathematically mysterious; they were missing endpoint/bridge fields
because the earlier endpoint exports only covered LongA rows.

Inputs:
  * repair/FCL window inventory for theta/Q_R2Q metadata
  * repo notes/O2 projection intervals for D_y, D_y_plus_h, observed_delta
  * repo notes/SR11 realpath samples for bridge excursion samples

Outputs are written beside this script.
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
REPO = Path(r"C:\Users\jhegy\source\repos\prime-mesh-theory")
ROOT_NOTES = REPO / "notes"

PROJECTION = ROOT_NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"
SAMPLES = ROOT_NOTES / "sr11_realpath_pstar" / "prime_mesh_r2q_sr11_realpath_noise_samples.csv"
if not SAMPLES.exists():
    SAMPLES = ROOT_NOTES / "prime_mesh_r2q_sr11_realpath_noise_samples.csv"

FCL_WINDOWS = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_windows.csv"
HEXC_ROWS = OUT / "prime_mesh_r2q_hexc_bridge_rigidity_rows.csv"
V2_ROWS = OUT / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v2.csv"

FULL_EXPORT_OUT = OUT / "prime_mesh_r2q_rawr2q_full_primitive_export_rows.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv"
SUMMARY_OUT = OUT / "prime_mesh_r2q_rawr2q_primitive_decomposition_summary_v3.csv"
SIGN_OUT = OUT / "prime_mesh_r2q_rawr2q_primitive_decomposition_sign_checks_v3.csv"
GAP_OUT = OUT / "prime_mesh_r2q_rawr2q_primitive_decomposition_gap_rows_v3.csv"
FAIL_OUT = OUT / "prime_mesh_r2q_rawr2q_primitive_decomposition_failures_v3.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_v3.md"
MANIFEST = OUT / "deposit_manifest.csv"

FORMULA_RESIDUAL_CAP = 0.03
Q_NEAR = 0.75
Q_FORBIDDEN = 1.0
Q_POS_CAP = 0.25


def log(msg: str) -> None:
    print(f"[rawr2q-v3 {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def to_bool(s: pd.Series, default: bool = False) -> pd.Series:
    if s is None:
        return pd.Series(default)
    if s.dtype == bool:
        return s.fillna(default)
    return s.astype(str).str.lower().map(
        {"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False}
    ).fillna(default)


def sign_label(values: pd.Series | np.ndarray) -> pd.Series:
    arr = pd.Series(values)
    return np.select([arr < 0, arr > 0], ["negative", "positive"], default="zero")


def read_projection() -> pd.DataFrame:
    required = [
        "block_id",
        "p_star",
        "y",
        "h",
        "D_y",
        "D_y_plus_h",
        "observed_delta",
        "denom_sqrt_h_logB",
        "Q_max",
        "is_tail",
        "depth_bin",
        "mu_bin",
        "scale_bin",
        "hi",
    ]
    df = pd.read_csv(PROJECTION, usecols=lambda c: c in required)
    for c in ["block_id", "p_star", "y", "h", "D_y", "D_y_plus_h", "observed_delta", "denom_sqrt_h_logB", "Q_max"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["block_id"] = df["block_id"].astype(int)
    df["p_star"] = df["p_star"].astype(int)
    df["y"] = df["y"].astype(int)
    df["h"] = df["h"].astype(int)
    return df


def read_fcl() -> pd.DataFrame:
    cols = [
        "block_id",
        "x",
        "y",
        "h",
        "p_star",
        "E_theta_local",
        "theta_local_sign",
        "E_theta",
        "E_theta_sign",
        "Q_R2Q",
        "post_P0",
        "post_P0_flag",
        "finite_certificate_flag",
        "positive_harmless_flag",
        "negative_transfer_flag",
        "near_forbidden_R2Q",
        "forbidden_R2Q",
        "channel_full",
        "channel_inferred",
        "O2_B3_repaid_flag",
        "B3_block_pass",
        "covered_flag",
        "source_coordinate",
        "side",
    ]
    df = pd.read_csv(FCL_WINDOWS, usecols=lambda c: c in cols)
    for c in ["block_id", "x", "y", "h", "p_star", "E_theta_local", "E_theta", "Q_R2Q"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["block_id"] = df["block_id"].astype(int)
    df["y"] = df["y"].astype(int)
    df["h"] = df["h"].astype(int)
    return df


def read_hexc_metadata() -> pd.DataFrame:
    if not HEXC_ROWS.exists():
        return pd.DataFrame()
    cols = [
        "candidate_id",
        "block_id",
        "x",
        "y",
        "h",
        "p_star",
        "right_endpoint",
        "endpoint_exclusion_flag",
        "endpoint_exclusion_Q",
        "endpoint_exclusion_harmful_flag",
        "O2_applicable_flag",
        "B3_applicable_flag",
        "C_minus_flag",
        "coordinate_available_flag",
    ]
    df = pd.read_csv(HEXC_ROWS, usecols=lambda c: c in cols)
    for c in ["block_id", "x", "y", "h", "p_star", "right_endpoint", "endpoint_exclusion_Q"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["block_id"] = df["block_id"].astype(int)
    return df


def collect_samples(intervals: pd.DataFrame) -> dict[tuple[int, int], pd.DataFrame]:
    wanted = {
        (int(r.block_id), int(r.y)): int(r.h)
        for r in intervals[["block_id", "y", "h"]].itertuples(index=False)
    }
    by_block: dict[int, set[int]] = {}
    for block_id, y in wanted:
        by_block.setdefault(block_id, set()).add(y)

    usecols = ["block_id", "y", "h", "D_y_plus_h"]
    kept: list[pd.DataFrame] = []
    log(f"Reading SR11 samples from {SAMPLES}")
    for chunk_idx, chunk in enumerate(pd.read_csv(SAMPLES, usecols=usecols, chunksize=250_000)):
        if chunk_idx % 10 == 0:
            log(f"  sample chunk {chunk_idx}")
        mask = np.zeros(len(chunk), dtype=bool)
        for block_id, ys in by_block.items():
            m = chunk["block_id"].eq(block_id) & chunk["y"].isin(ys)
            if m.any():
                mask |= m.to_numpy()
        part = chunk.loc[mask].copy()
        if len(part):
            max_h = part.apply(lambda r: wanted.get((int(r["block_id"]), int(r["y"])), -1), axis=1)
            part = part[part["h"].to_numpy() <= max_h.to_numpy()]
            if len(part):
                kept.append(part)

    if not kept:
        return {}
    samples = pd.concat(kept, ignore_index=True)
    out: dict[tuple[int, int], pd.DataFrame] = {}
    for key, part in samples.groupby(["block_id", "y"], sort=False):
        out[(int(key[0]), int(key[1]))] = part.sort_values("h")
    log(f"Collected sample paths for {len(out)} intervals")
    return out


def compute_bridge_primitives(rows: pd.DataFrame, samples: dict[tuple[int, int], pd.DataFrame]) -> pd.DataFrame:
    out_rows: list[dict[str, Any]] = []
    for r in rows.itertuples(index=False):
        block_id = int(r.block_id)
        y = int(r.y)
        h = int(r.h)
        d_start = float(r.D_y)
        d_end = float(r.D_y_plus_h)
        delta = float(r.observed_delta)
        p_star = int(r.p_star)
        denom = float(r.denom_sqrt_h_logB)

        part = samples.get((block_id, y), pd.DataFrame())
        if len(part):
            offsets = part["h"].astype(float).to_numpy()
            values = part["D_y_plus_h"].astype(float).to_numpy()
        else:
            offsets = np.array([], dtype=float)
            values = np.array([], dtype=float)

        offsets = np.concatenate([[0.0], offsets, [float(h)]])
        values = np.concatenate([[d_start], values, [d_end]])
        order = np.argsort(offsets)
        offsets = offsets[order]
        values = values[order]
        unique_offsets, unique_idx = np.unique(offsets, return_index=True)
        offsets = unique_offsets
        values = values[unique_idx]

        line = d_start + (offsets / float(h)) * delta if h else np.full_like(offsets, d_start)
        diff = values - line
        abs_diff = np.abs(diff)
        max_idx = int(abs_diff.argmax()) if len(abs_diff) else 0
        bridge_excursion_raw = float(abs_diff[max_idx]) if len(abs_diff) else 0.0
        bridge_excursion_signed = float(diff[max_idx]) if len(diff) else 0.0
        bridge_argmax = int(y + offsets[max_idx]) if len(offsets) else y

        q_delta = abs(delta) / denom if denom else math.nan
        q_exc = bridge_excursion_raw / denom if denom else math.nan
        out_rows.append(
            {
                "block_id": block_id,
                "y": y,
                "h": h,
                "p_star": p_star,
                "D_start": d_start,
                "D_end": d_end,
                "DeltaD": delta,
                "DeltaD_sign": "negative" if delta < 0 else ("positive" if delta > 0 else "zero"),
                "Q_delta_D": q_delta,
                "bridge_excursion_raw": bridge_excursion_raw,
                "bridge_excursion_signed": bridge_excursion_signed,
                "bridge_excursion_argmax": bridge_argmax,
                "bridge_path_n_samples": int(len(offsets)),
                "Q_exc": q_exc,
            }
        )
    return pd.DataFrame(out_rows)


def make_v3() -> tuple[pd.DataFrame, dict[str, Any]]:
    projection = read_projection()
    fcl = read_fcl()
    hexc = read_hexc_metadata()

    base = projection.merge(
        fcl,
        on=["block_id", "y", "h"],
        how="left",
        suffixes=("_proj", "_fcl"),
        validate="one_to_one",
    )
    if "p_star_fcl" in base:
        base["p_star"] = base["p_star_proj"].fillna(base["p_star_fcl"])
    if "x" not in base:
        base["x"] = base.get("hi", base["y"] + base["h"])
    base["x"] = pd.to_numeric(base["x"], errors="coerce").fillna(base["y"] + base["h"]).astype(int)
    base["right_endpoint"] = base["x"]
    base["Q_R2Q"] = pd.to_numeric(base.get("Q_R2Q", base["Q_max"]), errors="coerce").fillna(base["Q_max"])
    base["E_theta"] = pd.to_numeric(base.get("E_theta_local", base.get("E_theta")), errors="coerce")
    base["E_theta_sign"] = base.get("theta_local_sign", base.get("E_theta_sign", pd.Series(sign_label(base["E_theta"]))))
    base["E_theta_sign"] = base["E_theta_sign"].fillna(pd.Series(sign_label(base["E_theta"])))
    base["post_P0_flag"] = to_bool(base.get("post_P0_flag", base.get("post_P0", pd.Series(False, index=base.index))))
    if "post_P0" in base:
        base["post_P0_flag"] = base["post_P0_flag"] | to_bool(base["post_P0"])
    base["finite_zone_flag"] = ~base["post_P0_flag"]
    base["finite_certificate_flag"] = to_bool(base.get("finite_certificate_flag", pd.Series(False, index=base.index)))
    base["positive_harmless_flag"] = to_bool(base.get("positive_harmless_flag", pd.Series(False, index=base.index)))
    base["negative_transfer_flag"] = to_bool(base.get("negative_transfer_flag", pd.Series(False, index=base.index)))
    base["near_forbidden_flag"] = base["Q_R2Q"] > Q_NEAR
    base["forbidden_flag"] = base["Q_R2Q"] > Q_FORBIDDEN

    samples = collect_samples(base)
    prim = compute_bridge_primitives(base, samples)
    df = base.merge(prim, on=["block_id", "y", "h", "p_star"], how="left", validate="one_to_one")

    if len(hexc):
        keep = [
            c
            for c in hexc.columns
            if c
            not in {
                "x",
                "y",
                "h",
                "p_star",
            }
        ]
        df = df.merge(hexc[keep], on="block_id", how="left", suffixes=("", "_hexc"))
    else:
        df["candidate_id"] = [f"cand_{i:05d}" for i in range(len(df))]

    if "candidate_id" not in df or df["candidate_id"].isna().all():
        df["candidate_id"] = [f"cand_{i:05d}" for i in range(len(df))]
    df["candidate_id"] = df["candidate_id"].fillna(df["block_id"].map(lambda b: f"cand_{int(b)-1:05d}"))

    df["Q_formula_sum"] = df["Q_delta_D"] + df["Q_exc"]
    df["formula_residual"] = df["Q_R2Q"] - df["Q_formula_sum"]
    df["abs_formula_residual"] = df["formula_residual"].abs()
    df["formula_residual_frac"] = np.where(
        df["Q_R2Q"].abs() > 0,
        df["abs_formula_residual"] / df["Q_R2Q"].abs(),
        np.nan,
    )
    df["primitive_available_flag"] = df[["D_start", "D_end", "DeltaD", "Q_delta_D", "bridge_excursion_raw", "Q_exc"]].notna().all(axis=1)
    df["instrumentation_gap_flag"] = ~df["primitive_available_flag"]

    df["positive_harmless_flag"] = df["positive_harmless_flag"] | df["E_theta_sign"].eq("positive")
    df["threshold_relevant_flag"] = df["Q_R2Q"] > Q_NEAR
    df["pos_harm_antecedent"] = df["E_theta_sign"].eq("positive") & df["primitive_available_flag"]
    df["pos_harm_consequent"] = df["Q_delta_D"] <= Q_POS_CAP
    df["pos_harm_prim_violation"] = df["pos_harm_antecedent"] & ~df["pos_harm_consequent"]
    df["pos_harm_instrumentation_gap"] = df["E_theta_sign"].eq("positive") & ~df["primitive_available_flag"]

    df["neg_transfer_antecedent"] = (df["Q_delta_D"] > Q_NEAR) & df["primitive_available_flag"]
    df["neg_transfer_consequent"] = df["E_theta_sign"].eq("negative")
    df["neg_transfer_prim_violation"] = df["neg_transfer_antecedent"] & ~df["neg_transfer_consequent"]

    df["sign_consistent"] = df["DeltaD_sign"].eq(df["E_theta_sign"])
    df["sign_inconsistent_flag"] = df["primitive_available_flag"] & ~df["sign_consistent"]
    df["sign_inconsistent_positive_harmless"] = df["sign_inconsistent_flag"] & df["E_theta_sign"].eq("positive") & (df["Q_delta_D"] <= Q_POS_CAP)
    df["sign_inconsistent_threshold_relevant"] = df["sign_inconsistent_flag"] & df["threshold_relevant_flag"]
    df["sign_inconsistent_forbidden"] = df["sign_inconsistent_flag"] & df["forbidden_flag"]

    df["formula_residual_cap_violation"] = df["primitive_available_flag"] & (df["abs_formula_residual"] > FORMULA_RESIDUAL_CAP)
    df["threshold_relevant_missing_primitives"] = df["threshold_relevant_flag"] & ~df["primitive_available_flag"]
    df["positive_missing_primitive_rows_flag"] = df["E_theta_sign"].eq("positive") & ~df["primitive_available_flag"]

    def status(row: pd.Series) -> str:
        if not bool(row["primitive_available_flag"]):
            return "instrumentation_gap"
        if bool(row["formula_residual_cap_violation"]):
            return "formula_residual_violation"
        if bool(row["neg_transfer_prim_violation"]):
            return "negative_transfer_violation"
        if bool(row["pos_harm_prim_violation"]):
            return "positive_harmless_violation"
        if bool(row["sign_inconsistent_positive_harmless"]):
            return "sign_inconsistent_positive_harmless"
        if bool(row["neg_transfer_antecedent"]):
            return "primitive_negative_transfer_verified"
        if bool(row["pos_harm_antecedent"]):
            return "primitive_positive_cap_verified"
        return "primitive_full_verified"

    df["row_status"] = df.apply(status, axis=1)

    summary: dict[str, Any] = {
        "rows": int(len(df)),
        "primitive_full_rows": int(df["primitive_available_flag"].sum()),
        "primitive_missing_rows": int((~df["primitive_available_flag"]).sum()),
        "primitive_unavailable": int((~df["primitive_available_flag"]).sum()),
        "instrumentation_gap_rows": int(df["instrumentation_gap_flag"].sum()),
        "positive_rows": int(df["E_theta_sign"].eq("positive").sum()),
        "positive_missing_primitive_rows": int(df["positive_missing_primitive_rows_flag"].sum()),
        "positive_harmless_instrumentation_gap_rows": int(df["pos_harm_instrumentation_gap"].sum()),
        "threshold_relevant_rows": int(df["threshold_relevant_flag"].sum()),
        "threshold_relevant_missing_primitives": int(df["threshold_relevant_missing_primitives"].sum()),
        "forbidden_rows": int(df["forbidden_flag"].sum()),
        "formula_rows": int(df["primitive_available_flag"].sum()),
        "max_abs_formula_residual": float(df.loc[df["primitive_available_flag"], "abs_formula_residual"].max()),
        "mean_abs_formula_residual": float(df.loc[df["primitive_available_flag"], "abs_formula_residual"].mean()),
        "formula_residual_cap": FORMULA_RESIDUAL_CAP,
        "formula_residual_cap_violations": int(df["formula_residual_cap_violation"].sum()),
        "primitive_negative_transfer_antecedent_rows": int(df["neg_transfer_antecedent"].sum()),
        "primitive_negative_transfer_violations": int(df["neg_transfer_prim_violation"].sum()),
        "pass_primitive_negative_transfer": bool(df["neg_transfer_prim_violation"].sum() == 0),
        "primitive_positive_available_rows": int(df["pos_harm_antecedent"].sum()),
        "primitive_positive_violations": int(df["pos_harm_prim_violation"].sum()),
        "pass_primitive_positive_harmlessness": bool(df["pos_harm_prim_violation"].sum() == 0 and df["positive_missing_primitive_rows_flag"].sum() == 0),
        "pass_primitive_positive_available_harmlessness": bool(df["pos_harm_prim_violation"].sum() == 0),
        "sign_consistency_checked_rows": int(df["primitive_available_flag"].sum()),
        "sign_consistent_rows": int((df["primitive_available_flag"] & df["sign_consistent"]).sum()),
        "sign_inconsistent_rows": int(df["sign_inconsistent_flag"].sum()),
        "sign_inconsistent_positive_harmless_rows": int(df["sign_inconsistent_positive_harmless"].sum()),
        "sign_inconsistent_threshold_relevant_rows": int(df["sign_inconsistent_threshold_relevant"].sum()),
        "sign_inconsistent_forbidden_rows": int(df["sign_inconsistent_forbidden"].sum()),
    }
    summary["pass_rawr2q_operational_greenlight"] = bool(
        summary["threshold_relevant_missing_primitives"] == 0
        and summary["primitive_negative_transfer_violations"] == 0
        and summary["primitive_positive_violations"] == 0
        and summary["formula_residual_cap_violations"] == 0
    )
    summary["pass_rawr2q_primitive_proof_grade"] = bool(
        summary["primitive_missing_rows"] == 0
        and summary["positive_missing_primitive_rows"] == 0
        and summary["formula_residual_cap_violations"] == 0
        and summary["primitive_negative_transfer_violations"] == 0
        and summary["primitive_positive_violations"] == 0
    )
    summary["computation_route_used"] = "Route A: SR11/O2 projection intervals plus SR11 realpath samples"
    summary["proof_grade_blocker"] = (
        "none"
        if summary["pass_rawr2q_primitive_proof_grade"]
        else "formula residual cap violations remain after full primitive coverage"
        if summary["formula_residual_cap_violations"]
        else "primitive rows still missing"
        if summary["primitive_missing_rows"]
        else "positive primitive violations remain"
    )
    summary["recommended_next_file"] = (
        "Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_Closure_Update_v1.md"
        if summary["pass_rawr2q_primitive_proof_grade"]
        else "Prime_Mesh_R2Q_RawR2Q_FullPrimitiveExport_Repair_Map_v1.md"
    )
    return df, summary


def write_summary(summary: dict[str, Any]) -> None:
    with SUMMARY_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["field", "value"])
        for k, v in summary.items():
            w.writerow([k, v])


def write_doc(df: pd.DataFrame, summary: dict[str, Any]) -> None:
    status = "proof-grade full primitive export" if summary["pass_rawr2q_primitive_proof_grade"] else "partial"
    lines = [
        "# Prime Mesh R2Q - RawR2Q Primitive Decomposition v3",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-08",
        f"**Status:** {status}",
        "",
        "## 1. Executive Verdict",
        "",
    ]
    if summary["pass_rawr2q_primitive_proof_grade"]:
        lines += [
            r"\[",
            r"\boxed{\text{RawR2Q primitive decomposition is globally proof-grade for the audited inventory.}}",
            r"\]",
            "",
            "Route A succeeded: every coordinate-test row now has endpoint and bridge primitives.",
        ]
    elif summary["pass_rawr2q_operational_greenlight"]:
        lines += [
            r"\[",
            r"\boxed{\text{Operational greenlight passes, but primitive proof-grade remains partial.}}",
            r"\]",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{RawR2Q v3 has proof-facing failures requiring repair.}}",
            r"\]",
        ]
    lines += [
        "",
        "## 2. Inputs and Route",
        "",
        f"- Route used: `{summary['computation_route_used']}`.",
        f"- Projection input: `{PROJECTION}`.",
        f"- SR11 samples: `{SAMPLES}`.",
        "",
        "## 3. Primitive Coverage",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| rows | {summary['rows']} |",
        f"| primitive_full_rows | {summary['primitive_full_rows']} |",
        f"| primitive_missing_rows | {summary['primitive_missing_rows']} |",
        f"| positive_missing_primitive_rows | {summary['positive_missing_primitive_rows']} |",
        f"| threshold_relevant_missing_primitives | {summary['threshold_relevant_missing_primitives']} |",
        "",
        "## 4. Formula Decomposition",
        "",
        r"\[",
        r"Q_{\rm R2Q}(J)=Q_{\Delta D}(J)+Q_{\rm exc}(J)+\epsilon(J).",
        r"\]",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| formula_rows | {summary['formula_rows']} |",
        f"| max_abs_formula_residual | {summary['max_abs_formula_residual']} |",
        f"| mean_abs_formula_residual | {summary['mean_abs_formula_residual']} |",
        f"| formula_residual_cap | {summary['formula_residual_cap']} |",
        f"| formula_residual_cap_violations | {summary['formula_residual_cap_violations']} |",
        "",
        "## 5. NegativeTransfer Primitive Check",
        "",
        r"\[Q_{\Delta D}>3/4\Rightarrow E_\theta<0.\]",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| antecedent_rows | {summary['primitive_negative_transfer_antecedent_rows']} |",
        f"| violations | {summary['primitive_negative_transfer_violations']} |",
        f"| pass | {summary['pass_primitive_negative_transfer']} |",
        "",
        "## 6. PositiveHarmlessness Primitive Check",
        "",
        r"\[E_\theta>0\Rightarrow Q_{\Delta D}\le1/4.\]",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| positive_rows | {summary['positive_rows']} |",
        f"| primitive_positive_available_rows | {summary['primitive_positive_available_rows']} |",
        f"| positive_missing_primitive_rows | {summary['positive_missing_primitive_rows']} |",
        f"| primitive_positive_violations | {summary['primitive_positive_violations']} |",
        f"| pass_global_positive_harmlessness | {summary['pass_primitive_positive_harmlessness']} |",
        "",
        "## 7. Sign Inconsistency Classification",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| checked_rows | {summary['sign_consistency_checked_rows']} |",
        f"| sign_consistent_rows | {summary['sign_consistent_rows']} |",
        f"| sign_inconsistent_rows | {summary['sign_inconsistent_rows']} |",
        f"| sign_inconsistent_positive_harmless_rows | {summary['sign_inconsistent_positive_harmless_rows']} |",
        f"| sign_inconsistent_threshold_relevant_rows | {summary['sign_inconsistent_threshold_relevant_rows']} |",
        f"| sign_inconsistent_forbidden_rows | {summary['sign_inconsistent_forbidden_rows']} |",
        "",
        "The global biconditional `DeltaD < 0 iff E_theta < 0` is not asserted.  The proof-facing sign statement remains the threshold-relevant direction.",
        "",
        "## 8. Status by Row Class",
        "",
        df["row_status"].value_counts().rename_axis("row_status").reset_index(name="rows").to_markdown(index=False),
        "",
        "## 9. Proof Interpretation",
        "",
    ]
    if summary["pass_rawr2q_primitive_proof_grade"]:
        lines += [
            "Route A closes the instrumentation gap for the audited inventory. The previous 1302 positive-short gap rows now carry endpoint and bridge primitives, and no primitive proof-grade checks fail.",
            "",
            f"Recommended next file: `{summary['recommended_next_file']}`.",
        ]
    else:
        lines += [
            f"Route A did not fully close the proof-grade gate. Blocker: `{summary['proof_grade_blocker']}`.",
            "",
            f"Recommended next file: `{summary['recommended_next_file']}`.",
        ]
    lines += ["", "---", "", "*Prime Mesh Theory - RH Programme*"]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def refresh_manifest(paths: list[Path]) -> None:
    existing = pd.DataFrame()
    if MANIFEST.exists():
        try:
            existing = pd.read_csv(MANIFEST)
        except Exception:
            existing = pd.DataFrame()
    rows = []
    for p in paths:
        rows.append(
            {
                "file": p.name,
                "path": str(p),
                "bytes": p.stat().st_size if p.exists() else 0,
                "status": "new_or_refreshed",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    add = pd.DataFrame(rows)
    if len(existing):
        key = "file" if "file" in existing.columns else existing.columns[0]
        existing = existing[~existing[key].isin(add["file"])]
        combined = pd.concat([existing, add], ignore_index=True, sort=False)
    else:
        combined = add
    combined.to_csv(MANIFEST, index=False)


def main() -> None:
    log("Building RawR2Q v3 full primitive export")
    df, summary = make_v3()

    full_cols = [
        "candidate_id",
        "block_id",
        "x",
        "y",
        "h",
        "right_endpoint",
        "p_star",
        "post_P0_flag",
        "finite_zone_flag",
        "E_theta",
        "E_theta_sign",
        "Q_R2Q",
        "D_start",
        "D_end",
        "DeltaD",
        "DeltaD_sign",
        "Q_delta_D",
        "bridge_excursion_raw",
        "bridge_excursion_argmax",
        "bridge_path_n_samples",
        "Q_exc",
        "Q_formula_sum",
        "formula_residual",
        "abs_formula_residual",
        "positive_harmless_flag",
        "near_forbidden_flag",
        "forbidden_flag",
        "threshold_relevant_flag",
        "primitive_available_flag",
        "instrumentation_gap_flag",
    ]
    for c in full_cols:
        if c not in df:
            df[c] = np.nan
    df[full_cols].to_csv(FULL_EXPORT_OUT, index=False)
    df.to_csv(ROWS_OUT, index=False)
    write_summary(summary)

    sign_cols = [
        "candidate_id",
        "block_id",
        "E_theta",
        "E_theta_sign",
        "DeltaD",
        "DeltaD_sign",
        "Q_delta_D",
        "Q_R2Q",
        "sign_consistent",
        "sign_inconsistent_flag",
        "sign_inconsistent_positive_harmless",
        "sign_inconsistent_threshold_relevant",
        "sign_inconsistent_forbidden",
        "row_status",
    ]
    df[sign_cols].to_csv(SIGN_OUT, index=False)
    df.loc[df["instrumentation_gap_flag"]].to_csv(GAP_OUT, index=False)
    failures = df[
        df["formula_residual_cap_violation"]
        | df["neg_transfer_prim_violation"]
        | df["pos_harm_prim_violation"]
        | df["threshold_relevant_missing_primitives"]
    ].copy()
    failures.to_csv(FAIL_OUT, index=False)
    write_doc(df, summary)
    refresh_manifest([FULL_EXPORT_OUT, ROWS_OUT, SUMMARY_OUT, SIGN_OUT, GAP_OUT, FAIL_OUT, DOC_OUT, Path(__file__)])

    log("Summary:")
    for k, v in summary.items():
        log(f"  {k} = {v}")
    log(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
