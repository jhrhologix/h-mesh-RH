# Prime Mesh R2Q - H-Exc PrimeShockBridge KernelGram Audit v1

**Status:** PASS

## Purpose

This audit represents the sampled prime-shock bridge as a kernel quadratic form:

```text
B_prime(r)=sum_i w_i k_ai(r),  k_a(r)=1_{a<=r}-r/h
E_prime=w^T G w=||K w||^2.
```

## Summary

```text
rows = 1468
post_P0_rows = 142
post_P0_K_prime_max = 64.24988591171167
post_P0_K_prime_above_65_count = 0
post_P0_gram_reconstruction_error_max = 3.4415279515087605e-08
post_P0_spectral_bound_over_h_max = 119516.0554431092
post_P0_spectral_tightness_max = 55577.29324731847
post_P0_spectral_tightness_median = 131.67328350883045
post_P0_rayleigh_over_h_max = 0.06250000001022005
post_P0_top_eigenvalue_over_h_max = 0.3333333333333333
post_P0_top_eigenvector_alignment_max = 0.2897841487666825
post_P0_effective_rank_min = 0.0
post_P0_effective_rank_median = 0.0
best_proof_route_candidate = rayleigh_structural_bound
pass_kernelgram_empirical = True
```

## Interpretation

The most promising route is a Rayleigh-quotient structural bound for the actual Lambda weight vector on the Route-A grid.

## Files

- `script`: `prime_mesh_r2q_hexc_primeshock_kernelgram_audit.py`
- `summary`: `prime_mesh_r2q_hexc_primeshock_kernelgram_summary.csv`
- `rows`: `prime_mesh_r2q_hexc_primeshock_kernelgram_rows.csv`
- `by_regime`: `prime_mesh_r2q_hexc_primeshock_kernelgram_by_regime.csv`
- `extremes`: `prime_mesh_r2q_hexc_primeshock_kernelgram_extremes.csv`
- `failures`: `prime_mesh_r2q_hexc_primeshock_kernelgram_failures.csv`
- `note`: `Prime_Mesh_R2Q_HExc_PrimeShockBridge_KernelGram_Audit_v1.md`
