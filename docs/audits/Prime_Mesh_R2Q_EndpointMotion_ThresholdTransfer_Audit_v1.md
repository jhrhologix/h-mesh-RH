# Prime Mesh R2Q — EndpointMotion ThresholdTransfer Audit v1

**Date:** 2026-05-11

## 1. Scope

Test `Q_R2Q > 0.75 => E_theta < 0` and supporting gates without relying on the weak global dominance-ratio shortcut.

## 2. Summary

- Rows: `1468`; post-P0 rows: `142`.
- `Q_R2Q > 0.75` rows: `3`.
- Direct threshold transfer: `True`.
- Direct delta threshold: `False`.
- Endpoint sign bridge: `True`.
- Positive harmlessness `Q_R2Q <= 0.305`: `True`.
- Neutral `1e-8` threshold hits: `0`.
- Recommended theorem form: `direct_threshold_sign`.

## 3. Threshold Rows

| candidate | p_star | Q_R2Q | Q_delta_D | E_theta | threshold_relevant | forbidden |
|---:|---:|---:|---:|---:|---:|---:|
| hexc_00000 | 180530237 | 1.819352 | 1.8091175 | -3089.9881 | True | True |
| hexc_00006 | 30774449 | 0.86252635 | 0.85284271 | -928.35302 | True | False |
| hexc_00040 | 604672261 | 0.75685966 | 0.74670767 | -1617.0683 | True | False |

## 4. Dangerous / Threshold-Relevant Rows

| candidate | Q_R2Q | Q_delta_D | E_theta | row_regime |
|---:|---:|---:|---:|---|
| hexc_00000 | 1.819352 | 1.8091175 | -3089.9881 | primitive_negative_transfer_verified |
| hexc_00006 | 0.86252635 | 0.85284271 | -928.35302 | primitive_negative_transfer_verified |
| hexc_00040 | 0.75685966 | 0.74670767 | -1617.0683 | primitive_full_verified |

## 5. Positive Rows

`positive_E_theta_count = 1320`; `positive_E_theta_Q_R2Q_max = 0.215708483605`.

## 6. Neutral Rows

| tau | rows | Q_R2Q max | above 0.75 | threshold relevant | forbidden |
|---:|---:|---:|---:|---:|---:|
| 1e-12 | 0 | nan | 0 | 0 | 0 |
| 1e-10 | 0 | nan | 0 | 0 | 0 |
| 1e-08 | 0 | nan | 0 | 0 | 0 |
| 1e-06 | 0 | nan | 0 | 0 | 0 |
| 1e-04 | 0 | nan | 0 | 0 | 0 |

## 7. Counterexamples

Counterexample rows emitted: `1`.

| type | candidate | Q_R2Q | Q_delta_D | E_theta |
|---|---:|---:|---:|---:|
| direct_delta | hexc_00040 | 0.75685966 | 0.74670767 | -1617.0683 |

## 8. Recommended Next File

`Prime_Mesh_R2Q_EndpointMotion_DirectThresholdSign_Theorem_Target_v1.md`

## 9. Outputs

```text
prime_mesh_r2q_endpointmotion_thresholdtransfer_audit.py
prime_mesh_r2q_endpointmotion_thresholdtransfer_summary.csv
prime_mesh_r2q_endpointmotion_thresholdtransfer_rows.csv
prime_mesh_r2q_endpointmotion_thresholdtransfer_by_regime.csv
prime_mesh_r2q_endpointmotion_thresholdtransfer_counterexamples.csv
prime_mesh_r2q_endpointmotion_thresholdtransfer_positive_rows.csv
prime_mesh_r2q_endpointmotion_thresholdtransfer_neutral_rows.csv
prime_mesh_r2q_endpointmotion_thresholdtransfer_failures.csv
prime_mesh_r2q_endpointmotion_thresholdtransfer_threshold_rows.csv
prime_mesh_r2q_endpointmotion_thresholdtransfer_forbidden_rows.csv
prime_mesh_r2q_endpointmotion_thresholdtransfer_gap_scan.csv
```

*AI documentation pass: GPT-5.5*