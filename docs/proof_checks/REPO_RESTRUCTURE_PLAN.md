# Repository Restructure Plan — Dry Run

**Date:** 2026-05-11  
**Repository root:** `Hegyesy_Prime_Mesh_R2Q_ThetaBridge_Certificate_v1_2026-05`  
**Status:** dry-run plan only; no files moved by this plan.

---

## 1. Goal

Clean the public repository root without changing mathematical content, CSV
contents, certificate claims, theorem statements, or audit conclusions.

The intended visitor flow is:

```text
README.md                     <- what is this?
Manuscript PDF                <- read the paper, if present
audit/run_all_final_audits.py <- reproduce PASS
```

The intended reproduction command from repository root is:

```text
pip install -r requirements.txt
python audit/run_all_final_audits.py
```

The runner should also work from inside `audit/`:

```text
cd audit
python run_all_final_audits.py
```

---

## 2. Current Inventory Snapshot

Observed at package root:

- Markdown files: about `115` total, including `.github/ISSUE_TEMPLATE/*.md`.
- Python files: `77`.
- CSV files: `426`.
- Root text files: `requirements.txt`, `prime_mesh_r2q_final_artifact_hashes.txt`, plus logs under `final_audit_logs/`.
- Existing root keepers: `README.md`, `LICENSE`, `CITATION.cff`, `requirements.txt`.
- Missing expected public artifacts at this snapshot:
  - `Prime_Mesh_R2Q_ThetaBridge_Certificate_Manuscript_v1.pdf`
  - `PLAIN_ENGLISH_GUIDE.md`
  - `main.tex`
  - `references.bib`
  - `arxiv_prime_mesh_r2q_theta_bridge_v1.zip`

The package is already its own Git repository. Before actual moves, create a
cleanup branch inside this package repo:

```powershell
git checkout -b repo-clean-structure
```

---

## 3. Target Layout

```text
.
├── README.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── Prime_Mesh_R2Q_ThetaBridge_Certificate_Manuscript_v1.pdf
├── PLAIN_ENGLISH_GUIDE.md
├── audit/
├── docs/
│   ├── reviewer/
│   ├── closure_updates/
│   ├── audits/
│   ├── proof_checks/
│   └── legacy/
├── paper/
└── .github/
```

Notes:

- Keep `.github/` in place.
- Keep the manuscript PDF in root if/when it exists.
- Put arXiv/source bundles under `paper/`, not root.
- Do not move `.git/`, `.venv/`, or other local environment folders.

---

## 4. Root Files to Keep

Keep these in the repository root:

| Current path | Planned path | Action |
|---|---|---|
| `README.md` | `README.md` | keep and update path instructions only |
| `LICENSE` | `LICENSE` | keep |
| `CITATION.cff` | `CITATION.cff` | keep |
| `requirements.txt` | `requirements.txt` | keep |
| `Prime_Mesh_R2Q_ThetaBridge_Certificate_Manuscript_v1.pdf` | same | keep if added/present |
| `PLAIN_ENGLISH_GUIDE.md` | same | keep if added/present |

Root should not contain audit `.py`, certificate `.csv`, audit logs, or bulk
audit Markdown after the restructure.

---

## 5. Audit Directory Plan

Create:

```text
audit/
```

Move all runner-execution artifacts there:

| Current path pattern | Planned path | Reason |
|---|---|---|
| `run_all_final_audits.py` | `audit/run_all_final_audits.py` | one-command runner |
| `*.py` | `audit/*.py` | audit scripts and helper scripts |
| `*.csv` | `audit/*.csv` | certificate/result data and manifest CSV |
| `prime_mesh_r2q_final_artifact_hashes.txt` | `audit/prime_mesh_r2q_final_artifact_hashes.txt` | generated artifact hashes |
| `final_audit_logs/` | `audit/final_audit_logs/` | runner logs |

Important: do not edit CSV contents. These moves should be path-only moves.

### Runner changes required

Before/with the move, update `run_all_final_audits.py` so every path resolves
relative to the script directory:

```python
BASE_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = BASE_DIR.parent
LOG_DIR = BASE_DIR / "final_audit_logs"
```

Then all audit-local scripts, CSVs, logs, and generated runner outputs should
use `BASE_DIR / name`.

Recommended implementation details:

- Rename current `ROOT` to `BASE_DIR` or assign `ROOT = BASE_DIR` for minimal
  diff compatibility.
- Subprocess script paths should be `BASE_DIR / script_name`.
- Summary/failure CSV reads should be `BASE_DIR / file_name`.
- Generated report CSV/MD/hash files should be written under `BASE_DIR`.
- `deposit_manifest.csv` should become `audit/deposit_manifest.csv` and should
  store paths relative to `PACKAGE_ROOT`, not absolute local paths.
- Hash generation should continue hashing audit artifacts and should also seal
  public/reviewer documents under:
  - `PACKAGE_ROOT / "README.md"`
  - `PACKAGE_ROOT / "requirements.txt"`
  - `PACKAGE_ROOT / "CITATION.cff"`
  - `PACKAGE_ROOT / "docs"`
  - `PACKAGE_ROOT / "paper"`
  - root PDF / guide if present.

This prevents the restructure from weakening artifact coverage.

---

## 6. Docs Directory Plan

Create:

```text
docs/reviewer/
docs/closure_updates/
docs/audits/
docs/proof_checks/
docs/legacy/
```

### `docs/reviewer/`

Move final reviewer-facing guides and stable package descriptions here:

| Current path | Planned path |
|---|---|
| `README_REPRODUCIBILITY.md` | `docs/reviewer/README_REPRODUCIBILITY.md` |
| `Prime_Mesh_R2Q_Reviewer_Package_Index_v1.md` | `docs/reviewer/Prime_Mesh_R2Q_Reviewer_Package_Index_v1.md` |
| `Prime_Mesh_R2Q_HMesh_Definitions_v1.md` | `docs/reviewer/Prime_Mesh_R2Q_HMesh_Definitions_v1.md` |
| `AUTHORSHIP_AND_NAMING.md` | `docs/reviewer/AUTHORSHIP_AND_NAMING.md` |
| `Prime_Mesh_R2Q_External_Review_Cover_Letter_v1.md` | `docs/reviewer/Prime_Mesh_R2Q_External_Review_Cover_Letter_v1.md` |
| `Prime_Mesh_R2Q_External_Review_Response_Log_v1.md` | `docs/reviewer/Prime_Mesh_R2Q_External_Review_Response_Log_v1.md` |
| `ZENODO_AND_ARXIV_INSTRUCTIONS.md` | `docs/reviewer/ZENODO_AND_ARXIV_INSTRUCTIONS.md` |

### `docs/closure_updates/`

Move closure/update notes here:

| Current path pattern | Planned path |
|---|---|
| `*Closure_Update*.md` | `docs/closure_updates/` |
| `*PASS_Closure_Update*.md` | `docs/closure_updates/` |
| `Prime_Mesh_R2Q_ExportedPackage_PASS_Closure_Update_v1.md` | `docs/closure_updates/Prime_Mesh_R2Q_ExportedPackage_PASS_Closure_Update_v1.md` |
| `Prime_Mesh_R2Q_GlobalBridge_FinalCertificate_Closure_Update_v1.md` | `docs/closure_updates/Prime_Mesh_R2Q_GlobalBridge_FinalCertificate_Closure_Update_v1.md` |

### `docs/audits/`

Move audit note Markdown here:

| Current path pattern | Planned path |
|---|---|
| `Prime_Mesh_R2Q_*_Audit_v1.md` | `docs/audits/` |
| `Prime_Mesh_R2Q_*_Extraction_v1.md` | `docs/audits/` |
| `Prime_Mesh_R2Q_*_Export_Patch_v1.md` | `docs/audits/` |
| `Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_v3.md` | `docs/audits/` |

### `docs/proof_checks/`

Move proof-review, reproduction, and red-team documents here:

| Current path | Planned path |
|---|---|
| `Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md` | `docs/proof_checks/Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md` |
| `Prime_Mesh_R2Q_Final_RedTeam_Revalidation_Report_v2.md` | `docs/proof_checks/Prime_Mesh_R2Q_Final_RedTeam_Revalidation_Report_v2.md` |
| `Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md` | `docs/proof_checks/Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md` |
| `Prime_Mesh_R2Q_Reproducibility_Runbook_v1.md` | `docs/proof_checks/Prime_Mesh_R2Q_Reproducibility_Runbook_v1.md` |
| `Prime_Mesh_R2Q_RunAll_FinalAudits_Script_Spec_v1.md` | `docs/proof_checks/Prime_Mesh_R2Q_RunAll_FinalAudits_Script_Spec_v1.md` |
| `REPO_RESTRUCTURE_PLAN.md` | `docs/proof_checks/REPO_RESTRUCTURE_PLAN.md` after approval/move |
| `REPO_RESTRUCTURE_REPORT.md` | `docs/proof_checks/REPO_RESTRUCTURE_REPORT.md` after creation |

### `docs/legacy/`

Move old drafts, superseded targets, and non-final narrative drafts here unless
the reviewer index explicitly marks them as current.

Candidate patterns:

| Current path pattern | Planned path |
|---|---|
| `*_Target_v1.md` | `docs/legacy/` unless needed by reviewer index |
| `*_Draft_v1.md` | `docs/legacy/` unless moved to `paper/` |
| older/superseded non-audit Markdown | `docs/legacy/` |

Do not delete legacy files.

---

## 7. Paper Directory Plan

Create:

```text
paper/
```

Move paper sources and bundles here:

| Current path | Planned path | Note |
|---|---|---|
| `Prime_Mesh_R2Q_ThetaBridge_Manuscript_v1_source.md` | `paper/Prime_Mesh_R2Q_ThetaBridge_Manuscript_v1_source.md` | present |
| `Prime_Mesh_R2Q_Final_Paper_v1.md` | `paper/Prime_Mesh_R2Q_Final_Paper_v1.md` | paper source/prose |
| `Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md` | `paper/Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md` | paper draft |
| `main.tex` | `paper/main.tex` | if added/present |
| `references.bib` | `paper/references.bib` | if added/present |
| `arxiv_prime_mesh_r2q_theta_bridge_v1.zip` | `paper/arxiv_prime_mesh_r2q_theta_bridge_v1.zip` | if added/present |

If a manuscript PDF exists or is added, keep it in root:

```text
Prime_Mesh_R2Q_ThetaBridge_Certificate_Manuscript_v1.pdf
```

---

## 8. README Update Plan

Only update repository-layout and path instructions. Do not change mathematical
claims.

Replace quick start:

```bash
pip install -r requirements.txt
python run_all_final_audits.py
```

with:

```bash
pip install -r requirements.txt
python audit/run_all_final_audits.py
```

Add:

```markdown
## Repository layout

- `README.md` — public overview and cautious claim framing.
- `Prime_Mesh_R2Q_ThetaBridge_Certificate_Manuscript_v1.pdf` — manuscript, if present.
- `audit/` — one-command reproduction runner, audit scripts, CSV certificates, hashes, and logs.
- `docs/reviewer/` — reviewer guide, package index, definitions, authorship/naming.
- `docs/proof_checks/` — red-team, proof-audit, reproduction reports and runbooks.
- `docs/audits/` — detailed audit notes.
- `docs/closure_updates/` — closure and package repair notes.
- `docs/legacy/` — older drafts and superseded working notes.
- `paper/` — paper sources and arXiv bundle artifacts.
```

Also update "Where to start reading" paths:

```text
docs/reviewer/README_REPRODUCIBILITY.md
docs/reviewer/Prime_Mesh_R2Q_Reviewer_Package_Index_v1.md
paper/Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md
docs/proof_checks/Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md
```

---

## 9. Proposed Move Command Strategy

After this plan is reviewed, use `git mv` where possible. Do not drag-and-drop.

Recommended sequence:

1. Create branch:

   ```powershell
   git checkout -b repo-clean-structure
   ```

2. Create directories:

   ```powershell
   mkdir audit
   mkdir docs
   mkdir docs\reviewer
   mkdir docs\closure_updates
   mkdir docs\audits
   mkdir docs\proof_checks
   mkdir docs\legacy
   mkdir paper
   ```

3. Move runner/scripts/CSV/logs/hashes into `audit/` using `git mv`.
4. Move Markdown according to the classifications above using `git mv`.
5. Patch `audit/run_all_final_audits.py` for `BASE_DIR`/`PACKAGE_ROOT`.
6. Patch `README.md` quick start and layout only.
7. Run validation.

Do not run `git add .` blindly.

---

## 10. Validation Plan

From repository root:

```powershell
pip install -r requirements.txt
python audit/run_all_final_audits.py
```

Expected:

```text
Final certificate reproduction status: PASS
```

Also test from `audit/`:

```powershell
cd audit
python run_all_final_audits.py
```

Expected:

```text
Final certificate reproduction status: PASS
```

After validation, produce:

```text
REPO_RESTRUCTURE_REPORT.md
```

with:

- moved files summary;
- old path -> new path table;
- runner commands tested;
- PASS/FAIL result;
- any remaining issues.

---

## 11. Risk Check

The restructure can break reproduction if:

1. Any required script or CSV is moved outside `audit/`.
2. `run_all_final_audits.py` still reads from the process working directory.
3. Generated output paths are split between root and `audit/`.
4. Hash/manifest generation stops sealing reviewer docs after the docs move.
5. README points to the old root command after the runner is moved.

The core safe invariant is:

```text
runner + scripts + CSVs + logs + hashes live together in audit/
```

with `run_all_final_audits.py` resolving all audit-local paths from
`Path(__file__).resolve().parent`.

---

## 12. Dry-Run Verdict

Proceed after review. The proposed structure should clean the public root while
preserving reproducibility, provided the runner path patch is made before final
validation.

No mathematical content, CSV data, theorem statements, or audit conclusions are
to be changed.

---

*AI documentation pass: GPT-5.5*
