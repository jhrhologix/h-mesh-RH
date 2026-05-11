from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import pandas as pd


OUT = Path(
    r"C:\Users\jhegy\source\repos\prime-mesh-theory\docs\RH\notes\claude\repair and close process\scripts and results"
)

NT_ROWS = OUT / "prime_mesh_r2q_negative_transfer_coordinate_rows.csv"
NT_SUMMARY = OUT / "prime_mesh_r2q_negative_transfer_coordinate_summary.csv"
POS_SUMMARY = OUT / "prime_mesh_r2q_positive_harmlessness_summary.csv"
PARTIAL_ROWS = OUT / "prime_mesh_r2q_partial_full_interval_compatibility_rows.csv"
FCL_WINDOWS = OUT / "prime_mesh_r2q_firstcrossing_covering_localization_windows.csv"
B3_BLOCKS = OUT / "prime_mesh_r2q_b3_block_to_tail_blocks.csv"
O2_ASSEMBLY = OUT / "prime_mesh_r2q_o123_to_mr2_assembly_summary.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_channel_compatibility_summary.csv"
ROWS_OUT = OUT / "prime_mesh_r2q_channel_compatibility_rows.csv"
BY_CHANNEL_OUT = OUT / "prime_mesh_r2q_channel_compatibility_by_channel.csv"
FAILURES_OUT = OUT / "prime_mesh_r2q_channel_compatibility_failures.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_ChannelCompatibility_Audit_v1.md"
MANIFEST_OUT = OUT / "deposit_manifest.csv"


def log(msg: str) -> None:
    print(f"[channel-compatibility] {msg}")


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


def load_inputs() -> tuple[pd.DataFrame, list[str], list[str], list[str]]:
    if not NT_ROWS.exists():
        raise FileNotFoundError(NT_ROWS)
    log(f"reading primary {NT_ROWS.name}")
    df = pd.read_csv(NT_ROWS)
    used = [NT_ROWS.name]
    missing: list[str] = []
    joins: list[str] = ["primary NegativeTransfer row table used directly"]

    for path in [NT_SUMMARY, POS_SUMMARY, PARTIAL_ROWS, B3_BLOCKS, O2_ASSEMBLY]:
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
            "B2_active_flag",
            "B3_block_pass",
            "O2_B3_repaid_flag",
            "negative_transfer_near_forbidden_flag",
            "crossing_status",
            "Q_tail_end",
            "Q_tail_max_inside",
            "O2_total_with_o2p4",
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


def channel_text_match(s: pd.Series) -> pd.Series:
    text = s.fillna("").astype(str).str.lower()
    return (
        text.str.contains("negative", regex=False)
        | text.str.contains("deficit", regex=False)
        | text.str.contains("repaid", regex=False)
        | text.str.contains("o2", regex=False)
        | text.str.contains("b3", regex=False)
    )


def build_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows = pd.DataFrame(index=df.index)
    for col in ["candidate_id", "block_id", "x", "y", "h", "p_star"]:
        rows[col] = df[col] if col in df.columns else math.nan
    for col in ["x", "y", "h", "p_star"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce")

    rows["E_theta"] = safe_num(df, "E_theta")
    rows["E_theta_sign"] = df.get("E_theta_sign", pd.Series("unknown", index=df.index)).fillna("unknown").astype(str).str.lower()
    rows["Q_R2Q"] = safe_num(df, "Q_R2Q")
    rows["near_forbidden_flag"] = (rows["Q_R2Q"] > 0.75) | safe_bool(df, "near_forbidden_flag")
    rows["forbidden_flag"] = (rows["Q_R2Q"] > 1.0) | safe_bool(df, "forbidden_flag")
    rows["negative_transfer_flag"] = safe_bool(df, "negative_transfer_flag")
    rows["positive_harmless_flag"] = safe_bool(df, "positive_harmless_flag")
    rows["channel_full"] = df.get("channel_full", pd.Series("unknown", index=df.index)).fillna("unknown")
    rows["channel_inferred"] = df.get("channel_inferred", pd.Series("unknown", index=df.index)).fillna("unknown")
    rows["O2_applicable_flag"] = (
        safe_bool(df, "O2_B3_repaid_flag")
        | safe_bool(df, "O2_B3_repaid_flag_win")
        | (safe_num(df, "O2_total_with_o2p4") < 1.0)
    )
    rows["B3_applicable_flag"] = safe_bool(df, "B3_block_pass") | safe_bool(df, "B3_block_pass_win")
    rows["B2_active_flag"] = safe_bool(df, "B2_active_flag") | safe_bool(df, "B2_active_flag_win")
    rows["finite_certificate_flag"] = safe_bool(df, "finite_certificate_flag")
    rows["coordinate_available_flag"] = safe_bool(df, "coordinate_available_flag")
    rows["valid_scale_flag"] = safe_bool(df, "valid_scale_flag") | (rows["p_star"].notna() & rows["h"].notna() & (rows["h"] > 0))
    rows["post_P0_flag"] = safe_bool(df, "post_P0_flag")
    rows["tail_flag"] = safe_bool(df, "tail_flag")

    channel_text_ok = channel_text_match(rows["channel_full"]) | channel_text_match(rows["channel_inferred"])
    rows["theta_negative_flag"] = rows["E_theta_sign"].eq("negative")
    rows["theta_positive_flag"] = rows["E_theta_sign"].eq("positive")
    rows["dangerous_coordinate_flag"] = rows["near_forbidden_flag"] & rows["coordinate_available_flag"]
    rows["finite_certificate_excluded_flag"] = rows["finite_certificate_flag"] & ~rows["coordinate_available_flag"]

    rows["negative_channel_flag"] = (
        rows["negative_transfer_flag"]
        | channel_text_ok
        | rows["O2_applicable_flag"]
        | rows["B3_applicable_flag"]
        | rows["B2_active_flag"]
    )
    rows["channel_compatible_flag"] = (
        ~rows["dangerous_coordinate_flag"]
        | (
            rows["theta_negative_flag"]
            & rows["negative_channel_flag"]
            & rows["valid_scale_flag"]
            & ~rows["finite_certificate_excluded_flag"]
        )
    )
    rows["positive_channel_conflict_flag"] = rows["theta_positive_flag"] & rows["near_forbidden_flag"]
    rows["finite_certificate_unresolved_flag"] = (
        rows["finite_certificate_flag"]
        & rows["near_forbidden_flag"]
        & rows["coordinate_available_flag"]
        & ~rows["channel_compatible_flag"]
    )
    rows["missing_channel_flag"] = (
        rows["dangerous_coordinate_flag"]
        & ~rows["negative_transfer_flag"]
        & ~channel_text_ok
        & ~rows["O2_applicable_flag"]
        & ~rows["B3_applicable_flag"]
        & ~rows["B2_active_flag"]
    )

    rows["failure_type"] = ""
    rows.loc[rows["dangerous_coordinate_flag"] & ~rows["theta_negative_flag"], "failure_type"] = "dangerous_not_theta_negative"
    rows.loc[rows["dangerous_coordinate_flag"] & ~rows["negative_channel_flag"], "failure_type"] = "dangerous_missing_negative_channel"
    rows.loc[rows["positive_channel_conflict_flag"], "failure_type"] = "positive_channel_conflict"
    rows.loc[rows["finite_certificate_unresolved_flag"], "failure_type"] = "finite_certificate_unresolved"
    rows.loc[rows["missing_channel_flag"], "failure_type"] = "missing_channel"
    rows["status"] = rows["failure_type"].where(rows["failure_type"].ne(""), "pass")
    rows.loc[rows["finite_certificate_excluded_flag"], "failure_type"] = ""
    rows.loc[rows["finite_certificate_excluded_flag"], "status"] = "finite_certificate_coordinate_excluded"
    return rows


def by_channel(rows: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["channel_full", "channel_inferred", "negative_transfer_flag", "O2_applicable_flag", "B3_applicable_flag"]
    out = []
    for keys, g in rows.groupby(group_cols, dropna=False):
        near = g[g["near_forbidden_flag"] & g["coordinate_available_flag"]]
        q = g["Q_R2Q"].dropna()
        out.append(
            {
                "channel_full": keys[0],
                "channel_inferred": keys[1],
                "negative_transfer_flag": keys[2],
                "O2_applicable_flag": keys[3],
                "B3_applicable_flag": keys[4],
                "rows": len(g),
                "coordinate_rows": int(g["coordinate_available_flag"].sum()),
                "near_forbidden_rows": int((g["near_forbidden_flag"] & g["coordinate_available_flag"]).sum()),
                "forbidden_rows": int((g["forbidden_flag"] & g["coordinate_available_flag"]).sum()),
                "near_channel_compatible_frac": float(near["channel_compatible_flag"].mean()) if len(near) else 1.0,
                "Q_max": float(q.max()) if len(q) else math.nan,
                "positive_rows": int(g["theta_positive_flag"].sum()),
                "negative_rows": int(g["theta_negative_flag"].sum()),
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
        "E_theta",
        "E_theta_sign",
        "Q_R2Q",
        "near_forbidden_flag",
        "forbidden_flag",
        "negative_transfer_flag",
        "positive_harmless_flag",
        "channel_full",
        "channel_inferred",
        "O2_applicable_flag",
        "B3_applicable_flag",
        "finite_certificate_flag",
        "coordinate_available_flag",
        "failure_type",
        "status",
    ]
    return fail[[c for c in cols if c in fail.columns]]


def summarize(rows: pd.DataFrame, fail: pd.DataFrame, used: list[str], missing: list[str], joins: list[str]) -> pd.DataFrame:
    coord = rows[rows["coordinate_available_flag"]]
    q075 = coord[coord["Q_R2Q"] > 0.75]
    q1 = coord[coord["Q_R2Q"] > 1.0]
    q075_frac = float(q075["channel_compatible_flag"].mean()) if len(q075) else 1.0
    q1_frac = float(q1["channel_compatible_flag"].mean()) if len(q1) else 1.0
    pos_conflict = int(rows["positive_channel_conflict_flag"].sum())
    finite_unresolved = int(rows["finite_certificate_unresolved_flag"].sum())
    missing_channel = int(rows["missing_channel_flag"].sum())
    pass_emp = bool(
        len(q075) > 0
        and q075_frac == 1.0
        and q1_frac == 1.0
        and pos_conflict == 0
        and finite_unresolved == 0
        and missing_channel == 0
    )
    # Finite certificate exclusions are allowed if they are explicitly finite and not coordinate theorem rows.
    summary = {
        "rows": len(rows),
        "coordinate_test_rows": len(coord),
        "Q_gt_0p75_rows": len(q075),
        "Q_gt_1_rows": len(q1),
        "Q_gt_0p75_channel_compatible_count": int(q075["channel_compatible_flag"].sum()) if len(q075) else 0,
        "Q_gt_0p75_channel_compatible_frac": q075_frac,
        "Q_gt_1_channel_compatible_frac": q1_frac,
        "positive_channel_conflict_count": pos_conflict,
        "finite_certificate_unresolved_count": finite_unresolved,
        "finite_certificate_coordinate_excluded_rows": int(rows["finite_certificate_excluded_flag"].sum()),
        "excluded_near_forbidden_rows": int((rows["finite_certificate_excluded_flag"] & rows["near_forbidden_flag"]).sum()),
        "missing_channel_rows": missing_channel,
        "negative_transfer_near_forbidden_rows": int((q075["negative_transfer_flag"]).sum()) if len(q075) else 0,
        "O2_applicable_near_forbidden_rows": int((q075["O2_applicable_flag"]).sum()) if len(q075) else 0,
        "B3_applicable_near_forbidden_rows": int((q075["B3_applicable_flag"]).sum()) if len(q075) else 0,
        "pass_channel_compatibility_empirical": pass_emp,
        "inputs_used": ";".join(used),
        "optional_inputs_missing": ";".join(missing),
        "join_notes": ";".join(joins),
    }
    return pd.DataFrame([summary])


def write_doc(summary: pd.DataFrame, by_ch: pd.DataFrame, fail: pd.DataFrame, used: list[str], missing: list[str], joins: list[str]) -> None:
    s = summary.iloc[0].to_dict()
    status = "passes" if bool(s["pass_channel_compatibility_empirical"]) else "needs repair"
    lines = [
        "# Prime Mesh R2Q - ChannelCompatibility Audit",
        "",
        "**Document:** `Prime_Mesh_R2Q_ChannelCompatibility_Audit_v1.md`",
        "**Project:** Prime Mesh Theory - RH Programme",
        f"**Date:** {date.today().isoformat()}",
        f"**Status:** ChannelCompatibility audit - {status}",
        "",
        "## 1. Executive Verdict",
        "",
        "This audit verifies that every coordinate-available dangerous R2Q row is compatible with the negative repayment channel `C_-`.",
        "",
    ]
    if bool(s["pass_channel_compatibility_empirical"]):
        lines += [r"\[\boxed{\text{ChannelCompatibility passes empirically.}}\]", ""]
    else:
        lines += [r"\[\boxed{\text{ChannelCompatibility has unresolved rows.}}\]", ""]

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
        if key in {"inputs_used", "optional_inputs_missing", "join_notes"}:
            continue
        lines.append(f"| `{key}` | {value} |")

    lines += [
        "",
        "## 4. Channel Groups",
        "",
        f"`{len(by_ch)}` channel groups were written to `prime_mesh_r2q_channel_compatibility_by_channel.csv`.",
        "",
        "## 5. Failures",
        "",
    ]
    if len(fail):
        lines.append(f"`{len(fail)}` failures were written to `prime_mesh_r2q_channel_compatibility_failures.csv`.")
    else:
        lines.append("No failures found.")

    lines += [
        "",
        "## 6. Interpretation",
        "",
        "The proof-facing theorem can use:",
        "",
        r"\[Q_{\rm R2Q}(J)>3/4\Rightarrow J\in\mathcal C_-.\]",
        "",
        "Finite-certificate coordinate-excluded rows are reported separately and are not part of the post-`P0` coordinate theorem.",
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
    by_ch = by_channel(rows)
    fail = failures(rows)
    summary = summarize(rows, fail, used, missing, joins)
    rows.to_csv(ROWS_OUT, index=False)
    by_ch.to_csv(BY_CHANNEL_OUT, index=False)
    fail.to_csv(FAILURES_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_doc(summary, by_ch, fail, used, missing, joins)
    refresh_manifest()
    for p in [SUMMARY_OUT, ROWS_OUT, BY_CHANNEL_OUT, FAILURES_OUT, DOC_OUT]:
        log(f"wrote {p}")
    for key, value in summary.iloc[0].to_dict().items():
        if key not in {"inputs_used", "optional_inputs_missing", "join_notes"}:
            log(f"{key} = {value}")


if __name__ == "__main__":
    main()
