# Prime Mesh R2Q â€” Reproducibility Runbook v1

**Document:** `Prime_Mesh_R2Q_Reproducibility_Runbook_v1.md`  
**Project:** Prime Mesh Theory â€” RH Programme  
**Date:** 2026-05-11  
**Status:** Reproducibility / reviewer runbook  
**Purpose:** Provide exact run order, expected files, expected row counts, and validation checks for reproducing the certificate-level theta bridge stack.

---

## 1. Executive Purpose

This runbook is the reproducibility layer for the current Prime Mesh R2Q certificate stack.

The active final bridge is:

\[
G(x)=\theta(x)-x.
\]

The active envelope is:

\[
\mathcal E_\theta(x)=C_\theta\sqrt{x}\log^2x,
\]

with:

\[
C_\theta=1.9233607946440099.
\]

The certificate-level claim to reproduce is:

\[
\boxed{
\text{no post-}P_0\text{ first-exit obstruction survives for the active theta bridge.}
}
\]

where:

\[
P_0=500,000,000.
\]

This runbook is designed so a reviewer can rerun the audits and check whether the claimed counts and constants reproduce.

---

## 2. Main Folder

Primary working folder:

```text
<package-root>
```

All scripts and outputs below are expected to live in that folder unless explicitly noted.

---

## 3. Required Environment

Minimum environment:

```text
Python 3.10+
pandas
numpy
```

Recommended validation command:

```text
python --version
python -m pip freeze > environment_freeze.txt
```

Optional:

```text
python -m pip install pandas numpy
```

If scripts use extra libraries, record them in:

```text
requirements.txt
```

or:

```text
environment.yml
```

---

## 4. Reproduction Principles

Every final audit script should satisfy:

```text
[ ] Can run from the main folder.
[ ] Uses documented input files.
[ ] Writes deterministic CSV outputs.
[ ] Writes a markdown report.
[ ] Writes a summary CSV.
[ ] Writes row-level data where applicable.
[ ] Writes failures CSV even when empty.
[ ] Updates deposit_manifest.csv.
[ ] Does not require hidden state.
```

No script should silently use:

\[
Q_{\rm R2Q}>0.75\Rightarrow Q_{\Delta D}>0.75.
\]

No script should silently upgrade H-Exc sampled-grid control to full-grid control.

---

## 5. Master Run Order

Run audits in this order.

### Step 1 â€” H-Exc / local affine / sampled-grid stack

These are earlier repair-layer audits. Verify their output files exist and pass.

Expected key outputs include:

```text
Prime_Mesh_R2Q_HExc_LocalAffinity_EnergyBudget_Audit_v1.md
Prime_Mesh_R2Q_HExc_DN_Path_Definition_Extraction_v1.md
Prime_Mesh_R2Q_HExc_PrimeShockBridge_SampleGridStructure_Audit_v1.md
Prime_Mesh_R2Q_HExc_TJ_Grid_Extraction_Audit_v1.md
Prime_Mesh_R2Q_HExc_PrimeShockBridge_KernelGram_Audit_v1.md
Prime_Mesh_R2Q_HExc_PrimeShockBridge_RayleighCoupling_Audit_v1.md
```

Critical expected facts:

```text
[ ] H-Exc is sampled-grid only.
[ ] Full-grid lift is not claimed.
[ ] post_P0 K_prime max <= 65.
[ ] T_J rule is extracted.
[ ] Direct sampled-grid theorem form preserved.
```

---

### Step 2 â€” EndpointMotion direct threshold sign

Run or verify:

```text
python prime_mesh_r2q_endpointmotion_thresholdtransfer_audit.py
```

Expected outputs:

```text
prime_mesh_r2q_endpointmotion_thresholdtransfer_summary.csv
prime_mesh_r2q_endpointmotion_thresholdtransfer_rows.csv
Prime_Mesh_R2Q_EndpointMotion_ThresholdTransfer_Audit_v1.md
```

Expected key facts:

```text
[ ] Q_R2Q > 0.75 => E_theta < 0 passes.
[ ] Q_R2Q > 0.75 => Q_delta_D > 0.75 fails on hexc_00040.
[ ] Direct sign route is used.
[ ] Failed delta route is not used.
```

Expected threshold rows:

```text
hexc_00000
hexc_00006
hexc_00040
```

---

### Step 3 â€” O2 repayment

Run:

```text
python prime_mesh_r2q_o2_repayment_closure_audit.py
```

Expected outputs:

```text
prime_mesh_r2q_o2_repayment_closure_summary.csv
prime_mesh_r2q_o2_repayment_closure_rows.csv
Prime_Mesh_R2Q_O2_Repayment_Closure_Audit_v1.md
```

Expected facts:

```text
[ ] rows audited = 1468
[ ] negative subthreshold rows = 145
[ ] post-P0 negative subthreshold rows = 21
[ ] surviving unrepaid negative subthreshold rows = 0
[ ] O2 repayment failures = 0
[ ] O2 cap max < 0.05
```

Expected O2 cap max:

```text
0.0499059549846063
```

---

### Step 4 â€” B3 no-accumulation

Run:

```text
python prime_mesh_r2q_b3_noaccumulation_audit.py
```

Expected outputs:

```text
prime_mesh_r2q_b3_noaccumulation_summary.csv
prime_mesh_r2q_b3_noaccumulation_rows.csv
Prime_Mesh_R2Q_B3_NoAccumulation_Audit_v1.md
```

Expected facts:

```text
[ ] rows audited = 1469
[ ] post-P0 rows = 142
[ ] accumulation-risk rows = 142
[ ] surviving unrepaid accumulation rows = 0
[ ] B3 numeric balance failures = 0
[ ] persistence failures = 0
[ ] B3 noaccumulation failures = 0
[ ] O2/B3 consistency = True
```

---

### Step 5 â€” NeutralClause

Run:

```text
python prime_mesh_r2q_neutral_clause_closure_audit.py
```

Expected outputs:

```text
prime_mesh_r2q_neutral_clause_closure_summary.csv
prime_mesh_r2q_neutral_clause_closure_by_tau.csv
Prime_Mesh_R2Q_NeutralClause_Closure_Audit_v1.md
```

Expected facts:

```text
[ ] neutral rows = 0 for all tested tolerances 0 through 1e-2
[ ] closest row = hexc_00359
[ ] minimum |E_theta| = 1.5258205110753806
[ ] threshold rows = 3
[ ] threshold-row minimum |E_theta| = 928.3530182520336
[ ] NeutralClause failures = 0
```

---

### Step 6 â€” EndpointSign upper/lower split

Run:

```text
python prime_mesh_r2q_firstcrossing_endpointsign_audit.py
```

Expected outputs:

```text
prime_mesh_r2q_firstcrossing_endpointsign_summary.csv
prime_mesh_r2q_firstcrossing_endpointsign_upper_lower.csv
Prime_Mesh_R2Q_FirstCrossing_EndpointSign_Audit_v1.md
```

Expected facts:

```text
[ ] classification = upper_lower_split
[ ] E_theta is raw
[ ] orientation variable = local_theta_sign
[ ] upper/positive crossings = 1320
[ ] upper nonpositive E_theta = 0
[ ] lower/negative crossings = 148
[ ] lower nonnegative E_theta = 0
[ ] lower surviving unrepaid rows = 0
[ ] lower O2/B3 safety = True
[ ] failed delta route used = False
[ ] direct threshold sign found = True
```

---

### Step 7 â€” CoveringLocalization

Run:

```text
python prime_mesh_r2q_firstcrossing_coveringlocalization_audit.py
```

Expected outputs:

```text
prime_mesh_r2q_firstcrossing_coveringlocalization_summary.csv
prime_mesh_r2q_firstcrossing_coveringlocalization_data_crosscheck.csv
Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Audit_v1.md
```

Expected facts:

```text
[ ] classification = conditional_theta_window_plus_finite_continuous
[ ] coverage mode = theta_window_covering
[ ] covered candidates = 1469
[ ] uncovered candidates = 0
[ ] coverage failures = 0
[ ] theta candidates = 1468/1468 covered
[ ] B3 candidates = 1/1 covered
[ ] finite zone continuous certificate passes
[ ] sign preservation passes
[ ] failed delta route used = False
[ ] full-grid H-Exc upgrade used = False
```

---

### Step 8 â€” ThresholdRelevance

Run:

```text
python prime_mesh_r2q_firstcrossing_thresholdrelevance_audit.py
```

Expected outputs:

```text
prime_mesh_r2q_firstcrossing_thresholdrelevance_summary.csv
prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_failures.csv
Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Audit_v1.md
```

Expected facts:

```text
[ ] classification = fullfcl_backed_certificate_conditional
[ ] rows checked = 10140
[ ] threshold relevance failures = 0
[ ] Q_R2Q > 0.75 rows = 24
[ ] Q_R2Q <= 0.75 rows = 10115
[ ] subthreshold unclassified rows = 0
[ ] dangerous rows = 24/24 above threshold
[ ] forbidden rows = 11/11 above threshold
[ ] failed delta route used = False
[ ] direct threshold sign found = True
```

---

### Step 9 â€” Post-P0 ContinuousWindowSelection

Run:

```text
python prime_mesh_r2q_postp0_continuous_window_selection_audit.py
```

Expected outputs:

```text
prime_mesh_r2q_postp0_continuous_window_selection_summary.csv
prime_mesh_r2q_postp0_continuous_window_selection_gap_scan.csv
prime_mesh_r2q_postp0_continuous_window_selection_interval_audit.csv
Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Audit_v1.md
```

Expected facts:

```text
[ ] classification = theta_window_certificate_conditional
[ ] post-P0 audited windows = 142
[ ] covered audited windows = 142
[ ] uncovered audited windows = 0
[ ] upper audited candidates represented = 120/120
[ ] lower audited candidates bracketed = 22/22
[ ] P0 transition gap = 0
[ ] full-grid H-Exc upgrade used = False
[ ] failed delta route used = False
```

---

### Step 10 â€” CandidateCompleteness

Run:

```text
python prime_mesh_r2q_continuous_firstexit_candidate_completeness_audit.py
```

Expected outputs:

```text
prime_mesh_r2q_continuous_firstexit_candidate_completeness_summary.csv
prime_mesh_r2q_continuous_firstexit_candidate_completeness_gap_safety.csv
Prime_Mesh_R2Q_ContinuousFirstExit_CandidateCompleteness_Audit_v1.md
```

Expected facts before gap-margin closure:

```text
[ ] classification = gap_safety_incomplete
[ ] candidate generator found = True
[ ] executable generator-match certificate = not found
[ ] post-P0 candidate rows = 142
[ ] upper candidates = 120
[ ] upper missing = 0
[ ] lower candidates = 22
[ ] lower unbracketed = 0
[ ] coordinate gaps = 141
[ ] gap safety proven = 0
[ ] gap safety unknown = 141
[ ] P0 transition passes
[ ] full-grid H-Exc upgrade used = False
[ ] failed delta route used = False
```

---

### Step 11 â€” CandidateGap FirstExitImpossibility

Run:

```text
python prime_mesh_r2q_candidate_gap_firstexit_impossibility_audit.py
```

Expected outputs:

```text
prime_mesh_r2q_candidate_gap_firstexit_impossibility_summary.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_rows.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_unknown.csv
Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Audit_v1.md
```

Expected facts before normalized margin audit:

```text
[ ] classification = envelope_margin_data_missing
[ ] gap inventory = 141/141
[ ] safe gaps classified = 0
[ ] unknown gaps = 141
[ ] upper-exit safety = unknown for all gaps
[ ] lower-drift safety = unknown for all gaps
[ ] envelope margin bounds available = False
[ ] per-gap R(x) data available = False
[ ] full-grid H-Exc upgrade used = False
[ ] failed delta route used = False
```

---

### Step 12 â€” NormalizedError GapMargin

Run:

```text
python prime_mesh_r2q_normalized_error_gapmargin_audit.py
```

Expected outputs:

```text
prime_mesh_r2q_normalized_error_gapmargin_summary.csv
prime_mesh_r2q_normalized_error_gapmargin_rows.csv
prime_mesh_r2q_normalized_error_gapmargin_margin_safe.csv
prime_mesh_r2q_normalized_error_gapmargin_risk.csv
Prime_Mesh_R2Q_NormalizedError_GapMargin_Audit_v1.md
```

Expected facts:

```text
[ ] classification = all_gaps_margin_safe
[ ] gaps = 141/141
[ ] margin_safe gaps = 141
[ ] upper-risk gaps = 0
[ ] lower-risk gaps = 0
[ ] G(x) = theta(x) - x
[ ] envelope = C_theta * sqrt(x) * log(x)^2
[ ] C_theta = 1.9233607946440099
[ ] R_upper_global_max = -0.0006006774736066138
[ ] R_lower_global_min = -0.0007553068873594187
[ ] prime jumps inventoried inside gaps = 22637
```

---

## 6. Final One-Command Runner

Create:

```text
run_all_final_audits.py
```

Recommended behavior:

1. Run all final audit scripts in order.
2. Capture stdout/stderr to logs.
3. Stop on nonzero exit.
4. Verify expected output files exist.
5. Parse summary CSVs.
6. Compare expected counts.
7. Write final report:

```text
prime_mesh_r2q_final_reproduction_report.csv
Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md
```

---

## 7. Expected Final Reproduction Report Fields

```text
audit_name
script_name
script_exists
py_compile_pass
run_pass
summary_file_exists
expected_counts_pass
failure_file_empty
manifest_updated
notes
```

Final result fields:

```text
all_scripts_compile
all_scripts_run
all_expected_counts_match
all_failure_files_empty
final_certificate_reproduced
```

---

## 8. Validation Snippets

Use Python to check key CSV values.

Example pattern:

```python
import pandas as pd

summary = pd.read_csv("prime_mesh_r2q_normalized_error_gapmargin_summary.csv")
print(summary.to_string(index=False))
```

A robust validation script should not rely on row order unless fixed.

---

## 9. Hashing / File Integrity

After final run, generate hashes:

```text
python - <<'PY'
from pathlib import Path
import hashlib

for p in sorted(Path(".").glob("prime_mesh_r2q_*")):
    if p.is_file() and p.suffix in {".csv", ".py", ".md"}:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        print(h, p.name)
PY
```

Save to:

```text
prime_mesh_r2q_final_artifact_hashes.txt
```

---

## 10. Reviewer README Outline

Create:

```text
README_REPRODUCIBILITY.md
```

Include:

```text
1. Project goal
2. Active bridge: theta(x)-x
3. Envelope and constant
4. Folder layout
5. Environment setup
6. How to run all audits
7. Expected key results
8. Known caveats
9. How to inspect failure files
10. What is certificate-backed vs symbolic
```

---

## 11. Known Caveats to Include in README

```text
[ ] This is certificate-level.
[ ] Active bridge is theta(x)-x.
[ ] H-Exc is sampled-grid.
[ ] Candidate windows are sparse; gaps are closed by margin certificate, not tiling.
[ ] Failed delta-threshold route is excluded.
[ ] B3 is row-level, not chain-indexed.
[ ] Finite certificates are part of the result.
[ ] External review is required before any RH proof claim.
```

---

## 12. Final Reviewer Claim

Safe wording:

> This repository contains a reproducible certificate stack for the Prime Mesh R2Q active theta bridge. The stack verifies that post-\(P_0\) candidate windows, lower brackets, ThresholdRelevance, local obstruction closure, and coordinate gaps close against first-exit obstructions for the envelope \(1.9233607946440099\sqrt{x}\log^2x\). The result is a certificate-level route to an RH-scale Chebyshev/von Koch criterion, pending independent review.

Unsafe wording:

> This proves RH.

---

## 13. Recommended Next File

```text
Prime_Mesh_R2Q_Final_Paper_Abstract_and_Claims_v1.md
```

Purpose:

\[
\boxed{
\text{write a concise, non-overclaiming claims page for reviewers.}
}
\]

Alternative engineering file:

```text
Prime_Mesh_R2Q_RunAll_FinalAudits_Script_Spec_v1.md
```

Purpose:

\[
\boxed{
\text{specify the one-command final audit runner.}
}
\]

---

## 14. Honest Status

The theorem stack is now at the reproducibility phase.

The most valuable next action is to make the certificate independently runnable.

---

*Prime Mesh Theory â€” RH Programme*
