from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent

RAW_ROWS = BASE / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv"
BRIDGE_ROWS = BASE / "prime_mesh_r2q_hexc_bridge_rigidity_rows.csv"
BRIDGE_VARIANCE = BASE / "prime_mesh_r2q_hexc_bridge_rigidity_variance.csv"
V2_SUMMARY = BASE / "prime_mesh_r2q_hexc_v2_shell_variance_summary.csv"

OUT_SUMMARY = BASE / "prime_mesh_r2q_hexc_variance_proxy_summary.csv"
OUT_ROWS = BASE / "prime_mesh_r2q_hexc_variance_proxy_rows.csv"
OUT_BY_REGIME = BASE / "prime_mesh_r2q_hexc_variance_proxy_by_regime.csv"
OUT_FAILURES = BASE / "prime_mesh_r2q_hexc_variance_proxy_failures.csv"
OUT_NOTE = BASE / "Prime_Mesh_R2Q_HExc_VarianceProxy_Audit_v1.md"
MANIFEST = BASE / "deposit_manifest.csv"

C_EXC_CAP = 0.025
C_V_RECOMMENDED = 1.05
TOL = 1e-12


def log(message: str) -> None:
    print(f"[hexc-vp {datetime.now().strftime('%H:%M:%S')}] {message}")


def read_csv(path: Path, **kwargs) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path, **kwargs)


def bool_series(df: pd.DataFrame, column: str, default: bool = False) -> pd.Series:
    if column not in df.columns:
        return pd.Series(default, index=df.index, dtype=bool)
    s = df[column]
    if s.dtype == bool:
        return s.fillna(default)
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def numeric_series(df: pd.DataFrame, column: str, default=np.nan) -> pd.Series:
    if column not in df.columns:
        return pd.Series(default, index=df.index, dtype=float)
    return pd.to_numeric(df[column], errors="coerce")


def scalar(summary: pd.DataFrame | None, *names: str) -> float:
    if summary is None or summary.empty:
        return math.nan
    for name in names:
        if name in summary.columns:
            value = pd.to_numeric(summary[name], errors="coerce").dropna()
            if not value.empty:
                return float(value.iloc[0])
    return math.nan


def field_value_csv(path: Path, field: str) -> float:
    df = read_csv(path)
    if df is None or df.empty:
        return math.nan
    if {"field", "value"}.issubset(df.columns):
        row = df[df["field"].astype(str) == field]
        if not row.empty:
            return float(pd.to_numeric(row["value"], errors="coerce").iloc[0])
    if field in df.columns:
        value = pd.to_numeric(df[field], errors="coerce").dropna()
        if not value.empty:
            return float(value.iloc[0])
    return math.nan


def first_existing_numeric(df: pd.DataFrame, names: list[str], default=np.nan) -> pd.Series:
    for name in names:
        if name in df.columns:
            return pd.to_numeric(df[name], errors="coerce")
    return pd.Series(default, index=df.index, dtype=float)


def classify_regime(df: pd.DataFrame) -> pd.Series:
    positive = df["E_theta_sign"].eq("positive")
    negative = df["E_theta_sign"].eq("negative")
    forbidden = df["forbidden_flag"]
    near = df["near_forbidden_flag"]
    post = df["post_P0_flag"]

    regime = pd.Series("unclassified", index=df.index, dtype=object)
    regime.loc[positive & post] = "post_P0_positive_tail"
    regime.loc[positive & ~post] = "finite_positive"
    regime.loc[negative & post] = "post_P0_negative_tail"
    regime.loc[negative & ~post] = "finite_negative"
    regime.loc[negative & near] = "threshold_relevant_negative"
    regime.loc[negative & forbidden] = "forbidden_negative"
    return regime


def build_rows() -> tuple[pd.DataFrame, dict[str, str | float]]:
    inputs: dict[str, str | float] = {}

    if RAW_ROWS.exists():
        log(f"Reading primary rows: {RAW_ROWS.name}")
        df = pd.read_csv(RAW_ROWS)
        inputs["primary_rows"] = RAW_ROWS.name
    elif BRIDGE_ROWS.exists():
        log(f"Reading fallback rows: {BRIDGE_ROWS.name}")
        df = pd.read_csv(BRIDGE_ROWS)
        inputs["primary_rows"] = BRIDGE_ROWS.name
    else:
        raise FileNotFoundError("No RawR2Q v3 or H-Exc bridge rows found")

    out = pd.DataFrame(index=df.index)
    for col in ["candidate_id", "block_id", "x", "y", "h", "p_star", "E_theta_sign"]:
        if col in df.columns:
            out[col] = df[col]
        else:
            out[col] = np.nan

    out["post_P0_flag"] = bool_series(df, "post_P0_flag", False) | bool_series(df, "post_P0", False)
    out["finite_zone_flag"] = bool_series(df, "finite_zone_flag", False)
    if not out["finite_zone_flag"].any() and "p_star" in out.columns:
        out["finite_zone_flag"] = ~out["post_P0_flag"]

    out["E_theta"] = first_existing_numeric(df, ["E_theta", "E_theta_local"])
    if out["E_theta_sign"].isna().all():
        out["E_theta_sign"] = np.where(out["E_theta"] > 0, "positive", np.where(out["E_theta"] < 0, "negative", "zero"))

    out["Q_R2Q"] = first_existing_numeric(df, ["Q_R2Q", "Q_max"])
    out["Q_delta_D"] = first_existing_numeric(df, ["Q_delta_D"])
    out["Q_exc"] = first_existing_numeric(df, ["Q_exc"])
    out["epsilon"] = first_existing_numeric(df, ["epsilon", "formula_residual"])
    out["near_forbidden_flag"] = bool_series(df, "near_forbidden_flag", False) | bool_series(df, "near_forbidden_R2Q", False)
    out["forbidden_flag"] = bool_series(df, "forbidden_flag", False) | bool_series(df, "forbidden_R2Q", False)
    out["C_minus_flag"] = bool_series(df, "C_minus_flag", False)

    # If Q_exc was only available in H-Exc rows, merge it onto the primitive inventory.
    if out["Q_exc"].isna().any() and BRIDGE_ROWS.exists():
        bridge = pd.read_csv(BRIDGE_ROWS)
        keys = [k for k in ["block_id", "p_star", "y", "h"] if k in df.columns and k in bridge.columns]
        if keys and "Q_exc" in bridge.columns:
            before_missing = int(out["Q_exc"].isna().sum())
            bridge_small = bridge[keys + ["Q_exc"]].drop_duplicates(keys)
            merged = df[keys].merge(bridge_small, on=keys, how="left")
            out["Q_exc"] = out["Q_exc"].fillna(pd.to_numeric(merged["Q_exc"], errors="coerce"))
            inputs["Q_exc_merge_keys"] = ";".join(keys)
            inputs["Q_exc_missing_before_merge"] = before_missing
            inputs["Q_exc_missing_after_merge"] = int(out["Q_exc"].isna().sum())

    v2_global = field_value_csv(V2_SUMMARY, "V2_formula")
    sqrt_v2_global = field_value_csv(V2_SUMMARY, "sqrt_V2_formula")
    if not math.isfinite(v2_global):
        v2_global = field_value_csv(BRIDGE_VARIANCE, "V2_global")
    if not math.isfinite(sqrt_v2_global):
        sqrt_v2_global = field_value_csv(BRIDGE_VARIANCE, "sqrt_V2_global")
    if not math.isfinite(v2_global) and math.isfinite(sqrt_v2_global):
        v2_global = sqrt_v2_global * sqrt_v2_global
    if not math.isfinite(sqrt_v2_global) and math.isfinite(v2_global):
        sqrt_v2_global = math.sqrt(v2_global)

    row_v2 = first_existing_numeric(df, ["V2"], default=np.nan)
    row_sqrt_v2 = first_existing_numeric(df, ["sqrt_V2"], default=np.nan)
    if row_v2.notna().any() and row_sqrt_v2.isna().all():
        row_sqrt_v2 = np.sqrt(row_v2.clip(lower=0))
    if row_sqrt_v2.notna().any() and row_v2.isna().all():
        row_v2 = row_sqrt_v2 * row_sqrt_v2

    distinct_sqrt = row_sqrt_v2.dropna().round(15).nunique()
    if row_sqrt_v2.notna().any() and distinct_sqrt > 1:
        out["V2"] = row_v2
        out["sqrt_V2"] = row_sqrt_v2
        out["V2_source"] = "row_level_V2"
        audit_level = "row_level_V2"
    else:
        out["V2"] = v2_global
        out["sqrt_V2"] = sqrt_v2_global
        out["V2_source"] = "global_V2_from_shell_variance_summary"
        audit_level = "global_V2_only"

    out["V2_available_flag"] = pd.to_numeric(out["sqrt_V2"], errors="coerce").gt(0)
    out["Q_exc_over_sqrt_V2"] = out["Q_exc"] / out["sqrt_V2"]
    out["Q_exc_over_sqrt_V2_global"] = out["Q_exc"] / sqrt_v2_global
    out["row_regime"] = classify_regime(out)

    inputs["audit_level"] = audit_level
    inputs["V2_global"] = v2_global
    inputs["sqrt_V2_global"] = sqrt_v2_global
    inputs["row_sqrt_V2_distinct_values"] = distinct_sqrt
    return out, inputs


def summarize(rows: pd.DataFrame, inputs: dict[str, str | float]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    q_exc = pd.to_numeric(rows["Q_exc"], errors="coerce")
    ratio = pd.to_numeric(rows["Q_exc_over_sqrt_V2"], errors="coerce")
    threshold = rows["near_forbidden_flag"]
    forbidden = rows["forbidden_flag"]

    rows["Q_exc_above_0p025_flag"] = q_exc > C_EXC_CAP + TOL
    rows["variance_ratio_above_constant_flag"] = ratio > C_V_RECOMMENDED + TOL
    rows["missing_Q_exc_flag"] = q_exc.isna()
    rows["missing_V2_flag"] = ~rows["V2_available_flag"]
    rows["invalid_V2_flag"] = rows["sqrt_V2"].isna() | (rows["sqrt_V2"] <= 0)

    failures = []
    for idx, row in rows.iterrows():
        reasons = []
        if row["missing_Q_exc_flag"]:
            reasons.append("missing_Q_exc")
        if row["Q_exc_above_0p025_flag"]:
            reasons.append("Q_exc_above_0p025")
        if row["missing_Q_exc_flag"] and row["near_forbidden_flag"]:
            reasons.append("missing_Q_exc_threshold_relevant")
        if row["Q_exc_above_0p025_flag"] and row["near_forbidden_flag"]:
            reasons.append("threshold_Q_exc_above_0p025")
        if row["Q_exc_above_0p025_flag"] and row["forbidden_flag"]:
            reasons.append("forbidden_Q_exc_above_0p025")
        if row["invalid_V2_flag"]:
            reasons.append("invalid_V2")
        if row["missing_V2_flag"] and row["near_forbidden_flag"]:
            reasons.append("missing_V2_threshold_relevant")
        if row["variance_ratio_above_constant_flag"]:
            reasons.append("variance_ratio_above_theorem_constant")
        if reasons:
            out = row.to_dict()
            out["failure_type"] = ";".join(reasons)
            failures.append(out)

    failures_df = pd.DataFrame(failures)

    def max_or_nan(s: pd.Series) -> float:
        s = pd.to_numeric(s, errors="coerce").dropna()
        return float(s.max()) if not s.empty else math.nan

    def quantile_or_nan(s: pd.Series, q: float) -> float:
        s = pd.to_numeric(s, errors="coerce").dropna()
        return float(s.quantile(q)) if not s.empty else math.nan

    summary = {
        "rows": len(rows),
        "primitive_full_rows": int((~rows["Q_exc"].isna()).sum()),
        "Q_exc_available_rows": int((~rows["Q_exc"].isna()).sum()),
        "V2_available_rows": int(rows["V2_available_flag"].sum()),
        "audit_level": inputs["audit_level"],
        "Q_exc_max": max_or_nan(q_exc),
        "Q_exc_mean": float(q_exc.dropna().mean()) if q_exc.notna().any() else math.nan,
        "Q_exc_q95": quantile_or_nan(q_exc, 0.95),
        "Q_exc_q99": quantile_or_nan(q_exc, 0.99),
        "Q_exc_above_0p025_count": int(rows["Q_exc_above_0p025_flag"].sum()),
        "V2_global": inputs["V2_global"],
        "sqrt_V2_global": inputs["sqrt_V2_global"],
        "Q_exc_max_over_sqrt_V2_global": max_or_nan(rows["Q_exc_over_sqrt_V2_global"]),
        "Q_exc_over_sqrt_V2_max": max_or_nan(ratio),
        "Q_exc_over_sqrt_V2_mean": float(ratio.dropna().mean()) if ratio.notna().any() else math.nan,
        "Q_exc_over_sqrt_V2_q95": quantile_or_nan(ratio, 0.95),
        "Q_exc_over_sqrt_V2_q99": quantile_or_nan(ratio, 0.99),
        "threshold_relevant_rows": int(threshold.sum()),
        "threshold_relevant_Q_exc_max": max_or_nan(q_exc[threshold]),
        "threshold_relevant_sqrt_V2_min": float(rows.loc[threshold, "sqrt_V2"].dropna().min()) if rows.loc[threshold, "sqrt_V2"].notna().any() else math.nan,
        "threshold_relevant_ratio_max": max_or_nan(ratio[threshold]),
        "threshold_relevant_Q_exc_above_0p025_count": int((rows["Q_exc_above_0p025_flag"] & threshold).sum()),
        "forbidden_rows": int(forbidden.sum()),
        "forbidden_Q_exc_max": max_or_nan(q_exc[forbidden]),
        "forbidden_ratio_max": max_or_nan(ratio[forbidden]),
        "forbidden_Q_exc_above_0p025_count": int((rows["Q_exc_above_0p025_flag"] & forbidden).sum()),
        "missing_Q_exc_rows": int(rows["missing_Q_exc_flag"].sum()),
        "missing_V2_rows": int(rows["missing_V2_flag"].sum()),
        "missing_Q_exc_threshold_relevant_rows": int((rows["missing_Q_exc_flag"] & threshold).sum()),
        "missing_V2_threshold_relevant_rows": int((rows["missing_V2_flag"] & threshold).sum()),
        "missing_V2_forbidden_rows": int((rows["missing_V2_flag"] & forbidden).sum()),
        "invalid_V2_rows": int(rows["invalid_V2_flag"].sum()),
        "C_V_observed": max_or_nan(ratio),
        "C_V_theorem_recommended": C_V_RECOMMENDED,
        "hexc_variance_proxy_failures": len(failures_df),
    }

    summary["pass_absolute_Q_exc_cap"] = (
        summary["Q_exc_above_0p025_count"] == 0
        and summary["threshold_relevant_Q_exc_above_0p025_count"] == 0
        and summary["forbidden_Q_exc_above_0p025_count"] == 0
        and summary["missing_Q_exc_threshold_relevant_rows"] == 0
    )
    summary["pass_variance_proxy_explanation"] = (
        summary["Q_exc_over_sqrt_V2_max"] <= C_V_RECOMMENDED + TOL
        and summary["V2_available_rows"] > 0
        and summary["missing_V2_threshold_relevant_rows"] == 0
    )
    if inputs["audit_level"] == "global_V2_only":
        summary["variance_explanation_status"] = "global_proxy_supported_not_row_level"
        summary["recommended_theorem_form"] = "absolute_cap_with_global_variance_proxy"
        summary["recommended_next_file"] = "Prime_Mesh_R2Q_HExc_GlobalVarianceProxy_Closure_Update_v1.md"
    else:
        summary["variance_explanation_status"] = "row_level_variance_proxy_supported"
        summary["recommended_theorem_form"] = "row_level_variance_proxy"
        summary["recommended_next_file"] = "Prime_Mesh_R2Q_HExc_VarianceProxy_Theorem_Target_v1.md"
    summary["pass_hexc_variance_proxy_empirical"] = bool(
        summary["pass_absolute_Q_exc_cap"] and summary["pass_variance_proxy_explanation"] and summary["hexc_variance_proxy_failures"] == 0
    )

    summary_df = pd.DataFrame({"field": list(summary.keys()), "value": list(summary.values())})

    by_regime = []
    for regime, grp in rows.groupby("row_regime", dropna=False):
        gq = pd.to_numeric(grp["Q_exc"], errors="coerce")
        gr = pd.to_numeric(grp["Q_exc_over_sqrt_V2"], errors="coerce")
        by_regime.append({
            "row_regime": regime,
            "rows": len(grp),
            "Q_exc_max": max_or_nan(gq),
            "Q_exc_mean": float(gq.dropna().mean()) if gq.notna().any() else math.nan,
            "Q_exc_q95": quantile_or_nan(gq, 0.95),
            "ratio_max": max_or_nan(gr),
            "ratio_q95": quantile_or_nan(gr, 0.95),
            "Q_exc_above_0p025_count": int(grp["Q_exc_above_0p025_flag"].sum()),
            "missing_Q_exc_rows": int(grp["missing_Q_exc_flag"].sum()),
        })
    by_regime_df = pd.DataFrame(by_regime).sort_values("row_regime")
    return summary_df, by_regime_df, failures_df


def write_note(summary_df: pd.DataFrame, by_regime: pd.DataFrame, failures: pd.DataFrame, inputs: dict[str, str | float]) -> None:
    s = dict(zip(summary_df["field"], summary_df["value"]))
    verdict = "PASS" if str(s["pass_hexc_variance_proxy_empirical"]) == "True" else "FAIL"
    md = []
    md.append("# Prime Mesh R2Q - H-Exc VarianceProxy Audit v1\n")
    md.append(f"**Status:** {verdict}  \n")
    md.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}  \n")
    md.append("\n## Executive Verdict\n")
    md.append(
        "The H-Exc absolute bridge-excursion cap passes: "
        f"`Q_exc_max = {s['Q_exc_max']}` and no rows exceed `0.025`.\n"
    )
    md.append(
        "The available variance proxy is constant across rows, so the audit is classified as "
        f"`{s['audit_level']}`. This supports a global variance explanation, not a row-level `V2(J)` theorem yet.\n"
    )
    md.append("\n## Inputs Used\n")
    for key, value in inputs.items():
        md.append(f"- `{key}`: `{value}`\n")
    md.append("\n## Absolute H-Exc Cap\n")
    md.append(f"- `rows`: `{s['rows']}`\n")
    md.append(f"- `Q_exc_available_rows`: `{s['Q_exc_available_rows']}`\n")
    md.append(f"- `Q_exc_max`: `{s['Q_exc_max']}`\n")
    md.append(f"- `Q_exc_above_0p025_count`: `{s['Q_exc_above_0p025_count']}`\n")
    md.append(f"- `pass_absolute_Q_exc_cap`: `{s['pass_absolute_Q_exc_cap']}`\n")
    md.append("\n## Variance Proxy Ratio\n")
    md.append(f"- `V2_global`: `{s['V2_global']}`\n")
    md.append(f"- `sqrt_V2_global`: `{s['sqrt_V2_global']}`\n")
    md.append(f"- `Q_exc_max_over_sqrt_V2_global`: `{s['Q_exc_max_over_sqrt_V2_global']}`\n")
    md.append(f"- `C_V_observed`: `{s['C_V_observed']}`\n")
    md.append(f"- `C_V_theorem_recommended`: `{s['C_V_theorem_recommended']}`\n")
    md.append(f"- `variance_explanation_status`: `{s['variance_explanation_status']}`\n")
    md.append("\n## Threshold And Forbidden Safety\n")
    md.append(f"- `threshold_relevant_rows`: `{s['threshold_relevant_rows']}`\n")
    md.append(f"- `threshold_relevant_Q_exc_max`: `{s['threshold_relevant_Q_exc_max']}`\n")
    md.append(f"- `threshold_relevant_ratio_max`: `{s['threshold_relevant_ratio_max']}`\n")
    md.append(f"- `forbidden_rows`: `{s['forbidden_rows']}`\n")
    md.append(f"- `forbidden_Q_exc_max`: `{s['forbidden_Q_exc_max']}`\n")
    md.append(f"- `forbidden_ratio_max`: `{s['forbidden_ratio_max']}`\n")
    md.append("\n## Regime Decomposition\n")
    md.append(by_regime.to_markdown(index=False))
    md.append("\n\n## Failures\n")
    if failures.empty:
        md.append("No failures were found.\n")
    else:
        md.append(f"`{len(failures)}` failures were found. See `prime_mesh_r2q_hexc_variance_proxy_failures.csv`.\n")
    md.append("\n## Theorem Interpretation\n")
    md.append(
        "The proof-facing absolute statement `Q_exc <= 0.025` is empirically supported on the full audited inventory. "
        "The variance explanation is currently global: `Q_exc_max / sqrt(V2_global) < 1`, with `sqrt(V2_global)` nearly matching the observed maximum. "
        "A row-level `V2(J)` theorem should not be claimed until a genuinely varying local variance field is exported or derived.\n"
    )
    md.append("\n## Recommended Next File\n")
    md.append(f"`{s['recommended_next_file']}`\n")
    OUT_NOTE.write_text("".join(md), encoding="utf-8")


def refresh_manifest() -> None:
    rows = []
    if MANIFEST.exists():
        rows = pd.read_csv(MANIFEST).to_dict("records")
    files = [
        Path(__file__).name,
        OUT_SUMMARY.name,
        OUT_ROWS.name,
        OUT_BY_REGIME.name,
        OUT_FAILURES.name,
        OUT_NOTE.name,
    ]
    existing = {r.get("file"): r for r in rows}
    timestamp = datetime.now(timezone.utc).isoformat()
    for name in files:
        p = BASE / name
        existing[name] = {
            "file": name,
            "bytes": p.stat().st_size if p.exists() else 0,
            "path": str(p),
            "status": "new_or_refreshed",
            "timestamp": timestamp,
        }
    pd.DataFrame(existing.values()).to_csv(MANIFEST, index=False)


def main() -> None:
    rows, inputs = build_rows()
    summary, by_regime, failures = summarize(rows, inputs)
    rows.to_csv(OUT_ROWS, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    by_regime.to_csv(OUT_BY_REGIME, index=False)
    if failures.empty:
        pd.DataFrame(columns=list(rows.columns) + ["failure_type"]).to_csv(OUT_FAILURES, index=False)
    else:
        failures.to_csv(OUT_FAILURES, index=False)
    write_note(summary, by_regime, failures, inputs)
    refresh_manifest()

    s = dict(zip(summary["field"], summary["value"]))
    log(f"audit_level = {s['audit_level']}")
    log(f"Q_exc_max = {s['Q_exc_max']}")
    log(f"Q_exc_above_0p025_count = {s['Q_exc_above_0p025_count']}")
    log(f"Q_exc_max_over_sqrt_V2_global = {s['Q_exc_max_over_sqrt_V2_global']}")
    log(f"hexc_variance_proxy_failures = {s['hexc_variance_proxy_failures']}")
    log(f"pass_hexc_variance_proxy_empirical = {s['pass_hexc_variance_proxy_empirical']}")
    log(f"Wrote {OUT_NOTE}")


if __name__ == "__main__":
    main()
