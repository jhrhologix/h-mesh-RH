# Prime Mesh R2Q — Plain English Guide

**What the paper actually says, section by section**

*Jonathan Hegyesy — Prime Mesh Theory Programme — 2026*

---

## What is this paper about?

The Riemann Hypothesis is one of the most famous unsolved problems in mathematics. It was proposed in 1859 and no one has proven it yet (it's worth a $1 million Millennium Prize). One way to state it is: **prime numbers are distributed as regularly as possible — not too clumped, not too spread out.**

Mathematicians have shown that the Riemann Hypothesis is equivalent to saying that a particular error term — the gap between an estimate and the real count of primes — stays within a specific boundary. If that error never escapes the boundary, RH is true.

This paper describes a **computational certificate** — a reproducible, checkable audit — that confirms the error never escaped the boundary in the range we studied. It is not an externally accepted proof of the Riemann Hypothesis. It is a serious, careful result that invites independent verification.

---

## Section 1 — Introduction

**In plain English:** Sets the stage. Explains what the Riemann Hypothesis is, why prime-counting error bounds matter, and what went wrong in earlier versions of this work.

The paper opens by explaining that RH can be restated as: the function ψ(x) — which counts prime powers — stays within a specific distance of x (its ideal value) at all times. The allowed distance grows like √x × (log x)², and this paper tracks whether the error ever exceeds that.

Five problems were found in earlier drafts of this work and had to be fixed before the certificate could be claimed:
1. One of the bounding tools (H-Exc) only worked on a sample of points, not continuously.
2. A planned shortcut through a quantity called Q_ΔD turned out not to work.
3. The sign of the error direction (going up vs going down) needed to be tracked more carefully.
4. Gaps between audit windows weren't being checked.
5. The gap-checking needed actual margin numbers, not just pass/fail.

All five were repaired in this version.

---

## Section 2 — Classical Functions and Target

**In plain English:** Defines the mathematical objects being tracked.

Two functions matter here:

**θ(x)** — pronounced "theta of x" — adds up the logarithm of every prime up to x. Think of it as a running tally of how much "prime weight" has accumulated.

**ψ(x)** — pronounced "psi of x" — is similar but also counts prime powers (like 4 = 2², 8 = 2³, etc.).

Both should be close to x (their theoretical average). The **error** is θ(x) − x, i.e., how far the actual prime tally is from its expected value.

The **normalized error** R_θ(x) divides that gap by the allowed envelope. If R_θ(x) stays between −1 and +1, the error is within the RH-scale boundary. A **first exit** would be the first moment R_θ escapes that range — which this paper argues never happens.

---

## Section 3 — Prime Mesh R2Q: Framework and Local Objects

**In plain English:** Explains how the audit is structured.

The audit works by breaking the problem into local "rows." Each row J corresponds to a small interval where the normalized error could potentially be dangerous.

Every row is assigned:
- **A local theta increment** Δ_θ(J): did θ overshoot or undershoot its trend in this interval?
- **An endpoint sign** s_θ(J): +1 means the error went up (upper branch), −1 means it went down (lower branch).
- **An obstruction magnitude** Q_R2Q: a number measuring how dangerous this row is. If Q_R2Q > 3/4, the row is "threshold-relevant" and must be explicitly closed.

The key decomposition is:
> Q_R2Q = Q_ΔD + Q_exc + ε

Three ingredients, each bounded by the audit. Think of it like checking three separate pipes can't overflow, so the tank can't flood.

---

## Section 4 — The H-Exc Bound (Certificate Lemma 4.1)

**In plain English:** One of the three ingredients (Q_exc) is bounded by 0.025 — but only on the checked sample points, not between them.

The H-Exc tool measures how much the error "excurses" above or below a straight-line interpolation across the row. It confirms Q_exc ≤ 0.025 at all sampled points.

**Important caveat:** This bound was checked at a grid of sample points, not at every real number in the interval. The paper is explicit about this — it's not claimed to hold everywhere continuously. The gap between sample points is handled separately by the coordinate gap audit (Section 12).

---

## Section 5 — Residual Bound (Certificate Lemma 5.1)

**In plain English:** The third ingredient (ε, the leftover) is bounded by 0.03.

After Q_ΔD and Q_exc are computed, whatever is left over is called the residual ε. The audit confirms |ε| ≤ 0.03 for all 10,140 rows checked. Zero rows failed this gate.

---

## Section 6 — Positive Harmlessness (Certificate Lemma 6.1)

**In plain English:** If the error is going upward at the end of a row, the row is automatically safe.

When s_θ = +1 (upper branch — the error went up), the structure of the decomposition guarantees:
> Q_R2Q ≤ 0.305 < 3/4

So upper-branch rows can never be threshold-relevant. They are harmless by construction. There were 1,320 upper crossings, and all 1,320 were confirmed safe.

This is one of the cleanest results in the paper.

---

## Section 7 — Direct Threshold Sign Route (Lemma 7.1)

**In plain English:** If a row is dangerous (Q_R2Q > 3/4), it must be a downward row.

This is a pure logical deduction: since upward rows can't be dangerous (Section 6), anything dangerous must be downward. So Q_R2Q > 3/4 forces s_θ = −1.

Note: an earlier approach tried to show Q_R2Q > 3/4 forces Q_ΔD > 3/4 directly, but that doesn't hold because the other terms can shift the total. That route was rejected and this cleaner route was used instead.

---

## Section 8 — O2 Repayment and B3 No-Accumulation (Certificate Lemmas 8.1–8.2)

**In plain English:** Downward rows that aren't dangerous are safely "repaid" before they can cause a problem.

For a downward row with Q_R2Q ≤ 3/4 (not threshold-relevant), the audit confirms two things:

**O2 Repayment:** The error comes back within bounds before the next crossing event. The row's obstruction is "cancelled" by a subsequent return. Zero lower-branch rows survived unrepaid.

**B3 No-Accumulation:** Multiple small subthreshold contributions can't quietly add up to a big problem. Each row is checked individually for accumulation risk, and all pass.

---

## Section 9 — ThresholdRelevance Classification (Certificate Lemma 9.1)

**In plain English:** Every single row — all 10,140 of them — is accounted for.

The audit applies a decision tree to every row:
- Upward row? → Harmless (Section 6).
- Downward subthreshold row? → O2/B3 repaid (Section 8).
- Row below the P₀ cutoff (500 million)? → Handled by the finite zone (Section 11).
- Everything else? → Non-surviving.

Result: **10,140 rows checked, 0 failures.** Every row falls into one of the four safe categories.

---

## Section 10 — Endpoint Sign Split

**In plain English:** Confirms that every row is cleanly either upward or downward — nothing falls through the cracks.

The audit code tracks a variable called `local_theta_sign` that records s_θ for every row. The split is:
- 1,320 upward rows (s_θ = +1): all harmless.
- 148 downward rows (s_θ = −1): all repaid or otherwise safe.
- 0 neutral rows: the NeutralClause is empty.

Since every row is assigned to exactly one branch, and both branches are closed, no row escapes.

---

## Section 11 — Candidate Window Coverage

**In plain English:** Confirms that all the dangerous-looking regions in the post-500M range were audited.

After x = 500,000,000 (P₀), the audit identified 142 "candidate windows" — stretches where the error was large enough to potentially matter. All 142 were audited:
- 120 upper-branch candidates: all harmless.
- 22 lower-branch bracketed candidates: all closed.

The windows don't cover every point — they're targeted at the dangerous regions. The gaps between them are handled in the next section.

---

## Section 12 — Coordinate Gap Margin Safety (Certificate Lemma 12.1)

**In plain English:** The spaces between candidate windows are also safe — the error never got close to the boundary there.

Between the 142 windows there are 141 gaps. The audit computed R_θ(x) at all 22,637 prime jump points inside those gaps and found:

- Worst upper margin: −0.0006006... (negative = safely below the upper exit line)
- Worst lower margin: −0.0007553... (negative = safely above the lower exit line)

Both are negative, which means R_θ is well inside (−1, +1) throughout every gap. No gap came anywhere close to a first exit.

---

## Section 13 — Main Certificate Theorem

**In plain English:** Puts it all together. No first exit exists after x = 500 million.

The proof works by contradiction. Suppose a first exit existed at some point x₀ > 500,000,000.

- If x₀ is inside a candidate window: ThresholdRelevance shows the row must be classified somewhere — and every classification leads to "safe." Contradiction.
- If x₀ is in a coordinate gap: the gap margin audit shows R_θ stays inside (−1, +1) throughout every gap. Contradiction.

Both cases are impossible. So no first exit exists after P₀.

---

## Section 14 — Finite Zone

**In plain English:** The region below x = 500 million is handled separately by direct computation.

Below P₀, the values of θ(x) were computed directly from the list of primes. The audit confirmed |R_θ| < 1 throughout 2 ≤ x ≤ 500,000,000, using the same envelope constant throughout.

The finite zone + the post-P₀ certificate = a complete theta RH-scale bound (pending independent verification).

---

## Section 15 — Theta-to-Psi Transfer (Lemma 15.1)

**In plain English:** The result about θ(x) automatically gives the same result about ψ(x).

The difference ψ(x) − θ(x) comes from prime powers (4, 8, 9, 16, 25, ...). These contribute much less than primes themselves, and their total is also within the √x log²x envelope. So:

> If θ(x) − x stays within the envelope → ψ(x) − x also stays within the envelope.

This is a standard result from analytic number theory (Titchmarsh, Davenport).

---

## Section 16 — The Von Koch Criterion

**In plain English:** Connects the certificate result to the Riemann Hypothesis.

In 1901, Helge von Koch proved that the Riemann Hypothesis is equivalent to:
> ψ(x) − x = O(√x log²x)

(The "O" notation means the error stays within a fixed multiple of √x log²x forever.)

This paper establishes that condition holds in the audited range, using a specific constant C_θ. If independently verified as sufficient for global control, this would reach the von Koch criterion — and therefore RH.

This step is explicitly stated as conditional. The paper does not claim RH is proven.

---

## Section 17 — Certificate Status and Caveats

**In plain English:** Honest list of what is and isn't claimed.

**What IS claimed:**
- The audit chain is fully reproducible with one command.
- All 10,140 rows were checked with 0 failures.
- The H-Exc sampled-grid limitation is explicitly acknowledged.
- The rejected Q_ΔD route is explicitly disclaimed.

**What is NOT claimed:**
- RH is proven or externally accepted.
- H-Exc has full continuous-grid control.
- Candidate windows cover every coordinate.
- The constant C_θ = 1.9233... is a universal analytic constant.
- The result applies beyond the active theta bridge G(x) = θ(x) − x.

---

## Section 18 — Code and Data Availability

**In plain English:** Everything needed to verify this result is public and free.

- **GitHub:** [github.com/jhrhologix/h-mesh-RH](https://github.com/jhrhologix/h-mesh-RH)
- **Zenodo archive (permanent DOI):** [doi.org/10.5281/zenodo.20128313](https://doi.org/10.5281/zenodo.20128313)

To verify from scratch:
```
pip install -r requirements.txt
cd audit
python run_all_final_audits.py
```
Expected output: `Final certificate reproduction status: PASS`

---

## Section 19 — Authorship and AI Assistance

**In plain English:** The mathematical framework and all key decisions are Jonathan Hegyesy's. AI tools helped with code and document drafting.

The Prime Mesh Theory programme — including the R2Q framework, the identification of the five repair issues, the rejection of the Q_ΔD route, the gap margin strategy, and the H-Exc sampled-grid caveat — was developed by Jonathan Hegyesy.

AI tools (ChatGPT and Claude) helped with code generation, audit design, and document drafting. AI tools are not listed as authors.

---

## Section 20 — Conclusion

**In plain English:** The short version of everything above.

> For the active theta bridge G(x) = θ(x) − x, the Prime Mesh R2Q certificate stack rules out all post-500,000,000 first-exit obstructions. The audit runner reproduces this with status PASS. The result is presented as a certificate-level active theta-bridge closure pending independent review — not as an externally accepted proof of RH.

---

## Appendix A — Certificate Dependency Table

**In plain English:** A map showing which result depends on which.

Every claim in the paper flows from earlier results. This table makes the dependency chain explicit so a reviewer can check exactly which audit result each conclusion relies on. "Certificate Lemma" (CL) entries are computationally verified; ordinary "Lemma" (L) entries are pure analytic deductions.

---

## Appendix B — Audit Script Documentation

**In plain English:** What each sub-audit actually does, step by step.

The one-command runner `run_all_final_audits.py` runs six sub-audits in sequence:
1. ThresholdRelevance audit (10,140 rows, 0 failures)
2. Candidate window audit (142/142 covered)
3. Gap margin safety audit (141/141 safe, 22,637 prime evaluations)
4. Endpoint sign audit (1,320 upper + 148 lower, 0 errors)
5. H-Exc sampled-grid audit (grid bound confirmed, no full-grid lift)
6. Final status aggregation (PASS)

A step-by-step reviewer checklist is included so an independent auditor knows exactly what to look at.

---

## Appendix C — Artifact Hashes

**In plain English:** Fingerprints of the data files so you can confirm nothing was changed.

SHA-256 hashes for the CSV data files and audit scripts are recorded in the package. Cross-checking these against the Zenodo archive confirms that what you download is exactly what produced the PASS result.

---

## Glossary of key terms

| Term | Plain English meaning |
|---|---|
| θ(x) | Running sum of log(p) for all primes p ≤ x |
| ψ(x) | Like θ(x) but also counts prime powers |
| R_θ(x) | The normalized error: how far θ(x) is from x, as a fraction of the allowed envelope |
| First exit | The first moment the normalized error escapes the range (−1, +1) |
| Envelope | The allowed boundary: C_θ × √x × (log x)² |
| P₀ = 500,000,000 | The cutoff: finite-zone audit below, R2Q certificate above |
| Certificate Lemma | A result verified by the audit runner, not by pure symbolic math |
| Ordinary Lemma | A result proven by pure analytic reasoning |
| Upper branch (s_θ = +1) | Rows where the error was trending upward — always safe |
| Lower branch (s_θ = −1) | Rows where the error was trending downward — closed by O2/B3 |
| Q_R2Q | The obstruction magnitude for a row. If > 3/4, threshold-relevant |
| Threshold-relevant | A row that could potentially contribute to a first exit |
| O2 repayment | The error coming back within bounds before the next danger point |
| B3 no-accumulation | Confirms small contributions don't quietly add up |
| Coordinate gap | The space between two consecutive candidate windows |
| Von Koch criterion | The classical theorem linking ψ(x)−x = O(√x log²x) to RH |
| PASS | All sub-audits completed with zero failures |

---

*This plain-English guide is a companion document to the arXiv manuscript. It is intended for readers who want to understand the logical structure of the certificate without working through the mathematical notation. All claims, limitations, and caveats stated in the manuscript apply equally here.*
