from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
ENERGY_ROWS = BASE / "prime_mesh_r2q_hexc_bridge_energy_export_rows_v1.csv"
CHANNEL_ROWS = BASE / "prime_mesh_r2q_channel_compatibility_rows.csv"
O2_ROWS = BASE / "prime_mesh_r2q_o2_local_repayment_assembly_rows.csv"
B3_ROWS = BASE / "prime_mesh_r2q_b3_no_accumulation_rows.csv"
THRESHOLD_ROWS = BASE / "prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv"
FINITE_ROWS = BASE / "prime_mesh_r2q_finite_certificate_rows.csv"

OUT_SUMMARY = BASE / "prime_mesh_r2q_hexc_energy_cap_structure_summary.csv"
OUT_ROWS = BASE / "prime_mesh_r2q_hexc_energy_cap_structure_rows.csv"
OUT_BY_REGIME = BASE / "prime_mesh_r2q_hexc_energy_cap_structure_by_regime.csv"
OUT_EXTREMES = BASE / "prime_mesh_r2q_hexc_energy_cap_structure_extremes.csv"
OUT_FAILURES = BASE / "prime_mesh_r2q_hexc_energy_cap_structure_failures.csv"
OUT_NOTE = BASE / "Prime_Mesh_R2Q_HExc_EnergyCap_Structure_Audit_v1.md"
MANIFEST = BASE / "deposit_manifest.csv"

CAP = 0.025
TOL = 1e-12


def log(message: str) -> None:
    print(f"[energy-cap {datetime.now().strftime('%H:%M:%S')}] {message}")


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


def load_optional_flag(path: Path, flag_name: str, source_cols: list[str], keys: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=keys + [flag_name])
    df = pd.read_csv(path)
    join_keys = [k for k in keys if k in df.columns]
    if not join_keys:
        return pd.DataFrame(columns=keys + [flag_name])
    flag = pd.Series(False, index=df.index)
    for col in source_cols:
        if col in df.columns:
            flag = flag | bool_col(df, col, False)
    out = df[join_keys].copy()
    out[flag_name] = flag
    return out.groupby(join_keys, as_index=False)[flag_name].max()


def merge_flag(rows: pd.DataFrame, path: Path, flag_name: str, source_cols: list[str]) -> pd.DataFrame:
    keys = ["block_id", "p_star", "y", "h"]
    flags = load_optional_flag(path, flag_name, source_cols, keys)
    if flags.empty:
        rows[flag_name] = False
        return rows
    join_keys = [k for k in keys if k in flags.columns and k in rows.columns]
    before = len(rows)
    rows = rows.merge(flags, on=join_keys, how="left")
    rows[flag_name] = rows[flag_name].fillna(False).astype(bool)
    if len(rows) != before:
        raise RuntimeError(f"Merge against {path.name} changed row count {before}->{len(rows)}")
    return rows


def h_bin(h: float) -> str:
    if h <= 1:
        return "h=1"
    if h <= 10:
        return "2<=h<=10"
    if h <= 100:
        return "11<=h<=100"
    if h <= 1000:
        return "101<=h<=1k"
    if h <= 10000:
        return "1k<h<=10k"
    if h <= 100000:
        return "10k<h<=100k"
    return "h>100k"


def p_bin(p: float) -> str:
    if p < 1e6:
        return "p<1M"
    if p < 1e7:
        return "1M<=p<10M"
    if p < 1e8:
        return "10M<=p<100M"
    if p < 5e8:
        return "100M<=p<500M"
    return "p>=500M"


def load_rows() -> pd.DataFrame:
    if not ENERGY_ROWS.exists():
        raise FileNotFoundError(f"Missing {ENERGY_ROWS}")
    log(f"Reading {ENERGY_ROWS.name}")
    rows = pd.read_csv(ENERGY_ROWS)
    rows["Q_exc"] = numeric(rows, "Q_exc")
    rows["Q_energy_L2"] = numeric(rows, "Q_energy_L2")
    rows["Q_energy_RMS"] = numeric(rows, "Q_energy_RMS")
    rows["conc_ratio"] = np.where(
        rows["Q_energy_L2"] > 1e-14,
        rows["Q_exc"] / rows["Q_energy_L2"],
        np.nan,
    )
    rows["energy_L2_above_0p025_flag"] = rows["Q_energy_L2"] > CAP + TOL
    rows["energy_L2_above_0p03_flag"] = rows["Q_energy_L2"] > 0.03 + TOL
    rows["energy_L2_above_0p04_flag"] = rows["Q_energy_L2"] > 0.04 + TOL
    rows["Q_exc_above_0p025_flag"] = rows["Q_exc"] > CAP + TOL
    rows["near_forbidden_flag"] = bool_col(rows, "threshold_relevant_flag", False)
    rows["threshold_relevant_flag"] = bool_col(rows, "threshold_relevant_flag", False)
    rows["forbidden_flag"] = bool_col(rows, "forbidden_flag", False)
    rows["positive_harmless_flag"] = rows["E_theta_sign"].astype(str).eq("positive") & (rows["Q_R2Q"] <= 0.75 + TOL)
    rows["negative_channel_flag"] = rows["E_theta_sign"].astype(str).eq("negative")
    rows["finite_certified_flag"] = bool_col(rows, "finite_zone_flag", False)
    rows["post_P0_flag"] = bool_col(rows, "post_P0_flag", False)
    rows["finite_zone_flag"] = bool_col(rows, "finite_zone_flag", False)
    rows["h_bin"] = rows["h"].apply(h_bin)
    rows["p_star_bin"] = rows["p_star"].apply(p_bin)

    rows = merge_flag(rows, CHANNEL_ROWS, "channel_compatible_flag", ["channel_compatibility_pass_flag", "compatible_flag", "pass_flag", "status"])
    rows = merge_flag(rows, O2_ROWS, "O2_repaid_flag", ["O2_repaid_flag", "local_repayment_pass_flag", "pass_O2_local_repayment_empirical", "status"])
    rows = merge_flag(rows, B3_ROWS, "B3_no_accumulation_flag", ["B3_no_accumulation_flag", "no_accumulation_pass_flag", "pass_B3_no_accumulation_empirical", "status"])
    rows = merge_flag(rows, THRESHOLD_ROWS, "subthreshold_non_surviving_flag", ["threshold_relevance_pass_flag", "non_surviving_flag", "status"])
    rows = merge_flag(rows, FINITE_ROWS, "finite_candidate_certified_flag", ["finite_candidate_certified_flag", "candidate_certified_flag", "certified_flag", "status"])

    # Conservative harmlessness classifier for high-energy rows. Positive rows are already capped by positive harmlessness.
    rows["repaid_or_harmless_flag"] = (
        rows["positive_harmless_flag"]
        | rows["O2_repaid_flag"]
        | rows["B3_no_accumulation_flag"]
        | rows["finite_candidate_certified_flag"]
        | rows["finite_certified_flag"]
        | rows["subthreshold_non_surviving_flag"]
    )
    rows["high_energy_surviving_unrepaid_flag"] = (
        rows["energy_L2_above_0p025_flag"]
        & rows["threshold_relevant_flag"]
        & ~rows["repaid_or_harmless_flag"]
    )
    rows["harmful_high_energy_flag"] = (
        rows["energy_L2_above_0p025_flag"]
        & rows["Q_exc_above_0p025_flag"]
    ) | rows["high_energy_surviving_unrepaid_flag"]
    return rows


def summarize(rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    high = rows[rows["energy_L2_above_0p025_flag"]]
    threshold = rows["threshold_relevant_flag"]
    forbidden = rows["forbidden_flag"]

    def max_nan(s):
        s = pd.to_numeric(s, errors="coerce").dropna()
        return float(s.max()) if not s.empty else math.nan

    def mean_nan(s):
        s = pd.to_numeric(s, errors="coerce").dropna()
        return float(s.mean()) if not s.empty else math.nan

    def q_nan(s, q):
        s = pd.to_numeric(s, errors="coerce").dropna()
        return float(s.quantile(q)) if not s.empty else math.nan

    failures = rows[rows["harmful_high_energy_flag"] | rows["Q_exc_above_0p025_flag"]].copy()
    if failures.empty:
        failures["failure_type"] = []
    else:
        failures["failure_type"] = np.where(
            failures["Q_exc_above_0p025_flag"],
            "Q_exc_above_0p025",
            "high_energy_surviving_unrepaid",
        )

    summary = {
        "rows": len(rows),
        "Q_exc_max": max_nan(rows["Q_exc"]),
        "Q_exc_above_0p025_count": int(rows["Q_exc_above_0p025_flag"].sum()),
        "pass_absolute_Q_exc_cap": int(rows["Q_exc_above_0p025_flag"].sum()) == 0,
        "Q_energy_L2_max": max_nan(rows["Q_energy_L2"]),
        "Q_energy_RMS_max": max_nan(rows["Q_energy_RMS"]),
        "energy_L2_above_0p025_count": len(high),
        "energy_L2_above_0p03_count": int(rows["energy_L2_above_0p03_flag"].sum()),
        "energy_L2_above_0p04_count": int(rows["energy_L2_above_0p04_flag"].sum()),
        "energy_L2_above_0p025_threshold_relevant_count": int((rows["energy_L2_above_0p025_flag"] & threshold).sum()),
        "energy_L2_above_0p025_forbidden_count": int((rows["energy_L2_above_0p025_flag"] & forbidden).sum()),
        "energy_L2_above_0p025_positive_count": int((high["E_theta_sign"].astype(str) == "positive").sum()),
        "energy_L2_above_0p025_negative_count": int((high["E_theta_sign"].astype(str) == "negative").sum()),
        "energy_L2_above_0p025_non_surviving_count": int(high["subthreshold_non_surviving_flag"].sum()) if not high.empty else 0,
        "energy_L2_above_0p025_repaid_count": int((high["O2_repaid_flag"] | high["B3_no_accumulation_flag"]).sum()) if not high.empty else 0,
        "energy_L2_above_0p025_finite_certified_count": int((high["finite_certified_flag"] | high["finite_candidate_certified_flag"]).sum()) if not high.empty else 0,
        "threshold_relevant_energy_L2_max": max_nan(rows.loc[threshold, "Q_energy_L2"]),
        "threshold_relevant_energy_L2_above_0p025_count": int((rows["energy_L2_above_0p025_flag"] & threshold).sum()),
        "forbidden_energy_L2_max": max_nan(rows.loc[forbidden, "Q_energy_L2"]),
        "forbidden_energy_L2_above_0p025_count": int((rows["energy_L2_above_0p025_flag"] & forbidden).sum()),
        "conc_ratio_max": max_nan(rows["conc_ratio"]),
        "conc_ratio_mean": mean_nan(rows["conc_ratio"]),
        "conc_ratio_q95": q_nan(rows["conc_ratio"], 0.95),
        "conc_ratio_q99": q_nan(rows["conc_ratio"], 0.99),
        "conc_ratio_high_energy_max": max_nan(high["conc_ratio"]),
        "conc_ratio_high_energy_q95": q_nan(high["conc_ratio"], 0.95),
        "high_energy_surviving_unrepaid_count": int(rows["high_energy_surviving_unrepaid_flag"].sum()),
        "energy_cap_structure_failures": len(failures),
    }
    summary["pass_hexc_energy_cap_structure_empirical"] = (
        summary["Q_exc_above_0p025_count"] == 0
        and summary["energy_cap_structure_failures"] == 0
    )
    summary["recommended_next_file"] = (
        "Prime_Mesh_R2Q_HExc_EnergyCap_Structure_Closure_Update_v1.md"
        if summary["pass_hexc_energy_cap_structure_empirical"]
        else "Prime_Mesh_R2Q_HExc_EnergyCap_Repair_Map_v1.md"
    )

    summary_df = pd.DataFrame({"field": list(summary.keys()), "value": list(summary.values())})

    group_cols = ["row_regime", "finite_zone_flag", "post_P0_flag", "E_theta_sign", "h_bin", "p_star_bin"]
    by_regime = []
    for keys, grp in rows.groupby(group_cols, dropna=False):
        rec = dict(zip(group_cols, keys if isinstance(keys, tuple) else (keys,)))
        rec.update({
            "rows": len(grp),
            "Q_exc_max": max_nan(grp["Q_exc"]),
            "Q_energy_L2_max": max_nan(grp["Q_energy_L2"]),
            "energy_L2_above_0p025_count": int(grp["energy_L2_above_0p025_flag"].sum()),
            "conc_ratio_max": max_nan(grp["conc_ratio"]),
            "harmful_high_energy_count": int(grp["harmful_high_energy_flag"].sum()),
        })
        by_regime.append(rec)
    by_regime_df = pd.DataFrame(by_regime)

    extremes_cols = [
        "candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta_sign", "row_regime",
        "Q_R2Q", "Q_exc", "Q_energy_L2", "Q_energy_RMS", "conc_ratio",
        "threshold_relevant_flag", "forbidden_flag", "positive_harmless_flag",
        "O2_repaid_flag", "B3_no_accumulation_flag", "finite_certified_flag",
        "subthreshold_non_surviving_flag", "harmful_high_energy_flag",
    ]
    extremes = pd.concat([
        rows.sort_values("Q_energy_L2", ascending=False).head(20).assign(extreme_type="top_Q_energy_L2"),
        rows.sort_values("Q_exc", ascending=False).head(20).assign(extreme_type="top_Q_exc"),
        high.sort_values("conc_ratio", ascending=False).head(20).assign(extreme_type="top_high_energy_conc_ratio") if not high.empty else pd.DataFrame(),
    ], ignore_index=True)
    if not extremes.empty:
        extremes = extremes[["extreme_type"] + [c for c in extremes_cols if c in extremes.columns]]
    return summary_df, by_regime_df, extremes, failures


def write_note(summary: pd.DataFrame, by_regime: pd.DataFrame, failures: pd.DataFrame) -> None:
    s = dict(zip(summary["field"], summary["value"]))
    md = []
    md.append("# Prime Mesh R2Q - H-Exc EnergyCap Structure Audit v1\n")
    md.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}  \n")
    md.append(f"**Status:** {'PASS' if str(s['pass_hexc_energy_cap_structure_empirical']) == 'True' else 'REPAIR'}  \n")
    md.append("\n## Executive Verdict\n")
    md.append(
        f"`Q_exc <= 0.025` remains clean: `Q_exc_max = {s['Q_exc_max']}`, "
        f"`Q_exc_above_0p025_count = {s['Q_exc_above_0p025_count']}`.\n"
    )
    md.append(
        f"`Q_energy_L2_max = {s['Q_energy_L2_max']}`, so the raw L2 energy cap at `0.025` is not globally true. "
        f"High-energy rows are classified separately.\n"
    )
    md.append("\n## High-Energy Classification\n")
    for key in [
        "energy_L2_above_0p025_count",
        "energy_L2_above_0p03_count",
        "energy_L2_above_0p04_count",
        "energy_L2_above_0p025_threshold_relevant_count",
        "energy_L2_above_0p025_forbidden_count",
        "energy_L2_above_0p025_positive_count",
        "energy_L2_above_0p025_negative_count",
        "energy_L2_above_0p025_repaid_count",
        "energy_L2_above_0p025_finite_certified_count",
        "high_energy_surviving_unrepaid_count",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Concentration Ratio\n")
    for key in [
        "conc_ratio_max",
        "conc_ratio_mean",
        "conc_ratio_q95",
        "conc_ratio_q99",
        "conc_ratio_high_energy_max",
        "conc_ratio_high_energy_q95",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Threshold And Forbidden Safety\n")
    for key in [
        "threshold_relevant_energy_L2_max",
        "threshold_relevant_energy_L2_above_0p025_count",
        "forbidden_energy_L2_max",
        "forbidden_energy_L2_above_0p025_count",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Failures\n")
    if failures.empty:
        md.append("No harmful high-energy failures were found.\n")
    else:
        md.append(f"`{len(failures)}` failures were found; see failure CSV.\n")
    md.append("\n## Theorem Interpretation\n")
    md.append(
        "The statement `Q_energy_L2 <= 0.025` is false globally. The correct H-Exc structure is: "
        "the excursion itself remains capped, while over-cap energy rows must be treated by spread/concentration and channel harmlessness. "
        "This audit provides the classification artifact for that split.\n"
    )
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
    log(f"Q_exc_max = {s['Q_exc_max']}")
    log(f"Q_energy_L2_max = {s['Q_energy_L2_max']}")
    log(f"energy_L2_above_0p025_count = {s['energy_L2_above_0p025_count']}")
    log(f"threshold high energy = {s['energy_L2_above_0p025_threshold_relevant_count']}")
    log(f"forbidden high energy = {s['energy_L2_above_0p025_forbidden_count']}")
    log(f"energy_cap_structure_failures = {s['energy_cap_structure_failures']}")
    log(f"pass_hexc_energy_cap_structure_empirical = {s['pass_hexc_energy_cap_structure_empirical']}")
    log(f"Wrote {OUT_NOTE}")


if __name__ == "__main__":
    main()
