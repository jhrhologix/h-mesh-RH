# Prime Mesh R2Q — FirstCrossing EndpointSign Audit v1

**Date:** 2026-05-10

## 1. Scope

Resolve endpoint sign orientation for upper/lower first crossings.

## 2. Summary

- `E_theta` orientation: `raw`.
- Crossing sign variable: `local_theta_sign`.
- Upper crossings: `1320`; nonpositive `E_theta`: `0`.
- Lower crossings: `148`; nonnegative `E_theta`: `0`.
- Lower surviving unrepaid rows: `0`.
- Classification: `upper_lower_split`.
- Pass audit: `True`.

## 3. E_theta Definition/Orientation

`E_theta` is raw: the theta assembly defines it as `theta(b)-theta(a)-(b-a)=H(b)-H(a)`. The crossing sign is carried separately by `local_theta_sign`.

The derived outward quantity `E_theta_out = sigma * E_theta` is positive for every signed crossing row, but the v5 direct sign theorem is stated in raw `E_theta`, not outward-oriented coordinates.

## 4. Upper Crossings

| metric | value |
|---|---:|
| `rows` | `1320` |
| `Q_R2Q_max` | `0.2157084836048593` |
| `Q_R2Q_gt_0p75_count` | `0` |
| `E_theta_min` | `1.8396280710575184` |
| `E_theta_max` | `88.76041429147188` |
| `surviving_unrepaid_count` | `0` |

Upper/positive crossings satisfy raw `E_theta > 0`, so threshold upper crossings would contradict v5 direct sign.

## 5. Lower Crossings

| metric | value |
|---|---:|
| `rows` | `148` |
| `Q_R2Q_max` | `1.8193520399038576` |
| `Q_R2Q_gt_0p75_count` | `3` |
| `E_theta_min` | `-3089.9881332697114` |
| `E_theta_max` | `-1.5258205110753806` |
| `O2_safe_count` | `148` |
| `B3_safe_count` | `148` |
| `finite_certified_count` | `126` |
| `surviving_unrepaid_count` | `0` |

Lower/negative crossings satisfy raw `E_theta < 0`. They do not contradict direct sign directly, but the data shows zero surviving unrepaid lower candidates and complete safety through O2/B3/finite/non-surviving channels.

## 6. v5 Compatibility

- Uses direct threshold sign: `True`.
- Uses failed delta-threshold route: `False`.

## 7. Data Rows

Row-level outputs were written to `prime_mesh_r2q_firstcrossing_endpointsign_data_rows.csv`.

## 8. Gaps

| gap | status | detail | recommended file |
|---|---|---|---|
| Raw-vs-oriented endpoint sign | `resolved_as_raw_with_orientation_variable` | E_theta is raw; local_theta_sign gives crossing orientation and E_theta_out=sigma*E_theta is positive. | `Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Theorem_Target_v1.md` |
| Oriented local direct sign | `not_available` | Direct sign is stated in raw E_theta coordinates, so a uniform outward-oriented contradiction is not available without a signed local theorem. | `Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Theorem_Target_v1.md` |
| Lower crossing closure | `closed_by_o2b3_finite_data` | Lower rows are raw negative; data shows zero surviving unrepaid lower candidates and complete O2/B3/finite/non-surviving safety. | `Prime_Mesh_R2Q_FirstCrossing_LowerCrossing_O2B3_Closure_Target_v1.md` |

## 9. Counterexamples

Counterexample rows emitted: `0`.

## 10. Recommended Next File

`Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Theorem_Target_v1.md`.

## 11. Outputs

```text
prime_mesh_r2q_firstcrossing_endpointsign_audit.py
prime_mesh_r2q_firstcrossing_endpointsign_summary.csv
prime_mesh_r2q_firstcrossing_endpointsign_file_review.csv
prime_mesh_r2q_firstcrossing_endpointsign_statement_inventory.csv
prime_mesh_r2q_firstcrossing_endpointsign_data_rows.csv
prime_mesh_r2q_firstcrossing_endpointsign_upper_lower.csv
prime_mesh_r2q_firstcrossing_endpointsign_v5_compatibility.csv
prime_mesh_r2q_firstcrossing_endpointsign_gaps.csv
prime_mesh_r2q_firstcrossing_endpointsign_o2b3_lower.csv
prime_mesh_r2q_firstcrossing_endpointsign_orientation_test.csv
prime_mesh_r2q_firstcrossing_endpointsign_counterexamples.csv
```

*AI documentation pass: GPT-5.5*