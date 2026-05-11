# Prime Mesh R2Q - FiniteThetaEnvelope Codex Validation

**Document:** `Prime_Mesh_R2Q_FiniteThetaEnvelope_Codex_Validation_v1.md`  
**Project:** Prime Mesh Theory - RH Programme  
**Date:** 2026-05-08  
**Status:** independent validation of Claude finite theta-envelope certificate

## 1. Verdict

The attached finite theta-envelope certificate is validated.

Codex independently reran a segmented sieve verifier for:

\[
2 \le x < P_0,\qquad P_0=500,000,000.
\]

The independent verifier checked both:

- continuous prime-gap left limits \(q^-\);
- integer pre-prime points \(q-1\).

Both versions have the same worst point:

\[
x=2.
\]

## 2. Independent Check Numbers

| metric | value |
|---|---:|
| `P0` | 500000000 |
| `prime_count` | 26355867 |
| `theta_P0_minus` | 499983789.8137968 |
| `max_continuous_ratio` | 1.9233607946440099 |
| `max_continuous_x` | 2 |
| `max_continuous_type` | prime_endpoint |
| `max_integer_grid_ratio` | 1.9233607946440099 |
| `max_integer_grid_x` | 2 |
| `max_positive_ratio_found` | none |

The small difference between this theta total and Claude's reported:

\[
499983789.813729
\]

is floating-order accumulation noise and does not affect the maximum certificate constant, which is attained at \(x=2\).

## 3. Endpoint Convention Check

Claude's script checks \(q^-\) using:

\[
\frac{|\theta(q^-)-q|}{\sqrt q\log^2q}.
\]

This is the correct continuous left-limit object.

For an integer-only certificate, the corresponding point is \(q-1\). Codex checked that separately; it does not exceed the same worst ratio at \(x=2\).

## 4. Validated Certificate Constant

\[
\boxed{
C_{\theta,\mathrm{finite}} = 1.9233607946440099.
}
\]

Thus any global constant:

\[
C_\theta \ge 1.9233607946440099
\]

covers the finite zone \(2\le x<500,000,000\).

## 5. One Script Portability Note

The copied Claude script has its output directory hard-coded as:

```text
/sessions/awesome-jolly-mayer/mnt/00_guides
```

That does not affect the already-produced CSV/Markdown certificate files, but if rerun inside the Windows repo it should be patched to write to the repair `scripts and results` folder.

## 6. Proof-Stack Status

\[
\boxed{
\text{FiniteThetaEnvelopeCertificate is validated.}
}
\]

The finite side now has:

- finite candidate certificate: closed;
- continuous finite theta-envelope certificate: validated with \(C_{\theta,\mathrm{finite}}\approx1.9233607946\).

---

*Prime Mesh Theory - RH Programme*
