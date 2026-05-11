# Prime Mesh R2Q — B3 NoAccumulation Audit v1

**Date:** 2026-05-10

## 1. Scope

Audit no surviving unrepaid accumulation paths after H-Exc, EndpointMotion, and O2 closure.

## 2. Summary

- B3 mode: `dedicated_B3`.
- Rows: `1469`; post-P0 rows: `142`.
- Accumulation-risk rows: `142`.
- Surviving unrepaid accumulation rows: `0`.
- B3 numeric balance min: `-0.0`.
- B3 numeric failures: `0`.
- Zero/persistence failures: `0`.
- B3 noaccumulation failures: `0`.
- Best closure form: `B3_numeric_noaccumulation`.

## 3. Data Availability

Fields found: `B3_value;B3_balance;B3_margin;B3_repaid_flag;B3_surviving_flag;B3_block_pass`.

Accumulation fields found: `accumulation_value;accumulation_balance;accumulation_margin;accumulation_risk_flag;unrepaid_tail;tail_candidate_flag`.

## 4. Accumulation-Risk Rows

| candidate | p_star | Q_tail_max | Q_R2Q | finite | O2_safe | B3_pass | surviving_unrepaid |
|---:|---:|---:|---:|---:|---:|---:|---:|
| b3_00041 | 604672261 | 0.26027059 | 0.75685966 | False | True | True | False |
| b3_00064 | 604810421 | 0.19519148 | 0.44945681 | False | True | True | False |
| b3_00105 | 604432601 | 0.13388996 | 0.29148119 | False | True | True | False |
| b3_00184 | 604356173 | 0.082350082 | 0.28191696 | False | True | True | False |
| b3_00208 | 604822567 | 0.072029121 | 0.10303067 | False | True | True | False |
| b3_00215 | 604883911 | 0.069713648 | 0.12861532 | False | True | True | False |
| b3_00219 | 604167899 | 0.069092969 | 0.15509425 | False | True | True | False |
| b3_00223 | 604848841 | 0.06763465 | 0.13562307 | False | True | True | False |
| b3_00228 | 604708931 | 0.066325273 | 0.12801365 | False | True | True | False |
| b3_00297 | 604724143 | 0.044787103 | 0.14445938 | False | True | True | False |

## 5. Numeric B3 Balance

`pass_B3_numeric_balance = True`.

The audited accumulation proxy is zero across the B3 table, so the derived B3 balance/margin has no negative rows.

## 6. O2 Consistency

Negative subthreshold rows: `145`.

Negative subthreshold accumulation-risk rows: `21`.

Negative subthreshold surviving unrepaid accumulation rows: `0`.

`pass_O2_B3_consistency = True`.

## 7. Chain / Zero-Crossing Analysis

Chain mode: `no_chain_ids_available`.

Zero-crossing rows available: `1469`; total crossing flags: `1`.

`pass_zero_crossing_persistence = True`.

## 8. Neutral Rows

| tau | neutral rows | accumulation risk | surviving unrepaid | threshold rows |
|---:|---:|---:|---:|---:|
| 1e-12 | 0 | 0 | 0 | 0 |
| 1e-10 | 0 | 0 | 0 | 0 |
| 1e-08 | 0 | 0 | 0 | 0 |
| 1e-06 | 0 | 0 | 0 | 0 |
| 1e-04 | 0 | 0 | 0 | 0 |

## 9. Counterexamples

Counterexample rows emitted: `0`.

No B3 accumulation, numeric, persistence, or chain counterexamples were found.

## 10. Recommended Theorem Form

`B3_numeric_noaccumulation`.

## 11. Recommended Next File

`Prime_Mesh_R2Q_B3_NoAccumulation_Theorem_Target_v1.md`.

## 12. Outputs

```text
prime_mesh_r2q_b3_noaccumulation_audit.py
prime_mesh_r2q_b3_noaccumulation_summary.csv
prime_mesh_r2q_b3_noaccumulation_rows.csv
prime_mesh_r2q_b3_noaccumulation_by_regime.csv
prime_mesh_r2q_b3_noaccumulation_counterexamples.csv
prime_mesh_r2q_b3_noaccumulation_failures.csv
prime_mesh_r2q_b3_noaccumulation_chain_summary.csv
prime_mesh_r2q_b3_noaccumulation_neutral_rows.csv
prime_mesh_r2q_b3_noaccumulation_threshold_rows.csv
prime_mesh_r2q_b3_noaccumulation_o2_consistency.csv
prime_mesh_r2q_b3_noaccumulation_zero_crossings.csv
```

*AI documentation pass: GPT-5.5*