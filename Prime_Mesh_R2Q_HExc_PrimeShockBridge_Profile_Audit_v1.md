# Prime Mesh R2Q - H-Exc PrimeShockBridge Profile Audit v1

**Status:** PASS

## Purpose

This audit profiles the dominant H-Exc component

```text
B_prime(t)=sum_{y<n<=t} Lambda(n)-((t-y)/h)sum_{y<n<=y+h} Lambda(n)
```

with theorem-facing target:

```text
p_star >= P0 => ||B_prime||^2_{2,T_J}/h <= 65.
```

## Summary

```text
rows = 1468
post_P0_rows = 142
post_P0_K_prime_max = 64.2498859117116
post_P0_C_prime_max = 8.015602654305638
post_P0_K_prime_above_65_count = 0
post_P0_lambda_event_count_max = 7420
post_P0_prime_event_count_max = 7420
post_P0_prime_power_event_count_max = 0
post_P0_lambda_weight_sum_max = 150032.93169378873
post_P0_lambda_weight_sq_sum_max = 3033676.629773508
post_P0_lambda_event_weight_max = 20.220547809286526
post_P0_max_lambda_gap_max = 156
post_P0_sample_count_max = 41
post_P0_sample_count_over_h_max = 2.0
post_P0_effective_support_frac_max = 0.49999999975471576
post_P0_effective_support_frac_mean = 0.030813845621177914
post_P0_single_shock_bound_pass_count = 22
post_P0_event_l2_bound_pass_count = 0
post_P0_total_mass_bound_pass_count = 0
best_proof_route_candidate = sampled_bridge_direct
pass_primeshock_bridge_profile_empirical = True
```

## Interpretation

The clean route is the direct sampled prime-shock bridge bound: the audited `K_prime` itself stays below 65 post-P0, while crude event-count bounds are too loose.

## Files

- `script`: `prime_mesh_r2q_hexc_primeshock_bridge_profile_audit.py`
- `summary`: `prime_mesh_r2q_hexc_primeshock_bridge_profile_summary.csv`
- `rows`: `prime_mesh_r2q_hexc_primeshock_bridge_profile_rows.csv`
- `by_regime`: `prime_mesh_r2q_hexc_primeshock_bridge_profile_by_regime.csv`
- `extremes`: `prime_mesh_r2q_hexc_primeshock_bridge_profile_extremes.csv`
- `failures`: `prime_mesh_r2q_hexc_primeshock_bridge_profile_failures.csv`
- `note`: `Prime_Mesh_R2Q_HExc_PrimeShockBridge_Profile_Audit_v1.md`
