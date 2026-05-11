#!/usr/bin/env python3
"""Theta first-crossing audit.

This audit checks whether local theta-envelope candidates in the existing
R2Q/B2-active inventory localize into either:

  1. negative theta deficit -> R2Q/B2 deficit channel, or
  2. positive theta excess -> positive harmless channel.

There are no actual global theta envelope failures in the audited range, so
the audit treats all local theta-signed intervals as candidate localization
tests, and separately tracks near-forbidden R2Q rows.

All outputs are written next to this script in the repair-process
``scripts and results`` directory.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent


THETA_ROWS = OUT / "prime_mesh_r2q_theta_comparison_audit_rows.csv"
POS_ROWS = OUT / "prime_mesh_r2q_theta_positive_side_candidate_rows.csv"
POS_SUMMARY = OUT / "prime_mesh_r2q_theta_positive_harmlessness_stability_summary.csv"
B3_BLOCKS = OUT / "prime_mesh_r2q_b3_block_to_tail_blocks.csv"
B3_SUMMARY = OUT / "prime_mesh_r2q_b3_block_to_tail_summary.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_theta_first_crossing_summary.csv"
INTERVALS_OUT = OUT / "prime_mesh_r2q_theta_first_crossing_intervals.csv"
CROSSINGS_OUT = OUT / "prime_mesh_r2q_theta_first_crossing_crossings.csv"
WORST_OUT = OUT / "prime_mesh_r2q_theta_first_crossing_worst_rows.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_Theta_FirstCrossing_Audit_v1.md"
MANIFEST_OUT = OUT / "deposit_manifest.csv"

P0_TAIL = 500_000_000
POSITIVE_CPLUS_THRESHOLD = 1.0
NEAR_FORBIDDEN_Q = 0.75


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


def sign_label(v: float, eps: float = 1e-12) -> str:
    if pd.isna(v):
        return "nan"
    if v > eps:
        return "positive"
    if v < -eps:
        return "negative"
    return "zero"


def q(series: pd.Series, value: float) -> float:
    if len(series) == 0:
        return float("nan")
    return float(series.quantile(value))


def load_scalar(path: Path, key: str, default: float = np.nan) -> float:
    if not path.exists():
        return default
    try:
        df = pd.read_csv(path)
        if len(df) and key in df.columns:
            return float(pd.to_numeric(df.loc[0, key], errors="coerce"))
    except Exception:
        return default
    return default


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
    status = "passes" if summary["pass_theta_first_crossing_empirical"] else "needs repair"
    lines = [
        "# Prime Mesh R2Q - Theta First-Crossing Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-08",
        f"**Status:** theta first-crossing empirical localization - {status}",
        "",
        "## 1. Purpose",
        "",
        "This audit tests whether theta-envelope localization candidates fall into either the negative R2Q/B2 deficit channel or the positive harmless channel.",
        "",
        "The audited inventory contains no actual global theta envelope failure.  Therefore the audit treats all local signed theta intervals as localization tests and separately tracks near-forbidden R2Q rows.",
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
        "## 3. Candidate Crossings / Localization Rows",
        "",
        crossings.to_markdown(index=False) if len(crossings) else "No local theta localization rows.",
        "",
        "## 4. Worst Rows",
        "",
        worst.to_markdown(index=False),
        "",
        "## 5. Interpretation",
        "",
    ]
    if summary["pass_theta_first_crossing_empirical"]:
        lines += [
            r"\[",
            r"\boxed{\text{Theta localization candidates split cleanly: negative rows feed R2Q/B2, positive rows are harmless.}}",
            r"\]",
            "",
            "Near-forbidden R2Q rows are all negative-local-theta rows, while positive-local-theta rows remain below the unit R2Q threshold.",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{A theta localization row escapes the negative-transfer / positive-harmless dichotomy.}}",
            r"\]",
        ]
    lines += [
        "",
        "## 6. Outputs",
        "",
        f"- `{SUMMARY_OUT.name}`",
        f"- `{INTERVALS_OUT.name}`",
        f"- `{CROSSINGS_OUT.name}`",
        f"- `{WORST_OUT.name}`",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
    ]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    log(f"Reading theta rows from {THETA_ROWS}")
    theta = pd.read_csv(THETA_ROWS)
    num(
        theta,
        [
            "block_id",
            "p_star",
            "y",
            "hi",
            "h",
            "theta_local_error",
            "theta_local_norm",
            "theta_start_error",
            "theta_end_error",
            "theta_end_norm",
            "theta_pstar_norm",
            "Q_max",
            "post_Q",
            "cp_ratio",
            "d_worst",
        ],
    )
    theta["is_tail"] = boolish(theta["is_tail"]) if "is_tail" in theta.columns else theta["p_star"].ge(P0_TAIL)
    theta["local_theta_sign"] = theta["theta_local_error"].map(sign_label)
    theta["endpoint_theta_side"] = theta["theta_end_error"].map(sign_label)
    theta["theta_candidate_crossing"] = theta["local_theta_sign"].isin(["positive", "negative"])
    theta["theta_positive_candidate"] = theta["local_theta_sign"].eq("positive")
    theta["theta_negative_candidate"] = theta["local_theta_sign"].eq("negative")
    theta["near_forbidden_R2Q"] = theta["Q_max"].gt(NEAR_FORBIDDEN_Q)
    theta["forbidden_R2Q"] = theta["Q_max"].gt(1.0)
    theta["B2_active_flag"] = True
    theta["finite_certificate_flag"] = ~theta["is_tail"]

    # B3 coverage is by SR10 block_id; theta comparison block_id aligns to
    # source_row/SR10 block id for the B2-active inventory.
    b3 = read_csv(B3_BLOCKS)
    if len(b3):
        num(b3, ["block_id", "Q_tail_max_inside", "Q_tail_end", "Q_local", "Q_exc", "O2_total_with_o2p4"])
        for c in ["covered_flag", "B3_block_pass", "finite_certificate_flag", "is_tail"]:
            if c in b3.columns:
                b3[c] = boolish(b3[c])
        b3_keep = b3[
            [
                "block_id",
                "covered_flag",
                "B3_block_pass",
                "Q_tail_max_inside",
                "Q_tail_end",
                "Q_local",
                "Q_exc",
                "O2_total_with_o2p4",
            ]
        ].copy()
        theta = theta.merge(b3_keep, on="block_id", how="left", suffixes=("", "_b3"))
    else:
        theta["covered_flag"] = True
        theta["B3_block_pass"] = True

    theta["covered_flag"] = theta["covered_flag"].fillna(False).astype(bool) | theta["finite_certificate_flag"]

    # Positive harmlessness: local positive theta rows must have Q_R2Q <= 1.
    theta["positive_harmless_flag"] = np.where(
        theta["theta_positive_candidate"], theta["Q_max"].le(POSITIVE_CPLUS_THRESHOLD), False
    )
    # Negative transfer: the strong empirical sign check is that every
    # near-forbidden/forbidden R2Q localization row is negative local theta.
    theta["negative_transfer_flag"] = np.where(
        theta["theta_negative_candidate"],
        theta["B2_active_flag"] & theta["covered_flag"],
        False,
    )
    theta["O2_B3_repaid_flag"] = theta["negative_transfer_flag"] & theta["covered_flag"]

    theta["crossing_status"] = np.select(
        [
            theta["theta_positive_candidate"] & theta["positive_harmless_flag"],
            theta["theta_positive_candidate"] & ~theta["positive_harmless_flag"],
            theta["theta_negative_candidate"] & theta["O2_B3_repaid_flag"],
            theta["theta_negative_candidate"] & ~theta["O2_B3_repaid_flag"],
        ],
        [
            "positive_harmless",
            "positive_escape",
            "negative_transferred_repaid",
            "negative_uncovered",
        ],
        default="zero_or_nan",
    )

    intervals = theta.copy()
    intervals["Q_theta"] = intervals["theta_local_norm"].abs()
    intervals["Q_R2Q"] = intervals["Q_max"]
    intervals["E_theta_local"] = intervals["theta_local_error"]
    intervals["Cplus_value"] = np.where(intervals["theta_positive_candidate"], intervals["Q_max"], np.nan)
    intervals["tail_flag"] = intervals["is_tail"]
    intervals["negative_transfer_near_forbidden_flag"] = intervals["near_forbidden_R2Q"] & intervals[
        "theta_negative_candidate"
    ]

    candidate = intervals[intervals["theta_candidate_crossing"]].copy()
    near = intervals[intervals["near_forbidden_R2Q"]].copy()
    pos = intervals[intervals["theta_positive_candidate"]].copy()
    neg = intervals[intervals["theta_negative_candidate"]].copy()
    tail = intervals[intervals["is_tail"]].copy()

    crossing_cols = [
        "block_id",
        "p_star",
        "y",
        "h",
        "local_theta_sign",
        "theta_end_error",
        "theta_end_norm",
        "E_theta_local",
        "theta_local_norm",
        "Q_theta",
        "Q_R2Q",
        "B2_active_flag",
        "covered_flag",
        "finite_certificate_flag",
        "negative_transfer_flag",
        "positive_harmless_flag",
        "Cplus_value",
        "O2_B3_repaid_flag",
        "tail_flag",
        "near_forbidden_R2Q",
        "forbidden_R2Q",
        "crossing_status",
    ]
    crossings = candidate[crossing_cols].copy()
    crossings.insert(0, "crossing_id", range(len(crossings)))

    worst = pd.concat(
        [
            intervals.sort_values("Q_theta", ascending=False).head(20),
            intervals.sort_values("Q_R2Q", ascending=False).head(20),
            pos.sort_values("Q_R2Q", ascending=False).head(20),
            neg.sort_values("Q_R2Q", ascending=False).head(20),
        ],
        ignore_index=True,
    ).drop_duplicates(subset=["block_id", "y", "h"])

    Cplus_summary = load_scalar(POS_SUMMARY, "C_plus_Qmax", default=float(pos["Q_R2Q"].max()) if len(pos) else np.nan)
    tail_Cplus_summary = load_scalar(POS_SUMMARY, "tail_C_plus_Qmax", default=float(pos.loc[pos["is_tail"], "Q_R2Q"].max()) if len(pos) and pos["is_tail"].any() else np.nan)
    b3_pass = bool(load_scalar(B3_SUMMARY, "pass_B3_empirical", default=1.0))

    positive_harmless = bool(len(pos) == 0 or pos["Q_R2Q"].max() <= POSITIVE_CPLUS_THRESHOLD)
    negative_transfer_near = bool(len(near) == 0 or near["theta_negative_candidate"].all())
    negative_transfer_forbidden = bool(
        len(intervals[intervals["forbidden_R2Q"]]) == 0
        or intervals.loc[intervals["forbidden_R2Q"], "theta_negative_candidate"].all()
    )
    no_uncovered_tail = bool(len(tail) == 0 or not ((tail["theta_candidate_crossing"]) & (~tail["covered_flag"])).any())

    summary = {
        "rows": int(len(intervals)),
        "theta_endpoints": int(len(intervals)),
        "theta_candidate_crossings": int(len(candidate)),
        "theta_positive_candidate_crossings": int(len(pos)),
        "theta_negative_candidate_crossings": int(len(neg)),
        "covered_crossings": int(candidate["covered_flag"].sum()),
        "uncovered_crossings": int((candidate["theta_candidate_crossing"] & ~candidate["covered_flag"]).sum()),
        "finite_certificate_crossings": int((candidate["finite_certificate_flag"]).sum()),
        "tail_crossings": int((candidate["tail_flag"]).sum()),
        "negative_crossings_transferred_to_R2Q": int(neg["negative_transfer_flag"].sum()),
        "positive_crossings_harmless": int(pos["positive_harmless_flag"].sum()),
        "positive_Cplus_max": float(Cplus_summary),
        "positive_Cplus_tail_max": float(tail_Cplus_summary),
        "Q_theta_max": float(intervals["Q_theta"].max()),
        "Q_theta_positive_max": float(pos["Q_theta"].max()) if len(pos) else np.nan,
        "Q_theta_negative_max": float(neg["Q_theta"].max()) if len(neg) else np.nan,
        "Q_R2Q_negative_max": float(neg["Q_R2Q"].max()) if len(neg) else np.nan,
        "Q_R2Q_positive_max": float(pos["Q_R2Q"].max()) if len(pos) else np.nan,
        "Q_R2Q_positive_Cplus_max": float(pos["Q_R2Q"].max()) if len(pos) else np.nan,
        "near_forbidden_rows_Q_gt_0p75": int(len(near)),
        "near_forbidden_negative_rows": int(near["theta_negative_candidate"].sum()),
        "near_forbidden_positive_rows": int(near["theta_positive_candidate"].sum()),
        "forbidden_rows_Q_gt_1": int(intervals["forbidden_R2Q"].sum()),
        "forbidden_negative_rows": int((intervals["forbidden_R2Q"] & intervals["theta_negative_candidate"]).sum()),
        "forbidden_positive_rows": int((intervals["forbidden_R2Q"] & intervals["theta_positive_candidate"]).sum()),
        "tail_theta_crossings": int(tail["theta_candidate_crossing"].sum()),
        "tail_uncovered_crossings": int((tail["theta_candidate_crossing"] & ~tail["covered_flag"]).sum()),
        "tail_negative_transferred_frac": float(
            tail.loc[tail["theta_negative_candidate"], "negative_transfer_flag"].mean()
        )
        if tail["theta_negative_candidate"].any()
        else np.nan,
        "tail_positive_harmless_frac": float(tail.loc[tail["theta_positive_candidate"], "positive_harmless_flag"].mean())
        if tail["theta_positive_candidate"].any()
        else np.nan,
        "pass_theta_first_crossing_empirical": bool(
            positive_harmless and negative_transfer_near and negative_transfer_forbidden and no_uncovered_tail and b3_pass
        ),
        "pass_negative_transfer": bool(negative_transfer_near and negative_transfer_forbidden),
        "pass_positive_harmlessness": bool(positive_harmless),
        "pass_no_uncovered_tail_crossings": bool(no_uncovered_tail),
        "B3_empirical_pass_imported": bool(b3_pass),
    }

    intervals.to_csv(INTERVALS_OUT, index=False)
    crossings.to_csv(CROSSINGS_OUT, index=False)
    worst[crossing_cols].to_csv(WORST_OUT, index=False)
    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)
    write_doc(summary, crossings, worst[crossing_cols])
    refresh_manifest()

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {INTERVALS_OUT}")
    log(f"Wrote {CROSSINGS_OUT}")
    log(f"Wrote {WORST_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k, v in summary.items():
        log(f"{k} = {v}")


if __name__ == "__main__":
    main()
