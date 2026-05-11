# Prime Mesh R2Q - H-Exc PrimeShockBridge SampleGridStructure Audit v1

**Status:** PASS

## Purpose

This audit inspects the SR11/H-Exc sample grid behind the sampled prime-shock bridge bound:

```text
p_star >= P0 => ||B_prime||^2_{2,T_J}/h <= 65.
```

It compares sampled-grid energy to the optional full integer-grid energy and profiles event/sample alignment.

## Summary

```text
rows = 1468
post_P0_rows = 142
post_P0_K_sampled_max = 64.2498859117116
post_P0_K_sampled_above_65_count = 0
post_P0_K_full_max = 52989.54013889719
post_P0_full_to_sampled_energy_ratio_max = 24641.168087593134
post_P0_full_to_sampled_absmax_ratio_max = 2.510777681109823
post_P0_sample_count_max = 41
post_P0_sample_offset_gap_max = 43800
post_P0_sample_count_over_h_max = 2.0
post_P0_event_to_sample_alignment_score_min = 0.003165485405860318
post_P0_event_to_sample_alignment_score_mean = 0.8869136466733594
post_P0_nearest_sample_distance_to_event_max = 21878.0
post_P0_samples_on_event_count_max = 8
post_P0_samples_between_events_count_max = 39
lifting_plausible_empirical = False
sampled_only_warning = True
best_theorem_form_recommended = sampled_grid_only_with_no_full_lifting
pass_samplegrid_structure_empirical = True
```

## Interpretation

The bound is clean on the SR11/H-Exc sampled grid, but the full integer-grid energy is much larger. A full-grid lifting lemma is not supported by this audit; the theorem should remain sampled-grid unless a different lifting mechanism is supplied.

## Files

- `script`: `prime_mesh_r2q_hexc_primeshock_samplegrid_structure_audit.py`
- `summary`: `prime_mesh_r2q_hexc_primeshock_samplegrid_structure_summary.csv`
- `rows`: `prime_mesh_r2q_hexc_primeshock_samplegrid_structure_rows.csv`
- `by_regime`: `prime_mesh_r2q_hexc_primeshock_samplegrid_structure_by_regime.csv`
- `extremes`: `prime_mesh_r2q_hexc_primeshock_samplegrid_structure_extremes.csv`
- `failures`: `prime_mesh_r2q_hexc_primeshock_samplegrid_structure_failures.csv`
- `note`: `Prime_Mesh_R2Q_HExc_PrimeShockBridge_SampleGridStructure_Audit_v1.md`
