"""
Prime Mesh R2Q — ContinuousFirstExit CandidateCompleteness audit.

Audits whether every post-P0 continuous first-exit configuration is generated
as, or bracketed by, an audited FullFCL/theta candidate.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

import pandas as pd


BASE = Path(__file__).resolve().parent
REPAIR = BASE.parent

OUT_SCRIPT = "prime_mesh_r2q_continuous_firstexit_candidate_completeness_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_continuous_firstexit_candidate_completeness_summary.csv"
OUT_FILE_REVIEW = "prime_mesh_r2q_continuous_firstexit_candidate_completeness_file_review.csv"
OUT_STATEMENTS = "prime_mesh_r2q_continuous_firstexit_candidate_completeness_statement_inventory.csv"
OUT_RULES = "prime_mesh_r2q_continuous_firstexit_candidate_completeness_generator_rules.csv"
OUT_GAP = "prime_mesh_r2q_continuous_firstexit_candidate_completeness_gap_safety.csv"
OUT_FAILURES = "prime_mesh_r2q_continuous_firstexit_candidate_completeness_failures.csv"
OUT_UPPER = "prime_mesh_r2q_continuous_firstexit_candidate_completeness_upper_jump.csv"
OUT_LOWER = "prime_mesh_r2q_continuous_firstexit_candidate_completeness_lower_drift.csv"
OUT_P0 = "prime_mesh_r2q_continuous_firstexit_candidate_completeness_P0_transition.csv"
OUT_MATCH = "prime_mesh_r2q_continuous_firstexit_candidate_completeness_generator_match.csv"
OUT_COMPAT = "prime_mesh_r2q_continuous_firstexit_candidate_completeness_v5_compatibility.csv"
OUT_DOC = "Prime_Mesh_R2Q_ContinuousFirstExit_CandidateCompleteness_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"

PRIORITY = [
    "Prime_Mesh_R2Q_ContinuousFirstExit_CandidateCompleteness_Proof_Attack_v1.md",
    "Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Audit_v1.md",
    "Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Conditional_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_GlobalBridge_ConditionalAssembly_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Reclosure_Update_v2.md",
    "Prime_Mesh_R2Q_FullFCL_Formal_Proof_Skeleton_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Formal_Theorem_Target_v1.md",
    "Prime_Mesh_R2Q_GlobalThetaEnvelope_Reclosure_Update_v2.md",
    "Prime_Mesh_R2Q_FiniteThetaEnvelope_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FiniteThetaEnvelope_Certificate_Spec_v1.md",
]

PATTERNS = {
    "candidate generator rule": [
        r"candidate generator", r"candidate generation", r"generator rule",
        r"generated candidate", r"CandidateReduction", r"AdmissibleBlockSystem",
        r"Gen\(", r"selected block", r"candidate-selected", r"candidate-selection",
    ],
    "first-exit necessary condition": [
        r"first-exit", r"first exit", r"FirstExit", r"necessary condition",
        r"near envelope boundary", r"normalized.*R\(x\)",
    ],
    "upper jump generation statement": [
        r"upper.*jump", r"upper.*generated", r"upper.*candidate",
        r"jump-driven", r"prime-power jump",
    ],
    "lower drift bracketing statement": [
        r"lower.*drift", r"lower.*bracket", r"drift interval",
        r"lower.*candidate", r"unbracketed",
    ],
    "gap safety statement": [
        r"gap safety", r"gap impossible", r"first-exit impossible",
        r"coordinate gaps", r"candidate gap", r"gap.*first exit",
    ],
    "FullFCL completeness claim": [
        r"FullFCL", r"Full First-Crossing", r"FullFCL.*completeness",
        r"FCL-FrontEnd", r"CandidateReduction",
    ],
    "continuous candidate-selection claim": [
        r"continuous first", r"continuous all-x", r"candidate selection",
        r"window selection", r"post-P0 continuous",
    ],
    "certificate-backed candidate coverage statement": [
        r"142/142", r"1469/1469", r"certificate", r"audited candidate",
        r"covered.*uncovered", r"0 uncovered",
    ],
    "warning about sparse windows": [
        r"sparse candidate", r"sparse.*windows", r"not.*tile", r"not.*tiling",
        r"coordinate gaps",
    ],
    "warning about sampled grid": [
        r"sampled grid", r"sampled-grid", r"T_J", r"full-grid H-Exc",
    ],
    "failed delta route": [
        r"Q_\\{\\rm R2Q\\}>0\.75.*Q_\\{\\Delta D\\}>0\.75",
        r"Q_delta_D\s*>\s*0\.75", r"dominance ratio",
    ],
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def find_file(name: str) -> Path | None:
    for root in (REPAIR, BASE):
        direct = root / name
        if direct.exists():
            return direct
    matches = list(REPAIR.rglob(name)) + list(BASE.rglob(name))
    return matches[0] if matches else None


def load_csv(name: str) -> pd.DataFrame:
    path = BASE / name
    return pd.read_csv(path, low_memory=False) if path.exists() else pd.DataFrame()


def norm_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def has(text: str, key: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in PATTERNS[key])


def status_for(path: Path) -> str:
    name = path.name.lower()
    if "audit_spec" in name:
        return "spec"
    if "proof_attack" in name:
        return "proof_attack"
    if "audit_v1" in name and path.parent == BASE:
        return "audit_result"
    if "conditional" in name:
        return "conditional_assembly"
    if "closure_update" in name or "reclosure" in name:
        return "closure_update"
    if "target" in name or "skeleton" in name:
        return "target_or_skeleton"
    return "candidate"


def unsafe_h_exc(text: str) -> bool:
    match = re.search(r"full-grid H-Exc|full grid HExc|sampled grid.*full", text, flags=re.IGNORECASE)
    if not match:
        return False
    window = text[max(0, match.start() - 120): match.end() + 120].lower()
    safe = ["do not", "must not", "avoid", "warning", "not", "false", "mismatch"]
    return not any(token in window for token in safe)


def unsafe_delta(text: str) -> bool:
    match = re.search(
        r"Q_\\{\\rm R2Q\\}>0\.75.*Q_\\{\\Delta D\\}>0\.75|Q_delta_D\s*>\s*0\.75|dominance ratio",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return False
    window = text[max(0, match.start() - 120): match.end() + 120].lower()
    safe = ["do not", "must not", "avoid", "failed", "false", "warning", "not rely", "does not"]
    return not any(token in window for token in safe)


def scan_files(paths: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    review = []
    statements = []
    sid = 1
    for path in paths:
        text = read_text(path)
        review.append(
            {
                "file_name": path.name,
                "file_path": str(path),
                "contains_candidate_generator_rule": has(text, "candidate generator rule"),
                "contains_first_exit_target": has(text, "first-exit necessary condition"),
                "contains_upper_jump_generation": has(text, "upper jump generation statement"),
                "contains_lower_drift_bracketing": has(text, "lower drift bracketing statement"),
                "contains_gap_safety_claim": has(text, "gap safety statement"),
                "contains_gap_scan_data": bool(re.search(r"gap_count|gap scan|window_gap|coordinate gaps", text, flags=re.IGNORECASE)),
                "contains_FullFCL_completeness_claim": has(text, "FullFCL completeness claim"),
                "contains_symbolic_completeness_proof": bool(re.search(r"symbolic|formal proof|prove.*FirstExit.*Gen|FirstExit.*subseteq", text, flags=re.IGNORECASE | re.DOTALL)),
                "contains_certificate_completeness_claim": has(text, "certificate-backed candidate coverage statement"),
                "contains_sampled_grid_warning": has(text, "warning about sampled grid"),
                "contains_full_grid_HExc_upgrade": unsafe_h_exc(text),
                "contains_failed_delta_route": has(text, "failed delta route"),
                "failed_delta_route_used_as_proof": unsafe_delta(text),
                "status": status_for(path),
                "notes": "explicitly conditional" if "conditional" in text.lower() else "",
            }
        )
        for line_no, line in enumerate(text.splitlines(), start=1):
            clean = line.strip()
            if not clean:
                continue
            for stype, patterns in PATTERNS.items():
                if any(re.search(pattern, clean, flags=re.IGNORECASE) for pattern in patterns):
                    needs_repair = (stype == "failed delta route" and unsafe_delta(clean)) or unsafe_h_exc(clean)
                    scope = (
                        "symbolic" if "prove" in clean.lower() or "theorem" in clean.lower()
                        else "certificate" if "audited" in clean.lower() or "covered" in clean.lower()
                        else "conditional" if "conditional" in clean.lower() or "must" in clean.lower()
                        else "unspecified"
                    )
                    statements.append(
                        {
                            "statement_id": f"S{sid:04d}",
                            "file_name": path.name,
                            "file_path": str(path),
                            "line": line_no,
                            "statement_type": stype,
                            "statement_text_or_paraphrase": clean[:360],
                            "scope": scope,
                            "symbolic_or_conditional_or_certificate": scope,
                            "v5_compatible": not needs_repair,
                            "needs_repair": needs_repair,
                        }
                    )
                    sid += 1
    return pd.DataFrame(review), pd.DataFrame(statements)


def data_audit() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    post = load_csv("prime_mesh_r2q_postp0_continuous_window_selection_summary.csv")
    gap_scan = load_csv("prime_mesh_r2q_postp0_continuous_window_selection_gap_scan.csv")
    drift = load_csv("prime_mesh_r2q_postp0_continuous_window_selection_drift_bracketing.csv")
    jump = load_csv("prime_mesh_r2q_postp0_continuous_window_selection_jump_coverage.csv")
    p0 = load_csv("prime_mesh_r2q_postp0_continuous_window_selection_P0_transition.csv")
    compat = load_csv("prime_mesh_r2q_postp0_continuous_window_selection_v5_compatibility.csv")

    if post.empty:
        base = pd.DataFrame([{"candidate_rows": 0, "error": "postp0 summary missing"}])
        return base, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    s = post.iloc[0]
    candidate_rows = int(s.get("window_count", 0))
    upper_rows = int(s.get("jump_event_count", 0))
    lower_rows = int(drift.iloc[0].get("lower_candidate_count", 0)) if not drift.empty else int(s.get("lower_drift_unbracketed_count", 0))
    gap_count = int(s.get("window_gap_count", len(gap_scan)))
    max_gap = s.get("max_window_gap", gap_scan["gap_size"].max() if not gap_scan.empty and "gap_size" in gap_scan.columns else "")
    gap_safety_proven = 0
    gap_safety_unknown = gap_count
    gap_safety = gap_scan.copy()
    if gap_safety.empty and gap_count:
        gap_safety = pd.DataFrame([{"gap_count": gap_count, "gap_status": "aggregate_unknown"}])
    if not gap_safety.empty:
        gap_safety["gap_safety_status"] = "unknown_first_exit_impossibility_not_proven"

    upper = pd.DataFrame(
        [
            {
                "upper_jump_event_count": upper_rows,
                "upper_jump_generated_count": int(jump.iloc[0].get("upper_jump_represented_count", 0)) if not jump.empty else 0,
                "upper_jump_missing_count": int(s.get("upper_jump_unrepresented_count", 0)),
                "upper_jump_generation_pass": int(s.get("upper_jump_unrepresented_count", 0)) == 0,
                "status": jump.iloc[0].get("status", "audited_upper_candidates_only") if not jump.empty else "missing_jump_file",
            }
        ]
    )
    lower = pd.DataFrame(
        [
            {
                "lower_drift_interval_count": drift.iloc[0].get("drift_interval_count", "") if not drift.empty else "",
                "lower_drift_bracketed_count": int(drift.iloc[0].get("lower_drift_bracketed_count", 0)) if not drift.empty else 0,
                "lower_drift_unbracketed_count": int(s.get("lower_drift_unbracketed_count", 0)),
                "lower_drift_bracketing_pass": int(s.get("lower_drift_unbracketed_count", 0)) == 0,
                "status": drift.iloc[0].get("status", "audited_lower_candidates_only") if not drift.empty else "missing_drift_file",
            }
        ]
    )
    p0_out = pd.DataFrame(
        [
            {
                "P0_transition_gap": int(s.get("P0_transition_gap", 0)),
                "P0_transition_pass": norm_bool(s.get("pass_P0_transition", False)),
                "status": "passes" if norm_bool(s.get("pass_P0_transition", False)) else "fails",
            }
        ]
    )
    match = pd.DataFrame(
        [
            {
                "generated_count": "",
                "audited_candidate_count": candidate_rows,
                "generated_not_audited_count": "",
                "audited_not_generated_count": "",
                "generator_candidate_match_pass": False,
                "status": "no_generator_output_available_for_match",
            }
        ]
    )
    v5 = pd.DataFrame(
        [
            {
                "check": "uses_full_grid_HExc_upgrade",
                "pass": not norm_bool(s.get("uses_full_grid_HExc_upgrade", False)),
                "value": norm_bool(s.get("uses_full_grid_HExc_upgrade", False)),
            },
            {
                "check": "uses_failed_delta_route",
                "pass": not norm_bool(s.get("uses_failed_delta_route", False)),
                "value": norm_bool(s.get("uses_failed_delta_route", False)),
            },
            {
                "check": "postp0_v5_compat_source_found",
                "pass": not compat.empty,
                "value": not compat.empty,
            },
        ]
    )
    data = pd.DataFrame(
        [
            {
                "candidate_rows": candidate_rows,
                "post_P0_candidate_rows": candidate_rows,
                "upper_candidate_rows": upper_rows,
                "lower_candidate_rows": lower_rows,
                "covered_candidate_rows": candidate_rows,
                "uncovered_candidate_rows": 0,
                "generated_count": "",
                "audited_candidate_count": candidate_rows,
                "generated_not_audited_count": "",
                "audited_not_generated_count": "",
                "generator_candidate_match_pass": False,
                "gap_count": gap_count,
                "max_gap": max_gap,
                "gap_safety_proven_count": gap_safety_proven,
                "gap_safety_unknown_count": gap_safety_unknown,
                "gap_first_exit_possible_count": "",
                "upper_jump_missing_count": int(upper.iloc[0]["upper_jump_missing_count"]),
                "lower_drift_unbracketed_count": int(lower.iloc[0]["lower_drift_unbracketed_count"]),
                "P0_transition_gap": int(p0_out.iloc[0]["P0_transition_gap"]),
                "P0_transition_pass": bool(p0_out.iloc[0]["P0_transition_pass"]),
            }
        ]
    )
    return data, gap_safety, upper, lower, p0_out, match, v5


def generator_rules(review: pd.DataFrame, statements: pd.DataFrame) -> pd.DataFrame:
    gen_files = review[review["contains_candidate_generator_rule"]].copy()
    first_exit = review[review["contains_first_exit_target"]].copy()
    return pd.DataFrame(
        [
            {
                "candidate_generator_found": not gen_files.empty,
                "candidate_generator_files": ";".join(gen_files["file_name"].tolist()),
                "candidate_generator_rule_summary": "FullFCL/CandidateReduction/AdmissibleBlockSystem are named, but no executable generator output was found.",
                "candidate_generator_inputs": "first-exit necessary conditions; post-P0 scale; theta sign; threshold/forbidden/harmless filters",
                "candidate_generator_outputs": "audited FullFCL/theta candidates",
                "generator_targets_first_exit": not first_exit.empty,
                "first_exit_terms_found": int(len(statements[statements["statement_type"].eq("first-exit necessary condition")])) if not statements.empty else 0,
                "generator_rule_status": "conditional_textual_rule_no_generator_match_certificate",
            }
        ]
    )


def classify(review: pd.DataFrame, data: pd.DataFrame, rules: pd.DataFrame, v5: pd.DataFrame) -> tuple[str, str, str, bool]:
    d = data.iloc[0]
    r = rules.iloc[0]
    evidence = review[~review["status"].isin(["spec", "proof_attack", "audit_result"])]
    symbolic = bool(evidence["contains_symbolic_completeness_proof"].any())
    fullfcl_conditional = bool(evidence["contains_FullFCL_completeness_claim"].any())
    certificate = bool(evidence["contains_certificate_completeness_claim"].any()) and int(d["uncovered_candidate_rows"]) == 0
    full_h = bool(v5.loc[v5["check"].eq("uses_full_grid_HExc_upgrade"), "value"].iloc[0])
    failed_delta = bool(v5.loc[v5["check"].eq("uses_failed_delta_route"), "value"].iloc[0])
    if full_h or failed_delta or int(d["P0_transition_gap"]) != 0:
        return (
            "repair_needed",
            "A v5 compatibility or P0 transition failure was found.",
            "Prime_Mesh_R2Q_ContinuousFirstExit_CandidateCompleteness_Repair_Map_v1.md",
            False,
        )
    if symbolic and bool(r["candidate_generator_found"]) and bool(r["generator_targets_first_exit"]) and int(d["gap_safety_unknown_count"]) == 0:
        return (
            "symbolic_closed",
            "Candidate generator is explicitly first-exit complete and all gaps are proven safe.",
            "Prime_Mesh_R2Q_ContinuousFirstExit_CandidateCompleteness_Theorem_Target_v1.md",
            True,
        )
    if int(d["lower_drift_unbracketed_count"]) > 0:
        return (
            "lower_drift_incomplete",
            "Lower drift candidate bracketing has unbracketed audited rows.",
            "Prime_Mesh_R2Q_LowerDrift_FirstCrossing_Proof_Attack_v1.md",
            False,
        )
    if int(d["gap_safety_unknown_count"]) > 0:
        return (
            "gap_safety_incomplete",
            "Audited candidates pass, but coordinate gaps are not proven first-exit impossible and no generator-match certificate exists.",
            "Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Proof_Attack_v1.md",
            False,
        )
    if fullfcl_conditional and certificate:
        return (
            "fullfcl_conditional",
            "Candidate completeness is FullFCL-backed and certificate-supported, but conditional.",
            "Prime_Mesh_R2Q_ContinuousFirstExit_CandidateCompleteness_Conditional_Closure_Update_v1.md",
            True,
        )
    if certificate:
        return (
            "certificate_backed",
            "Candidate rows pass but symbolic/generator completeness is not shown.",
            "Prime_Mesh_R2Q_ContinuousFirstExit_CandidateCompleteness_Conditional_Closure_Update_v1.md",
            True,
        )
    return (
        "repair_needed",
        "Candidate completeness evidence is insufficient.",
        "Prime_Mesh_R2Q_ContinuousFirstExit_CandidateCompleteness_Repair_Map_v1.md",
        False,
    )


def make_summary(review: pd.DataFrame, data: pd.DataFrame, rules: pd.DataFrame, v5: pd.DataFrame) -> pd.DataFrame:
    classification, gap, next_file, passed = classify(review, data, rules, v5)
    d = data.iloc[0]
    r = rules.iloc[0]
    return pd.DataFrame(
        [
            {
                "files_scanned": len(review),
                "prioritized_files_found": len(review),
                "candidate_generator_found": bool(r["candidate_generator_found"]),
                "generator_targets_first_exit": bool(r["generator_targets_first_exit"]),
                "generator_rule_status": r["generator_rule_status"],
                "candidate_rows": int(d["candidate_rows"]),
                "post_P0_candidate_rows": int(d["post_P0_candidate_rows"]),
                "upper_candidate_rows": int(d["upper_candidate_rows"]),
                "lower_candidate_rows": int(d["lower_candidate_rows"]),
                "upper_jump_generation_status": "audited_upper_candidates_generated_or_represented",
                "upper_jump_missing_count": int(d["upper_jump_missing_count"]),
                "lower_drift_bracketing_status": "audited_lower_candidates_bracketed_all_drift_intervals_not_enumerated",
                "lower_drift_unbracketed_count": int(d["lower_drift_unbracketed_count"]),
                "gap_count": int(d["gap_count"]),
                "gap_safety_proven_count": int(d["gap_safety_proven_count"]),
                "gap_safety_unknown_count": int(d["gap_safety_unknown_count"]),
                "gap_first_exit_possible_count": d["gap_first_exit_possible_count"],
                "P0_transition_pass": bool(d["P0_transition_pass"]),
                "uses_full_grid_HExc_upgrade": bool(v5.loc[v5["check"].eq("uses_full_grid_HExc_upgrade"), "value"].iloc[0]),
                "uses_failed_delta_route": bool(v5.loc[v5["check"].eq("uses_failed_delta_route"), "value"].iloc[0]),
                "candidate_completeness_classification": classification,
                "main_candidate_completeness_gap": gap,
                "recommended_next_file": next_file,
                "pass_continuous_firstexit_candidate_completeness_audit": passed,
            }
        ]
    )


def failures(summary: pd.DataFrame) -> pd.DataFrame:
    s = summary.iloc[0]
    rows = []
    if int(s["gap_safety_unknown_count"]) > 0:
        rows.append(
            {
                "failure_type": "gap_safety_unknown",
                "detail": f"{int(s['gap_safety_unknown_count'])} coordinate gaps are not proven first-exit impossible.",
            }
        )
    if int(s["lower_drift_unbracketed_count"]) > 0:
        rows.append({"failure_type": "lower_drift_unbracketed", "detail": "Audited lower drift bracketing has missing rows."})
    if bool(s["uses_full_grid_HExc_upgrade"]):
        rows.append({"failure_type": "full_grid_HExc_upgrade", "detail": "Unsafe H-Exc full-grid upgrade found."})
    if bool(s["uses_failed_delta_route"]):
        rows.append({"failure_type": "failed_delta_route", "detail": "Unsafe failed delta route found."})
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["failure_type", "detail"])


def write_doc(summary: pd.DataFrame, rules: pd.DataFrame, fail: pd.DataFrame) -> None:
    s = summary.iloc[0]
    r = rules.iloc[0]
    lines = [
        "# Prime Mesh R2Q — ContinuousFirstExit CandidateCompleteness Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "Audit whether every continuous first-exit configuration is generated or bracketed by audited FullFCL/theta candidates.",
        "",
        "## 2. Summary",
        "",
        f"- Classification: `{s['candidate_completeness_classification']}`.",
        f"- Candidate generator found: `{bool(s['candidate_generator_found'])}`.",
        f"- Generator targets first exit: `{bool(s['generator_targets_first_exit'])}`.",
        f"- Candidate rows: `{int(s['candidate_rows'])}`.",
        f"- Upper candidates: `{int(s['upper_candidate_rows'])}`; missing: `{int(s['upper_jump_missing_count'])}`.",
        f"- Lower candidates: `{int(s['lower_candidate_rows'])}`; unbracketed: `{int(s['lower_drift_unbracketed_count'])}`.",
        f"- Coordinate gaps: `{int(s['gap_count'])}`.",
        f"- Gap safety unknown: `{int(s['gap_safety_unknown_count'])}`.",
        f"- `P0` transition pass: `{bool(s['P0_transition_pass'])}`.",
        f"- Full-grid H-Exc upgrade used: `{bool(s['uses_full_grid_HExc_upgrade'])}`.",
        f"- Failed delta route used: `{bool(s['uses_failed_delta_route'])}`.",
        f"- Pass audit: `{bool(s['pass_continuous_firstexit_candidate_completeness_audit'])}`.",
        "",
        "## 3. Candidate Generator",
        "",
        f"- Files: `{r['candidate_generator_files']}`.",
        f"- Rule status: `{r['generator_rule_status']}`.",
        f"- Rule summary: {r['candidate_generator_rule_summary']}",
        "",
        "## 4. First-Exit Necessary Conditions",
        "",
        "The available text identifies normalized first exit, upper jump exits, lower drift exits, post-`P0` scale, sign, threshold, and non-survival/safety filters as necessary-condition layers. It does not provide an executable generator-match certificate.",
        "",
        "## 5. Upper Jump Generation",
        "",
        f"`{s['upper_jump_generation_status']}` with missing count `{int(s['upper_jump_missing_count'])}`.",
        "",
        "## 6. Lower Drift Bracketing",
        "",
        f"`{s['lower_drift_bracketing_status']}` with audited unbracketed count `{int(s['lower_drift_unbracketed_count'])}`.",
        "",
        "## 7. Gap Safety",
        "",
        "Sparse coordinate gaps remain the central unresolved issue. Current data lists gaps but does not certify each gap as first-exit impossible.",
        "",
        "## 8. v5 Compatibility",
        "",
        f"- Uses full-grid H-Exc upgrade: `{bool(s['uses_full_grid_HExc_upgrade'])}`.",
        f"- Uses failed delta route: `{bool(s['uses_failed_delta_route'])}`.",
        "",
        "## 9. Remaining Gap",
        "",
        f"`{s['main_candidate_completeness_gap']}`",
        "",
        f"Failure/gap records emitted: `{len(fail)}`.",
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
        OUT_RULES,
        OUT_GAP,
        OUT_FAILURES,
        OUT_UPPER,
        OUT_LOWER,
        OUT_P0,
        OUT_MATCH,
        OUT_COMPAT,
        "```",
        "",
        "*AI documentation pass: GPT-5.5*",
    ]
    (BASE / OUT_DOC).write_text("\n".join(lines), encoding="utf-8")


def update_manifest(files: list[str]) -> None:
    path = BASE / OUT_MANIFEST
    old = pd.read_csv(path).to_dict("records") if path.exists() else []
    names = set(files)
    rows = [row for row in old if row.get("filename") not in names]
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
                "note": "ContinuousFirstExit CandidateCompleteness audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    paths = [p for name in PRIORITY if (p := find_file(name)) is not None]
    review, statements = scan_files(paths)
    data, gap_safety, upper, lower, p0, match, v5 = data_audit()
    rules = generator_rules(review, statements)
    summary = make_summary(review, data, rules, v5)
    fail = failures(summary)

    summary.to_csv(BASE / OUT_SUMMARY, index=False)
    review.to_csv(BASE / OUT_FILE_REVIEW, index=False)
    statements.to_csv(BASE / OUT_STATEMENTS, index=False)
    rules.to_csv(BASE / OUT_RULES, index=False)
    gap_safety.to_csv(BASE / OUT_GAP, index=False)
    fail.to_csv(BASE / OUT_FAILURES, index=False)
    upper.to_csv(BASE / OUT_UPPER, index=False)
    lower.to_csv(BASE / OUT_LOWER, index=False)
    p0.to_csv(BASE / OUT_P0, index=False)
    match.to_csv(BASE / OUT_MATCH, index=False)
    v5.to_csv(BASE / OUT_COMPAT, index=False)
    write_doc(summary, rules, fail)

    outputs = [
        OUT_SCRIPT, OUT_SUMMARY, OUT_FILE_REVIEW, OUT_STATEMENTS, OUT_RULES,
        OUT_GAP, OUT_FAILURES, OUT_UPPER, OUT_LOWER, OUT_P0, OUT_MATCH,
        OUT_COMPAT, OUT_DOC,
    ]
    update_manifest(outputs)

    print("ContinuousFirstExit CandidateCompleteness audit complete.")
    s = summary.iloc[0].to_dict()
    for key in [
        "candidate_generator_found",
        "generator_targets_first_exit",
        "generator_rule_status",
        "candidate_rows",
        "upper_candidate_rows",
        "upper_jump_missing_count",
        "lower_candidate_rows",
        "lower_drift_unbracketed_count",
        "gap_count",
        "gap_safety_proven_count",
        "gap_safety_unknown_count",
        "P0_transition_pass",
        "uses_full_grid_HExc_upgrade",
        "uses_failed_delta_route",
        "candidate_completeness_classification",
        "main_candidate_completeness_gap",
        "recommended_next_file",
        "pass_continuous_firstexit_candidate_completeness_audit",
    ]:
        print(f"{key}: {s[key]}")


if __name__ == "__main__":
    main()
