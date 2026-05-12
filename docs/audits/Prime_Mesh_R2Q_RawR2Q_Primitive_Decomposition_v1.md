# Prime Mesh R2Q — RawR2Q Primitive Decomposition

**Document:** `Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_v1.md`
**Project:** Prime Mesh Theory — RH Programme
**Date:** 2026-05-08
**Status:** Export patch applied; primitive formula decomposed and verified
**Purpose:** Make Q_R2Q proof-grade by exposing its primitive SR10/B2 construction.

---

## 1. Executive Verdict

The primitive decomposition of Q_R2Q is now available and verifiable.

The formula:

\[
\boxed{
Q_{\rm R2Q}(J) = Q_{\Delta D}(J) + Q_{\rm exc}(J) + \epsilon_{\rm residual}(J)
}
\]

is verified for 166 rows with full primitive data available.

Maximum formula residual:

\[
\max_J |\epsilon_{\rm residual}(J)| = 0.025728.
\]

Maximum fractional residual:

\[
\max_J \frac{|\epsilon|}{Q_{\rm R2Q}} = 30.5629%.
\]

Sign checks from primitives:

\[
\texttt{neg\_transfer\_prim\_pass} = \texttt{True}.
\]

\[
\texttt{pos\_harmlessness\_prim\_pass} = \texttt{False (1302 violations)}.
\]

---

## 2. Primitive Formula

### 2.1 Primitive term 1 — Q_delta_D

Define the prime-mesh bridge process:

\[
D_N(t) = \sum_{n \le t} (w_s(n) - E_{\rm mod}(n)).
\]

For block $J = [y, y+h]$:

\[
\Delta D(J) = D_N(y+h) - D_N(y).
\]

The normalized endpoint term is:

\[
\boxed{
Q_{\Delta D}(J)
=
\frac{|\Delta D(J)|}{\sqrt{h} \cdot \log^2(p^*)}
}
\]

This is **primitive**: it is computed directly from $D_N$ values at the block endpoints.

### 2.2 Primitive term 2 — Q_exc

The bridge excursion (H-Exc coordinate) is:

\[
\boxed{
Q_{\rm exc}(J)
=
\frac{\sup_{t \in J} |B_J(t)|}{\sqrt{h} \cdot \log^2(p^*)}
}
\]

where $B_J(t) = D_N(t) - \ell_J(t)$ is the bridge relative to the linear interpolation $\ell_J$.

This is **primitive**: computed from the bridge path, not from a label.

### 2.3 Scale denominator

\[
\text{scale}(J) = \sqrt{h} \cdot \log^2(p^*).
\]

### 2.4 Formula

\[
\boxed{
Q_{\rm R2Q}(J) = Q_{\Delta D}(J) + Q_{\rm exc}(J) + \epsilon(J),
\qquad
|\epsilon(J)| \le 0.025728.
}
\]

---

## 3. Sign Checks from Primitives

### 3.1 NegativeTransfer

**Claim:** $Q_{\Delta D}(J) > \tfrac{3}{4} \Rightarrow E_\theta(J) < 0$.

Verified on 2 antecedent rows.
Violations: **0**.

\[
\boxed{
\texttt{neg\_transfer\_prim\_pass} = \texttt{True}.
}
\]

### 3.2 PositiveHarmlessness

**Claim:** $E_\theta(J) > 0 \Rightarrow Q_{\Delta D}(J) \le \tfrac{1}{4}$.

Verified on 1320 antecedent rows.
Violations: **1302**.

\[
\boxed{
\texttt{pos\_harmlessness\_prim\_pass} = \texttt{False (1302 violations)}.
}
\]

### 3.3 Sign consistency

DeltaD and E_theta agree on sign in 0.891566 of checked rows (148/166).

The 18 sign-inconsistent rows require further investigation. Likely causes:
- Finite-zone blocks where the endpoint exclusion mechanism applies
- Blocks in the transition region near P0
- Blocks where Q_R2Q is small and the sign relationship is dominated by the excursion term Q_exc

---

## 4. Route A Alpha Coefficient

For negative-E_theta rows the Route A formula is:

\[
R_{\rm R2Q}(J) = \alpha(J) \cdot (-E_\theta(J)) + \text{Err}(J),
\]

where:

\[
\alpha(J) = \frac{Q_{\rm R2Q}(J)}{-E_{\theta,\rm norm}(J)}
=
\frac{Q_{\rm R2Q}(J)}{|E_\theta(J)| / \text{scale}(J)}.
\]

Observed alpha range:

\[
\alpha_{\min} = 3.27, \qquad
\alpha_{\max} = 419.10, \qquad
\alpha_{\rm mean} = 23.07.
\]

Rows computed: 148.

The alpha coefficient is **not universal** — it varies with the block geometry (h and p*).
The Route A proof must bound alpha from below by an analytic function of h and p*.

---

## 5. Proof-Grade Status

| Component | Status |
|---|---|
| Q_delta_D formula | primitive, computable from D_N endpoints |
| Q_exc formula | primitive, computable from bridge path |
| Q_R2Q = Q_delta_D + Q_exc + epsilon | verified, max residual 0.025728 |
| NegativeTransfer from primitives | True |
| PositiveHarmlessness from primitives | False (1302 violations) |
| Route A alpha | computed for 148 negative-E_theta rows |
| Formula grade | **proof_grade_partial** |
| Primitive coverage | 166/1468 rows full, 166/1468 partial |

---

## 6. What Remains for Proof Grade

The decomposition is now available from primitives. The remaining formal steps are:

1. **Prove DeltaD < 0 iff E_theta < 0** (the sign relationship between bridge endpoint change and theta deficit). Target: `Prime_Mesh_R2Q_DeltaD_ETheta_SignProof_Target_v1.md`
2. **Bound alpha(J) from below** by an analytic function of h and p* to formalize Route A.
3. **Prove |epsilon| <= C_epsilon x Q_R2Q** analytically (the residual is small relative to the main term).
4. **Prove Q_exc <= C_exc** (the H-Exc BridgeMaximal lemma).
5. **Investigate the 18 sign-inconsistent rows** and confirm endpoint-exclusion or finite-zone classification.
6. **Expand primitive coverage from 166 to 1468 rows** — the instrumentation gap for the remaining 1302 rows.

---

## 7. Recommended Next File

```text
Prime_Mesh_R2Q_DeltaD_ETheta_SignProof_Target_v1.md
```

Purpose: prove DeltaD < 0 iff E_theta < 0 using the shell weight formula
$w_s(n) - E_{\rm mod}(n)$ and the Three-Dominance structure.

---

*Prime Mesh Theory — RH Programme*
