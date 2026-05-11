# Prime Mesh R2Q - H-Exc BridgeShape/Curvature Audit v1

**Status:** empirical pass  
**Date:** 2026-05-09  
**Script:** `prime_mesh_r2q_hexc_bridgeshape_curvature_audit.py`

## Target

Profile the bridge path

```text
B_J(t)=D_N(t)-ell_J(t)
```

to choose the best proof mechanism for:

```text
p_star >= P0 => ||B_J||_2^2 <= 100 h.
```

## Main Results

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
pass_direct_bridge_envelope               = True

post_P0_B_abs_max                         = 311.51713925927834
post_P0_B_abs_max_above_10_count          = 23
post_P0_amplitude_route_bound_value_max   = 320.348161190922
post_P0_amplitude_route_fail_count        = 17
pass_amplitude_route_candidate            = False

post_P0_dB_L2_max                         = 583.7179531620146
post_P0_ddB_L2_max                        = 818.8316415567805
post_P0_ratio_B_L2_to_ddB_L2_max          = 2.0747631057556077
post_P0_ratio_B_L2_to_h_ddB_L2_max        = 0.11111111111111112

post_P0_bridge_energy_fraction_max        = 2.4265633807775952e-05
post_P0_kappa_L2_max                      = 0.7382422708040317
post_P0_effective_support_frac_min        = 0.0

threshold_relevant_C_bridge_max           = 2.2898667182106016
forbidden_C_bridge_max                    = 2.059215174853389
threshold_relevant_B_abs_max              = 667.0135370697717
forbidden_B_abs_max                       = 667.0135370697717

best_proof_route_candidate                = projection_residual_route
direct_bridge_shape_failures              = 0
pass_hexc_bridgeshape_curvature_empirical = True
```

## Interpretation

The direct bridge envelope remains clean:

```text
p_star >= 500,000,000 => C_bridge <= 8.008560508629008 < 10.
```

The simplest route suggested by this audit is:

```text
projection_residual_route
```

Reason:

```text
affine subtraction leaves a uniformly tiny residual energy fraction post-P0.
```

## Recommended Next File

```text
Prime_Mesh_R2Q_HExc_AffineProjectionResidual_Theorem_Target_v1.md
```
