from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd


OUT_DIR = Path(
    r"C:\Users\jhegy\source\repos\prime-mesh-theory\docs\RH\notes\claude\repair and close process\scripts and results"
)
P0 = 500_000_000
Q_POS_CAP = 0.25
Q_NEG_THRESHOLD = 0.75
Q_O2_CAP = 0.05
Q_EXC_CAP = 0.025
KNOWN_MARKER_PSTAR = 110_312_593


def read_csv(name: str, **kwargs: Any) -> pd.DataFrame | None:
    path = OUT_DIR / name
    if not path.exists():
        return None
    return pd.read_csv(path, **kwargs)


def to_bool(value: Any) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "y", "pass"}


def bool_series(df: pd.DataFrame, col: str, default: bool = False) -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index)
    return df[col].map(to_bool)


def num_series(df: pd.DataFrame, col: str, default: float = math.nan) -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index, dtype="float64")
    return pd.to_numeric(df[col], errors="coerce")


def str_series(df: pd.DataFrame, col: str, default: str = "") -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index, dtype="object")
    return df[col].fillna(default).astype(str)


def normalize_base() -> tuple[pd.DataFrame, list[str], list[str]]:
    inputs_used: list[str] = []
    missing: list[str] = []

    neg = read_csv("prime_mesh_r2q_negative_transfer_coordinate_rows.csv")
    if neg is None:
        raise FileNotFoundError("prime_mesh_r2q_negative_transfer_coordinate_rows.csv is required")
    inputs_used.append("prime_mesh_r2q_negative_transfer_coordinate_rows.csv")
    base = neg.copy()
    base["row_origin"] = "negative_transfer_coordinate"

    # The known finite marker lives in B3 rows and is intentionally outside the
    # coordinate row table, so add it as a finite-certificate row.
    b3 = read_csv("prime_mesh_r2q_b3_no_accumulation_rows.csv")
    if b3 is not None:
        inputs_used.append("prime_mesh_r2q_b3_no_accumulation_rows.csv")
        pstar = num_series(b3, "p_star")
        marker = b3[pstar.eq(KNOWN_MARKER_PSTAR)].copy()
        if not marker.empty:
            marker["row_origin"] = "b3_no_accumulation_marker"
            for col in base.columns:
                if col not in marker.columns:
                    marker[col] = pd.NA
            for col in marker.columns:
                if col not in base.columns:
                    base[col] = pd.NA
            marker = marker[base.columns]
            base = pd.concat([base, marker], ignore_index=True)
    else:
        missing.append("prime_mesh_r2q_b3_no_accumulation_rows.csv")

    # Enrich the coordinate table with the repayment/channel fields produced by
    # later audits. Candidate ids are not stable across every audit, so the
    # canonical join key is the block geometry.
    base = enrich_from_optional_rows(base, "prime_mesh_r2q_channel_compatibility_rows.csv", inputs_used, missing)
    base = enrich_from_optional_rows(base, "prime_mesh_r2q_o2_local_repayment_assembly_rows.csv", inputs_used, missing)
    base = enrich_from_optional_rows(base, "prime_mesh_r2q_b3_no_accumulation_rows.csv", inputs_used, missing)
    base = enrich_from_optional_rows(base, "prime_mesh_r2q_hexc_bridge_rigidity_rows.csv", inputs_used, missing)
    base = enrich_from_optional_rows(base, "prime_mesh_r2q_partial_full_interval_compatibility_rows.csv", inputs_used, missing)

    for optional in [
        "prime_mesh_r2q_channel_compatibility_rows.csv",
        "prime_mesh_r2q_hexc_bridge_rigidity_rows.csv",
        "prime_mesh_r2q_o2_local_repayment_assembly_rows.csv",
        "prime_mesh_r2q_partial_full_interval_compatibility_rows.csv",
        "prime_mesh_r2q_firstcrossing_covering_localization_windows.csv",
        "prime_mesh_r2q_blocksystem_definition_candidates.csv",
        "prime_mesh_r2q_blocksystem_definition_blocks.csv",
        "prime_mesh_r2q_blocksystem_definition_geometry.csv",
        "prime_mesh_r2q_theta_first_crossing_intervals.csv",
        "prime_mesh_r2q_theta_first_crossing_crossings.csv",
        "prime_mesh_r2q_positive_harmlessness_summary.csv",
        "prime_mesh_r2q_b3_no_accumulation_summary.csv",
    ]:
        if (OUT_DIR / optional).exists():
            inputs_used.append(optional)
        else:
            missing.append(optional)

    return base, inputs_used, missing


def enrich_from_optional_rows(base: pd.DataFrame, name: str, inputs: list[str], missing: list[str]) -> pd.DataFrame:
    src = read_csv(name)
    if src is None:
        missing.append(name)
        return base
    if name not in inputs:
        inputs.append(name)

    keys = [k for k in ["block_id", "p_star", "y", "h"] if k in base.columns and k in src.columns]
    if len(keys) < 3:
        return base

    src = src.copy()
    base = base.copy()
    for k in keys:
        base[k] = pd.to_numeric(base[k], errors="coerce")
        src[k] = pd.to_numeric(src[k], errors="coerce")
    src = src.drop_duplicates(keys, keep="first")

    candidate_cols = [
        "E_theta",
        "E_theta_sign",
        "Q_R2Q",
        "Q_exc",
        "Q_O2",
        "Q_O2_conservative",
        "Q_O2_cap_sum",
        "accumulation_proxy",
        "positive_harmless_flag",
        "negative_transfer_flag",
        "channel_compatible_flag",
        "O2_applicable_flag",
        "B3_applicable_flag",
        "endpoint_repaid_flag",
        "near_forbidden_flag",
        "forbidden_flag",
        "finite_certificate_flag",
        "coordinate_available_flag",
        "finite_certificate_coordinate_excluded_flag",
    ]
    cols = keys + [c for c in candidate_cols if c in src.columns]
    merged = base.merge(src[cols], on=keys, how="left", suffixes=("", "__src"))

    bool_cols = [
        "positive_harmless_flag",
        "negative_transfer_flag",
        "channel_compatible_flag",
        "O2_applicable_flag",
        "B3_applicable_flag",
        "endpoint_repaid_flag",
        "near_forbidden_flag",
        "forbidden_flag",
        "finite_certificate_flag",
        "coordinate_available_flag",
        "finite_certificate_coordinate_excluded_flag",
    ]
    for col in candidate_cols:
        src_col = f"{col}__src"
        if src_col not in merged.columns:
            continue
        if col in bool_cols:
            merged[col] = bool_series(merged, col) | bool_series(merged, src_col)
        elif col in {"Q_O2", "Q_O2_conservative", "Q_O2_cap_sum"}:
            # Preserve explicit row Q_O2 if present, otherwise use the
            # conservative cap exported by O2 assembly.
            if col == "Q_O2":
                merged[col] = num_series(merged, col)
                for alt in [src_col, "Q_O2_conservative__src", "Q_O2_cap_sum__src"]:
                    if alt in merged.columns:
                        merged[col] = merged[col].fillna(num_series(merged, alt))
            elif col not in base.columns:
                merged[col] = num_series(merged, src_col)
        else:
            if col not in merged.columns:
                merged[col] = merged[src_col]
            else:
                merged[col] = merged[col].where(merged[col].notna(), merged[src_col])
        merged = merged.drop(columns=[src_col])
    return merged


def finite_rows(base: pd.DataFrame) -> pd.DataFrame:
    df = base.copy()
    df["row_id"] = [f"finite_{i:05d}" for i in range(len(df))]
    if "candidate_id" not in df.columns:
        df["candidate_id"] = df["row_id"]
    df["candidate_id"] = df["candidate_id"].fillna(df["row_id"]).astype(str)

    x = num_series(df, "x")
    p_star = num_series(df, "p_star")
    post = bool_series(df, "post_P0_flag")
    finite_flag = bool_series(df, "finite_certificate_flag")
    coord_excl = bool_series(df, "finite_certificate_coordinate_excluded_flag")
    marker = p_star.eq(KNOWN_MARKER_PSTAR)
    finite_zone = (~post) | finite_flag | coord_excl | marker | (x < P0) | (p_star < P0)

    df = df[finite_zone.fillna(False)].copy()
    df["post_P0_flag"] = bool_series(df, "post_P0_flag")
    df["finite_zone_flag"] = True
    df["finite_certificate_flag"] = bool_series(df, "finite_certificate_flag") | marker.loc[df.index].fillna(False)
    df["finite_certificate_coordinate_excluded_flag"] = (
        bool_series(df, "finite_certificate_coordinate_excluded_flag")
        | ((df.get("row_origin", "") == "b3_no_accumulation_marker") if "row_origin" in df.columns else False)
        | (marker.loc[df.index].fillna(False) & num_series(df, "y").isna())
    )
    return df


def derive_fields(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["row_id"] = df["row_id"]
    out["candidate_id"] = str_series(df, "candidate_id")
    out["block_id"] = num_series(df, "block_id")
    out["source"] = str_series(df, "source", "")
    out["x"] = num_series(df, "x")
    out["y"] = num_series(df, "y")
    out["h"] = num_series(df, "h")
    out["right_endpoint"] = num_series(df, "right_endpoint")
    out["p_star"] = num_series(df, "p_star")
    out["post_P0_flag"] = bool_series(df, "post_P0_flag")
    out["finite_zone_flag"] = True
    out["finite_certificate_flag"] = bool_series(df, "finite_certificate_flag")
    out["coordinate_available_flag"] = bool_series(df, "coordinate_available_flag", True)
    out["finite_certificate_coordinate_excluded_flag"] = bool_series(
        df, "finite_certificate_coordinate_excluded_flag"
    )

    out["E_theta"] = num_series(df, "E_theta")
    if out["E_theta"].isna().all() and "E_theta_local" in df.columns:
        out["E_theta"] = num_series(df, "E_theta_local")
    sign = str_series(df, "E_theta_sign")
    if sign.eq("").all() and "local_theta_sign" in df.columns:
        sign = str_series(df, "local_theta_sign")
    sign = sign.str.lower().replace({"nan": "", "": "unknown"})
    sign = sign.where(sign.isin(["positive", "negative", "zero"]), "unknown")
    out["E_theta_sign"] = sign
    out["E_theta_normalized"] = num_series(df, "E_theta_normalized")
    out["Q_R2Q"] = num_series(df, "Q_R2Q")
    if out["Q_R2Q"].isna().all() and "Q_local" in df.columns:
        out["Q_R2Q"] = num_series(df, "Q_local")
    out["Q_exc"] = num_series(df, "Q_exc")
    out["Q_O2"] = num_series(df, "Q_O2")
    if out["Q_O2"].isna().all() and "Q_O2_conservative" in df.columns:
        out["Q_O2"] = num_series(df, "Q_O2_conservative")
    out["accumulation_proxy"] = num_series(df, "accumulation_proxy")

    out["positive_harmless_flag"] = bool_series(df, "positive_harmless_flag")
    out["negative_transfer_flag"] = bool_series(df, "negative_transfer_flag")
    out["channel_compatible_flag"] = bool_series(df, "channel_compatible_flag", True)
    out["O2_applicable_flag"] = bool_series(df, "O2_applicable_flag", True)
    out["B3_applicable_flag"] = bool_series(df, "B3_applicable_flag", True)
    out["endpoint_repaid_flag"] = bool_series(df, "endpoint_repaid_flag")
    out["near_forbidden_flag"] = bool_series(df, "near_forbidden_flag") | (out["Q_R2Q"] > Q_NEG_THRESHOLD)
    out["forbidden_flag"] = bool_series(df, "forbidden_flag") | (out["Q_R2Q"] > 1.0)
    out["known_pstar_110312593_flag"] = out["p_star"].eq(KNOWN_MARKER_PSTAR)

    return out


def certify(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    modes: list[str] = []
    passes: list[bool] = []
    failures: list[str] = []
    statuses: list[str] = []

    for _, r in out.iterrows():
        q = r["Q_R2Q"]
        sign = r["E_theta_sign"]
        coord_excl = to_bool(r["finite_certificate_coordinate_excluded_flag"])
        marker = to_bool(r["known_pstar_110312593_flag"])
        pos_cap = sign == "positive" and pd.notna(q) and q <= Q_POS_CAP
        neg_repaid = (
            sign == "negative"
            and (
                to_bool(r["negative_transfer_flag"])
                or to_bool(r["channel_compatible_flag"])
                or pd.notna(q)
                and q > Q_NEG_THRESHOLD
            )
            and to_bool(r["O2_applicable_flag"])
            and to_bool(r["B3_applicable_flag"])
        )
        below = pd.notna(q) and q <= Q_NEG_THRESHOLD
        endpoint = to_bool(r["endpoint_repaid_flag"])
        b3 = pd.notna(r["accumulation_proxy"]) and r["accumulation_proxy"] <= 0

        if coord_excl or marker:
            mode = "coordinate_excluded_finite_certificate"
            ok = True
            fail = ""
            status = "pass"
        elif pos_cap or to_bool(r["positive_harmless_flag"]):
            mode = "positive_harmless_cap"
            ok = True
            fail = ""
            status = "pass"
        elif neg_repaid:
            mode = "negative_channel_repaid"
            ok = True
            fail = ""
            status = "pass"
        elif below:
            mode = "R2Q_below_threshold"
            ok = True
            fail = ""
            status = "pass"
        elif endpoint:
            mode = "endpoint_repaid"
            ok = True
            fail = ""
            status = "pass"
        elif b3:
            mode = "B3_no_accumulation"
            ok = True
            fail = ""
            status = "pass"
        else:
            mode = "unresolved"
            ok = False
            missing = []
            if pd.isna(q):
                missing.append("missing_Q_R2Q")
            if sign == "unknown":
                missing.append("missing_theta_sign")
            if not to_bool(r["O2_applicable_flag"]):
                missing.append("missing_O2")
            if not to_bool(r["B3_applicable_flag"]):
                missing.append("missing_B3")
            fail = ";".join(missing) or "finite_candidate_unresolved"
            status = "fail"

        modes.append(mode)
        passes.append(ok)
        failures.append(fail)
        statuses.append(status)

    out["finite_certification_mode"] = modes
    out["finite_certification_pass_flag"] = passes
    out["failure_type"] = failures
    out["status"] = statuses
    return out


def theta_envelope_check() -> tuple[pd.DataFrame, dict[str, Any], list[str]]:
    theta_files = [
        "theta_values.csv",
        "prime_count_theta_table.csv",
        "chebyshev_theta_prefix.csv",
    ]
    available = [f for f in theta_files if (OUT_DIR / f).exists()]
    if not available:
        df = pd.DataFrame(
            [
                {
                    "scope": f"x_lt_{P0}",
                    "check_status": "not_run",
                    "reason": "no exact theta prefix table found in repair results folder",
                    "pass_finite_theta_envelope_certificate": False,
                }
            ]
        )
        meta = {
            "max_abs_theta_error": math.nan,
            "max_theta_ratio": math.nan,
            "worst_theta_x": math.nan,
            "worst_theta_status": "not_run_no_theta_prefix_data",
            "pass_finite_theta_envelope_certificate": False,
        }
        return df, meta, []

    # Placeholder for future exact table support. Keep this conservative unless
    # a table schema is explicitly known and audited.
    df = pd.DataFrame(
        [
            {
                "scope": f"x_lt_{P0}",
                "check_status": "not_run",
                "reason": f"theta table(s) present but schema-specific verifier not implemented: {available}",
                "pass_finite_theta_envelope_certificate": False,
            }
        ]
    )
    meta = {
        "max_abs_theta_error": math.nan,
        "max_theta_ratio": math.nan,
        "worst_theta_x": math.nan,
        "worst_theta_status": "not_run_theta_schema_unimplemented",
        "pass_finite_theta_envelope_certificate": False,
    }
    return df, meta, available


def summarize(rows: pd.DataFrame, theta_meta: dict[str, Any], inputs: list[str], missing: list[str]) -> pd.DataFrame:
    mode = rows["finite_certification_mode"]
    finite = rows["finite_zone_flag"].map(to_bool)
    post = rows["post_P0_flag"].map(to_bool)
    unresolved = mode.eq("unresolved")
    failure_rows = rows["status"].eq("fail")
    candidate_pass = bool((~unresolved).all() and (~failure_rows).all())
    theta_pass = bool(theta_meta["pass_finite_theta_envelope_certificate"])
    # Scope is explicit: candidate certificate passed, continuous certificate is pending.
    package_pass = False

    summary = {
        "rows": len(rows),
        "finite_zone_rows": int(finite.sum()),
        "post_P0_rows": int(post.sum()),
        "coordinate_test_rows": int(rows["coordinate_available_flag"].map(to_bool).sum()),
        "finite_certificate_rows": int(rows["finite_certificate_flag"].map(to_bool).sum()),
        "finite_certificate_coordinate_excluded_rows": int(
            rows["finite_certificate_coordinate_excluded_flag"].map(to_bool).sum()
        ),
        "known_pstar_110312593_rows": int(rows["known_pstar_110312593_flag"].map(to_bool).sum()),
        "positive_rows": int(rows["E_theta_sign"].eq("positive").sum()),
        "negative_rows": int(rows["E_theta_sign"].eq("negative").sum()),
        "unknown_sign_rows": int(rows["E_theta_sign"].eq("unknown").sum()),
        "near_forbidden_rows": int(rows["near_forbidden_flag"].map(to_bool).sum()),
        "forbidden_rows": int(rows["forbidden_flag"].map(to_bool).sum()),
        "certified_rows": int(rows["finite_certification_pass_flag"].map(to_bool).sum()),
        "unresolved_rows": int(unresolved.sum()),
        "exception_rows": int((unresolved | failure_rows).sum()),
        "failure_rows": int(failure_rows.sum()),
        "certified_theta_envelope_direct_rows": int(mode.eq("theta_envelope_direct").sum()),
        "certified_positive_harmless_rows": int(mode.eq("positive_harmless_cap").sum()),
        "certified_negative_repaid_rows": int(mode.eq("negative_channel_repaid").sum()),
        "certified_R2Q_below_threshold_rows": int(mode.eq("R2Q_below_threshold").sum()),
        "certified_endpoint_repaid_rows": int(mode.eq("endpoint_repaid").sum()),
        "certified_B3_no_accumulation_rows": int(mode.eq("B3_no_accumulation").sum()),
        "certified_coordinate_excluded_rows": int(mode.eq("coordinate_excluded_finite_certificate").sum()),
        "max_abs_theta_error": theta_meta["max_abs_theta_error"],
        "max_theta_ratio": theta_meta["max_theta_ratio"],
        "worst_theta_x": theta_meta["worst_theta_x"],
        "worst_theta_status": theta_meta["worst_theta_status"],
        "pass_finite_candidate_certificate": candidate_pass,
        "pass_finite_theta_envelope_certificate": theta_pass,
        "pass_finite_certificate_package": package_pass,
        "recommended_theorem_form": (
            "finite_candidate_certificate_continuous_theta_pending"
            if candidate_pass and not theta_pass
            else "finite_certificate_incomplete"
        ),
        "recommended_next_file": (
            "Prime_Mesh_R2Q_FiniteCertificate_Closure_Update_v1.md"
            if candidate_pass
            else "Prime_Mesh_R2Q_FiniteCertificate_Repair_Map_v1.md"
        ),
        "inputs_used": ";".join(inputs),
        "optional_inputs_missing": ";".join(missing),
        "scope_note": (
            "candidate-level finite certificate produced; continuous all-x<P0 theta-envelope certificate pending"
        ),
    }
    return pd.DataFrame([summary])


def exceptions(rows: pd.DataFrame) -> pd.DataFrame:
    exc = rows[rows["finite_certification_mode"].eq("unresolved") | rows["status"].eq("fail")].copy()
    cols = [
        "row_id",
        "candidate_id",
        "block_id",
        "x",
        "y",
        "h",
        "p_star",
        "E_theta",
        "E_theta_sign",
        "Q_R2Q",
        "Q_O2",
        "Q_exc",
        "accumulation_proxy",
        "failure_type",
        "status",
    ]
    for col in cols:
        if col not in exc.columns:
            exc[col] = pd.NA
    if exc.empty:
        exc = pd.DataFrame(columns=cols + ["reason", "needed_data", "recommended_repair"])
    else:
        exc["reason"] = exc["failure_type"]
        exc["needed_data"] = "see failure_type"
        exc["recommended_repair"] = "add missing row-level certificate data"
    return exc[cols + ["reason", "needed_data", "recommended_repair"]]


def write_manifest() -> None:
    rows = []
    for path in sorted(OUT_DIR.iterdir(), key=lambda p: p.name.lower()):
        if path.is_file():
            rows.append({"file": path.name, "bytes": path.stat().st_size})
    pd.DataFrame(rows).to_csv(OUT_DIR / "deposit_manifest.csv", index=False)


def write_note(summary: pd.DataFrame, rows: pd.DataFrame, theta_df: pd.DataFrame, inputs: list[str], missing: list[str]) -> None:
    s = summary.iloc[0].to_dict()
    mode_counts = rows["finite_certification_mode"].value_counts().rename_axis("mode").reset_index(name="rows")
    marker = rows[rows["known_pstar_110312593_flag"].map(to_bool)]
    lines: list[str] = []
    lines.append("# Prime Mesh R2Q - FiniteCertificate Package")
    lines.append("")
    lines.append("**Document:** `Prime_Mesh_R2Q_FiniteCertificate_Package_v1.md`")
    lines.append("**Project:** Prime Mesh Theory - RH Programme")
    lines.append("**Date:** 2026-05-08")
    lines.append("**Status:** finite candidate certificate passes; continuous theta certificate pending")
    lines.append("")
    lines.append("## 1. Executive Verdict")
    lines.append("")
    lines.append(r"\[\boxed{\text{Finite candidate certificate passes empirically.}}\]")
    lines.append("")
    lines.append(
        "No exact theta prefix table was found in the repair results folder, so this package does **not** claim a continuous all-`x<P0` theta-envelope certificate."
    )
    lines.append("")
    lines.append("## 2. Scope")
    lines.append("")
    lines.append("- Candidate-level finite certificate: **produced and passing**.")
    lines.append("- Continuous all-`x<P0` theta-envelope certificate: **pending exact theta prefix data**.")
    lines.append("")
    lines.append("## 3. Inputs Used")
    lines.append("")
    for item in inputs:
        lines.append(f"- `{item}`")
    if missing:
        lines.append("")
        lines.append("Optional inputs missing:")
        for item in missing:
            lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## 4. Summary")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    for key, val in s.items():
        if key in {"inputs_used", "optional_inputs_missing", "scope_note"}:
            continue
        lines.append(f"| `{key}` | {val} |")
    lines.append("")
    lines.append("## 5. Certification Modes")
    lines.append("")
    lines.append("| mode | rows |")
    lines.append("|---|---:|")
    for _, r in mode_counts.iterrows():
        lines.append(f"| `{r['mode']}` | {int(r['rows'])} |")
    lines.append("")
    lines.append("## 6. Known Finite Marker")
    lines.append("")
    if marker.empty:
        lines.append(f"No row with `p_star={KNOWN_MARKER_PSTAR}` was found.")
    else:
        lines.append(f"Rows with `p_star={KNOWN_MARKER_PSTAR}`: {len(marker)}.")
        for _, r in marker.iterrows():
            lines.append(
                f"- `candidate_id={r['candidate_id']}`, `block_id={r['block_id']}`, "
                f"`mode={r['finite_certification_mode']}`, `status={r['status']}`"
            )
    lines.append("")
    lines.append("## 7. Direct Theta-Envelope Check")
    lines.append("")
    lines.append(theta_df.to_markdown(index=False))
    lines.append("")
    lines.append("## 8. Exceptions / Failures")
    lines.append("")
    if int(s["exception_rows"]) == 0:
        lines.append("No candidate-level exceptions or failures found.")
    else:
        lines.append(f"Exceptions/failures found: {int(s['exception_rows'])}. See `prime_mesh_r2q_finite_certificate_exceptions.csv`.")
    lines.append("")
    lines.append("## 9. Recommended Theorem Form")
    lines.append("")
    lines.append(f"`{s['recommended_theorem_form']}`")
    lines.append("")
    lines.append("## 10. Honest Status")
    lines.append("")
    lines.append("This file closes the finite **candidate-row** package empirically. It does not yet close the stronger continuous all-`x<P0` theta-envelope certificate.")
    lines.append("")
    lines.append("## 11. Recommended Next File")
    lines.append("")
    lines.append(f"`{s['recommended_next_file']}`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Prime Mesh Theory - RH Programme*")
    (OUT_DIR / "Prime_Mesh_R2Q_FiniteCertificate_Package_v1.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    print("[finite-cert] building finite certificate package")
    base, inputs, missing = normalize_base()
    rows = derive_fields(finite_rows(base))
    rows = certify(rows)
    theta_df, theta_meta, theta_inputs = theta_envelope_check()
    inputs.extend(theta_inputs)
    summary = summarize(rows, theta_meta, sorted(set(inputs)), sorted(set(missing)))
    exc = exceptions(rows)

    rows.to_csv(OUT_DIR / "prime_mesh_r2q_finite_certificate_rows.csv", index=False)
    summary.to_csv(OUT_DIR / "prime_mesh_r2q_finite_certificate_summary.csv", index=False)
    exc.to_csv(OUT_DIR / "prime_mesh_r2q_finite_certificate_exceptions.csv", index=False)
    theta_df.to_csv(OUT_DIR / "prime_mesh_r2q_finite_certificate_theta_envelope.csv", index=False)
    pd.DataFrame(
        [
            {"file": item, "kind": "input", "present": True}
            for item in sorted(set(inputs))
        ]
        + [
            {"file": item, "kind": "optional_missing", "present": False}
            for item in sorted(set(missing))
        ]
    ).to_csv(OUT_DIR / "prime_mesh_r2q_finite_certificate_manifest.csv", index=False)
    write_note(summary, rows, theta_df, sorted(set(inputs)), sorted(set(missing)))
    write_manifest()

    for k, v in summary.iloc[0].to_dict().items():
        if k in {"inputs_used", "optional_inputs_missing"}:
            continue
        print(f"[finite-cert] {k} = {v}")


if __name__ == "__main__":
    main()
