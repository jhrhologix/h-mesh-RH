# Prime Mesh R2Q — O1 Gap C Shell Normalization Result

**Document:** `Prime_Mesh_R2Q_O1_GapC_Shell_Normalization_Result_v1.md`  
**Project:** Prime Mesh Theory — RH Programme  
**Date:** 2026-05-07  
**Status:** Gap C result/closure update after shell-normalization repair  
**Purpose:** Resolve the role of the \(1/12\), \(1/72\), \(2g(3)=1/3\), and residual-density laws in the O1 shell-ratio target.

---

## 1. Executive Verdict

O1 Gap C should now be treated as **partially upgraded but not fully closed**.

The exact identities are clean:

\[
d_3=\frac12,
\qquad
g(3)=\frac16,
\]

so:

\[
d_3g(3)=\frac1{12},
\]

and:

\[
d_3g(3)^2=\frac1{72}.
\]

But the O1 shell-ratio target is not the isolated identity:

\[
d_3g(3)=\frac1{12}.
\]

The actual O1 target is:

\[
\boxed{
R_3/R_2\to\frac13
}
\]

or equivalently:

\[
\boxed{
M_3/M_2\to\frac19.
}
\]

The correct leading shell-amplitude anchor appears to be:

\[
\boxed{
2g(3)=2\cdot\frac16=\frac13.
}
\]

Therefore the current best status is:

\[
\boxed{
\text{Gap C is reduced to proving that the O1 shell normalization converts the exact }3\text{-bearing branch }2g(3)=1/3
\text{ into }R_3/R_2=1/3+o(1),
}
\]

with residual non-\(3\) branch effects either cancelling, being absorbed into the shell-2 anchor, or contributing only the observed small deviation.

---

## 2. What Is Now Exact

### 2.1 The \(3\)-bearing branch

For the shifted-prime shell geometry, the \(q=3\) branch has density:

\[
d_3=\frac12.
\]

With:

\[
g(q)=\frac1{q(q-1)},
\]

we get:

\[
g(3)=\frac1{3\cdot2}=\frac16.
\]

Hence:

\[
d_3g(3)=\frac12\cdot\frac16=\frac1{12}.
\]

This is exact.

### 2.2 The bare second moment

The corresponding bare second-moment leading term is:

\[
d_3g(3)^2
=
\frac12\cdot\frac1{36}
=
\frac1{72}.
\]

This is also exact.

### 2.3 The shell-amplitude anchor

The natural shell-amplitude anchor is:

\[
2g(3)=\frac13.
\]

This is exact and directly matches the O1 RMS target:

\[
R_3/R_2\approx\frac13.
\]

This is the key clarification.

---

## 3. What the Earlier \(1/12\) Meant

The identity:

\[
d_3g(3)=\frac1{12}
\]

is a **weighted first-moment contribution** of the \(3\)-bearing branch.

It is useful, but it is not by itself the final O1 shell law.

The final shell law is about a normalized shell-amplitude ratio:

\[
R_3/R_2,
\]

or a normalized second-moment ratio:

\[
M_3/M_2.
\]

Therefore the earlier phrase:

\[
\mathbb E[g(2,\operatorname{spf})^2]\approx\frac1{12}
\]

should not be used unless the code/definition uses a normalized \(g\)-function or a shell-normalized quantity.

The safer language is:

\[
\boxed{
\text{The }1/12\text{ identity identifies the leading weighted }3\text{-bearing SPF contribution, while }2g(3)=1/3\text{ is the shell-amplitude anchor.}
}
\]

---

## 4. Residual Non-\(3\) Branch

The H-Cov23 support work identified the residual non-\(3\) marginal density:

\[
\widetilde d_q=2d_q^{\rm O1},
\qquad q\ge5.
\]

This residual branch lives after peeling off the exact \(3\)-bearing component.

Define:

\[
\delta
=
\sum_{q\ge5}\widetilde d_qg(q).
\]

The H-Cov23 support note gives:

\[
\delta\approx0.016655.
\]

This residual branch is small but not zero.

Therefore a proof of:

\[
R_3/R_2\to\frac13
\]

must explain why the residual branch:

1. cancels between left/right shell contributions;
2. is absorbed by the shell-2 normalization;
3. enters with negative correction matching the observed deviation;
4. or is lower order under the actual O1 aggregation.

---

## 5. Observed Ratio and Residual Correction

The observed LongA/O1 shell result was:

\[
R_3/R_2\approx0.331134.
\]

The exact anchor is:

\[
\frac13=0.3333333333\ldots.
\]

The deviation is:

\[
0.331134-\frac13
\approx
-0.002199.
\]

At the second-moment level:

\[
M_3/M_2\approx0.1096497,
\]

while:

\[
\frac19=0.1111111111\ldots.
\]

The deviation is:

\[
0.1096497-\frac19
\approx
-0.0014614.
\]

So the residual correction is small and negative.

This supports the interpretation:

\[
\boxed{
\text{the exact }3\text{-bearing anchor gives the main }1/3\text{ law, and the non-}3\text{ residual branch causes a small downward correction.}
}
\]

---

## 6. Repaired Gap C Result Statement

### Result — O1 Gap C Shell Normalization

The O1 shell-3 normalization target is:

\[
\boxed{
R_3/R_2
=
\frac13+\varepsilon_3
}
\]

with observed:

\[
\varepsilon_3\approx-0.002199.
\]

Equivalently:

\[
\boxed{
M_3/M_2
=
\frac19+\varepsilon_3^{(2)}
}
\]

with observed:

\[
\varepsilon_3^{(2)}\approx-0.0014614.
\]

The leading term is exact:

\[
\boxed{
2g(3)=\frac13.
}
\]

The remaining proof obligation is:

\[
\boxed{
\text{bound the non-}3\text{ residual correction within the O1 sign-margin budget.}
}
\]

---

## 7. Proof Target Version

For theorem-facing use, state Gap C as:

### Lemma Gap C — Shell-3 Normalization with Residual Error

Let \(R_2,R_3\) be the LongA shell RMS amplitudes in the O1 B2-active geometry. Then:

\[
\boxed{
\frac{R_3}{R_2}
=
\frac13
+
O(\varepsilon_{\rm res})
}
\]

where:

\[
\varepsilon_{\rm res}
\]

is the normalized contribution of the non-\(3\) residual branch:

\[
q\ge5.
\]

Moreover, the empirical audit gives:

\[
|\varepsilon_{\rm res}|\approx0.002199.
\]

A proof-grade target may allow a larger bound, provided it remains inside the O1 sign-margin budget.

At the second-moment level:

\[
\boxed{
\frac{M_3}{M_2}
=
\frac19
+
O(\varepsilon_{\rm res}).
}
\]

---

## 8. O1 Sign-Margin Relevance

The O1 sign margin was:

\[
\delta_{\rm sign}\approx0.148198888171.
\]

The observed shell-3 amplitude deviation:

\[
|\varepsilon_3|\approx0.002199
\]

is tiny relative to this margin.

Therefore, for the O1 sign theorem, it may not be necessary to prove exact convergence to:

\[
1/3.
\]

It may be enough to prove:

\[
\boxed{
\left|R_3/R_2-\frac13\right|
\le
\varepsilon_{\rm allowed}
}
\]

where:

\[
\varepsilon_{\rm allowed}\ll\delta_{\rm sign}.
\]

This is much easier than proving a sharp asymptotic.

---

## 9. What Is Closed vs Still Open

### Closed / exact

\[
d_3=\frac12.
\]

\[
g(3)=\frac16.
\]

\[
d_3g(3)=\frac1{12}.
\]

\[
d_3g(3)^2=\frac1{72}.
\]

\[
2g(3)=\frac13.
\]

### Formula-grade / strong support

\[
\widetilde d_q=2d_q^{\rm O1},
\qquad q\ge5.
\]

\[
\delta\approx0.016655.
\]

Observed:

\[
R_3/R_2\approx0.331134.
\]

Observed:

\[
M_3/M_2\approx0.1096497.
\]

### Still open

The exact normalization proof:

\[
R_3/R_2
=
2g(3)+\text{controlled residual}.
\]

The residual cancellation/absorption bound:

\[
|\text{residual correction}|
\le
\varepsilon_{\rm allowed}.
\]

---

## 10. Updated O1 Gap C Status

The old status was:

\[
\text{unclear }1/12\text{ identity}.
\]

The repaired status is:

\[
\boxed{
\text{Gap C is not fully closed, but it is sharply reduced.}
}
\]

More precisely:

\[
\boxed{
\text{the leading amplitude law is exact through }2g(3)=1/3,
}
\]

and:

\[
\boxed{
\text{the only remaining Gap C work is to bound the residual non-}3\text{ correction.}
}
\]

This is a substantial improvement.

---

## 11. Recommended Next Computation

If Codex is available, run a focused Gap C normalization audit.

Suggested file:

```text
notes/prime_mesh_r2q_o1_gapc_shell_normalization_audit.py
```

Required outputs:

```text
R2
R3
R3_over_R2
M2
M3
M3_over_M2
anchor_2g3
R3_minus_anchor
M3_minus_anchor2
residual_non3_mean
residual_non3_signed_contribution
residual_non3_abs_contribution
residual_left
residual_right
residual_cross
shell2_anchor_terms
shell3_anchor_terms
normalization_formula_detected
```

The key question is:

\[
\boxed{
\text{Is the observed }-0.002199\text{ deviation explained by a signed residual correction that is uniformly small?}
}
\]

---

## 12. Recommended Next Document

After the audit, write:

```text
Prime_Mesh_R2Q_O1_GapC_Residual_Correction_Result_v1.md
```

Purpose:

\[
\boxed{
\text{prove or empirically freeze the residual non-}3\text{ correction bound.}
}
\]

---

## 13. Honest Status

O1 Gap C is now much clearer.

It should not be advertised as:

\[
\text{closed by }1/12.
\]

It should be advertised as:

\[
\boxed{
\text{leading shell-amplitude anchor closed by }2g(3)=1/3,
\text{ residual correction still to bound.}
}
\]

This is the correct proof-facing position.

---

*Prime Mesh Theory — RH Programme*
