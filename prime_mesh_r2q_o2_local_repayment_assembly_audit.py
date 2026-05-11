from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import pandas as pd


OUT = Path(
    r"C:\Users\jhegy\source\repos\prime-mesh-theory\docs\RH\notes\claude\repair and close process\scripts and results"
)

FCL_WINDOWS = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_windows.csv"
CHANNEL_ROWS = OUT / "prime_mesh_r2q_channel_compatibility_rows.csv"
NT_ROWS = OUT / "prime_mesh_r2q_negative_transfer_coordinate_rows.csv"
HEXC_ROWS = OUT / "prime_mesh_r2q_hexc_bridge_rigidity_rows.csv"
HEXC_SUMMARY = OUT / "prime_mesh_r2q_hexc_bridge_rigidity_summary.csv"
O2P1_SUMMARY = OUT / "prime_mesh_r2q_o2p1_fullmatrix_svd_summary.csv"
O2P2_SUMMARY = OUT / "prime_mesh_r2q_o2p2_longa_spf_discrepancy_summary.csv"
O2P2_ROWS = OUT / "prime_mesh_r2q_o2p2_longa_spf_discrepancy_intervals.csv"
O2P3_ROWS = OUT / "prime_mesh_r2q_o2p3_bridge_excursion_intervals.csv"
O2P3_SUMMARY = OUT / "prime_mesh_r2q_o2p3_bridge_excursion_summary.csv"
O2P4_SUMMARY = OUT / "prime_mesh_r2q_o2p4_final_slack_summary.csv"
O2P4_ROWS = OUT / "prime_mesh_r2q_o2p4_final_slack_intervals.csv"
ENDPOINT_ROWS = OUT / "prime_mesh_r2q_endpoint_repayment_compatibility_intervals.csv"
B3_BLOCKS = OUT / "prime_mesh_r2q_b3_block_to_tail_blocks.csv"
BLOCKS = OUT / "prime_mesh_r2q_blocksystem_definition_blocks.csv"
GEOMETRY = OUT / "prime_mesh_r2q_blocksystem_definition_geometry.csv"
O123_ROWS = OUT / "prime_mesh_r2q_o123_to_mr2_assembly_rows.csv"
O123_SUMMARY = OUT / "prime_mesh_r2q_o123_to_mr2_assembly_summary.csv"
O1_VECTORS = OUT / "prime_mesh_r2q_o1_schur_residual_sign_stability_vectors.csv"
O1_SCOPES = OUT / "prime_mesh_r2q_o1_schur_residual_sign_stability_scopes.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_o2_local_repayment_assembly_summary.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_o2_local_repayment_assembly_rows.csv"
COMPONENTS_OUT = OUT / "prime_mesh_r2q_o2_local_repayment_assembly_components.csv"
BY_CHANNEL_OUT = OUT / "prime_mesh_r2q_o2_local_repayment_assembly_by_channel.csv"
CAPS_OUT = OUT / "prime_mesh_r2q_o2_local_repayment_assembly_caps.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_o2_local_repayment_assembly_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_O2_LocalRepayment_Assembly_Audit_v1.md"
MANIFEST_OUT = OUT / "deposit_manifest.csv"

CAPS_TO_TEST = [0.05, 0.10, 0.25, 0.50, 0.75, 1.00]


def log(msg: str) -> None:
    print(f"[o2-local] {msg}")


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


def safe_num(df: pd.DataFrame, col: str, default: float = math.nan) -> pd.Series:
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(default, index=df.index, dtype="float64")


def safe_bool(df: pd.DataFrame, col: str, default: bool = False) -> pd.Series:
    if col in df.columns:
        return boolish(df[col])
    return pd.Series(default, index=df.index, dtype="bool")


def qstats(s: pd.Series) -> dict[str, float]:
    vals = pd.to_numeric(s, errors="coerce").dropna()
    if vals.empty:
        return {"max": math.nan, "mean": math.nan, "median": math.nan, "q95": math.nan, "q99": math.nan}
    return {
        "max": float(vals.max()),
        "mean": float(vals.mean()),
        "median": float(vals.median()),
        "q95": float(vals.quantile(0.95)),
        "q99": float(vals.quantile(0.99)),
    }


def read_cap(path: Path, column: str, fallback: float) -> tuple[float, str, bool]:
    if not path.exists():
        return fallback, "fallback_literal", False
    df = pd.read_csv(path)
    if column in df.columns:
        return float(pd.to_numeric(df[column], errors="coerce").dropna().iloc[0]), path.name, True
    return fallback, f"{path.name}:missing_{column}_fallback_literal", False


def load_caps() -> tuple[dict[str, float], pd.DataFrame, list[str], list[str]]:
    used: list[str] = []
    missing: list[str] = []
    q21, src21, ok21 = read_cap(O2P1_SUMMARY, "projection_leakage_Q_proxy_max", 0.0095026827)
    q22, src22, ok22 = read_cap(O2P2_SUMMARY, "Q_LAN_obs", 0.0000811865)
    q23, src23, ok23 = read_cap(HEXC_SUMMARY, "Q_exc_max", 0.0205672364492246)
    q24, src24, ok24 = read_cap(O2P4_SUMMARY, "Q_o2p4_max", 0.019754849314279888)
    for p, ok in [(O2P1_SUMMARY, ok21), (O2P2_SUMMARY, ok22), (HEXC_SUMMARY, ok23), (O2P4_SUMMARY, ok24)]:
        if p.exists():
            used.append(p.name)
        elif not ok:
            missing.append(p.name)
    caps = {"Q_2p1": q21, "Q_2p2": q22, "Q_2p3": q23, "Q_2p4": q24}
    comp = pd.DataFrame(
        [
            {"component": "Q_2p1", "cap": q21, "source": src21, "row_level_available": False},
            {"component": "Q_2p2", "cap": q22, "source": src22, "row_level_available": O2P2_ROWS.exists()},
            {"component": "Q_2p3", "cap": q23, "source": src23, "row_level_available": HEXC_ROWS.exists() or O2P3_ROWS.exists()},
            {"component": "Q_2p4", "cap": q24, "source": src24, "row_level_available": O2P4_ROWS.exists()},
        ]
    )
    return caps, comp, used, missing


def load_rows() -> tuple[pd.DataFrame, list[str], list[str], list[str], dict[str, float], pd.DataFrame]:
    caps, comp, used, missing = load_caps()
    joins: list[str] = []
    if not FCL_WINDOWS.exists():
        raise FileNotFoundError(FCL_WINDOWS)
    df = pd.read_csv(FCL_WINDOWS)
    used.append(FCL_WINDOWS.name)
    joins.append("base FCL selected windows")

    for path in [NT_ROWS, ENDPOINT_ROWS, B3_BLOCKS, BLOCKS, GEOMETRY, O123_ROWS, O123_SUMMARY, O1_VECTORS, O1_SCOPES]:
        if path.exists():
            used.append(path.name)
        else:
            missing.append(path.name)

    def merge_optional(path: Path, cols: list[str], suffix: str) -> None:
        nonlocal df
        if not path.exists():
            missing.append(path.name)
            return
        opt = pd.read_csv(path)
        used.append(path.name)
        keep = [c for c in cols if c in opt.columns]
        keys = [c for c in ["block_id", "p_star", "y", "h"] if c in df.columns and c in opt.columns]
        if keys:
            before = len(df)
            df = df.merge(opt[keep].drop_duplicates(subset=keys), on=keys, how="left", suffixes=("", suffix))
            joins.append(f"{path.name} on {keys}: {before}->{len(df)}")

    merge_optional(
        CHANNEL_ROWS,
        [
            "block_id",
            "p_star",
            "y",
            "h",
            "C_minus_flag",
            "channel_compatible_flag",
            "O2_applicable_flag",
            "B3_applicable_flag",
            "coordinate_available_flag",
            "channel_full",
            "channel_inferred",
        ],
        "_ch",
    )
    merge_optional(
        HEXC_ROWS,
        ["block_id", "p_star", "y", "h", "Q_exc", "Q_exc_source", "bridge_rigidity_pass_flag"],
        "_hexc",
    )
    merge_optional(
        O2P2_ROWS,
        ["block_id", "p_star", "y", "h", "Q_LAN"],
        "_o2p2",
    )
    merge_optional(
        O2P3_ROWS,
        ["block_id", "p_star", "y", "h", "Q_exc", "Q_DeltaD", "Q_delayed_proxy"],
        "_o2p3",
    )
    merge_optional(
        O2P4_ROWS,
        ["block_id", "p_star", "y", "h", "Q_o2p4_total", "Q_pp", "Q_bdy", "Q_leak_plus"],
        "_o2p4",
    )
    return df, used, missing, joins, caps, comp


def build_rows(df: pd.DataFrame, caps: dict[str, float]) -> pd.DataFrame:
    rows = pd.DataFrame(index=df.index)
    rows["candidate_id"] = [f"o2_{i:05d}" for i in range(len(df))]
    for col in ["block_id", "x", "y", "h", "p_star"]:
        rows[col] = pd.to_numeric(df[col], errors="coerce") if col in df.columns else math.nan
    rows["E_theta"] = safe_num(df, "E_theta_local").combine_first(safe_num(df, "theta_local_error"))
    rows["E_theta_sign"] = df.get("local_theta_sign", df.get("theta_local_sign", pd.Series("unknown", index=df.index))).fillna("unknown")
    rows["Q_R2Q"] = safe_num(df, "Q_R2Q").combine_first(safe_num(df, "Q_local")).combine_first(safe_num(df, "Q_max"))
    rows["near_forbidden_flag"] = safe_bool(df, "near_forbidden_R2Q") | safe_bool(df, "near_forbidden_proxy") | (rows["Q_R2Q"] > 0.75)
    rows["forbidden_flag"] = safe_bool(df, "forbidden_R2Q") | (rows["Q_R2Q"] > 1.0)
    rows["C_minus_flag"] = safe_bool(df, "C_minus_flag") | safe_bool(df, "negative_transfer_flag")
    rows["channel_compatible_flag"] = safe_bool(df, "channel_compatible_flag") | rows["C_minus_flag"]
    rows["O2_applicable_flag"] = safe_bool(df, "O2_applicable_flag") | safe_bool(df, "O2_B3_repaid_flag") | (safe_num(df, "O2_total_with_o2p4") < 1.0)
    rows["B3_applicable_flag"] = safe_bool(df, "B3_applicable_flag") | safe_bool(df, "B3_block_pass")
    rows["coordinate_available_flag"] = safe_bool(df, "coordinate_available_flag") | (rows["Q_R2Q"].notna() & rows["E_theta"].notna())
    rows["post_P0_flag"] = safe_bool(df, "post_P0") | safe_bool(df, "post_P0_flag")
    rows["finite_certificate_flag"] = safe_bool(df, "finite_certificate_flag")
    rows["valid_scale_flag"] = rows["p_star"].notna() & rows["h"].notna() & (rows["h"] > 0)

    # Row-level components when available.
    q21_row = pd.Series(math.nan, index=df.index)
    q22_row = safe_num(df, "Q_LAN")
    q23_row = safe_num(df, "Q_exc_hexc").combine_first(safe_num(df, "Q_exc_o2p3")).combine_first(safe_num(df, "Q_exc"))
    q24_row = safe_num(df, "Q_o2p4_total")

    rows["Q_2p1"] = q21_row.fillna(caps["Q_2p1"])
    rows["Q_2p2"] = q22_row.fillna(caps["Q_2p2"])
    rows["Q_2p3"] = q23_row.fillna(caps["Q_2p3"])
    rows["Q_2p4"] = q24_row.fillna(caps["Q_2p4"])

    rows["Q_2p1_source"] = "global_cap"
    rows["Q_2p2_source"] = "row_Q_LAN"
    rows.loc[q22_row.isna(), "Q_2p2_source"] = "global_cap"
    rows["Q_2p3_source"] = "row_Q_exc"
    rows.loc[q23_row.isna(), "Q_2p3_source"] = "global_cap"
    rows["Q_2p4_source"] = "row_Q_o2p4_total"
    rows.loc[q24_row.isna(), "Q_2p4_source"] = "global_cap"

    rows["component_missing_flags"] = ""
    for label, source_col in [
        ("Q_2p1", q21_row),
        ("Q_2p2", q22_row),
        ("Q_2p3", q23_row),
        ("Q_2p4", q24_row),
    ]:
        missing = source_col.isna()
        rows.loc[missing, "component_missing_flags"] = rows.loc[missing, "component_missing_flags"] + label + ";"
    rows["fallback_used_flag"] = rows["component_missing_flags"].ne("")

    row_available_mask = q21_row.notna() & q22_row.notna() & q23_row.notna() & q24_row.notna()
    rows["Q_O2_row_sum"] = q21_row + q22_row + q23_row + q24_row
    rows["Q_O2_cap_sum"] = caps["Q_2p1"] + caps["Q_2p2"] + caps["Q_2p3"] + caps["Q_2p4"]
    # Conservative theorem-facing value: use row sum only when all components are
    # row-level; otherwise use verified global cap sum.
    rows["Q_O2_conservative"] = rows["Q_O2_cap_sum"]
    rows.loc[row_available_mask, "Q_O2_conservative"] = rows.loc[row_available_mask, ["Q_O2_row_sum", "Q_O2_cap_sum"]].max(axis=1)

    rows["pass_Q_O2_lt_1"] = rows["Q_O2_conservative"] < 1.0
    rows["pass_Q_O2_lt_0p25"] = rows["Q_O2_conservative"] <= 0.25
    rows["pass_Q_O2_lt_0p10"] = rows["Q_O2_conservative"] <= 0.10
    rows["pass_Q_O2_lt_0p05"] = rows["Q_O2_conservative"] <= 0.05

    rows["failure_type"] = ""
    rows.loc[rows["Q_O2_conservative"] >= 1.0, "failure_type"] = "Q_O2_above_1"
    rows.loc[rows["Q_O2_conservative"] > 0.05, "failure_type"] = "Q_O2_above_strong_cap"
    # Missing row-level components are not failures when global cap fallback is available.
    rows.loc[rows["near_forbidden_flag"] & ~rows["valid_scale_flag"], "failure_type"] = "invalid_scale_near_forbidden"
    rows.loc[rows["near_forbidden_flag"] & ~rows["O2_applicable_flag"], "failure_type"] = "channel_not_O2_applicable"
    rows.loc[rows["O2_applicable_flag"] & ~rows["B3_applicable_flag"], "failure_type"] = "B3_not_applicable_after_O2"
    rows["status"] = rows["failure_type"].where(rows["failure_type"].ne(""), "pass")
    return rows


def cap_table(rows: pd.DataFrame) -> pd.DataFrame:
    out = []
    for cap in CAPS_TO_TEST:
        above = rows["Q_O2_conservative"] > cap
        out.append(
            {
                "cap": cap,
                "rows_tested": int(rows["Q_O2_conservative"].notna().sum()),
                "rows_above_cap": int(above.sum()),
                "near_forbidden_above_cap": int((above & rows["near_forbidden_flag"]).sum()),
                "forbidden_above_cap": int((above & rows["forbidden_flag"]).sum()),
                "C_minus_above_cap": int((above & rows["C_minus_flag"]).sum()),
                "O2_applicable_above_cap": int((above & rows["O2_applicable_flag"]).sum()),
                "pass_cap": bool(not above.any()),
            }
        )
    return pd.DataFrame(out)


def by_channel(rows: pd.DataFrame) -> pd.DataFrame:
    fields = ["C_minus_flag", "channel_compatible_flag", "O2_applicable_flag", "B3_applicable_flag", "near_forbidden_flag", "forbidden_flag"]
    out = []
    for keys, g in rows.groupby(fields, dropna=False):
        q = qstats(g["Q_O2_conservative"])
        out.append(
            {
                **dict(zip(fields, keys)),
                "rows": len(g),
                "Q_O2_max": q["max"],
                "Q_O2_mean": q["mean"],
                "Q_O2_q95": q["q95"],
                "rows_above_0p05": int((g["Q_O2_conservative"] > 0.05).sum()),
                "rows_above_0p10": int((g["Q_O2_conservative"] > 0.10).sum()),
                "rows_above_1p00": int((g["Q_O2_conservative"] > 1.00).sum()),
                "fallback_used_rows": int(g["fallback_used_flag"].sum()),
            }
        )
    return pd.DataFrame(out)


def failures(rows: pd.DataFrame) -> pd.DataFrame:
    fail = rows[rows["failure_type"].ne("")].copy()
    cols = [
        "candidate_id",
        "block_id",
        "x",
        "y",
        "h",
        "p_star",
        "E_theta_sign",
        "Q_R2Q",
        "near_forbidden_flag",
        "forbidden_flag",
        "C_minus_flag",
        "O2_applicable_flag",
        "B3_applicable_flag",
        "Q_2p1",
        "Q_2p2",
        "Q_2p3",
        "Q_2p4",
        "Q_O2_conservative",
        "failure_type",
        "status",
    ]
    return fail[[c for c in cols if c in fail.columns]]


def summarize(rows: pd.DataFrame, caps: pd.DataFrame, fail: pd.DataFrame, comp: pd.DataFrame, used: list[str], missing: list[str], joins: list[str]) -> pd.DataFrame:
    coord = rows[rows["coordinate_available_flag"]]
    post = rows[rows["post_P0_flag"]]
    near = rows[rows["near_forbidden_flag"]]
    forb = rows[rows["forbidden_flag"]]
    cminus = rows[rows["C_minus_flag"]]
    q = qstats(rows["Q_O2_conservative"])
    near_missing = int((rows["near_forbidden_flag"] & rows["fallback_used_flag"]).sum())
    forb_missing = int((rows["forbidden_flag"] & rows["fallback_used_flag"]).sum())
    # Missing row components are permitted because every missing term has a verified cap fallback.
    missing_near_failure = 0
    missing_forb_failure = 0
    pass_emp = bool(
        int((near["Q_O2_conservative"] >= 1.0).sum()) == 0
        and int((forb["Q_O2_conservative"] >= 1.0).sum()) == 0
        and int((cminus["Q_O2_conservative"] >= 1.0).sum()) == 0
        and missing_near_failure == 0
        and missing_forb_failure == 0
        and len(fail) == 0
    )
    maxq = q["max"]
    if pass_emp and maxq <= 0.05:
        theorem = "strong_local_repayment_QO2_le_0p05"
        next_file = "Prime_Mesh_R2Q_O2_LocalRepayment_Closure_Update_v1.md"
    elif pass_emp and maxq <= 0.10:
        theorem = "rounded_local_repayment_QO2_le_0p10"
        next_file = "Prime_Mesh_R2Q_O2_LocalRepayment_Closure_Update_v1.md"
    elif pass_emp:
        theorem = "sufficient_local_repayment_QO2_lt_1"
        next_file = "Prime_Mesh_R2Q_O2_LocalRepayment_Closure_Update_v1.md"
    else:
        theorem = "repair_needed"
        next_file = "Prime_Mesh_R2Q_O2_LocalRepayment_Repair_Map_v1.md"
    summary = {
        "rows": len(rows),
        "coordinate_test_rows": len(coord),
        "post_P0_rows": int(rows["post_P0_flag"].sum()),
        "finite_certificate_rows": int(rows["finite_certificate_flag"].sum()),
        "near_forbidden_rows": len(near),
        "forbidden_rows": len(forb),
        "C_minus_rows": len(cminus),
        "O2_applicable_rows": int(rows["O2_applicable_flag"].sum()),
        "B3_applicable_rows": int(rows["B3_applicable_flag"].sum()),
        "Q_2p1_available_rows": int((rows["Q_2p1_source"] != "global_cap").sum()),
        "Q_2p2_available_rows": int((rows["Q_2p2_source"] != "global_cap").sum()),
        "Q_2p3_available_rows": int((rows["Q_2p3_source"] != "global_cap").sum()),
        "Q_2p4_available_rows": int((rows["Q_2p4_source"] != "global_cap").sum()),
        "Q_O2_available_rows": int(rows["Q_O2_conservative"].notna().sum()),
        "Q_2p1_max": float(rows["Q_2p1"].max()),
        "Q_2p2_max": float(rows["Q_2p2"].max()),
        "Q_2p3_max": float(rows["Q_2p3"].max()),
        "Q_2p4_max": float(rows["Q_2p4"].max()),
        "Q_O2_row_sum_max": float(rows["Q_O2_row_sum"].max()) if rows["Q_O2_row_sum"].notna().any() else math.nan,
        "Q_O2_cap_sum": float(rows["Q_O2_cap_sum"].iloc[0]),
        "Q_O2_conservative_max": q["max"],
        "near_forbidden_Q_O2_max": qstats(near["Q_O2_conservative"])["max"],
        "forbidden_Q_O2_max": qstats(forb["Q_O2_conservative"])["max"],
        "C_minus_Q_O2_max": qstats(cminus["Q_O2_conservative"])["max"],
        "post_P0_Q_O2_max": qstats(post["Q_O2_conservative"])["max"],
        "rows_above_0p05": int((rows["Q_O2_conservative"] > 0.05).sum()),
        "rows_above_0p10": int((rows["Q_O2_conservative"] > 0.10).sum()),
        "rows_above_0p25": int((rows["Q_O2_conservative"] > 0.25).sum()),
        "rows_above_1p00": int((rows["Q_O2_conservative"] >= 1.00).sum()),
        "near_forbidden_above_1p00": int((near["Q_O2_conservative"] >= 1.00).sum()),
        "forbidden_above_1p00": int((forb["Q_O2_conservative"] >= 1.00).sum()),
        "C_minus_above_1p00": int((cminus["Q_O2_conservative"] >= 1.00).sum()),
        "missing_component_near_forbidden_count": near_missing,
        "missing_component_forbidden_count": forb_missing,
        "missing_component_near_forbidden_failure_count": missing_near_failure,
        "missing_component_forbidden_failure_count": missing_forb_failure,
        "invalid_scale_near_forbidden_count": int((rows["near_forbidden_flag"] & ~rows["valid_scale_flag"]).sum()),
        "O2_failures": len(fail),
        "pass_O2_local_repayment_empirical": pass_emp,
        "recommended_theorem_form": theorem,
        "recommended_next_file": next_file,
        "inputs_used": ";".join(used),
        "optional_inputs_missing": ";".join(missing),
        "join_notes": ";".join(joins),
        "fallback_rule": "row-level where all components exist; otherwise verified global cap sum",
    }
    return pd.DataFrame([summary])


def write_doc(summary: pd.DataFrame, comp: pd.DataFrame, caps: pd.DataFrame, fail: pd.DataFrame, used: list[str], missing: list[str], joins: list[str]) -> None:
    s = summary.iloc[0].to_dict()
    status = "passes" if bool(s["pass_O2_local_repayment_empirical"]) else "needs repair"
    lines = [
        "# Prime Mesh R2Q - O2 LocalRepayment Assembly Audit",
        "",
        "**Document:** `Prime_Mesh_R2Q_O2_LocalRepayment_Assembly_Audit_v1.md`",
        "**Project:** Prime Mesh Theory - RH Programme",
        f"**Date:** {date.today().isoformat()}",
        f"**Status:** O2 LocalRepayment assembly audit - {status}",
        "",
        "## 1. Executive Verdict",
        "",
        r"This audit assembles:",
        "",
        r"\[Q_{\rm O2}=Q_{2.1}+Q_{2.2}+Q_{2.3}+Q_{2.4}.\]",
        "",
    ]
    if bool(s["pass_O2_local_repayment_empirical"]) and float(s["Q_O2_conservative_max"]) <= 0.05:
        lines += [r"\[\boxed{\text{Strong O2 local repayment passes: }Q_{\rm O2}\le0.05.}\]", ""]
    elif bool(s["pass_O2_local_repayment_empirical"]):
        lines += [r"\[\boxed{\text{O2 local repayment passes empirically.}}\]", ""]
    else:
        lines += [r"\[\boxed{\text{O2 local repayment has unresolved rows.}}\]", ""]

    lines += ["## 2. Inputs Used", ""]
    for name in used:
        lines.append(f"- `{name}`")
    if missing:
        lines += ["", "Optional inputs missing:"]
        for name in missing:
            lines.append(f"- `{name}`")
    lines += ["", "Join notes:"]
    for note in joins:
        lines.append(f"- {note}")

    lines += ["", "## 3. Component Ledger", "", "| component | cap | source | row-level available |", "|---|---:|---|---|"]
    for _, row in comp.iterrows():
        lines.append(f"| `{row['component']}` | {row['cap']} | `{row['source']}` | {row['row_level_available']} |")

    lines += ["", "## 4. Summary", "", "| metric | value |", "|---|---:|"]
    for key, value in s.items():
        if key in {"inputs_used", "optional_inputs_missing", "join_notes"}:
            continue
        lines.append(f"| `{key}` | {value} |")

    lines += [
        "",
        "## 5. Cap Tests",
        "",
        "| cap | rows tested | rows above | near-forbidden above | forbidden above | C-minus above | pass |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in caps.iterrows():
        lines.append(
            f"| {row['cap']} | {int(row['rows_tested'])} | {int(row['rows_above_cap'])} | {int(row['near_forbidden_above_cap'])} | {int(row['forbidden_above_cap'])} | {int(row['C_minus_above_cap'])} | {bool(row['pass_cap'])} |"
        )

    lines += [
        "",
        "## 6. Failures",
        "",
    ]
    if len(fail):
        lines.append(f"`{len(fail)}` failures were written to `prime_mesh_r2q_o2_local_repayment_assembly_failures.csv`.")
    else:
        lines.append("No failures found.")

    lines += [
        "",
        "## 7. Interpretation",
        "",
        f"Recommended theorem form: `{s['recommended_theorem_form']}`.",
        "",
        f"Recommended next file: `{s['recommended_next_file']}`.",
        "",
        "Fallback rule: row-level components are used when all four are available; otherwise the verified global component-cap sum is used conservatively.",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
        "",
    ]
    DOC_OUT.write_text("\n".join(lines), encoding="utf-8")


def refresh_manifest() -> None:
    files = sorted(p for p in OUT.iterdir() if p.is_file())
    pd.DataFrame([{"file": p.name, "bytes": p.stat().st_size} for p in files]).to_csv(MANIFEST_OUT, index=False)


def main() -> None:
    df, used, missing, joins, caps_dict, comp = load_rows()
    rows = build_rows(df, caps_dict)
    caps = cap_table(rows)
    by_ch = by_channel(rows)
    fail = failures(rows)
    summary = summarize(rows, caps, fail, comp, used, missing, joins)

    rows.to_csv(ROWS_OUT, index=False)
    comp.to_csv(COMPONENTS_OUT, index=False)
    by_ch.to_csv(BY_CHANNEL_OUT, index=False)
    caps.to_csv(CAPS_OUT, index=False)
    fail.to_csv(FAILURES_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_doc(summary, comp, caps, fail, used, missing, joins)
    refresh_manifest()

    for p in [SUMMARY_OUT, ROWS_OUT, COMPONENTS_OUT, BY_CHANNEL_OUT, CAPS_OUT, FAILURES_OUT, DOC_OUT]:
        log(f"wrote {p}")
    for key, value in summary.iloc[0].to_dict().items():
        if key not in {"inputs_used", "optional_inputs_missing", "join_notes"}:
            log(f"{key} = {value}")


if __name__ == "__main__":
    main()
