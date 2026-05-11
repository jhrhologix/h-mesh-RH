# Prime Mesh R2Q - RawR2Q Feature Decomposition Audit

**Document:** `Prime_Mesh_R2Q_RawR2Q_Feature_Decomposition_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** RawR2Q feature-basis diagnostic

## 1. Executive Verdict

\[\boxed{\text{Primitive feature basis is partial; export patch is still needed.}}\]

The audit reconstructs the raw target value:

\[
R_{\rm R2Q}^{\rm rec}=Q_{\rm R2Q}\sqrt h\log^2p^*.
\]

This reconstruction is a target value, not a derivation from primitive SR10/B2 features.

## 2. Inputs Used

- `prime_mesh_r2q_b3_no_accumulation_rows.csv`
- `prime_mesh_r2q_blocksystem_definition_blocks.csv`
- `prime_mesh_r2q_blocksystem_definition_geometry.csv`
- `prime_mesh_r2q_channel_compatibility_rows.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_windows.csv`
- `prime_mesh_r2q_hexc_bridge_rigidity_rows.csv`
- `prime_mesh_r2q_negative_transfer_coordinate_rows.csv`
- `prime_mesh_r2q_o1_schur_residual_sign_stability_scopes.csv`
- `prime_mesh_r2q_o1_schur_residual_sign_stability_vectors.csv`
- `prime_mesh_r2q_o2_local_repayment_assembly_caps.csv`
- `prime_mesh_r2q_o2_local_repayment_assembly_components.csv`
- `prime_mesh_r2q_o2_local_repayment_assembly_rows.csv`
- `prime_mesh_r2q_partial_full_interval_compatibility_rows.csv`

## 3. Summary

| metric | value |
|---|---:|
| `rows` | 1468 |
| `coordinate_test_rows` | 1468 |
| `post_P0_rows` | 142 |
| `finite_zone_rows` | 1326 |
| `Q_R2Q_available_rows` | 1468 |
| `R_R2Q_reconstructed_rows` | 1468 |
| `scale_available_rows` | 1468 |
| `candidate_feature_columns_found` | 207 |
| `primitive_feature_columns_found` | 70 |
| `leaky_feature_columns_excluded` | 137 |
| `primitive_feature_basis_available` | Partial |
| `best_model_name` | C_feature_augmented |
| `best_model_R2` | 0.9999992630629926 |
| `best_model_MAE` | 27.38306979550665 |
| `best_model_RMSE` | 37.583356460440726 |
| `best_model_max_abs_residual` | 158.47589235103806 |
| `theta_only_beta_sign` | positive |
| `positive_cap_explained_flag` | True |
| `threshold_classifier_false_positive_count` | 86 |
| `threshold_classifier_false_negative_count` | 0 |
| `raw_coordinate_formula_available` | False |
| `export_patch_needed` | True |
| `pass_rawr2q_feature_decomposition_audit` | True |
| `recommended_theorem_form` | raw_target_reconstructed_but_primitive_formula_missing |
| `recommended_next_file` | Prime_Mesh_R2Q_RawR2Q_Export_Patch_Spec_v1.md |

## 4. Top Primitive Candidate Columns

| column                                             | primitive_candidate   | leaky_excluded   |   non_null_count |           min |              max |           mean |       median |             std |   corr_with_R_R2Q_rec |   corr_with_Q_R2Q |   corr_with_E_theta |   corr_with_negative_indicator |   corr_with_near_forbidden_indicator |
|:---------------------------------------------------|:----------------------|:-----------------|-----------------:|--------------:|-----------------:|---------------:|-------------:|----------------:|----------------------:|------------------:|--------------------:|-------------------------------:|-------------------------------------:|
| theta_local_sum_from_sieve                         | True                  | False            |             1468 |   4.84419     | 681700           | 1070.14        | 18.5031      | 18675.8         |             0.999984  |          0.854262 |          -0.74576   |                      0.167682  |                            0.752794  |
| prime_log_sum                                      | True                  | False            |             1468 |   4.84419     | 681700           | 1070.14        | 18.5031      | 18675.8         |             0.999984  |          0.854262 |          -0.74576   |                      0.167682  |                            0.752794  |
| endpoint_repayment_Q                               | True                  | False            |             1468 |   0.0001198   |      1.80912     |    0.0247675   |  0.00530731  |     0.0763586   |             0.759402  |          0.947744 |          -0.850332  |                      0.487556  |                            0.658906  |
| bridge_excursion_raw                               | True                  | False            |              166 |  12.2372      |    667.014       |   92.9802      | 66.1077      |    85.4005      |             0.650613  |          0.817068 |          -0.8236    |                      0.265965  |                            0.523399  |
| bridge_excursion_absmax                            | True                  | False            |              166 |  12.2372      |    667.014       |   92.9802      | 66.1077      |    85.4005      |             0.650613  |          0.817068 |          -0.8236    |                      0.265965  |                            0.523399  |
| scale_ratio_local_to_global                        | True                  | False            |             1468 |   4.06597e-05 |      0.0887357   |    0.00147303  |  0.000171818 |     0.00551027  |             0.380021  |          0.645944 |          -0.493798  |                      0.434213  |                            0.35921   |
| Q_tail_max_inside                                  | True                  | False            |             1468 |   4.48978e-06 |      0.907132    |    0.0395055   |  0.0111877   |     0.0858839   |             0.361832  |          0.620976 |          -0.552504  |                      0.476248  |                            0.298109  |
| theta_negative_candidate                           | True                  | False            |             1468 |   0           |      1           |    0.100817    |  0           |     0.301189    |             0.171799  |          0.423906 |          -0.577518  |                      1         |                            0.135144  |
| endpoint_line_r2_min                               | True                  | False            |              166 |   0.729127    |      0.999994    |    0.972784    |  0.990402    |     0.0466023   |             0.0950557 |          0.227743 |          -0.299793  |                      0.564499  |                            0.0794036 |
| right_endpoint                                     | True                  | False            |             1468 | 127           |      6.04884e+08 |    1.22203e+08 |  3.96993e+07 |     1.69805e+08 |             0.0343348 |         -0.026092 |          -0.0883768 |                      0.0610396 |                            0.0399319 |
| x__prime_mesh_r2q_channel_compatibility_rows       | True                  | False            |             1468 | 127           |      6.04884e+08 |    1.22203e+08 |  3.96993e+07 |     1.69805e+08 |             0.0343348 |         -0.026092 |          -0.0883768 |                      0.0610396 |                            0.0399319 |
| x__prime_mesh_r2q_o2_local_repayment_assembly_rows | True                  | False            |             1468 | 127           |      6.04884e+08 |    1.22203e+08 |  3.96993e+07 |     1.69805e+08 |             0.0343348 |         -0.026092 |          -0.0883768 |                      0.0610396 |                            0.0399319 |

## 5. Model Results

| model                                   |   rows | status   | feature_list                                                                                                                                                                                                                                                                                                                                                    | coefficients                                                                                                                                                                                                               |         R2 |          MAE |        RMSE |   max_abs_residual |   condition_number | theta_only_beta_sign   |   precision |   recall |   false_positive_count |   false_negative_count |   positive_rows |   positive_above_0p25_count |   max_positive_Q |   separation_margin |
|:----------------------------------------|-------:|:---------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------:|-------------:|------------:|-------------------:|-------------------:|:-----------------------|------------:|---------:|-----------------------:|-----------------------:|----------------:|----------------------------:|-----------------:|--------------------:|
| A_theta_only_raw                        |   1468 | fit      | intercept;negative_E_theta                                                                                                                                                                                                                                                                                                                                      | 123.761331345;80.7499270193                                                                                                                                                                                                |   0.561692 | 2758.35      | 9876.89     |       294517       |      139.098       | positive               | nan         |      nan |                    nan |                    nan |             nan |                         nan |       nan        |         nan         |
| B_normalized_theta                      |   1468 | fit      | intercept;negative_E_theta_over_scale                                                                                                                                                                                                                                                                                                                           | 0.113894963293;0.93202610126                                                                                                                                                                                               |   0.101602 |    0.0196462 |    0.062109 |            1.69583 |       44.7261      | nan                    | nan         |      nan |                    nan |                    nan |             nan |                         nan |       nan        |         nan         |
| C_feature_augmented                     |    166 | fit      | intercept;negative_E_theta;theta_local_sum_from_sieve;prime_log_sum;endpoint_line_right;endpoint_repayment_Q;theta_local_error;E_theta_local;E_theta__prime_mesh_r2q_o2_local_repayment_assembly_rows;E_theta__prime_mesh_r2q_hexc_bridge_rigidity_rows;E_theta__prime_mesh_r2q_channel_compatibility_rows;E_theta;bridge_excursion_raw;bridge_excursion_absmax | 35.9614166453;-1.78535484108;-11440044.6089;11440045.4017;-0.00156784480435;263.989067717;-0.421341523885;-0.421341523885;-0.421341523885;-0.421341523885;-0.421341523885;-0.421341523885;-0.0275494886115;0.0260653475747 |   0.999999 |   27.3831    |   37.5834   |          158.476   |        4.07852e+50 | nan                    | nan         |      nan |                    nan |                    nan |             nan |                         nan |       nan        |         nan         |
| D_threshold_classifier_normalized_theta |   1468 | fit      | negative_E_theta_over_scale                                                                                                                                                                                                                                                                                                                                     | cutoff=0.0096769856776                                                                                                                                                                                                     | nan        |  nan         |  nan        |          nan       |      nan           | nan                    |   0.0337079 |        1 |                     86 |                      0 |             nan |                         nan |       nan        |         nan         |
| E_positive_cap                          |   1320 | checked  | nan                                                                                                                                                                                                                                                                                                                                                             | nan                                                                                                                                                                                                                        | nan        |  nan         |  nan        |          nan       |      nan           | nan                    | nan         |      nan |                    nan |                    nan |            1320 |                           0 |         0.215708 |           0.0342915 |

## 6. Leakage / Honesty Assessment

Columns that are final coordinates, threshold labels, pass/failure flags, channel labels, or downstream repayment flags were excluded from the primitive feature basis.

Current artifacts contain useful diagnostics and downstream components, but they do not expose a proof-grade primitive formula for the raw R2Q coordinate. A generation/export patch should record the SR10/B2 raw terms before the final `Q_R2Q` value is formed.

## 7. Recommended Next File

`Prime_Mesh_R2Q_RawR2Q_Export_Patch_Spec_v1.md`

---

*Prime Mesh Theory - RH Programme*