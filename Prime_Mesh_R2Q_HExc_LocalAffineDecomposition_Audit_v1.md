# Prime Mesh R2Q - H-Exc LocalAffineDecomposition Audit v1

**Status:** empirical pass  
**Date:** 2026-05-09  
**Script:** `prime_mesh_r2q_hexc_local_affine_decomposition_audit.py`

## Target

Identify the structural mechanism behind:

```text
p_star >= P0 => ||D_N - ell_endpoint||_2^2 <= 100h.
```

## Main Results

```text
rows                                      = 1468
path_sample_blocks                        = 1468
blocks_missing_path_samples               = 0
path_reconstruction_ok                    = True

post_P0_rows                              = 142
post_P0_E_end_over_h_max                  = 64.13704142037176
post_P0_C_end_max                         = 8.008560508628985
post_P0_E_end_over_h_above_100_count      = 0
post_P0_C_end_above_10_count              = 0
pass_endpoint_residual_bound              = True

post_P0_endpoint_residual_fraction_max    = 2.4265633807775945e-05
post_P0_affine_capture_fraction_min       = 0.9999757343661922
pass_local_affinity_fraction_strong       = True

post_P0_E_best_over_h_max                 = 29.98033535342825
post_P0_E_gap_over_h_max                  = 43.91930344849154
post_P0_E_best_plus_gap_over_h_max        = 64.13704142039329
endpoint_vs_best_split_clean_flag         = True

post_P0_ratio_E_end_to_h2_dR_sq_max       = 0.03703703703703704
post_P0_ratio_E_end_to_h4_ddR_sq_max      = 0.0013717421124828536
curvature_route_plausible_flag            = True

post_P0_shape_template_count_tol_0p5      = 25
post_P0_shape_template_count_tol_1p0      = 25
template_route_plausible_flag             = False

best_proof_route_candidate                = local_affinity_fraction
local_affine_decomposition_failures       = 0
pass_hexc_local_affine_decomposition_empirical = True
```

## Component Correlations

```text
corr(E_end/h, Q_delta_D) = 0.08591439351916125
corr(E_end/h, Q_exc)     = 0.8802713912442139
corr(E_end/h, epsilon)   = nan
corr(E_end/h, Q_R2Q)     = 0.12369263213148182
corr(E_end/h, kappa_L2)  = 0.056555973045118925
```

## Interpretation

The endpoint residual bound remains clean, and the strongest structural explanation is:

```text
local_affinity_fraction
```

Reason:

```text
endpoint affine interpolation captures at least 99.9975% of D_N path energy post-P0, and residual energy stays below 100h.
```

Recommended theorem form:

```text
local_affinity_energy_capture plus endpoint residual budget
```

## Recommended Next File

```text
Prime_Mesh_R2Q_HExc_LocalAffinity_EnergyCapture_Theorem_Target_v1.md
```
