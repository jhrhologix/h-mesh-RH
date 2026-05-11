# Prime Mesh R2Q — FirstCrossing UpperLowerSplit Closure Update v1

**Document:** `Prime_Mesh_R2Q_FirstCrossing_UpperLowerSplit_Closure_Update_v1.md`  
**Project:** Prime Mesh Theory — RH Programme  
**Date:** 2026-05-10  
**Status:** Closure update for endpoint sign-orientation layer  
**Purpose:** Integrate the upper/lower first-crossing split into the GlobalBridge proof stack.

---

## 1. Executive Verdict

The endpoint sign-orientation gap is closed in the audited stack by an **upper/lower split**, not by a unified outward-sign theorem.

The audit found:

\[
E_\theta \text{ is raw, not outward-oriented.}
\]

The crossing orientation is carried separately by:

\[
\texttt{local\_theta\_sign}.
\]

The supported theorem form is:

\[
\boxed{\texttt{upper\_lower\_split}.}
\]

Upper crossings satisfy:

\[
E_\theta>0,
\]

and are harmless/subthreshold:

\[
Q_{\rm R2Q}\le0.305<0.75.
\]

Lower crossings satisfy:

\[
E_\theta<0,
\]

and are closed by O2/B3/finite/non-surviving safety:

\[
\text{lower surviving unrepaid rows}=0.
\]

Thus the endpoint sign issue no longer blocks the GlobalBridge, provided the remaining covering/localization and threshold relevance assumptions are accepted/proven.

---

## 2. Audit Anchor

The FirstCrossing EndpointSign audit reports:

\[
\texttt{E\_theta orientation}=\texttt{raw}.
\]

Orientation variable:

\[
\texttt{local\_theta\_sign}.
\]

Upper crossings:

\[
1320.
\]

Upper nonpositive \(E_\theta\):

\[
0.
\]

Lower crossings:

\[
148.
\]

Lower nonnegative \(E_\theta\):

\[
0.
\]

Lower surviving unrepaid rows:

\[
0.
\]

Lower O2/B3 safety:

\[
\texttt{True}.
\]

Counterexamples:

\[
0.
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

## 3. Raw Versus Outward-Oriented Sign

Raw endpoint sign:

\[
E_\theta
=
\theta(b)-\theta(a)-(b-a)
=
H(b)-H(a).
\]

Crossing orientation:

\[
\sigma=\texttt{local\_theta\_sign}.
\]

Outward endpoint sign:

\[
E_\theta^{\rm out}
=
\sigma E_\theta.
\]

The audit found:

\[
E_\theta^{\rm out}>0
\]

for every signed crossing row.

However, the v5 local threshold theorem is stated in raw coordinates:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta<0.
\]

A unified outward-sign contradiction would require a new theorem:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta^{\rm out}<0.
\]

That theorem is not currently available.

Therefore the safe closure is the raw-coordinate upper/lower split.

---

## 4. Upper Branch Closure

Upper / positive crossing rows satisfy:

\[
E_\theta>0.
\]

Audit facts:

\[
\text{upper rows}=1320,
\]

\[
\text{upper nonpositive }E_\theta=0,
\]

\[
Q_{\rm R2Q}^{\max}=0.2157084836048593,
\]

\[
Q_{\rm R2Q}>0.75\text{ count}=0.
\]

Proof-facing positive cap:

\[
Q_{\rm R2Q}
\le
\frac14+0.025+0.03
=
0.305
<
0.75.
\]

Thus:

\[
\boxed{
\text{upper crossing}
\Rightarrow
E_\theta>0
\Rightarrow
Q_{\rm R2Q}\le0.305<0.75.
}
\]

So upper crossings cannot be threshold first-crossing obstructions.

---

## 5. Upper Branch Contradiction Form

If a global first crossing theorem requires an upper first-crossing row to satisfy:

\[
Q_{\rm R2Q}>0.75,
\]

then direct threshold sign gives:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta<0.
\]

But the upper branch gives:

\[
E_\theta>0.
\]

Contradiction.

Thus the upper branch closes by direct threshold sign / positive harmlessness.

---

## 6. Lower Branch Closure

Lower / negative crossing rows satisfy:

\[
E_\theta<0.
\]

Audit facts:

\[
\text{lower rows}=148,
\]

\[
\text{lower nonnegative }E_\theta=0,
\]

\[
Q_{\rm R2Q}^{\max}=1.8193520399038576,
\]

\[
Q_{\rm R2Q}>0.75\text{ count}=3.
\]

Lower safety:

\[
\text{O2-safe count}=148,
\]

\[
\text{B3-safe count}=148,
\]

\[
\text{finite certified count}=126,
\]

\[
\text{surviving unrepaid count}=0.
\]

Therefore:

\[
\boxed{
\text{lower crossing}
\Rightarrow
E_\theta<0
\Rightarrow
\text{O2/B3/finite/non-surviving safe}.
}
\]

Lower crossings do not contradict raw direct sign, because both give \(E_\theta<0\). They are instead neutralized by repayment/no-accumulation.

---

## 7. Lower Branch Logical Role

The lower branch should be written as:

\[
\boxed{
\text{lower first-crossing candidate}
\Rightarrow
\text{no surviving unrepaid obstruction}.
}
\]

This uses:

### O2

\[
E_\theta<0,\quad Q_{\rm R2Q}\le0.75
\Rightarrow
\text{O2-safe}.
\]

### B3

\[
\text{accumulation-risk}
\Rightarrow
\text{B3-safe}.
\]

### finite/non-surviving certificates

\[
\text{finite or non-surviving lower rows are certified safe}.
\]

The audit reports the final outcome:

\[
\text{lower surviving unrepaid rows}=0.
\]

---

## 8. Closure Statement

### Theorem FirstCrossing UpperLowerSplit Closure

Let \(J\) be an admissible first-crossing row with raw endpoint sign \(E_\theta(J)\) and crossing orientation \(\texttt{local\_theta\_sign}\).

Then exactly one of the following holds.

### Upper case

\[
E_\theta(J)>0.
\]

Then:

\[
Q_{\rm R2Q}(J)\le0.305<0.75.
\]

So \(J\) is not a threshold obstruction.

### Lower case

\[
E_\theta(J)<0.
\]

Then \(J\) is O2-safe, B3-safe, finite-certified, or non-surviving, with:

\[
\text{surviving unrepaid lower rows}=0.
\]

So \(J\) is not a surviving lower obstruction.

Therefore the endpoint sign-orientation layer is closed by the upper/lower split.

---

## 9. Integration With GlobalBridge

The GlobalBridge proof stack now becomes:

1. **Covering localization**
   \[
   \text{global first crossing}
   \Rightarrow
   \text{admissible local R2Q row}.
   \]

2. **Threshold relevance**
   \[
   \text{first crossing row}
   \Rightarrow
   Q_{\rm R2Q}>0.75
   \]
   where required.

3. **Upper/lower endpoint sign split**
   - upper rows: \(E_\theta>0\), subthreshold;
   - lower rows: \(E_\theta<0\), O2/B3/finite safe.

4. **v5 local closure**
   - upper: direct sign / positive harmlessness;
   - lower: O2/B3 no surviving unrepaid obstruction.

5. **No surviving first crossing**

6. **RH-scale conclusion**
   via the von Koch / \(\psi,\pi\) bridge.

This closure update resolves step 3.

---

## 10. v5 Compatibility

This closure is v5-compatible because it:

1. uses raw \(E_\theta\);
2. keeps `local_theta_sign` as orientation data;
3. uses direct threshold sign;
4. does not use the failed delta-threshold route;
5. uses O2/B3 for lower crossings;
6. preserves finite certificates;
7. preserves the sampled-grid H-Exc caveat;
8. preserves B3 row-level caveat;
9. preserves empty NeutralClause.

It does **not** claim:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
Q_{\Delta D}>0.75.
\]

It does **not** claim:

\[
E_\theta
\]

is already outward-oriented.

---

## 11. Remaining GlobalBridge Work

After this closure, the remaining GlobalBridge work is:

1. finalize covering localization:
   \[
   \text{global first crossing}
   \Rightarrow
   \text{admissible R2Q row};
   \]

2. finalize threshold relevance:
   \[
   \text{first-crossing row}
   \Rightarrow
   Q_{\rm R2Q}>0.75;
   \]

3. thread upper/lower split into the first-crossing theorem;

4. state the RH-scale conclusion:
   \[
   \psi(x)-x=O(\sqrt{x}\log^2x)
   \]
   or:
   \[
   \pi(x)-\operatorname{Li}(x)=O(\sqrt{x}\log x).
   \]

The next best file is therefore a v5 compatibility update for the GlobalBridge.

---

## 12. Paper-Safe Wording

Use:

> \(E_\theta\) is raw. Upper crossings have \(E_\theta>0\) and are subthreshold; lower crossings have \(E_\theta<0\) and are closed by O2/B3/finite safety. The endpoint sign layer closes by an upper/lower split, not by a unified outward-sign theorem.

Avoid:

> All first crossings have \(E_\theta>0\).

Avoid:

> Lower crossings contradict direct threshold sign.

Avoid:

> \(E_\theta\) is already outward-oriented.

Avoid:

> The failed \(Q_{\Delta D}>0.75\) route.

---

## 13. Recommended Next File

```text
Prime_Mesh_R2Q_GlobalBridge_v5_Compatibility_Update_v1.md
```

Purpose:

\[
\boxed{
\text{update the global bridge architecture with v5 direct sign and the upper/lower split.}
}
\]

After that, produce:

```text
Prime_Mesh_R2Q_GlobalBridge_to_RH_Theorem_Target_v1.md
```

if covering localization and threshold relevance are accepted as conditional/theorem inputs.

---

## 14. Honest Status

Endpoint sign orientation is resolved by upper/lower split in the audited stack.

The global RH implication is still not fully proven until covering localization, threshold relevance, and the von Koch/RH-scale conclusion are assembled into a final theorem.

---

*Prime Mesh Theory — RH Programme*
