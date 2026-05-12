from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
MC_ROWS = BASE / "prime_mesh_r2q_hexc_maximal_concentration_rows.csv"
ENERGY_ROWS = BASE / "prime_mesh_r2q_hexc_bridge_energy_export_rows_v1.csv"

OUT_SUMMARY = BASE / "prime_mesh_r2q_hexc_highenergy_scalecutoff_summary.csv"
OUT_ROWS = BASE / "prime_mesh_r2q_hexc_highenergy_scalecutoff_rows.csv"
OUT_RULES = BASE / "prime_mesh_r2q_hexc_highenergy_scalecutoff_rules.csv"
OUT_FAILURES = BASE / "prime_mesh_r2q_hexc_highenergy_scalecutoff_failures.csv"
OUT_NOTE = BASE / "Prime_Mesh_R2Q_HExc_HighEnergy_ScaleCutoff_Audit_v1.md"
MANIFEST = BASE / "deposit_manifest.csv"

P0 = 500_000_000
HIGH = 0.025
VERY_HIGH = 0.03
TOL = 1e-12


def log(message: str) -> None:
    print(f"[highenergy-cutoff {datetime.now().strftime('%H:%M:%S')}] {message}")


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


def load_rows() -> pd.DataFrame:
    path = MC_ROWS if MC_ROWS.exists() else ENERGY_ROWS
    if not path.exists():
        raise FileNotFoundError("Missing maximal concentration or bridge energy rows")
    log(f"Reading {path.name}")
    rows = pd.read_csv(path)
    rows["P0"] = P0
    rows["Q_energy_L2"] = numeric(rows, "Q_energy_L2")
    rows["Q_energy_RMS"] = numeric(rows, "Q_energy_RMS")
    rows["Q_R2Q"] = numeric(rows, "Q_R2Q")
    rows["Q_exc"] = numeric(rows, "Q_exc")
    rows["p_star"] = numeric(rows, "p_star")
    rows["x"] = numeric(rows, "x")
    rows["y"] = numeric(rows, "y")
    rows["h"] = numeric(rows, "h")
    rows["post_P0_by_pstar"] = rows["p_star"] >= P0
    rows["post_P0_by_x"] = rows["x"] >= P0
    rows["post_P0_by_y"] = rows["y"] >= P0
    rows["finite_zone_flag"] = bool_col(rows, "finite_zone_flag", False)
    rows["finite_certified_flag"] = bool_col(rows, "finite_certified_flag", False) | bool_col(rows, "finite_candidate_certified_flag", False)
    rows["threshold_relevant_flag"] = (rows["Q_R2Q"] > 0.75 + TOL) | bool_col(rows, "threshold_relevant_flag", False)
    rows["forbidden_flag"] = (rows["Q_R2Q"] > 1.0 + TOL) | bool_col(rows, "forbidden_flag", False)
    rows["high_energy_flag"] = rows["Q_energy_L2"] > HIGH + TOL
    rows["very_high_energy_flag"] = rows["Q_energy_L2"] > VERY_HIGH + TOL
    rows["non_surviving_flag"] = bool_col(rows, "threshold_relevance_non_surviving_flag", False) | bool_col(rows, "subthreshold_non_surviving_flag", False)
    rows["endpoint_repaid_flag"] = bool_col(rows, "endpoint_repaid_flag", False)
    rows["B3_no_accumulation_flag"] = bool_col(rows, "B3_no_accumulation_flag", False)
    rows["O2_repaid_flag"] = bool_col(rows, "O2_repaid_flag", False)
    rows["channel"] = np.where(rows["E_theta_sign"].astype(str).eq("negative"), "negative", "positive")
    rows["h_over_x"] = rows["h"] / rows["x"].replace(0, np.nan)
    rows["rho_proxy"] = rows["h_over_x"]
    rows["log_pstar"] = np.log(rows["p_star"].clip(lower=2))
    rows["surviving_proxy_flag"] = ~(
        rows["finite_certified_flag"]
        | rows["non_surviving_flag"]
        | rows["endpoint_repaid_flag"]
        | rows["B3_no_accumulation_flag"]
        | ((rows["Q_R2Q"] <= 0.75 + TOL) & rows["non_surviving_flag"])
    )
    if "row_regime" not in rows.columns:
        rows["row_regime"] = np.where(rows["E_theta_sign"].astype(str).eq("positive"), "positive", "negative")
    rows["status"] = "pass"
    return rows


def rule_candidates(rows: pd.DataFrame) -> pd.DataFrame:
    high = rows["high_energy_flag"]
    rules = []
    candidates = []
    for col, op in [
        ("p_star", "<"),
        ("x", "<"),
        ("y", "<"),
        ("h", "<="),
        ("h_over_x", ">"),
        ("rho_proxy", ">"),
        ("log_pstar", "<"),
    ]:
        values = pd.to_numeric(rows.loc[high, col], errors="coerce").dropna().unique()
        for value in values:
            candidates.append((col, op, float(value)))

    for col, op, cut in candidates:
        if op == "<":
            mask = rows[col] <= cut + TOL
            rule = f"{col} <= {cut:g}"
        elif op == "<=":
            mask = rows[col] <= cut + TOL
            rule = f"{col} <= {cut:g}"
        else:
            mask = rows[col] >= cut - TOL
            rule = f"{col} >= {cut:g}"
        captures = int((mask & high).sum())
        misses = int((~mask & high).sum())
        false_pos = mask & ~high
        rules.append({
            "rule": rule,
            "captures_high_energy_count": captures,
            "misses_high_energy_count": misses,
            "false_positive_count": int(false_pos.sum()),
            "threshold_relevant_false_positive_count": int((false_pos & rows["threshold_relevant_flag"]).sum()),
            "forbidden_false_positive_count": int((false_pos & rows["forbidden_flag"]).sum()),
            "surviving_false_positive_count": int((false_pos & rows["surviving_proxy_flag"]).sum()),
            "recommended_status": (
                "clean_high_energy_isolator"
                if misses == 0
                and int((false_pos & rows["threshold_relevant_flag"]).sum()) == 0
                and int((false_pos & rows["forbidden_flag"]).sum()) == 0
                and int((false_pos & rows["surviving_proxy_flag"]).sum()) == 0
                else "diagnostic"
            ),
        })
    out = pd.DataFrame(rules)
    if out.empty:
        return out
    return out.sort_values(
        ["misses_high_energy_count", "threshold_relevant_false_positive_count", "forbidden_false_positive_count", "surviving_false_positive_count", "false_positive_count"],
        ascending=True,
    )


def summarize(rows: pd.DataFrame, rules: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    high = rows["high_energy_flag"]
    very_high = rows["very_high_energy_flag"]
    post_p = rows["post_P0_by_pstar"]
    post_x = rows["post_P0_by_x"]
    post_y = rows["post_P0_by_y"]
    threshold = rows["threshold_relevant_flag"]
    forbidden = rows["forbidden_flag"]

    failures = rows[
        high
        & (
            threshold
            | forbidden
            | rows["surviving_proxy_flag"]
            | ~(rows["finite_certified_flag"] | rows["non_surviving_flag"] | rows["endpoint_repaid_flag"] | rows["B3_no_accumulation_flag"])
        )
    ].copy()
    if not failures.empty:
        failure_types = []
        for _, r in failures.iterrows():
            reasons = []
            if r["threshold_relevant_flag"]:
                reasons.append("high_energy_threshold_relevant")
            if r["forbidden_flag"]:
                reasons.append("high_energy_forbidden")
            if r["surviving_proxy_flag"]:
                reasons.append("high_energy_surviving_proxy")
            if not (r["finite_certified_flag"] or r["non_surviving_flag"] or r["endpoint_repaid_flag"] or r["B3_no_accumulation_flag"]):
                reasons.append("high_energy_not_certified_or_non_surviving")
            failure_types.append(";".join(reasons))
        failures["failure_type"] = failure_types

    best = rules.iloc[0].to_dict() if not rules.empty else {}
    preferred_pass = int((post_p & high).sum()) == 0
    acceptable_pass = (
        int((high & threshold).sum()) == 0
        and int((high & forbidden).sum()) == 0
        and int((high & rows["surviving_proxy_flag"]).sum()) == 0
        and int((high & rows["finite_certified_flag"]).sum()) == int(high.sum())
    )

    summary = {
        "rows": len(rows),
        "bridge_energy_available_rows": int(rows["Q_energy_L2"].notna().sum()),
        "bridge_energy_missing_rows": int(rows["Q_energy_L2"].isna().sum()),
        "P0": P0,
        "high_energy_threshold": HIGH,
        "very_high_energy_threshold": VERY_HIGH,
        "high_energy_rows": int(high.sum()),
        "very_high_energy_rows": int(very_high.sum()),
        "post_P0_pstar_rows": int(post_p.sum()),
        "post_P0_pstar_Q_energy_L2_max": max_nan(rows.loc[post_p, "Q_energy_L2"]),
        "post_P0_pstar_energy_above_0p025_count": int((post_p & high).sum()),
        "post_P0_pstar_energy_above_0p03_count": int((post_p & very_high).sum()),
        "pass_pstar_scale_cutoff": preferred_pass,
        "post_P0_x_rows": int(post_x.sum()),
        "post_P0_x_Q_energy_L2_max": max_nan(rows.loc[post_x, "Q_energy_L2"]),
        "post_P0_x_energy_above_0p025_count": int((post_x & high).sum()),
        "pass_x_scale_cutoff": int((post_x & high).sum()) == 0,
        "post_P0_y_rows": int(post_y.sum()),
        "post_P0_y_Q_energy_L2_max": max_nan(rows.loc[post_y, "Q_energy_L2"]),
        "post_P0_y_energy_above_0p025_count": int((post_y & high).sum()),
        "pass_y_scale_cutoff": int((post_y & high).sum()) == 0,
        "high_energy_finite_certified_count": int((high & rows["finite_certified_flag"]).sum()),
        "high_energy_not_finite_certified_count": int((high & ~rows["finite_certified_flag"]).sum()),
        "pass_high_energy_finite_certified": int((high & rows["finite_certified_flag"]).sum()) == int(high.sum()),
        "high_energy_threshold_relevant_count": int((high & threshold).sum()),
        "high_energy_forbidden_count": int((high & forbidden).sum()),
        "high_energy_Q_R2Q_max": max_nan(rows.loc[high, "Q_R2Q"]),
        "pass_high_energy_threshold_safe": int((high & threshold).sum()) == 0 and int((high & forbidden).sum()) == 0,
        "high_energy_surviving_proxy_count": int((high & rows["surviving_proxy_flag"]).sum()),
        "high_energy_non_surviving_count": int((high & ~rows["surviving_proxy_flag"]).sum()),
        "high_energy_endpoint_repaid_count": int((high & rows["endpoint_repaid_flag"]).sum()),
        "high_energy_B3_no_accumulation_count": int((high & rows["B3_no_accumulation_flag"]).sum()),
        "pass_high_energy_non_survival": int((high & rows["surviving_proxy_flag"]).sum()) == 0,
        "threshold_relevant_rows": int(threshold.sum()),
        "threshold_relevant_Q_energy_L2_max": max_nan(rows.loc[threshold, "Q_energy_L2"]),
        "threshold_relevant_energy_above_0p025_count": int((threshold & high).sum()),
        "forbidden_rows": int(forbidden.sum()),
        "forbidden_Q_energy_L2_max": max_nan(rows.loc[forbidden, "Q_energy_L2"]),
        "forbidden_energy_above_0p025_count": int((forbidden & high).sum()),
        "threshold_energy_margin_to_0p025": HIGH - max_nan(rows.loc[threshold, "Q_energy_L2"]),
        "forbidden_energy_margin_to_0p025": HIGH - max_nan(rows.loc[forbidden, "Q_energy_L2"]),
        "best_symbolic_rule": best.get("rule", ""),
        "best_symbolic_rule_misses": best.get("misses_high_energy_count", ""),
        "best_symbolic_rule_threshold_false_positives": best.get("threshold_relevant_false_positive_count", ""),
        "best_symbolic_rule_forbidden_false_positives": best.get("forbidden_false_positive_count", ""),
        "best_symbolic_rule_surviving_false_positives": best.get("surviving_false_positive_count", ""),
        "scale_cutoff_failures": len(failures),
        "pass_hexc_highenergy_scalecutoff_empirical": preferred_pass or acceptable_pass,
    }

    if preferred_pass:
        summary["recommended_theorem_form"] = "post_P0_scale_cutoff"
        summary["recommended_next_file"] = "Prime_Mesh_R2Q_HExc_HighEnergy_ScaleCutoff_Theorem_Target_v1.md"
    elif acceptable_pass:
        summary["recommended_theorem_form"] = "high_energy_harmlessness"
        summary["recommended_next_file"] = "Prime_Mesh_R2Q_HExc_HighEnergyHarmlessness_Theorem_Target_v2.md"
    else:
        summary["recommended_theorem_form"] = "repair_needed"
        summary["recommended_next_file"] = "Prime_Mesh_R2Q_HExc_HighEnergy_ScaleCutoff_Repair_Map_v1.md"

    return pd.DataFrame({"field": list(summary.keys()), "value": list(summary.values())}), failures


def write_note(summary: pd.DataFrame, rules: pd.DataFrame, failures: pd.DataFrame) -> None:
    s = dict(zip(summary["field"], summary["value"]))
    md = []
    md.append("# Prime Mesh R2Q - H-Exc HighEnergy ScaleCutoff Audit v1\n")
    md.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}  \n")
    md.append(f"**Status:** {'PASS' if str(s['pass_hexc_highenergy_scalecutoff_empirical']) == 'True' else 'REPAIR'}  \n")
    md.append("\n## Executive Verdict\n")
    md.append(
        f"The strict `p_star >= P0 => Q_energy_L2 <= 0.025` cutoff is `{s['pass_pstar_scale_cutoff']}`. "
        f"Post-P0 p-star rows have max energy `{s['post_P0_pstar_Q_energy_L2_max']}` with "
        f"`{s['post_P0_pstar_energy_above_0p025_count']}` over-cap rows.\n"
    )
    md.append(
        f"High-energy rows: `{s['high_energy_rows']}`. Threshold high-energy rows: `{s['high_energy_threshold_relevant_count']}`. "
        f"Forbidden high-energy rows: `{s['high_energy_forbidden_count']}`. Surviving high-energy rows: `{s['high_energy_surviving_proxy_count']}`.\n"
    )
    md.append("\n## Cutoff Tests\n")
    for key in [
        "post_P0_pstar_rows",
        "post_P0_pstar_Q_energy_L2_max",
        "post_P0_pstar_energy_above_0p025_count",
        "pass_pstar_scale_cutoff",
        "post_P0_x_Q_energy_L2_max",
        "pass_x_scale_cutoff",
        "post_P0_y_Q_energy_L2_max",
        "pass_y_scale_cutoff",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## High-Energy Harmlessness\n")
    for key in [
        "high_energy_finite_certified_count",
        "high_energy_not_finite_certified_count",
        "pass_high_energy_finite_certified",
        "pass_high_energy_threshold_safe",
        "pass_high_energy_non_survival",
        "threshold_relevant_Q_energy_L2_max",
        "forbidden_Q_energy_L2_max",
        "threshold_energy_margin_to_0p025",
        "forbidden_energy_margin_to_0p025",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Best Symbolic Rule\n")
    for key in [
        "best_symbolic_rule",
        "best_symbolic_rule_misses",
        "best_symbolic_rule_threshold_false_positives",
        "best_symbolic_rule_forbidden_false_positives",
        "best_symbolic_rule_surviving_false_positives",
    ]:
        md.append(f"- `{key}`: `{s[key]}`\n")
    md.append("\n## Failures\n")
    if failures.empty:
        md.append("No scale-cutoff/high-energy harmlessness failures were found.\n")
    else:
        md.append(f"`{len(failures)}` failures were found; see the failure CSV.\n")
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
    rules = rule_candidates(rows)
    summary, failures = summarize(rows, rules)
    rows.to_csv(OUT_ROWS, index=False)
    rules.to_csv(OUT_RULES, index=False)
    if failures.empty:
        pd.DataFrame(columns=list(rows.columns) + ["failure_type"]).to_csv(OUT_FAILURES, index=False)
    else:
        failures.to_csv(OUT_FAILURES, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    write_note(summary, rules, failures)
    refresh_manifest([Path(__file__), OUT_SUMMARY, OUT_ROWS, OUT_RULES, OUT_FAILURES, OUT_NOTE])
    s = dict(zip(summary["field"], summary["value"]))
    log(f"pass_pstar_scale_cutoff = {s['pass_pstar_scale_cutoff']}")
    log(f"post_P0_pstar_Q_energy_L2_max = {s['post_P0_pstar_Q_energy_L2_max']}")
    log(f"high_energy_rows = {s['high_energy_rows']}")
    log(f"high_energy_surviving_proxy_count = {s['high_energy_surviving_proxy_count']}")
    log(f"pass_hexc_highenergy_scalecutoff_empirical = {s['pass_hexc_highenergy_scalecutoff_empirical']}")
    log(f"Wrote {OUT_NOTE}")


if __name__ == "__main__":
    main()
