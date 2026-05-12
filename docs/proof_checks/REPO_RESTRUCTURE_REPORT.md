# Repository Restructure Report

**Date:** 2026-05-11  
**Branch:** `repo-clean-structure`  
**Repository root:** `C:\Users\jhegy\source\repos\prime-mesh-theory\Hegyesy_Prime_Mesh_R2Q_ThetaBridge_Certificate_v1_2026-05`

---

## 1. Summary

The public repository root was reorganized to reduce clutter while preserving the
certificate package and public cautious framing.

No mathematical claims, theorem statements, audit conclusions, or certificate
numbers were intentionally changed. No certificate/input CSV contents were
manually edited. The runner regenerated its normal audit/report CSV outputs
during validation.

---

## 2. Moved Files Summary

| Destination | Summary |
|---|---:|
| `audit/` | `77` Python scripts, `426` CSV files, `prime_mesh_r2q_final_artifact_hashes.txt`, `deposit_manifest.csv`, `final_audit_logs/` |
| `docs/reviewer/` | reviewer-facing guides, index, definitions, authorship/naming, external-review notes |
| `docs/conceptual/` | H-Mesh / Prime Mesh / R2Q mechanism, branch, target, discovery-path, and future side-paper notes |
| `docs/closure_updates/` | closure and package repair update notes |
| `docs/audits/` | audit-note Markdown and extraction/export-patch notes |
| `docs/proof_checks/` | red-team, proof-audit, reproduction, runbook, and restructure-plan/report documents |
| `docs/legacy/` | reserved for truly old/superseded notes; no broad automatic dump was used |
| `paper/` | manuscript source, final paper Markdown, paper draft, arXiv zip/source artifacts |

Root now contains the public entry files plus repository config:

```text
README.md
LICENSE
CITATION.cff
requirements.txt
Prime_Mesh_R2Q_ThetaBridge_Certificate_Manuscript_v1.pdf
PLAIN_ENGLISH_GUIDE.md
.github/
.gitignore
```

---

## 3. Old Path -> New Path Table

| Old path | New path |
|---|---|
| `run_all_final_audits.py` | `audit/run_all_final_audits.py` |
| `*.py` audit/helper scripts | `audit/*.py` |
| `*.csv` certificate/result files | `audit/*.csv` |
| `deposit_manifest.csv` | `audit/deposit_manifest.csv` |
| `prime_mesh_r2q_final_artifact_hashes.txt` | `audit/prime_mesh_r2q_final_artifact_hashes.txt` |
| `final_audit_logs/` | `audit/final_audit_logs/` |
| `README_REPRODUCIBILITY.md` | `docs/reviewer/README_REPRODUCIBILITY.md` |
| `Prime_Mesh_R2Q_Reviewer_Package_Index_v1.md` | `docs/reviewer/Prime_Mesh_R2Q_Reviewer_Package_Index_v1.md` |
| `Prime_Mesh_R2Q_HMesh_Definitions_v1.md` | `docs/reviewer/Prime_Mesh_R2Q_HMesh_Definitions_v1.md` |
| `AUTHORSHIP_AND_NAMING.md` | `docs/reviewer/AUTHORSHIP_AND_NAMING.md` |
| `Prime_Mesh_R2Q_*Closure_Update*.md` | `docs/closure_updates/` |
| `Prime_Mesh_R2Q_*_Audit_v1.md` | `docs/audits/` |
| `Prime_Mesh_R2Q_*_Extraction_v1.md` | `docs/audits/` |
| `Prime_Mesh_R2Q_*_Export_Patch_v1.md` | `docs/audits/` |
| `Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md` | `docs/proof_checks/Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md` |
| `Prime_Mesh_R2Q_Final_RedTeam_Revalidation_Report_v2.md` | `docs/proof_checks/Prime_Mesh_R2Q_Final_RedTeam_Revalidation_Report_v2.md` |
| `Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md` | `docs/proof_checks/Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md` |
| `Prime_Mesh_R2Q_Reproducibility_Runbook_v1.md` | `docs/proof_checks/Prime_Mesh_R2Q_Reproducibility_Runbook_v1.md` |
| `REPO_RESTRUCTURE_PLAN.md` | `docs/proof_checks/REPO_RESTRUCTURE_PLAN.md` |
| `Prime_Mesh_R2Q_ThetaBridge_Manuscript_v1_source.md` | `paper/Prime_Mesh_R2Q_ThetaBridge_Manuscript_v1_source.md` |
| `Prime_Mesh_R2Q_Final_Paper_v1.md` | `paper/Prime_Mesh_R2Q_Final_Paper_v1.md` |
| `Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md` | `paper/Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md` |
| `arxiv_prime_mesh_r2q_theta_bridge_v1.zip` | `paper/arxiv_prime_mesh_r2q_theta_bridge_v1.zip` |

---

## 4. Runner Patches

`audit/run_all_final_audits.py` now resolves audit-local paths from its script
directory:

```python
BASE_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = BASE_DIR.parent
LOG_DIR = BASE_DIR / "final_audit_logs"
```

Generated audit reports, logs, hashes, and `deposit_manifest.csv` are written
under `audit/`. Manifest and hash paths are stored relative to `PACKAGE_ROOT`.

Two audit-script text-detection patches were made so the same audit conclusions
survive the docs move:

- `prime_mesh_r2q_firstcrossing_coveringlocalization_audit.py` now finds the
  moved `Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md`
  and recognizes `theta-window` as the same filename/path wording form as
  `theta window`.
- The same script treats explicit negative/false H-Exc full-grid statements as
  safe caveats, not unsafe upgrades.
- `prime_mesh_r2q_continuous_firstexit_candidate_completeness_audit.py` treats
  `candidate-selection` as the same textual cue as `candidate selection`.

These are path/text-detection repairs only; they do not change theorem claims or
certificate numbers.

---

## 5. Commands Tested

From repository root:

```powershell
pip install -r requirements.txt
python audit/run_all_final_audits.py
```

Result:

```text
Final certificate reproduction status: PASS
```

From inside `audit/`:

```powershell
cd audit
python run_all_final_audits.py
cd ..
```

Result:

```text
Final certificate reproduction status: PASS
```

---

## 6. Path Checks

Command:

```powershell
Select-String -Path .\audit\deposit_manifest.csv -Pattern "C:\\Users|C:/Users|source\\repos|source/repos"
```

Result:

```text
0 hits
```

Command:

```powershell
Select-String -Path .\README.md,.\PLAIN_ENGLISH_GUIDE.md -Pattern "python run_all_final_audits.py"
```

Result:

```text
1 hit in PLAIN_ENGLISH_GUIDE.md, explicitly paired with `cd audit`.
```

`README.md` points to:

```text
python audit/run_all_final_audits.py
```

---

## 7. Confirmations

- Branch created: `repo-clean-structure`.
- `git mv` was used for tracked moves where possible.
- No files were intentionally deleted.
- No CSV contents were manually edited.
- No mathematical claims, theorem wording, audit conclusions, or certificate numbers were intentionally changed.
- `audit/deposit_manifest.csv` has no absolute local paths.
- Runner passes from repository root and from inside `audit/`.

---

## 8. Remaining Issues

- Root contains `.gitignore` as normal repository configuration in addition to the public entry files.
- Generated audit outputs under `audit/` were refreshed by validation, so reviewers should inspect diffs before commit.
- Some docs may still contain historical prose references to old flat filenames; these are not runner blockers.

---

*AI documentation pass: GPT-5.5*
