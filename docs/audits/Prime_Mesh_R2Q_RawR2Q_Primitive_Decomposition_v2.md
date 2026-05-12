# Prime Mesh R2Q — RawR2Q Primitive Decomposition (v2, corrected)

**Document:** `Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_v2.md`
**Project:** Prime Mesh Theory — RH Programme
**Date:** 2026-05-08
**Status:** Export patch v2 — PositiveHarmlessness check corrected
**Replaces:** `Prime_Mesh_R2Q_RawR2Q_Primitive_Decomposition_v1.md` (overclaimed)

---

## 1. Honest Verdict

\[
\boxed{
\text{RawR2Q primitive decomposition: partially validated.}
\quad
\text{Not yet proof-grade globally.}
}
\]

What validates:

- Formula $Q_{\rm R2Q} = Q_{\Delta D} + Q_{\rm exc} + \epsilon$ confirmed on **166 rows** (full primitive data).
- $\max|\epsilon| = 0.02572845$, $\text{mean}|\epsilon| = 0.00998078$.
- NegativeTransfer from primitives: **PASS** — 0 violations on 2 antecedent rows.
- PositiveHarmlessness from primitives: **PASS** — 0 violations on **18 primitive-available positive rows**.

What does **not** validate:

- v1 overclaimed PositiveHarmlessness as "PASS on 1320 rows". The 1302 instrumentation-gap rows (E_theta > 0, Q_delta_D missing) were incorrectly included in the antecedent. They are not counterexamples — they are **unevaluated**.
- Primitive coverage is only 166/1468 rows. 1302 rows remain in the instrumentation gap.
- The biconditional $\Delta D < 0 \iff E_\theta < 0$ is **false globally**: there are 18 sign-inconsistent rows, all of which are positive-harmless ($Q_{\Delta D} < 0.25$).

---

## 2. Primitive Formula

\[
\boxed{
Q_{\rm R2Q}(J) = Q_{\Delta D}(J) + Q_{\rm exc}(J) + \epsilon(J)
}
\]

where:

\[
Q_{\Delta D}(J) = \frac{|\Delta D(J)|}{\sqrt{h} \cdot \log^2(p^*)},
\qquad
Q_{\rm exc}(J) = \frac{\sup_{t \in J}|B_J(t)|}{\sqrt{h} \cdot \log^2(p^*)}
\]

Validated residual: $|\epsilon| \le 0.025728$ on 166 rows.

---

## 3. Corrected Sign Checks

### 3.1 NegativeTransfer

$Q_{\Delta D} > \tfrac{3}{4} \Rightarrow E_\theta < 0$

- Antecedent rows: 2
- Violations: **0**
- Status: **PASS**

### 3.2 PositiveHarmlessness (corrected)

$E_\theta > 0 \;\wedge\; \text{prim\_available} \Rightarrow Q_{\Delta D} \le \tfrac{1}{4}$

- Primitive-available positive rows (antecedent): **18**
- Violations: **0**
- Status: **PASS**
- Instrumentation-gap positive rows (not evaluated): **1302**

These 1302 gap rows are *not counterexamples* — their $Q_{\Delta D}$ is simply missing from the export. They are the primary target of the next patch.

### 3.3 Sign consistency

- Checked rows: 166
- Consistent: 148 (fraction 0.8916)
- Inconsistent: 18, of which **18 are positive-harmless** ($Q_{\Delta D} < 0.25$)

The proposed biconditional $\Delta D < 0 \iff E_\theta < 0$ is **not globally true**. The correct weaker claim is:

\[
\Delta D < 0 \;\Rightarrow\; E_\theta < 0
\quad\text{is consistent with all checked rows (no counterexample found)}.
\]

The converse ($E_\theta < 0 \Rightarrow \Delta D < 0$) fails for 18 rows, all positive-harmless.

---

## 4. Route A Alpha

- Rows computed: 148 (negative-E_theta with primitive data)
- Range: $\alpha \in [3.27,\, 419.10]$, mean $= 23.07$
- Alpha is **not universal** — analytic bounding from $h$ and $p^*$ is still required.

---

## 5. Coverage and Proof Grade

| Category | Count |
|---|---|
| Total rows | 1468 |
| primitive_full (Q_delta_D + Q_exc) | 166 |
| primitive_partial (Q_delta_D only) | 166 |
| instrumentation_gap (no primitive) | 1302 |
| pos_harm antecedent evaluated | 18 |
| pos_harm gap rows (not evaluated) | 1302 |
| Global proof grade | **proof_grade_partial** |

---

## 6. What Remains

1. **Full primitive export for all 1468 rows** — the 1302 gap rows need $D_N$ endpoint values exported from the bridge computation.
2. **Prove $\Delta D < 0 \Rightarrow E_\theta < 0$** (one direction only — the converse is false).
3. **Classify the 18 sign-inconsistent rows** — confirm all are positive-harmless and identify whether they arise from endpoint exclusion or the finite-zone structure.
4. **Bound alpha analytically** from $h$ and $p^*$.

---

## 7. Recommended Next File

```text
Prime_Mesh_R2Q_RawR2Q_FullPrimitiveExport_Patch_Spec_v1.md
```

Specifies what must be exported from the bridge computation to close the 1302 instrumentation-gap rows.

---

*Prime Mesh Theory — RH Programme*
