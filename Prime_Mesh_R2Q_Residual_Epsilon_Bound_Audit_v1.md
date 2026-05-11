# Prime Mesh R2Q - Residual Epsilon Bound Audit

**Document:** `Prime_Mesh_R2Q_Residual_Epsilon_Bound_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-09
**Status:** pass

## 1. Executive Verdict

\[
\boxed{|\epsilon(J)|\le0.03\text{ passes empirically on the full RawR2Q v3 inventory.}}
\]

## 2. Inputs Used

- Primary input: `<package-root>\prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv`.

## 3. Primitive Coverage

| metric | value |
|---|---:|
| rows | 1468 |
| primitive_full_rows | 1468 |
| missing_epsilon_rows | 0 |
| missing_component_rows | 0 |

## 4. Residual Cap Result

| metric | value |
|---|---:|
| abs_epsilon_max | 0.0257284509172872 |
| abs_epsilon_mean | 0.003016362868409504 |
| abs_epsilon_q95 | 0.01139000746469617 |
| abs_epsilon_q99 | 0.016417639920660736 |
| abs_epsilon_above_0p025_count | 1 |
| abs_epsilon_above_0p03_count | 0 |
| pass_residual_cap_0p03 | True |

## 5. Threshold / Forbidden Safety

| metric | value |
|---|---:|
| threshold_relevant_rows | 3 |
| threshold_relevant_abs_epsilon_max | 0.008682176944156815 |
| threshold_relevant_above_0p03_count | 0 |
| forbidden_rows | 1 |
| forbidden_abs_epsilon_max | 0.008004375573475095 |
| forbidden_above_0p03_count | 0 |

## 6. Regime Decomposition

| row_regime                  |   rows |   epsilon_min |   epsilon_max |   abs_epsilon_max |   abs_epsilon_mean |   abs_epsilon_q95 |   epsilon_positive_count |   epsilon_negative_count |   threshold_relevant_rows |   forbidden_rows |   above_0p025 |   above_0p03 |   failures |
|:----------------------------|-------:|--------------:|--------------:|------------------:|-------------------:|------------------:|-------------------------:|-------------------------:|--------------------------:|-----------------:|--------------:|-------------:|-----------:|
| finite_negative             |    124 |    0.00241284 |    0.0257285  |        0.0257285  |         0.0104809  |        0.0198921  |                      124 |                        0 |                         0 |                0 |             1 |            0 |          0 |
| finite_positive             |   1200 |   -0.0155683  |    0.0230549  |        0.0230549  |         0.00229671 |        0.00842495 |                     1136 |                       64 |                         0 |                0 |             0 |            0 |          0 |
| post_P0_negative_tail       |     21 |    0.00327832 |    0.0164109  |        0.0164109  |         0.00889184 |        0.0152679  |                       21 |                        0 |                         0 |                0 |             0 |            0 |          0 |
| post_P0_positive_tail       |    120 |   -0.0104134  |    0.00204325 |        0.0104134  |         0.00135861 |        0.00186079 |                      117 |                        3 |                         0 |                0 |             0 |            0 |          0 |
| threshold_relevant_negative |      2 |    0.00589605 |    0.00868218 |        0.00868218 |         0.00728911 |        0.00854287 |                        2 |                        0 |                         2 |                0 |             0 |            0 |          0 |
| forbidden_negative          |      1 |    0.00800438 |    0.00800438 |        0.00800438 |         0.00800438 |        0.00800438 |                        1 |                        0 |                         1 |                1 |             0 |            0 |          0 |

## 7. Correlation / Proxy Diagnostics

| proxy | corr(epsilon, proxy) | corr(abs_epsilon, proxy) |
|---|---:|---:|
| h | 0.09679671764142675 | 0.09849231891302322 |
| p_star | -0.018285634189081173 | -0.07968437351992687 |
| log_pstar | -0.09904714316506731 | -0.18164988826841688 |
| inv_log_pstar | 0.14845001333988514 | 0.2164647025564021 |
| sqrt_h_over_sqrt_x | 0.43433361494280204 | 0.48017291110486265 |
| rho_proxy | nan | nan |
| Q_delta_D | 0.24349729871301076 | 0.2815840802288292 |
| Q_exc | -0.1674840483921903 | 0.7595362158498448 |
| E_theta_normalized | -0.5719310888181022 | -0.5426181582245084 |

## 8. Extremes

| extreme                   |       value | candidate_id   |   block_id |         x |         y |      h |    p_star | E_theta_sign   |     Q_R2Q |   Q_delta_D |      Q_exc |     epsilon |   epsilon_abs | row_regime                  | status   |
|:--------------------------|------------:|:---------------|-----------:|----------:|----------:|-------:|----------:|:---------------|----------:|------------:|-----------:|------------:|--------------:|:----------------------------|:---------|
| abs_epsilon_max           |  0.0257285  | hexc_00007     |          8 |   3452747 |   3451296 |   1451 |   3452747 | negative       | 0.138347  |   0.104976  | 0.00764291 |  0.0257285  |    0.0257285  | finite_negative             | pass     |
| epsilon_min               | -0.0155683  | hexc_00059     |         60 |   3290983 |   3290975 |      8 |   3291137 | positive       | 0.0730965 |   0.0680976 | 0.0205672  | -0.0155683  |    0.0155683  | finite_positive             | pass     |
| epsilon_max               |  0.0257285  | hexc_00007     |          8 |   3452747 |   3451296 |   1451 |   3452747 | negative       | 0.138347  |   0.104976  | 0.00764291 |  0.0257285  |    0.0257285  | finite_negative             | pass     |
| threshold_abs_epsilon_max |  0.00868218 | hexc_00040     |         41 | 604672261 | 604520611 | 151650 | 604672261 | negative       | 0.75686   |   0.746708  | 0.00146982 |  0.00868218 |    0.00868218 | threshold_relevant_negative | pass     |
| forbidden_abs_epsilon_max |  0.00800438 | hexc_00000     |          1 | 180530237 | 179845447 | 684790 | 180530237 | negative       | 1.81935   |   1.80912   | 0.00223012 |  0.00800438 |    0.00800438 | forbidden_negative          | pass     |

## 9. Failures

No residual epsilon bound failures.

## 10. Recommended Theorem Form

`abs_epsilon_le_0p03`

## 11. Honest Status

This is an empirical audit and theorem-target preparation, not an analytic proof of the epsilon bound.

## 12. Recommended Next File

`Prime_Mesh_R2Q_Residual_Epsilon_Bound_Theorem_Target_v1.md`

---

*Prime Mesh Theory - RH Programme*
