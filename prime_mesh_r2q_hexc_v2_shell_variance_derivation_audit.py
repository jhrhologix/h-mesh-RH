#!/usr/bin/env python3
"""H-Exc V2 shell-variance derivation audit.

The H-Exc target suggests that the natural bridge-excursion constant is
sqrt(V2), where V2 is the bare shell-walk variance for

    w_2(p) = g(spf(p-2)) + g(spf(p+2)),  g(q)=1/(q(q-1)).

For p > 3, exactly one of p-2 and p+2 is divisible by 3, so

    w_2(p) = 1/6 + X_p,   X_p = g(spf(non-3 shift)).

The density-series formula is

    V2 = Var(X_p)
       = sum_{q>=5} \tilde d_q (g(q)-delta)^2
       = 2 epsilon_2 - 4 delta_tail^2,

with \tilde d_q = 2 d_q and

    d_q = 1/(q-1) * prod_{3 <= r < q} (r-2)/(r-1).

All outputs are written next to this script in the repair-process
``scripts and results`` directory.
"""

from __future__ import annotations

import math
import time
from pathlib import Path

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent


def find_repo_root(path: Path) -> Path:
    for p in [path, *path.parents]:
        if p.name == "prime-mesh-theory":
            return p
    raise RuntimeError(f"Could not locate prime-mesh-theory root from {path}")


ROOT = find_repo_root(OUT)
SITES = ROOT / "notes" / "prime_mesh_r2q_longa_shell_size_source_audit_sites.csv"
HEXC_SUMMARY = OUT / "prime_mesh_r2q_hexc_path_shape_summary.csv"
HEXC_INTERVALS = OUT / "prime_mesh_r2q_hexc_path_shape_intervals.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_hexc_v2_shell_variance_summary.csv"
TERMS_OUT = OUT / "prime_mesh_r2q_hexc_v2_shell_variance_terms.csv"
EMPIRICAL_OUT = OUT / "prime_mesh_r2q_hexc_v2_shell_variance_empirical.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_HExc_V2_Shell_Variance_Derivation_Audit_v1.md"
MANIFEST_OUT = OUT / "deposit_manifest.csv"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def primes_upto(n: int) -> list[int]:
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    r = int(math.isqrt(n))
    for p in range(2, r + 1):
        if sieve[p]:
            start = p * p
            sieve[start : n + 1 : p] = b"\x00" * (((n - start) // p) + 1)
    return [i for i in range(n + 1) if sieve[i]]


def g(q: int | float) -> float:
    qf = float(q)
    return 1.0 / (qf * (qf - 1.0))


def build_density_terms(q_max: int = 2_000_000) -> pd.DataFrame:
    """Build O1 SPF density terms for q>=5 up to q_max."""
    primes = [p for p in primes_upto(q_max) if p >= 3]
    prod = 1.0
    rows: list[dict[str, float]] = []
    for q in primes:
        if q == 3:
            prod *= (q - 2.0) / (q - 1.0)
            continue
        d_q = prod / (q - 1.0)
        tilde_d = 2.0 * d_q
        gq = g(q)
        rows.append(
            {
                "q": int(q),
                "d_q_O1": d_q,
                "tilde_d_q": tilde_d,
                "g_q": gq,
                "mean_term": tilde_d * gq,
                "second_term": tilde_d * gq * gq,
            }
        )
        prod *= (q - 2.0) / (q - 1.0)
    df = pd.DataFrame(rows)
    delta = float(df["mean_term"].sum())
    tail_mass = max(0.0, 1.0 - float(df["tilde_d_q"].sum()))
    if tail_mass:
        # The omitted large-SPF tail has negligible g(q) and g(q)^2 at this
        # cutoff, but it still contributes to centered variance as delta^2.
        tail = pd.DataFrame(
            [
                {
                    "q": -1,
                    "q_label": f">{q_max}",
                    "d_q_O1": tail_mass / 2.0,
                    "tilde_d_q": tail_mass,
                    "g_q": 0.0,
                    "mean_term": 0.0,
                    "second_term": 0.0,
                }
            ]
        )
        df["q_label"] = df["q"].astype(str)
        df = pd.concat([df, tail], ignore_index=True)
    else:
        df["q_label"] = df["q"].astype(str)
    df["variance_term"] = df["tilde_d_q"] * (df["g_q"] - delta) ** 2
    df["variance_term_abs"] = df["variance_term"].abs()
    df["mean_term_cumsum"] = df["mean_term"].cumsum()
    df["second_term_cumsum"] = df["second_term"].cumsum()
    df["variance_term_cumsum_using_truncated_delta"] = df["variance_term"].cumsum()
    return df


def empirical_from_sites() -> pd.DataFrame:
    if not SITES.exists():
        return pd.DataFrame()
    log(f"Reading LongA site table from {SITES}")
    sites = pd.read_csv(SITES, usecols=["block_id", "source_row", "p_star", "y", "h", "prime", "shell", "side", "spf_n"])
    for c in ["block_id", "source_row", "p_star", "y", "h", "prime", "shell", "spf_n"]:
        sites[c] = pd.to_numeric(sites[c], errors="coerce")
    sites["bare_g"] = 1.0 / (sites["spf_n"] * (sites["spf_n"] - 1.0))

    rows: list[dict[str, object]] = []
    group_cols = ["block_id", "source_row", "p_star", "y", "h", "prime", "shell"]
    walks = sites.groupby(group_cols, dropna=False)["bare_g"].sum().reset_index(name="w_shell")
    for shell, part in walks.groupby("shell"):
        values = part["w_shell"].to_numpy(dtype=float)
        rows.append(
            {
                "scope": f"LongA sites shell {int(shell)}",
                "shell": int(shell),
                "rows": int(len(values)),
                "mean_w": float(values.mean()),
                "var_w": float(values.var(ddof=0)),
                "std_w": float(values.std(ddof=0)),
                "min_w": float(values.min()),
                "max_w": float(values.max()),
            }
        )

    shell2 = walks[walks["shell"].eq(2)].copy()
    if len(shell2):
        shell2["residual_X"] = shell2["w_shell"] - (1.0 / 6.0)
        values = shell2["residual_X"].to_numpy(dtype=float)
        rows.append(
            {
                "scope": "LongA sites shell 2 residual X=w2-1/6",
                "shell": 2,
                "rows": int(len(values)),
                "mean_w": float(values.mean()),
                "var_w": float(values.var(ddof=0)),
                "std_w": float(values.std(ddof=0)),
                "min_w": float(values.min()),
                "max_w": float(values.max()),
            }
        )

    # A direct interval-level check: the shell-2 bare walk aggregated per interval.
    interval_walk = (
        sites[sites["shell"].eq(2)]
        .groupby(["block_id", "source_row", "p_star", "y", "h"], dropna=False)["bare_g"]
        .sum()
        .reset_index(name="W2_bare_interval")
    )
    if len(interval_walk):
        vals = interval_walk["W2_bare_interval"].to_numpy(dtype=float)
        rows.append(
            {
                "scope": "LongA interval aggregate shell 2 bare sum",
                "shell": 2,
                "rows": int(len(vals)),
                "mean_w": float(vals.mean()),
                "var_w": float(vals.var(ddof=0)),
                "std_w": float(vals.std(ddof=0)),
                "min_w": float(vals.min()),
                "max_w": float(vals.max()),
            }
        )
    return pd.DataFrame(rows)


def load_hexc_metrics() -> dict[str, float]:
    out: dict[str, float] = {}
    if HEXC_SUMMARY.exists():
        df = pd.read_csv(HEXC_SUMMARY)
        if len(df):
            for key in ["Q_exc_max", "Q_exc_mean", "Q_exc_median", "Q_exc_q95", "Q_exc_q99"]:
                if key in df.columns:
                    out[key] = float(pd.to_numeric(df.loc[0, key], errors="coerce"))
    if HEXC_INTERVALS.exists():
        intervals = pd.read_csv(HEXC_INTERVALS)
        intervals["p_star"] = pd.to_numeric(intervals["p_star"], errors="coerce")
        intervals["Q_exc"] = pd.to_numeric(intervals["Q_exc"], errors="coerce")
        tail = intervals[intervals["p_star"] >= 500_000_000]
        if len(tail):
            out["Q_exc_tail_max"] = float(tail["Q_exc"].max())
            out["Q_exc_tail_mean"] = float(tail["Q_exc"].mean())
        worst = intervals.loc[intervals["Q_exc"].idxmax()]
        out["worst_Q_block_id"] = int(worst["block_id"])
        out["worst_Q_p_star"] = int(worst["p_star"])
        out["worst_Q_h"] = int(worst["h"])
    return out


def refresh_manifest() -> None:
    rows = []
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            rows.append(
                {
                    "Name": p.name,
                    "Length": p.stat().st_size,
                    "LastWriteTime": pd.Timestamp(p.stat().st_mtime, unit="s"),
                }
            )
    pd.DataFrame(rows).to_csv(MANIFEST_OUT, index=False)


def write_doc(summary: dict[str, object], terms: pd.DataFrame, empirical: pd.DataFrame) -> None:
    lines = [
        "# Prime Mesh R2Q - H-Exc V2 Shell-Variance Derivation Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-07",
        "**Status:** Formula-grade V2 derivation audit",
        "",
        "## 1. Purpose",
        "",
        "This audit derives the H-Exc shell-variance constant from the bare shifted-SPF shell walk",
        "",
        r"\[",
        r"w_2(p)=g(\operatorname{spf}(p-2))+g(\operatorname{spf}(p+2)),",
        r"\qquad g(q)=\frac{1}{q(q-1)}.",
        r"\]",
        "",
        r"For primes \(p>3\), exactly one of \(p-2,p+2\) is divisible by 3, giving",
        "",
        r"\[",
        r"w_2(p)=\frac16+X_p,\qquad X_p=g(\operatorname{spf}(p_2^*)).",
        r"\]",
        "",
        "The variance target is",
        "",
        r"\[",
        r"V_2=\operatorname{Var}(X_p)=\sum_{q\ge5}\tilde d_q(g(q)-\delta)^2.",
        r"\]",
        "",
        "## 2. Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    for k, v in summary.items():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## 3. Dominant Series Terms",
        "",
        terms.sort_values("variance_term_abs", ascending=False)
        .head(20)
        .to_markdown(index=False),
        "",
        "## 4. Empirical LongA Site Check",
        "",
        empirical.to_markdown(index=False) if len(empirical) else "LongA site table was not available.",
        "",
        "## 5. Interpretation",
        "",
    ]
    ratio = float(summary.get("Q_exc_max_over_sqrt_V2_formula", float("nan")))
    if math.isfinite(ratio) and abs(ratio - 1.0) <= 0.01:
        lines += [
            r"\[",
            r"\boxed{\sqrt{V_2}\text{ matches the observed H-Exc maximum to within about }1\%.}",
            r"\]",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\sqrt{V_2}\text{ is the right scale to compare, but the observed maximum is not a direct equality.}}",
            r"\]",
        ]
    lines += [
        "",
        r"The dominant variance terms come from the small residual SPF classes \(q=5,7,11,\ldots\).  The explicit tail bucket has negligible mean but contributes centered variance.  This supports the deterministic H-Exc route: the internal bridge excursion is controlled by the shell-variance scale rather than by the large endpoint descent.",
        "",
        "## 6. Outputs",
        "",
        f"- `{SUMMARY_OUT.name}`",
        f"- `{TERMS_OUT.name}`",
        f"- `{EMPIRICAL_OUT.name}`",
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
    ]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    log("Building SPF density series")
    terms = build_density_terms()
    delta = float(terms["mean_term"].sum())
    second = float(terms["second_term"].sum())
    v2_formula = float(((terms["g_q"] - delta) ** 2 * terms["tilde_d_q"]).sum())
    sqrt_v2 = math.sqrt(v2_formula)

    # Same formula in the notation of the support note.
    # delta_tail = mu1 - 1/12, epsilon2=sum_{q>=5}d_q g(q)^2, with tilde=2d.
    delta_tail = delta / 2.0
    epsilon2 = second / 2.0
    v2_support_formula = 2.0 * epsilon2 - 4.0 * delta_tail * delta_tail

    empirical = empirical_from_sites()
    hexc = load_hexc_metrics()
    qmax = hexc.get("Q_exc_max", float("nan"))
    qtail = hexc.get("Q_exc_tail_max", float("nan"))

    terms["variance_share"] = terms["variance_term"] / v2_formula if v2_formula else np.nan
    terms["variance_share_cumsum_by_abs"] = (
        terms.sort_values("variance_term_abs", ascending=False)["variance_term"].cumsum() / v2_formula
    ).sort_index()

    empirical_shell2_var = float("nan")
    empirical_shell2_std = float("nan")
    if len(empirical):
        shell2 = empirical[empirical["scope"].eq("LongA sites shell 2")]
        if len(shell2):
            empirical_shell2_var = float(shell2["var_w"].iloc[0])
            empirical_shell2_std = float(shell2["std_w"].iloc[0])

    summary = {
        "q_max_series": int(terms.loc[terms["q"].gt(0), "q"].max()),
        "series_terms_including_tail_bucket": int(len(terms)),
        "series_prime_terms": int(terms["q"].gt(0).sum()),
        "tilde_density_mass_truncated": float(terms["tilde_d_q"].sum()),
        "delta_conditional_mean": delta,
        "delta_tail_support_notation": delta_tail,
        "epsilon2_support_notation": epsilon2,
        "V2_formula": v2_formula,
        "V2_support_formula_2eps_minus_4delta_tail_sq": v2_support_formula,
        "V2_formula_abs_delta": abs(v2_formula - v2_support_formula),
        "sqrt_V2_formula": sqrt_v2,
        "Q_exc_max": qmax,
        "Q_exc_tail_max": qtail,
        "Q_exc_max_over_sqrt_V2_formula": qmax / sqrt_v2 if sqrt_v2 else np.nan,
        "Q_exc_tail_max_over_sqrt_V2_formula": qtail / sqrt_v2 if sqrt_v2 else np.nan,
        "sqrt_V2_minus_Q_exc_max": sqrt_v2 - qmax,
        "relative_gap_sqrt_V2_vs_Q_exc_max": (sqrt_v2 - qmax) / sqrt_v2 if sqrt_v2 else np.nan,
        "empirical_Longa_shell2_var_w": empirical_shell2_var,
        "empirical_Longa_shell2_std_w": empirical_shell2_std,
        "empirical_Longa_shell2_var_over_V2_formula": empirical_shell2_var / v2_formula
        if v2_formula and math.isfinite(empirical_shell2_var)
        else np.nan,
        "dominant_q_by_variance": str(terms.sort_values("variance_term_abs", ascending=False).iloc[0]["q_label"]),
        "top5_variance_share_abs_order": float(
            terms.sort_values("variance_term_abs", ascending=False).head(5)["variance_term"].sum() / v2_formula
        ),
        "worst_Q_block_id": hexc.get("worst_Q_block_id", np.nan),
        "worst_Q_p_star": hexc.get("worst_Q_p_star", np.nan),
        "worst_Q_h": hexc.get("worst_Q_h", np.nan),
        "pass_Q_exc_matches_sqrt_V2_within_1pct": bool(abs(qmax / sqrt_v2 - 1.0) <= 0.01)
        if sqrt_v2 and math.isfinite(qmax)
        else False,
        "pass_tail_below_sqrt_V2": bool(qtail < sqrt_v2) if math.isfinite(qtail) else False,
    }

    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)
    terms.to_csv(TERMS_OUT, index=False)
    empirical.to_csv(EMPIRICAL_OUT, index=False)
    write_doc(summary, terms, empirical)
    refresh_manifest()

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {TERMS_OUT}")
    log(f"Wrote {EMPIRICAL_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k, v in summary.items():
        log(f"{k} = {v}")


if __name__ == "__main__":
    main()
