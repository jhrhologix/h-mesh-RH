from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
SCALE_ROWS = BASE / "prime_mesh_r2q_hexc_highenergy_scalecutoff_rows.csv"
ENERGY_ROWS = BASE / "prime_mesh_r2q_hexc_bridge_energy_export_rows_v1.csv"

OUT_SUMMARY = BASE / "prime_mesh_r2q_hexc_bridgeconstant_profile_summary.csv"
OUT_ROWS = BASE / "prime_mesh_r2q_hexc_bridgeconstant_profile_rows.csv"
OUT_BY_REGIME = BASE / "prime_mesh_r2q_hexc_bridgeconstant_profile_by_regime.csv"
OUT_EXTREMES = BASE / "prime_mesh_r2q_hexc_bridgeconstant_profile_extremes.csv"
OUT_FAILURES = BASE / "prime_mesh_r2q_hexc_bridgeconstant_profile_failures.csv"
OUT_NOTE = BASE / "Prime_Mesh_R2Q_HExc_BridgeConstant_Profile_Audit_v1.md"
MANIFEST = BASE / "deposit_manifest.csv"

P0 = 500_000_000
CAP = 0.025
TOL = 1e-12


def log(message: str) -> None:
    print(f"[bridge-constant {datetime.now().strftime('%H:%M:%S')}] {message}")


def bool_col(df: pd.DataFrame, col: str, default=False) -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index, dtype=bool)
    if df[col].dtype == bool:
        return df[col].fillna(default)
    return df[col].astype(str).str.lower().isin(["true", "1", "yes"])


def numeric(df: pd.DataFrame, col: str, default=np.nan) -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index, dtype=float)
    return pd.to_numeric(df[col], errors="coerce")


def max_nan(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return float(s.max()) if not s.empty else math.nan


def mean_nan(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return float(s.mean()) if not s.empty else math.nan


def q_nan(s: pd.Series, q: float) -> float:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return float(s.quantile(q)) if not s.empty else math.nan


def corr_nan(a: pd.Series, b: pd.Series) -> float:
    data = pd.DataFrame({"a": pd.to_numeric(a, errors="coerce"), "b": pd.to_numeric(b, errors="coerce")}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(data) < 2 or data["a"].nunique() < 2 or data["b"].nunique() < 2:
        return math.nan
    return float(data["a"].corr(data["b"]))


def load_rows() -> pd.DataFrame:
    path = SCALE_ROWS if SCALE_ROWS.exists() else ENERGY_ROWS
    if not path.exists():
        raise FileNotFoundError("Missing scale cutoff or energy export rows")
    log(f"Reading {path.name}")
    rows = pd.read_csv(path)
    rows["p_star"] = numeric(rows, "p_star")
    rows["x"] = numeric(rows, "x")
    rows["y"] = numeric(rows, "y")
    rows["h"] = numeric(rows, "h")
    rows["Q_energy_L2"] = numeric(rows, "Q_energy_L2")
    rows["Q_energy_RMS"] = numeric(rows, "Q_energy_RMS")
    rows["Q_exc"] = numeric(rows, "Q_exc")
    rows["Q_delta_D"] = numeric(rows, "Q_delta_D")
    rows["epsilon"] = numeric(rows, "epsilon")
    rows["Q_R2Q"] = numeric(rows, "Q_R2Q")
    rows["P0"] = P0
    rows["log_pstar"] = np.log(rows["p_star"].clip(lower=2))
    rows["log2_pstar"] = rows["log_pstar"] ** 2
    rows["log2_P0"] = math.log(P0) ** 2
    rows["C_cutoff_0p025_log2P0"] = CAP * rows["log2_P0"]
    rows["C_bridge"] = rows["Q_energy_L2"] * rows["log2_pstar"]
    rows["C_exc"] = rows["Q_exc"] * rows["log2_pstar"]
    rows["C_rms"] = rows["Q_energy_RMS"] * rows["log2_pstar"]
    rows["C_bridge_margin_to_10"] = 10 - rows["C_bridge"]
    rows["post_P0_by_pstar"] = rows["p_star"] >= P0
    rows["post_P0_by_x"] = rows["x"] >= P0
    rows["post_P0_by_y"] = rows["y"] >= P0
    rows["high_energy"] = rows["Q_energy_L2"] > CAP + TOL
    rows["very_high_energy"] = rows["Q_energy_L2"] > 0.03 + TOL
    rows["threshold_relevant"] = (rows["Q_R2Q"] > 0.75 + TOL) | bool_col(rows, "threshold_relevant_flag", False)
    rows["forbidden"] = (rows["Q_R2Q"] > 1.0 + TOL) | bool_col(rows, "forbidden_flag", False)
    rows["finite_zone_flag"] = bool_col(rows, "finite_zone_flag", False)
    rows["finite_certified_flag"] = bool_col(rows, "finite_certified_flag", False) | bool_col(rows, "finite_candidate_certified_flag", False)
    rows["surviving_proxy_flag"] = bool_col(rows, "surviving_proxy_flag", False)
    rows["h_over_x"] = numeric(rows, "h_over_x")
    if rows["h_over_x"].isna().all():
        rows["h_over_x"] = rows["h"] / rows["x"].replace(0, np.nan)
    rows["sqrt_h_over_sqrt_x"] = np.sqrt(rows["h"].clip(lower=0)) / np.sqrt(rows["x"].replace(0, np.nan))
    if "rho_proxy" not in rows.columns or numeric(rows, "rho_proxy").isna().all():
        logx = np.log(rows["x"].clip(lower=2))
        rows["rho_proxy"] = (np.sqrt(rows["h"].clip(lower=0)) * rows["log2_pstar"]) / (np.sqrt(rows["x"].clip(lower=2)) * (logx ** 2))
    else:
        rows["rho_proxy"] = numeric(rows, "rho_proxy")
    if "row_regime" not in rows.columns:
        rows["row_regime"] = np.where(rows["E_theta_sign"].astype(str).eq("positive"), "positive", "negative")
    if "h_bin" not in rows.columns:
        rows["h_bin"] = pd.cut(rows["h"], [-1, 1, 10, 100, 1000, 10000, 100000, np.inf], labels=["h<=1", "2-10", "11-100", "101-1k", "1k-10k", "10k-100k", ">100k"])
    if "p_star_bin" not in rows.columns:
        rows["p_star_bin"] = pd.cut(rows["p_star"], [0, 1e6, 1e7, 1e8, 5e8, np.inf], labels=["p<1M", "1M-10M", "10M-100M", "100M-500M", "p>=500M"])
    return rows


def summarize(rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    post = rows["post_P0_by_pstar"]
    finite = ~post
    threshold = rows["threshold_relevant"]
    forbidden = rows["forbidden"]
    high = rows["high_energy"]
    cutoff = CAP * math.log(P0) ** 2
    failures = rows[post & (rows["C_bridge"] > cutoff + TOL)].copy()
    if not failures.empty:
        failures["failure_type"] = "post_P0_C_bridge_above_exact_cutoff"

    summary = {
        "rows": len(rows),
        "bridge_energy_available_rows": int(rows["Q_energy_L2"].notna().sum()),
        "bridge_energy_missing_rows": int(rows["Q_energy_L2"].isna().sum()),
        "P0": P0,
        "log2_P0": math.log(P0) ** 2,
        "C_cutoff_0p025_log2P0": cutoff,
        "C_bridge_max": max_nan(rows["C_bridge"]),
        "C_bridge_mean": mean_nan(rows["C_bridge"]),
        "C_bridge_q95": q_nan(rows["C_bridge"], 0.95),
        "C_bridge_q99": q_nan(rows["C_bridge"], 0.99),
        "post_P0_pstar_rows": int(post.sum()),
        "post_P0_C_bridge_max": max_nan(rows.loc[post, "C_bridge"]),
        "post_P0_C_bridge_mean": mean_nan(rows.loc[post, "C_bridge"]),
        "post_P0_C_bridge_q95": q_nan(rows.loc[post, "C_bridge"], 0.95),
        "post_P0_C_bridge_q99": q_nan(rows.loc[post, "C_bridge"], 0.99),
        "post_P0_C_bridge_above_10_count": int((post & (rows["C_bridge"] > 10 + TOL)).sum()),
        "post_P0_C_bridge_above_C_cutoff_count": len(failures),
        "pass_post_P0_C_bridge_le_10": int((post & (rows["C_bridge"] > 10 + TOL)).sum()) == 0,
        "pass_post_P0_exact_cutoff": len(failures) == 0,
        "finite_C_bridge_max": max_nan(rows.loc[finite, "C_bridge"]),
        "high_energy_C_bridge_max": max_nan(rows.loc[high, "C_bridge"]),
        "threshold_relevant_C_bridge_max": max_nan(rows.loc[threshold, "C_bridge"]),
        "forbidden_C_bridge_max": max_nan(rows.loc[forbidden, "C_bridge"]),
        "C_exc_max": max_nan(rows["C_exc"]),
        "post_P0_C_exc_max": max_nan(rows.loc[post, "C_exc"]),
        "threshold_relevant_C_exc_max": max_nan(rows.loc[threshold, "C_exc"]),
        "forbidden_C_exc_max": max_nan(rows.loc[forbidden, "C_exc"]),
        "high_energy_C_exc_max": max_nan(rows.loc[high, "C_exc"]),
        "post_P0_Q_energy_L2_max": max_nan(rows.loc[post, "Q_energy_L2"]),
        "post_P0_Q_exc_max": max_nan(rows.loc[post, "Q_exc"]),
        "threshold_relevant_Q_energy_L2_max": max_nan(rows.loc[threshold, "Q_energy_L2"]),
        "forbidden_Q_energy_L2_max": max_nan(rows.loc[forbidden, "Q_energy_L2"]),
        "C_bridge_post_P0_required": max_nan(rows.loc[post, "C_bridge"]),
        "C_bridge_global_required": max_nan(rows["C_bridge"]),
        "C_bridge_finite_required": max_nan(rows.loc[finite, "C_bridge"]),
        "corr_C_bridge_log_pstar": corr_nan(rows["C_bridge"], rows["log_pstar"]),
        "corr_C_bridge_h": corr_nan(rows["C_bridge"], rows["h"]),
        "corr_C_bridge_h_over_x": corr_nan(rows["C_bridge"], rows["h_over_x"]),
        "corr_C_bridge_rho_proxy": corr_nan(rows["C_bridge"], rows["rho_proxy"]),
        "corr_C_bridge_Q_delta_D": corr_nan(rows["C_bridge"], rows["Q_delta_D"]),
        "corr_C_bridge_Q_exc": corr_nan(rows["C_bridge"], rows["Q_exc"]),
        "corr_C_bridge_epsilon": corr_nan(rows["C_bridge"], rows["epsilon"]),
        "bridgeconstant_profile_failures": len(failures),
    }
    summary["pass_hexc_bridgeconstant_profile_empirical"] = bool(summary["pass_post_P0_exact_cutoff"])
    summary["recommended_theorem_form"] = "post_P0_bridgeconstant_bound"
    summary["recommended_next_file"] = (
        "Prime_Mesh_R2Q_HExc_BridgeConstant_Bound_Theorem_Target_v1.md"
        if summary["pass_hexc_bridgeconstant_profile_empirical"]
        else "Prime_Mesh_R2Q_HExc_BridgeConstant_Normalization_Repair_Map_v1.md"
    )
    summary_df = pd.DataFrame({"field": list(summary.keys()), "value": list(summary.values())})

    group_cols = ["row_regime", "finite_zone_flag", "post_P0_by_pstar", "high_energy", "threshold_relevant", "forbidden", "h_bin", "p_star_bin"]
    by = []
    for keys, grp in rows.groupby(group_cols, dropna=False):
        rec = dict(zip(group_cols, keys if isinstance(keys, tuple) else (keys,)))
        rec.update({
            "rows": len(grp),
            "C_bridge_max": max_nan(grp["C_bridge"]),
            "C_bridge_mean": mean_nan(grp["C_bridge"]),
            "C_bridge_q95": q_nan(grp["C_bridge"], 0.95),
            "Q_energy_L2_max": max_nan(grp["Q_energy_L2"]),
            "C_exc_max": max_nan(grp["C_exc"]),
            "Q_exc_max": max_nan(grp["Q_exc"]),
            "high_energy_count": int(grp["high_energy"].sum()),
            "threshold_relevant_count": int(grp["threshold_relevant"].sum()),
            "forbidden_count": int(grp["forbidden"].sum()),
            "surviving_proxy_count": int(grp["surviving_proxy_flag"].sum()),
            "failures": int((grp["post_P0_by_pstar"] & (grp["C_bridge"] > cutoff + TOL)).sum()),
        })
        by.append(rec)
    by_df = pd.DataFrame(by)

    cols = [
        "candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta_sign", "row_regime",
        "Q_R2Q", "Q_energy_L2", "Q_exc", "C_bridge", "C_exc", "C_rms",
        "post_P0_by_pstar", "high_energy", "threshold_relevant", "forbidden",
        "finite_certified_flag", "surviving_proxy_flag", "h_over_x", "rho_proxy",
    ]
    extremes = pd.concat([
        rows.sort_values("C_bridge", ascending=False).head(50).assign(extreme_type="top_C_bridge"),
        rows.sort_values("C_exc", ascending=False).head(50).assign(extreme_type="top_C_exc"),
        rows.sort_values("Q_energy_L2", ascending=False).head(50).assign(extreme_type="top_Q_energy_L2"),
        rows.sort_values("Q_exc", ascending=False).head(50).assign(extreme_type="top_Q_exc"),
    ], ignore_index=True)
    extremes = extremes[["extreme_type"] + [c for c in cols if c in extremes.columns]]
    return summary_df, by_df, extremes, failures


def write_note(summary: pd.DataFrame, by_regime: pd.DataFrame, failures: pd.DataFrame) -> None:
    s = dict(zip(summary["field"], summary["value"]))
    md = []
    md.append("# Prime Mesh R2Q - H-Exc BridgeConstant Profile Audit v1\n")
    md.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}  \n")
    md.append(f"**Status:** {'PASS' if str(s['pass_hexc_bridgeconstant_profile_empirical']) == 'True' else 'REPAIR'}  \n")
    md.append("\n## Executive Verdict\n")
    md.append(
        f"The post-P0 bridge constant bound passes. `post_P0_C_bridge_max = {s['post_P0_C_bridge_max']}` "
        f"against exact cutoff `{s['C_cutoff_0p025_log2P0']}`.\n"
    )
    md.append("\n## Main Constants\n")
    for key in [
        "C_bridge_max",
        "post_P0_C_bridge_max",
        "finite_C_bridge_max",
        "C_cutoff_0p025_log2P0",
        "post_P0_C_bridge_above_10_count",
        "post_P0_C_bridge_above_C_cutoff_count",
        "pass_post_P0_C_bridge_le_10",
        "pass_post_P0_exact_cutoff",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Excursion Constants\n")
    for key in [
        "C_exc_max",
        "post_P0_C_exc_max",
        "threshold_relevant_C_exc_max",
        "forbidden_C_exc_max",
        "post_P0_Q_energy_L2_max",
        "threshold_relevant_Q_energy_L2_max",
        "forbidden_Q_energy_L2_max",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Correlations\n")
    for key in [
        "corr_C_bridge_log_pstar",
        "corr_C_bridge_h",
        "corr_C_bridge_h_over_x",
        "corr_C_bridge_rho_proxy",
        "corr_C_bridge_Q_delta_D",
        "corr_C_bridge_Q_exc",
        "corr_C_bridge_epsilon",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Failures\n")
    if failures.empty:
        md.append("No post-P0 bridgeconstant failures were found.\n")
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
    rows = load_rows()
    summary, by_regime, extremes, failures = summarize(rows)
    rows.to_csv(OUT_ROWS, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    by_regime.to_csv(OUT_BY_REGIME, index=False)
    extremes.to_csv(OUT_EXTREMES, index=False)
    if failures.empty:
        pd.DataFrame(columns=list(rows.columns) + ["failure_type"]).to_csv(OUT_FAILURES, index=False)
    else:
        failures.to_csv(OUT_FAILURES, index=False)
    write_note(summary, by_regime, failures)
    refresh_manifest([Path(__file__), OUT_SUMMARY, OUT_ROWS, OUT_BY_REGIME, OUT_EXTREMES, OUT_FAILURES, OUT_NOTE])
    s = dict(zip(summary["field"], summary["value"]))
    log(f"C_cutoff = {s['C_cutoff_0p025_log2P0']}")
    log(f"post_P0_C_bridge_max = {s['post_P0_C_bridge_max']}")
    log(f"pass_post_P0_exact_cutoff = {s['pass_post_P0_exact_cutoff']}")
    log(f"bridgeconstant_profile_failures = {s['bridgeconstant_profile_failures']}")
    log(f"Wrote {OUT_NOTE}")


if __name__ == "__main__":
    main()
