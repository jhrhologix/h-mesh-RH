# Prime Mesh R2Q — Final Conditional RH Assembly Update v5

**Document:** `Prime_Mesh_R2Q_Final_Conditional_RH_Assembly_Update_v5.md`  
**Project:** Prime Mesh Theory — RH Programme  
**Date:** 2026-05-10  
**Status:** Consolidated conditional assembly update after H-Exc, EndpointMotion, O2, B3, and NeutralClause closures  
**Purpose:** Record the current final R2Q/RH assembly state with all recently closed local obstruction layers integrated.

---

## 1. Executive Verdict

This v5 update consolidates the local obstruction stack.

The current status is:

\[
\boxed{
\text{Conditional RH assembly with local row-class obstruction stack closed in the audited/certificate layer.}
}
\]

It is **not** an unconditional proof of RH.

The newly integrated closures are:

1. **H-Exc closure**
   \[
   Q_{\rm exc}\le0.025.
   \]

2. **EndpointMotion direct threshold sign**
   \[
   Q_{\rm R2Q}>0.75\Rightarrow E_\theta<0.
   \]

3. **Positive harmlessness**
   \[
   E_\theta>0\Rightarrow Q_{\rm R2Q}\le0.305<0.75.
   \]

4. **O2 repayment**
   \[
   E_\theta<0,\quad Q_{\rm R2Q}\le0.75
   \Rightarrow
   \text{O2-safe}.
   \]

5. **B3 no-accumulation**
   \[
   \text{accumulation-risk}
   \Rightarrow
   \text{B3-safe}.
   \]

6. **NeutralClause**
   \[
   \mathcal N=\varnothing
   \]
   in the audited row set.

Together, these close the local row-class obstruction system in the audited Route-A SR11/R2Q stack.

---

## 2. Core Decomposition

The RawR2Q decomposition is:

\[
\boxed{
Q_{\rm R2Q}
=
Q_{\Delta D}
+
Q_{\rm exc}
+
\epsilon.
}
\]

The closed component caps are:

\[
Q_{\rm exc}\le0.025,
\]

\[
|\epsilon|\le0.03.
\]

On the positive endpoint branch:

\[
Q_{\Delta D}\le\frac14.
\]

Therefore:

\[
Q_{\rm R2Q}
\le
\frac14+0.025+0.03
=
0.305
<
0.75.
\]

This is the correct proof-facing positive cap.

Do **not** state:

\[
Q_{\rm R2Q}\le\frac14
\]

as the positive theorem unless a separate proof exists.

---

## 3. Local Row-Class Partition

The final local obstruction logic partitions rows into the following classes.

### Class P — Positive endpoint rows

\[
E_\theta>0.
\]

Closure:

\[
\boxed{
E_\theta>0
\Rightarrow
Q_{\rm R2Q}\le0.305<0.75.
}
\]

Thus positive rows cannot cross the R2Q threshold.

---

### Class T — Threshold rows

\[
Q_{\rm R2Q}>0.75.
\]

Closure:

\[
\boxed{
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta<0.
}
\]

Thus threshold rows are negative-transfer rows.

---

### Class N — Negative subthreshold rows

\[
E_\theta<0,
\qquad
Q_{\rm R2Q}\le0.75.
\]

Closure:

\[
\boxed{
E_\theta<0,\ Q_{\rm R2Q}\le0.75
\Rightarrow
\text{O2-safe}.
}
\]

Thus negative subthreshold rows are repaid / non-surviving / finite-certified / numerically neutralized.

---

### Class A — Accumulation-risk rows

Closure:

\[
\boxed{
\text{accumulation-risk}
\Rightarrow
\text{B3-safe}.
}
\]

Thus there are no surviving unrepaid accumulation paths in the audited row-level B3 table.

---

### Class Z — Neutral rows

\[
|E_\theta|\le\tau.
\]

Closure:

\[
\boxed{
\mathcal N=\varnothing
}
\]

for all tested tolerances up to:

\[
\tau=10^{-2}.
\]

Thus there is no neutral leftover case in the audited row set.

---

## 4. H-Exc Closure

The H-Exc target was:

\[
Q_{\rm exc}\le0.025.
\]

The closure route is sampled-grid bridge energy:

\[
\|B_J\|_{2,T_J}^2\le100h.
\]

Then:

\[
Q_{{\rm energy},L2}
=
\frac{\|B_J\|_{2,T_J}}{\sqrt h\log^2 p^*}
\le
\frac{10}{\log^2p^*}.
\]

For:

\[
p^*\ge P_0,
\qquad
P_0=500,000,000,
\]

this gives:

\[
Q_{{\rm energy},L2}\le0.025.
\]

Since:

\[
Q_{\rm exc}\le Q_{{\rm energy},L2},
\]

we get:

\[
\boxed{
Q_{\rm exc}\le0.025.
}
\]

---

## 5. Critical H-Exc Caveat: Sampled Grid Only

The H-Exc bridge theorem is sampled-grid only.

The grid is:

\[
T_J
=
\{y\}
\cup
\{y+r:\ r\text{ is an available SR11 }h\text{-sample for }(block_id,y),\ r\le h\}
\cup
\{y+h\}.
\]

The theorem is:

\[
\sum_{t\in T_J}|B_J(t)|^2\le100h.
\]

It is **not**:

\[
\sum_{t=y}^{y+h}|B_J(t)|^2\le100h.
\]

Full-grid lifting failed and must not be silently assumed.

Every H-Exc statement in the paper must carry the \(T_J\) sampled-grid subscript.

---

## 6. PrimeShockBridge Closure Inside H-Exc

The dominant H-Exc component is the sampled centered prime-shock bridge:

\[
B_{\rm prime}(r)
=
\sum_{y<n\le y+r}\Lambda(n)
-
\frac rh
\sum_{y<n\le y+h}\Lambda(n),
\qquad r\in R_J=T_J-y.
\]

Define:

\[
K_{\rm prime}
=
\frac{\|B_{\rm prime}\|_{2,T_J}^2}{h}.
\]

The closure theorem is:

\[
\boxed{
p^*(J)\ge P_0
\Rightarrow
K_{\rm prime}(J)\le65.
}
\]

It is proved/certified by RayleighCoupling:

\[
K_{\rm prime}=\rho_JW_J.
\]

with three branches:

\[
\boxed{
\begin{cases}
W_J\le1040, & \rho_J\le1/16,\quad K_{\rm prime}\le65,\\[4pt]
W_J>1040,\ h\ge800, & K_{\rm prime}\le45.488076<65,\\[4pt]
W_J>1040,\ h<800, & K_{\rm prime}\le65\text{ by finite sampled-grid certificate.}
\end{cases}
}
\]

The short-block certificate rows are:

\[
\{
\texttt{hexc\_00453},
\texttt{hexc\_00442},
\texttt{hexc\_00462},
\texttt{hexc\_00663}
\}.
\]

Worst short-block row:

\[
\texttt{hexc\_00453},
\qquad
K_{\rm prime}=64.2498859117,
\qquad
65-K_{\rm prime}=0.7501140883.
\]

---

## 7. EndpointMotion DirectThresholdSign Closure

The supported threshold theorem is direct sign transfer:

\[
\boxed{
Q_{\rm R2Q}>0.75
\Rightarrow
E_\theta<0.
}
\]

The two-step route:

\[
Q_{\rm R2Q}>0.75
\Rightarrow
Q_{\Delta D}>0.75
\Rightarrow
E_\theta<0
\]

must not be used as the formal proof path.

Reason:

\[
\texttt{hexc\_00040}
\]

has:

\[
Q_{\rm R2Q}=0.75685966,
\]

\[
Q_{\Delta D}=0.74670767<0.75,
\]

but:

\[
E_\theta=-1617.0683<0.
\]

So the direct sign theorem passes, while the delta-threshold intermediate fails.

Threshold rows:

| candidate | \(Q_{\rm R2Q}\) | \(Q_{\Delta D}\) | \(E_\theta\) |
|---|---:|---:|---:|
| `hexc_00000` | 1.819352 | 1.8091175 | -3089.9881 |
| `hexc_00006` | 0.86252635 | 0.85284271 | -928.35302 |
| `hexc_00040` | 0.75685966 | 0.74670767 | -1617.0683 |

All have:

\[
E_\theta<0.
\]

---

## 8. Positive Harmlessness Closure

Positive endpoint rows satisfy:

\[
E_\theta>0.
\]

The empirical maximum is:

\[
Q_{\rm R2Q}^{\max}=0.215708483605.
\]

The proof-facing cap is:

\[
Q_{\rm R2Q}
\le
\frac14+0.025+0.03
=
0.305.
\]

Thus:

\[
\boxed{
E_\theta>0
\Rightarrow
Q_{\rm R2Q}\le0.305<0.75.
}
\]

This is sufficient for positive harmlessness.

---

## 9. O2 Repayment Closure

The O2 target population is:

\[
E_\theta<0,
\qquad
Q_{\rm R2Q}\le0.75.
\]

Audit facts:

\[
\text{negative subthreshold rows}=145,
\]

\[
\text{post-}P_0\text{ negative subthreshold rows}=21,
\]

\[
\text{surviving unrepaid negative subthreshold rows}=0.
\]

The conservative O2 cap is:

\[
Q_{O2}^{\rm conservative}
=
0.0499059549846063
<
0.05.
\]

The margin is:

\[
9.40450153937\times10^{-5}.
\]

This is small but positive.

Closure:

\[
\boxed{
E_\theta<0,\ Q_{\rm R2Q}\le0.75
\Rightarrow
\text{O2-safe}.
}
\]

---

## 10. B3 NoAccumulation Closure

B3 closes hidden tail accumulation.

Audit facts:

\[
\text{B3 mode}=\texttt{dedicated\_B3},
\]

\[
\text{accumulation-risk rows}=142,
\]

\[
\text{surviving unrepaid accumulation rows}=0,
\]

\[
\text{B3 numeric failures}=0,
\]

\[
\text{persistence failures}=0.
\]

Closure:

\[
\boxed{
\text{accumulation-risk}
\Rightarrow
\text{B3-safe}.
}
\]

Caveat:

Chain IDs were not available.

So this is row-level/dedicated-table B3 closure, not explicit chain-indexed closure.

Paper-safe wording:

> B3 closes in a dedicated row-level numeric table; chain IDs were unavailable.

---

## 11. NeutralClause Closure

Neutral rows are:

\[
|E_\theta|\le\tau.
\]

The NeutralClause audit tested:

\[
\tau=0,\ 10^{-14},\ 10^{-12},\ 10^{-10},\ 10^{-8},\ 10^{-6},\ 10^{-4},\ 10^{-3},\ 10^{-2}.
\]

At every tolerance:

\[
\text{neutral rows}=0.
\]

Closest row to neutral:

\[
\texttt{hexc\_00359},
\]

\[
|E_\theta|=1.5258205110753806,
\]

\[
Q_{\rm R2Q}=0.0702213435707402.
\]

Threshold rows are far from neutral:

\[
\min_{\text{threshold rows}}|E_\theta|
=
928.3530182520336.
\]

Closure:

\[
\boxed{
\mathcal N=\varnothing
}
\]

in the audited row set.

---

## 12. Finite Certificates

Finite certificates remain part of the proof/certificate stack.

Examples include:

1. finite-zone rows below \(P_0\);
2. short high-weight PrimeShockBridge rows;
3. finite negative subthreshold rows;
4. finite certified O2 rows;
5. any finite exceptions explicitly named by prior audits.

Known finite/certificate rows or families mentioned in this stack include:

- PrimeShockBridge finite-zone exception:
  \[
  \texttt{hexc\_00304},
  \qquad
  p^*=30386821,
  \qquad
  K_{\rm prime}=73.9100313047598.
  \]

- Short high-weight certificate set:
  \[
  \{
  \texttt{hexc\_00453},
  \texttt{hexc\_00442},
  \texttt{hexc\_00462},
  \texttt{hexc\_00663}
  \}.
  \]

- finite-zone negative subthreshold rows:
  \[
  124
  \]
  certified.

A separate finite certificate index should collect these.

Recommended future file:

```text
Prime_Mesh_R2Q_FiniteCertificate_Index_v1.md
```

---

## 13. Current Conditional RH Chain

The current intended chain is:

1. RawR2Q decomposition:
   \[
   Q_{\rm R2Q}=Q_{\Delta D}+Q_{\rm exc}+\epsilon.
   \]

2. H-Exc closure:
   \[
   Q_{\rm exc}\le0.025.
   \]

3. Residual closure:
   \[
   |\epsilon|\le0.03.
   \]

4. Positive branch:
   \[
   E_\theta>0
   \Rightarrow
   Q_{\Delta D}\le1/4.
   \]

5. Therefore:
   \[
   E_\theta>0
   \Rightarrow
   Q_{\rm R2Q}\le0.305<0.75.
   \]

6. Direct threshold sign:
   \[
   Q_{\rm R2Q}>0.75
   \Rightarrow
   E_\theta<0.
   \]

7. Negative subthreshold O2:
   \[
   E_\theta<0,\ Q_{\rm R2Q}\le0.75
   \Rightarrow
   \text{O2-safe}.
   \]

8. B3:
   \[
   \text{accumulation-risk}
   \Rightarrow
   \text{B3-safe}.
   \]

9. NeutralClause:
   \[
   \mathcal N=\varnothing.
   \]

10. Therefore the local row-level obstruction system has no positive threshold, no surviving unrepaid negative subthreshold obstruction, no B3 tail accumulation, and no neutral leftover.

11. The remaining RH implication still depends on the broader conditional bridge from this row-level obstruction system to the RH-scale global statement.

---

## 14. Relation to Classical RH Bridge

The classical von Koch criterion states that RH is equivalent to an RH-scale prime-counting error:

\[
\pi(x)=\operatorname{Li}(x)+O(\sqrt{x}\log x).
\]

The Prime Mesh/R2Q program aims to show that the local R2Q obstruction system prevents first crossing / forbidden endpoint behavior sufficient to imply the RH-scale bound.

This final step remains conditional on the correctness of the global bridge from the audited local row stack to the classical global statement.

---

## 15. What Is Closed Now

The following are closed in the audited/certificate stack:

| Layer | Status |
|---|---|
| H-Exc | closed sampled-grid/certificate |
| PrimeShockBridge | closed sampled-grid/certificate |
| Direct threshold sign | closed |
| Positive harmlessness | closed with \(0.305<0.75\) |
| O2 repayment | closed numeric repayment |
| B3 no-accumulation | closed dedicated numeric row-level |
| NeutralClause | closed by emptiness |
| finite-zone rows | certificate-covered, but need final index |
| full-grid H-Exc | not claimed |
| chain-indexed B3 | not claimed |
| unconditional RH | not claimed |

---

## 16. Remaining Work

The remaining work is now mostly higher-level assembly and reproducibility:

1. **FiniteCertificate Index**
   - collect every finite/certificate row and family;
   - list source CSVs;
   - list margins and reconstruction checks.

2. **Global bridge theorem**
   - make explicit how the local R2Q row-class closure implies the global RH-scale prime-counting bound.

3. **Paper draft**
   - convert the conditional assembly into clean definitions, lemmas, theorem statements, and proof/certificate references.

4. **Optional symbolic upgrades**
   - replace finite certificates with symbolic lemmas where possible;
   - chain-indexed B3 audit if chain IDs become available;
   - symbolic neutral-gap theorem if desired.

---

## 17. Correct Status Label

Use:

\[
\boxed{
\text{Final conditional RH assembly, local obstruction stack closed in audited/certificate form.}
}
\]

Do not use:

\[
\text{RH proved.}
\]

Do not use:

\[
\text{unconditional RH proof.}
\]

Do not use:

\[
\text{full-grid H-Exc proof.}
\]

Do not use:

\[
\text{all finite certificates replaced by symbolic proofs.}
\]

---

## 18. Recommended Next File

```text
Prime_Mesh_R2Q_FiniteCertificate_Index_v1.md
```

Purpose:

\[
\boxed{
\text{collect all finite/certificate rows, source files, margins, reconstruction checks, and closure roles.}
}
\]

After that:

```text
Prime_Mesh_R2Q_Final_Conditional_RH_Paper_Draft_v1.md
```

or:

```text
Prime_Mesh_R2Q_GlobalBridge_to_RH_Proof_Attack_v1.md
```

depending on whether the next goal is documentation or the remaining global implication.

---

## 19. Honest Status

This is the strongest assembly state so far.

The local R2Q obstruction stack is closed in the audited/certificate layer.

The final RH result remains conditional on the global bridge from this local obstruction stack to the classical RH criterion, and on acceptance/reproducibility of the finite certificate components.

---

*Prime Mesh Theory — RH Programme*
