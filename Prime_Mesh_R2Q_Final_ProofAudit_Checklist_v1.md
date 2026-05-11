# Prime Mesh R2Q â€” Final ProofAudit Checklist v1

**Document:** `Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md`  
**Project:** Prime Mesh Theory â€” RH Programme  
**Date:** 2026-05-11  
**Status:** Final proof-audit and reproducibility checklist  
**Purpose:** Convert the certificate-level RH-scale paper draft into a proof-audit package before any external mathematical claim.

---

## 1. Executive Verdict

The Prime Mesh R2Q stack has reached a coherent **certificate-level GlobalBridge closure for the active theta bridge**:

\[
G(x)=\theta(x)-x.
\]

The active envelope is:

\[
\mathcal E_\theta(x)=1.9233607946440099\sqrt{x}\log^2x.
\]

The current final certificate stack claims:

\[
\text{no post-}P_0\text{ first-exit obstruction survives}
\]

for the active theta bridge, with \(P_0=500,000,000\).

Before any public or formal claim, every item in this checklist should be verified.

The safest current status remains:

\[
\boxed{
\text{certificate-level theta bridge route to RH-scale Chebyshev/von Koch control}.
}
\]

Do **not** state â€œRH is provenâ€ until the proof-audit and external reproducibility checks pass.

---

## 2. Core Claim to Audit

The current paper-safe main claim is:

> For the active theta bridge \(G(x)=\theta(x)-x\), the Prime Mesh R2Q certificate stack rules out post-\(P_0\) first-exit obstructions for the envelope \(1.9233607946440099\sqrt{x}\log^2x\). Candidate windows, lower brackets, ThresholdRelevance, local obstruction closure, and all coordinate gaps are certificate-closed. Combined with finite-zone certificates and the standard theta-to-psi transfer, this gives a certificate-level route to the von Koch RH-scale criterion.

The proof-audit must verify each clause independently.

---

## 3. Master Dependency Graph

The final certificate stack depends on these layers:

\[
\text{Finite certificates}
\]

\[
+\ \text{H-Exc sampled-grid closure}
\]

\[
+\ \text{Endpoint direct threshold sign}
\]

\[
+\ \text{Positive harmlessness}
\]

\[
+\ \text{O2 repayment}
\]

\[
+\ \text{B3 no-accumulation}
\]

\[
+\ \text{NeutralClause emptiness}
\]

\[
+\ \text{UpperLowerSplit}
\]

\[
+\ \text{CoveringLocalization}
\]

\[
+\ \text{ThresholdRelevance}
\]

\[
+\ \text{Post-}P_0\text{ ContinuousWindowSelection}
\]

\[
+\ \text{CandidateGap margin safety}
\]

\[
+\ \theta\text{-to-}\psi\text{ transfer}
\]

\[
+\ \text{von Koch criterion}.
\]

Each layer must be independently reproducible or clearly marked conditional/certificate-backed.

---

## 4. Required Final Artifacts

Verify these MD files exist and match current claims:

```text
Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md
Prime_Mesh_R2Q_GlobalBridge_FinalCertificate_Closure_Update_v1.md
Prime_Mesh_R2Q_ThetaBridge_vonKoch_RHScale_Conclusion_Target_v1.md
Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Certificate_Closure_Update_v1.md
Prime_Mesh_R2Q_NormalizedError_GapMargin_Audit_v1.md
Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Conditional_Closure_Update_v1.md
Prime_Mesh_R2Q_GlobalBridge_ConditionalAssembly_Closure_Update_v1.md
Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md
Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Closure_Update_v1.md
Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md
Prime_Mesh_R2Q_Final_Conditional_RH_Assembly_Update_v5.md
Prime_Mesh_R2Q_FiniteCertificate_Index_v1.md
```

---

## 5. Required Final CSVs / Data Artifacts

Verify these data outputs exist, open, and reproduce the stated counts:

```text
prime_mesh_r2q_normalized_error_gapmargin_summary.csv
prime_mesh_r2q_normalized_error_gapmargin_rows.csv
prime_mesh_r2q_normalized_error_gapmargin_margin_safe.csv
prime_mesh_r2q_normalized_error_gapmargin_risk.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_summary.csv
prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_failures.csv
prime_mesh_r2q_postp0_continuous_window_selection_summary.csv
prime_mesh_r2q_postp0_continuous_window_selection_gap_scan.csv
prime_mesh_r2q_postp0_continuous_window_selection_interval_audit.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_summary.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_rows.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_unknown.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_failures.csv
prime_mesh_r2q_firstcrossing_endpointsign_summary.csv
prime_mesh_r2q_firstcrossing_endpointsign_upper_lower.csv
prime_mesh_r2q_o2_repayment_closure_summary.csv
prime_mesh_r2q_b3_noaccumulation_summary.csv
prime_mesh_r2q_neutral_clause_closure_summary.csv
deposit_manifest.csv
```

---

## 6. Script Reproducibility Checklist

For every audit script in the final chain:

```text
[ ] Script exists.
[ ] Script compiles with python -m py_compile.
[ ] Script runs from a clean checkout / clean folder.
[ ] Script uses relative or documented paths.
[ ] Script writes deterministic outputs.
[ ] Script records source input files.
[ ] Script writes summary CSV.
[ ] Script writes row-level CSV where applicable.
[ ] Script writes failure CSV even if empty.
[ ] Script updates deposit_manifest.csv.
[ ] Re-running script does not change row counts unexpectedly.
```

Critical scripts include:

```text
prime_mesh_r2q_normalized_error_gapmargin_audit.py
prime_mesh_r2q_candidate_gap_firstexit_impossibility_audit.py
prime_mesh_r2q_postp0_continuous_window_selection_audit.py
prime_mesh_r2q_firstcrossing_thresholdrelevance_audit.py
prime_mesh_r2q_firstcrossing_endpointsign_audit.py
prime_mesh_r2q_firstcrossing_coveringlocalization_audit.py
prime_mesh_r2q_o2_repayment_closure_audit.py
prime_mesh_r2q_b3_noaccumulation_audit.py
prime_mesh_r2q_neutral_clause_closure_audit.py
```

---

## 7. Numerical Count Verification

Verify every number below directly from CSVs.

### Candidate windows

```text
[ ] post-P0 audited windows = 142
[ ] covered audited windows = 142
[ ] uncovered audited windows = 0
[ ] upper audited candidates = 120
[ ] upper represented = 120
[ ] lower audited candidates = 22
[ ] lower bracketed = 22
[ ] P0 transition gap = 0
```

### Coordinate gaps

```text
[ ] coordinate gaps = 141
[ ] margin-safe gaps = 141
[ ] upper-risk gaps = 0
[ ] lower-risk gaps = 0
[ ] prime jumps inventoried inside gaps = 22637
```

### Gap margin bounds

```text
[ ] G(x) = theta(x) - x
[ ] envelope = C_theta * sqrt(x) * log(x)^2
[ ] C_theta = 1.9233607946440099
[ ] R_upper_global_max = -0.0006006774736066138
[ ] R_lower_global_min = -0.0007553068873594187
[ ] all gap rows satisfy R_upper_max_bound < 1
[ ] all gap rows satisfy R_lower_min_bound > -1
```

### ThresholdRelevance

```text
[ ] threshold relevance rows = 10140
[ ] threshold relevance failures = 0
[ ] Q_R2Q > 0.75 rows = 24
[ ] Q_R2Q <= 0.75 rows = 10115
[ ] subthreshold unclassified rows = 0
[ ] dangerous rows above threshold = 24/24
[ ] forbidden rows above threshold = 11/11
```

### EndpointSign

```text
[ ] E_theta is raw
[ ] orientation variable = local_theta_sign
[ ] upper crossings = 1320
[ ] upper nonpositive E_theta = 0
[ ] lower crossings = 148
[ ] lower nonnegative E_theta = 0
[ ] lower surviving unrepaid rows = 0
```

### O2/B3/Neutral

```text
[ ] O2 repayment failures = 0
[ ] O2 cap max < 0.05
[ ] B3 noaccumulation failures = 0
[ ] Neutral rows = 0
[ ] minimum |E_theta| = 1.5258205110753806
```

---

## 8. Theorem Scope Checklist

Verify each theorem is scoped correctly.

### H-Exc

```text
[ ] H-Exc is stated as sampled-grid only.
[ ] T_J is defined.
[ ] No full integer-grid claim is made.
[ ] Full-grid lifting is marked false / not available.
```

### EndpointMotion

```text
[ ] Direct sign transfer is used:
    Q_R2Q > 0.75 => E_theta < 0.
[ ] Failed delta-threshold route is not used:
    Q_R2Q > 0.75 => Q_delta_D > 0.75.
[ ] hexc_00040 is noted as counterexample to the delta route.
```

### UpperLowerSplit

```text
[ ] E_theta is raw.
[ ] local_theta_sign is orientation data.
[ ] Upper rows close by positive harmlessness.
[ ] Lower rows close by O2/B3/finite/non-surviving safety.
[ ] No claim says all first crossings have E_theta > 0.
```

### ThresholdRelevance

```text
[ ] The theorem is contrapositive/certificate-backed.
[ ] It does not claim every row has Q_R2Q > 0.75.
[ ] It says surviving first-crossing obstruction => Q_R2Q > 0.75.
[ ] Subthreshold rows are all classified.
```

### CandidateGap

```text
[ ] Sparse windows are not claimed to tile all coordinates.
[ ] Gap safety is certified by normalized theta margin.
[ ] Active bridge is explicitly theta(x)-x.
[ ] The gap certificate is not claimed for other G(x) unless audited.
```

---

## 9. Classical Bridge Checklist

The paper must include a clean classical section.

### Theta-to-psi transfer

Prove or cite:

\[
\psi(x)=\theta(x)+\sum_{k\ge2}\sum_{p^k\le x}\log p.
\]

Then prove:

\[
\psi(x)-\theta(x)=O(\sqrt{x}\log^2x).
\]

Checklist:

```text
[ ] Prime-power correction is defined.
[ ] Bound uses standard theta(y)=O(y) or equivalent.
[ ] Sum over k >= 2 is justified.
[ ] Transfer from theta bound to psi bound is explicit.
```

### von Koch criterion

State or cite:

\[
\psi(x)-x=O(\sqrt{x}\log^2x)
\Longleftrightarrow
\mathrm{RH}.
\]

Checklist:

```text
[ ] Criterion is stated with correct function.
[ ] Big-O constants are allowed.
[ ] Domain x -> infinity is clear.
[ ] Finite-zone behavior is irrelevant to asymptotic criterion or separately certified.
```

---

## 10. Constants and Normalization Checklist

The proof must not hide where constants come from.

```text
[ ] C_theta = 1.9233607946440099 is defined.
[ ] It is identified as certificate-selected or derived.
[ ] Minimum allowed C_theta is documented.
[ ] Logs are natural logarithms.
[ ] theta(x) convention is stated.
[ ] P0 = 500,000,000 is stated.
[ ] Any finite-zone cutoff is stated.
[ ] All thresholds 0.75, 0.305, 0.025, 0.03 are defined.
```

---

## 11. Failure / Counterexample Checklist

Explicitly mention known failed routes.

```text
[ ] Do not use Q_R2Q > 0.75 => Q_delta_D > 0.75.
[ ] Mention hexc_00040 counterexample if discussing old route.
[ ] Do not use amplitude route for H-Exc.
[ ] Do not use full-grid H-Exc.
[ ] Do not claim independent Rayleigh constants where only coupled/product closure holds.
[ ] Do not claim B3 chain-indexed closure if only row-level closure is audited.
```

---

## 12. Certificate vs Symbolic Proof Labels

Every main result should be labeled:

```text
symbolic
certificate-backed
conditional
finite certificate
sampled-grid
row-level
active-theta-bridge-only
```

Suggested labels:

| Result | Label |
|---|---|
| H-Exc endpoint affine residual | sampled-grid certificate-backed |
| PrimeShockBridge | sampled-grid certificate-backed |
| Endpoint direct sign | certificate-backed / audited |
| O2 repayment | numeric certificate-backed |
| B3 noaccumulation | row-level certificate-backed |
| NeutralClause | empty certificate |
| ThresholdRelevance | FullFCL-backed certificate conditional |
| CandidateGap margin safety | active-theta-bridge certificate |
| GlobalBridge final closure | active-theta-bridge certificate-level |
| RH conclusion | conditional on certificate stack + classical bridge |

---

## 13. External Reviewer Package

Prepare a reviewer folder containing:

```text
README.md
environment.yml or requirements.txt
all audit scripts
all input CSVs
all output CSVs
deposit_manifest.csv
paper draft
proof audit checklist
```

README should include:

```text
[ ] How to run every audit.
[ ] Expected output filenames.
[ ] Expected row counts.
[ ] Expected max/min constants.
[ ] Known caveats.
[ ] How to verify no failed route is used.
```

---

## 14. Minimal Reproduction Command List

Create a shell or PowerShell script:

```text
run_all_final_audits.ps1
```

or:

```text
run_all_final_audits.py
```

It should run:

```text
python prime_mesh_r2q_normalized_error_gapmargin_audit.py
python prime_mesh_r2q_postp0_continuous_window_selection_audit.py
python prime_mesh_r2q_firstcrossing_thresholdrelevance_audit.py
python prime_mesh_r2q_firstcrossing_endpointsign_audit.py
python prime_mesh_r2q_o2_repayment_closure_audit.py
python prime_mesh_r2q_b3_noaccumulation_audit.py
python prime_mesh_r2q_neutral_clause_closure_audit.py
```

and compare outputs to expected values.

---

## 15. Red-Team Questions

Before sharing externally, answer these.

### Q1

Why does a certificate over audited candidates imply a global statement?

Expected answer:

Candidate windows are covered, coordinate gaps are margin-safe for the active theta bridge, and finite-zone certificates cover below \(P_0\).

### Q2

Why can no first exit occur in sparse coordinate gaps?

Expected answer:

The normalized theta ratio \(R_\theta(x)\) satisfies \(-1<R_\theta(x)<1\) throughout all 141 gaps, with certified global gap bounds.

### Q3

What prevents an upper first crossing?

Expected answer:

Upper crossings have \(E_\theta>0\), hence \(Q_{\rm R2Q}\le0.305<0.75\), contradicting ThresholdRelevance for surviving obstructions.

### Q4

What prevents a lower first crossing?

Expected answer:

Lower crossings have \(E_\theta<0\), but lower rows are O2/B3/finite/non-surviving safe; lower surviving unrepaid rows are zero.

### Q5

Where does RH enter?

Expected answer:

Through the classical theta-to-psi transfer and von Koch criterion after the theta bridge gives an RH-scale Chebyshev bound.

### Q6

Is this a symbolic proof or a certificate proof?

Expected answer:

Current status is certificate-level active-theta-bridge closure; symbolic/polished proof requires full reproducibility and formal presentation of the certificate stack.

---

## 16. Final Overclaim Guardrails

Do not write:

```text
We proved RH.
```

Use instead:

```text
We have a certificate-level Prime Mesh theta-bridge closure reaching the von Koch RH-scale criterion, pending external reproducibility and proof audit.
```

Do not write:

```text
All x are tiled by candidate windows.
```

Use instead:

```text
Candidate windows are sparse, but all coordinate gaps are margin-safe for the active theta bridge.
```

Do not write:

```text
H-Exc holds on the full integer grid.
```

Use instead:

```text
H-Exc is sampled-grid; full-grid lifting is not used.
```

Do not write:

```text
Threshold transfer is via Q_delta_D.
```

Use instead:

```text
The direct sign gate Q_R2Q > 0.75 => E_theta < 0 is used.
```

---

## 17. Recommended Next File

```text
Prime_Mesh_R2Q_Reproducibility_Runbook_v1.md
```

Purpose:

\[
\boxed{
\text{give exact commands, file paths, expected row counts, and expected hashes/values for reproducing the full certificate stack.}
}
\]

Alternative:

```text
Prime_Mesh_R2Q_Final_Paper_Abstract_and_Claims_v1.md
```

Purpose:

\[
\boxed{
\text{write a concise claims page suitable for sharing with a reviewer while avoiding overclaims.}
}
\]

---

## 18. Honest Final Status

The current work is strong and unusually complete for an exploratory proof programme.

But the next phase is not more theorem chasing. It is reproducibility, independent audit, and careful communication.

---

*Prime Mesh Theory â€” RH Programme*
