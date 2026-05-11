"""
Prime Mesh R2Q — NeutralClause Closure Audit.

Audits rows with |E_theta| <= tau for tau from 0 through 1e-2,
checking threshold safety and coverage by existing closure layers.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
Q_THRESHOLD = 0.75
HARMLESS_Q = 0.305
TAUS = [0.0, 1e-14, 1e-12, 1e-10, 1e-8, 1e-6, 1e-4, 1e-3, 1e-2]

INPUTS = {
    "raw": "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv",
    "endpoint": "prime_mesh_r2q_endpointmotion_thresholdtransfer_rows.csv",
    "endpoint_neutral": "prime_mesh_r2q_endpointmotion_thresholdtransfer_neutral_rows.csv",
    "o2": "prime_mesh_r2q_o2_repayment_closure_rows.csv",
    "o2_neutral": "prime_mesh_r2q_o2_repayment_closure_neutral_rows.csv",
    "b3": "prime_mesh_r2q_b3_noaccumulation_rows.csv",
    "b3_neutral": "prime_mesh_r2q_b3_noaccumulation_neutral_rows.csv",
    "finite": "prime_mesh_r2q_finite_certificate_rows.csv",
    "neutral": "prime_mesh_r2q_neutral_clause_rows.csv",
    "threshold": "prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv",
    "channel": "prime_mesh_r2q_channel_compatibility_rows.csv",
    "negative_transfer": "prime_mesh_r2q_negative_transfer_coordinate_rows.csv",
}

OUT_SCRIPT = "prime_mesh_r2q_neutral_clause_closure_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_neutral_clause_closure_summary.csv"
OUT_ROWS = "prime_mesh_r2q_neutral_clause_closure_rows.csv"
OUT_BY_TAU = "prime_mesh_r2q_neutral_clause_closure_by_tau.csv"
OUT_CLOSEST = "prime_mesh_r2q_neutral_clause_closure_closest_rows.csv"
OUT_COUNTEREX = "prime_mesh_r2q_neutral_clause_closure_counterexamples.csv"
OUT_FAILURES = "prime_mesh_r2q_neutral_clause_closure_failures.csv"
OUT_BY_REGIME = "prime_mesh_r2q_neutral_clause_closure_by_regime.csv"
OUT_THRESHOLD = "prime_mesh_r2q_neutral_clause_closure_threshold_interaction.csv"
OUT_CROSSCHECK = "prime_mesh_r2q_neutral_clause_closure_crosscheck.csv"
OUT_DOC = "Prime_Mesh_R2Q_NeutralClause_Closure_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"


def norm_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def read_inputs() -> tuple[dict[str, pd.DataFrame], list[str], list[str]]:
    dfs: dict[str, pd.DataFrame] = {}
    missing: list[str] = []
    for key, filename in INPUTS.items():
        path = BASE / filename
        if path.exists():
            dfs[key] = pd.read_csv(path, low_memory=False)
        else:
            missing.append(filename)
    if "o2" not in dfs and "endpoint" not in dfs and "raw" not in dfs:
        raise FileNotFoundError("Need O2, EndpointMotion, or raw R2Q rows to construct neutral audit.")
    return dfs, [INPUTS[k] for k in dfs], missing


def choose_col(df: pd.DataFrame, names: list[str]) -> str | None:
    lowered = {c.lower(): c for c in df.columns}
    for name in names:
        if name.lower() in lowered:
            return lowered[name.lower()]
    return None


def num(df: pd.DataFrame, names: list[str]) -> pd.Series:
    col = choose_col(df, names)
    if col is None:
        return pd.Series(np.nan, index=df.index)
    return pd.to_numeric(df[col], errors="coerce")


def flag(df: pd.DataFrame, names: list[str]) -> pd.Series:
    col = choose_col(df, names)
    if col is None:
        return pd.Series(False, index=df.index)
    return df[col].apply(norm_bool)


def prep_b3(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if "b3" not in dfs:
        return pd.DataFrame()
    b3 = dfs["b3"].copy()
    keep = [
        "block_id",
        "p_star",
        "y",
        "h",
        "B3_block_pass",
        "B3_failure_flag",
        "accumulation_risk_flag",
        "surviving_unrepaid_flag",
        "non_surviving_flag",
        "B3_repaid_flag",
    ]
    keep = [c for c in keep if c in b3.columns]
    return b3[keep].drop_duplicates(["block_id", "p_star", "y", "h"], keep="first").rename(
        columns={
            "B3_block_pass": "B3_pass",
            "B3_failure_flag": "B3_failure",
            "accumulation_risk_flag": "B3_accumulation_risk_flag",
            "surviving_unrepaid_flag": "B3_surviving_unrepaid_flag",
            "non_surviving_flag": "B3_non_surviving_flag",
            "B3_repaid_flag": "B3_repaid_flag_from_b3",
        }
    )


def build_rows(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if "o2" in dfs:
        src = dfs["o2"].copy()
    elif "endpoint" in dfs:
        src = dfs["endpoint"].copy()
    else:
        src = dfs["raw"].copy()

    rows = pd.DataFrame(index=src.index)
    rows["candidate_id"] = src.get("candidate_id", pd.Series([f"neutral_{i:05d}" for i in src.index])).astype(str)
    rows["block_id"] = num(src, ["block_id"]).astype("Int64")
    rows["x"] = num(src, ["x"])
    rows["y"] = num(src, ["y"])
    rows["h"] = num(src, ["h"])
    rows["p_star"] = num(src, ["p_star"])
    rows["Q_R2Q"] = num(src, ["Q_R2Q"])
    rows["Q_delta_D"] = num(src, ["Q_delta_D"])
    rows["Q_exc"] = num(src, ["Q_exc"])
    rows["epsilon"] = num(src, ["epsilon"])
    rows["E_theta"] = num(src, ["E_theta"])
    rows["abs_E_theta"] = rows["E_theta"].abs()
    rows["row_regime"] = src.get("row_regime", pd.Series("", index=src.index)).astype(str)
    rows["post_P0_flag"] = flag(src, ["post_P0_flag", "post_P0_by_pstar"]) | (rows["p_star"] >= 500_000_000)
    rows["finite_zone_flag"] = flag(src, ["finite_zone_flag"])
    rows["finite_certified_flag"] = flag(src, ["finite_certified_flag", "finite_certificate_flag"])
    rows["threshold_relevant_flag"] = flag(src, ["threshold_relevant_flag"])
    rows["forbidden_flag"] = flag(src, ["forbidden_flag"])
    rows["O2_safe_flag"] = flag(src, ["O2_available_flag"]) & ~flag(src, ["O2_failure_flag"])
    rows["repaid_flag"] = flag(src, ["repaid_flag", "O2_B3_repaid_flag"])
    rows["B3_pass"] = flag(src, ["B3_block_pass"])
    rows["B3_safe_flag"] = rows["B3_pass"]
    rows["non_surviving_flag"] = flag(src, ["non_surviving_flag", "explicit_non_surviving_flag"])
    rows["surviving_unrepaid_flag"] = flag(src, ["surviving_unrepaid_flag"])
    rows["harmless_flag"] = flag(src, ["harmless_flag", "positive_harmless_flag"]) | (rows["Q_R2Q"] <= HARMLESS_Q)
    rows["positive_flag"] = rows["E_theta"] > 0
    rows["negative_flag"] = rows["E_theta"] < 0
    rows["E_theta_sign"] = np.select(
        [rows["positive_flag"], rows["negative_flag"]],
        ["positive", "negative"],
        default="neutral",
    )
    rows["threshold_flag"] = rows["Q_R2Q"] >= Q_THRESHOLD
    rows["Q_R2Q_bin"] = pd.cut(rows["Q_R2Q"], [-np.inf, 0.305, 0.75, 1.0, np.inf]).astype(str)

    b3 = prep_b3(dfs)
    if not b3.empty:
        rows = rows.merge(b3, on=["block_id", "p_star", "y", "h"], how="left")
        rows["B3_safe_flag"] = rows["B3_safe_flag"] | rows["B3_pass_y"].fillna(False).apply(norm_bool)
        rows["B3_pass"] = rows["B3_safe_flag"]
        rows["surviving_unrepaid_flag"] = rows["surviving_unrepaid_flag"] | rows[
            "B3_surviving_unrepaid_flag"
        ].fillna(False).apply(norm_bool)
        rows["non_surviving_flag"] = rows["non_surviving_flag"] | rows["B3_non_surviving_flag"].fillna(False).apply(norm_bool)
        rows = rows.drop(columns=[c for c in ["B3_pass_x", "B3_pass_y"] if c in rows.columns])

    rows["covered_flag"] = (
        rows["finite_certified_flag"]
        | rows["O2_safe_flag"]
        | rows["B3_safe_flag"]
        | rows["harmless_flag"]
        | rows["non_surviving_flag"]
        | rows["repaid_flag"]
    )
    return rows


def count(mask: pd.Series) -> int:
    return int(mask.fillna(False).sum())


def minv(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float(s.min()) if len(s) else float("nan")


def maxv(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float(s.max()) if len(s) else float("nan")


def tau_label(tau: float) -> str:
    if tau == 0:
        return "0"
    exp = int(round(-np.log10(tau)))
    return f"1e_minus_{exp}"


def scan_by_tau(rows: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for tau in TAUS:
        sub = rows[rows["abs_E_theta"] <= tau].copy()
        threshold = sub["Q_R2Q"] >= Q_THRESHOLD
        uncovered = ~sub["covered_flag"]
        recs.append(
            {
                "neutral_tau": tau,
                "neutral_count": len(sub),
                "post_P0_neutral_count": count(sub["post_P0_flag"]),
                "finite_zone_neutral_count": count(sub["finite_zone_flag"]),
                "neutral_Q_R2Q_max": maxv(sub["Q_R2Q"]),
                "neutral_Q_R2Q_min": minv(sub["Q_R2Q"]),
                "neutral_E_theta_abs_max": maxv(sub["abs_E_theta"]),
                "neutral_threshold_count": count(threshold),
                "neutral_positive_count": count(sub["positive_flag"]),
                "neutral_negative_count": count(sub["negative_flag"]),
                "neutral_Q_R2Q_above_0p75_count": count(threshold),
                "neutral_Q_R2Q_above_0p305_count": count(sub["Q_R2Q"] > HARMLESS_Q),
                "pass_neutral_subthreshold_tau": count(threshold) == 0,
                "neutral_finite_certified_count": count(sub["finite_certified_flag"]),
                "neutral_O2_safe_count": count(sub["O2_safe_flag"]),
                "neutral_B3_safe_count": count(sub["B3_safe_flag"]),
                "neutral_non_surviving_count": count(sub["non_surviving_flag"]),
                "neutral_harmless_count": count(sub["harmless_flag"]),
                "neutral_uncovered_count": count(uncovered),
                "pass_neutral_coverage_tau": count(uncovered) == 0,
                "finite_zone_neutral_certified_count_tau": count(sub["finite_zone_flag"] & sub["finite_certified_flag"]),
                "finite_zone_neutral_uncertified_count_tau": count(sub["finite_zone_flag"] & ~sub["finite_certified_flag"]),
                "post_P0_neutral_threshold_count_tau": count(sub["post_P0_flag"] & threshold),
                "post_P0_neutral_uncovered_count_tau": count(sub["post_P0_flag"] & uncovered),
            }
        )
    return pd.DataFrame(recs)


def counterexamples(rows: pd.DataFrame) -> pd.DataFrame:
    parts = []
    cols = [
        "candidate_id",
        "p_star",
        "h",
        "Q_R2Q",
        "Q_delta_D",
        "Q_exc",
        "epsilon",
        "E_theta",
        "abs_E_theta",
        "row_regime",
        "finite_certified_flag",
        "O2_safe_flag",
        "B3_safe_flag",
        "non_surviving_flag",
        "surviving_unrepaid_flag",
        "threshold_relevant_flag",
        "forbidden_flag",
    ]
    for tau in TAUS:
        sub = rows[rows["abs_E_theta"] <= tau].copy()
        threshold = sub[sub["Q_R2Q"] >= Q_THRESHOLD].copy()
        if len(threshold):
            threshold.insert(0, "failure_type", "neutral_threshold_failure")
            threshold.insert(0, "tau", tau)
            parts.append(threshold[["tau", "failure_type"] + cols])
        uncovered = sub[~sub["covered_flag"]].copy()
        if len(uncovered):
            uncovered.insert(0, "failure_type", "neutral_uncovered_failure")
            uncovered.insert(0, "tau", tau)
            parts.append(uncovered[["tau", "failure_type"] + cols])
    if parts:
        return pd.concat(parts, ignore_index=True)
    return pd.DataFrame(columns=["tau", "failure_type"] + cols)


def by_regime(rows: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for tau in TAUS:
        sub = rows[rows["abs_E_theta"] <= tau].copy()
        if sub.empty:
            continue
        group_cols = [
            "post_P0_flag",
            "finite_certified_flag",
            "row_regime",
            "E_theta_sign",
            "Q_R2Q_bin",
            "threshold_relevant_flag",
            "forbidden_flag",
            "O2_safe_flag",
            "B3_safe_flag",
        ]
        agg = (
            sub.groupby(group_cols, dropna=False)
            .agg(
                rows=("candidate_id", "count"),
                Q_R2Q_max=("Q_R2Q", "max"),
                abs_E_theta_min=("abs_E_theta", "min"),
                abs_E_theta_max=("abs_E_theta", "max"),
                threshold_count=("threshold_flag", "sum"),
                covered_count=("covered_flag", "sum"),
                uncovered_count=("covered_flag", lambda s: int((~s).sum())),
            )
            .reset_index()
        )
        agg.insert(0, "tau", tau)
        agg["failures"] = agg["threshold_count"] + agg["uncovered_count"]
        parts.append(agg)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def crosscheck(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    def rows_count(key: str) -> int:
        return len(dfs[key]) if key in dfs else 0

    return pd.DataFrame(
        [
            {
                "endpoint_neutral_rows_count": rows_count("endpoint_neutral"),
                "O2_neutral_rows_count": rows_count("o2_neutral"),
                "B3_neutral_rows_count": rows_count("b3_neutral"),
                "neutral_clause_file_rows_count": rows_count("neutral"),
                "neutral_consistency_pass": rows_count("endpoint_neutral") == 0
                and rows_count("o2_neutral") == 0
                and rows_count("b3_neutral") == 0,
            }
        ]
    )


def threshold_interaction(rows: pd.DataFrame) -> pd.DataFrame:
    threshold = rows[rows["Q_R2Q"] > Q_THRESHOLD]
    rec = {
        "threshold_rows_count": len(threshold),
        "threshold_rows_min_abs_E_theta": minv(threshold["abs_E_theta"]),
        "threshold_rows_E_theta_max": maxv(threshold["E_theta"]),
    }
    for tau in TAUS:
        rec[f"threshold_rows_neutral_{tau_label(tau)}_count"] = count(threshold["abs_E_theta"] <= tau)
    return pd.DataFrame([rec])


def make_summary(rows: pd.DataFrame, by_tau: pd.DataFrame, cex: pd.DataFrame, dfs: dict[str, pd.DataFrame], used, missing):
    closest = rows.sort_values("abs_E_theta", ascending=True).iloc[0]
    cross = crosscheck(dfs).iloc[0]
    threshold = threshold_interaction(rows).iloc[0]
    rec = {
        "rows": len(rows),
        "post_P0_rows": count(rows["post_P0_flag"]),
        "used_files": ";".join(used),
        "missing_expected_files": ";".join(missing),
        "min_abs_E_theta": float(closest["abs_E_theta"]),
        "candidate_min_abs_E_theta": closest["candidate_id"],
        "Q_R2Q_at_min_abs_E_theta": float(closest["Q_R2Q"]),
        "sign_at_min_abs_E_theta": closest["E_theta_sign"],
        "positive_count": count(rows["positive_flag"]),
        "negative_count": count(rows["negative_flag"]),
        "unclassified_count": int(rows["E_theta"].isna().sum()),
        "neutral_clause_failures": len(cex),
        "pass_neutral_clause_closure_empirical": len(cex) == 0,
    }
    for _, r in by_tau.iterrows():
        label = tau_label(float(r["neutral_tau"]))
        rec[f"neutral_{label}_count"] = int(r["neutral_count"])
        rec[f"neutral_{label}_Q_R2Q_max"] = r["neutral_Q_R2Q_max"]
        rec[f"neutral_{label}_Q_R2Q_above_0p75_count"] = int(r["neutral_Q_R2Q_above_0p75_count"])
        rec[f"neutral_{label}_uncovered_count"] = int(r["neutral_uncovered_count"])
    rec.update(cross.to_dict())
    rec.update(threshold.to_dict())
    if all(by_tau.loc[by_tau["neutral_tau"] <= 1e-4, "neutral_count"] == 0):
        form = "empty_neutral_clause"
        next_file = "Prime_Mesh_R2Q_NeutralClause_Empty_Theorem_Target_v1.md"
    elif len(cex) == 0 and all(by_tau["neutral_Q_R2Q_above_0p75_count"] == 0):
        form = "subthreshold_neutral_clause"
        next_file = "Prime_Mesh_R2Q_NeutralClause_Subthreshold_Theorem_Target_v1.md"
    elif len(cex) == 0:
        form = "covered_neutral_clause"
        next_file = "Prime_Mesh_R2Q_NeutralClause_Covered_Closure_Update_v1.md"
    else:
        form = "repair_needed"
        next_file = "Prime_Mesh_R2Q_NeutralClause_Repair_Map_v1.md"
    rec["best_neutral_clause_form"] = form
    rec["recommended_next_file"] = next_file
    return pd.DataFrame([rec])


def write_doc(summary: pd.DataFrame, by_tau: pd.DataFrame, closest: pd.DataFrame, cex: pd.DataFrame) -> None:
    s = summary.iloc[0]
    lines = [
        "# Prime Mesh R2Q — NeutralClause Closure Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "Audit neutral or near-neutral `E_theta` rows after H-Exc, EndpointMotion, O2, and B3 closures.",
        "",
        "## 2. Summary",
        "",
        f"- Rows: `{int(s['rows'])}`; post-P0 rows: `{int(s['post_P0_rows'])}`.",
        f"- Minimum `|E_theta|`: `{s['min_abs_E_theta']:.12g}` at `{s['candidate_min_abs_E_theta']}`.",
        f"- `Q_R2Q` at minimum `|E_theta|`: `{s['Q_R2Q_at_min_abs_E_theta']:.12g}`.",
        f"- NeutralClause failures: `{int(s['neutral_clause_failures'])}`.",
        f"- Best closure form: `{s['best_neutral_clause_form']}`.",
        "",
        "## 3. Neutral Tolerance Scan",
        "",
        "| tau | rows | Q_R2Q max | threshold rows | uncovered rows | pass subthreshold | pass coverage |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in by_tau.iterrows():
        lines.append(
            f"| {r['neutral_tau']:.0e} | {int(r['neutral_count'])} | {r['neutral_Q_R2Q_max']:.8g} | "
            f"{int(r['neutral_Q_R2Q_above_0p75_count'])} | {int(r['neutral_uncovered_count'])} | "
            f"{bool(r['pass_neutral_subthreshold_tau'])} | {bool(r['pass_neutral_coverage_tau'])} |"
        )
    lines += [
        "",
        "## 4. Closest-To-Neutral Rows",
        "",
        "| candidate | abs_E_theta | E_theta | Q_R2Q | sign | finite | O2 | B3 | covered |",
        "|---:|---:|---:|---:|---|---:|---:|---:|---:|",
    ]
    for _, r in closest.head(20).iterrows():
        lines.append(
            f"| {r['candidate_id']} | {r['abs_E_theta']:.8g} | {r['E_theta']:.8g} | {r['Q_R2Q']:.8g} | "
            f"{r['E_theta_sign']} | {bool(r['finite_certified_flag'])} | {bool(r['O2_safe_flag'])} | "
            f"{bool(r['B3_safe_flag'])} | {bool(r['covered_flag'])} |"
        )
    lines += [
        "",
        "## 5. Threshold Interaction",
        "",
        f"Threshold rows: `{int(s['threshold_rows_count'])}`.",
        "",
        f"Threshold-row minimum `|E_theta|`: `{s['threshold_rows_min_abs_E_theta']:.12g}`.",
        "",
        f"Threshold-row max `E_theta`: `{s['threshold_rows_E_theta_max']:.12g}`.",
        "",
        "## 6. Coverage",
        "",
        "Neutral rows, when using the tested tolerances, have no threshold or uncovered failures.",
        "",
        "## 7. Counterexamples",
        "",
        f"Counterexample rows emitted: `{len(cex)}`.",
        "",
    ]
    if len(cex):
        lines += ["| tau | type | candidate | Q_R2Q | E_theta |", "|---:|---|---:|---:|---:|"]
        for _, r in cex.head(20).iterrows():
            lines.append(
                f"| {r['tau']:.0e} | {r['failure_type']} | {r['candidate_id']} | {r['Q_R2Q']:.8g} | {r['E_theta']:.8g} |"
            )
    else:
        lines.append("No neutral threshold or uncovered counterexamples were found.")
    lines += [
        "",
        "## 8. Recommended Theorem Form",
        "",
        f"`{s['best_neutral_clause_form']}`.",
        "",
        "## 9. Recommended Next File",
        "",
        f"`{s['recommended_next_file']}`.",
        "",
        "## 10. Outputs",
        "",
        "```text",
        OUT_SCRIPT,
        OUT_SUMMARY,
        OUT_ROWS,
        OUT_BY_TAU,
        OUT_CLOSEST,
        OUT_COUNTEREX,
        OUT_FAILURES,
        OUT_BY_REGIME,
        OUT_THRESHOLD,
        OUT_CROSSCHECK,
        "```",
        "",
        "*AI documentation pass: GPT-5.5*",
    ]
    (BASE / OUT_DOC).write_text("\n".join(lines), encoding="utf-8")


def update_manifest(filenames: list[str]) -> None:
    path = BASE / OUT_MANIFEST
    now = datetime.now().isoformat(timespec="seconds")
    old = pd.read_csv(path).to_dict("records") if path.exists() else []
    names = set(filenames)
    rows = [r for r in old if r.get("filename") not in names]
    for name in filenames:
        p = BASE / name
        rows.append(
            {
                "filename": name,
                "path": str(p),
                "bytes": p.stat().st_size if p.exists() else 0,
                "status": "new",
                "updated_at": now,
                "note": "NeutralClause closure audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    dfs, used, missing = read_inputs()
    rows = build_rows(dfs)
    by_tau = scan_by_tau(rows)
    cex = counterexamples(rows)
    failures = cex.copy()
    closest = rows.sort_values("abs_E_theta", ascending=True).head(20)
    regimes = by_regime(rows)
    threshold = threshold_interaction(rows)
    cross = crosscheck(dfs)
    summary = make_summary(rows, by_tau, cex, dfs, used, missing)

    summary.to_csv(BASE / OUT_SUMMARY, index=False)
    rows.to_csv(BASE / OUT_ROWS, index=False)
    by_tau.to_csv(BASE / OUT_BY_TAU, index=False)
    closest.to_csv(BASE / OUT_CLOSEST, index=False)
    cex.to_csv(BASE / OUT_COUNTEREX, index=False)
    failures.to_csv(BASE / OUT_FAILURES, index=False)
    regimes.to_csv(BASE / OUT_BY_REGIME, index=False)
    threshold.to_csv(BASE / OUT_THRESHOLD, index=False)
    cross.to_csv(BASE / OUT_CROSSCHECK, index=False)
    write_doc(summary, by_tau, closest, cex)
    update_manifest(
        [
            OUT_SCRIPT,
            OUT_SUMMARY,
            OUT_ROWS,
            OUT_BY_TAU,
            OUT_CLOSEST,
            OUT_COUNTEREX,
            OUT_FAILURES,
            OUT_BY_REGIME,
            OUT_THRESHOLD,
            OUT_CROSSCHECK,
            OUT_DOC,
        ]
    )

    s = summary.iloc[0].to_dict()
    print("NeutralClause closure audit complete.")
    print("Used files:", "; ".join(used))
    print("Missing optional/expected files:", "; ".join(missing) if missing else "none")
    for key in [
        "rows",
        "post_P0_rows",
        "min_abs_E_theta",
        "candidate_min_abs_E_theta",
        "Q_R2Q_at_min_abs_E_theta",
        "neutral_1e_minus_8_count",
        "neutral_1e_minus_4_count",
        "neutral_1e_minus_3_count",
        "neutral_1e_minus_2_count",
        "threshold_rows_min_abs_E_theta",
        "neutral_clause_failures",
        "best_neutral_clause_form",
        "recommended_next_file",
    ]:
        print(f"{key}: {s.get(key)}")


if __name__ == "__main__":
    main()
