# Prime Mesh R2Q — CandidateGap FirstExitImpossibility Audit v1

**Date:** 2026-05-11

## 1. Scope

Classify 141 coordinate gaps between sparse post-`P0` candidates.

## 2. Summary

- Gap safety classification: `envelope_margin_data_missing`.
- Gap count actual/expected: `141/141`.
- Unknown gaps: `141`.
- Failure/gap records: `141`.
- Uses full-grid H-Exc upgrade: `False`.
- Uses failed delta route: `False`.
- Pass audit: `False`.

## 3. Gap Inventory

`gap_inventory_pass=True`.

## 4. Safety Classes

| class | rows |
|---|---:|
| `unknown` | `141` |

## 5. Upper-Exit Safety

No per-gap jump-event inventory or upper-ratio monotonic certificate was available, so upper-exit safety is unknown for the gaps.

## 6. Lower-Drift Safety

Only aggregate audited lower-candidate bracketing exists. No per-gap lower drift interval mapping was available.

## 7. Unknown Gaps

Unknown gap rows emitted: `141`.

Needed repair data/lemma: `normalized_error_gap_bounds_or_generator_gap_contradiction_certificate`.

## 8. v5 Compatibility

- Full-grid H-Exc upgrade: `False`.
- Failed delta route: `False`.

## 9. Conclusion

`All gaps remain unknown because per-gap normalized error/envelope margin, jump-event, lower-bracket, and generator-contradiction data are unavailable.`

## 10. Recommended Next File

`Prime_Mesh_R2Q_NormalizedError_GapMargin_Audit_Spec_v1.md`.

## 11. Outputs

```text
prime_mesh_r2q_candidate_gap_firstexit_impossibility_audit.py
prime_mesh_r2q_candidate_gap_firstexit_impossibility_summary.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_rows.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_by_class.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_unknown.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_failures.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_upper.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_lower.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_jump_events.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_margin_bounds.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_v5_compatibility.csv
```

*AI documentation pass: GPT-5.5*