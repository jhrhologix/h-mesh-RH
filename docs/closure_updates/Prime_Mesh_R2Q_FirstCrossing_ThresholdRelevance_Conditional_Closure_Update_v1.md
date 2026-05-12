# Prime Mesh R2Q — FirstCrossing ThresholdRelevance Conditional Closure Update v1

**Document:** `Prime_Mesh_R2Q_FirstCrossing_ThresholdRelevance_Conditional_Closure_Update_v1.md`  
**Project:** Prime Mesh Theory — RH Programme  
**Date:** 2026-05-11  
**Status:** Conditional/certificate closure update for ThresholdRelevance  
**Purpose:** Integrate the ThresholdRelevance audit result into the GlobalBridge stack.

---

## 1. Executive Verdict

The ThresholdRelevance audit passes in the safe conditional/certificate form.

The classification is:

\[
\boxed{\texttt{fullfcl\_backed\_certificate\_conditional}.}
\]

The safe theorem form is the contrapositive:

\[
\boxed{
Q_{\rm R2Q}\le\frac34
\Rightarrow
\text{harmless / repaid / finite-certified / non-surviving}.
}
\]

Therefore:

\[
\boxed{
\text{any surviving first-crossing obstruction must satisfy }
Q_{\rm R2Q}>\frac34.
}
\]

This closes ThresholdRelevance for the audited FullFCL/candidate universe.

It remains conditional because it is not yet a standalone symbolic all-\(x\) theorem. It still depends on FullFCL / Covering candidate-selection assumptions.

---

## 2. Audit Anchor

The ThresholdRelevance audit reports:

\[
\text{rows checked}=10140.
\]

\[
\text{threshold relevance failures}=0.
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

Dangerous rows above threshold:

\[
24/24.
\]

Forbidden rows above threshold:

\[
11/11.
\]

Failed delta-threshold route used:

\[
\texttt{False}.
\]

Direct threshold sign found:

\[
\texttt{True}.
\]

---

## 3. Correct Theorem Form

The safest theorem form is not initially:

\[
\text{every candidate row has }Q_{\rm R2Q}>0.75.
\]

That is false, since:

\[
10115
\]

rows are subthreshold.

The correct closure is:

\[
\boxed{
Q_{\rm R2Q}\le0.75
\Rightarrow
\text{non-obstructing}.
}
\]

Equivalently:

\[
\boxed{
\text{surviving first-crossing obstruction}
\Rightarrow
Q_{\rm R2Q}>0.75.
}
\]

This matches the audit statement:

\[
\text{subthreshold unclassified rows}=0.
\]

Every subthreshold row is harmless, repaid, finite-certified, non-surviving, or otherwise not a first-crossing obstruction.

---

## 4. Dangerous and Forbidden Rows

The audit found:

\[
\text{dangerous rows}=24.
\]

All dangerous rows are above threshold:

\[
24/24.
\]

Forbidden rows:

\[
11.
\]

All forbidden rows are above threshold:

\[
11/11.
\]

Thus the dangerous/forbidden populations are exactly in the threshold-relevant sector.

This supports the statement:

\[
\boxed{
\text{dangerous/forbidden obstruction}
\Rightarrow
Q_{\rm R2Q}>0.75.
}
\]

---

## 5. Subthreshold Closure

Rows with:

\[
Q_{\rm R2Q}\le0.75
\]

are not ignored.

The audit checked:

\[
10115
\]

subthreshold rows.

Subthreshold unclassified rows:

\[
0.
\]

Therefore every subthreshold row is covered by one of the closure categories:

1. positive harmless;
2. O2-safe;
3. B3-safe;
4. finite-certified;
5. non-surviving;
6. not a first-crossing obstruction.

Thus:

\[
\boxed{
Q_{\rm R2Q}\le0.75
\Rightarrow
\text{not a surviving first-crossing obstruction}.
}
\]

---

## 6. v5 Compatibility

This closure is v5-compatible.

It uses direct threshold sign:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta<0.
\]

It does not use the failed implication:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
Q_{\Delta D}>0.75.
\]

That failed route must remain excluded because of `hexc_00040`.

The closure also fits the upper/lower split:

### Upper branch

\[
E_\theta>0
\Rightarrow
Q_{\rm R2Q}\le0.305<0.75.
\]

So upper rows are subthreshold and non-obstructing.

### Lower branch

\[
E_\theta<0.
\]

Lower rows are handled by O2/B3/finite/non-surviving safety.

---

## 7. Conditional Dependence

This closure is not standalone symbolic all-\(x\).

It depends on:

### FullFCL / candidate selection

The row universe audited is the FullFCL / first-crossing candidate universe.

### CoveringLocalization

The global first crossing must first be mapped into the audited/certified row universe.

The current CoveringLocalization status is:

\[
\texttt{conditional\_theta\_window\_plus\_finite\_continuous}.
\]

Thus the combined status is:

\[
\boxed{
\text{ThresholdRelevance is closed for the audited/candidate universe, conditional on FullFCL/Covering selection.}
}
\]

---

## 8. Closure Statement

### Conditional ThresholdRelevance Closure

Within the FullFCL / audited first-crossing candidate universe:

\[
\boxed{
Q_{\rm R2Q}\le\frac34
\Rightarrow
\text{harmless / repaid / finite-certified / non-surviving / non-obstructing}.
}
\]

Therefore:

\[
\boxed{
\text{surviving first-crossing obstruction}
\Rightarrow
Q_{\rm R2Q}>\frac34.
}
\]

The audit confirms this with:

\[
10140
\]

rows checked and:

\[
0
\]

threshold relevance failures.

---

## 9. Integration With Conditional GlobalBridge

The GlobalBridge chain now has both main conditional inputs in audited/certificate form.

### CoveringLocalization

\[
\text{candidate coverage}=1469/1469,
\]

but continuous post-\(P_0\) all-\(x\) window selection remains conditional.

### ThresholdRelevance

\[
\text{rows checked}=10140,\quad
\text{failures}=0,
\]

but the theorem remains FullFCL/candidate-selection conditional.

### EndpointSign

Resolved by upper/lower split.

### v5 Local Stack

Closed in audited/certificate form.

Together:

\[
\boxed{
\text{Assuming continuous window selection / FullFCL candidate selection, the v5 stack rules out surviving first-crossing obstructions.}
}
\]

---

## 10. What This Closure Does Not Claim

This closure does not claim a standalone symbolic all-\(x\) proof of ThresholdRelevance.

It does not claim every row has:

\[
Q_{\rm R2Q}>0.75.
\]

Most rows are subthreshold.

It does not claim RH is proven unconditionally.

It does not remove the CoveringLocalization conditionality.

It does not use the failed delta-threshold route.

---

## 11. Paper-Safe Wording

Use:

> ThresholdRelevance closes in contrapositive/certificate form: among 10,140 audited FullFCL/first-crossing candidate rows, there are zero threshold-relevance failures. All 10,115 subthreshold rows are classified harmless, repaid, finite-certified, non-surviving, or non-obstructing. Therefore any surviving first-crossing obstruction in the audited candidate universe must satisfy \(Q_{\rm R2Q}>3/4\).

Avoid:

> Every candidate has \(Q_{\rm R2Q}>3/4\).

Avoid:

> ThresholdRelevance is a standalone symbolic all-\(x\) theorem.

Avoid:

> The proof uses \(Q_{\Delta D}>0.75\).

---

## 12. Updated GlobalBridge Status

The GlobalBridge is now conditionally assembled as:

1. If RH-scale envelope fails, a first crossing exists.
2. Conditional CoveringLocalization maps it into the FullFCL/theta candidate universe.
3. ThresholdRelevance says any surviving obstruction must satisfy:
   \[
   Q_{\rm R2Q}>0.75.
   \]
4. EndpointSign splits:
   - upper: \(E_\theta>0\), hence subthreshold;
   - lower: \(E_\theta<0\), hence O2/B3/finite safe.
5. v5 local stack rules out surviving first-crossing obstruction.
6. Therefore the RH-scale envelope holds, conditional on covering/candidate-selection.
7. By von Koch, RH follows conditionally.

---

## 13. Remaining Open Item

The main remaining analytic bridge is now concentrated in one place:

\[
\boxed{
\text{post-}P_0\text{ continuous all-}x\text{ / FullFCL candidate-selection theorem}.
}
\]

In other words:

\[
\boxed{
\text{every possible global RH-scale first crossing belongs to the audited FullFCL/theta candidate universe}.
}
\]

Once this is proven symbolically, the conditional GlobalBridge becomes much stronger.

---

## 14. Recommended Next File

```text
Prime_Mesh_R2Q_GlobalBridge_ConditionalAssembly_Closure_Update_v1.md
```

Purpose:

\[
\boxed{
\text{combine CoveringLocalization conditional closure + ThresholdRelevance conditional closure + UpperLowerSplit + v5 stack into one final conditional GlobalBridge closure.}
}
\]

After that, the remaining proof attack is:

```text
Prime_Mesh_R2Q_PostP0_ContinuousWindowSelection_Proof_Attack_v1.md
```

---

## 15. Honest Status

ThresholdRelevance is closed in FullFCL-backed, certificate/candidate-set conditional form.

It is not yet a standalone symbolic continuous all-\(x\) theorem.

No threshold relevance failures were found.

No subthreshold unclassified rows remain.

---

*Prime Mesh Theory — RH Programme*
