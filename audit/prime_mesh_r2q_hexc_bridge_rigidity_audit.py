from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import pandas as pd


OUT = Path(
    r"C:\Users\jhegy\source\repos\prime-mesh-theory\docs\RH\notes\claude\repair and close process\scripts and results"
)

FCL_WINDOWS = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_windows.csv"
FCL_CROSSINGS = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv"
BLOCKS = OUT / "prime_mesh_r2q_blocksystem_definition_blocks.csv"
GEOMETRY = OUT / "prime_mesh_r2q_blocksystem_definition_geometry.csv"
NT_ROWS = OUT / "prime_mesh_r2q_negative_transfer_coordinate_rows.csv"
CHANNEL_ROWS = OUT / "prime_mesh_r2q_channel_compatibility_rows.csv"
O2P3_ROWS = OUT / "prime_mesh_r2q_o2p3_bridge_excursion_intervals.csv"
O2P3_SUMMARY = OUT / "prime_mesh_r2q_o2p3_bridge_excursion_summary.csv"
V2_SUMMARY = OUT / "prime_mesh_r2q_hexc_v2_shell_variance_summary.csv"
ENDPOINT_SUMMARY = OUT / "prime_mesh_r2q_endpoint_repayment_compatibility_summary.csv"
ENDPOINT_ROWS = OUT / "prime_mesh_r2q_endpoint_repayment_compatibility_intervals.csv"
B3_BLOCKS = OUT / "prime_mesh_r2q_b3_block_to_tail_blocks.csv"
O123_ROWS = OUT / "prime_mesh_r2q_o123_to_mr2_assembly_rows.csv"
O123_SUMMARY = OUT / "prime_mesh_r2q_o123_to_mr2_assembly_summary.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_hexc_bridge_rigidity_summary.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_hexc_bridge_rigidity_rows.csv"
BY_REGIME_OUT = OUT / "prime_mesh_r2q_hexc_bridge_rigidity_by_regime.csv"
VARIANCE_OUT = OUT / "prime_mesh_r2q_hexc_bridge_rigidity_variance.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_hexc_bridge_rigidity_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_HExc_BridgeRigidity_Audit_v1.md"
MANIFEST_OUT = OUT / "deposit_manifest.csv"

CAPS = [0.025, 0.05, 0.10, 0.25, 1.00]


def log(msg: str) -> None:
    print(f"[hexc-rigidity] {msg}")


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
        return {"min": math.nan, "max": math.nan, "mean": math.nan, "median": math.nan, "q95": math.nan, "q99": math.nan}
    return {
        "min": float(vals.min()),
        "max": float(vals.max()),
        "mean": float(vals.mean()),
        "median": float(vals.median()),
        "q95": float(vals.quantile(0.95)),
        "q99": float(vals.quantile(0.99)),
    }


def load_inputs() -> tuple[pd.DataFrame, list[str], list[str], list[str], dict[str, float | str]]:
    used: list[str] = []
    missing: list[str] = []
    joins: list[str] = []
    meta: dict[str, float | str] = {}

    if not FCL_WINDOWS.exists():
        raise FileNotFoundError(FCL_WINDOWS)
    log(f"reading base {FCL_WINDOWS.name}")
    df = pd.read_csv(FCL_WINDOWS)
    used.append(FCL_WINDOWS.name)
    joins.append("base FCL selected windows used as row inventory")

    optional = [FCL_CROSSINGS, BLOCKS, GEOMETRY, NT_ROWS, B3_BLOCKS, O123_ROWS, O123_SUMMARY]
    for path in optional:
        if path.exists():
            used.append(path.name)
        else:
            missing.append(path.name)

    if CHANNEL_ROWS.exists():
        ch = pd.read_csv(CHANNEL_ROWS)
        used.append(CHANNEL_ROWS.name)
        keep = [
            "block_id",
            "p_star",
            "y",
            "h",
            "channel_full",
            "channel_inferred",
            "negative_transfer_flag",
            "O2_applicable_flag",
            "B3_applicable_flag",
            "coordinate_available_flag",
            "channel_compatible_flag",
        ]
        keep = [c for c in keep if c in ch.columns]
        keys = [c for c in ["block_id", "p_star", "y", "h"] if c in df.columns and c in ch.columns]
        if keys:
            before = len(df)
            df = df.merge(ch[keep].drop_duplicates(subset=keys), on=keys, how="left", suffixes=("", "_ch"))
            joins.append(f"{CHANNEL_ROWS.name} on {keys}: {before}->{len(df)}")
    else:
        missing.append(CHANNEL_ROWS.name)

    if O2P3_ROWS.exists():
        o2 = pd.read_csv(O2P3_ROWS)
        used.append(O2P3_ROWS.name)
        keep = [
            "block_id",
            "p_star",
            "y",
            "h",
            "D_start",
            "D_end",
            "DeltaD",
            "exc_abs",
            "exc_t",
            "Q_exc",
            "Q_DeltaD",
            "Q_delayed_proxy",
        ]
        keep = [c for c in keep if c in o2.columns]
        keys = [c for c in ["block_id", "p_star", "y", "h"] if c in df.columns and c in o2.columns]
        if keys:
            before = len(df)
            df = df.merge(o2[keep].drop_duplicates(subset=keys), on=keys, how="left", suffixes=("", "_o2p3"))
            joins.append(f"{O2P3_ROWS.name} on {keys}: {before}->{len(df)}")
    else:
        missing.append(O2P3_ROWS.name)

    if ENDPOINT_ROWS.exists():
        ep = pd.read_csv(ENDPOINT_ROWS)
        used.append(ENDPOINT_ROWS.name)
        keep = [
            "block_id",
            "p_star",
            "y",
            "h",
            "endpoint_harmful_flag",
            "endpoint_harmful_Q",
            "endpoint_already_counted_flag",
            "endpoint_favorable_flag",
        ]
        keep = [c for c in keep if c in ep.columns]
        keys = [c for c in ["block_id", "p_star", "y", "h"] if c in df.columns and c in ep.columns]
        if keys:
            before = len(df)
            df = df.merge(ep[keep].drop_duplicates(subset=keys), on=keys, how="left", suffixes=("", "_endpoint"))
            joins.append(f"{ENDPOINT_ROWS.name} on {keys}: {before}->{len(df)}")
    else:
        missing.append(ENDPOINT_ROWS.name)

    if V2_SUMMARY.exists():
        v2 = pd.read_csv(V2_SUMMARY).iloc[0].to_dict()
        used.append(V2_SUMMARY.name)
        meta["V2_global"] = float(v2.get("V2_formula", math.nan))
        meta["sqrt_V2_global"] = float(v2.get("sqrt_V2_formula", math.nan))
        meta["variance_source"] = V2_SUMMARY.name
    else:
        missing.append(V2_SUMMARY.name)
        meta["V2_global"] = math.nan
        meta["sqrt_V2_global"] = math.nan
        meta["variance_source"] = "not_available"

    if O2P3_SUMMARY.exists():
        used.append(O2P3_SUMMARY.name)
    else:
        missing.append(O2P3_SUMMARY.name)

    if ENDPOINT_SUMMARY.exists():
        eps = pd.read_csv(ENDPOINT_SUMMARY).iloc[0].to_dict()
        used.append(ENDPOINT_SUMMARY.name)
        meta["endpoint_exclusion_status"] = "available"
        meta["endpoint_exclusion_harmful_count"] = float(eps.get("endpoint_harmful_frac", math.nan)) * float(eps.get("rows", 0))
        meta["endpoint_exclusion_Qmax"] = float(eps.get("Q_DeltaD_harmful_max", math.nan))
    else:
        missing.append(ENDPOINT_SUMMARY.name)
        meta["endpoint_exclusion_status"] = "not_available"
        meta["endpoint_exclusion_harmful_count"] = math.nan
        meta["endpoint_exclusion_Qmax"] = math.nan

    return df, used, missing, joins, meta


def build_rows(df: pd.DataFrame, meta: dict[str, float | str]) -> pd.DataFrame:
    rows = pd.DataFrame(index=df.index)
    rows["candidate_id"] = [f"hexc_{i:05d}" for i in range(len(df))]
    for col in ["block_id", "x", "y", "h", "p_star"]:
        rows[col] = df[col] if col in df.columns else math.nan
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    rows["right_endpoint"] = rows["y"] + rows["h"]
    rows["post_P0_flag"] = safe_bool(df, "post_P0") | safe_bool(df, "post_P0_flag")
    rows["finite_certificate_flag"] = safe_bool(df, "finite_certificate_flag")
    rows["E_theta"] = safe_num(df, "E_theta_local").combine_first(safe_num(df, "theta_local_error"))
    rows["E_theta_sign"] = df.get("local_theta_sign", df.get("theta_local_sign", pd.Series("unknown", index=df.index))).fillna("unknown")
    rows["Q_R2Q"] = safe_num(df, "Q_R2Q").combine_first(safe_num(df, "Q_local")).combine_first(safe_num(df, "Q_max"))
    rows["near_forbidden_flag"] = safe_bool(df, "near_forbidden_R2Q") | safe_bool(df, "near_forbidden_proxy") | (rows["Q_R2Q"] > 0.75)
    rows["forbidden_flag"] = safe_bool(df, "forbidden_R2Q") | (rows["Q_R2Q"] > 1.0)
    rows["channel_inferred"] = df.get("channel_inferred", pd.Series("not_available", index=df.index)).fillna("not_available")
    rows["channel_full"] = df.get("channel_full", df.get("crossing_status", pd.Series("not_available", index=df.index))).fillna("not_available")
    rows["C_minus_flag"] = (
        safe_bool(df, "negative_transfer_flag")
        | rows["channel_inferred"].astype(str).str.lower().str.contains("negative", regex=False)
        | rows["channel_full"].astype(str).str.lower().str.contains("negative", regex=False)
    )
    rows["O2_applicable_flag"] = safe_bool(df, "O2_applicable_flag") | safe_bool(df, "O2_B3_repaid_flag") | (safe_num(df, "O2_total_with_o2p4") < 1.0)
    rows["B3_applicable_flag"] = safe_bool(df, "B3_applicable_flag") | safe_bool(df, "B3_block_pass")
    rows["coordinate_available_flag"] = rows["Q_R2Q"].notna() & rows["E_theta"].notna()

    rows["D_left"] = safe_num(df, "D_start")
    rows["D_right"] = safe_num(df, "D_end")
    rows["D_mid_proxy"] = math.nan
    rows["endpoint_line_left"] = rows["D_left"]
    rows["endpoint_line_right"] = rows["D_right"]
    rows["bridge_excursion_raw"] = safe_num(df, "exc_abs")
    rows["bridge_excursion_absmax"] = safe_num(df, "exc_abs")
    # Prefer exact O2.3 interval Q_exc, then FCL window Q_exc.
    q_o2p3 = safe_num(df, "Q_exc_o2p3")
    q_fcl = safe_num(df, "Q_exc")
    rows["Q_exc"] = q_o2p3.combine_first(q_fcl)
    rows["Q_exc_source"] = "missing"
    rows.loc[q_fcl.notna(), "Q_exc_source"] = "fcl_window"
    rows.loc[q_o2p3.notna(), "Q_exc_source"] = "existing_o2p3"

    rows["V2"] = float(meta.get("V2_global", math.nan))
    rows["sqrt_V2"] = float(meta.get("sqrt_V2_global", math.nan))
    rows["Q_exc_over_sqrt_V2"] = rows["Q_exc"] / rows["sqrt_V2"]
    rows["variance_proxy_source"] = str(meta.get("variance_source", "not_available"))

    rows["endpoint_exclusion_flag"] = safe_bool(df, "endpoint_already_counted_flag") | safe_bool(df, "endpoint_favorable_flag")
    rows["endpoint_exclusion_Q"] = safe_num(df, "endpoint_harmful_Q").fillna(0.0)
    rows["endpoint_exclusion_harmful_flag"] = safe_bool(df, "endpoint_harmful_flag") | (rows["endpoint_exclusion_Q"] > 0)
    if meta.get("endpoint_exclusion_status") == "available":
        rows["endpoint_exclusion_flag"] = rows["endpoint_exclusion_flag"] | rows["Q_exc"].notna()

    rows["valid_scale_flag"] = rows["p_star"].notna() & rows["h"].notna() & (rows["h"] > 0)
    rows["bridge_rigidity_pass_flag"] = rows["Q_exc"].notna() & (rows["Q_exc"] < 1.0) & ~rows["endpoint_exclusion_harmful_flag"] & rows["valid_scale_flag"]

    rows["failure_type"] = ""
    rows.loc[rows["Q_exc"] > 1.0, "failure_type"] = "Q_exc_above_1"
    rows.loc[rows["Q_exc"] > 0.25, "failure_type"] = "Q_exc_above_0p25"
    rows.loc[rows["Q_exc"] > 0.10, "failure_type"] = "Q_exc_above_0p10"
    rows.loc[rows["Q_exc"] > 0.05, "failure_type"] = "Q_exc_above_0p05"
    rows.loc[rows["Q_exc"] > 0.025, "failure_type"] = "Q_exc_above_0p025"
    rows.loc[rows["near_forbidden_flag"] & rows["Q_exc"].isna() & ~rows["finite_certificate_flag"], "failure_type"] = "missing_Q_exc_near_forbidden"
    rows.loc[rows["near_forbidden_flag"] & ~rows["valid_scale_flag"] & ~rows["finite_certificate_flag"], "failure_type"] = "missing_scale_near_forbidden"
    rows.loc[rows["V2"].isna(), "failure_type"] = "variance_proxy_missing"
    rows.loc[rows["Q_exc_over_sqrt_V2"] > 1.25, "failure_type"] = "variance_ratio_unstable"
    rows.loc[rows["endpoint_exclusion_harmful_flag"], "failure_type"] = "endpoint_exclusion_failure"
    rows["status"] = rows["failure_type"].where(rows["failure_type"].ne(""), "pass")
    return rows


def cap_table(rows: pd.DataFrame) -> pd.DataFrame:
    out = []
    for cap in CAPS:
        above = rows["Q_exc"] > cap
        out.append(
            {
                "cap": cap,
                "rows_tested": int(rows["Q_exc"].notna().sum()),
                "rows_above_cap": int(above.sum()),
                "near_forbidden_rows_above_cap": int((above & rows["near_forbidden_flag"]).sum()),
                "C_minus_rows_above_cap": int((above & rows["C_minus_flag"]).sum()),
                "post_P0_rows_above_cap": int((above & rows["post_P0_flag"]).sum()),
                "pass_cap": bool(not above.any()),
            }
        )
    return pd.DataFrame(out)


def by_regime(rows: pd.DataFrame) -> pd.DataFrame:
    fields = [
        "post_P0_flag",
        "finite_certificate_flag",
        "E_theta_sign",
        "near_forbidden_flag",
        "C_minus_flag",
        "O2_applicable_flag",
        "B3_applicable_flag",
        "Q_exc_source",
        "variance_proxy_source",
    ]
    out = []
    for field in fields:
        for value, g in rows.groupby(field, dropna=False):
            q = qstats(g["Q_exc"])
            sv = qstats(g["sqrt_V2"])
            ratio = qstats(g["Q_exc_over_sqrt_V2"])
            out.append(
                {
                    "regime_field": field,
                    "regime_value": value,
                    "rows": len(g),
                    "Q_exc_min": q["min"],
                    "Q_exc_max": q["max"],
                    "Q_exc_mean": q["mean"],
                    "Q_exc_median": q["median"],
                    "Q_exc_q95": q["q95"],
                    "Q_exc_q99": q["q99"],
                    "sqrt_V2_min": sv["min"],
                    "sqrt_V2_max": sv["max"],
                    "Q_exc_over_sqrt_V2_max": ratio["max"],
                    "rows_above_0p025": int((g["Q_exc"] > 0.025).sum()),
                    "rows_above_0p05": int((g["Q_exc"] > 0.05).sum()),
                    "rows_above_0p10": int((g["Q_exc"] > 0.10).sum()),
                    "rows_above_1p00": int((g["Q_exc"] > 1.00).sum()),
                }
            )
    return pd.DataFrame(out)


def variance_table(rows: pd.DataFrame, meta: dict[str, float | str]) -> pd.DataFrame:
    q = qstats(rows["Q_exc"])
    ratio = qstats(rows["Q_exc_over_sqrt_V2"])
    return pd.DataFrame(
        [
            {
                "V2_available_rows": int(rows["V2"].notna().sum()),
                "V2_global": meta.get("V2_global", math.nan),
                "sqrt_V2_global": meta.get("sqrt_V2_global", math.nan),
                "sqrt_V2_min": float(rows["sqrt_V2"].min()) if rows["sqrt_V2"].notna().any() else math.nan,
                "sqrt_V2_max": float(rows["sqrt_V2"].max()) if rows["sqrt_V2"].notna().any() else math.nan,
                "sqrt_V2_mean": float(rows["sqrt_V2"].mean()) if rows["sqrt_V2"].notna().any() else math.nan,
                "Q_exc_max": q["max"],
                "Q_exc_over_sqrt_V2_max": ratio["max"],
                "Q_exc_over_sqrt_V2_mean": ratio["mean"],
                "variance_explains_excursion_flag": bool(
                    pd.notna(meta.get("sqrt_V2_global", math.nan))
                    and abs(float(meta.get("sqrt_V2_global", math.nan)) - q["max"]) / float(meta.get("sqrt_V2_global", math.nan)) <= 0.01
                ),
            }
        ]
    )


def failures(rows: pd.DataFrame) -> pd.DataFrame:
    fail = rows[rows["failure_type"].ne("")].copy()
    if fail.empty:
        return pd.DataFrame(
            columns=[
                "candidate_id",
                "block_id",
                "x",
                "y",
                "h",
                "p_star",
                "Q_R2Q",
                "Q_exc",
                "sqrt_V2",
                "Q_exc_over_sqrt_V2",
                "cap",
                "failure_type",
                "reason",
                "status",
            ]
        )
    reason = {
        "Q_exc_above_1": "bridge excursion exceeds unit cap",
        "Q_exc_above_0p25": "bridge excursion exceeds 0.25 cap",
        "Q_exc_above_0p10": "bridge excursion exceeds 0.10 cap",
        "Q_exc_above_0p05": "bridge excursion exceeds 0.05 cap",
        "Q_exc_above_0p025": "bridge excursion exceeds strong 0.025 cap",
        "missing_Q_exc_near_forbidden": "near-forbidden row has no Q_exc",
        "missing_scale_near_forbidden": "near-forbidden row has invalid local scale",
        "variance_proxy_missing": "V2 variance proxy missing",
        "variance_ratio_unstable": "Q_exc/sqrt(V2) exceeds stability threshold",
        "endpoint_exclusion_failure": "endpoint exclusion reports harmful endpoint",
    }
    fail["cap"] = fail["failure_type"].map(
        {
            "Q_exc_above_1": 1.0,
            "Q_exc_above_0p25": 0.25,
            "Q_exc_above_0p10": 0.10,
            "Q_exc_above_0p05": 0.05,
            "Q_exc_above_0p025": 0.025,
        }
    )
    fail["reason"] = fail["failure_type"].map(reason).fillna("unclassified")
    cols = [
        "candidate_id",
        "block_id",
        "x",
        "y",
        "h",
        "p_star",
        "Q_R2Q",
        "Q_exc",
        "sqrt_V2",
        "Q_exc_over_sqrt_V2",
        "cap",
        "failure_type",
        "reason",
        "status",
    ]
    return fail[cols]


def summarize(rows: pd.DataFrame, var: pd.DataFrame, fail: pd.DataFrame, caps: pd.DataFrame, meta: dict[str, float | str], used: list[str], missing: list[str], joins: list[str]) -> pd.DataFrame:
    q = qstats(rows["Q_exc"])
    coord = rows[rows["coordinate_available_flag"]]
    post = rows[rows["post_P0_flag"]]
    near = rows[rows["near_forbidden_flag"]]
    cminus = rows[rows["C_minus_flag"]]
    endpoint_status = str(meta.get("endpoint_exclusion_status", "not_available"))
    endpoint_harmful = int(round(float(meta.get("endpoint_exclusion_harmful_count", 0) or 0))) if endpoint_status == "available" else 0
    missing_near = int((rows["near_forbidden_flag"] & rows["Q_exc"].isna() & ~rows["finite_certificate_flag"]).sum())
    invalid_scale_near = int((rows["near_forbidden_flag"] & ~rows["valid_scale_flag"] & ~rows["finite_certificate_flag"]).sum())
    pass_emp = bool(q["max"] < 1 and missing_near == 0 and endpoint_harmful == 0 and invalid_scale_near == 0)
    if q["max"] <= 0.025 and bool(var.iloc[0]["variance_explains_excursion_flag"]) and endpoint_harmful == 0:
        theorem = "strong_bridge_rigidity_Cexc_0p025"
        next_file = "Prime_Mesh_R2Q_HExc_BridgeRigidity_Closure_Update_v1.md"
    elif q["max"] <= 0.05 and pass_emp:
        theorem = "good_bridge_rigidity_Cexc_0p05"
        next_file = "Prime_Mesh_R2Q_HExc_BridgeRigidity_Closure_Update_v1.md"
    elif pass_emp:
        theorem = "sufficient_bridge_rigidity_Cexc_lt_1"
        next_file = "Prime_Mesh_R2Q_HExc_BridgeRigidity_Closure_Update_v1.md"
    else:
        theorem = "repair_needed"
        next_file = "Prime_Mesh_R2Q_HExc_BridgeRigidity_Repair_Map_v1.md"
    summary = {
        "rows": len(rows),
        "coordinate_test_rows": len(coord),
        "post_P0_rows": int(rows["post_P0_flag"].sum()),
        "finite_certificate_rows": int(rows["finite_certificate_flag"].sum()),
        "near_forbidden_rows": int(rows["near_forbidden_flag"].sum()),
        "forbidden_rows": int(rows["forbidden_flag"].sum()),
        "C_minus_rows": int(rows["C_minus_flag"].sum()),
        "O2_applicable_rows": int(rows["O2_applicable_flag"].sum()),
        "B3_applicable_rows": int(rows["B3_applicable_flag"].sum()),
        "Q_exc_available_rows": int(rows["Q_exc"].notna().sum()),
        "Q_exc_missing_rows": int(rows["Q_exc"].isna().sum()),
        "Q_exc_max": q["max"],
        "Q_exc_mean": q["mean"],
        "Q_exc_q95": q["q95"],
        "Q_exc_q99": q["q99"],
        "near_forbidden_Q_exc_max": qstats(near["Q_exc"])["max"],
        "C_minus_Q_exc_max": qstats(cminus["Q_exc"])["max"],
        "post_P0_Q_exc_max": qstats(post["Q_exc"])["max"],
        "V2_available_rows": int(rows["V2"].notna().sum()),
        "V2_global": meta.get("V2_global", math.nan),
        "sqrt_V2_global": meta.get("sqrt_V2_global", math.nan),
        "Q_exc_max_over_sqrt_V2_global": var.iloc[0]["Q_exc_over_sqrt_V2_max"],
        "Q_exc_over_sqrt_V2_max": var.iloc[0]["Q_exc_over_sqrt_V2_max"],
        "variance_explains_excursion_flag": bool(var.iloc[0]["variance_explains_excursion_flag"]),
        "endpoint_exclusion_status": endpoint_status,
        "endpoint_exclusion_harmful_count": endpoint_harmful,
        "pass_endpoint_exclusion": bool(endpoint_status != "available" or endpoint_harmful == 0),
        "rows_above_0p025": int((rows["Q_exc"] > 0.025).sum()),
        "rows_above_0p05": int((rows["Q_exc"] > 0.05).sum()),
        "rows_above_0p10": int((rows["Q_exc"] > 0.10).sum()),
        "rows_above_0p25": int((rows["Q_exc"] > 0.25).sum()),
        "rows_above_1p00": int((rows["Q_exc"] > 1.00).sum()),
        "pass_cap_0p025": bool(caps.loc[caps["cap"].eq(0.025), "pass_cap"].iloc[0]),
        "pass_cap_0p05": bool(caps.loc[caps["cap"].eq(0.05), "pass_cap"].iloc[0]),
        "pass_cap_0p10": bool(caps.loc[caps["cap"].eq(0.10), "pass_cap"].iloc[0]),
        "pass_cap_0p25": bool(caps.loc[caps["cap"].eq(0.25), "pass_cap"].iloc[0]),
        "pass_cap_1p00": bool(caps.loc[caps["cap"].eq(1.00), "pass_cap"].iloc[0]),
        "missing_Q_exc_near_forbidden_count": missing_near,
        "invalid_scale_near_forbidden_count": invalid_scale_near,
        "hexc_failures": len(fail),
        "pass_hexc_bridge_rigidity_empirical": pass_emp,
        "recommended_theorem_form": theorem,
        "recommended_next_file": next_file,
        "inputs_used": ";".join(used),
        "optional_inputs_missing": ";".join(missing),
        "join_notes": ";".join(joins),
        "audit_level": "row-level_existing_o2p3_plus_fcl_Qexc",
    }
    return pd.DataFrame([summary])


def write_doc(summary: pd.DataFrame, caps: pd.DataFrame, var: pd.DataFrame, fail: pd.DataFrame, used: list[str], missing: list[str], joins: list[str]) -> None:
    s = summary.iloc[0].to_dict()
    status = "passes" if bool(s["pass_hexc_bridge_rigidity_empirical"]) else "needs repair"
    lines = [
        "# Prime Mesh R2Q - H-Exc BridgeRigidity Audit",
        "",
        "**Document:** `Prime_Mesh_R2Q_HExc_BridgeRigidity_Audit_v1.md`",
        "**Project:** Prime Mesh Theory - RH Programme",
        f"**Date:** {date.today().isoformat()}",
        f"**Status:** H-Exc BridgeRigidity audit - {status}",
        "",
        "## 1. Executive Verdict",
        "",
        r"This audit tests:",
        "",
        r"\[Q_{\rm exc}(J)=\frac{\sup_{t\in J}|D_N(t)-\ell_J(t)|}{\sqrt h\log^2p^*}\le C_{\rm exc}.\]",
        "",
    ]
    if bool(s["pass_cap_0p025"]):
        lines += [r"\[\boxed{\text{Strong H-Exc cap passes: }Q_{\rm exc}\le0.025.}\]", ""]
    elif bool(s["pass_cap_0p05"]):
        lines += [r"\[\boxed{\text{Good H-Exc cap passes: }Q_{\rm exc}\le0.05.}\]", ""]
    elif bool(s["pass_hexc_bridge_rigidity_empirical"]):
        lines += [r"\[\boxed{\text{Sufficient H-Exc cap passes: }Q_{\rm exc}<1.}\]", ""]
    else:
        lines += [r"\[\boxed{\text{H-Exc has unresolved rows.}}\]", ""]

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

    lines += [
        "",
        "## 3. Audit Level",
        "",
        f"`{s['audit_level']}`",
        "",
        "## 4. Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    for key, value in s.items():
        if key in {"inputs_used", "optional_inputs_missing", "join_notes"}:
            continue
        lines.append(f"| `{key}` | {value} |")

    lines += [
        "",
        "## 5. Cap Tests",
        "",
        "| cap | rows tested | rows above | near-forbidden above | pass |",
        "|---:|---:|---:|---:|---|",
    ]
    for _, row in caps.iterrows():
        lines.append(
            f"| {row['cap']} | {int(row['rows_tested'])} | {int(row['rows_above_cap'])} | {int(row['near_forbidden_rows_above_cap'])} | {bool(row['pass_cap'])} |"
        )

    lines += [
        "",
        "## 6. Variance Proxy Result",
        "",
        f"- `sqrt_V2_global`: `{s['sqrt_V2_global']}`",
        f"- `Q_exc_max`: `{s['Q_exc_max']}`",
        f"- `Q_exc_max_over_sqrt_V2_global`: `{s['Q_exc_max_over_sqrt_V2_global']}`",
        f"- `variance_explains_excursion_flag`: `{s['variance_explains_excursion_flag']}`",
        "",
        "## 7. Endpoint Exclusion",
        "",
        f"- `endpoint_exclusion_status`: `{s['endpoint_exclusion_status']}`",
        f"- `endpoint_exclusion_harmful_count`: `{s['endpoint_exclusion_harmful_count']}`",
        f"- `pass_endpoint_exclusion`: `{s['pass_endpoint_exclusion']}`",
        "",
        "## 8. Failures",
        "",
    ]
    if len(fail):
        lines.append(f"`{len(fail)}` diagnostic failures were written to `prime_mesh_r2q_hexc_bridge_rigidity_failures.csv`.")
    else:
        lines.append("No failures found.")

    lines += [
        "",
        "## 9. Interpretation",
        "",
        f"Recommended theorem form: `{s['recommended_theorem_form']}`.",
        "",
        f"Recommended next file: `{s['recommended_next_file']}`.",
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
    df, used, missing, joins, meta = load_inputs()
    rows = build_rows(df, meta)
    caps = cap_table(rows)
    regimes = by_regime(rows)
    var = variance_table(rows, meta)
    fail = failures(rows)
    summary = summarize(rows, var, fail, caps, meta, used, missing, joins)

    rows.to_csv(ROWS_OUT, index=False)
    regimes.to_csv(BY_REGIME_OUT, index=False)
    var.to_csv(VARIANCE_OUT, index=False)
    fail.to_csv(FAILURES_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_doc(summary, caps, var, fail, used, missing, joins)
    refresh_manifest()

    for p in [SUMMARY_OUT, ROWS_OUT, BY_REGIME_OUT, VARIANCE_OUT, FAILURES_OUT, DOC_OUT]:
        log(f"wrote {p}")
    for key, value in summary.iloc[0].to_dict().items():
        if key not in {"inputs_used", "optional_inputs_missing", "join_notes"}:
            log(f"{key} = {value}")


if __name__ == "__main__":
    main()
