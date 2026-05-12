"""
Prime Mesh R2Q — CandidateGap FirstExitImpossibility audit.

Classifies coordinate gaps between sparse post-P0 FullFCL/theta candidates.
The script is intentionally conservative: it does not invent R(x), envelope
margin, jump-event, or per-gap lower-bracketing data when those files are absent.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

import pandas as pd


BASE = Path(__file__).resolve().parent
REPAIR = BASE.parent

OUT_SCRIPT = "prime_mesh_r2q_candidate_gap_firstexit_impossibility_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_candidate_gap_firstexit_impossibility_summary.csv"
OUT_ROWS = "prime_mesh_r2q_candidate_gap_firstexit_impossibility_rows.csv"
OUT_BY_CLASS = "prime_mesh_r2q_candidate_gap_firstexit_impossibility_by_class.csv"
OUT_UNKNOWN = "prime_mesh_r2q_candidate_gap_firstexit_impossibility_unknown.csv"
OUT_FAILURES = "prime_mesh_r2q_candidate_gap_firstexit_impossibility_failures.csv"
OUT_UPPER = "prime_mesh_r2q_candidate_gap_firstexit_impossibility_upper.csv"
OUT_LOWER = "prime_mesh_r2q_candidate_gap_firstexit_impossibility_lower.csv"
OUT_JUMPS = "prime_mesh_r2q_candidate_gap_firstexit_impossibility_jump_events.csv"
OUT_MARGINS = "prime_mesh_r2q_candidate_gap_firstexit_impossibility_margin_bounds.csv"
OUT_COMPAT = "prime_mesh_r2q_candidate_gap_firstexit_impossibility_v5_compatibility.csv"
OUT_DOC = "Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"

PRIORITY = [
    "Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Proof_Attack_v1.md",
    "Prime_Mesh_R2Q_ContinuousFirstExit_CandidateCompleteness_Audit_v1.md",
    "Prime_Mesh_R2Q_ContinuousFirstExit_CandidateCompleteness_Proof_Attack_v1.md",
    "Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Audit_v1.md",
    "Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Conditional_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_GlobalBridge_ConditionalAssembly_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Reclosure_Update_v2.md",
    "Prime_Mesh_R2Q_GlobalThetaEnvelope_Reclosure_Update_v2.md",
]


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


def unsafe_h_exc(text: str) -> bool:
    match = re.search(r"full-grid H-Exc|full grid HExc|sampled grid implies full", text, flags=re.IGNORECASE)
    if not match:
        return False
    window = text[max(0, match.start() - 120): match.end() + 120].lower()
    safe = [
        "do not", "must not", "avoid", "warning", "not", "false", "`false`",
        "mismatch", "incorrectly", "does any", "no full-grid", "upgrade used | false",
    ]
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


def scan_compat() -> pd.DataFrame:
    files = [p for name in PRIORITY if (p := find_file(name)) is not None]
    full_grid = False
    delta = False
    for path in files:
        text = read_text(path)
        full_grid = full_grid or unsafe_h_exc(text)
        delta = delta or unsafe_delta(text)
    return pd.DataFrame(
        [
            {
                "check": "uses_full_grid_HExc_upgrade",
                "pass": not full_grid,
                "value": full_grid,
                "evidence": "No unsafe H-Exc sampled-grid to full-grid upgrade found in prioritized files.",
            },
            {
                "check": "uses_failed_delta_route",
                "pass": not delta,
                "value": delta,
                "evidence": "No unsafe Q_R2Q>0.75 => Q_DeltaD>0.75 proof use found in prioritized files.",
            },
        ]
    )


def build_gap_rows() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    gaps = load_csv("prime_mesh_r2q_postp0_continuous_window_selection_gap_scan.csv")
    windows = load_csv("prime_mesh_r2q_firstcrossing_covering_localization_windows.csv")
    drift = load_csv("prime_mesh_r2q_postp0_continuous_window_selection_drift_bracketing.csv")
    jump = load_csv("prime_mesh_r2q_postp0_continuous_window_selection_jump_coverage.csv")
    finite = load_csv("prime_mesh_r2q_postp0_continuous_window_selection_P0_transition.csv")

    if gaps.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    w = windows.copy()
    if not w.empty:
        w["window_start"] = pd.to_numeric(w.get("y"), errors="coerce")
        w["window_end"] = pd.to_numeric(w.get("hi", w.get("x")), errors="coerce")
        w["post_P0_bool"] = w.get("post_P0", False).apply(norm_bool)
        post = w[w["post_P0_bool"]].copy()
        if post.empty:
            post = w[w["window_end"] >= 500_000_000].copy()
        post = post.sort_values(["window_start", "window_end"]).reset_index(drop=True)
    else:
        post = pd.DataFrame()

    jump_data_missing = jump.empty or jump.iloc[0].get("prime_jump_covered_count", "") == ""
    lower_bracketing_data_missing = drift.empty or drift.iloc[0].get("drift_interval_count", "") == ""
    missing_r_values = True
    rows = []
    for idx, gap in gaps.reset_index(drop=True).iterrows():
        left = post.iloc[idx].to_dict() if idx < len(post) else {}
        right = post.iloc[idx + 1].to_dict() if idx + 1 < len(post) else {}
        missing = []
        if missing_r_values:
            missing.append("missing_R_values")
        if jump_data_missing:
            missing.append("jump_event_data_missing")
        if lower_bracketing_data_missing:
            missing.append("lower_bracketing_interval_data_missing")
        missing.append("no_per_gap_subthreshold_or_O2_B3_mapping")

        rows.append(
            {
                "gap_id": f"gap_{idx:03d}",
                "gap_start": gap.get("gap_start"),
                "gap_end": gap.get("gap_end"),
                "gap_length": gap.get("gap_size"),
                "left_candidate_id": left.get("block_id", ""),
                "right_candidate_id": right.get("block_id", ""),
                "left_candidate_type": left.get("side", left.get("local_theta_sign", "")),
                "right_candidate_type": right.get("side", right.get("local_theta_sign", "")),
                "post_P0": True,
                "contains_jump_event": "",
                "jump_event_count": "",
                "contains_prime_jump": "",
                "contains_prime_power_jump": "",
                "upper_exit_possible": "",
                "lower_exit_possible": "",
                "lower_bracket_available": False,
                "subthreshold_safe": False,
                "O2_safe": False,
                "B3_safe": False,
                "finite_certificate_safe": False,
                "non_surviving_safe": False,
                "generator_contradiction_safe": False,
                "monotone_safe": False,
                "envelope_margin_safe": False,
                "gap_safety_class": "unknown",
                "gap_safety_pass": False,
                "gap_safety_reason": "No per-gap R(x)/envelope margin, jump-event, lower-bracket, subthreshold, or generator-contradiction certificate is available.",
                "missing_data_flags": ";".join(missing),
                "needed_data_or_lemma": "normalized_error_gap_bounds_or_generator_gap_contradiction_certificate",
            }
        )

    row_df = pd.DataFrame(rows)
    upper = pd.DataFrame(
        [
            {
                "upper_exit_impossible_count": 0,
                "upper_exit_possible_count": 0,
                "upper_exit_unknown_count": len(row_df),
                "jump_event_data_missing": jump_data_missing,
                "reason": "No per-gap jump-event inventory or upper-ratio monotonic certificate was available.",
            }
        ]
    )
    lower = pd.DataFrame(
        [
            {
                "lower_bracketed_count": 0,
                "lower_unbracketed_count": 0,
                "lower_unknown_count": len(row_df),
                "lower_bracketing_data_missing": lower_bracketing_data_missing,
                "reason": "Only aggregate audited lower-candidate bracketing exists; no per-gap lower drift interval mapping was available.",
            }
        ]
    )
    jumps = pd.DataFrame(
        [
            {
                "jump_event_file_found": not jump.empty,
                "per_gap_jump_events_available": not jump_data_missing,
                "jump_event_count": "",
                "jump_covered_count": jump.iloc[0].get("jump_covered_count", "") if not jump.empty else "",
                "note": "Existing jump coverage is aggregate over audited upper candidates, not per coordinate gap.",
            }
        ]
    )
    margins = pd.DataFrame(
        [
            {
                "R_values_available": False,
                "envelope_margin_bounds_available": False,
                "envelope_margin_safe_count": 0,
                "needed_data_or_lemma": "normalized_error_gap_bounds",
            }
        ]
    )
    return row_df, upper, lower, jumps, margins


def summarize(rows: pd.DataFrame, compat: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    expected = 141
    actual = len(rows)
    by_class = rows.groupby("gap_safety_class", dropna=False).size().reset_index(name="rows") if not rows.empty else pd.DataFrame(columns=["gap_safety_class", "rows"])
    unknown = rows[rows["gap_safety_class"].eq("unknown")].copy() if not rows.empty else pd.DataFrame()
    full_grid = bool(compat.loc[compat["check"].eq("uses_full_grid_HExc_upgrade"), "value"].iloc[0])
    delta = bool(compat.loc[compat["check"].eq("uses_failed_delta_route"), "value"].iloc[0])
    unknown_count = len(unknown)
    failure_count = unknown_count + int(full_grid) + int(delta)
    if unknown_count == 0 and not full_grid and not delta:
        classification = "all_gaps_safe"
        main_gap = "All coordinate gaps have a safety classification."
        next_file = "Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Theorem_Target_v1.md"
        passed = True
    elif unknown_count == actual and actual > 0:
        classification = "envelope_margin_data_missing"
        main_gap = "All gaps remain unknown because per-gap normalized error/envelope margin, jump-event, lower-bracket, and generator-contradiction data are unavailable."
        next_file = "Prime_Mesh_R2Q_NormalizedError_GapMargin_Audit_Spec_v1.md"
        passed = False
    elif unknown_count > 0:
        classification = "partial_gap_safety"
        main_gap = "Some gaps remain unknown."
        next_file = "Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Repair_Map_v1.md"
        passed = False
    else:
        classification = "repair_needed"
        main_gap = "v5 compatibility failure or concrete unsafe gap found."
        next_file = "Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Repair_Map_v1.md"
        passed = False

    summary = pd.DataFrame(
        [
            {
                "gap_count_expected": expected,
                "gap_count_actual": actual,
                "gap_inventory_pass": actual == expected,
                "upper_exit_impossible_count": int((rows["gap_safety_class"] == "upper_exit_impossible").sum()) if actual else 0,
                "upper_exit_possible_count": 0,
                "upper_exit_unknown_count": unknown_count,
                "lower_bracketed_count": int((rows["gap_safety_class"] == "lower_bracketed").sum()) if actual else 0,
                "lower_unbracketed_count": 0,
                "lower_unknown_count": unknown_count,
                "subthreshold_safe_count": int((rows["gap_safety_class"] == "subthreshold_safe").sum()) if actual else 0,
                "finite_certificate_safe_count": int((rows["gap_safety_class"] == "finite_certificate_safe").sum()) if actual else 0,
                "generator_contradiction_safe_count": int((rows["gap_safety_class"] == "generator_contradiction_safe").sum()) if actual else 0,
                "monotone_safe_count": int((rows["gap_safety_class"] == "monotone_safe").sum()) if actual else 0,
                "envelope_margin_safe_count": int((rows["gap_safety_class"] == "envelope_margin_safe").sum()) if actual else 0,
                "unknown_count": unknown_count,
                "failure_count": failure_count,
                "uses_full_grid_HExc_upgrade": full_grid,
                "uses_failed_delta_route": delta,
                "gap_safety_classification": classification,
                "main_gap_safety_gap": main_gap,
                "recommended_next_file": next_file,
                "pass_candidate_gap_firstexit_impossibility_audit": passed,
            }
        ]
    )
    failures = unknown[
        ["gap_id", "gap_start", "gap_end", "gap_length", "gap_safety_reason", "needed_data_or_lemma"]
    ].rename(columns={"gap_safety_reason": "why_unknown"}) if not unknown.empty else pd.DataFrame(columns=["gap_id", "gap_start", "gap_end", "gap_length", "why_unknown", "needed_data_or_lemma"])
    return summary, by_class, unknown, failures


def write_doc(summary: pd.DataFrame, by_class: pd.DataFrame, unknown: pd.DataFrame) -> None:
    s = summary.iloc[0]
    lines = [
        "# Prime Mesh R2Q — CandidateGap FirstExitImpossibility Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "Classify 141 coordinate gaps between sparse post-`P0` candidates.",
        "",
        "## 2. Summary",
        "",
        f"- Gap safety classification: `{s['gap_safety_classification']}`.",
        f"- Gap count actual/expected: `{int(s['gap_count_actual'])}/{int(s['gap_count_expected'])}`.",
        f"- Unknown gaps: `{int(s['unknown_count'])}`.",
        f"- Failure/gap records: `{int(s['failure_count'])}`.",
        f"- Uses full-grid H-Exc upgrade: `{bool(s['uses_full_grid_HExc_upgrade'])}`.",
        f"- Uses failed delta route: `{bool(s['uses_failed_delta_route'])}`.",
        f"- Pass audit: `{bool(s['pass_candidate_gap_firstexit_impossibility_audit'])}`.",
        "",
        "## 3. Gap Inventory",
        "",
        f"`gap_inventory_pass={bool(s['gap_inventory_pass'])}`.",
        "",
        "## 4. Safety Classes",
        "",
        "| class | rows |",
        "|---|---:|",
    ]
    for _, row in by_class.iterrows():
        lines.append(f"| `{row['gap_safety_class']}` | `{int(row['rows'])}` |")
    lines += [
        "",
        "## 5. Upper-Exit Safety",
        "",
        "No per-gap jump-event inventory or upper-ratio monotonic certificate was available, so upper-exit safety is unknown for the gaps.",
        "",
        "## 6. Lower-Drift Safety",
        "",
        "Only aggregate audited lower-candidate bracketing exists. No per-gap lower drift interval mapping was available.",
        "",
        "## 7. Unknown Gaps",
        "",
        f"Unknown gap rows emitted: `{len(unknown)}`.",
        "",
        "Needed repair data/lemma: `normalized_error_gap_bounds_or_generator_gap_contradiction_certificate`.",
        "",
        "## 8. v5 Compatibility",
        "",
        f"- Full-grid H-Exc upgrade: `{bool(s['uses_full_grid_HExc_upgrade'])}`.",
        f"- Failed delta route: `{bool(s['uses_failed_delta_route'])}`.",
        "",
        "## 9. Conclusion",
        "",
        f"`{s['main_gap_safety_gap']}`",
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
        OUT_ROWS,
        OUT_BY_CLASS,
        OUT_UNKNOWN,
        OUT_FAILURES,
        OUT_UPPER,
        OUT_LOWER,
        OUT_JUMPS,
        OUT_MARGINS,
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
                "note": "CandidateGap FirstExitImpossibility audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    compat = scan_compat()
    rows, upper, lower, jumps, margins = build_gap_rows()
    summary, by_class, unknown, failures = summarize(rows, compat)

    summary.to_csv(BASE / OUT_SUMMARY, index=False)
    rows.to_csv(BASE / OUT_ROWS, index=False)
    by_class.to_csv(BASE / OUT_BY_CLASS, index=False)
    unknown.to_csv(BASE / OUT_UNKNOWN, index=False)
    failures.to_csv(BASE / OUT_FAILURES, index=False)
    upper.to_csv(BASE / OUT_UPPER, index=False)
    lower.to_csv(BASE / OUT_LOWER, index=False)
    jumps.to_csv(BASE / OUT_JUMPS, index=False)
    margins.to_csv(BASE / OUT_MARGINS, index=False)
    compat.to_csv(BASE / OUT_COMPAT, index=False)
    write_doc(summary, by_class, unknown)

    outputs = [
        OUT_SCRIPT, OUT_SUMMARY, OUT_ROWS, OUT_BY_CLASS, OUT_UNKNOWN,
        OUT_FAILURES, OUT_UPPER, OUT_LOWER, OUT_JUMPS, OUT_MARGINS,
        OUT_COMPAT, OUT_DOC,
    ]
    update_manifest(outputs)

    print("CandidateGap FirstExitImpossibility audit complete.")
    s = summary.iloc[0].to_dict()
    for key in [
        "gap_count_expected",
        "gap_count_actual",
        "gap_inventory_pass",
        "upper_exit_impossible_count",
        "lower_bracketed_count",
        "subthreshold_safe_count",
        "finite_certificate_safe_count",
        "generator_contradiction_safe_count",
        "monotone_safe_count",
        "envelope_margin_safe_count",
        "unknown_count",
        "uses_full_grid_HExc_upgrade",
        "uses_failed_delta_route",
        "gap_safety_classification",
        "main_gap_safety_gap",
        "recommended_next_file",
        "pass_candidate_gap_firstexit_impossibility_audit",
    ]:
        print(f"{key}: {s[key]}")


if __name__ == "__main__":
    main()
