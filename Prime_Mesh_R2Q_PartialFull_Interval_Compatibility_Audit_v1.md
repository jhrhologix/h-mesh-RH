# Prime Mesh R2Q - Partial/Full Interval Compatibility Audit

**Document:** `Prime_Mesh_R2Q_PartialFull_Interval_Compatibility_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** Partial/full interval compatibility audit - passes

## 1. Executive Verdict

This audit checks whether the interval used for signed theta extraction is compatible with the full R2Q/B2 repayment block:

\[J_x=[y,x],\qquad J=[y,y+h].\]

\[\boxed{\text{Partial/full compatibility passes empirically.}}\]

## 2. Inputs Used

- `prime_mesh_r2q_blocksystem_definition_candidates.csv`
- `prime_mesh_r2q_blocksystem_definition_blocks.csv`
- `prime_mesh_r2q_blocksystem_definition_selection_map.csv`
- `prime_mesh_r2q_blocksystem_definition_geometry.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv`
- `prime_mesh_r2q_o2p4_final_slack_intervals.csv`

## 3. Summary

| metric | value |
|---|---:|
| `rows` | 1469 |
| `post_P0_rows` | 142 |
| `right_endpoint_rows` | 1469 |
| `partial_used_rows` | 0 |
| `post_P0_partial_used_rows` | 0 |
| `finite_certificate_outside_block_rows` | 0 |
| `partial_used_frac` | 0.0 |
| `sign_known_rows` | 1468 |
| `sign_preserved_rows` | 1468 |
| `sign_mismatch_rows` | 0 |
| `dangerous_sign_mismatch_rows` | 0 |
| `positive_partial_rows` | 1320 |
| `negative_partial_rows` | 148 |
| `zero_partial_rows` | 0 |
| `positive_partial_Qmax` | 0.2157084836048593 |
| `negative_partial_Qmax` | 1.8193520399038576 |
| `full_Qmax` | 1.8193520399038576 |
| `mismatch_Qmax` | 0.0 |
| `boundary_slack_proxy_max` | 0.0 |
| `boundary_repaid_rows` | 1469 |
| `boundary_unknown_rows` | 0 |
| `partial_full_failures` | 0 |
| `post_P0_partial_full_failures` | 0 |
| `pass_partial_full_empirical` | True |

## 4. Endpoint-Control Result

- `right_endpoint_rows`: `1469`
- `partial_used_rows`: `0`
- `post_P0_partial_used_rows`: `0`
- `finite_certificate_outside_block_rows`: `0`

\[\boxed{\text{All post-}P_0\text{ selected rows use the full endpoint interval }J_x=J.}\]

## 5. Sign Preservation Result

- `sign_known_rows`: `1468`
- `sign_preserved_rows`: `1468`
- `sign_mismatch_rows`: `0`
- `dangerous_sign_mismatch_rows`: `0`

## 6. Boundary Slack / O2.4 Compatibility

- `boundary_slack_proxy_max`: `0.0`
- `boundary_repaid_rows`: `1469`
- `boundary_unknown_rows`: `0`

## 7. Failures

No failures found.

## 8. Interpretation for FCL

The post-`P0` FCL front end does not need a separate partial/full sign-transfer repair in the audited inventory: selected post-`P0` rows already use endpoint-compatible full intervals.

## 9. Outputs

- `prime_mesh_r2q_partial_full_interval_compatibility_summary.csv`
- `prime_mesh_r2q_partial_full_interval_compatibility_rows.csv`
- `prime_mesh_r2q_partial_full_interval_compatibility_failures.csv`

---

*Prime Mesh Theory - RH Programme*
