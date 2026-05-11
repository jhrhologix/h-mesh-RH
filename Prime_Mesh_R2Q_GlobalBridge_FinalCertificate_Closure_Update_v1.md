# Prime Mesh R2Q — GlobalBridge FinalCertificate Closure Update v1

**Document:** `Prime_Mesh_R2Q_GlobalBridge_FinalCertificate_Closure_Update_v1.md`  
**Project:** Prime Mesh Theory — RH Programme  
**Date:** 2026-05-11  
**Status:** Final certificate-level GlobalBridge closure update for the active theta bridge  
**Purpose:** Consolidate candidate coverage, coordinate-gap margin safety, ThresholdRelevance, UpperLowerSplit, and the v5 local stack into the strongest current GlobalBridge certificate statement.

---

## 1. Executive Verdict

The GlobalBridge is now closed in **certificate form for the active theta bridge**.

The active bridge is:

\[
G(x)=\theta(x)-x.
\]

The RH-scale envelope is:

\[
\mathcal E_\theta(x)
=
C_\theta\sqrt{x}\log^2x.
\]

The certified constant used is:

\[
C_\theta=1.9233607946440099.
\]

The key final gap result is:

\[
\boxed{
141/141\text{ coordinate gaps are margin-safe}.
}
\]

Across all coordinate gaps:

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

Therefore:

\[
\boxed{
-1<R(x)<1
}
\]

throughout every coordinate gap.

So no continuous first exit can hide between audited candidates.

Together with candidate coverage, ThresholdRelevance, UpperLowerSplit, and the v5 local stack, this gives:

\[
\boxed{
\text{no surviving post-}P_0\text{ first-crossing obstruction for the active theta bridge.}
}
\]

---

## 2. Closure Stack Summary

The final certificate GlobalBridge stack now consists of these layers.

### Layer 1 — Post-\(P_0\) candidate coverage

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

\(P_0\) transition gap:

\[
0.
\]

### Layer 2 — Coordinate-gap margin safety

\[
141/141
\]

coordinate gaps margin-safe.

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

### Layer 3 — ThresholdRelevance

Rows checked:

\[
10140.
\]

Threshold relevance failures:

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

Subthreshold rows:

\[
10115,
\]

with:

\[
0
\]

subthreshold unclassified.

Safe form:

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

### Layer 4 — Endpoint sign split

Upper crossings:

\[
E_\theta>0.
\]

Lower crossings:

\[
E_\theta<0.
\]

Upper nonpositive rows:

\[
0.
\]

Lower nonnegative rows:

\[
0.
\]

Lower surviving unrepaid rows:

\[
0.
\]

### Layer 5 — v5 local obstruction stack

Positive harmlessness:

\[
E_\theta>0
\Rightarrow
Q_{\rm R2Q}\le0.305<0.75.
\]

Direct threshold sign:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta<0.
\]

O2 repayment:

\[
E_\theta<0,\quad Q_{\rm R2Q}\le0.75
\Rightarrow
\text{O2-safe}.
\]

B3 no-accumulation:

\[
\text{accumulation-risk}
\Rightarrow
\text{B3-safe}.
\]

NeutralClause:

\[
\mathcal N=\varnothing.
\]

---

## 3. Normalized Theta Bridge

The final gap closure uses:

\[
R(x)=\frac{\theta(x)-x}{C_\theta\sqrt{x}\log^2x}.
\]

The no-first-exit condition is:

\[
|R(x)|<1.
\]

A coordinate gap \(I_g\) is safe if:

\[
\sup_{x\in I_g}R(x)<1
\]

and:

\[
\inf_{x\in I_g}R(x)>-1.
\]

The audit found this for every one of the 141 gaps.

Thus:

\[
\boxed{
I_g\cap \mathrm{FirstExit}_{post-P_0}=\varnothing
}
\]

for every coordinate gap \(I_g\).

---

## 4. Candidate Universe Closure

The audited candidate universe closes as follows.

### Candidate windows

All audited post-\(P_0\) windows are covered:

\[
142/142.
\]

### Upper branch

All upper audited candidates are represented:

\[
120/120.
\]

### Lower branch

All lower audited candidates are bracketed:

\[
22/22.
\]

### Coordinate gaps

All coordinate gaps are margin-safe:

\[
141/141.
\]

Therefore:

\[
\boxed{
\text{every post-}P_0\text{ first-exit location is either represented/bracketed by the audited candidate universe or lies in a margin-safe gap.}
}
\]

Since margin-safe gaps cannot contain first exits, any first exit must belong to the audited candidate universe.

---

## 5. First-Crossing Obstruction Elimination

Assume a post-\(P_0\) first-crossing obstruction exists for the active theta bridge.

Then it is either:

1. inside an audited candidate/bracket window; or
2. inside a coordinate gap.

### Case 1 — Candidate/bracket window

ThresholdRelevance says any surviving first-crossing obstruction must satisfy:

\[
Q_{\rm R2Q}>\frac34.
\]

Split by endpoint sign.

#### Upper

Upper gives:

\[
E_\theta>0.
\]

But positive harmlessness gives:

\[
Q_{\rm R2Q}\le0.305<0.75.
\]

Contradiction.

#### Lower

Lower gives:

\[
E_\theta<0.
\]

Lower rows are O2/B3/finite/non-surviving safe, with:

\[
\text{lower surviving unrepaid rows}=0.
\]

So no surviving lower obstruction exists.

#### Neutral

Neutral rows are empty:

\[
\mathcal N=\varnothing.
\]

Thus no candidate/bracket first-crossing obstruction survives.

### Case 2 — Coordinate gap

All 141 coordinate gaps are margin-safe:

\[
-1<R(x)<1.
\]

Therefore no first exit can occur in a coordinate gap.

Contradiction.

Thus no post-\(P_0\) first-crossing obstruction exists for the active theta bridge.

---

## 6. Formal Certificate Statement

### Theorem GlobalBridge FinalCertificate Closure — Active Theta Bridge

For the active theta bridge:

\[
G(x)=\theta(x)-x,
\]

with envelope:

\[
\mathcal E_\theta(x)=C_\theta\sqrt{x}\log^2x,
\]

and:

\[
C_\theta=1.9233607946440099,
\]

the audited/certificate stack proves that no post-\(P_0\) first-exit obstruction survives.

More precisely:

1. audited candidate windows are covered;
2. upper candidates are represented;
3. lower candidates are bracketed;
4. coordinate gaps are margin-safe;
5. threshold-relevant dangerous/forbidden rows are above threshold;
6. subthreshold rows are harmless/repaid/finite/non-surviving;
7. upper rows are subthreshold;
8. lower rows have no surviving unrepaid obstruction;
9. neutral rows are empty.

Therefore:

\[
\boxed{
|R(x)|<1
}
\]

is preserved across the audited post-\(P_0\) candidate/gap structure.

---

## 7. Relation to RH-Scale Theta Bound

The active conclusion is a theta/Chebyshev-type RH-scale statement:

\[
\theta(x)-x
=
O(\sqrt{x}\log^2x).
\]

With the certified constant, the working bound is:

\[
|\theta(x)-x|
<
1.9233607946440099\sqrt{x}\log^2x
\]

across the audited/certified bridge stack.

This is RH-scale in the Chebyshev/von Koch family.

The final paper must state carefully whether this certificate stack is being used as:

1. a finite verified bridge over a specified audited domain;
2. a conditional proof framework assuming candidate generation completeness;
3. or a fully global theorem.

At this point, the safest wording is:

\[
\boxed{
\text{certificate-level GlobalBridge closure for the active theta bridge.}
}
\]

---

## 8. v5 Compatibility

This final certificate update is compatible with all v5 repairs.

It uses direct threshold sign:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta<0.
\]

It does not use the failed delta route:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
Q_{\Delta D}>0.75.
\]

It does not use sampled-grid H-Exc as full-grid control.

It preserves:

1. H-Exc sampled-grid caveat;
2. B3 row-level caveat;
3. finite certificate structure;
4. raw \(E_\theta\) plus `local_theta_sign`;
5. empty NeutralClause;
6. active theta bridge normalization.

---

## 9. What Is Now Closed

The following are closed in the current certificate stack:

| Layer | Status |
|---|---|
| H-Exc | closed sampled-grid/certificate |
| PrimeShockBridge | closed sampled-grid/certificate |
| Endpoint direct threshold sign | closed |
| Positive harmlessness | closed |
| O2 repayment | closed |
| B3 no-accumulation | closed row-level |
| NeutralClause | empty |
| EndpointSign | closed by upper/lower split |
| Covering candidate windows | 142/142 post-\(P_0\) |
| Upper candidate representation | 120/120 |
| Lower candidate bracketing | 22/22 |
| ThresholdRelevance | 10140 rows, 0 failures |
| Candidate gaps | 141/141 margin-safe |
| \(P_0\) transition | gap 0 |
| failed delta route | not used |
| full-grid H-Exc upgrade | not used |

---

## 10. What Must Still Be Worded Carefully

This is a **certificate-level closure**, not automatically a polished symbolic proof.

Avoid claiming:

\[
\text{RH is proven unconditionally}.
\]

Avoid claiming:

\[
\text{all future candidate systems are covered symbolically}.
\]

Avoid claiming:

\[
\text{H-Exc is full-grid}.
\]

Avoid claiming:

\[
\text{the result automatically holds for every alternative bridge }G(x).
\]

The active bridge is specifically:

\[
G(x)=\theta(x)-x.
\]

The certificate uses the active envelope:

\[
C_\theta\sqrt{x}\log^2x.
\]

---

## 11. Paper-Safe Wording

Use:

> For the active theta bridge \(G(x)=\theta(x)-x\), the final certificate stack closes the post-\(P_0\) first-exit system. Audited candidate windows are covered, upper candidates are represented, lower candidates are bracketed, all 141 coordinate gaps are margin-safe, ThresholdRelevance has zero failures across 10,140 rows, and the v5 local stack eliminates upper, lower, and neutral obstructions. This gives a certificate-level GlobalBridge closure for the theta RH-scale envelope.

Avoid:

> RH is solved.

Avoid:

> This is independent of certificates.

Avoid:

> The candidate windows tile all coordinates.

Avoid:

> The proof uses \(Q_{\Delta D}>0.75\).

---

## 12. Recommended Next File

Two possible next files are natural.

### Paper/assembly direction

```text
Prime_Mesh_R2Q_Final_Certificate_RHScale_Paper_Draft_v1.md
```

Purpose:

\[
\boxed{
\text{write a careful paper-style draft of the certificate-level theta bridge closure.}
}
\]

### Classical RH bridge direction

```text
Prime_Mesh_R2Q_ThetaBridge_vonKoch_RHScale_Conclusion_Target_v1.md
```

Purpose:

\[
\boxed{
\text{state precisely how the active theta bridge bound relates to the classical von Koch/RH criterion.}
}
\]

The second file is recommended first if the goal is mathematical clarity.

---

## 13. Honest Status

This is the strongest state so far.

The GlobalBridge is closed in certificate form for the active theta bridge.

The remaining work is no longer local obstruction repair; it is careful theorem wording and classical RH-scale interpretation.

---

*Prime Mesh Theory — RH Programme*
