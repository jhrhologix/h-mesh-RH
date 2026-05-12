# Prime Mesh R2Q - RawR2Q Component Bounds Audit

**Document:** `Prime_Mesh_R2Q_RawR2Q_Component_Bounds_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** pass

## 1. Executive Verdict

\[
\boxed{\text{RawR2Q component bounds pass empirically on the full v3 primitive inventory.}}
\]

## 2. Inputs Used

- Primary rows: `<package-root>\prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv`.
- v3 summary: `<package-root>\prime_mesh_r2q_rawr2q_primitive_decomposition_summary_v3.csv`.
- full primitive export: `<package-root>\prime_mesh_r2q_rawr2q_full_primitive_export_rows.csv`.

## 3. Primitive Coverage

| metric | value |
|---|---:|
| rows | 1468 |
| primitive_full_rows | 1468 |
| primitive_missing_rows | 0 |
| threshold_relevant_rows | 3 |
| threshold_relevant_missing_component_count | 0 |

## 4. Component Ledger

| component | bound | max/count | pass |
|---|---:|---:|---:|
| `Q_exc` | <= 0.025 | 0.0205672364492246 / above cap 0 | True |
| `abs(epsilon)` | <= 0.03 | 0.0257284509172871 / above cap 0 | True |
| positive `Q_delta_D` | <= 0.25 | 0.1926535586334653 / above cap 0 | True |
| `Q_delta_D > 3/4` sign | negative theta | violations 0 | True |

## 5. Endpoint-Motion Component

| metric | value |
|---|---:|
| Q_delta_D_max | 1.8091175489119344 |
| Q_delta_D_positive_max | 0.1926535586334653 |
| Q_delta_D_negative_max | 1.8091175489119344 |
| Q_delta_D_threshold_relevant_max | 1.8091175489119344 |
| Q_delta_D_gt_0p75_count | 2 |
| Q_delta_D_gt_0p75_violations | 0 |

## 6. Bridge-Excursion Component

| metric | value |
|---|---:|
| Q_exc_max | 0.0205672364492246 |
| Q_exc_mean | 0.001224311884935629 |
| Q_exc_q95 | 0.009898102196655285 |
| Q_exc_q99 | 0.014359962721857807 |
| Q_exc_above_0p025_count | 0 |

## 7. Residual Component

| metric | value |
|---|---:|
| epsilon_min | -0.0155683033703539 |
| epsilon_max | 0.0257284509172871 |
| abs_epsilon_max | 0.0257284509172871 |
| abs_epsilon_mean | 0.0030163628684094107 |
| abs_epsilon_above_0p03_count | 0 |
| epsilon_positive_count | 1401 |
| epsilon_negative_count | 67 |

## 8. Formula Reconstruction

`epsilon` is the exported v3 formula residual. Therefore `Q_reconstructed = Q_delta_D + Q_exc + epsilon` should reproduce `Q_R2Q` up to floating tolerance.

| metric | value |
|---|---:|
| formula_rows | 1468 |
| formula_residual_max_abs | 2.220446049250313e-16 |
| formula_residual_mean_abs | 9.819858368778792e-17 |
| formula_residual_cap_violations | 0 |
| pass_formula_reconstruction | True |

## 9. Regime Decomposition

| row_regime                  |   rows |   Q_R2Q_max |   Q_delta_D_max |   Q_exc_max |   abs_epsilon_max |   positive_rows |   negative_rows |   threshold_relevant_rows |   failures |
|:----------------------------|-------:|------------:|----------------:|------------:|------------------:|----------------:|----------------:|--------------------------:|-----------:|
| forbidden_negative          |      1 |    1.81935  |        1.80912  |  0.00223012 |        0.00800438 |               0 |               1 |                         1 |          0 |
| threshold_relevant_negative |      2 |    0.862526 |        0.852843 |  0.00378759 |        0.00868218 |               0 |               2 |                         2 |          0 |
| subthreshold_negative       |    145 |    0.681224 |        0.664359 |  0.0128662  |        0.0257285  |               0 |             145 |                         0 |          0 |
| positive_harmless           |   1320 |    0.215708 |        0.192654 |  0.0205672  |        0.0230549  |            1320 |               0 |                         0 |          0 |

## 10. Extremes

| extreme                |      value | candidate_id   |   block_id |         x |         y |      h |    p_star | E_theta_sign   |     Q_R2Q |   Q_delta_D |      Q_exc |     epsilon | row_regime            | status   |
|:-----------------------|-----------:|:---------------|-----------:|----------:|----------:|-------:|----------:|:---------------|----------:|------------:|-----------:|------------:|:----------------------|:---------|
| Q_R2Q_max              |  1.81935   | hexc_00000     |          1 | 180530237 | 179845447 | 684790 | 180530237 | negative       | 1.81935   |   1.80912   | 0.00223012 |  0.00800438 | forbidden_negative    | pass     |
| Q_delta_D_max          |  1.80912   | hexc_00000     |          1 | 180530237 | 179845447 | 684790 | 180530237 | negative       | 1.81935   |   1.80912   | 0.00223012 |  0.00800438 | forbidden_negative    | pass     |
| Q_exc_max              |  0.0205672 | hexc_00059     |         60 |   3290983 |   3290975 |      8 |   3291137 | positive       | 0.0730965 |   0.0680976 | 0.0205672  | -0.0155683  | positive_harmless     | pass     |
| abs_epsilon_max        |  0.0257285 | hexc_00007     |          8 |   3452747 |   3451296 |   1451 |   3452747 | negative       | 0.138347  |   0.104976  | 0.00764291 |  0.0257285  | subthreshold_negative | pass     |
| epsilon_min            | -0.0155683 | hexc_00059     |         60 |   3290983 |   3290975 |      8 |   3291137 | positive       | 0.0730965 |   0.0680976 | 0.0205672  | -0.0155683  | positive_harmless     | pass     |
| epsilon_max            |  0.0257285 | hexc_00007     |          8 |   3452747 |   3451296 |   1451 |   3452747 | negative       | 0.138347  |   0.104976  | 0.00764291 |  0.0257285  | subthreshold_negative | pass     |
| positive_Q_delta_D_max |  0.192654  | hexc_00033     |         34 |       127 |       126 |      1 |       127 | positive       | 0.215708  |   0.192654  | 0          |  0.0230549  | positive_harmless     | pass     |

## 11. Failures

No component-bound failures.

## 12. Recommended Theorem Form

`Q_exc_le_0p025_abs_epsilon_le_0p03_positive_endpoint_cap_negative_threshold_transfer`

## 13. Recommended Next File

`Prime_Mesh_R2Q_RawR2Q_Component_Bounds_Theorem_Target_v1.md`

---

*Prime Mesh Theory - RH Programme*
