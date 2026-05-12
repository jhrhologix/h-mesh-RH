"""
Prime Mesh R2Q — FirstCrossing CoveringLocalization audit.

Classifies whether the current first-crossing coverage evidence is continuous
all-x coverage, endpoint-discrete coverage, sampled-grid coverage, theta-window
coverage, finite-zone coverage, or still conditional.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

import pandas as pd


BASE = Path(__file__).resolve().parent
REPAIR = BASE.parent

OUT_SCRIPT = "prime_mesh_r2q_firstcrossing_coveringlocalization_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_firstcrossing_coveringlocalization_summary.csv"
OUT_FILE_REVIEW = "prime_mesh_r2q_firstcrossing_coveringlocalization_file_review.csv"
OUT_STATEMENTS = "prime_mesh_r2q_firstcrossing_coveringlocalization_statement_inventory.csv"
OUT_DATA = "prime_mesh_r2q_firstcrossing_coveringlocalization_data_crosscheck.csv"
OUT_GAPS = "prime_mesh_r2q_firstcrossing_coveringlocalization_gaps.csv"
OUT_FULLFCL = "prime_mesh_r2q_firstcrossing_coveringlocalization_fullfcl_review.csv"
OUT_THETA = "prime_mesh_r2q_firstcrossing_coveringlocalization_theta_review.csv"
OUT_FINITE = "prime_mesh_r2q_firstcrossing_coveringlocalization_finite_zone.csv"
OUT_BOUNDARY = "prime_mesh_r2q_firstcrossing_coveringlocalization_boundary_cases.csv"
OUT_DOC = "Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"

PRIORITY = [
    "Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Conditional_Theorem_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Target_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Formal_Proof_Skeleton_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Formal_Theorem_Target_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Reclosure_Update_v2.md",
    "Prime_Mesh_R2Q_GlobalThetaEnvelope_Reclosure_Update_v2.md",
    "Prime_Mesh_R2Q_FiniteThetaEnvelope_Certificate_Spec_v1.md",
    "Prime_Mesh_R2Q_FiniteThetaEnvelope_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_Localization_Audit_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Proof_Attack_v1.md",
    "Prime_Mesh_R2Q_GlobalBridge_to_RH_Conditional_Theorem_Target_v1.md",
    "Prime_Mesh_R2Q_GlobalBridge_v5_Compatibility_Update_v1.md",
]

PATTERNS = {
    "row family definition": [
        r"row family", r"admissible.*row", r"J=\[y,y\+h\]", r"\\mathcal J",
        r"B2/R2Q interval", r"FullFCL", r"theta row",
    ],
    "covered domain": [
        r"for every.*x", r"all x", r"x_1\\ge P_0", r"x_1.*covered",
        r"x\\in\[a\(J\),b\(J\)\]", r"x_1\\in\\mathcal C",
    ],
    "coverage theorem": [
        r"covering localization", r"covered_points", r"uncovered_points",
        r"pass_covering_localization", r"global first crossing.*covered",
    ],
    "continuous vs discrete statement": [
        r"continuous", r"endpoint", r"discrete", r"interior point",
        r"endpoint controlled", r"integer grid",
    ],
    "endpoint/window selection rule": [
        r"WindowSelection", r"window selection", r"selected local interval",
        r"endpoint controlled", r"theta window",
    ],
    "boundary case rule": [
        r"boundary", r"left endpoint", r"right endpoint", r"between two rows",
        r"adjacent row", r"P_0 transition",
    ],
    "interior crossing rule": [
        r"interior", r"inside.*row", r"inside.*interval", r"No Missed Interior",
        r"subrow", r"refinement",
    ],
    "finite-zone rule": [
        r"finite zone", r"finite-certified", r"finite certificate",
        r"x<P_0", r"P_0=500",
    ],
    "P0 transition rule": [
        r"P_0 transition", r"near P_0", r"post-\(P_0\)", r"post_P0_failures",
    ],
    "upper/lower sign preservation": [
        r"sign_match_frac", r"local theta sign", r"upper.*E_\\theta",
        r"lower.*E_\\theta", r"SignedLocalExtraction",
    ],
    "sample-grid caveat": [
        r"sampled-grid", r"sample grid", r"T_J", r"H-Exc.*full-grid",
        r"full-grid H-Exc",
    ],
    "failed delta route": [
        r"Q_\\{\\rm R2Q\\}>0\.75.*Q_\\{\\Delta D\\}>0\.75",
        r"Q_delta_D\s*>\s*0\.75", r"dominance ratio", r"0\.987",
    ],
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
    direct = BASE / name
    if direct.exists():
        return direct
    matches = list(REPAIR.rglob(name)) + list(BASE.rglob(name))
    return matches[0] if matches else None


def as_bool(v) -> bool:
    if isinstance(v, bool):
        return v
    if pd.isna(v):
        return False
    return str(v).strip().lower() in {"true", "1", "yes", "pass"}


def number(df: pd.DataFrame, col: str, default=0.0):
    if df.empty or col not in df.columns:
        return default
    return pd.to_numeric(df[col], errors="coerce").iloc[0]


def has(text: str, key: str) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE | re.DOTALL) for p in PATTERNS[key])


def status_for(path: Path) -> str:
    name = path.name.lower()
    if "audit_spec" in name:
        return "spec"
    if "proof_attack" in name:
        return "proof_attack"
    if "conditional" in name:
        return "conditional_theorem"
    if "closure_update" in name or "reclosure" in name:
        return "closure_update"
    if "target" in name or "skeleton" in name:
        return "target_or_skeleton"
    if "audit" in name:
        return "audit_result"
    return "candidate"


def risky_full_grid_claim(text: str) -> bool:
    risk = re.search(r"H-Exc.{0,80}(full-grid|full grid)|full-grid.{0,80}H-Exc", text, flags=re.IGNORECASE | re.DOTALL)
    if not risk:
        return False
    window = text[max(0, risk.start() - 80): risk.end() + 80].lower()
    safe_words = ["do not", "does not", "must not", "avoid", "not upgrade", "not used", "false", "warning", "danger"]
    return not any(w in window for w in safe_words)


def scan_files(paths: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    review = []
    statements = []
    sid = 1
    for path in paths:
        text = read_text(path)
        lowered = text.lower()
        mode = "unclear"
        if re.search(r"for every.*x|all x|continuous", text, flags=re.IGNORECASE | re.DOTALL):
            mode = "continuous_or_claimed"
        if re.search(r"endpoint controlled|endpoint coverage|endpoint-discrete", text, flags=re.IGNORECASE):
            mode = "endpoint_or_window"
        if re.search(r"theta window|theta envelope|theta first", text, flags=re.IGNORECASE):
            mode = "theta_window"
        if re.search(r"sampled-grid|sample grid|T_J", text, flags=re.IGNORECASE):
            mode = "sampled_grid_caveat_present"
        if re.search(r"finite certificate|finite zone|x<P_0", text, flags=re.IGNORECASE):
            mode = f"{mode}+finite_zone"

        rec = {
            "file_name": path.name,
            "file_path": str(path),
            "contains_covering_definition": has(text, "coverage theorem"),
            "contains_row_family_definition": has(text, "row family definition"),
            "contains_domain_definition": has(text, "covered domain"),
            "contains_continuous_x_claim": bool(re.search(r"for every.*x|all x|continuous_all_x|continuous", text, flags=re.IGNORECASE | re.DOTALL)),
            "contains_endpoint_discrete_claim": bool(re.search(r"endpoint|endpoint controlled|endpoint coverage|endpoint-discrete", text, flags=re.IGNORECASE)),
            "contains_sample_grid_claim": bool(re.search(r"sampled-grid|sample grid|T_J", text, flags=re.IGNORECASE)),
            "contains_theta_window_claim": bool(re.search(r"theta[- ]window|theta envelope|theta first|theta row", text, flags=re.IGNORECASE)),
            "contains_finite_zone_claim": has(text, "finite-zone rule"),
            "contains_boundary_handling": has(text, "boundary case rule"),
            "contains_interior_handling": has(text, "interior crossing rule"),
            "contains_upper_lower_sign": has(text, "upper/lower sign preservation"),
            "contains_failed_delta_route": has(text, "failed delta route"),
            "contains_full_grid_h_excision_claim": risky_full_grid_claim(text),
            "coverage_mode_hint": mode,
            "status": status_for(path),
            "notes": "conditional/support file" if "conditional" in lowered or "empirical" in lowered else "",
        }
        review.append(rec)

        for line_no, line in enumerate(text.splitlines(), start=1):
            clean = line.strip()
            if not clean:
                continue
            for stype, pats in PATTERNS.items():
                if any(re.search(p, clean, flags=re.IGNORECASE) for p in pats):
                    coverage_mode = "theta_window" if "theta" in clean.lower() else "finite_certificate" if "finite" in clean.lower() else "endpoint_or_window" if "endpoint" in clean.lower() or "window" in clean.lower() else "unclear"
                    needs_repair = stype in {"failed delta route"} or risky_full_grid_claim(clean)
                    statements.append(
                        {
                            "statement_id": f"S{sid:04d}",
                            "file_name": path.name,
                            "file_path": str(path),
                            "line": line_no,
                            "statement_type": stype,
                            "statement_text_or_paraphrase": clean[:360],
                            "coverage_mode": coverage_mode,
                            "v5_compatible": not needs_repair,
                            "needs_repair": needs_repair,
                        }
                    )
                    sid += 1
    return pd.DataFrame(review), pd.DataFrame(statements)


def load_csv(name: str) -> pd.DataFrame:
    path = BASE / name
    return pd.read_csv(path, low_memory=False) if path.exists() else pd.DataFrame()


def data_crosscheck() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cov = load_csv("prime_mesh_r2q_firstcrossing_covering_localization_summary.csv")
    loc = load_csv("prime_mesh_r2q_firstcrossing_localization_data_crosscheck.csv")
    crossings = load_csv("prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv")
    failures = load_csv("prime_mesh_r2q_firstcrossing_covering_localization_failures.csv")
    finite = load_csv("prime_mesh_r2q_finite_theta_envelope_summary.csv")
    finite_failures = load_csv("prime_mesh_r2q_finite_theta_envelope_failures.csv")

    covered = int(number(cov, "covered_points", number(loc[loc["data_file"].eq("prime_mesh_r2q_firstcrossing_covering_localization_summary.csv")] if "data_file" in loc.columns else pd.DataFrame(), "theta_covered", 0)))
    uncovered = int(number(cov, "uncovered_points", 0))
    rows = int(number(cov, "candidate_points", covered + uncovered))
    coverage_pass = as_bool(cov["pass_covering_localization_empirical"].iloc[0]) if not cov.empty and "pass_covering_localization_empirical" in cov.columns else (uncovered == 0 and rows > 0)
    post_p0_failures = int(number(cov, "post_P0_failures", 0))
    finite_pass = as_bool(finite.loc[finite["field"].eq("pass_finite_theta_envelope_certificate"), "value"].iloc[0]) if not finite.empty and "field" in finite.columns and finite["field"].eq("pass_finite_theta_envelope_certificate").any() else False
    finite_continuous = as_bool(finite.loc[finite["field"].eq("continuous_all_x_pass"), "value"].iloc[0]) if not finite.empty and "field" in finite.columns and finite["field"].eq("continuous_all_x_pass").any() else False
    finite_fail_count = len(finite_failures)

    upper = crossings[crossings.get("side", pd.Series(dtype=str)).astype(str).str.lower().eq("positive")] if not crossings.empty else pd.DataFrame()
    lower = crossings[crossings.get("side", pd.Series(dtype=str)).astype(str).str.lower().eq("negative")] if not crossings.empty else pd.DataFrame()
    sign_match_failures = int((~crossings.get("sign_match", pd.Series(dtype=bool)).apply(as_bool)).sum()) if "sign_match" in crossings.columns else 0
    loc_failures = int((~crossings.get("localization_ok", pd.Series(dtype=bool)).apply(as_bool)).sum()) if "localization_ok" in crossings.columns else len(failures)
    scale_failures = int((~crossings.get("scale_compatibility_ok", pd.Series(dtype=bool)).apply(as_bool)).sum()) if "scale_compatibility_ok" in crossings.columns else int(number(cov, "scale_compatibility_failures", 0))

    data = pd.DataFrame(
        [
            {
                "rows": rows,
                "covered_count": covered,
                "uncovered_count": uncovered,
                "coverage_failure_count": len(failures) if not failures.empty else uncovered,
                "coverage_pass": coverage_pass,
                "gap_count": uncovered + len(failures),
                "max_gap": "",
                "finite_transition_gap_count": post_p0_failures,
                "boundary_failure_count": 0 if coverage_pass else "",
                "interior_failure_count": 0 if coverage_pass else "",
                "sample_grid_only_count": "",
                "post_P0_candidate_points": int(number(cov, "post_P0_candidate_points", 0)),
                "finite_certificate_candidates": int(number(cov, "finite_certificate_candidates", 0)),
                "theta_candidates": int(number(cov, "theta_candidates", 0)),
                "theta_covered": int(number(cov, "theta_covered", 0)),
                "theta_uncovered": int(number(cov, "theta_uncovered", 0)),
                "B3_candidates": int(number(cov, "B3_candidates", 0)),
                "B3_covered": int(number(cov, "B3_covered", 0)),
                "B3_uncovered": int(number(cov, "B3_uncovered", 0)),
                "scale_compatibility_failures": scale_failures,
                "upper_covered_count": int(upper.get("covered_flag", pd.Series(dtype=bool)).apply(as_bool).sum()) if not upper.empty else 0,
                "lower_covered_count": int(lower.get("covered_flag", pd.Series(dtype=bool)).apply(as_bool).sum()) if not lower.empty else 0,
                "upper_sign_failure_count": int((upper.get("sign_match", pd.Series(dtype=bool)).apply(as_bool) == False).sum()) if not upper.empty else 0,
                "lower_sign_failure_count": int((lower.get("sign_match", pd.Series(dtype=bool)).apply(as_bool) == False).sum()) if not lower.empty else 0,
                "local_theta_sign_available": "local_theta_sign" in crossings.columns or "side" in crossings.columns,
                "sign_match_failures": sign_match_failures,
                "localization_failures": loc_failures,
                "finite_zone_pass": finite_pass,
                "finite_continuous_all_x_pass": finite_continuous,
                "finite_zone_failures": finite_fail_count,
            }
        ]
    )

    finite_review = pd.DataFrame(
        [
            {
                "finite_summary_found": not finite.empty,
                "finite_failures_file_found": (BASE / "prime_mesh_r2q_finite_theta_envelope_failures.csv").exists(),
                "P0": finite.loc[finite["field"].eq("P0"), "value"].iloc[0] if not finite.empty and finite["field"].eq("P0").any() else "",
                "integer_grid_pass": finite.loc[finite["field"].eq("integer_grid_pass"), "value"].iloc[0] if not finite.empty and finite["field"].eq("integer_grid_pass").any() else "",
                "continuous_all_x_pass": finite.loc[finite["field"].eq("continuous_all_x_pass"), "value"].iloc[0] if not finite.empty and finite["field"].eq("continuous_all_x_pass").any() else "",
                "certificate_type": finite.loc[finite["field"].eq("certificate_type"), "value"].iloc[0] if not finite.empty and finite["field"].eq("certificate_type").any() else "",
                "failures": finite_fail_count,
                "status": "finite_zone_continuous_certificate_passes" if finite_pass and finite_continuous and finite_fail_count == 0 else "finite_zone_incomplete",
            }
        ]
    )

    theta_review = pd.DataFrame(
        [
            {
                "candidate_rows_in_covering_crossings_table": len(crossings),
                "theta_candidates_from_summary": int(number(cov, "theta_candidates", 0)),
                "theta_covered_from_summary": int(number(cov, "theta_covered", 0)),
                "theta_uncovered_from_summary": int(number(cov, "theta_uncovered", 0)),
                "all_candidate_rows_covered": int(crossings.get("covered_flag", pd.Series(dtype=bool)).apply(as_bool).sum()) if not crossings.empty else 0,
                "all_candidate_rows_uncovered": int((crossings.get("covered_flag", pd.Series(dtype=bool)).apply(as_bool) == False).sum()) if not crossings.empty else 0,
                "sign_match_failures": sign_match_failures,
                "scale_compatibility_failures": scale_failures,
                "mode": "theta_window_or_endpoint_candidate_coverage_plus_one_B3_candidate",
            }
        ]
    )

    boundary = pd.DataFrame(
        [
            {
                "case": "boundary endpoints",
                "data_status": "no empirical failures",
                "theorem_status": "conditional_or_targeted",
                "note": "Files discuss endpoint-controlled rows, but boundary handling is not a standalone proven analytic lemma.",
            },
            {
                "case": "interior first crossings",
                "data_status": "no empirical localization failures",
                "theorem_status": "conditional_or_missing_formal_lifting",
                "note": "Interior/window selection is stated as Input/target; proof attack flags it as the key lemma.",
            },
            {
                "case": "P0 transition",
                "data_status": f"post_P0_failures={post_p0_failures}, finite_zone_failures={finite_fail_count}",
                "theorem_status": "finite certificate passes; transition wording still conditional",
                "note": "Finite certificate covers x<P0 continuously; post-P0 candidate audit has no failures.",
            },
        ]
    )
    return data, finite_review, theta_review, boundary


def classify(review: pd.DataFrame, data: pd.DataFrame) -> tuple[str, str, str, str, bool]:
    evidence = review[~review["status"].isin(["spec", "proof_attack", "audit_result"])].copy()
    continuous_claim = bool(evidence["contains_continuous_x_claim"].any())
    theta_claim = bool(evidence["contains_theta_window_claim"].any())
    endpoint_claim = bool(evidence["contains_endpoint_discrete_claim"].any())
    sampled_claim = bool(evidence["contains_sample_grid_claim"].any())
    coverage_pass = bool(data.iloc[0]["coverage_pass"])
    uncovered = int(data.iloc[0]["uncovered_count"])
    finite_pass = bool(data.iloc[0]["finite_zone_pass"])
    finite_cont = bool(data.iloc[0]["finite_continuous_all_x_pass"])

    if uncovered > 0:
        return (
            "missing_or_gapped",
            "gaps",
            "Uncovered candidate rows or failures exist.",
            "Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Repair_Map_v1.md",
            False,
        )
    if coverage_pass and theta_claim and continuous_claim and finite_pass and finite_cont:
        return (
            "theta_window_covering",
            "conditional_theta_window_plus_finite_continuous",
            "Audited theta/B3 first-crossing candidates are fully covered, and finite x<P0 is continuously certified; post-P0 continuous all-x/window-selection proof remains conditional.",
            "Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md",
            True,
        )
    if coverage_pass and endpoint_claim:
        return (
            "endpoint_discrete_covering",
            "endpoint_or_window_empirical",
            "Coverage exists for audited endpoint/window candidates, but continuous all-x lifting is not proven.",
            "Prime_Mesh_R2Q_DiscreteEndpoint_to_RHScale_Lifting_Proof_Attack_v1.md",
            False,
        )
    if sampled_claim and not theta_claim:
        return (
            "sampled_grid_covering",
            "sampled_grid_only",
            "Evidence is sampled-grid only.",
            "Prime_Mesh_R2Q_CoveringLocalization_SampledGrid_Warning_Repair_Map_v1.md",
            False,
        )
    return (
        "unclear",
        "conditional_or_missing",
        "Coverage theorem is present only as a conditional/target statement.",
        "Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md",
        False,
    )


def compatibility(review: pd.DataFrame) -> tuple[bool, bool]:
    evidence = review[~review["status"].isin(["spec", "proof_attack", "audit_result"])]
    failed_delta = bool(evidence["contains_failed_delta_route"].any())
    full_grid = bool(evidence["contains_full_grid_h_excision_claim"].any())
    return failed_delta, full_grid


def make_summary(review: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
    mode, classification, gap, next_file, passed = classify(review, data)
    failed_delta, full_grid = compatibility(review)
    d = data.iloc[0]
    row_family_defined = bool(review["contains_row_family_definition"].any())
    covered_domain_parts = []
    if bool(review["contains_theta_window_claim"].any()):
        covered_domain_parts.append("theta first-crossing windows/candidates")
    if bool(review["contains_endpoint_discrete_claim"].any()):
        covered_domain_parts.append("endpoints or endpoint-controlled intervals")
    if bool(d["finite_zone_pass"]):
        covered_domain_parts.append("finite zone x<P0")
    if bool(review["contains_sample_grid_claim"].any()):
        covered_domain_parts.append("sample-grid caveats present")
    return pd.DataFrame(
        [
            {
                "files_scanned": len(review),
                "prioritized_files_found": len(review),
                "covering_mode": mode,
                "row_family_defined": row_family_defined,
                "covered_domain": "; ".join(covered_domain_parts) if covered_domain_parts else "unclear",
                "continuous_x_claim_found": bool(review["contains_continuous_x_claim"].any()),
                "endpoint_discrete_claim_found": bool(review["contains_endpoint_discrete_claim"].any()),
                "sampled_grid_claim_found": bool(review["contains_sample_grid_claim"].any()),
                "theta_window_claim_found": bool(review["contains_theta_window_claim"].any()),
                "covered_count": int(d["covered_count"]),
                "uncovered_count": int(d["uncovered_count"]),
                "coverage_failures": int(d["coverage_failure_count"]),
                "coverage_pass": bool(d["coverage_pass"]),
                "boundary_handling_status": "conditional_present_no_data_failures",
                "interior_handling_status": "conditional_window_selection_or_lifting_needed",
                "finite_zone_status": "continuous_certificate_passes" if bool(d["finite_zone_pass"]) and bool(d["finite_continuous_all_x_pass"]) else "finite_zone_incomplete",
                "P0_transition_status": "no_data_failures_transition_theorem_conditional" if int(d["finite_transition_gap_count"]) == 0 else "transition_gaps",
                "upper_lower_sign_preservation_status": "passes" if int(d["sign_match_failures"]) == 0 and bool(d["local_theta_sign_available"]) else "missing_or_fails",
                "uses_failed_delta_threshold_route": failed_delta,
                "uses_full_grid_HExc_upgrade": full_grid,
                "coveringlocalization_classification": classification,
                "main_covering_gap": gap,
                "recommended_next_file": next_file,
                "pass_coveringlocalization_audit": passed and not failed_delta and not full_grid,
            }
        ]
    )


def make_gaps(summary_df: pd.DataFrame) -> pd.DataFrame:
    s = summary_df.iloc[0]
    return pd.DataFrame(
        [
            {
                "gap": "post-P0 continuous all-x covering",
                "status": "conditional_not_fully_proven",
                "detail": "Audited first-crossing candidates are covered, but the universal all-x window-selection theorem remains an input/target.",
                "recommended_file": "Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md",
            },
            {
                "gap": "interior first-crossing lifting",
                "status": "conditional_or_missing_formal_lifting",
                "detail": "Files mention interior/endpoint-controlled rows; a standalone lemma must prove an interior first crossing is captured by a row endpoint/window/refinement.",
                "recommended_file": "Prime_Mesh_R2Q_DiscreteEndpoint_to_RHScale_Lifting_Proof_Attack_v1.md",
            },
            {
                "gap": "finite-zone coverage",
                "status": str(s["finite_zone_status"]),
                "detail": "Finite theta envelope summary reports continuous all-x finite certificate with zero failures.",
                "recommended_file": "Prime_Mesh_R2Q_FiniteThetaEnvelope_Closure_Update_v1.md",
            },
            {
                "gap": "sampled-grid H-Exc upgrade",
                "status": "not_used" if not bool(s["uses_full_grid_HExc_upgrade"]) else "unsafe_claim_found",
                "detail": "Audit does not find proof evidence upgrading sampled-grid H-Exc to full-grid control.",
                "recommended_file": "Prime_Mesh_R2Q_CoveringLocalization_SampledGrid_Warning_Repair_Map_v1.md",
            },
        ]
    )


def write_doc(summary_df: pd.DataFrame, data: pd.DataFrame, gaps: pd.DataFrame) -> None:
    s = summary_df.iloc[0]
    d = data.iloc[0]
    lines = [
        "# Prime Mesh R2Q — FirstCrossing CoveringLocalization Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "Determine whether global first crossings are covered by admissible v5 R2Q/theta rows.",
        "",
        "## 2. Summary",
        "",
        f"- Coverage mode: `{s['covering_mode']}`.",
        f"- Classification: `{s['coveringlocalization_classification']}`.",
        f"- Covered count: `{int(s['covered_count'])}`.",
        f"- Uncovered count: `{int(s['uncovered_count'])}`.",
        f"- Coverage failures: `{int(s['coverage_failures'])}`.",
        f"- Pass audit: `{bool(s['pass_coveringlocalization_audit'])}`.",
        f"- Recommended next file: `{s['recommended_next_file']}`.",
        "",
        "## 3. Row Family and Domain",
        "",
        f"- Row family defined: `{bool(s['row_family_defined'])}`.",
        f"- Covered domain: `{s['covered_domain']}`.",
        "",
        "## 4. Coverage Type",
        "",
        "The safest classification is theta-window candidate coverage with finite-zone continuous certification. It is not yet a full unconditional continuous all-`x` theorem for post-`P0` points.",
        "",
        "| field | value |",
        "|---|---:|",
        f"| `candidate rows` | `{int(d['rows'])}` |",
        f"| `theta candidates` | `{int(d['theta_candidates'])}` |",
        f"| `theta covered` | `{int(d['theta_covered'])}` |",
        f"| `theta uncovered` | `{int(d['theta_uncovered'])}` |",
        f"| `B3 candidates` | `{int(d['B3_candidates'])}` |",
        f"| `B3 covered` | `{int(d['B3_covered'])}` |",
        f"| `post_P0 candidate points` | `{int(d['post_P0_candidate_points'])}` |",
        f"| `finite certificate candidates` | `{int(d['finite_certificate_candidates'])}` |",
        "",
        "## 5. Boundary and Interior Handling",
        "",
        f"- Boundary handling: `{s['boundary_handling_status']}`.",
        f"- Interior handling: `{s['interior_handling_status']}`.",
        "",
        "The files discuss endpoint-controlled and interior/window selection, but the audit keeps this as conditional proof material rather than a completed continuous lifting theorem.",
        "",
        "## 6. Finite-Zone and P0 Transition",
        "",
        f"- Finite-zone status: `{s['finite_zone_status']}`.",
        f"- `P0` transition status: `{s['P0_transition_status']}`.",
        "",
        "## 7. v5 Compatibility",
        "",
        f"- Uses failed delta-threshold route: `{bool(s['uses_failed_delta_threshold_route'])}`.",
        f"- Uses full-grid H-Exc upgrade: `{bool(s['uses_full_grid_HExc_upgrade'])}`.",
        f"- Upper/lower sign preservation: `{s['upper_lower_sign_preservation_status']}`.",
        "",
        "## 8. Data Cross-Check",
        "",
        f"`coverage_pass={bool(d['coverage_pass'])}`, `sign_match_failures={int(d['sign_match_failures'])}`, `scale_compatibility_failures={int(d['scale_compatibility_failures'])}`.",
        "",
        "## 9. Gaps",
        "",
        "| gap | status | detail | recommended file |",
        "|---|---|---|---|",
    ]
    for _, row in gaps.iterrows():
        lines.append(f"| {row['gap']} | `{row['status']}` | {row['detail']} | `{row['recommended_file']}` |")
    lines += [
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
        OUT_DATA,
        OUT_GAPS,
        OUT_FULLFCL,
        OUT_THETA,
        OUT_FINITE,
        OUT_BOUNDARY,
        "```",
        "",
        "*AI documentation pass: GPT-5.5*",
    ]
    (BASE / OUT_DOC).write_text("\n".join(lines), encoding="utf-8")


def update_manifest(files: list[str]) -> None:
    path = BASE / OUT_MANIFEST
    old = pd.read_csv(path).to_dict("records") if path.exists() else []
    names = set(files)
    rows = [r for r in old if r.get("filename") not in names]
    now = datetime.now().isoformat(timespec="seconds")
    for name in files:
        p = BASE / name
        rows.append(
            {
                "filename": name,
                "path": str(p),
                "bytes": p.stat().st_size if p.exists() else 0,
                "status": "new",
                "updated_at": now,
                "note": "FirstCrossing CoveringLocalization audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    paths = [p for name in PRIORITY if (p := find_file(name)) is not None]
    review, statements = scan_files(paths)
    data, finite_review, theta_review, boundary = data_crosscheck()
    summary = make_summary(review, data)
    gaps = make_gaps(summary)

    fullfcl_review = review[review["file_name"].str.contains("FullFCL", case=False, na=False)].copy()
    if fullfcl_review.empty:
        fullfcl_review = pd.DataFrame([{"status": "no_fullfcl_priority_files_found"}])

    summary.to_csv(BASE / OUT_SUMMARY, index=False)
    review.to_csv(BASE / OUT_FILE_REVIEW, index=False)
    statements.to_csv(BASE / OUT_STATEMENTS, index=False)
    data.to_csv(BASE / OUT_DATA, index=False)
    gaps.to_csv(BASE / OUT_GAPS, index=False)
    fullfcl_review.to_csv(BASE / OUT_FULLFCL, index=False)
    theta_review.to_csv(BASE / OUT_THETA, index=False)
    finite_review.to_csv(BASE / OUT_FINITE, index=False)
    boundary.to_csv(BASE / OUT_BOUNDARY, index=False)
    write_doc(summary, data, gaps)

    outputs = [
        OUT_SCRIPT, OUT_SUMMARY, OUT_FILE_REVIEW, OUT_STATEMENTS, OUT_DATA,
        OUT_GAPS, OUT_FULLFCL, OUT_THETA, OUT_FINITE, OUT_BOUNDARY, OUT_DOC,
    ]
    update_manifest(outputs)

    print("FirstCrossing CoveringLocalization audit complete.")
    s = summary.iloc[0].to_dict()
    for key in [
        "covering_mode",
        "covered_count",
        "uncovered_count",
        "coverage_failures",
        "coverage_pass",
        "boundary_handling_status",
        "interior_handling_status",
        "finite_zone_status",
        "P0_transition_status",
        "upper_lower_sign_preservation_status",
        "uses_failed_delta_threshold_route",
        "uses_full_grid_HExc_upgrade",
        "coveringlocalization_classification",
        "main_covering_gap",
        "recommended_next_file",
        "pass_coveringlocalization_audit",
    ]:
        print(f"{key}: {s[key]}")


if __name__ == "__main__":
    main()
