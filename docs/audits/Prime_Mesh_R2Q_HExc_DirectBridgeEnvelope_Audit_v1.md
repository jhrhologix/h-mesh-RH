# Prime Mesh R2Q - H-Exc DirectBridgeEnvelope Audit v1

**Status:** empirical pass  
**Date:** 2026-05-09  
**Script:** `prime_mesh_r2q_hexc_direct_bridge_envelope_audit.py`

## Target

This audit profiles the direct path-level bridge envelope

```text
B_J(t) = D_N(t) - ell_J(t)
```

and tests the theorem-facing post-`P0` bound:

```text
p_star >= P0 => ||B_J||_2 <= 10 sqrt(h)
```

equivalently:

```text
C_bridge = ||B_J||_2 / sqrt(h) <= 10.
```

## Summary

```text
rows                                      = 1468
path_sample_blocks                        = 1468
blocks_missing_path_samples               = 0
path_reconstruction_ok                    = True

post_P0_rows                              = 142
post_P0_C_bridge_max                      = 8.008560508629008
post_P0_C_bridge_sq_max                   = 64.13704142037213
post_P0_C_bridge_above_10_count           = 0
post_P0_C_bridge_sq_above_100_count       = 0
pass_direct_bridgeconstant_bound          = True

C_bridge_max                              = 8.580752479596955
C_bridge_sq_max                           = 73.62931311610929
C_bridge_q95                              = 4.950687126456709
C_bridge_q99                              = 6.655962344149671

threshold_relevant_C_bridge_max           = 2.2898667182106016
threshold_relevant_C_bridge_sq_max        = 5.2434895871685905
forbidden_C_bridge_max                    = 2.059215174853389
forbidden_C_bridge_sq_max                 = 4.240367136346474

B_L2_recompute_error_max                  = 1.1368683772161603e-13
C_bridge_recompute_error_max              = 4.04121180963557e-14

kappa_L2_max                              = 0.8120333708824421
post_P0_kappa_L2_max                      = 0.7382422708040356
threshold_relevant_kappa_L2_max           = 0.4917426743343476
forbidden_kappa_L2_max                    = 0.3914300949670945

direct_bridge_envelope_failures           = 0
pass_hexc_direct_bridge_envelope_empirical = True
```

## Interpretation

The direct bridge envelope passes empirically:

```text
p_star >= 500,000,000 => C_bridge <= 8.008560508629008 < 10.
```

Equivalently:

```text
p_star >= 500,000,000 => ||B_J||_2^2 / h <= 64.13704142037213 < 100.
```

The path reconstruction also matches the exported bridge energy to numerical precision, so this audit supports using the direct path-level object rather than the failed centered-increment square-sum route.

## Recommended Next File

```text
Prime_Mesh_R2Q_HExc_DirectBridgeEnvelope_Theorem_Target_v1.md
```
