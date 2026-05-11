# Prime Mesh R2Q - O2 Negative Tail Source Audit

**Document:** `Prime_Mesh_R2Q_O2_Negative_Tail_Source_Audit_v1.md`  
**Project:** Prime Mesh Theory - RH Programme  
**Date:** 2026-05-06  
**Status:** O2-B source diagnostic

## 1. Purpose

This audit asks whether the small negative values of the canonical post-response residual have a coherent arithmetic source.  The diagnostic classifies negative rows by scale, interval length, mu-bin, depth, residues, shell pattern, prime-power slack, and recovery-block position.

The normalized residual is

\[
z(J)=\frac{\mathcal E_{\rm post}(J)}{\sqrt{|J|}\log^2 p^*}.
\]

The negative obstruction size is \([-z(J)]_+\).

## 2. Summary

| metric                          | value               |
|:--------------------------------|:--------------------|
| rows                            | 1468                |
| negative_rows                   | 136                 |
| negative_frac                   | 0.09264305177111716 |
| global_neg_max                  | 0.03946320129494251 |
| global_mean_z                   | 0.03502034658669661 |
| global_std_z                    | 0.05036600955827812 |
| tail_rows                       | 142                 |
| tail_negative_rows              | 23                  |
| tail_negative_frac              | 0.1619718309859155  |
| tail_neg_max                    | 0.03437235322817768 |
| worst_block_id                  | 272                 |
| worst_p_star                    | 39651113            |
| worst_y                         | 39650618            |
| worst_h                         | 347                 |
| worst_is_tail                   | False               |
| worst_scale_bin                 | p<100M              |
| worst_mu_bin                    | 0.25-0.50           |
| worst_depth_bin                 | 0.50-0.55           |
| worst_h_bin                     | 257<=h<=1024        |
| worst_Q_pp                      | 0.0                 |
| worst_Qpp_over_denom            | 0.0                 |
| worst_shell_pattern             | 11111               |
| tail_worst_block_id             | 41                  |
| tail_worst_p_star               | 604672261           |
| tail_worst_y                    | 604520611           |
| tail_worst_h                    | 151650              |
| top_neg_mass_scale_bin          | 100M<=p<500M        |
| top_neg_mass_frac_scale_bin     | 0.4030843810796788  |
| top_neg_mass_h_bin              | 1025<=h<=8192       |
| top_neg_mass_frac_h_bin         | 0.36376823206429254 |
| top_neg_mass_mu_bin             | 0.25-0.50           |
| top_neg_mass_frac_mu_bin        | 0.37895467004071626 |
| top_neg_mass_depth_bin          | 0.50-0.55           |
| top_neg_mass_frac_depth_bin     | 0.9365235052222338  |
| top_neg_mass_pstar_mod_30       | 29                  |
| top_neg_mass_frac_pstar_mod_30  | 0.16669253524304414 |
| top_neg_mass_y_mod_30           | 10                  |
| top_neg_mass_frac_y_mod_30      | 0.19623191263483117 |
| top_neg_mass_shell_pattern      | 11111               |
| top_neg_mass_frac_shell_pattern | 0.7312450385522723  |

## 3. Largest Negative Rows

|   block_id |    p_star |         y |      h |   canonical_z |     neg_Q | is_tail   | scale_bin    | decade   | depth_bin   | mu_bin     | h_bin         |   pstar_mod_30 |   y_mod_30 |   h_mod_30 |   Q_pp |   Qpp_over_denom |   cp_ratio |   prime_count |   local_prime_count |   d_worst |   mu_over_sqrt_p |   recovery_position | recovery_pos_bin   |   shell_pattern |   shell_active_count |   canonical_scaled_E_post |   denom_sqrt_h_logB |
|-----------:|----------:|----------:|-------:|--------------:|----------:|:----------|:-------------|:---------|:------------|:-----------|:--------------|---------------:|-----------:|-----------:|-------:|-----------------:|-----------:|--------------:|--------------------:|----------:|-----------------:|--------------------:|:-------------------|----------------:|---------------------:|--------------------------:|--------------------:|
|        272 |  39651113 |  39650618 |    347 |    -0.0394632 | 0.0394632 | False     | p<100M       | 1e7-1e8  | 0.50-0.55   | 0.25-0.50  | 257<=h<=1024  |             23 |          8 |         17 |      0 |                0 |  0.0666566 |            23 |                  23 |  0.513008 |        0.272645  |           0.188525  | 0.05-0.25          |           11111 |                    5 |                  -225.017 |             5701.96 |
|         41 | 604672261 | 604520611 | 151650 |    -0.0343724 | 0.0343724 | True      | p>=500M      | 1e8-1e9  | 0.55-0.60   | 0.018-0.05 | h>8192        |              1 |          1 |          0 |      0 |                0 |  0.75686   |          7420 |                7420 |  0.565068 |        0.0188626 |           0         | <=0.05             |           11111 |                    5 |                 -5472.69  |           159218    |
|        320 | 604702619 | 604700469 |   2150 |    -0.0337921 | 0.0337921 | True      | p>=500M      | 1e8-1e9  | 0.50-0.55   | 0.25-0.50  | 1025<=h<=8192 |             29 |          9 |         20 |      0 |                0 |  0.0924905 |            94 |                  94 |  0.510444 |        0.268371  |           0.0236149 | <=0.05             |           11111 |                    5 |                  -640.629 |            18958    |
|         87 | 109467389 | 109460158 |   7231 |    -0.0308563 | 0.0308563 | False     | 100M<=p<500M | 1e8-1e9  | 0.50-0.55   | 0.05-0.10  | 1025<=h<=8192 |             29 |         28 |          1 |      0 |                0 |  0.204545  |           381 |                 381 |  0.538161 |        0.09984   |           0.0472991 | <=0.05             |           11111 |                    5 |                  -899.102 |            29138.4  |
|        382 | 604365031 | 604363228 |   1803 |    -0.0287128 | 0.0287128 | True      | p>=500M      | 1e8-1e9  | 0.50-0.55   | 0.10-0.25  | 1025<=h<=8192 |              1 |         28 |          3 |      0 |                0 |  0.086994  |            82 |                  82 |  0.508479 |        0.243184  |           0.0470402 | <=0.05             |           11111 |                    5 |                  -498.451 |            17359.9  |
|         69 | 108581987 | 108578163 |   3824 |    -0.0271616 | 0.0271616 | False     | 100M<=p<500M | 1e8-1e9  | 0.50-0.55   | 0.10-0.25  | 1025<=h<=8192 |             17 |          3 |         14 |      0 |                0 |  0.14696   |           185 |                 185 |  0.546663 |        0.226129  |           0.0314083 | <=0.05             |           11111 |                    5 |                  -575.041 |            21171.1  |
|        338 | 108591737 | 108591025 |    712 |    -0.0264538 | 0.0264538 | False     | 100M<=p<500M | 1e8-1e9  | 0.50-0.55   | 0.25-0.50  | 257<=h<=1024  |             17 |         25 |         22 |      0 |                0 |  0.0670777 |            36 |                  36 |  0.509554 |        0.25701   |           0.0704961 | 0.05-0.25          |           11111 |                    5 |                  -241.667 |             9135.44 |
|        271 | 187425023 | 187423758 |   1265 |    -0.0237093 | 0.0237093 | False     | 100M<=p<500M | 1e8-1e9  | 0.50-0.55   | 0.25-0.50  | 1025<=h<=8192 |             23 |         18 |          5 |      0 |                0 |  0.085523  |            63 |                  63 |  0.513023 |        0.251828  |           0.110408  | 0.05-0.25          |           11111 |                    5 |                  -305.988 |            12905.8  |
|        130 | 109678603 | 109674416 |   4187 |    -0.0228913 | 0.0228913 | False     | 100M<=p<500M | 1e8-1e9  | 0.50-0.55   | 0.10-0.25  | 1025<=h<=8192 |             13 |         26 |         17 |      0 |                0 |  0.152804  |           213 |                 213 |  0.528377 |        0.138458  |           0.0157499 | <=0.05             |           11111 |                    5 |                  -507.666 |            22177.3  |
|         64 | 604810421 | 604757400 |  53021 |    -0.0228235 | 0.0228235 | True      | p>=500M      | 1e8-1e9  | 0.50-0.55   | 0.018-0.05 | h>8192        |             11 |          0 |         11 |      0 |                0 |  0.449457  |          2571 |                2571 |  0.548798 |        0.041351  |           0.0078777 | <=0.05             |           11111 |                    5 |                 -2148.76  |            94146.6  |
|        299 |  39651863 |  39651244 |    619 |    -0.0226646 | 0.0226646 | False     | p<100M       | 1e7-1e8  | 0.50-0.55   | 0.10-0.25  | 257<=h<=1024  |             23 |          4 |         19 |      0 |                0 |  0.0700648 |            34 |                  34 |  0.511154 |        0.209     |           0.0705706 | 0.05-0.25          |           11111 |                    5 |                  -172.605 |             7615.62 |
|        279 |  40863643 |  40862800 |    843 |    -0.0224694 | 0.0224694 | False     | p<100M       | 1e7-1e8  | 0.50-0.55   | 0.10-0.25  | 257<=h<=1024  |             13 |         10 |          3 |      0 |                0 |  0.0829201 |            48 |                  48 |  0.512416 |        0.164908  |           0.118201  | 0.05-0.25          |           11111 |                    5 |                  -200.382 |             8917.99 |

## 4. Strongest Feature Concentrations

| feature              | value        |   rows |   neg_rows |   neg_frac |       mean_z |      min_z |   neg_max |   median_h |   median_qpp_over_denom |   median_cp_ratio |
|:---------------------|:-------------|-------:|-----------:|-----------:|-------------:|-----------:|----------:|-----------:|------------------------:|------------------:|
| h_mod_30             | 17           |      6 |          5 |  0.833333  | -0.0132948   | -0.0394632 | 0.0394632 |     1292   |                       0 |         0.109525  |
| shell_pattern        | 11111        |    166 |         99 |  0.596386  | -0.000661478 | -0.0394632 | 0.0394632 |     1253.5 |                       0 |         0.0948286 |
| shell_active_count   | 5            |    166 |         99 |  0.596386  | -0.000661478 | -0.0394632 | 0.0394632 |     1253.5 |                       0 |         0.0948286 |
| short_boundary_proxy | False        |    163 |         97 |  0.595092  | -0.000821455 | -0.0394632 | 0.0394632 |     1265   |                       0 |         0.0958699 |
| h                    | 257<=h<=1024 |     61 |         35 |  0.57377   | -0.00180909  | -0.0394632 | 0.0394632 |      626   |                       0 |         0.07222   |
| recovery_position    | 0.05-0.25    |     72 |         37 |  0.513889  |  0.00400711  | -0.0394632 | 0.0394632 |      708.5 |                       0 |         0.0756355 |
| y_mod_30             | 8            |      9 |          3 |  0.333333  |  0.00447337  | -0.0394632 | 0.0394632 |     1515   |                       0 |         0.118438  |
| mu                   | 0.25-0.50    |    196 |         53 |  0.270408  |  0.02562     | -0.0394632 | 0.0394632 |        1   |                       0 |         0.0627272 |
| decade               | 1e7-1e8      |    536 |         47 |  0.0876866 |  0.0313998   | -0.0394632 | 0.0394632 |        1   |                       0 |         0.0587895 |
| depth                | 0.50-0.55    |   1408 |        123 |  0.087358  |  0.0341263   | -0.0394632 | 0.0394632 |        1   |                       0 |         0.0579297 |
| tail                 | False        |   1326 |        113 |  0.0852187 |  0.0374077   | -0.0394632 | 0.0394632 |        1   |                       0 |         0.058379  |
| pstar_mod_30         | 23           |    192 |         15 |  0.078125  |  0.0347899   | -0.0394632 | 0.0394632 |        1   |                       0 |         0.0553677 |
| scale                | p<100M       |    796 |         59 |  0.0741206 |  0.0477731   | -0.0394632 | 0.0394632 |        1   |                       0 |         0.0608948 |
| y_mod_30             | 1            |      4 |          3 |  0.75      | -0.0137919   | -0.0343724 | 0.0343724 |     6779   |                       0 |         0.170582  |
| recovery_position    | <=0.05       |     90 |         55 |  0.611111  | -0.00176092  | -0.0343724 | 0.0343724 |     2341.5 |                       0 |         0.129777  |
| h_mod_30             | 0            |      5 |          3 |  0.6       |  0.00587089  | -0.0343724 | 0.0343724 |     4200   |                       0 |         0.128615  |
| h                    | h>8192       |     21 |         11 |  0.52381   |  0.0042407   | -0.0343724 | 0.0343724 |    15789   |                       0 |         0.307552  |
| mu                   | 0.018-0.05   |      6 |          3 |  0.5       | -0.000502817 | -0.0343724 | 0.0343724 |    57341.5 |                       0 |         0.49769   |
| depth                | 0.55-0.60    |     44 |          9 |  0.204545  |  0.0399151   | -0.0343724 | 0.0343724 |     1429.5 |                       0 |         0.132112  |
| tail                 | True         |    142 |         23 |  0.161972  |  0.0127271   | -0.0343724 | 0.0343724 |        1   |                       0 |         0.0499716 |

## 5. Interpretation

The purpose of this audit is source detection, not a new bound.

The main finding is that the remaining negative residuals do **not** point to prime-power slack, boundary truncation, or missing-shell degeneracy.  The worst row has

\[
Q_{\rm pp}=0,
\qquad
Q_{\rm pp}/(\sqrt h\log^2p^*)=0,
\qquad
\text{shell pattern}=11111.
\]

The same fully active shell pattern carries about \(73.1\%\) of the negative mass.  Thus the small negative residual is a genuine LongA / centered-post-response fluctuation, not a bookkeeping nuisance.

The largest global negative value is still only

\[
0.0394632013,
\]

and the largest post-\(500M\) tail negative value is

\[
0.0343723532.
\]

Both remain far below the theorem envelope \(1\), and even below the stronger empirical threshold \(0.05\).

There is mild concentration in the active B2 barrier band \(d\in[0.50,0.55]\), which carries \(93.65\%\) of the negative mass.  This is expected: these are exactly the first-crossing candidate rows O2 is designed to control.  It does not create a new side case.

Conclusion:

\[
\boxed{
\text{O2-B should be treated as a centered LongA fluctuation theorem.}
}
\]

No separate prime-power, boundary, sparse-shell, or residue-class exception is indicated by this audit.

---

*Prime Mesh Theory - RH Programme*
