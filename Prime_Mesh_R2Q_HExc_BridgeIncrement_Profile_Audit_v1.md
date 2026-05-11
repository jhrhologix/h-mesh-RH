# Prime Mesh R2Q - H-Exc BridgeIncrement Profile Audit v1
**Generated:** 2026-05-09T22:53:10.382258+00:00  
**Status:** PASS  

## Executive Verdict
Path reconstruction passes with `B_L2_recompute_error_max = 1.1368683772161603e-13`. Post-P0 `C_bridge_max = 8.008560508629008`.

## Increment Route
- `R_inc_max`: `1.91757864004104`
- `post_P0_R_inc_max`: `1.4609419049190016`
- `recommended_C_inc`: `2`
- `recommended_C_inc_post_P0`: `2`
- `A_centered_sqsum_over_sqrt_h_max`: `265.38120455170895`
- `post_P0_A_centered_sqsum_over_sqrt_h_max`: `115.82408797947872`
- `C_inc_times_A_global`: `530.7624091034179`
- `C_inc_times_A_post_P0`: `231.64817595895744`
- `pass_increment_square_sum_route`: `False`

## Direct Bridge Constant
- `C_bridge_max`: `8.580752479596955`
- `post_P0_C_bridge_max`: `8.008560508629008`
- `post_P0_C_bridge_above_10_count`: `0`
- `pass_post_P0_C_bridge_le_10`: `True`
- `threshold_relevant_C_bridge_max`: `2.2898667182106016`
- `forbidden_C_bridge_max`: `2.059215174853389`

## Failures
No bridge-increment profile failures were found.

## Recommended Next File
`Prime_Mesh_R2Q_HExc_BridgeConstant_Formal_Proof_Draft_v1.md`
