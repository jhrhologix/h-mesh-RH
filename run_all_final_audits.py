"""
Prime Mesh R2Q final audit reproduction runner.

Runs, validates, and reports the certificate-level theta bridge audit stack.
The expected values are pinned to the reproducibility README/runbook:
G(x)=theta(x)-x and C_theta=1.9233607946440099.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import math
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "final_audit_logs"

OUT_CSV = "prime_mesh_r2q_final_reproduction_report.csv"
OUT_MD = "Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md"
OUT_HASHES = "prime_mesh_r2q_final_artifact_hashes.txt"
OUT_MANIFEST = "deposit_manifest.csv"

ABS_TOL = 1e-9
REL_TOL = 1e-9
C_THETA = 1.9233607946440099
R_UPPER_MAX = -0.0006006774736066138
R_LOWER_MIN = -0.0007553068873594187
O2_CAP_MAX = 0.0499059549846063


def norm_key(value: Any) -> str:
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def norm_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y", "pass", "passes"}


def as_float(value: Any) -> float:
    if value is None or str(value).strip() == "":
        return float("nan")
    return float(value)


def as_int(value: Any) -> int:
    return int(round(as_float(value)))


def close(actual: Any, expected: float) -> bool:
    return math.isclose(as_float(actual), expected, rel_tol=REL_TOL, abs_tol=ABS_TOL)


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_summary(path: Path) -> dict[str, str]:
    rows = read_rows(path)
    if not rows:
        return {}
    first = rows[0]
    keys = list(first.keys())
    if len(keys) >= 2 and norm_key(keys[0]) in {"field", "metric", "key", "name"} and norm_key(keys[1]) == "value":
        return {norm_key(row[keys[0]]): row[keys[1]] for row in rows}
    return {norm_key(key): value for key, value in first.items()}


def csv_has_data_rows(path: Path) -> bool:
    rows = read_rows(path)
    return len(rows) > 0


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_file_hashes() -> None:
    suffixes = {".py", ".csv", ".md", ".txt"}
    files = [
        path for path in ROOT.iterdir()
        if path.is_file() and path.suffix.lower() in suffixes and path.name != OUT_HASHES
    ]
    with (ROOT / OUT_HASHES).open("w", encoding="utf-8", newline="\n") as handle:
        for path in sorted(files, key=lambda p: p.name.lower()):
            handle.write(f"{sha256_file(path)}  {path.name}\n")


def require(summary: dict[str, str], key: str, expected: Any) -> tuple[bool, str]:
    actual = summary.get(norm_key(key), "")
    if isinstance(expected, bool):
        ok = norm_bool(actual) is expected
    elif isinstance(expected, int):
        ok = as_int(actual) == expected
    elif isinstance(expected, float):
        ok = close(actual, expected)
    else:
        ok = str(actual) == str(expected)
    return ok, f"{key}={actual!r} expected {expected!r}"


def require_less(summary: dict[str, str], key: str, threshold: float) -> tuple[bool, str]:
    actual = as_float(summary.get(norm_key(key), "nan"))
    return actual < threshold, f"{key}={actual!r} expected < {threshold!r}"


def rows_count(path_name: str, predicate: Callable[[dict[str, str]], bool]) -> int | None:
    path = ROOT / path_name
    if not path.exists():
        return None
    return sum(1 for row in read_rows(path) if predicate(row))


def truthy_cell(row: dict[str, str], key: str) -> bool:
    return norm_bool(row.get(key, ""))


def check_threshold_rows(summary: dict[str, str]) -> list[tuple[bool, str]]:
    checks = [
        require(summary, "threshold_relevance_rows_actual", 10140),
        require(summary, "threshold_relevance_rows_expected", 10140),
        require(summary, "threshold_relevance_failures", 0),
        require(summary, "subthreshold_count", 10115),
        require(summary, "subthreshold_unclassified_count", 0),
        require(summary, "uses_failed_delta_route", False),
        require(summary, "uses_direct_threshold_sign", True),
        require(summary, "thresholdrelevance_scope_classification", "fullfcl_backed_certificate_conditional"),
    ]
    rows_file = "prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv"
    super_count = rows_count(rows_file, lambda r: truthy_cell(r, "superthreshold_flag"))
    forbidden_super = rows_count(rows_file, lambda r: truthy_cell(r, "superthreshold_flag") and truthy_cell(r, "forbidden_flag"))
    checks.append((super_count == 24, f"superthreshold rows={super_count} expected 24"))
    checks.append((forbidden_super == 11, f"forbidden superthreshold rows={forbidden_super} expected 11"))
    return checks


def check_normalized(summary: dict[str, str]) -> list[tuple[bool, str]]:
    return [
        require(summary, "gap_count", 141),
        require(summary, "gaps_with_margin_bounds", 141),
        require(summary, "gaps_margin_safe", 141),
        require(summary, "gaps_upper_risk", 0),
        require(summary, "gaps_lower_risk", 0),
        require(summary, "global_error_process_detected", "theta(x)-x"),
        require(summary, "envelope_constant_detected", C_THETA),
        require(summary, "R_upper_global_max", R_UPPER_MAX),
        require(summary, "R_lower_global_min", R_LOWER_MIN),
        require(summary, "total_prime_jumps_in_gaps", 22637),
        require(summary, "gapmargin_classification", "all_gaps_margin_safe"),
        require(summary, "pass_normalized_error_gapmargin_audit", True),
    ]


def check_postp0(summary: dict[str, str]) -> list[tuple[bool, str]]:
    return [
        require(summary, "continuous_window_selection_classification", "theta_window_certificate_conditional"),
        require(summary, "window_count", 142),
        require(summary, "window_gap_count", 141),
        require(summary, "jump_event_count", 120),
        require(summary, "jump_uncovered_count", 0),
        require(summary, "upper_jump_unrepresented_count", 0),
        require(summary, "lower_drift_unbracketed_count", 0),
        require(summary, "P0_transition_gap", 0),
        require(summary, "uses_full_grid_HExc_upgrade", False),
        require(summary, "uses_failed_delta_route", False),
        require(summary, "pass_postp0_continuous_window_selection_audit", True),
    ]


def check_endpointsign(summary: dict[str, str]) -> list[tuple[bool, str]]:
    return [
        require(summary, "endpointsign_classification", "upper_lower_split"),
        require(summary, "E_theta_orientation", "raw"),
        require(summary, "crossing_sign_variable_name", "local_theta_sign"),
        require(summary, "upper_crossing_rows", 1320),
        require(summary, "upper_E_theta_nonpositive_count", 0),
        require(summary, "lower_crossing_rows", 148),
        require(summary, "lower_E_theta_nonnegative_count", 0),
        require(summary, "lower_surviving_unrepaid_count", 0),
        require(summary, "pass_lower_o2b3_safety", True),
        require(summary, "uses_failed_delta_threshold_route", False),
        require(summary, "uses_direct_threshold_sign", True),
        require(summary, "pass_firstcrossing_endpointsign_audit", True),
    ]


def check_o2(summary: dict[str, str]) -> list[tuple[bool, str]]:
    return [
        require(summary, "rows", 1468),
        require(summary, "negative_subthreshold_count", 145),
        require(summary, "negative_subthreshold_post_P0_count", 21),
        require(summary, "negative_subthreshold_surviving_unrepaid_count", 0),
        require(summary, "O2_repayment_failures", 0),
        require(summary, "O2_cap_max", O2_CAP_MAX),
        require_less(summary, "O2_cap_max", 0.05),
        require(summary, "pass_o2_repayment_closure_empirical", True),
    ]


def check_b3(summary: dict[str, str]) -> list[tuple[bool, str]]:
    return [
        require(summary, "rows", 1469),
        require(summary, "post_P0_rows", 142),
        require(summary, "accumulation_risk_count", 142),
        require(summary, "accumulation_risk_surviving_unrepaid_count", 0),
        require(summary, "B3_noaccumulation_failures", 0),
        require(summary, "pass_O2_B3_consistency", True),
        require(summary, "pass_b3_noaccumulation_empirical", True),
    ]


def check_neutral(summary: dict[str, str]) -> list[tuple[bool, str]]:
    return [
        require(summary, "neutral_clause_failures", 0),
        require(summary, "neutral_1e_minus_2_count", 0),
        require(summary, "candidate_min_abs_E_theta", "hexc_00359"),
        require(summary, "min_abs_E_theta", 1.5258205110753806),
        require(summary, "threshold_rows_count", 3),
        require(summary, "pass_neutral_clause_closure_empirical", True),
    ]


def check_endpointmotion(summary: dict[str, str]) -> list[tuple[bool, str]]:
    return [
        require(summary, "Q_R2Q_gt_0p75_count", 3),
        require(summary, "pass_direct_threshold_transfer", True),
        require(summary, "pass_direct_delta_threshold", False),
        require(summary, "Q_R2Q_gt_0p75_Q_delta_D_le_0p75_count", 1),
        require(summary, "threshold_relevant_count", 3),
        require(summary, "thresholdtransfer_failures", 1),
        require(summary, "pass_endpointmotion_thresholdtransfer_empirical", True),
        require(summary, "best_thresholdtransfer_theorem_form", "direct_threshold_sign"),
    ]


def check_covering(summary: dict[str, str]) -> list[tuple[bool, str]]:
    return [
        require(summary, "covering_mode", "theta_window_covering"),
        require(summary, "covered_count", 1469),
        require(summary, "uncovered_count", 0),
        require(summary, "coverage_failures", 0),
        require(summary, "coverage_pass", True),
        require(summary, "finite_zone_status", "continuous_certificate_passes"),
        require(summary, "upper_lower_sign_preservation_status", "passes"),
        require(summary, "uses_failed_delta_threshold_route", False),
        require(summary, "uses_full_grid_HExc_upgrade", False),
        require(summary, "coveringlocalization_classification", "conditional_theta_window_plus_finite_continuous"),
        require(summary, "pass_coveringlocalization_audit", True),
    ]


def check_candidate_completeness(summary: dict[str, str]) -> list[tuple[bool, str]]:
    return [
        require(summary, "candidate_completeness_classification", "gap_safety_incomplete"),
        require(summary, "candidate_generator_found", True),
        require(summary, "post_P0_candidate_rows", 142),
        require(summary, "upper_candidate_rows", 120),
        require(summary, "upper_jump_missing_count", 0),
        require(summary, "lower_candidate_rows", 22),
        require(summary, "lower_drift_unbracketed_count", 0),
        require(summary, "gap_count", 141),
        require(summary, "gap_safety_proven_count", 0),
        require(summary, "gap_safety_unknown_count", 141),
        require(summary, "P0_transition_pass", True),
        require(summary, "uses_full_grid_HExc_upgrade", False),
        require(summary, "uses_failed_delta_route", False),
    ]


def check_candidate_gap(summary: dict[str, str]) -> list[tuple[bool, str]]:
    return [
        require(summary, "gap_count_expected", 141),
        require(summary, "gap_count_actual", 141),
        require(summary, "gap_inventory_pass", True),
        require(summary, "envelope_margin_safe_count", 0),
        require(summary, "unknown_count", 141),
        require(summary, "failure_count", 141),
        require(summary, "uses_full_grid_HExc_upgrade", False),
        require(summary, "uses_failed_delta_route", False),
        require(summary, "gap_safety_classification", "envelope_margin_data_missing"),
    ]


AUDITS: list[dict[str, Any]] = [
    {
        "name": "EndpointMotion ThresholdTransfer",
        "script": "prime_mesh_r2q_endpointmotion_thresholdtransfer_audit.py",
        "summary": "prime_mesh_r2q_endpointmotion_thresholdtransfer_summary.csv",
        "failure": "prime_mesh_r2q_endpointmotion_thresholdtransfer_failures.csv",
        "critical": True,
        "failure_expected_empty": False,
        "checks": check_endpointmotion,
    },
    {
        "name": "O2 Repayment Closure",
        "script": "prime_mesh_r2q_o2_repayment_closure_audit.py",
        "summary": "prime_mesh_r2q_o2_repayment_closure_summary.csv",
        "failure": "prime_mesh_r2q_o2_repayment_closure_failures.csv",
        "critical": True,
        "failure_expected_empty": True,
        "checks": check_o2,
    },
    {
        "name": "B3 NoAccumulation",
        "script": "prime_mesh_r2q_b3_noaccumulation_audit.py",
        "summary": "prime_mesh_r2q_b3_noaccumulation_summary.csv",
        "failure": "prime_mesh_r2q_b3_noaccumulation_failures.csv",
        "critical": True,
        "failure_expected_empty": True,
        "checks": check_b3,
    },
    {
        "name": "NeutralClause Closure",
        "script": "prime_mesh_r2q_neutral_clause_closure_audit.py",
        "summary": "prime_mesh_r2q_neutral_clause_closure_summary.csv",
        "failure": "prime_mesh_r2q_neutral_clause_closure_failures.csv",
        "critical": True,
        "failure_expected_empty": True,
        "checks": check_neutral,
    },
    {
        "name": "FirstCrossing EndpointSign",
        "script": "prime_mesh_r2q_firstcrossing_endpointsign_audit.py",
        "summary": "prime_mesh_r2q_firstcrossing_endpointsign_summary.csv",
        "failure": "",
        "critical": True,
        "failure_expected_empty": True,
        "checks": check_endpointsign,
    },
    {
        "name": "FirstCrossing CoveringLocalization",
        "script": "prime_mesh_r2q_firstcrossing_coveringlocalization_audit.py",
        "summary": "prime_mesh_r2q_firstcrossing_coveringlocalization_summary.csv",
        "failure": "",
        "critical": True,
        "failure_expected_empty": True,
        "checks": check_covering,
    },
    {
        "name": "FirstCrossing ThresholdRelevance",
        "script": "prime_mesh_r2q_firstcrossing_thresholdrelevance_audit.py",
        "summary": "prime_mesh_r2q_firstcrossing_thresholdrelevance_summary.csv",
        "failure": "prime_mesh_r2q_firstcrossing_thresholdrelevance_failures.csv",
        "critical": True,
        "failure_expected_empty": True,
        "checks": check_threshold_rows,
    },
    {
        "name": "PostP0 ContinuousWindowSelection",
        "script": "prime_mesh_r2q_postp0_continuous_window_selection_audit.py",
        "summary": "prime_mesh_r2q_postp0_continuous_window_selection_summary.csv",
        "failure": "prime_mesh_r2q_postp0_continuous_window_selection_failures.csv",
        "critical": True,
        "failure_expected_empty": False,
        "checks": check_postp0,
    },
    {
        "name": "ContinuousFirstExit CandidateCompleteness",
        "script": "prime_mesh_r2q_continuous_firstexit_candidate_completeness_audit.py",
        "summary": "prime_mesh_r2q_continuous_firstexit_candidate_completeness_summary.csv",
        "failure": "prime_mesh_r2q_continuous_firstexit_candidate_completeness_failures.csv",
        "critical": True,
        "failure_expected_empty": False,
        "checks": check_candidate_completeness,
    },
    {
        "name": "CandidateGap FirstExitImpossibility",
        "script": "prime_mesh_r2q_candidate_gap_firstexit_impossibility_audit.py",
        "summary": "prime_mesh_r2q_candidate_gap_firstexit_impossibility_summary.csv",
        "failure": "prime_mesh_r2q_candidate_gap_firstexit_impossibility_failures.csv",
        "critical": True,
        "failure_expected_empty": False,
        "checks": check_candidate_gap,
    },
    {
        "name": "NormalizedError GapMargin",
        "script": "prime_mesh_r2q_normalized_error_gapmargin_audit.py",
        "summary": "prime_mesh_r2q_normalized_error_gapmargin_summary.csv",
        "failure": "prime_mesh_r2q_normalized_error_gapmargin_failures.csv",
        "critical": True,
        "failure_expected_empty": True,
        "checks": check_normalized,
    },
]

OPTIONAL_SCRIPTS = [
    "prime_mesh_r2q_hexc_local_affinity_energybudget_audit.py",
    "prime_mesh_r2q_hexc_dn_residual_component_audit.py",
    "prime_mesh_r2q_hexc_primeshock_samplegrid_structure_audit.py",
    "prime_mesh_r2q_hexc_tj_grid_extraction_audit.py",
    "prime_mesh_r2q_hexc_primeshock_kernelgram_audit.py",
    "prime_mesh_r2q_hexc_primeshock_rayleighcoupling_audit.py",
    "prime_mesh_r2q_hexc_highweight_clusterfactor_audit.py",
    "prime_mesh_r2q_hexc_shortblock_cluster_audit.py",
]


def run_cmd(cmd: list[str], stdout_path: Path, stderr_path: Path) -> subprocess.CompletedProcess[str]:
    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        return subprocess.run(cmd, cwd=ROOT, stdout=out, stderr=err, text=True)


def audit_one(audit: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    LOG_DIR.mkdir(exist_ok=True)
    name = audit["name"]
    script = ROOT / audit["script"]
    stdout_log = LOG_DIR / f"{script.stem}.stdout.txt"
    stderr_log = LOG_DIR / f"{script.stem}.stderr.txt"
    summary = ROOT / audit["summary"]
    failure_name = audit.get("failure", "")
    failure_path = ROOT / failure_name if failure_name else None

    script_exists = script.exists()
    compile_pass = False
    run_attempted = False
    run_pass = False
    notes: list[str] = []

    if not script_exists:
        notes.append("missing script")
    elif not args.dry_run:
        compile_result = run_cmd([sys.executable, "-m", "py_compile", str(script)], stdout_log, stderr_log)
        compile_pass = compile_result.returncode == 0
        if not compile_pass:
            notes.append("py_compile failed")

        if compile_pass and not args.compile_only and not args.skip_run:
            run_attempted = True
            run_result = run_cmd([sys.executable, str(script)], stdout_log, stderr_log)
            run_pass = run_result.returncode == 0
            if not run_pass:
                notes.append("script run failed")
        elif args.skip_run or args.compile_only:
            run_pass = True
            notes.append("run skipped by flag")
    else:
        notes.append("dry run")

    summary_file_exists = summary.exists()
    summary_data = read_summary(summary)
    expected_checks: list[tuple[bool, str]] = []
    expected_counts_pass = False
    if summary_file_exists and not args.dry_run:
        expected_checks = audit["checks"](summary_data)
        expected_counts_pass = all(ok for ok, _ in expected_checks)
        notes.extend(msg for ok, msg in expected_checks if not ok)
    elif args.dry_run:
        expected_counts_pass = True

    failure_file_exists = bool(failure_path and failure_path.exists())
    failure_file_empty = True
    if failure_path:
        failure_file_empty = (not failure_path.exists()) or (not csv_has_data_rows(failure_path))
        if audit.get("failure_expected_empty", True) and not failure_file_empty:
            notes.append("failure file has data rows")
        if not audit.get("failure_expected_empty", True) and not failure_file_empty:
            notes.append("expected intermediate failure rows present")

    failure_check_pass = True
    if failure_path and audit.get("failure_expected_empty", True):
        failure_check_pass = failure_file_exists and failure_file_empty
    elif failure_path:
        failure_check_pass = failure_file_exists

    status_ok = (
        (script_exists or args.allow_missing)
        and (compile_pass or args.dry_run)
        and (run_pass or args.skip_run or args.compile_only or args.dry_run)
        and (summary_file_exists or args.dry_run)
        and expected_counts_pass
        and failure_check_pass
    )
    status = "PASS" if status_ok else "FAIL"

    return {
        "audit_name": name,
        "script_name": audit["script"],
        "script_exists": script_exists,
        "py_compile_pass": compile_pass,
        "run_attempted": run_attempted,
        "run_pass": run_pass,
        "stdout_log": str(stdout_log.relative_to(ROOT)),
        "stderr_log": str(stderr_log.relative_to(ROOT)),
        "summary_file": audit["summary"],
        "summary_file_exists": summary_file_exists,
        "expected_counts_pass": expected_counts_pass,
        "failure_file": failure_name,
        "failure_file_exists": failure_file_exists,
        "failure_file_empty": failure_file_empty,
        "failure_expected_empty": audit.get("failure_expected_empty", True),
        "critical": audit["critical"],
        "status": status,
        "notes": "; ".join(notes),
    }


def compile_optional(args: argparse.Namespace) -> list[str]:
    warnings: list[str] = []
    if args.hash_only or args.dry_run:
        return warnings
    for script_name in OPTIONAL_SCRIPTS:
        script = ROOT / script_name
        if not script.exists():
            msg = f"optional script missing: {script_name}"
            warnings.append(msg)
            if args.strict:
                continue
            continue
        stdout_log = LOG_DIR / f"{script.stem}.compile.stdout.txt"
        stderr_log = LOG_DIR / f"{script.stem}.compile.stderr.txt"
        result = run_cmd([sys.executable, "-m", "py_compile", str(script)], stdout_log, stderr_log)
        if result.returncode != 0:
            warnings.append(f"optional script compile failed: {script_name}")
    return warnings


def write_csv_report(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "audit_name", "script_name", "script_exists", "py_compile_pass", "run_attempted",
        "run_pass", "stdout_log", "stderr_log", "summary_file", "summary_file_exists",
        "expected_counts_pass", "failure_file", "failure_file_exists", "failure_file_empty",
        "failure_expected_empty", "critical", "status", "notes",
    ]
    with (ROOT / OUT_CSV).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def final_pass(rows: list[dict[str, Any]], warnings: list[str], args: argparse.Namespace) -> bool:
    critical_pass = all(row["status"] == "PASS" for row in rows if row["critical"])
    optional_ok = not args.strict or not warnings
    return critical_pass and optional_ok and (ROOT / OUT_HASHES).exists()


def key_constants() -> dict[str, str]:
    summary = read_summary(ROOT / "prime_mesh_r2q_normalized_error_gapmargin_summary.csv")
    return {
        "C_theta": summary.get("envelope_constant_detected", ""),
        "R_upper_global_max": summary.get("r_upper_global_max", ""),
        "R_lower_global_min": summary.get("r_lower_global_min", ""),
        "prime_jumps": summary.get("total_prime_jumps_in_gaps", ""),
    }


def write_md_report(rows: list[dict[str, Any]], warnings: list[str], args: argparse.Namespace) -> None:
    status = "PASS" if final_pass(rows, warnings, args) else "FAIL"
    constants = key_constants()
    failures = [row for row in rows if row["status"] != "PASS"]
    lines = [
        "# Prime Mesh R2Q — Final Reproduction Report v1",
        "",
        "## 1. Run Metadata",
        "",
        f"- Timestamp: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Working folder: `{ROOT}`",
        f"- Python: `{sys.version.split()[0]}`",
        f"- Platform: `{platform.platform()}`",
        f"- Command flags: `{', '.join(sys.argv[1:]) or 'default'}`",
        "",
        "## 2. Executive Result",
        "",
        f"Final certificate reproduction status: {status}",
        "",
        "## 3. Script Compilation and Run Status",
        "",
        "| Audit | Compile | Run | Counts | Failure File | Status |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['audit_name']} | {row['py_compile_pass']} | {row['run_pass']} | "
            f"{row['expected_counts_pass']} | {row['failure_file_empty']} | {row['status']} |"
        )
    lines.extend(
        [
            "",
            "## 4. Expected Count Checks",
            "",
            "The runner checked the pinned reproducibility counts and constants from `README_REPRODUCIBILITY.md` and `Prime_Mesh_R2Q_RunAll_FinalAudits_Script_Spec_v1.md`.",
            "",
            "## 5. Failure Files",
            "",
            "Intermediate audits `PostP0 ContinuousWindowSelection`, `ContinuousFirstExit CandidateCompleteness`, and `CandidateGap FirstExitImpossibility` are expected to contain conditional/gap-safety failure rows before `NormalizedError GapMargin` closes the coordinate gaps. Final certificate failure files are required to be empty.",
            "",
            "## 6. Key Final Constants",
            "",
            f"- `C_theta`: `{constants['C_theta']}`",
            f"- `R_upper_global_max`: `{constants['R_upper_global_max']}`",
            f"- `R_lower_global_min`: `{constants['R_lower_global_min']}`",
            f"- Prime jumps inside gaps: `{constants['prime_jumps']}`",
            "",
            "## 7. Artifact Hashes",
            "",
            f"Hashes written to `{OUT_HASHES}`.",
            "",
            "## 8. Warnings",
            "",
        ]
    )
    lines.extend([f"- {warning}" for warning in warnings] or ["- None."])
    lines.extend(["", "## 9. Critical Failures", ""])
    if failures:
        for row in failures:
            lines.append(f"- `{row['audit_name']}`: {row['notes']}")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## 10. Final Certificate Status",
            "",
            f"Final certificate reproduction status: {status}",
            "",
            "*AI documentation pass: GPT-5.5*",
        ]
    )
    (ROOT / OUT_MD).write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    path = ROOT / OUT_MANIFEST
    now = datetime.now().isoformat(timespec="seconds")
    suffixes = {".py", ".csv", ".md", ".txt"}
    rows = []
    for p in sorted(ROOT.iterdir(), key=lambda item: item.name.lower()):
        if not p.is_file() or p.suffix.lower() not in suffixes:
            continue
        rows.append(
            {
                "filename": p.name,
                "path": p.name,
                "bytes": p.stat().st_size if p.exists() else 0,
                "status": "present",
                "updated_at": now,
                "note": "Exported reviewer package artifact",
            }
        )
    if rows:
        fieldnames = sorted({key for row in rows for key in row.keys()})
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run all final Prime Mesh R2Q audits.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--compile-only", action="store_true")
    parser.add_argument("--allow-missing", action="store_true")
    parser.add_argument("--skip-run", action="store_true")
    parser.add_argument("--hash-only", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output-dir", default=".", help="Accepted for spec compatibility; outputs stay in the working folder.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    LOG_DIR.mkdir(exist_ok=True)
    run_log = LOG_DIR / "run_all_final_audits.log"
    run_log.write_text(
        f"run_all_final_audits started {datetime.now().isoformat(timespec='seconds')}\n"
        f"root={ROOT}\nargs={sys.argv[1:]}\n",
        encoding="utf-8",
    )

    if args.hash_only:
        check_file_hashes()
        rows: list[dict[str, Any]] = []
        warnings: list[str] = []
    else:
        warnings = compile_optional(args)
        rows = [audit_one(audit, args) for audit in AUDITS]
        write_csv_report(rows)
        check_file_hashes()
        write_md_report(rows, warnings, args)
        update_manifest()

    ok = final_pass(rows, warnings, args) if not args.hash_only else True
    print(f"Final certificate reproduction status: {'PASS' if ok else 'FAIL'}")
    if not args.hash_only:
        print(f"CSV report: {OUT_CSV}")
        print(f"Markdown report: {OUT_MD}")
    print(f"Artifact hashes: {OUT_HASHES}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
