# Prime Mesh R2Q - H-Exc PrimeShockBridge RayleighWeight Audit v1

**Status:** PASS

## Purpose

This audit tests the factorization:

```text
K_prime = (w^T G w / (h ||w||_2^2)) * ||w||_2^2 = rho_J * W_J.
```

## Summary

```text
rows = 1468
post_P0_rows = 142
post_P0_K_prime_max = 64.24988591171167
post_P0_rayleigh_over_h_max = 0.06250000001022
post_P0_weight_l2_sq_max = 3033676.629773508
post_P0_product_reconstruction_error_max = 8.697043085703626e-12
independent_constants_close = False
best_independent_rho = nan
best_independent_W0 = nan
best_independent_product = nan
direct_product_max = 64.24988591171059
direct_product_margin_to_65 = 0.7501140882894077
best_theorem_form_recommended = direct_rayleigh_product_bound
pass_rayleighweight_empirical = True
```

## Interpretation

Independent constants do not close cleanly: the worst Rayleigh factor and worst weight energy occur in different regimes, and their independent product is too large. The proof-facing theorem should use a direct Rayleigh-product bound.

## Files

- `script`: `prime_mesh_r2q_hexc_primeshock_rayleighweight_audit.py`
- `summary`: `prime_mesh_r2q_hexc_primeshock_rayleighweight_summary.csv`
- `rows`: `prime_mesh_r2q_hexc_primeshock_rayleighweight_rows.csv`
- `constants`: `prime_mesh_r2q_hexc_primeshock_rayleighweight_constants.csv`
- `by_regime`: `prime_mesh_r2q_hexc_primeshock_rayleighweight_by_regime.csv`
- `extremes`: `prime_mesh_r2q_hexc_primeshock_rayleighweight_extremes.csv`
- `failures`: `prime_mesh_r2q_hexc_primeshock_rayleighweight_failures.csv`
- `note`: `Prime_Mesh_R2Q_HExc_PrimeShockBridge_RayleighWeight_Audit_v1.md`
