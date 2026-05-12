# Prime Mesh R2Q - RawR2Q Primitive Decomposition v3

**Document:** `Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_v3.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** proof-grade full primitive export

## 1. Executive Verdict

\[
\boxed{\text{RawR2Q primitive decomposition is globally proof-grade for the audited inventory.}}
\]

Route A succeeded: every coordinate-test row now has endpoint and bridge primitives.

## 2. Inputs and Route

- Route used: `Route A: SR11/O2 projection intervals plus SR11 realpath samples`.
- Projection input: `<repo-root>\notes\prime_mesh_r2q_o2_projection_orthogonality_audit_intervals.csv`.
- SR11 samples: `<repo-root>\notes\sr11_realpath_pstar\prime_mesh_r2q_sr11_realpath_noise_samples.csv`.

## 3. Primitive Coverage

| metric | value |
|---|---:|
| rows | 1468 |
| primitive_full_rows | 1468 |
| primitive_missing_rows | 0 |
| positive_missing_primitive_rows | 0 |
| threshold_relevant_missing_primitives | 0 |

## 4. Formula Decomposition

\[
Q_{\rm R2Q}(J)=Q_{\Delta D}(J)+Q_{\rm exc}(J)+\epsilon(J).
\]

| metric | value |
|---|---:|
| formula_rows | 1468 |
| max_abs_formula_residual | 0.02572845091728715 |
| mean_abs_formula_residual | 0.0030163628684094605 |
| formula_residual_cap | 0.03 |
| formula_residual_cap_violations | 0 |

## 5. NegativeTransfer Primitive Check

\[Q_{\Delta D}>3/4\Rightarrow E_\theta<0.\]

| metric | value |
|---|---:|
| antecedent_rows | 2 |
| violations | 0 |
| pass | True |

## 6. PositiveHarmlessness Primitive Check

\[E_\theta>0\Rightarrow Q_{\Delta D}\le1/4.\]

| metric | value |
|---|---:|
| positive_rows | 1320 |
| primitive_positive_available_rows | 1320 |
| positive_missing_primitive_rows | 0 |
| primitive_positive_violations | 0 |
| pass_global_positive_harmlessness | True |

## 7. Sign Inconsistency Classification

| metric | value |
|---|---:|
| checked_rows | 1468 |
| sign_consistent_rows | 148 |
| sign_inconsistent_rows | 1320 |
| sign_inconsistent_positive_harmless_rows | 1320 |
| sign_inconsistent_threshold_relevant_rows | 0 |
| sign_inconsistent_forbidden_rows | 0 |

The global biconditional `DeltaD < 0 iff E_theta < 0` is not asserted.  The proof-facing sign statement remains the threshold-relevant direction.

## 8. Status by Row Class

| row_status                           |   rows |
|:-------------------------------------|-------:|
| sign_inconsistent_positive_harmless  |   1320 |
| primitive_full_verified              |    146 |
| primitive_negative_transfer_verified |      2 |

## 9. Proof Interpretation

Route A closes the instrumentation gap for the audited inventory. The previous 1302 positive-short gap rows now carry endpoint and bridge primitives, and no primitive proof-grade checks fail.

Recommended next file: `Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_Closure_Update_v1.md`.

---

*Prime Mesh Theory - RH Programme*
