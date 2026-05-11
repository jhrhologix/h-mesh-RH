# Prime Mesh R2Q - PositiveHarmlessness Decomposition Audit

**Document:** `Prime_Mesh_R2Q_PositiveHarmlessness_Decomposition_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** PositiveHarmlessness decomposition audit - passes

## 1. Executive Verdict

This audit decomposes positive-theta rows and tests caps for:

\[E_\theta(J)>0\Rightarrow Q_{\rm R2Q}(J)\le C_+<1.\]

\[\boxed{\text{Strong positive cap passes: }C_+=1/4.}\]

## 2. Inputs Used

- `prime_mesh_r2q_negative_transfer_coordinate_rows.csv`
- `prime_mesh_r2q_negative_transfer_coordinate_summary.csv`
- `prime_mesh_r2q_negative_transfer_coordinate_by_sign.csv`
- `prime_mesh_r2q_negative_transfer_coordinate_thresholds.csv`
- `prime_mesh_r2q_partial_full_interval_compatibility_rows.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv`
- `prime_mesh_r2q_blocksystem_definition_geometry.csv`
- `prime_mesh_r2q_blocksystem_definition_blocks.csv`
- `prime_mesh_r2q_o1_schur_residual_sign_stability_vectors.csv`
- `prime_mesh_r2q_o1_schur_residual_sign_stability_scopes.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_windows.csv`

Join notes:
- primary rows used directly
- prime_mesh_r2q_firstcrossing_covering_localization_windows.csv on ['block_id', 'p_star', 'y', 'h']: 1469->1469

## 3. Summary

| metric | value |
|---|---:|
| `rows` | 1469 |
| `coordinate_test_rows` | 1468 |
| `positive_rows` | 1320 |
| `negative_rows` | 148 |
| `zero_rows` | 0 |
| `unknown_sign_rows` | 0 |
| `post_P0_rows` | 142 |
| `tail_rows` | 142 |
| `finite_certificate_rows` | 1326 |
| `positive_Qmin` | 0.0489909092562281 |
| `positive_Qmax` | 0.2157084836048593 |
| `positive_Qmean` | 0.05974208202963205 |
| `positive_Qmedian` | 0.057717756889844846 |
| `positive_Qq95` | 0.07588258117850578 |
| `positive_Qq99` | 0.10698189098852476 |
| `positive_tail_rows` | 120 |
| `positive_tail_Qmin` | 0.0489909092562281 |
| `positive_tail_Qmax` | 0.0585344103602869 |
| `positive_tail_Qmean` | 0.04998167621469551 |
| `positive_tail_Qmedian` | 0.049916660467031054 |
| `positive_tail_Qq95` | 0.05045060587909455 |
| `positive_tail_Qq99` | 0.056234009578331016 |
| `post_P0_positive_rows` | 120 |
| `post_P0_positive_Qmax` | 0.0585344103602869 |
| `non_tail_positive_rows` | 1200 |
| `non_tail_positive_Qmax` | 0.2157084836048593 |
| `finite_positive_rows` | 1200 |
| `finite_positive_Qmax` | 0.2157084836048593 |
| `positive_near_forbidden_count` | 0 |
| `positive_forbidden_count` | 0 |
| `positive_above_0p25_count` | 0 |
| `positive_above_0p50_count` | 0 |
| `positive_above_0p75_count` | 0 |
| `positive_above_1p00_count` | 0 |
| `lowest_global_positive_cap_passed` | 0.25 |
| `lowest_tail_positive_cap_passed` | 0.25 |
| `pass_positive_cap_0p25` | True |
| `pass_positive_cap_0p50` | True |
| `pass_positive_cap_0p75` | True |
| `pass_positive_cap_1p00` | True |
| `pass_positive_harmlessness_empirical` | True |
| `recommended_theorem_form` | global_strong_cap_Cplus_1_over_4 |
| `recommended_next_file` | Prime_Mesh_R2Q_PositiveHarmlessness_Theorem_Target_v1.md |

## 4. Cap Tests

| cap | positive rows | above cap | tail above cap | post-P0 above cap | global pass | tail pass | post-P0 pass |
|---:|---:|---:|---:|---:|---|---|---|
| 0.25 | 1320 | 0 | 0 | 0 | True | True | True |
| 0.5 | 1320 | 0 | 0 | 0 | True | True | True |
| 0.75 | 1320 | 0 | 0 | 0 | True | True | True |
| 1.0 | 1320 | 0 | 0 | 0 | True | True | True |

## 5. Extreme Positive Rows

- `positive_Qmax`: `0.2157084836048593`
- `positive_tail_Qmax`: `0.0585344103602869`
- `post_P0_positive_Qmax`: `0.0585344103602869`
- `positive rows with Q>0.25`: `0`

## 6. Regime Decomposition

`29` regime rows were written to `prime_mesh_r2q_positive_harmlessness_by_regime.csv`.

## 7. Failures

No cap failures found.

## 8. Interpretation

Recommended theorem form: `global_strong_cap_Cplus_1_over_4`.

Recommended next file: `Prime_Mesh_R2Q_PositiveHarmlessness_Theorem_Target_v1.md`.

---

*Prime Mesh Theory - RH Programme*
