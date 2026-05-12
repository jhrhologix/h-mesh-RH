# Prime Mesh R2Q - H-Exc VarianceProxy Audit v1
**Status:** PASS  
**Generated:** 2026-05-09T21:21:46.809887+00:00  

## Executive Verdict
The H-Exc absolute bridge-excursion cap passes: `Q_exc_max = 0.0205672364492246` and no rows exceed `0.025`.
The available variance proxy is constant across rows, so the audit is classified as `global_V2_only`. This supports a global variance explanation, not a row-level `V2(J)` theorem yet.

## Inputs Used
- `primary_rows`: `prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv`
- `audit_level`: `global_V2_only`
- `V2_global`: `0.0004263792000474`
- `sqrt_V2_global`: `0.0206489515483821`
- `row_sqrt_V2_distinct_values`: `0`

## Absolute H-Exc Cap
- `rows`: `1468`
- `Q_exc_available_rows`: `1468`
- `Q_exc_max`: `0.0205672364492246`
- `Q_exc_above_0p025_count`: `0`
- `pass_absolute_Q_exc_cap`: `True`

## Variance Proxy Ratio
- `V2_global`: `0.0004263792000474`
- `sqrt_V2_global`: `0.0206489515483821`
- `Q_exc_max_over_sqrt_V2_global`: `0.9960426514166575`
- `C_V_observed`: `0.9960426514166575`
- `C_V_theorem_recommended`: `1.05`
- `variance_explanation_status`: `global_proxy_supported_not_row_level`

## Threshold And Forbidden Safety
- `threshold_relevant_rows`: `3`
- `threshold_relevant_Q_exc_max`: `0.0037875901851982`
- `threshold_relevant_ratio_max`: `0.18342772398509347`
- `forbidden_rows`: `1`
- `forbidden_Q_exc_max`: `0.0022301154184481`
- `forbidden_ratio_max`: `0.10800138753886686`

## Regime Decomposition
| row_regime                  |   rows |   Q_exc_max |   Q_exc_mean |   Q_exc_q95 |   ratio_max |   ratio_q95 |   Q_exc_above_0p025_count |   missing_Q_exc_rows |
|:----------------------------|-------:|------------:|-------------:|------------:|------------:|------------:|--------------------------:|---------------------:|
| finite_negative             |    124 |  0.0128662  |  0.00613266  | 0.0103822   |    0.623092 | 0.502795    |                         0 |                    0 |
| finite_positive             |   1200 |  0.0205672  |  0.000745393 | 0.0099539   |    0.996043 | 0.482054    |                         0 |                    0 |
| forbidden_negative          |      1 |  0.00223012 |  0.00223012  | 0.00223012  |    0.108001 | 0.108001    |                         0 |                    0 |
| post_P0_negative_tail       |     21 |  0.00692146 |  0.00494531  | 0.00673342  |    0.335197 | 0.32609     |                         0 |                    0 |
| post_P0_positive_tail       |    120 |  0.0122978  |  0.000258572 | 8.89766e-15 |    0.595564 | 4.30901e-13 |                         0 |                    0 |
| threshold_relevant_negative |      2 |  0.00378759 |  0.0026287   | 0.0036717   |    0.183428 | 0.177815    |                         0 |                    0 |

## Failures
No failures were found.

## Theorem Interpretation
The proof-facing absolute statement `Q_exc <= 0.025` is empirically supported on the full audited inventory. The variance explanation is currently global: `Q_exc_max / sqrt(V2_global) < 1`, with `sqrt(V2_global)` nearly matching the observed maximum. A row-level `V2(J)` theorem should not be claimed until a genuinely varying local variance field is exported or derived.

## Recommended Next File
`Prime_Mesh_R2Q_HExc_GlobalVarianceProxy_Closure_Update_v1.md`
