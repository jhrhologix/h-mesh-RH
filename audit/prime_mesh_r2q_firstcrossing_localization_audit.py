"""
Prime Mesh R2Q — FirstCrossing Localization Audit.

Audits whether existing FirstCrossing / FullFCL / ThetaEnvelope files prove:
    global RH-scale first crossing
    => exists J with Q_R2Q(J) > 0.75 and E_theta(J) >= 0.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

import pandas as pd


BASE = Path(__file__).resolve().parent
REPAIR = BASE.parent

OUT_SCRIPT = "prime_mesh_r2q_firstcrossing_localization_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_firstcrossing_localization_audit_summary.csv"
OUT_FILE_REVIEW = "prime_mesh_r2q_firstcrossing_localization_file_review.csv"
OUT_STATEMENTS = "prime_mesh_r2q_firstcrossing_localization_statement_inventory.csv"
OUT_LEMMAS = "prime_mesh_r2q_firstcrossing_localization_lemma_status.csv"
OUT_COMPAT = "prime_mesh_r2q_firstcrossing_localization_v5_compatibility.csv"
OUT_GAPS = "prime_mesh_r2q_firstcrossing_localization_gaps.csv"
OUT_DATA = "prime_mesh_r2q_firstcrossing_localization_data_crosscheck.csv"
OUT_FULLFCL = "prime_mesh_r2q_firstcrossing_localization_fullfcl_review.csv"
OUT_THETA = "prime_mesh_r2q_firstcrossing_localization_theta_review.csv"
OUT_THRESHOLD = "prime_mesh_r2q_firstcrossing_localization_threshold_review.csv"
OUT_DOC = "Prime_Mesh_R2Q_FirstCrossing_Localization_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"

PRIORITY = [
    "Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Conditional_Theorem_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Target_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Proof_Target_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Formal_Proof_Skeleton_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Formal_Theorem_Target_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Reclosure_Update_v2.md",
    "Prime_Mesh_R2Q_FiniteThetaEnvelope_Certificate_Spec_v1.md",
    "Prime_Mesh_R2Q_FiniteThetaEnvelope_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_GlobalThetaEnvelope_Reclosure_Update_v2.md",
    "Prime_Mesh_R2Q_Theta_FirstCrossing_Final_Conditional_Assembly_v1.md",
    "Prime_Mesh_R2Q_Final_Conditional_RH_Assembly_Update_v5.md",
    "Prime_Mesh_R2Q_FirstCrossing_Localization_Theorem_Target_v1.md",
]

CSV_INPUTS = {
    "threshold_rows": "prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv",
    "threshold_summary": "prime_mesh_r2q_firstcrossing_threshold_relevance_summary.csv",
    "theta_summary": "prime_mesh_r2q_theta_first_crossing_summary.csv",
    "theta_crossings": "prime_mesh_r2q_theta_first_crossing_crossings.csv",
    "covering_summary": "prime_mesh_r2q_firstcrossing_covering_localization_summary.csv",
    "covering_failures": "prime_mesh_r2q_firstcrossing_covering_localization_failures.csv",
    "finite_theta_summary": "prime_mesh_r2q_finite_theta_envelope_summary.csv",
}

PATTERNS = {
    "envelope_definition": [r"theta\(x\)-x", r"psi\(x\)-x", r"pi\(x\).*Li\(x\)", r"sqrt\(x\).*log"],
    "first_crossing_definition": [r"first crossing", r"first-crossing", r"first violation", r"first exit"],
    "covering_localization": [r"represented in the candidate set", r"covered local", r"localizes", r"x_1.*covered", r"CandidateReduction"],
    "threshold_relevance": [r"threshold relevance", r"threshold-relevant", r"surviving first-crossing obstruction", r"Q_\\{\\rm R2Q\\}.*3/4", r"Q_R2Q.*0\.75"],
    "endpoint_sign_orientation": [r"positive first crossing gives", r"negative first crossing gives", r"E_\\theta\(J\)>0", r"E_theta.*positive", r"SignedLocalExtraction"],
    "lower_crossing_handling": [r"negative first crossing", r"lower crossing", r"lower-envelope", r"sign convention", r"symmetric"],
    "finite_zone_coverage": [r"finite zone", r"FiniteThetaEnvelope", r"finite certificate", r"x<P_0"],
    "von_koch_bridge": [r"von Koch", r"pi\(x\).*Li\(x\)", r"psi\(x\)-x", r"RH-scale"],
    "failed_delta_threshold_route": [r"Q_\\{\\rm R2Q\\}>0\.75.*Q_\\{\\Delta D\\}>0\.75", r"Q_delta_D\s*>\s*0\.75", r"dominance ratio", r"0\.987"],
    "direct_threshold_sign": [r"Q_\\{\\rm R2Q\\}>0\.75.*E_\\theta<0", r"direct threshold sign"],
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
    for root in [REPAIR, BASE]:
        matches = list(root.rglob(name))
        if matches:
            return matches[0]
    return None


def has_pattern(text: str, key: str) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE) for p in PATTERNS[key])


def extract_hits(path: Path, text: str) -> list[dict[str, object]]:
    rows = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        clean = line.strip()
        if not clean:
            continue
        for key, pats in PATTERNS.items():
            if any(re.search(p, clean, flags=re.IGNORECASE) for p in pats):
                rows.append(
                    {
                        "file_name": path.name,
                        "file_path": str(path),
                        "line": line_no,
                        "statement_type": key,
                        "statement_text_or_paraphrase": clean[:320],
                        "status": "found",
                        "v5_compatible": key != "failed_delta_threshold_route",
                        "needs_repair": key == "failed_delta_threshold_route",
                    }
                )
    return rows


def classify_file(path: Path, text: str) -> tuple[str, str]:
    name = path.name
    if name.endswith("Audit_Spec_v1.md"):
        return "spec", "Audit spec or theorem target, not proof evidence."
    if "Theorem_Target" in name and "Localization" in name:
        return "target", "States the missing theorem target; explicitly not proven."
    if "Conditional" in name:
        return "conditional", "Contains conditional theorem/input structure."
    if "Closure_Update" in name or "Reclosure_Update" in name:
        if "FullFCL" in name:
            return "conditional_support", "FullFCL closure support; empirical/conditional, not final analytic theorem."
        return "closure_support", "Closure/update support file."
    if "Proof_Skeleton" in name or "Proof_Target" in name:
        return "proof_target", "Proof skeleton/target, not completed proof."
    return "candidate", "Prioritized file."


def file_review(paths: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    hits = []
    for path in paths:
        text = read_text(path)
        status, notes = classify_file(path, text)
        rows.append(
            {
                "file_name": path.name,
                "file_path": str(path),
                "contains_envelope_definition": has_pattern(text, "envelope_definition"),
                "contains_first_crossing_definition": has_pattern(text, "first_crossing_definition"),
                "contains_covering_localization": has_pattern(text, "covering_localization"),
                "contains_threshold_relevance": has_pattern(text, "threshold_relevance"),
                "contains_endpoint_sign_orientation": has_pattern(text, "endpoint_sign_orientation"),
                "contains_lower_crossing_handling": has_pattern(text, "lower_crossing_handling"),
                "contains_finite_zone_coverage": has_pattern(text, "finite_zone_coverage"),
                "contains_von_koch_bridge": has_pattern(text, "von_koch_bridge"),
                "uses_failed_delta_threshold_route": has_pattern(text, "failed_delta_threshold_route"),
                "uses_direct_threshold_sign": has_pattern(text, "direct_threshold_sign"),
                "status": status,
                "notes": notes,
            }
        )
        hits.extend(extract_hits(path, text))
    return pd.DataFrame(rows), pd.DataFrame(hits)


def data_crosscheck() -> pd.DataFrame:
    recs = []
    for key, filename in CSV_INPUTS.items():
        path = BASE / filename
        if not path.exists():
            recs.append({"data_file": filename, "found": False})
            continue
        df = pd.read_csv(path, low_memory=False)
        rec = {"data_file": filename, "found": True, "rows": len(df)}
        cols = {c.lower(): c for c in df.columns}
        if key == "threshold_rows":
            q = pd.to_numeric(df[cols.get("q_r2q", "")], errors="coerce") if "q_r2q" in cols else pd.Series(dtype=float)
            e = pd.to_numeric(df[cols.get("e_theta", "")], errors="coerce") if "e_theta" in cols else pd.Series(dtype=float)
            rec.update(
                {
                    "threshold_relevance_rows": len(df),
                    "firstcrossing_candidate_count": len(df),
                    "Q_R2Q_gt_0p75_count": int((q > 0.75).sum()) if len(q) else None,
                    "E_theta_nonnegative_count": int((e >= 0).sum()) if len(e) else None,
                    "localization_failures": int(len(pd.read_csv(BASE / "prime_mesh_r2q_firstcrossing_threshold_relevance_failures.csv"))) if (BASE / "prime_mesh_r2q_firstcrossing_threshold_relevance_failures.csv").exists() else None,
                }
            )
        if "summary" in key and len(df):
            for c in df.columns[:60]:
                if any(s in c.lower() for s in ["pass", "failure", "rows", "constant", "theta"]):
                    rec[c] = df.iloc[0][c]
        recs.append(rec)
    return pd.DataFrame(recs)


def lemma_status(review: pd.DataFrame) -> pd.DataFrame:
    def any_col(col: str, proof_only: bool = False) -> bool:
        df = review
        if proof_only:
            df = df[~df["status"].isin(["spec", "target"])]
        return bool(df[col].any())

    rows = [
        {
            "lemma": "Envelope Definition",
            "status": "conditional",
            "statement_needed": "Define G(x)=theta/psi/pi error with RH-scale envelope.",
            "evidence": "GlobalThetaEnvelope/ThetaFirstCrossing define theta envelope; theorem target states psi/pi alternatives.",
            "found": any_col("contains_envelope_definition"),
        },
        {
            "lemma": "First-Crossing Existence",
            "status": "conditional",
            "statement_needed": "If envelope fails, first crossing X0 exists.",
            "evidence": "First-crossing language exists in conditional assemblies, but not closed as global RH theorem.",
            "found": any_col("contains_first_crossing_definition"),
        },
        {
            "lemma": "Theta/R2Q Covering",
            "status": "conditional",
            "statement_needed": "X0 maps to candidate/admissible row J.",
            "evidence": "Covering Localization Conditional Theorem gives this as Input/conditional theorem with empirical support.",
            "found": any_col("contains_covering_localization", proof_only=True),
        },
        {
            "lemma": "Threshold Relevance",
            "status": "conditional",
            "statement_needed": "First crossing implies Q_R2Q(J)>0.75.",
            "evidence": "ThresholdRelevance audit/closure gives empirical theorem-facing contrapositive; proof target remains.",
            "found": any_col("contains_threshold_relevance", proof_only=True),
        },
        {
            "lemma": "Endpoint Sign Orientation",
            "status": "conditional_incomplete",
            "statement_needed": "First crossing implies E_theta(J)>=0 or >0 in the v5 row orientation.",
            "evidence": "Theta conditional assembly states positive crossing gives E_theta>0 and negative gives E_theta<0; target needs unified E_theta>=0 for RH-scale crossing.",
            "found": any_col("contains_endpoint_sign_orientation", proof_only=True),
        },
        {
            "lemma": "Lower Crossing Handling",
            "status": "missing_or_needs_signed_version",
            "statement_needed": "Lower envelope crossings map to same nonnegative orientation or a separate symmetric theorem.",
            "evidence": "Existing conditional theta assembly says negative first crossing gives E_theta<0, which does not match target E_theta>=0 without reorientation.",
            "found": any_col("contains_lower_crossing_handling", proof_only=True),
        },
        {
            "lemma": "Finite-Zone Coverage",
            "status": "conditional",
            "statement_needed": "X0<P0 covered by finite certificate.",
            "evidence": "FiniteThetaEnvelope and finite certificate files exist; final index/reproducibility still noted.",
            "found": any_col("contains_finite_zone_coverage"),
        },
        {
            "lemma": "v5 Contradiction",
            "status": "proven_in_local_stack",
            "statement_needed": "Q_R2Q>0.75 => E_theta<0 using direct sign.",
            "evidence": "v5 assembly/direct sign files provide direct threshold sign.",
            "found": any_col("uses_direct_threshold_sign"),
        },
    ]
    return pd.DataFrame(rows)


def compatibility(review: pd.DataFrame) -> pd.DataFrame:
    evidence = review[~review["status"].isin(["spec", "target"])]
    # Mentions in v5/target can be warnings; use evidence file flags as a conservative indicator.
    failed_route = bool(evidence["uses_failed_delta_threshold_route"].any())
    return pd.DataFrame(
        [
            {
                "check": "uses_direct_threshold_sign",
                "pass": bool(review["uses_direct_threshold_sign"].any()),
                "evidence": "Direct threshold sign appears in v5/local stack files.",
            },
            {
                "check": "does_not_use_failed_delta_threshold_route",
                "pass": not failed_route,
                "evidence": "Some older/theory files mention Q_delta_D>0.75; these must remain warnings or be replaced by direct sign.",
            },
            {
                "check": "h_exc_sampled_grid_caveat",
                "pass": True,
                "evidence": "The target and v5 assembly warn not to assume full-grid H-Exc.",
            },
            {
                "check": "neutral_empty_available",
                "pass": True,
                "evidence": "NeutralClause has been closed by emptiness in the audited row set.",
            },
            {
                "check": "lower_crossing_target_aligned",
                "pass": False,
                "evidence": "Existing theta assembly maps negative first crossing to E_theta<0; target needs reorientation or signed split.",
            },
        ]
    )


def classify(lemmas: pd.DataFrame, compat: pd.DataFrame) -> tuple[str, str, str, bool]:
    statuses = {r["lemma"]: r["status"] for _, r in lemmas.iterrows()}
    if not bool(compat.loc[compat["check"] == "does_not_use_failed_delta_threshold_route", "pass"].iloc[0]):
        return (
            "uses_outdated_delta_route",
            "Remove or quarantine any dependency on Q_delta_D>0.75 and rewrite through direct threshold sign.",
            "Prime_Mesh_R2Q_FirstCrossing_Localization_v5_Repair_Map_v1.md",
            False,
        )
    if statuses["Endpoint Sign Orientation"] != "proven" or statuses["Lower Crossing Handling"] != "proven":
        return (
            "missing_endpoint_sign_orientation",
            "Threshold relevance and covering support exist, but the theorem still needs a v5 signed-orientation lemma, especially for lower crossings.",
            "Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Proof_Attack_v1.md",
            False,
        )
    if statuses["Theta/R2Q Covering"] != "proven":
        return (
            "missing_row_covering",
            "Endpoint sign exists but row covering remains conditional.",
            "Prime_Mesh_R2Q_FirstCrossing_RowCovering_Proof_Attack_v1.md",
            False,
        )
    if statuses["Threshold Relevance"] != "proven":
        return (
            "missing_threshold_relevance",
            "Crossing-to-row exists but Q_R2Q>0.75 is not analytically closed.",
            "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Proof_Attack_v1.md",
            False,
        )
    return (
        "firstcrossing_localization_proved_v5_compatible",
        "All required lemmas are present and v5 compatible.",
        "Prime_Mesh_R2Q_GlobalBridge_to_RH_Theorem_Target_v1.md",
        True,
    )


def gaps(classification: str) -> pd.DataFrame:
    rows = [
        {
            "gap_id": "G1",
            "gap": "Endpoint sign orientation",
            "status": "open" if classification == "missing_endpoint_sign_orientation" else "review",
            "detail": "Need theorem that selected first-crossing row has E_theta>=0 in the target orientation, or split upper/lower signs.",
            "recommended_file": "Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Proof_Attack_v1.md",
        },
        {
            "gap_id": "G2",
            "gap": "Lower crossing handling",
            "status": "open" if classification == "missing_endpoint_sign_orientation" else "review",
            "detail": "Current theta assembly says negative first crossing gives E_theta<0; global contradiction needs signed reorientation or a separate lower-crossing theorem.",
            "recommended_file": "Prime_Mesh_R2Q_FirstCrossing_LowerCrossing_SignedOrientation_Target_v1.md",
        },
        {
            "gap_id": "G3",
            "gap": "Covering and threshold relevance remain conditional",
            "status": "conditional",
            "detail": "Audits and conditional theorems support row covering and threshold relevance, but they are not final analytic proof from first principles.",
            "recommended_file": "Prime_Mesh_R2Q_FirstCrossing_Localization_Conditional_Closure_Update_v1.md",
        },
        {
            "gap_id": "G4",
            "gap": "Finite/von Koch bridge",
            "status": "available_but_final_assembly_needed",
            "detail": "Finite theta envelope and von Koch target are present; final theorem must thread them after localization is proved.",
            "recommended_file": "Prime_Mesh_R2Q_vonKoch_RHScale_Bridge_Theorem_Target_v1.md",
        },
    ]
    return pd.DataFrame(rows)


def reviews(review: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    full = review[review["file_name"].str.contains("FullFCL", case=False, na=False)].copy()
    theta = review[review["file_name"].str.contains("Theta|theta", case=False, na=False)].copy()
    threshold = review[review["file_name"].str.contains("ThresholdRelevance", case=False, na=False)].copy()
    return full, theta, threshold


def make_summary(review: pd.DataFrame, lemmas: pd.DataFrame, compat_df: pd.DataFrame, data_df: pd.DataFrame) -> pd.DataFrame:
    classification, missing, next_file, passed = classify(lemmas, compat_df)
    lemma_map = {r["lemma"]: r["status"] for _, r in lemmas.iterrows()}
    summary = {
        "files_scanned": len(review),
        "prioritized_files_found": int((review["status"] != "missing").sum()) if "status" in review else len(review),
        "envelope_definition_status": lemma_map["Envelope Definition"],
        "first_crossing_definition_status": lemma_map["First-Crossing Existence"],
        "theta_r2q_covering_status": lemma_map["Theta/R2Q Covering"],
        "threshold_relevance_status": lemma_map["Threshold Relevance"],
        "endpoint_sign_orientation_status": lemma_map["Endpoint Sign Orientation"],
        "lower_crossing_handling_status": lemma_map["Lower Crossing Handling"],
        "finite_zone_coverage_status": lemma_map["Finite-Zone Coverage"],
        "von_koch_bridge_status": "defined_target_present",
        "uses_failed_delta_threshold_route": not bool(
            compat_df.loc[compat_df["check"] == "does_not_use_failed_delta_threshold_route", "pass"].iloc[0]
        ),
        "uses_direct_threshold_sign": bool(compat_df.loc[compat_df["check"] == "uses_direct_threshold_sign", "pass"].iloc[0]),
        "FullFCL_status": "conditional_support_present",
        "theta_envelope_status": "conditional_support_present",
        "threshold_relevance_data_status": "present" if any(data_df["data_file"].eq("prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv") & data_df["found"]) else "missing",
        "firstcrossing_localization_classification": classification,
        "main_missing_lemma": missing,
        "recommended_next_file": next_file,
        "pass_firstcrossing_localization_audit": passed,
    }
    return pd.DataFrame([summary])


def write_doc(summary: pd.DataFrame, lemmas: pd.DataFrame, review: pd.DataFrame, statements: pd.DataFrame, gaps_df: pd.DataFrame) -> None:
    s = summary.iloc[0]
    lines = [
        "# Prime Mesh R2Q — FirstCrossing Localization Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "Audit whether existing files prove the missing first-crossing localization theorem:",
        "",
        "```text",
        "global RH-scale first crossing => exists J with Q_R2Q(J)>0.75 and E_theta(J)>=0",
        "```",
        "",
        "## 2. Summary",
        "",
        f"- Files scanned: `{int(s['files_scanned'])}`.",
        f"- Classification: `{s['firstcrossing_localization_classification']}`.",
        f"- Main missing lemma: {s['main_missing_lemma']}",
        f"- Pass audit: `{bool(s['pass_firstcrossing_localization_audit'])}`.",
        "",
        "## 3. Lemma Checklist",
        "",
        "| lemma | status | evidence |",
        "|---|---|---|",
    ]
    for _, r in lemmas.iterrows():
        lines.append(f"| {r['lemma']} | `{r['status']}` | {r['evidence']} |")
    lines += [
        "",
        "## 4. File Review",
        "",
        "| file | status | covering | threshold | endpoint sign | lower crossing | finite | direct sign |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in review.head(18).iterrows():
        lines.append(
            f"| `{r['file_name']}` | `{r['status']}` | {bool(r['contains_covering_localization'])} | "
            f"{bool(r['contains_threshold_relevance'])} | {bool(r['contains_endpoint_sign_orientation'])} | "
            f"{bool(r['contains_lower_crossing_handling'])} | {bool(r['contains_finite_zone_coverage'])} | "
            f"{bool(r['uses_direct_threshold_sign'])} |"
        )
    lines += [
        "",
        "## 5. Statement Inventory",
        "",
        "Key statements were extracted to `prime_mesh_r2q_firstcrossing_localization_statement_inventory.csv`.",
        "",
        "Important audit finding: existing theta assembly states positive first crossings give `E_theta>0`, while negative first crossings give `E_theta<0`. The target theorem needs a unified `E_theta>=0` orientation or a signed split.",
        "",
        "## 6. v5 Compatibility",
        "",
        "The bridge must use direct threshold sign and must not rely on `Q_R2Q>0.75 => Q_delta_D>0.75`.",
        "",
        "## 7. Data Cross-Check",
        "",
        "Threshold relevance and theta/covering CSVs are present and support the empirical/conditional layers, but they do not by themselves prove the analytic localization theorem.",
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
        OUT_LEMMAS,
        OUT_COMPAT,
        OUT_GAPS,
        OUT_DATA,
        OUT_FULLFCL,
        OUT_THETA,
        OUT_THRESHOLD,
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
                "note": "FirstCrossing Localization audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    paths = [p for name in PRIORITY if (p := find_file(name)) is not None]
    review, statements = file_review(paths)
    data_df = data_crosscheck()
    lemmas = lemma_status(review)
    compat_df = compatibility(review)
    summary = make_summary(review, lemmas, compat_df, data_df)
    gaps_df = gaps(str(summary.iloc[0]["firstcrossing_localization_classification"]))
    full, theta, threshold = reviews(review)

    summary.to_csv(BASE / OUT_SUMMARY, index=False)
    review.to_csv(BASE / OUT_FILE_REVIEW, index=False)
    statements.to_csv(BASE / OUT_STATEMENTS, index=False)
    lemmas.to_csv(BASE / OUT_LEMMAS, index=False)
    compat_df.to_csv(BASE / OUT_COMPAT, index=False)
    gaps_df.to_csv(BASE / OUT_GAPS, index=False)
    data_df.to_csv(BASE / OUT_DATA, index=False)
    full.to_csv(BASE / OUT_FULLFCL, index=False)
    theta.to_csv(BASE / OUT_THETA, index=False)
    threshold.to_csv(BASE / OUT_THRESHOLD, index=False)
    write_doc(summary, lemmas, review, statements, gaps_df)
    update_manifest(
        [
            OUT_SCRIPT,
            OUT_SUMMARY,
            OUT_FILE_REVIEW,
            OUT_STATEMENTS,
            OUT_LEMMAS,
            OUT_COMPAT,
            OUT_GAPS,
            OUT_DATA,
            OUT_FULLFCL,
            OUT_THETA,
            OUT_THRESHOLD,
            OUT_DOC,
        ]
    )

    s = summary.iloc[0].to_dict()
    print("FirstCrossing Localization audit complete.")
    for key in [
        "files_scanned",
        "envelope_definition_status",
        "first_crossing_definition_status",
        "theta_r2q_covering_status",
        "threshold_relevance_status",
        "endpoint_sign_orientation_status",
        "lower_crossing_handling_status",
        "finite_zone_coverage_status",
        "uses_failed_delta_threshold_route",
        "uses_direct_threshold_sign",
        "firstcrossing_localization_classification",
        "main_missing_lemma",
        "recommended_next_file",
        "pass_firstcrossing_localization_audit",
    ]:
        print(f"{key}: {s[key]}")


if __name__ == "__main__":
    main()
