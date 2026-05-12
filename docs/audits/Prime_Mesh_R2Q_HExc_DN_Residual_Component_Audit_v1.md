# Prime Mesh R2Q - H-Exc D_N Residual Component Audit v1

**Status:** PASS

## Purpose

This audit decomposes the sampled H-Exc bridge residual

```text
B_J(t)=D_N(t)-ell_J(t)=B_comp(t)-B_prime(t)
```

using the SR11 increment definition

```text
d_N(n)=C_N E_mod(n)-Lambda(n).
```

## Main Results

```text
rows = 1468
post_P0_rows = 142
C_N_used = 1.29340026
path_reconstruction_abs_error_max = 1.7241982277482748e-06
post_P0_K_total_max = 64.13704142037267
post_P0_C_total_max = 8.008560508629042
post_P0_K_unreduced_max = 64.2506254824152
post_P0_K_comp_max = 0.00774483441003735
post_P0_K_prime_max = 64.2498859117116
post_P0_cancellation_fraction_min = -0.016149220199091152
post_P0_cancellation_fraction_mean = 0.0015721075171889387
post_P0_cos_comp_prime_mean = -0.05566872372374199
post_P0_source_smallness_rows = 142
post_P0_source_cancellation_rows = 0
post_P0_source_mixed_safe_rows = 0
component_identity_failures = 0
post_P0_component_bound_failures = 0
best_proof_source_post_P0 = smallness_driven
pass_hexc_dn_residual_component_empirical = True
```

## Interpretation

The post-P0 H-Exc endpoint-residual bound is empirically component-smallness driven:
both centered composite response and centered prime shock remain small enough that their
unreduced energy already stays inside the `100h` budget.

## Files

- `script`: `prime_mesh_r2q_hexc_dn_residual_component_audit.py`
- `summary`: `prime_mesh_r2q_hexc_dn_residual_component_summary.csv`
- `rows`: `prime_mesh_r2q_hexc_dn_residual_component_rows.csv`
- `by_regime`: `prime_mesh_r2q_hexc_dn_residual_component_by_regime.csv`
- `extremes`: `prime_mesh_r2q_hexc_dn_residual_component_extremes.csv`
- `failures`: `prime_mesh_r2q_hexc_dn_residual_component_failures.csv`
- `note`: `Prime_Mesh_R2Q_HExc_DN_Residual_Component_Audit_v1.md`
