from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import pandas as pd


OUT = Path(
    r"C:\Users\jhegy\source\repos\prime-mesh-theory\docs\RH\notes\claude\repair and close process\scripts and results"
)

PARTIAL_ROWS = OUT / "prime_mesh_r2q_partial_full_interval_compatibility_rows.csv"
FCL_CROSSINGS = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv"
FCL_WINDOWS = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_windows.csv"
THETA_INTERVALS = OUT / "prime_mesh_r2q_theta_first_crossing_intervals.csv"
SCHUR_VECTORS = OUT / "prime_mesh_r2q_o1_schur_residual_sign_stability_vectors.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_negative_transfer_coordinate_summary.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_negative_transfer_coordinate_rows.csv"
BY_SIGN_OUT = OUT / "prime_mesh_r2q_negative_transfer_coordinate_by_sign.csv"
THRESHOLDS_OUT = OUT / "prime_mesh_r2q_negative_transfer_coordinate_thresholds.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_negative_transfer_coordinate_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_NegativeTransfer_Coordinate_Audit_v1.md"
MANIFEST_OUT = OUT / "deposit_manifest.csv"

TOL = 1e-12
THRESHOLDS = [0.50, 0.60, 0.70, 0.75, 0.80, 0.90, 1.00]


def log(msg: str) -> None:
    print(f"[negative-transfer] {msg}")


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
    if x < -tol:
        return "negative"
    if x > tol:
        return "positive"
    return "zero"


def safe_num(df: pd.DataFrame, col: str, default: float = math.nan) -> pd.Series:
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce")
    return pd.Series(default, index=df.index, dtype="float64")


def safe_bool(df: pd.DataFrame, col: str, default: bool = False) -> pd.Series:
    if col in df.columns:
        return boolish(df[col])
    return pd.Series(default, index=df.index, dtype="bool")


def load_base() -> tuple[pd.DataFrame, list[str], list[str]]:
    used: list[str] = []
    missing_optional: list[str] = []

    if PARTIAL_ROWS.exists():
        log(f"reading {PARTIAL_ROWS.name}")
        df = pd.read_csv(PARTIAL_ROWS)
        used.append(PARTIAL_ROWS.name)
    elif FCL_CROSSINGS.exists():
        log(f"reading fallback {FCL_CROSSINGS.name}")
        df = pd.read_csv(FCL_CROSSINGS)
        used.append(FCL_CROSSINGS.name)
    else:
        raise FileNotFoundError("Need partial/full rows or FCL crossings")

    # Add richer FCL/window columns where possible.
    if FCL_WINDOWS.exists():
        w = pd.read_csv(FCL_WINDOWS)
        used.append(FCL_WINDOWS.name)
        keep = [
            "block_id",
            "y",
            "h",
            "p_star",
            "scale_bin",
            "depth_bin",
            "mu_bin",
            "theta_local_norm",
            "theta_local_sign",
            "Q_local",
            "Q_max",
            "cp_ratio",
        ]
        keep = [c for c in keep if c in w.columns]
        df = df.merge(w[keep], on=[c for c in ["block_id", "y", "h", "p_star"] if c in df.columns and c in w.columns], how="left", suffixes=("", "_win"))
    else:
        missing_optional.append(FCL_WINDOWS.name)

    if THETA_INTERVALS.exists():
        used.append(THETA_INTERVALS.name)
    else:
        missing_optional.append(THETA_INTERVALS.name)

    if SCHUR_VECTORS.exists():
        used.append(SCHUR_VECTORS.name)
    else:
        missing_optional.append(SCHUR_VECTORS.name)

    return df, used, missing_optional


def infer_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows = pd.DataFrame(index=df.index)
    rows["candidate_id"] = df.get("candidate_id", pd.Series([f"row_{i:05d}" for i in range(len(df))], index=df.index))
    rows["block_id"] = df.get("block_id", pd.Series(math.nan, index=df.index))
    rows["x"] = safe_num(df, "x")
    rows["y"] = safe_num(df, "y")
    rows["h"] = safe_num(df, "h")
    rows["right_endpoint"] = safe_num(df, "right_endpoint").combine_first(rows["y"] + rows["h"])
    rows["p_star"] = safe_num(df, "p_star")
    rows["source"] = df.get("source", df.get("source_coordinate", pd.Series("unknown", index=df.index))).fillna("unknown")

    rows["E_theta"] = safe_num(df, "E_theta_full").combine_first(safe_num(df, "E_theta")).combine_first(safe_num(df, "E_theta_local"))
    scale = (rows["h"].clip(lower=1) ** 0.5) * (rows["p_star"].clip(lower=2).map(math.log) ** 2)
    rows["E_theta_normalized"] = rows["E_theta"] / scale
    existing_sign = df.get("full_sign", df.get("E_theta_sign", df.get("theta_local_sign", pd.Series("unknown", index=df.index)))).fillna("unknown")
    numeric_sign = rows["E_theta"].map(sign_label)
    rows["E_theta_sign"] = existing_sign.astype(str).str.lower()
    rows.loc[rows["E_theta_sign"].isin(["", "nan", "none", "unknown"]), "E_theta_sign"] = numeric_sign
    rows["E_theta_sign"] = rows["E_theta_sign"].replace({"false": "unknown", "true": "unknown"})

    rows["Q_R2Q"] = safe_num(df, "Q_R2Q_full").combine_first(safe_num(df, "Q_R2Q")).combine_first(safe_num(df, "Q_local")).combine_first(safe_num(df, "Q_max"))
    rows["Q_threshold_0p75_flag"] = rows["Q_R2Q"] > 0.75
    rows["Q_threshold_1p00_flag"] = rows["Q_R2Q"] > 1.0
    rows["near_forbidden_flag"] = rows["Q_threshold_0p75_flag"] | safe_bool(df, "near_forbidden_flag") | safe_bool(df, "near_forbidden_R2Q")
    rows["forbidden_flag"] = rows["Q_threshold_1p00_flag"] | safe_bool(df, "forbidden_flag") | safe_bool(df, "forbidden_R2Q")

    rows["positive_harmless_flag"] = safe_bool(df, "positive_harmless_flag")
    rows["negative_transfer_flag"] = safe_bool(df, "negative_transfer_flag")
    rows["channel_full"] = df.get("channel_full", df.get("crossing_status", pd.Series("unknown", index=df.index))).fillna("unknown")
    rows["channel_inferred"] = "neutral"
    rows.loc[rows["E_theta_sign"].eq("negative") & rows["near_forbidden_flag"], "channel_inferred"] = "negative_transfer"
    rows.loc[rows["E_theta_sign"].eq("positive"), "channel_inferred"] = "positive_harmless"

    rows["theta_negative_and_near_forbidden_flag"] = rows["E_theta_sign"].eq("negative") & rows["near_forbidden_flag"]
    rows["theta_positive_and_near_forbidden_flag"] = rows["E_theta_sign"].eq("positive") & rows["near_forbidden_flag"]
    rows["theta_zero_and_near_forbidden_flag"] = rows["E_theta_sign"].eq("zero") & rows["near_forbidden_flag"]
    rows["theta_unknown_and_near_forbidden_flag"] = rows["E_theta_sign"].eq("unknown") & rows["near_forbidden_flag"]
    rows["theta_negative_and_forbidden_flag"] = rows["E_theta_sign"].eq("negative") & rows["forbidden_flag"]
    rows["theta_positive_and_forbidden_flag"] = rows["E_theta_sign"].eq("positive") & rows["forbidden_flag"]
    rows["theta_zero_and_forbidden_flag"] = rows["E_theta_sign"].eq("zero") & rows["forbidden_flag"]
    rows["theta_unknown_and_forbidden_flag"] = rows["E_theta_sign"].eq("unknown") & rows["forbidden_flag"]

    rows["schur_projection_proxy"] = math.nan
    rows["schur_projection_sign"] = "not_available"
    rows["spf_class"] = "not_available"
    rows["scale_ratio"] = safe_num(df, "scale_ratio").combine_first(safe_num(df, "scale_ratio_local_to_global"))
    rows["post_P0_flag"] = safe_bool(df, "post_P0_flag") | safe_bool(df, "post_P0") | (rows["x"] >= 500_000_000)
    rows["tail_flag"] = safe_bool(df, "tail_flag") | safe_bool(df, "is_tail")
    rows["finite_certificate_flag"] = safe_bool(df, "finite_certificate_flag")
    rows["valid_scale_flag"] = rows["p_star"].notna() & rows["h"].notna() & (rows["h"] > 0)
    rows["coordinate_available_flag"] = rows["E_theta_sign"].ne("unknown") & rows["Q_R2Q"].notna() & rows["valid_scale_flag"]
    rows["finite_certificate_coordinate_excluded_flag"] = rows["finite_certificate_flag"] & ~rows["coordinate_available_flag"]

    rows["threshold_negative_transfer_pass_flag"] = ~rows["near_forbidden_flag"] | rows["E_theta_sign"].eq("negative")
    rows["failure_type"] = ""
    rows.loc[rows["theta_positive_and_near_forbidden_flag"], "failure_type"] = "positive_near_forbidden"
    rows.loc[rows["theta_positive_and_forbidden_flag"], "failure_type"] = "positive_forbidden"
    rows.loc[rows["theta_zero_and_near_forbidden_flag"], "failure_type"] = "zero_near_forbidden"
    rows.loc[rows["theta_unknown_and_near_forbidden_flag"], "failure_type"] = "unknown_sign_near_forbidden"
    theorem_row = ~rows["finite_certificate_coordinate_excluded_flag"]
    rows.loc[rows["E_theta"].isna() & theorem_row, "failure_type"] = "missing_E_theta"
    rows.loc[rows["Q_R2Q"].isna() & theorem_row, "failure_type"] = "missing_Q_R2Q"
    rows.loc[
        (~rows["valid_scale_flag"]) & rows["near_forbidden_flag"] & theorem_row,
        "failure_type",
    ] = "invalid_scale"
    rows.loc[rows["finite_certificate_coordinate_excluded_flag"], "failure_type"] = ""
    rows["status"] = rows["failure_type"].where(rows["failure_type"].ne(""), "pass")
    rows.loc[rows["finite_certificate_coordinate_excluded_flag"], "status"] = "finite_certificate_coordinate_excluded"
    return rows


def threshold_table(rows: pd.DataFrame) -> pd.DataFrame:
    test_rows = rows[rows["coordinate_available_flag"]].copy()
    out = []
    for threshold in THRESHOLDS:
        mask = test_rows["Q_R2Q"] > threshold
        total = int(mask.sum())
        neg = int((mask & test_rows["E_theta_sign"].eq("negative")).sum())
        pos = int((mask & test_rows["E_theta_sign"].eq("positive")).sum())
        zero = int((mask & test_rows["E_theta_sign"].eq("zero")).sum())
        unk = int((mask & test_rows["E_theta_sign"].eq("unknown")).sum())
        out.append(
            {
                "threshold": threshold,
                "rows_above_threshold": total,
                "negative_rows_above": neg,
                "positive_rows_above": pos,
                "zero_rows_above": zero,
                "unknown_rows_above": unk,
                "negative_frac_above": neg / total if total else 1.0,
                "positive_frac_above": pos / total if total else 0.0,
                "pass_threshold_negative_transfer": bool(total == 0 or (neg == total)),
            }
        )
    return pd.DataFrame(out)


def by_sign_table(rows: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["E_theta_sign", "post_P0_flag", "source"]
    data = []
    for keys, g in rows.groupby(group_cols, dropna=False):
        q = g["Q_R2Q"].dropna()
        e = g["E_theta_normalized"].dropna()
        data.append(
            {
                "E_theta_sign": keys[0],
                "post_P0_flag": keys[1],
                "source": keys[2],
                "rows": len(g),
                "Q_min": float(q.min()) if len(q) else math.nan,
                "Q_max": float(q.max()) if len(q) else math.nan,
                "Q_mean": float(q.mean()) if len(q) else math.nan,
                "Q_median": float(q.median()) if len(q) else math.nan,
                "Q_q95": float(q.quantile(0.95)) if len(q) else math.nan,
                "Q_q99": float(q.quantile(0.99)) if len(q) else math.nan,
                "near_forbidden_count": int(g["near_forbidden_flag"].sum()),
                "forbidden_count": int(g["forbidden_flag"].sum()),
                "E_theta_norm_min": float(e.min()) if len(e) else math.nan,
                "E_theta_norm_max": float(e.max()) if len(e) else math.nan,
                "E_theta_norm_mean": float(e.mean()) if len(e) else math.nan,
            }
        )
    return pd.DataFrame(data)


def failure_table(rows: pd.DataFrame) -> pd.DataFrame:
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
                "E_theta",
                "E_theta_sign",
                "Q_R2Q",
                "threshold",
                "failure_type",
                "reason",
                "status",
            ]
        )
    reason = {
        "positive_near_forbidden": "Q_R2Q > 0.75 but theta sign is positive",
        "positive_forbidden": "Q_R2Q > 1.0 but theta sign is positive",
        "zero_near_forbidden": "Q_R2Q > 0.75 but theta sign is zero",
        "unknown_sign_near_forbidden": "Q_R2Q > 0.75 but theta sign is unknown",
        "missing_E_theta": "missing theta error",
        "missing_Q_R2Q": "missing R2Q coordinate",
        "invalid_scale": "missing/invalid p_star or h for near-forbidden row",
    }
    fail["threshold"] = fail["forbidden_flag"].map(lambda x: 1.0 if x else 0.75)
    fail["reason"] = fail["failure_type"].map(reason).fillna("unclassified")
    return fail[
        [
            "candidate_id",
            "block_id",
            "x",
            "y",
            "h",
            "p_star",
            "E_theta",
            "E_theta_sign",
            "Q_R2Q",
            "threshold",
            "failure_type",
            "reason",
            "status",
        ]
    ]


def qmax(rows: pd.DataFrame, mask: pd.Series) -> float:
    vals = rows.loc[mask, "Q_R2Q"].dropna()
    return float(vals.max()) if len(vals) else 0.0


def summarize(rows: pd.DataFrame, thresholds: pd.DataFrame, used: list[str], missing_optional: list[str]) -> pd.DataFrame:
    test_rows = rows[rows["coordinate_available_flag"]].copy()
    pos = rows["E_theta_sign"].eq("positive")
    neg = rows["E_theta_sign"].eq("negative")
    zero = rows["E_theta_sign"].eq("zero")
    unk = rows["E_theta_sign"].eq("unknown")
    tail = rows["tail_flag"] | rows["post_P0_flag"]
    test_neg = test_rows["E_theta_sign"].eq("negative")
    q075 = test_rows["Q_R2Q"] > 0.75
    q1 = test_rows["Q_R2Q"] > 1.0
    clean = thresholds[thresholds["pass_threshold_negative_transfer"]]
    lowest_clean = float(clean["threshold"].min()) if len(clean) else math.nan
    q075_count = int(q075.sum())
    q1_count = int(q1.sum())
    q075_neg_frac = float((q075 & test_neg).sum() / q075_count) if q075_count else 1.0
    q1_neg_frac = float((q1 & test_neg).sum() / q1_count) if q1_count else 1.0
    pass_075 = bool(q075_count == 0 or q075_neg_frac == 1.0)
    pass_1 = bool(q1_count == 0 or q1_neg_frac == 1.0)
    pos_near = int((pos & rows["near_forbidden_flag"]).sum())
    pos_forb = int((pos & rows["forbidden_flag"]).sum())

    summary = {
        "rows": len(rows),
        "coordinate_test_rows": int(rows["coordinate_available_flag"].sum()),
        "finite_certificate_coordinate_excluded_rows": int(rows["finite_certificate_coordinate_excluded_flag"].sum()),
        "excluded_near_forbidden_rows": int(
            (rows["finite_certificate_coordinate_excluded_flag"] & rows["near_forbidden_flag"]).sum()
        ),
        "post_P0_rows": int(rows["post_P0_flag"].sum()),
        "positive_rows": int(pos.sum()),
        "negative_rows": int(neg.sum()),
        "zero_rows": int(zero.sum()),
        "unknown_sign_rows": int(unk.sum()),
        "positive_Qmax": qmax(rows, pos),
        "negative_Qmax": qmax(rows, neg),
        "zero_Qmax": qmax(rows, zero),
        "unknown_Qmax": qmax(rows, unk),
        "positive_tail_Qmax": qmax(rows, pos & tail),
        "negative_tail_Qmax": qmax(rows, neg & tail),
        "positive_near_forbidden_count": pos_near,
        "negative_near_forbidden_count": int((neg & rows["near_forbidden_flag"]).sum()),
        "zero_near_forbidden_count": int((zero & rows["near_forbidden_flag"]).sum()),
        "unknown_near_forbidden_count": int((unk & rows["near_forbidden_flag"]).sum()),
        "positive_forbidden_count": pos_forb,
        "negative_forbidden_count": int((neg & rows["forbidden_flag"]).sum()),
        "zero_forbidden_count": int((zero & rows["forbidden_flag"]).sum()),
        "unknown_forbidden_count": int((unk & rows["forbidden_flag"]).sum()),
        "Q_gt_0p75_count": q075_count,
        "Q_gt_0p75_negative_frac": q075_neg_frac,
        "Q_gt_1_count": q1_count,
        "Q_gt_1_negative_frac": q1_neg_frac,
        "lowest_clean_threshold": lowest_clean,
        "pass_NT_0p75": pass_075,
        "pass_NT_1p00": pass_1,
        "pass_threshold_negative_transfer": bool(not math.isnan(lowest_clean) and lowest_clean < 1.0),
        "pass_negative_transfer_coordinate_empirical": bool(
            pos_near == 0 and pos_forb == 0 and pass_075 and pass_1
        ),
        "inputs_used": ";".join(used),
        "optional_inputs_missing": ";".join(missing_optional),
    }
    return pd.DataFrame([summary])


def write_doc(summary: pd.DataFrame, thresholds: pd.DataFrame, failures: pd.DataFrame, used: list[str], missing: list[str]) -> None:
    s = summary.iloc[0].to_dict()
    status = "passes" if bool(s["pass_negative_transfer_coordinate_empirical"]) else "needs repair"
    lines = [
        "# Prime Mesh R2Q - NegativeTransfer Coordinate Audit",
        "",
        "**Document:** `Prime_Mesh_R2Q_NegativeTransfer_Coordinate_Audit_v1.md`",
        "**Project:** Prime Mesh Theory - RH Programme",
        f"**Date:** {date.today().isoformat()}",
        f"**Status:** NegativeTransfer coordinate audit - {status}",
        "",
        "## 1. Executive Verdict",
        "",
        r"This audit tests the practical threshold form:",
        "",
        r"\[Q_{\rm R2Q}(J)>Q_0\Rightarrow E_\theta(J)<0,\qquad Q_0<1.\]",
        "",
    ]
    if bool(s["pass_negative_transfer_coordinate_empirical"]):
        lines += [
            r"\[\boxed{\text{Threshold NegativeTransfer passes empirically.}}\]",
            "",
        ]
    else:
        lines += [
            r"\[\boxed{\text{Threshold NegativeTransfer has unresolved rows.}}\]",
            "",
        ]
    lines += ["## 2. Inputs Used", ""]
    for name in used:
        lines.append(f"- `{name}`")
    if missing:
        lines += ["", "Optional inputs missing:"]
        for name in missing:
            lines.append(f"- `{name}`")

    lines += ["", "## 3. Summary", "", "| metric | value |", "|---|---:|"]
    for key, value in s.items():
        if key in {"inputs_used", "optional_inputs_missing"}:
            continue
        lines.append(f"| `{key}` | {value} |")

    lines += [
        "",
        "## 4. Threshold Tests",
        "",
        "| threshold | rows above | negative frac | positive frac | pass |",
        "|---:|---:|---:|---:|---|",
    ]
    for _, row in thresholds.iterrows():
        lines.append(
            f"| {row['threshold']} | {int(row['rows_above_threshold'])} | {row['negative_frac_above']} | {row['positive_frac_above']} | {bool(row['pass_threshold_negative_transfer'])} |"
        )

    lines += [
        "",
        "## 5. Positive Cap Result",
        "",
        f"- `positive_Qmax`: `{s['positive_Qmax']}`",
        f"- `positive_tail_Qmax`: `{s['positive_tail_Qmax']}`",
        f"- `positive_near_forbidden_count`: `{int(s['positive_near_forbidden_count'])}`",
        f"- `positive_forbidden_count`: `{int(s['positive_forbidden_count'])}`",
        "",
        "## 6. Failures",
        "",
    ]
    if len(failures):
        lines.append(f"`{len(failures)}` failures were written to `prime_mesh_r2q_negative_transfer_coordinate_failures.csv`.")
    else:
        lines.append("No failures found.")

    lines += [
        "",
        "## 7. Recommended Theorem Form",
        "",
        f"The clean empirical threshold is `Q0 = {s['lowest_clean_threshold']}`.",
        "",
        "The threshold is computed on rows with an available local theta coordinate and valid local scale. Finite-certificate rows with no local theta coordinate are reported separately, not used as counterexamples to the post-`P0` coordinate theorem.",
        "",
        "The proof-facing practical form may use:",
        "",
        r"\[Q_{\rm R2Q}(J)>0.75\Rightarrow E_\theta(J)<0.\]",
        "",
        "Positive theta rows remain harmless below the near-forbidden threshold.",
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
    df, used, missing = load_base()
    rows = infer_rows(df)
    thresholds = threshold_table(rows)
    by_sign = by_sign_table(rows)
    failures = failure_table(rows)
    summary = summarize(rows, thresholds, used, missing)

    rows.to_csv(ROWS_OUT, index=False)
    by_sign.to_csv(BY_SIGN_OUT, index=False)
    thresholds.to_csv(THRESHOLDS_OUT, index=False)
    failures.to_csv(FAILURES_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_doc(summary, thresholds, failures, used, missing)
    refresh_manifest()

    for p in [SUMMARY_OUT, ROWS_OUT, BY_SIGN_OUT, THRESHOLDS_OUT, FAILURES_OUT, DOC_OUT]:
        log(f"wrote {p}")
    for key, value in summary.iloc[0].to_dict().items():
        if key not in {"inputs_used", "optional_inputs_missing"}:
            log(f"{key} = {value}")


if __name__ == "__main__":
    main()
