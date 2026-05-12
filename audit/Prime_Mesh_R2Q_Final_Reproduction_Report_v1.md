# Prime Mesh R2Q — Final Reproduction Report v1

## 1. Run Metadata

- Timestamp: `2026-05-11T23:01:39`
- Working folder: `C:\Users\jhegy\source\repos\prime-mesh-theory\Hegyesy_Prime_Mesh_R2Q_ThetaBridge_Certificate_v1_2026-05\audit`
- Python: `3.13.1`
- Platform: `Windows-11-10.0.26200-SP0`
- Command flags: `default`

## 2. Executive Result

Final certificate reproduction status: PASS

## 3. Script Compilation and Run Status

| Audit | Compile | Run | Counts | Failure File | Status |
|---|---:|---:|---:|---:|---:|
| EndpointMotion ThresholdTransfer | True | True | True | False | PASS |
| O2 Repayment Closure | True | True | True | True | PASS |
| B3 NoAccumulation | True | True | True | True | PASS |
| NeutralClause Closure | True | True | True | True | PASS |
| FirstCrossing EndpointSign | True | True | True | True | PASS |
| FirstCrossing CoveringLocalization | True | True | True | True | PASS |
| FirstCrossing ThresholdRelevance | True | True | True | True | PASS |
| PostP0 ContinuousWindowSelection | True | True | True | False | PASS |
| ContinuousFirstExit CandidateCompleteness | True | True | True | False | PASS |
| CandidateGap FirstExitImpossibility | True | True | True | False | PASS |
| NormalizedError GapMargin | True | True | True | True | PASS |

## 4. Expected Count Checks

The runner checked the pinned reproducibility counts and constants from `README_REPRODUCIBILITY.md` and `Prime_Mesh_R2Q_RunAll_FinalAudits_Script_Spec_v1.md`.

## 5. Failure Files

Intermediate audits `PostP0 ContinuousWindowSelection`, `ContinuousFirstExit CandidateCompleteness`, and `CandidateGap FirstExitImpossibility` are expected to contain conditional/gap-safety failure rows before `NormalizedError GapMargin` closes the coordinate gaps. Final certificate failure files are required to be empty.

## 6. Key Final Constants

- `C_theta`: `1.9233607946440099`
- `R_upper_global_max`: `-0.0006006774736066138`
- `R_lower_global_min`: `-0.0007553068873594187`
- Prime jumps inside gaps: `22637`

## 7. Artifact Hashes

Hashes written to `prime_mesh_r2q_final_artifact_hashes.txt`.

## 8. Warnings

- None.

## 9. Critical Failures

- None.

## 10. Final Certificate Status

Final certificate reproduction status: PASS

*AI documentation pass: GPT-5.5*