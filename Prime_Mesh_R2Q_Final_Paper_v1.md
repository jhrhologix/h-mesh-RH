# Prime Mesh R2Q â€” Final Paper v1

**Title:** A Certificate-Level Prime Mesh R2Q Closure for the Chebyshev Theta RH-Scale Envelope  
**Project:** Prime Mesh Theory â€” RH Programme  
**Date:** 2026-05-11  
**Status:** Continuous paper manuscript draft  
**Scope:** Active theta bridge \(G(x)=\theta(x)-x\), certificate-level reproducible closure

---

## Abstract

We present a certificate-level Prime Mesh R2Q closure for the active Chebyshev theta bridge

\[
G(x)=\theta(x)-x.
\]

The bridge studies first exits from the RH-scale envelope

\[
\mathcal E_\theta(x)=C_\theta\sqrt{x}\log^2x,
\]

with certified constant

\[
C_\theta=1.9233607946440099.
\]

The proof architecture combines a local R2Q obstruction stack, endpoint sign classification, sampled-grid H-Exc control, O2 repayment, B3 no-accumulation, ThresholdRelevance, candidate coverage, and normalized coordinate-gap margin certificates.

The final reproducibility runner

```text
run_all_final_audits.py
```

reproduces the certificate stack with final status:

\[
\texttt{PASS}.
\]

The reproduced audit results include:

\[
142/142
\]

post-\(P_0\) candidate windows covered,

\[
120/120
\]

upper candidates represented,

\[
22/22
\]

lower candidates bracketed,

\[
141/141
\]

coordinate gaps margin-safe,

and

\[
10140
\]

ThresholdRelevance rows with zero failures.

For the coordinate gaps, the normalized theta ratio

\[
R_\theta(x)=
\frac{\theta(x)-x}{1.9233607946440099\sqrt{x}\log^2x}
\]

has certified global gap bounds

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

Thus no continuous first exit can occur inside any coordinate gap under the active theta bridge. Candidate/bracket windows are eliminated by the repaired R2Q local stack. Together, these results give a reproducible certificate-level route from the theta bridge to a Chebyshev/von Koch RH-scale criterion, pending independent proof audit.

---

## 1. Introduction

The Riemann Hypothesis is classically equivalent to RH-scale error bounds for prime-counting functions. One Chebyshev/von Koch form is

\[
\psi(x)-x=O(\sqrt{x}\log^2x).
\]

The Prime Mesh R2Q programme seeks to rule out first exits from an RH-scale envelope by converting a global first-crossing obstruction into a local R2Q obstruction row and then proving that no such row can survive.

Earlier versions of the project had important gaps:

1. H-Exc needed a sampled-grid rather than full-grid theorem.
2. A threshold-transfer route through \(Q_{\Delta D}\) failed.
3. Endpoint sign orientation had to be split into upper and lower crossings.
4. Sparse candidate windows left coordinate gaps.
5. The gap safety problem required normalized error margin data.

The current version repairs these issues in certificate form for the active theta bridge

\[
G(x)=\theta(x)-x.
\]

The result is not presented here as an externally accepted proof of RH. It is presented as a reproducible certificate-level closure of the Prime Mesh R2Q theta bridge, together with the classical path from theta RH-scale control to the von Koch criterion.

---

## 2. Classical Functions and Target

The first Chebyshev function is

\[
\theta(x)=\sum_{p\le x}\log p.
\]

The second Chebyshev function is

\[
\psi(x)=\sum_{n\le x}\Lambda(n),
\]

where

\[
\Lambda(n)=
\begin{cases}
\log p,& n=p^k,\ k\ge1,\\
0,& \text{otherwise}.
\end{cases}
\]

The active bridge uses

\[
G_\theta(x)=\theta(x)-x.
\]

The envelope is

\[
\mathcal E_\theta(x)=C_\theta\sqrt{x}\log^2x,
\]

with

\[
C_\theta=1.9233607946440099.
\]

This full decimal is the canonical package constant. Some finite-certificate
artifacts print the same finite requirement as \(1.9233607946\) or rounded as
\(1.923361\); those shorter displays are not separate constants.

The normalized theta error is

\[
R_\theta(x)=
\frac{\theta(x)-x}{C_\theta\sqrt{x}\log^2x}.
\]

A first exit is a point where

\[
|R_\theta(x)|>1
\]

after prior values have remained within the safe region.

The post-tail cutoff used in the certificate stack is

\[
P_0=500,000,000.
\]

---

## 3. Prime Mesh R2Q Local Objects

The R2Q framework assigns local rows \(J\) with an endpoint sign \(E_\theta(J)\) and an obstruction magnitude \(Q_{\rm R2Q}(J)\).

The repaired decomposition is

\[
Q_{\rm R2Q}=Q_{\Delta D}+Q_{\rm exc}+\epsilon.
\]

The local stack uses the following certified components.

### 3.1 H-Exc Bound

\[
Q_{\rm exc}\le0.025.
\]

The H-Exc theorem is explicitly **sampled-grid**, not full integer-grid.

### 3.2 Residual Bound

\[
|\epsilon|\le0.03.
\]

### 3.3 Positive Harmlessness

\[
E_\theta>0
\Rightarrow
Q_{\rm R2Q}\le0.305<0.75.
\]

### 3.4 Direct Threshold Sign

\[
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta<0.
\]

This is the direct sign route.

The failed route

\[
Q_{\rm R2Q}>0.75
\Rightarrow
Q_{\Delta D}>0.75
\]

is not used.

### 3.5 O2 Repayment

\[
E_\theta<0,\quad Q_{\rm R2Q}\le0.75
\Rightarrow
\text{O2-safe}.
\]

### 3.6 B3 No-Accumulation

\[
\text{accumulation-risk}
\Rightarrow
\text{B3-safe}.
\]

### 3.7 NeutralClause

\[
\mathcal N=\varnothing.
\]

---

## 4. H-Exc and the Sampled-Grid Caveat

The H-Exc layer uses a path \(D_N(t)\) and an affine endpoint line \(\ell_J(t)\). The bridge object is

\[
B_J(t)=D_N(t)-\ell_J(t),
\]

where

\[
\ell_J(t)
=
D_N(y)+\frac{t-y}{h}\bigl(D_N(y+h)-D_N(y)\bigr).
\]

The norm used is sampled over \(T_J\):

\[
\|B_J\|^2_{2,T_J}
=
\sum_{t\in T_J}|B_J(t)|^2.
\]

The H-Exc sample-grid audit explicitly ruled out a silent full-grid lift. Therefore the present paper never uses H-Exc as full integer-grid control.

This caveat matters because the global first-exit argument is eventually closed not by full-grid H-Exc, but by candidate windows plus normalized gap-margin certificates.

---

## 5. Endpoint Sign Split

The endpoint sign audit found that \(E_\theta\) is raw, not already outward-oriented.

The orientation variable is

\[
\texttt{local\_theta\_sign}.
\]

The correct closure is an upper/lower split.

### 5.1 Upper Branch

Upper crossings satisfy

\[
E_\theta>0.
\]

Audit count:

\[
1320
\]

upper crossings, with

\[
0
\]

upper nonpositive \(E_\theta\) rows.

By positive harmlessness,

\[
E_\theta>0
\Rightarrow
Q_{\rm R2Q}\le0.305<0.75.
\]

Thus upper rows cannot be surviving threshold-relevant obstructions.

### 5.2 Lower Branch

Lower crossings satisfy

\[
E_\theta<0.
\]

Audit count:

\[
148
\]

lower crossings, with

\[
0
\]

lower nonnegative \(E_\theta\) rows.

Lower rows do not contradict direct threshold sign, since threshold sign also forces \(E_\theta<0\). They are instead closed by O2/B3/finite/non-surviving safety.

The audit found

\[
0
\]

lower surviving unrepaid rows.

---

## 6. ThresholdRelevance

The ThresholdRelevance layer establishes the contrapositive closure:

\[
Q_{\rm R2Q}\le\frac34
\Rightarrow
\text{harmless / repaid / finite-certified / non-surviving}.
\]

Equivalently,

\[
\text{surviving first-crossing obstruction}
\Rightarrow
Q_{\rm R2Q}>\frac34.
\]

The audit classified this layer as

\[
\texttt{fullfcl\_backed\_certificate\_conditional}.
\]

The reproduced counts are:

\[
10140
\]

rows checked,

\[
0
\]

ThresholdRelevance failures,

\[
24
\]

rows above threshold,

\[
10115
\]

subthreshold rows,

\[
0
\]

subthreshold unclassified rows,

\[
24/24
\]

dangerous rows above threshold,

and

\[
11/11
\]

forbidden rows above threshold.

---

## 7. Candidate Coverage

The post-\(P_0\) continuous-window audit verifies:

\[
142/142
\]

post-\(P_0\) audited windows covered.

Upper candidates:

\[
120/120
\]

represented.

Lower candidates:

\[
22/22
\]

bracketed.

The \(P_0\) transition gap is

\[
0.
\]

This does not mean the windows tile every coordinate. They are sparse candidate windows. The coordinate gaps are handled separately by margin certificates.

---

## 8. Coordinate Gap Margin Safety

The sparse candidate windows leave

\[
141
\]

coordinate gaps.

The NormalizedError GapMargin audit evaluates the active theta ratio

\[
R_\theta(x)=
\frac{\theta(x)-x}{1.9233607946440099\sqrt{x}\log^2x}.
\]

It classifies all gaps as margin-safe:

\[
141/141.
\]

The global bounds over all gaps are

\[
R_{\rm upper,global,max}
=
-0.0006006774736066138,
\]

and

\[
R_{\rm lower,global,min}
=
-0.0007553068873594187.
\]

There are

\[
0
\]

upper-risk gaps and

\[
0
\]

lower-risk gaps.

The audit inventoried

\[
22637
\]

prime jumps inside gaps.

Despite these jumps, the normalized theta ratio remains strictly inside the envelope throughout every coordinate gap:

\[
-1<R_\theta(x)<1.
\]

Therefore no continuous first exit occurs in any coordinate gap.

---

## 9. Main Certificate Theorem

### Theorem 1 â€” Active ThetaBridge FinalCertificate Closure

For the active bridge

\[
G_\theta(x)=\theta(x)-x,
\]

with envelope

\[
\mathcal E_\theta(x)
=
1.9233607946440099\sqrt{x}\log^2x,
\]

the reproduced Prime Mesh R2Q certificate stack rules out post-\(P_0\) first-exit obstructions in the audited/certified system.

More precisely:

1. all \(142/142\) post-\(P_0\) candidate windows are covered;
2. all \(120/120\) upper candidates are represented;
3. all \(22/22\) lower candidates are bracketed;
4. all \(141/141\) coordinate gaps are margin-safe;
5. ThresholdRelevance has \(0\) failures across \(10140\) rows;
6. upper rows are subthreshold by positive harmlessness;
7. lower rows have no surviving unrepaid obstruction;
8. neutral rows are empty.

Therefore no post-\(P_0\) first-exit obstruction survives for the active theta bridge.

---

## 10. Proof Skeleton

Assume a post-\(P_0\) first exit exists for the active theta bridge.

It must lie either:

1. in an audited candidate/bracket window; or
2. in a coordinate gap.

### Case 1 â€” Candidate or Bracket Window

By ThresholdRelevance, any surviving first-crossing obstruction satisfies

\[
Q_{\rm R2Q}>0.75.
\]

Split by endpoint sign.

If upper, then

\[
E_\theta>0.
\]

By positive harmlessness,

\[
Q_{\rm R2Q}\le0.305<0.75,
\]

contradiction.

If lower, then

\[
E_\theta<0.
\]

Lower rows are O2/B3/finite/non-surviving safe, with lower surviving unrepaid rows equal to zero. Thus no lower obstruction survives.

Neutral rows are empty.

Therefore no candidate/bracket first-exit obstruction survives.

### Case 2 â€” Coordinate Gap

All coordinate gaps are margin-safe:

\[
-1<R_\theta(x)<1.
\]

Thus no first exit can occur in a coordinate gap.

Both cases contradict the existence of a surviving post-\(P_0\) first exit.

---

## 11. Finite Zone

The post-tail argument begins after

\[
P_0=500,000,000.
\]

Rows below this cutoff are handled by finite certificates. The final claim must include the finite certificate index and finite-zone verification.

The global certificate conclusion is therefore:

\[
\text{finite-zone certificates}
+
\text{post-}P_0\text{ certificate closure}
\Rightarrow
\text{certificate-level theta RH-scale bound}.
\]

---

## 12. Theta-to-Psi Transfer

The second Chebyshev function satisfies

\[
\psi(x)
=
\theta(x)
+
\sum_{k\ge2}\sum_{p^k\le x}\log p.
\]

Define the prime-power correction

\[
P_{\rm powers}(x)=\psi(x)-\theta(x).
\]

Then

\[
P_{\rm powers}(x)
\le
\sum_{k\ge2}\theta(x^{1/k}).
\]

Using standard estimates such as

\[
\theta(y)=O(y),
\]

we obtain safely

\[
P_{\rm powers}(x)=O(\sqrt{x}\log^2x).
\]

This is the standard prime-power correction estimate; for example, it follows
from the elementary bound \(\theta(y)=O(y)\) applied to
\(\sum_{k\ge2}\theta(x^{1/k})\). Standard references include E. C. Titchmarsh,
*The Theory of the Riemann Zeta-Function*, 2nd ed., edited by D. R. Heath-Brown,
and H. Davenport, *Multiplicative Number Theory*, 3rd ed.

Thus

\[
\theta(x)-x=O(\sqrt{x}\log^2x)
\Rightarrow
\psi(x)-x=O(\sqrt{x}\log^2x).
\]

---

## 13. von Koch Criterion

A classical von Koch criterion states that

\[
\psi(x)-x=O(\sqrt{x}\log^2x)
\]

is an RH-scale condition equivalent to the Riemann Hypothesis in the standard
framework. This is the classical von Koch criterion; see H. von Koch, "Sur la
distribution des nombres premiers," *Acta Mathematica* 24 (1901), and modern
accounts such as Titchmarsh, *The Theory of the Riemann Zeta-Function*.

Therefore, if the active theta bridge certificate stack is independently
verified as sufficient to establish the stated global theta control, then the
theta bridge gives

\[
\theta(x)-x=O(\sqrt{x}\log^2x),
\]

which transfers to

\[
\psi(x)-x=O(\sqrt{x}\log^2x),
\]

and hence reaches the von Koch RH-scale criterion.

The current paper states this as a certificate-level route, pending independent verification.

---

## 14. Reproducibility

The final one-command runner is

```text
run_all_final_audits.py
```

It produces:

```text
Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md
prime_mesh_r2q_final_reproduction_report.csv
prime_mesh_r2q_final_artifact_hashes.txt
final_audit_logs/
```

The reported final status is

\[
\texttt{PASS}.
\]

It reproduces the key results:

\[
G(x)=\theta(x)-x,
\]

\[
C_\theta=1.9233607946440099,
\]

\[
142/142
\]

post-\(P_0\) windows covered,

\[
141/141
\]

coordinate gaps margin-safe,

\[
10140
\]

ThresholdRelevance rows checked,

\[
R_{\rm upper,global,max}
=
-0.0006006774736066138,
\]

\[
R_{\rm lower,global,min}
=
-0.0007553068873594187,
\]

and

\[
22637
\]

prime jumps inside gaps.

---

## 15. Certificate vs. Symbolic Proof

The current status is certificate-level.

This means:

1. the audit chain is reproducible;
2. the numerical/certificate claims are explicit;
3. failure routes are excluded;
4. the final runner returns PASS;
5. independent review is still required.

This paper does not claim that RH is externally accepted as proven.

It does not claim H-Exc full-grid control.

It does not claim the candidate windows tile all coordinates.

It does not claim the result applies automatically to every possible \(G(x)\).

The active bridge is

\[
G(x)=\theta(x)-x.
\]

---

## 16. Known Excluded Routes and Caveats

The following route is explicitly rejected:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
Q_{\Delta D}>0.75.
\]

The direct sign route is used instead:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta<0.
\]

H-Exc is sampled-grid only.

B3 is row-level, not chain-indexed.

Finite certificates are part of the result.

Coordinate gaps are closed by normalized theta margin certificates, not by tiling.

---

## 17. Reviewer Instructions

A reviewer should begin with:

```text
README_REPRODUCIBILITY.md
Prime_Mesh_R2Q_Reviewer_Package_Index_v1.md
Prime_Mesh_R2Q_Final_Reproduction_Report_v1.md
Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md
```

Then run:

```text
python run_all_final_audits.py
```

and verify final status:

```text
PASS
```

The reviewer should inspect:

```text
prime_mesh_r2q_normalized_error_gapmargin_rows.csv
prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv
prime_mesh_r2q_postp0_continuous_window_selection_summary.csv
prime_mesh_r2q_final_artifact_hashes.txt
```

---

## 18. Safe Main Claim

A safe statement is:

> The Prime Mesh R2Q active theta-bridge certificate stack has one-command reproducibility. Running `run_all_final_audits.py` reproduces final status `PASS`, including \(142/142\) post-\(P_0\) windows covered, \(141/141\) coordinate gaps margin-safe, \(10{,}140\) ThresholdRelevance rows checked with zero failures, and normalized gap bounds strictly inside the RH-scale envelope. This gives a certificate-level route to the Chebyshev/von Koch RH-scale criterion for the active theta bridge, pending independent review.

---

## 19. What Not To Claim Yet

Do not claim:

\[
\text{RH is proven}.
\]

Do not claim:

\[
\text{the result is peer-reviewed}.
\]

Do not claim:

\[
\text{the certificate stack is unnecessary}.
\]

Do not claim:

\[
\text{H-Exc full-grid control is available}.
\]

Do not claim:

\[
\text{candidate windows tile all coordinates}.
\]

---

## 20. Conclusion

The Prime Mesh R2Q programme has reached a strong reproducible certificate milestone.

For the active theta bridge

\[
G(x)=\theta(x)-x,
\]

the certificate stack rules out post-\(P_0\) first-exit obstructions against the envelope

\[
1.9233607946440099\sqrt{x}\log^2x.
\]

The final runner reproduces the stack with status

\[
\texttt{PASS}.
\]

The next phase is independent review, proof-audit, and careful presentation of the certificate-level route to the von Koch RH-scale criterion.

---

*Prime Mesh Theory â€” RH Programme*
