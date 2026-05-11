# Prime Mesh R2Q — Exported Package PASS Closure Update v1

**Date:** 2026-05-11  
**Package root tested:** `<repo-root>\Hegyesy_Prime_Mesh_R2Q_ThetaBridge_Certificate_v1_2026-05`  
**Final status:** `PASS`

---

## 1. Command Used

From the exported package root:

```text
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_all_final_audits.py
```

Final output:

```text
Final certificate reproduction status: PASS
CSV report: prime_mesh_r2q_final_reproduction_report.csv
Markdown report: Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md
Artifact hashes: prime_mesh_r2q_final_artifact_hashes.txt
```

Hash-only stability check:

```text
.\.venv\Scripts\python.exe run_all_final_audits.py --hash-only
.\.venv\Scripts\python.exe run_all_final_audits.py --hash-only
hash_stable=True
```

---

## 2. Fixed Blockers

1. Added the missing required CSV:

   ```text
   prime_mesh_r2q_rawr2q_primitive_decomposition_rows_v3.csv
   ```

2. Added the canonical ThresholdRelevance rows file expected by scripts:

   ```text
   prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv
   ```

   Documentation references were updated to the underscore form. The old no-underscore row file remains only as a compatibility copy.

3. Established the exported package root as the canonical reviewer root:

   ```text
   Hegyesy_Prime_Mesh_R2Q_ThetaBridge_Certificate_v1_2026-05
   ```

   Running `python run_all_final_audits.py` from that root now passes.

4. Added `requirements.txt` at both repository root and exported package root with:

   ```text
   pandas>=1.5.0
   numpy>=1.23.0
   ```

5. Regenerated `deposit_manifest.csv` with relative package-root paths and confirmed it includes reviewer-facing root docs:

   ```text
   README_REPRODUCIBILITY.md
   Prime_Mesh_R2Q_Reviewer_Package_Index_v1.md
   Prime_Mesh_R2Q_Final_Paper_v1.md
   AUTHORSHIP_AND_NAMING.md
   requirements.txt
   run_all_final_audits.py
   ```

6. Regenerated `prime_mesh_r2q_final_artifact_hashes.txt`; root Markdown files are included.

7. Added cautious classical references in `Prime_Mesh_R2Q_Final_Paper_v1.md` for:

   - the prime-power correction \(\psi(x)-\theta(x)\);
   - the von Koch criterion.

8. Tightened overclaim wording in `Prime_Mesh_R2Q_HMesh_Definitions_v1.md`.

9. Clarified finite constant precision:

   ```text
   1.9233607946440099  canonical
   1.9233607946        truncated display
   1.923361            rounded display
   ```

10. Removed unused duplicate/legacy audit scripts from the exported package:

   ```text
   prime_mesh_r2q_firstcrossing_threshold_relevance_audit.py
   prime_mesh_r2q_b3_no_accumulation_audit.py
   ```

---

## 3. Remaining Non-Blocking Issues

Some historical/generated audit Markdown files still include absolute local source paths in explanatory prose. They do not affect package execution or the exported runner, but should be cleaned before archival publication.

The no-underscore ThresholdRelevance rows file remains as a compatibility copy. The canonical name is the underscore form:

```text
prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv
```

---

## 4. Closure Statement

The exported reviewer package now reproduces `PASS` from its own root without requiring navigation into the internal repair folder. This update changes package integrity, reproducibility, and wording/citation support only; it does not strengthen or alter the mathematical claims.

---

*AI documentation pass: GPT-5.5*
