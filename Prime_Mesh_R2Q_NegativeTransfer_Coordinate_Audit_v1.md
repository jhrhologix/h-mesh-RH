# Prime Mesh R2Q - NegativeTransfer Coordinate Audit

**Document:** `Prime_Mesh_R2Q_NegativeTransfer_Coordinate_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** NegativeTransfer coordinate audit - passes

## 1. Executive Verdict

This audit tests the practical threshold form:

\[Q_{\rm R2Q}(J)>Q_0\Rightarrow E_\theta(J)<0,\qquad Q_0<1.\]

\[\boxed{\text{Threshold NegativeTransfer passes empirically.}}\]

## 2. Inputs Used

- `prime_mesh_r2q_partial_full_interval_compatibility_rows.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_windows.csv`
- `prime_mesh_r2q_theta_first_crossing_intervals.csv`
- `prime_mesh_r2q_o1_schur_residual_sign_stability_vectors.csv`

## 3. Summary

| metric | value |
|---|---:|
| `rows` | 1469 |
| `coordinate_test_rows` | 1468 |
| `finite_certificate_coordinate_excluded_rows` | 1 |
| `excluded_near_forbidden_rows` | 1 |
| `post_P0_rows` | 142 |
| `positive_rows` | 1320 |
| `negative_rows` | 148 |
| `zero_rows` | 0 |
| `unknown_sign_rows` | 1 |
| `positive_Qmax` | 0.2157084836048593 |
| `negative_Qmax` | 1.8193520399038576 |
| `zero_Qmax` | 0.0 |
| `unknown_Qmax` | 1.1611207216949435 |
| `positive_tail_Qmax` | 0.0585344103602869 |
| `negative_tail_Qmax` | 0.7568596623500748 |
| `positive_near_forbidden_count` | 0 |
| `negative_near_forbidden_count` | 3 |
| `zero_near_forbidden_count` | 0 |
| `unknown_near_forbidden_count` | 1 |
| `positive_forbidden_count` | 0 |
| `negative_forbidden_count` | 1 |
| `zero_forbidden_count` | 0 |
| `unknown_forbidden_count` | 1 |
| `Q_gt_0p75_count` | 3 |
| `Q_gt_0p75_negative_frac` | 1.0 |
| `Q_gt_1_count` | 1 |
| `Q_gt_1_negative_frac` | 1.0 |
| `lowest_clean_threshold` | 0.5 |
| `pass_NT_0p75` | True |
| `pass_NT_1p00` | True |
| `pass_threshold_negative_transfer` | True |
| `pass_negative_transfer_coordinate_empirical` | True |

## 4. Threshold Tests

| threshold | rows above | negative frac | positive frac | pass |
|---:|---:|---:|---:|---|
| 0.5 | 5 | 1.0 | 0.0 | True |
| 0.6 | 4 | 1.0 | 0.0 | True |
| 0.7 | 3 | 1.0 | 0.0 | True |
| 0.75 | 3 | 1.0 | 0.0 | True |
| 0.8 | 2 | 1.0 | 0.0 | True |
| 0.9 | 1 | 1.0 | 0.0 | True |
| 1.0 | 1 | 1.0 | 0.0 | True |

## 5. Positive Cap Result

- `positive_Qmax`: `0.2157084836048593`
- `positive_tail_Qmax`: `0.0585344103602869`
- `positive_near_forbidden_count`: `0`
- `positive_forbidden_count`: `0`

## 6. Failures

No failures found.

## 7. Recommended Theorem Form

The clean empirical threshold is `Q0 = 0.5`.

The threshold is computed on rows with an available local theta coordinate and valid local scale. Finite-certificate rows with no local theta coordinate are reported separately, not used as counterexamples to the post-`P0` coordinate theorem.

The proof-facing practical form may use:

\[Q_{\rm R2Q}(J)>0.75\Rightarrow E_\theta(J)<0.\]

Positive theta rows remain harmless below the near-forbidden threshold.

---

*Prime Mesh Theory - RH Programme*
