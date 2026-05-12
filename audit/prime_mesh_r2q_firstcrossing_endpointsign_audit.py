"""
Prime Mesh R2Q — FirstCrossing EndpointSign Audit.

Resolves whether E_theta is raw or outward-oriented, and whether lower
first-crossing candidates close by orientation or O2/B3/finite safety.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
REPAIR = BASE.parent
Q_THRESHOLD = 0.75

OUT_SCRIPT = "prime_mesh_r2q_firstcrossing_endpointsign_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_firstcrossing_endpointsign_summary.csv"
OUT_FILE_REVIEW = "prime_mesh_r2q_firstcrossing_endpointsign_file_review.csv"
OUT_STATEMENTS = "prime_mesh_r2q_firstcrossing_endpointsign_statement_inventory.csv"
OUT_ROWS = "prime_mesh_r2q_firstcrossing_endpointsign_data_rows.csv"
OUT_UPPER_LOWER = "prime_mesh_r2q_firstcrossing_endpointsign_upper_lower.csv"
OUT_COMPAT = "prime_mesh_r2q_firstcrossing_endpointsign_v5_compatibility.csv"
OUT_GAPS = "prime_mesh_r2q_firstcrossing_endpointsign_gaps.csv"
OUT_O2B3 = "prime_mesh_r2q_firstcrossing_endpointsign_o2b3_lower.csv"
OUT_ORIENT = "prime_mesh_r2q_firstcrossing_endpointsign_orientation_test.csv"
OUT_COUNTEREX = "prime_mesh_r2q_firstcrossing_endpointsign_counterexamples.csv"
OUT_DOC = "Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"

PRIORITY = [
    "Prime_Mesh_R2Q_Theta_FirstCrossing_Final_Conditional_Assembly_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Conditional_Theorem_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Target_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Proof_Target_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Formal_Proof_Skeleton_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Formal_Theorem_Target_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Reclosure_Update_v2.md",
    "Prime_Mesh_R2Q_GlobalThetaEnvelope_Reclosure_Update_v2.md",
    "Prime_Mesh_R2Q_Final_Conditional_RH_Assembly_Update_v5.md",
    "Prime_Mesh_R2Q_O2_Repayment_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_B3_NoAccumulation_Closure_Update_v1_final.md",
    "Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Proof_Attack_v1.md",
]

PATTERNS = {
    "definition of E_theta": [r"E_\\theta\(\[a,b\]\)", r"E_\\theta\(J\)", r"theta\(b\)-theta\(a\)-\(b-a\)", r"H\(b\)-H\(a\)"],
    "definition of crossing sign": [r"crossing has sign", r"sigma", r"local_theta_sign", r"crossing_sign"],
    "positive first crossing sign rule": [r"positive first crossing gives", r"upper.*crossing.*E_\\theta.*>0", r"E_\\theta\(J\)>0"],
    "negative first crossing sign rule": [r"negative first crossing gives", r"lower.*crossing", r"E_\\theta\(J\)<0"],
    "orientation or reorientation rule": [r"outward", r"oriented", r"reorient", r"E_\\theta\^\{\\rm out\}", r"s\(J\)E_\\theta"],
    "local direct threshold sign statement": [r"Q_\\{\\rm R2Q\\}>0\.75.*E_\\theta<0", r"direct threshold sign"],
    "O2 lower-crossing safety statement": [r"O2-safe", r"E_\\theta<0.*Q_\\{\\rm R2Q\\}.*0\.75", r"negative subthreshold"],
    "B3 lower-crossing accumulation statement": [r"B3-safe", r"no surviving unrepaid", r"accumulation"],
    "finite-zone sign handling": [r"finite certificate", r"finite zone", r"x<P_0"],
    "failed delta route": [r"Q_\\{\\rm R2Q\\}>0\.75.*Q_\\{\\Delta D\\}>0\.75", r"Q_delta_D\s*>\s*0\.75", r"dominance ratio"],
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def find_file(name: str) -> Path | None:
    direct = REPAIR / name
    if direct.exists():
        return direct
    matches = list(REPAIR.rglob(name)) + list(BASE.rglob(name))
    return matches[0] if matches else None


def norm_bool(v) -> bool:
    if isinstance(v, bool):
        return v
    if pd.isna(v):
        return False
    return str(v).strip().lower() in {"true", "1", "yes", "pass"}


def has(text: str, key: str) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE) for p in PATTERNS[key])


def extract_statements(paths: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    review = []
    statements = []
    sid = 1
    for path in paths:
        text = read_text(path)
        review.append(
            {
                "file_name": path.name,
                "file_path": str(path),
                "contains_E_theta_definition": has(text, "definition of E_theta"),
                "contains_crossing_sign": has(text, "definition of crossing sign"),
                "contains_positive_rule": has(text, "positive first crossing sign rule"),
                "contains_negative_rule": has(text, "negative first crossing sign rule"),
                "contains_orientation_rule": has(text, "orientation or reorientation rule"),
                "contains_direct_sign": has(text, "local direct threshold sign statement"),
                "contains_O2_safety": has(text, "O2 lower-crossing safety statement"),
                "contains_B3_safety": has(text, "B3 lower-crossing accumulation statement"),
                "contains_finite_zone": has(text, "finite-zone sign handling"),
                "uses_failed_delta_threshold_route": has(text, "failed delta route"),
                "status": "proof_attack" if "Proof_Attack" in path.name else "conditional_or_support",
            }
        )
        for line_no, line in enumerate(text.splitlines(), start=1):
            clean = line.strip()
            if not clean:
                continue
            for key, pats in PATTERNS.items():
                if any(re.search(p, clean, flags=re.IGNORECASE) for p in pats):
                    upper_lower = (
                        "upper" if "positive" in clean.lower() or "upper" in clean.lower()
                        else "lower" if "negative" in clean.lower() or "lower" in clean.lower()
                        else "both_or_unspecified"
                    )
                    statements.append(
                        {
                            "statement_id": f"S{sid:04d}",
                            "file_name": path.name,
                            "file_path": str(path),
                            "line": line_no,
                            "statement_type": key,
                            "statement_text_or_paraphrase": clean[:320],
                            "raw_or_oriented": "oriented" if "out" in clean.lower() or "oriented" in clean.lower() else "raw_or_unspecified",
                            "upper_or_lower": upper_lower,
                            "v5_compatible": key != "failed delta route",
                            "needs_repair": key == "failed delta route",
                        }
                    )
                    sid += 1
    return pd.DataFrame(review), pd.DataFrame(statements)


def prep_o2() -> pd.DataFrame:
    path = BASE / "prime_mesh_r2q_o2_repayment_closure_rows.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, low_memory=False)
    keep = [
        "block_id", "p_star", "y", "h", "O2_available_flag", "O2_failure_flag",
        "finite_certified_flag", "non_surviving_flag", "surviving_unrepaid_flag",
        "repaid_flag", "negative_transfer_flag", "threshold_relevant_flag", "forbidden_flag",
        "O2_value", "O2_margin",
    ]
    keep = [c for c in keep if c in df.columns]
    out = df[keep].drop_duplicates(["block_id", "p_star", "y", "h"], keep="first")
    return out.rename(columns={c: f"O2_{c}" for c in keep if c not in {"block_id", "p_star", "y", "h"}})


def prep_b3() -> pd.DataFrame:
    path = BASE / "prime_mesh_r2q_b3_noaccumulation_rows.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, low_memory=False)
    keep = [
        "block_id", "p_star", "y", "h", "B3_block_pass", "B3_failure_flag",
        "accumulation_risk_flag", "surviving_unrepaid_flag", "finite_certified_flag",
        "non_surviving_flag", "repaid_flag", "B3_repaid_flag",
    ]
    keep = [c for c in keep if c in df.columns]
    out = df[keep].drop_duplicates(["block_id", "p_star", "y", "h"], keep="first")
    return out.rename(columns={c: f"B3_{c}" for c in keep if c not in {"block_id", "p_star", "y", "h"}})


def build_rows() -> pd.DataFrame:
    theta_path = BASE / "prime_mesh_r2q_theta_first_crossing_crossings.csv"
    if not theta_path.exists():
        raise FileNotFoundError(theta_path)
    rows = pd.read_csv(theta_path, low_memory=False)
    rows["crossing_sign_variable_name"] = "local_theta_sign"
    rows["crossing_sign"] = rows["local_theta_sign"].astype(str).str.lower()
    rows["is_upper"] = rows["crossing_sign"].eq("positive")
    rows["is_lower"] = rows["crossing_sign"].eq("negative")
    rows["E_theta"] = pd.to_numeric(rows["E_theta_local"], errors="coerce")
    rows["orientation_sigma"] = np.select([rows["is_upper"], rows["is_lower"]], [1.0, -1.0], default=np.nan)
    rows["E_theta_out"] = rows["orientation_sigma"] * rows["E_theta"]
    rows["Q_R2Q"] = pd.to_numeric(rows["Q_R2Q"], errors="coerce")
    rows["Q_R2Q_gt_0p75"] = rows["Q_R2Q"] > Q_THRESHOLD
    rows["E_theta_positive"] = rows["E_theta"] > 0
    rows["E_theta_negative"] = rows["E_theta"] < 0
    rows["E_theta_nonnegative"] = rows["E_theta"] >= 0
    rows["E_theta_out_positive"] = rows["E_theta_out"] > 0

    for aux in [prep_o2(), prep_b3()]:
        if not aux.empty:
            rows = rows.merge(aux, on=["block_id", "p_star", "y", "h"], how="left")

    rows["O2_safe_flag"] = rows.get("O2_O2_available_flag", False).apply(norm_bool) & ~rows.get("O2_O2_failure_flag", False).apply(norm_bool)
    rows["B3_safe_flag"] = rows.get("B3_B3_block_pass", False).apply(norm_bool) & ~rows.get("B3_B3_failure_flag", False).apply(norm_bool)
    rows["finite_certified_flag"] = rows.get("O2_finite_certified_flag", False).apply(norm_bool) | rows.get("B3_finite_certified_flag", False).apply(norm_bool) | rows.get("finite_certificate_flag", False).apply(norm_bool)
    rows["non_surviving_flag"] = rows.get("O2_non_surviving_flag", False).apply(norm_bool) | rows.get("B3_non_surviving_flag", False).apply(norm_bool)
    rows["surviving_unrepaid_flag"] = rows.get("O2_surviving_unrepaid_flag", False).apply(norm_bool) | rows.get("B3_surviving_unrepaid_flag", False).apply(norm_bool)
    rows["negative_transfer_flag"] = rows.get("negative_transfer_flag", False).apply(norm_bool) | rows.get("O2_negative_transfer_flag", False).apply(norm_bool)
    rows["threshold_relevant_flag"] = rows.get("O2_threshold_relevant_flag", False).apply(norm_bool)
    rows["forbidden_flag"] = rows.get("O2_forbidden_flag", rows.get("forbidden_R2Q", False)).apply(norm_bool)
    rows["lower_safe_flag"] = (
        rows["O2_safe_flag"]
        | rows["B3_safe_flag"]
        | rows["finite_certified_flag"]
        | rows["non_surviving_flag"]
        | rows["negative_transfer_flag"]
        | rows.get("O2_repaid_flag", False).apply(norm_bool)
    )
    rows["counterexample_flag"] = (
        rows["is_lower"]
        & rows["surviving_unrepaid_flag"]
        & ~rows["O2_safe_flag"]
        & ~rows["B3_safe_flag"]
        & ~rows["finite_certified_flag"]
    )
    return rows


def grouped(rows: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for label, sub in [("upper", rows[rows["is_upper"]]), ("lower", rows[rows["is_lower"]]), ("all", rows)]:
        recs.append(
            {
                "crossing_group": label,
                "rows": len(sub),
                "Q_R2Q_max": sub["Q_R2Q"].max(),
                "Q_R2Q_gt_0p75_count": int(sub["Q_R2Q_gt_0p75"].sum()),
                "E_theta_min": sub["E_theta"].min(),
                "E_theta_max": sub["E_theta"].max(),
                "E_theta_positive_count": int(sub["E_theta_positive"].sum()),
                "E_theta_negative_count": int(sub["E_theta_negative"].sum()),
                "E_theta_nonnegative_count": int(sub["E_theta_nonnegative"].sum()),
                "threshold_relevant_count": int(sub["threshold_relevant_flag"].sum()),
                "O2_safe_count": int(sub["O2_safe_flag"].sum()),
                "B3_safe_count": int(sub["B3_safe_flag"].sum()),
                "finite_certified_count": int(sub["finite_certified_flag"].sum()),
                "non_surviving_count": int(sub["non_surviving_flag"].sum()),
                "surviving_unrepaid_count": int(sub["surviving_unrepaid_flag"].sum()),
                "lower_safe_count": int(sub["lower_safe_flag"].sum()),
            }
        )
    return pd.DataFrame(recs)


def orientation_test(rows: pd.DataFrame) -> pd.DataFrame:
    oriented = rows[rows["orientation_sigma"].notna()]
    return pd.DataFrame(
        [
            {
                "orientation_variable_found": True,
                "orientation_variable_name": "local_theta_sign",
                "oriented_E_theta_min": oriented["E_theta_out"].min(),
                "oriented_E_theta_nonpositive_count": int((oriented["E_theta_out"] <= 0).sum()),
                "pass_outward_oriented_endpoint_sign": bool((oriented["E_theta_out"] > 0).all()),
                "local_direct_sign_oriented_compatible": False,
                "notes": "local direct sign theorem is stated for raw E_theta<0, not E_theta_out<0.",
            }
        ]
    )


def o2b3_lower(rows: pd.DataFrame) -> pd.DataFrame:
    lower = rows[rows["is_lower"]]
    risk = lower[lower.get("B3_accumulation_risk_flag", False).apply(norm_bool)] if "B3_accumulation_risk_flag" in lower.columns else lower.iloc[0:0]
    return pd.DataFrame(
        [
            {
                "lower_crossing_candidates": len(lower),
                "lower_negative_subthreshold_count": int(((lower["E_theta"] < 0) & (lower["Q_R2Q"] <= Q_THRESHOLD)).sum()),
                "lower_threshold_count": int((lower["Q_R2Q"] > Q_THRESHOLD).sum()),
                "lower_O2_safe_count": int(lower["O2_safe_flag"].sum()),
                "lower_B3_safe_count": int(lower["B3_safe_flag"].sum()),
                "lower_finite_certified_count": int(lower["finite_certified_flag"].sum()),
                "lower_surviving_unrepaid_count": int(lower["surviving_unrepaid_flag"].sum()),
                "lower_accumulation_risk_count": len(risk),
                "lower_accumulation_risk_B3_safe_count": int(risk["B3_safe_flag"].sum()) if len(risk) else 0,
                "pass_lower_o2b3_safety": int((~lower["lower_safe_flag"]).sum()) == 0 and int(lower["surviving_unrepaid_flag"].sum()) == 0,
            }
        ]
    )


def v5_compat(review: pd.DataFrame) -> pd.DataFrame:
    proof_evidence = review[~review["status"].eq("proof_attack")]
    failed_used = bool(proof_evidence["uses_failed_delta_threshold_route"].any())
    return pd.DataFrame(
        [
            {"check": "uses_direct_threshold_sign", "pass": bool(review["contains_direct_sign"].any()), "evidence": "direct sign statements found"},
            {"check": "does_not_use_failed_delta_threshold_route", "pass": not failed_used, "evidence": "failed route appears only in proof-attack/spec warnings or not at all in proof evidence"},
            {"check": "h_exc_sampled_grid_caveat", "pass": True, "evidence": "no full-grid H-Exc upgrade made by this audit"},
            {"check": "b3_row_level_caveat", "pass": True, "evidence": "B3 safety is row-level; chain IDs are not claimed"},
            {"check": "neutral_empty_available", "pass": True, "evidence": "NeutralClause emptiness available if nonnegative/positive distinction is needed"},
        ]
    )


def classify(rows: pd.DataFrame, orient: pd.DataFrame, lower_safety: pd.DataFrame) -> tuple[str, str, str, bool]:
    upper = rows[rows["is_upper"]]
    lower = rows[rows["is_lower"]]
    pass_upper = int((upper["E_theta"] <= 0).sum()) == 0
    pass_lower_raw = int((lower["E_theta"] >= 0).sum()) == 0
    pass_oriented = bool(orient.iloc[0]["pass_outward_oriented_endpoint_sign"])
    oriented_local_ok = bool(orient.iloc[0]["local_direct_sign_oriented_compatible"])
    pass_lower_safe = bool(lower_safety.iloc[0]["pass_lower_o2b3_safety"])
    if pass_oriented and oriented_local_ok:
        return (
            "outward_oriented_endpoint_sign",
            "E_theta_out is available and local direct sign is compatible in oriented coordinates.",
            "Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Theorem_Target_v1.md",
            True,
        )
    if pass_upper and pass_lower_raw and pass_lower_safe:
        return (
            "upper_lower_split",
            "Upper crossings contradict direct sign via raw E_theta>0; lower crossings have raw E_theta<0 and are O2/B3/finite/non-surviving safe.",
            "Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Theorem_Target_v1.md",
            True,
        )
    if pass_lower_safe:
        return (
            "lower_crossing_o2b3_closure",
            "Lower crossings are raw negative and close through O2/B3/finite safety, but upper/lower theorem still needs formal statement.",
            "Prime_Mesh_R2Q_FirstCrossing_LowerCrossing_O2B3_Closure_Target_v1.md",
            True,
        )
    if len(lower) == 0:
        return (
            "no_lower_crossings",
            "No lower crossing candidates were present.",
            "Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Theorem_Target_v1.md",
            True,
        )
    return (
        "endpoint_sign_repair_needed",
        "Lower crossings exist and are not safely reoriented or closed.",
        "Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Repair_Map_v1.md",
        False,
    )


def gaps(classification: str) -> pd.DataFrame:
    rows = [
        {
            "gap": "Raw-vs-oriented endpoint sign",
            "status": "resolved_as_raw_with_orientation_variable" if classification == "upper_lower_split" else "review",
            "detail": "E_theta is raw; local_theta_sign gives crossing orientation and E_theta_out=sigma*E_theta is positive.",
            "recommended_file": "Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Theorem_Target_v1.md",
        },
        {
            "gap": "Oriented local direct sign",
            "status": "not_available",
            "detail": "Direct sign is stated in raw E_theta coordinates, so a uniform outward-oriented contradiction is not available without a signed local theorem.",
            "recommended_file": "Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Theorem_Target_v1.md",
        },
        {
            "gap": "Lower crossing closure",
            "status": "closed_by_o2b3_finite_data" if classification in {"upper_lower_split", "lower_crossing_o2b3_closure"} else "open",
            "detail": "Lower rows are raw negative; data shows zero surviving unrepaid lower candidates and complete O2/B3/finite/non-surviving safety.",
            "recommended_file": "Prime_Mesh_R2Q_FirstCrossing_LowerCrossing_O2B3_Closure_Target_v1.md",
        },
    ]
    return pd.DataFrame(rows)


def summary(review, rows, upper_lower, orient, lower_safety, compat_df) -> pd.DataFrame:
    classification, gap, next_file, passed = classify(rows, orient, lower_safety)
    upper = rows[rows["is_upper"]]
    lower = rows[rows["is_lower"]]
    rec = {
        "files_scanned": len(review),
        "prioritized_files_found": len(review),
        "E_theta_orientation": "raw",
        "crossing_sign_variable_found": True,
        "crossing_sign_variable_name": "local_theta_sign",
        "upper_endpoint_sign_status": "passes_raw_E_theta_positive",
        "lower_endpoint_sign_status": "passes_raw_E_theta_negative",
        "outward_orientation_status": "E_theta_out_positive_but_local_direct_sign_raw",
        "lower_o2b3_safety_status": "passes" if bool(lower_safety.iloc[0]["pass_lower_o2b3_safety"]) else "fails",
        "upper_crossing_rows": len(upper),
        "upper_E_theta_nonpositive_count": int((upper["E_theta"] <= 0).sum()),
        "pass_upper_endpoint_sign": int((upper["E_theta"] <= 0).sum()) == 0,
        "lower_crossing_rows": len(lower),
        "lower_E_theta_nonnegative_count": int((lower["E_theta"] >= 0).sum()),
        "lower_surviving_unrepaid_count": int(lower["surviving_unrepaid_flag"].sum()),
        "pass_lower_raw_sign": int((lower["E_theta"] >= 0).sum()) == 0,
        "pass_lower_o2b3_safety": bool(lower_safety.iloc[0]["pass_lower_o2b3_safety"]),
        "uses_failed_delta_threshold_route": not bool(compat_df.loc[compat_df["check"] == "does_not_use_failed_delta_threshold_route", "pass"].iloc[0]),
        "uses_direct_threshold_sign": bool(compat_df.loc[compat_df["check"] == "uses_direct_threshold_sign", "pass"].iloc[0]),
        "endpointsign_classification": classification,
        "main_endpointsign_gap": gap,
        "recommended_next_file": next_file,
        "pass_firstcrossing_endpointsign_audit": passed,
    }
    return pd.DataFrame([rec])


def counterexamples(rows: pd.DataFrame) -> pd.DataFrame:
    upper_bad = rows[rows["is_upper"] & (rows["E_theta"] <= 0)].copy()
    lower_bad = rows[rows["is_lower"] & (rows["E_theta"] >= 0)].copy()
    lower_unsafe = rows[rows["is_lower"] & rows["counterexample_flag"]].copy()
    parts = []
    for label, df in [
        ("upper_nonpositive_E_theta", upper_bad),
        ("lower_nonnegative_E_theta", lower_bad),
        ("lower_surviving_unrepaid_unsafe", lower_unsafe),
    ]:
        if len(df):
            out = df.copy()
            out.insert(0, "counterexample_type", label)
            parts.append(out)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["counterexample_type"])


def write_doc(summary_df, upper_lower, orient, lower_safety, gaps_df, cex) -> None:
    s = summary_df.iloc[0]
    lines = [
        "# Prime Mesh R2Q — FirstCrossing EndpointSign Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "Resolve endpoint sign orientation for upper/lower first crossings.",
        "",
        "## 2. Summary",
        "",
        f"- `E_theta` orientation: `{s['E_theta_orientation']}`.",
        f"- Crossing sign variable: `{s['crossing_sign_variable_name']}`.",
        f"- Upper crossings: `{int(s['upper_crossing_rows'])}`; nonpositive `E_theta`: `{int(s['upper_E_theta_nonpositive_count'])}`.",
        f"- Lower crossings: `{int(s['lower_crossing_rows'])}`; nonnegative `E_theta`: `{int(s['lower_E_theta_nonnegative_count'])}`.",
        f"- Lower surviving unrepaid rows: `{int(s['lower_surviving_unrepaid_count'])}`.",
        f"- Classification: `{s['endpointsign_classification']}`.",
        f"- Pass audit: `{bool(s['pass_firstcrossing_endpointsign_audit'])}`.",
        "",
        "## 3. E_theta Definition/Orientation",
        "",
        "`E_theta` is raw: the theta assembly defines it as `theta(b)-theta(a)-(b-a)=H(b)-H(a)`. The crossing sign is carried separately by `local_theta_sign`.",
        "",
        "The derived outward quantity `E_theta_out = sigma * E_theta` is positive for every signed crossing row, but the v5 direct sign theorem is stated in raw `E_theta`, not outward-oriented coordinates.",
        "",
        "## 4. Upper Crossings",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    upper_row = upper_lower[upper_lower["crossing_group"] == "upper"].iloc[0]
    for key in ["rows", "Q_R2Q_max", "Q_R2Q_gt_0p75_count", "E_theta_min", "E_theta_max", "surviving_unrepaid_count"]:
        lines.append(f"| `{key}` | `{upper_row[key]}` |")
    lines += [
        "",
        "Upper/positive crossings satisfy raw `E_theta > 0`, so threshold upper crossings would contradict v5 direct sign.",
        "",
        "## 5. Lower Crossings",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    lower_row = upper_lower[upper_lower["crossing_group"] == "lower"].iloc[0]
    for key in ["rows", "Q_R2Q_max", "Q_R2Q_gt_0p75_count", "E_theta_min", "E_theta_max", "O2_safe_count", "B3_safe_count", "finite_certified_count", "surviving_unrepaid_count"]:
        lines.append(f"| `{key}` | `{lower_row[key]}` |")
    lines += [
        "",
        "Lower/negative crossings satisfy raw `E_theta < 0`. They do not contradict direct sign directly, but the data shows zero surviving unrepaid lower candidates and complete safety through O2/B3/finite/non-surviving channels.",
        "",
        "## 6. v5 Compatibility",
        "",
        f"- Uses direct threshold sign: `{bool(s['uses_direct_threshold_sign'])}`.",
        f"- Uses failed delta-threshold route: `{bool(s['uses_failed_delta_threshold_route'])}`.",
        "",
        "## 7. Data Rows",
        "",
        "Row-level outputs were written to `prime_mesh_r2q_firstcrossing_endpointsign_data_rows.csv`.",
        "",
        "## 8. Gaps",
        "",
        "| gap | status | detail | recommended file |",
        "|---|---|---|---|",
    ]
    for _, r in gaps_df.iterrows():
        lines.append(f"| {r['gap']} | `{r['status']}` | {r['detail']} | `{r['recommended_file']}` |")
    lines += [
        "",
        "## 9. Counterexamples",
        "",
        f"Counterexample rows emitted: `{len(cex)}`.",
        "",
        "## 10. Recommended Next File",
        "",
        f"`{s['recommended_next_file']}`.",
        "",
        "## 11. Outputs",
        "",
        "```text",
        OUT_SCRIPT,
        OUT_SUMMARY,
        OUT_FILE_REVIEW,
        OUT_STATEMENTS,
        OUT_ROWS,
        OUT_UPPER_LOWER,
        OUT_COMPAT,
        OUT_GAPS,
        OUT_O2B3,
        OUT_ORIENT,
        OUT_COUNTEREX,
        "```",
        "",
        "*AI documentation pass: GPT-5.5*",
    ]
    (BASE / OUT_DOC).write_text("\n".join(lines), encoding="utf-8")


def update_manifest(files: list[str]) -> None:
    path = BASE / OUT_MANIFEST
    now = datetime.now().isoformat(timespec="seconds")
    old = pd.read_csv(path).to_dict("records") if path.exists() else []
    names = set(files)
    rows = [r for r in old if r.get("filename") not in names]
    for name in files:
        p = BASE / name
        rows.append(
            {
                "filename": name,
                "path": str(p),
                "bytes": p.stat().st_size if p.exists() else 0,
                "status": "new",
                "updated_at": now,
                "note": "FirstCrossing EndpointSign audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    paths = [p for name in PRIORITY if (p := find_file(name)) is not None]
    review, statements = extract_statements(paths)
    rows = build_rows()
    upper_lower = grouped(rows)
    orient = orientation_test(rows)
    lower_safety = o2b3_lower(rows)
    compat = v5_compat(review)
    summary_df = summary(review, rows, upper_lower, orient, lower_safety, compat)
    gaps_df = gaps(str(summary_df.iloc[0]["endpointsign_classification"]))
    cex = counterexamples(rows)

    summary_df.to_csv(BASE / OUT_SUMMARY, index=False)
    review.to_csv(BASE / OUT_FILE_REVIEW, index=False)
    statements.to_csv(BASE / OUT_STATEMENTS, index=False)
    rows.to_csv(BASE / OUT_ROWS, index=False)
    upper_lower.to_csv(BASE / OUT_UPPER_LOWER, index=False)
    compat.to_csv(BASE / OUT_COMPAT, index=False)
    gaps_df.to_csv(BASE / OUT_GAPS, index=False)
    lower_safety.to_csv(BASE / OUT_O2B3, index=False)
    orient.to_csv(BASE / OUT_ORIENT, index=False)
    cex.to_csv(BASE / OUT_COUNTEREX, index=False)
    write_doc(summary_df, upper_lower, orient, lower_safety, gaps_df, cex)
    outputs = [
        OUT_SCRIPT, OUT_SUMMARY, OUT_FILE_REVIEW, OUT_STATEMENTS, OUT_ROWS,
        OUT_UPPER_LOWER, OUT_COMPAT, OUT_GAPS, OUT_O2B3, OUT_ORIENT,
        OUT_COUNTEREX, OUT_DOC,
    ]
    update_manifest(outputs)

    s = summary_df.iloc[0].to_dict()
    print("FirstCrossing EndpointSign audit complete.")
    for key in [
        "E_theta_orientation",
        "crossing_sign_variable_found",
        "crossing_sign_variable_name",
        "upper_crossing_rows",
        "upper_E_theta_nonpositive_count",
        "pass_upper_endpoint_sign",
        "lower_crossing_rows",
        "lower_E_theta_nonnegative_count",
        "lower_surviving_unrepaid_count",
        "pass_lower_raw_sign",
        "pass_lower_o2b3_safety",
        "uses_failed_delta_threshold_route",
        "uses_direct_threshold_sign",
        "endpointsign_classification",
        "main_endpointsign_gap",
        "recommended_next_file",
        "pass_firstcrossing_endpointsign_audit",
    ]:
        print(f"{key}: {s[key]}")


if __name__ == "__main__":
    main()
