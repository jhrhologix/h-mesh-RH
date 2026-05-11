# Prime Mesh R2Q — NormalizedError GapMargin Audit v1

**Date:** 2026-05-10

## 1. Scope

Generate per-gap normalized theta-error margin data for the 141 coordinate gaps.

## 2. Summary

- Classification: `all_gaps_margin_safe`.
- Gap count: `141`.
- Gaps with continuous margin bounds: `141`.
- Margin-safe gaps: `141`.
- Upper-risk gaps: `0`.
- Lower-risk gaps: `0`.
- Missing-data gaps: `0`.
- Global error process: `theta(x)-x`.
- Envelope: `C_theta*sqrt(x)*log(x)^2`.
- Envelope constant used: `1.9233607946440099`.
- Pass audit: `True`.

## 3. Margin Extremes

- `R_upper_global_max`: `-0.0006006774736066138`.
- `R_lower_global_min`: `-0.0007553068873594187`.
- Minimum upper margin to `1`: `1.0006006774736067`.
- Minimum lower margin to `-1`: `0.9992446931126406`.
- Prime jumps inside gaps: `22637`.

## 4. Interpretation

The audit uses the theta bridge because the active GlobalThetaEnvelope files define `G(x)=theta(x)-x`. It uses the minimum required global constant `C_theta >= 1.9233607946440099`; larger constants only increase the safety margin.

## 5. v5 Compatibility

- Full-grid H-Exc upgrade: `False`.
- Failed delta route: `False`.

## 6. Recommended Next File

`Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Certificate_Closure_Update_v1.md`.

## 7. Outputs

```text
prime_mesh_r2q_normalized_error_gapmargin_audit.py
prime_mesh_r2q_normalized_error_gapmargin_summary.csv
prime_mesh_r2q_normalized_error_gapmargin_rows.csv
prime_mesh_r2q_normalized_error_gapmargin_margin_safe.csv
prime_mesh_r2q_normalized_error_gapmargin_risk.csv
prime_mesh_r2q_normalized_error_gapmargin_missing_data.csv
prime_mesh_r2q_normalized_error_gapmargin_failures.csv
prime_mesh_r2q_normalized_error_gapmargin_jump_inventory.csv
prime_mesh_r2q_normalized_error_gapmargin_by_process.csv
prime_mesh_r2q_normalized_error_gapmargin_sampled_only.csv
prime_mesh_r2q_normalized_error_gapmargin_data_requirements.csv
```

*AI documentation pass: GPT-5.5*