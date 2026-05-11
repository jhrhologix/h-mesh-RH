# Prime Mesh R2Q - H-Exc D_N Path Definition Extraction v1

**Status:** definition extracted from local scripts  
**Date:** 2026-05-09  
**Purpose:** freeze the exact `D_N(t)` path, sample grid, endpoint affine line, bridge residual, and norm convention used by the H-Exc audits.

## Executive Result

The H-Exc path is a sampled SR11 real recovery path. At the symbolic upstream level, SR11 reconstructs `D_N` from integer increments

```text
Delta D_N(n) = C_N E_mod(n) - Lambda(n).
```

Inside the H-Exc repair audits, that upstream path is used through exported samples:

```text
D_t = D_N(t)
line_t = ell_J(t)
diff = B_J(t) = D_N(t) - ell_J(t)
```

from:

```text
prime_mesh_r2q_hexc_bridge_path_samples_v1.csv
```

The H-Exc theorem currently being audited is therefore the sampled-grid statement:

```text
sum_{t in T_J} |D_N(t) - ell_J(t)|^2 <= 100 h
```

for post-`P0` rows.

## Source Files Inspected

Primary H-Exc export:

```text
<package-root>/prime_mesh_r2q_hexc_bridge_energy_export_patch.py
```

RawR2Q full primitive export:

```text
<package-root>/prime_mesh_r2q_rawr2q_full_primitive_export_patch.py
```

SR11 upstream reconstruction:

```text
<repo-root>/docs/RH/scripts/prime_mesh_r2q_sr11_reconstruct_recovery_path_noise.py
```

Primary exported path table:

```text
<package-root>/prime_mesh_r2q_hexc_bridge_path_samples_v1.csv
```

## A. Exact Upstream Path Definition

The SR11 reconstruction script states and implements:

```text
Delta D_N(n) = C_N E_mod(n) - Lambda(n).
```

For a recovery block with `worst_prime` and `end_prime`, it computes increments on:

```text
n in [worst_prime + 1, end_prime].
```

Then:

```text
prefix[0] = 0
prefix[k] = sum_{i=1}^k Delta D_N(worst_prime+i)
D_N(worst_prime+k) = D_worst + prefix[k].
```

If only normalized depth is available, SR11 may reconstruct the raw starting value by:

```text
D_worst = -d_worst * sqrt(p_star).
```

The implemented local increment uses:

```text
E_mod(n) = g(n)^2
g(n) = dist(spf(n) mod spf(n-1), 0 mod spf(n-1)) / spf(n-1)
Lambda(n) = log p if n = p^k, else 0.
```

Equivalently:

```text
D_N(t) = D_N(a) + sum_{a < n <= t} (C_N E_mod(n) - Lambda(n)).
```

This is the symbolic formula needed for the final H-Exc analytic lemma.

## B. Exact H-Exc Sample Grid

For each H-Exc row `J=[y,y+h]`, the repair export reads SR11 rows with matching:

```text
(p_star, y)
```

and internal SR11 offsets:

```text
1 <= h_sample <= h.
```

It then prepends the left endpoint:

```text
offset = 0
D_t = D_start = D_N(y).
```

Thus the H-Exc sample grid is:

```text
T_J = {y} union { y + h_sample : SR11 exported a row for (p_star, y, h_sample), 1 <= h_sample <= h }.
```

The right endpoint is included when SR11 contains the `h_sample = h` row. The export requires the endpoint sample to exist for a pass.

The exported grid type is:

```text
sr11_realpath_offsets_plus_left_endpoint
```

Important proof note: this is a sampled grid norm, not yet a proof of the full integer-grid norm unless a separate grid-density/interpolation lemma is added.

## C. Exact Endpoint Affine Line

For each row:

```text
D_start = D_N(y)
D_end = D_N(y+h)
DeltaD = D_end - D_start
```

The endpoint affine line is exactly:

```text
ell_J(t) = D_start + ((t-y)/h) * DeltaD.
```

In exported columns:

```text
line_t = D_start + (offset / h) * DeltaD
offset = t - y.
```

This is in the same raw `D_N` normalization as `D_t`.

## D. Exact Bridge Residual

The bridge residual is:

```text
B_J(t) = D_N(t) - ell_J(t).
```

In exported columns:

```text
diff = D_t - line_t
abs_diff = abs(diff).
```

At the left endpoint:

```text
B_J(y) = 0.
```

At the right endpoint, when sampled:

```text
B_J(y+h) = 0.
```

The increment form is:

```text
B_J(t)
= sum_{y<n<=t} d_N(n)
  - ((t-y)/h) sum_{y<n<=y+h} d_N(n),

d_N(n) = C_N E_mod(n) - Lambda(n).
```

For sampled offsets `u_i=t_i-y`:

```text
B_i = D_i - (D_0 + (u_i/h)(D_m-D_0)).
```

## E. Norm and Normalization

The H-Exc bridge energy audit uses the unweighted sampled square-sum:

```text
||B_J||_{2,J}^2 = sum_{t in T_J} |B_J(t)|^2.
```

In code:

```text
bridge_energy_L2_raw = sum(diff * diff)
```

Despite the historical column name, `bridge_energy_L2_raw` is the square-sum, not the L2 norm. The true L2 norm is:

```text
sqrt(bridge_energy_L2_raw).
```

The normalized quantities are:

```text
denom = sqrt(h) * log(p_star)^2
Q_energy_L2 = sqrt(sum diff^2) / denom
Q_exc = max |diff| / denom
C_bridge = sqrt(sum diff^2) / sqrt(h)
```

The endpoint-affine H-Exc target is:

```text
C_bridge^2 = ||B_J||_{2,J}^2 / h <= 100.
```

## F. Residual Decomposition

Using the upstream increment formula, the residual decomposes as:

```text
B_J(t)
= [partial composite response - partial prime shock]
 - ((t-y)/h)[total composite response - total prime shock].
```

More explicitly:

```text
B_J(t)
= sum_{y<n<=t} (C_N E_mod(n) - Lambda(n))
 - ((t-y)/h) sum_{y<n<=y+h} (C_N E_mod(n) - Lambda(n)).
```

So the non-affine residual is the centered partial-sum bridge of:

```text
C_N E_mod(n) - Lambda(n).
```

This is the analytic object behind the H-Exc endpoint-affine residual theorem.

## G. Existing Support

The following audits verify the implementation-level object:

```text
H-Exc DirectBridgeEnvelope:
p_star >= 500M => ||B_J||_2^2/h <= 64.137 < 100.
```

```text
AffineProjectionResidual:
endpoint residual bound passes; endpoint line remains the theorem object.
```

```text
LocalAffineDecomposition:
endpoint affine line captures at least 99.9975% of D_N path energy post-P0.
```

```text
LocalAffinity EnergyBudget:
direct product eta_aff*K_D <= 100 passes, but independent eta_aff and K_D caps do not.
```

## H. Current Blocker

The path definition is now clear, but the proof must be careful about the norm:

```text
Current audits prove/support the sampled-grid H-Exc norm on T_J.
```

To make the H-Exc theorem fully proof-grade, one of the following must be stated:

```text
1. The theorem is intentionally a sampled-grid theorem on T_J; or
2. A grid-lifting lemma promotes the sampled SR11 grid bound to the full integer interval.
```

The natural next theorem target is therefore:

```text
Prime_Mesh_R2Q_HExc_DN_Path_Definition_Theorem_Target_v1.md
```

with a flagged follow-up if full integer-grid control is required:

```text
Prime_Mesh_R2Q_HExc_SampledGrid_to_IntegerGrid_Lifting_Target_v1.md
```

## Candidate Lemma

Let `J=[y,y+h]` be an admissible post-`P0` block and let:

```text
d_N(n)=C_N E_mod(n)-Lambda(n),
D_N(t)=D_N(y)+sum_{y<n<=t}d_N(n).
```

Let:

```text
ell_J(t)=D_N(y)+((t-y)/h)(D_N(y+h)-D_N(y)).
```

On the SR11/H-Exc sample grid `T_J`,

```text
sum_{t in T_J} |D_N(t)-ell_J(t)|^2 <= 100h.
```

Equivalently:

```text
||D_N-ell_J||_{2,T_J} <= 10 sqrt(h).
```

This is the central H-Exc endpoint-affine residual lemma in extracted notation.

