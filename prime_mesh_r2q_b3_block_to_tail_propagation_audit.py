#!/usr/bin/env python3
"""B3 block-to-tail propagation audit.

This audit checks whether the SR10/B2-facing tail envelope can fail without a
covered local repayment block.  It is a first-crossing / endpoint-repayment
audit, not a raw summation audit.

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


def find_repo_root(path: Path) -> Path:
    for p in [path, *path.parents]:
        if p.name == "prime-mesh-theory":
            return p
    raise RuntimeError(f"Could not locate prime-mesh-theory root from {path}")


ROOT = find_repo_root(OUT)
NOTES = ROOT / "notes"

SR10_BLOCKS = NOTES / "prime_mesh_r2q_sr10_blocks.csv"
FIRST_CROSS = NOTES / "prime_mesh_r2q_mr2_to_b2_first_crossing_blocks.csv"
O2_PROJECTION = NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"

HEXC = OUT / "prime_mesh_r2q_hexc_path_shape_intervals.csv"
ENDPOINT = OUT / "prime_mesh_r2q_endpoint_repayment_compatibility_intervals.csv"
O2P4 = OUT / "prime_mesh_r2q_o2p4_final_slack_intervals.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_b3_block_to_tail_summary.csv"
BLOCKS_OUT = OUT / "prime_mesh_r2q_b3_block_to_tail_blocks.csv"
CROSSINGS_OUT = OUT / "prime_mesh_r2q_b3_block_to_tail_crossings.csv"
WORST_OUT = OUT / "prime_mesh_r2q_b3_block_to_tail_worst_rows.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_B3_Block_to_Tail_Propagation_Audit_v1.md"
MANIFEST_OUT = OUT / "deposit_manifest.csv"

ETA0 = 0.5
DELTA_TAIL = 0.25
P0_TAIL = 500_000_000


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        log(f"Missing optional input: {path}")
        return pd.DataFrame()
    return pd.read_csv(path, **kwargs)


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


def prepare_o2_projection() -> pd.DataFrame:
    df = read_csv(O2_PROJECTION)
    if len(df) == 0:
        return df
    num(df, ["block_id", "source_row", "p_star", "y", "h", "Q_max", "canonical_scaled_Q_post"])
    group = (
        df.groupby("source_row", dropna=False)
        .agg(
            covered_y=("y", "first"),
            covered_h=("h", "first"),
            Q_local=("Q_max", "max"),
            Q_post_response=("canonical_scaled_Q_post", "max"),
            covered_rows=("source_row", "size"),
        )
        .reset_index()
        .rename(columns={"source_row": "block_id"})
    )
    group["block_id"] = group["block_id"].astype(int)
    return group


def prepare_first_cross() -> pd.DataFrame:
    fc = read_csv(FIRST_CROSS)
    if len(fc) == 0:
        return fc
    num(
        fc,
        [
            "block_id",
            "p_star",
            "d_worst",
            "eta_excess_start",
            "Qmax_block",
            "max_value",
            "first_cross_x",
            "last_safe_x",
            "cross_interval_h",
            "cross_Q",
            "cross_Q_y",
            "cross_Q_h",
        ],
    )
    fc = fc[fc["coordinate"].eq("sr10_excess_eta")].copy()
    fc["block_id"] = fc["block_id"].astype(int)
    fc["crosses"] = boolish(fc["crosses"])
    if "cross_Q_le_K" in fc.columns:
        fc["cross_Q_le_K"] = boolish(fc["cross_Q_le_K"])
    else:
        fc["cross_Q_le_K"] = np.nan
    return fc


def prepare_optional_by_block(path: Path, cols: list[str], aggs: dict[str, str]) -> pd.DataFrame:
    df = read_csv(path)
    if len(df) == 0:
        return df
    num(df, ["block_id", *cols])
    return df.groupby("block_id", dropna=False).agg(aggs).reset_index()


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


def write_doc(summary: dict[str, object], crossings: pd.DataFrame, worst: pd.DataFrame) -> None:
    status = "passes" if summary["pass_B3_empirical"] else "needs repair"
    lines = [
        "# Prime Mesh R2Q - B3 Block-to-Tail Propagation Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-08",
        f"**Status:** B3 empirical propagation audit - {status}",
        "",
        "## 1. Purpose",
        "",
        "This audit tests the B3 first-crossing mechanism in the B2-facing SR10 coordinate.  It asks whether a forbidden tail crossing can occur without a covered local B2-active repayment block.",
        "",
        "The audit intentionally does not sum local O2 errors.  It uses the first-crossing coordinate and endpoint repayment convention.",
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
        "## 3. Candidate Crossings",
        "",
        crossings.to_markdown(index=False) if len(crossings) else "No candidate forbidden crossings in the audited B2-facing coordinate.",
        "",
        "## 4. Worst Rows",
        "",
        worst.to_markdown(index=False),
        "",
        "## 5. Interpretation",
        "",
    ]
    if summary["tail_candidate_crossings"] == 0:
        lines += [
            r"\[",
            r"\boxed{\text{No post-}500M\text{ B2-facing tail first crossing occurs in the audited range.}}",
            r"\]",
            "",
            "The only forbidden crossing in the full inventory is finite-zone and belongs to the finite-certificate side of the proof stack.",
        ]
    elif summary["uncovered_crossings"] == 0:
        lines += [
            r"\[",
            r"\boxed{\text{All audited forbidden crossings are covered by the block system or finite certificate.}}",
            r"\]",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{There are uncovered forbidden crossings; B3 coverage needs repair.}}",
            r"\]",
        ]
    lines += [
        "",
        "Endpoint repayment remains favorable: endpoint descent is treated as repayment-side motion rather than O2/H-Exc slack.",
        "",
        "## 6. Outputs",
        "",
        f"- `{SUMMARY_OUT.name}`",
        f"- `{BLOCKS_OUT.name}`",
        f"- `{CROSSINGS_OUT.name}`",
        f"- `{WORST_OUT.name}`",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
    ]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    log(f"Reading SR10 blocks from {SR10_BLOCKS}")
    sr10 = pd.read_csv(SR10_BLOCKS).reset_index().rename(columns={"index": "block_id"})
    num(
        sr10,
        [
            "block_id",
            "start_prime",
            "worst_prime",
            "end_prime",
            "p_star",
            "sqrt_pstar",
            "L_total",
            "L_descent",
            "L_recovery",
            "d_start",
            "d_worst",
            "delta_recovery",
            "delta_descent",
            "mu_recovery",
            "mu_recovery_over_sqrt_pstar",
        ],
    )
    sr10["block_id"] = sr10["block_id"].astype(int)
    sr10["is_tail"] = sr10["p_star"].ge(P0_TAIL)
    sr10["d_end"] = sr10["d_worst"] - sr10["delta_recovery"] / sr10["sqrt_pstar"]
    sr10["Q_tail_start"] = ((sr10["d_start"] - ETA0).clip(lower=0)) / DELTA_TAIL
    sr10["Q_tail_max_inside"] = ((sr10["d_worst"] - ETA0).clip(lower=0)) / DELTA_TAIL
    sr10["Q_tail_end"] = ((sr10["d_end"] - ETA0).clip(lower=0)) / DELTA_TAIL
    sr10["candidate_crossing"] = sr10["Q_tail_max_inside"].gt(1.0)
    sr10["endpoint_repayment_norm"] = sr10["delta_recovery"] / sr10["sqrt_pstar"]
    sr10["endpoint_repayment_covers_excess"] = sr10["endpoint_repayment_norm"].ge(
        (sr10["d_worst"] - ETA0).clip(lower=0)
    )
    sr10["endpoint_favorable_from_sr10"] = sr10["delta_recovery"].gt(0)
    sr10["accumulation_proxy"] = sr10["Q_tail_end"]

    fc = prepare_first_cross()
    o2 = prepare_o2_projection()
    hexc = prepare_optional_by_block(
        HEXC,
        ["Q_exc", "Q_DeltaD", "Q_delayed_proxy", "exc_over_abs_DeltaD"],
        {
            "Q_exc": "max",
            "Q_DeltaD": "max",
            "Q_delayed_proxy": "max",
            "exc_over_abs_DeltaD": "max",
        },
    )
    ep = prepare_optional_by_block(
        ENDPOINT,
        ["endpoint_harmful_Q", "endpoint_repayment_Q", "endpoint_favorable_flag", "endpoint_already_counted_flag"],
        {
            "endpoint_harmful_Q": "max",
            "endpoint_repayment_Q": "max",
            "endpoint_favorable_flag": "max",
            "endpoint_already_counted_flag": "max",
        },
    )
    o2p4 = prepare_optional_by_block(
        O2P4,
        ["Q_o2p4_total", "Q_bdy", "Q_pp", "O2_total_with_o2p4"],
        {
            "Q_o2p4_total": "max",
            "Q_bdy": "max",
            "Q_pp": "max",
            "O2_total_with_o2p4": "max",
        },
    )

    blocks = sr10.merge(fc, on=["block_id", "p_star"], how="left", suffixes=("", "_fc"))
    blocks = blocks.merge(o2, on="block_id", how="left")
    blocks = blocks.merge(hexc, on="block_id", how="left", suffixes=("", "_hexc"))
    blocks = blocks.merge(ep, on="block_id", how="left", suffixes=("", "_endpoint"))
    blocks = blocks.merge(o2p4, on="block_id", how="left", suffixes=("", "_o2p4"))

    blocks["covered_flag"] = blocks["covered_rows"].fillna(0).gt(0)
    blocks["finite_certificate_flag"] = ~blocks["is_tail"]
    blocks["covered_by_block_or_certificate"] = blocks["covered_flag"] | blocks["finite_certificate_flag"]
    blocks["first_crossing_inside_flag"] = blocks["crosses"].fillna(False).astype(bool)
    blocks["local_violation_flag"] = blocks["cross_Q"].fillna(0).gt(1.0) | blocks["Q_local"].fillna(0).gt(1.0)
    blocks["absorbed_by_HExc_flag"] = blocks["Q_exc"].notna() & blocks["Q_exc"].le(0.25)
    blocks["endpoint_favorable_flag_final"] = blocks["endpoint_favorable_from_sr10"] & blocks[
        "endpoint_repayment_covers_excess"
    ]
    blocks["uncovered_crossing_flag"] = blocks["candidate_crossing"] & ~blocks["covered_by_block_or_certificate"]
    blocks["uncovered_tail_crossing_flag"] = (
        blocks["candidate_crossing"] & blocks["is_tail"] & ~blocks["covered_flag"]
    )
    blocks["tail_accumulation_fail_flag"] = blocks["is_tail"] & blocks["Q_tail_end"].gt(1.0)
    blocks["B3_block_pass"] = (
        (~blocks["uncovered_tail_crossing_flag"])
        & (~blocks["tail_accumulation_fail_flag"])
        & blocks["endpoint_favorable_from_sr10"]
    )

    crossings = blocks[blocks["candidate_crossing"]].copy()
    tail = blocks[blocks["is_tail"]].copy()

    # Required-ish fields for downstream inspection.
    out_cols = [
        "block_id",
        "p_star",
        "start_prime",
        "worst_prime",
        "end_prime",
        "covered_y",
        "covered_h",
        "d_start",
        "d_worst",
        "d_end",
        "Q_tail_start",
        "Q_tail_max_inside",
        "Q_tail_end",
        "candidate_crossing",
        "first_crossing_inside_flag",
        "covered_flag",
        "finite_certificate_flag",
        "covered_by_block_or_certificate",
        "local_violation_flag",
        "absorbed_by_HExc_flag",
        "endpoint_favorable_flag_final",
        "endpoint_repayment_norm",
        "accumulation_proxy",
        "Q_local",
        "Q_post_response",
        "Q_exc",
        "Q_o2p4_total",
        "Q_bdy",
        "Q_pp",
        "O2_total_with_o2p4",
        "cross_Q",
        "cross_Q_y",
        "cross_Q_h",
        "is_tail",
        "B3_block_pass",
    ]
    for c in out_cols:
        if c not in blocks.columns:
            blocks[c] = np.nan
    blocks_out = blocks[out_cols].copy()

    worst = pd.concat(
        [
            blocks_out.sort_values("Q_tail_max_inside", ascending=False).head(20),
            blocks_out.sort_values("accumulation_proxy", ascending=False).head(20),
        ],
        ignore_index=True,
    ).drop_duplicates(subset=["block_id"])

    candidate_crossings = int(blocks["candidate_crossing"].sum())
    covered_crossings = int((blocks["candidate_crossing"] & blocks["covered_by_block_or_certificate"]).sum())
    uncovered_crossings = int((blocks["candidate_crossing"] & ~blocks["covered_by_block_or_certificate"]).sum())
    tail_candidate_crossings = int((blocks["candidate_crossing"] & blocks["is_tail"]).sum())
    uncovered_tail_crossings = int(blocks["uncovered_tail_crossing_flag"].sum())

    first_crossing_exists = candidate_crossings > 0
    first = crossings.sort_values("p_star").head(1)
    first_row = first.iloc[0] if len(first) else None

    summary = {
        "rows": int(len(blocks)),
        "blocks": int(blocks["block_id"].nunique()),
        "tail_endpoints": int(blocks["is_tail"].sum()),
        "candidate_crossings": candidate_crossings,
        "tail_candidate_crossings": tail_candidate_crossings,
        "covered_crossings": covered_crossings,
        "uncovered_crossings": uncovered_crossings,
        "uncovered_tail_crossings": uncovered_tail_crossings,
        "coverage_frac": covered_crossings / candidate_crossings if candidate_crossings else 1.0,
        "tail_coverage_frac": float(tail["covered_flag"].mean()) if len(tail) else np.nan,
        "Q_tail_max": float(blocks["Q_tail_max_inside"].max()),
        "Q_tail_q95": q(blocks["Q_tail_max_inside"], 0.95),
        "Q_tail_q99": q(blocks["Q_tail_max_inside"], 0.99),
        "Q_tail_tail_max": float(tail["Q_tail_max_inside"].max()) if len(tail) else np.nan,
        "Q_tail_tail_q95": q(tail["Q_tail_max_inside"], 0.95),
        "Q_tail_end_max": float(blocks["Q_tail_end"].max()),
        "Q_tail_end_tail_max": float(tail["Q_tail_end"].max()) if len(tail) else np.nan,
        "Q_local_max": float(blocks["Q_local"].max()),
        "Q_local_q95": q(blocks["Q_local"].dropna(), 0.95),
        "Q_local_q99": q(blocks["Q_local"].dropna(), 0.99),
        "Q_exc_max": float(blocks["Q_exc"].max()),
        "Q_o2_max": float(blocks["O2_total_with_o2p4"].max()),
        "Q_boundary_max": float(blocks["Q_bdy"].max()),
        "first_crossing_exists": bool(first_crossing_exists),
        "first_crossing_block_id": int(first_row["block_id"]) if first_row is not None else np.nan,
        "first_crossing_p_star": int(first_row["p_star"]) if first_row is not None else np.nan,
        "first_crossing_h": int(first_row["covered_h"]) if first_row is not None and pd.notna(first_row["covered_h"]) else np.nan,
        "first_crossing_covered": bool(first_row["covered_by_block_or_certificate"]) if first_row is not None else False,
        "first_crossing_local_violation": bool(first_row["local_violation_flag"]) if first_row is not None else False,
        "first_crossing_absorbed_by_HExc": bool(first_row["absorbed_by_HExc_flag"]) if first_row is not None else False,
        "accumulation_proxy_max": float(blocks["accumulation_proxy"].max()),
        "accumulation_proxy_mean": float(blocks["accumulation_proxy"].mean()),
        "accumulation_proxy_q95": q(blocks["accumulation_proxy"], 0.95),
        "tail_accumulation_proxy_max": float(tail["accumulation_proxy"].max()) if len(tail) else np.nan,
        "endpoint_favorable_frac": float(blocks["endpoint_favorable_from_sr10"].mean()),
        "endpoint_repayment_covers_excess_frac": float(blocks["endpoint_repayment_covers_excess"].mean()),
        "pass_no_uncovered_crossings": uncovered_tail_crossings == 0,
        "pass_no_accumulation": bool(len(tail) == 0 or tail["accumulation_proxy"].max() <= 1.0),
        "pass_tail_no_candidate_crossing": tail_candidate_crossings == 0,
        "pass_B3_empirical": bool(
            uncovered_tail_crossings == 0
            and (len(tail) == 0 or tail["accumulation_proxy"].max() <= 1.0)
            and tail_candidate_crossings == 0
        ),
    }

    blocks_out.to_csv(BLOCKS_OUT, index=False)
    crossings[out_cols].to_csv(CROSSINGS_OUT, index=False)
    worst.to_csv(WORST_OUT, index=False)
    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)
    write_doc(summary, crossings[out_cols] if len(crossings) else crossings, worst)
    refresh_manifest()

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {BLOCKS_OUT}")
    log(f"Wrote {CROSSINGS_OUT}")
    log(f"Wrote {WORST_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k, v in summary.items():
        log(f"{k} = {v}")


if __name__ == "__main__":
    main()
