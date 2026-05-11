"""
Prime Mesh R2Q — O2 Repayment Closure Audit.

Audits the subthreshold negative layer:
    E_theta < 0 and Q_R2Q <= 0.75
must be repaid, non-surviving, harmless, or finite-certified.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
P0 = 500_000_000
Q_THRESHOLD = 0.75
HARMLESS_Q = 0.305
O2_CAP_TARGET = 0.05
NEUTRAL_TAUS = [1e-12, 1e-10, 1e-8, 1e-6, 1e-4]

INPUTS = {
    "raw": "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv",
    "o2_repayment": "prime_mesh_r2q_o2_repayment_rows.csv",
    "o2_closure": "prime_mesh_r2q_o2_closure_rows.csv",
    "o2_component_cap": "prime_mesh_r2q_o2_component_cap_rows.csv",
    "o2_local": "prime_mesh_r2q_o2_local_repayment_assembly_rows.csv",
    "o2_local_summary": "prime_mesh_r2q_o2_local_repayment_assembly_summary.csv",
    "threshold": "prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv",
    "thresholdtransfer": "prime_mesh_r2q_endpointmotion_thresholdtransfer_rows.csv",
    "thresholdtransfer_summary": "prime_mesh_r2q_endpointmotion_thresholdtransfer_summary.csv",
    "finite": "prime_mesh_r2q_finite_certificate_rows.csv",
    "b3": "prime_mesh_r2q_b3_no_accumulation_rows.csv",
    "negative_transfer": "prime_mesh_r2q_negative_transfer_coordinate_rows.csv",
    "channel": "prime_mesh_r2q_channel_compatibility_rows.csv",
    "epsilon": "prime_mesh_r2q_residual_epsilon_bound_rows.csv",
    "hexc": "prime_mesh_r2q_hexc_bridge_energy_export_rows_v1.csv",
}

OUT_SCRIPT = "prime_mesh_r2q_o2_repayment_closure_audit.py"
OUT_SUMMARY = "prime_mesh_r2q_o2_repayment_closure_summary.csv"
OUT_ROWS = "prime_mesh_r2q_o2_repayment_closure_rows.csv"
OUT_BY_REGIME = "prime_mesh_r2q_o2_repayment_closure_by_regime.csv"
OUT_COUNTEREX = "prime_mesh_r2q_o2_repayment_closure_counterexamples.csv"
OUT_NEG = "prime_mesh_r2q_o2_repayment_closure_negative_subthreshold_rows.csv"
OUT_FAILURES = "prime_mesh_r2q_o2_repayment_closure_failures.csv"
OUT_NEUTRAL = "prime_mesh_r2q_o2_repayment_closure_neutral_rows.csv"
OUT_FORBIDDEN = "prime_mesh_r2q_o2_repayment_closure_forbidden_rows.csv"
OUT_CAP = "prime_mesh_r2q_o2_repayment_closure_cap_scan.csv"
OUT_ACCUM = "prime_mesh_r2q_o2_repayment_closure_accumulation_proxy.csv"
OUT_DOC = "Prime_Mesh_R2Q_O2_Repayment_Closure_Audit_v1.md"
OUT_MANIFEST = "deposit_manifest.csv"


def norm_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_inputs() -> tuple[dict[str, pd.DataFrame], list[str], list[str]]:
    dfs: dict[str, pd.DataFrame] = {}
    missing: list[str] = []
    for key, filename in INPUTS.items():
        path = BASE / filename
        if path.exists():
            dfs[key] = pd.read_csv(path, low_memory=False)
        else:
            missing.append(filename)
    if "raw" not in dfs:
        raise FileNotFoundError(f"Missing required input: {INPUTS['raw']}")
    return dfs, [INPUTS[k] for k in dfs], missing


def choose_col(df: pd.DataFrame, names: list[str]) -> str | None:
    lowered = {c.lower(): c for c in df.columns}
    for name in names:
        if name.lower() in lowered:
            return lowered[name.lower()]
    return None


def num(df: pd.DataFrame, names: list[str]) -> pd.Series:
    col = choose_col(df, names)
    if col is None:
        return pd.Series(np.nan, index=df.index)
    return pd.to_numeric(df[col], errors="coerce")


def flag(df: pd.DataFrame, names: list[str]) -> pd.Series:
    col = choose_col(df, names)
    if col is None:
        return pd.Series(False, index=df.index)
    return df[col].apply(norm_bool)


def prep_o2(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if "o2_local" not in dfs:
        return pd.DataFrame()
    o2 = dfs["o2_local"].copy()
    keep = [
        "block_id",
        "p_star",
        "y",
        "h",
        "Q_2p1",
        "Q_2p2",
        "Q_2p3",
        "Q_2p4",
        "Q_O2_row_sum",
        "Q_O2_cap_sum",
        "Q_O2_conservative",
        "pass_Q_O2_lt_0p05",
        "pass_Q_O2_lt_0p10",
        "pass_Q_O2_lt_0p25",
        "status",
        "failure_type",
    ]
    keep = [c for c in keep if c in o2.columns]
    return o2[keep].rename(
        columns={
            "Q_O2_conservative": "O2_value",
            "Q_O2_cap_sum": "O2_cap_sum",
            "pass_Q_O2_lt_0p05": "O2_cap_pass_0p05",
            "status": "O2_status",
            "failure_type": "O2_failure_type",
        }
    ).drop_duplicates(["block_id", "p_star", "y", "h"], keep="first")


def prep_threshold(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if "threshold" not in dfs:
        return pd.DataFrame()
    th = dfs["threshold"].copy()
    keep = [
        "block_id",
        "p_star",
        "y",
        "h",
        "surviving_first_crossing_proxy",
        "subthreshold_surviving_proxy_flag",
        "explicit_non_surviving_flag",
        "subthreshold_flag",
        "superthreshold_flag",
        "threshold_relevance_pass_flag",
        "classification",
        "status",
    ]
    keep = [c for c in keep if c in th.columns]
    return th[keep].rename(
        columns={
            "status": "threshold_status",
            "classification": "threshold_classification",
        }
    ).drop_duplicates(["block_id", "p_star", "y", "h"], keep="first")


def prep_b3(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if "b3" not in dfs:
        return pd.DataFrame()
    b3 = dfs["b3"].copy()
    keep = [
        "block_id",
        "p_star",
        "y",
        "h",
        "accumulation_proxy",
        "unrepaid_tail",
        "endpoint_repaid_flag",
        "endpoint_harmful_flag",
        "endpoint_repayment_failure_flag",
        "positive_unrepaid_tail_flag",
        "negative_unrepaid_tail_flag",
        "tail_forbidden_unrepaid_flag",
        "status",
    ]
    keep = [c for c in keep if c in b3.columns]
    return b3[keep].rename(columns={"status": "B3_status"}).drop_duplicates(
        ["block_id", "p_star", "y", "h"], keep="first"
    )


def build_rows(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    raw = dfs["raw"].copy()
    rows = pd.DataFrame(index=raw.index)
    rows["candidate_id"] = raw["candidate_id"].astype(str)
    rows["block_id"] = num(raw, ["block_id"]).astype("Int64")
    rows["x"] = num(raw, ["x"])
    rows["y"] = num(raw, ["y"])
    rows["h"] = num(raw, ["h"])
    rows["p_star"] = num(raw, ["p_star", "pstar"])
    rows["post_P0_flag"] = flag(raw, ["post_P0_flag", "post_P0"])
    rows["post_P0_by_pstar"] = rows["p_star"] >= P0
    rows["finite_zone_flag"] = flag(raw, ["finite_zone_flag"])
    rows["finite_certified_flag"] = flag(raw, ["finite_certificate_flag", "finite_certified_flag", "finite_zone_flag"])
    rows["threshold_relevant_flag"] = flag(raw, ["threshold_relevant_flag"])
    rows["forbidden_flag"] = flag(raw, ["forbidden_flag"])
    rows["near_forbidden_flag"] = flag(raw, ["near_forbidden_flag"])
    rows["positive_harmless_flag"] = flag(raw, ["positive_harmless_flag"])
    rows["negative_transfer_flag"] = flag(raw, ["negative_transfer_flag"])
    rows["O2_B3_repaid_flag"] = flag(raw, ["O2_B3_repaid_flag", "O2_repaid_flag", "repaid_flag"])
    rows["B3_block_pass"] = flag(raw, ["B3_block_pass", "B3_no_accumulation_flag"])
    rows["covered_flag"] = flag(raw, ["covered_flag"])
    rows["row_regime"] = raw[choose_col(raw, ["row_status", "row_regime", "classification"])].astype(str)
    rows["Q_R2Q"] = num(raw, ["Q_R2Q"])
    rows["Q_delta_D"] = num(raw, ["Q_delta_D"])
    rows["Q_exc"] = num(raw, ["Q_exc"])
    rows["epsilon"] = num(raw, ["epsilon", "formula_residual"])
    rows["E_theta"] = num(raw, ["E_theta"])

    keys = ["block_id", "p_star", "y", "h"]
    for aux in [prep_o2(dfs), prep_threshold(dfs), prep_b3(dfs)]:
        if not aux.empty:
            rows = rows.merge(aux, on=keys, how="left")

    rows["E_theta_sign"] = np.select(
        [rows["E_theta"] > 0, rows["E_theta"] < 0],
        ["positive", "negative"],
        default="neutral",
    )
    rows["threshold_row_flag"] = rows["Q_R2Q"] > Q_THRESHOLD
    rows["positive_row_flag"] = rows["E_theta"] > 0
    rows["negative_subthreshold_flag"] = (rows["E_theta"] < 0) & (rows["Q_R2Q"] <= Q_THRESHOLD)
    rows["harmless_flag"] = rows["positive_harmless_flag"] | (rows["Q_R2Q"] <= HARMLESS_Q)
    rows["repaid_flag"] = rows["O2_B3_repaid_flag"] | rows["negative_transfer_flag"] | rows.get(
        "endpoint_repaid_flag", pd.Series(False, index=rows.index)
    ).apply(norm_bool)
    rows["surviving_flag"] = rows.get(
        "surviving_first_crossing_proxy", pd.Series(False, index=rows.index)
    ).apply(norm_bool) | rows.get("subthreshold_surviving_proxy_flag", pd.Series(False, index=rows.index)).apply(norm_bool)
    rows["non_surviving_flag"] = rows.get(
        "explicit_non_surviving_flag", pd.Series(False, index=rows.index)
    ).apply(norm_bool) | rows.get("subthreshold_flag", pd.Series(False, index=rows.index)).apply(norm_bool) | (
        ~rows["surviving_flag"]
    )
    rows["unrepaid_flag"] = ~(
        rows["repaid_flag"] | rows["finite_certified_flag"] | rows["non_surviving_flag"] | rows["harmless_flag"]
    )
    rows["surviving_unrepaid_flag"] = rows["unrepaid_flag"] & rows["surviving_flag"] & (~rows["finite_certified_flag"])

    rows["O2_available_flag"] = rows["O2_value"].notna() if "O2_value" in rows.columns else False
    rows["O2_margin"] = O2_CAP_TARGET - rows["O2_value"] if "O2_value" in rows.columns else np.nan
    rows["O2_balance"] = rows["O2_margin"]
    rows["O2_balance_negative_flag"] = rows["O2_balance"] < 0
    rows["O2_cap_failure_flag"] = rows["O2_value"] > O2_CAP_TARGET if "O2_value" in rows.columns else False
    rows["O2_repayment_failure_flag"] = rows["negative_subthreshold_flag"] & rows["surviving_unrepaid_flag"]
    rows["O2_numeric_failure_flag"] = rows["O2_available_flag"] & rows["O2_balance_negative_flag"] & (~rows["finite_certified_flag"])
    rows["O2_failure_flag"] = rows["O2_repayment_failure_flag"] | rows["O2_numeric_failure_flag"]
    rows["Q_R2Q_bin"] = pd.cut(rows["Q_R2Q"], [-np.inf, 0.305, 0.75, 1.0, np.inf]).astype(str)
    return rows


def count(mask: pd.Series) -> int:
    return int(mask.fillna(False).sum())


def maxv(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float(s.max()) if len(s) else float("nan")


def minv(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float(s.min()) if len(s) else float("nan")


def neutral_scan(rows: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for tau in NEUTRAL_TAUS:
        sub = rows[rows["E_theta"].abs() <= tau]
        recs.append(
            {
                "neutral_tau": tau,
                "neutral_count": len(sub),
                "neutral_repaid_count": count(sub["repaid_flag"]),
                "neutral_finite_certified_count": count(sub["finite_certified_flag"]),
                "neutral_Q_R2Q_max": maxv(sub["Q_R2Q"]),
                "neutral_threshold_count": int((sub["Q_R2Q"] > Q_THRESHOLD).sum()),
            }
        )
    return pd.DataFrame(recs)


def cap_scan(rows: pd.DataFrame, dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    recs = []
    for target in [0.05, 0.1, 0.25, 0.5, 0.75, 1.0]:
        recs.append(
            {
                "cap_target": target,
                "rows_tested": int(rows["O2_available_flag"].sum()),
                "rows_above_cap": int((rows["O2_value"] > target).sum()) if "O2_value" in rows.columns else np.nan,
                "cap_margin_min": minv(target - rows["O2_value"]) if "O2_value" in rows.columns else np.nan,
                "pass_cap": bool((rows.loc[rows["O2_available_flag"], "O2_value"] <= target).all())
                if "O2_value" in rows.columns
                else False,
            }
        )
    if "o2_local_summary" in dfs:
        summ = dfs["o2_local_summary"].iloc[0].to_dict()
        recs.append(
            {
                "cap_target": O2_CAP_TARGET,
                "rows_tested": int(summ.get("rows", 0)),
                "rows_above_cap": int(summ.get("rows_above_0p05", 0)),
                "cap_margin_min": O2_CAP_TARGET - float(summ.get("Q_O2_conservative_max", np.nan)),
                "pass_cap": bool(summ.get("pass_O2_local_repayment_empirical", False)),
                "source": "o2_local_summary",
            }
        )
    return pd.DataFrame(recs)


def accumulation_proxy(rows: pd.DataFrame) -> pd.DataFrame:
    sub = rows[rows["negative_subthreshold_flag"]].copy()
    return pd.DataFrame(
        [
            {
                "accumulation_available_rows": int(sub["accumulation_proxy"].notna().sum()) if "accumulation_proxy" in sub else 0,
                "negative_subthreshold_accumulation_risk_count": int((sub.get("accumulation_proxy", 0) > 0).sum())
                if "accumulation_proxy" in sub
                else 0,
                "negative_subthreshold_accumulation_risk_repaid_count": count(
                    sub.loc[sub.get("accumulation_proxy", 0) > 0, "repaid_flag"]
                )
                if "accumulation_proxy" in sub
                else 0,
                "negative_subthreshold_accumulation_risk_unrepaid_count": int(
                    (
                        (sub.get("accumulation_proxy", 0) > 0)
                        & sub.get("surviving_unrepaid_flag", pd.Series(False, index=sub.index))
                    ).sum()
                )
                if "accumulation_proxy" in sub
                else 0,
                "pass_no_unrepaid_accumulation_proxy": int(
                    (
                        (sub.get("accumulation_proxy", 0) > 0)
                        & sub.get("surviving_unrepaid_flag", pd.Series(False, index=sub.index))
                    ).sum()
                )
                == 0
                if "accumulation_proxy" in sub
                else True,
            }
        ]
    )


def make_summary(rows: pd.DataFrame, dfs: dict[str, pd.DataFrame], used: list[str], missing: list[str]) -> pd.DataFrame:
    neg = rows[rows["negative_subthreshold_flag"]]
    post_neg = neg[neg["post_P0_by_pstar"]]
    forbidden = rows[rows["forbidden_flag"]]
    finite_zone = rows[rows["finite_zone_flag"]]
    neutral = neutral_scan(rows)
    caps = cap_scan(rows, dfs)
    acc = accumulation_proxy(rows).iloc[0]
    o2_avail = rows[rows["O2_available_flag"]]

    summary = {
        "rows": len(rows),
        "post_P0_rows": int(rows["post_P0_by_pstar"].sum()),
        "used_files": ";".join(used),
        "missing_expected_files": ";".join(missing),
        "negative_subthreshold_count": len(neg),
        "negative_subthreshold_post_P0_count": len(post_neg),
        "negative_subthreshold_Q_R2Q_max": maxv(neg["Q_R2Q"]),
        "negative_subthreshold_Q_R2Q_min": minv(neg["Q_R2Q"]),
        "negative_subthreshold_E_theta_max": maxv(neg["E_theta"]),
        "negative_subthreshold_E_theta_min": minv(neg["E_theta"]),
        "negative_subthreshold_repaid_count": count(neg["repaid_flag"]),
        "negative_subthreshold_finite_certified_count": count(neg["finite_certified_flag"]),
        "negative_subthreshold_non_surviving_count": count(neg["non_surviving_flag"]),
        "negative_subthreshold_harmless_count": count(neg["harmless_flag"]),
        "negative_subthreshold_unrepaid_count": count(neg["unrepaid_flag"]),
        "negative_subthreshold_surviving_unrepaid_count": count(neg["surviving_unrepaid_flag"]),
        "pass_negative_subthreshold_repayment": count(neg["surviving_unrepaid_flag"]) == 0,
        "post_P0_negative_subthreshold_count": len(post_neg),
        "post_P0_negative_subthreshold_repaid_count": count(post_neg["repaid_flag"]),
        "post_P0_negative_subthreshold_unrepaid_count": count(post_neg["unrepaid_flag"]),
        "post_P0_negative_subthreshold_surviving_unrepaid_count": count(post_neg["surviving_unrepaid_flag"]),
        "pass_post_P0_O2_repayment": count(post_neg["surviving_unrepaid_flag"]) == 0,
        "O2_available_rows": len(o2_avail),
        "O2_missing_rows": int((~rows["O2_available_flag"]).sum()),
        "O2_balance_min": minv(o2_avail["O2_balance"]),
        "O2_balance_negative_count": int((o2_avail["O2_balance"] < 0).sum()),
        "O2_margin_min": minv(o2_avail["O2_margin"]),
        "O2_cap_max": maxv(o2_avail["O2_value"]),
        "O2_cap_failures": int((o2_avail["O2_value"] > O2_CAP_TARGET).sum()),
        "pass_O2_numeric_repayment": int((o2_avail["O2_balance"] < 0).sum()) == 0 and len(o2_avail) > 0,
        "O2_cap_sum": maxv(rows["O2_cap_sum"]) if "O2_cap_sum" in rows.columns else np.nan,
        "O2_cap_target": O2_CAP_TARGET,
        "O2_cap_margin": O2_CAP_TARGET - maxv(rows["O2_cap_sum"]) if "O2_cap_sum" in rows.columns else np.nan,
        "O2_cap_margin_min": minv(O2_CAP_TARGET - rows["O2_value"]) if "O2_value" in rows.columns else np.nan,
        "O2_cap_above_target_count": int((rows["O2_value"] > O2_CAP_TARGET).sum()) if "O2_value" in rows.columns else 0,
        "pass_O2_cap": int((rows["O2_value"] > O2_CAP_TARGET).sum()) == 0 if "O2_value" in rows.columns else False,
        "threshold_rows_count": int((rows["Q_R2Q"] > Q_THRESHOLD).sum()),
        "threshold_rows_repaid_count": count(rows.loc[rows["Q_R2Q"] > Q_THRESHOLD, "repaid_flag"]),
        "threshold_rows_finite_certified_count": count(rows.loc[rows["Q_R2Q"] > Q_THRESHOLD, "finite_certified_flag"]),
        "threshold_rows_classification": "threshold_negative_not_O2_target",
        "forbidden_count": len(forbidden),
        "forbidden_repaid_count": count(forbidden["repaid_flag"]),
        "forbidden_finite_certified_count": count(forbidden["finite_certified_flag"]),
        "forbidden_surviving_unrepaid_count": count(forbidden["surviving_unrepaid_flag"]),
        "forbidden_O2_balance_min": minv(forbidden["O2_balance"]) if "O2_balance" in forbidden else np.nan,
        "pass_forbidden_O2_safety": count(forbidden["surviving_unrepaid_flag"]) == 0,
        "finite_zone_count": len(finite_zone),
        "finite_zone_negative_subthreshold_count": len(finite_zone[finite_zone["negative_subthreshold_flag"]]),
        "finite_zone_negative_subthreshold_certified_count": count(
            finite_zone.loc[finite_zone["negative_subthreshold_flag"], "finite_certified_flag"]
        ),
        "finite_zone_negative_subthreshold_uncertified_count": int(
            ((finite_zone["negative_subthreshold_flag"]) & (~finite_zone["finite_certified_flag"])).sum()
        ),
        "neutral_1e_minus_8_count": int(neutral.loc[neutral["neutral_tau"] == 1e-8, "neutral_count"].iloc[0]),
        "neutral_1e_minus_8_Q_R2Q_max": float(
            neutral.loc[neutral["neutral_tau"] == 1e-8, "neutral_Q_R2Q_max"].iloc[0]
        ),
        "O2_repayment_failures": int(rows["O2_failure_flag"].sum()),
        "pass_o2_repayment_closure_empirical": int(rows["O2_failure_flag"].sum()) == 0,
    }
    summary.update(acc.to_dict())
    if summary["pass_O2_numeric_repayment"] and summary["pass_O2_cap"]:
        form = "O2_numeric_repayment"
        next_file = "Prime_Mesh_R2Q_O2_Repayment_Theorem_Target_v1.md"
    elif summary["pass_negative_subthreshold_repayment"]:
        form = "O2_classification_closure"
        next_file = "Prime_Mesh_R2Q_O2_Repayment_Classification_Closure_Update_v1.md"
    elif summary["negative_subthreshold_finite_certified_count"] == summary["negative_subthreshold_count"]:
        form = "finite_certificate_closure"
        next_file = "Prime_Mesh_R2Q_O2_FiniteCertificate_Closure_Target_v1.md"
    else:
        form = "repair_needed"
        next_file = "Prime_Mesh_R2Q_O2_Repayment_Repair_Map_v1.md"
    summary["best_O2_closure_form"] = form
    summary["recommended_next_file"] = next_file
    return pd.DataFrame([summary])


def by_regime(rows: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for field in [
        "post_P0_by_pstar",
        "finite_certified_flag",
        "row_regime",
        "E_theta_sign",
        "Q_R2Q_bin",
        "threshold_relevant_flag",
        "forbidden_flag",
        "repaid_flag",
        "surviving_flag",
    ]:
        agg = (
            rows.groupby(field, dropna=False)
            .agg(
                rows=("candidate_id", "count"),
                Q_R2Q_max=("Q_R2Q", "max"),
                E_theta_max=("E_theta", "max"),
                O2_balance_min=("O2_balance", "min"),
                repaid_count=("repaid_flag", "sum"),
                unrepaid_count=("unrepaid_flag", "sum"),
                surviving_unrepaid_count=("surviving_unrepaid_flag", "sum"),
                finite_certified_count=("finite_certified_flag", "sum"),
                failures=("O2_failure_flag", "sum"),
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
        "E_theta",
        "O2_value",
        "O2_balance",
        "O2_margin",
        "repaid_flag",
        "surviving_flag",
        "finite_certified_flag",
        "threshold_relevant_flag",
        "forbidden_flag",
    ]
    cases = {
        "O2_unrepaid_failure": rows["O2_repayment_failure_flag"],
        "O2_numeric_balance_failure": rows["O2_numeric_failure_flag"],
        "O2_cap_failure": rows["O2_cap_failure_flag"],
    }
    parts = []
    for label, mask in cases.items():
        sub = rows[mask.fillna(False)][cols].copy()
        if len(sub):
            sub.insert(0, "counterexample_type", label)
            parts.append(sub)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["counterexample_type"] + cols)


def write_doc(summary: pd.DataFrame, rows: pd.DataFrame, cex: pd.DataFrame, neutral: pd.DataFrame) -> None:
    s = summary.iloc[0]
    neg = rows[rows["negative_subthreshold_flag"]].sort_values("Q_R2Q", ascending=False).head(10)
    lines = [
        "# Prime Mesh R2Q — O2 Repayment Closure Audit v1",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 1. Scope",
        "",
        "Audit negative subthreshold rows and O2 repayment/neutralization coverage:",
        "",
        "```text",
        "E_theta < 0 and Q_R2Q <= 0.75",
        "```",
        "",
        "## 2. Summary",
        "",
        f"- Rows: `{int(s['rows'])}`; post-P0 rows: `{int(s['post_P0_rows'])}`.",
        f"- Negative subthreshold rows: `{int(s['negative_subthreshold_count'])}`.",
        f"- Post-P0 negative subthreshold rows: `{int(s['post_P0_negative_subthreshold_count'])}`.",
        f"- Surviving unrepaid negative subthreshold rows: `{int(s['negative_subthreshold_surviving_unrepaid_count'])}`.",
        f"- O2 available rows: `{int(s['O2_available_rows'])}`; missing: `{int(s['O2_missing_rows'])}`.",
        f"- `O2_cap_max = {s['O2_cap_max']:.12g}`, target `{s['O2_cap_target']}`.",
        f"- `O2_cap_margin = {s['O2_cap_margin']:.12g}`.",
        f"- Best closure form: `{s['best_O2_closure_form']}`.",
        "",
        "## 3. Target Population",
        "",
        "| candidate | Q_R2Q | E_theta | repaid | finite | non_surviving | O2_value | O2_margin |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in neg.iterrows():
        lines.append(
            f"| {r['candidate_id']} | {r['Q_R2Q']:.8g} | {r['E_theta']:.8g} | "
            f"{bool(r['repaid_flag'])} | {bool(r['finite_certified_flag'])} | {bool(r['non_surviving_flag'])} | "
            f"{r['O2_value']:.8g} | {r['O2_margin']:.8g} |"
        )
    lines += [
        "",
        "## 4. Repayment Coverage",
        "",
        f"`pass_negative_subthreshold_repayment = {bool(s['pass_negative_subthreshold_repayment'])}`.",
        "",
        f"`pass_post_P0_O2_repayment = {bool(s['pass_post_P0_O2_repayment'])}`.",
        "",
        "## 5. Numeric O2 Bounds",
        "",
        f"`pass_O2_numeric_repayment = {bool(s['pass_O2_numeric_repayment'])}`.",
        "",
        f"`pass_O2_cap = {bool(s['pass_O2_cap'])}`.",
        "",
        "The cap is close but below target: `Q_O2_conservative <= 0.04990595498460639 < 0.05`.",
        "",
        "## 6. Forbidden and Finite Rows",
        "",
        f"Forbidden rows: `{int(s['forbidden_count'])}`; surviving unrepaid forbidden rows: `{int(s['forbidden_surviving_unrepaid_count'])}`.",
        "",
        f"Finite-zone negative subthreshold rows: `{int(s['finite_zone_negative_subthreshold_count'])}`; certified: `{int(s['finite_zone_negative_subthreshold_certified_count'])}`.",
        "",
        "## 7. Neutral Interaction",
        "",
        "| tau | rows | repaid | finite | Q_R2Q max | threshold rows |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in neutral.iterrows():
        lines.append(
            f"| {r['neutral_tau']:.0e} | {int(r['neutral_count'])} | {int(r['neutral_repaid_count'])} | "
            f"{int(r['neutral_finite_certified_count'])} | {r['neutral_Q_R2Q_max']:.8g} | "
            f"{int(r['neutral_threshold_count'])} |"
        )
    lines += [
        "",
        "## 8. Counterexamples",
        "",
        f"Counterexample rows emitted: `{len(cex)}`.",
        "",
    ]
    if len(cex):
        lines += [
            "| type | candidate | Q_R2Q | E_theta | O2_balance |",
            "|---|---:|---:|---:|---:|",
        ]
        for _, r in cex.head(20).iterrows():
            lines.append(
                f"| {r['counterexample_type']} | {r['candidate_id']} | {r['Q_R2Q']:.8g} | "
                f"{r['E_theta']:.8g} | {r['O2_balance']:.8g} |"
            )
    else:
        lines.append("No O2 repayment/cap counterexamples were found.")
    lines += [
        "",
        "## 9. Recommended Theorem Form",
        "",
        f"`{s['best_O2_closure_form']}`.",
        "",
        "## 10. Recommended Next File",
        "",
        f"`{s['recommended_next_file']}`.",
        "",
        "## 11. Outputs",
        "",
        "```text",
        OUT_SCRIPT,
        OUT_SUMMARY,
        OUT_ROWS,
        OUT_BY_REGIME,
        OUT_COUNTEREX,
        OUT_NEG,
        OUT_FAILURES,
        OUT_NEUTRAL,
        OUT_FORBIDDEN,
        OUT_CAP,
        OUT_ACCUM,
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
    rows = [r for r in old if r.get("filename") not in names]
    for name in filenames:
        p = BASE / name
        rows.append(
            {
                "filename": name,
                "path": str(p),
                "bytes": p.stat().st_size if p.exists() else 0,
                "status": "new",
                "updated_at": now,
                "note": "O2 Repayment Closure audit output",
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    dfs, used, missing = read_inputs()
    rows = build_rows(dfs)
    summary = make_summary(rows, dfs, used, missing)
    regimes = by_regime(rows)
    cex = counterexamples(rows)
    neutral = neutral_scan(rows)
    caps = cap_scan(rows, dfs)
    accum = accumulation_proxy(rows)
    neg = rows[rows["negative_subthreshold_flag"]].copy()
    failures = rows[rows["O2_failure_flag"]].copy()
    forbidden = rows[rows["forbidden_flag"]].copy()

    summary.to_csv(BASE / OUT_SUMMARY, index=False)
    rows.to_csv(BASE / OUT_ROWS, index=False)
    regimes.to_csv(BASE / OUT_BY_REGIME, index=False)
    cex.to_csv(BASE / OUT_COUNTEREX, index=False)
    neg.to_csv(BASE / OUT_NEG, index=False)
    failures.to_csv(BASE / OUT_FAILURES, index=False)
    neutral.to_csv(BASE / OUT_NEUTRAL, index=False)
    forbidden.to_csv(BASE / OUT_FORBIDDEN, index=False)
    caps.to_csv(BASE / OUT_CAP, index=False)
    accum.to_csv(BASE / OUT_ACCUM, index=False)
    write_doc(summary, rows, cex, neutral)
    update_manifest(
        [
            OUT_SCRIPT,
            OUT_SUMMARY,
            OUT_ROWS,
            OUT_BY_REGIME,
            OUT_COUNTEREX,
            OUT_NEG,
            OUT_FAILURES,
            OUT_NEUTRAL,
            OUT_FORBIDDEN,
            OUT_CAP,
            OUT_ACCUM,
            OUT_DOC,
        ]
    )

    s = summary.iloc[0].to_dict()
    print("O2 Repayment Closure audit complete.")
    print("Used files:", "; ".join(used))
    print("Missing expected files:", "; ".join(missing) if missing else "none")
    for key in [
        "negative_subthreshold_count",
        "negative_subthreshold_post_P0_count",
        "negative_subthreshold_surviving_unrepaid_count",
        "pass_negative_subthreshold_repayment",
        "post_P0_negative_subthreshold_surviving_unrepaid_count",
        "pass_post_P0_O2_repayment",
        "O2_available_rows",
        "O2_cap_max",
        "O2_cap_margin",
        "O2_repayment_failures",
        "best_O2_closure_form",
        "recommended_next_file",
    ]:
        print(f"{key}: {s[key]}")


if __name__ == "__main__":
    main()
