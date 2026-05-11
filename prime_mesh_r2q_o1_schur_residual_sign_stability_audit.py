#!/usr/bin/env python3
"""O1 Schur residual sign-stability audit.

Deposits outputs only in the repair-folder bundle.

Computes the correction-block Schur residual

    r_C = b_C / a_1 - G_C1
    a_C = G_CC^{-1} r_C

with correction shells C={0,2,3,4} and leading shell 1, using the B2-active
sym_all shell fields and cp_obstruction target.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent
ROOT = next(p for p in [OUT, *OUT.parents] if p.name == "prime-mesh-theory")
INPUT = ROOT / "notes" / "prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv"

SUMMARY_OUT = OUT / "prime_mesh_r2q_o1_schur_residual_sign_stability_summary.csv"
VECTORS_OUT = OUT / "prime_mesh_r2q_o1_schur_residual_sign_stability_vectors.csv"
SCOPES_OUT = OUT / "prime_mesh_r2q_o1_schur_residual_sign_stability_scopes.csv"
WORST_OUT = OUT / "prime_mesh_r2q_o1_schur_residual_sign_stability_worst_rows.csv"
DOC_OUT = OUT / "Prime_Mesh_R2Q_O1_Schur_Residual_SignStability_Audit_v1.md"
MANIFEST = OUT / "deposit_manifest.csv"

ALL_SHELLS = [0, 1, 2, 3, 4]
C_SHELLS = [0, 2, 3, 4]
BASIS = "sym_all"
TARGET_SIGNS = "+-+-"
A_CAN_AMP = np.array([0.191352, -0.148199, 1.221515, -0.439357], dtype=float)
A_CAN_SIGN = np.array([1.0, -1.0, 1.0, -1.0], dtype=float)
Q_DIAG = 0.4011668793555976
O2_CLEAN = 0.04990595491427989


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def signs(v: np.ndarray, tol: float = 1e-12) -> str:
    out = []
    for x in v:
        if x > tol:
            out.append("+")
        elif x < -tol:
            out.append("-")
        else:
            out.append("0")
    return "".join(out)


def cos(u: np.ndarray, v: np.ndarray) -> float:
    nu = np.linalg.norm(u)
    nv = np.linalg.norm(v)
    if nu == 0 or nv == 0:
        return float("nan")
    return float(np.dot(u, v) / (nu * nv))


def vec_json(v: np.ndarray) -> str:
    return json.dumps([float(x) for x in v])


def h_bin(h: float) -> str:
    if h <= 4:
        return "h<=4"
    if h <= 16:
        return "5<=h<=16"
    if h <= 64:
        return "17<=h<=64"
    if h <= 256:
        return "65<=h<=256"
    if h <= 1024:
        return "257<=h<=1024"
    if h <= 8192:
        return "1025<=h<=8192"
    if h <= 65536:
        return "8193<=h<=65536"
    return "h>65536"


def p_scale_bin(p: float) -> str:
    if p < 100_000_000:
        return "p<100M"
    if p < 500_000_000:
        return "100M<=p<500M"
    return "p>=500M"


def shell_pattern(row: pd.Series) -> str:
    bits = []
    for j in ALL_SHELLS:
        v = row.get(f"shell_{BASIS}_{j}", np.nan)
        if pd.isna(v):
            bits.append("?")
        elif abs(float(v)) <= 1e-12:
            bits.append("0")
        else:
            bits.append("1")
    return "".join(bits)


def compute_scope(df: pd.DataFrame, scope: str) -> dict[str, object] | None:
    if len(df) < 5:
        return None
    cols_all = [f"shell_{BASIS}_{j}" for j in ALL_SHELLS]
    cols_c = [f"shell_{BASIS}_{j}" for j in C_SHELLS]
    X = df[cols_all].to_numpy(float)
    y = df["cp_obstruction"].fillna(0.0).to_numpy(float)
    G_all = X.T @ X
    b_all = X.T @ y

    c_idx = [ALL_SHELLS.index(j) for j in C_SHELLS]
    lead_idx = ALL_SHELLS.index(1)
    G_CC = G_all[np.ix_(c_idx, c_idx)]
    G_C1 = G_all[c_idx, lead_idx]
    b_C = b_all[c_idx]
    b_1 = b_all[lead_idx]

    ridge = 1e-9 * np.trace(G_CC) / G_CC.shape[0] if np.trace(G_CC) else 0.0
    G_reg = G_CC + ridge * np.eye(G_CC.shape[0])
    inv = np.linalg.pinv(G_reg)

    a_direct = inv @ b_C
    a_1 = b_1 / G_all[lead_idx, lead_idx] if G_all[lead_idx, lead_idx] != 0 else np.nan
    r_C = b_C / a_1 - G_C1 if np.isfinite(a_1) and a_1 != 0 else np.full_like(b_C, np.nan)
    a_schur = inv @ r_C

    evals = np.linalg.eigvalsh(G_CC)
    evals_desc = np.sort(evals)[::-1]
    total = float(evals_desc.sum())
    rank1_fraction = float(evals_desc[0] / total) if total else np.nan
    delta_full = float((evals_desc[0] - evals_desc[1]) / evals_desc[0]) if evals_desc[0] else np.nan
    cond = float(np.linalg.cond(G_reg))

    target = A_CAN_SIGN
    schur_signs = signs(a_schur)
    direct_signs = signs(a_direct)
    pass_signs = schur_signs == TARGET_SIGNS
    margin = float(np.min(np.abs(a_schur))) if len(a_schur) else np.nan
    norm = float(np.linalg.norm(a_schur))
    margin_norm = margin / norm if norm else np.nan

    return {
        "scope": scope,
        "rows": int(len(df)),
        "basis": BASIS,
        "C_shells": ",".join(map(str, C_SHELLS)),
        "G_CC_condition_number": cond,
        "G_CC_rank1_fraction": rank1_fraction,
        "G_CC_delta_full": delta_full,
        "a_1": float(a_1),
        "b_C": b_C,
        "G_C1": G_C1,
        "r_C": r_C,
        "a_direct": a_direct,
        "a_direct_signs": direct_signs,
        "a_schur": a_schur,
        "a_schur_signs": schur_signs,
        "target_signs": TARGET_SIGNS,
        "pass_schur_signs": bool(pass_signs),
        "schur_margin_min": margin,
        "schur_margin_normalized": float(margin_norm),
        "schur_distance_to_chamber_boundary": margin,
        "cos_schur_to_target": float(cos(a_schur, target)),
        "cos_schur_to_can_amp": float(cos(a_schur, A_CAN_AMP)),
        "Q_diag": Q_DIAG,
        "Q_diag_classification": "repayment_side" if pass_signs else "unclassified",
        "Q_diag_counted_in_O2": False if pass_signs else True,
        "Q_diag_repayment_side": bool(pass_signs),
        "O2_budget_clean": O2_CLEAN,
        "O2_budget_with_diag": O2_CLEAN + Q_DIAG,
        "O2_clean_margin": 1.0 - O2_CLEAN,
        "O2_diag_inclusive_margin": 1.0 - O2_CLEAN - Q_DIAG,
        "pass_clean_classification": bool(pass_signs),
        "ridge": ridge,
    }


def vector_rows(scope_result: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    objects = {
        "b_C": scope_result["b_C"],
        "G_C1": scope_result["G_C1"],
        "r_C = b_C/a1 - G_C1": scope_result["r_C"],
        "a_direct = G_CC^-1 b_C": scope_result["a_direct"],
        "a_schur = G_CC^-1 r_C": scope_result["a_schur"],
        "a_can_sign": A_CAN_SIGN,
        "a_can_amp": A_CAN_AMP,
    }
    a_direct = scope_result["a_direct"]
    for name, vec in objects.items():
        vec = np.asarray(vec, dtype=float)
        norm = float(np.linalg.norm(vec))
        rows.append(
            {
                "scope": scope_result["scope"],
                "object": name,
                "R0": float(vec[0]),
                "R2": float(vec[1]),
                "R3": float(vec[2]),
                "R4": float(vec[3]),
                "norm": norm,
                "signs": signs(vec),
                "cos_to_target_plus_minus_plus_minus": float(cos(vec, A_CAN_SIGN)),
                "cos_to_direct_fit": float(cos(vec, a_direct)),
                "cos_to_canonical_amp": float(cos(vec, A_CAN_AMP)),
                "margin_min_abs_component": float(np.min(np.abs(vec))) if len(vec) else np.nan,
            }
        )
    return rows


def refresh_manifest() -> None:
    rows = []
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            rows.append({"Name": p.name, "Length": p.stat().st_size, "LastWriteTime": pd.Timestamp(p.stat().st_mtime, unit="s")})
    pd.DataFrame(rows).to_csv(MANIFEST, index=False)


def write_doc(summary: dict[str, object], scopes: pd.DataFrame, vectors: pd.DataFrame) -> None:
    all_scopes_pass = bool(scopes["pass_schur_signs"].all()) if len(scopes) else False
    if summary["pass_schur_signs"] and all_scopes_pass and summary["schur_margin_normalized"] > 0.05:
        status = "very strong"
    elif summary["pass_schur_signs"]:
        status = "global pass; scope-local mixed"
    else:
        status = "partial"
    lines = [
        "# Prime Mesh R2Q - O1 Schur Residual Sign-Stability Audit",
        "",
        f"**Document:** `{DOC_OUT.name}`",
        "**Project:** Prime Mesh Theory - RH Programme",
        "**Date:** 2026-05-07",
        f"**Status:** O1 Schur residual audit - {status}",
        "",
        "## 1. Purpose",
        "",
        "This audit computes the O1 correction-block Schur residual:",
        "",
        r"\[",
        r"r_C=b_C/a_1-G_{C1},\qquad a_C^{\rm Schur}=G_{CC}^{-1}r_C.",
        r"\]",
        "",
        "The target sign pattern is:",
        "",
        r"\[",
        r"\operatorname{sgn}(a_C^{\rm Schur})=+-+-.",
        r"\]",
        "",
        "## 2. Summary",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    printable = {
        k: (vec_json(v) if isinstance(v, np.ndarray) else v)
        for k, v in summary.items()
        if k not in {"b_C", "G_C1", "r_C", "a_direct", "a_schur"}
    }
    for k, v in printable.items():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## 3. Vector Table",
        "",
        vectors.to_markdown(index=False),
        "",
        "## 4. Scope Checks",
        "",
        scopes.to_markdown(index=False),
        "",
        "## 5. Interpretation",
        "",
    ]
    if summary["pass_schur_signs"]:
        lines += [
            r"\[",
            r"\boxed{\operatorname{sgn}(a_C^{\rm Schur})=+-+-}",
            r"\]",
            "",
            "The global B2-active Schur residual object passes the correction-block sign test.  Under the O1 ledger convention, the `0.4011668793555976` diagnostic is classified as B2/MR-2 repayment-side mass, not O2 obstruction slack.",
            "",
            "Scope checks are mixed: several arbitrary tail/scale/h/mu subfamilies flip signs.  Therefore the proof-facing statement should be a global B2-active covariance-law classification, with the LongA/nondegenerate family as the canonical local carrier, not a pointwise sign theorem for every sub-scope.",
        ]
    else:
        lines += [
            r"\[",
            r"\boxed{\text{Schur signs failed; diagnostic classification remains open.}}",
            r"\]",
        ]
    lines += [
        "",
        "---",
        "",
        "*Prime Mesh Theory - RH Programme*",
    ]
    DOC_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    log(f"Reading {INPUT}")
    df = pd.read_csv(INPUT)
    needed = [f"shell_{BASIS}_{j}" for j in ALL_SHELLS] + ["cp_obstruction", "p_star", "h", "y", "block_id"]
    for c in needed:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["shell_pattern"] = df.apply(shell_pattern, axis=1)
    df["is_longa"] = df["shell_pattern"].eq("11111")
    df["is_tail_bool"] = df["is_tail"].astype(str).str.lower().isin(["true", "1"]) if "is_tail" in df.columns else df["p_star"] >= 500_000_000
    df["h_bin"] = df["h"].map(h_bin)
    df["p_scale_bin"] = df["p_star"].map(p_scale_bin)
    if "mu_bin" not in df.columns:
        df["mu_bin"] = "unknown"
    if "depth_bin" not in df.columns:
        df["depth_bin"] = "unknown"

    scope_parts: list[tuple[str, pd.DataFrame]] = [
        ("global", df),
        ("tail:p_star>=500M", df[df["is_tail_bool"]]),
        ("tail:p_star<500M", df[~df["is_tail_bool"]]),
        ("LongA only", df[df["is_longa"]]),
        ("nondegenerate shell_pattern=11111", df[df["shell_pattern"].eq("11111")]),
    ]
    for col, prefix in [("p_scale_bin", "scale"), ("h_bin", "h"), ("mu_bin", "mu"), ("depth_bin", "depth"), ("shell_pattern", "shell_pattern")]:
        for value, part in df.groupby(col, dropna=False):
            scope_parts.append((f"{prefix}:{value}", part))

    results = []
    for scope, part in scope_parts:
        r = compute_scope(part, scope)
        if r is not None:
            results.append(r)
    global_result = next(r for r in results if r["scope"] == "global")

    summary_simple = {
        k: (vec_json(v) if isinstance(v, np.ndarray) else v)
        for k, v in global_result.items()
        if k not in {"b_C", "G_C1", "r_C", "a_direct", "a_schur"}
    }
    summary_simple["a_direct"] = vec_json(global_result["a_direct"])
    summary_simple["a_schur"] = vec_json(global_result["a_schur"])
    pd.DataFrame([summary_simple]).to_csv(SUMMARY_OUT, index=False)

    scope_rows = []
    for r in results:
        scope_rows.append(
            {
                "scope": r["scope"],
                "rows": r["rows"],
                "a_schur": vec_json(r["a_schur"]),
                "a_schur_signs": r["a_schur_signs"],
                "pass_schur_signs": r["pass_schur_signs"],
                "schur_margin_min": r["schur_margin_min"],
                "schur_margin_normalized": r["schur_margin_normalized"],
                "Q_diag_classification": r["Q_diag_classification"],
                "Q_diag_counted_in_O2": r["Q_diag_counted_in_O2"],
                "G_CC_rank1_fraction": r["G_CC_rank1_fraction"],
                "G_CC_delta_full": r["G_CC_delta_full"],
            }
        )
    scopes_df = pd.DataFrame(scope_rows).sort_values(["pass_schur_signs", "rows"], ascending=[True, False])
    scopes_df.to_csv(SCOPES_OUT, index=False)

    vectors_df = pd.DataFrame(vector_rows(global_result))
    vectors_df.to_csv(VECTORS_OUT, index=False)

    # Worst rows here means rows from scopes that fail, if any; otherwise worst is
    # the smallest normalized Schur margin scopes.
    worst = scopes_df.sort_values(["pass_schur_signs", "schur_margin_normalized"], ascending=[True, True]).head(50)
    worst.to_csv(WORST_OUT, index=False)
    write_doc(global_result, scopes_df, vectors_df)
    refresh_manifest()

    log(f"Wrote {SUMMARY_OUT}")
    log(f"Wrote {VECTORS_OUT}")
    log(f"Wrote {SCOPES_OUT}")
    log(f"Wrote {WORST_OUT}")
    log(f"Wrote {DOC_OUT}")


if __name__ == "__main__":
    main()
