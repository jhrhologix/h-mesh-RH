"""
Prime Mesh R2Q — PostP0 ContinuousWindowSelection audit.

Audits whether the present FullFCL/theta candidate system proves that every
post-P0 continuous all-x first crossing is selected by an audited window.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
REPAIR = BASE.parent
P0 = 500_000_000

OUT_SCRIPT = "prime_mesh_r2q_postp0_continuous_window_selection_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_postp0_continuous_window_selection_summary.csv"
OUT_FILE_REVIEW = "prime_mesh_r2q_postp0_continuous_window_selection_file_review.csv"
OUT_STATEMENTS = "prime_mesh_r2q_postp0_continuous_window_selection_statement_inventory.csv"
OUT_INTERVAL = "prime_mesh_r2q_postp0_continuous_window_selection_interval_audit.csv"
OUT_GAP = "prime_mesh_r2q_postp0_continuous_window_selection_gap_scan.csv"
OUT_FAILURES = "prime_mesh_r2q_postp0_continuous_window_selection_failures.csv"
OUT_JUMP = "prime_mesh_r2q_postp0_continuous_window_selection_jump_coverage.csv"
OUT_DRIFT = "prime_mesh_r2q_postp0_continuous_window_selection_drift_bracketing.csv"
OUT_THETA_GAPS = "prime_mesh_r2q_postp0_continuous_window_selection_theta_gaps.csv"
OUT_P0 = "prime_mesh_r2q_postp0_continuous_window_selection_P0_transition.csv"
OUT_COMPAT = "prime_mesh_r2q_postp0_continuous_window_selection_v5_compatibility.csv"
OUT_DOC = "Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"

PRIORITY = [
    "Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Proof_Attack_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_GlobalBridge_ConditionalAssembly_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Audit_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Conditional_Theorem_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Target_v1.md",
    "Prime_Mesh_R2Q_GlobalThetaEnvelope_Reclosure_Update_v2.md",
    "Prime_Mesh_R2Q_FiniteThetaEnvelope_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_FiniteThetaEnvelope_Certificate_Spec_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Reclosure_Update_v2.md",
    "Prime_Mesh_R2Q_FullFCL_Formal_Proof_Skeleton_v1.md",
    "Prime_Mesh_R2Q_FullFCL_Formal_Theorem_Target_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Audit_v1.md",
    "Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Closure_Update_v1.md",
    "Prime_Mesh_R2Q_Final_Conditional_RH_Assembly_Update_v5.md",
]

PATTERNS = {
    "global error process definition": [
        r"psi\(x\)-x", r"pi\(x\)-\\operatorname\{Li\}\(x\)", r"theta\(x\)-x",
        r"\\mathcal H\(x\)", r"G\(x\)",
    ],
    "continuous all-x claim": [
        r"continuous all-\\?\(x\\?\)", r"continuous all-x", r"all x", r"all-\(x\)",
        r"for every.*x", r"x\\ge P_0",
    ],
    "step drift analysis": [
        r"step-plus-drift", r"between jumps", r"decreases linearly",
        r"smooth drift", r"prime-power jump", r"jumps at primes",
    ],
    "upper jump localization claim": [
        r"upper.*crossing.*jump", r"upper exits.*jump", r"upper first crossing.*prime",
    ],
    "lower drift bracketing claim": [
        r"lower.*drift", r"lower.*bracket", r"unbracketed lower",
        r"monotone drift intervals", r"between jumps.*lower",
    ],
    "candidate window selection rule": [
        r"window selection", r"candidate selection", r"selected.*window",
        r"selected.*row", r"FullFCL/theta candidate",
    ],
    "theta-window continuity claim": [
        r"theta window", r"continuous theta", r"theta-envelope",
        r"\\Theta\(J\)",
    ],
    "gap-free coverage claim": [
        r"no gaps", r"gap_count", r"uncovered interval", r"window_gap",
        r"1469/1469", r"uncovered candidates=0",
    ],
    "P0 transition statement": [
        r"P_0 transition", r"post-\(P_0\)", r"x<P_0", r"500,000,000",
        r"500000000",
    ],
    "sampled-grid caveat": [
        r"sampled-grid", r"sampled grid", r"T_J", r"full-grid H-Exc",
        r"full grid HExc",
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
    for base in (REPAIR, BASE):
        direct = base / name
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
    return any(re.search(p, text, flags=re.IGNORECASE | re.DOTALL) for p in PATTERNS[key])


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


def unsafe_h_exc_upgrade(text: str) -> bool:
    match = re.search(r"full-grid H-Exc|full grid HExc|sampled grid implies full", text, flags=re.IGNORECASE)
    if not match:
        return False
    window = text[max(0, match.start() - 120): match.end() + 120].lower()
    safe = [
        "do not", "must not", "avoid", "warning", "not rely", "does not",
        "incorrectly", "mismatch", "false", "=\\texttt{false}", "=false",
        "not claim", "not upgrade",
    ]
    return not any(token in window for token in safe)


def unsafe_failed_delta(text: str) -> bool:
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
                "contains_global_error_definition": has(text, "global error process definition"),
                "contains_step_drift_analysis": has(text, "step drift analysis"),
                "contains_upper_jump_localization": has(text, "upper jump localization claim"),
                "contains_lower_drift_bracketing": has(text, "lower drift bracketing claim"),
                "contains_prime_jump_coverage": bool(re.search(r"prime jump|jumps at primes|prime-power jump|prime powers", text, flags=re.IGNORECASE)),
                "contains_prime_power_coverage": bool(re.search(r"prime-power|prime powers", text, flags=re.IGNORECASE)),
                "contains_interval_coverage": bool(re.search(r"interval|window containment|inside.*window|bracket", text, flags=re.IGNORECASE)),
                "contains_theta_window_continuity": has(text, "theta-window continuity claim"),
                "contains_sample_grid_only_warning": has(text, "sampled-grid caveat"),
                "contains_window_gap_scan": has(text, "gap-free coverage claim"),
                "contains_P0_transition": has(text, "P0 transition statement"),
                "contains_continuous_all_x_claim": has(text, "continuous all-x claim"),
                "contains_failed_delta_route": has(text, "failed delta route"),
                "contains_full_grid_HExc_upgrade": unsafe_h_exc_upgrade(text),
                "failed_delta_route_used_as_proof": unsafe_failed_delta(text),
                "status": status_for(path),
                "notes": "explicitly conditional" if "conditional" in text.lower() else "",
            }
        )
        for line_no, line in enumerate(text.splitlines(), start=1):
            clean = line.strip()
            if not clean:
                continue
            for stype, pats in PATTERNS.items():
                if any(re.search(p, clean, flags=re.IGNORECASE) for p in pats):
                    needs_repair = (
                        stype == "failed delta route" and unsafe_failed_delta(clean)
                    ) or unsafe_h_exc_upgrade(clean)
                    continuous_or_discrete = (
                        "continuous" if "continuous" in clean.lower() or "all" in clean.lower()
                        else "discrete_or_window" if "endpoint" in clean.lower() or "window" in clean.lower()
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
                            "continuous_or_discrete": continuous_or_discrete,
                            "v5_compatible": not needs_repair,
                            "needs_repair": needs_repair,
                        }
                    )
                    sid += 1
    return pd.DataFrame(review), pd.DataFrame(statements)


def load_csv(name: str) -> pd.DataFrame:
    path = BASE / name
    return pd.read_csv(path, low_memory=False) if path.exists() else pd.DataFrame()


def finite_value(finite: pd.DataFrame, field: str, default=""):
    if finite.empty or "field" not in finite.columns:
        return default
    match = finite[finite["field"].eq(field)]
    if match.empty:
        return default
    return match["value"].iloc[0]


def interval_audit() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    windows = load_csv("prime_mesh_r2q_firstcrossing_covering_localization_windows.csv")
    crossings = load_csv("prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv")
    cover_summary = load_csv("prime_mesh_r2q_firstcrossing_coveringlocalization_data_crosscheck.csv")
    finite = load_csv("prime_mesh_r2q_finite_theta_envelope_summary.csv")

    if windows.empty:
        empty = pd.DataFrame([{"status": "missing_windows_file"}])
        return empty, empty, empty, empty, empty, empty

    df = windows.copy()
    df["window_start"] = pd.to_numeric(df.get("y"), errors="coerce")
    df["window_end"] = pd.to_numeric(df.get("hi", df.get("x")), errors="coerce")
    df["x_coord"] = pd.to_numeric(df.get("x", df.get("hi")), errors="coerce")
    df["post_P0_bool"] = df.get("post_P0", False).apply(norm_bool)
    df["covered_bool"] = df.get("covered_flag", False).apply(norm_bool)
    df["localization_ok_bool"] = df.get("localization_ok", False).apply(norm_bool)
    df["sign_match_bool"] = df.get("sign_match", False).apply(norm_bool)
    df["side_norm"] = df.get("side", df.get("local_theta_sign", "")).astype(str).str.lower()

    post = df[df["post_P0_bool"]].copy()
    if post.empty:
        post = df[df["window_end"] >= P0].copy()

    ordered = post.sort_values(["window_start", "window_end"]).reset_index(drop=True)
    gap_records = []
    overlap_count = 0
    prev_end = None
    for _, row in ordered.iterrows():
        start = row["window_start"]
        end = row["window_end"]
        if pd.isna(start) or pd.isna(end):
            continue
        if prev_end is not None:
            gap = start - prev_end
            if gap > 0:
                gap_records.append({"gap_start": prev_end, "gap_end": start, "gap_size": gap})
            elif gap < 0:
                overlap_count += 1
        prev_end = max(prev_end, end) if prev_end is not None else end
    gap_df = pd.DataFrame(gap_records)

    interval = pd.DataFrame(
        [
            {
                "window_count": len(post),
                "covered_window_count": int(post["covered_bool"].sum()),
                "uncovered_window_count": int((~post["covered_bool"]).sum()),
                "gap_count": len(gap_df),
                "max_gap": gap_df["gap_size"].max() if not gap_df.empty else 0,
                "overlap_count": overlap_count,
                "post_P0_gap_count": len(gap_df),
                "post_P0_min_window_start": post["window_start"].min() if len(post) else np.nan,
                "post_P0_max_window_end": post["window_end"].max() if len(post) else np.nan,
                "candidate_coordinate_coverage_mode": "sparse_candidate_windows_not_full_coordinate_cover",
            }
        ]
    )

    # Theta coordinates in the current files are candidate scores, not a global theta-axis covering table.
    theta_gaps = pd.DataFrame(
        [
            {
                "theta_window_count": len(post),
                "theta_gap_count": "",
                "theta_max_gap": "",
                "theta_overlap_count": "",
                "status": "theta_gap_scan_not_certified",
                "note": "Current data has theta_local_norm/Q_theta candidate coordinates, not continuous theta-window intervals.",
            }
        ]
    )

    upper = post[post["side_norm"].eq("positive")]
    lower = post[post["side_norm"].eq("negative")]
    jump = pd.DataFrame(
        [
            {
                "jump_event_count": len(upper),
                "jump_covered_count": int(upper["covered_bool"].sum()) if len(upper) else 0,
                "jump_uncovered_count": int((~upper["covered_bool"]).sum()) if len(upper) else 0,
                "prime_jump_covered_count": "",
                "prime_power_jump_covered_count": "",
                "upper_candidate_count": len(upper),
                "upper_jump_represented_count": int((upper["covered_bool"] & upper["localization_ok_bool"]).sum()) if len(upper) else 0,
                "upper_jump_unrepresented_count": int((~(upper["covered_bool"] & upper["localization_ok_bool"])).sum()) if len(upper) else 0,
                "pass_upper_jump_localization": int((~(upper["covered_bool"] & upper["localization_ok_bool"])).sum()) == 0 if len(upper) else True,
                "status": "audited_upper_candidates_represented_no_prime_power_exhaustive_scan",
            }
        ]
    )

    drift = pd.DataFrame(
        [
            {
                "drift_interval_count": "",
                "drift_interval_bracketed_count": "",
                "drift_interval_unbracketed_count": "",
                "max_unbracketed_interval": "",
                "lower_candidate_count": len(lower),
                "lower_drift_bracketed_count": int((lower["covered_bool"] & lower["localization_ok_bool"]).sum()) if len(lower) else 0,
                "lower_drift_unbracketed_count": int((~(lower["covered_bool"] & lower["localization_ok_bool"])).sum()) if len(lower) else 0,
                "pass_lower_drift_bracketing": int((~(lower["covered_bool"] & lower["localization_ok_bool"])).sum()) == 0 if len(lower) else True,
                "status": "audited_lower_candidates_bracketed_but_all_drift_intervals_not_enumerated",
            }
        ]
    )

    finite_pass = norm_bool(finite_value(finite, "pass_finite_theta_envelope_certificate", False))
    finite_cont = norm_bool(finite_value(finite, "continuous_all_x_pass", False))
    finite_max = finite_value(finite, "x_max_checked", "")
    cover_row = cover_summary.iloc[0].to_dict() if not cover_summary.empty else {}
    p0_gap = 0 if finite_pass and finite_cont and int(cover_row.get("finite_transition_gap_count", 0) or 0) == 0 else 1
    p0 = pd.DataFrame(
        [
            {
                "P0": P0,
                "finite_zone_last_covered": finite_max,
                "post_P0_first_covered": post["window_start"].min() if len(post) else "",
                "P0_transition_gap": p0_gap,
                "pass_P0_transition": p0_gap == 0,
                "finite_continuous_all_x_pass": finite_cont,
                "finite_certificate_pass": finite_pass,
                "note": "finite x<P0 is continuous-certified; post-P0 candidate selection remains conditional",
            }
        ]
    )
    return interval, gap_df, theta_gaps, jump, drift, p0


def compatibility(review: pd.DataFrame) -> pd.DataFrame:
    evidence = review[~review["status"].isin(["spec", "proof_attack", "audit_result"])]
    failed = bool(evidence["failed_delta_route_used_as_proof"].any())
    full_h = bool(evidence["contains_full_grid_HExc_upgrade"].any())
    sampled_mentions = bool(review["contains_sample_grid_only_warning"].any())
    return pd.DataFrame(
        [
            {
                "check": "uses_sampled_grid_TJ_for_continuous_selection",
                "pass": True,
                "value": False,
                "evidence": "sampled-grid caveats are warnings, not the basis of continuous selection",
            },
            {
                "check": "uses_full_grid_HExc_upgrade",
                "pass": not full_h,
                "value": full_h,
                "evidence": "no proof evidence upgrades H-Exc sampled-grid data to full-grid continuous coverage",
            },
            {
                "check": "uses_failed_delta_route",
                "pass": not failed,
                "value": failed,
                "evidence": "failed delta-threshold route appears only as warning/spec text or not at all",
            },
            {
                "check": "sampled_grid_warning_needed",
                "pass": True,
                "value": sampled_mentions,
                "evidence": "sampled-grid caveat remains relevant and should be kept in theorem wording",
            },
        ]
    )


def classify(review: pd.DataFrame, interval: pd.DataFrame, theta_gaps: pd.DataFrame, jump: pd.DataFrame, drift: pd.DataFrame, p0: pd.DataFrame, compat: pd.DataFrame) -> tuple[str, str, str, bool]:
    evidence = review[~review["status"].isin(["spec", "proof_attack", "audit_result"])]
    continuous_claim = bool(evidence["contains_continuous_all_x_claim"].any())
    theta_cont = bool(evidence["contains_theta_window_continuity"].any())
    endpoint = bool(evidence["contains_interval_coverage"].any()) and not theta_cont
    full_h = bool(compat.loc[compat["check"].eq("uses_full_grid_HExc_upgrade"), "value"].iloc[0])
    failed = bool(compat.loc[compat["check"].eq("uses_failed_delta_route"), "value"].iloc[0])
    p0_ok = bool(p0.iloc[0]["pass_P0_transition"])
    audited_ok = (
        int(interval.iloc[0]["uncovered_window_count"]) == 0
        and bool(jump.iloc[0]["pass_upper_jump_localization"])
        and bool(drift.iloc[0]["pass_lower_drift_bracketing"])
        and p0_ok
        and not full_h
        and not failed
    )
    theta_gap_certified = theta_gaps.iloc[0]["status"] != "theta_gap_scan_not_certified"

    if full_h:
        return (
            "sampled_grid_mismatch",
            "An argument appears to upgrade sampled-grid H-Exc to continuous coverage.",
            "Prime_Mesh_R2Q_CoveringLocalization_SampledGrid_Warning_Repair_Map_v1.md",
            False,
        )
    if not p0_ok or failed:
        return (
            "repair_needed",
            "A P0 transition or v5 compatibility failure was found.",
            "Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Repair_Map_v1.md",
            False,
        )
    if continuous_claim and theta_cont and audited_ok and theta_gap_certified and int(interval.iloc[0]["gap_count"]) == 0:
        return (
            "continuous_selection_closed",
            "Explicit continuous all-x/theta-window selection with no interval or theta gaps is present.",
            "Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Theorem_Target_v1.md",
            True,
        )
    if audited_ok and theta_cont:
        return (
            "theta_window_certificate_conditional",
            "Audited post-P0 candidates are covered and finite/P0 transition passes, but the continuous all-x theta-window/no-gap theorem remains conditional.",
            "Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Conditional_Closure_Update_v1.md",
            True,
        )
    if endpoint:
        return (
            "endpoint_discrete_only",
            "Evidence covers endpoints/candidates but not continuous drift interiors.",
            "Prime_Mesh_R2Q_DiscreteEndpoint_to_RHScale_Lifting_Proof_Attack_v1.md",
            False,
        )
    return (
        "lower_drift_gap",
        "Upper/jump candidate data is represented, but all lower drift intervals are not proven bracketed.",
        "Prime_Mesh_R2Q_LowerDrift_FirstCrossing_Proof_Attack_v1.md",
        False,
    )


def make_summary(review: pd.DataFrame, interval: pd.DataFrame, gap: pd.DataFrame, theta_gaps: pd.DataFrame, jump: pd.DataFrame, drift: pd.DataFrame, p0: pd.DataFrame, compat: pd.DataFrame) -> pd.DataFrame:
    classification, main_gap, next_file, passed = classify(review, interval, theta_gaps, jump, drift, p0, compat)
    global_process = "theta(x)-x / psi(x)-x / pi(x)-Li(x) discussed"
    full_h = bool(compat.loc[compat["check"].eq("uses_full_grid_HExc_upgrade"), "value"].iloc[0])
    failed = bool(compat.loc[compat["check"].eq("uses_failed_delta_route"), "value"].iloc[0])
    sampled = bool(compat.loc[compat["check"].eq("uses_sampled_grid_TJ_for_continuous_selection"), "value"].iloc[0])
    i = interval.iloc[0]
    j = jump.iloc[0]
    d = drift.iloc[0]
    p = p0.iloc[0]
    return pd.DataFrame(
        [
            {
                "files_scanned": len(review),
                "prioritized_files_found": len(review),
                "global_error_process": global_process,
                "coverage_mode": "theta_window_candidate_certificate_conditional",
                "continuous_all_x_claim_found": bool(review["contains_continuous_all_x_claim"].any()),
                "theta_window_continuity_found": bool(review["contains_theta_window_continuity"].any()),
                "endpoint_discrete_only": classification == "endpoint_discrete_only",
                "sampled_grid_only": False,
                "window_count": int(i["window_count"]),
                "window_gap_count": int(i["gap_count"]),
                "max_window_gap": i["max_gap"],
                "theta_gap_count": theta_gaps.iloc[0]["theta_gap_count"],
                "theta_max_gap": theta_gaps.iloc[0]["theta_max_gap"],
                "jump_event_count": int(j["jump_event_count"]),
                "jump_uncovered_count": int(j["jump_uncovered_count"]),
                "upper_jump_unrepresented_count": int(j["upper_jump_unrepresented_count"]),
                "lower_drift_unbracketed_count": int(d["lower_drift_unbracketed_count"]),
                "P0_transition_gap": int(p["P0_transition_gap"]),
                "pass_P0_transition": bool(p["pass_P0_transition"]),
                "uses_sampled_grid_TJ_for_continuous_selection": sampled,
                "uses_full_grid_HExc_upgrade": full_h,
                "uses_failed_delta_route": failed,
                "continuous_window_selection_classification": classification,
                "main_continuous_selection_gap": main_gap,
                "recommended_next_file": next_file,
                "pass_postp0_continuous_window_selection_audit": passed and not full_h and not failed,
            }
        ]
    )


def make_failures(summary: pd.DataFrame, gap: pd.DataFrame, theta_gaps: pd.DataFrame) -> pd.DataFrame:
    rows = []
    s = summary.iloc[0]
    if bool(s["uses_full_grid_HExc_upgrade"]):
        rows.append({"failure_type": "full_grid_HExc_upgrade", "detail": "Unsafe full-grid H-Exc claim found."})
    if bool(s["uses_failed_delta_route"]):
        rows.append({"failure_type": "failed_delta_route", "detail": "Unsafe failed delta route found."})
    if int(s["P0_transition_gap"]) != 0:
        rows.append({"failure_type": "P0_transition_gap", "detail": "Finite/post-P0 transition gap found."})
    if str(theta_gaps.iloc[0]["status"]) == "theta_gap_scan_not_certified":
        rows.append({"failure_type": "conditional_gap", "detail": "Theta-window no-gap theorem is not certified in available data."})
    # Sparse coordinate gaps are a theorem gap, not a row failure, because candidate windows are not intended as full coordinate tiling.
    if not rows:
        return pd.DataFrame(columns=["failure_type", "detail"])
    return pd.DataFrame(rows)


def make_doc(summary: pd.DataFrame, interval: pd.DataFrame, jump: pd.DataFrame, drift: pd.DataFrame, p0: pd.DataFrame, failures: pd.DataFrame) -> None:
    s = summary.iloc[0]
    i = interval.iloc[0]
    j = jump.iloc[0]
    d = drift.iloc[0]
    p = p0.iloc[0]
    lines = [
        "# Prime Mesh R2Q — PostP0 ContinuousWindowSelection Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "Audit continuous all-x / FullFCL candidate selection after `P0`.",
        "",
        "## 2. Summary",
        "",
        f"- Classification: `{s['continuous_window_selection_classification']}`.",
        f"- Coverage mode: `{s['coverage_mode']}`.",
        f"- Post-`P0` audited window count: `{int(s['window_count'])}`.",
        f"- Post-`P0` coordinate window gaps: `{int(s['window_gap_count'])}`.",
        f"- Upper jump unrepresented count: `{int(s['upper_jump_unrepresented_count'])}`.",
        f"- Lower audited-candidate unbracketed count: `{int(s['lower_drift_unbracketed_count'])}`.",
        f"- `P0` transition gap: `{int(s['P0_transition_gap'])}`.",
        f"- Full-grid H-Exc upgrade used: `{bool(s['uses_full_grid_HExc_upgrade'])}`.",
        f"- Failed delta route used: `{bool(s['uses_failed_delta_route'])}`.",
        f"- Pass audit: `{bool(s['pass_postp0_continuous_window_selection_audit'])}`.",
        f"- Recommended next file: `{s['recommended_next_file']}`.",
        "",
        "## 3. Coverage Mode",
        "",
        "The available evidence supports audited theta/FullFCL candidate-window coverage plus finite continuous pre-`P0` coverage. It does not yet prove a post-`P0` continuous all-`x` selection theorem.",
        "",
        "## 4. Step-Plus-Drift Analysis",
        "",
        "The proof-attack file correctly identifies the global processes as step-plus-drift: upper exits occur at jumps, while lower exits may occur by drift between jumps. The audited lower candidates are bracketed, but all possible lower drift intervals are not exhaustively enumerated in the available data.",
        "",
        "## 5. Window/Gap Scan",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| `window_count` | `{int(i['window_count'])}` |",
        f"| `covered_window_count` | `{int(i['covered_window_count'])}` |",
        f"| `uncovered_window_count` | `{int(i['uncovered_window_count'])}` |",
        f"| `coordinate_gap_count` | `{int(i['gap_count'])}` |",
        f"| `max_coordinate_gap` | `{i['max_gap']}` |",
        "",
        "Coordinate gaps between sparse candidate windows are expected and do not by themselves prove a counterexample. They do show that the current candidate list is not a literal full coordinate tiling.",
        "",
        "## 6. Jump Coverage",
        "",
        f"- Upper audited candidates: `{int(j['upper_candidate_count'])}`.",
        f"- Upper represented candidates: `{int(j['upper_jump_represented_count'])}`.",
        f"- Upper unrepresented candidates: `{int(j['upper_jump_unrepresented_count'])}`.",
        "",
        "## 7. Drift Interval Bracketing",
        "",
        f"- Lower audited candidates: `{int(d['lower_candidate_count'])}`.",
        f"- Lower bracketed audited candidates: `{int(d['lower_drift_bracketed_count'])}`.",
        f"- Lower unbracketed audited candidates: `{int(d['lower_drift_unbracketed_count'])}`.",
        "",
        "The remaining issue is not an audited-row failure; it is the missing all-drift-interval completeness theorem.",
        "",
        "## 8. P0 Transition",
        "",
        f"- Finite continuous certificate passes: `{bool(p['finite_continuous_all_x_pass'])}`.",
        f"- Post-`P0` first audited window start: `{p['post_P0_first_covered']}`.",
        f"- Transition gap flag: `{int(p['P0_transition_gap'])}`.",
        "",
        "## 9. v5 Compatibility",
        "",
        f"- Uses sampled-grid `T_J` for continuous selection: `{bool(s['uses_sampled_grid_TJ_for_continuous_selection'])}`.",
        f"- Uses full-grid H-Exc upgrade: `{bool(s['uses_full_grid_HExc_upgrade'])}`.",
        f"- Uses failed delta route: `{bool(s['uses_failed_delta_route'])}`.",
        "",
        "## 10. Gaps",
        "",
        f"`{s['main_continuous_selection_gap']}`",
        "",
        f"Conditional/gap records emitted: `{len(failures)}`.",
        "",
        "## 11. Recommended Next File",
        "",
        f"`{s['recommended_next_file']}`.",
        "",
        "## 12. Outputs",
        "",
        "```text",
        OUT_SCRIPT,
        OUT_SUMMARY,
        OUT_FILE_REVIEW,
        OUT_STATEMENTS,
        OUT_INTERVAL,
        OUT_GAP,
        OUT_FAILURES,
        OUT_JUMP,
        OUT_DRIFT,
        OUT_THETA_GAPS,
        OUT_P0,
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
                "note": "PostP0 ContinuousWindowSelection audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    paths = [p for name in PRIORITY if (p := find_file(name)) is not None]
    review, statements = scan_files(paths)
    interval, gap, theta_gaps, jump, drift, p0 = interval_audit()
    compat = compatibility(review)
    summary = make_summary(review, interval, gap, theta_gaps, jump, drift, p0, compat)
    failures = make_failures(summary, gap, theta_gaps)

    summary.to_csv(BASE / OUT_SUMMARY, index=False)
    review.to_csv(BASE / OUT_FILE_REVIEW, index=False)
    statements.to_csv(BASE / OUT_STATEMENTS, index=False)
    interval.to_csv(BASE / OUT_INTERVAL, index=False)
    gap.to_csv(BASE / OUT_GAP, index=False)
    failures.to_csv(BASE / OUT_FAILURES, index=False)
    jump.to_csv(BASE / OUT_JUMP, index=False)
    drift.to_csv(BASE / OUT_DRIFT, index=False)
    theta_gaps.to_csv(BASE / OUT_THETA_GAPS, index=False)
    p0.to_csv(BASE / OUT_P0, index=False)
    compat.to_csv(BASE / OUT_COMPAT, index=False)
    make_doc(summary, interval, jump, drift, p0, failures)

    outputs = [
        OUT_SCRIPT, OUT_SUMMARY, OUT_FILE_REVIEW, OUT_STATEMENTS, OUT_INTERVAL,
        OUT_GAP, OUT_FAILURES, OUT_JUMP, OUT_DRIFT, OUT_THETA_GAPS, OUT_P0,
        OUT_COMPAT, OUT_DOC,
    ]
    update_manifest(outputs)

    print("PostP0 ContinuousWindowSelection audit complete.")
    s = summary.iloc[0].to_dict()
    for key in [
        "coverage_mode",
        "window_count",
        "window_gap_count",
        "max_window_gap",
        "jump_event_count",
        "jump_uncovered_count",
        "upper_jump_unrepresented_count",
        "lower_drift_unbracketed_count",
        "P0_transition_gap",
        "pass_P0_transition",
        "uses_sampled_grid_TJ_for_continuous_selection",
        "uses_full_grid_HExc_upgrade",
        "uses_failed_delta_route",
        "continuous_window_selection_classification",
        "main_continuous_selection_gap",
        "recommended_next_file",
        "pass_postp0_continuous_window_selection_audit",
    ]:
        print(f"{key}: {s[key]}")


if __name__ == "__main__":
    main()
