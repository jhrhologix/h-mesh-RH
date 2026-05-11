# Prime Mesh R2Q — FiniteThetaEnvelope Certificate

**Document:** `Prime_Mesh_R2Q_FiniteThetaEnvelope_Certificate_v1.md`
**Project:** Prime Mesh Theory — RH Programme
**Date:** 2026-05-08
**Status:** Finite continuous theta-envelope certificate PASSED
**Purpose:** Close the missing all-x < P0 theta-envelope certificate.

---

## 1. Executive Verdict

\[
\boxed{
\texttt{pass\_finite\_theta\_envelope\_certificate}=\texttt{True}.
}
\]

The continuous finite-zone theta-envelope certificate passes.

Every x in:

\[
[2, P_0), \qquad P_0 = 500,000,000
\]

satisfies:

\[
\boxed{
|\theta(x) - x| \le C_\theta \sqrt{x} \log^2 x,
\qquad
C_\theta = C_{\theta,\text{finite}} = 1.923361.
}
\]

---

## 2. Method

The function $\theta(x) = \sum_{p \le x} \log p$ is a step function.

Between consecutive primes $p_n < x < p_{n+1}$:

\[
\theta(x) = \theta(p_n), \qquad H(x) = \theta(p_n) - x.
\]

The denominator $M(x) = \sqrt{x} \log^2 x$ is strictly increasing for $x \ge 2$.

Therefore the ratio $R(x) = |H(x)|/M(x)$ is maximized at one of two candidates per prime gap:

1. The **prime right-endpoint** $x = p_n$: $R = |\theta(p_n) - p_n| / M(p_n)$.
2. The **left limit** $x \to p_{n+1}^-$: $R = |\theta(p_n) - p_{n+1}| / M(p_{n+1})$.

Both are checked at every prime.
The pre-check for $p = 2$ (the first prime) is excluded because $x < 2$ is outside the domain $[2, P_0)$.

---

## 3. Computation

**Method:** Segmented sieve of Eratosthenes (numpy), 4,194,304 per segment.

**Primes sieved:** $[2, 499,999,999]$.

\[
\pi(500,000,000) = 26,355,867.
\]

\[
\theta(499,999,999) = 499983789.813729.
\]

**Elapsed time:** 33.1 seconds.

---

## 4. Certificate Result

\[
C_{\theta,\text{finite}} = \max_{2 \le x < P_0} R(x) = 1.9233607946.
\]

\[
\boxed{
C_{\theta,\text{finite}} = 1.923361.
}
\]

Worst point:

\[
x_{\text{worst}} = 2, \qquad H(x_{\text{worst}}) = -1.306853, \qquad \text{type: prime_endpoint}.
\]

Positive-side maximum:

\[
R_{+,\max} = 0.0000000000 \quad\text{at }x = 2.
\]

Negative-side maximum:

\[
R_{-,\max} = 1.9233607946 \quad\text{at }x = 2.
\]

---

## 5. Pass Criteria

\[
\texttt{prefix\_complete\_flag} = \texttt{True}.
\]

\[
\texttt{integer\_grid\_pass} = \texttt{True}.
\]

\[
\texttt{continuous\_all\_x\_pass} = \texttt{True}.
\]

\[
\texttt{failures} = 0.
\]

Therefore:

\[
\boxed{
\texttt{pass\_finite\_theta\_envelope\_certificate} = \texttt{True}.
}
\]

---

## 6. Continuous Certificate Argument

The step-function structure of $\theta(x)$ reduces the continuous maximum to a finite check.

In each gap $(p_n, p_{n+1})$:

\[
R(x) = \frac{|\theta(p_n) - x|}{\sqrt{x} \log^2 x}.
\]

Since $M(x) = \sqrt{x} \log^2 x$ is increasing on $[2, \infty)$ and the numerator $|\theta(p_n) - x|$ is linear with slope $\pm 1$, the continuous maximum of $R(x)$ over the gap is bounded by:

\[
\max\left(R(p_n),\; R(p_{n+1}^-)\right).
\]

Both are computed and checked.

Therefore the integer-grid certificate plus the step-function argument constitutes a **complete continuous certificate**.

---

## 7. Consequence for RH Assembly

The FiniteCertificate lemma in the conditional RH theorem is now closed:

\[
\boxed{
\text{FiniteThetaEnvelopeCertificate passes with }C_{\theta,\text{finite}} = 1.923361.
}
\]

The global theta envelope theorem requires $C_\theta \ge C_{\theta,\text{finite}} = 1.923361$ to cover the finite zone.

The post-$P_0$ asymptotic mechanism (FCL + ThetaSignBridge + O2/B3) must be consistent with this constant.

---

## 8. Updated Proof Stack Status

\[
\boxed{
\mathsf{FullFCL} \text{ empirically closed above } P_0.
}
\]

\[
\boxed{
\mathsf{FiniteCandidateCertificate} \text{ closed (1328/1328 rows).}
}
\]

\[
\boxed{
\mathsf{FiniteThetaEnvelopeCertificate} \text{ closed with } C_{\theta,\text{finite}} = 1.923361.
}
\]

The remaining open items are the analytic proof lemmas (NegativeTransfer, PositiveHarmlessness, H-Exc BridgeMaximal, O2, B3, etc.).

---

*Prime Mesh Theory — RH Programme*
