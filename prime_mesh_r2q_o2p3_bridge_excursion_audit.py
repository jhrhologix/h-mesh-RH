#!/usr/bin/env python3
"""O2.3 bridge-excursion audit for LongA/B2-active intervals.

This audit measures the bridge excursion in the same SR11/O2 coordinate used by
the recovery-block inventory.  The SR11 realpath sample table stores D_y and
D_{y+h} values for many sampled offsets h.  For each LongA interval J=[y,y+h],
we collect all sampled offsets with the same (block_id, y) and 0 <= offset <= h,
add the interval endpoint, and compute the maximal sampled deviation from the
endpoint interpolation line.

Important: this is a sampled-path audit, not a proof of the continuous/integer
supremum over every t in J.  It is the correct coordinate audit for O2.3 because
it uses the same bridge coordinate as the SR11/O2 recovery stack.
"""

from __future__ import annotations

import math
import shutil
import time
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
DOCS = ROOT / "docs" / "RH" / "notes"
REPAIR = DOCS / "claude" / "repair and close process" / "scripts and results"

INPUT = NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"
SAMPLES = NOTES / "sr11_realpath_pstar" / "prime_mesh_r2q_sr11_realpath_noise_samples.csv"
if not SAMPLES.exists():
    SAMPLES = NOTES / "prime_mesh_r2q_sr11_realpath_noise_samples.csv"

SUMMARY_OUT = NOTES / "prime_mesh_r2q_o2p3_bridge_excursion_summary.csv"
INTERVALS_OUT = NOTES / "prime_mesh_r2q_o2p3_bridge_excursion_intervals.csv"
SCOPES_OUT = NOTES / "prime_mesh_r2q_o2p3_bridge_excursion_scopes.csv"
WORST_PATHS_OUT = NOTES / "prime_mesh_r2q_o2p3_bridge_excursion_worst_paths.csv"
DOC_OUT = DOCS / "Prime_Mesh_R2Q_O2p3_Bridge_Excursion_Audit_v1.md"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def h_bin(h: float) -> str:
    if h <= 4:
        return "h<=4"
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


def p_scale_bin(p: float) -> str:
    if p < 100_000_000:
        return "p<100M"
    if p < 500_000_000:
        return "100M<=p<500M"
    return "p>=500M"


def shell_pattern(row: pd.Series) -> str:
    bits: list[str] = []
    for j in range(5):
        v = row.get(f"shell_sym_all_{j}", np.nan)
        if pd.isna(v):
            bits.append("?")
        elif abs(float(v)) <= 1e-12:
            bits.append("0")
        else:
            bits.append("1")
    return "".join(bits)


def summarize(df: pd.DataFrame, scope: str) -> dict[str, object]:
    worst_idx = df["Q_delayed_proxy"].idxmax()
    worst = df.loc[worst_idx]
    return {
        "scope": scope,
        "rows": int(len(df)),
        "Q_exc_max": float(df["Q_exc"].max()),
        "Q_exc_mean": float(df["Q_exc"].mean()),
        "Q_exc_median": float(df["Q_exc"].median()),
        "Q_exc_q95": float(df["Q_exc"].quantile(0.95)),
        "Q_exc_q99": float(df["Q_exc"].quantile(0.99)),
        "Q_DeltaD_max": float(df["Q_DeltaD"].max()),
        "Q_DeltaD_mean": float(df["Q_DeltaD"].mean()),
        "Q_DeltaD_median": float(df["Q_DeltaD"].median()),
        "Q_DeltaD_q95": float(df["Q_DeltaD"].quantile(0.95)),
        "Q_DeltaD_q99": float(df["Q_DeltaD"].quantile(0.99)),
        "Q_DeltaD_log1_max": float(df["Q_DeltaD_log1"].max()),
        "Q_delayed_proxy_max": float(df["Q_delayed_proxy"].max()),
        "Q_delayed_proxy_mean": float(df["Q_delayed_proxy"].mean()),
        "Q_delayed_proxy_q95": float(df["Q_delayed_proxy"].quantile(0.95)),
        "Q_delayed_proxy_q99": float(df["Q_delayed_proxy"].quantile(0.99)),
        "sampled_points_min": int(df["sampled_points"].min()),
        "sampled_points_median": float(df["sampled_points"].median()),
        "sampled_points_max": int(df["sampled_points"].max()),
        "pass_Q_exc_le_0p05_frac": float((df["Q_exc"] <= 0.05).mean()),
        "pass_Q_exc_le_0p10_frac": float((df["Q_exc"] <= 0.10).mean()),
        "pass_Q_exc_le_0p25_frac": float((df["Q_exc"] <= 0.25).mean()),
        "pass_Q_exc_le_1_frac": float((df["Q_exc"] <= 1.0).mean()),
        "pass_Q_delayed_le_0p05_frac": float((df["Q_delayed_proxy"] <= 0.05).mean()),
        "pass_Q_delayed_le_0p10_frac": float((df["Q_delayed_proxy"] <= 0.10).mean()),
        "pass_Q_delayed_le_0p25_frac": float((df["Q_delayed_proxy"] <= 0.25).mean()),
        "pass_Q_delayed_le_1_frac": float((df["Q_delayed_proxy"] <= 1.0).mean()),
        "worst_block_id": int(worst["block_id"]),
        "worst_p_star": int(worst["p_star"]),
        "worst_h": int(worst["h"]),
    }


def collect_samples(long_a: pd.DataFrame) -> dict[tuple[int, int], pd.DataFrame]:
    wanted: dict[tuple[int, int], int] = {
        (int(r.block_id), int(r.y)): int(r.h) for r in long_a[["block_id", "y", "h"]].itertuples(index=False)
    }
    by_block: dict[int, set[int]] = {}
    for block_id, y in wanted:
        by_block.setdefault(block_id, set()).add(y)

    usecols = ["block_id", "y", "h", "D_y", "D_y_plus_h", "observed_delta"]
    kept: list[pd.DataFrame] = []
    log(f"Reading SR11 samples from {SAMPLES}")
    for chunk_idx, chunk in enumerate(pd.read_csv(SAMPLES, usecols=usecols, chunksize=250_000)):
        if chunk_idx % 20 == 0:
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
    all_samples = pd.concat(kept, ignore_index=True)
    result: dict[tuple[int, int], pd.DataFrame] = {}
    for key, part in all_samples.groupby(["block_id", "y"], sort=False):
        result[(int(key[0]), int(key[1]))] = part.sort_values("h")
    return result


def write_doc(summary: dict[str, object], scopes: pd.DataFrame, intervals: pd.DataFrame) -> None:
    if summary["Q_exc_max"] <= 0.05 and summary["Q_delayed_proxy_max"] > 1.0:
        status = "mixed: excursion very strong, endpoint proxy fails"
    elif summary["Q_exc_max"] <= 0.05 and summary["Q_delayed_proxy_max"] <= 0.10:
        status = "very strong"
    elif summary["Q_exc_max"] <= 0.10 and summary["Q_delayed_proxy_max"] <= 0.25:
        status = "strong"
    elif summary["Q_delayed_proxy_max"] < 1.0:
        status = "usable"
    else:
        status = "fail"

    lines = [
        "# Prime Mesh R2Q - O2.3 Bridge Excursion Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-07",
        f"**Status:** O2.3 sampled bridge-excursion audit - {status}",
        "",
        "## 1. Purpose",
        "",
        "This audit measures the bridge excursion in the SR11/O2 recovery coordinate over LongA/B2-active intervals.",
        "",
        r"\[",
        r"Q_{\rm exc}(J)=\frac{\sup_{t\in J}|D_N(t)-\ell_J(t)|}{\sqrt h\log^2p^*}.",
        r"\]",
        "",
        "The supremum here is over the sampled SR11 realpath points available for each interval, not every integer point.",
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
        "## 3. Scope Table",
        "",
        scopes.to_markdown(index=False),
        "",
        "## 4. Worst Intervals",
        "",
        intervals.sort_values("Q_delayed_proxy", ascending=False).head(20).to_markdown(index=False),
        "",
        "## 5. Interpretation",
        "",
    ]
    if status == "very strong":
        lines += [
            r"\[",
            r"\boxed{\text{O2.3 is empirically budget-closed on the sampled SR11 bridge path; analytic maximal-excursion proof still needed.}}",
            r"\]",
        ]
    elif status in {"strong", "usable"}:
        lines += [
            r"\[",
            r"\boxed{\text{O2.3 remains empirically safe on the sampled bridge path, but the delayed proxy is not tiny.}}",
            r"\]",
        ]
    elif status.startswith("mixed"):
        lines += [
            r"\[",
            r"\boxed{\text{The internal bridge excursion is very small, but }Q_{\Delta D}\text{ dominates the delayed proxy.}}",
            r"\]",
            "",
            "This means the sampled H-Exc component is budget-safe, while the companion endpoint term should not be treated as an internal-excursion failure.  The endpoint drop is the large recovery-block motion already visible in the R2Q/B2 descent inventory.",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{O2.3 is the dominant sampled O2 obstruction and needs sharper delayed-recovery control.}}",
            r"\]",
        ]
    lines += [
        "",
        "The audit is not a proof of H-Exc.  A proof still requires a deterministic bridge discrepancy theorem, arithmetic maximal inequality, or equivalent exact mesh identity.",
        "",
        "## 6. Coordinate Note",
        "",
        "A direct arithmetic reconstruction from `C_N E(n)-Lambda(n)` matches the SR11 `drift_term`, not the SR11 `D_y_plus_h-D_y` recovery coordinate.  This audit therefore uses the SR11 realpath sample coordinate directly.",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
    ]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    log(f"Reading {INPUT}")
    df = pd.read_csv(INPUT)
    for c in ["block_id", "p_star", "y", "h", "D_y", "D_y_plus_h", "observed_delta"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["shell_pattern"] = df.apply(shell_pattern, axis=1)
    long_a = df[df["shell_pattern"].eq("11111")].copy()
    long_a = long_a.sort_values(["p_star", "y", "h"]).reset_index(drop=True)
    log(f"LongA intervals: {len(long_a)}")

    samples = collect_samples(long_a)
    rows: list[dict[str, object]] = []
    worst_paths: list[pd.DataFrame] = []

    for idx, row in long_a.iterrows():
        block_id = int(row["block_id"])
        y = int(row["y"])
        h = int(row["h"])
        key = (block_id, y)
        part = samples.get(key, pd.DataFrame()).copy()
        d_start = float(row["D_y"])
        d_end = float(row["D_y_plus_h"])
        delta = float(row["observed_delta"])

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

        line = d_start + (offsets / h) * delta
        diff = values - line
        abs_diff = np.abs(diff)
        max_idx = int(abs_diff.argmax()) if len(abs_diff) else 0
        exc_abs = float(abs_diff[max_idx]) if len(abs_diff) else 0.0
        exc_signed = float(diff[max_idx]) if len(diff) else 0.0
        exc_t = int(y + offsets[max_idx])

        denom = math.sqrt(h) * (math.log(float(row["p_star"])) ** 2)
        denom_log1 = math.sqrt(h) * math.log(float(row["p_star"]))
        q_exc = exc_abs / denom if denom else np.nan
        q_delta = abs(delta) / denom if denom else np.nan
        q_delta_log1 = abs(delta) / denom_log1 if denom_log1 else np.nan
        q_delayed = q_exc + q_delta

        rec_pos = np.nan
        if "worst_prime" in row and "L_recovery" in row and float(row["L_recovery"]) != 0:
            rec_pos = (y - float(row["worst_prime"])) / float(row["L_recovery"])

        result = {
            "block_id": block_id,
            "p_star": int(row["p_star"]),
            "y": y,
            "h": h,
            "D_start": d_start,
            "D_end": d_end,
            "DeltaD": delta,
            "exc_abs": exc_abs,
            "exc_t": exc_t,
            "exc_signed": exc_signed,
            "Q_exc": q_exc,
            "Q_DeltaD": q_delta,
            "Q_DeltaD_log1": q_delta_log1,
            "Q_delayed_proxy": q_delayed,
            "sampled_points": int(len(offsets)),
            "sampled_offset_min": float(offsets.min()) if len(offsets) else np.nan,
            "sampled_offset_max": float(offsets.max()) if len(offsets) else np.nan,
            "is_tail": bool(row.get("is_tail", int(row["p_star"]) >= 500_000_000)),
            "h_bin": h_bin(h),
            "p_scale_bin": p_scale_bin(float(row["p_star"])),
            "mu_bin_if_available": row.get("mu_bin", ""),
            "depth_bin": row.get("depth_bin", ""),
            "recovery_position": rec_pos,
        }
        rows.append(result)

        path = pd.DataFrame(
            {
                "block_id": block_id,
                "p_star": int(row["p_star"]),
                "y": y,
                "h": h,
                "t": y + offsets.astype(int),
                "offset": offsets,
                "D_t": values,
                "line_t": line,
                "diff": diff,
                "abs_diff": abs_diff,
                "Q_delayed_proxy": q_delayed,
            }
        )
        worst_paths.append(path)

    out = pd.DataFrame(rows)
    out.to_csv(INTERVALS_OUT, index=False)

    scopes = [summarize(out, "global")]
    for label, part in [
        ("tail:p_star>=500M", out[out["is_tail"]]),
        ("tail:p_star<500M", out[~out["is_tail"]]),
        ("scale:p<100M", out[out["p_star"] < 100_000_000]),
        ("scale:100M<=p<500M", out[(out["p_star"] >= 100_000_000) & (out["p_star"] < 500_000_000)]),
        ("scale:p>=500M", out[out["p_star"] >= 500_000_000]),
    ]:
        if len(part):
            scopes.append(summarize(part, label))
    for col, prefix in [("h_bin", "h"), ("mu_bin_if_available", "mu"), ("depth_bin", "depth")]:
        for value, part in out.groupby(col, dropna=False):
            if len(part):
                scopes.append(summarize(part, f"{prefix}:{value}"))
    scopes_df = pd.DataFrame(scopes).sort_values(["Q_delayed_proxy_max", "rows"], ascending=[False, False])
    scopes_df.to_csv(SCOPES_OUT, index=False)

    worst_keys = set(
        tuple(x)
        for x in out.sort_values("Q_delayed_proxy", ascending=False)
        .head(20)[["block_id", "y", "h"]]
        .itertuples(index=False, name=None)
    )
    pd.concat(
        [p for p in worst_paths if (int(p["block_id"].iloc[0]), int(p["y"].iloc[0]), int(p["h"].iloc[0])) in worst_keys],
        ignore_index=True,
    ).to_csv(WORST_PATHS_OUT, index=False)

    worst = out.loc[out["Q_delayed_proxy"].idxmax()]
    summary = summarize(out, "global")
    summary.update(
        {
            "interval_rows": int(len(out)),
            "longA_rows": int(len(out)),
            "basis": "sym_all",
            "scope": "LongA/B2-active",
            "worst_y": int(worst["y"]),
            "worst_exc_abs": float(worst["exc_abs"]),
            "worst_DeltaD_abs": float(abs(worst["DeltaD"])),
            "worst_t_location": int(worst["exc_t"]),
            "sample_source": str(SAMPLES.relative_to(ROOT)),
        }
    )
    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)

    write_doc(summary, scopes_df, out)

    REPAIR.mkdir(parents=True, exist_ok=True)
    for path in [Path(__file__), SUMMARY_OUT, INTERVALS_OUT, SCOPES_OUT, WORST_PATHS_OUT, DOC_OUT]:
        shutil.copy2(path, REPAIR / path.name)
    manifest = pd.DataFrame(
        [
            {"Name": p.name, "Length": p.stat().st_size, "LastWriteTime": pd.Timestamp(p.stat().st_mtime, unit="s")}
            for p in sorted(REPAIR.iterdir())
            if p.is_file()
        ]
    )
    manifest.to_csv(REPAIR / "deposit_manifest.csv", index=False)

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {INTERVALS_OUT}")
    log(f"Wrote {SCOPES_OUT}")
    log(f"Wrote {WORST_PATHS_OUT}")
    log(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
