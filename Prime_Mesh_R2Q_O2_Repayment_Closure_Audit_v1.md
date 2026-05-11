# Prime Mesh R2Q — O2 Repayment Closure Audit v1

**Date:** 2026-05-10

## 1. Scope

Audit negative subthreshold rows and O2 repayment/neutralization coverage:

```text
E_theta < 0 and Q_R2Q <= 0.75
```

## 2. Summary

- Rows: `1468`; post-P0 rows: `142`.
- Negative subthreshold rows: `145`.
- Post-P0 negative subthreshold rows: `21`.
- Surviving unrepaid negative subthreshold rows: `0`.
- O2 available rows: `1468`; missing: `0`.
- `O2_cap_max = 0.0499059549846`, target `0.05`.
- `O2_cap_margin = 9.40450153937e-05`.
- Best closure form: `O2_numeric_repayment`.

## 3. Target Population

| candidate | Q_R2Q | E_theta | repaid | finite | non_surviving | O2_value | O2_margin |
|---:|---:|---:|---:|---:|---:|---:|---:|
| hexc_00002 | 0.68122415 | -1027.9446 | True | True | True | 0.049905955 | 9.4045015e-05 |
| hexc_00023 | 0.54592311 | -1166.6734 | True | True | True | 0.049905955 | 9.4045015e-05 |
| hexc_00009 | 0.46258 | -1758.548 | True | True | True | 0.049905955 | 9.4045015e-05 |
| hexc_00063 | 0.44945681 | -1034.3984 | True | False | True | 0.049905955 | 9.4045015e-05 |
| hexc_00024 | 0.35576655 | -719.80643 | True | True | True | 0.049905955 | 9.4045015e-05 |
| hexc_00020 | 0.33812405 | -424.33161 | True | True | True | 0.049905955 | 9.4045015e-05 |
| hexc_00008 | 0.32129499 | -480.6815 | True | True | True | 0.049905955 | 9.4045015e-05 |
| hexc_00048 | 0.30755186 | -291.87336 | True | True | True | 0.049905955 | 9.4045015e-05 |
| hexc_00104 | 0.29148119 | -688.59134 | True | False | True | 0.049905955 | 9.4045015e-05 |
| hexc_00183 | 0.28191696 | -365.24465 | True | False | True | 0.049905955 | 9.4045015e-05 |

## 4. Repayment Coverage

`pass_negative_subthreshold_repayment = True`.

`pass_post_P0_O2_repayment = True`.

## 5. Numeric O2 Bounds

`pass_O2_numeric_repayment = True`.

`pass_O2_cap = True`.

The cap is close but below target: `Q_O2_conservative <= 0.04990595498460639 < 0.05`.

## 6. Forbidden and Finite Rows

Forbidden rows: `1`; surviving unrepaid forbidden rows: `0`.

Finite-zone negative subthreshold rows: `124`; certified: `124`.

## 7. Neutral Interaction

| tau | rows | repaid | finite | Q_R2Q max | threshold rows |
|---:|---:|---:|---:|---:|---:|
| 1e-12 | 0 | 0 | 0 | nan | 0 |
| 1e-10 | 0 | 0 | 0 | nan | 0 |
| 1e-08 | 0 | 0 | 0 | nan | 0 |
| 1e-06 | 0 | 0 | 0 | nan | 0 |
| 1e-04 | 0 | 0 | 0 | nan | 0 |

## 8. Counterexamples

Counterexample rows emitted: `0`.

No O2 repayment/cap counterexamples were found.

## 9. Recommended Theorem Form

`O2_numeric_repayment`.

## 10. Recommended Next File

`Prime_Mesh_R2Q_O2_Repayment_Theorem_Target_v1.md`.

## 11. Outputs

```text
prime_mesh_r2q_o2_repayment_closure_audit.py
prime_mesh_r2q_o2_repayment_closure_summary.csv
prime_mesh_r2q_o2_repayment_closure_rows.csv
prime_mesh_r2q_o2_repayment_closure_by_regime.csv
prime_mesh_r2q_o2_repayment_closure_counterexamples.csv
prime_mesh_r2q_o2_repayment_closure_negative_subthreshold_rows.csv
prime_mesh_r2q_o2_repayment_closure_failures.csv
prime_mesh_r2q_o2_repayment_closure_neutral_rows.csv
prime_mesh_r2q_o2_repayment_closure_forbidden_rows.csv
prime_mesh_r2q_o2_repayment_closure_cap_scan.csv
prime_mesh_r2q_o2_repayment_closure_accumulation_proxy.csv
```

*AI documentation pass: GPT-5.5*