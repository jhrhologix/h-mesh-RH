# Prime Mesh R2Q â€” Reviewer Package Index v1

**Document:** `Prime_Mesh_R2Q_Reviewer_Package_Index_v1.md`  
**Project:** Prime Mesh Theory â€” RH Programme  
**Date:** 2026-05-11  
**Status:** Reviewer package index  
**Purpose:** Provide a clean reading order and artifact map for reviewing the certificate-level active theta-bridge closure.

---

## 1. Executive Purpose

This index tells a reviewer what to read, in what order, and why.

The current package is a **certificate-level Prime Mesh R2Q closure for the active theta bridge**

\[
G(x)=\theta(x)-x,
\]

with envelope

\[
1.9233607946440099\sqrt{x}\log^2x.
\]

The current reproducibility status is:

\[
\boxed{\texttt{PASS}}
\]

from the one-command runner:

```text
run_all_final_audits.py
```

The package should be reviewed as a certificate-backed, reproducible RH-scale bridge claim, not as an already peer-reviewed proof of RH.

---

## 2. Recommended Reading Order

### Stage 1 â€” Start Here

Read these first.

```text
README_REPRODUCIBILITY.md
Prime_Mesh_R2Q_Final_Paper_Abstract_and_Claims_v1.md
Prime_Mesh_R2Q_Final_Reproduction_PASS_Closure_Update_v1.md
```

Purpose:

- understand the safe claim;
- understand the active bridge;
- confirm the final reproduction status is PASS.

---

### Stage 2 â€” Reproduction / Verification Layer

Read these next.

```text
Prime_Mesh_R2Q_Reproducibility_Runbook_v1.md
Prime_Mesh_R2Q_RunAll_FinalAudits_Script_Spec_v1.md
Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md
prime_mesh_r2q_final_reproduction_report.csv
prime_mesh_r2q_final_artifact_hashes.txt
```

Purpose:

- understand how to rerun the audits;
- inspect expected counts;
- inspect the actual PASS report;
- verify artifact hashes.

---

### Stage 3 â€” Main Paper Draft

Read:

```text
Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md
```

Purpose:

- see the assembled proof/certificate narrative;
- inspect definitions;
- inspect theorem stack;
- inspect theta-to-\(\psi\) transfer and von Koch discussion.

---

### Stage 4 â€” Final Certificate Closure

Read:

```text
Prime_Mesh_R2Q_GlobalBridge_FinalCertificate_Closure_Update_v1.md
Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Certificate_Closure_Update_v1.md
Prime_Mesh_R2Q_ThetaBridge_vonKoch_RHScale_Conclusion_Target_v1.md
```

Purpose:

- inspect the final GlobalBridge certificate closure;
- inspect the coordinate-gap margin closure;
- inspect the classical RH-scale conclusion target.

---

### Stage 5 â€” Gap-Margin Audit

Read:

```text
Prime_Mesh_R2Q_NormalizedError_GapMargin_Audit_v1.md
prime_mesh_r2q_normalized_error_gapmargin_summary.csv
prime_mesh_r2q_normalized_error_gapmargin_rows.csv
prime_mesh_r2q_normalized_error_gapmargin_margin_safe.csv
prime_mesh_r2q_normalized_error_gapmargin_risk.csv
```

Purpose:

- verify \(141/141\) coordinate gaps are margin-safe;
- verify \(G(x)=\theta(x)-x\);
- verify \(C_\theta=1.9233607946440099\);
- verify the normalized bounds:
  \[
  R_{\rm upper,global,max}=-0.0006006774736066138,
  \]
  \[
  R_{\rm lower,global,min}=-0.0007553068873594187.
  \]

This is one of the most important review layers.

---

### Stage 6 â€” Candidate Coverage and Selection

Read:

```text
Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Audit_v1.md
Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Conditional_Closure_Update_v1.md
prime_mesh_r2q_postp0_continuous_window_selection_summary.csv
prime_mesh_r2q_postp0_continuous_window_selection_gap_scan.csv
prime_mesh_r2q_postp0_continuous_window_selection_interval_audit.csv
```

Purpose:

- verify \(142/142\) post-\(P_0\) audited windows are covered;
- verify \(120/120\) upper candidates are represented;
- verify \(22/22\) lower candidates are bracketed;
- verify \(P_0\) transition gap is \(0\).

---

### Stage 7 â€” ThresholdRelevance

Read:

```text
Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Audit_v1.md
Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md
prime_mesh_r2q_firstcrossing_thresholdrelevance_summary.csv
prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_failures.csv
```

Purpose:

- verify \(10{,}140\) rows checked;
- verify zero failures;
- verify \(24/24\) dangerous rows above threshold;
- verify \(11/11\) forbidden rows above threshold;
- verify \(10{,}115\) subthreshold rows have zero unclassified.

---

### Stage 8 â€” Endpoint Sign and Local Obstruction Closure

Read:

```text
Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Audit_v1.md
Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Closure_Update_v1.md
prime_mesh_r2q_firstcrossing_endpointsign_summary.csv
prime_mesh_r2q_firstcrossing_endpointsign_upper_lower.csv
```

Purpose:

- verify \(E_\theta\) is raw;
- verify `local_theta_sign` carries orientation;
- verify upper/lower split;
- verify lower surviving unrepaid rows are zero.

Then read:

```text
Prime_Mesh_R2Q_O2_Repayment_Closure_Audit_v1.md
Prime_Mesh_R2Q_B3_NoAccumulation_Audit_v1.md
Prime_Mesh_R2Q_NeutralClause_Closure_Audit_v1.md
```

Purpose:

- verify O2 repayment closure;
- verify B3 no-accumulation closure;
- verify NeutralClause emptiness.

---

### Stage 9 â€” H-Exc / Sampled-Grid Foundations

Read:

```text
Prime_Mesh_R2Q_HExc_LocalAffinity_EnergyBudget_Audit_v1.md
Prime_Mesh_R2Q_HExc_DN_Path_Definition_Extraction_v1.md
Prime_Mesh_R2Q_HExc_PrimeShockBridge_SampleGridStructure_Audit_v1.md
Prime_Mesh_R2Q_HExc_TJ_Grid_Extraction_Audit_v1.md
Prime_Mesh_R2Q_HExc_PrimeShockBridge_KernelGram_Audit_v1.md
Prime_Mesh_R2Q_HExc_PrimeShockBridge_RayleighCoupling_Audit_v1.md
```

Purpose:

- verify the H-Exc/local-affinity stack;
- confirm the proof is sampled-grid only;
- confirm full-grid H-Exc is not used;
- inspect the PrimeShockBridge/Rayleigh coupling support.

---

### Stage 10 â€” Proof Audit

Read:

```text
Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md
```

Purpose:

- verify every required theorem/certificate;
- check overclaim guardrails;
- prepare red-team review.

---

## 3. Artifact Categories

### A. Top-Level Reviewer Files

```text
README_REPRODUCIBILITY.md
Prime_Mesh_R2Q_Final_Paper_Abstract_and_Claims_v1.md
Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md
Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md
Prime_Mesh_R2Q_Reviewer_Package_Index_v1.md
```

### B. Reproduction Files

```text
run_all_final_audits.py
Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md
prime_mesh_r2q_final_reproduction_report.csv
prime_mesh_r2q_final_artifact_hashes.txt
final_audit_logs/
```

### C. Final Closure Files

```text
Prime_Mesh_R2Q_Final_Reproduction_PASS_Closure_Update_v1.md
Prime_Mesh_R2Q_GlobalBridge_FinalCertificate_Closure_Update_v1.md
Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Certificate_Closure_Update_v1.md
Prime_Mesh_R2Q_ThetaBridge_vonKoch_RHScale_Conclusion_Target_v1.md
```

### D. Core Audit Files

```text
Prime_Mesh_R2Q_NormalizedError_GapMargin_Audit_v1.md
Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Audit_v1.md
Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Audit_v1.md
Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Audit_v1.md
Prime_Mesh_R2Q_O2_Repayment_Closure_Audit_v1.md
Prime_Mesh_R2Q_B3_NoAccumulation_Audit_v1.md
Prime_Mesh_R2Q_NeutralClause_Closure_Audit_v1.md
```

### E. Supporting Repair Files

```text
Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Audit_v1.md
Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md
Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md
Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Closure_Update_v1.md
Prime_Mesh_R2Q_GlobalBridge_ConditionalAssembly_Closure_Update_v1.md
Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Conditional_Closure_Update_v1.md
Prime_Mesh_R2Q_ContinuousFirstExit_CandidateCompleteness_Audit_v1.md
Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Audit_v1.md
```

---

## 4. Key Numerical Results to Verify

### Active bridge

\[
G(x)=\theta(x)-x.
\]

### Envelope

\[
\mathcal E_\theta(x)
=
1.9233607946440099\sqrt{x}\log^2x.
\]

### Candidate windows

\[
142/142.
\]

### Upper candidates

\[
120/120.
\]

### Lower candidates

\[
22/22.
\]

### Coordinate gaps

\[
141/141\text{ margin-safe}.
\]

### ThresholdRelevance

\[
10140\text{ rows},\quad0\text{ failures}.
\]

### Gap bounds

\[
R_{\rm upper,global,max}
=
-0.0006006774736066138.
\]

\[
R_{\rm lower,global,min}
=
-0.0007553068873594187.
\]

### Prime jumps inside gaps

\[
22637.
\]

---

## 5. Reviewer Red Flags

A reviewer should flag any claim that says:

```text
RH is proven.
```

without qualifying the current result as certificate-level and pending independent review.

A reviewer should flag any use of:

\[
Q_{\rm R2Q}>0.75\Rightarrow Q_{\Delta D}>0.75.
\]

That route is rejected.

A reviewer should flag any claim that H-Exc is full-grid.

H-Exc is sampled-grid only.

A reviewer should flag any claim that candidate windows tile all coordinates.

They do not. Coordinate gaps are closed by normalized theta margin certificates.

A reviewer should flag any claim that the result automatically holds for every bridge \(G(x)\).

The active bridge is:

\[
G(x)=\theta(x)-x.
\]

---

## 6. Minimal Review Path

A fast reviewer can check:

1. `README_REPRODUCIBILITY.md`
2. `Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md`
3. `prime_mesh_r2q_normalized_error_gapmargin_summary.csv`
4. `prime_mesh_r2q_normalized_error_gapmargin_rows.csv`
5. `prime_mesh_r2q_firstcrossing_thresholdrelevance_summary.csv`
6. `Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md`
7. `Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md`

This verifies the core claim quickly.

---

## 7. Full Review Path

A full reviewer should:

1. Run:
   ```text
   python run_all_final_audits.py
   ```

2. Confirm:
   ```text
   Final certificate reproduction status: PASS
   ```

3. Review every audit note and CSV in the dependency graph.

4. Verify no failure CSV contains unexplained rows.

5. Verify hashes.

6. Review theorem scoping.

7. Review classical theta-to-\(\psi\) transfer.

8. Review von Koch criterion wording.

---

## 8. What the Package Currently Claims

The package claims:

\[
\boxed{
\text{one-command reproducible certificate-level closure for the active theta bridge.}
}
\]

It does not claim:

\[
\boxed{
\text{peer-reviewed proof of RH}.
}
\]

---

## 9. Recommended Next Step

After this index, the next useful document is:

```text
Prime_Mesh_R2Q_Final_Paper_v1.md
```

Purpose:

\[
\boxed{
\text{combine the paper draft, claims page, and closure updates into one continuous manuscript.}
}
\]

Alternatively:

```text
Prime_Mesh_R2Q_External_Review_Cover_Letter_v1.md
```

Purpose:

\[
\boxed{
\text{write a short, cautious letter to send with the reviewer package.}
}
\]

---

## 10. Honest Status

The package is ready to be organized for review.

The next work is presentation and external verification, not more internal repair.

---

*Prime Mesh Theory â€” RH Programme*
