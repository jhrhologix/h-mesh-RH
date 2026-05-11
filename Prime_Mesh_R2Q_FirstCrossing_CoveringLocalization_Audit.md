# Prime Mesh R2Q — FirstCrossing CoveringLocalization Audit v1

**Date:** 2026-05-10

## 1. Scope

Determine whether global first crossings are covered by admissible v5 R2Q/theta rows.

## 2. Summary

- Coverage mode: `theta_window_covering`.
- Classification: `conditional_theta_window_plus_finite_continuous`.
- Covered count: `1469`.
- Uncovered count: `0`.
- Coverage failures: `0`.
- Pass audit: `True`.
- Recommended next file: `Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md`.

## 3. Row Family and Domain

- Row family defined: `True`.
- Covered domain: `theta first-crossing windows/candidates; endpoints or endpoint-controlled intervals; finite zone x<P0; sample-grid caveats present`.

## 4. Coverage Type

The safest classification is theta-window candidate coverage with finite-zone continuous certification. It is not yet a full unconditional continuous all-`x` theorem for post-`P0` points.

| field | value |
|---|---:|
| `candidate rows` | `1469` |
| `theta candidates` | `1468` |
| `theta covered` | `1468` |
| `theta uncovered` | `0` |
| `B3 candidates` | `1` |
| `B3 covered` | `1` |
| `post_P0 candidate points` | `142` |
| `finite certificate candidates` | `1327` |

## 5. Boundary and Interior Handling

- Boundary handling: `conditional_present_no_data_failures`.
- Interior handling: `conditional_window_selection_or_lifting_needed`.

The files discuss endpoint-controlled and interior/window selection, but the audit keeps this as conditional proof material rather than a completed continuous lifting theorem.

## 6. Finite-Zone and P0 Transition

- Finite-zone status: `continuous_certificate_passes`.
- `P0` transition status: `no_data_failures_transition_theorem_conditional`.

## 7. v5 Compatibility

- Uses failed delta-threshold route: `False`.
- Uses full-grid H-Exc upgrade: `False`.
- Upper/lower sign preservation: `passes`.

## 8. Data Cross-Check

`coverage_pass=True`, `sign_match_failures=0`, `scale_compatibility_failures=0`.

## 9. Gaps

| gap | status | detail | recommended file |
|---|---|---|---|
| post-P0 continuous all-x covering | `conditional_not_fully_proven` | Audited first-crossing candidates are covered, but the universal all-x window-selection theorem remains an input/target. | `Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md` |
| interior first-crossing lifting | `conditional_or_missing_formal_lifting` | Files mention interior/endpoint-controlled rows; a standalone lemma must prove an interior first crossing is captured by a row endpoint/window/refinement. | `Prime_Mesh_R2Q_DiscreteEndpoint_to_RHScale_Lifting_Proof_Attack_v1.md` |
| finite-zone coverage | `continuous_certificate_passes` | Finite theta envelope summary reports continuous all-x finite certificate with zero failures. | `Prime_Mesh_R2Q_FiniteThetaEnvelope_Closure_Update_v1.md` |
| sampled-grid H-Exc upgrade | `not_used` | Audit does not find proof evidence upgrading sampled-grid H-Exc to full-grid control. | `Prime_Mesh_R2Q_CoveringLocalization_SampledGrid_Warning_Repair_Map_v1.md` |

## 10. Recommended Next File

`Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md`.

## 11. Outputs

```text
prime_mesh_r2q_firstcrossing_coveringlocalization_audit.py
prime_mesh_r2q_firstcrossing_coveringlocalization_summary.csv
prime_mesh_r2q_firstcrossing_coveringlocalization_file_review.csv
prime_mesh_r2q_firstcrossing_coveringlocalization_statement_inventory.csv
prime_mesh_r2q_firstcrossing_coveringlocalization_data_crosscheck.csv
prime_mesh_r2q_firstcrossing_coveringlocalization_gaps.csv
prime_mesh_r2q_firstcrossing_coveringlocalization_fullfcl_review.csv
prime_mesh_r2q_firstcrossing_coveringlocalization_theta_review.csv
prime_mesh_r2q_firstcrossing_coveringlocalization_finite_zone.csv
prime_mesh_r2q_firstcrossing_coveringlocalization_boundary_cases.csv
```
