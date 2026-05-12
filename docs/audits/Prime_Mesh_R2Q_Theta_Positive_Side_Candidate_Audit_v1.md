# Prime Mesh R2Q - Theta Positive-Side Candidate Audit

**Document:** `Prime_Mesh_R2Q_Theta_Positive_Side_Candidate_Audit_v1.md`  
**Project:** Prime Mesh Theory - RH Programme  
**Date:** 2026-05-06  
**Status:** positive-side reflected-coordinate diagnostic

## 1. Purpose

This audit searches for a reflected R2Q coordinate that detects local positive Chebyshev excess \(E_\theta(J)>0\).  It also tests a simple transport idea: whether positive local excess is followed inside the same block by a negative local theta interval.

## 2. Summary

| metric                                        | value                 |
|:----------------------------------------------|:----------------------|
| rows                                          | 1468                  |
| positive_theta_rows                           | 1320                  |
| negative_theta_rows                           | 148                   |
| positive_theta_frac                           | 0.8991825613079019    |
| negative_theta_frac                           | 0.1008174386920981    |
| best_positive_side_coordinate                 | k4_sym_comp_norm      |
| best_corr_positive_theta                      | 0.7151293504980537    |
| best_abs_corr_abs_theta                       | -0.20845291390105647  |
| best_median_separation                        | 0.0038604065633255384 |
| positive_side_Qmax_current_R2Q                | 0.2157084836048593    |
| negative_side_Qmax_current_R2Q                | 1.8193520399038576    |
| positive_side_current_R2Q_pass_frac_Q_le_1    | 1.0                   |
| positive_side_current_R2Q_pass_frac_Q_le_0p75 | 1.0                   |
| transport_positive_rows                       | 1320                  |
| transport_has_later_negative_frac             | 0.0                   |
| transport_median_lag                          | nan                   |
| transport_median_neg_abs_over_pos             | nan                   |
| transport_cover_frac_neg_abs_ge_pos           | 0.0                   |

## 3. Candidate Coordinates

| coordinate                  |   rows_valid |   corr_with_positive_theta |   abs_corr_with_abs_theta |   positive_median |   nonpositive_median |   median_separation_pos_minus_nonpos |   positive_q90 |   nonpositive_q90 |   threshold_pos_q10 |   recall_at_pos_q10 |   false_positive_at_pos_q10 |   max_on_positive |   min_on_positive |
|:----------------------------|-------------:|---------------------------:|--------------------------:|------------------:|---------------------:|-------------------------------------:|---------------:|------------------:|--------------------:|--------------------:|----------------------------:|------------------:|------------------:|
| k4_sym_comp_norm            |         1468 |                   0.715129 |                 -0.208453 |        0.00118304 |          -0.00267737 |                           0.00386041 |    0.00178887  |       -0.00144996 |         0.000885805 |                 0.9 |                   0         |       0.0154323   |      -0.00419565  |
| k4_sym_all_norm             |         1468 |                   0.637377 |                 -0.27898  |        0.00117898 |          -0.00338684 |                           0.00456582 |    0.00161162  |       -0.00182664 |         0.000885725 |                 0.9 |                   0         |       0.0154323   |      -0.00606095  |
| neg_Qmax                    |         1468 |                   0.288569 |                 -0.288569 |       -0.0577178  |          -0.0989411  |                           0.0412234  |   -0.0522195   |       -0.0677084  |        -0.0706975   |                 0.9 |                   0.162162  |      -0.0489909   |      -0.215708    |
| cp_residual_norm            |         1468 |                   0.288549 |                 -0.288549 |       -0.0577178  |          -0.0989411  |                           0.0412234  |   -0.0522195   |       -0.0677084  |        -0.0706975   |                 0.9 |                   0.162162  |      -0.0489909   |      -0.215708    |
| repay_minus_prime_norm      |         1468 |                   0.240957 |                 -0.240957 |       -0.0561011  |          -0.0804519  |                           0.0243508  |   -0.0516042   |       -0.049982   |        -0.0686674   |                 0.9 |                   0.304054  |      -0.044324    |      -0.192654    |
| D_end_norm                  |         1468 |                   0.170985 |                 -0.170985 |       -0.504771   |          -0.664632   |                           0.159861   |   -0.501178    |       -0.557593   |        -0.531573    |                 0.9 |                   0.0337838 |      -0.499341    |      -1.04788     |
| delta_D_norm                |         1468 |                   0.168223 |                 -0.168223 |       -0.00272742 |          -0.136901   |                           0.134174   |   -0.00136756  |       -0.044403   |        -0.01131     |                 0.9 |                   0         |      -0.000809013 |      -0.401159    |
| D_start_norm                |         1468 |                   0.160173 |                 -0.160173 |       -0.501598   |          -0.527899   |                           0.0263008  |   -0.499273    |       -0.508913   |        -0.521116    |                 0.9 |                   0.398649  |      -0.423444    |      -0.97702     |
| canonical_response_norm     |         1468 |                   0.130691 |                  0.130691 |        0.0909617  |           0.0957409  |                          -0.00477923 |    0.137908    |        0.250433   |         0.068333    |                 0.9 |                   0.804054  |       1.19052     |       0.0271934   |
| neg_canonical_response_norm |         1468 |                  -0.130691 |                  0.130691 |       -0.0909617  |          -0.0957409  |                           0.00477923 |   -0.068333    |       -0.0585856  |        -0.137908    |                 0.9 |                   0.702703  |      -0.0271934   |      -1.19052     |
| neg_D_start_norm            |         1468 |                  -0.160173 |                 -0.160173 |        0.501598   |           0.527899   |                          -0.0263008  |    0.521116    |        0.580253   |         0.499273    |                 0.9 |                   1         |       0.97702     |       0.423444    |
| neg_delta_D_norm            |         1468 |                  -0.168223 |                 -0.168223 |        0.00272742 |           0.136901   |                          -0.134174   |    0.01131     |        0.935022   |         0.00136756  |                 0.9 |                   1         |       0.401159    |       0.000809013 |
| neg_D_end_norm              |         1468 |                  -0.170985 |                 -0.170985 |        0.504771   |           0.664632   |                          -0.159861   |    0.531573    |        1.546      |         0.501178    |                 0.9 |                   1         |       1.04788     |       0.499341    |
| prime_minus_repay_norm      |         1468 |                  -0.240957 |                 -0.240957 |        0.0561011  |           0.0804519  |                          -0.0243508  |    0.0686674   |        0.235231   |         0.0516042   |                 0.9 |                   0.891892  |       0.192654    |       0.044324    |
| neg_cp_residual_norm        |         1468 |                  -0.288549 |                 -0.288549 |        0.0577178  |           0.0989411  |                          -0.0412234  |    0.0706975   |        0.249834   |         0.0522195   |                 0.9 |                   0.993243  |       0.215708    |       0.0489909   |
| cp_obstruction_norm         |         1468 |                  -0.288549 |                 -0.288549 |        0.0577178  |           0.0989411  |                          -0.0412234  |    0.0706975   |        0.249834   |         0.0522195   |                 0.9 |                   0.993243  |       0.215708    |       0.0489909   |
| Qmax                        |         1468 |                  -0.288569 |                 -0.288569 |        0.0577178  |           0.0989411  |                          -0.0412234  |    0.0706975   |        0.249834   |         0.0522195   |                 0.9 |                   0.993243  |       0.215708    |       0.0489909   |
| neg_k4_sym_all_norm         |         1468 |                  -0.637377 |                 -0.27898  |       -0.00117898 |           0.00338684 |                          -0.00456582 |   -0.000885725 |        0.00941682 |        -0.00161162  |                 0.9 |                   1         |       0.00606095  |      -0.0154323   |
| neg_k4_sym_comp_norm        |         1468 |                  -0.715129 |                 -0.208453 |       -0.00118304 |           0.00267737 |                          -0.00386041 |   -0.000885805 |        0.00738405 |        -0.00178887  |                 0.9 |                   1         |       0.00419565  |      -0.0154323   |

## 4. Transport Summary

|       |   block_id |         p_star |          pos_y |      pos_h |   pos_theta_local_norm |   neg_y |   neg_h |   neg_theta_local_norm |   lag |   neg_abs_over_pos |
|:------|-----------:|---------------:|---------------:|-----------:|-----------------------:|--------:|--------:|-----------------------:|------:|-------------------:|
| count |   1320     | 1320           | 1320           | 1320       |         1320           |       0 |       0 |                      0 |     0 |                  0 |
| mean  |    798.643 |    1.18733e+08 |    1.18733e+08 |    4.48561 |            0.0548119   |     nan |     nan |                    nan |   nan |                nan |
| std   |    396.537 |    1.66021e+08 |    1.66021e+08 |   38.7621  |            0.0105316   |     nan |     nan |                    nan |   nan |                nan |
| min   |      2     |  127           |  126           |    1       |            0.000248794 |     nan |     nan |                    nan |   nan |                nan |
| 25%   |    476.75  |    1.79965e+07 |    1.79965e+07 |    1       |            0.0498557   |     nan |     nan |                    nan |   nan |                nan |
| 50%   |    808.5   |    3.96914e+07 |    3.96914e+07 |    1       |            0.0538871   |     nan |     nan |                    nan |   nan |                nan |
| 75%   |   1138.25  |    1.78894e+08 |    1.78894e+08 |    1       |            0.0563398   |     nan |     nan |                    nan |   nan |                nan |
| max   |   1468     |    6.04884e+08 |    6.04884e+08 |  811       |            0.163818    |     nan |     nan |                    nan |   nan |                nan |

## 5. Interpretation

The strongest coordinate by correlation is the first candidate for a positive-side dual.  If all correlations are weak or if transport coverage is poor, the positive side likely requires a new construction rather than a simple sign reversal.

The audit gives two useful facts.

First, positive local theta excess is common:

\[
\texttt{positive\_theta\_rows}=1320,
\qquad
\texttt{positive\_theta\_frac}=0.8991825613.
\]

But positive rows are not dangerous for the current R2Q margin:

\[
\texttt{positive\_side\_Qmax\_current\_R2Q}=0.2157084836<1.
\]

In fact:

\[
\texttt{positive\_side\_current\_R2Q\_pass\_frac\_Q\_le\_1}=1.
\]

The large R2Q obstruction belongs to the negative local theta side:

\[
\texttt{negative\_side\_Qmax\_current\_R2Q}=1.8193520399.
\]

Second, the best positive-side coordinate among the tested candidates is:

\[
\texttt{k4\_sym\_comp\_norm},
\]

with:

\[
\operatorname{corr}
\left(
\texttt{k4\_sym\_comp\_norm},
E_\theta^+(J)
\right)
=0.7151293505.
\]

So the positive side is not invisible to the shell geometry.  It is visible through a symmetric-composite K4-family coordinate, but it does not create the forbidden-crossing obstruction.

The simple delayed-transport test did **not** find support:

\[
\texttt{transport\_has\_later\_negative\_frac}=0.
\]

Thus the positive side does not appear to be handled by immediate later negative intervals in the same R2Q block.

Conclusion:

\[
\boxed{
\text{positive local theta excess appears R2Q-harmless in the audited family.}
}
\]

The next proof target should not be a delayed-transport theorem.  It should be a positive-side harmlessness lemma:

\[
\boxed{
E_\theta(J)>0
\quad\Rightarrow\quad
Q_{\rm R2Q}(J)\le C_+<1.
}
\]

The empirical anchor is:

\[
C_+^{\rm obs}=0.2157084836.
\]

---

*Prime Mesh Theory - RH Programme*
