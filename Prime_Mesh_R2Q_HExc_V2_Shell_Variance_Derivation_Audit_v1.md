# Prime Mesh R2Q - H-Exc V2 Shell-Variance Derivation Audit

**Document:** `Prime_Mesh_R2Q_HExc_V2_Shell_Variance_Derivation_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-07
**Status:** Formula-grade V2 derivation audit

## 1. Purpose

This audit derives the H-Exc shell-variance constant from the bare shifted-SPF shell walk

\[
w_2(p)=g(\operatorname{spf}(p-2))+g(\operatorname{spf}(p+2)),
\qquad g(q)=\frac{1}{q(q-1)}.
\]

For primes \(p>3\), exactly one of \(p-2,p+2\) is divisible by 3, giving

\[
w_2(p)=\frac16+X_p,\qquad X_p=g(\operatorname{spf}(p_2^*)).
\]

The variance target is

\[
V_2=\operatorname{Var}(X_p)=\sum_{q\ge5}\tilde d_q(g(q)-\delta)^2.
\]

## 2. Summary

| metric | value |
|---|---:|
| `q_max_series` | 1999993 |
| `series_terms_including_tail_bucket` | 148932 |
| `series_prime_terms` | 148931 |
| `tilde_density_mass_truncated` | 1.0 |
| `delta_conditional_mean` | 0.016654656424565092 |
| `delta_tail_support_notation` | 0.008327328212282546 |
| `epsilon2_support_notation` | 0.0003518783903338706 |
| `V2_formula` | 0.00042637920004743376 |
| `V2_support_formula_2eps_minus_4delta_tail_sq` | 0.0004263792000474339 |
| `V2_formula_abs_delta` | 1.6263032587282567e-19 |
| `sqrt_V2_formula` | 0.020648951548382154 |
| `Q_exc_max` | 0.0205672364492246 |
| `Q_exc_tail_max` | 0.0069214615088821 |
| `Q_exc_max_over_sqrt_V2_formula` | 0.9960426514166548 |
| `Q_exc_tail_max_over_sqrt_V2_formula` | 0.3351967528552023 |
| `sqrt_V2_minus_Q_exc_max` | 8.171509915755326e-05 |
| `relative_gap_sqrt_V2_vs_Q_exc_max` | 0.0039573485833451745 |
| `empirical_Longa_shell2_var_w` | 0.00042619672108959 |
| `empirical_Longa_shell2_std_w` | 0.020644532474473478 |
| `empirical_Longa_shell2_var_over_V2_formula` | 0.99957202659552 |
| `dominant_q_by_variance` | 5 |
| `top5_variance_share_abs_order` | 0.758037663199219 |
| `worst_Q_block_id` | 60 |
| `worst_Q_p_star` | 3291137 |
| `worst_Q_h` | 8 |
| `pass_Q_exc_matches_sqrt_V2_within_1pct` | True |
| `pass_tail_below_sqrt_V2` | True |

## 3. Dominant Series Terms

|   q |     d_q_O1 |   tilde_d_q |         g_q |   mean_term |   second_term | q_label   |   variance_term |   variance_term_abs |   mean_term_cumsum |   second_term_cumsum |   variance_term_cumsum_using_truncated_delta |   variance_share |   variance_share_cumsum_by_abs |
|----:|-----------:|------------:|------------:|------------:|--------------:|:----------|----------------:|--------------------:|-------------------:|---------------------:|---------------------------------------------:|-----------------:|-------------------------------:|
|   5 | 0.125      |  0.25       | 0.05        | 0.0125      |   0.000625    | 5         |     0.000277978 |         0.000277978 |          0.0125    |          0.000625    |                                  0.000277978 |       0.65195    |                       0.65195  |
|  -1 | 0.0510917  |  0.102183   | 0           | 0           |   0           | >2000000  |     2.83434e-05 |         2.83434e-05 |          0.0166547 |          0.000703757 |                                  0.000426379 |       0.0664745  |                       0.718425 |
|   7 | 0.0625     |  0.125      | 0.0238095   | 0.00297619  |   7.08617e-05 | 7         |     6.39902e-06 |         6.39902e-06 |          0.0154762 |          0.000695862 |                                  0.000284377 |       0.0150078  |                       0.733432 |
|  17 | 0.0161133  |  0.0322266  | 0.00367647  | 0.00011848  |   4.35588e-07 | 17        |     5.42803e-06 |         5.42803e-06 |          0.0164633 |          0.000703389 |                                  0.0002983   |       0.0127305  |                       0.746163 |
|  19 | 0.0134277  |  0.0268555  | 0.00292398  | 7.85248e-05 |   2.29605e-07 | 19        |     5.0631e-06  |         5.0631e-06  |          0.0165419 |          0.000703618 |                                  0.000303363 |       0.0118746  |                       0.758038 |
|  13 | 0.0234375  |  0.046875   | 0.00641026  | 0.000300481 |   1.92616e-06 | 13        |     4.91942e-06 |         4.91942e-06 |          0.0163449 |          0.000702953 |                                  0.000292872 |       0.0115377  |                       0.769575 |
|  23 | 0.010376   |  0.020752   | 0.00197628  | 4.10118e-05 |   8.10509e-08 | 23        |     4.4711e-06  |         4.4711e-06  |          0.0165829 |          0.000703699 |                                  0.000307834 |       0.0104862  |                       0.780062 |
|  29 | 0.00778198 |  0.015564   | 0.00123153  | 1.91674e-05 |   2.36052e-08 | 29        |     3.70225e-06 |         3.70225e-06 |          0.016602  |          0.000703723 |                                  0.000311537 |       0.00868299 |                       0.788745 |
|  11 | 0.03125    |  0.0625     | 0.00909091  | 0.000568182 |   5.16529e-06 | 11        |     3.57564e-06 |         3.57564e-06 |          0.0160444 |          0.000701027 |                                  0.000287953 |       0.00838606 |                       0.797131 |
|  31 | 0.00700378 |  0.0140076  | 0.00107527  | 1.50619e-05 |   1.61956e-08 | 31        |     3.39988e-06 |         3.39988e-06 |          0.0166171 |          0.000703739 |                                  0.000314936 |       0.00797384 |                       0.805104 |
|  37 | 0.00564194 |  0.0112839  | 0.000750751 | 8.47138e-06 |   6.35989e-09 | 37        |     2.85408e-06 |         2.85408e-06 |          0.0166256 |          0.000703746 |                                  0.000317791 |       0.00669376 |                       0.811798 |
|  41 | 0.0049367  |  0.00987339 | 0.000609756 | 6.02036e-06 |   3.67095e-09 | 41        |     2.54179e-06 |         2.54179e-06 |          0.0166316 |          0.000703749 |                                  0.000320332 |       0.00596135 |                       0.81776  |
|  43 | 0.00458407 |  0.00916815 | 0.00055371  | 5.07649e-06 |   2.8109e-09  | 43        |     2.37676e-06 |         2.37676e-06 |          0.0166367 |          0.000703752 |                                  0.000322709 |       0.00557428 |                       0.823334 |
|  47 | 0.00408581 |  0.00817161 | 0.000462535 | 3.77965e-06 |   1.74822e-09 | 47        |     2.14247e-06 |         2.14247e-06 |          0.0166404 |          0.000703754 |                                  0.000324852 |       0.0050248  |                       0.828359 |
|  53 | 0.00353579 |  0.00707159 | 0.000362845 | 2.56589e-06 |   9.31019e-10 | 53        |     1.87696e-06 |         1.87696e-06 |          0.016643  |          0.000703755 |                                  0.000326728 |       0.0044021  |                       0.832761 |
|  59 | 0.00310906 |  0.00621812 | 0.000292227 | 1.8171e-06  |   5.31005e-10 | 59        |     1.66477e-06 |         1.66477e-06 |          0.0166448 |          0.000703755 |                                  0.000328393 |       0.00390444 |                       0.836665 |
|  61 | 0.00295361 |  0.00590721 | 0.000273224 | 1.61399e-06 |   4.40982e-10 | 61        |     1.58521e-06 |         1.58521e-06 |          0.0166464 |          0.000703756 |                                  0.000329978 |       0.00371784 |                       0.840383 |
|  67 | 0.00264035 |  0.00528069 | 0.000226142 | 1.19419e-06 |   2.70056e-10 | 67        |     1.42524e-06 |         1.42524e-06 |          0.0166476 |          0.000703756 |                                  0.000331404 |       0.00334265 |                       0.843726 |
|  71 | 0.00245175 |  0.0049035  | 0.000201207 | 9.86619e-07 |   1.98515e-10 | 71        |     1.32746e-06 |         1.32746e-06 |          0.0166486 |          0.000703756 |                                  0.000332731 |       0.00311332 |                       0.846839 |
|  73 | 0.00234959 |  0.00469919 | 0.000190259 | 8.94061e-07 |   1.70103e-10 | 73        |     1.27384e-06 |         1.27384e-06 |          0.0166495 |          0.000703756 |                                  0.000334005 |       0.00298757 |                       0.849827 |

## 4. Empirical LongA Site Check

| scope                                     |   shell |   rows |     mean_w |            var_w |       std_w |    min_w |       max_w |
|:------------------------------------------|--------:|-------:|-----------:|-----------------:|------------:|---------:|------------:|
| LongA sites shell 2                       |       2 |  82533 |  0.183292  |      0.000426197 |   0.0206445 | 0.166667 |    0.216667 |
| LongA sites shell 3                       |       3 |  82533 |  1         |      0           |   0         | 1        |    1        |
| LongA sites shell 4                       |       4 |  82533 |  0.183433  |      0.000427907 |   0.0206859 | 0.166667 |    0.216667 |
| LongA sites shell 2 residual X=w2-1/6     |       2 |  82533 |  0.0166254 |      0.000426197 |   0.0206445 | 0        |    0.05     |
| LongA interval aggregate shell 2 bare sum |       2 |    166 | 91.1304    | 279376           | 528.561     | 0.500363 | 6572.54     |

## 5. Interpretation

\[
\boxed{\sqrt{V_2}\text{ matches the observed H-Exc maximum to within about }1\%.}
\]

The dominant variance terms come from the small residual SPF classes \(q=5,7,11,\ldots\).  The explicit tail bucket has negligible mean but contributes centered variance.  This supports the deterministic H-Exc route: the internal bridge excursion is controlled by the shell-variance scale rather than by the large endpoint descent.

## 6. Outputs

- `prime_mesh_r2q_hexc_v2_shell_variance_summary.csv`
- `prime_mesh_r2q_hexc_v2_shell_variance_terms.csv`
- `prime_mesh_r2q_hexc_v2_shell_variance_empirical.csv`

---

*Prime Mesh Theory - RH Programme*
