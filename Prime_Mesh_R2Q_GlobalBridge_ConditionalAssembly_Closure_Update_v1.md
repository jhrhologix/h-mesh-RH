# Prime Mesh R2Q — GlobalBridge ConditionalAssembly Closure Update v1

**Document:** `Prime_Mesh_R2Q_GlobalBridge_ConditionalAssembly_Closure_Update_v1.md`  
**Project:** Prime Mesh Theory — RH Programme  
**Date:** 2026-05-11  
**Status:** Conditional GlobalBridge closure update  
**Purpose:** Consolidate CoveringLocalization, ThresholdRelevance, UpperLowerSplit, and the v5 local stack into one conditional GlobalBridge assembly.

---

## 1. Executive Verdict

The GlobalBridge is now conditionally assembled.

The correct status is:

\[
\boxed{
\text{GlobalBridge closed conditionally on post-}P_0\text{ continuous all-}x\text{ / FullFCL candidate selection.}
}
\]

The audited/certificate pieces now align:

1. **CoveringLocalization**
   \[
   \texttt{conditional\_theta\_window\_plus\_finite\_continuous}.
   \]

2. **ThresholdRelevance**
   \[
   \texttt{fullfcl\_backed\_certificate\_conditional}.
   \]

3. **EndpointSign**
   \[
   \texttt{upper\_lower\_split}.
   \]

4. **v5 local obstruction stack**
   closed in audited/certificate form.

Thus:

\[
\boxed{
\text{assuming every post-}P_0\text{ continuous global first crossing enters the audited FullFCL/theta candidate universe, no surviving first-crossing obstruction remains.}
}
\]

The remaining open analytic bridge is concentrated in one statement:

\[
\boxed{
\text{post-}P_0\text{ continuous all-}x\text{ / FullFCL candidate-selection theorem.}
}
\]

---

## 2. Conditional Inputs Now Available

### Input A — CoveringLocalization

Audit classification:

\[
\boxed{
\texttt{conditional\_theta\_window\_plus\_finite\_continuous}.
}
\]

Audit facts:

\[
\text{covered candidates}=1469,
\]

\[
\text{uncovered candidates}=0,
\]

\[
\text{coverage failures}=0.
\]

Theta candidates:

\[
1468/1468\text{ covered}.
\]

B3 candidates:

\[
1/1\text{ covered}.
\]

Finite-zone continuous certificate:

\[
\text{passes}.
\]

Remaining caveat:

\[
\text{post-}P_0\text{ continuous all-}x\text{ / window-selection proof remains conditional}.
\]

---

### Input B — ThresholdRelevance

Audit classification:

\[
\boxed{
\texttt{fullfcl\_backed\_certificate\_conditional}.
}
\]

Audit facts:

\[
\text{rows checked}=10140,
\]

\[
\text{threshold relevance failures}=0,
\]

\[
Q_{\rm R2Q}>0.75\text{ rows}=24,
\]

\[
Q_{\rm R2Q}\le0.75\text{ rows}=10115,
\]

\[
\text{subthreshold unclassified rows}=0.
\]

Dangerous rows:

\[
24/24\text{ above threshold}.
\]

Forbidden rows:

\[
11/11\text{ above threshold}.
\]

Safe theorem form:

\[
\boxed{
Q_{\rm R2Q}\le\frac34
\Rightarrow
\text{harmless / repaid / finite-certified / non-surviving}.
}
\]

Equivalently:

\[
\boxed{
\text{surviving first-crossing obstruction}
\Rightarrow
Q_{\rm R2Q}>\frac34.
}
\]

---

### Input C — EndpointSign UpperLowerSplit

Endpoint sign audit classification:

\[
\boxed{
\texttt{upper\_lower\_split}.
}
\]

Raw endpoint sign:

\[
E_\theta\text{ is raw}.
\]

Orientation variable:

\[
\texttt{local\_theta\_sign}.
\]

Upper crossings:

\[
1320,
\qquad
\text{upper nonpositive }E_\theta=0.
\]

Lower crossings:

\[
148,
\qquad
\text{lower nonnegative }E_\theta=0.
\]

Lower surviving unrepaid rows:

\[
0.
\]

Lower O2/B3 safety:

\[
\texttt{True}.
\]

Thus:

\[
\boxed{
\text{upper}\Rightarrow E_\theta>0,
}
\]

\[
\boxed{
\text{lower}\Rightarrow E_\theta<0.
}
\]

---

### Input D — v5 Local Obstruction Stack

The v5 local stack provides:

#### Positive harmlessness

\[
E_\theta>0
\Rightarrow
Q_{\rm R2Q}\le0.305<0.75.
\]

#### Direct threshold sign

\[
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta<0.
\]

#### O2 repayment

\[
E_\theta<0,\quad Q_{\rm R2Q}\le0.75
\Rightarrow
\text{O2-safe}.
\]

#### B3 no-accumulation

\[
\text{accumulation-risk}
\Rightarrow
\text{B3-safe}.
\]

#### NeutralClause

\[
\mathcal N=\varnothing.
\]

---

## 3. Conditional GlobalBridge Closure Statement

### Theorem Conditional GlobalBridge Closure

Assume:

1. a global RH-scale envelope is fixed for:
   \[
   G(x)=\psi(x)-x
   \]
   or:
   \[
   G(x)=\pi(x)-\operatorname{Li}(x);
   \]

2. if the envelope fails, there is a first crossing \(X_0\);

3. post-\(P_0\) continuous all-\(x\) / FullFCL candidate selection holds:
   \[
   X_0\Rightarrow J_0\in\mathcal C_{\rm FullFCL/theta};
   \]

4. finite-zone crossings are certificate-covered;

5. the v5 local stack holds.

Then no surviving first-crossing obstruction exists.

Therefore the RH-scale envelope holds conditionally.

---

## 4. Proof Skeleton

Assume for contradiction that the RH-scale envelope fails.

Then a first crossing \(X_0\) exists.

By conditional CoveringLocalization:

\[
X_0\Rightarrow J_0
\]

for some audited FullFCL/theta candidate row \(J_0\).

By ThresholdRelevance in contrapositive/certificate form:

\[
\text{if }Q_{\rm R2Q}(J_0)\le\frac34,
\]

then \(J_0\) is harmless / repaid / finite-certified / non-surviving.

Thus any surviving first-crossing obstruction must have:

\[
Q_{\rm R2Q}(J_0)>\frac34.
\]

Now split by endpoint sign.

---

### Upper branch

If \(J_0\) is upper, then:

\[
E_\theta(J_0)>0.
\]

By v5 positive harmlessness:

\[
Q_{\rm R2Q}(J_0)\le0.305<0.75.
\]

Therefore \(J_0\) cannot be a surviving threshold-relevant obstruction.

Contradiction.

---

### Lower branch

If \(J_0\) is lower, then:

\[
E_\theta(J_0)<0.
\]

The lower branch audit gives:

\[
\text{lower surviving unrepaid rows}=0.
\]

And all lower rows are O2/B3/finite/non-surviving safe.

Therefore \(J_0\) cannot be a surviving lower first-crossing obstruction.

Contradiction.

---

### Neutral branch

The neutral class is empty:

\[
\mathcal N=\varnothing.
\]

So no neutral first-crossing obstruction exists.

---

Therefore no first crossing exists.

Hence the selected RH-scale envelope holds, conditionally on the continuous all-\(x\) / FullFCL candidate-selection theorem.

---

## 5. RH-Scale Conclusion

Once the selected envelope is identified, the conclusion is either:

\[
\boxed{
\psi(x)-x=O(\sqrt{x}\log^2x)
}
\]

or:

\[
\boxed{
\pi(x)-\operatorname{Li}(x)=O(\sqrt{x}\log x).
}
\]

By the von Koch criterion, either RH-scale bound implies RH.

However, in this document the conclusion remains conditional on the continuous candidate-selection theorem.

---

## 6. What Is Now Closed

The following pieces are closed in audited/certificate or conditional-certificate form:

| Layer | Status |
|---|---|
| H-Exc | closed sampled-grid/certificate |
| Endpoint direct threshold sign | closed |
| Positive harmlessness | closed |
| O2 repayment | closed numeric/certificate |
| B3 no-accumulation | closed row-level numeric |
| NeutralClause | closed by emptiness |
| Endpoint sign orientation | closed by upper/lower split |
| Covering candidate universe | 1469/1469 covered |
| ThresholdRelevance candidate universe | 10140 rows, 0 failures |
| Dangerous/forbidden threshold support | dangerous 24/24, forbidden 11/11 above threshold |

---

## 7. What Remains Open

The remaining open theorem is:

\[
\boxed{
\text{post-}P_0\text{ continuous all-}x\text{ / FullFCL candidate-selection theorem}.
}
\]

Expanded:

\[
\boxed{
\text{every possible continuous RH-scale first crossing after }P_0
\text{ enters the audited FullFCL/theta candidate universe}.
}
\]

This is stronger than audited candidate coverage.

The audit already shows:

\[
1469/1469
\]

candidate coverage.

But it does not yet prove that the candidate universe captures every possible continuous all-\(x\) first crossing.

---

## 8. v5 Compatibility

This conditional assembly is v5-compatible.

It uses:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta<0.
\]

It does **not** use:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
Q_{\Delta D}>0.75.
\]

It preserves:

1. H-Exc sampled-grid caveat;
2. B3 row-level caveat;
3. finite certificates;
4. raw \(E_\theta\) plus `local_theta_sign`;
5. empty NeutralClause;
6. lower branch O2/B3 safety.

---

## 9. Paper-Safe Wording

Use:

> Conditional on the post-\(P_0\) continuous all-\(x\) / FullFCL candidate-selection theorem, the v5 GlobalBridge has no surviving first-crossing obstruction. Covering passes for 1469/1469 audited candidates, ThresholdRelevance has 0 failures across 10,140 rows, upper crossings are subthreshold, lower crossings are O2/B3/finite safe, and neutral rows are empty.

Avoid:

> The global bridge is unconditional.

Avoid:

> Continuous all-\(x\) covering is proven.

Avoid:

> RH is proven.

Avoid:

> The proof uses \(Q_{\Delta D}>0.75\).

Avoid:

> H-Exc full-grid control is available.

---

## 10. Recommended Next File

The remaining proof attack should now focus directly on the one remaining continuous-selection theorem:

```text
Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Proof_Attack_v1.md
```

Purpose:

\[
\boxed{
\text{attack the theorem that every post-}P_0\text{ continuous all-}x\text{ first crossing enters the audited FullFCL/theta candidate universe.}
}
\]

Alternative if drafting paper:

```text
Prime_Mesh_R2Q_Final_Conditional_RH_Paper_Draft_v1.md
```

---

## 11. Honest Status

The conditional GlobalBridge is assembled.

The only major remaining analytic gap is continuous all-\(x\) / FullFCL candidate selection after \(P_0\).

Until that is proven, the RH conclusion remains conditional.

---

*Prime Mesh Theory — RH Programme*
