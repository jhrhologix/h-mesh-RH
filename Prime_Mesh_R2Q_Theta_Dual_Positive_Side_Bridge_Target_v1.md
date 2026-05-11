# Prime Mesh R2Q - Theta Dual Positive-Side Bridge Target

**Document:** `Prime_Mesh_R2Q_Theta_Dual_Positive_Side_Bridge_Target_v1.md`  
**Project:** Prime Mesh Theory - RH Programme  
**Date:** 2026-05-06  
**Status:** proof-target note after theta comparison audit  
**Purpose:** isolate the missing positive-side bridge for two-sided Chebyshev control

---

## 1. Purpose

The theta comparison audit tested whether the current R2Q forbidden-crossing mechanism detects both signs of

\[
E_\theta(x)=\theta(x)-x.
\]

It does not yet do so.

The current R2Q crossing inventory detects the negative Chebyshev side:

\[
\theta(x)-x<0.
\]

The remaining bridge target is therefore:

\[
\boxed{
\text{find the reflected / dual R2Q mechanism controlling } \theta(x)-x>0.
}
\]

---

## 2. Audit Result

The audit computed cumulative Chebyshev error at all R2Q interval endpoints using an independent segmented sieve.

Endpoint convention self-check:

\[
\texttt{prime\_log\_sum\_check\_abs\_max}
=2.387474523857236\times10^{-6}.
\]

Thus the local identity

\[
\sum_{y<p\le y+h}\log p
=
\theta(y+h)-\theta(y)
\]

holds to floating precision.  The sign result is not caused by a half-open interval convention error.

The endpoint signs were:

\[
\texttt{theta\_endpoint\_positive\_rows}=0,
\qquad
\texttt{theta\_endpoint\_negative\_rows}=1468.
\]

The local interval signs were:

\[
\texttt{theta\_local\_positive\_rows}=1320,
\qquad
\texttt{theta\_local\_negative\_rows}=148.
\]

Near-forbidden rows:

\[
\texttt{near\_forbidden\_theta\_local\_positive\_rows}=0,
\qquad
\texttt{near\_forbidden\_theta\_local\_negative\_rows}=3.
\]

Therefore:

\[
\boxed{
\text{current R2Q near-forbidden crossings detect negative local theta deficit, not the positive side.}
}
\]

---

## 3. What Current R2Q Controls

The B2 / MR-2 coordinate is deficit-facing:

\[
d_{\rm B2}(y)
=
\left(
\frac{-D_N(y)}{\sqrt{p^*}}-\eta_0
\right)_+.
\]

This is naturally sensitive to an unrepaid prime shock / negative recovery excursion.

In theta language, the corresponding local obstruction is:

\[
E_\theta(J)
=
\sum_{y<p\le y+h}\log p-h<0.
\]

The audit confirms that the near-forbidden rows are exactly on this negative local side.

---

## 4. Missing Positive-Side Object

A positive Chebyshev excess is:

\[
E_\theta(J)>0,
\]

meaning the interval contains more prime log mass than its length.

This is not a deficit of prime mass.  It is a prime-density excess.

The reflected R2Q object should therefore be an excess-facing coordinate, for example:

\[
d_{\rm B2}^{+}(y)
=
\left(
\frac{D_N(y)}{\sqrt{p^*}}-\eta_0^+
\right)_+,
\]

or, more locally,

\[
Q_{\rm R2Q}^{+}(J)
=
\frac{
\left[
P(J)-R(J)-\operatorname{Drift}^{+}(J)
\right]_+
}{
\sqrt{|J|}\log^2p^*
}.
\]

The exact sign convention must be chosen so that:

\[
Q_{\rm R2Q}^{+}(J)
\quad\text{detects}\quad
\theta(J)-|J|>0.
\]

---

## 5. Candidate Dual Mechanisms

### Candidate A - Sign-reflected bridge walk

Use the same bridge identity but reverse the excursion coordinate:

\[
D_N^+(x)=-D_N(x).
\]

Then repeat the B1/B2/B3 structure for positive excursions of \(D_N\).

The proof question is whether the same local shell response exists with reversed orientation:

\[
a^{\rm B2,+}
\sim
-a^{\rm B2}
\quad\text{or}\quad
\text{a related K4-family stencil}.
\]

### Candidate B - Prime-excess renewal blocks

Define renewal blocks around positive local theta excess:

\[
E_\theta(J)>0.
\]

Then ask whether composite mesh response over nearby intervals repays the excess in the reflected direction.

The corresponding local theorem would be:

\[
Q_{\rm MR2}^{+}(J)\le1.
\]

### Candidate C - Pairing positive excess to later negative recovery

Positive theta excess may not create a same-window R2Q forbidden crossing.  It may be paired to a later negative recovery block.

The theorem target would be a transport/compensation statement:

\[
E_\theta^+(J)
\le
\sum_{J'\in\mathcal R(J)}
E_\theta^-(J')
+
O(\sqrt{|J|}\log^2p^*).
\]

This would show that positive excess is absorbed by the same negative-deficit machinery after a delay.

---

## 6. Required Positive-Side Lemma

The final two-sided theta bridge needs one of the following:

\[
\boxed{
\text{Dual R2Q Tail Closure: }
Q_{\rm R2Q}^{+}(J)\le1.
}
\]

or:

\[
\boxed{
\text{Positive-to-negative transport: }
E_\theta^+(J)
\text{ is absorbed by controlled negative recovery blocks.}
}
\]

or:

\[
\boxed{
\text{Independent upper Chebyshev side: }
\theta(x)-x
\le
C\sqrt{x}\log^2x.
}
\]

The first two are internal H-Mesh/R2Q routes.  The third risks importing a classical RH-equivalent estimate if not proved by mesh arithmetic.

---

## 7. Next Audit

Create:

```text
notes/prime_mesh_r2q_theta_positive_side_candidate_audit.py
```

Purpose:

\[
\boxed{
\text{identify which reflected coordinate detects }E_\theta(J)>0.
}
\]

Tasks:

1. Select rows with local theta excess:

   \[
   E_\theta(J)>0.
   \]

2. Compare against candidate reflected coordinates:

   \[
   D_N(y),\quad
   D_N(y+h),\quad
   \Delta D_N(J),
   \quad
   -Q_{\rm MR2}(J),
   \quad
   R(J)-P(J).
   \]

3. Fit/test whether a positive-side local margin exists:

   \[
   Q_{\rm R2Q}^{+}(J)
   \le
   1.
   \]

4. Check whether the same K4-family response appears with reversed orientation.

Key output:

```text
positive_theta_rows
best_positive_side_coordinate
corr_positive_theta_with_coordinate
positive_side_Qmax
positive_side_pass_frac
positive_side_k4_orientation
```

---

## 8. Current Position

R2Q tail closure is strong on the negative Chebyshev side.  The final comparison bridge is not yet two-sided.

The next mathematical target is:

\[
\boxed{
\text{construct and verify the positive-side dual R2Q mechanism.}
}
\]

Once that dual mechanism is available, the bridge

\[
\text{R2Q tail closure}
\Rightarrow
|\theta(x)-x|
\le
C\sqrt{x}\log^2x
\]

becomes a realistic theorem target rather than a one-sided inference.

---

*Prime Mesh Theory - RH Programme*
