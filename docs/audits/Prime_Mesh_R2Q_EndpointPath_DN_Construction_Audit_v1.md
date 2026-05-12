# Prime Mesh R2Q - EndpointPath D_N Construction Audit

**Document:** `Prime_Mesh_R2Q_EndpointPath_DN_Construction_Audit_v1.md`
**Project:** Prime Mesh Theory - RH Programme
**Date:** 2026-05-08
**Status:** pass

## 1. Executive Verdict

\[
\boxed{\text{EndpointPath }D_N\text{ construction is internally consistent on the full primitive inventory.}}
\]

## 2. Inputs Used

- Primary inventory: `<package-root>\prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv`.

## 3. Construction Checks

| metric | value |
|---|---:|
| `rows` | 1468 |
| `primitive_full_rows` | 1468 |
| `missing_D_endpoint_rows` | 0 |
| `missing_DeltaD_rows` | 0 |
| `missing_Q_delta_D_rows` | 0 |
| `missing_bridge_excursion_rows` | 0 |
| `missing_Q_exc_rows` | 0 |
| `invalid_scale_rows` | 0 |
| `max_abs_DeltaD_recompute_error` | 3.6415315207705135e-12 |
| `max_abs_Q_delta_D_recompute_error` | 2.220446049250313e-16 |
| `max_abs_Q_exc_recompute_error` | 1.0061396160665481e-16 |
| `max_formula_reconstruction_error` | 2.220446049250313e-16 |
| `formula_reconstruction_failures` | 0 |
| `threshold_relevant_rows` | 3 |
| `threshold_relevant_DN_failures` | 0 |
| `forbidden_rows` | 1 |
| `forbidden_DN_failures` | 0 |
| `positive_rows` | 1320 |
| `positive_DN_failures` | 0 |
| `endpoint_path_construction_failures` | 0 |
| `pass_endpoint_path_DN_construction_empirical` | True |

## 4. Regime Table

| row_regime                  |   rows |   threshold_relevant_rows |   forbidden_rows |   max_abs_DeltaD_error |   max_abs_Q_delta_D_error |   max_abs_Q_exc_error |   max_formula_error |   failures |
|:----------------------------|-------:|--------------------------:|-----------------:|-----------------------:|--------------------------:|----------------------:|--------------------:|-----------:|
| threshold_relevant_negative |      2 |                         2 |                0 |            0           |               0           |           8.04478e-17 |         1.11022e-16 |          0 |
| forbidden_negative          |      1 |                         1 |                1 |            0           |               2.22045e-16 |           8.45678e-17 |         2.22045e-16 |          0 |
| positive_harmless           |   1320 |                         0 |                0 |            3.64153e-12 |               1.04083e-16 |           1.00614e-16 |         2.01228e-16 |          0 |
| subthreshold_negative       |    145 |                         0 |                0 |            3.63798e-12 |               1.11022e-16 |           9.93129e-17 |         2.22045e-16 |          0 |

## 5. Failures

No EndpointPath construction failures.

## 6. Recommended Theorem Form

`DN_endpoint_path_construction_verified_for_full_primitive_inventory`

## 7. Recommended Next File

`Prime_Mesh_R2Q_EndpointPath_DN_Construction_Closure_Update_v1.md`

---

*Prime Mesh Theory - RH Programme*
