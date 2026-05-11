# Prime Mesh R2Q - EndpointMotion DirectFormula Audit

**Document:** `Prime_Mesh_R2Q_EndpointMotion_DirectFormula_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** threshold/cap pass

## 1. Executive Verdict

\[
\boxed{\text{No full global direct formula is strong enough; the threshold/cap theorem target is clean.}}
\]

## 2. Inputs and Joins

- Primary input: `<package-root>\prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv`.
- Optional context was not required for the core formula tests; all primitive fields came from v3.

## 3. Primitive Field Availability

| metric | value |
|---|---:|
| rows | 1468 |
| primitive_full_rows | 1468 |
| missing_required_fields | 0 |

## 4. Positive Endpoint Cap Result

| metric | value |
|---|---:|
| positive_rows | 1320 |
| Q_delta_D_positive_max | 0.1926535586334653 |
| positive_above_0p25_count | 0 |
| positive_cap_supported | True |

## 5. Threshold Endpoint Transfer Result

| metric | value |
|---|---:|
| Q_delta_D_gt_0p75_rows | 2 |
| Q_delta_D_gt_0p75_violations | 0 |
| threshold_formula_supported | True |
| threshold_relevant_endpoint_dominant_frac | 1.0 |
| min_Q_delta_D_share_threshold_relevant | 0.9865866873249447 |

## 6. Sign-Inconsistency Classification

| metric | value |
|---|---:|
| sign_inconsistent_rows | 1320 |
| sign_inconsistent_positive_harmless_rows | 1320 |
| sign_inconsistent_threshold_relevant_rows | 0 |
| sign_inconsistent_forbidden_rows | 0 |
| sign_inconsistency_harmless_supported | True |

## 7. Candidate Direct Formula Models

| model_name                | fit_scope   | features_used                                                                               |   rows_used | coefficient_table                                                                                                                                                                                                            |           R2 |           MAE |         RMSE |   max_abs_residual |   residual_q95 |   residual_q99 |   positive_cap_violations |   threshold_transfer_violations |   sign_failure_count | recommended_status           |
|:--------------------------|:------------|:--------------------------------------------------------------------------------------------|------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------:|--------------:|-------------:|-------------------:|---------------:|---------------:|--------------------------:|--------------------------------:|---------------------:|:-----------------------------|
| A_global_theta            | global      | neg_E_theta_norm                                                                            |        1468 | intercept=-0.102434867772;neg_E_theta_norm=-0.762604665839                                                                                                                                                                   |   0.0716086  |   0.0184586   |   0.0615355  |          1.6988    |     0.0513151  |     0.166432   |                         0 |                               0 |                    0 | not_supported                |
| A_negative_theta          | negative    | neg_E_theta_norm                                                                            |         148 | intercept=-0.120956790193;neg_E_theta_norm=-1.29648193134                                                                                                                                                                    |   0.00172069 |   0.089008    |   0.183925   |          1.67477   |     0.196144   |     0.669164   |                         0 |                               0 |                    0 | not_supported                |
| A_positive_theta          | positive    | neg_E_theta_norm                                                                            |        1320 | intercept=-0.00784145206853;neg_E_theta_norm=0.912691783069                                                                                                                                                                  |   0.753618   |   0.00191174  |   0.00549394 |          0.0927358 |     0.00284149 |     0.0252814  |                         0 |                               0 |                    0 | formula_candidate_partial    |
| B_global_geometry_theta   | global      | neg_E_theta_norm;rho_proxy;h_over_x;pstar_over_x;log_pstar;inv_log_pstar;sqrt_h_over_sqrt_x |        1468 | intercept=1.3919995903;neg_E_theta_norm=0.783552266741;rho_proxy=1.39199959013;h_over_x=19.6853805397;pstar_over_x=-3.70083179016;log_pstar=0.0247643365217;inv_log_pstar=8.16376002603;sqrt_h_over_sqrt_x=-14.55992207      |   0.566973   |   0.0131842   |   0.042026   |          0.978537  |     0.057306   |     0.154619   |                         0 |                               0 |                    0 | formula_candidate_partial    |
| B_negative_geometry_theta | negative    | neg_E_theta_norm;rho_proxy;h_over_x;pstar_over_x;log_pstar;inv_log_pstar;sqrt_h_over_sqrt_x |         148 | intercept=4335.93863202;neg_E_theta_norm=0.601544293894;rho_proxy=4335.93863192;h_over_x=7.03448642529;pstar_over_x=-8677.31952747;log_pstar=0.121378989044;inv_log_pstar=58.7724628182;sqrt_h_over_sqrt_x=-21.0839349063    |   0.840471   |   0.0398215   |   0.0735249  |          0.500229  |     0.133875   |     0.313688   |                         0 |                               0 |                    0 | formula_candidate_partial    |
| B_positive_geometry_theta | positive    | neg_E_theta_norm;rho_proxy;h_over_x;pstar_over_x;log_pstar;inv_log_pstar;sqrt_h_over_sqrt_x |        1320 | intercept=0.688833749879;neg_E_theta_norm=0.25877570491;rho_proxy=0.688833749863;h_over_x=12.6622891616;pstar_over_x=-1.49164006909;log_pstar=0.0032775480989;inv_log_pstar=0.246572218547;sqrt_h_over_sqrt_x=-2.18097928736 |   0.974253   |   0.000842149 |   0.00177599 |          0.0264962 |     0.00265158 |     0.00754001 |                         0 |                               0 |                    0 | formula_candidate_strong     |
| C_threshold_classifier    | all         | Q_delta_D_minus_0p75;minus_E_theta;Q_delta_D_share                                          |        1468 |                                                                                                                                                                                                                              | nan          | nan           | nan          |        nan         |   nan          |   nan          |                         0 |                               0 |                    0 | threshold_only_sufficient    |
| D_positive_cap            | positive    | h_bin;p_star_bin;finite_tail                                                                |        1320 |                                                                                                                                                                                                                              | nan          | nan           | nan          |        nan         |   nan          |   nan          |                         0 |                               0 |                    0 | positive_cap_only_sufficient |

## 8. Regime Decomposition

| row_regime                  |   rows |   Q_delta_D_max |   Q_R2Q_max |   DeltaD_norm_signed_min |   DeltaD_norm_signed_max |   E_theta_norm_min |   E_theta_norm_max |   threshold_relevant_rows |   sign_inconsistent_rows |   failures |
|:----------------------------|-------:|----------------:|------------:|-------------------------:|-------------------------:|-------------------:|-------------------:|--------------------------:|-------------------------:|-----------:|
| forbidden_negative          |      1 |        1.80912  |    1.81935  |                -1.80912  |               -1.80912   |       -0.0103312   |       -0.0103312   |                         1 |                        0 |          0 |
| threshold_relevant_negative |      2 |        0.852843 |    0.862526 |                -0.852843 |               -0.746708  |       -0.0101563   |       -0.00967699  |                         2 |                        0 |          0 |
| subthreshold_negative       |    145 |        0.664359 |    0.681224 |                -0.664359 |               -0.0382937 |       -0.0285688   |       -0.000197853 |                         0 |                        0 |          0 |
| positive_harmless           |   1320 |        0.192654 |    0.215708 |                -0.192654 |               -0.044324  |        0.000248794 |        0.163818    |                         0 |                     1320 |          0 |

## 9. Best Model / Theorem Interpretation

Best fitted model: `B_positive_geometry_theta` with `R2=0.9742532675086427` and `max_abs_residual=0.026496238161577354`.

The positive branch has a strong geometry-theta formula candidate, but the global and negative-branch fits are not strong enough to serve as the main theorem object. The clean proof target is the threshold/cap structure.

## 10. Failures

No direct-formula structural failures for the threshold/cap pass criteria.

## 11. Recommended Next File

`Prime_Mesh_R2Q_EndpointMotion_ThresholdCap_Theorem_Target_v1.md`

---

*Prime Mesh Theory - RH Programme*
