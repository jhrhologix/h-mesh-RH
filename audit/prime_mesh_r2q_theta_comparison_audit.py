#!/usr/bin/env python
"""Compare R2Q crossing diagnostics with Chebyshev theta error signs.

Question:
    Do R2Q forbidden-crossing / B2-active diagnostics see both positive and
    negative crossings of theta(x)-x?

The audit uses two theta objects:
  1. local interval error, already available as sum_{y<p<=y+h} log p - h;
  2. cumulative endpoint error theta(x)-x, computed at the interval endpoints
     by a segmented sieve.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
DOCS = ROOT / "docs" / "RH" / "notes"

INPUT = NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"

SUMMARY_OUT = NOTES / "prime_mesh_r2q_theta_comparison_audit_summary.csv"
SCOPES_OUT = NOTES / "prime_mesh_r2q_theta_comparison_audit_scopes.csv"
ROWS_OUT = NOTES / "prime_mesh_r2q_theta_comparison_audit_rows.csv"
DOC_OUT = DOCS / "Prime_Mesh_R2Q_Theta_Comparison_Audit_v1.md"


def log(msg: str) -> None:
    from datetime import datetime

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def base_primes(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    if limit >= 0:
        sieve[0:2] = b"\x00\x00"
    r = int(math.isqrt(limit))
    for p in range(2, r + 1):
        if sieve[p]:
            start = p * p
            sieve[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)
    return [i for i, v in enumerate(sieve) if v]


def theta_at_queries(queries: list[int], segment_size: int = 2_000_000) -> dict[int, float]:
    """Return theta(q)=sum_{p<=q} log p for sorted query points."""
    qs = sorted(set(int(q) for q in queries if q >= 2))
    if not qs:
        return {}
    max_n = qs[-1]
    primes = base_primes(int(math.isqrt(max_n)) + 1)
    out: dict[int, float] = {}
    theta = 0.0
    qi = 0

    low = 2
    while low <= max_n:
        high = min(max_n, low + segment_size - 1)
        size = high - low + 1
        seg = bytearray(b"\x01") * size
        for p in primes:
            pp = p * p
            if pp > high:
                break
            start = max(pp, ((low + p - 1) // p) * p)
            seg[start - low : size : p] = b"\x00" * (((high - start) // p) + 1)

        # Answer any queries before primes in this segment.
        while qi < len(qs) and qs[qi] < low:
            out[qs[qi]] = theta
            qi += 1

        for offset, is_prime in enumerate(seg):
            n = low + offset
            if is_prime and n >= 2:
                theta += math.log(n)
            while qi < len(qs) and qs[qi] == n:
                out[qs[qi]] = theta
                qi += 1

        while qi < len(qs) and qs[qi] <= high:
            out[qs[qi]] = theta
            qi += 1
        low = high + 1
        if low % (50_000_000) < segment_size:
            log(f"theta sieve reached {high:,} / {max_n:,}")

    while qi < len(qs):
        out[qs[qi]] = theta
        qi += 1
    return out


def norm_theta(err: pd.Series, x: pd.Series) -> pd.Series:
    x = x.replace(0, np.nan)
    return err / (np.sqrt(x) * np.log(x).pow(2))


def sign_label(v: float, eps: float = 1e-12) -> str:
    if pd.isna(v):
        return "nan"
    if v > eps:
        return "positive"
    if v < -eps:
        return "negative"
    return "zero"


def summarize(df: pd.DataFrame, scope: str) -> dict[str, object]:
    pos_end = (df["theta_end_error"] > 0).sum()
    neg_end = (df["theta_end_error"] < 0).sum()
    pos_local = (df["theta_local_error"] > 0).sum()
    neg_local = (df["theta_local_error"] < 0).sum()
    return {
        "scope": scope,
        "rows": len(df),
        "theta_end_pos_rows": int(pos_end),
        "theta_end_neg_rows": int(neg_end),
        "theta_end_pos_frac": pos_end / len(df) if len(df) else np.nan,
        "theta_end_neg_frac": neg_end / len(df) if len(df) else np.nan,
        "theta_local_pos_rows": int(pos_local),
        "theta_local_neg_rows": int(neg_local),
        "theta_local_pos_frac": pos_local / len(df) if len(df) else np.nan,
        "theta_local_neg_frac": neg_local / len(df) if len(df) else np.nan,
        "theta_end_norm_abs_max": df["theta_end_norm"].abs().max(),
        "theta_start_norm_abs_max": df["theta_start_norm"].abs().max(),
        "theta_local_norm_abs_max": df["theta_local_norm"].abs().max(),
        "mean_theta_end_norm": df["theta_end_norm"].mean(),
        "mean_theta_local_norm": df["theta_local_norm"].mean(),
        "post_Q_max": df["post_Q"].max(),
        "mr2_Q_max": df["Q_max"].max() if "Q_max" in df else np.nan,
        "corr_postQ_abs_theta_end_norm": df["post_Q"].corr(df["theta_end_norm"].abs())
        if len(df) > 2
        else np.nan,
        "corr_mr2Q_abs_theta_local_norm": df["Q_max"].corr(df["theta_local_norm"].abs())
        if "Q_max" in df and len(df) > 2
        else np.nan,
        "corr_cp_ratio_theta_local_norm": df["cp_ratio"].corr(df["theta_local_norm"])
        if "cp_ratio" in df and len(df) > 2
        else np.nan,
    }


def main() -> None:
    log(f"Reading {INPUT}")
    df = pd.read_csv(INPUT)

    for c in [
        "p_star",
        "y",
        "h",
        "hi",
        "block_id",
        "prime_log_sum",
        "Q_max",
        "cp_ratio",
        "canonical_scaled_E_post",
        "denom_sqrt_h_logB",
        "D_y",
        "D_y_plus_h",
        "d_worst",
    ]:
        if c in df.columns:
            df[c] = num(df[c])

    if "hi" not in df.columns:
        df["hi"] = df["y"] + df["h"]

    df["post_z"] = df["canonical_scaled_E_post"] / df["denom_sqrt_h_logB"].replace(0, np.nan)
    df["post_Q"] = (-df["post_z"]).clip(lower=0)
    df["theta_local_error"] = df["prime_log_sum"] - df["h"]
    df["theta_local_norm"] = df["theta_local_error"] / (
        np.sqrt(df["h"].replace(0, np.nan)) * np.log(df["p_star"]).pow(2)
    )

    queries = []
    for col in ["y", "hi", "p_star"]:
        queries.extend(df[col].dropna().astype(int).tolist())

    log(f"Computing theta at {len(set(queries))} unique endpoints up to {max(queries):,}")
    theta_map = theta_at_queries(queries)

    df["theta_start"] = df["y"].astype(int).map(theta_map)
    df["theta_end"] = df["hi"].astype(int).map(theta_map)
    df["theta_pstar"] = df["p_star"].astype(int).map(theta_map)
    df["theta_start_error"] = df["theta_start"] - df["y"]
    df["theta_end_error"] = df["theta_end"] - df["hi"]
    df["theta_pstar_error"] = df["theta_pstar"] - df["p_star"]
    df["theta_local_sum_from_sieve"] = df["theta_end"] - df["theta_start"]
    df["prime_log_sum_check_delta"] = df["prime_log_sum"] - df["theta_local_sum_from_sieve"]
    df["theta_start_norm"] = norm_theta(df["theta_start_error"], df["y"])
    df["theta_end_norm"] = norm_theta(df["theta_end_error"], df["hi"])
    df["theta_pstar_norm"] = norm_theta(df["theta_pstar_error"], df["p_star"])

    df["theta_start_sign"] = df["theta_start_error"].map(sign_label)
    df["theta_end_sign"] = df["theta_end_error"].map(sign_label)
    df["theta_local_sign"] = df["theta_local_error"].map(sign_label)
    df["theta_crosses_sign"] = df["theta_start_sign"].ne(df["theta_end_sign"])
    df.loc[df["theta_start_sign"].eq("zero") | df["theta_end_sign"].eq("zero"), "theta_crosses_sign"] = False
    df["is_tail_bool"] = df["is_tail"].astype(str).str.lower().isin(["true", "1"]) if "is_tail" in df else False
    df["forbidden_proxy"] = df["Q_max"] > 1 if "Q_max" in df else False
    df["near_forbidden_proxy"] = df["Q_max"] > 0.75 if "Q_max" in df else False

    scopes = [summarize(df, "global")]
    for col, prefix in [
        ("is_tail_bool", "tail"),
        ("scale_bin", "scale"),
        ("depth_bin", "depth"),
        ("mu_bin", "mu"),
        ("theta_end_sign", "theta_end_sign"),
        ("theta_local_sign", "theta_local_sign"),
        ("near_forbidden_proxy", "near_forbidden"),
    ]:
        if col in df.columns:
            for key, g in df.groupby(col, dropna=False):
                scopes.append(summarize(g, f"{prefix}:{key}"))
    scopes_df = pd.DataFrame(scopes)

    # Detection table: do R2Q active/near-forbidden rows include both theta signs?
    positive_rows = df[df["theta_end_error"] > 0]
    negative_rows = df[df["theta_end_error"] < 0]
    local_pos = df[df["theta_local_error"] > 0]
    local_neg = df[df["theta_local_error"] < 0]

    summary = {
        "rows": len(df),
        "theta_endpoint_positive_rows": len(positive_rows),
        "theta_endpoint_negative_rows": len(negative_rows),
        "theta_endpoint_positive_frac": len(positive_rows) / len(df),
        "theta_endpoint_negative_frac": len(negative_rows) / len(df),
        "theta_local_positive_rows": len(local_pos),
        "theta_local_negative_rows": len(local_neg),
        "theta_local_positive_frac": len(local_pos) / len(df),
        "theta_local_negative_frac": len(local_neg) / len(df),
        "theta_endpoint_sign_cross_rows": int(df["theta_crosses_sign"].sum()),
        "theta_endpoint_norm_abs_max": df["theta_end_norm"].abs().max(),
        "theta_local_norm_abs_max": df["theta_local_norm"].abs().max(),
        "theta_pstar_norm_abs_max": df["theta_pstar_norm"].abs().max(),
        "prime_log_sum_check_abs_max": df["prime_log_sum_check_delta"].abs().max(),
        "prime_log_sum_check_mean_abs": df["prime_log_sum_check_delta"].abs().mean(),
        "prime_log_sum_check_nonzero_rows_gt_1e_9": int((df["prime_log_sum_check_delta"].abs() > 1e-9).sum()),
        "near_forbidden_rows_Q_gt_0p75": int(df["near_forbidden_proxy"].sum()),
        "near_forbidden_theta_endpoint_positive_rows": int((df["near_forbidden_proxy"] & (df["theta_end_error"] > 0)).sum()),
        "near_forbidden_theta_endpoint_negative_rows": int((df["near_forbidden_proxy"] & (df["theta_end_error"] < 0)).sum()),
        "near_forbidden_theta_local_positive_rows": int((df["near_forbidden_proxy"] & (df["theta_local_error"] > 0)).sum()),
        "near_forbidden_theta_local_negative_rows": int((df["near_forbidden_proxy"] & (df["theta_local_error"] < 0)).sum()),
        "forbidden_rows_Q_gt_1": int(df["forbidden_proxy"].sum()),
        "corr_Qmax_abs_theta_local_norm": df["Q_max"].corr(df["theta_local_norm"].abs()) if "Q_max" in df else np.nan,
        "corr_Qmax_theta_local_norm": df["Q_max"].corr(df["theta_local_norm"]) if "Q_max" in df else np.nan,
        "corr_postQ_abs_theta_end_norm": df["post_Q"].corr(df["theta_end_norm"].abs()),
        "corr_postQ_theta_end_norm": df["post_Q"].corr(df["theta_end_norm"]),
        "corr_dworst_theta_pstar_norm": df["d_worst"].corr(df["theta_pstar_norm"]) if "d_worst" in df else np.nan,
        "max_positive_theta_end_norm": df["theta_end_norm"].max(),
        "min_negative_theta_end_norm": df["theta_end_norm"].min(),
        "max_positive_theta_local_norm": df["theta_local_norm"].max(),
        "min_negative_theta_local_norm": df["theta_local_norm"].min(),
    }

    rows_keep = [
        "block_id",
        "p_star",
        "y",
        "hi",
        "h",
        "prime_log_sum",
        "theta_local_error",
        "theta_local_sum_from_sieve",
        "prime_log_sum_check_delta",
        "theta_local_norm",
        "theta_start_error",
        "theta_end_error",
        "theta_end_norm",
        "theta_pstar_error",
        "theta_pstar_norm",
        "theta_start_sign",
        "theta_end_sign",
        "theta_local_sign",
        "theta_crosses_sign",
        "Q_max",
        "near_forbidden_proxy",
        "post_Q",
        "cp_ratio",
        "d_worst",
        "is_tail",
        "scale_bin",
        "depth_bin",
        "mu_bin",
    ]
    rows_keep = [c for c in rows_keep if c in df.columns]

    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)
    scopes_df.to_csv(SCOPES_OUT, index=False)
    df[rows_keep].to_csv(ROWS_OUT, index=False)

    with DOC_OUT.open("w", encoding="utf-8") as f:
        f.write("# Prime Mesh R2Q - Theta Comparison Audit\n\n")
        f.write("**Document:** `Prime_Mesh_R2Q_Theta_Comparison_Audit_v1.md`  \n")
        f.write("**Project:** Prime Mesh Theory - RH Programme  \n")
        f.write("**Date:** 2026-05-06  \n")
        f.write("**Status:** R2Q-to-theta sign comparison diagnostic\n\n")
        f.write("## 1. Purpose\n\n")
        f.write(
            "This audit checks whether the R2Q B2-active / near-forbidden "
            "crossing diagnostics see both signs of the Chebyshev error "
            "\\(\\theta(x)-x\\).  It measures both local interval theta error "
            "and cumulative endpoint theta error.\n\n"
        )
        f.write("## 2. Summary\n\n")
        f.write(pd.DataFrame([summary]).T.reset_index().rename(columns={"index": "metric", 0: "value"}).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 3. Scope Table\n\n")
        f.write(scopes_df.to_markdown(index=False))
        f.write("\n\n")
        f.write("## 4. Interpretation\n\n")
        f.write(
            "The key output is whether positive and negative theta signs both "
            "appear inside the R2Q active and near-forbidden rows.  If only one "
            "sign appears, the R2Q tail closure would need an additional dual "
            "or reflected argument for the other sign.\n\n"
        )
        f.write("---\n\n")
        f.write("*Prime Mesh Theory - RH Programme*\n")

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {SCOPES_OUT}")
    log(f"Wrote {ROWS_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k, v in summary.items():
        if k in [
            "theta_endpoint_positive_rows",
            "theta_endpoint_negative_rows",
            "theta_local_positive_rows",
            "theta_local_negative_rows",
            "near_forbidden_rows_Q_gt_0p75",
            "near_forbidden_theta_endpoint_positive_rows",
            "near_forbidden_theta_endpoint_negative_rows",
            "near_forbidden_theta_local_positive_rows",
            "near_forbidden_theta_local_negative_rows",
            "corr_Qmax_theta_local_norm",
        ]:
            log(f"{k} = {v}")


if __name__ == "__main__":
    main()
