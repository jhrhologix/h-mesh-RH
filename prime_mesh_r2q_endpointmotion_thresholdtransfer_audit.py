"""
Prime Mesh R2Q — EndpointMotion ThresholdTransfer Audit.

Tests the row-level gates:
  Q_R2Q > 0.75 => E_theta < 0
  Q_R2Q > 0.75 => Q_delta_D > 0.75
  Q_delta_D > 0.75 => E_theta < 0

The audit intentionally does not rely on the weak global dominance-ratio shortcut.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
P0 = 500_000_000
THRESHOLD = 0.75
POSITIVE_CAP = 0.305
COMPONENT_CAP = 0.055
NEUTRAL_TAUS = [1e-12, 1e-10, 1e-8, 1e-6, 1e-4]

INPUTS = {
    "raw": "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv",
    "sign_bridge": "prime_mesh_r2q_endpointmotion_sign_bridge_rows.csv",
    "threshold": "prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv",
    "epsilon": "prime_mesh_r2q_residual_epsilon_bound_rows.csv",
    "hexc": "prime_mesh_r2q_hexc_bridge_energy_export_rows_v1.csv",
    "finite": "prime_mesh_r2q_finite_certificate_rows.csv",
}

OUT_SCRIPT = "prime_mesh_r2q_endpointmotion_thresholdtransfer_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_endpointmotion_thresholdtransfer_summary.csv"
OUT_ROWS = "prime_mesh_r2q_endpointmotion_thresholdtransfer_rows.csv"
OUT_BY_REGIME = "prime_mesh_r2q_endpointmotion_thresholdtransfer_by_regime.csv"
OUT_COUNTEREX = "prime_mesh_r2q_endpointmotion_thresholdtransfer_counterexamples.csv"
OUT_POSITIVE = "prime_mesh_r2q_endpointmotion_thresholdtransfer_positive_rows.csv"
OUT_NEUTRAL = "prime_mesh_r2q_endpointmotion_thresholdtransfer_neutral_rows.csv"
OUT_FAILURES = "prime_mesh_r2q_endpointmotion_thresholdtransfer_failures.csv"
OUT_THRESHOLD = "prime_mesh_r2q_endpointmotion_thresholdtransfer_threshold_rows.csv"
OUT_FORBIDDEN = "prime_mesh_r2q_endpointmotion_thresholdtransfer_forbidden_rows.csv"
OUT_GAP = "prime_mesh_r2q_endpointmotion_thresholdtransfer_gap_scan.csv"
OUT_DOC = "Prime_Mesh_R2Q_EndpointMotion_ThresholdTransfer_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"


def norm_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes"}


def get_col(df: pd.DataFrame, aliases: list[str]) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    for alias in aliases:
        if alias.lower() in cols:
            return cols[alias.lower()]
    return None


def series_or_nan(df: pd.DataFrame, aliases: list[str]) -> pd.Series:
    col = get_col(df, aliases)
    if col is None:
        return pd.Series(np.nan, index=df.index)
    return pd.to_numeric(df[col], errors="coerce")


def bool_series(df: pd.DataFrame, aliases: list[str]) -> pd.Series:
    col = get_col(df, aliases)
    if col is None:
        return pd.Series(False, index=df.index)
    return df[col].apply(norm_bool)


def read_inputs() -> tuple[dict[str, pd.DataFrame], list[str], list[str]]:
    used: dict[str, pd.DataFrame] = {}
    missing: list[str] = []
    for key, name in INPUTS.items():
        path = BASE / name
        if path.exists():
            used[key] = pd.read_csv(path, low_memory=False)
        else:
            missing.append(name)
    required_missing = [INPUTS["raw"]] if "raw" not in used else []
    if required_missing:
        raise FileNotFoundError(f"Missing required canonical row source: {required_missing}")
    return used, [INPUTS[k] for k in used], missing


def build_rows(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    raw = dfs["raw"].copy()
    rows = pd.DataFrame(index=raw.index)

    rows["candidate_id"] = raw[get_col(raw, ["candidate_id", "row_id", "id"])].astype(str)
    rows["block_id"] = series_or_nan(raw, ["block_id"]).astype("Int64")
    rows["x"] = series_or_nan(raw, ["x"])
    rows["y"] = series_or_nan(raw, ["y"])
    rows["h"] = series_or_nan(raw, ["h"])
    rows["p_star"] = series_or_nan(raw, ["p_star", "pstar"])
    rows["post_P0_flag"] = bool_series(raw, ["post_P0_flag", "post_P0"])
    rows["post_P0_by_pstar"] = rows["p_star"] >= P0
    rows["finite_certified_flag"] = bool_series(raw, ["finite_certificate_flag", "finite_certified_flag", "finite_zone_flag"])
    rows["finite_zone_flag"] = bool_series(raw, ["finite_zone_flag"])
    rows["threshold_relevant_flag"] = bool_series(raw, ["threshold_relevant_flag", "threshold_relevant"])
    rows["forbidden_flag"] = bool_series(raw, ["forbidden_flag", "forbidden"])
    rows["near_forbidden_flag"] = bool_series(raw, ["near_forbidden_flag", "near_forbidden"])
    rows["positive_harmless_flag"] = bool_series(raw, ["positive_harmless_flag"])
    rows["negative_transfer_flag"] = bool_series(raw, ["negative_transfer_flag"])
    rows["row_regime"] = raw[get_col(raw, ["row_status", "row_regime", "classification"])].astype(str)

    rows["Q_R2Q"] = series_or_nan(raw, ["Q_R2Q", "Q_r2q", "Q", "Q_total", "raw_Q_R2Q"])
    rows["Q_delta_D"] = series_or_nan(raw, ["Q_delta_D", "Q_DeltaD", "Q_Delta_D", "Q_dD", "Q_endpoint"])
    rows["Q_exc"] = series_or_nan(raw, ["Q_exc", "Q_hexc", "Q_energy_L2"])
    rows["epsilon"] = series_or_nan(raw, ["epsilon", "eps", "residual_epsilon", "formula_residual"])
    rows["E_theta"] = series_or_nan(raw, ["E_theta", "Etheta", "theta_error", "endpoint_motion", "E_endpoint"])

    # Prefer residual-epsilon audit's epsilon when available because it carries the explicit exported value.
    if "epsilon" in dfs:
        eps = dfs["epsilon"].copy()
        eps_id = get_col(eps, ["candidate_id"])
        if eps_id is not None:
            eps_cols = [c for c in ["candidate_id", "epsilon", "epsilon_abs"] if c in eps.columns]
            if "epsilon" in eps_cols:
                rows = rows.merge(eps[eps_cols].rename(columns={"epsilon": "epsilon_audit"}), on="candidate_id", how="left")
                rows["epsilon"] = rows["epsilon_audit"].combine_first(rows["epsilon"])
                rows = rows.drop(columns=["epsilon_audit"])

    rows["Q_R2Q_recon"] = rows["Q_delta_D"] + rows["Q_exc"] + rows["epsilon"]
    rows["Q_R2Q_reconstruction_error"] = (rows["Q_R2Q"] - rows["Q_R2Q_recon"]).abs()
    rows["E_theta_sign"] = np.select(
        [rows["E_theta"] > 0, rows["E_theta"] < 0],
        ["positive", "negative"],
        default="neutral",
    )

    rows["Q_R2Q_gt_0p75"] = rows["Q_R2Q"] > THRESHOLD
    rows["Q_delta_D_gt_0p75"] = rows["Q_delta_D"] > THRESHOLD
    rows["E_theta_positive"] = rows["E_theta"] > 0
    rows["E_theta_nonnegative"] = rows["E_theta"] >= 0
    rows["E_theta_negative"] = rows["E_theta"] < 0
    rows["positive_harmless_bound"] = rows["Q_R2Q"] <= POSITIVE_CAP
    rows["positive_subthreshold_bound"] = rows["Q_R2Q"] < THRESHOLD
    rows["Q_R2Q_minus_Q_delta_D"] = rows["Q_R2Q"] - rows["Q_delta_D"]
    rows["Q_exc_plus_abs_epsilon"] = rows["Q_exc"] + rows["epsilon"].abs()
    rows["direct_threshold_sign_counterexample"] = rows["Q_R2Q_gt_0p75"] & rows["E_theta_nonnegative"]
    rows["direct_delta_counterexample"] = rows["Q_R2Q_gt_0p75"] & (rows["Q_delta_D"] <= THRESHOLD)
    rows["endpoint_sign_bridge_counterexample"] = rows["Q_delta_D_gt_0p75"] & rows["E_theta_nonnegative"]
    rows["positive_harmless_counterexample_0p305"] = rows["E_theta_positive"] & (rows["Q_R2Q"] > POSITIVE_CAP)
    rows["positive_harmless_counterexample_0p75"] = rows["E_theta_positive"] & (rows["Q_R2Q"] >= THRESHOLD)
    rows["thresholdtransfer_failure_flag"] = (
        rows["direct_threshold_sign_counterexample"]
        | rows["direct_delta_counterexample"]
        | rows["endpoint_sign_bridge_counterexample"]
        | rows["positive_harmless_counterexample_0p75"]
    )
    rows["Q_R2Q_bin"] = pd.cut(rows["Q_R2Q"], [-np.inf, 0.305, 0.75, 0.805, 1.0, np.inf]).astype(str)
    rows["Q_delta_D_bin"] = pd.cut(rows["Q_delta_D"], [-np.inf, 0.25, 0.75, 1.0, np.inf]).astype(str)
    return rows


def count_true(s: pd.Series) -> int:
    return int(s.fillna(False).sum())


def max_or_nan(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float(s.max()) if len(s) else float("nan")


def min_or_nan(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float(s.min()) if len(s) else float("nan")


def subset_stats(rows: pd.DataFrame, mask: pd.Series, prefix: str) -> dict[str, object]:
    sub = rows[mask.fillna(False)]
    return {
        f"{prefix}_count": len(sub),
        f"{prefix}_Q_R2Q_max": max_or_nan(sub["Q_R2Q"]),
        f"{prefix}_Q_R2Q_min": min_or_nan(sub["Q_R2Q"]),
        f"{prefix}_Q_delta_D_min": min_or_nan(sub["Q_delta_D"]),
        f"{prefix}_E_theta_max": max_or_nan(sub["E_theta"]),
        f"{prefix}_positive_E_theta_count": count_true(sub["E_theta_positive"]),
        f"{prefix}_nonnegative_E_theta_count": count_true(sub["E_theta_nonnegative"]),
        f"{prefix}_Q_delta_D_le_0p75_count": int((sub["Q_delta_D"] <= THRESHOLD).sum()),
    }


def neutral_scan(rows: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for tau in NEUTRAL_TAUS:
        sub = rows[rows["E_theta"].abs() <= tau]
        recs.append(
            {
                "neutral_tau": tau,
                "neutral_count": len(sub),
                "neutral_Q_R2Q_max": max_or_nan(sub["Q_R2Q"]),
                "neutral_Q_R2Q_above_0p75_count": int((sub["Q_R2Q"] > THRESHOLD).sum()),
                "neutral_threshold_relevant_count": count_true(sub["threshold_relevant_flag"]),
                "neutral_forbidden_count": count_true(sub["forbidden_flag"]),
            }
        )
    return pd.DataFrame(recs)


def gap_scan(rows: pd.DataFrame) -> pd.DataFrame:
    thr = rows[rows["Q_R2Q_gt_0p75"]]
    return pd.DataFrame(
        [
            {
                "Q_R2Q_gt_0p75_min": min_or_nan(thr["Q_R2Q"]),
                "Q_R2Q_gt_0p75_gap_min": min_or_nan(thr["Q_R2Q"] - THRESHOLD),
                "Q_R2Q_gt_0p75_count_below_0p805": int((thr["Q_R2Q"] < 0.805).sum()),
                "Q_R2Q_gt_0p75_count_below_0p80": int((thr["Q_R2Q"] < 0.80).sum()),
                "Q_R2Q_gt_0p75_count_below_0p78": int((thr["Q_R2Q"] < 0.78).sum()),
            }
        ]
    )


def choose_next(summary: dict[str, object]) -> tuple[str, str]:
    if (
        summary["pass_direct_threshold_transfer"]
        and summary["pass_direct_delta_threshold"]
        and summary["pass_endpoint_sign_bridge"]
        and summary["pass_positive_subthreshold_0p75"]
    ):
        return "direct_threshold_transfer", "Prime_Mesh_R2Q_EndpointMotion_ThresholdTransfer_Theorem_Target_v1.md"
    if summary["pass_direct_threshold_transfer"] and not summary["pass_direct_delta_threshold"]:
        return "direct_threshold_sign", "Prime_Mesh_R2Q_EndpointMotion_DirectThresholdSign_Theorem_Target_v1.md"
    if summary["pass_threshold_relevant_transfer"]:
        return "dangerous_row_transfer", "Prime_Mesh_R2Q_ThresholdRelevance_DangerousRow_Theorem_Target_v1.md"
    return "repair_needed", "Prime_Mesh_R2Q_EndpointMotion_ThresholdTransfer_Repair_Map_v1.md"


def make_summary(rows: pd.DataFrame, used_files: list[str], missing_files: list[str]) -> pd.DataFrame:
    thr = rows[rows["Q_R2Q_gt_0p75"]]
    dthr = rows[rows["Q_delta_D_gt_0p75"]]
    positive = rows[rows["E_theta_positive"]]
    threshold_relevant = rows[rows["threshold_relevant_flag"]]
    forbidden = rows[rows["forbidden_flag"]]
    neutral = neutral_scan(rows)
    gap = gap_scan(rows).iloc[0]

    summary: dict[str, object] = {
        "rows": len(rows),
        "post_P0_rows": int(rows["post_P0_by_pstar"].sum()),
        "used_files": ";".join(used_files),
        "missing_expected_files": ";".join(missing_files),
        "Q_R2Q_gt_0p75_count": len(thr),
        "Q_R2Q_gt_0p75_Q_R2Q_min": min_or_nan(thr["Q_R2Q"]),
        "Q_R2Q_gt_0p75_Q_delta_D_min": min_or_nan(thr["Q_delta_D"]),
        "Q_R2Q_gt_0p75_E_theta_max": max_or_nan(thr["E_theta"]),
        "Q_R2Q_gt_0p75_positive_E_theta_count": count_true(thr["E_theta_positive"]),
        "Q_R2Q_gt_0p75_nonnegative_E_theta_count": count_true(thr["E_theta_nonnegative"]),
        "Q_R2Q_gt_0p75_Q_delta_D_le_0p75_count": int((thr["Q_delta_D"] <= THRESHOLD).sum()),
        "pass_direct_threshold_transfer": len(thr[thr["E_theta_nonnegative"]]) == 0,
        "pass_direct_delta_threshold": len(thr[thr["Q_delta_D"] <= THRESHOLD]) == 0,
        "Q_delta_D_gt_0p75_count": len(dthr),
        "Q_delta_D_gt_0p75_E_theta_max": max_or_nan(dthr["E_theta"]),
        "Q_delta_D_gt_0p75_positive_E_theta_count": count_true(dthr["E_theta_positive"]),
        "Q_delta_D_gt_0p75_nonnegative_E_theta_count": count_true(dthr["E_theta_nonnegative"]),
        "pass_endpoint_sign_bridge": len(dthr[dthr["E_theta_nonnegative"]]) == 0,
        "positive_E_theta_count": len(positive),
        "positive_E_theta_Q_R2Q_max": max_or_nan(positive["Q_R2Q"]),
        "positive_E_theta_Q_delta_D_max": max_or_nan(positive["Q_delta_D"]),
        "positive_E_theta_Q_exc_max": max_or_nan(positive["Q_exc"]),
        "positive_E_theta_epsilon_abs_max": max_or_nan(positive["epsilon"].abs()),
        "positive_E_theta_Q_R2Q_above_0p305_count": int((positive["Q_R2Q"] > POSITIVE_CAP).sum()),
        "positive_E_theta_Q_R2Q_above_0p75_count": int((positive["Q_R2Q"] >= THRESHOLD).sum()),
        "pass_positive_harmless_0p305": int((positive["Q_R2Q"] > POSITIVE_CAP).sum()) == 0,
        "pass_positive_subthreshold_0p75": int((positive["Q_R2Q"] >= THRESHOLD).sum()) == 0,
        "neutral_1e_minus_8_count": int(neutral.loc[neutral["neutral_tau"] == 1e-8, "neutral_count"].iloc[0]),
        "neutral_1e_minus_8_Q_R2Q_max": float(neutral.loc[neutral["neutral_tau"] == 1e-8, "neutral_Q_R2Q_max"].iloc[0]),
        "neutral_1e_minus_8_Q_R2Q_above_0p75_count": int(
            neutral.loc[neutral["neutral_tau"] == 1e-8, "neutral_Q_R2Q_above_0p75_count"].iloc[0]
        ),
        "threshold_gap_min": gap["Q_R2Q_gt_0p75_gap_min"],
        "Q_R2Q_gt_0p75_count_below_0p805": int(gap["Q_R2Q_gt_0p75_count_below_0p805"]),
        "Q_R2Q_gt_0p75_count_below_0p80": int(gap["Q_R2Q_gt_0p75_count_below_0p80"]),
        "Q_R2Q_gt_0p75_count_below_0p78": int(gap["Q_R2Q_gt_0p75_count_below_0p78"]),
        "Q_exc_max_on_threshold_rows": max_or_nan(thr["Q_exc"]),
        "epsilon_abs_max_on_threshold_rows": max_or_nan(thr["epsilon"].abs()),
        "Q_exc_plus_abs_epsilon_max_on_threshold_rows": max_or_nan(thr["Q_exc_plus_abs_epsilon"]),
        "Q_R2Q_minus_Q_delta_D_max_on_threshold_rows": max_or_nan(thr["Q_R2Q_minus_Q_delta_D"]),
        "component_cap_0p055_pass_on_threshold_rows": bool((thr["Q_R2Q_minus_Q_delta_D"] <= COMPONENT_CAP).all()),
    }
    summary.update(subset_stats(rows, rows["threshold_relevant_flag"], "threshold_relevant"))
    summary["pass_threshold_relevant_transfer"] = (
        len(threshold_relevant[threshold_relevant["E_theta_nonnegative"]]) == 0
        and len(threshold_relevant[threshold_relevant["Q_delta_D"] <= THRESHOLD]) == 0
    )
    summary.update(subset_stats(rows, rows["forbidden_flag"], "forbidden"))
    summary["pass_forbidden_transfer"] = (
        len(forbidden[forbidden["E_theta_nonnegative"]]) == 0
        and len(forbidden[forbidden["Q_delta_D"] <= THRESHOLD]) == 0
    )
    summary["thresholdtransfer_failures"] = int(rows["thresholdtransfer_failure_flag"].sum())
    summary["pass_endpointmotion_thresholdtransfer_empirical"] = (
        summary["pass_direct_threshold_transfer"]
        and summary["pass_endpoint_sign_bridge"]
        and summary["pass_positive_subthreshold_0p75"]
    )
    theorem, next_file = choose_next(summary)
    summary["best_thresholdtransfer_theorem_form"] = theorem
    summary["recommended_next_file"] = next_file
    return pd.DataFrame([summary])


def by_regime(rows: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for field in [
        "post_P0_by_pstar",
        "finite_certified_flag",
        "row_regime",
        "threshold_relevant_flag",
        "forbidden_flag",
        "E_theta_sign",
        "Q_R2Q_bin",
        "Q_delta_D_bin",
    ]:
        agg = (
            rows.groupby(field, dropna=False)
            .agg(
                rows=("candidate_id", "count"),
                Q_R2Q_max=("Q_R2Q", "max"),
                Q_delta_D_min=("Q_delta_D", "min"),
                E_theta_max=("E_theta", "max"),
                positive_E_theta_count=("E_theta_positive", "sum"),
                nonnegative_E_theta_count=("E_theta_nonnegative", "sum"),
                threshold_failures=("direct_threshold_sign_counterexample", "sum"),
                delta_failures=("direct_delta_counterexample", "sum"),
                positive_harmless_failures=("positive_harmless_counterexample_0p305", "sum"),
            )
            .reset_index()
            .rename(columns={field: "regime_value"})
        )
        agg.insert(0, "regime_field", field)
        frames.append(agg)
    return pd.concat(frames, ignore_index=True)


def counterexamples(rows: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "candidate_id",
        "p_star",
        "h",
        "row_regime",
        "Q_R2Q",
        "Q_delta_D",
        "Q_exc",
        "epsilon",
        "Q_R2Q_recon",
        "Q_R2Q_reconstruction_error",
        "E_theta",
        "threshold_relevant_flag",
        "forbidden_flag",
        "finite_certified_flag",
    ]
    parts = []
    cases = {
        "direct_threshold_sign": rows["direct_threshold_sign_counterexample"],
        "direct_delta": rows["direct_delta_counterexample"],
        "endpoint_sign_bridge": rows["endpoint_sign_bridge_counterexample"],
        "positive_harmless_0p305": rows["positive_harmless_counterexample_0p305"],
        "positive_harmless_0p75": rows["positive_harmless_counterexample_0p75"],
    }
    for name, mask in cases.items():
        sub = rows[mask.fillna(False)][cols].copy()
        if len(sub):
            sub.insert(0, "counterexample_type", name)
            parts.append(sub)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["counterexample_type"] + cols)


def write_doc(summary: pd.DataFrame, rows: pd.DataFrame, cex: pd.DataFrame, neutral: pd.DataFrame) -> None:
    s = summary.iloc[0]
    threshold_rows = rows[rows["Q_R2Q_gt_0p75"]].sort_values("Q_R2Q", ascending=False).head(12)
    dangerous = rows[rows["threshold_relevant_flag"]].sort_values("Q_R2Q", ascending=False).head(12)
    lines = [
        "# Prime Mesh R2Q — EndpointMotion ThresholdTransfer Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "Test `Q_R2Q > 0.75 => E_theta < 0` and supporting gates without relying on the weak global dominance-ratio shortcut.",
        "",
        "## 2. Summary",
        "",
        f"- Rows: `{int(s['rows'])}`; post-P0 rows: `{int(s['post_P0_rows'])}`.",
        f"- `Q_R2Q > 0.75` rows: `{int(s['Q_R2Q_gt_0p75_count'])}`.",
        f"- Direct threshold transfer: `{bool(s['pass_direct_threshold_transfer'])}`.",
        f"- Direct delta threshold: `{bool(s['pass_direct_delta_threshold'])}`.",
        f"- Endpoint sign bridge: `{bool(s['pass_endpoint_sign_bridge'])}`.",
        f"- Positive harmlessness `Q_R2Q <= 0.305`: `{bool(s['pass_positive_harmless_0p305'])}`.",
        f"- Neutral `1e-8` threshold hits: `{int(s['neutral_1e_minus_8_Q_R2Q_above_0p75_count'])}`.",
        f"- Recommended theorem form: `{s['best_thresholdtransfer_theorem_form']}`.",
        "",
        "## 3. Threshold Rows",
        "",
        "| candidate | p_star | Q_R2Q | Q_delta_D | E_theta | threshold_relevant | forbidden |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in threshold_rows.iterrows():
        lines.append(
            f"| {r['candidate_id']} | {r['p_star']:.0f} | {r['Q_R2Q']:.8g} | {r['Q_delta_D']:.8g} | "
            f"{r['E_theta']:.8g} | {bool(r['threshold_relevant_flag'])} | {bool(r['forbidden_flag'])} |"
        )
    lines += [
        "",
        "## 4. Dangerous / Threshold-Relevant Rows",
        "",
        "| candidate | Q_R2Q | Q_delta_D | E_theta | row_regime |",
        "|---:|---:|---:|---:|---|",
    ]
    for _, r in dangerous.iterrows():
        lines.append(
            f"| {r['candidate_id']} | {r['Q_R2Q']:.8g} | {r['Q_delta_D']:.8g} | "
            f"{r['E_theta']:.8g} | {r['row_regime']} |"
        )
    lines += [
        "",
        "## 5. Positive Rows",
        "",
        f"`positive_E_theta_count = {int(s['positive_E_theta_count'])}`; "
        f"`positive_E_theta_Q_R2Q_max = {s['positive_E_theta_Q_R2Q_max']:.12g}`.",
        "",
        "## 6. Neutral Rows",
        "",
        "| tau | rows | Q_R2Q max | above 0.75 | threshold relevant | forbidden |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in neutral.iterrows():
        lines.append(
            f"| {r['neutral_tau']:.0e} | {int(r['neutral_count'])} | {r['neutral_Q_R2Q_max']:.8g} | "
            f"{int(r['neutral_Q_R2Q_above_0p75_count'])} | {int(r['neutral_threshold_relevant_count'])} | "
            f"{int(r['neutral_forbidden_count'])} |"
        )
    lines += [
        "",
        "## 7. Counterexamples",
        "",
        f"Counterexample rows emitted: `{len(cex)}`.",
        "",
    ]
    if len(cex):
        lines += [
            "| type | candidate | Q_R2Q | Q_delta_D | E_theta |",
            "|---|---:|---:|---:|---:|",
        ]
        for _, r in cex.head(20).iterrows():
            lines.append(
                f"| {r['counterexample_type']} | {r['candidate_id']} | {r['Q_R2Q']:.8g} | "
                f"{r['Q_delta_D']:.8g} | {r['E_theta']:.8g} |"
            )
    else:
        lines.append("No counterexamples for the tested gates.")
    lines += [
        "",
        "## 8. Recommended Next File",
        "",
        f"`{s['recommended_next_file']}`",
        "",
        "## 9. Outputs",
        "",
        "```text",
        OUT_SCRIPT,
        OUT_SUMMARY,
        OUT_ROWS,
        OUT_BY_REGIME,
        OUT_COUNTEREX,
        OUT_POSITIVE,
        OUT_NEUTRAL,
        OUT_FAILURES,
        OUT_THRESHOLD,
        OUT_FORBIDDEN,
        OUT_GAP,
        "```",
        "",
        "*AI documentation pass: GPT-5.5*",
    ]
    (BASE / OUT_DOC).write_text("\n".join(lines), encoding="utf-8")


def update_manifest(filenames: list[str]) -> None:
    path = BASE / OUT_MANIFEST
    now = datetime.now().isoformat(timespec="seconds")
    old = pd.read_csv(path).to_dict("records") if path.exists() else []
    names = set(filenames)
    rows = [row for row in old if row.get("filename") not in names]
    for name in filenames:
        p = BASE / name
        rows.append(
            {
                "filename": name,
                "path": str(p),
                "bytes": p.stat().st_size if p.exists() else 0,
                "status": "new",
                "updated_at": now,
                "note": "EndpointMotion ThresholdTransfer audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    dfs, used_files, missing_files = read_inputs()
    rows = build_rows(dfs)
    summary = make_summary(rows, used_files, missing_files)
    regime = by_regime(rows)
    cex = counterexamples(rows)
    neutral = neutral_scan(rows)
    failures = rows[rows["thresholdtransfer_failure_flag"]].copy()
    threshold_rows = rows[rows["Q_R2Q_gt_0p75"]].copy()
    forbidden_rows = rows[rows["forbidden_flag"]].copy()
    gap = gap_scan(rows)

    rows.to_csv(BASE / OUT_ROWS, index=False)
    summary.to_csv(BASE / OUT_SUMMARY, index=False)
    regime.to_csv(BASE / OUT_BY_REGIME, index=False)
    cex.to_csv(BASE / OUT_COUNTEREX, index=False)
    rows[rows["E_theta_positive"]].to_csv(BASE / OUT_POSITIVE, index=False)
    neutral.to_csv(BASE / OUT_NEUTRAL, index=False)
    failures.to_csv(BASE / OUT_FAILURES, index=False)
    threshold_rows.to_csv(BASE / OUT_THRESHOLD, index=False)
    forbidden_rows.to_csv(BASE / OUT_FORBIDDEN, index=False)
    gap.to_csv(BASE / OUT_GAP, index=False)
    write_doc(summary, rows, cex, neutral)
    update_manifest(
        [
            OUT_SCRIPT,
            OUT_SUMMARY,
            OUT_ROWS,
            OUT_BY_REGIME,
            OUT_COUNTEREX,
            OUT_POSITIVE,
            OUT_NEUTRAL,
            OUT_FAILURES,
            OUT_THRESHOLD,
            OUT_FORBIDDEN,
            OUT_GAP,
            OUT_DOC,
        ]
    )

    s = summary.iloc[0].to_dict()
    print("EndpointMotion ThresholdTransfer audit complete.")
    print("Used files:", "; ".join(used_files))
    print("Missing expected files:", "; ".join(missing_files) if missing_files else "none")
    for key in [
        "rows",
        "post_P0_rows",
        "Q_R2Q_gt_0p75_count",
        "Q_R2Q_gt_0p75_Q_delta_D_min",
        "Q_R2Q_gt_0p75_E_theta_max",
        "pass_direct_threshold_transfer",
        "pass_direct_delta_threshold",
        "pass_endpoint_sign_bridge",
        "pass_positive_harmless_0p305",
        "pass_positive_subthreshold_0p75",
        "thresholdtransfer_failures",
        "best_thresholdtransfer_theorem_form",
        "recommended_next_file",
    ]:
        print(f"{key}: {s[key]}")


if __name__ == "__main__":
    main()
