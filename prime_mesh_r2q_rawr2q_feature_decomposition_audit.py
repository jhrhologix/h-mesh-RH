from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


OUT_DIR = Path(
    r"C:\Users\jhegy\source\repos\prime-mesh-theory\docs\RH\notes\claude\repair and close process\scripts and results"
)

FEATURE_KEYWORDS = [
    "schur",
    "projection",
    "residual",
    "svd",
    "matrix",
    "rank",
    "shell",
    "spf",
    "omega",
    "longa",
    "bridge",
    "exc",
    "slack",
    "tail",
    "endpoint",
    "boundary",
    "prime",
    "theta",
    "local",
    "mass",
    "deficit",
    "surplus",
    "feature",
    "component",
    "kernel",
    "k4",
    "o1",
    "o2",
    "b2",
    "r2q",
]

LEAKY_TOKENS = [
    "q_r2q",
    "q_max",
    "q_local",
    "q_threshold",
    "near_forbidden",
    "forbidden",
    "positive_harmless",
    "negative_transfer",
    "channel_compatible",
    "o2_applicable",
    "b3_applicable",
    "b3_no",
    "pass_",
    "status",
    "failure",
    "classification",
    "flag",
    "source",
    "candidate_id",
    "block_id",
    "selected_block_id",
]

FINAL_COORDINATES = {"Q_R2Q", "Q_local", "Q_max", "Q_R2Q_full"}


def read_csv(name: str, **kwargs: Any) -> pd.DataFrame | None:
    p = OUT_DIR / name
    if not p.exists():
        return None
    return pd.read_csv(p, **kwargs)


def to_bool(v: Any) -> bool:
    if pd.isna(v):
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    return str(v).strip().lower() in {"true", "1", "yes", "pass", "y"}


def nser(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(np.nan, index=df.index, dtype="float64")
    return pd.to_numeric(df[col], errors="coerce")


def bser(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(False, index=df.index)
    return df[col].map(to_bool)


def sser(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series("", index=df.index, dtype="object")
    return df[col].fillna("").astype(str)


def safe_corr(a: pd.Series, b: pd.Series) -> float:
    x = pd.to_numeric(a, errors="coerce")
    y = pd.to_numeric(b, errors="coerce")
    mask = x.notna() & y.notna()
    if int(mask.sum()) < 3:
        return float("nan")
    if float(x[mask].std()) == 0.0 or float(y[mask].std()) == 0.0:
        return float("nan")
    return float(x[mask].corr(y[mask]))


def canonical_base() -> tuple[pd.DataFrame, list[str], list[str]]:
    used: list[str] = []
    missing: list[str] = []
    base = read_csv("prime_mesh_r2q_firstcrossing_covering_localization_windows.csv")
    if base is None:
        base = read_csv("prime_mesh_r2q_negative_transfer_coordinate_rows.csv")
        if base is None:
            raise FileNotFoundError("No base R2Q row table found")
        used.append("prime_mesh_r2q_negative_transfer_coordinate_rows.csv")
    else:
        used.append("prime_mesh_r2q_firstcrossing_covering_localization_windows.csv")

    base = base.copy()
    base["row_id"] = [f"rawr2q_{i:05d}" for i in range(len(base))]

    # Join row-level companion tables when geometry keys exist. This increases
    # the feature inventory but does not make downstream labels primitive.
    for file_name in [
        "prime_mesh_r2q_negative_transfer_coordinate_rows.csv",
        "prime_mesh_r2q_partial_full_interval_compatibility_rows.csv",
        "prime_mesh_r2q_channel_compatibility_rows.csv",
        "prime_mesh_r2q_o2_local_repayment_assembly_rows.csv",
        "prime_mesh_r2q_hexc_bridge_rigidity_rows.csv",
        "prime_mesh_r2q_b3_no_accumulation_rows.csv",
    ]:
        src = read_csv(file_name)
        if src is None:
            missing.append(file_name)
            continue
        if file_name not in used:
            used.append(file_name)
        keys = [k for k in ["block_id", "p_star", "y", "h"] if k in base.columns and k in src.columns]
        if len(keys) < 3:
            continue
        left = base.copy()
        right = src.copy()
        for k in keys:
            left[k] = pd.to_numeric(left[k], errors="coerce")
            right[k] = pd.to_numeric(right[k], errors="coerce")
        right = right.drop_duplicates(keys, keep="first")
        add_cols = [c for c in right.columns if c not in keys]
        # Avoid giant duplicate label bloat where possible; keep suffix so the
        # audit can still inspect provenance.
        base = left.merge(right[keys + add_cols], on=keys, how="left", suffixes=("", f"__{Path(file_name).stem}"))

    for file_name in [
        "prime_mesh_r2q_blocksystem_definition_blocks.csv",
        "prime_mesh_r2q_blocksystem_definition_geometry.csv",
        "prime_mesh_r2q_o1_schur_residual_sign_stability_vectors.csv",
        "prime_mesh_r2q_o1_schur_residual_sign_stability_scopes.csv",
        "prime_mesh_r2q_o2_local_repayment_assembly_components.csv",
        "prime_mesh_r2q_o2_local_repayment_assembly_caps.csv",
    ]:
        if (OUT_DIR / file_name).exists():
            used.append(file_name)
        else:
            missing.append(file_name)
    return base, sorted(set(used)), sorted(set(missing))


def prepare_rows(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["row_id"] = df["row_id"]
    out["candidate_id"] = sser(df, "candidate_id")
    out["block_id"] = nser(df, "block_id")
    out["x"] = nser(df, "x")
    if out["x"].isna().all() and "hi" in df.columns:
        out["x"] = nser(df, "hi")
    out["y"] = nser(df, "y")
    out["h"] = nser(df, "h")
    out["p_star"] = nser(df, "p_star")
    out["right_endpoint"] = nser(df, "right_endpoint")
    if out["right_endpoint"].isna().all() and "hi" in df.columns:
        out["right_endpoint"] = nser(df, "hi")
    out["E_theta"] = nser(df, "E_theta")
    if out["E_theta"].isna().all() and "E_theta_local" in df.columns:
        out["E_theta"] = nser(df, "E_theta_local")
    if out["E_theta"].isna().all() and "theta_local_error" in df.columns:
        out["E_theta"] = nser(df, "theta_local_error")
    sign = sser(df, "E_theta_sign")
    if sign.eq("").all():
        sign = sser(df, "local_theta_sign")
    out["E_theta_sign"] = sign.str.lower().replace({"": "unknown", "nan": "unknown"})
    q = nser(df, "Q_R2Q")
    if q.isna().all() and "Q_local" in df.columns:
        q = nser(df, "Q_local")
    out["Q_R2Q"] = q
    h = out["h"]
    p = out["p_star"]
    denom = np.sqrt(h) * np.log(p) ** 2
    denom = denom.where((h > 0) & (p > 1))
    out["scale_denominator"] = denom
    out["R_R2Q_reconstructed"] = out["Q_R2Q"] * denom
    out["channel"] = sser(df, "channel_full")
    if out["channel"].eq("").all():
        out["channel"] = sser(df, "channel_inferred")
    out["post_P0_flag"] = bser(df, "post_P0_flag") | bser(df, "post_P0")
    out["finite_zone_flag"] = bser(df, "finite_certificate_flag") | (~out["post_P0_flag"])
    out["near_forbidden_flag"] = bser(df, "near_forbidden_flag") | bser(df, "near_forbidden_R2Q") | out["Q_R2Q"].gt(0.75)
    out["forbidden_flag"] = bser(df, "forbidden_flag") | bser(df, "forbidden_R2Q") | out["Q_R2Q"].gt(1.0)
    return out


def is_feature_candidate(col: str, series: pd.Series) -> bool:
    name = col.lower()
    if not pd.api.types.is_numeric_dtype(series):
        return False
    if any(tok in name for tok in LEAKY_TOKENS):
        return False
    if col in FINAL_COORDINATES:
        return False
    return any(tok in name for tok in FEATURE_KEYWORDS)


def is_leaky_candidate(col: str, series: pd.Series) -> bool:
    name = col.lower()
    if not pd.api.types.is_numeric_dtype(series):
        return False
    return any(tok in name for tok in LEAKY_TOKENS) or col in FINAL_COORDINATES


def feature_inventory(df: pd.DataFrame, rows: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    primitive_cols: list[str] = []
    leaky_cols: list[str] = []
    y_raw = rows["R_R2Q_reconstructed"]
    y_q = rows["Q_R2Q"]
    e = rows["E_theta"]
    neg = rows["E_theta_sign"].eq("negative").astype(int)
    near = rows["near_forbidden_flag"].astype(int)
    records = []
    for col in df.columns:
        ser = pd.to_numeric(df[col], errors="coerce") if col in df.columns else pd.Series(dtype=float)
        if not pd.api.types.is_numeric_dtype(ser):
            continue
        leaky = is_leaky_candidate(col, ser)
        primitive = is_feature_candidate(col, ser)
        if not (leaky or primitive):
            continue
        if primitive:
            primitive_cols.append(col)
        if leaky:
            leaky_cols.append(col)
        non = int(ser.notna().sum())
        records.append(
            {
                "column": col,
                "primitive_candidate": primitive,
                "leaky_excluded": leaky,
                "non_null_count": non,
                "min": float(ser.min()) if non else np.nan,
                "max": float(ser.max()) if non else np.nan,
                "mean": float(ser.mean()) if non else np.nan,
                "median": float(ser.median()) if non else np.nan,
                "std": float(ser.std()) if non else np.nan,
                "corr_with_R_R2Q_rec": safe_corr(ser, y_raw),
                "corr_with_Q_R2Q": safe_corr(ser, y_q),
                "corr_with_E_theta": safe_corr(ser, e),
                "corr_with_negative_indicator": safe_corr(ser, neg),
                "corr_with_near_forbidden_indicator": safe_corr(ser, near),
            }
        )
    features = pd.DataFrame(records).sort_values(
        ["primitive_candidate", "corr_with_R_R2Q_rec"], ascending=[False, False], na_position="last"
    )
    return features, primitive_cols, leaky_cols


def fit_linear(name: str, X: np.ndarray, y: np.ndarray, feature_names: list[str]) -> dict[str, Any]:
    mask = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
    n = int(mask.sum())
    if n < X.shape[1] + 2:
        return {"model": name, "rows": n, "status": "insufficient_rows"}
    Xm = X[mask]
    ym = y[mask]
    beta, *_ = np.linalg.lstsq(Xm, ym, rcond=None)
    pred = Xm @ beta
    resid = ym - pred
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((ym - ym.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot else np.nan
    cond = float(np.linalg.cond(Xm)) if Xm.shape[1] > 1 else 1.0
    return {
        "model": name,
        "rows": n,
        "status": "fit",
        "feature_list": ";".join(feature_names),
        "coefficients": ";".join(f"{v:.12g}" for v in beta),
        "R2": r2,
        "MAE": float(np.mean(np.abs(resid))),
        "RMSE": float(np.sqrt(np.mean(resid**2))),
        "max_abs_residual": float(np.max(np.abs(resid))),
        "condition_number": cond,
    }


def model_tests(df: pd.DataFrame, rows: pd.DataFrame, primitive_cols: list[str]) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    y_raw = rows["R_R2Q_reconstructed"].to_numpy(dtype=float)
    y_q = rows["Q_R2Q"].to_numpy(dtype=float)
    e = rows["E_theta"].to_numpy(dtype=float)
    denom = rows["scale_denominator"].to_numpy(dtype=float)
    neg_e = -e

    X_a = np.column_stack([np.ones(len(rows)), neg_e])
    rec_a = fit_linear("A_theta_only_raw", X_a, y_raw, ["intercept", "negative_E_theta"])
    rec_a["theta_only_beta_sign"] = (
        "positive" if rec_a.get("status") == "fit" and float(rec_a["coefficients"].split(";")[1]) > 0 else "nonpositive_or_unfit"
    )
    records.append(rec_a)

    norm_theta = np.divide(-e, denom, out=np.full_like(e, np.nan), where=np.isfinite(denom) & (denom != 0))
    X_b = np.column_stack([np.ones(len(rows)), norm_theta])
    records.append(fit_linear("B_normalized_theta", X_b, y_q, ["intercept", "negative_E_theta_over_scale"]))

    # Keep a small stable feature set: strongest primitive correlations by
    # absolute raw-coordinate correlation, excluding direct theta duplicates if
    # they are exact aliases.
    scored = []
    for col in primitive_cols:
        ser = pd.to_numeric(df[col], errors="coerce")
        corr = safe_corr(ser, rows["R_R2Q_reconstructed"])
        if np.isfinite(corr):
            scored.append((abs(corr), col))
    top_cols = [c for _, c in sorted(scored, reverse=True)[:12]]
    if top_cols:
        mats = [np.ones(len(rows)), neg_e]
        names = ["intercept", "negative_E_theta"]
        for col in top_cols:
            mats.append(pd.to_numeric(df[col], errors="coerce").to_numpy(dtype=float))
            names.append(col)
        records.append(fit_linear("C_feature_augmented", np.column_stack(mats), y_raw, names))
    else:
        records.append({"model": "C_feature_augmented", "rows": 0, "status": "no_primitive_features"})

    # Threshold classifier: intentionally simple. The question is whether the
    # primitive numeric score separates, not to optimize a black-box classifier.
    threshold_target = rows["Q_R2Q"].gt(0.75)
    score = norm_theta
    mask = np.isfinite(score)
    if int(mask.sum()) and threshold_target.any():
        # classify using the minimum score observed among true threshold rows
        cutoff = float(np.nanmin(score[threshold_target.to_numpy() & mask]))
        pred = score >= cutoff
        records.append(
            {
                "model": "D_threshold_classifier_normalized_theta",
                "rows": int(mask.sum()),
                "status": "fit",
                "feature_list": "negative_E_theta_over_scale",
                "coefficients": f"cutoff={cutoff:.12g}",
                "precision": float((pred & threshold_target.to_numpy()).sum() / max(int(pred.sum()), 1)),
                "recall": float((pred & threshold_target.to_numpy()).sum() / max(int(threshold_target.sum()), 1)),
                "false_positive_count": int((pred & ~threshold_target.to_numpy()).sum()),
                "false_negative_count": int((~pred & threshold_target.to_numpy()).sum()),
            }
        )
    else:
        records.append({"model": "D_threshold_classifier_normalized_theta", "rows": int(mask.sum()), "status": "insufficient_target"})

    pos = rows["E_theta_sign"].eq("positive")
    pos_q = rows.loc[pos, "Q_R2Q"]
    records.append(
        {
            "model": "E_positive_cap",
            "rows": int(pos.sum()),
            "status": "checked",
            "positive_rows": int(pos.sum()),
            "positive_above_0p25_count": int(pos_q.gt(0.25).sum()),
            "max_positive_Q": float(pos_q.max()) if len(pos_q) else np.nan,
            "separation_margin": float(0.25 - pos_q.max()) if len(pos_q) else np.nan,
        }
    )
    return pd.DataFrame(records)


def refresh_manifest() -> None:
    rows = []
    for path in sorted(OUT_DIR.iterdir(), key=lambda p: p.name.lower()):
        if path.is_file():
            rows.append({"file": path.name, "bytes": path.stat().st_size})
    pd.DataFrame(rows).to_csv(OUT_DIR / "deposit_manifest.csv", index=False)


def write_note(summary: pd.DataFrame, features: pd.DataFrame, models: pd.DataFrame, used: list[str], missing: list[str]) -> None:
    s = summary.iloc[0].to_dict()
    top_features = features[features["primitive_candidate"]].head(12)
    lines: list[str] = []
    lines.append("# Prime Mesh R2Q - RawR2Q Feature Decomposition Audit")
    lines.append("")
    lines.append("**Document:** `Prime_Mesh_R2Q_RawR2Q_Feature_Decomposition_Audit_v1.md`")
    lines.append("**Project:** Prime Mesh Theory - RH Programme")
    lines.append("**Date:** 2026-05-08")
    lines.append("**Status:** RawR2Q feature-basis diagnostic")
    lines.append("")
    lines.append("## 1. Executive Verdict")
    lines.append("")
    if s["primitive_feature_basis_available"] == "False":
        lines.append(r"\[\boxed{\text{Proof-grade primitive RawR2Q feature basis is not available in current CSVs.}}\]")
    elif s["primitive_feature_basis_available"] == "Partial":
        lines.append(r"\[\boxed{\text{Primitive feature basis is partial; export patch is still needed.}}\]")
    else:
        lines.append(r"\[\boxed{\text{Primitive RawR2Q feature basis appears available.}}\]")
    lines.append("")
    lines.append("The audit reconstructs the raw target value:")
    lines.append("")
    lines.append(r"\[")
    lines.append(r"R_{\rm R2Q}^{\rm rec}=Q_{\rm R2Q}\sqrt h\log^2p^*.")
    lines.append(r"\]")
    lines.append("")
    lines.append("This reconstruction is a target value, not a derivation from primitive SR10/B2 features.")
    lines.append("")
    lines.append("## 2. Inputs Used")
    lines.append("")
    for item in used:
        lines.append(f"- `{item}`")
    if missing:
        lines.append("")
        lines.append("Optional inputs missing:")
        for item in missing:
            lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## 3. Summary")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    for key, val in s.items():
        if key in {"inputs_used", "optional_inputs_missing"}:
            continue
        lines.append(f"| `{key}` | {val} |")
    lines.append("")
    lines.append("## 4. Top Primitive Candidate Columns")
    lines.append("")
    lines.append(top_features.to_markdown(index=False) if not top_features.empty else "No primitive candidate columns found.")
    lines.append("")
    lines.append("## 5. Model Results")
    lines.append("")
    lines.append(models.to_markdown(index=False))
    lines.append("")
    lines.append("## 6. Leakage / Honesty Assessment")
    lines.append("")
    lines.append("Columns that are final coordinates, threshold labels, pass/failure flags, channel labels, or downstream repayment flags were excluded from the primitive feature basis.")
    lines.append("")
    lines.append("Current artifacts contain useful diagnostics and downstream components, but they do not expose a proof-grade primitive formula for the raw R2Q coordinate. A generation/export patch should record the SR10/B2 raw terms before the final `Q_R2Q` value is formed.")
    lines.append("")
    lines.append("## 7. Recommended Next File")
    lines.append("")
    lines.append(f"`{s['recommended_next_file']}`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Prime Mesh Theory - RH Programme*")
    (OUT_DIR / "Prime_Mesh_R2Q_RawR2Q_Feature_Decomposition_Audit_v1.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df, used, missing = canonical_base()
    rows = prepare_rows(df)
    features, primitive_cols, leaky_cols = feature_inventory(df, rows)
    models = model_tests(df, rows, primitive_cols)
    best = models.loc[models.get("R2", pd.Series(dtype=float)).astype(float).idxmax()] if "R2" in models and models["R2"].notna().any() else pd.Series(dtype=object)

    coord_rows = int(rows["Q_R2Q"].notna().sum())
    raw_rows = int(rows["R_R2Q_reconstructed"].notna().sum())
    scale_rows = int(rows["scale_denominator"].notna().sum())
    # Partial when we have correlated diagnostics but no explicit formula/source
    # columns naming raw coordinate components.
    primitive_basis = "Partial" if primitive_cols else "False"
    raw_formula = False
    export_patch = True

    positive_model = models[models["model"].eq("E_positive_cap")]
    positive_cap = bool(
        not positive_model.empty
        and int(positive_model.iloc[0].get("positive_above_0p25_count", 1)) == 0
    )
    threshold_model = models[models["model"].str.startswith("D_threshold")]
    fp = int(threshold_model.iloc[0].get("false_positive_count", -1)) if not threshold_model.empty else -1
    fn = int(threshold_model.iloc[0].get("false_negative_count", -1)) if not threshold_model.empty else -1

    summary = pd.DataFrame(
        [
            {
                "rows": len(rows),
                "coordinate_test_rows": coord_rows,
                "post_P0_rows": int(rows["post_P0_flag"].sum()),
                "finite_zone_rows": int(rows["finite_zone_flag"].sum()),
                "Q_R2Q_available_rows": coord_rows,
                "R_R2Q_reconstructed_rows": raw_rows,
                "scale_available_rows": scale_rows,
                "candidate_feature_columns_found": int(len(features)),
                "primitive_feature_columns_found": int(len(primitive_cols)),
                "leaky_feature_columns_excluded": int(len(leaky_cols)),
                "primitive_feature_basis_available": primitive_basis,
                "best_model_name": best.get("model", ""),
                "best_model_R2": best.get("R2", np.nan),
                "best_model_MAE": best.get("MAE", np.nan),
                "best_model_RMSE": best.get("RMSE", np.nan),
                "best_model_max_abs_residual": best.get("max_abs_residual", np.nan),
                "theta_only_beta_sign": models.loc[models["model"].eq("A_theta_only_raw"), "theta_only_beta_sign"].iloc[0],
                "positive_cap_explained_flag": positive_cap,
                "threshold_classifier_false_positive_count": fp,
                "threshold_classifier_false_negative_count": fn,
                "raw_coordinate_formula_available": raw_formula,
                "export_patch_needed": export_patch,
                "pass_rawr2q_feature_decomposition_audit": True,
                "recommended_theorem_form": "raw_target_reconstructed_but_primitive_formula_missing",
                "recommended_next_file": "Prime_Mesh_R2Q_RawR2Q_Export_Patch_Spec_v1.md",
                "inputs_used": ";".join(used),
                "optional_inputs_missing": ";".join(missing),
            }
        ]
    )

    failures = pd.DataFrame(
        [
            {
                "failure_type": "primitive_raw_formula_missing",
                "severity": "export_patch_needed",
                "reason": "Current CSVs expose Q_R2Q and diagnostics/downstream components but not a proof-grade primitive decomposition of R_R2Q before normalization.",
                "recommended_repair": "Patch SR10/B2/R2Q generation scripts to export raw coordinate terms and primitive feature basis.",
            }
        ]
    )

    rows.to_csv(OUT_DIR / "prime_mesh_r2q_rawr2q_feature_decomposition_rows.csv", index=False)
    features.to_csv(OUT_DIR / "prime_mesh_r2q_rawr2q_feature_decomposition_features.csv", index=False)
    models.to_csv(OUT_DIR / "prime_mesh_r2q_rawr2q_feature_decomposition_models.csv", index=False)
    failures.to_csv(OUT_DIR / "prime_mesh_r2q_rawr2q_feature_decomposition_failures.csv", index=False)
    summary.to_csv(OUT_DIR / "prime_mesh_r2q_rawr2q_feature_decomposition_summary.csv", index=False)
    write_note(summary, features, models, used, missing)
    refresh_manifest()

    for k, v in summary.iloc[0].to_dict().items():
        if k in {"inputs_used", "optional_inputs_missing"}:
            continue
        print(f"[rawr2q] {k} = {v}")


if __name__ == "__main__":
    main()
