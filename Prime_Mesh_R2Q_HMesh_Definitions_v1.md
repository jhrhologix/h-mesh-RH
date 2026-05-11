# Hegyesy Mesh — Core Definitions

**Document:** `Prime_Mesh_R2Q_HMesh_Definitions_v1.md`
**Project:** Prime Mesh Theory — RH Programme
**Date:** 2026-05-11
**Author:** Jonathan Hegyesy
**Purpose:** Reviewer-facing dictionary of the core H-Mesh objects underlying the Prime Mesh R2Q certificate stack.

---

## 1. What Is the Hegyesy Mesh?

The **Hegyesy Mesh**, abbreviated **H-Mesh**, is the local geometric structure obtained by cutting
the prime-error function into finite windows and comparing each window to its endpoint
interpolation.

In one sentence:

> The H-Mesh turns the global prime-error problem into local first-exit geometry.

The global object under study is the active theta bridge:

$$
G(x) = \theta(x) - x,
$$

where $\theta(x) = \sum_{p \le x} \log p$ is the Chebyshev prime-counting function.

The H-Mesh decomposes the global control of $G(x)$ into local window-level certificates.
Each window either generates a first-exit obstruction or is certified harmless.
If every window is certified harmless, no first exit from the RH-scale envelope can occur.

---

## 2. Core Objects

### 2.1 Local Window

A **local window** is a closed interval:

$$
J = [y,\, y + h],
$$

with left endpoint $y$, width $h > 0$, and a designated **scale prime** $p^*(J)$, the largest
prime in $J$ (or the nearest prime above $y + h$ when $J$ contains no prime).

The cutoff below which the finite certificate applies directly is:

$$
P_0 = 500{,}000{,}000.
$$

Post-$P_0$ windows ($p^*(J) \ge P_0$) are the primary targets of the R2Q certificate stack.

### 2.2 Endpoint Path

The **endpoint path** is the log-prime weighted cumulative function:

$$
D_N(t) = \sum_{\substack{p \le t \\ p \text{ prime}}} \log p \;-\; t
\;=\; \theta(t) - t.
$$

For a window $J = [y, y+h]$:

$$
D_N(y) = \theta(y) - y, \qquad D_N(y+h) = \theta(y+h) - (y+h).
$$

The **endpoint displacement** is:

$$
\Delta D(J) = D_N(y+h) - D_N(y) = [\theta(y+h) - \theta(y)] - h = E_\theta(J),
$$

where $E_\theta(J) = \theta(y+h) - \theta(y) - h$ is the **local theta excess** of window $J$.

### 2.3 Affine Interpolation

The **affine interpolation** of $D_N$ across $J$ is the linear function:

$$
\ell_J(t) = D_N(y) + \frac{t - y}{h}\bigl[D_N(y+h) - D_N(y)\bigr], \qquad t \in J.
$$

This is the straight-line segment connecting the two endpoint values.

### 2.4 Bridge Excursion

The **bridge** is the centered departure of the endpoint path from its affine interpolation:

$$
B_J(t) = D_N(t) - \ell_J(t), \qquad t \in J.
$$

By construction $B_J(y) = B_J(y+h) = 0$.

The **bridge excursion** is the maximum departure on the sampled grid $T_J$:

$$
Q_{\rm exc}(J) = \frac{\sup_{t \in T_J} |B_J(t)|}{\sqrt{h}\,\log^2 p^*}.
$$

### 2.5 Sampled Grid

The **sampled grid** $T_J$ is the set of SR11 audit sample points inside $J$:

$$
T_J \subset J, \qquad N_s = |T_J|.
$$

**Critical caveat:** the H-Exc bridge bound is a *sampled-grid* result, not a full-integer-grid
result. The full-grid quantity $K_{\rm full}$ can be orders of magnitude larger than the
sampled-grid quantity $K_{\rm sampled}$. All H-Exc certificate statements reference $T_J$.

### 2.6 Endpoint-Motion Coordinate

The **endpoint-motion coordinate** is the normalized displacement:

$$
Q_{\Delta D}(J) = \frac{|\Delta D(J)|}{\sqrt{h}\,\log^2 p^*}.
$$

### 2.7 R2Q Obstruction Coordinate

The **R2Q obstruction coordinate** is the full normalized obstruction:

$$
\boxed{Q_{\rm R2Q}(J) = Q_{\Delta D}(J) + Q_{\rm exc}(J) + \epsilon(J),}
$$

where $\epsilon(J)$ is a small residual from discretization and normalization.

The primitive decomposition is empirically verified on all 1,468 audited rows with
residual $|\epsilon(J)| \le 0.03$ and reconstruction error $\le 2.22 \times 10^{-16}$.

### 2.8 Threshold and Channel Classification

A window $J$ is **threshold-relevant** if:

$$
Q_{\rm R2Q}(J) > \tfrac{3}{4}.
$$

A threshold-relevant window enters the **negative channel** $\mathcal{C}_-$, meaning:

$$
Q_{\rm R2Q}(J) > \tfrac{3}{4} \;\Rightarrow\; E_\theta(J) < 0.
$$

A window with $E_\theta(J) > 0$ is **positive-harmless**:

$$
E_\theta(J) > 0 \;\Rightarrow\; Q_{\rm R2Q}(J) \le 0.305 < \tfrac{3}{4}.
$$

---

## 3. The R2Q Certificate Mechanism

The R2Q certificate stack asks, for every local window $J$:

> Can $J$ produce a first exit from the RH-scale envelope
> $\mathcal{E}_\theta(x) = C_\theta \sqrt{x}\,\log^2 x$?

A first exit is impossible if every post-$P_0$ window satisfies one of:

1. **Positive harmlessness:** $E_\theta(J) > 0 \Rightarrow Q_{\rm R2Q}(J) \le 0.305$.
2. **Negative channel repayment:** $J \in \mathcal{C}_-$ is repaid by O2 local repayment.
3. **B3 no-accumulation:** negative-channel rows do not accumulate into a surviving tail obstruction.
4. **Finite certificate:** below $P_0$, a direct continuous theta-envelope certificate applies
   with $C_{\theta,\rm finite} = 1.9233607946440099$.
5. **Coordinate-gap margin:** coordinate gaps between candidate windows satisfy
   $|R_\theta(x)| < 1$ throughout, verified for all 141 gaps.

---

## 4. Certified Constants

| Quantity | Value |
|---|---|
| Envelope constant $C_\theta$ | $1.9233607946440099$ |
| Finite zone cutoff $P_0$ | $500{,}000{,}000$ |
| Q-exc empirical max | $0.0205672364492246$ |
| Q-exc theorem cap | $\le 0.025$ |
| $|\epsilon|$ empirical max | $0.0257284509172872$ |
| $|\epsilon|$ theorem cap | $\le 0.03$ |
| O2 repayment cap $Q_{\rm O2}$ | $\le 0.05$ |
| Gap $R_\theta$ upper max | $-0.0006006774736066138$ |
| Gap $R_\theta$ lower min | $-0.0007553068873594187$ |
| ThresholdRelevance rows checked | $10{,}140$ |
| ThresholdRelevance failures | $0$ |

---

## 5. Relationship to Classical RH

The H-Mesh certificate gives:

$$
|\theta(x) - x| \le C_\theta \sqrt{x}\,\log^2 x \qquad (x \ge 2).
$$

The classical transfer is:

$$
|\theta(x) - x| = O(\sqrt{x}\,\log^2 x)
\;\Rightarrow\;
\psi(x) - x = O(\sqrt{x}\,\log^2 x),
$$

because $\psi(x) - \theta(x) = O(\sqrt{x}\,\log x)$ from prime-power estimates.

By the von Koch criterion:

$$
\psi(x) - x = O(\sqrt{x}\,\log^2 x) \;\Longleftrightarrow\; \mathrm{RH}.
$$

The Prime Mesh R2Q certificate gives a reproducible route to this criterion,
pending independent analytic proof of the remaining component theorems.

---

## 6. What the H-Mesh Is Not

- It is **not** a harmonic analysis framework. "H" stands for Hegyesy, not harmonic.
- It is **not** a full-integer-grid bridge bound. H-Exc is sampled-grid only.
- It is **not** a completed proof of RH. It is a certificate-level route with explicit
  remaining analytic proof obligations.

The remaining formal proof obligations are documented in:

```
Prime_Mesh_R2Q_Formal_Analytic_Proof_Roadmap_v1.md
Prime_Mesh_R2Q_Final_ProofAudit_Checklist_v1.md
```

---

## 7. Glossary

| Term | Definition |
|---|---|
| H-Mesh | Hegyesy Mesh — the local prime-error window geometry |
| $J = [y, y+h]$ | Local window with width $h$ and scale prime $p^*$ |
| $D_N(t)$ | Endpoint path $= \theta(t) - t$ |
| $\ell_J(t)$ | Affine interpolation of $D_N$ across $J$ |
| $B_J(t)$ | Bridge excursion $= D_N(t) - \ell_J(t)$ |
| $T_J$ | SR11 sampled grid inside $J$ |
| $E_\theta(J)$ | Local theta excess $= \theta(y+h) - \theta(y) - h$ |
| $Q_{\Delta D}$ | Normalized endpoint-motion coordinate |
| $Q_{\rm exc}$ | Normalized bridge excursion on $T_J$ |
| $Q_{\rm R2Q}$ | Full R2Q obstruction coordinate |
| $\mathcal{C}_-$ | Negative channel (threshold-relevant rows) |
| $P_0$ | Finite-zone cutoff $= 500{,}000{,}000$ |
| $C_\theta$ | Certified envelope constant $= 1.9233607946440099$ |
| FullFCL | Full First-Crossing Lemma — the main GlobalBridge theorem |

---

*Prime Mesh Theory — RH Programme*
*Jonathan Hegyesy, 2026*
