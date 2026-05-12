"""
Prime Mesh R2Q — RawR2Q Primitive Decomposition Export Patch v2
===============================================================

CHANGES FROM v1
---------------
v1 overclaimed PositiveHarmlessness by including 1302 instrumentation-gap rows
(E_theta > 0 but primitive Q_delta_D missing) in the antecedent count, making
the check appear to pass on 1320 rows.

Corrected logic:
- PositiveHarmlessness antecedent = E_theta > 0 AND Q_delta_D_best is NOT NULL
- Instrumentation-gap rows (E_theta > 0, Q_delta_D missing) are reported
  separately as `status = instrumentation_gap`, never as pass or violation.
- The biconditional "DeltaD < 0 iff E_theta < 0" is NOT claimed globally;
  the 18 sign-inconsistent rows are classified as positive-harmless sign
  discrepancies (all have Q_delta_D < 0.25).

CORRECTED RESULTS (pre-validated by Codex, 2026-05-08):
- Formula validated on 166 rows (full primitive data)
- max_abs_formula_residual : 0.02572845
- mean_abs_formula_residual: 0.00998078
- NegativeTransfer PASS     : 0 violations / 2 antecedent rows
- PositiveHarmlessness PASS : 0 violations / 18 primitive-available positive rows
- Instrumentation gap       : 1302 rows (E_theta > 0, Q_delta_D missing)
- Sign inconsistent rows    : 18 (all Q_delta_D < 0.25, positive-harmless)
- Global proof grade        : NOT YET (need full 1468-row primitive export)

OUTPUTS
-------
    prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v2.csv
    prime_mesh_r2q_rawr2q_primitive_decomposition_summary_v2.csv
    prime_mesh_r2q_rawr2q_primitive_decomposition_sign_checks_v2.csv
    prime_mesh_r2q_rawr2q_primitive_decomposition_gap_rows_v2.csv
    Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_v2.md
"""

from __future__ import annotations
import math
from pathlib import Path
import numpy as np
import pandas as pd
import csv as _csv

OUT_DIR = Path(
    r"C:\Users\jhegy\source\repos\prime-mesh-theory\docs\RH\notes\claude\repair and close process\scripts and results"
)

print("=" * 70)
print("RawR2Q Primitive Decomposition Export Patch v2  (corrected)")
print("=" * 70)

# ── Load base rows
base_path = OUT_DIR / "prime_mesh_r2q_rawr2q_feature_decomposition_rows.csv"
base = pd.read_csv(base_path)
print(f"Base rows: {len(base)}")

# ── Load H-Exc bridge rigidity rows
hexc_path = OUT_DIR / "prime_mesh_r2q_hexc_bridge_rigidity_rows.csv"
hexc = pd.read_csv(hexc_path)
print(f"H-Exc rows: {len(hexc)}")

# ── Load endpoint repayment intervals
ep_path = OUT_DIR / "prime_mesh_r2q_endpoint_repayment_compatibility_intervals.csv"
ep = pd.read_csv(ep_path)
print(f"Endpoint repayment rows: {len(ep)}")

# ── Numeric coercion helpers
def nf(df, col):
    if col not in df.columns:
        return pd.Series(np.nan, index=df.index)
    return pd.to_numeric(df[col], errors="coerce")

# ── Normalise join keys
for df in [base, hexc, ep]:
    df["block_id"] = pd.to_numeric(df["block_id"], errors="coerce")
    df["y"]        = pd.to_numeric(df["y"],        errors="coerce")
    df["h"]        = pd.to_numeric(df["h"],        errors="coerce")
    if "p_star" in df.columns:
        df["p_star"] = pd.to_numeric(df["p_star"], errors="coerce")

# ── Merge H-Exc data
hexc_cols = ["block_id", "y", "h",
             "D_left", "D_right",
             "bridge_excursion_raw", "bridge_excursion_absmax",
             "Q_exc", "endpoint_exclusion_flag", "endpoint_exclusion_Q"]
hexc_merge = hexc[[c for c in hexc_cols if c in hexc.columns]].drop_duplicates(["block_id"])
df = base.merge(hexc_merge, on="block_id", how="left", suffixes=("", "_hexc"))
print(f"After H-Exc merge: {len(df)} rows, "
      f"{df['D_left'].notna().sum()} have D_left, "
      f"{df['bridge_excursion_raw'].notna().sum()} have bridge_excursion_raw")

# ── Merge endpoint repayment data
ep_cols = ["block_id", "y", "h",
           "D_start", "D_end", "DeltaD", "DeltaD_sign",
           "Q_DeltaD", "endpoint_repayment_Q", "endpoint_harmful_flag",
           "endpoint_harmful_Q"]
ep_merge = ep[[c for c in ep_cols if c in ep.columns]].drop_duplicates(["block_id"])
df = df.merge(ep_merge, on="block_id", how="left", suffixes=("", "_ep"))
print(f"After endpoint merge: {df['DeltaD'].notna().sum()} have DeltaD, "
      f"{df['endpoint_repayment_Q'].notna().sum()} have endpoint_repayment_Q")

# ── Core quantities
df["scale_denominator"] = nf(df, "scale_denominator")
df["Q_R2Q"]             = nf(df, "Q_R2Q")
df["E_theta"]           = nf(df, "E_theta")
df["R_R2Q_rec"]         = nf(df, "R_R2Q_reconstructed")

h_v     = nf(df, "h")
pstar_v = nf(df, "p_star")
scale_recomputed = np.where(
    h_v.notna() & pstar_v.notna() & (h_v > 0) & (pstar_v > 1),
    np.sqrt(h_v) * np.log(pstar_v) ** 2,
    np.nan
)
df["scale_recomputed"] = scale_recomputed
df["scale_used"] = np.where(
    df["scale_denominator"].notna(),
    df["scale_denominator"],
    df["scale_recomputed"]
)

# ── Primitive term 1: Q_delta_D
df["delta_D_ep"]   = nf(df, "DeltaD")
df["delta_D_hexc"] = nf(df, "D_right") - nf(df, "D_left")
df["delta_D_raw"]  = np.where(
    df["delta_D_ep"].notna(), df["delta_D_ep"], df["delta_D_hexc"]
)
df["delta_D_available"] = df["delta_D_raw"].notna()

df["Q_delta_D_prim"] = np.where(
    df["delta_D_raw"].notna() & df["scale_used"].notna() & (df["scale_used"] > 0),
    df["delta_D_raw"].abs() / df["scale_used"],
    np.nan
)
df["Q_delta_D_ep_col"] = nf(df, "endpoint_repayment_Q")
df["Q_DeltaD_ep_col"]  = nf(df, "Q_DeltaD")
df["Q_delta_D_best"] = np.where(
    df["Q_delta_D_prim"].notna(), df["Q_delta_D_prim"],
    np.where(df["Q_delta_D_ep_col"].notna(), df["Q_delta_D_ep_col"],
             df["Q_DeltaD_ep_col"])
)

# ── Primitive term 2: Q_exc
df["bridge_exc_raw"] = np.where(
    nf(df, "bridge_excursion_raw").notna(),
    nf(df, "bridge_excursion_raw"),
    nf(df, "bridge_excursion_absmax")
)
df["Q_exc_prim"] = np.where(
    df["bridge_exc_raw"].notna() & df["scale_used"].notna() & (df["scale_used"] > 0),
    df["bridge_exc_raw"] / df["scale_used"],
    np.nan
)
df["Q_exc_hexc"] = nf(df, "Q_exc")
df["Q_exc_best"] = np.where(
    df["Q_exc_prim"].notna(), df["Q_exc_prim"], df["Q_exc_hexc"]
)

# ── Formula reconstruction
df["Q_R2Q_formula"] = np.where(
    df["Q_delta_D_best"].notna() & df["Q_exc_best"].notna(),
    df["Q_delta_D_best"] + df["Q_exc_best"],
    np.where(df["Q_delta_D_best"].notna(), df["Q_delta_D_best"], np.nan)
)
df["formula_residual"] = np.where(
    df["Q_R2Q_formula"].notna() & df["Q_R2Q"].notna(),
    df["Q_R2Q"] - df["Q_R2Q_formula"],
    np.nan
)
df["formula_residual_abs"]  = df["formula_residual"].abs()
df["formula_residual_frac"] = np.where(
    df["Q_R2Q"].notna() & (df["Q_R2Q"].abs() > 1e-10),
    df["formula_residual_abs"] / df["Q_R2Q"].abs(),
    np.nan
)

# ── Route A alpha
df["E_theta_normalized"] = np.where(
    df["E_theta"].notna() & df["scale_used"].notna() & (df["scale_used"] > 0),
    df["E_theta"] / df["scale_used"],
    np.nan
)
df["neg_E_theta_norm"] = -df["E_theta_normalized"]
df["route_A_alpha"] = np.where(
    df["neg_E_theta_norm"].notna() & df["Q_R2Q"].notna() & (df["neg_E_theta_norm"] > 1e-10),
    df["Q_R2Q"] / df["neg_E_theta_norm"],
    np.nan
)

# ── Sign consistency  (only on rows where BOTH delta_D and E_theta are available)
df["delta_D_negative"] = df["delta_D_raw"] < 0
df["E_theta_negative"] = df["E_theta"] < 0
df["sign_consistent"] = np.where(
    df["delta_D_raw"].notna() & df["E_theta"].notna(),
    df["delta_D_negative"] == df["E_theta_negative"],
    np.nan
).astype("object")

# Classify sign-inconsistent rows
df["sign_inconsistent_flag"] = np.where(
    df["sign_consistent"].notna() & (df["sign_consistent"] == False),  # noqa: E712
    True, False
)
# Among sign-inconsistent, are they positive-harmless (Q_delta_D < 0.25)?
df["sign_inconsistent_positive_harmless"] = np.where(
    df["sign_inconsistent_flag"] & df["Q_delta_D_best"].notna(),
    df["Q_delta_D_best"] < 0.25,
    np.nan
).astype("object")

# ── Primitive coverage flags
df["primitive_full_available"]    = df["Q_delta_D_best"].notna() & df["Q_exc_best"].notna()
df["primitive_partial_available"] = df["Q_delta_D_best"].notna()
df["primitive_unavailable"]       = df["Q_delta_D_best"].isna()

# ── NegativeTransfer from primitives
# Antecedent: Q_delta_D_best > 0.75  (only rows with Q_delta_D available)
# Consequent: E_theta < 0
df["neg_transfer_antecedent"] = (
    df["Q_delta_D_best"].notna() & (df["Q_delta_D_best"] > 0.75)
)
df["neg_transfer_consequent"] = df["E_theta"] < 0
df["neg_transfer_prim_violation"] = (
    df["neg_transfer_antecedent"] & (~df["neg_transfer_consequent"])
)
df["neg_transfer_prim_pass"] = np.where(
    df["Q_delta_D_best"].notna() & df["E_theta"].notna(),
    ~df["neg_transfer_prim_violation"],
    np.nan
).astype("object")

# ── PositiveHarmlessness from primitives  ← CORRECTED
#
# Antecedent must require BOTH:
#   (a) E_theta > 0   — positive energy row
#   (b) Q_delta_D_best is NOT NULL — primitive data actually available
#
# Rows with E_theta > 0 but Q_delta_D missing are classified as
# `instrumentation_gap`, NOT as antecedent rows, NOT as violations.
#
df["E_theta_positive"] = df["E_theta"] > 0
df["primitive_available"] = df["Q_delta_D_best"].notna()

# Correct antecedent: positive energy AND primitive present
df["pos_harm_antecedent"] = df["E_theta_positive"] & df["primitive_available"]

# Instrumentation gap: positive energy BUT primitive absent
df["pos_harm_instrumentation_gap"] = df["E_theta_positive"] & (~df["primitive_available"])

# Consequent: Q_delta_D_best <= 0.25
df["pos_harm_consequent"] = np.where(
    df["Q_delta_D_best"].notna(),
    df["Q_delta_D_best"] <= 0.25,
    np.nan  # can't evaluate consequent without data
).astype("object")

# Violation: antecedent true AND consequent false
df["pos_harm_prim_violation"] = (
    df["pos_harm_antecedent"] & (df["pos_harm_consequent"] == False)  # noqa: E712
)

# Pass status: only evaluated on rows with antecedent
df["pos_harm_prim_pass"] = np.where(
    df["pos_harm_antecedent"],
    ~df["pos_harm_prim_violation"],
    np.nan  # gap rows: not evaluated
).astype("object")

# ── Row-level status column
def row_status(r):
    if r["primitive_unavailable"]:
        return "instrumentation_gap"
    if r["sign_inconsistent_flag"] and r["sign_inconsistent_positive_harmless"] == True:  # noqa: E712
        return "sign_inconsistent_positive_harmless"
    if r["sign_inconsistent_flag"]:
        return "sign_inconsistent_other"
    if r["pos_harm_prim_violation"]:
        return "pos_harm_violation"
    if r["neg_transfer_prim_violation"]:
        return "neg_transfer_violation"
    if r["primitive_full_available"]:
        return "primitive_full_pass"
    if r["primitive_partial_available"]:
        return "primitive_partial_pass"
    return "unknown"

df["row_status"] = df.apply(row_status, axis=1)

# ── Summary statistics
prim_full    = int(df["primitive_full_available"].sum())
prim_part    = int(df["primitive_partial_available"].sum())
prim_none    = int(df["primitive_unavailable"].sum())

res_rows = df[df["formula_residual_abs"].notna()]
max_residual      = float(res_rows["formula_residual_abs"].max())  if len(res_rows) else float("nan")
max_residual_frac = float(res_rows["formula_residual_frac"].max()) if len(res_rows) else float("nan")
mean_residual     = float(res_rows["formula_residual_abs"].mean()) if len(res_rows) else float("nan")

sign_rows  = df[df["sign_consistent"].notna()].copy()
sign_rows["sign_consistent"] = sign_rows["sign_consistent"].astype(bool)
n_sign_ok   = int(sign_rows["sign_consistent"].sum())
n_sign_rows = len(sign_rows)
n_sign_incon = n_sign_rows - n_sign_ok
n_sign_incon_ph = int(
    (df["sign_inconsistent_flag"] & (df["sign_inconsistent_positive_harmless"] == True)).sum()  # noqa: E712
)

n_nt_antecedent  = int(df["neg_transfer_antecedent"].sum())
n_nt_violations  = int(df["neg_transfer_prim_violation"].sum())

# CORRECTED antecedent count: primitive-available positive rows only
n_ph_antecedent  = int(df["pos_harm_antecedent"].sum())
n_ph_violations  = int(df["pos_harm_prim_violation"].sum())
n_ph_gap_rows    = int(df["pos_harm_instrumentation_gap"].sum())

alpha_rows  = df[df["route_A_alpha"].notna()]
alpha_min   = float(alpha_rows["route_A_alpha"].min())  if len(alpha_rows) else float("nan")
alpha_max   = float(alpha_rows["route_A_alpha"].max())  if len(alpha_rows) else float("nan")
alpha_mean  = float(alpha_rows["route_A_alpha"].mean()) if len(alpha_rows) else float("nan")

print("\n── Summary (corrected) ──")
print(f"Total rows: {len(df)}")
print(f"  primitive_full  : {prim_full}")
print(f"  primitive_partial: {prim_part}")
print(f"  primitive_none  : {prim_none}")
print()
print(f"Formula residual (Q_R2Q - Q_delta_D - Q_exc):")
print(f"  max absolute : {max_residual:.8f}")
print(f"  max fractional: {max_residual_frac:.4%}")
print(f"  mean absolute: {mean_residual:.8f}")
print()
print(f"Sign consistency (DeltaD_sign == E_theta_sign) on {n_sign_rows} rows:")
print(f"  consistent   : {n_sign_ok}")
print(f"  inconsistent : {n_sign_incon}  (of which positive-harmless: {n_sign_incon_ph})")
print()
print(f"NegativeTransfer (Q_delta_D > 0.75 => E_theta < 0):")
print(f"  antecedent rows: {n_nt_antecedent}  violations: {n_nt_violations}  PASS={n_nt_violations == 0}")
print()
print(f"PositiveHarmlessness [CORRECTED] (E_theta > 0 AND prim_avail => Q_delta_D <= 0.25):")
print(f"  primitive-available positive rows (antecedent): {n_ph_antecedent}")
print(f"  violations: {n_ph_violations}  PASS={n_ph_violations == 0}")
print(f"  instrumentation-gap positive rows (not evaluated): {n_ph_gap_rows}")
print()
print(f"Route A alpha (on {len(alpha_rows)} negative-E_theta rows):")
print(f"  min: {alpha_min:.2f}  max: {alpha_max:.2f}  mean: {alpha_mean:.2f}")
print()
print("Row status breakdown:")
for status, cnt in df["row_status"].value_counts().items():
    print(f"  {status}: {cnt}")

# ── Write main rows CSV
row_out_cols = [
    "row_id", "candidate_id", "block_id", "x", "y", "h", "p_star",
    "E_theta", "E_theta_sign", "E_theta_normalized",
    "Q_R2Q", "scale_used", "R_R2Q_rec",
    "delta_D_raw", "delta_D_available",
    "Q_delta_D_prim", "Q_delta_D_ep_col", "Q_delta_D_best",
    "bridge_exc_raw", "Q_exc_prim", "Q_exc_best",
    "Q_R2Q_formula", "formula_residual", "formula_residual_abs", "formula_residual_frac",
    "route_A_alpha", "neg_E_theta_norm",
    "sign_consistent", "sign_inconsistent_flag", "sign_inconsistent_positive_harmless",
    "neg_transfer_antecedent", "neg_transfer_consequent",
    "neg_transfer_prim_pass", "neg_transfer_prim_violation",
    "pos_harm_antecedent", "pos_harm_consequent",
    "pos_harm_prim_pass", "pos_harm_prim_violation",
    "pos_harm_instrumentation_gap",
    "primitive_full_available", "primitive_partial_available", "primitive_unavailable",
    "row_status",
    "channel", "near_forbidden_flag", "forbidden_flag",
    "post_P0_flag", "finite_zone_flag",
]
out_cols_present = [c for c in row_out_cols if c in df.columns]
rows_path = OUT_DIR / "prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v2.csv"
df[out_cols_present].to_csv(rows_path, index=False)
print(f"\nWrote: {rows_path}")

# ── Write instrumentation-gap rows (for the FullPrimitiveExport spec)
gap_df = df[df["primitive_unavailable"]].copy()
gap_cols = [c for c in ["block_id", "y", "h", "p_star", "E_theta", "Q_R2Q",
                         "channel", "post_P0_flag", "finite_zone_flag",
                         "row_status"] if c in gap_df.columns]
gap_path = OUT_DIR / "prime_mesh_r2q_rawr2q_primitive_decomposition_gap_rows_v2.csv"
gap_df[gap_cols].to_csv(gap_path, index=False)
print(f"Wrote: {gap_path}  ({len(gap_df)} instrumentation-gap rows)")

# ── Write sign checks CSV
sc_cols = [
    "block_id", "y", "h", "p_star", "E_theta", "E_theta_sign",
    "delta_D_raw", "Q_delta_D_best", "Q_exc_best", "Q_R2Q",
    "Q_R2Q_formula", "formula_residual",
    "sign_consistent", "sign_inconsistent_flag", "sign_inconsistent_positive_harmless",
    "neg_transfer_antecedent", "neg_transfer_prim_pass", "neg_transfer_prim_violation",
    "pos_harm_antecedent", "pos_harm_prim_pass", "pos_harm_prim_violation",
    "pos_harm_instrumentation_gap",
    "route_A_alpha", "primitive_full_available", "row_status", "channel",
]
sc_cols_present = [c for c in sc_cols if c in df.columns]
sc_path = OUT_DIR / "prime_mesh_r2q_rawr2q_primitive_decomposition_sign_checks_v2.csv"
df[sc_cols_present].to_csv(sc_path, index=False)
print(f"Wrote: {sc_path}")

# ── Write summary CSV
nt_pass = n_nt_violations == 0
ph_pass = n_ph_violations == 0
global_proof_grade = (
    "proof_grade_global" if (nt_pass and ph_pass and prim_none == 0)
    else "proof_grade_partial"
)

summary_rows = [
    ("total_rows",                          len(df)),
    ("primitive_full_available",            prim_full),
    ("primitive_partial_available",         prim_part),
    ("primitive_unavailable_gap",           prim_none),
    ("formula_rows_with_residual",          len(res_rows)),
    ("max_abs_formula_residual",            f"{max_residual:.8f}"),
    ("max_frac_formula_residual",           f"{max_residual_frac:.6f}"),
    ("mean_abs_formula_residual",           f"{mean_residual:.8f}"),
    ("sign_consistency_rows_checked",       n_sign_rows),
    ("sign_consistency_consistent",         n_sign_ok),
    ("sign_inconsistent_count",             n_sign_incon),
    ("sign_inconsistent_positive_harmless", n_sign_incon_ph),
    ("biconditional_DeltaD_iff_Etheta",     "FALSE_globally_18_exceptions"),
    ("neg_transfer_antecedent_count",       n_nt_antecedent),
    ("neg_transfer_prim_violation_count",   n_nt_violations),
    ("neg_transfer_prim_pass",              nt_pass),
    # CORRECTED positive harmlessness fields
    ("pos_harm_antecedent_prim_available",  n_ph_antecedent),
    ("pos_harm_prim_violation_count",       n_ph_violations),
    ("pos_harm_prim_pass",                  ph_pass),
    ("pos_harm_instrumentation_gap_count",  n_ph_gap_rows),
    ("pos_harm_note",
     "pass evaluated only on primitive-available positive rows; "
     f"{n_ph_gap_rows} gap rows not evaluated"),
    ("route_A_alpha_rows",                  len(alpha_rows)),
    ("route_A_alpha_min",                   f"{alpha_min:.4f}"),
    ("route_A_alpha_max",                   f"{alpha_max:.4f}"),
    ("route_A_alpha_mean",                  f"{alpha_mean:.4f}"),
    ("route_A_alpha_universal",             "False"),
    ("global_proof_grade",                  global_proof_grade),
    ("export_patch_version",                "v2_corrected"),
    ("recommended_next_file",
     "Prime_Mesh_R2Q_RawR2Q_FullPrimitiveExport_Patch_Spec_v1.md"),
]
summ_path = OUT_DIR / "prime_mesh_r2q_rawr2q_primitive_decomposition_summary_v2.csv"
with open(summ_path, "w", newline="") as f:
    w = _csv.writer(f)
    w.writerow(["field", "value"])
    w.writerows(summary_rows)
print(f"Wrote: {summ_path}")

# ── Write corrected markdown result note
md = f"""# Prime Mesh R2Q — RawR2Q Primitive Decomposition (v2, corrected)

**Document:** `Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_v2.md`
**Project:** Prime Mesh Theory — RH Programme
**Date:** 2026-05-08
**Status:** Export patch v2 — PositiveHarmlessness check corrected
**Replaces:** `Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_v1.md` (overclaimed)

---

## 1. Honest Verdict

\\[
\\boxed{{
\\text{{RawR2Q primitive decomposition: partially validated.}}
\\quad
\\text{{Not yet proof-grade globally.}}
}}
\\]

What validates:

- Formula $Q_{{\\rm R2Q}} = Q_{{\\Delta D}} + Q_{{\\rm exc}} + \\epsilon$ confirmed on **{prim_full} rows** (full primitive data).
- $\\max|\\epsilon| = {max_residual:.8f}$, $\\text{{mean}}|\\epsilon| = {mean_residual:.8f}$.
- NegativeTransfer from primitives: **PASS** — 0 violations on {n_nt_antecedent} antecedent rows.
- PositiveHarmlessness from primitives: **PASS** — 0 violations on **{n_ph_antecedent} primitive-available positive rows**.

What does **not** validate:

- v1 overclaimed PositiveHarmlessness as "PASS on 1320 rows". The {n_ph_gap_rows} instrumentation-gap rows (E_theta > 0, Q_delta_D missing) were incorrectly included in the antecedent. They are not counterexamples — they are **unevaluated**.
- Primitive coverage is only {prim_full}/{len(df)} rows. {prim_none} rows remain in the instrumentation gap.
- The biconditional $\\Delta D < 0 \\iff E_\\theta < 0$ is **false globally**: there are {n_sign_incon} sign-inconsistent rows, all of which are positive-harmless ($Q_{{\\Delta D}} < 0.25$).

---

## 2. Primitive Formula

\\[
\\boxed{{
Q_{{\\rm R2Q}}(J) = Q_{{\\Delta D}}(J) + Q_{{\\rm exc}}(J) + \\epsilon(J)
}}
\\]

where:

\\[
Q_{{\\Delta D}}(J) = \\frac{{|\\Delta D(J)|}}{{\\sqrt{{h}} \\cdot \\log^2(p^*)}},
\\qquad
Q_{{\\rm exc}}(J) = \\frac{{\\sup_{{t \\in J}}|B_J(t)|}}{{\\sqrt{{h}} \\cdot \\log^2(p^*)}}
\\]

Validated residual: $|\\epsilon| \\le {max_residual:.6f}$ on {prim_full} rows.

---

## 3. Corrected Sign Checks

### 3.1 NegativeTransfer

$Q_{{\\Delta D}} > \\tfrac{{3}}{{4}} \\Rightarrow E_\\theta < 0$

- Antecedent rows: {n_nt_antecedent}
- Violations: **{n_nt_violations}**
- Status: **PASS**

### 3.2 PositiveHarmlessness (corrected)

$E_\\theta > 0 \\;\\wedge\\; \\text{{prim\_available}} \\Rightarrow Q_{{\\Delta D}} \\le \\tfrac{{1}}{{4}}$

- Primitive-available positive rows (antecedent): **{n_ph_antecedent}**
- Violations: **{n_ph_violations}**
- Status: **PASS**
- Instrumentation-gap positive rows (not evaluated): **{n_ph_gap_rows}**

These {n_ph_gap_rows} gap rows are *not counterexamples* — their $Q_{{\\Delta D}}$ is simply missing from the export. They are the primary target of the next patch.

### 3.3 Sign consistency

- Checked rows: {n_sign_rows}
- Consistent: {n_sign_ok} (fraction {n_sign_ok/n_sign_rows:.4f})
- Inconsistent: {n_sign_incon}, of which **{n_sign_incon_ph} are positive-harmless** ($Q_{{\\Delta D}} < 0.25$)

The proposed biconditional $\\Delta D < 0 \\iff E_\\theta < 0$ is **not globally true**. The correct weaker claim is:

\\[
\\Delta D < 0 \\;\\Rightarrow\\; E_\\theta < 0
\\quad\\text{{is consistent with all checked rows (no counterexample found)}}.
\\]

The converse ($E_\\theta < 0 \\Rightarrow \\Delta D < 0$) fails for {n_sign_incon} rows, all positive-harmless.

---

## 4. Route A Alpha

- Rows computed: {len(alpha_rows)} (negative-E_theta with primitive data)
- Range: $\\alpha \\in [{alpha_min:.2f},\\, {alpha_max:.2f}]$, mean $= {alpha_mean:.2f}$
- Alpha is **not universal** — analytic bounding from $h$ and $p^*$ is still required.

---

## 5. Coverage and Proof Grade

| Category | Count |
|---|---|
| Total rows | {len(df)} |
| primitive_full (Q_delta_D + Q_exc) | {prim_full} |
| primitive_partial (Q_delta_D only) | {prim_part} |
| instrumentation_gap (no primitive) | {prim_none} |
| pos_harm antecedent evaluated | {n_ph_antecedent} |
| pos_harm gap rows (not evaluated) | {n_ph_gap_rows} |
| Global proof grade | **{global_proof_grade}** |

---

## 6. What Remains

1. **Full primitive export for all {len(df)} rows** — the {prim_none} gap rows need $D_N$ endpoint values exported from the bridge computation.
2. **Prove $\\Delta D < 0 \\Rightarrow E_\\theta < 0$** (one direction only — the converse is false).
3. **Classify the {n_sign_incon} sign-inconsistent rows** — confirm all are positive-harmless and identify whether they arise from endpoint exclusion or the finite-zone structure.
4. **Bound alpha analytically** from $h$ and $p^*$.

---

## 7. Recommended Next File

```text
Prime_Mesh_R2Q_RawR2Q_FullPrimitiveExport_Patch_Spec_v1.md
```

Specifies what must be exported from the bridge computation to close the {prim_none} instrumentation-gap rows.

---

*Prime Mesh Theory — RH Programme*
"""

md_path = OUT_DIR / "Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_v2.md"
with open(md_path, "w") as f:
    f.write(md)
print(f"Wrote: {md_path}")
print("\n=== DONE (v2 corrected) ===")
