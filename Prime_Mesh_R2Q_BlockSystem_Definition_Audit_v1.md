# Prime Mesh R2Q - BlockSystem Definition Audit

**Document:** `Prime_Mesh_R2Q_BlockSystem_Definition_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** BlockSystem export audit - passes

## 1. Executive Verdict

This audit exports the empirical block-system layer needed by the deterministic FCL front end:

\[
\mathcal X_{\rm cand},\quad \mathcal B,\quad \Phi,\quad x\preceq J,\quad \rho(x,J),\quad p^*/x,\quad h/x.
\]

## 2. Inputs Used

- `prime_mesh_r2q_firstcrossing_covering_localization_crossings.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_windows.csv`
- `prime_mesh_r2q_b3_block_to_tail_blocks.csv`

## 3. Summary

| metric | value |
|---|---:|
| `rows` | 1469 |
| `post_P0_rows` | 142 |
| `candidate_rows` | 1469 |
| `block_rows` | 1469 |
| `selection_rows` | 1469 |
| `pstar_over_x_min` | 1.0 |
| `pstar_over_x_max` | 1.0056242504445638 |
| `pstar_over_x_mean` | 1.0000067522497174 |
| `h_over_x_min` | 1.6532086363467068e-09 |
| `h_over_x_max` | 0.007874015748031496 |
| `h_over_x_mean` | 3.378813482259336e-05 |
| `scale_ratio_min` | 4.0659668423964146e-05 |
| `scale_ratio_max` | 0.08873565094161139 |
| `scale_ratio_mean` | 0.0015017582664258184 |
| `scale_ratio_q95` | 0.006601895332031715 |
| `scale_ratio_q99` | 0.024582301584379455 |
| `post_P0_pstar_over_x_min` | 1.0 |
| `post_P0_pstar_over_x_max` | 1.0000003823184502 |
| `post_P0_h_over_x_max` | 0.0002507970181221857 |
| `post_P0_scale_ratio_max` | 0.01583657217083879 |
| `coverage_failures` | 0 |
| `compatibility_failures` | 0 |
| `geometry_failures` | 0 |
| `post_P0_failures` | 0 |
| `pass_blocksystem_definition_empirical` | True |

## 4. Failures

No failures found.

## 5. Interpretation

\[
\boxed{\text{The empirical BlockSystem definition passes: }\Phi\text{ is total on candidates and geometry is valid.}}
\]

The post-`P0` candidate set has no coverage, compatibility, geometry, or control-relation failures.

## 6. Outputs

- `prime_mesh_r2q_blocksystem_definition_summary.csv`
- `prime_mesh_r2q_blocksystem_definition_candidates.csv`
- `prime_mesh_r2q_blocksystem_definition_blocks.csv`
- `prime_mesh_r2q_blocksystem_definition_selection_map.csv`
- `prime_mesh_r2q_blocksystem_definition_geometry.csv`
- `prime_mesh_r2q_blocksystem_definition_failures.csv`

---

*Prime Mesh Theory - RH Programme*
