#!/usr/bin/env python
"""O2.1 full correction-matrix/SVD audit.

Builds the full correction block C={0,2,3,4} from the R2Q B2-active
sym_all shell fields, computes spectral structure, fitted response, canonical
response alignment, and observed projection leakage proxies.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
DOCS = ROOT / "docs" / "RH" / "notes"

INPUT = NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"
O2_SUMMARY = NOTES / "prime_mesh_r2q_o2_projection_orthogonality_audit_summary.csv"
O2D_SUMMARY = NOTES / "prime_mesh_r2q_o2d_slack_absorption_summary.csv"

SUMMARY_OUT = NOTES / "prime_mesh_r2q_o2p1_fullmatrix_svd_summary.csv"
MATRICES_OUT = NOTES / "prime_mesh_r2q_o2p1_fullmatrix_svd_matrices.csv"
VECTORS_OUT = NOTES / "prime_mesh_r2q_o2p1_fullmatrix_svd_vectors.csv"
DOC_OUT = DOCS / "RH" / "notes" / "Prime_Mesh_R2Q_O2p1_FullMatrix_SVD_Result_v1.md"

# Correct DOC_OUT if this script is run from repo root layout.
DOC_OUT = DOCS / "Prime_Mesh_R2Q_O2p1_FullMatrix_SVD_Result_v1.md"


SHELLS = [0, 2, 3, 4]
BASIS = "sym_all"
SHELL_COLS = [f"shell_{BASIS}_{j}" for j in SHELLS]

# Full B2-active canonical vector from the previous O1/O2 fit, correction block
# ordered as C={0,2,3,4}.
A_CAN_AMP = np.array([0.191352, -0.148199, 1.221515, -0.439357], dtype=float)
A_CAN_SIGN = np.array([1.0, -1.0, 1.0, -1.0], dtype=float)
MODE_PM_PM = np.array([1.0, -1.0, 1.0, -1.0], dtype=float)
MODE_PM_MP = np.array([1.0, -1.0, -1.0, 1.0], dtype=float)


def log(msg: str) -> None:
    from datetime import datetime

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def vec_to_json(v: np.ndarray) -> str:
    return json.dumps([float(x) for x in v])


def mat_to_json(m: np.ndarray) -> str:
    return json.dumps([[float(x) for x in row] for row in m])


def signs_array(a: np.ndarray, tol: float = 1e-12) -> list[str]:
    out = []
    for x in a:
        if x > tol:
            out.append("+")
        elif x < -tol:
            out.append("-")
        else:
            out.append("0")
    return out


def signs_matrix(m: np.ndarray, tol: float = 1e-12) -> str:
    return ";".join("".join(signs_array(row, tol)) for row in m)


def cos(u: np.ndarray, v: np.ndarray) -> float:
    nu = np.linalg.norm(u)
    nv = np.linalg.norm(v)
    if nu == 0 or nv == 0:
        return float("nan")
    return float(np.dot(u, v) / (nu * nv))


def load_metric(path: Path, key: str, default: float = np.nan) -> float:
    if not path.exists():
        return default
    try:
        df = pd.read_csv(path)
        if key in df.columns and len(df):
            return float(pd.to_numeric(df.loc[0, key], errors="coerce"))
    except Exception:
        return default
    return default


def main() -> None:
    log(f"Reading {INPUT}")
    df = pd.read_csv(INPUT)
    for c in SHELL_COLS + [
        "cp_obstruction",
        "cp_residual",
        "denom_sqrt_h_logB",
        "canonical_scaled_E_post",
        "canonical_scaled_Q_post",
        "fitted_E_post",
        "fitted_Q_post",
    ]:
        if c in df.columns:
            df[c] = num(df[c])

    missing = [c for c in SHELL_COLS if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing shell columns: {missing}")

    # The B2-active target used in prior fits is positive CP underperformance.
    X = df[SHELL_COLS].to_numpy(dtype=float)
    y = df["cp_obstruction"].fillna(0.0).to_numpy(dtype=float)
    rows = len(df)

    G = X.T @ X
    b = X.T @ y
    ridge = 1e-9 * np.trace(G) / G.shape[0]
    G_ridge = G + ridge * np.eye(G.shape[0])
    G_inv = np.linalg.pinv(G_ridge)
    a_fit = G_inv @ b

    # Normalize all response vectors so their index-shell-1 analog, here shell 2
    # in the correction block, has comparable sign/magnitude when possible.
    # For C={0,2,3,4}, the second component is shell 2.
    if abs(a_fit[1]) > 1e-15:
        a_fit_norm = a_fit / abs(a_fit[1])
    else:
        a_fit_norm = a_fit.copy()

    # Empirical covariance scale; eigenvalues of symmetric PSD G.
    evals, evecs = np.linalg.eigh(G)
    order = np.argsort(evals)[::-1]
    evals = evals[order]
    evecs = evecs[:, order]
    v1 = evecs[:, 0]
    if v1[0] < 0:
        v1 = -v1
    total = float(np.sum(evals))
    lambda1 = float(evals[0])
    lambda2 = float(evals[1])
    rank1_fraction = lambda1 / total if total else np.nan
    eig2_over_eig1 = lambda2 / lambda1 if lambda1 else np.nan
    delta_full = (lambda1 - lambda2) / lambda1 if lambda1 else np.nan
    H = G - lambda1 * np.outer(v1, v1)
    H_norm = float(np.linalg.norm(H, ord=2))
    H_norm_over_lambda = H_norm / lambda1 if lambda1 else np.nan

    # Compare dominant covariance and inverse-response modes.
    dom_cos_pmpm = abs(cos(v1, MODE_PM_PM))
    dom_cos_pmmp = abs(cos(v1, MODE_PM_MP))
    inv = np.linalg.pinv(G_ridge)
    inv_evals, inv_evecs = np.linalg.eigh(inv)
    inv_order = np.argsort(np.abs(inv_evals))[::-1]
    inv_v1 = inv_evecs[:, inv_order[0]]
    if inv_v1[0] < 0:
        inv_v1 = -inv_v1

    cos_fit_sign = cos(a_fit, A_CAN_SIGN)
    cos_fit_amp = cos(a_fit, A_CAN_AMP)
    abs_cos_fit_sign = abs(cos_fit_sign)
    abs_cos_fit_amp = abs(cos_fit_amp)
    projection_leakage_proxy = (max(0.0, 1.0 - abs_cos_fit_amp**2)) ** 0.5 if np.isfinite(abs_cos_fit_amp) else np.nan

    denom = df["denom_sqrt_h_logB"].replace(0, np.nan)
    canonical_scaled_post_Q_max = float(df["canonical_scaled_Q_post"].max())
    canonical_scaled_post_Q_tail_max = (
        float(df.loc[df["is_tail"].astype(str).str.lower().isin(["true", "1"]), "canonical_scaled_Q_post"].max())
        if "is_tail" in df.columns
        else np.nan
    )
    projection_leakage_Q_proxy_max = load_metric(O2D_SUMMARY, "projection_leakage_Q_proxy_max")
    if np.isnan(projection_leakage_Q_proxy_max):
        fitted_Q = (-df["fitted_E_post"] / denom).clip(lower=0)
        can_Q = (-df["canonical_scaled_E_post"] / denom).clip(lower=0)
        projection_leakage_Q_proxy_max = float((can_Q - fitted_Q).clip(lower=0).max())

    canonical_scaled_post_max_abs_shell_cos = load_metric(
        O2_SUMMARY, "canonical_scaled_post_max_abs_shell_cos"
    )
    canonical_scaled_post_max_abs_shell_corr = load_metric(
        O2_SUMMARY, "canonical_scaled_post_max_abs_shell_corr"
    )

    summary = {
        "rows": rows,
        "basis": BASIS,
        "scope": "B2-active full interval inventory",
        "shells": ",".join(map(str, SHELLS)),
        "lambda1": lambda1,
        "lambda2": lambda2,
        "lambda3": float(evals[2]),
        "lambda4": float(evals[3]),
        "rank1_fraction": rank1_fraction,
        "eig2_over_eig1": eig2_over_eig1,
        "delta_full": delta_full,
        "H_norm_over_lambda": H_norm_over_lambda,
        "dominant_mode_cos_plus_minus_plus_minus": dom_cos_pmpm,
        "dominant_mode_cos_plus_minus_minus_plus": dom_cos_pmmp,
        "inverse_dominant_mode_cos_plus_minus_plus_minus": abs(cos(inv_v1, MODE_PM_PM)),
        "inverse_dominant_mode_cos_plus_minus_minus_plus": abs(cos(inv_v1, MODE_PM_MP)),
        "G_CC_signs": signs_matrix(G),
        "G_CC_inverse_signs": signs_matrix(inv),
        "a_fit": vec_to_json(a_fit_norm),
        "a_fit_raw": vec_to_json(a_fit),
        "a_fit_signs": "".join(signs_array(a_fit)),
        "a_can_sign": vec_to_json(A_CAN_SIGN),
        "a_can_amp": vec_to_json(A_CAN_AMP),
        "cos_fit_vs_can_sign": cos_fit_sign,
        "cos_fit_vs_can_amp": cos_fit_amp,
        "abs_cos_fit_vs_can_sign": abs_cos_fit_sign,
        "abs_cos_fit_vs_can_amp": abs_cos_fit_amp,
        "projection_leakage_proxy": projection_leakage_proxy,
        "canonical_scaled_post_max_abs_shell_cos": canonical_scaled_post_max_abs_shell_cos,
        "canonical_scaled_post_max_abs_shell_corr": canonical_scaled_post_max_abs_shell_corr,
        "projection_leakage_Q_proxy_max": projection_leakage_Q_proxy_max,
        "canonical_scaled_post_Q_max": canonical_scaled_post_Q_max,
        "canonical_scaled_post_Q_tail_max": canonical_scaled_post_Q_tail_max,
        "pass_rank1_0p99": rank1_fraction >= 0.99,
        "pass_delta_0p10": delta_full >= 0.10,
        "pass_delta_0p25": delta_full >= 0.25,
        "pass_cos_0p95": abs_cos_fit_amp >= 0.95,
        "pass_cos_0p98": abs_cos_fit_amp >= 0.98,
        "pass_projection_Q_0p05": projection_leakage_Q_proxy_max < 0.05,
        "ridge": ridge,
    }

    matrices = []
    for name, mat in [
        ("G_CC_empirical", G),
        ("G_CC_inverse", inv),
        ("rank1_lambda_vvT", lambda1 * np.outer(v1, v1)),
        ("H_residual", H),
    ]:
        for i, ri in enumerate(SHELLS):
            for j, cj in enumerate(SHELLS):
                matrices.append(
                    {
                        "matrix": name,
                        "row_shell": ri,
                        "col_shell": cj,
                        "value": mat[i, j],
                        "sign": signs_array(np.array([mat[i, j]]))[0],
                    }
                )

    vectors = []
    for name, vec in [
        ("eigenvalues_desc", evals),
        ("dominant_eigenvector_G", v1),
        ("dominant_eigenvector_G_inverse", inv_v1),
        ("b_C", b),
        ("a_fit_raw", a_fit),
        ("a_fit_norm_by_abs_shell2", a_fit_norm),
        ("a_can_sign", A_CAN_SIGN),
        ("a_can_amp", A_CAN_AMP),
        ("mode_plus_minus_plus_minus", MODE_PM_PM),
        ("mode_plus_minus_minus_plus", MODE_PM_MP),
    ]:
        for i, value in enumerate(vec):
            vectors.append(
                {
                    "vector": name,
                    "index": i,
                    "shell": SHELLS[i] if len(vec) == len(SHELLS) else i,
                    "value": value,
                    "sign": signs_array(np.array([value]))[0],
                }
            )

    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([summary]).to_csv(SUMMARY_OUT, index=False)
    pd.DataFrame(matrices).to_csv(MATRICES_OUT, index=False)
    pd.DataFrame(vectors).to_csv(VECTORS_OUT, index=False)

    with DOC_OUT.open("w", encoding="utf-8") as f:
        f.write("# Prime Mesh R2Q - O2.1 Full-Matrix/SVD Result\n\n")
        f.write("**Document:** `Prime_Mesh_R2Q_O2p1_FullMatrix_SVD_Result_v1.md`  \n")
        f.write("**Project:** Prime Mesh Theory - RH Programme  \n")
        f.write("**Date:** 2026-05-07  \n")
        f.write("**Status:** O2.1 full correction-matrix/SVD computation result\n\n")
        f.write("## 1. Purpose\n\n")
        f.write(
            "This computation builds the full correction covariance matrix "
            "\\(G_{CC}\\) for shells \\(C=\\{0,2,3,4\\}\\) using the B2-active "
            "`sym_all` shell fields, computes its SVD/eigenstructure, fits "
            "\\(a_{\\rm fit}=G_{CC}^{-1}b_C\\), and compares the fitted response "
            "to the canonical O1 response.\n\n"
        )
        f.write("## 2. Summary\n\n")
        f.write(pd.DataFrame([summary]).T.reset_index().rename(columns={"index": "metric", 0: "value"}).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 3. Matrix Entries\n\n")
        f.write(pd.DataFrame(matrices).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 4. Vectors\n\n")
        f.write(pd.DataFrame(vectors).to_markdown(index=False))
        f.write("\n\n")
        f.write("## 5. Interpretation\n\n")
        if summary["pass_rank1_0p99"] and summary["pass_delta_0p10"] and summary["pass_cos_0p95"] and summary["pass_projection_Q_0p05"]:
            f.write(
                "The full correction matrix passes the requested strong O2.1 "
                "criteria: rank-one structure, full spectral gap, canonical "
                "response alignment, and observed projection leakage below the "
                "O2 budget threshold.\n\n"
            )
            f.write("\\[\n\\boxed{\\text{O2.1 is formula-grade at the full-matrix/SVD level, pending formal write-up.}}\n\\]\n")
        else:
            f.write(
                "The full correction matrix gives a partial O2.1 result.  The "
                "failed criteria identify the remaining matrix/projection "
                "obligation.\n"
            )
        f.write("\n---\n\n")
        f.write("*Prime Mesh Theory - RH Programme*\n")

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {MATRICES_OUT}")
    log(f"Wrote {VECTORS_OUT}")
    log(f"Wrote {DOC_OUT}")
    for k in [
        "rank1_fraction",
        "delta_full",
        "H_norm_over_lambda",
        "dominant_mode_cos_plus_minus_plus_minus",
        "dominant_mode_cos_plus_minus_minus_plus",
        "cos_fit_vs_can_amp",
        "projection_leakage_Q_proxy_max",
        "canonical_scaled_post_Q_max",
        "canonical_scaled_post_Q_tail_max",
        "pass_rank1_0p99",
        "pass_delta_0p10",
        "pass_cos_0p95",
        "pass_projection_Q_0p05",
    ]:
        log(f"{k} = {summary[k]}")


if __name__ == "__main__":
    main()
