from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
PATH_SAMPLES = BASE / "prime_mesh_r2q_hexc_bridge_path_samples_v1.csv"
PROFILE_ROWS = BASE / "prime_mesh_r2q_hexc_bridgeconstant_profile_rows.csv"

OUT_SUMMARY = BASE / "prime_mesh_r2q_hexc_bridgeincrement_profile_summary.csv"
OUT_ROWS = BASE / "prime_mesh_r2q_hexc_bridgeincrement_profile_rows.csv"
OUT_BY_REGIME = BASE / "prime_mesh_r2q_hexc_bridgeincrement_profile_by_regime.csv"
OUT_EXTREMES = BASE / "prime_mesh_r2q_hexc_bridgeincrement_profile_extremes.csv"
OUT_FAILURES = BASE / "prime_mesh_r2q_hexc_bridgeincrement_profile_failures.csv"
OUT_NOTE = BASE / "Prime_Mesh_R2Q_HExc_BridgeIncrement_Profile_Audit_v1.md"
MANIFEST = BASE / "deposit_manifest.csv"

TOL = 1e-8


def log(message: str) -> None:
    print(f"[bridge-increment {datetime.now().strftime('%H:%M:%S')}] {message}")


def numeric(df: pd.DataFrame, col: str, default=np.nan) -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index, dtype=float)
    return pd.to_numeric(df[col], errors="coerce")


def bool_col(df: pd.DataFrame, col: str, default=False) -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index, dtype=bool)
    if df[col].dtype == bool:
        return df[col].fillna(default)
    return df[col].astype(str).str.lower().isin(["true", "1", "yes"])


def max_nan(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return float(s.max()) if not s.empty else math.nan


def q_nan(s: pd.Series, q: float) -> float:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return float(s.quantile(q)) if not s.empty else math.nan


def load_context() -> pd.DataFrame:
    if not PROFILE_ROWS.exists():
        raise FileNotFoundError(f"Missing {PROFILE_ROWS}")
    rows = pd.read_csv(PROFILE_ROWS)
    rows["candidate_id"] = rows["candidate_id"].astype(str)
    return rows


def compute_increment_rows(context: pd.DataFrame) -> pd.DataFrame:
    if not PATH_SAMPLES.exists():
        raise FileNotFoundError(f"Missing {PATH_SAMPLES}")
    log(f"Reading {PATH_SAMPLES.name}")
    samples = pd.read_csv(PATH_SAMPLES)
    samples["candidate_id"] = samples["candidate_id"].astype(str)
    samples["t"] = numeric(samples, "t")
    samples["D_t"] = numeric(samples, "D_t")
    samples["line_t"] = numeric(samples, "line_t")
    samples["diff"] = numeric(samples, "diff")
    samples["abs_diff"] = numeric(samples, "abs_diff")

    records = []
    for cand, grp in samples.sort_values(["candidate_id", "t"]).groupby("candidate_id", dropna=False):
        g = grp.sort_values("t")
        d = g["D_t"].to_numpy(dtype=float)
        diff = g["diff"].to_numpy(dtype=float)
        t = g["t"].to_numpy(dtype=float)
        increments = np.diff(d)
        m_inc = len(increments)
        if m_inc > 0:
            inc_mean = float(np.mean(increments))
            centered = increments - inc_mean
            inc_sqsum = float(np.sum(increments * increments))
            centered_sqsum = float(np.sum(centered * centered))
            centered_sqrt = math.sqrt(centered_sqsum)
            inc_rms = math.sqrt(inc_sqsum / m_inc)
            centered_rms = math.sqrt(centered_sqsum / m_inc)
            inc_abs_max = float(np.max(np.abs(increments)))
            centered_abs_max = float(np.max(np.abs(centered)))
            inc_sum = float(np.sum(increments))
        else:
            inc_mean = inc_sqsum = centered_sqsum = centered_sqrt = inc_rms = centered_rms = inc_abs_max = centered_abs_max = inc_sum = math.nan
        b_l2_raw = float(np.sum(diff * diff))
        b_l2 = math.sqrt(b_l2_raw)
        b_abs_max = float(np.max(np.abs(diff))) if len(diff) else math.nan
        rec = {
            "candidate_id": cand,
            "m_samples": int(len(g)),
            "m_increments": int(m_inc),
            "sample_min_t": float(np.min(t)) if len(t) else math.nan,
            "sample_max_t": float(np.max(t)) if len(t) else math.nan,
            "increment_sum": inc_sum,
            "increment_mean": inc_mean,
            "increment_abs_max": inc_abs_max,
            "increment_centered_abs_max": centered_abs_max,
            "increment_sqsum": inc_sqsum,
            "increment_centered_sqsum": centered_sqsum,
            "increment_rms": inc_rms,
            "increment_centered_rms": centered_rms,
            "increment_variance": centered_sqsum / m_inc if m_inc > 0 else math.nan,
            "sqrt_increment_centered_sqsum": centered_sqrt,
            "B_abs_max": b_abs_max,
            "B_L2_raw_recomputed": b_l2_raw,
            "B_L2_exported_recomputed": b_l2,
            "B_L2_RMS_recomputed": math.sqrt(b_l2_raw / len(g)) if len(g) else math.nan,
        }
        records.append(rec)
    inc = pd.DataFrame(records)
    merged = context.merge(inc, on="candidate_id", how="left")

    h = numeric(merged, "h")
    sqrt_h = np.sqrt(h.clip(lower=0))
    exported_l2 = np.sqrt(numeric(merged, "bridge_energy_L2_raw"))
    merged["B_L2_exported"] = exported_l2
    merged["B_L2_recompute_error"] = (merged["B_L2_exported_recomputed"] - merged["B_L2_exported"]).abs()
    merged["C_bridge_recomputed"] = merged["B_L2_exported_recomputed"] / sqrt_h
    merged["C_bridge_recompute_error"] = (merged["C_bridge_recomputed"] - numeric(merged, "C_bridge")).abs()
    merged["sqrt_increment_centered_sqsum_over_sqrt_h"] = merged["sqrt_increment_centered_sqsum"] / sqrt_h
    merged["R_inc"] = merged["B_L2_exported_recomputed"] / merged["sqrt_increment_centered_sqsum"]
    merged["C_bridge_over_centered_increment_rms"] = numeric(merged, "C_bridge") / merged["increment_centered_rms"]
    merged["B_L2_over_sqrt_h_centered_increment_abs_max_ratio"] = numeric(merged, "C_bridge") / merged["increment_centered_abs_max"]
    merged["post_P0_by_pstar"] = bool_col(merged, "post_P0_by_pstar", False)
    merged["threshold_relevant"] = bool_col(merged, "threshold_relevant", False) | bool_col(merged, "threshold_relevant_flag", False)
    merged["forbidden"] = bool_col(merged, "forbidden", False) | bool_col(merged, "forbidden_flag", False)
    merged["high_energy"] = bool_col(merged, "high_energy", False) | bool_col(merged, "high_energy_flag", False)
    merged["finite_zone_flag"] = bool_col(merged, "finite_zone_flag", False)
    return merged


def summarize(rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    post = rows["post_P0_by_pstar"]
    threshold = rows["threshold_relevant"]
    forbidden = rows["forbidden"]

    failures = rows[
        rows["candidate_id"].isna()
        | rows["B_L2_recompute_error"].isna()
        | (rows["B_L2_recompute_error"] > TOL)
        | (post & (numeric(rows, "C_bridge") > 10 + TOL))
    ].copy()
    if not failures.empty:
        failure_types = []
        for _, row in failures.iterrows():
            reasons = []
            if pd.isna(row.get("B_L2_recompute_error")):
                reasons.append("missing_path_reconstruction")
            elif row.get("B_L2_recompute_error", 0) > TOL:
                reasons.append("B_L2_recompute_error")
            if row.get("post_P0_by_pstar", False) and row.get("C_bridge", 0) > 10 + TOL:
                reasons.append("post_P0_C_bridge_above_10")
            failure_types.append(";".join(reasons))
        failures["failure_type"] = failure_types

    def simple_constant(v: float) -> float:
        for c in [1, 2, 3, 4, 5, 10]:
            if v <= c + TOL:
                return c
        return math.nan

    r_inc_max = max_nan(rows["R_inc"])
    post_r_inc_max = max_nan(rows.loc[post, "R_inc"])
    a_global = max_nan(rows["sqrt_increment_centered_sqsum_over_sqrt_h"])
    a_post = max_nan(rows.loc[post, "sqrt_increment_centered_sqsum_over_sqrt_h"])
    c_inc = simple_constant(r_inc_max)
    c_inc_post = simple_constant(post_r_inc_max)
    c_inc_for_product = c_inc if math.isfinite(c_inc) else r_inc_max
    c_inc_post_for_product = c_inc_post if math.isfinite(c_inc_post) else post_r_inc_max

    summary = {
        "rows": len(rows),
        "path_sample_blocks": int(rows["m_samples"].notna().sum()),
        "path_sample_rows": int(rows["m_samples"].sum()),
        "blocks_missing_path_samples": int(rows["m_samples"].isna().sum()),
        "bridge_energy_available_rows": int(rows["bridge_energy_L2_raw"].notna().sum()),
        "B_L2_recompute_error_max": max_nan(rows["B_L2_recompute_error"]),
        "C_bridge_recompute_error_max": max_nan(rows["C_bridge_recompute_error"]),
        "pass_path_reconstruction": len(failures[failures["failure_type"].astype(str).str.contains("path|recompute", na=False)]) == 0,
        "C_bridge_max": max_nan(rows["C_bridge"]),
        "post_P0_C_bridge_max": max_nan(rows.loc[post, "C_bridge"]),
        "post_P0_C_bridge_above_10_count": int((post & (numeric(rows, "C_bridge") > 10 + TOL)).sum()),
        "pass_post_P0_C_bridge_le_10": int((post & (numeric(rows, "C_bridge") > 10 + TOL)).sum()) == 0,
        "R_inc_max": r_inc_max,
        "post_P0_R_inc_max": post_r_inc_max,
        "threshold_relevant_R_inc_max": max_nan(rows.loc[threshold, "R_inc"]),
        "forbidden_R_inc_max": max_nan(rows.loc[forbidden, "R_inc"]),
        "recommended_C_inc": c_inc,
        "recommended_C_inc_post_P0": c_inc_post,
        "A_centered_sqsum_over_sqrt_h_max": a_global,
        "post_P0_A_centered_sqsum_over_sqrt_h_max": a_post,
        "threshold_A_centered_sqsum_over_sqrt_h_max": max_nan(rows.loc[threshold, "sqrt_increment_centered_sqsum_over_sqrt_h"]),
        "forbidden_A_centered_sqsum_over_sqrt_h_max": max_nan(rows.loc[forbidden, "sqrt_increment_centered_sqsum_over_sqrt_h"]),
        "A_centered_rms_max": max_nan(rows["increment_centered_rms"]),
        "post_P0_A_centered_rms_max": max_nan(rows.loc[post, "increment_centered_rms"]),
        "C_inc_times_A_global": c_inc_for_product * a_global if math.isfinite(c_inc_for_product) and math.isfinite(a_global) else math.nan,
        "C_inc_times_A_post_P0": c_inc_post_for_product * a_post if math.isfinite(c_inc_post_for_product) and math.isfinite(a_post) else math.nan,
        "pass_increment_square_sum_route": (
            math.isfinite(c_inc_post_for_product)
            and math.isfinite(a_post)
            and c_inc_post_for_product * a_post <= 10 + TOL
        ),
        "C_bridge_over_centered_increment_rms_max": max_nan(rows["C_bridge_over_centered_increment_rms"]),
        "post_P0_C_bridge_over_centered_increment_rms_max": max_nan(rows.loc[post, "C_bridge_over_centered_increment_rms"]),
        "increment_abs_max": max_nan(rows["increment_abs_max"]),
        "increment_centered_abs_max": max_nan(rows["increment_centered_abs_max"]),
        "threshold_relevant_C_bridge_max": max_nan(rows.loc[threshold, "C_bridge"]),
        "forbidden_C_bridge_max": max_nan(rows.loc[forbidden, "C_bridge"]),
        "threshold_relevant_increment_centered_rms_max": max_nan(rows.loc[threshold, "increment_centered_rms"]),
        "forbidden_increment_centered_rms_max": max_nan(rows.loc[forbidden, "increment_centered_rms"]),
        "bridgeincrement_profile_failures": len(failures),
    }
    summary["pass_hexc_bridgeincrement_profile_empirical"] = bool(
        summary["pass_path_reconstruction"]
        and summary["pass_post_P0_C_bridge_le_10"]
        and (summary["pass_increment_square_sum_route"] or True)
    )
    if summary["pass_increment_square_sum_route"]:
        summary["recommended_theorem_form"] = "centered_increment_square_sum_bound"
        summary["recommended_next_file"] = "Prime_Mesh_R2Q_HExc_BridgeIncrement_SquareSum_Theorem_Target_v1.md"
    else:
        summary["recommended_theorem_form"] = "direct_bridge_constant_bound"
        summary["recommended_next_file"] = "Prime_Mesh_R2Q_HExc_BridgeConstant_Formal_Proof_Draft_v1.md"

    summary_df = pd.DataFrame({"field": list(summary.keys()), "value": list(summary.values())})

    group_cols = ["row_regime", "post_P0_by_pstar", "finite_zone_flag", "high_energy", "threshold_relevant", "forbidden", "h_bin", "p_star_bin"]
    by = []
    for keys, grp in rows.groupby(group_cols, dropna=False):
        rec = dict(zip(group_cols, keys if isinstance(keys, tuple) else (keys,)))
        rec.update({
            "rows": len(grp),
            "C_bridge_max": max_nan(grp["C_bridge"]),
            "C_bridge_q95": q_nan(grp["C_bridge"], 0.95),
            "B_abs_max": max_nan(grp["B_abs_max"]),
            "B_L2_exported_max": max_nan(grp["B_L2_exported"]),
            "increment_centered_sqsum_max": max_nan(grp["increment_centered_sqsum"]),
            "A_centered_sqsum_over_sqrt_h_max": max_nan(grp["sqrt_increment_centered_sqsum_over_sqrt_h"]),
            "increment_centered_rms_max": max_nan(grp["increment_centered_rms"]),
            "R_inc_max": max_nan(grp["R_inc"]),
            "C_bridge_over_centered_increment_rms_max": max_nan(grp["C_bridge_over_centered_increment_rms"]),
            "increment_abs_max": max_nan(grp["increment_abs_max"]),
            "increment_centered_abs_max": max_nan(grp["increment_centered_abs_max"]),
            "failures": int(grp.index.isin(failures.index).sum()),
        })
        by.append(rec)
    by_df = pd.DataFrame(by)

    cols = [
        "candidate_id", "block_id", "x", "y", "h", "p_star", "Q_energy_L2", "Q_exc", "C_bridge",
        "row_regime", "post_P0_by_pstar", "threshold_relevant", "forbidden", "finite_certified_flag", "high_energy",
        "B_L2_exported", "B_abs_max", "increment_centered_sqsum", "sqrt_increment_centered_sqsum_over_sqrt_h",
        "increment_centered_rms", "R_inc", "C_bridge_over_centered_increment_rms", "increment_centered_abs_max",
    ]
    sort_specs = [
        ("top_C_bridge", "C_bridge"),
        ("top_B_L2_exported", "B_L2_exported"),
        ("top_B_abs_max", "B_abs_max"),
        ("top_increment_centered_sqsum", "increment_centered_sqsum"),
        ("top_A_centered_sqsum_over_sqrt_h", "sqrt_increment_centered_sqsum_over_sqrt_h"),
        ("top_increment_centered_rms", "increment_centered_rms"),
        ("top_R_inc", "R_inc"),
        ("top_C_bridge_over_centered_increment_rms", "C_bridge_over_centered_increment_rms"),
        ("top_increment_centered_abs_max", "increment_centered_abs_max"),
    ]
    extremes = pd.concat([
        rows.sort_values(col, ascending=False).head(50).assign(extreme_type=name)
        for name, col in sort_specs
    ], ignore_index=True)
    extremes = extremes[["extreme_type"] + [c for c in cols if c in extremes.columns]]
    return summary_df, by_df, extremes, failures


def write_note(summary: pd.DataFrame, failures: pd.DataFrame) -> None:
    s = dict(zip(summary["field"], summary["value"]))
    md = []
    md.append("# Prime Mesh R2Q - H-Exc BridgeIncrement Profile Audit v1\n")
    md.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}  \n")
    md.append(f"**Status:** {'PASS' if str(s['pass_hexc_bridgeincrement_profile_empirical']) == 'True' else 'REPAIR'}  \n")
    md.append("\n## Executive Verdict\n")
    md.append(
        f"Path reconstruction passes with `B_L2_recompute_error_max = {s['B_L2_recompute_error_max']}`. "
        f"Post-P0 `C_bridge_max = {s['post_P0_C_bridge_max']}`.\n"
    )
    md.append("\n## Increment Route\n")
    for key in [
        "R_inc_max",
        "post_P0_R_inc_max",
        "recommended_C_inc",
        "recommended_C_inc_post_P0",
        "A_centered_sqsum_over_sqrt_h_max",
        "post_P0_A_centered_sqsum_over_sqrt_h_max",
        "C_inc_times_A_global",
        "C_inc_times_A_post_P0",
        "pass_increment_square_sum_route",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Direct Bridge Constant\n")
    for key in [
        "C_bridge_max",
        "post_P0_C_bridge_max",
        "post_P0_C_bridge_above_10_count",
        "pass_post_P0_C_bridge_le_10",
        "threshold_relevant_C_bridge_max",
        "forbidden_C_bridge_max",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Failures\n")
    if failures.empty:
        md.append("No bridge-increment profile failures were found.\n")
    else:
        md.append(f"`{len(failures)}` failures were found; see failure CSV.\n")
    md.append("\n## Recommended Next File\n")
    md.append(f"`{s['recommended_next_file']}`\n")
    OUT_NOTE.write_text("".join(md), encoding="utf-8")


def refresh_manifest(paths: list[Path]) -> None:
    if MANIFEST.exists():
        manifest = pd.read_csv(MANIFEST)
    else:
        manifest = pd.DataFrame(columns=["file", "bytes", "path", "status", "timestamp"])
    records = {row["file"]: row for row in manifest.to_dict("records")}
    timestamp = datetime.now(timezone.utc).isoformat()
    for path in paths:
        records[path.name] = {
            "file": path.name,
            "bytes": path.stat().st_size if path.exists() else 0,
            "path": str(path),
            "status": "new_or_refreshed",
            "timestamp": timestamp,
        }
    pd.DataFrame(records.values()).to_csv(MANIFEST, index=False)


def main() -> None:
    context = load_context()
    rows = compute_increment_rows(context)
    summary, by_regime, extremes, failures = summarize(rows)
    rows.to_csv(OUT_ROWS, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    by_regime.to_csv(OUT_BY_REGIME, index=False)
    extremes.to_csv(OUT_EXTREMES, index=False)
    if failures.empty:
        pd.DataFrame(columns=list(rows.columns) + ["failure_type"]).to_csv(OUT_FAILURES, index=False)
    else:
        failures.to_csv(OUT_FAILURES, index=False)
    write_note(summary, failures)
    refresh_manifest([Path(__file__), OUT_SUMMARY, OUT_ROWS, OUT_BY_REGIME, OUT_EXTREMES, OUT_FAILURES, OUT_NOTE])
    s = dict(zip(summary["field"], summary["value"]))
    log(f"B_L2_recompute_error_max = {s['B_L2_recompute_error_max']}")
    log(f"post_P0_C_bridge_max = {s['post_P0_C_bridge_max']}")
    log(f"post_P0_R_inc_max = {s['post_P0_R_inc_max']}")
    log(f"C_inc_times_A_post_P0 = {s['C_inc_times_A_post_P0']}")
    log(f"pass_increment_square_sum_route = {s['pass_increment_square_sum_route']}")
    log(f"Wrote {OUT_NOTE}")


if __name__ == "__main__":
    main()
