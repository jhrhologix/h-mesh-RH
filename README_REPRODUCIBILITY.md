# Prime Mesh R2Q — Reproducibility README

**Project:** Prime Mesh Theory — RH Programme  
**Author:** Jonathan Hegyesy  
**Date:** 2026-05-11  
**Status:** Reviewer-facing reproducibility guide  
**Scope:** Certificate-level active theta bridge reproduction package

---

## 1. Purpose

This folder contains the audit/certificate stack for the current Prime Mesh R2Q active theta bridge:

\[
G(x)=\theta(x)-x.
\]

The active RH-scale envelope is:

\[
\mathcal E_\theta(x)
=
1.9233607946440099\sqrt{x}\log^2x.
\]

The goal of the reproducibility package is to let a reviewer rerun the final audits and verify the certificate-level claim:

\[
\boxed{
\text{no post-}P_0\text{ first-exit obstruction survives for the active theta bridge.}
}
\]

The cutoff is:

\[
P_0=500,000,000.
\]

---

## 2. Current Claim

The safe claim is:

> This repository contains a certificate-level Prime Mesh R2Q closure for the active theta bridge \(G(x)=\theta(x)-x\). The stack audits post-\(P_0\) first-exit obstructions against the envelope \(1.9233607946440099\sqrt{x}\log^2x\). Candidate windows, lower brackets, ThresholdRelevance, local obstruction closure, and coordinate gaps are certificate-closed. This gives a certificate-level route to a Chebyshev/von Koch RH-scale criterion, pending independent verification.

Do **not** read this package as an externally accepted proof of RH without independent audit.

---

## 3. Main Results to Reproduce

The final expected headline results are:

### Active bridge

\[
G(x)=\theta(x)-x.
\]

### Envelope

\[
C_\theta\sqrt{x}\log^2x,
\]

with:

\[
C_\theta=1.9233607946440099.
\]

### Candidate windows

\[
142/142
\]

post-\(P_0\) audited windows covered.

### Upper candidates

\[
120/120
\]

represented.

### Lower candidates

\[
22/22
\]

bracketed.

### Coordinate gaps

\[
141/141
\]

coordinate gaps margin-safe.

### Gap normalized bounds

\[
R_{\rm upper,global,max}
=
-0.0006006774736066138,
\]

\[
R_{\rm lower,global,min}
=
-0.0007553068873594187.
\]

### ThresholdRelevance

\[
10140
\]

rows checked,

\[
0
\]

failures.

### Dangerous/forbidden rows

\[
24/24
\]

dangerous rows above threshold,

\[
11/11
\]

forbidden rows above threshold.

---

## 4. Folder Layout

All files are self-contained in this package folder (the root of the repository).
Run all scripts from this folder — no external dependencies or parent-directory files are required.

Expected contents:

```text
*.py       audit scripts
*.csv      audit inputs/outputs
*.md       audit notes and closure updates
deposit_manifest.csv
requirements.txt
run_all_final_audits.py
README_REPRODUCIBILITY.md
CITATION.cff
LICENSE
AUTHORSHIP_AND_NAMING.md
```

---

## 5. Environment

Minimum:

```text
Python 3.10+
pandas
numpy
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Check environment:

```bash
python --version
python -m pip freeze > environment_freeze.txt
```

---

## 6. One-Command Reproduction

```bash
python run_all_final_audits.py
```

Expected final outputs:

```text
Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md
prime_mesh_r2q_final_reproduction_report.csv
prime_mesh_r2q_final_artifact_hashes.txt
final_audit_logs/
```

The final report should say:

```text
Final certificate reproduction status: PASS
```

only if all critical scripts compile, run, and match expected counts.

---

## 7. Manual Reproduction Order

If running audits individually, use this order:

```bash
python prime_mesh_r2q_endpointmotion_thresholdtransfer_audit.py
python prime_mesh_r2q_o2_repayment_closure_audit.py
python prime_mesh_r2q_b3_noaccumulation_audit.py
python prime_mesh_r2q_neutral_clause_closure_audit.py
python prime_mesh_r2q_firstcrossing_endpointsign_audit.py
python prime_mesh_r2q_firstcrossing_coveringlocalization_audit.py
python prime_mesh_r2q_firstcrossing_thresholdrelevance_audit.py
python prime_mesh_r2q_postp0_continuous_window_selection_audit.py
python prime_mesh_r2q_continuous_firstexit_candidate_completeness_audit.py
python prime_mesh_r2q_candidate_gap_firstexit_impossibility_audit.py
python prime_mesh_r2q_normalized_error_gapmargin_audit.py
```

Earlier H-Exc/PrimeShock audits may also be rerun, but the final reproduction hinge is the stack above plus the already deposited repair outputs.

---

## 8. Critical Output Files

A reviewer should inspect these first.

```text
Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md
Prime_Mesh_R2Q_GlobalBridge_FinalCertificate_Closure_Update_v1.md
Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Certificate_Closure_Update_v1.md
Prime_Mesh_R2Q_NormalizedError_GapMargin_Audit_v1.md
Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Audit_v1.md
Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Audit_v1.md
Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Audit_v1.md
Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md
Prime_Mesh_R2Q_Reproducibility_Runbook_v1.md
```

Critical CSVs:

```text
prime_mesh_r2q_normalized_error_gapmargin_summary.csv
prime_mesh_r2q_normalized_error_gapmargin_rows.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_summary.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_rows.csv
prime_mesh_r2q_postp0_continuous_window_selection_summary.csv
prime_mesh_r2q_postp0_continuous_window_selection_gap_scan.csv
prime_mesh_r2q_firstcrossing_endpointsign_summary.csv
prime_mesh_r2q_o2_repayment_closure_summary.csv
prime_mesh_r2q_b3_noaccumulation_summary.csv
prime_mesh_r2q_neutral_clause_closure_summary.csv
deposit_manifest.csv
```

Note: `prime_mesh_r2q_firstcrossing_thresholdrelevance_rows.csv` contains the row-level
ThresholdRelevance data. The equivalent cross-check file is also available as
`prime_mesh_r2q_firstcrossing_thresholdrelevance_data_crosscheck.csv`.

---

## 9. Expected Validation Checks

### NormalizedError GapMargin

Expected:

```text
classification = all_gaps_margin_safe
gaps = 141/141
margin_safe gaps = 141
upper-risk gaps = 0
lower-risk gaps = 0
G(x) = theta(x) - x
C_theta = 1.9233607946440099
R_upper_global_max = -0.0006006774736066138
R_lower_global_min = -0.0007553068873594187
prime jumps inventoried inside gaps = 22637
```

### ThresholdRelevance

Expected:

```text
classification = fullfcl_backed_certificate_conditional
rows checked = 10140
threshold relevance failures = 0
Q_R2Q > 0.75 rows = 24
Q_R2Q <= 0.75 rows = 10115
subthreshold unclassified rows = 0
dangerous rows above threshold = 24/24
forbidden rows above threshold = 11/11
```

### Post-P0 ContinuousWindowSelection

Expected:

```text
classification = theta_window_certificate_conditional
post-P0 audited windows = 142
covered audited windows = 142
uncovered audited windows = 0
upper candidates represented = 120/120
lower candidates bracketed = 22/22
P0 transition gap = 0
```

### EndpointSign

Expected:

```text
classification = upper_lower_split
E_theta orientation = raw
orientation variable = local_theta_sign
upper crossings = 1320
upper nonpositive E_theta = 0
lower crossings = 148
lower nonnegative E_theta = 0
lower surviving unrepaid rows = 0
```

### O2 / B3 / Neutral

Expected:

```text
O2 repayment failures = 0
O2 cap max < 0.05
B3 noaccumulation failures = 0
Neutral rows = 0
minimum |E_theta| = 1.5258205110753806
```

---

## 10. Known Caveats

This package is certificate-level.

The active bridge is:

\[
G(x)=\theta(x)-x.
\]

The result is not automatically transferred to every alternative bridge \(G(x)\) unless separately audited.

H-Exc is sampled-grid only.

The candidate windows are sparse. They do not tile all coordinates. Coordinate gaps are closed by normalized theta margin certificates, not by tiling.

The failed route:

\[
Q_{\rm R2Q}>0.75\Rightarrow Q_{\Delta D}>0.75
\]

is not used.

The direct route is:

\[
Q_{\rm R2Q}>0.75\Rightarrow E_\theta<0.
\]

B3 is row-level, not chain-indexed.

Finite certificates are part of the result.

The theta-to-\(\psi\) transfer and von Koch criterion must be written/cited carefully in any paper.

---

## 11. How the First-Exit Closure Works

A post-\(P_0\) first exit is either:

1. inside an audited candidate/bracket window; or
2. inside a coordinate gap.

Candidate/bracket windows are closed by:

- ThresholdRelevance;
- upper/lower endpoint sign split;
- positive harmlessness;
- O2 repayment;
- B3 no-accumulation;
- finite/non-surviving safety;
- empty NeutralClause.

Coordinate gaps are closed by normalized margin:

\[
-1<R_\theta(x)<1
\]

throughout all 141 gaps.

Therefore no post-\(P_0\) first-exit obstruction survives in the certificate stack.

---

## 12. How This Relates to RH-Scale Control

The active certificate target is:

\[
\theta(x)-x=O(\sqrt{x}\log^2x).
\]

The classical transfer is:

\[
\theta(x)-x=O(\sqrt{x}\log^2x)
\Rightarrow
\psi(x)-x=O(\sqrt{x}\log^2x),
\]

because prime-power terms satisfy:

\[
\psi(x)-\theta(x)=O(\sqrt{x}\log^2x)
\]

by standard estimates.

Then the von Koch criterion relates:

\[
\psi(x)-x=O(\sqrt{x}\log^2x)
\]

to RH.

This package gives a certificate-level route to that criterion, not yet an externally accepted proof.

---

## 13. Red-Team Questions for Reviewers

### Q1. Do the final audit scripts reproduce the stated row counts?

Check the final reproduction report and summary CSVs.

### Q2. Are coordinate gaps actually safe?

Inspect:

```text
prime_mesh_r2q_normalized_error_gapmargin_rows.csv
```

Verify every row satisfies:

```text
R_upper_max_bound < 1
R_lower_min_bound > -1
```

### Q3. Are subthreshold rows all classified?

Inspect ThresholdRelevance output. Expected:

```text
subthreshold unclassified rows = 0
```

### Q4. Is the failed delta-threshold route used anywhere?

Search for:

```text
Q_delta_D > 0.75
Q_R2Q > 0.75 => Q_delta_D
```

It should appear only as a warning/rejected route.

### Q5. Is H-Exc being used as full-grid control?

It should not be. H-Exc remains sampled-grid only.

### Q6. Are finite certificates included?

Check:

```text
Prime_Mesh_R2Q_FiniteCertificate_Package_v1.md
deposit_manifest.csv
```

---

## 14. Reviewer-Safe Language

Use:

> certificate-level theta bridge closure

Use:

> reproducible audit stack

Use:

> route to the von Koch RH-scale criterion

Avoid:

> proof of RH

Avoid:

> unconditional theorem

Avoid:

> all \(x\) tiled by candidate windows

Avoid:

> H-Exc full-grid control

---

## 15. Suggested Reviewer Workflow

1. Read this README.
2. Read the final proof-audit checklist.
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python run_all_final_audits.py`
5. Open `Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md`
6. Verify the final status is PASS.
7. Inspect NormalizedError GapMargin rows.
8. Inspect ThresholdRelevance failures.
9. Inspect endpoint sign split.
10. Inspect finite certificate index.
11. Review the final paper draft.

---

## 16. Current Status

The package is ready for external review.

The one-command runner is implemented:

```text
run_all_final_audits.py
```

Expected result:

```text
Final certificate reproduction status: PASS
```

The next writing milestone is a cleaned paper draft with complete references for the theta-to-\(\psi\) transfer and von Koch criterion.

---

## 17. Citation

If you use or reference this work, please cite using `CITATION.cff` in this folder,
or as:

> Jonathan Hegyesy. *Hegyesy Prime Mesh R2Q ThetaBridge Certificate v1*. 2026.
> https://github.com/jhrhologix/h-mesh-RH

---

*Prime Mesh Theory — RH Programme*  
*Originator: Jonathan Hegyesy*
