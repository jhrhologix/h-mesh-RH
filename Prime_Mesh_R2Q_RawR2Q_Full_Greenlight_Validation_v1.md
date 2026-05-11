# Prime Mesh R2Q - RawR2Q Full Greenlight Validation

**Document:** `Prime_Mesh_R2Q_RawR2Q_Full_Greenlight_Validation_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** operational greenlight passes; primitive proof-grade still partial

## 1. Executive Verdict

\[\boxed{\text{RawR2Q operational greenlight passes.}}\]

Every threshold-relevant/dangerous row has primitive coverage and passes the primitive checks. The rows still missing primitives are all positive-harmless and below the `1/4` cap.

However, this is **not** a full primitive proof-grade greenlight, because 1302 rows still lack exported `Q_delta_D/Q_exc` primitives.

## 2. Summary

| metric | value |
|---|---:|
| `rows` | 1468 |
| `primitive_full_rows` | 166 |
| `primitive_missing_rows` | 1302 |
| `positive_rows` | 1320 |
| `positive_missing_primitive_rows` | 1302 |
| `positive_missing_cap_pass_rows` | 1302 |
| `superthreshold_rows` | 3 |
| `superthreshold_missing_primitive_rows` | 0 |
| `forbidden_rows` | 1 |
| `forbidden_missing_primitive_rows` | 0 |
| `primitive_negative_transfer_antecedent_rows` | 2 |
| `primitive_negative_transfer_violations` | 0 |
| `primitive_positive_available_rows` | 18 |
| `primitive_positive_available_violations` | 0 |
| `formula_rows` | 166 |
| `max_abs_formula_residual` | 0.0257284509172871 |
| `formula_residual_cap` | 0.03 |
| `formula_residual_cap_violations` | 0 |
| `operational_greenlight_failures` | 0 |
| `pass_rawr2q_operational_greenlight` | True |
| `pass_rawr2q_primitive_proof_grade` | False |
| `proof_grade_blocker` | 1302 positive-harmless rows still lack primitive endpoint/bridge export |
| `recommended_theorem_form` | threshold_relevant_rows_primitive_verified_positive_missing_rows_cap_harmless |
| `recommended_next_file` | Prime_Mesh_R2Q_RawR2Q_PositiveShort_PrimitiveExemption_Or_Export_Target_v1.md |

## 3. Class Breakdown

| greenlight_class                           |   rows |
|:-------------------------------------------|-------:|
| primitive_full_verified                    |    146 |
| primitive_negative_transfer_verified       |      2 |
| primitive_positive_cap_verified            |     18 |
| structural_positive_cap_missing_primitives |   1302 |

## 4. Interpretation

Operationally, RawR2Q is green for the proof stack because no missing-primitive row is threshold-relevant:

\[
Q_{\rm R2Q}>3/4 \Rightarrow \text{primitive data available and NegativeTransfer passes.}
\]

But proof-grade RawR2Q still requires either full primitive export for the positive-harmless rows or a formal theorem that positive-harmless short rows do not require the endpoint primitive channel.

## 5. Recommended Next File

`Prime_Mesh_R2Q_RawR2Q_PositiveShort_PrimitiveExemption_Or_Export_Target_v1.md`

---

*Prime Mesh Theory - RH Programme*