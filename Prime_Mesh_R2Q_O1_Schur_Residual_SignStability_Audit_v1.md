# Prime Mesh R2Q - O1 Schur Residual Sign-Stability Audit

**Document:** `Prime_Mesh_R2Q_O1_Schur_Residual_SignStability_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-07
**Status:** O1 Schur residual audit - global pass; scope-local mixed

## 1. Purpose

This audit computes the O1 correction-block Schur residual:

\[
r_C=b_C/a_1-G_{C1},\qquad a_C^{\rm Schur}=G_{CC}^{-1}r_C.
\]

The target sign pattern is:

\[
\operatorname{sgn}(a_C^{\rm Schur})=+-+-.
\]

## 2. Summary

| metric | value |
|---|---:|
| `scope` | global |
| `rows` | 1468 |
| `basis` | sym_all |
| `C_shells` | 0,2,3,4 |
| `G_CC_condition_number` | 100530434.05360726 |
| `G_CC_rank1_fraction` | 0.999999654383076 |
| `G_CC_delta_full` | 0.9999997620428832 |
| `a_1` | 29.07642633083056 |
| `a_direct_signs` | +++- |
| `a_schur_signs` | +-+- |
| `target_signs` | +-+- |
| `pass_schur_signs` | True |
| `schur_margin_min` | 0.1359042109222659 |
| `schur_margin_normalized` | 0.05469331899090342 |
| `schur_distance_to_chamber_boundary` | 0.1359042109222659 |
| `cos_schur_to_target` | 0.7418870163028932 |
| `cos_schur_to_can_amp` | 0.9980706943195704 |
| `Q_diag` | 0.4011668793555976 |
| `Q_diag_classification` | repayment_side |
| `Q_diag_counted_in_O2` | False |
| `Q_diag_repayment_side` | True |
| `O2_budget_clean` | 0.04990595491427989 |
| `O2_budget_with_diag` | 0.4510728342698775 |
| `O2_clean_margin` | 0.9500940450857202 |
| `O2_diag_inclusive_margin` | 0.5489271657301226 |
| `pass_clean_classification` | True |
| `ridge` | 8.31575283338249 |

## 3. Vector Table

| scope   | object                 |              R0 |              R2 |              R3 |              R4 |            norm | signs   |   cos_to_target_plus_minus_plus_minus |   cos_to_direct_fit |   cos_to_canonical_amp |   margin_min_abs_component |
|:--------|:-----------------------|----------------:|----------------:|----------------:|----------------:|----------------:|:--------|--------------------------------------:|--------------------:|-----------------------:|---------------------------:|
| global  | b_C                    |     3.39822e+10 |     6.79623e+10 |     2.25051e+10 |     6.79622e+10 |     1.04398e+11 | ++++    |                            -0.380453  |           0.0485344 |              -0.043079 |                2.25051e+10 |
| global  | G_C1                   |     1.16871e+09 |     2.33735e+09 |     7.73973e+08 |     2.33735e+09 |     3.59045e+09 | ++++    |                            -0.380456  |           0.0485295 |              -0.043084 |                7.73973e+08 |
| global  | r_C = b_C/a1 - G_C1    | 10157.7         | 16724.8         | 24543.2         | 16508.3         | 35465.3         | ++++    |                             0.0206926 |           0.540176  |               0.473863 |            10157.7         |
| global  | a_direct = G_CC^-1 b_C |    12.5055      |     0.840624    |    59.5174      |   -21.9806      |    64.6727      | +++-    |                             0.720264  |           1         |               0.990948 |                0.840624    |
| global  | a_schur = G_CC^-1 r_C  |     0.417766    |    -0.135904    |     2.29901     |    -0.834264    |     2.48484     | +-+-    |                             0.741887  |           0.99737   |               0.998071 |                0.135904    |
| global  | a_can_sign             |     1           |    -1           |     1           |    -1           |     2           | +-+-    |                             1         |           0.720264  |               0.757451 |                1           |
| global  | a_can_amp              |     0.191352    |    -0.148199    |     1.22151     |    -0.439357    |     1.3205      | +-+-    |                             0.757451  |           0.990948  |               1        |                0.148199    |

## 4. Scope Checks

| scope                             |   rows | a_schur                                                                                | a_schur_signs   | pass_schur_signs   |   schur_margin_min |   schur_margin_normalized | Q_diag_classification   | Q_diag_counted_in_O2   |   G_CC_rank1_fraction |   G_CC_delta_full |
|:----------------------------------|-------:|:---------------------------------------------------------------------------------------|:----------------|:-------------------|-------------------:|--------------------------:|:------------------------|:-----------------------|----------------------:|------------------:|
| tail:p_star<500M                  |   1326 | [0.3855588559366179, -0.18938541267561826, -0.055298160288600906, 0.01490661689219297] | +--+            | False              |          0.0149066 |                 0.0343976 | unclassified            | True                   |              1        |          1        |
| h:h<=4                            |   1302 | [0.21505608036104568, -0.007890512081202838, -0.9322449534241836, 0.0]                 | +--0            | False              |          0         |                 0         | unclassified            | True                   |              0.883857 |          0.870274 |
| shell_pattern:10000               |   1241 | [NaN, NaN, NaN, NaN]                                                                   | 0000            | False              |        nan         |               nan         | unclassified            | True                   |              1        |          1        |
| scale:p<100M                      |    796 | [0.4672612950942223, 0.0772684471313767, 0.24154658612408708, -0.3910403307338107]     | +++-            | False              |          0.0772684 |                 0.117079  | unclassified            | True                   |              0.999997 |          0.999998 |
| mu:>=1.00                         |    597 | [1.4760559588686898e-12, -2.6191379911262707e-13, 0.0, 0.0]                            | +000            | False              |          0         |                 0         | unclassified            | True                   |              0.969422 |          0.968458 |
| mu:0.25-0.50                      |    196 | [0.33133330312041576, -0.2289486803274925, 0.11835742824007878, 0.02291793982869028]   | +-++            | False              |          0.0229179 |                 0.0545151 | unclassified            | True                   |              0.999812 |          0.999906 |
| tail:p_star>=500M                 |    142 | [0.7693794820081126, 0.033243527057342126, 0.036117001528134574, -0.4300257130478564]  | +++-            | False              |          0.0332435 |                 0.0376584 | unclassified            | True                   |              1        |          1        |
| scale:p>=500M                     |    142 | [0.7693794820081126, 0.033243527057342126, 0.036117001528134574, -0.4300257130478564]  | +++-            | False              |          0.0332435 |                 0.0376584 | unclassified            | True                   |              1        |          1        |
| h:1025<=h<=8192                   |     75 | [1.681692873347174, -3.7610204876920577, 0.18445747295147163, 2.857647423471361]       | +-++            | False              |          0.184457  |                 0.0367641 | unclassified            | True                   |              0.999973 |          0.999974 |
| mu:0.10-0.25                      |     74 | [0.30622464729699317, -2.764253655428405, 0.22680638720293267, 2.536978897290687]      | +-++            | False              |          0.226806  |                 0.0601404 | unclassified            | True                   |              0.999979 |          0.999981 |
| h:257<=h<=1024                    |     61 | [0.6859595726077288, -0.4529599821158552, 0.28896970252994536, 0.010168691394286888]   | +-++            | False              |          0.0101687 |                 0.0116695 | unclassified            | True                   |              0.999808 |          0.999832 |
| depth:0.55-0.60                   |     44 | [-3.0124301886592804, 1.3138928392912987, 2.3035165641282704, -0.575389792878596]      | -++-            | False              |          0.57539   |                 0.141917  | unclassified            | True                   |              0.999999 |          0.999999 |
| shell_pattern:10100               |     30 | [1.8820577420749357e-14, 1.8820590973276513e-14, 0.0, 0.0]                             | 0000            | False              |          0         |                 0         | unclassified            | True                   |              1        |          1        |
| shell_pattern:11110               |     19 | [-6.650712278263252e-10, -6.650717625548367e-10, 5.986228950747094e-09, 0.0]           | --+0            | False              |          0         |                 0         | unclassified            | True                   |              1        |          1        |
| mu:0.05-0.10                      |     14 | [-2.156035887521057, -20.570217369998772, 1.308163615004446, 21.214114548483906]       | --++            | False              |          1.30816   |                 0.0441099 | unclassified            | True                   |              0.999995 |          0.999995 |
| shell_pattern:11100               |     12 | [1.647945424565478e-08, 1.6479461351082136e-08, 0.0, 0.0]                              | ++00            | False              |          0         |                 0         | unclassified            | True                   |              1        |          1        |
| depth:0.60-0.65                   |      7 | [0.20178544149941846, 0.5349644408570757, 0.5489303612597953, -0.8201107974802788]     | +++-            | False              |          0.201785  |                 0.176922  | unclassified            | True                   |              1        |          1        |
| h:5<=h<=16                        |      6 | [-1.8027943325659734, 1.909877818538682, -0.682338584994385, -0.4773489382427485]      | -+--            | False              |          0.477349  |                 0.173254  | unclassified            | True                   |              0.993328 |          0.994117 |
| mu:0.018-0.05                     |      6 | [6.077942846069163, 29.461089034035467, 6.970029854468876, -34.821524830508]           | +++-            | False              |          6.07794   |                 0.130595  | unclassified            | True                   |              0.999999 |          0.999999 |
| depth:0.65-0.70                   |      5 | [0.8845744218968292, -2.589817154876922, 0.27025643249137055, 2.0577109250299017]      | +-++            | False              |          0.270256  |                 0.0786852 | unclassified            | True                   |              1        |          1        |
| global                            |   1468 | [0.4177662612488078, -0.1359042109222659, 2.299008780408493, -0.8342635552207134]      | +-+-            | True               |          0.135904  |                 0.0546933 | repayment_side          | False                  |              1        |          1        |
| depth:0.50-0.55                   |   1408 | [0.3770866594719713, -0.07363889017218483, 0.4238063409461045, -0.2560401770960129]    | +-+-            | True               |          0.0736389 |                 0.117498  | repayment_side          | False                  |              0.999982 |          0.999988 |
| mu:0.50-1.00                      |    579 | [0.30362792956438683, -0.11217427615162662, 0.19199371860184034, -0.10423153147309971] | +-+-            | True               |          0.104232  |                 0.266911  | repayment_side          | False                  |              0.98777  |          0.989176 |
| scale:100M<=p<500M                |    530 | [0.6271132246942965, -0.23277338530124592, 1.3449282042650124, -0.5259577070252757]    | +-+-            | True               |          0.232773  |                 0.146259  | repayment_side          | False                  |              1        |          1        |
| LongA only                        |    166 | [1.1110809339816115, -0.17524611527355916, 2.2926590191146987, -1.1394873409323463]    | +-+-            | True               |          0.175246  |                 0.0626682 | repayment_side          | False                  |              1        |          1        |
| nondegenerate shell_pattern=11111 |    166 | [1.1110809339816115, -0.17524611527355916, 2.2926590191146987, -1.1394873409323463]    | +-+-            | True               |          0.175246  |                 0.0626682 | repayment_side          | False                  |              1        |          1        |
| shell_pattern:11111               |    166 | [1.1110809339816115, -0.17524611527355916, 2.2926590191146987, -1.1394873409323463]    | +-+-            | True               |          0.175246  |                 0.0626682 | repayment_side          | False                  |              1        |          1        |
| h:8193<=h<=65536                  |     18 | [22.208033816721127, -5.751034863584323, 3.854768446915596, -6.636661986604963]        | +-+-            | True               |          3.85477   |                 0.159351  | repayment_side          | False                  |              0.999998 |          0.999998 |

## 5. Interpretation

\[
\boxed{\operatorname{sgn}(a_C^{\rm Schur})=+-+-}
\]

The global B2-active Schur residual object passes the correction-block sign test.  Under the O1 ledger convention, the `0.4011668793555976` diagnostic is classified as B2/MR-2 repayment-side mass, not O2 obstruction slack.

Scope checks are mixed: several arbitrary tail/scale/h/mu subfamilies flip signs.  Therefore the proof-facing statement should be a global B2-active covariance-law classification, with the LongA/nondegenerate family as the canonical local carrier, not a pointwise sign theorem for every sub-scope.

---

*Prime Mesh Theory - RH Programme*
