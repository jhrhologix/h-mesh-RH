# Prime Mesh R2Q - ChannelCompatibility Audit

**Document:** `Prime_Mesh_R2Q_ChannelCompatibility_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** ChannelCompatibility audit - passes

## 1. Executive Verdict

This audit verifies that every coordinate-available dangerous R2Q row is compatible with the negative repayment channel `C_-`.

\[\boxed{\text{ChannelCompatibility passes empirically.}}\]

## 2. Inputs Used

- `prime_mesh_r2q_negative_transfer_coordinate_rows.csv`
- `prime_mesh_r2q_negative_transfer_coordinate_summary.csv`
- `prime_mesh_r2q_positive_harmlessness_summary.csv`
- `prime_mesh_r2q_partial_full_interval_compatibility_rows.csv`
- `prime_mesh_r2q_b3_block_to_tail_blocks.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_windows.csv`

Optional inputs missing:
- `prime_mesh_r2q_o123_to_mr2_assembly_summary.csv`

Join notes:
- primary NegativeTransfer row table used directly
- prime_mesh_r2q_firstcrossing_covering_localization_windows.csv on ['block_id', 'p_star', 'y', 'h']: 1469->1469

## 3. Summary

| metric | value |
|---|---:|
| `rows` | 1469 |
| `coordinate_test_rows` | 1468 |
| `Q_gt_0p75_rows` | 3 |
| `Q_gt_1_rows` | 1 |
| `Q_gt_0p75_channel_compatible_count` | 3 |
| `Q_gt_0p75_channel_compatible_frac` | 1.0 |
| `Q_gt_1_channel_compatible_frac` | 1.0 |
| `positive_channel_conflict_count` | 0 |
| `finite_certificate_unresolved_count` | 0 |
| `finite_certificate_coordinate_excluded_rows` | 1 |
| `excluded_near_forbidden_rows` | 1 |
| `missing_channel_rows` | 0 |
| `negative_transfer_near_forbidden_rows` | 3 |
| `O2_applicable_near_forbidden_rows` | 3 |
| `B3_applicable_near_forbidden_rows` | 3 |
| `pass_channel_compatibility_empirical` | True |

## 4. Channel Groups

`4` channel groups were written to `prime_mesh_r2q_channel_compatibility_by_channel.csv`.

## 5. Failures

No failures found.

## 6. Interpretation

The proof-facing theorem can use:

\[Q_{\rm R2Q}(J)>3/4\Rightarrow J\in\mathcal C_-.\]

Finite-certificate coordinate-excluded rows are reported separately and are not part of the post-`P0` coordinate theorem.

---

*Prime Mesh Theory - RH Programme*
