#!/usr/bin/env python3
"""BlockSystem definition audit/export for FCL.

Exports the concrete empirical objects needed by the deterministic FCL front
end:

    X_cand, B, Phi, x preceq J, rho(x,J), p*/x, h/x.

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

FCL_CROSSINGS = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv"
FCL_WINDOWS = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_windows.csv"
B3_BLOCKS = OUT / "prime_mesh_r2q_b3_block_to_tail_blocks.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_blocksystem_definition_summary.csv"
CANDIDATES_OUT = OUT / "prime_mesh_r2q_blocksystem_definition_candidates.csv"
BLOCKS_OUT = OUT / "prime_mesh_r2q_blocksystem_definition_blocks.csv"
SELECTION_OUT = OUT / "prime_mesh_r2q_blocksystem_definition_selection_map.csv"
GEOMETRY_OUT = OUT / "prime_mesh_r2q_blocksystem_definition_geometry.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_blocksystem_definition_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_BlockSystem_Definition_Audit_v1.md"
MANIFEST_OUT = OUT / "deposit_manifest.csv"

P0 = 500_000_000


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        log(f"Missing input: {path}")
        return pd.DataFrame()
    return pd.read_csv(path)


def num(df: pd.DataFrame, cols: list[str]) -> None:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")


def boolish(s: pd.Series) -> pd.Series:
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def scale_ratio(h: float, p_star: float, x: float) -> float:
    if h <= 0 or p_star <= 1 or x <= 1:
        return float("nan")
    return math.sqrt(h) * math.log(p_star) ** 2 / (math.sqrt(x) * math.log(x) ** 2)


def q(series: pd.Series, value: float) -> float:
    clean = series.replace([np.inf, -np.inf], np.nan).dropna()
    if len(clean) == 0:
        return float("nan")
    return float(clean.quantile(value))


def add_failure(rows: list[dict[str, object]], row: pd.Series, failure_type: str, reason: str) -> None:
    rows.append(
        {
            "candidate_id": row.get("candidate_id", ""),
            "x": row.get("x", np.nan),
            "source": row.get("source", ""),
            "failure_type": failure_type,
            "selected_block_id": row.get("selected_block_id", ""),
            "reason": reason,
            "post_P0_flag": bool(row.get("post_P0_flag", False)),
            "finite_certificate_flag": bool(row.get("finite_certificate_flag", False)),
            "status": row.get("status", ""),
        }
    )


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


def write_doc(summary: dict[str, object], failures: pd.DataFrame) -> None:
    status = "passes" if summary["pass_blocksystem_definition_empirical"] else "needs repair"
    lines = [
        "# Prime Mesh R2Q - BlockSystem Definition Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-08",
        f"**Status:** BlockSystem export audit - {status}",
        "",
        "## 1. Executive Verdict",
        "",
        "This audit exports the empirical block-system layer needed by the deterministic FCL front end:",
        "",
        r"\[",
        r"\mathcal X_{\rm cand},\quad \mathcal B,\quad \Phi,\quad x\preceq J,\quad \rho(x,J),\quad p^*/x,\quad h/x.",
        r"\]",
        "",
        "## 2. Inputs Used",
        "",
        f"- `{FCL_CROSSINGS.name}`",
        f"- `{FCL_WINDOWS.name}`",
        f"- `{B3_BLOCKS.name}`",
        "",
        "## 3. Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    for k, v in summary.items():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## 4. Failures",
        "",
        failures.to_markdown(index=False) if len(failures) else "No failures found.",
        "",
        "## 5. Interpretation",
        "",
    ]
    if summary["pass_blocksystem_definition_empirical"]:
        lines += [
            r"\[",
            r"\boxed{\text{The empirical BlockSystem definition passes: }\Phi\text{ is total on candidates and geometry is valid.}}",
            r"\]",
            "",
            "The post-`P0` candidate set has no coverage, compatibility, geometry, or control-relation failures.",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{The BlockSystem export found failures; inspect the failure table before theorem freeze.}}",
            r"\]",
        ]
    lines += [
        "",
        "## 6. Outputs",
        "",
        f"- `{SUMMARY_OUT.name}`",
        f"- `{CANDIDATES_OUT.name}`",
        f"- `{BLOCKS_OUT.name}`",
        f"- `{SELECTION_OUT.name}`",
        f"- `{GEOMETRY_OUT.name}`",
        f"- `{FAILURES_OUT.name}`",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
    ]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    log("Reading FCL crossings and windows")
    crossings = read_csv(FCL_CROSSINGS)
    windows = read_csv(FCL_WINDOWS)
    b3 = read_csv(B3_BLOCKS)
    if len(crossings) == 0:
        raise SystemExit("Missing FCL crossings; run FCL stress audit first.")

    num(crossings, ["x", "p_star", "y", "h", "block_id", "Q_theta", "Q_R2Q", "E_theta_local"])
    for c in [
        "covered_flag",
        "finite_certificate_flag",
        "tail_flag",
        "B2_active_flag",
        "negative_transfer_flag",
        "positive_harmless_flag",
        "O2_B3_repaid_flag",
        "sign_match",
        "scale_compatibility_ok",
        "localization_ok",
        "post_P0",
    ]:
        if c in crossings.columns:
            crossings[c] = boolish(crossings[c])

    num(windows, ["block_id", "p_star", "y", "h", "Q_R2Q", "E_theta_local"])
    for c in [
        "B2_active_flag",
        "covered_flag",
        "finite_certificate_flag",
        "negative_transfer_flag",
        "positive_harmless_flag",
        "O2_B3_repaid_flag",
        "tail_flag",
    ]:
        if c in windows.columns:
            windows[c] = boolish(windows[c])

    if len(b3):
        num(b3, ["block_id", "p_star", "start_prime", "worst_prime", "end_prime", "Q_tail_max_inside", "Q_local"])
        for c in ["covered_flag", "finite_certificate_flag", "covered_by_block_or_certificate", "B3_block_pass", "is_tail"]:
            if c in b3.columns:
                b3[c] = boolish(b3[c])

    # Candidate export X_cand.
    cand = crossings.copy().reset_index(drop=True)
    cand.insert(0, "candidate_id", [f"cand_{i:05d}" for i in range(len(cand))])
    cand["theta_candidate_flag"] = cand["source_coordinate"].eq("theta_local")
    cand["B3_candidate_flag"] = cand["source_coordinate"].eq("B3_tail")
    cand["source"] = np.select(
        [cand["theta_candidate_flag"] & cand["B3_candidate_flag"], cand["theta_candidate_flag"], cand["B3_candidate_flag"]],
        ["theta+B3", "theta", "B3"],
        default="unknown",
    )
    cand["post_P0_flag"] = cand["x"].ge(P0)
    cand["finite_certificate_flag"] = cand["finite_certificate_flag"] | ~cand["post_P0_flag"]
    cand["selected_block_id"] = cand.apply(
        lambda r: f"{r['source_coordinate']}:{int(r['block_id'])}:{int(float(r['y']))}:{int(float(r['h']))}"
        if pd.notna(r["block_id"]) and pd.notna(r["y"]) and pd.notna(r["h"])
        else "",
        axis=1,
    )
    cand["covered_flag"] = cand["covered_flag"].fillna(False)
    cand["status"] = np.where(cand["covered_flag"], "covered", "uncovered")

    # Geometry/control values.
    cand["right_endpoint"] = cand["y"] + cand["h"]
    cand["right_endpoint_control_flag"] = (cand["x"] - cand["right_endpoint"]).abs().le(1e-9)
    cand["containing_block_control_flag"] = (cand["y"] <= cand["x"]) & (cand["x"] <= cand["right_endpoint"])
    cand["partial_interval_used_flag"] = cand["B3_candidate_flag"] | (
        cand["containing_block_control_flag"] & ~cand["right_endpoint_control_flag"]
    )
    cand["control_type"] = np.select(
        [
            cand["finite_certificate_flag"],
            cand["right_endpoint_control_flag"],
            cand["containing_block_control_flag"],
            cand["partial_interval_used_flag"],
        ],
        ["finite_certificate", "right_endpoint", "containing_block", "partial_interval"],
        default="failure",
    )
    cand["scale_ratio"] = [
        scale_ratio(float(h), float(p), float(x)) for h, p, x in zip(cand["h"], cand["p_star"], cand["x"])
    ]
    cand["pstar_over_x"] = cand["p_star"] / cand["x"].replace(0, np.nan)
    cand["h_over_x"] = cand["h"] / cand["x"].replace(0, np.nan)
    cand["pstar_comparable_flag"] = cand["pstar_over_x"].between(0, 10, inclusive="neither")
    cand["h_short_flag"] = cand["h_over_x"].between(0, 1, inclusive="neither")
    cand["scale_positive_flag"] = cand["scale_ratio"].replace([np.inf, -np.inf], np.nan).gt(0)
    cand["geometry_pass_flag"] = cand["pstar_comparable_flag"] & cand["h_short_flag"] & cand["scale_positive_flag"] & cand["scale_ratio"].lt(1)
    cand["x_precedes_J_flag"] = cand["finite_certificate_flag"] | cand["right_endpoint_control_flag"] | cand["containing_block_control_flag"]
    cand["control_relation_flag"] = (
        cand["covered_flag"]
        & cand["x_precedes_J_flag"]
        & cand["geometry_pass_flag"]
        & cand["scale_compatibility_ok"].fillna(False)
    ) | cand["finite_certificate_flag"]

    # Block family B.
    theta_blocks = windows.copy()
    theta_blocks["block_family_id"] = theta_blocks.apply(
        lambda r: f"theta_local:{int(r['block_id'])}:{int(float(r['y']))}:{int(float(r['h']))}", axis=1
    )
    theta_blocks["right_endpoint"] = theta_blocks["y"] + theta_blocks["h"]
    theta_blocks["E_theta"] = theta_blocks["E_theta_local"]
    theta_blocks["E_theta_sign"] = theta_blocks["side"] if "side" in theta_blocks.columns else theta_blocks["local_theta_sign"]
    theta_blocks["Q_R2Q"] = theta_blocks["Q_R2Q"]
    theta_blocks["repayment_compatible_flag"] = theta_blocks["negative_transfer_flag"] | theta_blocks["positive_harmless_flag"]
    theta_blocks["endpoint_orientation"] = theta_blocks["side"] if "side" in theta_blocks.columns else theta_blocks["local_theta_sign"]
    theta_blocks["partial_interval_allowed"] = False
    theta_blocks["post_P0_block_flag"] = theta_blocks["p_star"].ge(P0)

    b3_blocks = []
    if len(b3):
        for _, r in b3[b3.get("candidate_crossing", pd.Series(False, index=b3.index)).fillna(False)].iterrows():
            y = float(r.get("start_prime", np.nan))
            x = float(r.get("worst_prime", np.nan))
            h = max(1.0, x - y) if pd.notna(x) and pd.notna(y) else np.nan
            b3_blocks.append(
                {
                    "block_family_id": f"B3_tail:{int(r['block_id'])}:{int(y) if pd.notna(y) else 0}:{int(h) if pd.notna(h) else 0}",
                    "block_id": int(r["block_id"]),
                    "y": y,
                    "h": h,
                    "right_endpoint": x,
                    "p_star": float(r["p_star"]),
                    "E_theta": np.nan,
                    "E_theta_sign": "negative",
                    "Q_R2Q": float(r.get("Q_tail_max_inside", np.nan)),
                    "B2_active_flag": bool(r.get("covered_by_block_or_certificate", False)),
                    "repayment_compatible_flag": bool(r.get("B3_block_pass", False)),
                    "endpoint_orientation": "negative",
                    "partial_interval_allowed": True,
                    "post_P0_block_flag": bool(float(r["p_star"]) >= P0),
                }
            )
    b3_blocks_df = pd.DataFrame(b3_blocks)

    block_cols = [
        "block_family_id",
        "block_id",
        "y",
        "h",
        "right_endpoint",
        "p_star",
        "E_theta",
        "E_theta_sign",
        "Q_R2Q",
        "B2_active_flag",
        "repayment_compatible_flag",
        "endpoint_orientation",
        "partial_interval_allowed",
        "post_P0_block_flag",
    ]
    for c in block_cols:
        if c not in theta_blocks.columns:
            theta_blocks[c] = np.nan
        if len(b3_blocks_df) and c not in b3_blocks_df.columns:
            b3_blocks_df[c] = np.nan
    blocks = pd.concat([theta_blocks[block_cols], b3_blocks_df[block_cols] if len(b3_blocks_df) else pd.DataFrame(columns=block_cols)], ignore_index=True)

    selection_cols = [
        "candidate_id",
        "x",
        "selected_block_id",
        "control_type",
        "right_endpoint_control_flag",
        "containing_block_control_flag",
        "partial_interval_used_flag",
        "x_precedes_J_flag",
        "scale_ratio",
        "pstar_over_x",
        "h_over_x",
        "status",
    ]
    selection = cand[selection_cols].copy()

    geometry_cols = [
        "candidate_id",
        "x",
        "selected_block_id",
        "p_star",
        "h",
        "pstar_over_x",
        "h_over_x",
        "scale_ratio",
        "pstar_comparable_flag",
        "h_short_flag",
        "scale_positive_flag",
        "geometry_pass_flag",
    ]
    geometry = cand[geometry_cols].copy()

    # Failure export.
    failures: list[dict[str, object]] = []
    for _, r in cand.iterrows():
        if not bool(r["covered_flag"]):
            add_failure(failures, r, "uncovered_candidate", "candidate has no selected covered block")
        if not r["selected_block_id"]:
            add_failure(failures, r, "missing_selected_block", "selected_block_id is empty")
        if pd.isna(r["p_star"]):
            add_failure(failures, r, "missing_p_star", "p_star is missing")
        elif float(r["p_star"]) <= 1:
            add_failure(failures, r, "bad_p_star", "p_star <= 1")
        if pd.isna(r["h"]):
            add_failure(failures, r, "missing_h", "h is missing")
        elif float(r["h"]) <= 0:
            add_failure(failures, r, "bad_h", "h <= 0")
        if not bool(r["scale_positive_flag"]):
            add_failure(failures, r, "scale_ratio_invalid", "scale ratio is not positive finite")
        if not bool(r["pstar_comparable_flag"]):
            add_failure(failures, r, "pstar_not_comparable", "pstar_over_x outside guardrail")
        if not bool(r["h_short_flag"]):
            add_failure(failures, r, "h_not_short", "h_over_x outside guardrail")
        if not bool(r["x_precedes_J_flag"]):
            add_failure(failures, r, "control_relation_false", "x does not satisfy x preceq J")
        if not bool(r["control_relation_flag"]):
            add_failure(failures, r, "control_relation_false", "full control relation failed")
        if pd.isna(r.get("side", np.nan)):
            add_failure(failures, r, "endpoint_orientation_missing", "side/orientation missing")
        if bool(r.get("post_P0_flag", False)) and r.get("side") == "negative" and not bool(r.get("O2_B3_repaid_flag", False)):
            add_failure(failures, r, "O2_B3_import_missing", "post-P0 negative row missing O2/B3 import")

    failures_df = pd.DataFrame(failures)

    coverage_failures = int((~cand["covered_flag"]).sum())
    compatibility_failures = int((~cand["control_relation_flag"]).sum())
    geometry_failures = int((~cand["geometry_pass_flag"]).sum())
    post_P0_failures = int(failures_df["post_P0_flag"].sum()) if len(failures_df) else 0

    post = cand[cand["post_P0_flag"]]
    summary = {
        "rows": int(len(cand)),
        "post_P0_rows": int(len(post)),
        "candidate_rows": int(len(cand)),
        "block_rows": int(len(blocks)),
        "selection_rows": int(len(selection)),
        "pstar_over_x_min": float(cand["pstar_over_x"].min()),
        "pstar_over_x_max": float(cand["pstar_over_x"].max()),
        "pstar_over_x_mean": float(cand["pstar_over_x"].mean()),
        "h_over_x_min": float(cand["h_over_x"].min()),
        "h_over_x_max": float(cand["h_over_x"].max()),
        "h_over_x_mean": float(cand["h_over_x"].mean()),
        "scale_ratio_min": float(cand["scale_ratio"].min()),
        "scale_ratio_max": float(cand["scale_ratio"].max()),
        "scale_ratio_mean": float(cand["scale_ratio"].mean()),
        "scale_ratio_q95": q(cand["scale_ratio"], 0.95),
        "scale_ratio_q99": q(cand["scale_ratio"], 0.99),
        "post_P0_pstar_over_x_min": float(post["pstar_over_x"].min()) if len(post) else np.nan,
        "post_P0_pstar_over_x_max": float(post["pstar_over_x"].max()) if len(post) else np.nan,
        "post_P0_h_over_x_max": float(post["h_over_x"].max()) if len(post) else np.nan,
        "post_P0_scale_ratio_max": float(post["scale_ratio"].max()) if len(post) else np.nan,
        "coverage_failures": coverage_failures,
        "compatibility_failures": compatibility_failures,
        "geometry_failures": geometry_failures,
        "post_P0_failures": post_P0_failures,
        "pass_blocksystem_definition_empirical": bool(
            coverage_failures == 0
            and compatibility_failures == 0
            and geometry_failures == 0
            and post_P0_failures == 0
        ),
    }

    candidates_out = cand[
        [
            "candidate_id",
            "x",
            "source",
            "theta_candidate_flag",
            "B3_candidate_flag",
            "post_P0_flag",
            "finite_certificate_flag",
            "selected_block_id",
            "covered_flag",
            "control_relation_flag",
            "status",
        ]
    ].copy()

    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)
    candidates_out.to_csv(CANDIDATES_OUT, index=False)
    blocks.to_csv(BLOCKS_OUT, index=False)
    selection.to_csv(SELECTION_OUT, index=False)
    geometry.to_csv(GEOMETRY_OUT, index=False)
    failures_df.to_csv(FAILURES_OUT, index=False)
    write_doc(summary, failures_df)
    refresh_manifest()

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {CANDIDATES_OUT}")
    log(f"Wrote {BLOCKS_OUT}")
    log(f"Wrote {SELECTION_OUT}")
    log(f"Wrote {GEOMETRY_OUT}")
    log(f"Wrote {FAILURES_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k, v in summary.items():
        log(f"{k} = {v}")


if __name__ == "__main__":
    main()
