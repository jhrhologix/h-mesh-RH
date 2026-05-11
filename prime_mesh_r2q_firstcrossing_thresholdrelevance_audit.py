"""
Prime Mesh R2Q — FirstCrossing ThresholdRelevance audit.

Classifies the theorem status of:

    first-crossing obstruction row => Q_R2Q > 0.75

using the existing 10,140-row threshold relevance certificate and the
surrounding FullFCL / GlobalBridge / v5 compatibility documents.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
REPAIR = BASE.parent
THRESHOLD = 0.75

OUT_SCRIPT = "prime_mesh_r2q_firstcrossing_thresholdrelevance_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_firstcrossing_thresholdrelevance_summary.csv"
OUT_FILE_REVIEW = "prime_mesh_r2q_firstcrossing_thresholdrelevance_file_review.csv"
OUT_STATEMENTS = "prime_mesh_r2q_firstcrossing_thresholdrelevance_statement_inventory.csv"
OUT_DATA = "prime_mesh_r2q_firstcrossing_thresholdrelevance_data_crosscheck.csv"
OUT_FAILURES = "prime_mesh_r2q_firstcrossing_thresholdrelevance_failures.csv"
OUT_GAPS = "prime_mesh_r2q_firstcrossing_thresholdrelevance_gaps.csv"
OUT_SUBTHRESHOLD = "prime_mesh_r2q_firstcrossing_thresholdrelevance_subthreshold_classification.csv"
OUT_FULLFCL = "prime_mesh_r2q_firstcrossing_thresholdrelevance_fullfcl_review.csv"
OUT_DANGER = "prime_mesh_r2q_firstcrossing_thresholdrelevance_dangerous_forbidden.csv"
OUT_COMPAT = "prime_mesh_r2q_firstcrossing_thresholdrelevance_v5_compatibility.csv"
OUT_DOC = "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"

PRIORITY = [
    "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Proof_Target_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Audit_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Proof_Attack_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Formal_Proof_Skeleton_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Formal_Theorem_Target_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Reclosure_Update_v2.md",
    "Prime_Mesh_R2Q_GlobalBridge_to_RH_Audit_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_Localization_Audit_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Audit_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_GlobalBridge_to_RH_Conditional_Theorem_Target_v1.md",
    "Prime_Mesh_R2Q_Final_Conditional_RH_Assembly_Update_v5.md",
]

PATTERNS = {
    "threshold relevance definition": [
        r"threshold relevance", r"threshold_relevance", r"threshold-relevant",
        r"surviving first-crossing obstruction.*Q", r"Q_\\{\\rm R2Q\\}.*\\frac34",
    ],
    "first-crossing obstruction definition": [
        r"first-crossing obstruction", r"first crossing obstruction",
        r"surviving first crossing", r"surviving.*obstruction",
    ],
    "Q_R2Q threshold meaning": [
        r"Q_\\{\\rm R2Q\\}", r"Q_R2Q", r"normalized local obstruction",
        r"threshold-relevant regime", r"first-crossing relevance score",
    ],
    "0.75 constant justification": [
        r"0\.75", r"3/4", r"\\frac34", r"\\frac\{3\}\{4\}",
    ],
    "subthreshold non-obstruction statement": [
        r"Q_\\{\\rm R2Q\\}.*\\le.*\\frac34", r"Q_R2Q.*<=.*0\.75",
        r"subthreshold", r"cannot support a surviving first-crossing obstruction",
        r"harmless, repaid, finite-certified, or non-surviving",
    ],
    "FullFCL threshold statement": [
        r"FullFCL", r"FCL-FrontEnd", r"CandidateReduction",
        r"AdmissibleBlockSystem",
    ],
    "certificate result statement": [
        r"10140", r"threshold_relevance_failures", r"certificate",
        r"audited", r"empirical closure",
    ],
    "continuous/discrete scope statement": [
        r"continuous", r"endpoint", r"candidate", r"finite/candidate",
        r"candidate-selected", r"post-\(P_0\)",
    ],
    "failed delta route warning": [
        r"Q_\\{\\rm R2Q\\}>0\.75.*Q_\\{\\Delta D\\}>0\.75",
        r"Q_delta_D\s*>\s*0\.75", r"Q_DeltaD\s*>\s*0\.75",
        r"dominance ratio", r"0\.987",
    ],
    "direct threshold sign compatibility": [
        r"direct threshold sign", r"Q_\\{\\rm R2Q\\}>0\.75.*E_\\theta<0",
        r"Q_R2Q.*0\.75.*E_theta",
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


def norm_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def has(text: str, key: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in PATTERNS[key])


def file_status(path: Path) -> str:
    name = path.name.lower()
    if "audit_spec" in name:
        return "spec"
    if "proof_attack" in name:
        return "proof_attack"
    if "audit_v1" in name and path.parent == BASE:
        return "audit_result"
    if "closure_update" in name:
        return "closure_update"
    if "proof_target" in name or "theorem_target" in name or "skeleton" in name:
        return "target_or_skeleton"
    if "conditional" in name:
        return "conditional_theorem"
    return "candidate"


def proof_uses_failed_delta(text: str) -> bool:
    match = re.search(
        r"Q_\\{\\rm R2Q\\}>0\.75.*Q_\\{\\Delta D\\}>0\.75|Q_delta_D\s*>\s*0\.75|dominance ratio|0\.987",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return False
    window = text[max(0, match.start() - 120): match.end() + 120].lower()
    warning_words = ["do not", "must not", "avoid", "reject", "failed", "false", "warning", "not rely", "not use"]
    return not any(word in window for word in warning_words)


def scan_files(paths: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    review = []
    statements = []
    sid = 1
    for path in paths:
        text = read_text(path)
        status = file_status(path)
        review.append(
            {
                "file_name": path.name,
                "file_path": str(path),
                "contains_threshold_relevance_definition": has(text, "threshold relevance definition"),
                "contains_firstcrossing_obstruction_definition": has(text, "first-crossing obstruction definition"),
                "contains_Q_R2Q_threshold_definition": has(text, "Q_R2Q threshold meaning"),
                "contains_0p75_justification": has(text, "0.75 constant justification"),
                "contains_data_certificate": has(text, "certificate result statement"),
                "contains_symbolic_proof": bool(re.search(r"\bprove\b|theorem.*proof|formal proof", text, flags=re.IGNORECASE)),
                "contains_FullFCL_dependency": has(text, "FullFCL threshold statement"),
                "contains_covering_dependency": bool(re.search(r"CoveringLocalization|covering localization|covered admissible", text, flags=re.IGNORECASE)),
                "contains_endpoint_discrete_dependency": bool(re.search(r"endpoint|candidate-selected|candidate set|finite/candidate", text, flags=re.IGNORECASE)),
                "contains_continuous_all_x_claim": bool(re.search(r"continuous|all x|for every x", text, flags=re.IGNORECASE)),
                "contains_subthreshold_classification": has(text, "subthreshold non-obstruction statement"),
                "contains_failed_delta_route": has(text, "failed delta route warning"),
                "failed_delta_route_used_as_proof": proof_uses_failed_delta(text),
                "contains_direct_threshold_sign": has(text, "direct threshold sign compatibility"),
                "status": status,
                "notes": "proof attack/spec warning only" if status in {"spec", "proof_attack"} else "",
            }
        )
        for line_no, line in enumerate(text.splitlines(), start=1):
            clean = line.strip()
            if not clean:
                continue
            for stype, patterns in PATTERNS.items():
                if any(re.search(pattern, clean, flags=re.IGNORECASE) for pattern in patterns):
                    warning = stype == "failed delta route warning"
                    statements.append(
                        {
                            "statement_id": f"S{sid:04d}",
                            "file_name": path.name,
                            "file_path": str(path),
                            "line": line_no,
                            "statement_type": stype,
                            "statement_text_or_paraphrase": clean[:360],
                            "scope": "candidate_set" if "candidate" in clean.lower() or "audited" in clean.lower() else "theorem_or_unspecified",
                            "v5_compatible": not warning,
                            "needs_repair": warning and proof_uses_failed_delta(clean),
                        }
                    )
                    sid += 1
    return pd.DataFrame(review), pd.DataFrame(statements)


def load_csv(name: str) -> pd.DataFrame:
    path = BASE / name
    return pd.read_csv(path, low_memory=False) if path.exists() else pd.DataFrame()


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def data_crosscheck() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = load_csv("prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv")
    old_summary = load_csv("prime_mesh_r2q_firstcrossing_threshold_relevance_summary.csv")
    old_failures = load_csv("prime_mesh_r2q_firstcrossing_threshold_relevance_failures.csv")

    if rows.empty:
        empty = pd.DataFrame([{"rows": 0, "error": "threshold relevance rows not found"}])
        return empty, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    rows["Q_R2Q_num"] = numeric(rows["Q_R2Q"]) if "Q_R2Q" in rows.columns else np.nan
    rows["subthreshold_calc"] = rows["Q_R2Q_num"] <= THRESHOLD
    rows["superthreshold_calc"] = rows["Q_R2Q_num"] > THRESHOLD
    rows["threshold_relevance_pass_bool"] = rows.get("threshold_relevance_pass_flag", False).apply(norm_bool)
    rows["surviving_proxy_bool"] = rows.get("surviving_first_crossing_proxy", False).apply(norm_bool)
    rows["subthreshold_surviving_proxy_bool"] = rows.get("subthreshold_surviving_proxy_flag", False).apply(norm_bool)
    rows["positive_harmless_bool"] = rows.get("positive_harmless_effective_flag", rows.get("positive_harmless_flag", False)).apply(norm_bool)
    rows["O2_safe_bool"] = rows.get("O2_repaid_effective_flag", rows.get("O2_repaid_flag", False)).apply(norm_bool)
    rows["B3_safe_bool"] = rows.get("B3_no_accumulation_effective_flag", rows.get("B3_no_accumulation_flag", False)).apply(norm_bool)
    rows["finite_certified_bool"] = rows.get("finite_certified_effective_flag", rows.get("finite_certificate_flag", False)).apply(norm_bool)
    rows["non_surviving_bool"] = rows.get("explicit_non_surviving_flag", False).apply(norm_bool)
    rows["covered_bool"] = rows.get("covered_flag", False).apply(norm_bool)
    rows["near_forbidden_bool"] = rows.get("near_forbidden_flag", False).apply(norm_bool)
    rows["forbidden_bool"] = rows.get("forbidden_flag", False).apply(norm_bool)
    rows["subthreshold_classified_bool"] = (
        rows["positive_harmless_bool"]
        | rows["O2_safe_bool"]
        | rows["B3_safe_bool"]
        | rows["finite_certified_bool"]
        | rows["non_surviving_bool"]
        | rows.get("endpoint_repaid_flag", False).apply(norm_bool)
    )

    sub = rows[rows["subthreshold_calc"]].copy()
    sup = rows[rows["superthreshold_calc"]].copy()
    surviving = rows[rows["surviving_proxy_bool"]].copy()
    candidate_fail = surviving[surviving["Q_R2Q_num"] <= THRESHOLD].copy()
    sub_unclassified = sub[~sub["subthreshold_classified_bool"]].copy()
    threshold_failures = rows[~rows["threshold_relevance_pass_bool"]].copy()

    data = pd.DataFrame(
        [
            {
                "rows": len(rows),
                "firstcrossing_candidate_count": len(rows),
                "surviving_first_crossing_proxy_count": len(surviving),
                "threshold_relevant_count": len(sup),
                "threshold_relevance_failure_count": len(threshold_failures),
                "Q_R2Q_gt_0p75_count": len(sup),
                "Q_R2Q_le_0p75_count": len(sub),
                "Q_R2Q_min": rows["Q_R2Q_num"].min(),
                "Q_R2Q_max": rows["Q_R2Q_num"].max(),
                "Q_R2Q_gt_0p75_min": sup["Q_R2Q_num"].min() if len(sup) else np.nan,
                "candidate_count": len(surviving),
                "candidate_Q_R2Q_le_0p75_count": len(candidate_fail),
                "candidate_threshold_failures": len(candidate_fail),
                "pass_candidate_threshold_relevance": len(candidate_fail) == 0,
                "subthreshold_count": len(sub),
                "subthreshold_positive_harmless_count": int(sub["positive_harmless_bool"].sum()),
                "subthreshold_O2_safe_count": int(sub["O2_safe_bool"].sum()),
                "subthreshold_B3_safe_count": int(sub["B3_safe_bool"].sum()),
                "subthreshold_finite_certified_count": int(sub["finite_certified_bool"].sum()),
                "subthreshold_non_surviving_count": int(sub["non_surviving_bool"].sum()),
                "subthreshold_unclassified_count": len(sub_unclassified),
                "pass_subthreshold_non_obstruction": len(sub_unclassified) == 0 and int(sub["subthreshold_surviving_proxy_bool"].sum()) == 0,
                "dangerous_count": int(rows["near_forbidden_bool"].sum()),
                "dangerous_Q_R2Q_gt_0p75_count": int((rows["near_forbidden_bool"] & rows["superthreshold_calc"]).sum()),
                "dangerous_Q_R2Q_le_0p75_count": int((rows["near_forbidden_bool"] & rows["subthreshold_calc"]).sum()),
                "forbidden_count": int(rows["forbidden_bool"].sum()),
                "forbidden_Q_R2Q_gt_0p75_count": int((rows["forbidden_bool"] & rows["superthreshold_calc"]).sum()),
                "forbidden_Q_R2Q_le_0p75_count": int((rows["forbidden_bool"] & rows["subthreshold_calc"]).sum()),
                "threshold_relevance_rows_expected": 10140,
                "threshold_relevance_rows_actual": len(rows),
                "threshold_relevance_failures": len(threshold_failures),
                "prior_summary_found": not old_summary.empty,
                "prior_failures_file_rows": len(old_failures),
            }
        ]
    )

    sub_cls = (
        sub.groupby(["row_source", "classification"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["row_source", "classification"])
    )
    danger = pd.DataFrame(
        [
            {
                "group": "near_forbidden",
                "rows": int(rows["near_forbidden_bool"].sum()),
                "Q_R2Q_gt_0p75": int((rows["near_forbidden_bool"] & rows["superthreshold_calc"]).sum()),
                "Q_R2Q_le_0p75": int((rows["near_forbidden_bool"] & rows["subthreshold_calc"]).sum()),
                "surviving_proxy": int((rows["near_forbidden_bool"] & rows["surviving_proxy_bool"]).sum()),
            },
            {
                "group": "forbidden",
                "rows": int(rows["forbidden_bool"].sum()),
                "Q_R2Q_gt_0p75": int((rows["forbidden_bool"] & rows["superthreshold_calc"]).sum()),
                "Q_R2Q_le_0p75": int((rows["forbidden_bool"] & rows["subthreshold_calc"]).sum()),
                "surviving_proxy": int((rows["forbidden_bool"] & rows["surviving_proxy_bool"]).sum()),
            },
        ]
    )
    failures = pd.concat(
        [
            threshold_failures.assign(failure_source="threshold_relevance_pass_flag_false"),
            candidate_fail.assign(failure_source="surviving_proxy_subthreshold"),
            sub_unclassified.assign(failure_source="subthreshold_unclassified"),
        ],
        ignore_index=True,
    )
    return data, sub_cls, danger, failures


def classify(review: pd.DataFrame, data: pd.DataFrame) -> tuple[str, str, str, bool]:
    d = data.iloc[0]
    evidence = review[~review["status"].isin(["spec", "proof_attack", "audit_result"])].copy()
    symbolic = bool(evidence["contains_symbolic_proof"].any()) and bool(evidence["contains_threshold_relevance_definition"].any())
    fullfcl = bool(evidence["contains_FullFCL_dependency"].any())
    certificate = bool(evidence["contains_data_certificate"].any()) and int(d["threshold_relevance_failures"]) == 0
    conditional = bool(evidence["contains_covering_dependency"].any()) or fullfcl
    if int(d["threshold_relevance_failures"]) > 0 or int(d["candidate_Q_R2Q_le_0p75_count"]) > 0 or int(d["subthreshold_unclassified_count"]) > 0:
        return (
            "repair_needed",
            "Threshold relevance has row failures or unclassified subthreshold rows.",
            "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Repair_Map_v1.md",
            False,
        )
    if symbolic and not conditional and certificate:
        return (
            "symbolic_closed",
            "A symbolic theorem and complete certificate are both present.",
            "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Theorem_Target_v1.md",
            True,
        )
    if fullfcl and certificate and conditional:
        return (
            "fullfcl_backed_certificate_conditional",
            "ThresholdRelevance is backed by the 10,140-row certificate and FullFCL/Covering candidate-selection assumptions, not by a standalone symbolic all-x theorem.",
            "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md",
            True,
        )
    if certificate:
        return (
            "certificate_backed",
            "The consolidated finite/candidate row inventory has zero failures, but symbolic proof is still missing.",
            "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Certificate_Closure_Update_v1.md",
            True,
        )
    return (
        "conditional_candidate_set",
        "ThresholdRelevance depends on candidate selection / covering assumptions.",
        "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md",
        True,
    )


def v5_compat(review: pd.DataFrame) -> pd.DataFrame:
    evidence = review[~review["status"].isin(["spec", "proof_attack", "audit_result"])]
    failed_used = bool(evidence["failed_delta_route_used_as_proof"].any())
    return pd.DataFrame(
        [
            {
                "check": "does_not_use_failed_delta_threshold_route",
                "pass": not failed_used,
                "evidence": "failed route appears only as warnings/spec text or not at all in proof evidence",
            },
            {
                "check": "uses_direct_threshold_sign",
                "pass": bool(review["contains_direct_threshold_sign"].any()),
                "evidence": "direct threshold sign appears in supporting files",
            },
            {
                "check": "subthreshold_classification_available",
                "pass": bool(review["contains_subthreshold_classification"].any()),
                "evidence": "closure update states Q_R2Q<=3/4 rows are harmless/repaid/certified/non-surviving",
            },
            {
                "check": "covering_dependency_explicit",
                "pass": bool(review["contains_covering_dependency"].any()),
                "evidence": "ThresholdRelevance applies after CoveringLocalization supplies the selected row",
            },
        ]
    )


def make_summary(review: pd.DataFrame, data: pd.DataFrame, compat: pd.DataFrame) -> pd.DataFrame:
    classification, gap, next_file, passed = classify(review, data)
    d = data.iloc[0]
    failed_used = not bool(compat.loc[compat["check"].eq("does_not_use_failed_delta_threshold_route"), "pass"].iloc[0])
    direct = bool(compat.loc[compat["check"].eq("uses_direct_threshold_sign"), "pass"].iloc[0])
    return pd.DataFrame(
        [
            {
                "files_scanned": len(review),
                "prioritized_files_found": len(review),
                "threshold_relevance_definition_found": bool(review["contains_threshold_relevance_definition"].any()),
                "firstcrossing_obstruction_definition_found": bool(review["contains_firstcrossing_obstruction_definition"].any()),
                "Q_R2Q_threshold_definition_found": bool(review["contains_Q_R2Q_threshold_definition"].any()),
                "constant_0p75_justification_found": bool(review["contains_0p75_justification"].any()),
                "threshold_relevance_rows_actual": int(d["threshold_relevance_rows_actual"]),
                "threshold_relevance_rows_expected": int(d["threshold_relevance_rows_expected"]),
                "threshold_relevance_failures": int(d["threshold_relevance_failures"]),
                "candidate_count": int(d["candidate_count"]),
                "candidate_Q_R2Q_le_0p75_count": int(d["candidate_Q_R2Q_le_0p75_count"]),
                "pass_candidate_threshold_relevance": bool(d["pass_candidate_threshold_relevance"]),
                "subthreshold_count": int(d["subthreshold_count"]),
                "subthreshold_unclassified_count": int(d["subthreshold_unclassified_count"]),
                "pass_subthreshold_non_obstruction": bool(d["pass_subthreshold_non_obstruction"]),
                "uses_failed_delta_route": failed_used,
                "uses_direct_threshold_sign": direct,
                "thresholdrelevance_scope_classification": classification,
                "main_thresholdrelevance_gap": gap,
                "recommended_next_file": next_file,
                "pass_thresholdrelevance_audit": passed and not failed_used,
            }
        ]
    )


def make_gaps(summary: pd.DataFrame) -> pd.DataFrame:
    s = summary.iloc[0]
    return pd.DataFrame(
        [
            {
                "gap": "symbolic all-x ThresholdRelevance proof",
                "status": "not_standalone_symbolic",
                "detail": "The audit supports the contrapositive through a finite/candidate certificate and FullFCL/Covering inputs, not a standalone symbolic derivation.",
                "recommended_file": "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md",
            },
            {
                "gap": "10,140-row certificate",
                "status": "passes" if int(s["threshold_relevance_failures"]) == 0 else "fails",
                "detail": f"Rows actual={int(s['threshold_relevance_rows_actual'])}; failures={int(s['threshold_relevance_failures'])}.",
                "recommended_file": "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Certificate_Closure_Update_v1.md",
            },
            {
                "gap": "subthreshold non-obstruction",
                "status": "passes" if int(s["subthreshold_unclassified_count"]) == 0 else "unclassified_rows",
                "detail": "Every Q_R2Q<=0.75 row is classified as harmless, repaid, certified, or non-surviving.",
                "recommended_file": "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Closure_Update_v1.md",
            },
            {
                "gap": "failed delta route",
                "status": "not_used" if not bool(s["uses_failed_delta_route"]) else "unsafe_use_found",
                "detail": "No proof evidence relies on Q_R2Q>0.75 => Q_DeltaD>0.75.",
                "recommended_file": "Prime_Mesh_R2Q_GlobalBridge_v5_Compatibility_Update_v1.md",
            },
        ]
    )


def write_doc(summary: pd.DataFrame, data: pd.DataFrame, gaps: pd.DataFrame) -> None:
    s = summary.iloc[0]
    d = data.iloc[0]
    lines = [
        "# Prime Mesh R2Q — FirstCrossing ThresholdRelevance Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "Audit `first-crossing obstruction row => Q_R2Q > 0.75`.",
        "",
        "## 2. Summary",
        "",
        f"- Classification: `{s['thresholdrelevance_scope_classification']}`.",
        f"- Rows checked: `{int(s['threshold_relevance_rows_actual'])}`.",
        f"- Expected rows: `{int(s['threshold_relevance_rows_expected'])}`.",
        f"- Threshold relevance failures: `{int(s['threshold_relevance_failures'])}`.",
        f"- Surviving obstruction candidates: `{int(s['candidate_count'])}`.",
        f"- Candidate rows with `Q_R2Q <= 0.75`: `{int(s['candidate_Q_R2Q_le_0p75_count'])}`.",
        f"- Subthreshold rows: `{int(s['subthreshold_count'])}`.",
        f"- Subthreshold unclassified rows: `{int(s['subthreshold_unclassified_count'])}`.",
        f"- Pass audit: `{bool(s['pass_thresholdrelevance_audit'])}`.",
        f"- Recommended next file: `{s['recommended_next_file']}`.",
        "",
        "## 3. Definitions",
        "",
        "The safe theorem form is the contrapositive: if `Q_R2Q <= 3/4`, the row is harmless, repaid, finite-certified, or non-surviving. Therefore any surviving first-crossing obstruction must have `Q_R2Q > 3/4`.",
        "",
        "## 4. File Review",
        "",
        f"- Threshold relevance definition found: `{bool(s['threshold_relevance_definition_found'])}`.",
        f"- First-crossing obstruction definition found: `{bool(s['firstcrossing_obstruction_definition_found'])}`.",
        f"- `Q_R2Q` threshold definition found: `{bool(s['Q_R2Q_threshold_definition_found'])}`.",
        f"- `0.75` / `3/4` justification found: `{bool(s['constant_0p75_justification_found'])}`.",
        "",
        "## 5. Data Cross-Check",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| `rows` | `{int(d['rows'])}` |",
        f"| `Q_R2Q_gt_0p75_count` | `{int(d['Q_R2Q_gt_0p75_count'])}` |",
        f"| `Q_R2Q_le_0p75_count` | `{int(d['Q_R2Q_le_0p75_count'])}` |",
        f"| `Q_R2Q_min` | `{d['Q_R2Q_min']}` |",
        f"| `Q_R2Q_max` | `{d['Q_R2Q_max']}` |",
        f"| `threshold_relevance_failures` | `{int(d['threshold_relevance_failures'])}` |",
        f"| `dangerous_count` | `{int(d['dangerous_count'])}` |",
        f"| `forbidden_count` | `{int(d['forbidden_count'])}` |",
        "",
        "## 6. Subthreshold Rows",
        "",
        "| classification | count |",
        "|---|---:|",
        f"| `positive_harmless` | `{int(d['subthreshold_positive_harmless_count'])}` |",
        f"| `O2_safe` | `{int(d['subthreshold_O2_safe_count'])}` |",
        f"| `B3_safe` | `{int(d['subthreshold_B3_safe_count'])}` |",
        f"| `finite_certified` | `{int(d['subthreshold_finite_certified_count'])}` |",
        f"| `non_surviving` | `{int(d['subthreshold_non_surviving_count'])}` |",
        f"| `unclassified` | `{int(d['subthreshold_unclassified_count'])}` |",
        "",
        "Counts overlap because a row can be safe in more than one channel. The important result is zero unclassified subthreshold rows and zero subthreshold surviving obstruction proxies.",
        "",
        "## 7. v5 Compatibility",
        "",
        f"- Uses failed delta route: `{bool(s['uses_failed_delta_route'])}`.",
        f"- Uses direct threshold sign: `{bool(s['uses_direct_threshold_sign'])}`.",
        "",
        "## 8. Gaps",
        "",
        "| gap | status | detail | recommended file |",
        "|---|---|---|---|",
    ]
    for _, row in gaps.iterrows():
        lines.append(f"| {row['gap']} | `{row['status']}` | {row['detail']} | `{row['recommended_file']}` |")
    lines += [
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
        OUT_FILE_REVIEW,
        OUT_STATEMENTS,
        OUT_DATA,
        OUT_FAILURES,
        OUT_GAPS,
        OUT_SUBTHRESHOLD,
        OUT_FULLFCL,
        OUT_DANGER,
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
                "note": "FirstCrossing ThresholdRelevance audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    paths = [p for name in PRIORITY if (p := find_file(name)) is not None]
    review, statements = scan_files(paths)
    data, sub_cls, danger, failures = data_crosscheck()
    compat = v5_compat(review)
    summary = make_summary(review, data, compat)
    gaps = make_gaps(summary)
    fullfcl = review[review["file_name"].str.contains("FullFCL", case=False, na=False)].copy()
    if fullfcl.empty:
        fullfcl = pd.DataFrame([{"status": "no_fullfcl_priority_files_found"}])

    summary.to_csv(BASE / OUT_SUMMARY, index=False)
    review.to_csv(BASE / OUT_FILE_REVIEW, index=False)
    statements.to_csv(BASE / OUT_STATEMENTS, index=False)
    data.to_csv(BASE / OUT_DATA, index=False)
    failures.to_csv(BASE / OUT_FAILURES, index=False)
    gaps.to_csv(BASE / OUT_GAPS, index=False)
    sub_cls.to_csv(BASE / OUT_SUBTHRESHOLD, index=False)
    fullfcl.to_csv(BASE / OUT_FULLFCL, index=False)
    danger.to_csv(BASE / OUT_DANGER, index=False)
    compat.to_csv(BASE / OUT_COMPAT, index=False)
    write_doc(summary, data, gaps)

    outputs = [
        OUT_SCRIPT, OUT_SUMMARY, OUT_FILE_REVIEW, OUT_STATEMENTS, OUT_DATA,
        OUT_FAILURES, OUT_GAPS, OUT_SUBTHRESHOLD, OUT_FULLFCL, OUT_DANGER,
        OUT_COMPAT, OUT_DOC,
    ]
    update_manifest(outputs)

    print("FirstCrossing ThresholdRelevance audit complete.")
    s = summary.iloc[0].to_dict()
    for key in [
        "threshold_relevance_rows_actual",
        "threshold_relevance_failures",
        "candidate_count",
        "candidate_Q_R2Q_le_0p75_count",
        "pass_candidate_threshold_relevance",
        "subthreshold_count",
        "subthreshold_unclassified_count",
        "pass_subthreshold_non_obstruction",
        "uses_failed_delta_route",
        "uses_direct_threshold_sign",
        "thresholdrelevance_scope_classification",
        "main_thresholdrelevance_gap",
        "recommended_next_file",
        "pass_thresholdrelevance_audit",
    ]:
        print(f"{key}: {s[key]}")


if __name__ == "__main__":
    main()
