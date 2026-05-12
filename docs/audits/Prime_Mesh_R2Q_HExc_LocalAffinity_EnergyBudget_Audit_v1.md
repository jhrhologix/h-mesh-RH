# Prime Mesh R2Q - H-Exc LocalAffinity EnergyBudget Audit v1

**Status:** empirical pass  
**Date:** 2026-05-09  
**Script:** `prime_mesh_r2q_hexc_local_affinity_energybudget_audit.py`

## Target

Test the local-affinity energy budget:

```text
eta_aff = ||D_N - ell_endpoint||_2^2 / ||D_N||_2^2
K_D     = ||D_N||_2^2 / h
K_R     = ||D_N - ell_endpoint||_2^2 / h
```

with:

```text
K_R = eta_aff * K_D.
```

## Main Results

```text
rows                                      = 1468
path_sample_blocks                        = 1468
blocks_missing_path_samples               = 0
path_reconstruction_ok                    = True

post_P0_rows                              = 142

product_reconstruction_error_max          = 7.105427357601002e-15
post_P0_product_reconstruction_error_max  = 7.105427357601002e-15
pass_product_identity                     = True

post_P0_K_R_max                           = 64.13704142037176
post_P0_K_R_above_100_count               = 0
pass_endpoint_residual_budget             = True

post_P0_eta_aff_max                       = 2.426563380777594e-05
post_P0_eta_aff_q95                       = 9.480056936638822e-06
post_P0_eta_aff_q99                       = 2.251319445928661e-05
recommended_eta0                          = nan
pass_eta_aff_cap                          = False

post_P0_K_D_max                           = 316352183.9207044
post_P0_K_D_q95                           = 309962175.02075917
post_P0_K_D_q99                           = 315264958.53195125
recommended_K0                            = nan
pass_K_D_cap                              = False

recommended_eta0_times_K0                 = nan
pass_two_part_energy_budget               = False

post_P0_eta_times_KD_max                  = 64.13704142037176
post_P0_eta_times_KD_above_100_count      = 0
pass_direct_product_budget                = True

threshold_relevant_eta_times_KD_max       = 5.243489587168667
forbidden_eta_times_KD_max                = 4.240367136346573
threshold_relevant_K_R_max                = 5.243489587168667
forbidden_K_R_max                         = 4.240367136346573

best_theorem_form_recommended             = direct_local_affinity_product
local_affinity_energybudget_failures      = 0
pass_hexc_local_affinity_energybudget_empirical = True
```

## Interpretation

The direct product budget closes, but the attempted separate constants do not:

```text
max_post_P0 eta_aff*K_D = 64.13704142037176 <= 100
max_post_P0 eta_aff     = 2.426563380777594e-05
max_post_P0 K_D         = 316352183.9207044
```

So the proof-facing object should stay the direct product / endpoint residual bound, with local-affinity used as explanatory structure rather than as two independent caps.

Recommended theorem form:

```text
direct_local_affinity_product: eta_aff*K_D <= 100
```

## Recommended Next File

```text
Prime_Mesh_R2Q_HExc_EndpointAffineResidual_Formal_Proof_Draft_v1.md
```
