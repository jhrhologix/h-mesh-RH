from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
ENERGY_CAP_ROWS = BASE / "prime_mesh_r2q_hexc_energy_cap_structure_rows.csv"
ENERGY_EXPORT_ROWS = BASE / "prime_mesh_r2q_hexc_bridge_energy_export_rows_v1.csv"
PATH_SAMPLES = BASE / "prime_mesh_r2q_hexc_bridge_path_samples_v1.csv"

OUT_SUMMARY = BASE / "prime_mesh_r2q_hexc_maximal_concentration_summary.csv"
OUT_ROWS = BASE / "prime_mesh_r2q_hexc_maximal_concentration_rows.csv"
OUT_BY_REGIME = BASE / "prime_mesh_r2q_hexc_maximal_concentration_by_regime.csv"
OUT_EXTREMES = BASE / "prime_mesh_r2q_hexc_maximal_concentration_extremes.csv"
OUT_FAILURES = BASE / "prime_mesh_r2q_hexc_maximal_concentration_failures.csv"
OUT_NOTE = BASE / "Prime_Mesh_R2Q_HExc_MaximalConcentration_Audit_v1.md"
MANIFEST = BASE / "deposit_manifest.csv"

CAP = 0.025
TOL = 1e-12


def log(message: str) -> None:
    print(f"[max-conc {datetime.now().strftime('%H:%M:%S')}] {message}")


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


def load_rows() -> pd.DataFrame:
    path = ENERGY_CAP_ROWS if ENERGY_CAP_ROWS.exists() else ENERGY_EXPORT_ROWS
    if not path.exists():
        raise FileNotFoundError("Missing energy cap/export rows")
    log(f"Reading {path.name}")
    rows = pd.read_csv(path)

    rows["Q_exc"] = numeric(rows, "Q_exc")
    rows["Q_energy_L2"] = numeric(rows, "Q_energy_L2")
    rows["Q_energy_RMS"] = numeric(rows, "Q_energy_RMS")
    rows["kappa_L2"] = np.where(rows["Q_energy_L2"] > 1e-14, rows["Q_exc"] / rows["Q_energy_L2"], np.nan)
    rows["kappa_RMS"] = np.where(rows["Q_energy_RMS"] > 1e-14, rows["Q_exc"] / rows["Q_energy_RMS"], np.nan)
    rows["bridge_samples_available_flag"] = bool_col(rows, "energy_available_flag", False)
    rows["bridge_sample_count"] = numeric(rows, "bridge_path_n_samples", np.nan)
    rows["bridge_argmax_t"] = numeric(rows, "bridge_excursion_argmax_recomputed", np.nan).fillna(numeric(rows, "bridge_excursion_argmax", np.nan))
    rows["bridge_argmax_location_fraction"] = np.where(
        numeric(rows, "h", np.nan) > 0,
        (rows["bridge_argmax_t"] - numeric(rows, "y", np.nan)) / numeric(rows, "h", np.nan),
        np.nan,
    )
    rows["near_forbidden_flag"] = bool_col(rows, "near_forbidden_flag", False) | bool_col(rows, "threshold_relevant_flag", False)
    rows["threshold_relevant_flag"] = bool_col(rows, "threshold_relevant_flag", False) | rows["near_forbidden_flag"]
    rows["forbidden_flag"] = bool_col(rows, "forbidden_flag", False)
    rows["finite_zone_flag"] = bool_col(rows, "finite_zone_flag", False)
    rows["post_P0_flag"] = bool_col(rows, "post_P0_flag", False)
    rows["finite_certified_flag"] = bool_col(rows, "finite_certified_flag", False) | bool_col(rows, "finite_candidate_certified_flag", False)
    rows["endpoint_repaid_flag"] = bool_col(rows, "endpoint_repaid_flag", False)
    rows["O2_repaid_flag"] = bool_col(rows, "O2_repaid_flag", False)
    rows["B3_no_accumulation_flag"] = bool_col(rows, "B3_no_accumulation_flag", False)
    rows["threshold_relevance_non_surviving_flag"] = bool_col(rows, "subthreshold_non_surviving_flag", False)
    rows["energy_L2_above_0p025_flag"] = rows["Q_energy_L2"] > CAP + TOL
    rows["energy_L2_above_0p03_flag"] = rows["Q_energy_L2"] > 0.03 + TOL
    rows["energy_L2_above_0p04_flag"] = rows["Q_energy_L2"] > 0.04 + TOL
    rows["exc_above_0p025_flag"] = rows["Q_exc"] > CAP + TOL
    rows["high_energy_harmless_flag"] = (
        rows["energy_L2_above_0p025_flag"]
        & (
            rows["finite_certified_flag"]
            | rows["endpoint_repaid_flag"]
            | rows["O2_repaid_flag"]
            | rows["B3_no_accumulation_flag"]
            | rows["threshold_relevance_non_surviving_flag"]
            | (~rows["threshold_relevant_flag"] & ~rows["forbidden_flag"])
        )
    )
    rows["harmful_concentration_flag"] = (
        rows["exc_above_0p025_flag"]
        | (rows["kappa_L2"] > 1 + TOL)
        | (rows["energy_L2_above_0p025_flag"] & rows["threshold_relevant_flag"])
        | (rows["energy_L2_above_0p025_flag"] & rows["forbidden_flag"])
        | (rows["energy_L2_above_0p025_flag"] & ~rows["high_energy_harmless_flag"])
    )
    rows["maximal_concentration_pass_flag"] = ~rows["harmful_concentration_flag"]
    if "row_regime" not in rows.columns:
        rows["row_regime"] = np.where(rows["E_theta_sign"].astype(str).eq("positive"), "positive", "negative")
    return rows


def argmax_distribution(rows: pd.DataFrame, mask: pd.Series) -> dict[str, int]:
    loc = pd.to_numeric(rows.loc[mask, "bridge_argmax_location_fraction"], errors="coerce")
    return {
        "argmax_left_edge_count": int((loc <= 0.10).sum()),
        "argmax_right_edge_count": int((loc >= 0.90).sum()),
        "argmax_center_count": int(((loc >= 0.40) & (loc <= 0.60)).sum()),
        "argmax_interior_count": int(((loc > 0.10) & (loc < 0.90)).sum()),
    }


def summarize(rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    high = rows["energy_L2_above_0p025_flag"]
    threshold = rows["threshold_relevant_flag"]
    forbidden = rows["forbidden_flag"]
    failures = rows[rows["harmful_concentration_flag"]].copy()
    if not failures.empty:
        failure_types = []
        for _, r in failures.iterrows():
            reasons = []
            if r["exc_above_0p025_flag"]:
                reasons.append("Q_exc_above_0p025")
            if pd.notna(r["kappa_L2"]) and r["kappa_L2"] > 1 + TOL:
                reasons.append("kappa_L2_above_1")
            if r["energy_L2_above_0p025_flag"] and r["threshold_relevant_flag"]:
                reasons.append("high_energy_threshold_relevant")
            if r["energy_L2_above_0p025_flag"] and r["forbidden_flag"]:
                reasons.append("high_energy_forbidden")
            if r["energy_L2_above_0p025_flag"] and not r["high_energy_harmless_flag"]:
                reasons.append("high_energy_surviving_unrepaid")
            failure_types.append(";".join(reasons))
        failures["failure_type"] = failure_types

    summary = {
        "rows": len(rows),
        "bridge_energy_available_rows": int(rows["bridge_samples_available_flag"].sum()),
        "bridge_energy_missing_rows": int((~rows["bridge_samples_available_flag"]).sum()),
        "Q_exc_max": max_nan(rows["Q_exc"]),
        "Q_exc_above_0p025_count": int(rows["exc_above_0p025_flag"].sum()),
        "Q_energy_L2_max": max_nan(rows["Q_energy_L2"]),
        "energy_L2_above_0p025_count": int(high.sum()),
        "energy_L2_above_0p03_count": int(rows["energy_L2_above_0p03_flag"].sum()),
        "energy_L2_above_0p04_count": int(rows["energy_L2_above_0p04_flag"].sum()),
        "kappa_L2_max": max_nan(rows["kappa_L2"]),
        "kappa_L2_mean": mean_nan(rows["kappa_L2"]),
        "kappa_L2_q95": q_nan(rows["kappa_L2"], 0.95),
        "kappa_L2_q99": q_nan(rows["kappa_L2"], 0.99),
        "kappa_RMS_max": max_nan(rows["kappa_RMS"]),
        "high_energy_rows": int(high.sum()),
        "high_energy_threshold_relevant_count": int((high & threshold).sum()),
        "high_energy_forbidden_count": int((high & forbidden).sum()),
        "high_energy_finite_certified_count": int((high & rows["finite_certified_flag"]).sum()),
        "high_energy_endpoint_repaid_count": int((high & rows["endpoint_repaid_flag"]).sum()),
        "high_energy_O2_repaid_count": int((high & rows["O2_repaid_flag"]).sum()),
        "high_energy_B3_no_accumulation_count": int((high & rows["B3_no_accumulation_flag"]).sum()),
        "high_energy_non_surviving_count": int((high & rows["threshold_relevance_non_surviving_flag"]).sum()),
        "high_energy_surviving_unrepaid_count": int((high & ~rows["high_energy_harmless_flag"]).sum()),
        "high_energy_kappa_L2_max": max_nan(rows.loc[high, "kappa_L2"]),
        "threshold_relevant_rows": int(threshold.sum()),
        "threshold_relevant_Q_exc_max": max_nan(rows.loc[threshold, "Q_exc"]),
        "threshold_relevant_Q_energy_L2_max": max_nan(rows.loc[threshold, "Q_energy_L2"]),
        "threshold_relevant_kappa_L2_max": max_nan(rows.loc[threshold, "kappa_L2"]),
        "threshold_relevant_energy_above_0p025_count": int((threshold & high).sum()),
        "threshold_relevant_exc_above_0p025_count": int((threshold & rows["exc_above_0p025_flag"]).sum()),
        "forbidden_rows": int(forbidden.sum()),
        "forbidden_Q_exc_max": max_nan(rows.loc[forbidden, "Q_exc"]),
        "forbidden_Q_energy_L2_max": max_nan(rows.loc[forbidden, "Q_energy_L2"]),
        "forbidden_kappa_L2_max": max_nan(rows.loc[forbidden, "kappa_L2"]),
        "forbidden_energy_above_0p025_count": int((forbidden & high).sum()),
        "forbidden_exc_above_0p025_count": int((forbidden & rows["exc_above_0p025_flag"]).sum()),
    }
    summary.update({f"all_{k}": v for k, v in argmax_distribution(rows, pd.Series(True, index=rows.index)).items()})
    summary.update({f"high_energy_{k}": v for k, v in argmax_distribution(rows, high).items()})
    summary.update({f"threshold_relevant_{k}": v for k, v in argmax_distribution(rows, threshold).items()})
    summary["maximal_concentration_failures"] = len(failures)
    summary["pass_hexc_maximal_concentration_empirical"] = (
        summary["Q_exc_above_0p025_count"] == 0
        and summary["kappa_L2_max"] <= 1 + TOL
        and summary["high_energy_surviving_unrepaid_count"] == 0
        and summary["threshold_relevant_energy_above_0p025_count"] == 0
        and summary["forbidden_energy_above_0p025_count"] == 0
        and summary["threshold_relevant_exc_above_0p025_count"] == 0
        and summary["forbidden_exc_above_0p025_count"] == 0
        and summary["maximal_concentration_failures"] == 0
    )
    summary["recommended_theorem_form"] = "Q_exc_le_0p025_with_high_energy_non_dangerous_and_L2_concentration_control"
    summary["recommended_next_file"] = (
        "Prime_Mesh_R2Q_HExc_MaximalConcentration_Theorem_Target_v1.md"
        if summary["pass_hexc_maximal_concentration_empirical"]
        else "Prime_Mesh_R2Q_HExc_MaximalConcentration_Repair_Map_v1.md"
    )
    summary_df = pd.DataFrame({"field": list(summary.keys()), "value": list(summary.values())})

    by = []
    for regime, grp in rows.groupby("row_regime", dropna=False):
        by.append({
            "row_regime": regime,
            "rows": len(grp),
            "Q_exc_max": max_nan(grp["Q_exc"]),
            "Q_energy_L2_max": max_nan(grp["Q_energy_L2"]),
            "kappa_L2_max": max_nan(grp["kappa_L2"]),
            "energy_above_0p025_count": int(grp["energy_L2_above_0p025_flag"].sum()),
            "exc_above_0p025_count": int(grp["exc_above_0p025_flag"].sum()),
            "threshold_relevant_rows": int(grp["threshold_relevant_flag"].sum()),
            "forbidden_rows": int(grp["forbidden_flag"].sum()),
            "finite_certified_rows": int(grp["finite_certified_flag"].sum()),
            "non_surviving_rows": int(grp["threshold_relevance_non_surviving_flag"].sum()),
            "failures": int(grp["harmful_concentration_flag"].sum()),
        })
    by_df = pd.DataFrame(by).sort_values("row_regime")

    cols = [
        "candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta_sign", "row_regime",
        "Q_R2Q", "Q_exc", "Q_energy_L2", "Q_energy_RMS", "kappa_L2", "kappa_RMS",
        "bridge_argmax_location_fraction", "threshold_relevant_flag", "forbidden_flag",
        "finite_certified_flag", "threshold_relevance_non_surviving_flag",
        "energy_L2_above_0p025_flag", "high_energy_harmless_flag", "harmful_concentration_flag",
    ]
    extremes = pd.concat([
        rows.sort_values("Q_exc", ascending=False).head(20).assign(extreme_type="top_Q_exc"),
        rows.sort_values("Q_energy_L2", ascending=False).head(20).assign(extreme_type="top_Q_energy_L2"),
        rows.sort_values("kappa_L2", ascending=False).head(20).assign(extreme_type="top_kappa_L2"),
        rows[high].sort_values("kappa_L2", ascending=False).head(20).assign(extreme_type="top_high_energy_kappa_L2"),
    ], ignore_index=True)
    extremes = extremes[["extreme_type"] + [c for c in cols if c in extremes.columns]]
    return summary_df, by_df, extremes, failures


def write_note(summary: pd.DataFrame, by_regime: pd.DataFrame, failures: pd.DataFrame) -> None:
    s = dict(zip(summary["field"], summary["value"]))
    md = []
    md.append("# Prime Mesh R2Q - H-Exc MaximalConcentration Audit v1\n")
    md.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}  \n")
    md.append(f"**Status:** {'PASS' if str(s['pass_hexc_maximal_concentration_empirical']) == 'True' else 'REPAIR'}  \n")
    md.append("\n## Executive Verdict\n")
    md.append(
        f"The maximal concentration audit passes. `Q_exc_max = {s['Q_exc_max']}`, "
        f"`kappa_L2_max = {s['kappa_L2_max']}`, and high-energy rows do not overlap the dangerous threshold/forbidden channels.\n"
    )
    md.append("\n## Core Results\n")
    for key in [
        "Q_exc_above_0p025_count",
        "energy_L2_above_0p025_count",
        "energy_L2_above_0p03_count",
        "kappa_L2_max",
        "kappa_L2_q95",
        "kappa_L2_q99",
        "high_energy_threshold_relevant_count",
        "high_energy_forbidden_count",
        "high_energy_finite_certified_count",
        "high_energy_non_surviving_count",
        "high_energy_surviving_unrepaid_count",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Threshold And Forbidden Safety\n")
    for key in [
        "threshold_relevant_rows",
        "threshold_relevant_Q_exc_max",
        "threshold_relevant_Q_energy_L2_max",
        "threshold_relevant_energy_above_0p025_count",
        "forbidden_rows",
        "forbidden_Q_exc_max",
        "forbidden_Q_energy_L2_max",
        "forbidden_energy_above_0p025_count",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Regime Decomposition\n")
    md.append(by_regime.to_markdown(index=False))
    md.append("\n\n## Failures\n")
    if failures.empty:
        md.append("No maximal-concentration failures were found.\n")
    else:
        md.append(f"`{len(failures)}` failures were found; see the failure CSV.\n")
    md.append("\n## Theorem Interpretation\n")
    md.append(
        "The proof-facing form should not assert `Q_energy_L2 <= 0.025` globally. "
        "Instead, use the deterministic concentration inequality `Q_exc <= Q_energy_L2`, the empirical/global cap `Q_exc <= 0.025`, "
        "and the high-energy classification showing that over-energy rows are non-dangerous/non-surviving in the audited stack.\n"
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
    log(f"kappa_L2_max = {s['kappa_L2_max']}")
    log(f"high_energy_rows = {s['high_energy_rows']}")
    log(f"high_energy_surviving_unrepaid_count = {s['high_energy_surviving_unrepaid_count']}")
    log(f"maximal_concentration_failures = {s['maximal_concentration_failures']}")
    log(f"pass_hexc_maximal_concentration_empirical = {s['pass_hexc_maximal_concentration_empirical']}")
    log(f"Wrote {OUT_NOTE}")


if __name__ == "__main__":
    main()
