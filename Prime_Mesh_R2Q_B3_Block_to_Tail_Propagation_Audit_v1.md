# Prime Mesh R2Q - B3 Block-to-Tail Propagation Audit

**Document:** `Prime_Mesh_R2Q_B3_Block_to_Tail_Propagation_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** B3 empirical propagation audit - passes

## 1. Purpose

This audit tests the B3 first-crossing mechanism in the B2-facing SR10 coordinate.  It asks whether a forbidden tail crossing can occur without a covered local B2-active repayment block.

The audit intentionally does not sum local O2 errors.  It uses the first-crossing coordinate and endpoint repayment convention.

## 2. Summary

| metric | value |
|---|---:|
| `rows` | 1469 |
| `blocks` | 1469 |
| `tail_endpoints` | 142 |
| `candidate_crossings` | 1 |
| `tail_candidate_crossings` | 0 |
| `covered_crossings` | 1 |
| `uncovered_crossings` | 0 |
| `uncovered_tail_crossings` | 0 |
| `coverage_frac` | 1.0 |
| `tail_coverage_frac` | 1.0 |
| `Q_tail_max` | 1.1611207216949437 |
| `Q_tail_q95` | 0.1625305292252603 |
| `Q_tail_q99` | 0.446753993019563 |
| `Q_tail_tail_max` | 0.260270594288893 |
| `Q_tail_tail_q95` | 0.06756918130289642 |
| `Q_tail_end_max` | 0.0 |
| `Q_tail_end_tail_max` | 0.0 |
| `Q_local_max` | 1.8193520399038576 |
| `Q_local_q95` | 0.11197206188260186 |
| `Q_local_q99` | 0.24985438637345367 |
| `Q_exc_max` | 0.0205672364492246 |
| `Q_o2_max` | 0.0499059549142798 |
| `Q_boundary_max` | 0.0197548493142798 |
| `first_crossing_exists` | True |
| `first_crossing_block_id` | 0 |
| `first_crossing_p_star` | 110312593 |
| `first_crossing_h` | nan |
| `first_crossing_covered` | True |
| `first_crossing_local_violation` | False |
| `first_crossing_absorbed_by_HExc` | False |
| `accumulation_proxy_max` | 0.0 |
| `accumulation_proxy_mean` | 0.0 |
| `accumulation_proxy_q95` | 0.0 |
| `tail_accumulation_proxy_max` | 0.0 |
| `endpoint_favorable_frac` | 1.0 |
| `endpoint_repayment_covers_excess_frac` | 1.0 |
| `pass_no_uncovered_crossings` | True |
| `pass_no_accumulation` | True |
| `pass_tail_no_candidate_crossing` | True |
| `pass_B3_empirical` | True |

## 3. Candidate Crossings

|   block_id |    p_star |   start_prime |   worst_prime |   end_prime |   covered_y |   covered_h |   d_start |   d_worst |    d_end |   Q_tail_start |   Q_tail_max_inside |   Q_tail_end | candidate_crossing   | first_crossing_inside_flag   | covered_flag   | finite_certificate_flag   | covered_by_block_or_certificate   | local_violation_flag   | absorbed_by_HExc_flag   | endpoint_favorable_flag_final   |   endpoint_repayment_norm |   accumulation_proxy |   Q_local |   Q_post_response |   Q_exc |   Q_o2p4_total |   Q_bdy |   Q_pp |   O2_total_with_o2p4 |     cross_Q |   cross_Q_y |   cross_Q_h | is_tail   | B3_block_pass   |
|-----------:|----------:|--------------:|--------------:|------------:|------------:|------------:|----------:|----------:|---------:|---------------:|--------------------:|-------------:|:---------------------|:-----------------------------|:---------------|:--------------------------|:----------------------------------|:-----------------------|:------------------------|:--------------------------------|--------------------------:|---------------------:|----------:|------------------:|--------:|---------------:|--------:|-------:|---------------------:|------------:|------------:|------------:|:----------|:----------------|
|          0 | 110312593 |     109816669 |     110102617 |   110312593 |         nan |         nan |  0.499058 |   0.79028 | 0.497392 |              0 |             1.16112 |            0 | True                 | True                         | False          | True                      | True                              | False                  | False                   | True                            |                  0.292888 |                    0 |       nan |               nan |     nan |            nan |     nan |    nan |                  nan | 4.27186e-05 | 1.10103e+08 |           1 | False     | True            |

## 4. Worst Rows

|   block_id |    p_star |   start_prime |   worst_prime |   end_prime |        covered_y |   covered_h |   d_start |   d_worst |    d_end |   Q_tail_start |   Q_tail_max_inside |   Q_tail_end | candidate_crossing   | first_crossing_inside_flag   | covered_flag   | finite_certificate_flag   | covered_by_block_or_certificate   | local_violation_flag   | absorbed_by_HExc_flag   | endpoint_favorable_flag_final   |   endpoint_repayment_norm |   accumulation_proxy |     Q_local |   Q_post_response |        Q_exc |   Q_o2p4_total |   Q_bdy |          Q_pp |   O2_total_with_o2p4 |       cross_Q |     cross_Q_y |   cross_Q_h | is_tail   | B3_block_pass   |
|-----------:|----------:|--------------:|--------------:|------------:|-----------------:|------------:|----------:|----------:|---------:|---------------:|--------------------:|-------------:|:---------------------|:-----------------------------|:---------------|:--------------------------|:----------------------------------|:-----------------------|:------------------------|:--------------------------------|--------------------------:|---------------------:|------------:|------------------:|-------------:|---------------:|--------:|--------------:|---------------------:|--------------:|--------------:|------------:|:----------|:----------------|
|          0 | 110312593 |     109816669 |     110102617 |   110312593 |    nan           |         nan |  0.499058 |  0.79028  | 0.497392 |     0          |            1.16112  |            0 | True                 | True                         | False          | True                      | True                              | False                  | False                   | True                            |                 0.292888  |                    0 | nan         |      nan          | nan          |  nan           |     nan | nan           |          nan         |   4.27186e-05 |   1.10103e+08 |           1 | False     | True            |
|          1 | 180530237 |     179667343 |     179845447 |   180530237 |      1.79845e+08 |      684790 |  0.499554 |  0.726783 | 0.49896  |     0          |            0.907132 |            0 | False                | False                        | True           | True                      | True                              | True                   | True                    | True                            |                 0.227824  |                    0 |   1.81935   |        0.00159904 |   0.00223012 |    9.53303e-05 |       0 |   9.53303e-05 |            0.0302464 | nan           | nan           |         nan | False     | True            |
|          3 |  30974597 |      30851291 |      30909673 |    30974597 |      3.09102e+07 |       64413 |  0.501308 |  0.715728 | 0.49642  |     0.005231   |            0.862912 |            0 | False                | False                        | True           | True                      | True                              | False                  | True                    | True                            |                 0.219308  |                    0 |   0.681224  |        0          |   0.00224161 |    0.00011421  |       0 |   0.00011421  |            0.0302653 | nan           | nan           |         nan | False     | True            |
|          2 |     24317 |         24097 |         24137 |       24317 |  24178           |           3 |  0.511162 |  0.714183 | 0.395611 |     0.0446492  |            0.856731 |            0 | False                | False                        | True           | True                      | True                              | False                  | False                   | True                            |                 0.318572  |                    0 |   0.115798  |        0          | nan          |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|          4 |     59921 |         59387 |         59753 |       59921 |  59920           |           1 |  0.498515 |  0.712961 | 0.472496 |     0          |            0.851845 |            0 | False                | False                        | True           | True                      | True                              | False                  | False                   | True                            |                 0.240466  |                    0 |   0.0921983 |        0          | nan          |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|          5 |    356077 |        354961 |        355111 |      356077 | 355293           |         784 |  0.503428 |  0.680821 | 0.495617 |     0.0137139  |            0.723286 |            0 | False                | False                        | True           | True                      | True                              | False                  | True                    | True                            |                 0.185204  |                    0 |   0.156681  |        0          |   0.0128662  |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|          6 |   3448507 |       3441799 |       3445943 |     3448507 |      3.44602e+06 |        2483 |  0.505986 |  0.676618 | 0.494926 |     0.0239423  |            0.706471 |            0 | False                | False                        | True           | True                      | True                              | False                  | True                    | True                            |                 0.181692  |                    0 |   0.178697  |        0.00751677 |   0.00763878 |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|          7 |  30774449 |      30650107 |      30670319 |    30774449 |      3.06703e+07 |      104130 |  0.500808 |  0.661967 | 0.494505 |     0.00323256 |            0.647867 |            0 | False                | False                        | True           | True                      | True                              | False                  | True                    | True                            |                 0.167462  |                    0 |   0.862526  |        0          |   0.00378759 |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|          8 |   3452747 |       3448573 |       3451211 |     3452747 |      3.4513e+06  |        1451 |  0.4997   |  0.660108 | 0.497655 |     0          |            0.640433 |            0 | False                | False                        | True           | True                      | True                              | False                  | True                    | True                            |                 0.162454  |                    0 |   0.138347  |        0          |   0.00764291 |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|          9 |  12883477 |      12848027 |      12871811 |    12883477 |      1.2872e+07  |       11482 |  0.499865 |  0.659808 | 0.497399 |     0          |            0.639233 |            0 | False                | False                        | True           | True                      | True                              | False                  | True                    | True                            |                 0.162409  |                    0 |   0.321295  |        0          |   0.00391915 |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|         10 | 178298621 |     178089889 |     178254509 |   178298621 |      1.78255e+08 |       43765 |  0.499738 |  0.641975 | 0.499888 |     0          |            0.567902 |            0 | False                | False                        | True           | True                      | True                              | False                  | True                    | True                            |                 0.142087  |                    0 |   0.46258   |        0.00917827 |   0.00251433 |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|         12 |   3279709 |       3277541 |       3278837 |     3279709 |      3.27891e+06 |         797 |  0.502392 |  0.623549 | 0.498226 |     0.00956659 |            0.494197 |            0 | False                | False                        | True           | True                      | True                              | False                  | True                    | True                            |                 0.125323  |                    0 |   0.106006  |        0.0173446  |   0.0114063  |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|         13 |     42899 |         42737 |         42863 |       42899 |  42898           |           1 |  0.504233 |  0.618882 | 0.494986 |     0.0169339  |            0.475526 |            0 | False                | False                        | True           | True                      | True                              | False                  | False                   | True                            |                 0.123895  |                    0 |   0.0968248 |        0          | nan          |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|         11 |       211 |           199 |           199 |         211 |    210           |           1 |  0.616167 |  0.616167 | 0.118753 |     0.464669   |            0.464669 |            0 | False                | False                        | True           | True                      | True                              | False                  | False                   | True                            |                 0.497414  |                    0 |   0.191276  |        0          | nan          |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|         14 |   1195669 |       1192831 |       1195247 |     1195669 |      1.19539e+06 |         205 |  0.502921 |  0.615701 | 0.485712 |     0.0116821  |            0.462805 |            0 | False                | False                        | True           | True                      | True                              | False                  | True                    | True                            |                 0.129989  |                    0 |   0.0899444 |        0          |   0.0127145  |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|         15 |     43133 |         42929 |         43067 |       43133 |  43132           |           1 |  0.503247 |  0.6098   | 0.498702 |     0.0129877  |            0.439201 |            0 | False                | False                        | True           | True                      | True                              | False                  | False                   | True                            |                 0.111098  |                    0 |   0.0943897 |        0          | nan          |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|         16 |     58309 |         58211 |         58243 |       58309 |  58308           |           1 |  0.504164 |  0.601001 | 0.416719 |     0.0166572  |            0.404003 |            0 | False                | False                        | True           | True                      | True                              | False                  | False                   | True                            |                 0.184282  |                    0 |   0.0939517 |        0          | nan          |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|         17 |     59333 |         59209 |         59243 |       59333 |  59332           |           1 |  0.513163 |  0.599015 | 0.409594 |     0.0526539  |            0.39606  |            0 | False                | False                        | True           | True                      | True                              | False                  | False                   | True                            |                 0.18942   |                    0 |   0.0929815 |        0          | nan          |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|         18 |   3241093 |       3236963 |       3239081 |     3241093 |      3.23913e+06 |        1964 |  0.499862 |  0.597142 | 0.486914 |     0          |            0.388569 |            0 | False                | False                        | True           | True                      | True                              | False                  | True                    | True                            |                 0.110229  |                    0 |   0.159654  |        0          |   0.00817498 |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |
|         19 |   1515197 |       1513397 |       1513751 |     1515197 |      1.51385e+06 |        1344 |  0.50001  |  0.594294 | 0.495001 |     3.9944e-05 |            0.377175 |            0 | False                | False                        | True           | True                      | True                              | False                  | True                    | True                            |                 0.0992931 |                    0 |   0.151085  |        0          |   0.0103426  |    0           |       0 |   0           |            0.0301511 | nan           | nan           |         nan | False     | True            |

## 5. Interpretation

\[
\boxed{\text{No post-}500M\text{ B2-facing tail first crossing occurs in the audited range.}}
\]

The only forbidden crossing in the full inventory is finite-zone and belongs to the finite-certificate side of the proof stack.

Endpoint repayment remains favorable: endpoint descent is treated as repayment-side motion rather than O2/H-Exc slack.

## 6. Outputs

- `prime_mesh_r2q_b3_block_to_tail_summary.csv`
- `prime_mesh_r2q_b3_block_to_tail_blocks.csv`
- `prime_mesh_r2q_b3_block_to_tail_crossings.csv`
- `prime_mesh_r2q_b3_block_to_tail_worst_rows.csv`

---

*Prime Mesh Theory - RH Programme*
