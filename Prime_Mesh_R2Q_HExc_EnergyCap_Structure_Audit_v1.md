# Prime Mesh R2Q - H-Exc EnergyCap Structure Audit v1
**Generated:** 2026-05-09T21:51:14.536204+00:00  
**Status:** PASS  

## Executive Verdict
`Q_exc <= 0.025` remains clean: `Q_exc_max = 0.0205672364492246`, `Q_exc_above_0p025_count = 0`.
`Q_energy_L2_max = 0.036413013628854`, so the raw L2 energy cap at `0.025` is not globally true. High-energy rows are classified separately.

## High-Energy Classification
- `energy_L2_above_0p025_count`: `10`
- `energy_L2_above_0p03_count`: `2`
- `energy_L2_above_0p04_count`: `0`
- `energy_L2_above_0p025_threshold_relevant_count`: `0`
- `energy_L2_above_0p025_forbidden_count`: `0`
- `energy_L2_above_0p025_positive_count`: `4`
- `energy_L2_above_0p025_negative_count`: `6`
- `energy_L2_above_0p025_repaid_count`: `0`
- `energy_L2_above_0p025_finite_certified_count`: `10`
- `high_energy_surviving_unrepaid_count`: `0`

## Concentration Ratio
- `conc_ratio_max`: `0.8120333708824421`
- `conc_ratio_mean`: `0.5364768030232963`
- `conc_ratio_q95`: `0.7100398405978393`
- `conc_ratio_q99`: `0.7322082430970421`
- `conc_ratio_high_energy_max`: `0.70711576075991`
- `conc_ratio_high_energy_q95`: `0.6925379659915168`

## Threshold And Forbidden Safety
- `threshold_relevant_energy_L2_max`: `0.0077023825323383`
- `threshold_relevant_energy_L2_above_0p025_count`: `0`
- `forbidden_energy_L2_max`: `0.0056973529810874`
- `forbidden_energy_L2_above_0p025_count`: `0`

## Failures
No harmful high-energy failures were found.

## Theorem Interpretation
The statement `Q_energy_L2 <= 0.025` is false globally. The correct H-Exc structure is: the excursion itself remains capped, while over-cap energy rows must be treated by spread/concentration and channel harmlessness. This audit provides the classification artifact for that split.

## Recommended Next File
`Prime_Mesh_R2Q_HExc_EnergyCap_Structure_Closure_Update_v1.md`
