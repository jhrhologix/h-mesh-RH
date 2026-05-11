# Prime Mesh R2Q - O1 Gap C Shell Normalization Audit

**Document:** `Prime_Mesh_R2Q_O1_GapC_Shell_Normalization_Audit_v1.md`  
**Project:** Prime Mesh Theory - RH Programme  
**Date:** 2026-05-07  
**Status:** Gap C computation after shell-normalization repair

## 1. Purpose

This audit decomposes the LongA shell-3 aggregate into the exact q=3 SPF branch and the residual non-3 branch, then measures the observed deviation of the O1 aggregate ratio from the anchor \(R_3/R_2=1/3\).

## 2. Summary

| metric                             |           value |
|:-----------------------------------|----------------:|
| site_rows_shell3                   | 165066          |
| interval_rows_longa                |    166          |
| W2_anchor                          |      1.5745     |
| C_N_est                            |      6.29801    |
| rebuild_R3_abs_max                 |      2.01536    |
| rebuild_R3_mean_abs                |      0.628427   |
| q3_count_frac                      |      0.500927   |
| q3_sumW_frac                       |      0.671345   |
| q3_sumW2_frac                      |      0.627881   |
| q3_meanW_over_shell2               |      0.444444   |
| aggregate_M3_over_M2               |      0.10965    |
| aggregate_R3_R2_rms                |      0.331134   |
| target_R3_R2                       |      0.333333   |
| rms_deviation_from_1over3          |     -0.00219932 |
| aggregate_M3_over_M2_target_1over9 |      0.111111   |
| M_deviation_from_1over9            |     -0.00146138 |
| M3_q3_component_over_M2            |      0.0493983  |
| M3_non3_component_over_M2          |      0.0118555  |
| M3_cross_component_over_M2         |      0.0483987  |
| q3_rms_component_over_R2           |      0.222257   |
| q3_anchor_deviation_from_1over3    |     -0.111076   |
| non3_signed_mean_R3_over_R2        |      0.106057   |
| observed_abs_rms_dev               |      0.00219932 |
| observed_abs_M_dev                 |      0.00146138 |
| O1_sign_margin                     |      0.148199   |
| rms_dev_over_sign_margin           |      0.0148403  |
| M_dev_over_sign_margin             |      0.00986091 |
| passes_rms_dev_within_sign_margin  |      1          |
| passes_M_dev_within_sign_margin    |      1          |

## 3. SPF Class Decomposition

|   q |   count |   count_frac |        sum_W |   sum_W_frac |         sum_W2 |   sum_W2_frac |     mean_W |   mean_W_over_shell2 |     mean_W2 |   side_left_frac |
|----:|--------:|-------------:|-------------:|-------------:|---------------:|--------------:|-----------:|---------------------:|------------:|-----------------:|
|   3 |   82686 |   0.500927   | 57861.9      |  0.671345    | 40490.6        |   0.627881    | 0.699779   |           0.444444   | 0.489691    |         0.5      |
|   5 |   20611 |   0.124865   | 20769.3      |  0.240977    | 20928.9        |   0.324541    | 1.00768    |           0.64       | 1.01542     |         0.504197 |
|   7 |   10299 |   0.0623932  |  5294.96     |  0.0614349   |  2722.26       |   0.0422137   | 0.514123   |           0.326531   | 0.264323    |         0.50869  |
|  11 |    5105 |   0.030927   |  1062.85     |  0.0123318   |   221.285      |   0.00343143  | 0.208199   |           0.132231   | 0.0433467   |         0.497747 |
|  13 |    3904 |   0.0236511  |   581.951    |  0.00675211  |    86.7488     |   0.0013452   | 0.149065   |           0.0946746  | 0.0222205   |         0.496414 |
|  17 |    2655 |   0.0160845  |   231.436    |  0.00268524  |    20.1742     |   0.000312838 | 0.0871697  |           0.0553633  | 0.00759856  |         0.500565 |
|  19 |    2257 |   0.0136733  |   157.503    |  0.00182743  |    10.9912     |   0.000170438 | 0.0697841  |           0.0443213  | 0.00486982  |         0.47984  |
|  23 |    1713 |   0.0103777  |    81.5765   |  0.000946495 |     3.88484    |   6.02416e-05 | 0.047622   |           0.0302457  | 0.00226786  |         0.493287 |
|  29 |    1301 |   0.0078817  |    38.9713   |  0.000452166 |     1.16738    |   1.81024e-05 | 0.0299549  |           0.019025   | 0.000897294 |         0.515757 |
|  31 |    1140 |   0.00690633 |    29.8844   |  0.000346735 |     0.783402   |   1.21481e-05 | 0.0262144  |           0.0166493  | 0.000687195 |         0.485088 |
|  37 |     938 |   0.00568258 |    17.2609   |  0.00020027  |     0.317631   |   4.92546e-06 | 0.0184018  |           0.0116874  | 0.000338626 |         0.450959 |
|  41 |     855 |   0.00517975 |    12.8133   |  0.000148667 |     0.192025   |   2.9777e-06  | 0.0149863  |           0.00951814 | 0.000224591 |         0.488889 |
|  43 |     767 |   0.00464663 |    10.4501   |  0.000121248 |     0.14238    |   2.20786e-06 | 0.0136247  |           0.00865333 | 0.000185632 |         0.494133 |
|  47 |     674 |   0.00408322 |     7.68648  |  8.91827e-05 |     0.0876588  |   1.35931e-06 | 0.0114043  |           0.0072431  | 0.000130058 |         0.468843 |
|  53 |     603 |   0.00365308 |     5.4079   |  6.27454e-05 |     0.0484999  |   7.5208e-07  | 0.00896833 |           0.00569598 | 8.0431e-05  |         0.480929 |
|  59 |     505 |   0.00305938 |     3.65469  |  4.24037e-05 |     0.0264491  |   4.10142e-07 | 0.00723701 |           0.00459638 | 5.23744e-05 |         0.508911 |
|  61 |     473 |   0.00286552 |     3.20232  |  3.71551e-05 |     0.0216805  |   3.36196e-07 | 0.00677024 |           0.00429992 | 4.58361e-05 |         0.486258 |
|  67 |     453 |   0.00274436 |     2.54221  |  2.94961e-05 |     0.0142668  |   2.21233e-07 | 0.00561195 |           0.00356427 | 3.1494e-05  |         0.498896 |
|  71 |     400 |   0.00242327 |     1.99897  |  2.31932e-05 |     0.00998972 |   1.54909e-07 | 0.00499743 |           0.00317397 | 2.49743e-05 |         0.5175   |
|  73 |     420 |   0.00254444 |     1.98549  |  2.30367e-05 |     0.00938609 |   1.45549e-07 | 0.00472735 |           0.00300244 | 2.23478e-05 |         0.509524 |
|  79 |     351 |   0.00212642 |     1.41683  |  1.64388e-05 |     0.00571907 |   8.86848e-08 | 0.00403654 |           0.00256369 | 1.62937e-05 |         0.492877 |
|  83 |     316 |   0.00191439 |     1.15556  |  1.34075e-05 |     0.00422573 |   6.55277e-08 | 0.00365685 |           0.00232254 | 1.33726e-05 |         0.487342 |
|  89 |     330 |   0.0019992  |     1.04954  |  1.21773e-05 |     0.00333796 |   5.17612e-08 | 0.00318041 |           0.00201995 | 1.0115e-05  |         0.484848 |
|  97 |     288 |   0.00174476 |     0.771103 |  8.94675e-06 |     0.00206458 |   3.20152e-08 | 0.00267744 |           0.0017005  | 7.16869e-06 |         0.503472 |
| 103 |     269 |   0.00162965 |     0.638765 |  7.4113e-06  |     0.00151681 |   2.35209e-08 | 0.00237459 |           0.00150815 | 5.63869e-06 |         0.494424 |

## 4. Interpretation

The interval-level shell field rebuild check verifies that the site decomposition matches the O1 aggregate shell field.  The observed aggregate ratio is compared directly against \(1/3\), and the non-3 residual/cross terms are reported in the same second-moment normalization as O1.

The key budget comparison is

\[
|R_3/R_2-1/3|/\delta_{\rm sign}.
\]

The LongA aggregate result is:

\[
R_3/R_2=0.3311340148,
\]

so:

\[
R_3/R_2-\frac13=-0.0021993185.
\]

At the second-moment level:

\[
M_3/M_2=0.1096497358,
\]

so:

\[
M_3/M_2-\frac19=-0.0014613754.
\]

Both deviations are tiny relative to the O1 sign margin:

\[
\frac{|R_3/R_2-1/3|}{\delta_{\rm sign}}
=0.0148403174,
\]

and:

\[
\frac{|M_3/M_2-1/9|}{\delta_{\rm sign}}
=0.0098609063.
\]

The q=3 branch is the leading SPF class:

\[
\texttt{q3\_count\_frac}=0.500926902,
\]

\[
\texttt{q3\_sumW\_frac}=0.6713453503,
\]

\[
\texttt{q3\_sumW2\_frac}=0.6278811045.
\]

However, the interval-level second moment is not q=3 alone.  In O1 normalization:

\[
\frac{M_{3,q=3}}{M_2}=0.0493982891,
\]

\[
\frac{M_{3,q\ne3}}{M_2}=0.0118554882,
\]

\[
\frac{2\langle R_{3,q=3},R_{3,q\ne3}\rangle}{M_2}=0.0483987227.
\]

Thus the near-\(1/9\) law is produced by the q=3 carrier plus the non-3 residual and its coherent cross term.  The final correction relative to \(1/9\) is small and negative, but the non-3 branch is not zero at the component level.

Conclusion:

\[
\boxed{
\text{Gap C is numerically reduced to a small shell-normalization defect safely inside the O1 sign margin.}
}
\]

The proof-facing statement should therefore be:

\[
\boxed{
M_3/M_2=\frac19+\varepsilon_3^{(2)},
\qquad
|\varepsilon_3^{(2)}|\ll\delta_{\rm sign}.
}
\]

The audit supports this with:

\[
|\varepsilon_3^{(2)}|=0.0014613754.
\]

---

*Prime Mesh Theory - RH Programme*
