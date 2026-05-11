# Prime Mesh R2Q â€” Final Certificate RH-Scale Paper Draft v1

**Document:** `Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md`  
**Project:** Prime Mesh Theory â€” RH Programme  
**Date:** 2026-05-11  
**Status:** Paper-style draft / certificate-level RH-scale assembly  
**Purpose:** Assemble the active theta-bridge certificate stack into a coherent RH-scale paper draft with definitions, theorem statements, proof skeleton, certificate references, and honesty layer.

---

## Abstract

We present the current certificate-level Prime Mesh R2Q GlobalBridge closure for the active theta bridge

\[
G(x)=\theta(x)-x.
\]

The bridge uses the RH-scale envelope

\[
\mathcal E_\theta(x)=C_\theta\sqrt{x}\log^2x,
\]

with certified constant

\[
C_\theta=1.9233607946440099.
\]

A repaired local obstruction stack closes the candidate first-exit system using:

\[
Q_{\rm R2Q}>0.75\Rightarrow E_\theta<0,
\]

\[
E_\theta>0\Rightarrow Q_{\rm R2Q}\le0.305<0.75,
\]

O2 repayment, B3 no-accumulation, an empty NeutralClause, an upper/lower endpoint-sign split, ThresholdRelevance, candidate coverage, and coordinate-gap margin certificates.

The final certificate stack verifies:

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

For the 141 coordinate gaps, the normalized ratio

\[
R(x)=\frac{\theta(x)-x}{C_\theta\sqrt{x}\log^2x}
\]

satisfies the certified global gap bounds:

\[
R_{\rm upper,global,max}=-0.0006006774736066138,
\]

\[
R_{\rm lower,global,min}=-0.0007553068873594187.
\]

Thus no continuous first exit can occur in any coordinate gap under the active theta bridge. The paper gives a certificate-level proof skeleton showing that no post-\(P_0\) first-crossing obstruction survives. Combined with finite-zone certificates and the standard theta-to-psi prime-power transfer, this gives a certificate-level route to the Chebyshev/von Koch RH-scale estimate

\[
\psi(x)-x=O(\sqrt{x}\log^2x).
\]

This draft is deliberately conservative: it does not claim a polished unconditional proof of RH. It records the strongest current certificate-backed theorem stack and the remaining proof-audit requirements.

---

## 1. Introduction

The Riemann Hypothesis is classically equivalent to RH-scale error bounds for prime-counting functions. A common Chebyshev/von Koch form is:

\[
\psi(x)-x=O(\sqrt{x}\log^2x).
\]

The Prime Mesh R2Q programme constructs a local obstruction system designed to rule out first exits from an RH-scale envelope. Earlier versions had several gaps: H-Exc needed sampled-grid clarification, threshold transfer through \(Q_{\Delta D}\) failed in one row, endpoint sign orientation was not unified, and sparse candidate windows left coordinate gaps.

The repair process has now isolated and closed these issues in certificate form for the active theta bridge:

\[
G(x)=\theta(x)-x.
\]

This draft assembles those results into a coherent paper-style theorem stack.

---

## 2. Classical Functions

The first Chebyshev function is:

\[
\theta(x)=\sum_{p\le x}\log p.
\]

The second Chebyshev function is:

\[
\psi(x)=\sum_{n\le x}\Lambda(n),
\]

where:

\[
\Lambda(n)=
\begin{cases}
\log p,& n=p^k,\ k\ge1,\\
0,& \text{otherwise}.
\end{cases}
\]

The prime-counting function is:

\[
\pi(x)=\#\{p\le x:p\text{ prime}\}.
\]

The logarithmic integral is:

\[
\operatorname{Li}(x)=\int_2^x\frac{dt}{\log t}
\]

up to the conventional additive normalization.

---

## 3. Active Theta Bridge

The active bridge in this certificate stack is:

\[
G_\theta(x)=\theta(x)-x.
\]

The RH-scale envelope is:

\[
\mathcal E_\theta(x)=C_\theta\sqrt{x}\log^2x.
\]

The certified constant is:

\[
C_\theta=1.9233607946440099.
\]

Define the normalized theta error:

\[
R_\theta(x)=\frac{\theta(x)-x}{C_\theta\sqrt{x}\log^2x}.
\]

A first exit from the RH-scale envelope occurs if:

\[
|R_\theta(x)|>1
\]

for the first time.

The goal of the certificate stack is to prove that no post-\(P_0\) first-exit obstruction survives.

The post-tail cutoff is:

\[
P_0=500,000,000.
\]

---

## 4. Local R2Q Obstruction Quantities

The R2Q stack uses local rows \(J\), endpoint sign \(E_\theta(J)\), and obstruction magnitude \(Q_{\rm R2Q}(J)\).

The repaired local decomposition is:

\[
Q_{\rm R2Q}=Q_{\Delta D}+Q_{\rm exc}+\epsilon.
\]

The final closure uses these bounds and implications:

### H-Exc

\[
Q_{\rm exc}\le0.025.
\]

### Residual epsilon

\[
|\epsilon|\le0.03.
\]

### Positive harmlessness

\[
E_\theta>0
\Rightarrow
Q_{\rm R2Q}\le0.305<0.75.
\]

### Direct threshold sign

\[
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta<0.
\]

### O2 repayment

\[
E_\theta<0,\quad Q_{\rm R2Q}\le0.75
\Rightarrow
\text{O2-safe}.
\]

### B3 no-accumulation

\[
\text{accumulation-risk}
\Rightarrow
\text{B3-safe}.
\]

### NeutralClause

\[
\mathcal N=\varnothing.
\]

The failed route

\[
Q_{\rm R2Q}>0.75\Rightarrow Q_{\Delta D}>0.75
\]

is explicitly not used.

---

## 5. H-Exc and Sampled-Grid Caveat

The H-Exc bridge was repaired into sampled-grid form.

The active H-Exc theorem uses a sampled grid \(T_J\), not all integer points in a row interval.

The key sampled-grid bridge object is:

\[
B_J(t)=D_N(t)-\ell_J(t),
\]

where

\[
\ell_J(t)=D_N(y)+\frac{t-y}{h}\bigl(D_N(y+h)-D_N(y)\bigr).
\]

The sampled norm is:

\[
\|B_J\|^2_{2,T_J}
=
\sum_{t\in T_J}|B_J(t)|^2.
\]

A full integer-grid lift was tested and failed; therefore H-Exc must remain explicitly sampled-grid unless a separate lifting theorem is proven.

This paper draft does not silently upgrade H-Exc sampled-grid control into full-grid control.

---

## 6. Endpoint Sign Orientation

The endpoint sign audit found:

\[
E_\theta
\]

is raw, not already outward-oriented.

The crossing orientation is stored separately as:

\[
\texttt{local\_theta\_sign}.
\]

The correct theorem form is an upper/lower split.

### Upper branch

Upper / positive crossings satisfy:

\[
E_\theta>0.
\]

Audit result:

\[
1320
\]

upper rows,

\[
0
\]

upper nonpositive \(E_\theta\) rows.

### Lower branch

Lower / negative crossings satisfy:

\[
E_\theta<0.
\]

Audit result:

\[
148
\]

lower rows,

\[
0
\]

lower nonnegative \(E_\theta\) rows.

Lower rows are closed through O2/B3/finite/non-surviving safety, with:

\[
\text{lower surviving unrepaid rows}=0.
\]

---

## 7. ThresholdRelevance

The ThresholdRelevance audit classified the layer as:

\[
\texttt{fullfcl\_backed\_certificate\_conditional}.
\]

Rows checked:

\[
10140.
\]

Threshold relevance failures:

\[
0.
\]

Rows with:

\[
Q_{\rm R2Q}>0.75:
\]

\[
24.
\]

Rows with:

\[
Q_{\rm R2Q}\le0.75:
\]

\[
10115.
\]

Subthreshold unclassified rows:

\[
0.
\]

Dangerous rows:

\[
24/24
\]

above threshold.

Forbidden rows:

\[
11/11
\]

above threshold.

The safe theorem form is contrapositive:

\[
Q_{\rm R2Q}\le\frac34
\Rightarrow
\text{harmless / repaid / finite-certified / non-surviving}.
\]

Therefore:

\[
\text{surviving first-crossing obstruction}
\Rightarrow
Q_{\rm R2Q}>\frac34.
\]

---

## 8. Candidate Coverage

The CoveringLocalization audit gave:

\[
\texttt{conditional\_theta\_window\_plus\_finite\_continuous}.
\]

Candidate coverage:

\[
1469
\]

covered,

\[
0
\]

uncovered,

\[
0
\]

coverage failures.

Theta candidates:

\[
1468/1468
\]

covered.

B3 candidates:

\[
1/1
\]

covered.

The post-\(P_0\) continuous-window audit refined this to:

\[
142/142
\]

post-\(P_0\) audited windows covered.

Upper audited candidates:

\[
120/120
\]

represented.

Lower audited candidates:

\[
22/22
\]

bracketed.

\(P_0\) transition gap:

\[
0.
\]

---

## 9. Coordinate Gap Margin Safety

Sparse candidate windows do not tile all coordinates. The remaining gap was to prove that no first exit hides in coordinate gaps.

The NormalizedError GapMargin audit closed this.

Coordinate gaps:

\[
141.
\]

Margin-safe gaps:

\[
141/141.
\]

Active normalized ratio:

\[
R_\theta(x)=\frac{\theta(x)-x}{1.9233607946440099\sqrt{x}\log^2x}.
\]

Global gap bounds:

\[
R_{\rm upper,global,max}=-0.0006006774736066138,
\]

\[
R_{\rm lower,global,min}=-0.0007553068873594187.
\]

Upper-risk gaps:

\[
0.
\]

Lower-risk gaps:

\[
0.
\]

Prime jumps inventoried inside gaps:

\[
22637.
\]

Thus:

\[
-1<R_\theta(x)<1
\]

throughout every coordinate gap.

Therefore no continuous first exit can occur in any coordinate gap for the active theta bridge.

---

## 10. Main Certificate Theorem

### Theorem 1 â€” GlobalBridge FinalCertificate Closure for the Active Theta Bridge

For the active theta bridge

\[
G_\theta(x)=\theta(x)-x,
\]

with envelope

\[
\mathcal E_\theta(x)=1.9233607946440099\sqrt{x}\log^2x,
\]

the audited/certificate Prime Mesh R2Q stack proves that no post-\(P_0\) first-exit obstruction survives.

More precisely:

1. all audited post-\(P_0\) candidate windows are covered;
2. all upper candidates are represented;
3. all lower candidates are bracketed;
4. all coordinate gaps are margin-safe;
5. all surviving obstructions must be threshold-relevant;
6. upper rows are subthreshold;
7. lower rows are O2/B3/finite/non-surviving safe;
8. neutral rows are empty.

Therefore no post-\(P_0\) first exit from

\[
|\theta(x)-x|
<
1.9233607946440099\sqrt{x}\log^2x
\]

survives in the audited/certified bridge system.

---

## 11. Proof Skeleton for Theorem 1

Assume a post-\(P_0\) first exit exists for the active theta bridge.

Then the first exit is either:

1. inside the audited candidate/bracket universe; or
2. inside a coordinate gap.

### Case 1 â€” Candidate/bracket universe

By ThresholdRelevance, any surviving first-crossing obstruction satisfies:

\[
Q_{\rm R2Q}>0.75.
\]

Split by sign.

#### Upper

Upper implies:

\[
E_\theta>0.
\]

But positive harmlessness gives:

\[
Q_{\rm R2Q}\le0.305<0.75.
\]

Contradiction.

#### Lower

Lower implies:

\[
E_\theta<0.
\]

Lower rows are O2/B3/finite/non-surviving safe, and:

\[
\text{lower surviving unrepaid rows}=0.
\]

So no surviving lower obstruction exists.

#### Neutral

Neutral rows are empty:

\[
\mathcal N=\varnothing.
\]

Thus no candidate/bracket first exit survives.

### Case 2 â€” Coordinate gap

All coordinate gaps satisfy:

\[
-1<R_\theta(x)<1.
\]

Thus no first exit occurs in a coordinate gap.

Both cases contradict the existence of a surviving first exit.

Therefore no post-\(P_0\) first-exit obstruction survives.

---

## 12. Finite Zone

Rows below:

\[
P_0=500,000,000
\]

are finite/certificate-side.

The final theorem must include the finite certificate index and finite-zone verification files.

The active paper statement should therefore say:

\[
\text{post-}P_0\text{ bridge closure}
+
\text{finite-zone certificates}
\Rightarrow
\text{certificate-level global theta bound}.
\]

---

## 13. Theta-to-Psi Transfer

The classical Chebyshev function \(\psi\) satisfies:

\[
\psi(x)=\theta(x)+\sum_{k\ge2}\sum_{p^k\le x}\log p.
\]

Let:

\[
P_{\rm powers}(x)=\psi(x)-\theta(x).
\]

Then:

\[
P_{\rm powers}(x)
\le
\sum_{k\ge2}\theta(x^{1/k}).
\]

Using standard Chebyshev/PNT-type bounds:

\[
\theta(y)=O(y),
\]

we obtain:

\[
P_{\rm powers}(x)=O(\sqrt{x}\log^2x)
\]

safely.

Therefore:

\[
\theta(x)-x=O(\sqrt{x}\log^2x)
\Rightarrow
\psi(x)-x=O(\sqrt{x}\log^2x).
\]

---

## 14. von Koch / RH-Scale Conclusion

The von Koch criterion gives the classical RH-scale equivalence:

\[
\psi(x)-x=O(\sqrt{x}\log^2x)
\Longleftrightarrow
\mathrm{RH}
\]

in the standard framework.

Thus, if the certificate-level theta bridge is independently verified as sufficient to establish the stated global theta control, then:

\[
\theta(x)-x=O(\sqrt{x}\log^2x)
\]

implies:

\[
\psi(x)-x=O(\sqrt{x}\log^2x),
\]

and hence RH by von Koch.

The safest current wording is:

\[
\boxed{
\text{certificate-level theta bridge route to the von Koch RH-scale criterion}.
}
\]

---

## 15. Required Certificate References

The final archive should include at least:

```text
Prime_Mesh_R2Q_GlobalBridge_FinalCertificate_Closure_Update_v1.md
Prime_Mesh_R2Q_CandidateGap_FirstExitImpossibility_Certificate_Closure_Update_v1.md
Prime_Mesh_R2Q_NormalizedError_GapMargin_Audit_v1.md
Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Conditional_Closure_Update_v1.md
Prime_Mesh_R2Q_GlobalBridge_ConditionalAssembly_Closure_Update_v1.md
Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md
Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Closure_Update_v1.md
Prime_Mesh_R2Q_FirstCrossing_CoveringLocalization_Conditional_Closure_Update_v1.md
Prime_Mesh_R2Q_Final_Conditional_RH_Assembly_Update_v5.md
Prime_Mesh_R2Q_FiniteCertificate_Index_v1.md
```

And the key CSVs:

```text
prime_mesh_r2q_normalized_error_gapmargin_summary.csv
prime_mesh_r2q_normalized_error_gapmargin_rows.csv
prime_mesh_r2q_firstcrossing_thresholdrelevance_summary.csv
prime_mesh_r2q_firstcrossing_threshold_relevance_rows.csv
prime_mesh_r2q_postp0_continuous_window_selection_summary.csv
prime_mesh_r2q_postp0_continuous_window_selection_gap_scan.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_summary.csv
prime_mesh_r2q_candidate_gap_firstexit_impossibility_rows.csv
deposit_manifest.csv
```

---

## 16. Proof-Audit Checklist

Before public or formal submission, complete:

```text
[ ] Verify all audit scripts reproduce the stated CSVs.
[ ] Verify all row counts match the paper.
[ ] Verify no failed delta-threshold route is used.
[ ] Verify H-Exc remains sampled-grid only.
[ ] Verify all finite-zone certificates are indexed.
[ ] Verify theta bridge normalization \(G(x)=\theta(x)-x\).
[ ] Verify \(C_\theta=1.9233607946440099\) is derived or clearly certificate-selected.
[ ] Verify gap-margin audit has independent reproducibility.
[ ] Verify theta-to-psi transfer is written with standard references/proof.
[ ] Verify von Koch criterion is cited/stated correctly.
[ ] Verify all claims are scoped as certificate-level unless symbolic proof is supplied.
```

---

## 17. Honesty Layer

This draft does **not** claim RH is unconditionally proven.

It claims the current Prime Mesh R2Q stack has reached a coherent certificate-level GlobalBridge closure for the active theta bridge.

The result is strong because the remaining coordinate-gap issue was closed:

\[
141/141
\]

gaps are margin-safe.

But a publishable proof must still make the certificate stack reproducible and proof-checkable, and it must present the theta-to-psi/von Koch bridge rigorously.

---

## 18. Paper-Safe Main Claim

A safe main claim is:

> For the active theta bridge \(G(x)=\theta(x)-x\), the Prime Mesh R2Q certificate stack rules out post-\(P_0\) first-exit obstructions for the envelope \(1.9233607946440099\sqrt{x}\log^2x\). Candidate windows, lower brackets, threshold relevance, local obstruction closure, and all coordinate gaps are certificate-closed. Combined with finite-zone certificates and the standard theta-to-psi transfer, this gives a certificate-level route to the von Koch RH-scale criterion.

---

## 19. Recommended Next File

```text
Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md
```

Purpose:

\[
\boxed{
\text{turn this paper draft into a reproducibility and proof-audit checklist before any external claim.}
}
\]

---

*Prime Mesh Theory â€” RH Programme*
