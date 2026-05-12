from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import pandas as pd


OUT = Path(
    r"C:\Users\jhegy\source\repos\prime-mesh-theory\docs\RH\notes\claude\repair and close process\scripts and results"
)

PRIMARY = OUT / "prime_mesh_r2q_negative_transfer_coordinate_rows.csv"
NT_SUMMARY = OUT / "prime_mesh_r2q_negative_transfer_coordinate_summary.csv"
NT_BY_SIGN = OUT / "prime_mesh_r2q_negative_transfer_coordinate_by_sign.csv"
NT_THRESHOLDS = OUT / "prime_mesh_r2q_negative_transfer_coordinate_thresholds.csv"
PARTIAL_ROWS = OUT / "prime_mesh_r2q_partial_full_interval_compatibility_rows.csv"
FCL_WINDOWS = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_windows.csv"
FCL_CROSSINGS = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv"
GEOMETRY = OUT / "prime_mesh_r2q_blocksystem_definition_geometry.csv"
BLOCKS = OUT / "prime_mesh_r2q_blocksystem_definition_blocks.csv"
SCHUR_VECTORS = OUT / "prime_mesh_r2q_o1_schur_residual_sign_stability_vectors.csv"
SCHUR_SCOPES = OUT / "prime_mesh_r2q_o1_schur_residual_sign_stability_scopes.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_positive_harmlessness_summary.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_positive_harmlessness_rows.csv"
BY_REGIME_OUT = OUT / "prime_mesh_r2q_positive_harmlessness_by_regime.csv"
CAPS_OUT = OUT / "prime_mesh_r2q_positive_harmlessness_caps.csv"
EXTREMES_OUT = OUT / "prime_mesh_r2q_positive_harmlessness_extremes.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_positive_harmlessness_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_PositiveHarmlessness_Decomposition_Audit_v1.md"
MANIFEST_OUT = OUT / "deposit_manifest.csv"

CAPS = [0.25, 0.50, 0.75, 1.00]


def log(msg: str) -> None:
    print(f"[positive-harmlessness] {msg}")


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


def ensure_col(df: pd.DataFrame, col: str, value: object = "not_available") -> None:
    if col not in df.columns:
        df[col] = value


def load_inputs() -> tuple[pd.DataFrame, list[str], list[str], list[str]]:
    if not PRIMARY.exists():
        raise FileNotFoundError(PRIMARY)
    log(f"reading primary {PRIMARY.name}")
    df = pd.read_csv(PRIMARY)
    used = [PRIMARY.name]
    missing: list[str] = []
    joins: list[str] = ["primary rows used directly"]

    optional_files = [
        NT_SUMMARY,
        NT_BY_SIGN,
        NT_THRESHOLDS,
        PARTIAL_ROWS,
        FCL_CROSSINGS,
        GEOMETRY,
        BLOCKS,
        SCHUR_VECTORS,
        SCHUR_SCOPES,
    ]
    for path in optional_files:
        if path.exists():
            used.append(path.name)
        else:
            missing.append(path.name)

    if FCL_WINDOWS.exists():
        w = pd.read_csv(FCL_WINDOWS)
        used.append(FCL_WINDOWS.name)
        keep = [
            "block_id",
            "p_star",
            "y",
            "h",
            "scale_bin",
            "depth_bin",
            "mu_bin",
            "Q_max",
            "Q_local",
            "cp_ratio",
            "d_worst",
            "shell_pattern",
        ]
        keep = [c for c in keep if c in w.columns]
        join_keys = [c for c in ["block_id", "p_star", "y", "h"] if c in df.columns and c in w.columns]
        if join_keys:
            before = len(df)
            df = df.merge(w[keep].drop_duplicates(subset=join_keys), on=join_keys, how="left", suffixes=("", "_win"))
            joins.append(f"{FCL_WINDOWS.name} on {join_keys}: {before}->{len(df)}")
    else:
        missing.append(FCL_WINDOWS.name)

    return df, used, missing, joins


def build_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows = pd.DataFrame(index=df.index)
    for col in [
        "candidate_id",
        "block_id",
        "x",
        "y",
        "h",
        "right_endpoint",
        "p_star",
        "source",
        "channel_full",
        "channel_inferred",
        "spf_class",
        "schur_projection_sign",
    ]:
        rows[col] = df[col] if col in df.columns else "not_available"

    for col in ["x", "y", "h", "right_endpoint", "p_star"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce")

    rows["E_theta"] = safe_num(df, "E_theta")
    rows["E_theta_normalized"] = safe_num(df, "E_theta_normalized")
    rows["E_theta_sign"] = df.get("E_theta_sign", pd.Series("unknown", index=df.index)).fillna("unknown").astype(str).str.lower()
    rows["positive_theta_flag"] = rows["E_theta_sign"].eq("positive")
    rows["negative_theta_flag"] = rows["E_theta_sign"].eq("negative")
    rows["zero_theta_flag"] = rows["E_theta_sign"].eq("zero")
    rows["unknown_theta_flag"] = rows["E_theta_sign"].eq("unknown")

    rows["Q_R2Q"] = safe_num(df, "Q_R2Q")
    for cap in CAPS:
        label = str(cap).replace(".", "p")
        rows[f"Q_cap_{label}_fail_flag"] = rows["positive_theta_flag"] & (rows["Q_R2Q"] > cap)
    rows["near_forbidden_flag"] = safe_bool(df, "near_forbidden_flag") | (rows["Q_R2Q"] > 0.75)
    rows["forbidden_flag"] = safe_bool(df, "forbidden_flag") | (rows["Q_R2Q"] > 1.0)

    rows["post_P0_flag"] = safe_bool(df, "post_P0_flag")
    rows["tail_flag"] = safe_bool(df, "tail_flag")
    rows["finite_certificate_flag"] = safe_bool(df, "finite_certificate_flag")
    rows["coordinate_available_flag"] = safe_bool(df, "coordinate_available_flag")
    rows["valid_scale_flag"] = safe_bool(df, "valid_scale_flag")
    rows["scale_ratio"] = safe_num(df, "scale_ratio")

    for col in ["scale_bin", "depth_bin", "mu_bin", "shell_pattern"]:
        rows[col] = df[col] if col in df.columns else "not_available"
        rows[col] = rows[col].fillna("not_available")

    rows["schur_projection_proxy"] = safe_num(df, "schur_projection_proxy")
    rows["schur_projection_sign"] = rows["schur_projection_sign"].fillna("not_available")
    rows["spf_class"] = rows["spf_class"].fillna("not_available")
    rows["channel_full"] = rows["channel_full"].fillna("not_available")
    rows["channel_inferred"] = rows["channel_inferred"].fillna("not_available")

    rows["positive_harmless_cap_class"] = "not_positive"
    pos = rows["positive_theta_flag"]
    rows.loc[pos & (rows["Q_R2Q"] <= 0.25), "positive_harmless_cap_class"] = "Q<=0.25"
    rows.loc[pos & (rows["Q_R2Q"] > 0.25) & (rows["Q_R2Q"] <= 0.50), "positive_harmless_cap_class"] = "0.25<Q<=0.50"
    rows.loc[pos & (rows["Q_R2Q"] > 0.50) & (rows["Q_R2Q"] <= 0.75), "positive_harmless_cap_class"] = "0.50<Q<=0.75"
    rows.loc[pos & (rows["Q_R2Q"] > 0.75) & (rows["Q_R2Q"] <= 1.00), "positive_harmless_cap_class"] = "0.75<Q<=1.00"
    rows.loc[pos & (rows["Q_R2Q"] > 1.00), "positive_harmless_cap_class"] = "Q>1.00"

    rows["positive_harmless_pass_flag"] = ~pos | (rows["Q_R2Q"] <= 1.0)
    rows["failure_type"] = ""
    rows.loc[pos & (rows["Q_R2Q"] > 0.25), "failure_type"] = "positive_above_0p25"
    rows.loc[pos & (rows["Q_R2Q"] > 0.50), "failure_type"] = "positive_above_0p50"
    rows.loc[pos & (rows["Q_R2Q"] > 0.75), "failure_type"] = "positive_above_0p75"
    rows.loc[pos & (rows["Q_R2Q"] > 1.00), "failure_type"] = "positive_above_1p00"
    rows.loc[pos & rows["near_forbidden_flag"], "failure_type"] = "positive_near_forbidden"
    rows.loc[pos & rows["forbidden_flag"], "failure_type"] = "positive_forbidden"
    rows.loc[rows["coordinate_available_flag"] & rows["E_theta"].isna(), "failure_type"] = "missing_E_theta"
    rows.loc[rows["coordinate_available_flag"] & rows["Q_R2Q"].isna(), "failure_type"] = "missing_Q_R2Q"
    rows.loc[rows["coordinate_available_flag"] & ~rows["valid_scale_flag"], "failure_type"] = "invalid_scale"
    rows.loc[rows["unknown_theta_flag"] & (rows["Q_R2Q"] > 0.75), "failure_type"] = "unknown_sign_with_large_Q"
    rows["status"] = rows["failure_type"].where(rows["failure_type"].ne(""), "pass")
    return rows


def q_stats(vals: pd.Series) -> dict[str, float]:
    vals = pd.to_numeric(vals, errors="coerce").dropna()
    if vals.empty:
        return {"min": math.nan, "max": math.nan, "mean": math.nan, "median": math.nan, "q90": math.nan, "q95": math.nan, "q99": math.nan}
    return {
        "min": float(vals.min()),
        "max": float(vals.max()),
        "mean": float(vals.mean()),
        "median": float(vals.median()),
        "q90": float(vals.quantile(0.90)),
        "q95": float(vals.quantile(0.95)),
        "q99": float(vals.quantile(0.99)),
    }


def make_caps(rows: pd.DataFrame) -> pd.DataFrame:
    pos = rows[rows["positive_theta_flag"] & rows["coordinate_available_flag"]].copy()
    out = []
    for cap in CAPS:
        tail = pos[pos["tail_flag"] | pos["post_P0_flag"]]
        post = pos[pos["post_P0_flag"]]
        out.append(
            {
                "cap": cap,
                "positive_rows_tested": len(pos),
                "positive_rows_above_cap": int((pos["Q_R2Q"] > cap).sum()),
                "positive_rows_at_or_below_cap": int((pos["Q_R2Q"] <= cap).sum()),
                "positive_frac_at_or_below_cap": float((pos["Q_R2Q"] <= cap).mean()) if len(pos) else 1.0,
                "positive_tail_rows_tested": len(tail),
                "positive_tail_rows_above_cap": int((tail["Q_R2Q"] > cap).sum()),
                "positive_tail_frac_at_or_below_cap": float((tail["Q_R2Q"] <= cap).mean()) if len(tail) else 1.0,
                "post_P0_positive_rows_tested": len(post),
                "post_P0_positive_rows_above_cap": int((post["Q_R2Q"] > cap).sum()),
                "post_P0_positive_frac_at_or_below_cap": float((post["Q_R2Q"] <= cap).mean()) if len(post) else 1.0,
                "pass_global_positive_cap": bool((pos["Q_R2Q"] <= cap).all()),
                "pass_tail_positive_cap": bool((tail["Q_R2Q"] <= cap).all()),
                "pass_post_P0_positive_cap": bool((post["Q_R2Q"] <= cap).all()),
            }
        )
    return pd.DataFrame(out)


def make_by_regime(rows: pd.DataFrame) -> pd.DataFrame:
    fields = [
        "post_P0_flag",
        "tail_flag",
        "finite_certificate_flag",
        "source",
        "scale_bin",
        "depth_bin",
        "mu_bin",
        "spf_class",
        "channel_full",
        "channel_inferred",
        "schur_projection_sign",
    ]
    out = []
    base = rows[rows["coordinate_available_flag"]].copy()
    for field in fields:
        if field not in base.columns:
            continue
        for value, g in base.groupby(field, dropna=False):
            pos = g[g["positive_theta_flag"]]
            q = q_stats(pos["Q_R2Q"])
            e = q_stats(pos["E_theta_normalized"])
            out.append(
                {
                    "regime_field": field,
                    "regime_value": value,
                    "rows": len(g),
                    "positive_rows": int(g["positive_theta_flag"].sum()),
                    "negative_rows": int(g["negative_theta_flag"].sum()),
                    "zero_rows": int(g["zero_theta_flag"].sum()),
                    "unknown_rows": int(g["unknown_theta_flag"].sum()),
                    "Q_min": q["min"],
                    "Q_max": q["max"],
                    "Q_mean": q["mean"],
                    "Q_median": q["median"],
                    "Q_q90": q["q90"],
                    "Q_q95": q["q95"],
                    "Q_q99": q["q99"],
                    "E_theta_norm_min": e["min"],
                    "E_theta_norm_max": e["max"],
                    "E_theta_norm_mean": e["mean"],
                    "near_forbidden_count": int(pos["near_forbidden_flag"].sum()),
                    "forbidden_count": int(pos["forbidden_flag"].sum()),
                    "cap_0p25_fail_count": int((pos["Q_R2Q"] > 0.25).sum()),
                    "cap_0p50_fail_count": int((pos["Q_R2Q"] > 0.50).sum()),
                    "cap_0p75_fail_count": int((pos["Q_R2Q"] > 0.75).sum()),
                    "cap_1p00_fail_count": int((pos["Q_R2Q"] > 1.00).sum()),
                    "positive_Qmax": q["max"],
                    "positive_tail_Qmax": q_stats(pos.loc[pos["tail_flag"] | pos["post_P0_flag"], "Q_R2Q"])["max"],
                    "pass_cap_0p25": bool((pos["Q_R2Q"] <= 0.25).all()),
                    "pass_cap_0p50": bool((pos["Q_R2Q"] <= 0.50).all()),
                    "pass_cap_0p75": bool((pos["Q_R2Q"] <= 0.75).all()),
                    "pass_cap_1p00": bool((pos["Q_R2Q"] <= 1.00).all()),
                }
            )
    return pd.DataFrame(out)


def make_extremes(rows: pd.DataFrame) -> pd.DataFrame:
    pos = rows[rows["positive_theta_flag"] & rows["coordinate_available_flag"]].copy()
    pieces = []

    def add(df: pd.DataFrame, label: str, n: int | None = None) -> None:
        if df.empty:
            return
        d = df.sort_values("Q_R2Q", ascending=False).copy()
        if n is not None:
            d = d.head(n)
        d["extreme_set"] = label
        d["rank_in_set"] = range(1, len(d) + 1)
        pieces.append(d)

    add(pos, "top25_global_positive_Q", 25)
    add(pos[pos["tail_flag"] | pos["post_P0_flag"]], "top25_tail_positive_Q", 25)
    add(pos[pos["post_P0_flag"]], "top25_post_P0_positive_Q", 25)
    add(pos[pos["Q_R2Q"] > 0.20], "positive_Q_gt_0p20")
    add(pos[pos["Q_R2Q"] > 0.25], "positive_Q_gt_0p25")
    add(pos[pos["Q_R2Q"] > 0.75], "positive_Q_gt_0p75")
    add(pos[pos["Q_R2Q"] > 1.00], "positive_Q_gt_1p00")
    if not pieces:
        return pd.DataFrame()
    cols = [
        "extreme_set",
        "rank_in_set",
        "candidate_id",
        "block_id",
        "x",
        "y",
        "h",
        "p_star",
        "E_theta",
        "E_theta_normalized",
        "E_theta_sign",
        "Q_R2Q",
        "post_P0_flag",
        "tail_flag",
        "finite_certificate_flag",
        "source",
        "scale_bin",
        "depth_bin",
        "mu_bin",
        "spf_class",
        "channel_full",
        "channel_inferred",
        "status",
    ]
    out = pd.concat(pieces, ignore_index=True)
    return out[[c for c in cols if c in out.columns]]


def make_failures(rows: pd.DataFrame) -> pd.DataFrame:
    pos = rows[rows["positive_theta_flag"] & rows["coordinate_available_flag"]].copy()
    out = []
    failure_defs = [
        (0.25, "positive_above_0p25", "positive theta row exceeds Q cap 0.25"),
        (0.50, "positive_above_0p50", "positive theta row exceeds Q cap 0.50"),
        (0.75, "positive_above_0p75", "positive theta row exceeds Q cap 0.75"),
        (1.00, "positive_above_1p00", "positive theta row exceeds Q cap 1.00"),
    ]
    for _, row in pos.iterrows():
        for cap, ftype, reason in failure_defs:
            if row["Q_R2Q"] > cap:
                out.append(
                    {
                        "candidate_id": row["candidate_id"],
                        "block_id": row["block_id"],
                        "x": row["x"],
                        "y": row["y"],
                        "h": row["h"],
                        "p_star": row["p_star"],
                        "E_theta": row["E_theta"],
                        "E_theta_sign": row["E_theta_sign"],
                        "Q_R2Q": row["Q_R2Q"],
                        "cap": cap,
                        "failure_type": ftype,
                        "reason": reason,
                        "status": "strong_cap_failure" if cap == 0.25 else "diagnostic",
                    }
                )
        if row["near_forbidden_flag"]:
            out.append({**{k: row[k] for k in ["candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta", "E_theta_sign", "Q_R2Q"]}, "cap": 0.75, "failure_type": "positive_near_forbidden", "reason": "positive theta row is near-forbidden", "status": "minimal_cap_failure"})
        if row["forbidden_flag"]:
            out.append({**{k: row[k] for k in ["candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta", "E_theta_sign", "Q_R2Q"]}, "cap": 1.00, "failure_type": "positive_forbidden", "reason": "positive theta row is forbidden", "status": "minimal_cap_failure"})
    return pd.DataFrame(out)


def make_summary(rows: pd.DataFrame, caps: pd.DataFrame) -> pd.DataFrame:
    test = rows[rows["coordinate_available_flag"]].copy()
    pos = test[test["positive_theta_flag"]].copy()
    tail_pos = pos[pos["tail_flag"] | pos["post_P0_flag"]]
    post_pos = pos[pos["post_P0_flag"]]
    non_tail_pos = pos[~(pos["tail_flag"] | pos["post_P0_flag"])]
    finite_pos = pos[pos["finite_certificate_flag"]]
    ps = q_stats(pos["Q_R2Q"])
    ts = q_stats(tail_pos["Q_R2Q"])

    def lowest_pass(scope_col: str) -> float:
        passed = caps[caps[scope_col]]
        return float(passed["cap"].min()) if len(passed) else math.nan

    summary = {
        "rows": len(rows),
        "coordinate_test_rows": len(test),
        "positive_rows": len(pos),
        "negative_rows": int(test["negative_theta_flag"].sum()),
        "zero_rows": int(test["zero_theta_flag"].sum()),
        "unknown_sign_rows": int(test["unknown_theta_flag"].sum()),
        "post_P0_rows": int(test["post_P0_flag"].sum()),
        "tail_rows": int((test["tail_flag"] | test["post_P0_flag"]).sum()),
        "finite_certificate_rows": int(test["finite_certificate_flag"].sum()),
        "positive_Qmin": ps["min"],
        "positive_Qmax": ps["max"],
        "positive_Qmean": ps["mean"],
        "positive_Qmedian": ps["median"],
        "positive_Qq95": ps["q95"],
        "positive_Qq99": ps["q99"],
        "positive_tail_rows": len(tail_pos),
        "positive_tail_Qmin": ts["min"],
        "positive_tail_Qmax": ts["max"],
        "positive_tail_Qmean": ts["mean"],
        "positive_tail_Qmedian": ts["median"],
        "positive_tail_Qq95": ts["q95"],
        "positive_tail_Qq99": ts["q99"],
        "post_P0_positive_rows": len(post_pos),
        "post_P0_positive_Qmax": q_stats(post_pos["Q_R2Q"])["max"],
        "non_tail_positive_rows": len(non_tail_pos),
        "non_tail_positive_Qmax": q_stats(non_tail_pos["Q_R2Q"])["max"],
        "finite_positive_rows": len(finite_pos),
        "finite_positive_Qmax": q_stats(finite_pos["Q_R2Q"])["max"],
        "positive_near_forbidden_count": int(pos["near_forbidden_flag"].sum()),
        "positive_forbidden_count": int(pos["forbidden_flag"].sum()),
        "positive_above_0p25_count": int((pos["Q_R2Q"] > 0.25).sum()),
        "positive_above_0p50_count": int((pos["Q_R2Q"] > 0.50).sum()),
        "positive_above_0p75_count": int((pos["Q_R2Q"] > 0.75).sum()),
        "positive_above_1p00_count": int((pos["Q_R2Q"] > 1.00).sum()),
        "lowest_global_positive_cap_passed": lowest_pass("pass_global_positive_cap"),
        "lowest_tail_positive_cap_passed": lowest_pass("pass_tail_positive_cap"),
        "pass_positive_cap_0p25": bool(caps.loc[caps["cap"].eq(0.25), "pass_global_positive_cap"].iloc[0]),
        "pass_positive_cap_0p50": bool(caps.loc[caps["cap"].eq(0.50), "pass_global_positive_cap"].iloc[0]),
        "pass_positive_cap_0p75": bool(caps.loc[caps["cap"].eq(0.75), "pass_global_positive_cap"].iloc[0]),
        "pass_positive_cap_1p00": bool(caps.loc[caps["cap"].eq(1.00), "pass_global_positive_cap"].iloc[0]),
        "pass_positive_harmlessness_empirical": bool(int((pos["Q_R2Q"] > 1.00).sum()) == 0 and int(pos["forbidden_flag"].sum()) == 0),
    }
    if summary["pass_positive_cap_0p25"]:
        summary["recommended_theorem_form"] = "global_strong_cap_Cplus_1_over_4"
        summary["recommended_next_file"] = "Prime_Mesh_R2Q_PositiveHarmlessness_Theorem_Target_v1.md"
    elif summary["pass_positive_cap_0p75"]:
        summary["recommended_theorem_form"] = "threshold_complement_Cplus_3_over_4"
        summary["recommended_next_file"] = "Prime_Mesh_R2Q_PositiveHarmlessness_ThresholdComplement_Target_v1.md"
    else:
        summary["recommended_theorem_form"] = "tail_plus_certificate"
        summary["recommended_next_file"] = "Prime_Mesh_R2Q_PositiveHarmlessness_TailSplit_Theorem_Target_v1.md"
    return pd.DataFrame([summary])


def write_doc(summary: pd.DataFrame, caps: pd.DataFrame, by_regime: pd.DataFrame, extremes: pd.DataFrame, failures: pd.DataFrame, used: list[str], missing: list[str], joins: list[str]) -> None:
    s = summary.iloc[0].to_dict()
    status = "passes" if bool(s["pass_positive_harmlessness_empirical"]) else "needs repair"
    lines = [
        "# Prime Mesh R2Q - PositiveHarmlessness Decomposition Audit",
        "",
        "**Document:** `Prime_Mesh_R2Q_PositiveHarmlessness_Decomposition_Audit_v1.md`",
        "**Project:** Prime Mesh Theory - RH Programme",
        f"**Date:** {date.today().isoformat()}",
        f"**Status:** PositiveHarmlessness decomposition audit - {status}",
        "",
        "## 1. Executive Verdict",
        "",
        r"This audit decomposes positive-theta rows and tests caps for:",
        "",
        r"\[E_\theta(J)>0\Rightarrow Q_{\rm R2Q}(J)\le C_+<1.\]",
        "",
    ]
    if bool(s["pass_positive_cap_0p25"]):
        lines += [r"\[\boxed{\text{Strong positive cap passes: }C_+=1/4.}\]", ""]
    elif bool(s["pass_positive_cap_0p75"]):
        lines += [r"\[\boxed{\text{Threshold positive cap passes: }C_+=3/4.}\]", ""]
    elif bool(s["pass_positive_harmlessness_empirical"]):
        lines += [r"\[\boxed{\text{Minimal positive harmlessness passes: }C_+<1.}\]", ""]
    else:
        lines += [r"\[\boxed{\text{Positive harmlessness has unresolved rows.}}\]", ""]

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

    lines += ["", "## 3. Summary", "", "| metric | value |", "|---|---:|"]
    for key, value in s.items():
        lines.append(f"| `{key}` | {value} |")

    lines += [
        "",
        "## 4. Cap Tests",
        "",
        "| cap | positive rows | above cap | tail above cap | post-P0 above cap | global pass | tail pass | post-P0 pass |",
        "|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for _, row in caps.iterrows():
        lines.append(
            f"| {row['cap']} | {int(row['positive_rows_tested'])} | {int(row['positive_rows_above_cap'])} | {int(row['positive_tail_rows_above_cap'])} | {int(row['post_P0_positive_rows_above_cap'])} | {bool(row['pass_global_positive_cap'])} | {bool(row['pass_tail_positive_cap'])} | {bool(row['pass_post_P0_positive_cap'])} |"
        )

    lines += [
        "",
        "## 5. Extreme Positive Rows",
        "",
        f"- `positive_Qmax`: `{s['positive_Qmax']}`",
        f"- `positive_tail_Qmax`: `{s['positive_tail_Qmax']}`",
        f"- `post_P0_positive_Qmax`: `{s['post_P0_positive_Qmax']}`",
        f"- `positive rows with Q>0.25`: `{s['positive_above_0p25_count']}`",
        "",
        "## 6. Regime Decomposition",
        "",
        f"`{len(by_regime)}` regime rows were written to `prime_mesh_r2q_positive_harmlessness_by_regime.csv`.",
        "",
        "## 7. Failures",
        "",
    ]
    hard_failures = failures[failures["cap"] >= 1.0] if len(failures) else failures
    if len(failures):
        lines.append(f"`{len(failures)}` cap diagnostic rows were written to `prime_mesh_r2q_positive_harmlessness_failures.csv`.")
        if len(hard_failures):
            lines.append(f"`{len(hard_failures)}` rows fail the minimal cap `C_+<1`.")
        else:
            lines.append("No rows fail the minimal cap `C_+<1`.")
    else:
        lines.append("No cap failures found.")

    lines += [
        "",
        "## 8. Interpretation",
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
    df, used, missing, joins = load_inputs()
    rows = build_rows(df)
    caps = make_caps(rows)
    by_regime = make_by_regime(rows)
    extremes = make_extremes(rows)
    failures = make_failures(rows)
    summary = make_summary(rows, caps)

    rows.to_csv(ROWS_OUT, index=False)
    by_regime.to_csv(BY_REGIME_OUT, index=False)
    caps.to_csv(CAPS_OUT, index=False)
    extremes.to_csv(EXTREMES_OUT, index=False)
    failures.to_csv(FAILURES_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_doc(summary, caps, by_regime, extremes, failures, used, missing, joins)
    refresh_manifest()

    for p in [SUMMARY_OUT, ROWS_OUT, BY_REGIME_OUT, CAPS_OUT, EXTREMES_OUT, FAILURES_OUT, DOC_OUT]:
        log(f"wrote {p}")
    for key, value in summary.iloc[0].to_dict().items():
        log(f"{key} = {value}")


if __name__ == "__main__":
    main()
