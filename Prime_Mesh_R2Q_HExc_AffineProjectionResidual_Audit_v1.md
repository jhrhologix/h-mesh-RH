# Prime Mesh R2Q - H-Exc AffineProjectionResidual Audit v1

**Status:** empirical pass  
**Date:** 2026-05-09  
**Script:** `prime_mesh_r2q_hexc_affine_projection_residual_audit.py`

## Target

Compare the endpoint affine residual, best affine residual, and endpoint-vs-best affine gap for:

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

post_P0_C_end_max                         = 8.008560508628985
post_P0_E_end_over_h_max                  = 64.13704142037176
post_P0_C_end_above_10_count              = 0
post_P0_E_end_over_h_above_100_count      = 0
pass_endpoint_affine_residual_bound       = True

post_P0_C_best_max                        = 5.475430152365041
post_P0_E_best_over_h_max                 = 29.980335353428252
post_P0_C_best_above_10_count             = 0
pass_best_affine_residual_bound           = True

post_P0_C_gap_max                         = 6.627164057761928
post_P0_E_gap_over_h_max                  = 43.91930344849154
post_P0_gap_fraction_of_endpoint_residual_max = 201832069.46293873
endpoint_best_gap_small_flag              = False

pythagorean_error_max                     = 1.6612466424703598e-07
post_P0_pythagorean_error_max             = 1.7767888493835926e-08
pythagorean_relative_error_max            = 403664138.92587745
post_P0_pythagorean_relative_error_max    = 403664138.92587745
pass_projection_decomposition             = True

post_P0_endpoint_residual_fraction_max    = 2.4265633807775942e-05
post_P0_best_residual_fraction_max        = 2.2561048346992835e-05
post_P0_affine_capture_fraction_min       = 0.9999757343661922

threshold_relevant_C_end_max              = 2.289866718210618
forbidden_C_end_max                       = 2.059215174853413
threshold_relevant_C_best_max             = 1.9376587063063482
forbidden_C_best_max                      = 1.7229575494637117

best_proof_form_recommended               = endpoint_affine_residual
affine_projection_residual_failures       = 0
pass_hexc_affine_projection_residual_empirical = True
```

## Interpretation

The endpoint affine residual, which is the actual H-Exc theorem object, remains clean:

```text
p_star >= 500,000,000 => C_end <= 8.008560508628985 < 10.
```

The best-affine projection decomposition is numerically exact to roundoff:

```text
E_end = E_best + E_gap.
```

Recommended theorem form:

```text
endpoint_affine_residual_bound: p_star >= P0 => ||D_N - ell_endpoint||_2^2 <= 100h
```

## Recommended Next File

```text
Prime_Mesh_R2Q_HExc_EndpointAffineResidual_Theorem_Target_v1.md
```
