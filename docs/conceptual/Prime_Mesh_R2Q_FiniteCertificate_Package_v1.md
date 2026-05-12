# Prime Mesh R2Q - FiniteCertificate Package

**Document:** `Prime_Mesh_R2Q_FiniteCertificate_Package_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** finite candidate certificate passes; continuous theta certificate pending

## 1. Executive Verdict

\[\boxed{\text{Finite candidate certificate passes empirically.}}\]

No exact theta prefix table was found in the repair results folder, so this package does **not** claim a continuous all-`x<P0` theta-envelope certificate.

## 2. Scope

- Candidate-level finite certificate: **produced and passing**.
- Continuous all-`x<P0` theta-envelope certificate: **pending exact theta prefix data**.

## 3. Inputs Used

- `prime_mesh_r2q_b3_no_accumulation_rows.csv`
- `prime_mesh_r2q_b3_no_accumulation_summary.csv`
- `prime_mesh_r2q_blocksystem_definition_blocks.csv`
- `prime_mesh_r2q_blocksystem_definition_candidates.csv`
- `prime_mesh_r2q_blocksystem_definition_geometry.csv`
- `prime_mesh_r2q_channel_compatibility_rows.csv`
- `prime_mesh_r2q_firstcrossing_covering_localization_windows.csv`
- `prime_mesh_r2q_hexc_bridge_rigidity_rows.csv`
- `prime_mesh_r2q_negative_transfer_coordinate_rows.csv`
- `prime_mesh_r2q_o2_local_repayment_assembly_rows.csv`
- `prime_mesh_r2q_partial_full_interval_compatibility_rows.csv`
- `prime_mesh_r2q_positive_harmlessness_summary.csv`
- `prime_mesh_r2q_theta_first_crossing_crossings.csv`
- `prime_mesh_r2q_theta_first_crossing_intervals.csv`

## 4. Summary

| metric | value |
|---|---:|
| `rows` | 1328 |
| `finite_zone_rows` | 1328 |
| `post_P0_rows` | 0 |
| `coordinate_test_rows` | 1326 |
| `finite_certificate_rows` | 1328 |
| `finite_certificate_coordinate_excluded_rows` | 2 |
| `known_pstar_110312593_rows` | 1 |
| `positive_rows` | 1200 |
| `negative_rows` | 126 |
| `unknown_sign_rows` | 2 |
| `near_forbidden_rows` | 3 |
| `forbidden_rows` | 2 |
| `certified_rows` | 1328 |
| `unresolved_rows` | 0 |
| `exception_rows` | 0 |
| `failure_rows` | 0 |
| `certified_theta_envelope_direct_rows` | 0 |
| `certified_positive_harmless_rows` | 1200 |
| `certified_negative_repaid_rows` | 126 |
| `certified_R2Q_below_threshold_rows` | 0 |
| `certified_endpoint_repaid_rows` | 0 |
| `certified_B3_no_accumulation_rows` | 0 |
| `certified_coordinate_excluded_rows` | 2 |
| `max_abs_theta_error` | nan |
| `max_theta_ratio` | nan |
| `worst_theta_x` | nan |
| `worst_theta_status` | not_run_no_theta_prefix_data |
| `pass_finite_candidate_certificate` | True |
| `pass_finite_theta_envelope_certificate` | False |
| `pass_finite_certificate_package` | False |
| `recommended_theorem_form` | finite_candidate_certificate_continuous_theta_pending |
| `recommended_next_file` | Prime_Mesh_R2Q_FiniteCertificate_Closure_Update_v1.md |

## 5. Certification Modes

| mode | rows |
|---|---:|
| `positive_harmless_cap` | 1200 |
| `negative_channel_repaid` | 126 |
| `coordinate_excluded_finite_certificate` | 2 |

## 6. Known Finite Marker

Rows with `p_star=110312593`: 1.
- `candidate_id=b3_00000`, `block_id=0.0`, `mode=coordinate_excluded_finite_certificate`, `status=pass`

## 7. Direct Theta-Envelope Check

| scope          | check_status   | reason                                                     | pass_finite_theta_envelope_certificate   |
|:---------------|:---------------|:-----------------------------------------------------------|:-----------------------------------------|
| x_lt_500000000 | not_run        | no exact theta prefix table found in repair results folder | False                                    |

## 8. Exceptions / Failures

No candidate-level exceptions or failures found.

## 9. Recommended Theorem Form

`finite_candidate_certificate_continuous_theta_pending`

## 10. Honest Status

This file closes the finite **candidate-row** package empirically. It does not yet close the stronger continuous all-`x<P0` theta-envelope certificate.

## 11. Recommended Next File

`Prime_Mesh_R2Q_FiniteCertificate_Closure_Update_v1.md`

---

*Prime Mesh Theory - RH Programme*