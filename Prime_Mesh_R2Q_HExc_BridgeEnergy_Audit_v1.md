# Prime Mesh R2Q - H-Exc BridgeEnergy Audit v1
**Generated:** 2026-05-09T21:36:07.797473+00:00  
**Status:** PASS  

## Executive Verdict
The absolute bridge-excursion cap remains clean: `Q_exc_max = 0.0205672364492246` with `0` rows above `0.025`.
Row-level bridge-energy coverage is partial: `40` of `1468` rows have path samples. The resulting variance mode is `partial_row_level_energy_available`.

## Bridge Energy Availability
- `bridge_samples_available_rows`: `40`
- `bridge_samples_missing_rows`: `1428`
- `bridge_energy_available_rows`: `40`
- `bridge_energy_missing_rows`: `1428`
- `threshold_relevant_bridge_energy_missing_count`: `0`
- `forbidden_bridge_energy_missing_count`: `0`

## Energy Maximal Candidate
- `Q_energy_rms_min`: `0.0005591881416907784`
- `Q_energy_rms_max`: `0.010160864897962174`
- `Q_energy_rms_mean`: `0.003155585955741569`
- `Q_exc_over_Q_energy_rms_max`: `5.135749976105505`
- `Q_exc_over_Q_energy_rms_q95`: `4.356893827137932`
- `lowest_Cmax_energy_pass`: `10`
- `pass_energy_maximal_candidate`: `True`

## Global V2 Reference
- `sqrt_V2_global`: `0.0206489515483821`
- `Q_exc_max_over_sqrt_V2_global`: `0.9960426514166575`

## Regime Decomposition
| row_regime                  |   rows |   Q_exc_max |   Q_exc_mean |   bridge_energy_available_rows |   Q_energy_rms_max |   Q_exc_over_Q_energy_rms_max |   Q_exc_above_0p025_count |
|:----------------------------|-------:|------------:|-------------:|-------------------------------:|-------------------:|------------------------------:|--------------------------:|
| finite_negative             |    124 |  0.0128662  |  0.00613266  |                             26 |        0.00615492  |                       5.13575 |                         0 |
| finite_positive             |   1200 |  0.0205672  |  0.000745393 |                              8 |        0.0101609   |                       2.72862 |                         0 |
| forbidden_negative          |      1 |  0.00223012 |  0.00223012  |                              1 |        0.000889777 |                       2.50638 |                         0 |
| post_P0_negative_tail       |     21 |  0.00692146 |  0.00494531  |                              3 |        0.00124416  |                       4.25814 |                         0 |
| post_P0_positive_tail       |    120 |  0.0122978  |  0.000258572 |                              0 |      nan           |                     nan       |                         0 |
| threshold_relevant_negative |      2 |  0.00378759 |  0.0026287   |                              2 |        0.00120291  |                       3.14869 |                         0 |

## Failures
No absolute-cap failures were found.

## Interpretation
This audit does not justify a full row-level bridge-energy theorem because most rows do not export path samples. It does confirm that the absolute `Q_exc <= 0.025` cap remains intact and that partial path samples can be converted into bridge-energy quantities. The next proof-facing move should be an export patch that records row-level bridge samples or precomputed bridge energy for every FCL-compatible row.

## Recommended Next File
`Prime_Mesh_R2Q_HExc_BridgeEnergy_Export_Patch_Spec_v1.md`
