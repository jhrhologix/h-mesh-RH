# Prime Mesh R2Q — FirstCrossing ThresholdRelevance Audit v1

**Date:** 2026-05-10

## 1. Scope

Audit `first-crossing obstruction row => Q_R2Q > 0.75`.

## 2. Summary

- Classification: `fullfcl_backed_certificate_conditional`.
- Rows checked: `10140`.
- Expected rows: `10140`.
- Threshold relevance failures: `0`.
- Surviving obstruction candidates: `0`.
- Candidate rows with `Q_R2Q <= 0.75`: `0`.
- Subthreshold rows: `10115`.
- Subthreshold unclassified rows: `0`.
- Pass audit: `True`.
- Recommended next file: `Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md`.

## 3. Definitions

The safe theorem form is the contrapositive: if `Q_R2Q <= 3/4`, the row is harmless, repaid, finite-certified, or non-surviving. Therefore any surviving first-crossing obstruction must have `Q_R2Q > 3/4`.

## 4. File Review

- Threshold relevance definition found: `True`.
- First-crossing obstruction definition found: `True`.
- `Q_R2Q` threshold definition found: `True`.
- `0.75` / `3/4` justification found: `True`.

## 5. Data Cross-Check

| metric | value |
|---|---:|
| `rows` | `10140` |
| `Q_R2Q_gt_0p75_count` | `24` |
| `Q_R2Q_le_0p75_count` | `10115` |
| `Q_R2Q_min` | `0.0` |
| `Q_R2Q_max` | `1.8193520399038576` |
| `threshold_relevance_failures` | `0` |
| `dangerous_count` | `24` |
| `forbidden_count` | `11` |

## 6. Subthreshold Rows

| classification | count |
|---|---:|
| `positive_harmless` | `7800` |
| `O2_safe` | `4690` |
| `B3_safe` | `5865` |
| `finite_certified` | `9269` |
| `non_surviving` | `10115` |
| `unclassified` | `0` |

Counts overlap because a row can be safe in more than one channel. The important result is zero unclassified subthreshold rows and zero subthreshold surviving obstruction proxies.

## 7. v5 Compatibility

- Uses failed delta route: `False`.
- Uses direct threshold sign: `True`.

## 8. Gaps

| gap | status | detail | recommended file |
|---|---|---|---|
| symbolic all-x ThresholdRelevance proof | `not_standalone_symbolic` | The audit supports the contrapositive through a finite/candidate certificate and FullFCL/Covering inputs, not a standalone symbolic derivation. | `Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md` |
| 10,140-row certificate | `passes` | Rows actual=10140; failures=0. | `Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Certificate_Closure_Update_v1.md` |
| subthreshold non-obstruction | `passes` | Every Q_R2Q<=0.75 row is classified as harmless, repaid, certified, or non-surviving. | `Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Closure_Update_v1.md` |
| failed delta route | `not_used` | No proof evidence relies on Q_R2Q>0.75 => Q_DeltaD>0.75. | `Prime_Mesh_R2Q_GlobalBridge_v5_Compatibility_Update_v1.md` |

## 9. Recommended Next File

`Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md`.

## 10. Outputs

```text
prime_mesh_r2q_firstcrossing_thresholdrelevance_audit.py
prime_mesh_r2q_firstcrossing_thresholdrelevance_summary.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_file_review.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_statement_inventory.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_data_crosscheck.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_failures.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_gaps.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_subthreshold_classification.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_fullfcl_review.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_dangerous_forbidden.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_v5_compatibility.csv
```

*AI documentation pass: GPT-5.5*