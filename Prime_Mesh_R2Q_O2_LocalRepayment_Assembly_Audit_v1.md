# Prime Mesh R2Q - O2 LocalRepayment Assembly Audit

**Document:** `Prime_Mesh_R2Q_O2_LocalRepayment_Assembly_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** O2 LocalRepayment assembly audit - passes

## 1. Executive Verdict

This audit assembles:

\[Q_{\rm O2}=Q_{2.1}+Q_{2.2}+Q_{2.3}+Q_{2.4}.\]

\[\boxed{\text{Strong O2 local repayment passes: }Q_{\rm O2}\le0.05.}\]

## 2. Inputs Used

- `prime_mesh_r2q_o2p1_fullmatrix_svd_summary.csv`
- `prime_mesh_r2q_o2p2_longa_spf_discrepancy_summary.csv`
- `prime_mesh_r2q_hexc_bridge_rigidity_summary.csv`
- `prime_mesh_r2q_o2p4_final_slack_summary.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_windows.csv`
- `prime_mesh_r2q_negative_transfer_coordinate_rows.csv`
- `prime_mesh_r2q_endpoint_repayment_compatibility_intervals.csv`
- `prime_mesh_r2q_b3_block_to_tail_blocks.csv`
- `prime_mesh_r2q_blocksystem_definition_blocks.csv`
- `prime_mesh_r2q_blocksystem_definition_geometry.csv`
- `prime_mesh_r2q_o1_schur_residual_sign_stability_vectors.csv`
- `prime_mesh_r2q_o1_schur_residual_sign_stability_scopes.csv`
- `prime_mesh_r2q_channel_compatibility_rows.csv`
- `prime_mesh_r2q_hexc_bridge_rigidity_rows.csv`
- `prime_mesh_r2q_o2p2_longa_spf_discrepancy_intervals.csv`
- `prime_mesh_r2q_o2p3_bridge_excursion_intervals.csv`
- `prime_mesh_r2q_o2p4_final_slack_intervals.csv`

Optional inputs missing:
- `prime_mesh_r2q_o123_to_mr2_assembly_rows.csv`
- `prime_mesh_r2q_o123_to_mr2_assembly_summary.csv`

Join notes:
- base FCL selected windows
- prime_mesh_r2q_channel_compatibility_rows.csv on ['block_id', 'p_star', 'y', 'h']: 1468->1468
- prime_mesh_r2q_hexc_bridge_rigidity_rows.csv on ['block_id', 'p_star', 'y', 'h']: 1468->1468
- prime_mesh_r2q_o2p2_longa_spf_discrepancy_intervals.csv on ['block_id', 'p_star', 'y', 'h']: 1468->1468
- prime_mesh_r2q_o2p3_bridge_excursion_intervals.csv on ['block_id', 'p_star', 'y', 'h']: 1468->1468
- prime_mesh_r2q_o2p4_final_slack_intervals.csv on ['block_id', 'p_star', 'y', 'h']: 1468->1468

## 3. Component Ledger

| component | cap | source | row-level available |
|---|---:|---|---|
| `Q_2p1` | 0.009502682738794 | `prime_mesh_r2q_o2p1_fullmatrix_svd_summary.csv` | False |
| `Q_2p2` | 8.118648230799173e-05 | `prime_mesh_r2q_o2p2_longa_spf_discrepancy_summary.csv` | True |
| `Q_2p3` | 0.0205672364492246 | `prime_mesh_r2q_hexc_bridge_rigidity_summary.csv` | True |
| `Q_2p4` | 0.0197548493142798 | `prime_mesh_r2q_o2p4_final_slack_summary.csv` | True |

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
| `Q_2p1_available_rows` | 0 |
| `Q_2p2_available_rows` | 166 |
| `Q_2p3_available_rows` | 166 |
| `Q_2p4_available_rows` | 1468 |
| `Q_O2_available_rows` | 1468 |
| `Q_2p1_max` | 0.009502682738794 |
| `Q_2p2_max` | 8.118648230799173e-05 |
| `Q_2p3_max` | 0.0205672364492246 |
| `Q_2p4_max` | 0.0197548493142798 |
| `Q_O2_row_sum_max` | nan |
| `Q_O2_cap_sum` | 0.04990595498460639 |
| `Q_O2_conservative_max` | 0.04990595498460639 |
| `near_forbidden_Q_O2_max` | 0.04990595498460639 |
| `forbidden_Q_O2_max` | 0.04990595498460639 |
| `C_minus_Q_O2_max` | 0.04990595498460639 |
| `post_P0_Q_O2_max` | 0.04990595498460639 |
| `rows_above_0p05` | 0 |
| `rows_above_0p10` | 0 |
| `rows_above_0p25` | 0 |
| `rows_above_1p00` | 0 |
| `near_forbidden_above_1p00` | 0 |
| `forbidden_above_1p00` | 0 |
| `C_minus_above_1p00` | 0 |
| `missing_component_near_forbidden_count` | 3 |
| `missing_component_forbidden_count` | 1 |
| `missing_component_near_forbidden_failure_count` | 0 |
| `missing_component_forbidden_failure_count` | 0 |
| `invalid_scale_near_forbidden_count` | 0 |
| `O2_failures` | 0 |
| `pass_O2_local_repayment_empirical` | True |
| `recommended_theorem_form` | strong_local_repayment_QO2_le_0p05 |
| `recommended_next_file` | Prime_Mesh_R2Q_O2_LocalRepayment_Closure_Update_v1.md |
| `fallback_rule` | row-level where all components exist; otherwise verified global cap sum |

## 5. Cap Tests

| cap | rows tested | rows above | near-forbidden above | forbidden above | C-minus above | pass |
|---:|---:|---:|---:|---:|---:|---|
| 0.05 | 1468 | 0 | 0 | 0 | 0 | True |
| 0.1 | 1468 | 0 | 0 | 0 | 0 | True |
| 0.25 | 1468 | 0 | 0 | 0 | 0 | True |
| 0.5 | 1468 | 0 | 0 | 0 | 0 | True |
| 0.75 | 1468 | 0 | 0 | 0 | 0 | True |
| 1.0 | 1468 | 0 | 0 | 0 | 0 | True |

## 6. Failures

No failures found.

## 7. Interpretation

Recommended theorem form: `strong_local_repayment_QO2_le_0p05`.

Recommended next file: `Prime_Mesh_R2Q_O2_LocalRepayment_Closure_Update_v1.md`.

Fallback rule: row-level components are used when all four are available; otherwise the verified global component-cap sum is used conservatively.

---

*Prime Mesh Theory - RH Programme*
