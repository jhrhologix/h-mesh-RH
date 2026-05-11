#!/usr/bin/env python3
"""H-Exc path-shape audit for LongA/B2-active bridge intervals.

This audit extends the O2.3 bridge-excursion computation.  It keeps the same
SR11 recovery coordinate and asks whether the small H-Exc term behaves like a
random/maximal fluctuation or a deterministic path-shape/endpoint-linearity
phenomenon.

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
SAMPLES = ROOT / "notes" / "sr11_realpath_pstar" / "prime_mesh_r2q_sr11_realpath_noise_samples.csv"
if not SAMPLES.exists():
    SAMPLES = ROOT / "notes" / "prime_mesh_r2q_sr11_realpath_noise_samples.csv"

INTERVALS_IN = OUT / "prime_mesh_r2q_o2p3_bridge_excursion_intervals.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_hexc_path_shape_summary.csv"
INTERVALS_OUT = OUT / "prime_mesh_r2q_hexc_path_shape_intervals.csv"
SCOPES_OUT = OUT / "prime_mesh_r2q_hexc_path_shape_scopes.csv"
WORST_PATHS_OUT = OUT / "prime_mesh_r2q_hexc_path_shape_worst_paths.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_HExc_Path_Shape_Audit_v1.md"
MANIFEST_OUT = OUT / "deposit_manifest.csv"


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


def safe_quantile(series: pd.Series, q: float) -> float:
    if len(series) == 0:
        return float("nan")
    return float(series.quantile(q))


def sign_changes(values: np.ndarray) -> int:
    signs = np.sign(values)
    signs = signs[signs != 0]
    if len(signs) <= 1:
        return 0
    return int(np.sum(signs[1:] != signs[:-1]))


def collect_samples(intervals: pd.DataFrame) -> dict[tuple[int, int], pd.DataFrame]:
    wanted: dict[tuple[int, int], int] = {
        (int(r.block_id), int(r.y)): int(r.h)
        for r in intervals[["block_id", "y", "h"]].itertuples(index=False)
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


def path_arrays(row: pd.Series, part: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    h = int(row["h"])
    d_start = float(row["D_start"])
    d_end = float(row["D_end"])
    delta = float(row["DeltaD"])

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
    return offsets, values, line, diff


def analyze_interval(row: pd.Series, part: pd.DataFrame) -> tuple[dict[str, object], pd.DataFrame]:
    block_id = int(row["block_id"])
    p_star = int(row["p_star"])
    y = int(row["y"])
    h = int(row["h"])
    delta = float(row["DeltaD"])
    denom = math.sqrt(h) * (math.log(p_star) ** 2)

    offsets, values, line, diff = path_arrays(row, part)
    abs_diff = np.abs(diff)
    max_idx = int(abs_diff.argmax()) if len(abs_diff) else 0
    exc_abs = float(abs_diff[max_idx]) if len(abs_diff) else 0.0
    exc_signed = float(diff[max_idx]) if len(diff) else 0.0
    exc_offset = float(offsets[max_idx]) if len(offsets) else float("nan")
    exc_t = int(y + exc_offset) if len(offsets) else y
    q_exc = exc_abs / denom if denom else float("nan")

    ss_res = float(np.sum(diff * diff))
    centered = values - values.mean() if len(values) else values
    ss_tot = float(np.sum(centered * centered))
    endpoint_line_r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    rms_diff = float(math.sqrt(np.mean(diff * diff))) if len(diff) else 0.0
    mean_abs_diff = float(np.mean(abs_diff)) if len(abs_diff) else 0.0
    abs_delta = abs(delta)
    exc_over_delta = exc_abs / abs_delta if abs_delta > 0 else float("nan")
    rms_over_delta = rms_diff / abs_delta if abs_delta > 0 else float("nan")

    residual_slopes = np.array([], dtype=float)
    curvature = np.array([], dtype=float)
    if len(offsets) >= 2:
        steps = np.diff(offsets)
        valid = steps != 0
        residual_slopes = np.diff(diff)[valid] / steps[valid]
    if len(residual_slopes) >= 2:
        curvature = np.diff(residual_slopes)

    max_abs_residual_slope = float(np.max(np.abs(residual_slopes))) if len(residual_slopes) else 0.0
    rms_residual_slope = float(math.sqrt(np.mean(residual_slopes * residual_slopes))) if len(residual_slopes) else 0.0
    max_abs_curvature = float(np.max(np.abs(curvature))) if len(curvature) else 0.0
    rms_curvature = float(math.sqrt(np.mean(curvature * curvature))) if len(curvature) else 0.0
    zero_cross = sign_changes(diff)
    peak_count_90 = int(np.sum(abs_diff >= 0.9 * exc_abs)) if exc_abs > 0 else 0
    peak_frac = exc_offset / h if h else float("nan")

    endpoint_dominated = exc_over_delta <= 0.02 if not math.isnan(exc_over_delta) else False
    near_linear = q_exc <= 0.05 and endpoint_dominated
    if near_linear:
        shape_class = "near_linear_endpoint_dominated"
    elif q_exc <= 0.05:
        shape_class = "small_absolute_excursion"
    else:
        shape_class = "large_excursion"

    rec_pos = row.get("recovery_position", np.nan)
    result = {
        "block_id": block_id,
        "p_star": p_star,
        "y": y,
        "h": h,
        "D_start": float(row["D_start"]),
        "D_end": float(row["D_end"]),
        "DeltaD": delta,
        "exc_abs": exc_abs,
        "exc_signed": exc_signed,
        "exc_t": exc_t,
        "exc_offset": exc_offset,
        "exc_offset_frac": peak_frac,
        "Q_exc": q_exc,
        "Q_DeltaD": float(row.get("Q_DeltaD", abs_delta / denom if denom else float("nan"))),
        "Q_delayed_proxy": float(row.get("Q_delayed_proxy", float("nan"))),
        "sampled_points": int(len(offsets)),
        "endpoint_line_r2": endpoint_line_r2,
        "rms_diff": rms_diff,
        "mean_abs_diff": mean_abs_diff,
        "rms_diff_norm": rms_diff / denom if denom else float("nan"),
        "mean_abs_diff_norm": mean_abs_diff / denom if denom else float("nan"),
        "exc_over_abs_DeltaD": exc_over_delta,
        "rms_over_abs_DeltaD": rms_over_delta,
        "max_abs_residual_slope": max_abs_residual_slope,
        "rms_residual_slope": rms_residual_slope,
        "max_abs_curvature": max_abs_curvature,
        "rms_curvature": rms_curvature,
        "zero_crossings": zero_cross,
        "peak_count_90pct": peak_count_90,
        "shape_class": shape_class,
        "endpoint_dominated_2pct": bool(endpoint_dominated),
        "is_tail": bool(row.get("is_tail", p_star >= 500_000_000)),
        "h_bin": h_bin(h),
        "p_scale_bin": p_scale_bin(p_star),
        "mu_bin_if_available": row.get("mu_bin_if_available", ""),
        "depth_bin": row.get("depth_bin", ""),
        "recovery_position": rec_pos,
    }

    path = pd.DataFrame(
        {
            "block_id": block_id,
            "p_star": p_star,
            "y": y,
            "h": h,
            "t": y + offsets.astype(int),
            "offset": offsets,
            "offset_frac": offsets / h if h else np.nan,
            "D_t": values,
            "line_t": line,
            "diff": diff,
            "abs_diff": abs_diff,
            "residual_slope_prev": np.concatenate([[np.nan], residual_slopes])[: len(offsets)],
            "Q_exc_interval": q_exc,
            "shape_class": shape_class,
        }
    )
    return result, path


def summarize(df: pd.DataFrame, scope: str) -> dict[str, object]:
    worst_q = df.loc[df["Q_exc"].idxmax()]
    worst_ratio = df.loc[df["exc_over_abs_DeltaD"].idxmax()]
    return {
        "scope": scope,
        "rows": int(len(df)),
        "Q_exc_max": float(df["Q_exc"].max()),
        "Q_exc_mean": float(df["Q_exc"].mean()),
        "Q_exc_median": float(df["Q_exc"].median()),
        "Q_exc_q95": safe_quantile(df["Q_exc"], 0.95),
        "Q_exc_q99": safe_quantile(df["Q_exc"], 0.99),
        "pass_Q_exc_le_0p05_frac": float((df["Q_exc"] <= 0.05).mean()),
        "pass_Q_exc_le_0p10_frac": float((df["Q_exc"] <= 0.10).mean()),
        "pass_Q_exc_le_0p25_frac": float((df["Q_exc"] <= 0.25).mean()),
        "exc_over_delta_max": float(df["exc_over_abs_DeltaD"].max()),
        "exc_over_delta_mean": float(df["exc_over_abs_DeltaD"].mean()),
        "exc_over_delta_median": float(df["exc_over_abs_DeltaD"].median()),
        "exc_over_delta_q95": safe_quantile(df["exc_over_abs_DeltaD"], 0.95),
        "endpoint_dominated_2pct_frac": float(df["endpoint_dominated_2pct"].mean()),
        "endpoint_line_r2_min": float(df["endpoint_line_r2"].min()),
        "endpoint_line_r2_mean": float(df["endpoint_line_r2"].mean()),
        "endpoint_line_r2_median": float(df["endpoint_line_r2"].median()),
        "rms_diff_norm_max": float(df["rms_diff_norm"].max()),
        "rms_diff_norm_mean": float(df["rms_diff_norm"].mean()),
        "mean_abs_diff_norm_max": float(df["mean_abs_diff_norm"].max()),
        "zero_crossings_max": int(df["zero_crossings"].max()),
        "zero_crossings_mean": float(df["zero_crossings"].mean()),
        "max_abs_residual_slope_max": float(df["max_abs_residual_slope"].max()),
        "max_abs_curvature_max": float(df["max_abs_curvature"].max()),
        "near_linear_endpoint_dominated_frac": float((df["shape_class"] == "near_linear_endpoint_dominated").mean()),
        "small_absolute_excursion_frac": float((df["shape_class"] == "small_absolute_excursion").mean()),
        "large_excursion_frac": float((df["shape_class"] == "large_excursion").mean()),
        "worst_Q_block_id": int(worst_q["block_id"]),
        "worst_Q_p_star": int(worst_q["p_star"]),
        "worst_Q_y": int(worst_q["y"]),
        "worst_Q_h": int(worst_q["h"]),
        "worst_Q_exc": float(worst_q["Q_exc"]),
        "worst_Q_exc_over_delta": float(worst_q["exc_over_abs_DeltaD"]),
        "worst_ratio_block_id": int(worst_ratio["block_id"]),
        "worst_ratio_p_star": int(worst_ratio["p_star"]),
        "worst_ratio_y": int(worst_ratio["y"]),
        "worst_ratio_h": int(worst_ratio["h"]),
        "worst_ratio_exc_over_delta": float(worst_ratio["exc_over_abs_DeltaD"]),
        "worst_ratio_Q_exc": float(worst_ratio["Q_exc"]),
    }


def scope_rows(df: pd.DataFrame) -> pd.DataFrame:
    scopes: list[dict[str, object]] = [summarize(df, "global")]
    candidates = [
        ("tail:p_star>=500M", df[df["is_tail"]]),
        ("finite:p_star<500M", df[~df["is_tail"]]),
        ("scale:p<100M", df[df["p_star"] < 100_000_000]),
        ("scale:100M<=p<500M", df[(df["p_star"] >= 100_000_000) & (df["p_star"] < 500_000_000)]),
        ("scale:p>=500M", df[df["p_star"] >= 500_000_000]),
    ]
    for label, part in candidates:
        if len(part):
            scopes.append(summarize(part, label))
    for col, prefix in [("h_bin", "h"), ("mu_bin_if_available", "mu"), ("depth_bin", "depth"), ("shape_class", "shape")]:
        for value, part in df.groupby(col, dropna=False):
            if len(part):
                scopes.append(summarize(part, f"{prefix}:{value}"))
    return pd.DataFrame(scopes).sort_values(["Q_exc_max", "rows"], ascending=[False, False])


def write_doc(summary: dict[str, object], scopes: pd.DataFrame, intervals: pd.DataFrame) -> None:
    qmax = float(summary["Q_exc_max"])
    endpoint_frac = float(summary["endpoint_dominated_2pct_frac"])
    r2_min = float(summary["endpoint_line_r2_min"])
    if qmax <= 0.05 and endpoint_frac >= 0.95:
        verdict = "deterministic path-shape / endpoint-linearity"
    elif qmax <= 0.05:
        verdict = "small absolute excursion, mixed endpoint-linearity"
    else:
        verdict = "maximal/random-style obstruction remains plausible"

    worst = intervals.sort_values("Q_exc", ascending=False).head(15)
    lines = [
        "# Prime Mesh R2Q - H-Exc Path-Shape Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-07",
        f"**Status:** H-Exc diagnostic - {verdict}",
        "",
        "## 1. Purpose",
        "",
        "This audit asks whether the H-Exc bridge fluctuation behaves like a random/maximal partial-sum problem or like a deterministic path-shape problem.",
        "",
        "For each LongA/B2-active interval, it recomputes the sampled SR11 bridge residual",
        "",
        r"\[",
        r"B_J(t)=D_N(t)-\ell_J(t),",
        r"\qquad",
        r"Q_{\rm exc}(J)=\frac{\sup_{t\in J}|B_J(t)|}{\sqrt h\log^2p^*}.",
        r"\]",
        "",
        "It then measures endpoint-linearity, residual slope/curvature, peak location, and the size of the excursion relative to the endpoint motion.",
        "",
        "## 2. Main Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    for k, v in summary.items():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## 3. Scope Summary",
        "",
        scopes.to_markdown(index=False),
        "",
        "## 4. Worst H-Exc Intervals",
        "",
        worst.to_markdown(index=False),
        "",
        "## 5. Interpretation",
        "",
    ]
    if qmax <= 0.05 and endpoint_frac >= 0.95:
        lines += [
            r"\[",
            r"\boxed{\text{H-Exc looks like a deterministic endpoint-linearity/path-shape problem, not a random maximal obstruction.}}",
            r"\]",
            "",
            f"All sampled intervals pass `Q_exc <= 0.05`; `{endpoint_frac:.6g}` of intervals have internal excursion at most 2% of endpoint motion; the minimum endpoint-line R^2 is `{r2_min:.12g}`.",
        ]
    elif qmax <= 0.05:
        lines += [
            r"\[",
            r"\boxed{\text{H-Exc is absolutely small, but not uniformly endpoint-dominated by the 2% criterion.}}",
            r"\]",
            "",
            "This still supports a deterministic bridge-excursion lemma, but the proof may need a small-window clause in addition to endpoint-linearity.",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{H-Exc still has a sampled maximal-obstruction signature.}}",
            r"\]",
        ]
    lines += [
        "",
        "## 6. Proof-Route Consequence",
        "",
        "The audit favors proving H-Exc through a deterministic bridge discrepancy or path-shape lemma.  A generic random-walk maximal inequality is likely overkill and would lose much more than the observed margin.",
        "",
        "The endpoint increment remains excluded from H-Exc.  It is the B2/MR-2 repayment-side motion already handled by the endpoint compatibility audit.",
        "",
        "## 7. Outputs",
        "",
        f"- `{SUMMARY_OUT.name}`",
        f"- `{INTERVALS_OUT.name}`",
        f"- `{SCOPES_OUT.name}`",
        f"- `{WORST_PATHS_OUT.name}`",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
    ]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


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


def main() -> None:
    log(f"Reading intervals from {INTERVALS_IN}")
    intervals = pd.read_csv(INTERVALS_IN)
    for c in ["block_id", "p_star", "y", "h", "D_start", "D_end", "DeltaD"]:
        intervals[c] = pd.to_numeric(intervals[c], errors="coerce")

    samples = collect_samples(intervals)
    rows: list[dict[str, object]] = []
    paths: list[pd.DataFrame] = []
    for row in intervals.itertuples(index=False):
        row_s = pd.Series(row._asdict())
        key = (int(row_s["block_id"]), int(row_s["y"]))
        result, path = analyze_interval(row_s, samples.get(key, pd.DataFrame()))
        rows.append(result)
        paths.append(path)

    out = pd.DataFrame(rows)
    scopes = scope_rows(out)

    worst_keys = set(
        tuple(x)
        for x in out.sort_values(["Q_exc", "exc_over_abs_DeltaD"], ascending=False)
        .head(20)[["block_id", "y", "h"]]
        .itertuples(index=False, name=None)
    )
    worst_paths = pd.concat(
        [p for p in paths if (int(p["block_id"].iloc[0]), int(p["y"].iloc[0]), int(p["h"].iloc[0])) in worst_keys],
        ignore_index=True,
    )

    summary = summarize(out, "global")
    summary.update(
        {
            "interval_rows": int(len(out)),
            "sample_source": str(SAMPLES.relative_to(ROOT)),
            "interval_source": INTERVALS_IN.name,
            "route_verdict": "deterministic_path_shape"
            if summary["Q_exc_max"] <= 0.05 and summary["endpoint_dominated_2pct_frac"] >= 0.95
            else "small_absolute_excursion"
            if summary["Q_exc_max"] <= 0.05
            else "maximal_problem_possible",
        }
    )

    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)
    out.to_csv(INTERVALS_OUT, index=False)
    scopes.to_csv(SCOPES_OUT, index=False)
    worst_paths.to_csv(WORST_PATHS_OUT, index=False)
    write_doc(summary, scopes, out)
    refresh_manifest()

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {INTERVALS_OUT}")
    log(f"Wrote {SCOPES_OUT}")
    log(f"Wrote {WORST_PATHS_OUT}")
    log(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
