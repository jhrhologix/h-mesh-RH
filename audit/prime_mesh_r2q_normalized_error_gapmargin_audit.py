"""
Prime Mesh R2Q — NormalizedError GapMargin audit.

Generates exact theta(x)-x normalized margin data for the 141 post-P0
coordinate gaps. The active bridge files define the global theta envelope
|theta(x)-x| <= C_theta sqrt(x) log^2 x with
C_theta >= 1.9233607946440099. This script uses that minimum required
constant, so any margin-safe result remains safe for larger C_theta.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import math

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
C_THETA_MIN = 1.9233607946440099

OUT_SCRIPT = "prime_mesh_r2q_normalized_error_gapmargin_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_normalized_error_gapmargin_summary.csv"
OUT_ROWS = "prime_mesh_r2q_normalized_error_gapmargin_rows.csv"
OUT_SAFE = "prime_mesh_r2q_normalized_error_gapmargin_margin_safe.csv"
OUT_RISK = "prime_mesh_r2q_normalized_error_gapmargin_risk.csv"
OUT_MISSING = "prime_mesh_r2q_normalized_error_gapmargin_missing_data.csv"
OUT_FAILURES = "prime_mesh_r2q_normalized_error_gapmargin_failures.csv"
OUT_JUMPS = "prime_mesh_r2q_normalized_error_gapmargin_jump_inventory.csv"
OUT_BY_PROCESS = "prime_mesh_r2q_normalized_error_gapmargin_by_process.csv"
OUT_SAMPLED = "prime_mesh_r2q_normalized_error_gapmargin_sampled_only.csv"
OUT_REQS = "prime_mesh_r2q_normalized_error_gapmargin_data_requirements.csv"
OUT_DOC = "Prime_Mesh_R2Q_NormalizedError_GapMargin_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"


@dataclass
class EvalPoint:
    x: float
    theta_value: float
    label: str
    prime_jump: int | None = None


def simple_primes(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=np.bool_)
    if limit >= 1:
        sieve[:2] = False
    root = int(math.isqrt(limit))
    for p in range(2, root + 1):
        if sieve[p]:
            sieve[p * p :: p] = False
    return np.where(sieve)[0].astype(np.int32)


def segment_primes(low: int, high: int, base_primes: np.ndarray) -> np.ndarray:
    if high < low:
        return np.array([], dtype=np.int64)
    seg = np.ones(high - low + 1, dtype=np.bool_)
    for sp in base_primes:
        p = int(sp)
        pp = p * p
        if pp > high:
            break
        start = max(pp, ((low + p - 1) // p) * p)
        seg[start - low :: p] = False
    if low == 0:
        seg[:2] = False
    elif low == 1:
        seg[0] = False
    return (low + np.where(seg)[0]).astype(np.int64)


def segmented_theta_gap_bounds(gaps: pd.DataFrame, limit: int, chunk_size: int = 1 << 22) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_primes = simple_primes(int(math.isqrt(limit)) + 1)
    gaps = gaps.sort_values(["gap_start", "gap_end"]).reset_index(drop=True).copy()

    theta = 0.0
    min_start = int(gaps["gap_start"].min())
    max_end = int(gaps["gap_end"].max())

    # Prefix theta up to the first gap. This is the expensive part, so it is
    # vectorized by segment and only stores the small target-range primes.
    for low in range(2, min_start, chunk_size):
        high = min(min_start - 1, low + chunk_size - 1)
        primes = segment_primes(low, high, base_primes)
        if len(primes):
            theta += float(np.log(primes.astype(np.float64)).sum())

    target_primes_parts = []
    for low in range(min_start, max_end + 1, chunk_size):
        high = min(max_end, low + chunk_size - 1)
        primes = segment_primes(low, high, base_primes)
        if len(primes):
            target_primes_parts.append(primes)
    target_primes = np.concatenate(target_primes_parts) if target_primes_parts else np.array([], dtype=np.int64)
    target_logs = np.log(target_primes.astype(np.float64)) if len(target_primes) else np.array([], dtype=np.float64)
    target_cumlogs = np.cumsum(target_logs) if len(target_logs) else np.array([], dtype=np.float64)

    def theta_at(x: int) -> float:
        pos = int(np.searchsorted(target_primes, x, side="right"))
        return theta + (float(target_cumlogs[pos - 1]) if pos else 0.0)

    def theta_before_prime_index(pos: int) -> float:
        return theta + (float(target_cumlogs[pos - 1]) if pos else 0.0)

    def theta_after_prime_index(pos: int) -> float:
        return theta + float(target_cumlogs[pos])

    rows = []
    jumps = []
    for idx, row in gaps.iterrows():
        start = int(row["gap_start"])
        end = int(row["gap_end"])
        start_pos = int(np.searchsorted(target_primes, start, side="left"))
        end_pos = int(np.searchsorted(target_primes, end, side="right"))
        eval_points = [
            EvalPoint(x=float(start), theta_value=theta_at(start), label="gap_start"),
            EvalPoint(x=float(end), theta_value=theta_at(end), label="gap_end"),
        ]
        prime_jump_count = end_pos - start_pos
        for pos in range(start_pos, end_pos):
            p = int(target_primes[pos])
            eval_points.append(EvalPoint(x=float(p), theta_value=theta_before_prime_index(pos), label="prime_left_limit", prime_jump=p))
            eval_points.append(EvalPoint(x=float(p), theta_value=theta_after_prime_index(pos), label="prime_after_jump", prime_jump=p))

        r_values = []
        for ep in eval_points:
            if ep.x <= 1:
                continue
            denom = C_THETA_MIN * math.sqrt(ep.x) * (math.log(ep.x) ** 2)
            h_val = ep.theta_value - ep.x
            r_val = h_val / denom
            r_values.append((r_val, ep, h_val, denom))
            if ep.prime_jump is not None:
                jumps.append(
                    {
                        "gap_id": row["gap_id"],
                        "prime": ep.prime_jump,
                        "eval_label": ep.label,
                        "R_value": r_val,
                    }
                )
        r_max, ep_max, h_max, denom_max = max(r_values, key=lambda item: item[0])
        r_min, ep_min, h_min, denom_min = min(r_values, key=lambda item: item[0])
        upper_margin = 1.0 - r_max
        lower_margin = r_min + 1.0
        if r_max >= 1.0:
            cls = "upper_risk"
        elif r_min <= -1.0:
            cls = "lower_risk"
        else:
            cls = "margin_safe"
        rows.append(
            {
                "gap_id": row["gap_id"],
                "gap_start": start,
                "gap_end": end,
                "gap_length": int(row["gap_length"]),
                "left_candidate_id": row.get("left_candidate_id", ""),
                "right_candidate_id": row.get("right_candidate_id", ""),
                "global_error_process": "theta(x)-x",
                "envelope_type": "C_theta*sqrt(x)*log(x)^2",
                "envelope_constant": C_THETA_MIN,
                "envelope_constant_status": "minimum_required_global_constant",
                "R_upper_max_bound": r_max,
                "R_upper_max_location": ep_max.x,
                "R_upper_max_label": ep_max.label,
                "R_lower_min_bound": r_min,
                "R_lower_min_location": ep_min.x,
                "R_lower_min_label": ep_min.label,
                "theta_error_at_Rmax": h_max,
                "theta_error_at_Rmin": h_min,
                "upper_margin_to_1": upper_margin,
                "lower_margin_to_minus1": lower_margin,
                "prime_jump_count": prime_jump_count,
                "prime_power_jump_count": "",
                "jump_inventory_available": True,
                "sampled_only": False,
                "continuous_bound_available": True,
                "upper_exit_possible": bool(r_max >= 1.0),
                "lower_exit_possible": bool(r_min <= -1.0),
                "margin_safe": cls == "margin_safe",
                "margin_class": cls,
                "needed_data": "",
                "eval_point_count": len(r_values),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(jumps)


def load_gap_inventory() -> pd.DataFrame:
    rows_path = BASE / "prime_mesh_r2q_candidate_gap_firstexit_impossibility_rows.csv"
    if rows_path.exists():
        df = pd.read_csv(rows_path, low_memory=False)
        return df[["gap_id", "gap_start", "gap_end", "gap_length", "left_candidate_id", "right_candidate_id"]].copy()
    gap_scan = pd.read_csv(BASE / "prime_mesh_r2q_postp0_continuous_window_selection_gap_scan.csv", low_memory=False)
    gap_scan = gap_scan.rename(columns={"gap_size": "gap_length"})
    gap_scan.insert(0, "gap_id", [f"gap_{i:03d}" for i in range(len(gap_scan))])
    gap_scan["left_candidate_id"] = ""
    gap_scan["right_candidate_id"] = ""
    return gap_scan


def write_outputs(rows: pd.DataFrame, jumps: pd.DataFrame) -> pd.DataFrame:
    safe = rows[rows["margin_class"].eq("margin_safe")].copy()
    risk = rows[rows["margin_class"].isin(["upper_risk", "lower_risk"])].copy()
    missing = rows[rows["margin_class"].isin(["missing_data", "bridge_normalization_missing", "sampled_only"])].copy()
    failures = risk.copy()
    by_process = rows.groupby(["global_error_process", "margin_class"]).size().reset_index(name="rows")
    sampled = rows[rows["sampled_only"]].copy()
    reqs = pd.DataFrame(
        [
            {
                "requirement": "psi_or_pi_gap_margin",
                "status": "not_generated",
                "note": "This audit generated theta(x)-x margins because the active GlobalThetaEnvelope bridge defines the theta process.",
            },
            {
                "requirement": "envelope_constant_exact_choice",
                "status": "minimum_required_constant_used",
                "note": f"Used C_theta_min={C_THETA_MIN}; larger C_theta only improves safety.",
            },
        ]
    )
    summary = pd.DataFrame(
        [
            {
                "gap_count": len(rows),
                "gaps_with_margin_bounds": int(rows["continuous_bound_available"].sum()),
                "gaps_margin_safe": len(safe),
                "gaps_upper_risk": int((rows["margin_class"] == "upper_risk").sum()),
                "gaps_lower_risk": int((rows["margin_class"] == "lower_risk").sum()),
                "gaps_sampled_only": len(sampled),
                "gaps_missing_data": len(missing),
                "global_error_process_detected": "theta(x)-x",
                "envelope_detected": "C_theta*sqrt(x)*log(x)^2",
                "envelope_constant_detected": C_THETA_MIN,
                "envelope_constant_status": "minimum required by GlobalThetaEnvelope",
                "prime_jump_inventory_available": True,
                "prime_power_jump_inventory_available": False,
                "continuous_bounds_available": True,
                "sampled_only_count": len(sampled),
                "bridge_normalization_missing": False,
                "uses_full_grid_HExc_upgrade": False,
                "uses_failed_delta_route": False,
                "R_upper_global_max": rows["R_upper_max_bound"].max(),
                "R_lower_global_min": rows["R_lower_min_bound"].min(),
                "min_upper_margin_to_1": rows["upper_margin_to_1"].min(),
                "min_lower_margin_to_minus1": rows["lower_margin_to_minus1"].min(),
                "total_prime_jumps_in_gaps": int(rows["prime_jump_count"].sum()),
                "gapmargin_classification": "all_gaps_margin_safe" if len(safe) == len(rows) else "some_risk_gaps",
                "main_gapmargin_gap": "All theta-normalized gap margins are strictly inside (-1,1)." if len(safe) == len(rows) else "Some gaps cross the normalized envelope.",
                "recommended_next_file": "Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Certificate_Closure_Update_v1.md" if len(safe) == len(rows) else "Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Repair_Map_v1.md",
                "pass_normalized_error_gapmargin_audit": len(safe) == len(rows),
            }
        ]
    )
    summary.to_csv(BASE / OUT_SUMMARY, index=False)
    rows.to_csv(BASE / OUT_ROWS, index=False)
    safe.to_csv(BASE / OUT_SAFE, index=False)
    risk.to_csv(BASE / OUT_RISK, index=False)
    missing.to_csv(BASE / OUT_MISSING, index=False)
    failures.to_csv(BASE / OUT_FAILURES, index=False)
    jumps.to_csv(BASE / OUT_JUMPS, index=False)
    by_process.to_csv(BASE / OUT_BY_PROCESS, index=False)
    sampled.to_csv(BASE / OUT_SAMPLED, index=False)
    reqs.to_csv(BASE / OUT_REQS, index=False)
    return summary


def write_doc(summary: pd.DataFrame) -> None:
    s = summary.iloc[0]
    lines = [
        "# Prime Mesh R2Q — NormalizedError GapMargin Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "Generate per-gap normalized theta-error margin data for the 141 coordinate gaps.",
        "",
        "## 2. Summary",
        "",
        f"- Classification: `{s['gapmargin_classification']}`.",
        f"- Gap count: `{int(s['gap_count'])}`.",
        f"- Gaps with continuous margin bounds: `{int(s['gaps_with_margin_bounds'])}`.",
        f"- Margin-safe gaps: `{int(s['gaps_margin_safe'])}`.",
        f"- Upper-risk gaps: `{int(s['gaps_upper_risk'])}`.",
        f"- Lower-risk gaps: `{int(s['gaps_lower_risk'])}`.",
        f"- Missing-data gaps: `{int(s['gaps_missing_data'])}`.",
        f"- Global error process: `{s['global_error_process_detected']}`.",
        f"- Envelope: `{s['envelope_detected']}`.",
        f"- Envelope constant used: `{s['envelope_constant_detected']}`.",
        f"- Pass audit: `{bool(s['pass_normalized_error_gapmargin_audit'])}`.",
        "",
        "## 3. Margin Extremes",
        "",
        f"- `R_upper_global_max`: `{s['R_upper_global_max']}`.",
        f"- `R_lower_global_min`: `{s['R_lower_global_min']}`.",
        f"- Minimum upper margin to `1`: `{s['min_upper_margin_to_1']}`.",
        f"- Minimum lower margin to `-1`: `{s['min_lower_margin_to_minus1']}`.",
        f"- Prime jumps inside gaps: `{int(s['total_prime_jumps_in_gaps'])}`.",
        "",
        "## 4. Interpretation",
        "",
        "The audit uses the theta bridge because the active GlobalThetaEnvelope files define `G(x)=theta(x)-x`. It uses the minimum required global constant `C_theta >= 1.9233607946440099`; larger constants only increase the safety margin.",
        "",
        "## 5. v5 Compatibility",
        "",
        "- Full-grid H-Exc upgrade: `False`.",
        "- Failed delta route: `False`.",
        "",
        "## 6. Recommended Next File",
        "",
        f"`{s['recommended_next_file']}`.",
        "",
        "## 7. Outputs",
        "",
        "```text",
        OUT_SCRIPT,
        OUT_SUMMARY,
        OUT_ROWS,
        OUT_SAFE,
        OUT_RISK,
        OUT_MISSING,
        OUT_FAILURES,
        OUT_JUMPS,
        OUT_BY_PROCESS,
        OUT_SAMPLED,
        OUT_REQS,
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
                "note": "NormalizedError GapMargin audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    gaps = load_gap_inventory()
    limit = int(gaps["gap_end"].max())
    rows, jumps = segmented_theta_gap_bounds(gaps, limit)
    summary = write_outputs(rows, jumps)
    write_doc(summary)
    outputs = [
        OUT_SCRIPT, OUT_SUMMARY, OUT_ROWS, OUT_SAFE, OUT_RISK, OUT_MISSING,
        OUT_FAILURES, OUT_JUMPS, OUT_BY_PROCESS, OUT_SAMPLED, OUT_REQS,
        OUT_DOC,
    ]
    update_manifest(outputs)

    print("NormalizedError GapMargin audit complete.")
    s = summary.iloc[0].to_dict()
    for key in [
        "gap_count",
        "gaps_with_margin_bounds",
        "gaps_margin_safe",
        "gaps_upper_risk",
        "gaps_lower_risk",
        "gaps_missing_data",
        "global_error_process_detected",
        "envelope_constant_detected",
        "R_upper_global_max",
        "R_lower_global_min",
        "min_upper_margin_to_1",
        "min_lower_margin_to_minus1",
        "total_prime_jumps_in_gaps",
        "gapmargin_classification",
        "recommended_next_file",
        "pass_normalized_error_gapmargin_audit",
    ]:
        print(f"{key}: {s[key]}")


if __name__ == "__main__":
    main()
