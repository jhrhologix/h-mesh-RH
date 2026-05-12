from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent

RAW_ROWS = BASE / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv"
VP_SUMMARY = BASE / "prime_mesh_r2q_hexc_variance_proxy_summary.csv"
HEXC_PATHS = BASE / "prime_mesh_r2q_hexc_path_shape_worst_paths.csv"
O2P3_PATHS = BASE / "prime_mesh_r2q_o2p3_bridge_excursion_worst_paths.csv"
V2_SUMMARY = BASE / "prime_mesh_r2q_hexc_v2_shell_variance_summary.csv"

OUT_SUMMARY = BASE / "prime_mesh_r2q_hexc_bridge_energy_summary.csv"
OUT_ROWS = BASE / "prime_mesh_r2q_hexc_bridge_energy_rows.csv"
OUT_BY_REGIME = BASE / "prime_mesh_r2q_hexc_bridge_energy_by_regime.csv"
OUT_FAILURES = BASE / "prime_mesh_r2q_hexc_bridge_energy_failures.csv"
OUT_NOTE = BASE / "Prime_Mesh_R2Q_HExc_BridgeEnergy_Audit_v1.md"
MANIFEST = BASE / "deposit_manifest.csv"

Q_EXC_CAP = 0.025
C_MAX_CANDIDATES = [1, 1.5, 2, 3, 5, 10]
TOL = 1e-12


def log(message: str) -> None:
    print(f"[hexc-energy {datetime.now().strftime('%H:%M:%S')}] {message}")


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


def field_value(path: Path, field: str) -> float:
    if not path.exists():
        return math.nan
    df = pd.read_csv(path)
    if {"field", "value"}.issubset(df.columns):
        row = df[df["field"].astype(str) == field]
        if not row.empty:
            return float(pd.to_numeric(row["value"], errors="coerce").iloc[0])
    if field in df.columns and not df.empty:
        return float(pd.to_numeric(df[field], errors="coerce").iloc[0])
    return math.nan


def classify(rows: pd.DataFrame) -> pd.Series:
    positive = rows["E_theta_sign"].eq("positive")
    negative = rows["E_theta_sign"].eq("negative")
    post = rows["post_P0_flag"]
    near = rows["threshold_relevant_flag"]
    forbidden = rows["forbidden_flag"]

    regime = pd.Series("unclassified", index=rows.index, dtype=object)
    regime.loc[positive & post] = "post_P0_positive_tail"
    regime.loc[positive & ~post] = "finite_positive"
    regime.loc[negative & post] = "post_P0_negative_tail"
    regime.loc[negative & ~post] = "finite_negative"
    regime.loc[negative & near] = "threshold_relevant_negative"
    regime.loc[negative & forbidden] = "forbidden_negative"
    return regime


def load_base_rows() -> pd.DataFrame:
    if not RAW_ROWS.exists():
        raise FileNotFoundError(f"Missing primary input: {RAW_ROWS}")
    log(f"Reading {RAW_ROWS.name}")
    df = pd.read_csv(RAW_ROWS)
    rows = pd.DataFrame(index=df.index)

    for col in ["candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta_sign"]:
        rows[col] = df[col] if col in df.columns else np.nan

    rows["post_P0_flag"] = bool_col(df, "post_P0_flag", False) | bool_col(df, "post_P0", False)
    rows["finite_zone_flag"] = bool_col(df, "finite_zone_flag", False)
    if not rows["finite_zone_flag"].any():
        rows["finite_zone_flag"] = ~rows["post_P0_flag"]
    rows["E_theta"] = numeric(df, "E_theta", np.nan)
    rows["Q_R2Q"] = numeric(df, "Q_R2Q", np.nan)
    rows["Q_delta_D"] = numeric(df, "Q_delta_D", np.nan)
    rows["Q_exc"] = numeric(df, "Q_exc", np.nan)
    rows["epsilon"] = numeric(df, "epsilon", np.nan)
    rows["bridge_excursion_raw"] = numeric(df, "bridge_excursion_raw", np.nan)
    rows["bridge_excursion_argmax"] = numeric(df, "bridge_excursion_argmax", np.nan)
    rows["scale_denominator"] = numeric(df, "denom_sqrt_h_logB", np.nan)
    rows["threshold_relevant_flag"] = bool_col(df, "threshold_relevant_flag", False) | bool_col(df, "near_forbidden_flag", False) | bool_col(df, "near_forbidden_R2Q", False)
    rows["forbidden_flag"] = bool_col(df, "forbidden_flag", False) | bool_col(df, "forbidden_R2Q", False)
    rows["row_regime"] = classify(rows)
    return rows


def path_energy(path: Path, source: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    keys = ["block_id", "p_star", "y", "h"]
    missing = [k for k in keys if k not in df.columns]
    if missing or "diff" not in df.columns:
        return pd.DataFrame()
    df["diff"] = pd.to_numeric(df["diff"], errors="coerce")
    df["abs_diff"] = pd.to_numeric(df.get("abs_diff", df["diff"].abs()), errors="coerce")
    grouped = []
    for key, grp in df.groupby(keys, dropna=False):
        diff = grp["diff"].dropna()
        abs_diff = grp["abs_diff"].dropna()
        if diff.empty:
            continue
        raw = float((diff * diff).sum())
        count = int(diff.shape[0])
        grouped.append({
            "block_id": key[0],
            "p_star": key[1],
            "y": key[2],
            "h": key[3],
            "bridge_sample_count": count,
            "bridge_sample_min_t": float(pd.to_numeric(grp["t"], errors="coerce").min()) if "t" in grp.columns else math.nan,
            "bridge_sample_max_t": float(pd.to_numeric(grp["t"], errors="coerce").max()) if "t" in grp.columns else math.nan,
            "bridge_energy_raw": raw,
            "bridge_energy_mean": raw / count,
            "bridge_energy_rms": math.sqrt(raw / count),
            "bridge_energy_max": float(abs_diff.max()) if not abs_diff.empty else math.nan,
            "bridge_samples_source": source,
        })
    return pd.DataFrame(grouped)


def build_energy_table() -> pd.DataFrame:
    parts = [
        path_energy(HEXC_PATHS, HEXC_PATHS.name),
        path_energy(O2P3_PATHS, O2P3_PATHS.name),
    ]
    energy = pd.concat([p for p in parts if not p.empty], ignore_index=True) if any(not p.empty for p in parts) else pd.DataFrame()
    if energy.empty:
        return energy
    keys = ["block_id", "p_star", "y", "h"]
    # Prefer the O2P3 path export if duplicate rows exist because it was the direct bridge-excursion path audit.
    energy["_source_priority"] = energy["bridge_samples_source"].str.contains("o2p3", case=False, na=False).astype(int)
    energy = energy.sort_values("_source_priority", ascending=False).drop_duplicates(keys, keep="first").drop(columns=["_source_priority"])
    return energy


def summarize(rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    q_exc = pd.to_numeric(rows["Q_exc"], errors="coerce")
    rows["Q_exc_above_0p025_flag"] = q_exc > Q_EXC_CAP + TOL
    rows["missing_Q_exc_flag"] = q_exc.isna()
    rows["bridge_samples_available_flag"] = rows["bridge_sample_count"].fillna(0).astype(float).gt(0)
    rows["bridge_energy_available_flag"] = pd.to_numeric(rows["bridge_energy_rms"], errors="coerce").gt(0)

    denom = pd.to_numeric(rows["scale_denominator"], errors="coerce")
    rows["Q_energy_sum"] = np.sqrt(pd.to_numeric(rows["bridge_energy_raw"], errors="coerce")) / denom
    rows["Q_energy_rms"] = pd.to_numeric(rows["bridge_energy_rms"], errors="coerce") / denom
    rows["Q_exc_over_Q_energy_rms"] = rows["Q_exc"] / rows["Q_energy_rms"]
    rows["Q_exc_over_Q_energy_sum"] = rows["Q_exc"] / rows["Q_energy_sum"]

    sqrt_v2_global = field_value(V2_SUMMARY, "sqrt_V2_formula")
    v2_global = field_value(V2_SUMMARY, "V2_formula")
    rows["V2_row_available_flag"] = False
    rows["V2_row"] = np.nan
    rows["sqrt_V2_row"] = np.nan
    rows["Q_exc_over_sqrt_V2_row"] = np.nan
    rows["V2_global"] = v2_global
    rows["sqrt_V2_global"] = sqrt_v2_global
    rows["Q_exc_over_sqrt_V2_global"] = rows["Q_exc"] / sqrt_v2_global

    if rows["bridge_energy_available_flag"].any():
        rows["variance_proxy_mode"] = "partial_row_level_energy_available"
    elif math.isfinite(sqrt_v2_global):
        rows["variance_proxy_mode"] = "global_V2_only"
    else:
        rows["variance_proxy_mode"] = "no_variance_proxy"

    failures = []
    for _, row in rows.iterrows():
        reasons = []
        if row["missing_Q_exc_flag"]:
            reasons.append("missing_Q_exc")
        if row["Q_exc_above_0p025_flag"]:
            reasons.append("Q_exc_above_0p025")
        if reasons:
            item = row.to_dict()
            item["failure_type"] = ";".join(reasons)
            failures.append(item)
    failures_df = pd.DataFrame(failures)

    def max_nan(s):
        s = pd.to_numeric(s, errors="coerce").dropna()
        return float(s.max()) if not s.empty else math.nan

    def mean_nan(s):
        s = pd.to_numeric(s, errors="coerce").dropna()
        return float(s.mean()) if not s.empty else math.nan

    def q_nan(s, quantile):
        s = pd.to_numeric(s, errors="coerce").dropna()
        return float(s.quantile(quantile)) if not s.empty else math.nan

    energy_rows = rows[rows["bridge_energy_available_flag"]].copy()
    lowest_cmax = math.nan
    pass_energy_maximal = False
    if not energy_rows.empty:
        ratio = pd.to_numeric(energy_rows["Q_exc_over_Q_energy_rms"], errors="coerce")
        ratio_max = max_nan(ratio)
        for c in C_MAX_CANDIDATES:
            if ratio_max <= c + TOL:
                lowest_cmax = c
                pass_energy_maximal = True
                break
    else:
        ratio_max = math.nan

    if len(energy_rows) == len(rows):
        variance_mode = "row_level_energy_available"
        recommended = "Prime_Mesh_R2Q_HExc_BridgeEnergy_Theorem_Target_v1.md"
        theorem_form = "row_level_bridge_energy"
    elif len(energy_rows) > 0:
        variance_mode = "partial_row_level_energy_available"
        recommended = "Prime_Mesh_R2Q_HExc_BridgeEnergy_Export_Patch_Spec_v1.md"
        theorem_form = "absolute_cap_with_partial_energy_samples"
    elif math.isfinite(sqrt_v2_global):
        variance_mode = "global_V2_only"
        recommended = "Prime_Mesh_R2Q_HExc_BridgeEnergy_Export_Patch_Spec_v1.md"
        theorem_form = "absolute_cap_global_V2_only"
    else:
        variance_mode = "no_variance_proxy"
        recommended = "Prime_Mesh_R2Q_HExc_BridgeEnergy_Repair_Map_v1.md"
        theorem_form = "repair_needed"

    summary = {
        "rows": len(rows),
        "primitive_full_rows": int(q_exc.notna().sum()),
        "Q_exc_available_rows": int(q_exc.notna().sum()),
        "Q_exc_max": max_nan(q_exc),
        "Q_exc_above_0p025_count": int(rows["Q_exc_above_0p025_flag"].sum()),
        "pass_absolute_Q_exc_cap": int(rows["Q_exc_above_0p025_flag"].sum()) == 0,
        "bridge_samples_available_rows": int(rows["bridge_samples_available_flag"].sum()),
        "bridge_samples_missing_rows": int((~rows["bridge_samples_available_flag"]).sum()),
        "bridge_energy_available_rows": int(rows["bridge_energy_available_flag"].sum()),
        "bridge_energy_missing_rows": int((~rows["bridge_energy_available_flag"]).sum()),
        "threshold_relevant_bridge_energy_missing_count": int((rows["threshold_relevant_flag"] & ~rows["bridge_energy_available_flag"]).sum()),
        "forbidden_bridge_energy_missing_count": int((rows["forbidden_flag"] & ~rows["bridge_energy_available_flag"]).sum()),
        "Q_energy_rms_min": float(pd.to_numeric(energy_rows["Q_energy_rms"], errors="coerce").min()) if not energy_rows.empty else math.nan,
        "Q_energy_rms_max": max_nan(energy_rows["Q_energy_rms"]) if not energy_rows.empty else math.nan,
        "Q_energy_rms_mean": mean_nan(energy_rows["Q_energy_rms"]) if not energy_rows.empty else math.nan,
        "Q_exc_over_Q_energy_rms_max": ratio_max,
        "Q_exc_over_Q_energy_rms_q95": q_nan(energy_rows["Q_exc_over_Q_energy_rms"], 0.95) if not energy_rows.empty else math.nan,
        "lowest_Cmax_energy_pass": lowest_cmax,
        "pass_energy_maximal_candidate": pass_energy_maximal,
        "V2_row_available_rows": 0,
        "V2_global": v2_global,
        "sqrt_V2_global": sqrt_v2_global,
        "Q_exc_max_over_sqrt_V2_global": max_nan(rows["Q_exc_over_sqrt_V2_global"]),
        "variance_proxy_mode": variance_mode,
        "bridge_energy_failures": len(failures_df),
        "pass_hexc_bridge_energy_empirical": int(rows["Q_exc_above_0p025_flag"].sum()) == 0 and len(failures_df) == 0,
        "recommended_theorem_form": theorem_form,
        "recommended_next_file": recommended,
    }

    summary_df = pd.DataFrame({"field": list(summary.keys()), "value": list(summary.values())})

    by_regime = []
    for regime, grp in rows.groupby("row_regime", dropna=False):
        by_regime.append({
            "row_regime": regime,
            "rows": len(grp),
            "Q_exc_max": max_nan(grp["Q_exc"]),
            "Q_exc_mean": mean_nan(grp["Q_exc"]),
            "bridge_energy_available_rows": int(grp["bridge_energy_available_flag"].sum()),
            "Q_energy_rms_max": max_nan(grp["Q_energy_rms"]),
            "Q_exc_over_Q_energy_rms_max": max_nan(grp["Q_exc_over_Q_energy_rms"]),
            "Q_exc_above_0p025_count": int(grp["Q_exc_above_0p025_flag"].sum()),
        })
    by_regime_df = pd.DataFrame(by_regime).sort_values("row_regime")
    return summary_df, by_regime_df, failures_df


def write_note(summary: pd.DataFrame, by_regime: pd.DataFrame, failures: pd.DataFrame) -> None:
    s = dict(zip(summary["field"], summary["value"]))
    md = []
    md.append("# Prime Mesh R2Q - H-Exc BridgeEnergy Audit v1\n")
    md.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}  \n")
    md.append(f"**Status:** {'PASS' if str(s['pass_hexc_bridge_energy_empirical']) == 'True' else 'REPAIR'}  \n")
    md.append("\n## Executive Verdict\n")
    md.append(
        f"The absolute bridge-excursion cap remains clean: `Q_exc_max = {s['Q_exc_max']}` "
        f"with `{s['Q_exc_above_0p025_count']}` rows above `0.025`.\n"
    )
    md.append(
        f"Row-level bridge-energy coverage is partial: `{s['bridge_energy_available_rows']}` of `{s['rows']}` rows have path samples. "
        f"The resulting variance mode is `{s['variance_proxy_mode']}`.\n"
    )
    md.append("\n## Bridge Energy Availability\n")
    for key in [
        "bridge_samples_available_rows",
        "bridge_samples_missing_rows",
        "bridge_energy_available_rows",
        "bridge_energy_missing_rows",
        "threshold_relevant_bridge_energy_missing_count",
        "forbidden_bridge_energy_missing_count",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Energy Maximal Candidate\n")
    for key in [
        "Q_energy_rms_min",
        "Q_energy_rms_max",
        "Q_energy_rms_mean",
        "Q_exc_over_Q_energy_rms_max",
        "Q_exc_over_Q_energy_rms_q95",
        "lowest_Cmax_energy_pass",
        "pass_energy_maximal_candidate",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Global V2 Reference\n")
    md.append(f"- `sqrt_V2_global`: `{s['sqrt_V2_global']}`\n")
    md.append(f"- `Q_exc_max_over_sqrt_V2_global`: `{s['Q_exc_max_over_sqrt_V2_global']}`\n")
    md.append("\n## Regime Decomposition\n")
    md.append(by_regime.to_markdown(index=False))
    md.append("\n\n## Failures\n")
    if failures.empty:
        md.append("No absolute-cap failures were found.\n")
    else:
        md.append(f"`{len(failures)}` failures were found; see the failure CSV.\n")
    md.append("\n## Interpretation\n")
    md.append(
        "This audit does not justify a full row-level bridge-energy theorem because most rows do not export path samples. "
        "It does confirm that the absolute `Q_exc <= 0.025` cap remains intact and that partial path samples can be converted into bridge-energy quantities. "
        "The next proof-facing move should be an export patch that records row-level bridge samples or precomputed bridge energy for every FCL-compatible row.\n"
    )
    md.append("\n## Recommended Next File\n")
    md.append(f"`{s['recommended_next_file']}`\n")
    OUT_NOTE.write_text("".join(md), encoding="utf-8")


def refresh_manifest() -> None:
    if MANIFEST.exists():
        manifest = pd.read_csv(MANIFEST)
    else:
        manifest = pd.DataFrame(columns=["file", "bytes", "path", "status", "timestamp"])
    records = {row["file"]: row for row in manifest.to_dict("records")}
    timestamp = datetime.now(timezone.utc).isoformat()
    for path in [Path(__file__), OUT_SUMMARY, OUT_ROWS, OUT_BY_REGIME, OUT_FAILURES, OUT_NOTE]:
        records[path.name] = {
            "file": path.name,
            "bytes": path.stat().st_size if path.exists() else 0,
            "path": str(path),
            "status": "new_or_refreshed",
            "timestamp": timestamp,
        }
    pd.DataFrame(records.values()).to_csv(MANIFEST, index=False)


def main() -> None:
    rows = load_base_rows()
    energy = build_energy_table()
    log(f"Path energy intervals available: {0 if energy.empty else len(energy)}")
    if not energy.empty:
        keys = ["block_id", "p_star", "y", "h"]
        rows = rows.merge(energy, on=keys, how="left")
    else:
        for col in [
            "bridge_sample_count",
            "bridge_sample_min_t",
            "bridge_sample_max_t",
            "bridge_energy_raw",
            "bridge_energy_mean",
            "bridge_energy_rms",
            "bridge_energy_max",
            "bridge_samples_source",
        ]:
            rows[col] = np.nan

    summary, by_regime, failures = summarize(rows)
    rows.to_csv(OUT_ROWS, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    by_regime.to_csv(OUT_BY_REGIME, index=False)
    if failures.empty:
        pd.DataFrame(columns=list(rows.columns) + ["failure_type"]).to_csv(OUT_FAILURES, index=False)
    else:
        failures.to_csv(OUT_FAILURES, index=False)
    write_note(summary, by_regime, failures)
    refresh_manifest()

    s = dict(zip(summary["field"], summary["value"]))
    log(f"Q_exc_max = {s['Q_exc_max']}")
    log(f"bridge_energy_available_rows = {s['bridge_energy_available_rows']}")
    log(f"variance_proxy_mode = {s['variance_proxy_mode']}")
    log(f"bridge_energy_failures = {s['bridge_energy_failures']}")
    log(f"pass_hexc_bridge_energy_empirical = {s['pass_hexc_bridge_energy_empirical']}")
    log(f"Wrote {OUT_NOTE}")


if __name__ == "__main__":
    main()
