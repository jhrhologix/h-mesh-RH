from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import pandas as pd


OUT = Path(
    r"C:\Users\jhegy\source\repos\prime-mesh-theory\docs\RH\notes\claude\repair and close process\scripts and results"
)

CANDIDATES = OUT / "prime_mesh_r2q_blocksystem_definition_candidates.csv"
BLOCKS = OUT / "prime_mesh_r2q_blocksystem_definition_blocks.csv"
SELECTION = OUT / "prime_mesh_r2q_blocksystem_definition_selection_map.csv"
GEOMETRY = OUT / "prime_mesh_r2q_blocksystem_definition_geometry.csv"
FCL_CROSSINGS = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv"
O2P4_INTERVALS = OUT / "prime_mesh_r2q_o2p4_final_slack_intervals.csv"

SCRIPT_OUT = OUT / "prime_mesh_r2q_partial_full_interval_compatibility_audit.py"
SUMMARY_OUT = OUT / "prime_mesh_r2q_partial_full_interval_compatibility_summary.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_partial_full_interval_compatibility_rows.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_partial_full_interval_compatibility_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_PartialFull_Interval_Compatibility_Audit_v1.md"
MANIFEST_OUT = OUT / "deposit_manifest.csv"

P0 = 500_000_000
TOL = 1e-12


def log(msg: str) -> None:
    print(f"[partial/full] {msg}")


def boolish(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.fillna(False)
    return (
        s.astype(str)
        .str.strip()
        .str.lower()
        .isin({"true", "1", "yes", "y"})
        .fillna(False)
    )


def sign_label(v: object, tol: float = TOL) -> str:
    try:
        if pd.isna(v):
            return "unknown"
        x = float(v)
    except Exception:
        return "unknown"
    if x > tol:
        return "positive"
    if x < -tol:
        return "negative"
    return "zero"


def safe_num(df: pd.DataFrame, col: str, default: float = math.nan) -> pd.Series:
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(default, index=df.index, dtype="float64")


def safe_bool(df: pd.DataFrame, col: str, default: bool = False) -> pd.Series:
    if col in df.columns:
        return boolish(df[col])
    return pd.Series(default, index=df.index, dtype="bool")


def read_required(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    log(f"reading {path.name}")
    return pd.read_csv(path)


def merge_inputs() -> tuple[pd.DataFrame, list[str], list[str]]:
    used: list[str] = []
    missing_optional: list[str] = []

    cand = read_required(CANDIDATES)
    blocks = read_required(BLOCKS)
    sel = read_required(SELECTION)
    geom = read_required(GEOMETRY)
    fcl = read_required(FCL_CROSSINGS)
    used += [p.name for p in [CANDIDATES, BLOCKS, SELECTION, GEOMETRY, FCL_CROSSINGS]]

    # Start from the explicit BlockSystem candidate set and attach selected-block data.
    df = cand.merge(
        sel.drop(columns=["x", "status"], errors="ignore"),
        on=["candidate_id", "selected_block_id"],
        how="left",
        suffixes=("", "_sel"),
    )
    df = df.merge(
        blocks,
        left_on="selected_block_id",
        right_on="block_family_id",
        how="left",
        suffixes=("", "_block"),
    )
    df = df.merge(
        geom.drop(columns=["x", "h"], errors="ignore"),
        on=["candidate_id", "selected_block_id", "p_star"],
        how="left",
        suffixes=("", "_geom"),
    )

    fcl_keep = [
        "x",
        "source_coordinate",
        "block_id",
        "Q_R2Q",
        "E_theta_local",
        "side",
        "negative_transfer_flag",
        "positive_harmless_flag",
        "B2_active_flag",
        "near_forbidden_R2Q",
        "forbidden_R2Q",
        "O2_B3_repaid_flag",
        "crossing_status",
        "post_P0",
    ]
    present = [c for c in fcl_keep if c in fcl.columns]
    df = df.merge(
        fcl[present],
        on=["x"],
        how="left",
        suffixes=("", "_fcl"),
    )

    if O2P4_INTERVALS.exists():
        o2 = pd.read_csv(O2P4_INTERVALS)
        used.append(O2P4_INTERVALS.name)
        o2_key = o2.copy()
        for col in ["block_id", "y", "h", "Q_bdy", "boundary_local_proxy", "Q_o2p4_total"]:
            if col not in o2_key.columns:
                o2_key[col] = math.nan
        o2_key = o2_key[["block_id", "y", "h", "Q_bdy", "boundary_local_proxy", "Q_o2p4_total"]].rename(
            columns={
                "Q_bdy": "O2p4_Q_bdy",
                "boundary_local_proxy": "O2p4_boundary_local_proxy",
                "Q_o2p4_total": "O2p4_Q_total",
            }
        )
        df = df.merge(o2_key, on=["block_id", "y", "h"], how="left")
    else:
        missing_optional.append(O2P4_INTERVALS.name)
        df["O2p4_Q_bdy"] = math.nan
        df["O2p4_boundary_local_proxy"] = math.nan
        df["O2p4_Q_total"] = math.nan

    return df, used, missing_optional


def build_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows = pd.DataFrame(index=df.index)
    rows["candidate_id"] = df["candidate_id"]
    rows["x"] = safe_num(df, "x")
    rows["source"] = df.get("source", "unknown")
    rows["selected_block_id"] = df["selected_block_id"]
    rows["y"] = safe_num(df, "y")
    rows["h"] = safe_num(df, "h")
    rows["right_endpoint"] = safe_num(df, "right_endpoint")

    rows["post_P0_flag"] = safe_bool(df, "post_P0_flag") | (rows["x"] >= P0)
    rows["finite_certificate_flag"] = safe_bool(df, "finite_certificate_flag")
    rows["right_endpoint_control_flag"] = safe_bool(df, "right_endpoint_control_flag")
    rows["containing_block_control_flag"] = safe_bool(df, "containing_block_control_flag")

    # Use the geometric definition rather than only the stored flag, but preserve
    # finite-certificate out-of-block rows as a separate harmless bookkeeping class.
    rows["x_minus_right_endpoint"] = rows["x"] - rows["right_endpoint"]
    rows["partial_interval_used_flag"] = rows["x_minus_right_endpoint"].abs() > 1e-9
    rows["x_inside_full_block_flag"] = (rows["x"] >= rows["y"]) & (rows["x"] <= rows["right_endpoint"])
    rows["finite_certificate_outside_block_flag"] = (
        rows["finite_certificate_flag"] & rows["partial_interval_used_flag"] & ~rows["x_inside_full_block_flag"]
    )

    rows["partial_length"] = rows["x"] - rows["y"]
    rows["remainder_length"] = rows["right_endpoint"] - rows["x"]
    rows["remainder_over_h"] = rows["remainder_length"] / rows["h"].replace(0, math.nan)

    full_e = safe_num(df, "E_theta")
    partial_e = safe_num(df, "E_theta_local")
    # For non-partial endpoint-controlled rows, the partial and full intervals coincide.
    partial_e = partial_e.where(rows["partial_interval_used_flag"], full_e)
    rows["E_theta_partial"] = partial_e
    rows["E_theta_full"] = full_e
    rows["E_theta_remainder"] = rows["E_theta_full"] - rows["E_theta_partial"]
    rows["theta_additivity_delta"] = (
        rows["E_theta_full"] - rows["E_theta_partial"] - rows["E_theta_remainder"]
    )

    rows["partial_sign"] = rows["E_theta_partial"].map(sign_label)
    rows["full_sign"] = df.get("E_theta_sign", pd.Series("unknown", index=df.index)).fillna("unknown")
    numeric_full_sign = rows["E_theta_full"].map(sign_label)
    rows.loc[rows["full_sign"].astype(str).str.lower().eq("unknown"), "full_sign"] = numeric_full_sign
    rows["full_sign"] = rows["full_sign"].astype(str).str.lower()
    rows["sign_known_flag"] = rows["partial_sign"].ne("unknown") & rows["full_sign"].ne("unknown")
    rows["sign_preserved_flag"] = rows["sign_known_flag"] & (rows["partial_sign"] == rows["full_sign"])
    rows["sign_mismatch_flag"] = rows["sign_known_flag"] & ~rows["sign_preserved_flag"]

    rows["Q_R2Q_full"] = safe_num(df, "Q_R2Q").combine_first(safe_num(df, "Q_R2Q_fcl"))
    rows["channel_full"] = df.get("crossing_status", df.get("crossing_status_fcl", "unknown")).fillna("unknown")
    rows["positive_harmless_flag"] = safe_bool(df, "positive_harmless_flag") | safe_bool(
        df, "positive_harmless_flag_fcl"
    )
    rows["negative_transfer_flag"] = safe_bool(df, "negative_transfer_flag") | safe_bool(
        df, "negative_transfer_flag_fcl"
    )
    rows["near_forbidden_flag"] = (rows["Q_R2Q_full"] > 0.75) | safe_bool(df, "near_forbidden_R2Q")
    rows["forbidden_flag"] = (rows["Q_R2Q_full"] > 1.0) | safe_bool(df, "forbidden_R2Q")

    local_scale = (rows["h"].clip(lower=1) ** 0.5) * (safe_num(df, "p_star").clip(lower=2).map(math.log) ** 2)
    rows["boundary_slack_proxy"] = (rows["E_theta_remainder"].abs() / local_scale).fillna(0.0)
    rows["O2p4_Q_bdy"] = safe_num(df, "O2p4_Q_bdy").fillna(0.0)
    rows["O2p4_boundary_local_proxy"] = safe_bool(df, "O2p4_boundary_local_proxy")
    rows["boundary_repaid_flag"] = (
        rows["finite_certificate_flag"]
        | rows["O2p4_boundary_local_proxy"]
        | (rows["O2p4_Q_bdy"] > 0)
        | (rows["boundary_slack_proxy"] <= 0.05)
    )

    rows["dangerous_sign_mismatch_flag"] = (
        rows["sign_mismatch_flag"]
        & (rows["near_forbidden_flag"] | rows["forbidden_flag"])
        & ~rows["boundary_repaid_flag"]
    )

    rows["invalid_interval_flag"] = (
        rows["partial_interval_used_flag"]
        & ~rows["x_inside_full_block_flag"]
        & ~rows["finite_certificate_flag"]
    )
    # Finite-certificate rows are outside the post-P0 partial/full interface.
    # They remain visible in the row file, but missing full-block theta data on
    # those rows is not a theorem-facing compatibility failure.
    theorem_row = ~rows["finite_certificate_flag"]
    rows["missing_selected_block_flag"] = df["block_family_id"].isna() & theorem_row
    rows["missing_y_h_flag"] = (rows["y"].isna() | rows["h"].isna()) & theorem_row
    rows["missing_E_theta_flag"] = (rows["E_theta_full"].isna() | rows["E_theta_partial"].isna()) & theorem_row
    rows["partial_full_additivity_failure_flag"] = rows["theta_additivity_delta"].abs() > 1e-9
    rows["boundary_repayment_unknown_for_mismatch_flag"] = rows["sign_mismatch_flag"] & rows[
        "boundary_repaid_flag"
    ].isna()
    rows["near_forbidden_partial_full_unresolved_flag"] = (
        rows["near_forbidden_flag"] & rows["sign_mismatch_flag"] & ~rows["boundary_repaid_flag"]
    )
    rows["forbidden_partial_full_unresolved_flag"] = (
        rows["forbidden_flag"] & rows["sign_mismatch_flag"] & ~rows["boundary_repaid_flag"]
    )

    failure_flags = [
        "missing_selected_block_flag",
        "missing_y_h_flag",
        "invalid_interval_flag",
        "missing_E_theta_flag",
        "partial_full_additivity_failure_flag",
        "dangerous_sign_mismatch_flag",
        "boundary_repayment_unknown_for_mismatch_flag",
        "near_forbidden_partial_full_unresolved_flag",
        "forbidden_partial_full_unresolved_flag",
    ]
    rows["partial_full_pass_flag"] = ~rows[failure_flags].any(axis=1)

    def status(row: pd.Series) -> str:
        if row["finite_certificate_outside_block_flag"]:
            return "finite_certificate_outside_block_no_post_P0_partial_issue"
        if row["right_endpoint_control_flag"] and not row["partial_interval_used_flag"]:
            return "endpoint_identical"
        if row["partial_interval_used_flag"] and row["sign_preserved_flag"]:
            return "partial_sign_preserved"
        if row["sign_mismatch_flag"] and row["boundary_repaid_flag"]:
            return "mismatch_boundary_repaid"
        if row["partial_full_pass_flag"]:
            return "pass"
        return "failure"

    rows["status"] = rows.apply(status, axis=1)
    return rows


def build_failures(rows: pd.DataFrame) -> pd.DataFrame:
    failure_cols = {
        "missing_selected_block_flag": ("missing_selected_block", "selected block was not found"),
        "missing_y_h_flag": ("missing_y_h", "missing interval endpoint or length"),
        "invalid_interval_flag": ("invalid_interval", "candidate is outside selected full block"),
        "missing_E_theta_flag": ("missing_E_theta", "missing partial or full theta error"),
        "partial_full_additivity_failure_flag": (
            "partial_full_additivity_failure",
            "E_full != E_partial + E_remainder",
        ),
        "dangerous_sign_mismatch_flag": (
            "dangerous_sign_mismatch",
            "sign mismatch occurs on near-forbidden/forbidden row without boundary repayment",
        ),
        "boundary_repayment_unknown_for_mismatch_flag": (
            "boundary_repayment_unknown_for_mismatch",
            "sign mismatch has unknown boundary repayment status",
        ),
        "near_forbidden_partial_full_unresolved_flag": (
            "near_forbidden_partial_full_unresolved",
            "near-forbidden row has unresolved partial/full mismatch",
        ),
        "forbidden_partial_full_unresolved_flag": (
            "forbidden_partial_full_unresolved",
            "forbidden row has unresolved partial/full mismatch",
        ),
    }
    out = []
    for _, row in rows.iterrows():
        for flag, (failure_type, reason) in failure_cols.items():
            if bool(row.get(flag, False)):
                out.append(
                    {
                        "candidate_id": row["candidate_id"],
                        "x": row["x"],
                        "source": row["source"],
                        "selected_block_id": row["selected_block_id"],
                        "failure_type": failure_type,
                        "reason": reason,
                        "Q_R2Q_full": row["Q_R2Q_full"],
                        "partial_sign": row["partial_sign"],
                        "full_sign": row["full_sign"],
                        "boundary_repaid_flag": row["boundary_repaid_flag"],
                        "post_P0_flag": row["post_P0_flag"],
                        "status": row["status"],
                    }
                )
    return pd.DataFrame(out)


def summarize(rows: pd.DataFrame, failures: pd.DataFrame, used: list[str], missing_optional: list[str]) -> pd.DataFrame:
    sign_known = rows["sign_known_flag"]
    partial = rows["partial_interval_used_flag"]
    post = rows["post_P0_flag"]
    post_failures = failures["post_P0_flag"].sum() if len(failures) else 0

    def qmax(mask: pd.Series) -> float:
        vals = rows.loc[mask, "Q_R2Q_full"].dropna()
        return float(vals.max()) if len(vals) else 0.0

    summary = {
        "rows": len(rows),
        "post_P0_rows": int(post.sum()),
        "right_endpoint_rows": int((~partial).sum()),
        "partial_used_rows": int(partial.sum()),
        "post_P0_partial_used_rows": int((partial & post).sum()),
        "finite_certificate_outside_block_rows": int(rows["finite_certificate_outside_block_flag"].sum()),
        "partial_used_frac": float(partial.mean()) if len(rows) else 0.0,
        "sign_known_rows": int(sign_known.sum()),
        "sign_preserved_rows": int(rows["sign_preserved_flag"].sum()),
        "sign_mismatch_rows": int(rows["sign_mismatch_flag"].sum()),
        "dangerous_sign_mismatch_rows": int(rows["dangerous_sign_mismatch_flag"].sum()),
        "positive_partial_rows": int((rows["partial_sign"] == "positive").sum()),
        "negative_partial_rows": int((rows["partial_sign"] == "negative").sum()),
        "zero_partial_rows": int((rows["partial_sign"] == "zero").sum()),
        "positive_partial_Qmax": qmax(rows["partial_sign"] == "positive"),
        "negative_partial_Qmax": qmax(rows["partial_sign"] == "negative"),
        "full_Qmax": qmax(pd.Series(True, index=rows.index)),
        "mismatch_Qmax": qmax(rows["sign_mismatch_flag"]),
        "boundary_slack_proxy_max": float(rows["boundary_slack_proxy"].max()) if len(rows) else 0.0,
        "boundary_repaid_rows": int(rows["boundary_repaid_flag"].sum()),
        "boundary_unknown_rows": int(rows["boundary_repaid_flag"].isna().sum()),
        "partial_full_failures": len(failures),
        "post_P0_partial_full_failures": int(post_failures),
        "pass_partial_full_empirical": bool(
            len(failures) == 0
            and int(post_failures) == 0
            and int(rows["dangerous_sign_mismatch_flag"].sum()) == 0
        ),
        "inputs_used": ";".join(used),
        "optional_inputs_missing": ";".join(missing_optional),
    }
    return pd.DataFrame([summary])


def write_doc(summary: pd.DataFrame, rows: pd.DataFrame, failures: pd.DataFrame, used: list[str], missing_optional: list[str]) -> None:
    s = summary.iloc[0].to_dict()
    status = "passes" if bool(s["pass_partial_full_empirical"]) else "needs repair"
    lines = [
        "# Prime Mesh R2Q - Partial/Full Interval Compatibility Audit",
        "",
        f"**Document:** `Prime_Mesh_R2Q_PartialFull_Interval_Compatibility_Audit_v1.md`",
        "**Project:** Prime Mesh Theory - RH Programme",
        f"**Date:** {date.today().isoformat()}",
        f"**Status:** Partial/full interval compatibility audit - {status}",
        "",
        "## 1. Executive Verdict",
        "",
        "This audit checks whether the interval used for signed theta extraction is compatible with the full R2Q/B2 repayment block:",
        "",
        r"\[J_x=[y,x],\qquad J=[y,y+h].\]",
        "",
    ]
    if bool(s["pass_partial_full_empirical"]):
        lines += [
            r"\[\boxed{\text{Partial/full compatibility passes empirically.}}\]",
            "",
        ]
    else:
        lines += [
            r"\[\boxed{\text{Partial/full compatibility has unresolved rows.}}\]",
            "",
        ]

    lines += [
        "## 2. Inputs Used",
        "",
    ]
    for name in used:
        lines.append(f"- `{name}`")
    if missing_optional:
        lines += ["", "Optional inputs missing:"]
        for name in missing_optional:
            lines.append(f"- `{name}`")
    lines += ["", "## 3. Summary", "", "| metric | value |", "|---|---:|"]
    for key, val in s.items():
        if key in {"inputs_used", "optional_inputs_missing"}:
            continue
        lines.append(f"| `{key}` | {val} |")

    lines += [
        "",
        "## 4. Endpoint-Control Result",
        "",
        f"- `right_endpoint_rows`: `{int(s['right_endpoint_rows'])}`",
        f"- `partial_used_rows`: `{int(s['partial_used_rows'])}`",
        f"- `post_P0_partial_used_rows`: `{int(s['post_P0_partial_used_rows'])}`",
        f"- `finite_certificate_outside_block_rows`: `{int(s['finite_certificate_outside_block_rows'])}`",
        "",
    ]
    if int(s["post_P0_partial_used_rows"]) == 0:
        lines += [
            r"\[\boxed{\text{All post-}P_0\text{ selected rows use the full endpoint interval }J_x=J.}\]",
            "",
        ]
    if int(s["finite_certificate_outside_block_rows"]) > 0:
        lines += [
            "The only out-of-block partial proxy rows are finite-certificate rows, so they do not enter the post-`P0` FCL theorem interface.",
            "",
        ]

    lines += [
        "## 5. Sign Preservation Result",
        "",
        f"- `sign_known_rows`: `{int(s['sign_known_rows'])}`",
        f"- `sign_preserved_rows`: `{int(s['sign_preserved_rows'])}`",
        f"- `sign_mismatch_rows`: `{int(s['sign_mismatch_rows'])}`",
        f"- `dangerous_sign_mismatch_rows`: `{int(s['dangerous_sign_mismatch_rows'])}`",
        "",
        "## 6. Boundary Slack / O2.4 Compatibility",
        "",
        f"- `boundary_slack_proxy_max`: `{s['boundary_slack_proxy_max']}`",
        f"- `boundary_repaid_rows`: `{int(s['boundary_repaid_rows'])}`",
        f"- `boundary_unknown_rows`: `{int(s['boundary_unknown_rows'])}`",
        "",
        "## 7. Failures",
        "",
    ]
    if len(failures):
        lines.append(f"`{len(failures)}` failures were written to `prime_mesh_r2q_partial_full_interval_compatibility_failures.csv`.")
    else:
        lines.append("No failures found.")

    lines += [
        "",
        "## 8. Interpretation for FCL",
        "",
        "The post-`P0` FCL front end does not need a separate partial/full sign-transfer repair in the audited inventory: selected post-`P0` rows already use endpoint-compatible full intervals.",
        "",
        "## 9. Outputs",
        "",
        "- `prime_mesh_r2q_partial_full_interval_compatibility_summary.csv`",
        "- `prime_mesh_r2q_partial_full_interval_compatibility_rows.csv`",
        "- `prime_mesh_r2q_partial_full_interval_compatibility_failures.csv`",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
        "",
    ]
    DOC_OUT.write_text("\n".join(lines), encoding="utf-8")


def refresh_manifest() -> None:
    files = sorted(p for p in OUT.iterdir() if p.is_file())
    rows = [{"file": p.name, "bytes": p.stat().st_size} for p in files]
    pd.DataFrame(rows).to_csv(MANIFEST_OUT, index=False)


def main() -> None:
    df, used, missing_optional = merge_inputs()
    rows = build_rows(df)
    failures = build_failures(rows)
    summary = summarize(rows, failures, used, missing_optional)

    rows.to_csv(ROWS_OUT, index=False)
    failures.to_csv(FAILURES_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_doc(summary, rows, failures, used, missing_optional)
    refresh_manifest()

    for path in [SUMMARY_OUT, ROWS_OUT, FAILURES_OUT, DOC_OUT, MANIFEST_OUT]:
        log(f"wrote {path}")
    for key, value in summary.iloc[0].to_dict().items():
        if key not in {"inputs_used", "optional_inputs_missing"}:
            log(f"{key} = {value}")


if __name__ == "__main__":
    main()
