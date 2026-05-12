# Prime Mesh R2Q - H-Exc BridgeRigidity Audit

**Document:** `Prime_Mesh_R2Q_HExc_BridgeRigidity_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** H-Exc BridgeRigidity audit - passes

## 1. Executive Verdict

This audit tests:

\[Q_{\rm exc}(J)=\frac{\sup_{t\in J}|D_N(t)-\ell_J(t)|}{\sqrt h\log^2p^*}\le C_{\rm exc}.\]

\[\boxed{\text{Strong H-Exc cap passes: }Q_{\rm exc}\le0.025.}\]

## 2. Inputs Used

- `prime_mesh_r2q_firstcrossing_covering_localization_windows.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv`
- `prime_mesh_r2q_blocksystem_definition_blocks.csv`
- `prime_mesh_r2q_blocksystem_definition_geometry.csv`
- `prime_mesh_r2q_negative_transfer_coordinate_rows.csv`
- `prime_mesh_r2q_b3_block_to_tail_blocks.csv`
- `prime_mesh_r2q_channel_compatibility_rows.csv`
- `prime_mesh_r2q_o2p3_bridge_excursion_intervals.csv`
- `prime_mesh_r2q_endpoint_repayment_compatibility_intervals.csv`
- `prime_mesh_r2q_hexc_v2_shell_variance_summary.csv`
- `prime_mesh_r2q_o2p3_bridge_excursion_summary.csv`
- `prime_mesh_r2q_endpoint_repayment_compatibility_summary.csv`

Optional inputs missing:
- `prime_mesh_r2q_o123_to_mr2_assembly_rows.csv`
- `prime_mesh_r2q_o123_to_mr2_assembly_summary.csv`

Join notes:
- base FCL selected windows used as row inventory
- prime_mesh_r2q_channel_compatibility_rows.csv on ['block_id', 'p_star', 'y', 'h']: 1468->1468
- prime_mesh_r2q_o2p3_bridge_excursion_intervals.csv on ['block_id', 'p_star', 'y', 'h']: 1468->1468
- prime_mesh_r2q_endpoint_repayment_compatibility_intervals.csv on ['block_id', 'p_star', 'y', 'h']: 1468->1468

## 3. Audit Level

`row-level_existing_o2p3_plus_fcl_Qexc`

## 4. Summary

| metric | value |
|---|---:|
| `rows` | 1468 |
| `coordinate_test_rows` | 1468 |
| `post_P0_rows` | 142 |
| `finite_certificate_rows` | 1326 |
| `near_forbidden_rows` | 3 |
| `forbidden_rows` | 1 |
| `C_minus_rows` | 148 |
| `O2_applicable_rows` | 1468 |
| `B3_applicable_rows` | 1468 |
| `Q_exc_available_rows` | 166 |
| `Q_exc_missing_rows` | 1302 |
| `Q_exc_max` | 0.0205672364492246 |
| `Q_exc_mean` | 0.006318694000692473 |
| `Q_exc_q95` | 0.01132508783831245 |
| `Q_exc_q99` | 0.016202783327572565 |
| `near_forbidden_Q_exc_max` | 0.0037875901851982 |
| `C_minus_Q_exc_max` | 0.0128661873649445 |
| `post_P0_Q_exc_max` | 0.0069214615088821 |
| `V2_available_rows` | 1468 |
| `V2_global` | 0.0004263792000474 |
| `sqrt_V2_global` | 0.0206489515483821 |
| `Q_exc_max_over_sqrt_V2_global` | 0.9960426514166575 |
| `Q_exc_over_sqrt_V2_max` | 0.9960426514166575 |
| `variance_explains_excursion_flag` | True |
| `endpoint_exclusion_status` | available |
| `endpoint_exclusion_harmful_count` | 0 |
| `pass_endpoint_exclusion` | True |
| `rows_above_0p025` | 0 |
| `rows_above_0p05` | 0 |
| `rows_above_0p10` | 0 |
| `rows_above_0p25` | 0 |
| `rows_above_1p00` | 0 |
| `pass_cap_0p025` | True |
| `pass_cap_0p05` | True |
| `pass_cap_0p10` | True |
| `pass_cap_0p25` | True |
| `pass_cap_1p00` | True |
| `missing_Q_exc_near_forbidden_count` | 0 |
| `invalid_scale_near_forbidden_count` | 0 |
| `hexc_failures` | 0 |
| `pass_hexc_bridge_rigidity_empirical` | True |
| `recommended_theorem_form` | strong_bridge_rigidity_Cexc_0p025 |
| `recommended_next_file` | Prime_Mesh_R2Q_HExc_BridgeRigidity_Closure_Update_v1.md |
| `audit_level` | row-level_existing_o2p3_plus_fcl_Qexc |

## 5. Cap Tests

| cap | rows tested | rows above | near-forbidden above | pass |
|---:|---:|---:|---:|---|
| 0.025 | 166 | 0 | 0 | True |
| 0.05 | 166 | 0 | 0 | True |
| 0.1 | 166 | 0 | 0 | True |
| 0.25 | 166 | 0 | 0 | True |
| 1.0 | 166 | 0 | 0 | True |

## 6. Variance Proxy Result

- `sqrt_V2_global`: `0.0206489515483821`
- `Q_exc_max`: `0.0205672364492246`
- `Q_exc_max_over_sqrt_V2_global`: `0.9960426514166575`
- `variance_explains_excursion_flag`: `True`

## 7. Endpoint Exclusion

- `endpoint_exclusion_status`: `available`
- `endpoint_exclusion_harmful_count`: `0`
- `pass_endpoint_exclusion`: `True`

## 8. Failures

No failures found.

## 9. Interpretation

Recommended theorem form: `strong_bridge_rigidity_Cexc_0p025`.

Recommended next file: `Prime_Mesh_R2Q_HExc_BridgeRigidity_Closure_Update_v1.md`.

---

*Prime Mesh Theory - RH Programme*
