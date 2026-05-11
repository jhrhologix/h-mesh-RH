# Prime Mesh R2Q - First-Crossing Covering Localization Stress Audit

**Document:** `Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Stress_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** unified FCL stress audit - passes

## 1. Purpose

This audit stress-tests the exact window-selection and sign-localization logic shared by B3 and theta first-crossing.

It checks whether candidate points are covered, whether local theta signs match the channel classification, whether positive rows remain harmless, and whether local/global denominator ratios stay finite and ordered.

## 2. Summary

| metric | value |
|---|---:|
| `candidate_points` | 1469 |
| `post_P0_candidate_points` | 142 |
| `covered_points` | 1469 |
| `uncovered_points` | 0 |
| `coverage_frac` | 1.0 |
| `theta_candidates` | 1468 |
| `theta_covered` | 1468 |
| `theta_uncovered` | 0 |
| `B3_candidates` | 1 |
| `B3_covered` | 1 |
| `B3_uncovered` | 0 |
| `B3_tail_candidates` | 0 |
| `B3_tail_covered` | 0 |
| `B3_tail_uncovered` | 0 |
| `sign_match_frac` | 1.0 |
| `negative_transfer_frac` | 1.0 |
| `positive_harmless_frac` | 1.0 |
| `scale_compatibility_min` | 4.0659668423964146e-05 |
| `scale_compatibility_max` | 0.08873565094161139 |
| `scale_compatibility_q95` | 0.006601895332031715 |
| `scale_compatibility_failures` | 0 |
| `finite_certificate_candidates` | 1327 |
| `post_P0_failures` | 0 |
| `positive_Q_R2Q_max` | 0.2157084836048593 |
| `positive_tail_Q_R2Q_max` | 0.0585344103602869 |
| `negative_Q_R2Q_max` | 1.8193520399038576 |
| `near_forbidden_negative_count` | 4 |
| `near_forbidden_positive_count` | 0 |
| `forbidden_negative_count` | 2 |
| `forbidden_positive_count` | 0 |
| `pass_covering_localization_empirical` | True |

## 3. Failures

No failures found.

## 4. Highest-Risk Crossings

|         x |    p_star |           y |      h | side     | source_coordinate   |   block_id |    Q_theta |     Q_R2Q |   E_theta_local |   theta_local_norm | covered_flag   | finite_certificate_flag   | tail_flag   | B2_active_flag   | negative_transfer_flag   | positive_harmless_flag   |   Cplus_value | O2_B3_repaid_flag   |   scale_ratio_local_to_global |   scale_ratio_global_to_local | sign_match   | scale_compatibility_ok   | localization_ok   | crossing_status             | post_P0   | failure_reason   |
|----------:|----------:|------------:|-------:|:---------|:--------------------|-----------:|-----------:|----------:|----------------:|-------------------:|:---------------|:--------------------------|:------------|:-----------------|:-------------------------|:-------------------------|--------------:|:--------------------|------------------------------:|------------------------------:|:-------------|:-------------------------|:------------------|:----------------------------|:----------|:-----------------|
| 604672261 | 604672261 | 6.04521e+08 | 151650 | negative | theta_local         |         41 | 0.0101563  | 0.75686   |      -1617.07   |        -0.0101563  | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.0158366   |                        63.145 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604810421 | 604810421 | 6.04757e+08 |  53021 | negative | theta_local         |         64 | 0.0109871  | 0.449457  |      -1034.4    |        -0.0109871  | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00936298  |                       106.804 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604432601 | 604432601 | 6.0441e+08  |  22162 | negative | theta_local         |        105 | 0.0113137  | 0.291481  |       -688.591  |        -0.0113137  | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00605523  |                       165.147 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604356173 | 604356173 | 6.04335e+08 |  20686 | negative | theta_local         |        184 | 0.00621151 | 0.281917  |       -365.245  |        -0.00621151 | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00585048  |                       170.926 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604167899 | 604167899 | 6.04162e+08 |   6250 | negative | theta_local         |        219 | 0.0119549  | 0.155094  |       -386.386  |        -0.0119549  | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00321633  |                       310.913 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604724143 | 604724143 | 6.04719e+08 |   5423 | negative | theta_local         |        297 | 0.00953372 | 0.144459  |       -287.049  |        -0.00953372 | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00299462  |                       333.933 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604848841 | 604848841 | 6.04844e+08 |   4791 | negative | theta_local         |        223 | 0.0135309  | 0.135623  |       -382.934  |        -0.0135309  | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00281442  |                       355.312 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604883911 | 604883911 | 6.0488e+08  |   4200 | negative | theta_local         |        215 | 0.0158035  | 0.128615  |       -418.758  |        -0.0158035  | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00263505  |                       379.5   | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604708931 | 604708931 | 6.04705e+08 |   4338 | negative | theta_local         |        228 | 0.0161719  | 0.128014  |       -435.491  |        -0.0161719  | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00267838  |                       373.361 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604685377 | 604685377 | 6.04683e+08 |   2559 | negative | theta_local         |        335 | 0.0064099  | 0.103143  |       -132.574  |        -0.0064099  | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00205717  |                       486.104 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604822567 | 604822567 | 6.0482e+08  |   2762 | negative | theta_local         |        208 | 0.0212617  | 0.103031  |       -456.869  |        -0.0212617  | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00213697  |                       467.953 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604681513 | 604681513 | 6.04679e+08 |   2583 | negative | theta_local         |        379 | 0.00948126 | 0.100571  |       -197.015  |        -0.00948126 | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.0020668   |                       483.839 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604702619 | 604702619 | 6.047e+08   |   2150 | negative | theta_local         |        320 | 0.01315    | 0.0924905 |       -249.297  |        -0.01315    | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00188559  |                       530.337 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604360789 | 604360789 | 6.04359e+08 |   2075 | negative | theta_local         |        301 | 0.0126191  | 0.0905498 |       -235.009  |        -0.0126191  | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00185294  |                       539.683 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604365031 | 604365031 | 6.04363e+08 |   1803 | negative | theta_local         |        382 | 0.00835176 | 0.086994  |       -144.986  |        -0.00835176 | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00172722  |                       578.964 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604870961 | 604870961 | 6.04869e+08 |   1710 | negative | theta_local         |        304 | 0.0114422  | 0.0842281 |       -193.461  |        -0.0114422  | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00168138  |                       594.748 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604813747 | 604813747 | 6.04812e+08 |   1557 | negative | theta_local         |        432 | 0.00626832 | 0.0809592 |       -101.129  |        -0.00626832 | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00160448  |                       623.256 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604434563 | 604434563 | 6.04433e+08 |   1183 | negative | theta_local         |        316 | 0.0151081  | 0.0706268 |       -212.449  |        -0.0151081  | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.001399    |                       714.796 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604143557 | 604143557 | 6.04143e+08 |    767 | negative | theta_local         |        454 | 0.00523959 | 0.0613546 |        -59.3237 |        -0.00523959 | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00112675  |                       887.508 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604711937 | 604711937 | 6.04711e+08 |    771 | negative | theta_local         |        443 | 0.00735603 | 0.0595213 |        -83.5111 |        -0.00735603 | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00112915  |                       885.619 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604864891 | 604865039 | 6.04865e+08 |      3 | positive | theta_local         |        680 | 0.0528692  | 0.0585344 |         37.441  |         0.0528692  | True           | False                     | True        | True             | False                    | True                     |     0.0585344 | False               |                   7.04257e-05 |                     14199.4   | True         | True                     | True              | positive_harmless           | True      |                  |
| 604715329 | 604715411 | 6.04715e+08 |      3 | positive | theta_local         |        608 | 0.0528698  | 0.0575299 |         37.4405 |         0.0528698  | True           | False                     | True        | True             | False                    | True                     |     0.0575299 | False               |                   7.04345e-05 |                     14197.6   | True         | True                     | True              | positive_harmless           | True      |                  |
| 604208350 | 604208581 | 6.04208e+08 |    503 | negative | theta_local         |        463 | 0.00193409 | 0.0555704 |        -17.7337 |        -0.00193409 | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.000912411 |                      1096     | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604206971 | 604206971 | 6.04206e+08 |    626 | negative | theta_local         |        664 | 0.00782843 | 0.0508465 |        -80.0755 |        -0.00782843 | True           | False                     | True        | True             | True                     | False                    |   nan         | True                |                   0.00101787  |                       982.439 | True         | True                     | True              | negative_transferred_repaid | True      |                  |
| 604322441 | 604322441 | 6.04322e+08 |      1 | positive | theta_local         |       1364 | 0.0470109  | 0.0507093 |         19.2196 |         0.0470109  | True           | False                     | True        | True             | False                    | True                     |     0.0507093 | False               |                   4.06786e-05 |                     24583     | True         | True                     | True              | positive_harmless           | True      |                  |

## 5. Interpretation

\[
\boxed{\text{No empirical covering, sign, or scale leak appears in the audited FCL inventory.}}
\]

The finite-zone candidate remains assigned to finite certificate.  Post-`P0` candidates are covered, sign-compatible, and positive rows remain harmless.

## 6. Outputs

- `prime_mesh_r2q_firstcrossing_covering_localization_summary.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_windows.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_failures.csv`

---

*Prime Mesh Theory - RH Programme*
