# Prime Mesh R2Q - H-Exc MaximalConcentration Audit v1
**Generated:** 2026-05-09T21:57:44.170315+00:00  
**Status:** PASS  

## Executive Verdict
The maximal concentration audit passes. `Q_exc_max = 0.0205672364492246`, `kappa_L2_max = 0.8120333708824421`, and high-energy rows do not overlap the dangerous threshold/forbidden channels.

## Core Results
- `Q_exc_above_0p025_count`: `0`
- `energy_L2_above_0p025_count`: `10`
- `energy_L2_above_0p03_count`: `2`
- `kappa_L2_max`: `0.8120333708824421`
- `kappa_L2_q95`: `0.7100398405978393`
- `kappa_L2_q99`: `0.7322082430970421`
- `high_energy_threshold_relevant_count`: `0`
- `high_energy_forbidden_count`: `0`
- `high_energy_finite_certified_count`: `10`
- `high_energy_non_surviving_count`: `10`
- `high_energy_surviving_unrepaid_count`: `0`

## Threshold And Forbidden Safety
- `threshold_relevant_rows`: `3`
- `threshold_relevant_Q_exc_max`: `0.0037875901851982`
- `threshold_relevant_Q_energy_L2_max`: `0.0077023825323383`
- `threshold_relevant_energy_above_0p025_count`: `0`
- `forbidden_rows`: `1`
- `forbidden_Q_exc_max`: `0.0022301154184481`
- `forbidden_Q_energy_L2_max`: `0.0056973529810874`
- `forbidden_energy_above_0p025_count`: `0`

## Regime Decomposition
| row_regime                  |   rows |   Q_exc_max |   Q_energy_L2_max |   kappa_L2_max |   energy_above_0p025_count |   exc_above_0p025_count |   threshold_relevant_rows |   forbidden_rows |   finite_certified_rows |   non_surviving_rows |   failures |
|:----------------------------|-------:|------------:|------------------:|---------------:|---------------------------:|------------------------:|--------------------------:|-----------------:|------------------------:|---------------------:|-----------:|
| finite_negative             |    124 |  0.0128662  |        0.036413   |       0.812033 |                          6 |                       0 |                         0 |                0 |                     124 |                  124 |          0 |
| finite_positive             |   1200 |  0.0205672  |        0.0304826  |       0.710755 |                          4 |                       0 |                         0 |                0 |                    1200 |                 1200 |          0 |
| forbidden_negative          |      1 |  0.00223012 |        0.00569735 |       0.39143  |                          0 |                       0 |                         1 |                1 |                       1 |                    1 |          0 |
| post_P0_negative_tail       |     21 |  0.00692146 |        0.0195894  |       0.738242 |                          0 |                       0 |                         0 |                0 |                       0 |                   21 |          0 |
| post_P0_positive_tail       |    120 |  0.0122978  |        0.0173299  |       0.709628 |                          0 |                       0 |                         0 |                0 |                       0 |                  120 |          0 |
| threshold_relevant_negative |      2 |  0.00378759 |        0.00770238 |       0.491743 |                          0 |                       0 |                         2 |                0 |                       1 |                    2 |          0 |

## Failures
No maximal-concentration failures were found.

## Theorem Interpretation
The proof-facing form should not assert `Q_energy_L2 <= 0.025` globally. Instead, use the deterministic concentration inequality `Q_exc <= Q_energy_L2`, the empirical/global cap `Q_exc <= 0.025`, and the high-energy classification showing that over-energy rows are non-dangerous/non-surviving in the audited stack.

## Recommended Next File
`Prime_Mesh_R2Q_HExc_MaximalConcentration_Theorem_Target_v1.md`
