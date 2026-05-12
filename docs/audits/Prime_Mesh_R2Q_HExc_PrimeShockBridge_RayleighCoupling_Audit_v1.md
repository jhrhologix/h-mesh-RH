# Prime Mesh R2Q - H-Exc PrimeShockBridge RayleighCoupling Audit v1

**Status:** PASS

## Purpose

This audit profiles the coupling

```text
K_prime = rho_J W_J
rho_J = w^T G_J w / (h ||w||_2^2)
W_J = ||w||_2^2.
```

## Summary

```text
rows = 1468
post_P0_rows = 142
post_P0_K_prime_max = 64.24988591171059
post_P0_K_prime_above_65_count = 0
post_P0_product_margin_min = 0.7501140882894077
post_P0_corr_rho_W = -0.022268635156078374
post_P0_corr_logrho_logW = -0.9713786595637668
post_P0_spearman_rho_W = 0.6479036094678277
post_P0_W_large_rows = 22
post_P0_W_large_rho_max = 0.0044902565189875
post_P0_rho_large_rows = 1
post_P0_rho_large_W_max = 817.7394705925482
regime_split_candidate = two_regime
best_theorem_form_recommended = two_regime_coupling
pass_rayleighcoupling_empirical = True
```

## Interpretation

A two-regime coupling theorem is supported: high weight forces tiny Rayleigh, while high Rayleigh occurs only at low weight.

## Files

- `script`: `prime_mesh_r2q_hexc_primeshock_rayleighcoupling_audit.py`
- `summary`: `prime_mesh_r2q_hexc_primeshock_rayleighcoupling_summary.csv`
- `rows`: `prime_mesh_r2q_hexc_primeshock_rayleighcoupling_rows.csv`
- `W_envelope`: `prime_mesh_r2q_hexc_primeshock_rayleighcoupling_W_envelope.csv`
- `rho_envelope`: `prime_mesh_r2q_hexc_primeshock_rayleighcoupling_rho_envelope.csv`
- `split_candidates`: `prime_mesh_r2q_hexc_primeshock_rayleighcoupling_split_candidates.csv`
- `by_regime`: `prime_mesh_r2q_hexc_primeshock_rayleighcoupling_by_regime.csv`
- `extremes`: `prime_mesh_r2q_hexc_primeshock_rayleighcoupling_extremes.csv`
- `failures`: `prime_mesh_r2q_hexc_primeshock_rayleighcoupling_failures.csv`
- `note`: `Prime_Mesh_R2Q_HExc_PrimeShockBridge_RayleighCoupling_Audit_v1.md`
