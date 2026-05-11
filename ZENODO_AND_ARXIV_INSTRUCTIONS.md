# Zenodo DOI + arXiv Submission Instructions

**Project:** Prime Mesh Theory — RH Programme  
**Author:** Jonathan Hegyesy  
**Date:** 2026-05-11

---

## Step 1 — Create a GitHub Release (required for Zenodo)

1. Go to: https://github.com/jhrhologix/h-mesh-RH/releases
2. Click **Draft a new release**
3. Tag: `v1.0.0` (already pushed by `push_to_github.ps1`)
4. Title: `Hegyesy Prime Mesh R2Q ThetaBridge Certificate v1`
5. Description:

```
Certificate-level Prime Mesh R2Q closure for the active theta bridge G(x) = θ(x) − x
against the RH-scale envelope 1.9233607946440099 √x log²x.

One-command reproducible audit stack (run_all_final_audits.py → PASS).
Includes H-Mesh definitions, all audit scripts, CSVs, closure documents,
CITATION.cff, LICENSE, and authorship statement.

Originator: Jonathan Hegyesy
Framework: Hegyesy Mesh (H-Mesh) / Prime Mesh Theory

Safe claim: reproducible certificate-level route toward the von Koch RH-scale criterion,
pending independent mathematical verification.
```

6. Click **Publish release**

---

## Step 2 — Connect GitHub to Zenodo

1. Go to: https://zenodo.org
2. Log in (or create a free account)
3. Click your username → **GitHub** (in the sidebar)
4. Find `jhrhologix/h-mesh-RH` in the list
5. Toggle it **ON**
6. Go back to GitHub and **re-publish the v1.0.0 release** (or Zenodo may auto-detect it)
7. Zenodo will automatically archive the release and assign a DOI

Your DOI will look like: `10.5281/zenodo.XXXXXXX`

---

## Step 3 — Add DOI badge to README (optional but recommended)

After Zenodo assigns your DOI, add this to the top of `README_REPRODUCIBILITY.md`:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

Then commit and push the updated README.

---

## Step 4 — arXiv Preprint

### Title (safe, accurate)

```
A Certificate-Level Prime Mesh R2Q Closure for the Chebyshev Theta RH-Scale Envelope
```

### Primary category

```
math.NT  (Number Theory)
```

### Abstract (draft)

```
We present a reproducible certificate-level closure for the active theta bridge
G(x) = θ(x) − x against the Riemann Hypothesis scale envelope
C_θ √x log²x, with C_θ = 1.9233607946440099.

The Prime Mesh R2Q framework decomposes the global prime-error control problem
into local first-exit geometry. The certificate stack audits post-P₀ obstructions
(P₀ = 5 × 10⁸) across candidate/bracket windows and coordinate gaps. All 142
post-P₀ windows are covered (120 upper, 22 lower), all 141 coordinate gaps satisfy
|R_θ(x)| < 1 (global max = −0.0006006...), and 10,140 ThresholdRelevance rows
yield zero failures. The result is a one-command reproducible audit stack
(run_all_final_audits.py → PASS).

This constitutes a certificate-level route toward the Chebyshev/von Koch
RH-scale criterion θ(x) − x = O(√x log²x), pending independent mathematical
verification. The package is available at https://github.com/jhrhologix/h-mesh-RH
(DOI: 10.5281/zenodo.XXXXXXX).
```

### First-time arXiv submission notes

- arXiv may require **endorsement** for math.NT if you are a first-time submitter.
- Find an endorser: a faculty mathematician in analytic/computational number theory
  who can vouch for the submission (not for the result, just that it is a legitimate
  mathematical document).
- If you cannot find an endorser, submit to math.GM (General Mathematics) first,
  then cross-list to math.NT once endorsed.
- Do NOT title the paper "Proof of the Riemann Hypothesis" — use the safe title above.

---

## Stage Timeline (recommended)

| Stage | Action | When |
|-------|--------|------|
| 1 | GitHub public + Zenodo DOI | Now (after push) |
| 2 | Private review (3–5 experts) | Week 1–4 |
| 3 | arXiv preprint | After at least one expert review |
| 4 | Journal submission | After arXiv + positive expert feedback |

### Suggested journals (in order of fit)

1. **Research in Number Theory** — computational + certificate results, open access
2. **Journal of Number Theory** — established, accepts computational proofs
3. **Mathematics of Computation** — if computational methodology is the primary contribution
4. **Experimental Mathematics** — if framed as a verified computational result
5. **Annals of Mathematics / Inventiones** — only after strong positive expert review

---

*Prime Mesh Theory — RH Programme*  
*Originator: Jonathan Hegyesy*
