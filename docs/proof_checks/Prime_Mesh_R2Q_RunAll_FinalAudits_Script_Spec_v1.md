# Prime Mesh R2Q — RunAll FinalAudits Script Spec v1

**Document:** `Prime_Mesh_R2Q_RunAll_FinalAudits_Script_Spec_v1.md`  
**Project:** Prime Mesh Theory — RH Programme  
**Date:** 2026-05-11  
**Status:** Engineering spec for one-command final certificate reproduction  
**Purpose:** Specify a single runner that compiles, runs, validates, and reports the full final Prime Mesh R2Q certificate audit stack.

---

## 1. Executive Purpose

The certificate-level theta bridge stack is now at the reproducibility phase.

This spec defines a one-command runner:

```text
run_all_final_audits.py
```

Its job is to reproduce the final audit stack and verify the expected headline results:

\[
G(x)=\theta(x)-x,
\]

\[
\mathcal E_\theta(x)=1.9233607946440099\sqrt{x}\log^2x,
\]

\[
142/142
\]

post-\(P_0\) candidate windows covered,

\[
141/141
\]

coordinate gaps margin-safe,

and

\[
10140
\]

ThresholdRelevance rows with zero failures.

The runner should create:

```text
Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md
prime_mesh_r2q_final_reproduction_report.csv
prime_mesh_r2q_final_artifact_hashes.txt
```

---

## 2. Working Folder

Primary folder:

```text
<package-root>
```

The runner should be placed in this folder:

```text
run_all_final_audits.py
```

It should run from the same folder.

---

## 3. Runner Responsibilities

The runner must:

```text
[ ] detect the working directory;
[ ] verify required scripts exist;
[ ] compile scripts with python -m py_compile;
[ ] run scripts in the correct order;
[ ] capture stdout/stderr logs;
[ ] verify required output files exist;
[ ] parse summary CSVs;
[ ] compare expected row counts / constants;
[ ] check failure CSVs are empty where expected;
[ ] generate SHA256 hashes for key artifacts;
[ ] write a final CSV report;
[ ] write a final MD report;
[ ] exit nonzero if any critical check fails.
```

---

## 4. Audit Run Order

The runner should execute these scripts in order if present.

### Core final scripts

```text
prime_mesh_r2q_endpointmotion_thresholdtransfer_audit.py
prime_mesh_r2q_o2_repayment_closure_audit.py
prime_mesh_r2q_b3_noaccumulation_audit.py
prime_mesh_r2q_neutral_clause_closure_audit.py
prime_mesh_r2q_firstcrossing_endpointsign_audit.py
prime_mesh_r2q_firstcrossing_coveringlocalization_audit.py
prime_mesh_r2q_firstcrossing_thresholdrelevance_audit.py
prime_mesh_r2q_postp0_continuous_window_selection_audit.py
prime_mesh_r2q_continuous_firstexit_candidate_completeness_audit.py
prime_mesh_r2q_candidate_gap_firstexit_impossibility_audit.py
prime_mesh_r2q_normalized_error_gapmargin_audit.py
```

### Optional earlier H-Exc / PrimeShock scripts

If present, run or at least compile:

```text
prime_mesh_r2q_hexc_local_affinity_energybudget_audit.py
prime_mesh_r2q_hexc_dn_residual_component_audit.py
prime_mesh_r2q_hexc_primeshock_samplegrid_structure_audit.py
prime_mesh_r2q_hexc_tj_grid_extraction_audit.py
prime_mesh_r2q_hexc_primeshock_kernelgram_audit.py
prime_mesh_r2q_hexc_primeshock_rayleighcoupling_audit.py
prime_mesh_r2q_hexc_highweight_clusterfactor_audit.py
prime_mesh_r2q_hexc_shortblock_cluster_audit.py
```

Recommended behavior:

- Missing optional H-Exc scripts should produce a warning, not fatal.
- Missing core final scripts should be fatal unless the runner is invoked with `--allow-missing`.

---

## 5. Command-Line Options

The runner should support:

```text
python run_all_final_audits.py
```

Optional flags:

```text
--dry-run
--compile-only
--allow-missing
--skip-run
--hash-only
--strict
--output-dir .
```

### Flag behavior

```text
--dry-run
```

Print planned scripts and checks without running.

```text
--compile-only
```

Compile scripts only.

```text
--allow-missing
```

Continue if a script is missing, but mark it in the report.

```text
--skip-run
```

Skip script execution and validate existing outputs only.

```text
--hash-only
```

Only generate artifact hashes.

```text
--strict
```

Treat optional missing files as failures.

---

## 6. Logs

Create a logs folder:

```text
final_audit_logs/
```

For each script:

```text
final_audit_logs/<script_name>.stdout.txt
final_audit_logs/<script_name>.stderr.txt
```

Also create:

```text
final_audit_logs/run_all_final_audits.log
```

---

## 7. Final Report CSV Schema

Write:

```text
prime_mesh_r2q_final_reproduction_report.csv
```

Columns:

```text
audit_name
script_name
script_exists
py_compile_pass
run_attempted
run_pass
stdout_log
stderr_log
summary_file
summary_file_exists
expected_counts_pass
failure_file
failure_file_exists
failure_file_empty
critical
status
notes
```

---

## 8. Final Report MD Outline

Write:

```text
Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md
```

Outline:

```text
# Prime Mesh R2Q — Final Reproduction Report v1

## 1. Run metadata
date/time, working folder, Python version, platform.

## 2. Executive result
PASS / FAIL.

## 3. Script compilation and run status
table.

## 4. Expected count checks
table.

## 5. Failure files
table.

## 6. Key final constants
C_theta, R_upper_global_max, R_lower_global_min.

## 7. Artifact hashes
location of hash file.

## 8. Warnings
missing optional scripts, lint timeouts, noncritical warnings.

## 9. Critical failures
if any.

## 10. Final certificate status
reproduced / not reproduced.
```

---

## 9. Expected Summary Checks

The runner should validate the following.

### EndpointMotion threshold transfer

Summary file:

```text
prime_mesh_r2q_endpointmotion_thresholdtransfer_summary.csv
```

Expected:

```text
direct sign transfer passes = True
Q_R2Q > 0.75 => E_theta < 0 = PASS
failed delta route = detected as failed / not used
threshold rows = 3
```

If exact column names vary, the runner should search summary key/value rows flexibly.

---

### O2 repayment

Summary file:

```text
prime_mesh_r2q_o2_repayment_closure_summary.csv
```

Expected:

```text
rows audited = 1468
negative subthreshold rows = 145
post-P0 negative subthreshold rows = 21
surviving unrepaid negative subthreshold rows = 0
O2 repayment failures = 0
O2 cap max = 0.0499059549846063
O2 cap max < 0.05
```

---

### B3 no-accumulation

Summary file:

```text
prime_mesh_r2q_b3_noaccumulation_summary.csv
```

Expected:

```text
rows audited = 1469
post-P0 rows = 142
accumulation-risk rows = 142
surviving unrepaid accumulation rows = 0
B3 noaccumulation failures = 0
O2/B3 consistency = True
```

---

### NeutralClause

Summary file:

```text
prime_mesh_r2q_neutral_clause_closure_summary.csv
```

Expected:

```text
neutral rows = 0
closest row = hexc_00359
minimum |E_theta| = 1.5258205110753806
threshold rows = 3
NeutralClause failures = 0
```

---

### EndpointSign

Summary file:

```text
prime_mesh_r2q_firstcrossing_endpointsign_summary.csv
```

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
lower O2/B3 safety = True
failed delta route used = False
direct threshold sign found = True
```

---

### CoveringLocalization

Summary file:

```text
prime_mesh_r2q_firstcrossing_coveringlocalization_summary.csv
```

Expected:

```text
classification = conditional_theta_window_plus_finite_continuous
coverage mode = theta_window_covering
covered candidates = 1469
uncovered candidates = 0
coverage failures = 0
theta candidates covered = 1468/1468
B3 candidates covered = 1/1
finite zone continuous certificate passes
sign preservation passes
failed delta route used = False
full-grid H-Exc upgrade used = False
```

---

### ThresholdRelevance

Summary file:

```text
prime_mesh_r2q_firstcrossing_thresholdrelevance_summary.csv
```

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
failed delta route used = False
direct threshold sign found = True
```

---

### PostP0 ContinuousWindowSelection

Summary file:

```text
prime_mesh_r2q_postp0_continuous_window_selection_summary.csv
```

Expected:

```text
classification = theta_window_certificate_conditional
post-P0 audited windows = 142
covered audited windows = 142
uncovered audited windows = 0
upper audited candidates represented = 120/120
lower audited candidates bracketed = 22/22
P0 transition gap = 0
full-grid H-Exc upgrade used = False
failed delta route used = False
```

---

### ContinuousFirstExit CandidateCompleteness

Summary file:

```text
prime_mesh_r2q_continuous_firstexit_candidate_completeness_summary.csv
```

Expected intermediate classification:

```text
classification = gap_safety_incomplete
post-P0 candidate rows = 142
upper candidates = 120
upper missing = 0
lower candidates = 22
lower unbracketed = 0
coordinate gaps = 141
gap safety proven = 0
gap safety unknown = 141
P0 transition passes
full-grid H-Exc upgrade used = False
failed delta route used = False
```

Note: This is expected as an intermediate audit before NormalizedError closes gaps.

---

### CandidateGap FirstExitImpossibility

Summary file:

```text
prime_mesh_r2q_candidate_gap_firstexit_impossibility_summary.csv
```

Expected intermediate classification:

```text
classification = envelope_margin_data_missing
gap inventory = 141/141
safe gaps classified = 0
unknown gaps = 141
envelope margin bounds available = False
per-gap R(x) data available = False
full-grid H-Exc upgrade used = False
failed delta route used = False
```

Note: This is expected as an intermediate audit before NormalizedError closes gaps.

---

### NormalizedError GapMargin

Summary file:

```text
prime_mesh_r2q_normalized_error_gapmargin_summary.csv
```

Expected final classification:

```text
classification = all_gaps_margin_safe
gaps = 141/141
margin safe gaps = 141
upper-risk gaps = 0
lower-risk gaps = 0
G(x) = theta(x) - x
envelope = C_theta * sqrt(x) * log(x)^2
C_theta = 1.9233607946440099
R_upper_global_max = -0.0006006774736066138
R_lower_global_min = -0.0007553068873594187
prime jumps inventoried inside gaps = 22637
```

This is a critical final check.

---

## 10. Failure File Checks

The runner should verify failure files exist and are empty or contain zero failure rows.

Important failure files:

```text
prime_mesh_r2q_firstcrossing_thresholdrelevance_failures.csv
prime_mesh_r2q_postp0_continuous_window_selection_failures.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_failures.csv
prime_mesh_r2q_normalized_error_gapmargin_failures.csv
prime_mesh_r2q_o2_repayment_closure_failures.csv
prime_mesh_r2q_b3_noaccumulation_failures.csv
prime_mesh_r2q_neutral_clause_closure_failures.csv
```

If a failure file has only headers, treat as empty.

If a failure file is missing, mark warning or failure depending on criticality.

---

## 11. Flexible Summary Parser

Because different audits may write summary CSVs in different formats, the runner should support:

### Format A — key/value rows

```text
metric,value
rows,1468
failures,0
```

### Format B — one-row wide summary

```text
rows,failures,classification
1468,0,...
```

### Format C — mixed columns

The runner should search case-insensitively and normalize:

```text
spaces -> underscores
hyphens -> underscores
lowercase
```

Example key normalization:

```python
def norm_key(s):
    return str(s).strip().lower().replace(" ", "_").replace("-", "_")
```

---

## 12. Floating-Point Tolerances

Use tolerances:

```text
absolute tolerance = 1e-9
relative tolerance = 1e-9
```

For these exact constants:

```text
C_theta = 1.9233607946440099
R_upper_global_max = -0.0006006774736066138
R_lower_global_min = -0.0007553068873594187
O2 cap max = 0.0499059549846063
```

---

## 13. Artifact Hashes

Write:

```text
prime_mesh_r2q_final_artifact_hashes.txt
```

Hash at least:

```text
*.py
*.csv
*.md
```

in the final scripts/results folder.

Each line:

```text
sha256  filename
```

---

## 14. Suggested Implementation Skeleton

```python
from pathlib import Path
import subprocess
import sys
import csv
import hashlib
import platform
from datetime import datetime

ROOT = Path.cwd()
LOG_DIR = ROOT / "final_audit_logs"
LOG_DIR.mkdir(exist_ok=True)

AUDITS = [
    {
        "name": "NormalizedError GapMargin",
        "script": "prime_mesh_r2q_normalized_error_gapmargin_audit.py",
        "summary": "prime_mesh_r2q_normalized_error_gapmargin_summary.csv",
        "critical": True,
    },
    # add remaining audits in run order
]

def run_cmd(cmd, stdout_path, stderr_path):
    with open(stdout_path, "w", encoding="utf-8") as out, open(stderr_path, "w", encoding="utf-8") as err:
        return subprocess.run(cmd, cwd=ROOT, stdout=out, stderr=err, text=True)

def sha256_file(path):
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()
```

The final implementation should include validation logic.

---

## 15. Cursor Build Prompt

```text
Create:

run_all_final_audits.py

in:

<package-root>

Purpose:
One-command reproduction runner for the final Prime Mesh R2Q certificate stack.

Requirements:
1. Compile core scripts with python -m py_compile.
2. Run scripts in the order specified in Prime_Mesh_R2Q_RunAll_FinalAudits_Script_Spec_v1.md.
3. Capture logs in final_audit_logs/.
4. Verify output summary CSVs exist.
5. Parse summary CSVs flexibly.
6. Check expected counts/constants:
   - NormalizedError GapMargin: all_gaps_margin_safe, 141 margin-safe gaps, 0 upper/lower risk, C_theta, R bounds, 22637 jumps.
   - PostP0 ContinuousWindowSelection: 142/142 windows, 120/120 upper, 22/22 lower, P0 gap 0.
   - ThresholdRelevance: 10140 rows, 0 failures, 24 above threshold, 10115 subthreshold, 0 unclassified.
   - EndpointSign: upper_lower_split, 1320 upper, 148 lower, 0 sign failures.
   - O2/B3/Neutral expected counts.
7. Check failure CSVs are empty.
8. Generate SHA256 hashes.
9. Write:
   - prime_mesh_r2q_final_reproduction_report.csv
   - Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md
   - prime_mesh_r2q_final_artifact_hashes.txt
10. Exit nonzero on critical failure.
11. Support flags:
   --dry-run
   --compile-only
   --allow-missing
   --skip-run
   --hash-only
   --strict

Do not use web.
Do not modify input CSVs except deposit_manifest if an existing audit script does that.
```

---

## 16. Expected Final PASS Statement

The MD report should end with:

```text
Final certificate reproduction status: PASS
```

only if:

```text
[ ] all critical scripts exist;
[ ] all critical scripts compile;
[ ] all critical scripts run;
[ ] all critical summary files exist;
[ ] all expected counts match;
[ ] all critical failure files are empty;
[ ] final hashes are written.
```

Otherwise:

```text
Final certificate reproduction status: FAIL
```

with a list of failed checks.

---

## 17. Honest Status

This spec does not run the audits itself.

It defines the runner needed for independent reproducibility.

Once implemented and passing, the project will have a one-command reproduction package for the certificate-level theta bridge.

---

*Prime Mesh Theory — RH Programme*
