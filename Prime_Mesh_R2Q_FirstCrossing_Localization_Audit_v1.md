# Prime Mesh R2Q — FirstCrossing Localization Audit v1

**Date:** 2026-05-10

## 1. Scope

Audit whether existing files prove the missing first-crossing localization theorem:

```text
global RH-scale first crossing => exists J with Q_R2Q(J)>0.75 and E_theta(J)>=0
```

## 2. Summary

- Files scanned: `15`.
- Classification: `missing_endpoint_sign_orientation`.
- Main missing lemma: Threshold relevance and covering support exist, but the theorem still needs a v5 signed-orientation lemma, especially for lower crossings.
- Pass audit: `False`.

## 3. Lemma Checklist

| lemma | status | evidence |
|---|---|---|
| Envelope Definition | `conditional` | GlobalThetaEnvelope/ThetaFirstCrossing define theta envelope; theorem target states psi/pi alternatives. |
| First-Crossing Existence | `conditional` | First-crossing language exists in conditional assemblies, but not closed as global RH theorem. |
| Theta/R2Q Covering | `conditional` | Covering Localization Conditional Theorem gives this as Input/conditional theorem with empirical support. |
| Threshold Relevance | `conditional` | ThresholdRelevance audit/closure gives empirical theorem-facing contrapositive; proof target remains. |
| Endpoint Sign Orientation | `conditional_incomplete` | Theta conditional assembly states positive crossing gives E_theta>0 and negative gives E_theta<0; target needs unified E_theta>=0 for RH-scale crossing. |
| Lower Crossing Handling | `missing_or_needs_signed_version` | Existing conditional theta assembly says negative first crossing gives E_theta<0, which does not match target E_theta>=0 without reorientation. |
| Finite-Zone Coverage | `conditional` | FiniteThetaEnvelope and finite certificate files exist; final index/reproducibility still noted. |
| v5 Contradiction | `proven_in_local_stack` | v5 assembly/direct sign files provide direct threshold sign. |

## 4. File Review

| file | status | covering | threshold | endpoint sign | lower crossing | finite | direct sign |
|---|---|---:|---:|---:|---:|---:|---:|
| `Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Closure_Update_v1.md` | `closure_support` | True | False | False | False | False | False |
| `Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Conditional_Theorem_v1.md` | `conditional` | True | False | True | False | False | False |
| `Prime_Mesh_R2Q_FirstCrossing_Covering_Localization_Target_v1.md` | `candidate` | True | False | True | False | True | False |
| `Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Closure_Update_v1.md` | `closure_support` | False | True | False | False | True | False |
| `Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Proof_Target_v1.md` | `proof_target` | True | True | True | False | False | False |
| `Prime_Mesh_R2Q_FullFCL_Closure_Update_v1.md` | `conditional_support` | True | False | True | False | True | False |
| `Prime_Mesh_R2Q_FullFCL_Formal_Proof_Skeleton_v1.md` | `proof_target` | True | True | True | False | False | False |
| `Prime_Mesh_R2Q_FullFCL_Formal_Theorem_Target_v1.md` | `candidate` | True | True | True | False | True | False |
| `Prime_Mesh_R2Q_FullFCL_Reclosure_Update_v2.md` | `conditional_support` | True | True | True | False | False | False |
| `Prime_Mesh_R2Q_FiniteThetaEnvelope_Certificate_Spec_v1.md` | `candidate` | True | False | False | False | True | False |
| `Prime_Mesh_R2Q_FiniteThetaEnvelope_Closure_Update_v1.md` | `closure_support` | False | False | False | False | True | False |
| `Prime_Mesh_R2Q_GlobalThetaEnvelope_Reclosure_Update_v2.md` | `closure_support` | False | True | True | False | True | False |
| `Prime_Mesh_R2Q_Theta_FirstCrossing_Final_Conditional_Assembly_v1.md` | `conditional` | True | False | True | True | True | False |
| `Prime_Mesh_R2Q_Final_Conditional_RH_Assembly_Update_v5.md` | `conditional` | False | False | False | False | True | True |
| `Prime_Mesh_R2Q_FirstCrossing_Localization_Theorem_Target_v1.md` | `target` | True | True | False | True | True | True |

## 5. Statement Inventory

Key statements were extracted to `prime_mesh_r2q_firstcrossing_localization_statement_inventory.csv`.

Important audit finding: existing theta assembly states positive first crossings give `E_theta>0`, while negative first crossings give `E_theta<0`. The target theorem needs a unified `E_theta>=0` orientation or a signed split.

## 6. v5 Compatibility

The bridge must use direct threshold sign and must not rely on `Q_R2Q>0.75 => Q_delta_D>0.75`.

## 7. Data Cross-Check

Threshold relevance and theta/covering CSVs are present and support the empirical/conditional layers, but they do not by themselves prove the analytic localization theorem.

## 8. Gaps

| gap | status | detail | recommended file |
|---|---|---|---|
| Endpoint sign orientation | `open` | Need theorem that selected first-crossing row has E_theta>=0 in the target orientation, or split upper/lower signs. | `Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Proof_Attack_v1.md` |
| Lower crossing handling | `open` | Current theta assembly says negative first crossing gives E_theta<0; global contradiction needs signed reorientation or a separate lower-crossing theorem. | `Prime_Mesh_R2Q_FirstCrossing_LowerCrossing_SignedOrientation_Target_v1.md` |
| Covering and threshold relevance remain conditional | `conditional` | Audits and conditional theorems support row covering and threshold relevance, but they are not final analytic proof from first principles. | `Prime_Mesh_R2Q_FirstCrossing_Localization_Conditional_Closure_Update_v1.md` |
| Finite/von Koch bridge | `available_but_final_assembly_needed` | Finite theta envelope and von Koch target are present; final theorem must thread them after localization is proved. | `Prime_Mesh_R2Q_vonKoch_RHScale_Bridge_Theorem_Target_v1.md` |

## 9. Recommended Next File

`Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Proof_Attack_v1.md`.

## 10. Outputs

```text
prime_mesh_r2q_firstcrossing_localization_audit.py
prime_mesh_r2q_firstcrossing_localization_audit_summary.csv
prime_mesh_r2q_firstcrossing_localization_file_review.csv
prime_mesh_r2q_firstcrossing_localization_statement_inventory.csv
prime_mesh_r2q_firstcrossing_localization_lemma_status.csv
prime_mesh_r2q_firstcrossing_localization_v5_compatibility.csv
prime_mesh_r2q_firstcrossing_localization_gaps.csv
prime_mesh_r2q_firstcrossing_localization_data_crosscheck.csv
prime_mesh_r2q_firstcrossing_localization_fullfcl_review.csv
prime_mesh_r2q_firstcrossing_localization_theta_review.csv
prime_mesh_r2q_firstcrossing_localization_threshold_review.csv
```

*AI documentation pass: GPT-5.5*