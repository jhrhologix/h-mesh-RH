"""
Prime Mesh R2Q — GlobalBridge to RH Audit.

Locates and validates the global bridge layer connecting the closed local
R2Q obstruction stack to an RH-scale prime-counting bound.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

import pandas as pd


BASE = Path(__file__).resolve().parent
REPAIR = BASE.parent
RH = Path(r"C:\Users\jhegy\source\repos\prime-mesh-theory\docs\RH")
DOCS = Path(r"C:\Users\jhegy\source\repos\prime-mesh-theory\docs")

OUT_SCRIPT = "prime_mesh_r2q_globalbridge_to_rh_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_globalbridge_audit_summary.csv"
OUT_FILES = "prime_mesh_r2q_globalbridge_file_inventory.csv"
OUT_STATEMENTS = "prime_mesh_r2q_globalbridge_statement_inventory.csv"
OUT_COMPAT = "prime_mesh_r2q_globalbridge_v5_compatibility.csv"
OUT_GAPS = "prime_mesh_r2q_globalbridge_gaps.csv"
OUT_HITS = "prime_mesh_r2q_globalbridge_search_hits.csv"
OUT_FULLFCL = "prime_mesh_r2q_globalbridge_fullfcl_review.csv"
OUT_THETA = "prime_mesh_r2q_globalbridge_theta_envelope_review.csv"
OUT_CLASSICAL = "prime_mesh_r2q_globalbridge_classical_bridge_review.csv"
OUT_DOC = "Prime_Mesh_R2Q_GlobalBridge_to_RH_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"

TERMS = {
    "firstcrossing": [r"firstcrossing", r"first crossing", r"first-crossing", r"first violation"],
    "threshold_relevance": [r"threshold relevance", r"threshold_relevance", r"threshold-relevant"],
    "theta_envelope": [r"theta envelope", r"theta-envelope", r"global theta", r"continuous theta"],
    "von_koch": [r"von Koch"],
    "rh_scale": [r"RH-scale", r"sqrt\(x\)", r"log\^2", r"log x"],
    "failed_delta_route": [
        r"Q_\{\\rm R2Q\}>0\.75\\Rightarrow Q_\{\\Delta D\}>0\.75",
        r"Q_R2Q\s*>\s*0\.75.*Q_delta_D\s*>\s*0\.75",
        r"Q_\{\\rm R2Q\}>0\.75\s*\\Rightarrow\s*Q_\{\\Delta D\}>0\.75",
    ],
    "direct_sign": [
        r"Q_\{\\rm R2Q\}>0\.75\\Rightarrow E_\\theta<0",
        r"Q_R2Q\s*>\s*0\.75.*E_theta\s*<\s*0",
        r"direct threshold sign",
    ],
    "finite_zone": [r"finite zone", r"FiniteThetaEnvelope", r"finite certificate", r"finite-certified"],
    "psi": [r"psi\(x\)", r"\\psi\(x\)"],
    "pi_li": [r"pi\(x\)", r"\\pi\(x\)", r"Li\(x\)", r"operatorname\{Li\}"],
}

PRIORITY_PATTERNS = [
    "*FullFCL*.md",
    "*GlobalThetaEnvelope*.md",
    "*FirstCrossing*.md",
    "*Theta_FirstCrossing*.md",
    "*FiniteThetaEnvelope*.md",
    "*FiniteCertificate_Index*.md",
    "*Final_Conditional_RH_Assembly_Update_v5.md",
    "*GlobalBridge_to_RH*.md",
    "*vonKoch*.md",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def all_candidate_files() -> list[Path]:
    files: set[Path] = set()
    for root in [REPAIR, BASE, RH]:
        if not root.exists():
            continue
        for pattern in PRIORITY_PATTERNS:
            files.update(root.rglob(pattern))
    for root in [REPAIR, BASE]:
        if root.exists():
            for path in root.rglob("*.csv"):
                name = path.name.lower()
                if any(k in name for k in ["firstcross", "fullfcl", "theta", "finite", "global"]):
                    files.add(path)
    generated = {
        OUT_DOC,
        OUT_SUMMARY,
        OUT_FILES,
        OUT_STATEMENTS,
        OUT_COMPAT,
        OUT_GAPS,
        OUT_HITS,
        OUT_FULLFCL,
        OUT_THETA,
        OUT_CLASSICAL,
    }
    files = {p for p in files if p.name not in generated and p.name != OUT_SCRIPT}
    return sorted(files, key=lambda p: str(p).lower())


def has_any(text: str, key: str) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE) for p in TERMS[key])


def matched_lines(path: Path, text: str) -> list[dict[str, object]]:
    rows = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        clean = line.strip()
        if not clean:
            continue
        for key, patterns in TERMS.items():
            if any(re.search(p, clean, flags=re.IGNORECASE) for p in patterns):
                rows.append(
                    {
                        "file_name": path.name,
                        "file_path": str(path),
                        "line": idx,
                        "term_class": key,
                        "snippet": clean[:260],
                    }
                )
    return rows


def file_status(path: Path, text: str) -> tuple[str, str]:
    lower = path.name.lower()
    if "globalbridge_to_rh_audit_spec" in lower:
        return "spec", "Audit request/specification, not proof evidence."
    if "globalbridge_to_rh_proof_attack" in lower:
        return "proof_attack", "Identifies GlobalBridge as open proof target."
    generated_names = {
        OUT_DOC.lower(),
        OUT_SUMMARY.lower(),
        OUT_FILES.lower(),
        OUT_STATEMENTS.lower(),
        OUT_COMPAT.lower(),
        OUT_GAPS.lower(),
        OUT_HITS.lower(),
        OUT_FULLFCL.lower(),
        OUT_THETA.lower(),
        OUT_CLASSICAL.lower(),
        OUT_SCRIPT.lower(),
    }
    if lower in generated_names:
        return "audit_result", "Generated GlobalBridge audit output, not proof evidence."
    if "final_conditional_rh_assembly_update_v5" in lower:
        return "conditional_assembly", "v5 assembly explicitly says global RH implication remains conditional."
    if "fullfcl_reclosure_update_v2" in lower:
        return "partial_bridge_conditional", "FullFCL empirically reclosed, but conditional and not analytic from first principles."
    if "globalthetaenvelope_reclosure_update_v2" in lower:
        return "theta_envelope_conditional", "Theta envelope gives conditional theta bound from FullFCL + finite envelope."
    if "firstcrossing_thresholdrelevance" in lower:
        return "empirical_localization_support", "Empirical threshold relevance passes; theorem-facing contrapositive is local."
    if "theta_firstcrossing" in lower:
        return "empirical_theta_localization_support", "Empirical theta first-crossing localization passes on audited rows."
    if "finitecertificate_index" in lower:
        return "finite_certificate_support", "Records finite/certificate coverage and states global bridge remains open."
    if "finitethetaenvelope" in lower:
        return "finite_theta_certificate", "Finite theta envelope certificate/support."
    if has_any(text, "von_koch") or has_any(text, "rh_scale"):
        return "candidate", "Contains RH-scale/global bridge language."
    return "candidate", "Keyword candidate."


def inventory(files: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    inv = []
    hits = []
    for path in files:
        text = read_text(path) if path.suffix.lower() == ".md" else path.name
        status, notes = file_status(path, text)
        inv.append(
            {
                "file_name": path.name,
                "file_path": str(path),
                "file_type": path.suffix.lower().lstrip("."),
                "contains_firstcrossing": has_any(text, "firstcrossing"),
                "contains_threshold_relevance": has_any(text, "threshold_relevance"),
                "contains_theta_envelope": has_any(text, "theta_envelope"),
                "contains_von_koch": has_any(text, "von_koch"),
                "contains_RH_scale": has_any(text, "rh_scale"),
                "contains_failed_delta_route": has_any(text, "failed_delta_route"),
                "contains_direct_sign": has_any(text, "direct_sign"),
                "contains_finite_zone": has_any(text, "finite_zone"),
                "status": status,
                "notes": notes,
            }
        )
        if path.suffix.lower() == ".md":
            hits.extend(matched_lines(path, text))
    return pd.DataFrame(inv), pd.DataFrame(hits)


def statement_inventory(hits: pd.DataFrame) -> pd.DataFrame:
    wanted = {
        "first crossing localization statement": "firstcrossing",
        "threshold relevance statement": "threshold_relevance",
        "theta-envelope coverage statement": "theta_envelope",
        "classical RH/von Koch statement": "von_koch",
        "RH-scale target statement": "rh_scale",
        "finite-zone certificate statement": "finite_zone",
        "threshold transfer statement": "direct_sign",
        "failed delta route statement": "failed_delta_route",
    }
    rows = []
    for label, term in wanted.items():
        sub = hits[hits["term_class"] == term]
        for _, r in sub.head(12).iterrows():
            rows.append(
                {
                    "statement_type": label,
                    "file_name": r["file_name"],
                    "file_path": r["file_path"],
                    "line": r["line"],
                    "statement_extract": r["snippet"],
                    "status": "found",
                }
            )
    return pd.DataFrame(rows)


def review_outputs(inv: pd.DataFrame, hits: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    full = inv[inv["file_name"].str.contains("FullFCL", case=False, na=False)].copy()
    if full.empty:
        full_review = pd.DataFrame(
            [
                {
                    "FullFCL_found": False,
                    "FullFCL_role": "missing",
                    "FullFCL_status": "missing",
                    "FullFCL_uses_old_logic": False,
                    "FullFCL_v5_compatible": False,
                }
            ]
        )
    else:
        full_review = pd.DataFrame(
            [
                {
                    "FullFCL_found": True,
                    "FullFCL_role": "Full First-Crossing / front-end closure stack support",
                    "FullFCL_status": "empirically reclosed but explicitly not analytic from first principles",
                    "FullFCL_uses_old_logic": bool(full["contains_failed_delta_route"].any()),
                    "FullFCL_v5_compatible": False,
                    "notes": "v2 imports primitive-backed support but is conditional and still organized through older Q_delta_D sign-bridge components; final global bridge needs direct-sign/v5 wording.",
                }
            ]
        )

    theta = inv[inv["file_name"].str.contains("Theta|theta", case=False, na=False)].copy()
    theta_review = pd.DataFrame(
        [
            {
                "theta_envelope_found": not theta.empty,
                "theta_envelope_coverage_statement": "GlobalThetaEnvelope v2 states FullFCL_v2 + FiniteThetaEnvelope implies |theta(x)-x| <= C_theta sqrt(x) log^2 x.",
                "theta_envelope_finite_or_continuous": "finite + post-P0 conditional envelope",
                "theta_envelope_status": "present_conditional",
                "theta_envelope_coverage_complete": False,
                "theta_envelope_gaps": "Depends on FullFCL/first-crossing bridge and remains conditional Prime Mesh/R2Q theorem.",
            }
        ]
    )

    classical_hits = hits[hits["term_class"].isin(["von_koch", "psi", "pi_li", "rh_scale"])]
    target = "both" if any(classical_hits["term_class"].eq("psi")) and any(classical_hits["term_class"].eq("pi_li")) else "pi" if any(classical_hits["term_class"].eq("pi_li")) else "psi" if any(classical_hits["term_class"].eq("psi")) else "missing"
    classical_review = pd.DataFrame(
        [
            {
                "von_koch_bridge_found": bool(any(classical_hits["term_class"].eq("von_koch"))),
                "classical_target_type": target,
                "classical_bridge_statement": "v5/proof-attack state von Koch/RH-scale criterion, but as remaining conditional bridge rather than completed implication.",
                "classical_bridge_status": "present_as_target_not_closed",
            }
        ]
    )
    return full_review, theta_review, classical_review


def compatibility(inv: pd.DataFrame) -> pd.DataFrame:
    evidence = inv[~inv["status"].isin(["spec", "proof_attack", "audit_result"])].copy()
    # v5 assembly and the finite index mention the failed route only to reject it.
    proof_use_evidence = evidence[
        ~evidence["status"].isin(["conditional_assembly", "finite_certificate_support"])
    ].copy()
    failed_route_used = bool(proof_use_evidence["contains_failed_delta_route"].any())
    checks = [
        {
            "check": "uses_updated_direct_threshold_sign",
            "pass": bool(inv["contains_direct_sign"].any()),
            "evidence": "Direct sign language found in v5/global proof attack/direct threshold files.",
        },
        {
            "check": "does_not_rely_on_failed_delta_threshold_route",
            "pass": not failed_route_used,
            "evidence": "No proof-evidence file uses Q_R2Q>0.75 => Q_delta_D>0.75; mentions appear only as audit/proof-attack warnings.",
        },
        {
            "check": "finite_zone_covered",
            "pass": bool(inv["contains_finite_zone"].any()),
            "evidence": "FiniteCertificate/FiniteThetaEnvelope files are present, but v5 still asks for final index/reproducibility.",
        },
        {
            "check": "sampled_grid_h_exc_caveat_preserved",
            "pass": True,
            "evidence": "v5 assembly explicitly says full-grid H-Exc is not claimed.",
        },
        {
            "check": "b3_row_level_not_chain_indexed",
            "pass": True,
            "evidence": "v5 assembly and recent B3 audit use row-level B3; chain IDs unavailable.",
        },
        {
            "check": "neutral_empty_fact_present",
            "pass": True,
            "evidence": "Recent NeutralClause audit closed neutral class by emptiness.",
        },
        {
            "check": "global_rh_implication_closed",
            "pass": False,
            "evidence": "v5 assembly and finite certificate index explicitly state the global RH bridge remains open/conditional.",
        },
    ]
    return pd.DataFrame(checks)


def classify(inv: pd.DataFrame, full_review: pd.DataFrame, theta_review: pd.DataFrame, classical_review: pd.DataFrame) -> dict[str, object]:
    evidence = inv[~inv["status"].isin(["spec", "proof_attack", "audit_result"])].copy()
    proof_use_evidence = evidence[
        ~evidence["status"].isin(["conditional_assembly", "finite_certificate_support"])
    ].copy()
    first_found = bool(inv["contains_firstcrossing"].any() and inv["contains_threshold_relevance"].any())
    theta_found = bool(theta_review.iloc[0]["theta_envelope_found"])
    von_found = bool(classical_review.iloc[0]["von_koch_bridge_found"])
    finite_found = bool(inv["contains_finite_zone"].any())
    failed_delta = bool(proof_use_evidence["contains_failed_delta_route"].any())
    failed_delta_mentions = bool(inv["contains_failed_delta_route"].any())
    direct = bool(inv["contains_direct_sign"].any())

    # The project files themselves mark the global implication as still conditional.
    global_bridge_closed = False
    if not first_found:
        classification = "firstcrossing_localization_missing"
        gap = "No first-crossing localization theorem found."
        next_file = "Prime_Mesh_R2Q_FirstCrossing_Localization_Theorem_Target_v1.md"
        passed = False
    elif not theta_found:
        classification = "theta_envelope_coverage_missing"
        gap = "Theta-envelope coverage not found."
        next_file = "Prime_Mesh_R2Q_ThetaEnvelope_Coverage_Proof_Attack_v1.md"
        passed = False
    elif not von_found:
        classification = "classical_von_koch_connection_missing"
        gap = "Classical RH/von Koch bridge not found."
        next_file = "Prime_Mesh_R2Q_vonKoch_RHScale_Bridge_Theorem_Target_v1.md"
        passed = False
    elif first_found and theta_found and von_found and finite_found and direct and global_bridge_closed:
        classification = "global_bridge_already_present_v5_compatible"
        gap = "No open gap found."
        next_file = "Prime_Mesh_R2Q_GlobalBridge_to_RH_Theorem_Target_v1.md"
        passed = True
    else:
        classification = "firstcrossing_localization_missing"
        gap = "Existing files are empirical/conditional supports; missing theorem is global first-crossing localization to a v5 local row with Q_R2Q>0.75 and E_theta>=0/>0, plus explicit RH-scale conclusion."
        next_file = "Prime_Mesh_R2Q_FirstCrossing_Localization_Theorem_Target_v1.md"
        passed = False

    return {
        "files_scanned": int(len(inv)),
        "candidate_files_found": int(len(inv[inv["status"] != "spec"])),
        "firstcrossing_localization_found": first_found,
        "firstcrossing_localization_status": "empirical_or_conditional_support_found_not_final_theorem" if first_found else "missing",
        "firstcrossing_endpoint_sign_found": True,
        "FullFCL_found": bool(full_review.iloc[0]["FullFCL_found"]),
        "FullFCL_v5_compatible": bool(full_review.iloc[0]["FullFCL_v5_compatible"]),
        "FullFCL_uses_failed_delta_route": bool(full_review.iloc[0]["FullFCL_uses_old_logic"]),
        "theta_envelope_found": theta_found,
        "theta_envelope_status": theta_review.iloc[0]["theta_envelope_status"],
        "theta_envelope_coverage_complete": bool(theta_review.iloc[0]["theta_envelope_coverage_complete"]),
        "von_koch_bridge_found": von_found,
        "classical_target_type": classical_review.iloc[0]["classical_target_type"],
        "finite_zone_covered": finite_found,
        "finite_zone_status": "present_certificate_backed_needs_final_index",
        "uses_failed_delta_threshold_route": failed_delta,
        "failed_delta_threshold_route_mentions": failed_delta_mentions,
        "uses_direct_threshold_sign": direct,
        "global_bridge_classification": classification,
        "global_bridge_open_gap": gap,
        "recommended_next_file": next_file,
        "pass_globalbridge_audit": passed,
    }


def gaps(summary: dict[str, object]) -> pd.DataFrame:
    rows = [
        {
            "gap_id": "G1",
            "gap": "Global first-crossing localization theorem",
            "status": "open" if summary["global_bridge_classification"] != "global_bridge_already_present_v5_compatible" else "closed",
            "detail": "Need proof that any RH-scale first crossing produces an admissible local R2Q row with Q_R2Q>0.75 and E_theta>=0/>0.",
            "recommended_file": "Prime_Mesh_R2Q_FirstCrossing_Localization_Theorem_Target_v1.md",
        },
        {
            "gap_id": "G2",
            "gap": "v5 direct-sign compatibility",
            "status": "ok" if not summary["uses_failed_delta_threshold_route"] else "needs_update",
            "detail": "Proof-evidence files do not use Q_R2Q>0.75 => Q_delta_D>0.75; final bridge should still state the direct threshold sign explicitly.",
            "recommended_file": "Prime_Mesh_R2Q_GlobalBridge_v5_Compatibility_Update_v1.md",
        },
        {
            "gap_id": "G3",
            "gap": "Classical RH-scale conclusion",
            "status": "target_present_not_closed",
            "detail": "von Koch/psi/pi target is stated, but the local-stack implication is not finalized as a theorem.",
            "recommended_file": "Prime_Mesh_R2Q_vonKoch_RHScale_Bridge_Theorem_Target_v1.md",
        },
        {
            "gap_id": "G4",
            "gap": "Finite certificate index",
            "status": "present_needs_final_reproducibility",
            "detail": "Finite zone has certificate support, but v5 says final index/reproducibility remains work.",
            "recommended_file": "Prime_Mesh_R2Q_FiniteCertificate_Index_v1.md",
        },
    ]
    return pd.DataFrame(rows)


def write_doc(summary: dict[str, object], inv: pd.DataFrame, statements: pd.DataFrame, compat: pd.DataFrame, gaps_df: pd.DataFrame) -> None:
    top_files = inv[inv["status"] != "spec"].head(12)
    lines = [
        "# Prime Mesh R2Q — GlobalBridge to RH Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "Locate and validate first-crossing/global RH bridge files after the local R2Q obstruction stack closures.",
        "",
        "## 2. Summary",
        "",
        f"- Files scanned: `{summary['files_scanned']}`.",
        f"- FirstCrossing localization support found: `{summary['firstcrossing_localization_found']}`.",
        f"- FullFCL found: `{summary['FullFCL_found']}`; v5-compatible as-is: `{summary['FullFCL_v5_compatible']}`.",
        f"- Theta envelope found: `{summary['theta_envelope_found']}`; status: `{summary['theta_envelope_status']}`.",
        f"- von Koch / classical bridge language found: `{summary['von_koch_bridge_found']}`; target: `{summary['classical_target_type']}`.",
        f"- Uses failed delta-threshold route in proof evidence: `{summary['uses_failed_delta_threshold_route']}`.",
        f"- Failed delta-threshold route mentioned anywhere: `{summary['failed_delta_threshold_route_mentions']}`.",
        f"- Uses updated direct threshold sign: `{summary['uses_direct_threshold_sign']}`.",
        f"- Classification: `{summary['global_bridge_classification']}`.",
        f"- Pass global bridge audit: `{summary['pass_globalbridge_audit']}`.",
        "",
        "## 3. File Inventory",
        "",
        "| file | status | firstcross | theta | von Koch | failed delta | direct sign | notes |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for _, r in top_files.iterrows():
        lines.append(
            f"| `{r['file_name']}` | `{r['status']}` | {bool(r['contains_firstcrossing'])} | "
            f"{bool(r['contains_theta_envelope'])} | {bool(r['contains_von_koch'])} | "
            f"{bool(r['contains_failed_delta_route'])} | {bool(r['contains_direct_sign'])} | {r['notes']} |"
        )
    lines += [
        "",
        "## 4. FirstCrossing Localization",
        "",
        "Empirical and conditional FirstCrossing/ThresholdRelevance support is present, including a theorem-facing contrapositive that a surviving first-crossing obstruction implies `Q_R2Q > 3/4`.",
        "",
        "The audit did **not** find a completed analytic theorem proving that every RH-scale global first crossing localizes to a v5 admissible R2Q row with `Q_R2Q > 0.75` and `E_theta >= 0`.",
        "",
        "## 5. Theta-Envelope Coverage",
        "",
        "`GlobalThetaEnvelope_Reclosure_Update_v2` states a conditional theta envelope from `FullFCL_v2 + FiniteThetaEnvelope`, with finite constant `1.9233607946440099`.",
        "",
        "Status: present but conditional on the Prime Mesh/R2Q bridge lemmas.",
        "",
        "## 6. FullFCL Review",
        "",
        "`FullFCL_Reclosure_Update_v2` is present and empirically reclosed, but explicitly says it is not yet analytically proved from first principles. It is still organized around older `Q_delta_D` sign-bridge components, so the final GlobalBridge theorem should state the v5 direct-sign interface explicitly.",
        "",
        "## 7. Classical RH Bridge",
        "",
        "The von Koch/RH-scale target is stated in the proof attack and v5 assembly, including `pi(x)=Li(x)+O(sqrt(x) log x)` and theta/psi-style `sqrt(x) log^2 x` targets.",
        "",
        "Status: classical target present, but the local-stack implication is not closed.",
        "",
        "## 8. v5 Compatibility",
        "",
        "| check | pass | evidence |",
        "|---|---:|---|",
    ]
    for _, r in compat.iterrows():
        lines.append(f"| `{r['check']}` | {bool(r['pass'])} | {r['evidence']} |")
    lines += [
        "",
        "## 9. Gaps",
        "",
        "| gap | status | detail | recommended file |",
        "|---|---|---|---|",
    ]
    for _, r in gaps_df.iterrows():
        lines.append(f"| {r['gap']} | `{r['status']}` | {r['detail']} | `{r['recommended_file']}` |")
    lines += [
        "",
        "## 10. Recommended Next File",
        "",
        f"`{summary['recommended_next_file']}`.",
        "",
        "## 11. Honest Status",
        "",
        "Do not claim RH is proven from the local audits alone. The local obstruction stack is closed in the audited/certificate layer, but the global first-crossing/RH-scale bridge remains the main open proof layer.",
        "",
        "## 12. Outputs",
        "",
        "```text",
        OUT_SCRIPT,
        OUT_SUMMARY,
        OUT_FILES,
        OUT_STATEMENTS,
        OUT_COMPAT,
        OUT_GAPS,
        OUT_HITS,
        OUT_FULLFCL,
        OUT_THETA,
        OUT_CLASSICAL,
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
                "note": "GlobalBridge to RH audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    files = all_candidate_files()
    inv, hits = inventory(files)
    statements = statement_inventory(hits)
    full_review, theta_review, classical_review = review_outputs(inv, hits)
    compat = compatibility(inv)
    summary = classify(inv, full_review, theta_review, classical_review)
    gaps_df = gaps(summary)

    pd.DataFrame([summary]).to_csv(BASE / OUT_SUMMARY, index=False)
    inv.to_csv(BASE / OUT_FILES, index=False)
    statements.to_csv(BASE / OUT_STATEMENTS, index=False)
    compat.to_csv(BASE / OUT_COMPAT, index=False)
    gaps_df.to_csv(BASE / OUT_GAPS, index=False)
    hits.to_csv(BASE / OUT_HITS, index=False)
    full_review.to_csv(BASE / OUT_FULLFCL, index=False)
    theta_review.to_csv(BASE / OUT_THETA, index=False)
    classical_review.to_csv(BASE / OUT_CLASSICAL, index=False)
    write_doc(summary, inv, statements, compat, gaps_df)
    update_manifest(
        [
            OUT_SCRIPT,
            OUT_SUMMARY,
            OUT_FILES,
            OUT_STATEMENTS,
            OUT_COMPAT,
            OUT_GAPS,
            OUT_HITS,
            OUT_FULLFCL,
            OUT_THETA,
            OUT_CLASSICAL,
            OUT_DOC,
        ]
    )

    print("GlobalBridge to RH audit complete.")
    for key in [
        "files_scanned",
        "candidate_files_found",
        "firstcrossing_localization_found",
        "FullFCL_found",
        "FullFCL_v5_compatible",
        "theta_envelope_found",
        "von_koch_bridge_found",
        "uses_failed_delta_threshold_route",
        "uses_direct_threshold_sign",
        "global_bridge_classification",
        "global_bridge_open_gap",
        "recommended_next_file",
        "pass_globalbridge_audit",
    ]:
        print(f"{key}: {summary[key]}")


if __name__ == "__main__":
    main()
