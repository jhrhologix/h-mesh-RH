# Hegyesy Prime Mesh R2Q — ThetaBridge Certificate

**Author:** Jonathan Hegyesy  
**Date:** 2026-05-11  
**Status:** Certificate-level closure — pending independent review  
**Tag:** v1.0-review  
[![DOI](https://zenodo.org/badge/1226172726.svg)](https://doi.org/10.5281/zenodo.20128313)

---

> The exported Prime Mesh R2Q ThetaBridge certificate package reproduces final status `PASS` from its own package root in a fresh Python environment. The result is presented as a certificate-level active theta-bridge closure pending independent review, not as an externally accepted proof of RH.

---

## What this is

A reproducible certificate-level closure for the active theta bridge

$$G(x) = \theta(x) - x$$

against the RH-scale envelope

$$\mathcal{E}_\theta(x) = 1.9233607946440099\,\sqrt{x}\log^2 x$$

with cutoff $P_0 = 500{,}000{,}000$.

This constitutes a certificate-level route toward the Chebyshev/von Koch RH-scale criterion. It is not presented as a peer-reviewed or community-accepted proof of RH.

---

## Quick start

```bash
pip install -r requirements.txt
python audit/run_all_final_audits.py
```

Expected result:

```
Final certificate reproduction status: PASS
```

---

## Key results

| Check | Result |
|-------|--------|
| Coordinate gaps margin-safe | 141 / 141 |
| Post-P₀ candidate windows covered | 142 / 142 |
| Upper candidates represented | 120 / 120 |
| Lower candidates bracketed | 22 / 22 |
| ThresholdRelevance rows checked | 10,140 |
| ThresholdRelevance failures | 0 |
| R_upper_global_max | −0.0006006774736066138 |
| R_lower_global_min | −0.0007553068873594187 |

---

## Where to start reading

1. `docs/reviewer/README_REPRODUCIBILITY.md` — full reproducibility guide
2. `docs/reviewer/Prime_Mesh_R2Q_Reviewer_Package_Index_v1.md` — reading order for reviewers
3. `paper/Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md` — paper draft
4. `docs/proof_checks/Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md` — proof audit checklist

---

## Repository layout

- `README.md` — public overview and cautious claim framing.
- `Prime_Mesh_R2Q_ThetaBridge_Certificate_Manuscript_v1.pdf` — manuscript PDF.
- `PLAIN_ENGLISH_GUIDE.md` — section-by-section plain-language guide.
- `audit/` — one-command reproduction runner, audit scripts, CSV certificates, hashes, and logs.
- `docs/reviewer/` — reviewer guide, package index, definitions, authorship/naming.
- `docs/conceptual/` — H-Mesh, Prime Mesh, R2Q mechanism, discovery-path, and future side-paper material.
- `docs/proof_checks/` — red-team, proof-audit, reproduction reports, and runbooks.
- `docs/audits/` — detailed audit notes.
- `docs/closure_updates/` — closure and package repair notes.
- `docs/legacy/` — older drafts and superseded working notes.
- `paper/` — paper sources and arXiv bundle artifacts.

---

## Framework

This work is part of the **Hegyesy Mesh (H-Mesh)** programme — a local prime-error geometry framework that decomposes the global theta-bridge control problem into window-level first-exit certificates.

See `docs/reviewer/Prime_Mesh_R2Q_HMesh_Definitions_v1.md` for definitions.

---

## Citation

```bibtex
@software{hegyesy2026hmesh,
  author    = {Hegyesy, Jonathan},
  title     = {Hegyesy Prime Mesh R2Q ThetaBridge Certificate v1},
  year      = {2026},
  doi       = {10.5281/zenodo.20128313},
  url       = {https://doi.org/10.5281/zenodo.20128313}
}
```

---

## License

CC BY 4.0 — see `LICENSE`.  
AI tools assisted with code and drafting. See `docs/reviewer/AUTHORSHIP_AND_NAMING.md`.
