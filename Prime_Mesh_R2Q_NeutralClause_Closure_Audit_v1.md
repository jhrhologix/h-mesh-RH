# Prime Mesh R2Q — NeutralClause Closure Audit v1

**Date:** 2026-05-10

## 1. Scope

Audit neutral or near-neutral `E_theta` rows after H-Exc, EndpointMotion, O2, and B3 closures.

## 2. Summary

- Rows: `1468`; post-P0 rows: `142`.
- Minimum `|E_theta|`: `1.52582051108` at `hexc_00359`.
- `Q_R2Q` at minimum `|E_theta|`: `0.0702213435707`.
- NeutralClause failures: `0`.
- Best closure form: `empty_neutral_clause`.

## 3. Neutral Tolerance Scan

| tau | rows | Q_R2Q max | threshold rows | uncovered rows | pass subthreshold | pass coverage |
|---:|---:|---:|---:|---:|---:|---:|
| 0e+00 | 0 | nan | 0 | 0 | True | True |
| 1e-14 | 0 | nan | 0 | 0 | True | True |
| 1e-12 | 0 | nan | 0 | 0 | True | True |
| 1e-10 | 0 | nan | 0 | 0 | True | True |
| 1e-08 | 0 | nan | 0 | 0 | True | True |
| 1e-06 | 0 | nan | 0 | 0 | True | True |
| 1e-04 | 0 | nan | 0 | 0 | True | True |
| 1e-03 | 0 | nan | 0 | 0 | True | True |
| 1e-02 | 0 | nan | 0 | 0 | True | True |

## 4. Closest-To-Neutral Rows

| candidate | abs_E_theta | E_theta | Q_R2Q | sign | finite | O2 | B3 | covered |
|---:|---:|---:|---:|---|---:|---:|---:|---:|
| hexc_00359 | 1.5258205 | -1.5258205 | 0.070221344 | negative | True | True | True | True |
| hexc_00278 | 1.7644553 | -1.7644553 | 0.082920075 | negative | True | True | True | True |
| hexc_00193 | 1.8396281 | 1.8396281 | 0.080583324 | positive | True | True | True | True |
| hexc_00116 | 3.3720181 | -3.3720181 | 0.09277101 | negative | True | True | True | True |
| hexc_00033 | 3.8441871 | 3.8441871 | 0.21570848 | positive | True | True | True | True |
| hexc_00004 | 4.3154603 | -4.3154603 | 0.15668101 | negative | True | True | True | True |
| hexc_00010 | 4.3518581 | 4.3518581 | 0.19127642 | positive | True | True | True | True |
| hexc_00058 | 4.6801726 | 4.6801726 | 0.1707576 | positive | True | True | True | True |
| hexc_00105 | 5.1717006 | 5.1717006 | 0.1648069 | positive | True | True | True | True |
| hexc_00134 | 5.2850399 | -5.2850399 | 0.071634801 | negative | True | True | True | True |
| hexc_00201 | 5.5117453 | 5.5117453 | 0.15516105 | positive | True | True | True | True |
| hexc_00036 | 6.412764 | 6.412764 | 0.13894959 | positive | True | True | True | True |
| hexc_00136 | 6.9441375 | 6.9441375 | 0.12520237 | positive | True | True | True | True |
| hexc_00075 | 6.9651983 | 6.9651983 | 0.12822614 | positive | True | True | True | True |
| hexc_01135 | 7.682199 | 7.682199 | 0.11666047 | positive | True | True | True | True |
| hexc_00099 | 7.7673291 | 7.7673291 | 0.11598968 | positive | True | True | True | True |
| hexc_00084 | 8.2454179 | 8.2454179 | 0.10867259 | positive | True | True | True | True |
| hexc_00085 | 8.6714924 | 8.6714924 | 0.10698357 | positive | True | True | True | True |
| hexc_00375 | 8.6763987 | 8.6763987 | 0.10343765 | positive | True | True | True | True |
| hexc_00677 | 8.6917166 | 8.6917166 | 0.10697473 | positive | True | True | True | True |

## 5. Threshold Interaction

Threshold rows: `3`.

Threshold-row minimum `|E_theta|`: `928.353018252`.

Threshold-row max `E_theta`: `-928.353018252`.

## 6. Coverage

Neutral rows, when using the tested tolerances, have no threshold or uncovered failures.

## 7. Counterexamples

Counterexample rows emitted: `0`.

No neutral threshold or uncovered counterexamples were found.

## 8. Recommended Theorem Form

`empty_neutral_clause`.

## 9. Recommended Next File

`Prime_Mesh_R2Q_NeutralClause_Empty_Theorem_Target_v1.md`.

## 10. Outputs

```text
prime_mesh_r2q_neutral_clause_closure_audit.py
prime_mesh_r2q_neutral_clause_closure_summary.csv
prime_mesh_r2q_neutral_clause_closure_rows.csv
prime_mesh_r2q_neutral_clause_closure_by_tau.csv
prime_mesh_r2q_neutral_clause_closure_closest_rows.csv
prime_mesh_r2q_neutral_clause_closure_counterexamples.csv
prime_mesh_r2q_neutral_clause_closure_failures.csv
prime_mesh_r2q_neutral_clause_closure_by_regime.csv
prime_mesh_r2q_neutral_clause_closure_threshold_interaction.csv
prime_mesh_r2q_neutral_clause_closure_crosscheck.csv
```

*AI documentation pass: GPT-5.5*