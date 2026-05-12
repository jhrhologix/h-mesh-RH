# Prime Mesh R2Q - EndpointMotion Structure Audit

**Document:** `Prime_Mesh_R2Q_EndpointMotion_Structure_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** pass

## 1. Executive Verdict

\[
\boxed{\text{EndpointMotion structure passes empirically: positive cap, threshold transfer, and harmless sign inconsistency all hold.}}
\]

## 2. Inputs Used

- Primary inventory: `<package-root>\prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv`.

## 3. Primitive Coverage

| metric | value |
|---|---:|
| rows | 1468 |
| primitive_full_rows | 1468 |
| primitive_missing_rows | 0 |

## 4. Endpoint-Motion Cap Results

| metric | value |
|---|---:|
| positive_rows | 1320 |
| Q_delta_D_positive_max | 0.1926535586334653 |
| positive_Q_delta_D_q95 | 0.07317313180348672 |
| positive_Q_delta_D_q99 | 0.09993047017263122 |
| positive_above_0p25_count | 0 |
| pass_positive_endpoint_cap | True |

## 5. Threshold-Transfer Results

| metric | value |
|---|---:|
| Q_delta_D_gt_0p75_rows | 2 |
| Q_delta_D_gt_0p75_negative_rows | 2 |
| Q_delta_D_gt_0p75_positive_rows | 0 |
| Q_delta_D_gt_0p75_violations | 0 |
| pass_endpoint_threshold_transfer | True |

## 6. Threshold-Relevant Component Shares

| metric | value |
|---|---:|
| threshold_relevant_rows | 3 |
| threshold_relevant_endpoint_dominant_frac | 1.0 |
| min_Q_delta_D_share_threshold_relevant | 0.9865866873249447 |
| pass_threshold_endpoint_dominance | True |

## 7. Positive Short-Window / Tail Decomposition

| separator                   |   rows |   Q_delta_D_max |   Q_delta_D_q95 |   Q_delta_D_q99 |   above_0p25 |
|:----------------------------|-------:|----------------:|----------------:|----------------:|-------------:|
| all_positive                |   1320 |       0.192654  |       0.0731731 |       0.0999305 |            0 |
| positive_finite             |   1200 |       0.192654  |       0.0749753 |       0.104407  |            0 |
| positive_tail               |    120 |       0.0561929 |       0.0486667 |       0.0547624 |            0 |
| positive_h_bin:257<=h<=1024 |      9 |       0.107214  |       0.0968014 |       0.105131  |            0 |
| positive_h_bin:2<=h<=4      |     61 |       0.110614  |       0.0880421 |       0.0988798 |            0 |
| positive_h_bin:5<=h<=16     |      6 |       0.0680976 |       0.0670569 |       0.0678895 |            0 |
| positive_h_bin:65<=h<=256   |      3 |       0.064822  |       0.0631345 |       0.0644845 |            0 |
| positive_h_bin:h=1          |   1241 |       0.192654  |       0.0698377 |       0.0998299 |            0 |
| positive_p_bin:100K<=p<1M   |     34 |       0.091057  |       0.0880529 |       0.0900722 |            0 |
| positive_p_bin:100M<=p<500M |    475 |       0.0613169 |       0.0531021 |       0.0612819 |            0 |
| positive_p_bin:1K<=p<100K   |     22 |       0.129018  |       0.12074   |       0.127283  |            0 |
| positive_p_bin:1M<=p<100M   |    664 |       0.107214  |       0.0698051 |       0.0766394 |            0 |
| positive_p_bin:p<1K         |      5 |       0.192654  |       0.189235  |       0.19197   |            0 |
| positive_p_bin:p>=500M      |    120 |       0.0561929 |       0.0486667 |       0.0547624 |            0 |

## 8. Sign Inconsistency Harmlessness

| metric | value |
|---|---:|
| sign_inconsistent_rows | 1320 |
| sign_inconsistent_positive_rows | 1320 |
| sign_inconsistent_Q_delta_D_max | 0.1926535586334653 |
| sign_inconsistent_Q_R2Q_max | 0.2157084836048593 |
| sign_inconsistent_threshold_relevant_rows | 0 |
| sign_inconsistent_forbidden_rows | 0 |
| pass_sign_inconsistency_harmless | True |

## 9. Regime Decomposition

| row_regime                          |   rows |   Q_R2Q_max |   Q_delta_D_max |   Q_exc_max |   epsilon_abs_max |   threshold_relevant_rows |   sign_inconsistent_rows |   failures |
|:------------------------------------|-------:|------------:|----------------:|------------:|------------------:|--------------------------:|-------------------------:|-----------:|
| forbidden_negative                  |      1 |    1.81935  |        1.80912  |  0.00223012 |        0.00800438 |                         1 |                        0 |          0 |
| threshold_relevant_negative         |      2 |    0.862526 |        0.852843 |  0.00378759 |        0.00868218 |                         2 |                        0 |          0 |
| finite_negative_repaid              |    124 |    0.681224 |        0.664359 |  0.0128662  |        0.0257285  |                         0 |                        0 |          0 |
| post_P0_negative_tail               |     21 |    0.449457 |        0.436528 |  0.00692146 |        0.0164109  |                         0 |                        0 |          0 |
| sign_inconsistent_positive_harmless |   1320 |    0.215708 |        0.192654 |  0.0205672  |        0.0230549  |                         0 |                     1320 |          0 |

## 10. Extremes

| extreme                       |    value | candidate_id   |   block_id |         x |         y |      h |    p_star | E_theta_sign   | DeltaD_sign   |    Q_R2Q |   Q_delta_D |   Q_delta_D_share | row_regime                          | status   |
|:------------------------------|---------:|:---------------|-----------:|----------:|----------:|-------:|----------:|:---------------|:--------------|---------:|------------:|------------------:|:------------------------------------|:---------|
| Q_delta_D_max                 | 1.80912  | hexc_00000     |          1 | 180530237 | 179845447 | 684790 | 180530237 | negative       | negative      | 1.81935  |    1.80912  |          0.994375 | forbidden_negative                  | pass     |
| positive_Q_delta_D_max        | 0.192654 | hexc_00033     |         34 |       127 |       126 |      1 |       127 | positive       | negative      | 0.215708 |    0.192654 |          0.89312  | sign_inconsistent_positive_harmless | pass     |
| negative_Q_delta_D_max        | 1.80912  | hexc_00000     |          1 | 180530237 | 179845447 | 684790 | 180530237 | negative       | negative      | 1.81935  |    1.80912  |          0.994375 | forbidden_negative                  | pass     |
| threshold_Q_delta_D_share_min | 0.986587 | hexc_00040     |         41 | 604672261 | 604520611 | 151650 | 604672261 | negative       | negative      | 0.75686  |    0.746708 |          0.986587 | threshold_relevant_negative         | pass     |
| sign_inconsistent_Q_R2Q_max   | 0.215708 | hexc_00033     |         34 |       127 |       126 |      1 |       127 | positive       | negative      | 0.215708 |    0.192654 |          0.89312  | sign_inconsistent_positive_harmless | pass     |

## 11. Failures

No EndpointMotion structure failures.

## 12. Recommended Theorem Form

`positive_endpoint_cap_plus_threshold_endpoint_transfer_with_harmless_sign_inconsistency`

## 13. Recommended Next File

`Prime_Mesh_R2Q_EndpointMotion_Structure_Theorem_Target_v1.md`

---

*Prime Mesh Theory - RH Programme*
