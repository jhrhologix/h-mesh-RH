# Prime Mesh R2Q - O2-D Slack Absorption Audit

**Document:** `Prime_Mesh_R2Q_O2D_Slack_Absorption_Audit_v1.md`  
**Project:** Prime Mesh Theory - RH Programme  
**Date:** 2026-05-06  
**Status:** O2-D slack absorption diagnostic

## 1. Purpose

This audit measures prime-power slack, local boundary/missing-shell exposure, projection leakage, and finite-zone certificate slack in the same O2 normalization.

The main normalization is \(\sqrt{|J|}\log^2p^*\).

## 2. Summary

| metric                                           | value                        |
|:-------------------------------------------------|:-----------------------------|
| rows                                             | 1468                         |
| global_Qpost_max                                 | 0.03946320129494251          |
| tail_Qpost_max                                   | 0.03437235322817768          |
| Qpp_max                                          | 0.0006293709991497           |
| Qpp_tail_max                                     | 0.0                          |
| Qpp_over_denom_max                               | 0.0006293709991497           |
| boundary_local_slack_max                         | 0.019754849314279888         |
| boundary_local_slack_tail_max                    | 0.019754849314279888         |
| projection_leakage_E_abs_max                     | 0.4011668793555976           |
| projection_leakage_response_abs_max              | 0.4011668793555976           |
| projection_leakage_Q_proxy_max                   | 0.009502682738794031         |
| finite_zone_Qpost_max                            | 0.03946320129494251          |
| finite_zone_rows                                 | 1326                         |
| C_slack_proxy_max_component                      | 0.019754849314279888         |
| C_slack_proxy_sum_overcount                      | 0.019754849314279888         |
| passes_Cslack_0p25_component                     | True                         |
| passes_Cslack_0p50_component                     | True                         |
| passes_total_budget_1_component_plus_O2B_O2C_obs | True                         |
| passes_sum_overcount_0p25                        | True                         |
| passes_sum_overcount_0p50                        | True                         |
| passes_sum_overcount_plus_O2B_O2C_obs_le_1       | True                         |
| worst_slack_component                            | projection_leak_response_abs |
| worst_slack_block_id                             | 34                           |
| worst_slack_p_star                               | 127                          |
| worst_slack_value                                | 0.4011668793555976           |

## 3. Component Table

| component                      |   rows |         max |   tail_max |   finite_max |        mean |         q95 |        q99 |   nonzero_frac |   worst_block_id |   worst_p_star |   worst_h | worst_is_tail   |   worst_shell_pattern |
|:-------------------------------|-------:|------------:|-----------:|-------------:|------------:|------------:|-----------:|---------------:|-----------------:|---------------:|----------:|:----------------|----------------------:|
| projection_leak_response_abs   |   1468 | 0.401167    | 0.0269831  |  0.401167    | 0.0306472   | 0.0481127   | 0.0885983  |     1          |               34 |            127 |         1 | False           |                 10000 |
| projection_leak_E_abs          |   1468 | 0.401167    | 0.0269831  |  0.401167    | 0.0306472   | 0.0481127   | 0.0885983  |     1          |               34 |            127 |         1 | False           |                 10000 |
| post_Q                         |   1468 | 0.0394632   | 0.0343724  |  0.0394632   | 0.00128256  | 0.0138172   | 0.022006   |     0.0926431  |              272 |       39651113 |       347 | False           |                 11111 |
| finite_zone_Q                  |   1468 | 0.0394632   | 0          |  0.0394632   | 0.000996281 | 0.00996578  | 0.0187476  |     0.0769755  |              272 |       39651113 |       347 | False           |                 11111 |
| slack_proxy_sum_overcount      |   1468 | 0.0197548   | 0.0197548  |  0.0185637   | 0.000429001 | 0.000107602 | 0.0165368  |     0.0531335  |              680 |      604865039 |         3 | True            |                 10100 |
| boundary_local_proxy_Q         |   1468 | 0.0197548   | 0.0197548  |  0.0185637   | 0.000367188 | 0           | 0.0165368  |     0.0265668  |              680 |      604865039 |         3 | True            |                 10100 |
| projection_leak_negative_extra |   1468 | 0.00950268  | 0.00950268 |  0.00739997  | 6.08948e-05 | 0           | 0.00203534 |     0.023842   |               41 |      604672261 |    151650 | True            |                 11111 |
| Qpp_norm                       |   1468 | 0.000629371 | 0          |  0.000629371 | 9.18333e-07 | 0           | 0          |     0.00340599 |              153 |      108849263 |      1843 | False           |                 11111 |

## 4. Worst Slack Proxy Rows

|   block_id |    p_star |         y |   h |     post_z |    post_Q | is_tail   | is_longa   |   shell_pattern | boundary_local_proxy   | short_window_proxy   | missing_shell_proxy   |   Qpp_norm |   leak_E_z_abs |   leak_response_z_abs |   leak_negative_extra_Q |   finite_zone_Q |   slack_proxy_sum | scale_bin    | depth_bin   | mu_bin    |   cp_ratio |
|-----------:|----------:|----------:|----:|-----------:|----------:|:----------|:-----------|----------------:|:-----------------------|:---------------------|:----------------------|-----------:|---------------:|----------------------:|------------------------:|----------------:|------------------:|:-------------|:------------|:----------|-----------:|
|        680 | 604865039 | 604864888 |   3 | -0.0197548 | 0.0197548 | True      | False      |           10100 | True                   | True                 | True                  |          0 |      0.0269824 |             0.0269824 |                       0 |       0         |         0.0197548 | p>=500M      | 0.50-0.55   | >=1.00    |  0.0585344 |
|        608 | 604715411 | 604715326 |   3 | -0.0187494 | 0.0187494 | True      | False      |           10100 | True                   | True                 | True                  |          0 |      0.0269831 |             0.0269831 |                       0 |       0         |         0.0187494 | p>=500M      | 0.50-0.55   | 0.50-1.00 |  0.0575299 |
|        350 | 178894987 | 178894798 |   3 | -0.0185637 | 0.0185637 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0305529 |             0.0305529 |                       0 |       0.0185637 |         0.0185637 | 100M<=p<500M | 0.50-0.55   | >=1.00    |  0.0624749 |
|        559 | 179412683 | 179412616 |   3 | -0.0180972 | 0.0180972 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0305436 |             0.0305436 |                       0 |       0.0180972 |         0.0180972 | 100M<=p<500M | 0.50-0.55   | 0.50-1.00 |  0.061995  |
|        327 | 109497203 | 109497076 |   3 | -0.0175886 | 0.0175886 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0321948 |             0.0321948 |                       0 |       0.0175886 |         0.0175886 | 100M<=p<500M | 0.50-0.55   | 0.50-1.00 |  0.0638595 |
|        635 | 109814437 | 109814320 |   3 | -0.017119  | 0.017119  | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0321848 |             0.0321848 |                       0 |       0.017119  |         0.017119  | 100M<=p<500M | 0.50-0.55   | 0.50-1.00 |  0.0633755 |
|        370 | 179411909 | 179411668 |   3 | -0.0170084 | 0.0170084 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0305436 |             0.0305436 |                       0 |       0.0170084 |         0.0170084 | 100M<=p<500M | 0.50-0.55   | 0.25-0.50 |  0.0609062 |
|        411 | 179436077 | 179435746 |   3 | -0.0169142 | 0.0169142 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0305432 |             0.0305432 |                       0 |       0.0169142 |         0.0169142 | 100M<=p<500M | 0.50-0.55   | 0.25-0.50 |  0.0608113 |
|        243 |  30781319 |  30781182 |   7 | -0.0168424 | 0.0168424 | False     | True       |           11111 | True                   | True                 | False                 |          0 |      0.0260176 |             0.0260176 |                       0 |       0.0168424 |         0.0168424 | p<100M       | 0.50-0.55   | 0.50-1.00 |  0.0666639 |
|        453 | 180641999 | 180641716 |   3 | -0.0168341 | 0.0168341 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0305217 |             0.0305217 |                       0 |       0.0168341 |         0.0168341 | 100M<=p<500M | 0.50-0.55   | 0.25-0.50 |  0.0607004 |
|        486 | 179621809 | 179621500 |   3 | -0.0168262 | 0.0168262 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0305399 |             0.0305399 |                       0 |       0.0168262 |         0.0168262 | 100M<=p<500M | 0.50-0.55   | 0.25-0.50 |  0.0607186 |
|        458 | 109709861 | 109709668 |   3 | -0.0168159 | 0.0168159 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0321881 |             0.0321881 |                       0 |       0.0168159 |         0.0168159 | 100M<=p<500M | 0.50-0.55   | 0.50-1.00 |  0.0630771 |
|        520 | 179378513 | 179378386 |   3 | -0.0168136 | 0.0168136 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0305442 |             0.0305442 |                       0 |       0.0168136 |         0.0168136 | 100M<=p<500M | 0.50-0.55   | 0.25-0.50 |  0.0607122 |
|        537 | 109705961 | 109705906 |   3 | -0.0166845 | 0.0166845 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0321882 |             0.0321882 |                       0 |       0.0166845 |         0.0166845 | 100M<=p<500M | 0.50-0.55   | 0.50-1.00 |  0.062946  |
|        288 | 108533687 | 108533470 |   3 | -0.0166509 | 0.0166509 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0322256 |             0.0322256 |                       0 |       0.0166509 |         0.0166509 | 100M<=p<500M | 0.50-0.55   | 0.50-1.00 |  0.0629661 |
|        329 | 109452269 | 109452148 |   3 | -0.0164805 | 0.0164805 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0321963 |             0.0321963 |                       0 |       0.0164805 |         0.0164805 | 100M<=p<500M | 0.50-0.55   | 0.50-1.00 |  0.0627535 |
|        356 |  33821677 |  33821502 |   7 | -0.0161796 | 0.0161796 | False     | True       |           11111 | True                   | True                 | False                 |          0 |      0.0257357 |             0.0257357 |                       0 |       0.0161796 |         0.0161796 | p<100M       | 0.50-0.55   | 0.25-0.50 |  0.0654612 |
|        487 | 109567891 | 109567750 |   3 | -0.0161482 | 0.0161482 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0321926 |             0.0321926 |                       0 |       0.0161482 |         0.0161482 | 100M<=p<500M | 0.50-0.55   | 0.25-0.50 |  0.062416  |
|        345 |  31018529 |  31018450 |   3 | -0.0159249 | 0.0159249 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0370751 |             0.0370751 |                       0 |       0.0159249 |         0.0159249 | p<100M       | 0.50-0.55   | >=1.00    |  0.0692098 |
|        173 |  30850439 |  30850276 |   3 | -0.0154505 | 0.0154505 | False     | False      |           10100 | True                   | True                 | True                  |          0 |      0.0370985 |             0.0370985 |                       0 |       0.0154505 |         0.0154505 | p<100M       | 0.50-0.55   | 0.50-1.00 |  0.068769  |

## 5. Interpretation

The component maximum is the theorem-facing conservative slack proxy.  The sum proxy is an intentional overcount, useful as a stress test but not as the exact decomposition because several terms overlap by construction.

The O2-D slack terms are safely inside the remaining O2 budget in the negative-obstruction sense.

Prime-power slack is tiny:

\[
\max_J Q_{\rm pp}/(\sqrt{|J|}\log^2p^*)=0.000629371,
\]

and it is zero in the post-\(500M\) tail.

Boundary / missing-shell local slack is also small:

\[
\max_J Q_{\rm bdry}^{\rm proxy}=0.0197548493.
\]

Projection leakage needs one important interpretation.  The absolute canonical-vs-fitted displacement can be large in small finite rows:

\[
\max |\mathcal L_{\rm leak}|/(\sqrt{|J|}\log^2p^*)=0.4011668794,
\]

but this is not the negative obstruction contribution.  The quantity relevant to O2-D is the extra negative leakage relative to the fitted projection:

\[
\max_J
\left(
[-\mathcal E_{\rm canonical}]_+
-
[-\mathcal E_{\rm fitted}]_+
\right)_+
=0.0095026827.
\]

Thus the theorem-facing slack proxy is:

\[
C_{\rm slack}^{\rm proxy}=0.0197548493.
\]

Together with the observed O2-B and O2-C constants,

\[
0.0394632013+0.0343723532+0.0197548493
=0.0935904038<1.
\]

Even the intentionally overcounted slack sum remains below \(0.25\).

Conclusion:

\[
\boxed{
\text{O2-D slack absorption is safely inside budget in the audited range.}
}
\]

The remaining O2 obstruction is still the small centered LongA fluctuation, not prime powers, boundary exposure, or projection leakage.

---

*Prime Mesh Theory - RH Programme*
