# Prime Mesh R2Q - EndpointMotion PositiveCap Audit

**Document:** `Prime_Mesh_R2Q_EndpointMotion_PositiveCap_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-09
**Status:** pass

## 1. Executive Verdict

\[
\boxed{E_\theta(J)>0\Rightarrow Q_{\Delta D}(J)\le1/4\text{ passes empirically on the full v3 inventory.}}
\]

## 2. Inputs Used

- Primary input: `<package-root>\prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv`.

## 3. Primitive Coverage

| metric | value |
|---|---:|
| rows | 1468 |
| primitive_full_rows | 1468 |
| primitive_missing_rows | 0 |

## 4. Positive Cap Result

| metric | value |
|---|---:|
| positive_rows | 1320 |
| positive_Q_delta_D_max | 0.1926535586334653 |
| positive_Q_delta_D_q95 | 0.07317313180348672 |
| positive_Q_delta_D_q99 | 0.09993047017263122 |
| positive_above_0p20_count | 0 |
| positive_above_0p225_count | 0 |
| positive_above_0p24_count | 0 |
| positive_above_0p25_count | 0 |
| positive_cap_margin_to_0p25 | 0.05734644136653469 |

## 5. Regime Decomposition

| regime                              |   rows |   Q_delta_D_min |   Q_delta_D_max |   Q_delta_D_mean |   Q_delta_D_median |   Q_delta_D_q95 |   Q_delta_D_q99 |   above_0p20 |   above_0p225 |   above_0p24 |   above_0p25 |   Q_R2Q_max |   Q_exc_max |   abs_epsilon_max |
|:------------------------------------|-------:|----------------:|----------------:|-----------------:|-------------------:|----------------:|----------------:|-------------:|--------------:|-------------:|-------------:|------------:|------------:|------------------:|
| all_positive                        |   1320 |       0.044324  |       0.192654  |        0.0578678 |          0.0561011 |       0.0731731 |       0.0999305 |            0 |             0 |            0 |            0 |   0.215708  | 0.0205672   |         0.0230549 |
| finite_zone                         |   1200 |       0.044324  |       0.192654  |        0.0587757 |          0.0565978 |       0.0749753 |       0.104407  |            0 |             0 |            0 |            0 |   0.215708  | 0.0205672   |         0.0230549 |
| post_P0_tail                        |    120 |       0.0484881 |       0.0561929 |        0.0487889 |          0.0486646 |       0.0486667 |       0.0547624 |            0 |             0 |            0 |            0 |   0.0585344 | 0.0122978   |         0.0104134 |
| sign_inconsistent_positive_harmless |   1320 |       0.044324  |       0.192654  |        0.0578678 |          0.0561011 |       0.0731731 |       0.0999305 |            0 |             0 |            0 |            0 |   0.215708  | 0.0205672   |         0.0230549 |
| h_bin:257<=h<=1024                  |      9 |       0.0475037 |       0.107214  |        0.0655803 |          0.0580684 |       0.0968014 |       0.105131  |            0 |             0 |            0 |            0 |   0.122517  | 0.00890987  |         0.011557  |
| h_bin:2<=h<=4                       |     61 |       0.0484881 |       0.110614  |        0.0646414 |          0.0612882 |       0.0880421 |       0.0988798 |            0 |             0 |            0 |            0 |   0.115798  | 0.0184359   |         0.0144978 |
| h_bin:5<=h<=16                      |      6 |       0.0555864 |       0.0680976 |        0.061849  |          0.0627875 |       0.0670569 |       0.0678895 |            0 |             0 |            0 |            0 |   0.0730965 | 0.0205672   |         0.0155683 |
| h_bin:65<=h<=256                    |      3 |       0.044324  |       0.064822  |        0.0523642 |          0.0479465 |       0.0631345 |       0.0644845 |            0 |             0 |            0 |            0 |   0.0899444 | 0.0127145   |         0.0124079 |
| h_bin:h=1                           |   1241 |       0.0486638 |       0.192654  |        0.057473  |          0.0560969 |       0.0698377 |       0.0998299 |            0 |             0 |            0 |            0 |   0.215708  | 8.89862e-15 |         0.0230549 |
| p_star_bin:100K<=p<1M               |     34 |       0.0711609 |       0.091057  |        0.0777184 |          0.0762238 |       0.0880529 |       0.0900722 |            0 |             0 |            0 |            0 |   0.0944181 | 0.0151762   |         0.0128627 |
| p_star_bin:100M<=p<500M             |    475 |       0.0514062 |       0.0613169 |        0.052632  |          0.0530081 |       0.0531021 |       0.0612819 |            0 |             0 |            0 |            0 |   0.0638595 | 0.0134309   |         0.0126395 |
| p_star_bin:1K<=p<100K               |     22 |       0.0881934 |       0.129018  |        0.0988926 |          0.090944  |       0.12074   |       0.127283  |            0 |             0 |            0 |            0 |   0.13895   | 0.0184359   |         0.0132519 |
| p_star_bin:1M<=p<100M               |    664 |       0.044324  |       0.107214  |        0.0600585 |          0.0569493 |       0.0698051 |       0.0766394 |            0 |             0 |            0 |            0 |   0.122517  | 0.0205672   |         0.0155683 |
| p_star_bin:p<1K                     |      5 |       0.145943  |       0.192654  |        0.166746  |          0.166029  |       0.189235  |       0.19197   |            0 |             0 |            0 |            0 |   0.215708  | 5.50563e-17 |         0.0230549 |
| p_star_bin:p>=500M                  |    120 |       0.0484881 |       0.0561929 |        0.0487889 |          0.0486646 |       0.0486667 |       0.0547624 |            0 |             0 |            0 |            0 |   0.0585344 | 0.0122978   |         0.0104134 |

## 6. Sign-Inconsistency Harmlessness

| metric | value |
|---|---:|
| sign_inconsistent_positive_rows | 1320 |
| sign_inconsistent_positive_Q_delta_D_max | 0.1926535586334653 |
| sign_inconsistent_threshold_relevant_rows | 0 |
| sign_inconsistent_forbidden_rows | 0 |

## 7. Positive Formula Candidate Result

| model_name                |   rows_used | features_used                                                                               |       R2 |         MAE |       RMSE |   max_abs_residual |   residual_q95 |   residual_q99 |   positive_cap_violations_after_model_bound | recommended_status       |
|:--------------------------|------------:|:--------------------------------------------------------------------------------------------|---------:|------------:|-----------:|-------------------:|---------------:|---------------:|--------------------------------------------:|:-------------------------|
| B_positive_geometry_theta |        1320 | neg_E_theta_norm;rho_proxy;h_over_x;pstar_over_x;log_pstar;inv_log_pstar;sqrt_h_over_sqrt_x | 0.974253 | 0.000842149 | 0.00177599 |          0.0264962 |     0.00265158 |     0.00754001 |                                           0 | formula_candidate_strong |

This model is supporting evidence only. The audit pass depends on the actual cap.

## 8. Extremes

| extreme                           |     value | candidate_id   |   block_id |       x |       y |   h |   p_star |   Q_delta_D |     Q_R2Q |      Q_exc |     epsilon | h_bin        | p_star_bin   | status   |
|:----------------------------------|----------:|:---------------|-----------:|--------:|--------:|----:|---------:|------------:|----------:|-----------:|------------:|:-------------|:-------------|:---------|
| positive_Q_delta_D_max            | 0.192654  | hexc_00033     |         34 |     127 |     126 |   1 |      127 |   0.192654  | 0.215708  | 0          |  0.0230549  | h=1          | p<1K         | pass     |
| positive_Q_R2Q_max                | 0.215708  | hexc_00033     |         34 |     127 |     126 |   1 |      127 |   0.192654  | 0.215708  | 0          |  0.0230549  | h=1          | p<1K         | pass     |
| positive_Q_exc_max                | 0.0205672 | hexc_00059     |         60 | 3290983 | 3290975 |   8 |  3291137 |   0.0680976 | 0.0730965 | 0.0205672  | -0.0155683  | 5<=h<=16     | 1M<=p<100M   | pass     |
| positive_abs_epsilon_max          | 0.0230549 | hexc_00033     |         34 |     127 |     126 |   1 |      127 |   0.192654  | 0.215708  | 0          |  0.0230549  | h=1          | p<1K         | pass     |
| positive_formula_residual_abs_max | 0.0264962 | hexc_00047     |         48 | 3440630 | 3439819 | 811 |  3440807 |   0.107214  | 0.122517  | 0.00890987 |  0.00639372 | 257<=h<=1024 | 1M<=p<100M   | pass     |

## 9. Failures

No positive-cap failures.

## 10. Recommended Theorem Form

`E_theta_positive_implies_Q_delta_D_le_1_over_4`

## 11. Recommended Next File

`Prime_Mesh_R2Q_EndpointMotion_PositiveCap_Theorem_Target_v1.md`

---

*Prime Mesh Theory - RH Programme*
