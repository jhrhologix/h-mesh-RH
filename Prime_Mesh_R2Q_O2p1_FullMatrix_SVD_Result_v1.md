# Prime Mesh R2Q - O2.1 Full-Matrix/SVD Result

**Document:** `Prime_Mesh_R2Q_O2p1_FullMatrix_SVD_Result_v1.md`  
**Project:** Prime Mesh Theory - RH Programme  
**Date:** 2026-05-07  
**Status:** O2.1 full correction-matrix/SVD computation result

## 1. Purpose

This computation builds the full correction covariance matrix \(G_{CC}\) for shells \(C=\{0,2,3,4\}\) using the B2-active `sym_all` shell fields, computes its SVD/eigenstructure, fits \(a_{\rm fit}=G_{CC}^{-1}b_C\), and compares the fitted response to the canonical O1 response.

## 2. Summary

| metric                                          | value                                                                           |
|:------------------------------------------------|:--------------------------------------------------------------------------------|
| rows                                            | 1468                                                                            |
| basis                                           | sym_all                                                                         |
| scope                                           | B2-active full interval inventory                                               |
| shells                                          | 0,2,3,4                                                                         |
| lambda1                                         | 33262999837.270306                                                              |
| lambda2                                         | 7915.167536123199                                                               |
| lambda3                                         | 3258.5329451090242                                                              |
| lambda4                                         | 322.55916618958435                                                              |
| rank1_fraction                                  | 0.9999996543830764                                                              |
| eig2_over_eig1                                  | 2.3795711676174392e-07                                                          |
| delta_full                                      | 0.9999997620428832                                                              |
| H_norm_over_lambda                              | 2.379571167609421e-07                                                           |
| dominant_mode_cos_plus_minus_plus_minus         | 0.3804555823897679                                                              |
| dominant_mode_cos_plus_minus_minus_plus         | 0.05496970002002015                                                             |
| inverse_dominant_mode_cos_plus_minus_plus_minus | 0.07981267016739901                                                             |
| inverse_dominant_mode_cos_plus_minus_minus_plus | 0.7652947465314781                                                              |
| G_CC_signs                                      | ++++;++++;++++;++++                                                             |
| G_CC_inverse_signs                              | +--+;-++-;-++-;+--+                                                             |
| a_fit                                           | [14.87642536555883, 1.0, 70.80143048109257, -26.147906564525737]                |
| a_fit_raw                                       | [12.505485612899065, 0.840624364092946, 59.51740747503936, -21.980567328166217] |
| a_fit_signs                                     | +++-                                                                            |
| a_can_sign                                      | [1.0, -1.0, 1.0, -1.0]                                                          |
| a_can_amp                                       | [0.191352, -0.148199, 1.221515, -0.439357]                                      |
| cos_fit_vs_can_sign                             | 0.7202637632790672                                                              |
| cos_fit_vs_can_amp                              | 0.9909480803919306                                                              |
| abs_cos_fit_vs_can_sign                         | 0.7202637632790672                                                              |
| abs_cos_fit_vs_can_amp                          | 0.9909480803919306                                                              |
| projection_leakage_proxy                        | 0.1342456776494045                                                              |
| canonical_scaled_post_max_abs_shell_cos         | 0.0012691508455898                                                              |
| canonical_scaled_post_max_abs_shell_corr        | 0.0003089094488981                                                              |
| projection_leakage_Q_proxy_max                  | 0.009502682738794                                                               |
| canonical_scaled_post_Q_max                     | 0.0394632012949425                                                              |
| canonical_scaled_post_Q_tail_max                | 0.0343723532281776                                                              |
| pass_rank1_0p99                                 | True                                                                            |
| pass_delta_0p10                                 | True                                                                            |
| pass_delta_0p25                                 | True                                                                            |
| pass_cos_0p95                                   | True                                                                            |
| pass_cos_0p98                                   | True                                                                            |
| pass_projection_Q_0p05                          | True                                                                            |
| ridge                                           | 8.31575283338249                                                                |

## 3. Matrix Entries

| matrix           |   row_shell |   col_shell |           value | sign   |
|:-----------------|------------:|------------:|----------------:|:-------|
| G_CC_empirical   |           0 |           0 |     3.52435e+09 | +      |
| G_CC_empirical   |           0 |           2 |     7.04847e+09 | +      |
| G_CC_empirical   |           0 |           3 |     2.33398e+09 | +      |
| G_CC_empirical   |           0 |           4 |     7.04846e+09 | +      |
| G_CC_empirical   |           2 |           0 |     7.04847e+09 | +      |
| G_CC_empirical   |           2 |           2 |     1.40965e+10 | +      |
| G_CC_empirical   |           2 |           3 |     4.66782e+09 | +      |
| G_CC_empirical   |           2 |           4 |     1.40965e+10 | +      |
| G_CC_empirical   |           3 |           0 |     2.33398e+09 | +      |
| G_CC_empirical   |           3 |           2 |     4.66782e+09 | +      |
| G_CC_empirical   |           3 |           3 |     1.54568e+09 | +      |
| G_CC_empirical   |           3 |           4 |     4.66782e+09 | +      |
| G_CC_empirical   |           4 |           0 |     7.04846e+09 | +      |
| G_CC_empirical   |           4 |           2 |     1.40965e+10 | +      |
| G_CC_empirical   |           4 |           3 |     4.66782e+09 | +      |
| G_CC_empirical   |           4 |           4 |     1.40965e+10 | +      |
| G_CC_inverse     |           0 |           0 |     0.000308092 | +      |
| G_CC_inverse     |           0 |           2 |    -0.000297716 | -      |
| G_CC_inverse     |           0 |           3 |    -5.46054e-06 | -      |
| G_CC_inverse     |           0 |           4 |     0.000145474 | +      |
| G_CC_inverse     |           2 |           0 |    -0.000297716 | -      |
| G_CC_inverse     |           2 |           2 |     0.00161596  | +      |
| G_CC_inverse     |           2 |           3 |     4.24023e-06 | +      |
| G_CC_inverse     |           2 |           4 |    -0.00146851  | -      |
| G_CC_inverse     |           3 |           0 |    -5.46054e-06 | -      |
| G_CC_inverse     |           3 |           2 |     4.24023e-06 | +      |
| G_CC_inverse     |           3 |           3 |     0.000121011 | +      |
| G_CC_inverse     |           3 |           4 |    -4.15806e-05 | -      |
| G_CC_inverse     |           4 |           0 |     0.000145474 | +      |
| G_CC_inverse     |           4 |           2 |    -0.00146851  | -      |
| G_CC_inverse     |           4 |           3 |    -4.15806e-05 | -      |
| G_CC_inverse     |           4 |           4 |     0.00140954  | +      |
| rank1_lambda_vvT |           0 |           0 |     3.52434e+09 | +      |
| rank1_lambda_vvT |           0 |           2 |     7.04847e+09 | +      |
| rank1_lambda_vvT |           0 |           3 |     2.33398e+09 | +      |
| rank1_lambda_vvT |           0 |           4 |     7.04846e+09 | +      |
| rank1_lambda_vvT |           2 |           0 |     7.04847e+09 | +      |
| rank1_lambda_vvT |           2 |           2 |     1.40965e+10 | +      |
| rank1_lambda_vvT |           2 |           3 |     4.66783e+09 | +      |
| rank1_lambda_vvT |           2 |           4 |     1.40965e+10 | +      |
| rank1_lambda_vvT |           3 |           0 |     2.33398e+09 | +      |
| rank1_lambda_vvT |           3 |           2 |     4.66783e+09 | +      |
| rank1_lambda_vvT |           3 |           3 |     1.54567e+09 | +      |
| rank1_lambda_vvT |           3 |           4 |     4.66782e+09 | +      |
| rank1_lambda_vvT |           4 |           0 |     7.04846e+09 | +      |
| rank1_lambda_vvT |           4 |           2 |     1.40965e+10 | +      |
| rank1_lambda_vvT |           4 |           3 |     4.66782e+09 | +      |
| rank1_lambda_vvT |           4 |           4 |     1.40965e+10 | +      |
| H_residual       |           0 |           0 |  2931.01        | +      |
| H_residual       |           0 |           2 |  -366.815       | -      |
| H_residual       |           0 |           3 |  -728.955       | -      |
| H_residual       |           0 |           4 |  -857.356       | -      |
| H_residual       |           2 |           0 |  -366.815       | -      |
| H_residual       |           2 |           2 |   415.836       | +      |
| H_residual       |           2 |           3 | -1141.1         | -      |
| H_residual       |           2 |           4 |   145.434       | +      |
| H_residual       |           3 |           0 |  -728.955       | -      |
| H_residual       |           3 |           2 | -1141.1         | -      |
| H_residual       |           3 |           3 |  7538.15        | +      |
| H_residual       |           3 |           4 |  -990.546       | -      |
| H_residual       |           4 |           0 |  -857.356       | -      |
| H_residual       |           4 |           2 |   145.434       | +      |
| H_residual       |           4 |           3 |  -990.546       | -      |
| H_residual       |           4 |           4 |   611.261       | +      |

## 4. Vectors

| vector                         |   index |   shell |          value | sign   |
|:-------------------------------|--------:|--------:|---------------:|:-------|
| eigenvalues_desc               |       0 |       0 |    3.3263e+10  | +      |
| eigenvalues_desc               |       1 |       2 | 7915.17        | +      |
| eigenvalues_desc               |       2 |       3 | 3258.53        | +      |
| eigenvalues_desc               |       3 |       4 |  322.559       | +      |
| dominant_eigenvector_G         |       0 |       0 |    0.325506    | +      |
| dominant_eigenvector_G         |       1 |       2 |    0.650991    | +      |
| dominant_eigenvector_G         |       2 |       3 |    0.215565    | +      |
| dominant_eigenvector_G         |       3 |       4 |    0.65099     | +      |
| dominant_eigenvector_G_inverse |       0 |       0 |    0.116135    | +      |
| dominant_eigenvector_G_inverse |       1 |       2 |   -0.728972    | -      |
| dominant_eigenvector_G_inverse |       2 |       3 |   -0.0109512   | -      |
| dominant_eigenvector_G_inverse |       3 |       4 |    0.674531    | +      |
| b_C                            |       0 |       0 |    3.39822e+10 | +      |
| b_C                            |       1 |       2 |    6.79623e+10 | +      |
| b_C                            |       2 |       3 |    2.25051e+10 | +      |
| b_C                            |       3 |       4 |    6.79622e+10 | +      |
| a_fit_raw                      |       0 |       0 |   12.5055      | +      |
| a_fit_raw                      |       1 |       2 |    0.840624    | +      |
| a_fit_raw                      |       2 |       3 |   59.5174      | +      |
| a_fit_raw                      |       3 |       4 |  -21.9806      | -      |
| a_fit_norm_by_abs_shell2       |       0 |       0 |   14.8764      | +      |
| a_fit_norm_by_abs_shell2       |       1 |       2 |    1           | +      |
| a_fit_norm_by_abs_shell2       |       2 |       3 |   70.8014      | +      |
| a_fit_norm_by_abs_shell2       |       3 |       4 |  -26.1479      | -      |
| a_can_sign                     |       0 |       0 |    1           | +      |
| a_can_sign                     |       1 |       2 |   -1           | -      |
| a_can_sign                     |       2 |       3 |    1           | +      |
| a_can_sign                     |       3 |       4 |   -1           | -      |
| a_can_amp                      |       0 |       0 |    0.191352    | +      |
| a_can_amp                      |       1 |       2 |   -0.148199    | -      |
| a_can_amp                      |       2 |       3 |    1.22151     | +      |
| a_can_amp                      |       3 |       4 |   -0.439357    | -      |
| mode_plus_minus_plus_minus     |       0 |       0 |    1           | +      |
| mode_plus_minus_plus_minus     |       1 |       2 |   -1           | -      |
| mode_plus_minus_plus_minus     |       2 |       3 |    1           | +      |
| mode_plus_minus_plus_minus     |       3 |       4 |   -1           | -      |
| mode_plus_minus_minus_plus     |       0 |       0 |    1           | +      |
| mode_plus_minus_minus_plus     |       1 |       2 |   -1           | -      |
| mode_plus_minus_minus_plus     |       2 |       3 |   -1           | -      |
| mode_plus_minus_minus_plus     |       3 |       4 |    1           | +      |

## 5. Interpretation

The full correction matrix passes the requested strong O2.1 criteria: rank-one structure, full spectral gap, canonical response alignment, and observed projection leakage below the O2 budget threshold.

\[
\boxed{\text{O2.1 is formula-grade at the full-matrix/SVD level, pending formal write-up.}}
\]

Important nuance:

The raw direct fit

\[
a_{\rm fit}=G_{CC}^{-1}b_C
\]

has sign pattern:

\[
\texttt{+++-}.
\]

The earlier O1/LC-F correction-block sign theorem uses the Schur/correction residual object:

\[
a_C
=
G_{CC}^{-1}(b_C/a_1-G_{C1}),
\]

which is the object that produced the correction signs:

\[
\texttt{+-+-}.
\]

Thus this audit should be read as an O2.1 projection/SVD pass, not as a replacement for the O1 correction-block sign proof.  The amplitude canonical response still aligns strongly with the fitted projection:

\[
\cos(a_{\rm fit},a_{\rm can}^{\rm amp})=0.9909480804,
\]

and the observed negative projection leakage is small:

\[
Q_{\rm leak}^{\rm obs}=0.0095026827.
\]

So the projection-completeness conclusion is strong, while the correction-block sign mechanism remains the Schur-residual O1 object, not the raw direct \(G^{-1}b\) object.

---

*Prime Mesh Theory - RH Programme*
