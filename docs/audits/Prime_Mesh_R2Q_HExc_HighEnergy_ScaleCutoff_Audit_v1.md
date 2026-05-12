# Prime Mesh R2Q - H-Exc HighEnergy ScaleCutoff Audit v1
**Generated:** 2026-05-09T22:37:25.331871+00:00  
**Status:** PASS  

## Executive Verdict
The strict `p_star >= P0 => Q_energy_L2 <= 0.025` cutoff is `True`. Post-P0 p-star rows have max energy `0.0195894059694182` with `0` over-cap rows.
High-energy rows: `10`. Threshold high-energy rows: `0`. Forbidden high-energy rows: `0`. Surviving high-energy rows: `0`.

## Cutoff Tests
- `post_P0_pstar_rows`: `142`
- `post_P0_pstar_Q_energy_L2_max`: `0.0195894059694182`
- `post_P0_pstar_energy_above_0p025_count`: `0`
- `pass_pstar_scale_cutoff`: `True`
- `post_P0_x_Q_energy_L2_max`: `0.0195894059694182`
- `pass_x_scale_cutoff`: `True`
- `post_P0_y_Q_energy_L2_max`: `0.0195894059694182`
- `pass_y_scale_cutoff`: `True`

## High-Energy Harmlessness
- `high_energy_finite_certified_count`: `10`
- `high_energy_not_finite_certified_count`: `0`
- `pass_high_energy_finite_certified`: `True`
- `pass_high_energy_threshold_safe`: `True`
- `pass_high_energy_non_survival`: `True`
- `threshold_relevant_Q_energy_L2_max`: `0.0077023825323383`
- `forbidden_Q_energy_L2_max`: `0.0056973529810874`
- `threshold_energy_margin_to_0p025`: `0.017297617467661702`
- `forbidden_energy_margin_to_0p025`: `0.0193026470189126`

## Best Symbolic Rule
- `best_symbolic_rule`: `p_star <= 3.03868e+07`
- `best_symbolic_rule_misses`: `0`
- `best_symbolic_rule_threshold_false_positives`: `0`
- `best_symbolic_rule_forbidden_false_positives`: `0`
- `best_symbolic_rule_surviving_false_positives`: `0`

## Failures
No scale-cutoff/high-energy harmlessness failures were found.

## Recommended Next File
`Prime_Mesh_R2Q_HExc_HighEnergy_ScaleCutoff_Theorem_Target_v1.md`
